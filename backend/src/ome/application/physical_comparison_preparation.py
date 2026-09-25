from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ome.analysis import LapComparisonLap, LapComparisonRequest, LapComparisonSeries
from ome.application.comparison_report import ComparisonReportRequest
from ome.application.physical_track_reference import PhysicalTrackReferencePreparation
from ome.domain import CanonicalConcept
from ome.evidence import CanonicalSeriesEvidence, LapEvidenceContext, TransformationEvidence

PREPARATION_ID = "ome.preparation.physical-comparison-request"
PREPARATION_VERSION = "0.1.0"
ELAPSED_TRANSFORMATION_ID = "ome.preparation.lap-relative-elapsed-time"
ELAPSED_TRANSFORMATION_VERSION = "0.1.0"


class PhysicalComparisonPreparationIssueCode(StrEnum):
    EMPTY_DATASET_FINGERPRINT = "empty_dataset_fingerprint"
    DATASET_FINGERPRINT_MISMATCH = "dataset_fingerprint_mismatch"
    CONTEXT_DATASET_MISMATCH = "context_dataset_mismatch"
    SAME_LAP_CONTEXT = "same_lap_context"
    DISTANCE_DATASET_MISMATCH = "distance_dataset_mismatch"
    INVALID_TIME_EVIDENCE = "invalid_time_evidence"
    LENGTH_MISMATCH = "length_mismatch"
    INVALID_GRID_STEP = "invalid_grid_step"


@dataclass(frozen=True, slots=True)
class PhysicalComparisonPreparationIssue:
    code: PhysicalComparisonPreparationIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class PhysicalComparisonPreparationRequest:
    preparation: PhysicalTrackReferencePreparation
    grid_step_m: float


@dataclass(frozen=True, slots=True)
class PhysicalComparisonPreparationSuccess:
    report_request: ComparisonReportRequest
    dataset_fingerprint: str
    reference_context: LapEvidenceContext
    candidate_context: LapEvidenceContext
    preparation_id: str = PREPARATION_ID
    preparation_version: str = PREPARATION_VERSION


@dataclass(frozen=True, slots=True)
class PhysicalComparisonPreparationNotReady:
    issues: tuple[PhysicalComparisonPreparationIssue, ...]


PhysicalComparisonPreparationOutcome = (
    PhysicalComparisonPreparationSuccess | PhysicalComparisonPreparationNotReady
)


class PhysicalComparisonPreparationService:
    """Compose ready physical lap preparation into the existing comparison-report contract."""

    preparation_id = PREPARATION_ID
    preparation_version = PREPARATION_VERSION

    def prepare(
        self,
        request: PhysicalComparisonPreparationRequest,
    ) -> PhysicalComparisonPreparationOutcome:
        issues = self._readiness_issues(request)
        if issues:
            return PhysicalComparisonPreparationNotReady(issues=issues)

        preparation = request.preparation
        reference_elapsed = self._elapsed_series(
            preparation.dataset_fingerprint,
            preparation.reference_lap.timestamps_s,
            preparation.reference_lap.time_evidence,
        )
        candidate_elapsed = self._elapsed_series(
            preparation.dataset_fingerprint,
            preparation.candidate_lap.timestamps_s,
            preparation.candidate_lap.time_evidence,
        )

        comparison = LapComparisonRequest(
            lap_a=LapComparisonLap(
                context=preparation.reference_context,
                distance=preparation.reference_lap_distance,
                elapsed_time=reference_elapsed,
            ),
            lap_b=LapComparisonLap(
                context=preparation.candidate_context,
                distance=preparation.candidate_lap_distance,
                elapsed_time=candidate_elapsed,
            ),
            grid_step_m=request.grid_step_m,
        )
        report_request = ComparisonReportRequest(comparison=comparison)

        return PhysicalComparisonPreparationSuccess(
            report_request=report_request,
            dataset_fingerprint=preparation.dataset_fingerprint,
            reference_context=preparation.reference_context,
            candidate_context=preparation.candidate_context,
        )

    @classmethod
    def _readiness_issues(
        cls,
        request: PhysicalComparisonPreparationRequest,
    ) -> tuple[PhysicalComparisonPreparationIssue, ...]:
        preparation = request.preparation
        fingerprint = preparation.dataset_fingerprint
        issues: list[PhysicalComparisonPreparationIssue] = []

        if not fingerprint.strip():
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.EMPTY_DATASET_FINGERPRINT,
                    "Physical comparison preparation requires a dataset fingerprint.",
                )
            )

        if (
            preparation.reference_window.dataset_fingerprint != fingerprint
            or preparation.candidate_window.dataset_fingerprint != fingerprint
        ):
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.DATASET_FINGERPRINT_MISMATCH,
                    "Physical lap-window fingerprints must match the preparation dataset.",
                )
            )

        if (
            preparation.reference_context.dataset_fingerprint != fingerprint
            or preparation.candidate_context.dataset_fingerprint != fingerprint
        ):
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.CONTEXT_DATASET_MISMATCH,
                    "Reference and candidate context must match the preparation dataset.",
                )
            )

        if preparation.reference_context == preparation.candidate_context:
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.SAME_LAP_CONTEXT,
                    "Reference and candidate must identify different laps.",
                )
            )

        if (
            preparation.reference_lap_distance.evidence.dataset_fingerprint != fingerprint
            or preparation.candidate_lap_distance.evidence.dataset_fingerprint != fingerprint
        ):
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.DISTANCE_DATASET_MISMATCH,
                    "Canonical lap-distance evidence must match the preparation dataset.",
                )
            )

        if not math.isfinite(request.grid_step_m) or request.grid_step_m <= 0.0:
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.INVALID_GRID_STEP,
                    "Comparison grid step must be a positive finite number of metres.",
                )
            )

        issues.extend(
            cls._lap_time_issues(
                fingerprint=fingerprint,
                side="reference",
                timestamps_s=preparation.reference_lap.timestamps_s,
                time_evidence_fingerprint=(
                    preparation.reference_lap.time_evidence.dataset_fingerprint
                ),
                distance_length=len(preparation.reference_lap_distance.values),
            )
        )
        issues.extend(
            cls._lap_time_issues(
                fingerprint=fingerprint,
                side="candidate",
                timestamps_s=preparation.candidate_lap.timestamps_s,
                time_evidence_fingerprint=(
                    preparation.candidate_lap.time_evidence.dataset_fingerprint
                ),
                distance_length=len(preparation.candidate_lap_distance.values),
            )
        )

        return tuple(issues)

    @classmethod
    def _lap_time_issues(
        cls,
        *,
        fingerprint: str,
        side: str,
        timestamps_s: tuple[float, ...],
        time_evidence_fingerprint: str,
        distance_length: int,
    ) -> tuple[PhysicalComparisonPreparationIssue, ...]:
        issues: list[PhysicalComparisonPreparationIssue] = []

        if time_evidence_fingerprint != fingerprint:
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.DATASET_FINGERPRINT_MISMATCH,
                    f"{side.capitalize()} time evidence must match the preparation dataset.",
                )
            )

        if len(timestamps_s) != distance_length:
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.LENGTH_MISMATCH,
                    f"{side.capitalize()} distance/time series lengths must match.",
                )
            )

        if len(timestamps_s) < 2:
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.INVALID_TIME_EVIDENCE,
                    f"{side.capitalize()} elapsed-time evidence needs at least two samples.",
                )
            )
            return tuple(issues)

        if any(not math.isfinite(value) for value in timestamps_s):
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.INVALID_TIME_EVIDENCE,
                    f"{side.capitalize()} elapsed-time evidence must be finite.",
                )
            )
        elif not all(
            current > previous
            for previous, current in zip(timestamps_s, timestamps_s[1:], strict=False)
        ):
            issues.append(
                cls._issue(
                    PhysicalComparisonPreparationIssueCode.INVALID_TIME_EVIDENCE,
                    f"{side.capitalize()} elapsed-time evidence must be strictly increasing.",
                )
            )

        return tuple(issues)

    @staticmethod
    def _elapsed_series(
        fingerprint: str,
        timestamps_s: tuple[float, ...],
        source_evidence,
    ) -> LapComparisonSeries:
        start_s = timestamps_s[0]
        values = tuple(value - start_s for value in timestamps_s)
        transformation = TransformationEvidence(
            transformation_id=ELAPSED_TRANSFORMATION_ID,
            transformation_version=ELAPSED_TRANSFORMATION_VERSION,
            parameters={"source_start_s": start_s},
        )
        evidence = CanonicalSeriesEvidence(
            dataset_fingerprint=fingerprint,
            source_channel_identifier=source_evidence.source_channel_identifier,
            source_original_name=source_evidence.source_original_name,
            canonical_concept=CanonicalConcept.TIME_ELAPSED,
            unit="s",
            transformations=(*source_evidence.transformations, transformation),
        )
        return LapComparisonSeries(values=values, evidence=evidence)

    @staticmethod
    def _issue(
        code: PhysicalComparisonPreparationIssueCode,
        message: str,
    ) -> PhysicalComparisonPreparationIssue:
        return PhysicalComparisonPreparationIssue(code=code, message=message)
