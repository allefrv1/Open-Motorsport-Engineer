from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from ome.application.lap_window import (
    SourceLapWindowIssueCode,
    SourceLapWindowNotReady,
    SourceLapWindowRequest,
    SourceLapWindowSuccess,
    TraqmateLapWindowSelector,
)
from ome.domain import SampleSeries
from ome.ingestion import ImportSuccess, OMECsvProfileImporter, TraqmateTrackvisionCSVImporter

ROOT = Path(__file__).resolve().parents[2]
PORTLAND_FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-portland-laps-4-5.csv"
OME_FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"
FIXED_TIME = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


def import_portland():
    outcome = TraqmateTrackvisionCSVImporter().import_source(
        PORTLAND_FIXTURE,
        imported_at=FIXED_TIME,
    )
    assert isinstance(outcome, ImportSuccess)
    return outcome.dataset


def import_ome():
    outcome = OMECsvProfileImporter().import_source(
        OME_FIXTURE,
        imported_at=FIXED_TIME,
    )
    assert isinstance(outcome, ImportSuccess)
    return outcome.dataset


class Plan025PhysicalCarLapWindowSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.selector = TraqmateLapWindowSelector()
        self.dataset = import_portland()

    def select(self, lap_number: int):
        return self.selector.select(
            SourceLapWindowRequest(
                dataset=self.dataset,
                source_lap_number=lap_number,
            )
        )

    def test_lap_four_exact_complete_window(self) -> None:
        outcome = self.select(4)

        self.assertIsInstance(outcome, SourceLapWindowSuccess)
        assert isinstance(outcome, SourceLapWindowSuccess)
        window = outcome.window

        self.assertEqual(window.dataset_fingerprint, self.dataset.provenance.content_fingerprint)
        self.assertEqual(window.source_identity, "traqmate-portland-laps-4-5.csv")
        self.assertEqual(window.source_type, "traqmate-trackvision-csv")
        self.assertEqual(window.lap_channel_identifier, "Lap")
        self.assertEqual(window.time_channel_identifier, "Elapsed Time")
        self.assertEqual(window.source_lap_number, 4)
        self.assertEqual(window.start_index, 0)
        self.assertEqual(window.end_index_exclusive, 3618)
        self.assertEqual(window.closing_boundary_index, 3618)
        self.assertEqual(window.sample_count, 3618)
        self.assertEqual(window.start_elapsed_s, 885.9)
        self.assertEqual(window.closing_elapsed_s, 976.35)

    def test_lap_five_exact_complete_window(self) -> None:
        outcome = self.select(5)

        self.assertIsInstance(outcome, SourceLapWindowSuccess)
        assert isinstance(outcome, SourceLapWindowSuccess)
        window = outcome.window

        self.assertEqual(window.source_lap_number, 5)
        self.assertEqual(window.start_index, 3618)
        self.assertEqual(window.end_index_exclusive, 7249)
        self.assertEqual(window.closing_boundary_index, 7249)
        self.assertEqual(window.sample_count, 3631)
        self.assertEqual(window.start_elapsed_s, 976.35)
        self.assertEqual(window.closing_elapsed_s, 1067.125)

    def test_lap_six_is_explicitly_incomplete(self) -> None:
        outcome = self.select(6)

        self.assertIsInstance(outcome, SourceLapWindowNotReady)
        assert isinstance(outcome, SourceLapWindowNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (SourceLapWindowIssueCode.INCOMPLETE_LAP,),
        )

    def test_absent_requested_lap_is_explicitly_not_ready(self) -> None:
        outcome = self.select(99)

        self.assertIsInstance(outcome, SourceLapWindowNotReady)
        assert isinstance(outcome, SourceLapWindowNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (SourceLapWindowIssueCode.MISSING_LAP_MARKER,),
        )

    def test_duplicate_requested_marker_is_ambiguous_not_guessed(self) -> None:
        lap = self.dataset.channel("Lap")
        values = list(lap.series.values)
        self.assertIsNone(values[100])
        values[100] = "4"
        duplicate_lap = replace(
            lap,
            series=SampleSeries(
                timestamps_s=lap.series.timestamps_s,
                values=tuple(values),
            ),
        )
        dataset = replace(
            self.dataset,
            channels=tuple(
                duplicate_lap if channel.identifier == "Lap" else channel
                for channel in self.dataset.channels
            ),
        )

        outcome = self.selector.select(
            SourceLapWindowRequest(
                dataset=dataset,
                source_lap_number=4,
            )
        )

        self.assertIsInstance(outcome, SourceLapWindowNotReady)
        assert isinstance(outcome, SourceLapWindowNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (SourceLapWindowIssueCode.AMBIGUOUS_LAP_MARKER,),
        )

    def test_repeated_selection_is_deterministic(self) -> None:
        request = SourceLapWindowRequest(dataset=self.dataset, source_lap_number=4)

        first = self.selector.select(request)
        second = self.selector.select(request)

        self.assertEqual(first, second)

    def test_selection_does_not_mutate_dataset_or_fill_sparse_lap_cells(self) -> None:
        channels_before = self.dataset.channels
        lap = self.dataset.channel("Lap")
        lap_values_before = lap.series.values

        outcome = self.select(4)

        self.assertIsInstance(outcome, SourceLapWindowSuccess)
        self.assertIs(self.dataset.channels, channels_before)
        self.assertIs(self.dataset.channel("Lap").series.values, lap_values_before)
        self.assertEqual(
            tuple(
                (index, value) for index, value in enumerate(lap_values_before) if value is not None
            ),
            (
                (0, "4"),
                (3618, "5"),
                (7249, "6"),
            ),
        )

    def test_unsupported_source_type_is_not_ready(self) -> None:
        dataset = import_ome()

        outcome = self.selector.select(
            SourceLapWindowRequest(
                dataset=dataset,
                source_lap_number=1,
            )
        )

        self.assertIsInstance(outcome, SourceLapWindowNotReady)
        assert isinstance(outcome, SourceLapWindowNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (SourceLapWindowIssueCode.UNSUPPORTED_SOURCE_TYPE,),
        )

    def test_missing_lap_channel_is_not_ready(self) -> None:
        dataset = replace(
            self.dataset,
            channels=tuple(
                channel for channel in self.dataset.channels if channel.identifier != "Lap"
            ),
        )

        outcome = self.selector.select(
            SourceLapWindowRequest(
                dataset=dataset,
                source_lap_number=4,
            )
        )

        self.assertIsInstance(outcome, SourceLapWindowNotReady)
        assert isinstance(outcome, SourceLapWindowNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (SourceLapWindowIssueCode.MISSING_LAP_CHANNEL,),
        )

    def test_missing_elapsed_time_channel_is_not_ready(self) -> None:
        dataset = replace(
            self.dataset,
            channels=tuple(
                channel for channel in self.dataset.channels if channel.identifier != "Elapsed Time"
            ),
        )

        outcome = self.selector.select(
            SourceLapWindowRequest(
                dataset=dataset,
                source_lap_number=4,
            )
        )

        self.assertIsInstance(outcome, SourceLapWindowNotReady)
        assert isinstance(outcome, SourceLapWindowNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (SourceLapWindowIssueCode.MISSING_TIME_CHANNEL,),
        )

    def test_missing_dataset_fingerprint_is_not_ready(self) -> None:
        dataset = replace(
            self.dataset,
            provenance=replace(
                self.dataset.provenance,
                content_fingerprint="",
            ),
        )

        outcome = self.selector.select(
            SourceLapWindowRequest(
                dataset=dataset,
                source_lap_number=4,
            )
        )

        self.assertIsInstance(outcome, SourceLapWindowNotReady)
        assert isinstance(outcome, SourceLapWindowNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (SourceLapWindowIssueCode.MISSING_PROVENANCE,),
        )


if __name__ == "__main__":
    unittest.main()
