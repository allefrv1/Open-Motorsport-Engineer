from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum

from ome.domain.telemetry import SourceValue


class CanonicalConcept(StrEnum):
    TIME_ELAPSED = "time.elapsed"
    LAP_DISTANCE = "lap.distance"
    VEHICLE_SPEED = "vehicle.speed"
    DRIVER_THROTTLE = "driver.throttle"
    DRIVER_BRAKE = "driver.brake"
    DRIVER_STEERING = "driver.steering"
    ENGINE_SPEED = "engine.speed"
    TRANSMISSION_GEAR = "transmission.gear"


class ConversionKind(StrEnum):
    NUMERIC_IDENTITY = "numeric_identity"
    PERCENT_TO_FRACTION = "percent_to_fraction"
    RPM_TO_RAD_PER_SECOND = "rpm_to_rad_per_second"
    INTEGER_IDENTITY = "integer_identity"


class UnmappedReason(StrEnum):
    NO_MATCHING_RULE = "no_matching_rule"
    BLOCKED_BY_VALIDATION = "blocked_by_validation"
    RULE_PRECONDITION_FAILED = "rule_precondition_failed"
    AMBIGUOUS_RULE_MATCH = "ambiguous_rule_match"
    CONVERSION_FAILED = "conversion_failed"


NormalizedValue = float | int | bool | str | None


@dataclass(frozen=True, slots=True)
class NormalizationRule:
    rule_id: str
    rule_version: str
    source_type: str
    source_channel_identifier: str
    expected_original_name: str
    expected_unit: str | None
    canonical_concept: CanonicalConcept
    source_semantics: str
    target_unit: str | None
    conversion_kind: ConversionKind
    conversion_id: str
    conversion_version: str


@dataclass(frozen=True, slots=True)
class NormalizedSeries:
    timestamps_s: tuple[float, ...]
    values: tuple[NormalizedValue, ...]


@dataclass(frozen=True, slots=True)
class NormalizationMapping:
    source_channel_identifier: str
    source_original_name: str
    source_unit: str | None
    canonical_concept: CanonicalConcept
    source_semantics: str
    target_unit: str | None
    rule_id: str
    rule_version: str
    conversion_id: str
    conversion_version: str
    series: NormalizedSeries


@dataclass(frozen=True, slots=True)
class UnmappedChannel:
    source_channel_identifier: str
    source_original_name: str
    reason: UnmappedReason
    message: str


@dataclass(frozen=True, slots=True)
class NormalizationResult:
    dataset_fingerprint: str
    normalizer_id: str
    normalizer_version: str
    mappings: tuple[NormalizationMapping, ...]
    unmapped_channels: tuple[UnmappedChannel, ...]

    def mappings_for(
        self,
        canonical_concept: CanonicalConcept,
    ) -> tuple[NormalizationMapping, ...]:
        return tuple(
            mapping
            for mapping in self.mappings
            if mapping.canonical_concept is canonical_concept
        )

    def mapping_for_source(self, source_channel_identifier: str) -> NormalizationMapping:
        matches = tuple(
            mapping
            for mapping in self.mappings
            if mapping.source_channel_identifier == source_channel_identifier
        )
        if len(matches) != 1:
            raise KeyError(source_channel_identifier)
        return matches[0]

    def unmapped_for(
        self,
        source_channel_identifiers: Iterable[str],
    ) -> tuple[UnmappedChannel, ...]:
        selected = frozenset(source_channel_identifiers)
        return tuple(
            channel
            for channel in self.unmapped_channels
            if channel.source_channel_identifier in selected
        )


def source_value_type_name(value: SourceValue) -> str:
    if value is None:
        return "null"
    return type(value).__name__
