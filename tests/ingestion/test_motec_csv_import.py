from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from ome.domain import ValidationSeverity
from ome.ingestion import (
    ImportFailure,
    ImportFailureCode,
    ImportSuccess,
    MoTeCCSVImporter,
    OMECsvProfileImporter,
    TelemetryImportService,
)
from ome.validation import TelemetryValidator

ROOT = Path(__file__).resolve().parents[2]
MOTEC_FIXTURE = ROOT / "fixtures" / "public" / "trace" / "motec-canonical.csv"
MOTEC_DECREASING_TIME = ROOT / "fixtures" / "public" / "trace" / "motec-decreasing-time.csv"
OME_FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"
FIXED_TIME = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)


class Plan008MoTeCCSVImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.importer = MoTeCCSVImporter()
        self.validator = TelemetryValidator()

    def import_fixture(self) -> ImportSuccess:
        outcome = self.importer.import_source(MOTEC_FIXTURE, imported_at=FIXED_TIME)
        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        return outcome

    def test_supported_motec_csv_import_succeeds(self) -> None:
        outcome = self.import_fixture()

        self.assertEqual(outcome.dataset.source.source_type, "motec-csv")
        self.assertEqual(outcome.dataset.source.source_system, "MoTeC")
        self.assertIsNone(outcome.dataset.source.format_version)
        self.assertEqual(len(outcome.dataset.channels), 13)
        self.assertEqual(outcome.summary.source_identity, "motec-canonical.csv")

    def test_import_does_not_modify_source_bytes(self) -> None:
        before = MOTEC_FIXTURE.read_bytes()

        self.import_fixture()

        self.assertEqual(MOTEC_FIXTURE.read_bytes(), before)

    def test_preamble_rows_are_preserved_as_source_metadata(self) -> None:
        outcome = self.import_fixture()
        preamble = outcome.dataset.source.metadata["motec_preamble_rows"]

        self.assertEqual(
            preamble,
            (
                ("Format", "MoTeC CSV File"),
                ("Venue", "Synthetic Circuit"),
                ("Vehicle", "Fixture Car"),
                ("Driver", "TRACE Test Driver"),
            ),
        )

    def test_channel_names_units_and_order_are_preserved(self) -> None:
        outcome = self.import_fixture()
        channels = outcome.dataset.channels

        self.assertEqual(
            tuple(channel.original_name for channel in channels),
            (
                "Time",
                "Throttle Pos",
                "Brake Pos",
                "Clutch Pos",
                "Ground Speed",
                "Engine RPM",
                "Steering Angle",
                "Fuel Level",
                "Gear",
                "Position X",
                "Position Y",
                "Position Z",
                "Damper FL",
            ),
        )
        self.assertEqual(
            tuple(channel.identifier for channel in channels),
            tuple(channel.original_name for channel in channels),
        )
        self.assertEqual(outcome.dataset.channel("Ground Speed").metadata.unit, "km/h")
        self.assertEqual(outcome.dataset.channel("Gear").metadata.unit, "")
        self.assertEqual(outcome.dataset.channel("Damper FL").metadata.unit, "mm")

    def test_explicit_time_channel_drives_timestamps_and_remains_source_text(self) -> None:
        outcome = self.import_fixture()
        time = outcome.dataset.channel("Time")
        speed = outcome.dataset.channel("Ground Speed")

        self.assertEqual(time.series.timestamps_s, (12.5, 12.55))
        self.assertIs(speed.series.timestamps_s, time.series.timestamps_s)
        self.assertEqual(time.series.values, ("12.5", "12.55"))
        self.assertEqual(speed.series.values, ("180", "183.6"))

    def test_discrete_and_missing_like_text_are_not_normalized(self) -> None:
        outcome = self.import_fixture()

        gear = outcome.dataset.channel("Gear")
        damper = outcome.dataset.channel("Damper FL")

        self.assertEqual(gear.series.values, ("3", "N"))
        self.assertEqual(damper.series.values, ("42.5", "not available"))

    def test_missing_sample_rate_stays_unknown_and_visible(self) -> None:
        outcome = self.import_fixture()

        self.assertIsNone(outcome.dataset.channel("Ground Speed").metadata.sample_rate_hz)
        self.assertIn("sample_rate_hz", outcome.summary.missing_metadata)
        self.assertIn("missing_sample_rate", {issue.code for issue in outcome.summary.warnings})

    def test_explicit_sample_rate_is_preserved_without_inference(self) -> None:
        source = """Format,MoTeC CSV File
Sample Rate,100.000,Hz

Time,Motor Speed,Battery Volts
s,rpm,V

0.000,1000,36.1
0.010,1001,36.2
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample-rate.csv"
            path.write_text(source, encoding="utf-8")
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        self.assertEqual(outcome.dataset.channel("Motor Speed").metadata.sample_rate_hz, 100.0)
        self.assertEqual(outcome.dataset.channel("Battery Volts").metadata.sample_rate_hz, 100.0)
        self.assertEqual(outcome.dataset.source.metadata["sample_rate_hz"], 100.0)
        self.assertNotIn("sample_rate_hz", outcome.summary.missing_metadata)

    def test_quoted_and_unquoted_csv_are_semantically_equivalent(self) -> None:
        rows: list[list[str]]
        with MOTEC_FIXTURE.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))

        with tempfile.TemporaryDirectory() as directory:
            quoted = Path(directory) / "quoted.csv"
            with quoted.open("w", encoding="utf-8", newline="") as handle:
                csv.writer(handle, quoting=csv.QUOTE_ALL).writerows(rows)

            unquoted_outcome = self.importer.import_source(
                MOTEC_FIXTURE,
                imported_at=FIXED_TIME,
            )
            quoted_outcome = self.importer.import_source(
                quoted,
                imported_at=FIXED_TIME,
            )

        self.assertIsInstance(unquoted_outcome, ImportSuccess)
        self.assertIsInstance(quoted_outcome, ImportSuccess)
        assert isinstance(unquoted_outcome, ImportSuccess)
        assert isinstance(quoted_outcome, ImportSuccess)

        self.assertEqual(unquoted_outcome.dataset.channels, quoted_outcome.dataset.channels)
        self.assertEqual(
            unquoted_outcome.dataset.source.metadata["motec_preamble_rows"],
            quoted_outcome.dataset.source.metadata["motec_preamble_rows"],
        )

    def test_duplicate_source_names_get_deterministic_technical_identifiers(self) -> None:
        source = """Format,MoTeC CSV File
Sample Rate,100.000,Hz

Time,Engine Speed,Time
s,rpm,min

0.000,1000,1
0.010,1010,1
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.csv"
            path.write_text(source, encoding="utf-8")
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)

        channels = outcome.dataset.channels
        self.assertEqual(
            tuple(channel.identifier for channel in channels), ("Time", "Engine Speed", "Time#2")
        )
        self.assertEqual(
            tuple(channel.original_name for channel in channels), ("Time", "Engine Speed", "Time")
        )

        duplicate = outcome.dataset.channel("Time#2")
        self.assertEqual(duplicate.metadata.unit, "min")
        self.assertEqual(duplicate.metadata.source_attributes["motec_column_index"], 2)
        self.assertEqual(duplicate.metadata.source_attributes["motec_name_occurrence"], 2)
        self.assertEqual(duplicate.series.values, ("1", "1"))

    def test_adapter_arbitration_is_independent_of_registration_order(self) -> None:
        motec_first = TelemetryImportService([self.importer, OMECsvProfileImporter()])
        ome_first = TelemetryImportService([OMECsvProfileImporter(), self.importer])

        motec_a = motec_first.import_file(MOTEC_FIXTURE, imported_at=FIXED_TIME)
        motec_b = ome_first.import_file(MOTEC_FIXTURE, imported_at=FIXED_TIME)
        ome_a = motec_first.import_file(OME_FIXTURE, imported_at=FIXED_TIME)
        ome_b = ome_first.import_file(OME_FIXTURE, imported_at=FIXED_TIME)

        for outcome in (motec_a, motec_b):
            self.assertIsInstance(outcome, ImportSuccess)
            assert isinstance(outcome, ImportSuccess)
            self.assertEqual(outcome.dataset.source.source_type, "motec-csv")

        for outcome in (ome_a, ome_b):
            self.assertIsInstance(outcome, ImportSuccess)
            assert isinstance(outcome, ImportSuccess)
            self.assertEqual(outcome.dataset.source.source_type, "ome-csv-profile")

    def test_arbitrary_csv_is_not_claimed_as_motec(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generic.csv"
            path.write_text("time,speed\n0,10\n", encoding="utf-8")

            self.assertFalse(self.importer.supports(path))
            outcome = TelemetryImportService([self.importer]).import_file(
                path,
                imported_at=FIXED_TIME,
            )

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.UNSUPPORTED_SOURCE)

    def test_decreasing_time_imports_then_validation_blocks_it(self) -> None:
        outcome = self.importer.import_source(
            MOTEC_DECREASING_TIME,
            imported_at=FIXED_TIME,
        )

        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        self.assertEqual(outcome.dataset.channel("Time").series.timestamps_s, (1.0, 0.0))

        validation = self.validator.validate(outcome.dataset)

        self.assertTrue(validation.has_blocking_issues)
        self.assertIn(
            "decreasing_timestamp",
            {issue.code for issue in validation.issues},
        )
        issue = next(issue for issue in validation.issues if issue.code == "decreasing_timestamp")
        self.assertEqual(issue.severity, ValidationSeverity.BLOCKING)

    def test_provenance_fingerprint_is_deterministic_for_same_bytes(self) -> None:
        expected = f"sha256:{hashlib.sha256(MOTEC_FIXTURE.read_bytes()).hexdigest()}"

        first = self.importer.import_source(
            MOTEC_FIXTURE,
            imported_at=FIXED_TIME,
        )
        second = self.importer.import_source(
            MOTEC_FIXTURE,
            imported_at=datetime(2026, 9, 22, 13, 0, tzinfo=UTC),
        )

        self.assertIsInstance(first, ImportSuccess)
        self.assertIsInstance(second, ImportSuccess)
        assert isinstance(first, ImportSuccess)
        assert isinstance(second, ImportSuccess)

        self.assertEqual(first.dataset.provenance.content_fingerprint, expected)
        self.assertEqual(second.dataset.provenance.content_fingerprint, expected)
        self.assertEqual(first.dataset.channels, second.dataset.channels)
        self.assertNotEqual(
            first.dataset.provenance.imported_at, second.dataset.provenance.imported_at
        )

    def test_wrong_time_unit_is_explicit_invalid_profile_failure(self) -> None:
        source = """Format,MoTeC CSV File
Time,Ground Speed
ms,km/h
0,36
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "milliseconds.csv"
            path.write_text(source, encoding="utf-8")
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("seconds", outcome.message.lower())

    def test_wrong_data_row_width_is_explicit_invalid_profile_failure(self) -> None:
        source = """Format,MoTeC CSV File
Time,Ground Speed
s,km/h
0,36
0.1
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad-width.csv"
            path.write_text(source, encoding="utf-8")
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("fields", outcome.message.lower())

    def test_empty_data_table_is_explicit_invalid_profile_failure(self) -> None:
        source = """Format,MoTeC CSV File
Time,Ground Speed
s,km/h
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.csv"
            path.write_text(source, encoding="utf-8")
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("data row", outcome.message.lower())


if __name__ == "__main__":
    unittest.main()
