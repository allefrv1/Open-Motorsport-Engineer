from __future__ import annotations

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
    IRacingIBTImporter,
    MoTeCCSVImporter,
    OMECsvProfileImporter,
    TelemetryImportService,
    TraqmateTrackvisionCSVImporter,
)
from ome.validation import TelemetryValidator

ROOT = Path(__file__).resolve().parents[2]
TRAQMATE_FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-parking-lot.csv"
MOTEC_FIXTURE = ROOT / "fixtures" / "public" / "trace" / "motec-canonical.csv"
OME_FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"
FIXED_TIME = datetime(2026, 9, 23, 12, 0, tzinfo=UTC)


class Plan021TraqmateTrackvisionCSVImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.importer = TraqmateTrackvisionCSVImporter()
        self.validator = TelemetryValidator()

    def import_fixture(self) -> ImportSuccess:
        outcome = self.importer.import_source(
            TRAQMATE_FIXTURE,
            imported_at=FIXED_TIME,
        )
        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        return outcome

    def test_supported_real_traqmate_fixture_imports(self) -> None:
        outcome = self.import_fixture()

        self.assertEqual(outcome.dataset.source.source_type, "traqmate-trackvision-csv")
        self.assertEqual(outcome.dataset.source.source_system, "Traqmate Trackvision")
        self.assertEqual(outcome.dataset.source.format_version, "V2")
        self.assertEqual(outcome.summary.source_identity, "traqmate-parking-lot.csv")
        self.assertEqual(len(outcome.dataset.channels), 6)

    def test_source_preamble_is_preserved(self) -> None:
        outcome = self.import_fixture()

        self.assertEqual(
            outcome.dataset.source.metadata["traqmate_preamble_rows"],
            (
                ("Format", "Traqmate Trackvision", "V2"),
                ("Track", "Test Parking Lot"),
                ("Vehicle", "CORRADO"),
                ("Driver", "DJ"),
                ("Starting Date", "2020/06/11"),
                ("Starting Time", "22:16:027"),
                ("Sample Rate (samps/sec)", "10"),
                ("Duration (secs)", "196"),
            ),
        )
        self.assertEqual(outcome.dataset.source.metadata["sample_rate_hz"], 10.0)
        self.assertEqual(outcome.dataset.source.metadata["track"], "Test Parking Lot")
        self.assertEqual(outcome.dataset.source.metadata["vehicle"], "CORRADO")
        self.assertEqual(outcome.dataset.source.metadata["driver"], "DJ")

    def test_channel_names_units_and_source_order_are_preserved(self) -> None:
        outcome = self.import_fixture()
        channels = outcome.dataset.channels

        self.assertEqual(
            tuple(channel.original_name for channel in channels),
            (
                "Elapsed Time",
                "Lat (Degrees)",
                "Lon (Degrees)",
                "Altitude (meters)",
                "Velocity (MPH)",
                "Lap",
            ),
        )
        self.assertEqual(
            tuple(channel.identifier for channel in channels),
            tuple(channel.original_name for channel in channels),
        )
        self.assertEqual(
            tuple(channel.metadata.unit for channel in channels),
            ("s", "deg", "deg", "m", "mph", ""),
        )
        self.assertTrue(all(channel.metadata.sample_rate_hz == 10.0 for channel in channels))

    def test_elapsed_time_drives_timestamps_and_source_cells_remain_lexical(self) -> None:
        outcome = self.import_fixture()
        elapsed = outcome.dataset.channel("Elapsed Time")
        speed = outcome.dataset.channel("Velocity (MPH)")

        self.assertEqual(elapsed.series.timestamps_s[0], 0.0)
        self.assertEqual(elapsed.series.timestamps_s[-1], 196.1)
        self.assertEqual(len(elapsed.series.timestamps_s), 1962)
        self.assertIs(speed.series.timestamps_s, elapsed.series.timestamps_s)

        self.assertEqual(elapsed.series.values[0], "0.0")
        self.assertEqual(speed.series.values[0], "4.6975662133142455")
        self.assertEqual(speed.metadata.unit, "mph")

    def test_source_lap_values_are_preserved_without_context_invention(self) -> None:
        outcome = self.import_fixture()
        lap = outcome.dataset.channel("Lap")

        self.assertEqual(lap.series.values.count("1"), 717)
        self.assertEqual(lap.series.values.count("2"), 766)
        self.assertEqual(lap.series.values.count("3"), 479)

        identifiers = {channel.identifier for channel in outcome.dataset.channels}
        self.assertNotIn("lap.distance", identifiers)
        self.assertFalse(any("distance" in identifier.lower() for identifier in identifiers))

    def test_import_does_not_modify_source_bytes(self) -> None:
        before = TRAQMATE_FIXTURE.read_bytes()

        self.import_fixture()

        self.assertEqual(TRAQMATE_FIXTURE.read_bytes(), before)

    def test_provenance_fingerprint_is_deterministic(self) -> None:
        expected = "sha256:" + hashlib.sha256(TRAQMATE_FIXTURE.read_bytes()).hexdigest()

        first = self.importer.import_source(
            TRAQMATE_FIXTURE,
            imported_at=FIXED_TIME,
        )
        second = self.importer.import_source(
            TRAQMATE_FIXTURE,
            imported_at=datetime(2026, 9, 23, 13, 0, tzinfo=UTC),
        )

        self.assertIsInstance(first, ImportSuccess)
        self.assertIsInstance(second, ImportSuccess)
        assert isinstance(first, ImportSuccess)
        assert isinstance(second, ImportSuccess)

        self.assertEqual(first.dataset.provenance.content_fingerprint, expected)
        self.assertEqual(second.dataset.provenance.content_fingerprint, expected)
        self.assertEqual(first.dataset.channels, second.dataset.channels)
        self.assertNotEqual(
            first.dataset.provenance.imported_at,
            second.dataset.provenance.imported_at,
        )

    def test_csv_adapter_arbitration_is_registration_order_independent(self) -> None:
        adapters = (
            OMECsvProfileImporter(),
            MoTeCCSVImporter(),
            self.importer,
            IRacingIBTImporter(),
        )
        reverse_adapters = tuple(reversed(adapters))

        for configured in (adapters, reverse_adapters):
            service = TelemetryImportService(configured)

            traqmate = service.import_file(TRAQMATE_FIXTURE, imported_at=FIXED_TIME)
            motec = service.import_file(MOTEC_FIXTURE, imported_at=FIXED_TIME)
            ome = service.import_file(OME_FIXTURE, imported_at=FIXED_TIME)

            self.assertIsInstance(traqmate, ImportSuccess)
            self.assertIsInstance(motec, ImportSuccess)
            self.assertIsInstance(ome, ImportSuccess)
            assert isinstance(traqmate, ImportSuccess)
            assert isinstance(motec, ImportSuccess)
            assert isinstance(ome, ImportSuccess)

            self.assertEqual(
                traqmate.dataset.source.source_type,
                "traqmate-trackvision-csv",
            )
            self.assertEqual(motec.dataset.source.source_type, "motec-csv")
            self.assertEqual(ome.dataset.source.source_type, "ome-csv-profile")

    def test_arbitrary_csv_is_not_claimed(self) -> None:
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

    def test_unsupported_traqmate_version_fails_explicitly(self) -> None:
        source = """Format,Traqmate Trackvision,V3
Sample Rate (samps/sec),10
Elapsed Time,Velocity (MPH),Lap
0.0,10,1
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsupported.csv"
            path.write_text(source, encoding="utf-8")
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("V2", outcome.message)

    def test_missing_sample_rate_remains_unknown_instead_of_inferred(self) -> None:
        source = """Format,Traqmate Trackvision,V2
Track,Test
Elapsed Time,Velocity (MPH),Lap
0.0,10,1
0.1,11,1
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-rate.csv"
            path.write_text(source, encoding="utf-8")
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        self.assertIsNone(outcome.dataset.channel("Velocity (MPH)").metadata.sample_rate_hz)
        self.assertIn("sample_rate_hz", outcome.summary.missing_metadata)
        self.assertIn(
            "missing_sample_rate",
            {issue.code for issue in outcome.summary.warnings},
        )

    def test_decreasing_time_imports_then_validation_blocks_it(self) -> None:
        source = """Format,Traqmate Trackvision,V2
Sample Rate (samps/sec),10
Elapsed Time,Velocity (MPH),Lap
1.0,10,1
0.9,11,1
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "decreasing.csv"
            path.write_text(source, encoding="utf-8")
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)

        validation = self.validator.validate(outcome.dataset)

        self.assertTrue(validation.has_blocking_issues)
        issue = next(issue for issue in validation.issues if issue.code == "decreasing_timestamp")
        self.assertEqual(issue.severity, ValidationSeverity.BLOCKING)

    def test_wrong_row_width_fails_explicitly(self) -> None:
        source = """Format,Traqmate Trackvision,V2
Elapsed Time,Velocity (MPH),Lap
0.0,10,1
0.1,11
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad-width.csv"
            path.write_text(source, encoding="utf-8")
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("fields", outcome.message.lower())

    def test_empty_or_non_finite_elapsed_time_fails_explicitly(self) -> None:
        cases = {
            "empty": "",
            "nan": "nan",
            "infinity": "inf",
        }

        for name, time_value in cases.items():
            with self.subTest(name=name):
                source = (
                    "Format,Traqmate Trackvision,V2\n"
                    "Elapsed Time,Velocity (MPH),Lap\n"
                    f"{time_value},10,1\n"
                )
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / f"{name}.csv"
                    path.write_text(source, encoding="utf-8")
                    outcome = self.importer.import_source(
                        path,
                        imported_at=FIXED_TIME,
                    )

                self.assertIsInstance(outcome, ImportFailure)
                assert isinstance(outcome, ImportFailure)
                self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)

    def test_empty_data_table_fails_explicitly(self) -> None:
        source = """Format,Traqmate Trackvision,V2
Elapsed Time,Velocity (MPH),Lap
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
