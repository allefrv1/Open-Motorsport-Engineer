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
    ValidationCategory,
    ValidationSeverity,
    freeze_metadata,
)
from ome.ingestion import ImportSuccess, OMECsvProfileImporter
from ome.validation import TelemetryValidator

ROOT = Path(__file__).resolve().parents[2]
OME_FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"


def make_channel(
    identifier: str,
    *,
    timestamps: tuple[float, ...] = (0.0, 0.1, 0.2),
    values: tuple[str | int | float | bool | None, ...] = ("1", "2", "3"),
    original_name: str | None = None,
    unit: str | None = "m/s",
    sample_rate_hz: float | None = 10.0,
) -> SourceChannel:
    return SourceChannel(
        identifier=identifier,
        original_name=identifier if original_name is None else original_name,
        source_system="test",
        metadata=ChannelMetadata(
            unit=unit,
            sample_rate_hz=sample_rate_hz,
        ),
        series=SampleSeries(
            timestamps_s=timestamps,
            values=values,
        ),
    )


def make_dataset(
    *channels: SourceChannel,
    source_name: str = "test.csv",
    fingerprint: str = "sha256:test",
) -> ImportedTelemetryDataset:
    metadata = freeze_metadata({"fixture": "validation"})
    return ImportedTelemetryDataset(
        source=TelemetrySource(
            source_type="test",
            original_name=source_name,
            location="/tmp/test.csv",
            source_system="test",
            format_version="1",
            metadata=metadata,
        ),
        provenance=Provenance(
            original_source_name=source_name,
            source_format="test",
            source_system="test",
            content_fingerprint=fingerprint,
            source_size_bytes=1,
            importer_id="test.importer",
            importer_version="1",
            import_parameters=freeze_metadata({}),
            imported_at=datetime(2026, 9, 22, 12, 0, tzinfo=UTC),
            source_metadata=metadata,
        ),
        channels=tuple(channels),
        issues=(),
    )


class Req002TelemetryValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = TelemetryValidator()

    def test_ac001_validation_is_non_destructive(self) -> None:
        importer = OMECsvProfileImporter()
        outcome = importer.import_source(
            OME_FIXTURE,
            imported_at=datetime(2026, 9, 22, 12, 0, tzinfo=UTC),
        )
        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)

        dataset = outcome.dataset
        before = tuple(
            (
                channel.identifier,
                channel.original_name,
                channel.metadata,
                channel.series.timestamps_s,
                channel.series.values,
            )
            for channel in dataset.channels
        )

        result = self.validator.validate(dataset)

        after = tuple(
            (
                channel.identifier,
                channel.original_name,
                channel.metadata,
                channel.series.timestamps_s,
                channel.series.values,
            )
            for channel in dataset.channels
        )
        self.assertEqual(after, before)
        self.assertEqual(result.dataset_fingerprint, dataset.provenance.content_fingerprint)
        self.assertEqual(result.issues, ())

    def test_ac002_issue_contains_category_severity_scope_and_message(self) -> None:
        dataset = make_dataset(
            make_channel(
                "speed",
                timestamps=(0.0, 0.1, 0.1),
            )
        )

        result = self.validator.validate(dataset)
        issue = next(issue for issue in result.issues if issue.code == "duplicate_timestamp")

        self.assertEqual(issue.category, ValidationCategory.TIME)
        self.assertEqual(issue.severity, ValidationSeverity.BLOCKING)
        self.assertEqual(issue.channel_identifier, "speed")
        self.assertEqual(issue.time_start_s, 0.1)
        self.assertEqual(issue.time_end_s, 0.1)
        self.assertTrue(issue.message)
        self.assertEqual(issue.evidence["count"], 1)

    def test_ac003_missing_metadata_remains_explicit(self) -> None:
        dataset = make_dataset(
            make_channel(
                "speed",
                unit=None,
                sample_rate_hz=None,
            )
        )

        result = self.validator.validate(dataset)
        issues = {issue.code: issue for issue in result.issues}

        self.assertEqual(issues["missing_channel_unit"].severity, ValidationSeverity.WARNING)
        self.assertEqual(issues["missing_channel_unit"].channel_identifier, "speed")
        self.assertEqual(issues["missing_sample_rate"].severity, ValidationSeverity.WARNING)

    def test_ac004_structural_time_corruption_is_blocking(self) -> None:
        dataset = make_dataset(
            make_channel(
                "speed",
                timestamps=(0.0, 0.2, 0.1),
            )
        )

        result = self.validator.validate(dataset)

        self.assertTrue(result.has_blocking_issues)
        self.assertIn("decreasing_timestamp", {issue.code for issue in result.blocking_issues})

    def test_ac005_validation_does_not_repair_values_or_time(self) -> None:
        channel = make_channel(
            "speed",
            timestamps=(0.0, 0.1, 0.1),
            values=("10", None, "12"),
        )
        dataset = make_dataset(channel)
        timestamps_before = channel.series.timestamps_s
        values_before = channel.series.values
        unit_before = channel.metadata.unit

        result = self.validator.validate(dataset)

        self.assertEqual(channel.series.timestamps_s, timestamps_before)
        self.assertEqual(channel.series.values, values_before)
        self.assertEqual(channel.metadata.unit, unit_before)
        self.assertIn("duplicate_timestamp", {issue.code for issue in result.issues})
        self.assertIn("missing_sample_value", {issue.code for issue in result.issues})

    def test_ac006_validation_output_can_be_scoped_for_later_readiness(self) -> None:
        dataset = make_dataset(
            make_channel("speed", unit="m/s"),
            make_channel("rpm", unit=None),
        )

        result = self.validator.validate(dataset)
        speed_issues = result.relevant_issues(["speed"])
        rpm_issues = result.relevant_issues(["rpm"])

        self.assertNotIn("missing_channel_unit", {issue.code for issue in speed_issues})
        self.assertIn("missing_channel_unit", {issue.code for issue in rpm_issues})
        self.assertFalse(hasattr(result, "is_valid_for_all_analyses"))

    def test_empty_series_is_blocking(self) -> None:
        dataset = make_dataset(
            make_channel(
                "speed",
                timestamps=(),
                values=(),
            )
        )

        result = self.validator.validate(dataset)

        self.assertIn("empty_sample_series", {issue.code for issue in result.blocking_issues})

    def test_non_finite_timestamp_is_blocking(self) -> None:
        dataset = make_dataset(
            make_channel(
                "speed",
                timestamps=(0.0, math.nan, 0.2),
            )
        )

        result = self.validator.validate(dataset)
        issue = next(issue for issue in result.issues if issue.code == "non_finite_timestamp")

        self.assertEqual(issue.severity, ValidationSeverity.BLOCKING)
        self.assertEqual(issue.evidence["count"], 1)

    def test_non_finite_numeric_values_are_aggregated_as_warning(self) -> None:
        dataset = make_dataset(
            make_channel(
                "speed",
                values=(1.0, math.nan, math.inf),
            )
        )

        result = self.validator.validate(dataset)
        issue = next(issue for issue in result.issues if issue.code == "non_finite_numeric_value")

        self.assertEqual(issue.severity, ValidationSeverity.WARNING)
        self.assertEqual(issue.evidence["count"], 2)
        self.assertEqual(issue.evidence["first_sample_index"], 1)

    def test_missing_values_are_aggregated_as_warning(self) -> None:
        dataset = make_dataset(
            make_channel(
                "speed",
                values=(None, "11", None),
            )
        )

        result = self.validator.validate(dataset)
        matching = [issue for issue in result.issues if issue.code == "missing_sample_value"]

        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0].evidence["count"], 2)

    def test_invalid_sample_rate_is_warning_not_silent_repair(self) -> None:
        dataset = make_dataset(make_channel("speed", sample_rate_hz=-10.0))

        result = self.validator.validate(dataset)
        issue = next(issue for issue in result.issues if issue.code == "invalid_sample_rate")

        self.assertEqual(issue.severity, ValidationSeverity.WARNING)
        self.assertEqual(issue.evidence["sample_rate_hz"], "-10.0")
        self.assertEqual(dataset.channel("speed").metadata.sample_rate_hz, -10.0)

    def test_missing_content_fingerprint_is_blocking(self) -> None:
        dataset = make_dataset(make_channel("speed"), fingerprint="")

        result = self.validator.validate(dataset)

        self.assertIn(
            "missing_content_fingerprint",
            {issue.code for issue in result.blocking_issues},
        )


if __name__ == "__main__":
    unittest.main()
