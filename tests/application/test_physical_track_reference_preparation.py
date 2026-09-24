from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from ome.application import SourceLapWindowRequest, TraqmateLapWindowSelector
from ome.application.physical_track_reference import (
    PhysicalTrackReferencePreparationIssueCode,
    PhysicalTrackReferencePreparationNotReady,
    PhysicalTrackReferencePreparationRequest,
    PhysicalTrackReferencePreparationService,
    PhysicalTrackReferencePreparationSuccess,
)
from ome.domain import CanonicalConcept, ImportedTelemetryDataset, SampleSeries
from ome.evidence import LapEvidenceContext
from ome.ingestion import ImportSuccess, TraqmateTrackvisionCSVImporter

ROOT = Path(__file__).resolve().parents[2]
PORTLAND_FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-portland-laps-4-5.csv"
FIXED_TIME = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


def import_portland() -> ImportedTelemetryDataset:
    outcome = TraqmateTrackvisionCSVImporter().import_source(
        PORTLAND_FIXTURE,
        imported_at=FIXED_TIME,
    )
    assert isinstance(outcome, ImportSuccess)
    return outcome.dataset


def context(dataset: ImportedTelemetryDataset, lap_number: int) -> LapEvidenceContext:
    return LapEvidenceContext(
        dataset_fingerprint=dataset.provenance.content_fingerprint,
        session_identifier="session:portland",
        run_identifier="run:portland",
        lap_identifier=f"source-lap:{lap_number}",
    )


def selected_windows(dataset: ImportedTelemetryDataset):
    selector = TraqmateLapWindowSelector()
    reference = selector.select(SourceLapWindowRequest(dataset=dataset, source_lap_number=4))
    candidate = selector.select(SourceLapWindowRequest(dataset=dataset, source_lap_number=5))
    assert hasattr(reference, "window")
    assert hasattr(candidate, "window")
    return reference.window, candidate.window


def compact_dataset(dataset: ImportedTelemetryDataset) -> ImportedTelemetryDataset:
    elapsed = dataset.channel("Elapsed Time")
    latitude = dataset.channel("Lat (Degrees)")
    longitude = dataset.channel("Lon (Degrees)")
    lap = dataset.channel("Lap")

    timestamps = tuple(float(index) for index in range(7))
    elapsed_values = tuple(str(index) for index in range(7))
    latitudes = ("45.0", "45.0", "45.001", "45.0", "45.0", "45.001", "45.0")
    longitudes = (
        "-122.0",
        "-121.999",
        "-121.999",
        "-122.0",
        "-121.999",
        "-121.999",
        "-122.0",
    )
    laps = ("4", None, None, "5", None, None, "6")

    def channel_with(channel, values):
        return replace(
            channel,
            series=SampleSeries(
                timestamps_s=timestamps,
                values=values,
            ),
        )

    return replace(
        dataset,
        channels=(
            channel_with(elapsed, elapsed_values),
            channel_with(latitude, latitudes),
            channel_with(longitude, longitudes),
            channel_with(lap, laps),
        ),
    )


class Plan026PhysicalTrackReferencePreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.portland = import_portland()

    def setUp(self) -> None:
        self.service = PhysicalTrackReferencePreparationService()

    def request_for(self, dataset: ImportedTelemetryDataset):
        reference_window, candidate_window = selected_windows(dataset)
        return PhysicalTrackReferencePreparationRequest(
            dataset=dataset,
            reference_window=reference_window,
            candidate_window=candidate_window,
            reference_context=context(dataset, 4),
            candidate_context=context(dataset, 5),
        )

    def test_compact_reference_and_candidate_prepare_to_canonical_lap_distance(self) -> None:
        dataset = compact_dataset(self.portland)
        request = self.request_for(dataset)

        outcome = self.service.prepare(request)

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationSuccess)
        assert isinstance(outcome, PhysicalTrackReferencePreparationSuccess)
        prepared = outcome.preparation

        self.assertEqual(prepared.dataset_fingerprint, dataset.provenance.content_fingerprint)
        self.assertEqual(len(prepared.reference_lap.timestamps_s), 4)
        self.assertEqual(len(prepared.candidate_lap.timestamps_s), 4)
        self.assertEqual(prepared.reference_lap.timestamps_s[-1], 3.0)
        self.assertEqual(prepared.candidate_lap.timestamps_s[-1], 6.0)

        self.assertEqual(prepared.reference_window.sample_count, 3)
        self.assertEqual(prepared.candidate_window.sample_count, 3)

        self.assertIs(
            prepared.reference_lap_distance.evidence.canonical_concept,
            CanonicalConcept.LAP_DISTANCE,
        )
        self.assertIs(
            prepared.candidate_lap_distance.evidence.canonical_concept,
            CanonicalConcept.LAP_DISTANCE,
        )
        self.assertEqual(prepared.reference_lap_distance.evidence.unit, "m")
        self.assertEqual(prepared.candidate_lap_distance.evidence.unit, "m")

        self.assertEqual(prepared.reference_lap_distance.values[0], 0.0)
        self.assertAlmostEqual(
            prepared.reference_lap_distance.values[-1],
            prepared.reference_gps_path.total_distance_m,
        )
        self.assertEqual(
            prepared.candidate_lap_distance.values,
            prepared.candidate_projection.reference_distance_m,
        )

    def test_reference_mapping_is_explicit_and_candidate_projection_keeps_both_identities(
        self,
    ) -> None:
        dataset = compact_dataset(self.portland)
        outcome = self.service.prepare(self.request_for(dataset))

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationSuccess)
        assert isinstance(outcome, PhysicalTrackReferencePreparationSuccess)
        prepared = outcome.preparation

        transformation_ids = tuple(
            item.transformation_id
            for item in prepared.reference_lap_distance.evidence.transformations
        )
        self.assertIn(
            "ome.gps-path-distance.wgs84-geodesic",
            transformation_ids,
        )
        self.assertIn(
            "ome.preparation.explicit-reference-path-to-lap-distance",
            transformation_ids,
        )

        projection = prepared.candidate_projection.provenance
        self.assertEqual(projection.reference_context.lap_identifier, "source-lap:4")
        self.assertEqual(projection.candidate_context.lap_identifier, "source-lap:5")
        self.assertEqual(
            projection.reference_dataset_fingerprint,
            dataset.provenance.content_fingerprint,
        )
        self.assertEqual(
            projection.candidate_dataset_fingerprint,
            dataset.provenance.content_fingerprint,
        )

    def test_compact_preparation_is_deterministic_and_does_not_mutate_source(self) -> None:
        dataset = compact_dataset(self.portland)
        request = self.request_for(dataset)
        channels_before = dataset.channels

        first = self.service.prepare(request)
        second = self.service.prepare(request)

        self.assertEqual(first, second)
        self.assertIs(dataset.channels, channels_before)

    def test_portland_lap_four_reference_lap_five_candidate_prepares(self) -> None:
        outcome = self.service.prepare(self.request_for(self.portland))

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationSuccess)
        assert isinstance(outcome, PhysicalTrackReferencePreparationSuccess)
        prepared = outcome.preparation

        self.assertEqual(prepared.reference_window.source_lap_number, 4)
        self.assertEqual(prepared.candidate_window.source_lap_number, 5)
        self.assertEqual(
            len(prepared.reference_lap.timestamps_s),
            prepared.reference_window.sample_count + 1,
        )
        self.assertEqual(
            len(prepared.candidate_lap.timestamps_s),
            prepared.candidate_window.sample_count + 1,
        )
        self.assertGreater(prepared.reference_gps_path.total_distance_m, 3000.0)
        self.assertEqual(
            len(prepared.candidate_lap_distance.values),
            prepared.candidate_window.sample_count + 1,
        )

    def test_same_reference_and_candidate_window_is_not_ready(self) -> None:
        dataset = compact_dataset(self.portland)
        reference_window, _candidate_window = selected_windows(dataset)

        outcome = self.service.prepare(
            PhysicalTrackReferencePreparationRequest(
                dataset=dataset,
                reference_window=reference_window,
                candidate_window=reference_window,
                reference_context=context(dataset, 4),
                candidate_context=context(dataset, 4),
            )
        )

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationNotReady)
        assert isinstance(outcome, PhysicalTrackReferencePreparationNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (PhysicalTrackReferencePreparationIssueCode.SAME_LAP_WINDOW,),
        )

    def test_window_fingerprint_mismatch_is_not_ready(self) -> None:
        dataset = compact_dataset(self.portland)
        reference_window, candidate_window = selected_windows(dataset)
        invalid_reference = replace(
            reference_window,
            dataset_fingerprint="sha256:other",
        )

        outcome = self.service.prepare(
            PhysicalTrackReferencePreparationRequest(
                dataset=dataset,
                reference_window=invalid_reference,
                candidate_window=candidate_window,
                reference_context=context(dataset, 4),
                candidate_context=context(dataset, 5),
            )
        )

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationNotReady)
        assert isinstance(outcome, PhysicalTrackReferencePreparationNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (PhysicalTrackReferencePreparationIssueCode.WINDOW_DATASET_MISMATCH,),
        )

    def test_context_fingerprint_mismatch_is_not_ready(self) -> None:
        dataset = compact_dataset(self.portland)
        reference_window, candidate_window = selected_windows(dataset)
        invalid_context = replace(
            context(dataset, 4),
            dataset_fingerprint="sha256:other",
        )

        outcome = self.service.prepare(
            PhysicalTrackReferencePreparationRequest(
                dataset=dataset,
                reference_window=reference_window,
                candidate_window=candidate_window,
                reference_context=invalid_context,
                candidate_context=context(dataset, 5),
            )
        )

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationNotReady)
        assert isinstance(outcome, PhysicalTrackReferencePreparationNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (PhysicalTrackReferencePreparationIssueCode.CONTEXT_DATASET_MISMATCH,),
        )

    def test_missing_required_gps_channel_is_not_ready(self) -> None:
        dataset = compact_dataset(self.portland)
        dataset = replace(
            dataset,
            channels=tuple(
                channel for channel in dataset.channels if channel.identifier != "Lat (Degrees)"
            ),
        )
        reference_window, candidate_window = selected_windows(dataset)

        outcome = self.service.prepare(
            PhysicalTrackReferencePreparationRequest(
                dataset=dataset,
                reference_window=reference_window,
                candidate_window=candidate_window,
                reference_context=context(dataset, 4),
                candidate_context=context(dataset, 5),
            )
        )

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationNotReady)
        assert isinstance(outcome, PhysicalTrackReferencePreparationNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (PhysicalTrackReferencePreparationIssueCode.MISSING_SOURCE_CHANNEL,),
        )

    def test_non_numeric_selected_gps_value_is_not_ready(self) -> None:
        dataset = compact_dataset(self.portland)
        latitude = dataset.channel("Lat (Degrees)")
        values = list(latitude.series.values)
        values[1] = "invalid"
        invalid_latitude = replace(
            latitude,
            series=SampleSeries(
                timestamps_s=latitude.series.timestamps_s,
                values=tuple(values),
            ),
        )
        dataset = replace(
            dataset,
            channels=tuple(
                invalid_latitude if channel.identifier == "Lat (Degrees)" else channel
                for channel in dataset.channels
            ),
        )

        outcome = self.service.prepare(self.request_for(dataset))

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationNotReady)
        assert isinstance(outcome, PhysicalTrackReferencePreparationNotReady)
        self.assertEqual(
            tuple(issue.code for issue in outcome.issues),
            (PhysicalTrackReferencePreparationIssueCode.INVALID_SOURCE_EVIDENCE,),
        )


if __name__ == "__main__":
    unittest.main()
