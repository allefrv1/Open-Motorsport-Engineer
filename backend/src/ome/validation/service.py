from __future__ import annotations

import math

from ome.domain import ImportedTelemetryDataset, SourceChannel
from ome.validation.model import (
    ValidationCategory,
    ValidationIssue,
    ValidationIssueCode,
    ValidationLocation,
    ValidationResult,
    ValidationSeverity,
)


class TelemetryValidator:
    """Run source-independent, non-destructive telemetry validation checks."""

    def validate(self, dataset: ImportedTelemetryDataset) -> ValidationResult:
        issues: list[ValidationIssue] = []

        self._check_source_identity(dataset, issues)
        for channel in dataset.channels:
            self._check_channel_metadata(channel, issues)
            self._check_time_series(channel, issues)

        return ValidationResult(
            dataset_fingerprint=dataset.provenance.content_fingerprint,
            issues=tuple(issues),
        )

    @staticmethod
    def _check_source_identity(
        dataset: ImportedTelemetryDataset,
        issues: list[ValidationIssue],
    ) -> None:
        if dataset.source.original_name.strip():
            return

        issues.append(
            ValidationIssue(
                code=ValidationIssueCode.MISSING_SOURCE_IDENTITY,
                category=ValidationCategory.METADATA,
                severity=ValidationSeverity.WARNING,
                message="Dataset source identity is missing.",
                location=ValidationLocation(field="source.original_name"),
            )
        )

    @staticmethod
    def _check_channel_metadata(
        channel: SourceChannel,
        issues: list[ValidationIssue],
    ) -> None:
        unit = channel.metadata.unit
        if unit is None or not unit.strip():
            issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.MISSING_CHANNEL_UNIT,
                    category=ValidationCategory.METADATA,
                    severity=ValidationSeverity.WARNING,
                    message=f"Channel {channel.identifier!r} does not provide a unit.",
                    location=ValidationLocation(
                        channel_identifier=channel.identifier,
                        field="metadata.unit",
                    ),
                )
            )

        sample_rate_hz = channel.metadata.sample_rate_hz
        if sample_rate_hz is None:
            issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.MISSING_SAMPLE_RATE,
                    category=ValidationCategory.METADATA,
                    severity=ValidationSeverity.WARNING,
                    message=f"Channel {channel.identifier!r} does not provide a sample rate.",
                    location=ValidationLocation(
                        channel_identifier=channel.identifier,
                        field="metadata.sample_rate_hz",
                    ),
                )
            )
        elif not math.isfinite(sample_rate_hz) or sample_rate_hz <= 0:
            issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.INVALID_SAMPLE_RATE,
                    category=ValidationCategory.METADATA,
                    severity=ValidationSeverity.WARNING,
                    message=(
                        f"Channel {channel.identifier!r} provides an invalid sample rate "
                        f"{sample_rate_hz!r}."
                    ),
                    location=ValidationLocation(
                        channel_identifier=channel.identifier,
                        field="metadata.sample_rate_hz",
                    ),
                )
            )

    @staticmethod
    def _check_time_series(
        channel: SourceChannel,
        issues: list[ValidationIssue],
    ) -> None:
        timestamps = channel.series.timestamps_s
        if not timestamps:
            issues.append(
                ValidationIssue(
                    code=ValidationIssueCode.EMPTY_SAMPLE_SERIES,
                    category=ValidationCategory.STRUCTURE,
                    severity=ValidationSeverity.BLOCKING,
                    message=f"Channel {channel.identifier!r} has no samples.",
                    location=ValidationLocation(channel_identifier=channel.identifier),
                )
            )
            return

        previous_finite_timestamp: float | None = None

        for index, timestamp_s in enumerate(timestamps):
            if not math.isfinite(timestamp_s):
                issues.append(
                    ValidationIssue(
                        code=ValidationIssueCode.NON_FINITE_TIMESTAMP,
                        category=ValidationCategory.TIME,
                        severity=ValidationSeverity.BLOCKING,
                        message=(
                            f"Channel {channel.identifier!r} contains a non-finite timestamp "
                            f"at sample {index}."
                        ),
                        location=ValidationLocation(
                            channel_identifier=channel.identifier,
                            sample_index=index,
                            timestamp_s=timestamp_s,
                        ),
                    )
                )
                previous_finite_timestamp = None
                continue

            if previous_finite_timestamp is not None:
                if timestamp_s == previous_finite_timestamp:
                    issues.append(
                        ValidationIssue(
                            code=ValidationIssueCode.DUPLICATE_TIMESTAMP,
                            category=ValidationCategory.TIME,
                            severity=ValidationSeverity.BLOCKING,
                            message=(
                                f"Channel {channel.identifier!r} repeats timestamp "
                                f"{timestamp_s!r} at sample {index}."
                            ),
                            location=ValidationLocation(
                                channel_identifier=channel.identifier,
                                sample_index=index,
                                timestamp_s=timestamp_s,
                            ),
                        )
                    )
                elif timestamp_s < previous_finite_timestamp:
                    issues.append(
                        ValidationIssue(
                            code=ValidationIssueCode.DECREASING_TIMESTAMP,
                            category=ValidationCategory.TIME,
                            severity=ValidationSeverity.BLOCKING,
                            message=(
                                f"Channel {channel.identifier!r} timestamp decreases at "
                                f"sample {index}."
                            ),
                            location=ValidationLocation(
                                channel_identifier=channel.identifier,
                                sample_index=index,
                                timestamp_s=timestamp_s,
                            ),
                        )
                    )

            previous_finite_timestamp = timestamp_s
