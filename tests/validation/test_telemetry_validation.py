from __future__ import annotations

import math
import unittest
from datetime import UTC, datetime
from pathlib import Path

from ome.domain import (
    ChannelMetadata,
    ImportedTelemetryDataset,
    Provenance,
    SampleSeries,
    SourceChannel,
    TelemetrySource,
    freeze_metadata,
)
from ome.ingestion import ImportSuccess, OMECsvProfileImporter
from ome.validation import (
    TelemetryValidator,
    ValidationCategory,
    ValidationIssueCode,
    ValidationSeverity,
)

ROOT = Path(__file__).resolve().parents[2]
OME_FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"
FIXED_TIME = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)


def make_dataset(
    *,
    timestamps: tuple[float, ...] = (0.0, 0.1, 0.2),
    values: tuple[str | int | float | bool | None, ...] = ("1", "2", "3"),
    unit: str | None = "m/s",
    sample_rate_hz: float | None = 10.0,
    source_name: str = "fixture.csv",
) -> ImportedTelemetryDataset:
    source_metadata = freeze_metadata({"fixture": True})
    channel = SourceChannel(
        identifier="speed_src",
        original_name="Fixture Speed",
        source_system="OME Test",
        metadata=ChannelMetadata(
            unit=unit,
            sample_rate_hz=sample_rate_hz,
            data_type="float",
            description="Test speed channel",
        ),
        series=SampleSeries(timestamps_s=timestamps, values=values),
    )
    return ImportedTelemetryDataset(
        source=TelemetrySource(
            source_type="test",
            original_name=source_name,
            location="/fixture.csv",
            source_system="OME Test",
            format_version="0",
            metadata=source_metadata,
        ),
        provenance=Provenance(
            original_source_name=source_name,
            source_format="test",
            source_system="OME Test",
            content_fingerprint="sha256:test-fixture",
            source_size_bytes=123,
            importer_id="test.importer",
            importer_version="0",
            import_parameters=freeze_metadata({}),
            imported_at=FIXED_TIME,
            source_metadata=source_metadata,
        ),
        channels=(channel,),
        issues=(),
    )


class Req002TelemetryValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = TelemetryValidator()

    def test_ac001_validation_is_non_destructive(self) -> None:
        dataset = make_dataset()
        channel = dataset.channels[0]
        original_timestamps = channel.series.timestamps_s
        original_values = channel.series.values
        original_metadata = channel.metadata

        result = self.validator.validate(dataset)

        self.assertEqual(result.dataset_fingerprint, "sha256:test-fixture")
        self.assertIs(dataset.channels[0].series.timestamps_s, original_timestamps)
        self.assertIs(dataset.channels[0].series.values, original_values)
        self.assertIs(dataset.channels[0].metadata, original_metadata)

    def test_ac002_issue_has_category_severity_location_and_message(self) -> None:
        dataset = make_dataset(timestamps=(0.0, 0.1, 0.1))

        result = self.validator.validate(dataset)

        issue = next(
            issue
            for issue in result.issues
            if issue.code is ValidationIssueCode.DUPLICATE_TIMESTAMP
        )
        self.assertIs(issue.category, ValidationCategory.TIME)
        self.assertIs(issue.severity, ValidationSeverity.BLOCKING)
        self.assertEqual(issue.location.channel_identifier, "speed_src")
        self.assertEqual(issue.location.sample_index, 2)
        self.assertEqual(issue.location.timestamp_s, 0.1)
        self.assertTrue(issue.message)

    def test_ac003_missing_metadata_remains_explicit(self) -> None:
        dataset = make_dataset(unit=None, sample_rate_hz=None)

        result = self.validator.validate(dataset)

        issues = {issue.code: issue for issue in result.issues}
        self.assertIn(ValidationIssueCode.MISSING_CHANNEL_UNIT, issues)
        self.assertIn(ValidationIssueCode.MISSING_SAMPLE_RATE, issues)
        self.assertIs(
            issues[ValidationIssueCode.MISSING_CHANNEL_UNIT].severity,
            ValidationSeverity.WARNING,
        )
        self.assertIs(
            issues[ValidationIssueCode.MISSING_SAMPLE_RATE].severity,
            ValidationSeverity.WARNING,
        )
        self.assertIsNone(dataset.channels[0].metadata.unit)
        self.assertIsNone(dataset.channels[0].metadata.sample_rate_hz)

    def test_ac004_empty_series_is_blocking(self) -> None:
        dataset = make_dataset(timestamps=(), values=())

        result = self.validator.validate(dataset)

        self.assertTrue(result.has_blocking_issues)
        self.assertTrue(
            any(
                issue.code is ValidationIssueCode.EMPTY_SAMPLE_SERIES
                and issue.severity is ValidationSeverity.BLOCKING
                for issue in result.issues
            )
        )

    def test_ac004_decreasing_timestamp_is_blocking(self) -> None:
        dataset = make_dataset(timestamps=(0.0, 0.2, 0.1))

        result = self.validator.validate(dataset)

        self.assertTrue(result.has_blocking_issues)
        self.assertTrue(
            any(
                issue.code is ValidationIssueCode.DECREASING_TIMESTAMP
                for issue in result.blocking_issues
            )
        )

    def test_ac004_non_finite_timestamp_is_blocking(self) -> None:
        dataset = make_dataset(timestamps=(0.0, math.nan, 0.2))

        result = self.validator.validate(dataset)

        self.assertTrue(
            any(
                issue.code is ValidationIssueCode.NON_FINITE_TIMESTAMP
                and issue.severity is ValidationSeverity.BLOCKING
                for issue in result.issues
            )
        )

    def test_ac005_validation_does_not_repair_or_remove_evidence(self) -> None:
        dataset = make_dataset(timestamps=(0.0, 0.1, 0.1))
        before = dataset.channels[0].series

        self.validator.validate(dataset)

        self.assertIs(dataset.channels[0].series, before)
        self.assertEqual(dataset.channels[0].series.timestamps_s, (0.0, 0.1, 0.1))
        self.assertEqual(dataset.channels[0].series.values, ("1", "2", "3"))

    def test_ac006_result_is_evidence_not_global_analysis_readiness(self) -> None:
        result = self.validator.validate(make_dataset())

        self.assertFalse(hasattr(result, "is_valid"))
        self.assertEqual(result.issues, ())
        self.assertFalse(result.has_blocking_issues)

    def test_missing_source_identity_is_visible_warning(self) -> None:
        result = self.validator.validate(make_dataset(source_name=""))

        issue = next(
            issue
            for issue in result.issues
            if issue.code is ValidationIssueCode.MISSING_SOURCE_IDENTITY
        )
        self.assertIs(issue.category, ValidationCategory.METADATA)
        self.assertIs(issue.severity, ValidationSeverity.WARNING)
        self.assertEqual(issue.location.field, "source.original_name")

    def test_invalid_sample_rate_is_visible_without_repair(self) -> None:
        dataset = make_dataset(sample_rate_hz=-1.0)

        result = self.validator.validate(dataset)

        self.assertTrue(
            any(
                issue.code is ValidationIssueCode.INVALID_SAMPLE_RATE
                and issue.severity is ValidationSeverity.WARNING
                for issue in result.issues
            )
        )
        self.assertEqual(dataset.channels[0].metadata.sample_rate_hz, -1.0)

    def test_import_then_validate_integration_does_not_change_imported_dataset(self) -> None:
        outcome = OMECsvProfileImporter().import_source(OME_FIXTURE, imported_at=FIXED_TIME)
        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)

        dataset = outcome.dataset
        original_channels = dataset.channels
        result = self.validator.validate(dataset)

        self.assertIs(dataset.channels, original_channels)
        self.assertEqual(result.dataset_fingerprint, dataset.provenance.content_fingerprint)
        self.assertFalse(result.has_blocking_issues)


if __name__ == "__main__":
    unittest.main()
