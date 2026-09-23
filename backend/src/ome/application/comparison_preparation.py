from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from ome.analysis import (
    ContinuousOverlaySeries,
    GearOverlaySeries,
    LapComparisonLap,
    LapComparisonRequest,
    LapComparisonSeries,
)
from ome.application.comparison_report import (
    ComparisonReportRequest,
    ContinuousChannelPair,
    GearChannelPair,
)
from ome.application.context import ContextOrganizer
from ome.domain import (
    CanonicalConcept,
    ContextEvidence,
    ContextMarker,
    ImportedTelemetryDataset,
    NormalizationMapping,
    NormalizationResult,
    NormalizationRule,
    ValidationResult,
    ValidationSeverity,
)
from ome.evidence import CanonicalSeriesEvidence, LapEvidenceContext, TransformationEvidence
from ome.normalization import ConversionKind, TelemetryNormalizer
from ome.validation import TelemetryValidator

TIME_TRANSFORMATION_ID = "ome.preparation.ome-csv-time-axis"
TIME_TRANSFORMATION_VERSION = "0.1.0"

CONTINUOUS_CONCEPTS = (
    CanonicalConcept.VEHICLE_SPEED,
    CanonicalConcept.DRIVER_THROTTLE,
    CanonicalConcept.DRIVER_BRAKE,
    CanonicalConcept.DRIVER_STEERING,
    CanonicalConcept.ENGINE_SPEED,
)


class ComparisonPreparationIssueCode(StrEnum):
    INVALID_PROFILE = "invalid_profile"
    UNSUPPORTED_SOURCE_TYPE = "unsupported_source_type"
    BLOCKING_VALIDATION = "blocking_validation"
    MISSING_CONTEXT = "missing_context"
    INVALID_CONTEXT = "invalid_context"
    MISSING_TIME_EVIDENCE = "missing_time_evidence"
    INCONSISTENT_TIME_AXIS = "inconsistent_time_axis"
    MISSING_LAP_DISTANCE = "missing_lap_distance"
    AMBIGUOUS_LAP_DISTANCE = "ambiguous_lap_distance"
    INVALID_CANONICAL_VALUES = "invalid_canonical_values"


@dataclass(frozen=True, slots=True)
class ComparisonPreparationIssue:
    code: ComparisonPreparationIssueCode
    message: str
    lap_side: str | None = None
    canonical_concept: CanonicalConcept | None = None


@dataclass(frozen=True, slots=True)
class ComparisonPreparationProfile:
    profile_id: str
    profile_version: str
    source_type: str
    normalization_rules: tuple[NormalizationRule, ...]
    time_axis_identifier: str
    time_axis_original_name: str
    time_axis_unit: str
    time_axis_semantics: str
    context_metadata_key: str
    session_field: str
    run_field: str
    lap_field: str
    lap_number_field: str


@dataclass(frozen=True, slots=True)
class ComparisonPreparationRequest:
    lap_a: ImportedTelemetryDataset
    lap_b: ImportedTelemetryDataset
    profile: ComparisonPreparationProfile
    grid_step_m: float = 1.0


@dataclass(frozen=True, slots=True)
class ComparisonPreparationNotReady:
    issues: tuple[ComparisonPreparationIssue, ...]


@dataclass(frozen=True, slots=True)
class ComparisonPreparationSuccess:
    report_request: ComparisonReportRequest
    profile_id: str
    profile_version: str
    lap_a_validation: ValidationResult
    lap_b_validation: ValidationResult
    lap_a_normalization: NormalizationResult
    lap_b_normalization: NormalizationResult


ComparisonPreparationOutcome = ComparisonPreparationSuccess | ComparisonPreparationNotReady


def _rule(
    *,
    rule_id: str,
    source_channel_identifier: str,
    expected_original_name: str,
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
        source_type="ome-csv-profile",
        source_channel_identifier=source_channel_identifier,
        expected_original_name=expected_original_name,
        expected_unit=expected_unit,
        canonical_concept=canonical_concept,
        source_semantics=source_semantics,
        target_unit=target_unit,
        conversion_kind=conversion_kind,
        conversion_id=f"ome.conversion.{conversion_kind.value}",
        conversion_version="1.0.0",
        semantic_id=semantic_id,
    )


_MVP_OME_CSV_PROFILE = ComparisonPreparationProfile(
    profile_id="ome.mvp-comparison.ome-csv",
    profile_version="0.1.0",
    source_type="ome-csv-profile",
    normalization_rules=(
        _rule(
            rule_id="ome.mvp-comparison.lap-distance",
            source_channel_identifier="lap_distance_src",
            expected_original_name="Synthetic Lap Distance",
            expected_unit="m",
            canonical_concept=CanonicalConcept.LAP_DISTANCE,
            source_semantics="Synthetic monotonic lap distance supplied directly in metres.",
            target_unit="m",
            conversion_kind=ConversionKind.NUMERIC_IDENTITY,
        ),
        _rule(
            rule_id="ome.mvp-comparison.vehicle-speed",
            source_channel_identifier="speed_src",
            expected_original_name="Synthetic Vehicle Speed",
            expected_unit="m/s",
            canonical_concept=CanonicalConcept.VEHICLE_SPEED,
            source_semantics="Synthetic vehicle speed supplied directly in metres per second.",
            target_unit="m/s",
            conversion_kind=ConversionKind.NUMERIC_IDENTITY,
        ),
        _rule(
            rule_id="ome.mvp-comparison.throttle",
            source_channel_identifier="throttle_src",
            expected_original_name="Synthetic Throttle Position",
            expected_unit="%",
            canonical_concept=CanonicalConcept.DRIVER_THROTTLE,
            source_semantics="Synthetic driver throttle position expressed as percent.",
            target_unit="1",
            conversion_kind=ConversionKind.PERCENT_TO_FRACTION,
        ),
        _rule(
            rule_id="ome.mvp-comparison.brake",
            source_channel_identifier="brake_src",
            expected_original_name="Synthetic Brake Pedal Position",
            expected_unit="%",
            canonical_concept=CanonicalConcept.DRIVER_BRAKE,
            source_semantics="Synthetic brake pedal position expressed as percent.",
            target_unit="1",
            conversion_kind=ConversionKind.PERCENT_TO_FRACTION,
            semantic_id="driver.brake.pedal_position_ratio",
        ),
        _rule(
            rule_id="ome.mvp-comparison.steering",
            source_channel_identifier="steering_src",
            expected_original_name="Synthetic Steering Angle",
            expected_unit="rad",
            canonical_concept=CanonicalConcept.DRIVER_STEERING,
            source_semantics="Synthetic signed steering-wheel angle in radians.",
            target_unit="rad",
            conversion_kind=ConversionKind.NUMERIC_IDENTITY,
        ),
        _rule(
            rule_id="ome.mvp-comparison.engine-speed",
            source_channel_identifier="rpm_src",
            expected_original_name="Synthetic Engine Speed",
            expected_unit="rpm",
            canonical_concept=CanonicalConcept.ENGINE_SPEED,
            source_semantics="Synthetic engine rotational speed in revolutions per minute.",
            target_unit="rad/s",
            conversion_kind=ConversionKind.RPM_TO_RAD_PER_SECOND,
        ),
        _rule(
            rule_id="ome.mvp-comparison.gear",
            source_channel_identifier="gear_src",
            expected_original_name="Synthetic Gear",
            expected_unit="",
            canonical_concept=CanonicalConcept.TRANSMISSION_GEAR,
            source_semantics="Synthetic engaged forward gear number.",
            target_unit=None,
            conversion_kind=ConversionKind.INTEGER_IDENTITY,
        ),
    ),
    time_axis_identifier="time_s",
    time_axis_original_name="time_s",
    time_axis_unit="s",
    time_axis_semantics="elapsed_time_from_lap_reference",
    context_metadata_key="context",
    session_field="session",
    run_field="run",
    lap_field="lap",
    lap_number_field="lap_number",
)


def mvp_ome_csv_comparison_profile() -> ComparisonPreparationProfile:
    return _MVP_OME_CSV_PROFILE


class ComparisonPreparationService:
    def __init__(self) -> None:
        self._validator = TelemetryValidator()
        self._context_organizer = ContextOrganizer()

    def prepare(self, request: ComparisonPreparationRequest) -> ComparisonPreparationOutcome:
        profile_issues = self._profile_issues(request.profile)
        source_issues = self._source_issues(request)
        if profile_issues or source_issues:
            return ComparisonPreparationNotReady(issues=(*profile_issues, *source_issues))

        validation_a = self._validator.validate(request.lap_a)
        validation_b = self._validator.validate(request.lap_b)
        validation_issues = (
            *self._blocking_validation_issues(validation_a, "a"),
            *self._blocking_validation_issues(validation_b, "b"),
        )
        if validation_issues:
            return ComparisonPreparationNotReady(issues=validation_issues)

        normalizer = TelemetryNormalizer(request.profile.normalization_rules)
        normalization_a = normalizer.normalize(request.lap_a, validation_a)
        normalization_b = normalizer.normalize(request.lap_b, validation_b)

        context_a, context_issue_a = self._context(request.lap_a, request.profile, "a")
        context_b, context_issue_b = self._context(request.lap_b, request.profile, "b")

        distance_a, distance_issue_a = self._distance_series(
            normalization_a,
            request.profile,
            "a",
        )
        distance_b, distance_issue_b = self._distance_series(
            normalization_b,
            request.profile,
            "b",
        )
        time_a, time_issue_a = self._time_series(request.lap_a, request.profile, "a")
        time_b, time_issue_b = self._time_series(request.lap_b, request.profile, "b")

        readiness_issues = tuple(
            issue
            for issue in (
                context_issue_a,
                context_issue_b,
                distance_issue_a,
                distance_issue_b,
                time_issue_a,
                time_issue_b,
            )
            if issue is not None
        )
        if readiness_issues:
            return ComparisonPreparationNotReady(issues=readiness_issues)

        assert context_a is not None
        assert context_b is not None
        assert distance_a is not None
        assert distance_b is not None
        assert time_a is not None
        assert time_b is not None

        optional_issue = self._optional_ambiguity_issue(normalization_a, normalization_b)
        if optional_issue is not None:
            return ComparisonPreparationNotReady(issues=(optional_issue,))

        continuous_pairs = tuple(
            ContinuousChannelPair(
                canonical_concept=concept,
                lap_a_channel=self._continuous_series(
                    normalization_a,
                    concept,
                    request.profile,
                ),
                lap_b_channel=self._continuous_series(
                    normalization_b,
                    concept,
                    request.profile,
                ),
            )
            for concept in CONTINUOUS_CONCEPTS
        )

        gear_pair = GearChannelPair(
            lap_a_gear=self._gear_series(normalization_a, request.profile),
            lap_b_gear=self._gear_series(normalization_b, request.profile),
        )

        report_request = ComparisonReportRequest(
            comparison=LapComparisonRequest(
                lap_a=LapComparisonLap(
                    context=context_a,
                    distance=distance_a,
                    elapsed_time=time_a,
                ),
                lap_b=LapComparisonLap(
                    context=context_b,
                    distance=distance_b,
                    elapsed_time=time_b,
                ),
                grid_step_m=request.grid_step_m,
            ),
            continuous_channels=continuous_pairs,
            gear=gear_pair,
        )

        return ComparisonPreparationSuccess(
            report_request=report_request,
            profile_id=request.profile.profile_id,
            profile_version=request.profile.profile_version,
            lap_a_validation=validation_a,
            lap_b_validation=validation_b,
            lap_a_normalization=normalization_a,
            lap_b_normalization=normalization_b,
        )

    @staticmethod
    def _profile_issues(
        profile: ComparisonPreparationProfile,
    ) -> tuple[ComparisonPreparationIssue, ...]:
        if not profile.profile_id.strip() or not profile.profile_version.strip():
            return (
                ComparisonPreparationIssue(
                    code=ComparisonPreparationIssueCode.INVALID_PROFILE,
                    message="Preparation profile id/version must be non-empty.",
                ),
            )
        if not profile.normalization_rules:
            return (
                ComparisonPreparationIssue(
                    code=ComparisonPreparationIssueCode.INVALID_PROFILE,
                    message="Preparation profile must declare explicit normalization rules.",
                ),
            )
        if any(rule.source_type != profile.source_type for rule in profile.normalization_rules):
            return (
                ComparisonPreparationIssue(
                    code=ComparisonPreparationIssueCode.INVALID_PROFILE,
                    message="Every normalization rule must match the profile source type.",
                ),
            )

        rule_ids = tuple(rule.rule_id for rule in profile.normalization_rules)
        if len(set(rule_ids)) != len(rule_ids):
            return (
                ComparisonPreparationIssue(
                    code=ComparisonPreparationIssueCode.INVALID_PROFILE,
                    message="Preparation profile normalization rule ids must be unique.",
                ),
            )

        concepts = tuple(rule.canonical_concept for rule in profile.normalization_rules)
        if len(set(concepts)) != len(concepts):
            return (
                ComparisonPreparationIssue(
                    code=ComparisonPreparationIssueCode.INVALID_PROFILE,
                    message="Plan 016 preparation profile allows one rule per canonical concept.",
                ),
            )
        return ()

    @staticmethod
    def _source_issues(
        request: ComparisonPreparationRequest,
    ) -> tuple[ComparisonPreparationIssue, ...]:
        issues: list[ComparisonPreparationIssue] = []
        for side, dataset in (("a", request.lap_a), ("b", request.lap_b)):
            if dataset.source.source_type != request.profile.source_type:
                issues.append(
                    ComparisonPreparationIssue(
                        code=ComparisonPreparationIssueCode.UNSUPPORTED_SOURCE_TYPE,
                        message=(
                            f"Lap {side.upper()} source type {dataset.source.source_type!r} "
                            f"does not match preparation profile {request.profile.source_type!r}."
                        ),
                        lap_side=side,
                    )
                )
        return tuple(issues)

    @staticmethod
    def _blocking_validation_issues(
        validation: ValidationResult,
        side: str,
    ) -> tuple[ComparisonPreparationIssue, ...]:
        blocking = tuple(
            issue for issue in validation.issues if issue.severity is ValidationSeverity.BLOCKING
        )
        if not blocking:
            return ()
        codes = ", ".join(sorted({issue.code for issue in blocking}))
        return (
            ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.BLOCKING_VALIDATION,
                message=f"Lap {side.upper()} has blocking validation evidence: {codes}.",
                lap_side=side,
            ),
        )

    def _context(
        self,
        dataset: ImportedTelemetryDataset,
        profile: ComparisonPreparationProfile,
        side: str,
    ) -> tuple[LapEvidenceContext | None, ComparisonPreparationIssue | None]:
        raw_context = dataset.source.metadata.get(profile.context_metadata_key)
        if not isinstance(raw_context, Mapping):
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.MISSING_CONTEXT,
                message=f"Lap {side.upper()} has no explicit source context metadata.",
                lap_side=side,
            )

        session_value = self._marker_value(raw_context.get(profile.session_field))
        lap_value = self._marker_value(raw_context.get(profile.lap_field))
        run_raw = raw_context.get(profile.run_field)
        run_value = None if run_raw is None else self._marker_value(run_raw)

        if session_value is None or lap_value is None or (
            run_raw is not None and run_value is None
        ):
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.INVALID_CONTEXT,
                message=(
                    f"Lap {side.upper()} context must contain valid explicit "
                    "Session/Lap markers and a valid Run marker when supplied."
                ),
                lap_side=side,
            )

        lap_number_raw = raw_context.get(profile.lap_number_field)
        if lap_number_raw is None:
            lap_number: int | None = None
        elif isinstance(lap_number_raw, int) and not isinstance(lap_number_raw, bool):
            lap_number = lap_number_raw
        else:
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.INVALID_CONTEXT,
                message=f"Lap {side.upper()} lap_number must be an integer when supplied.",
                lap_side=side,
            )

        organized = self._context_organizer.organize(
            ContextEvidence(
                dataset_fingerprint=dataset.provenance.content_fingerprint,
                source_identity=dataset.source.original_name,
                session_marker=ContextMarker(
                    value=session_value,
                    source_field=(
                        f"{profile.context_metadata_key}.{profile.session_field}"
                    ),
                ),
                run_marker=(
                    None
                    if run_value is None
                    else ContextMarker(
                        value=run_value,
                        source_field=f"{profile.context_metadata_key}.{profile.run_field}",
                    )
                ),
                lap_marker=ContextMarker(
                    value=lap_value,
                    source_field=f"{profile.context_metadata_key}.{profile.lap_field}",
                ),
                lap_number=lap_number,
            )
        )
        if organized is None:
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.INVALID_CONTEXT,
                message=f"Lap {side.upper()} context could not be organized.",
                lap_side=side,
            )

        if organized.runs:
            run = organized.runs[0]
            if len(run.laps) != 1:
                return None, self._invalid_context_shape(side)
            lap = run.laps[0]
            run_identifier: str | None = run.identifier
        else:
            if len(organized.laps_without_run) != 1:
                return None, self._invalid_context_shape(side)
            lap = organized.laps_without_run[0]
            run_identifier = None

        return (
            LapEvidenceContext(
                dataset_fingerprint=dataset.provenance.content_fingerprint,
                session_identifier=organized.identifier,
                run_identifier=run_identifier,
                lap_identifier=lap.identifier,
            ),
            None,
        )

    @staticmethod
    def _invalid_context_shape(side: str) -> ComparisonPreparationIssue:
        return ComparisonPreparationIssue(
            code=ComparisonPreparationIssueCode.INVALID_CONTEXT,
            message=f"Lap {side.upper()} context is not a single explicit lap.",
            lap_side=side,
        )

    @staticmethod
    def _marker_value(value: object) -> str | int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.strip():
            return value
        return None

    def _distance_series(
        self,
        normalization: NormalizationResult,
        profile: ComparisonPreparationProfile,
        side: str,
    ) -> tuple[LapComparisonSeries | None, ComparisonPreparationIssue | None]:
        mappings = normalization.mappings_for(CanonicalConcept.LAP_DISTANCE)
        if not mappings:
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.MISSING_LAP_DISTANCE,
                message=f"Lap {side.upper()} has no prepared lap.distance evidence.",
                lap_side=side,
                canonical_concept=CanonicalConcept.LAP_DISTANCE,
            )
        if len(mappings) != 1:
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.AMBIGUOUS_LAP_DISTANCE,
                message=f"Lap {side.upper()} has ambiguous lap.distance evidence.",
                lap_side=side,
                canonical_concept=CanonicalConcept.LAP_DISTANCE,
            )

        values = self._numeric_values(mappings[0])
        if values is None:
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.INVALID_CANONICAL_VALUES,
                message=f"Lap {side.upper()} lap.distance contains invalid numeric evidence.",
                lap_side=side,
                canonical_concept=CanonicalConcept.LAP_DISTANCE,
            )

        return (
            LapComparisonSeries(
                values=values,
                evidence=self._mapping_evidence(mappings[0], normalization, profile),
            ),
            None,
        )

    def _time_series(
        self,
        dataset: ImportedTelemetryDataset,
        profile: ComparisonPreparationProfile,
        side: str,
    ) -> tuple[LapComparisonSeries | None, ComparisonPreparationIssue | None]:
        if not dataset.channels:
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.MISSING_TIME_EVIDENCE,
                message=f"Lap {side.upper()} has no source series carrying the shared time axis.",
                lap_side=side,
                canonical_concept=CanonicalConcept.TIME_ELAPSED,
            )

        timestamps = dataset.channels[0].series.timestamps_s
        if any(channel.series.timestamps_s != timestamps for channel in dataset.channels[1:]):
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.INCONSISTENT_TIME_AXIS,
                message=f"Lap {side.upper()} source channels do not share one time axis.",
                lap_side=side,
                canonical_concept=CanonicalConcept.TIME_ELAPSED,
            )

        source_provenance = dataset.source.metadata.get("source_provenance")
        time_axis = (
            source_provenance.get("time_axis")
            if isinstance(source_provenance, Mapping)
            else None
        )
        if not isinstance(time_axis, Mapping) or (
            time_axis.get("field") != profile.time_axis_identifier
            or time_axis.get("semantics") != profile.time_axis_semantics
            or time_axis.get("unit") != profile.time_axis_unit
        ):
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.MISSING_TIME_EVIDENCE,
                message=(
                    f"Lap {side.upper()} does not declare the controlled source time-axis "
                    "evidence required by the preparation profile."
                ),
                lap_side=side,
                canonical_concept=CanonicalConcept.TIME_ELAPSED,
            )

        if not timestamps or any(not math.isfinite(value) for value in timestamps):
            return None, ComparisonPreparationIssue(
                code=ComparisonPreparationIssueCode.INVALID_CANONICAL_VALUES,
                message=f"Lap {side.upper()} time axis contains invalid values.",
                lap_side=side,
                canonical_concept=CanonicalConcept.TIME_ELAPSED,
            )

        evidence = CanonicalSeriesEvidence(
            dataset_fingerprint=dataset.provenance.content_fingerprint,
            source_channel_identifier=profile.time_axis_identifier,
            source_original_name=profile.time_axis_original_name,
            canonical_concept=CanonicalConcept.TIME_ELAPSED,
            unit=profile.time_axis_unit,
            transformations=(
                TransformationEvidence(
                    transformation_id=TIME_TRANSFORMATION_ID,
                    transformation_version=TIME_TRANSFORMATION_VERSION,
                    parameters={
                        "preparation_profile_id": profile.profile_id,
                        "preparation_profile_version": profile.profile_version,
                        "source_contract": "ome-csv-profile/0.1",
                        "source_field": profile.time_axis_identifier,
                        "source_semantics": profile.time_axis_semantics,
                    },
                ),
            ),
        )
        return LapComparisonSeries(values=timestamps, evidence=evidence), None

    @staticmethod
    def _optional_ambiguity_issue(
        normalization_a: NormalizationResult,
        normalization_b: NormalizationResult,
    ) -> ComparisonPreparationIssue | None:
        for concept in (*CONTINUOUS_CONCEPTS, CanonicalConcept.TRANSMISSION_GEAR):
            if len(normalization_a.mappings_for(concept)) > 1 or len(
                normalization_b.mappings_for(concept)
            ) > 1:
                return ComparisonPreparationIssue(
                    code=ComparisonPreparationIssueCode.INVALID_PROFILE,
                    message=f"Optional concept {concept.value} has ambiguous prepared evidence.",
                    canonical_concept=concept,
                )
        return None

    def _continuous_series(
        self,
        normalization: NormalizationResult,
        concept: CanonicalConcept,
        profile: ComparisonPreparationProfile,
    ) -> ContinuousOverlaySeries | None:
        mappings = normalization.mappings_for(concept)
        if len(mappings) != 1:
            return None

        values = self._numeric_values(mappings[0])
        if values is None:
            return None

        return ContinuousOverlaySeries(
            timestamps_s=mappings[0].series.timestamps_s,
            values=values,
            evidence=self._mapping_evidence(mappings[0], normalization, profile),
        )

    def _gear_series(
        self,
        normalization: NormalizationResult,
        profile: ComparisonPreparationProfile,
    ) -> GearOverlaySeries | None:
        mappings = normalization.mappings_for(CanonicalConcept.TRANSMISSION_GEAR)
        if len(mappings) != 1:
            return None

        mapping = mappings[0]
        return GearOverlaySeries(
            timestamps_s=mapping.series.timestamps_s,
            values=mapping.series.values,
            evidence=self._mapping_evidence(mapping, normalization, profile),
        )

    @staticmethod
    def _numeric_values(mapping: NormalizationMapping) -> tuple[float, ...] | None:
        result: list[float] = []
        for value in mapping.series.values:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return None
            numeric = float(value)
            if not math.isfinite(numeric):
                return None
            result.append(numeric)
        return tuple(result)

    @staticmethod
    def _mapping_evidence(
        mapping: NormalizationMapping,
        normalization: NormalizationResult,
        profile: ComparisonPreparationProfile,
    ) -> CanonicalSeriesEvidence:
        unit = mapping.target_unit
        if unit is None:
            unit = mapping.source_unit or ""

        return CanonicalSeriesEvidence(
            dataset_fingerprint=normalization.dataset_fingerprint,
            source_channel_identifier=mapping.source_channel_identifier,
            source_original_name=mapping.source_original_name,
            canonical_concept=mapping.canonical_concept,
            unit=unit,
            semantic_id=mapping.semantic_id,
            transformations=(
                TransformationEvidence(
                    transformation_id=mapping.conversion_id,
                    transformation_version=mapping.conversion_version,
                    parameters={
                        "normalization_rule_id": mapping.rule_id,
                        "normalization_rule_version": mapping.rule_version,
                        "normalizer_id": normalization.normalizer_id,
                        "normalizer_version": normalization.normalizer_version,
                        "preparation_profile_id": profile.profile_id,
                        "preparation_profile_version": profile.profile_version,
                        "source_semantics": mapping.source_semantics,
                    },
                ),
            ),
        )
