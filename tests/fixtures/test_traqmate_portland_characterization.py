from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = (
    ROOT
    / "fixtures"
    / "public"
    / "exit-speed"
    / "traqmate-portland-laps-4-5.csv"
)
MANIFEST = ROOT / "fixtures" / "public" / "manifest.json"

EXPECTED_HEADER = (
    "GPS Reading",
    "GPS Time",
    "GPS Weeks",
    "Elapsed Time",
    "Lat (Degrees)",
    "Lon (Degrees)",
    "Lat (feet)",
    "Lon (feet)",
    "Altitude (feet)",
    "Temperature (degrees F)",
    "EastVel",
    "NorthVel",
    "VertVel",
    "Velocity (MPH)",
    "Heading(Deg)",
    "XGs",
    "YGs",
    "RPMs",
    "D4",
    "D5",
    "A0",
    "A1",
    "A2",
    "A3",
    "Gear",
    "Brake (calc)",
    "Accel (calc)",
    "Lap",
)


class TraqmatePortlandFixtureCharacterizationTests(unittest.TestCase):
    def read_source(self) -> tuple[list[list[str]], list[str], list[list[str]]]:
        with FIXTURE.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))

        header_index = next(
            index
            for index, row in enumerate(rows)
            if row and tuple(cell.strip() for cell in row) == EXPECTED_HEADER
        )
        return rows[:header_index], rows[header_index], rows[header_index + 1 :]

    def test_fixture_shape_is_stable_and_preserves_extended_layout(self) -> None:
        preamble, raw_header, data_rows = self.read_source()

        self.assertEqual(len(preamble), 16)
        self.assertEqual(len(raw_header), 28)
        self.assertEqual(tuple(cell.strip() for cell in raw_header), EXPECTED_HEADER)
        self.assertEqual(len(data_rows), 7250)

        self.assertEqual(tuple(cell.strip() for cell in preamble[0][:3]), (
            "Format",
            "Traqmate Trackvision",
            "V2",
        ))
        sample_rate = next(
            row for row in preamble if row and row[0].strip() == "Sample Rate (samps/sec)"
        )
        self.assertEqual(sample_rate[1].strip(), "40")

    def test_elapsed_gps_and_lap_column_positions_match_real_source(self) -> None:
        _preamble, raw_header, _data_rows = self.read_source()
        header = tuple(cell.strip() for cell in raw_header)

        self.assertEqual(header.index("Elapsed Time"), 3)
        self.assertEqual(header.index("Lat (Degrees)"), 4)
        self.assertEqual(header.index("Lon (Degrees)"), 5)
        self.assertEqual(header.index("Lap"), 27)

    def test_sparse_lap_markers_are_preserved_exactly(self) -> None:
        _preamble, raw_header, data_rows = self.read_source()
        header = tuple(cell.strip() for cell in raw_header)
        lap_index = header.index("Lap")
        time_index = header.index("Elapsed Time")

        markers = tuple(
            (index, row[lap_index], row[time_index])
            for index, row in enumerate(data_rows)
            if row[lap_index] != ""
        )

        self.assertEqual(
            markers,
            (
                (0, "4", "885.900000"),
                (3618, "5", "976.350000"),
                (7249, "6", "1067.125000"),
            ),
        )

    def test_manifest_pins_upstream_and_derived_fixture_identity(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        entry = next(
            item
            for item in manifest["fixtures"]
            if item["id"] == "exit-speed-traqmate-portland-laps-4-5"
        )

        self.assertEqual(
            entry["source_git_blob_sha"],
            "499762a9044ea0b09a698509e84681877baf7897",
        )
        self.assertEqual(
            entry["fixture_git_blob_sha"],
            "0c9c5f134ba9237a36329ec165b07ec37d63fbcd",
        )
        self.assertEqual(entry["source_data_row_index_zero_based"], [11360, 18609])
        self.assertEqual(entry["source_csv_file_lines_one_based"], [11378, 18627])
        self.assertEqual(entry["selected_data_rows"], 7250)
        self.assertEqual(entry["selected_lap_markers"], [4, 5, 6])
        self.assertEqual(entry["license"], "Apache-2.0")


if __name__ == "__main__":
    unittest.main()
