from __future__ import annotations

import hashlib
import struct
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from ome.ingestion import (
    IRacingIBTImporter,
    ImportFailure,
    ImportFailureCode,
    ImportSuccess,
    OMECsvProfileImporter,
    TelemetryImportService,
)
from tests.support.iracing_ibt_fixture import (
    DEFAULT_VARIABLES,
    DISK_SUBHEADER_SIZE,
    HEADER_SIZE,
    IRSDK_VERSION,
    VAR_HEADER_SIZE,
    build_array_variable_fixture,
    build_ibt_bytes,
    build_missing_session_time_fixture,
)

FIXED_TIME = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)


class Plan007IRacingIBTImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.importer = IRacingIBTImporter()
        self.service = TelemetryImportService(
            [OMECsvProfileImporter(), self.importer]
        )

    def write_fixture(self, directory: str, payload: bytes, name: str = "synthetic.ibt") -> Path:
        path = Path(directory) / name
        path.write_bytes(payload)
        return path

    def import_fixture(self) -> ImportSuccess:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory, build_ibt_bytes())
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        return outcome

    def test_fixture_builder_matches_reviewed_fixed_layout(self) -> None:
        payload = build_ibt_bytes()

        self.assertGreater(len(payload), HEADER_SIZE + DISK_SUBHEADER_SIZE)
        header = struct.unpack_from("<12i", payload, 0)
        self.assertEqual(header[0], IRSDK_VERSION)
        self.assertEqual(header[2], 60)
        self.assertEqual(header[6], len(DEFAULT_VARIABLES))
        self.assertEqual(header[7] % 16, 0)

        first_var_offset = header[7]
        second_var_offset = first_var_offset + VAR_HEADER_SIZE
        first_name = payload[first_var_offset + 16 : first_var_offset + 48]
        second_name = payload[second_var_offset + 16 : second_var_offset + 48]
        self.assertEqual(first_name.split(b"\x00", 1)[0], b"SessionTime")
        self.assertEqual(second_name.split(b"\x00", 1)[0], b"Speed")

    def test_supported_ibt_import_succeeds_with_source_channels(self) -> None:
        outcome = self.import_fixture()

        self.assertEqual(outcome.dataset.source.source_type, "iracing-ibt")
        self.assertEqual(outcome.dataset.source.source_system, "iRacing")
        self.assertEqual(outcome.dataset.source.format_version, "2")
        self.assertEqual(
            tuple(channel.identifier for channel in outcome.dataset.channels),
            tuple(variable.name for variable in DEFAULT_VARIABLES),
        )

    def test_channel_metadata_and_source_semantics_are_preserved(self) -> None:
        outcome = self.import_fixture()
        speed = outcome.dataset.channel("Speed")
        steering = outcome.dataset.channel("SteeringWheelAngle")

        self.assertEqual(speed.original_name, "Speed")
        self.assertEqual(speed.metadata.description, "GPS vehicle speed")
        self.assertEqual(speed.metadata.unit, "m/s")
        self.assertEqual(speed.metadata.sample_rate_hz, 60.0)
        self.assertEqual(speed.metadata.data_type, "float")
        self.assertEqual(speed.metadata.source_attributes["iracing_type_code"], 4)
        self.assertEqual(speed.metadata.source_attributes["iracing_count"], 1)

        self.assertEqual(steering.original_name, "SteeringWheelAngle")
        self.assertEqual(steering.metadata.unit, "rad")

    def test_session_time_is_preserved_and_used_as_explicit_timestamp_series(self) -> None:
        outcome = self.import_fixture()
        session_time = outcome.dataset.channel("SessionTime")
        speed = outcome.dataset.channel("Speed")

        self.assertEqual(session_time.series.values[0], 10.0)
        self.assertAlmostEqual(session_time.series.values[1], 10.0166666667)
        self.assertIs(speed.series.timestamps_s, session_time.series.timestamps_s)
        self.assertEqual(speed.series.timestamps_s[0], 10.0)
        self.assertAlmostEqual(speed.series.timestamps_s[2], 10.0333333333)
        self.assertEqual(speed.series.values, (50.0, 51.0, 52.0))

    def test_typed_source_values_are_preserved_without_normalization(self) -> None:
        outcome = self.import_fixture()

        throttle = outcome.dataset.channel("Throttle")
        gear = outcome.dataset.channel("Gear")
        lap = outcome.dataset.channel("Lap")

        self.assertAlmostEqual(throttle.series.values[0], 0.8)
        self.assertEqual(throttle.metadata.unit, "%")
        self.assertEqual(gear.series.values, (3, 3, 4))
        self.assertEqual(lap.series.values, (2, 2, 2))

    def test_header_and_session_info_metadata_are_preserved(self) -> None:
        outcome = self.import_fixture()
        metadata = outcome.dataset.source.metadata

        self.assertEqual(metadata["iracing_version"], 2)
        self.assertEqual(metadata["tick_rate_hz"], 60)
        self.assertEqual(metadata["session_record_count"], 3)
        self.assertEqual(metadata["session_lap_count"], 1)
        self.assertIn("Synthetic Test Circuit", metadata["session_info"])

    def test_provenance_and_fingerprint_are_deterministic(self) -> None:
        payload = build_ibt_bytes()
        expected_fingerprint = f"sha256:{hashlib.sha256(payload).hexdigest()}"

        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory, payload)
            first = self.importer.import_source(path, imported_at=FIXED_TIME)
            second = self.importer.import_source(
                path,
                imported_at=datetime(2026, 9, 22, 13, 0, tzinfo=UTC),
            )

        self.assertIsInstance(first, ImportSuccess)
        self.assertIsInstance(second, ImportSuccess)
        assert isinstance(first, ImportSuccess)
        assert isinstance(second, ImportSuccess)

        self.assertEqual(first.dataset.provenance.content_fingerprint, expected_fingerprint)
        self.assertEqual(second.dataset.provenance.content_fingerprint, expected_fingerprint)
        self.assertEqual(first.dataset.channels, second.dataset.channels)
        self.assertNotEqual(
            first.dataset.provenance.imported_at,
            second.dataset.provenance.imported_at,
        )

    def test_import_service_selects_ibt_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory, build_ibt_bytes())
            outcome = self.service.import_file(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        self.assertEqual(outcome.dataset.provenance.importer_id, "iracing.ibt")

    def test_truncated_ibt_fails_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory, build_ibt_bytes()[:80])
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("header", outcome.message.lower())

    def test_unsupported_irsdk_version_fails_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory, build_ibt_bytes(version=99))
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("version", outcome.message.lower())

    def test_missing_explicit_session_time_fails_instead_of_inference(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory, build_missing_session_time_fixture())
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("SessionTime", outcome.message)

    def test_array_variable_is_rejected_instead_of_flattened_or_discarded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory, build_array_variable_fixture())
            outcome = self.importer.import_source(path, imported_at=FIXED_TIME)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.INVALID_PROFILE)
        self.assertIn("array", outcome.message.lower())

    def test_non_ibt_extension_is_not_claimed_by_adapter(self) -> None:
        self.assertFalse(self.importer.supports(Path("telemetry.bin")))
        self.assertTrue(self.importer.supports(Path("telemetry.ibt")))


if __name__ == "__main__":
    unittest.main()
