from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ome.analysis import (
    ContinuousOverlayEngine,
    ContinuousOverlayNotReady,
    ContinuousOverlayRequest,
    ContinuousOverlaySeries,
    ContinuousOverlaySuccess,
    DeltaObservationEngine,
    DeltaObservationNotReady,
    DeltaObservationRequest,
    DeltaObservationSuccess,
    DiscreteGearOverlayEngine,
    GearOverlayNotReady,
    GearOverlayRequest,
    GearOverlaySeries,
    GearOverlaySuccess,
    LapComparisonEngine,
    LapComparisonNotReady,
    LapComparisonRequest,
    LapComparisonSuccess,
)
from ome.domain import CanonicalConcept
from ome.evidence import ComparisonReportProvenance

ASSEMBLER_ID = "ome.lap-comparison.report"
ASSEMBLER_VERSION = "0.1.0"

CONTINUOUS_REPORT_CONCEPTS = (
    CanonicalConcept.VEHICLE_SPEED,
    CanonicalConcept.DRIVER_THROTTLE,
    CanonicalConcept.DRIVER_BRAKE,
    CanonicalConcept.DRIVER_STEERING,
    CanonicalConcept.ENGINE_SPEED,
)
REPORT_CONCEPTS = (*CONTINUOUS_REPORT_CONCEPTS, CanonicalConcept.TRANSMISSION_GEAR)


class SupportingEvidenceKind(StrEnum):
    CONTINUOUS = "continuous"
    DISCRETE = "discrete"


class SupportingEvidenceStatus(StrEnum):
    AVAILABLE = "available"
    NOT_READY = "not_ready"


class ComparisonReportIssueCode(StrEnum):
    BASE_COMPARISON_NOT_READY = "base_comparison_not_ready"
    OBSERVATIONS_NOT_READY = "observations_not_ready"
    DUPLICATE_SUPPORTING_CONCEPT = "duplicate_supporting_concept"
    UNSUPPORTED_SUPPORTING_CONCEPT = "unsupported_supporting_concept"
    INCONSISTENT_COMPONENT_PROVENANCE = "inconsistent_component_provenance"


@dataclass(frozen=True, slots=True)
class ComparisonReportReadinessIssue:
    code: ComparisonReportIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class ContinuousChannelPair:
    canonical_concept: CanonicalConcept
    lap_a_channel: ContinuousOverlaySeries | None
    lap_b_channel: ContinuousOverlaySeries | None


@dataclass(frozen=True, slots=True)
class GearChannelPair:
    lap_a_gear: GearOverlaySeries | None
    lap_b_gear: GearOverlaySeries | None


@dataclass(frozen=True, slots=True)
class ComparisonReportRequest:
    comparison: LapComparisonRequest
    continuous_channels: tuple[ContinuousChannelPair, ...] = ()
    gear: GearChannelPair | None = None


@dataclass(frozen=True, slots=True)
class SupportingEvidenceSummary:
    canonical_concept: CanonicalConcept
    kind: SupportingEvidenceKind
    status: SupportingEvidenceStatus
    unit: str | None
    issue_codes: tuple[str, ...] = ()
    messages: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ComparisonReportNotReady:
    issues: tuple[ComparisonReportReadinessIssue, ...]
    base_comparison: LapComparisonNotReady | None = None


@dataclass(frozen=True, slots=True)
class ComparisonReportSuccess:
    comparison: LapComparisonSuccess
    observations: DeltaObservationSuccess
    continuous_overlays: tuple[ContinuousOverlaySuccess, ...]
    gear_overlay: GearOverlaySuccess | None
    supporting_evidence: tuple[SupportingEvidenceSummary, ...]
    provenance: ComparisonReportProvenance


ComparisonReportOutcome = ComparisonReportSuccess | ComparisonReportNotReady


class ComparisonReportService:
    assembler_id = ASSEMBLER_ID
    assembler_version = ASSEMBLER_VERSION

    def __init__(self) -> None:
        self._comparison_engine = LapComparisonEngine()
        self._observation_engine = DeltaObservationEngine()
        self._continuous_engine = ContinuousOverlayEngine()
        self._gear_engine = DiscreteGearOverlayEngine()

    def build(self, request: ComparisonReportRequest) -> ComparisonReportOutcome:
        declaration_issues = self._declaration_issues(request.continuous_channels)
        if declaration_issues:
            return ComparisonReportNotReady(issues=declaration_issues)

        comparison = self._comparison_engine.compare(request.comparison)
        if isinstance(comparison, LapComparisonNotReady):
            return ComparisonReportNotReady(
                issues=(
                    ComparisonReportReadinessIssue(
                        code=ComparisonReportIssueCode.BASE_COMPARISON_NOT_READY,
                        message="The base lap comparison is not ready.",
                    ),
                ),
                base_comparison=comparison,
            )

        observations = self._observation_engine.observe(
            DeltaObservationRequest(base_comparison=comparison)
        )
        if isinstance(observations, DeltaObservationNotReady):
            return ComparisonReportNotReady(
                issues=(
                    ComparisonReportReadinessIssue(
                        code=ComparisonReportIssueCode.OBSERVATIONS_NOT_READY,
                        message="Delta observations are not ready for the base comparison.",
                    ),
                )
            )

        if observations.provenance.base_comparison != comparison.provenance:
            return self._inconsistent_provenance()

        pair_by_concept = {
            pair.canonical_concept: pair for pair in request.continuous_channels
        }
        continuous_overlays: list[ContinuousOverlaySuccess] = []
        summaries: list[SupportingEvidenceSummary] = []

        for concept in CONTINUOUS_REPORT_CONCEPTS:
            pair = pair_by_concept.get(concept)
            outcome = self._continuous_engine.overlay(
                ContinuousOverlayRequest(
                    base_comparison=comparison,
                    canonical_concept=concept,
                    lap_a_channel=None if pair is None else pair.lap_a_channel,
                    lap_b_channel=None if pair is None else pair.lap_b_channel,
                )
            )
            if isinstance(outcome, ContinuousOverlaySuccess):
                if outcome.provenance.base_comparison != comparison.provenance:
                    return self._inconsistent_provenance()
                continuous_overlays.append(outcome)
                summaries.append(
                    SupportingEvidenceSummary(
                        canonical_concept=concept,
                        kind=SupportingEvidenceKind.CONTINUOUS,
                        status=SupportingEvidenceStatus.AVAILABLE,
                        unit=outcome.unit,
                    )
                )
            else:
                summaries.append(self._continuous_not_ready_summary(concept, outcome))

        gear_pair = request.gear
        gear_outcome = self._gear_engine.overlay(
            GearOverlayRequest(
                base_comparison=comparison,
                lap_a_gear=None if gear_pair is None else gear_pair.lap_a_gear,
                lap_b_gear=None if gear_pair is None else gear_pair.lap_b_gear,
            )
        )
        if isinstance(gear_outcome, GearOverlaySuccess):
            if gear_outcome.provenance.base_comparison != comparison.provenance:
                return self._inconsistent_provenance()
            gear_overlay: GearOverlaySuccess | None = gear_outcome
            summaries.append(
                SupportingEvidenceSummary(
                    canonical_concept=CanonicalConcept.TRANSMISSION_GEAR,
                    kind=SupportingEvidenceKind.DISCRETE,
                    status=SupportingEvidenceStatus.AVAILABLE,
                    unit=gear_outcome.unit,
                )
            )
        else:
            gear_overlay = None
            summaries.append(self._gear_not_ready_summary(gear_outcome))

        provenance = ComparisonReportProvenance(
            assembler_id=self.assembler_id,
            assembler_version=self.assembler_version,
            requested_concepts=REPORT_CONCEPTS,
            base_comparison=comparison.provenance,
            delta_observation=observations.provenance,
            continuous_overlays=tuple(
                overlay.provenance for overlay in continuous_overlays
            ),
            gear_overlay=None if gear_overlay is None else gear_overlay.provenance,
        )

        return ComparisonReportSuccess(
            comparison=comparison,
            observations=observations,
            continuous_overlays=tuple(continuous_overlays),
            gear_overlay=gear_overlay,
            supporting_evidence=tuple(summaries),
            provenance=provenance,
        )

    @staticmethod
    def _declaration_issues(
        pairs: tuple[ContinuousChannelPair, ...],
    ) -> tuple[ComparisonReportReadinessIssue, ...]:
        issues: list[ComparisonReportReadinessIssue] = []
        seen: set[CanonicalConcept] = set()

        for pair in pairs:
            concept = pair.canonical_concept
            if concept not in CONTINUOUS_REPORT_CONCEPTS:
                issues.append(
                    ComparisonReportReadinessIssue(
                        code=ComparisonReportIssueCode.UNSUPPORTED_SUPPORTING_CONCEPT,
                        message=f"{concept.value} is not a v0.1 continuous report concept.",
                    )
                )
                continue
            if concept in seen:
                issues.append(
                    ComparisonReportReadinessIssue(
                        code=ComparisonReportIssueCode.DUPLICATE_SUPPORTING_CONCEPT,
                        message=f"{concept.value} was declared more than once.",
                    )
                )
            seen.add(concept)

        return tuple(issues)

    @staticmethod
    def _continuous_not_ready_summary(
        concept: CanonicalConcept,
        outcome: ContinuousOverlayNotReady,
    ) -> SupportingEvidenceSummary:
        return SupportingEvidenceSummary(
            canonical_concept=concept,
            kind=SupportingEvidenceKind.CONTINUOUS,
            status=SupportingEvidenceStatus.NOT_READY,
            unit=None,
            issue_codes=tuple(issue.code.value for issue in outcome.issues),
            messages=tuple(issue.message for issue in outcome.issues),
        )

    @staticmethod
    def _gear_not_ready_summary(
        outcome: GearOverlayNotReady,
    ) -> SupportingEvidenceSummary:
        return SupportingEvidenceSummary(
            canonical_concept=CanonicalConcept.TRANSMISSION_GEAR,
            kind=SupportingEvidenceKind.DISCRETE,
            status=SupportingEvidenceStatus.NOT_READY,
            unit=None,
            issue_codes=tuple(issue.code.value for issue in outcome.issues),
            messages=tuple(issue.message for issue in outcome.issues),
        )

    @staticmethod
    def _inconsistent_provenance() -> ComparisonReportNotReady:
        return ComparisonReportNotReady(
            issues=(
                ComparisonReportReadinessIssue(
                    code=ComparisonReportIssueCode.INCONSISTENT_COMPONENT_PROVENANCE,
                    message="A report component does not reference the base comparison provenance.",
                ),
            )
        )
