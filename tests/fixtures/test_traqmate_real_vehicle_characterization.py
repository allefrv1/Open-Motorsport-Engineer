from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from ome.ingestion import (
    IRacingIBTImporter,
    ImportFailure,
    ImportFailureCode,
    MoTeCCSVImporter,
    OMECsvProfileImporter,
    TelemetryImportService,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-parking-lot.csv"


class TraqmateRealVehicleCharacterizationTests(unittest.TestCase):
    def read_source(self) -> tuple[list[list[str]], list[str], list[list[str]]]:
        with FIXTURE.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))

        header_index = next(
            index for index, row in enumerate(rows) if row and row[0] == "Elapsed Time"
        )
        return rows[:header_index], rows[header_index], rows[header_index + 1 :]

    def test_fixture_shape_is_stable_real_vehicle_evidence(self) -> None:
        preamble, header, data_rows = self.read_source()

        self.assertEqual(
            preamble,
            [
                ["Format", "Traqmate Trackvision", "V2"],
                ["Track", "Test Parking Lot"],
                ["Vehicle", "CORRADO"],
                ["Driver", "DJ"],
                ["Starting Date", "2020/06/11"],
                ["Starting Time", "22:16:027"],
                ["Sample Rate (samps/sec)", "10"],
                ["Duration (secs)", "196"],
            ],
        )
        self.assertEqual(
            header,
            [
                "Elapsed Time",
                "Lat (Degrees)",
                "Lon (Degrees)",
                "Altitude (meters)",
                "Velocity (MPH)",
                "Lap",
            ],
        )
        self.assertEqual(len(data_rows), 1962)

    def test_elapsed_time_and_source_laps_are_explicit(self) -> None:
        _preamble, header, data_rows = self.read_source()
        time_index = header.index("Elapsed Time")
        lap_index = header.index("Lap")

        times = tuple(float(row[time_index]) for row in data_rows)
        laps = tuple(row[lap_index] for row in data_rows)

        self.assertEqual(times[0], 0.0)
        self.assertEqual(times[-1], 196.1)
        self.assertTrue(all(current > previous for previous, current in zip(times, times[1:])))

        self.assertEqual(set(laps), {"1", "2", "3"})
        self.assertEqual(laps.count("1"), 717)
        self.assertEqual(laps.count("2"), 766)
        self.assertEqual(laps.count("3"), 479)

        time_steps = tuple(
            round(current - previous, 10)
            for previous, current in zip(times, times[1:])
        )
        self.assertEqual(set(time_steps), {0.1})

        transitions = tuple(
            (laps[index - 1], laps[index], times[index])
            for index in range(1, len(laps))
            if laps[index] != laps[index - 1]
        )
        self.assertEqual(
            transitions,
            (
                ("1", "2", 71.7),
                ("2", "3", 148.3),
            ),
        )

    def test_fixture_has_gps_and_velocity_but_no_distance_channel(self) -> None:
        _preamble, header, _data_rows = self.read_source()

        self.assertIn("Lat (Degrees)", header)
        self.assertIn("Lon (Degrees)", header)
        self.assertIn("Velocity (MPH)", header)
        self.assertFalse(any("distance" in name.lower() for name in header))

    def test_pre_plan021_importers_do_not_silently_claim_traqmate_csv(self) -> None:
        importers = (
            OMECsvProfileImporter(),
            MoTeCCSVImporter(),
            IRacingIBTImporter(),
        )

        for importer in importers:
            with self.subTest(importer=importer.importer_id):
                self.assertFalse(importer.supports(FIXTURE))

        outcome = TelemetryImportService(importers).import_file(FIXTURE)

        self.assertIsInstance(outcome, ImportFailure)
        assert isinstance(outcome, ImportFailure)
        self.assertEqual(outcome.code, ImportFailureCode.UNSUPPORTED_SOURCE)
        self.assertIn("No telemetry importer supports source", outcome.message)

    def test_same_csv_without_ome_sidecar_remains_unclaimed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "traqmate.csv"
            copy.write_bytes(FIXTURE.read_bytes())

            self.assertFalse(OMECsvProfileImporter().supports(copy))
            self.assertFalse(MoTeCCSVImporter().supports(copy))


if __name__ == "__main__":
    unittest.main()
