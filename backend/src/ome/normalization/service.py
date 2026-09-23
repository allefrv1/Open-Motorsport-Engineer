from __future__ import annotations

import math
from collections.abc import Iterable

from ome.domain import (
    ConversionKind,
    ImportedTelemetryDataset,
    NormalizationMapping,
    NormalizationResult,
    NormalizationRule,
    NormalizedSeries,
    SourceChannel,
    SourceValue,
    UnmappedChannel,
    UnmappedReason,
    ValidationResult,
    ValidationSeverity,
)


class _ConversionFailure(ValueError):
    pass


class TelemetryNormalizer:
    """Apply explicit, versioned normalization rules without mutating source evidence."""

    normalizer_id = "ome.telemetry-normalizer"
    normalizer_version = "0.1.0"

    def __init__(self, rules: Iterable[NormalizationRule]) -> None:
        self._rules = tuple(rules)

    def normalize(
        self,
        dataset: ImportedTelemetryDataset,
        validation: ValidationResult,
    ) -> NormalizationResult:
        if validation.dataset_fingerprint != dataset.provenance.content_fingerprint:
            raise ValueError("validation result does not belong to the telemetry dataset")

        mappings: list[NormalizationMapping] = []
        unmapped: list[UnmappedChannel] = []

        for channel in dataset.channels:
            blocked = tuple(
                issue
                for issue in validation.relevant_issues([channel.identifier])
                if issue.severity is ValidationSeverity.BLOCKING
            )
            if blocked:
                unmapped.append(
                    UnmappedChannel(
                        source_channel_identifier=channel.identifier,
                        source_original_name=channel.original_name,
                        reason=UnmappedReason.BLOCKED_BY_VALIDATION,
                        message=(
                            f"Channel {channel.identifier!r} has blocking validation evidence."
                        ),
                    )
                )
                continue

            candidates = self._candidate_rules(dataset, channel)
            if not candidates:
                unmapped.append(
                    UnmappedChannel(
                        source_channel_identifier=channel.identifier,
                        source_original_name=channel.original_name,
                        reason=UnmappedReason.NO_MATCHING_RULE,
                        message=(
                            f"No explicit normalization rule exists for {channel.identifier!r}."
                        ),
                    )
                )
                continue

            applicable = tuple(
                rule
                for rule in candidates
                if rule.expected_original_name == channel.original_name
                and rule.expected_unit == channel.metadata.unit
            )
            if not applicable:
                unmapped.append(
                    UnmappedChannel(
                        source_channel_identifier=channel.identifier,
                        source_original_name=channel.original_name,
                        reason=UnmappedReason.RULE_PRECONDITION_FAILED,
                        message=(
                            f"Explicit normalization rule preconditions do not match "
                            f"channel {channel.identifier!r}."
                        ),
                    )
                )
                continue

            if len(applicable) != 1:
                unmapped.append(
                    UnmappedChannel(
                        source_channel_identifier=channel.identifier,
                        source_original_name=channel.original_name,
                        reason=UnmappedReason.AMBIGUOUS_RULE_MATCH,
                        message=(
                            f"More than one explicit normalization rule matches "
                            f"channel {channel.identifier!r}."
                        ),
                    )
                )
                continue

            rule = applicable[0]
            try:
                normalized_values = tuple(
                    self._convert_value(value, rule.conversion_kind)
                    for value in channel.series.values
                )
            except _ConversionFailure as exc:
                unmapped.append(
                    UnmappedChannel(
                        source_channel_identifier=channel.identifier,
                        source_original_name=channel.original_name,
                        reason=UnmappedReason.CONVERSION_FAILED,
                        message=str(exc),
                    )
                )
                continue

            mappings.append(
                NormalizationMapping(
                    source_channel_identifier=channel.identifier,
                    source_original_name=channel.original_name,
                    source_unit=channel.metadata.unit,
                    canonical_concept=rule.canonical_concept,
                    source_semantics=rule.source_semantics,
                    target_unit=rule.target_unit,
                    rule_id=rule.rule_id,
                    rule_version=rule.rule_version,
                    conversion_id=rule.conversion_id,
                    conversion_version=rule.conversion_version,
                    series=NormalizedSeries(
                        timestamps_s=channel.series.timestamps_s,
                        values=normalized_values,
                    ),
                    semantic_id=rule.semantic_id,
                )
            )

        return NormalizationResult(
            dataset_fingerprint=dataset.provenance.content_fingerprint,
            normalizer_id=self.normalizer_id,
            normalizer_version=self.normalizer_version,
            mappings=tuple(mappings),
            unmapped_channels=tuple(unmapped),
        )

    def _candidate_rules(
        self,
        dataset: ImportedTelemetryDataset,
        channel: SourceChannel,
    ) -> tuple[NormalizationRule, ...]:
        return tuple(
            rule
            for rule in self._rules
            if rule.source_type == dataset.source.source_type
            and rule.source_channel_identifier == channel.identifier
        )

    @staticmethod
    def _convert_value(value: SourceValue, kind: ConversionKind) -> float | int | bool | str | None:
        if value is None:
            return None

        if isinstance(value, tuple):
            raise _ConversionFailure(
                "Array source value cannot be converted by a scalar normalization rule."
            )

        if kind is ConversionKind.INTEGER_IDENTITY:
            return _as_integer(value)

        numeric = _as_float(value)

        if kind is ConversionKind.NUMERIC_IDENTITY:
            return numeric
        if kind is ConversionKind.PERCENT_TO_FRACTION:
            return numeric / 100.0
        if kind is ConversionKind.RPM_TO_RAD_PER_SECOND:
            return numeric * 2.0 * math.pi / 60.0

        raise _ConversionFailure(f"Unsupported conversion kind: {kind}")


def _as_float(value: str | int | float | bool) -> float:
    if isinstance(value, bool):
        raise _ConversionFailure("Boolean source value cannot be converted to a numeric quantity.")

    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise _ConversionFailure(
            f"Source value {value!r} cannot be converted to a finite number."
        ) from exc

    if not math.isfinite(result):
        raise _ConversionFailure(f"Source value {value!r} is not finite.")
    return result


def _as_integer(value: str | int | float | bool) -> int:
    if isinstance(value, bool):
        raise _ConversionFailure("Boolean source value cannot be converted to an integer.")

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value) or not value.is_integer():
            raise _ConversionFailure(f"Source value {value!r} is not an integer.")
        return int(value)

    if isinstance(value, str):
        stripped = value.strip()
        try:
            return int(stripped)
        except ValueError as exc:
            raise _ConversionFailure(f"Source value {value!r} is not an integer.") from exc

    raise _ConversionFailure(f"Source value {value!r} is not an integer.")
