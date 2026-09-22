from __future__ import annotations

import math

from ome.domain import (
    ImportedTelemetryDataset,
    ValidationCategory,
    ValidationIssue,
    ValidationSeverity,
)


def check_time_structure(dataset: ImportedTelemetryDataset) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []

    for channel in dataset.channels:
        timestamps = channel.series.timestamps_s
        if not timestamps:
            issues.append(
                ValidationIssue(
                    code="empty_sample_series",
                    category=ValidationCategory.STRUCTURE,
                    severity=ValidationSeverity.BLOCKING,
                    channel_identifier=channel.identifier,
                    message=f"Channel {channel.identifier!r} has no samples.",
                )
            )
            continue

        non_finite_count = 0
        first_non_finite_index: int | None = None
        duplicate_count = 0
        first_duplicate: tuple[int, float] | None = None
        decreasing_count = 0
        first_decreasing: tuple[int, float, float] | None = None

        for index, timestamp in enumerate(timestamps):
            if not math.isfinite(timestamp):
                non_finite_count += 1
                if first_non_finite_index is None:
                    first_non_finite_index = index

            if index == 0:
                continue

            previous = timestamps[index - 1]
            if not math.isfinite(previous) or not math.isfinite(timestamp):
                continue

            if timestamp == previous:
                duplicate_count += 1
                if first_duplicate is None:
                    first_duplicate = (index, timestamp)
            elif timestamp < previous:
                decreasing_count += 1
                if first_decreasing is None:
                    first_decreasing = (index, previous, timestamp)

        if non_finite_count:
            issues.append(
                ValidationIssue(
                    code="non_finite_timestamp",
                    category=ValidationCategory.TIME,
                    severity=ValidationSeverity.BLOCKING,
                    channel_identifier=channel.identifier,
                    message=(
                        f"Channel {channel.identifier!r} contains "
                        f"{non_finite_count} non-finite timestamp(s)."
                    ),
                    evidence={
                        "count": non_finite_count,
                        "first_sample_index": first_non_finite_index,
                    },
                )
            )

        if duplicate_count and first_duplicate is not None:
            sample_index, timestamp = first_duplicate
            issues.append(
                ValidationIssue(
                    code="duplicate_timestamp",
                    category=ValidationCategory.TIME,
                    severity=ValidationSeverity.BLOCKING,
                    channel_identifier=channel.identifier,
                    time_start_s=timestamp,
                    time_end_s=timestamp,
                    message=(
                        f"Channel {channel.identifier!r} contains "
                        f"{duplicate_count} duplicate timestamp transition(s)."
                    ),
                    evidence={
                        "count": duplicate_count,
                        "first_sample_index": sample_index,
                    },
                )
            )

        if decreasing_count and first_decreasing is not None:
            sample_index, previous, current = first_decreasing
            issues.append(
                ValidationIssue(
                    code="decreasing_timestamp",
                    category=ValidationCategory.TIME,
                    severity=ValidationSeverity.BLOCKING,
                    channel_identifier=channel.identifier,
                    time_start_s=min(previous, current),
                    time_end_s=max(previous, current),
                    message=(
                        f"Channel {channel.identifier!r} contains "
                        f"{decreasing_count} decreasing timestamp transition(s)."
                    ),
                    evidence={
                        "count": decreasing_count,
                        "first_sample_index": sample_index,
                        "previous_timestamp_s": previous,
                        "current_timestamp_s": current,
                    },
                )
            )

    return tuple(issues)


def check_metadata(dataset: ImportedTelemetryDataset) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []

    if not dataset.provenance.content_fingerprint.strip():
        issues.append(
            ValidationIssue(
                code="missing_content_fingerprint",
                category=ValidationCategory.METADATA,
                severity=ValidationSeverity.BLOCKING,
                message="Dataset has no content fingerprint for provenance.",
            )
        )

    if not dataset.source.original_name.strip():
        issues.append(
            ValidationIssue(
                code="missing_source_identity",
                category=ValidationCategory.METADATA,
                severity=ValidationSeverity.WARNING,
                message="Dataset source has no original source name.",
            )
        )

    for channel in dataset.channels:
        metadata = channel.metadata

        if not channel.original_name.strip():
            issues.append(
                ValidationIssue(
                    code="missing_channel_source_name",
                    category=ValidationCategory.METADATA,
                    severity=ValidationSeverity.WARNING,
                    channel_identifier=channel.identifier,
                    message=f"Channel {channel.identifier!r} has no original source name.",
                )
            )

        if metadata.unit is None:
            issues.append(
                ValidationIssue(
                    code="missing_channel_unit",
                    category=ValidationCategory.METADATA,
                    severity=ValidationSeverity.WARNING,
                    channel_identifier=channel.identifier,
                    message=f"Channel {channel.identifier!r} has no supplied unit metadata.",
                )
            )

        sample_rate = metadata.sample_rate_hz
        if sample_rate is None:
            issues.append(
                ValidationIssue(
                    code="missing_sample_rate",
                    category=ValidationCategory.METADATA,
                    severity=ValidationSeverity.WARNING,
                    channel_identifier=channel.identifier,
                    message=(
                        f"Channel {channel.identifier!r} has no supplied sample-rate metadata."
                    ),
                )
            )
        elif not math.isfinite(sample_rate) or sample_rate <= 0:
            issues.append(
                ValidationIssue(
                    code="invalid_sample_rate",
                    category=ValidationCategory.METADATA,
                    severity=ValidationSeverity.WARNING,
                    channel_identifier=channel.identifier,
                    message=(
                        f"Channel {channel.identifier!r} has invalid sample-rate metadata."
                    ),
                    evidence={"sample_rate_hz": repr(sample_rate)},
                )
            )

    return tuple(issues)


def check_values(dataset: ImportedTelemetryDataset) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []

    for channel in dataset.channels:
        missing_count = 0
        first_missing_index: int | None = None
        non_finite_count = 0
        first_non_finite_index: int | None = None

        for index, value in enumerate(channel.series.values):
            if value is None:
                missing_count += 1
                if first_missing_index is None:
                    first_missing_index = index
            elif isinstance(value, float) and not math.isfinite(value):
                non_finite_count += 1
                if first_non_finite_index is None:
                    first_non_finite_index = index

        if missing_count:
            issues.append(
                _value_issue(
                    channel_identifier=channel.identifier,
                    code="missing_sample_value",
                    message=(
                        f"Channel {channel.identifier!r} contains "
                        f"{missing_count} missing sample value(s)."
                    ),
                    count=missing_count,
                    first_index=first_missing_index,
                    timestamps=channel.series.timestamps_s,
                )
            )

        if non_finite_count:
            issues.append(
                _value_issue(
                    channel_identifier=channel.identifier,
                    code="non_finite_numeric_value",
                    message=(
                        f"Channel {channel.identifier!r} contains "
                        f"{non_finite_count} non-finite numeric value(s)."
                    ),
                    count=non_finite_count,
                    first_index=first_non_finite_index,
                    timestamps=channel.series.timestamps_s,
                )
            )

    return tuple(issues)


def _value_issue(
    *,
    channel_identifier: str,
    code: str,
    message: str,
    count: int,
    first_index: int | None,
    timestamps: tuple[float, ...],
) -> ValidationIssue:
    time_s: float | None = None
    if first_index is not None and first_index < len(timestamps):
        candidate = timestamps[first_index]
        if math.isfinite(candidate):
            time_s = candidate

    return ValidationIssue(
        code=code,
        category=ValidationCategory.VALUE,
        severity=ValidationSeverity.WARNING,
        channel_identifier=channel_identifier,
        time_start_s=time_s,
        time_end_s=time_s,
        message=message,
        evidence={
            "count": count,
            "first_sample_index": first_index,
        },
    )
