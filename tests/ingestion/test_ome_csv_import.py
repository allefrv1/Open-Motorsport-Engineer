from __future__ import annotations

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from ome.ingestion import (
    ImportFailure,
    ImportFailureCode,
    ImportSuccess,
    OMECsvProfileImporter,
    TelemetryImportService,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"
FIXED_TIME = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)


class Req001OmeCsvImportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.importer = OMECsvProfileImporter()
        self.service = TelemetryImportService([self.importer])

    def import_fixture(self) -> ImportSuccess:
        outcome = self.service.import_file(FIXTURE, imported_at=FIXED_TIME)
        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        return outcome

    def test_ac001_supported_profile_import_succeeds(self) -> None:
        outcome = self.import_fixture()

        self.assertEqual(outcome.dataset.source.source_type, "ome-csv-profile")
        self.assertEqual(len(outcome.dataset.channels), 7)
        self.assertEqual(outcome.summary.source_identity, "basic-lap.csv")

    def test_ac002_import_does_not_modify_source_files(self) -> None:
        sidecar = FIXTURE.with_suffix(".ome.json")
        before_csv = FIXTURE.read_bytes()
        before_sidecar = sidecar.read_bytes()

        self.import_fixture()

        self.assertEqual(FIXTURE.read_bytes(), before_csv)
        self.assertEqual(sidecar.read_bytes(), before_sidecar)

    def test_ac003_provenance_identifies_source_and_importer(self) -> None:
        outcome = self.import_fixture()
        provenance = outcome.dataset.provenance

        self.assertEqual(provenance.original_source_name, "basic-lap.csv")
        self.assertEqual(provenance.source_format, "ome-csv-profile")
        self.assertEqual(provenance.source_system, "OME")
        self.assertEqual(provenance.importer_id, "ome.csv-profile")
        self.assertEqual(provenance.importer_version, "0.1.0")
        self.assertTrue(provenance.content_fingerprint.startswith("sha256:"))
        self.assertGreater(provenance.source_size_bytes, 0)

    def test_ac004_channel_inventory_preserves_source_identity(self) -> None:
        outcome = self.import_fixture()
        channels = {channel.identifier: channel for channel in outcome.dataset.channels}

        self.assertEqual(
            tuple(channels),
            (
                "speed_src",
                "throttle_src",
                "brake_src",
                "steering_src",
                "rpm_src",
                "gear_src",
                "lap_src",
            ),
        )
        self.assertEqual(channels["speed_src"].original_name, "Synthetic Vehicle Speed")
        self.assertEqual(channels["gear_src"].original_name, "Synthetic Gear")

    def test_ac005_source_metadata_is_preserved(self) -> None:
        outcome = self.import_fixture()
        speed = outcome.dataset.channel("speed_src")

        self.assertEqual(speed.metadata.unit, "m/s")
        self.assertEqual(speed.metadata.sample_rate_hz, 10.0)
        self.assertEqual(speed.metadata.data_type, "float")
        self.assertEqual(outcome.dataset.source.source_system, "OME")
        self.assertEqual(
            outcome.dataset.source.metadata["context"],
            {"session": "Harness fixture", "lap": 1},
        )
        self.assertEqual(
            outcome.summary.source_metadata["context"],
            {"session": "Harness fixture", "lap": 1},
        )

    def test_ac006_missing_metadata_remains_unknown_and_visible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "missing-unit.csv"
            csv_path.write_text("time_s,speed_src\n0.0,10.0\n0.1,11.0\n", encoding="utf-8")
            sidecar = {
                "ome_csv_version": "0.1",
                "source": {"description": "Missing metadata fixture"},
                "channels": {
                    "speed_src": {
                        "source_name": "Speed",
                    }
                },
            }
            csv_path.with_suffix(".ome.json").write_text(
                json.dumps(sidecar),
                encoding="utf-8",
            )

            outcome = self.service.import_file(csv_path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        channel = outcome.dataset.channel("speed_src")
        self.assertIsNone(channel.metadata.unit)
        self.assertIsNone(channel.metadata.sample_rate_hz)
        self.assertIn("channels.speed_src.unit", outcome.summary.missing_metadata)
        self.assertIn("sample_rate_hz", outcome.summary.missing_metadata)

    def test_ac007_unsupported_source_returns_explicit_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.ibt"
            path.write_bytes(b"not-an-ibt")

            outcome = self.service.import_file(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.UNSUPPORTED_SOURCE)

    def test_ac008_unreadable_source_returns_read_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "broken.csv"
            csv_path.write_bytes(b"\xff\xfe\xfd")
            sidecar = {
                "ome_csv_version": "0.1",
                "source": {"description": "Read failure fixture"},
                "channels": {"speed_src": {"source_name": "Speed", "unit": "m/s"}},
            }
            csv_path.with_suffix(".ome.json").write_text(
                json.dumps(sidecar),
                encoding="utf-8",
            )

            outcome = self.service.import_file(csv_path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.READ_ERROR)

    def test_ac009_import_does_not_normalize_channel_identity_or_values(self) -> None:
        outcome = self.import_fixture()
        speed = outcome.dataset.channel("speed_src")
        gear = outcome.dataset.channel("gear_src")

        self.assertEqual(speed.identifier, "speed_src")
        self.assertEqual(speed.original_name, "Synthetic Vehicle Speed")
        self.assertEqual(speed.series.values[:3], ("18.0", "18.8", "19.7"))
        self.assertEqual(gear.series.values[:3], ("2", "2", "2"))

    def test_ac010_semantic_import_is_reproducible(self) -> None:
        first = self.service.import_file(
            FIXTURE,
            imported_at=datetime(2026, 9, 22, 12, 0, tzinfo=UTC),
        )
        second = self.service.import_file(
            FIXTURE,
            imported_at=datetime(2026, 9, 22, 13, 0, tzinfo=UTC),
        )

        self.assertIsInstance(first, ImportSuccess)
        self.assertIsInstance(second, ImportSuccess)
        assert isinstance(first, ImportSuccess)
        assert isinstance(second, ImportSuccess)

        self.assertEqual(
            first.dataset.provenance.content_fingerprint,
            second.dataset.provenance.content_fingerprint,
        )
        self.assertEqual(first.dataset.channels, second.dataset.channels)
        self.assertEqual(first.summary, second.summary)
        self.assertNotEqual(
            first.dataset.provenance.imported_at,
            second.dataset.provenance.imported_at,
        )

    def test_missing_sidecar_is_invalid_profile_when_importer_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / "profile.csv"
            csv_path.write_text("time_s,speed_src\n0.0,10\n", encoding="utf-8")

            outcome = self.importer.import_source(csv_path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)

    def test_non_monotonic_profile_time_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "bad-time.csv"
            csv_path.write_text("time_s,speed_src\n1.0,10\n0.5,11\n", encoding="utf-8")
            sidecar = {
                "ome_csv_version": "0.1",
                "source": {"description": "Invalid time fixture"},
                "channels": {"speed_src": {"source_name": "Speed", "unit": "m/s"}},
            }
            csv_path.with_suffix(".ome.json").write_text(
                json.dumps(sidecar),
                encoding="utf-8",
            )

            outcome = self.importer.import_source(csv_path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("strictly increasing", outcome.message)

    def test_sidecar_channel_order_does_not_define_source_channel_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "mismatch.csv"
            csv_path.write_text("time_s,a,b\n0.0,1,2\n", encoding="utf-8")
            sidecar = {
                "ome_csv_version": "0.1",
                "source": {"description": "Channel mismatch fixture"},
                "channels": {
                    "b": {"source_name": "B"},
                    "a": {"source_name": "A"},
                },
            }
            csv_path.with_suffix(".ome.json").write_text(
                json.dumps(sidecar),
                encoding="utf-8",
            )

            outcome = self.importer.import_source(csv_path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        self.assertEqual(
            tuple(channel.identifier for channel in outcome.dataset.channels),
            ("a", "b"),
        )

    def test_empty_profile_has_explicit_invalid_profile_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "empty.csv"
            csv_path.write_text("time_s,speed_src\n", encoding="utf-8")
            sidecar = {
                "ome_csv_version": "0.1",
                "source": {"description": "Empty fixture"},
                "channels": {"speed_src": {"source_name": "Speed", "unit": "m/s"}},
            }
            csv_path.with_suffix(".ome.json").write_text(
                json.dumps(sidecar),
                encoding="utf-8",
            )

            outcome = self.importer.import_source(csv_path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("at least one sample row", outcome.message)


if __name__ == "__main__":
    unittest.main()
