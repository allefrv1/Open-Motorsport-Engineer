from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ome.analysis import ContinuousOverlaySeries, GearOverlaySeries
from ome.application.comparison_report import (
    ComparisonReportRequest,
    ContinuousChannelPair,
    GearChannelPair,
)
from ome.application.lap_window import SourceLapWindow
from ome.application.physical_comparison_preparation import PhysicalComparisonPreparationSuccess
from ome.application.physical_track_reference import PhysicalTrackReferencePreparation
from ome.domain import (
    CanonicalConcept,
    ImportedTelemetryDataset,
    NormalizationMapping,
    NormalizationResult,
    NormalizationRule,
)
from ome.evidence import CanonicalSeriesEvidence, TransformationEvidence
from ome.normalization import ConversionKind, TelemetryNormalizer
from ome.validation import TelemetryValidator

TRAQMATE_SOURCE_TYPE = "traqmate-trackvision-csv"
PREPARATION_ID = "ome.preparation.traqmate-supporting-lap-window"
PREPARATION_VERSION = "0.1.0"
BOUNDARY_ROLE = "shared_start_finish_evidence"
GEAR_SEMANTIC_ID = "transmission.gear.traqmate_derived_or_assigned"


class TraqmatePhysicalSupportingEvidenceIssueCode(StrEnum):
    UNSUPPORTED_SOURCE_TYPE = "unsupported_source_type"
    DATASET_FINGERPRINT_MISMATCH = "dataset_fingerprint_mismatch"
    BASE_CONTEXT_MISMATCH = "base_context_mismatch"
    WINDOW_OUT_OF_RANGE = "window_out_of_range"
    INVALID_SOURCE_TIME = "invalid_source_time"
    NORMALIZATION_NOT_READY = "normalization_not_ready"
    INVALID_SUPPORTING_VALUES = "invalid_supporting_values"


@dataclass(frozen=True, slots=True)
class TraqmatePhysicalSupportingEvidenceIssue:
    code: TraqmatePhysicalSupportingEvidenceIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class TraqmatePhysicalSupportingEvidenceRequest:
    dataset: ImportedTelemetryDataset
    physical_preparation: PhysicalTrackReferencePreparation
    base_preparation: PhysicalComparisonPreparationSuccess


@dataclass(frozen=True, slots=True)
class TraqmatePhysicalSupportingEvidenceSuccess:
    report_request: ComparisonReportRequest


@dataclass(frozen=True, slots=True)
class TraqmatePhysicalSupportingEvidenceNotReady:
    issues: tuple[TraqmatePhysicalSupportingEvidenceIssue, ...]


TraqmatePhysicalSupportingEvidenceOutcome = (
    TraqmatePhysicalSupportingEvidenceSuccess | TraqmatePhysicalSupportingEvidenceNotReady
)


def _rule(
    *,
    rule_id: str,
    source_channel_identifier: str,
    expected_unit: str | None,
    canonical_concept: CanonicalConcept,
    source_semantics: str,
    target_unit: str | None,
    conversion_kind: ConversionKind,
    semantic_id: str | None = None,
) -> NormalizationRule:
    return NormalizationRule(
        rule_id=rule_id,
        rule_version="0.1.0",
        source_type=TRAQMATE_SOURCE_TYPE,
        source_channel_identifier=source_channel_identifier,
        expected_original_name=source_channel_identifier,
        expected_unit=expected_unit,
        canonical_concept=canonical_concept,
        source_semantics=source_semantics,
        target_unit=target_unit,
        conversion_kind=conversion_kind,
        conversion_id=f"ome.conversion.{conversion_kind.value}",
        conversion_version="1.0.0",
        semantic_id=semantic_id,
    )


_TRAQMATE_PHYSICAL_RULES = (
    _rule(
        rule_id="ome.traqmate.vehicle-speed",
        source_channel_identifier="Velocity (MPH)",
        expected_unit="mph",
        canonical_concept=CanonicalConcept.VEHICLE_SPEED,
        source_semantics=(
            "Traqmate Trackvision exported vehicle velocity in miles per hour; "
            "the acquisition method is not further specialized."
        ),
        target_unit="m/s",
        conversion_kind=ConversionKind.MPH_TO_MPS,
    ),
    _rule(
        rule_id="ome.traqmate.engine-speed",
        source_channel_identifier="RPMs",
        expected_unit=None,
        canonical_concept=CanonicalConcept.ENGINE_SPEED,
        source_semantics=(
            "Traqmate Trackvision RPM source interpreted as engine rotational "
            "speed in revolutions per minute according to the accepted profile."
        ),
        target_unit="rad/s",
        conversion_kind=ConversionKind.RPM_TO_RAD_PER_SECOND,
    ),
    _rule(
        rule_id="ome.traqmate.gear",
        source_channel_identifier="Gear",
        expected_unit=None,
        canonical_concept=CanonicalConcept.TRANSMISSION_GEAR,
        source_semantics=(
            "Traqmate gear value whose source-system semantics may be derived or "
            "assigned rather than directly measured."
        ),
        target_unit=None,
        conversion_kind=ConversionKind.INTEGER_IDENTITY,
        semantic_id=GEAR_SEMANTIC_ID,
    ),
)


def traqmate_physical_normalization_rules() -> tuple[NormalizationRule, ...]:
    return _TRAQMATE_PHYSICAL_RULES


class TraqmatePhysicalSupportingEvidenceService:
    """Add only verified Traqmate supporting channels to a ready physical report request."""

    def prepare(
        self,
        request: TraqmatePhysicalSupportingEvidenceRequest,
    ) -> TraqmatePhysicalSupportingEvidenceOutcome:
        issues = self._request_issues(request)
        if issues:
            return TraqmatePhysicalSupportingEvidenceNotReady(issues=issues)

        dataset = request.dataset
        validation = TelemetryValidator().validate(dataset)
        normalization = TelemetryNormalizer(traqmate_physical_normalization_rules()).normalize(
            dataset, validation
        )

        speed_pair_or_issue = self._continuous_pair(
            dataset,
            normalization,
            request.physical_preparation.reference_window,
            request.physical_preparation.candidate_window,
            CanonicalConcept.VEHICLE_SPEED,
            "Velocity (MPH)",
        )
        rpm_pair_or_issue = self._continuous_pair(
            dataset,
            normalization,
            request.physical_preparation.reference_window,
            request.physical_preparation.candidate_window,
            CanonicalConcept.ENGINE_SPEED,
            "RPMs",
        )
        gear_pair_or_issue = self._gear_pair(
            dataset,
            normalization,
            request.physical_preparation.reference_window,
            request.physical_preparation.candidate_window,
        )

        supporting_issues = tuple(
            item
            for item in (
                speed_pair_or_issue
                if isinstance(speed_pair_or_issue, TraqmatePhysicalSupportingEvidenceIssue)
                else None,
                rpm_pair_or_issue
                if isinstance(rpm_pair_or_issue, TraqmatePhysicalSupportingEvidenceIssue)
                else None,
                gear_pair_or_issue
                if isinstance(gear_pair_or_issue, TraqmatePhysicalSupportingEvidenceIssue)
                else None,
            )
            if item is not None
        )
        if supporting_issues:
            return TraqmatePhysicalSupportingEvidenceNotReady(issues=supporting_issues)

        continuous_pairs = tuple(
            pair
            for pair in (speed_pair_or_issue, rpm_pair_or_issue)
            if isinstance(pair, ContinuousChannelPair)
        )
        gear_pair = gear_pair_or_issue if isinstance(gear_pair_or_issue, GearChannelPair) else None

        return TraqmatePhysicalSupportingEvidenceSuccess(
            report_request=ComparisonReportRequest(
                comparison=request.base_preparation.report_request.comparison,
                continuous_channels=continuous_pairs,
                gear=gear_pair,
            )
        )

    @classmethod
    def _request_issues(
        cls,
        request: TraqmatePhysicalSupportingEvidenceRequest,
    ) -> tuple[TraqmatePhysicalSupportingEvidenceIssue, ...]:
        dataset = request.dataset
        physical = request.physical_preparation
        base = request.base_preparation
        fingerprint = dataset.provenance.content_fingerprint
        issues: list[TraqmatePhysicalSupportingEvidenceIssue] = []

        if dataset.source.source_type != TRAQMATE_SOURCE_TYPE:
            issues.append(
                cls._issue(
                    TraqmatePhysicalSupportingEvidenceIssueCode.UNSUPPORTED_SOURCE_TYPE,
                    "Traqmate physical supporting evidence requires Trackvision CSV data.",
                )
            )

        if (
            physical.dataset_fingerprint != fingerprint
            or base.dataset_fingerprint != fingerprint
            or physical.reference_window.dataset_fingerprint != fingerprint
            or physical.candidate_window.dataset_fingerprint != fingerprint
        ):
            issues.append(
                cls._issue(
                    TraqmatePhysicalSupportingEvidenceIssueCode.DATASET_FINGERPRINT_MISMATCH,
                    (
                        "Dataset, physical preparation and base preparation "
                        "must share one fingerprint."
                    ),
                )
            )

        comparison = base.report_request.comparison
        if (
            base.reference_context != physical.reference_context
            or base.candidate_context != physical.candidate_context
            or comparison.lap_a.context != physical.reference_context
            or comparison.lap_b.context != physical.candidate_context
        ):
            issues.append(
                cls._issue(
                    TraqmatePhysicalSupportingEvidenceIssueCode.BASE_CONTEXT_MISMATCH,
                    "Base comparison contexts must match the physical preparation contexts.",
                )
            )

        source_length = cls._source_length(dataset)
        if source_length is None or any(
            not cls._window_is_in_range(window, source_length)
            for window in (physical.reference_window, physical.candidate_window)
        ):
            issues.append(
                cls._issue(
                    TraqmatePhysicalSupportingEvidenceIssueCode.WINDOW_OUT_OF_RANGE,
                    "Supporting source window or closing boundary lies outside source evidence.",
                )
            )

        return tuple(issues)

    @staticmethod
    def _source_length(dataset: ImportedTelemetryDataset) -> int | None:
        try:
            time_channel = dataset.channel("Elapsed Time")
        except KeyError:
            return None
        source_length = len(time_channel.series.values)
        if any(len(channel.series.values) != source_length for channel in dataset.channels):
            return None
        return source_length

    @staticmethod
    def _window_is_in_range(window: SourceLapWindow, source_length: int) -> bool:
        return (
            0 <= window.start_index < window.end_index_exclusive
            and window.end_index_exclusive == window.closing_boundary_index
            and window.closing_boundary_index < source_length
            and window.sample_count == window.end_index_exclusive - window.start_index
        )

    def _continuous_pair(
        self,
        dataset: ImportedTelemetryDataset,
        normalization: NormalizationResult,
        reference_window: SourceLapWindow,
        candidate_window: SourceLapWindow,
        concept: CanonicalConcept,
        source_identifier: str,
    ) -> ContinuousChannelPair | TraqmatePhysicalSupportingEvidenceIssue | None:
        if not self._has_source_channel(dataset, source_identifier):
            return None

        mapping = self._single_mapping(normalization, concept, source_identifier)
        if isinstance(mapping, TraqmatePhysicalSupportingEvidenceIssue):
            return mapping

        lap_a = self._continuous_series(dataset, mapping, reference_window)
        if isinstance(lap_a, TraqmatePhysicalSupportingEvidenceIssue):
            return lap_a
        lap_b = self._continuous_series(dataset, mapping, candidate_window)
        if isinstance(lap_b, TraqmatePhysicalSupportingEvidenceIssue):
            return lap_b

        return ContinuousChannelPair(
            canonical_concept=concept,
            lap_a_channel=lap_a,
            lap_b_channel=lap_b,
        )

    def _gear_pair(
        self,
        dataset: ImportedTelemetryDataset,
        normalization: NormalizationResult,
        reference_window: SourceLapWindow,
        candidate_window: SourceLapWindow,
    ) -> GearChannelPair | TraqmatePhysicalSupportingEvidenceIssue | None:
        if not self._has_source_channel(dataset, "Gear"):
            return None

        mapping = self._single_mapping(
            normalization,
            CanonicalConcept.TRANSMISSION_GEAR,
            "Gear",
        )
        if isinstance(mapping, TraqmatePhysicalSupportingEvidenceIssue):
            return mapping

        lap_a = self._gear_series(dataset, mapping, reference_window)
        if isinstance(lap_a, TraqmatePhysicalSupportingEvidenceIssue):
            return lap_a
        lap_b = self._gear_series(dataset, mapping, candidate_window)
        if isinstance(lap_b, TraqmatePhysicalSupportingEvidenceIssue):
            return lap_b

        return GearChannelPair(lap_a_gear=lap_a, lap_b_gear=lap_b)

    @classmethod
    def _single_mapping(
        cls,
        normalization: NormalizationResult,
        concept: CanonicalConcept,
        source_identifier: str,
    ) -> NormalizationMapping | TraqmatePhysicalSupportingEvidenceIssue:
        mappings = normalization.mappings_for(concept)
        exact = tuple(
            mapping
            for mapping in mappings
            if mapping.source_channel_identifier == source_identifier
        )
        if len(exact) != 1:
            return cls._issue(
                TraqmatePhysicalSupportingEvidenceIssueCode.NORMALIZATION_NOT_READY,
                f"Expected exactly one normalized mapping for {source_identifier!r}.",
            )
        return exact[0]

    def _continuous_series(
        self,
        dataset: ImportedTelemetryDataset,
        mapping: NormalizationMapping,
        window: SourceLapWindow,
    ) -> ContinuousOverlaySeries | TraqmatePhysicalSupportingEvidenceIssue:
        timestamps = self._relative_timestamps(dataset, window)
        if isinstance(timestamps, TraqmatePhysicalSupportingEvidenceIssue):
            return timestamps

        values = self._window_numeric_values(mapping, window)
        if values is None:
            return self._issue(
                TraqmatePhysicalSupportingEvidenceIssueCode.INVALID_SUPPORTING_VALUES,
                f"{mapping.source_channel_identifier!r} contains invalid numeric evidence.",
            )

        return ContinuousOverlaySeries(
            timestamps_s=timestamps,
            values=values,
            evidence=self._mapping_evidence(mapping, window),
        )

    def _gear_series(
        self,
        dataset: ImportedTelemetryDataset,
        mapping: NormalizationMapping,
        window: SourceLapWindow,
    ) -> GearOverlaySeries | TraqmatePhysicalSupportingEvidenceIssue:
        timestamps = self._relative_timestamps(dataset, window)
        if isinstance(timestamps, TraqmatePhysicalSupportingEvidenceIssue):
            return timestamps

        indexes = self._window_indexes(window)
        try:
            values = tuple(mapping.series.values[index] for index in indexes)
        except IndexError:
            return self._issue(
                TraqmatePhysicalSupportingEvidenceIssueCode.WINDOW_OUT_OF_RANGE,
                "Gear supporting window lies outside normalized source evidence.",
            )

        if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
            return self._issue(
                TraqmatePhysicalSupportingEvidenceIssueCode.INVALID_SUPPORTING_VALUES,
                "Canonical Traqmate gear evidence must contain integer values.",
            )

        return GearOverlaySeries(
            timestamps_s=timestamps,
            values=values,
            evidence=self._mapping_evidence(mapping, window),
        )

    @classmethod
    def _relative_timestamps(
        cls,
        dataset: ImportedTelemetryDataset,
        window: SourceLapWindow,
    ) -> tuple[float, ...] | TraqmatePhysicalSupportingEvidenceIssue:
        try:
            source = dataset.channel("Elapsed Time")
        except KeyError:
            return cls._issue(
                TraqmatePhysicalSupportingEvidenceIssueCode.INVALID_SOURCE_TIME,
                "Traqmate Elapsed Time source evidence is missing.",
            )

        indexes = cls._window_indexes(window)
        values: list[float] = []
        for index in indexes:
            try:
                raw = source.series.values[index]
            except IndexError:
                return cls._issue(
                    TraqmatePhysicalSupportingEvidenceIssueCode.WINDOW_OUT_OF_RANGE,
                    "Supporting time window lies outside source evidence.",
                )
            number = cls._finite_number(raw)
            if number is None:
                return cls._issue(
                    TraqmatePhysicalSupportingEvidenceIssueCode.INVALID_SOURCE_TIME,
                    "Supporting Elapsed Time values must be finite numeric source evidence.",
                )
            values.append(number - window.start_elapsed_s)

        timestamps = tuple(values)
        if not timestamps or timestamps[0] != 0.0:
            return cls._issue(
                TraqmatePhysicalSupportingEvidenceIssueCode.INVALID_SOURCE_TIME,
                "Supporting timestamps must begin at zero.",
            )
        if not all(
            current > previous
            for previous, current in zip(timestamps, timestamps[1:], strict=False)
        ):
            return cls._issue(
                TraqmatePhysicalSupportingEvidenceIssueCode.INVALID_SOURCE_TIME,
                "Supporting timestamps must be strictly increasing.",
            )
        return timestamps

    @classmethod
    def _window_numeric_values(
        cls,
        mapping: NormalizationMapping,
        window: SourceLapWindow,
    ) -> tuple[float, ...] | None:
        values: list[float] = []
        for index in cls._window_indexes(window):
            try:
                raw = mapping.series.values[index]
            except IndexError:
                return None
            if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                return None
            number = float(raw)
            if not math.isfinite(number):
                return None
            values.append(number)
        return tuple(values)

    @staticmethod
    def _window_indexes(window: SourceLapWindow) -> tuple[int, ...]:
        return tuple(range(window.start_index, window.end_index_exclusive)) + (
            window.closing_boundary_index,
        )

    @staticmethod
    def _has_source_channel(
        dataset: ImportedTelemetryDataset,
        identifier: str,
    ) -> bool:
        try:
            dataset.channel(identifier)
        except KeyError:
            return False
        return True

    @staticmethod
    def _finite_number(value: object) -> float | None:
        if value is None or isinstance(value, (bool, tuple)):
            return None
        if isinstance(value, (int, float)):
            number = float(value)
        elif isinstance(value, str):
            try:
                number = float(value.strip())
            except ValueError:
                return None
        else:
            return None
        return number if math.isfinite(number) else None

    @staticmethod
    def _mapping_evidence(
        mapping: NormalizationMapping,
        window: SourceLapWindow,
    ) -> CanonicalSeriesEvidence:
        unit = mapping.target_unit
        if unit is None:
            unit = mapping.source_unit or ""

        normalization = TransformationEvidence(
            transformation_id=mapping.conversion_id,
            transformation_version=mapping.conversion_version,
            parameters={
                "normalization_rule_id": mapping.rule_id,
                "normalization_rule_version": mapping.rule_version,
                "source_semantics": mapping.source_semantics,
            },
        )
        window_preparation = TransformationEvidence(
            transformation_id=PREPARATION_ID,
            transformation_version=PREPARATION_VERSION,
            parameters={
                "source_window_start_index": window.start_index,
                "source_window_end_index_exclusive": window.end_index_exclusive,
                "closing_boundary_source_index": window.closing_boundary_index,
                "closing_boundary_role": BOUNDARY_ROLE,
                "source_start_s": window.start_elapsed_s,
            },
        )
        return CanonicalSeriesEvidence(
            dataset_fingerprint=window.dataset_fingerprint,
            source_channel_identifier=mapping.source_channel_identifier,
            source_original_name=mapping.source_original_name,
            canonical_concept=mapping.canonical_concept,
            unit=unit,
            semantic_id=mapping.semantic_id,
            transformations=(normalization, window_preparation),
        )

    @staticmethod
    def _issue(
        code: TraqmatePhysicalSupportingEvidenceIssueCode,
        message: str,
    ) -> TraqmatePhysicalSupportingEvidenceIssue:
        return TraqmatePhysicalSupportingEvidenceIssue(code=code, message=message)
