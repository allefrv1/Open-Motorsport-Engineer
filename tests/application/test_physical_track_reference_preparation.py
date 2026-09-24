from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from ome.application import (
    PhysicalTrackReferencePreparationIssueCode,
    PhysicalTrackReferencePreparationNotReady,
    PhysicalTrackReferencePreparationRequest,
    PhysicalTrackReferencePreparationService,
    PhysicalTrackReferencePreparationSuccess,
    SourceLapWindowRequest,
    SourceLapWindowSuccess,
    TraqmateLapWindowSelector,
)
from ome.domain import CanonicalConcept
from ome.evidence import LapEvidenceContext
from ome.ingestion import ImportSuccess, TraqmateTrackvisionCSVImporter

ROOT = Path(__file__).resolve().parents[2]
PORTLAND_FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-portland-laps-4-5.csv"
FIXED_TIME = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


def import_portland():
    outcome = TraqmateTrackvisionCSVImporter().import_source(
        PORTLAND_FIXTURE,
        imported_at=FIXED_TIME,
    )
    assert isinstance(outcome, ImportSuccess)
    return outcome.dataset


def lap_context(fingerprint: str, lap_number: int) -> LapEvidenceContext:
    return LapEvidenceContext(
        dataset_fingerprint=fingerprint,
        session_identifier="session:portland",
        run_identifier="run:portland",
        lap_identifier=f"lap:{lap_number}",
    )


class Plan026PhysicalTrackReferencePreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = import_portland()
        selector = TraqmateLapWindowSelector()

        reference = selector.select(
            SourceLapWindowRequest(dataset=self.dataset, source_lap_number=4)
        )
        candidate = selector.select(
            SourceLapWindowRequest(dataset=self.dataset, source_lap_number=5)
        )
        assert isinstance(reference, SourceLapWindowSuccess)
        assert isinstance(candidate, SourceLapWindowSuccess)

        self.reference_window = reference.window
        self.candidate_window = candidate.window
        fingerprint = self.dataset.provenance.content_fingerprint
        self.reference_context = lap_context(fingerprint, 4)
        self.candidate_context = lap_context(fingerprint, 5)
        self.service = PhysicalTrackReferencePreparationService()

    def request(self) -> PhysicalTrackReferencePreparationRequest:
        return PhysicalTrackReferencePreparationRequest(
            dataset=self.dataset,
            reference_window=self.reference_window,
            candidate_window=self.candidate_window,
            reference_context=self.reference_context,
            candidate_context=self.candidate_context,
        )

    def prepare(self) -> PhysicalTrackReferencePreparationSuccess:
        outcome = self.service.prepare(self.request())
        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationSuccess)
        assert isinstance(outcome, PhysicalTrackReferencePreparationSuccess)
        return outcome

    def test_portland_lap_four_reference_lap_five_candidate_succeeds(self) -> None:
        outcome = self.prepare()

        self.assertEqual(outcome.reference_window.source_lap_number, 4)
        self.assertEqual(outcome.candidate_window.source_lap_number, 5)
        self.assertEqual(outcome.reference_context.lap_identifier, "lap:4")
        self.assertEqual(outcome.candidate_context.lap_identifier, "lap:5")
        self.assertEqual(
            outcome.reference_lap_distance.evidence.canonical_concept,
            CanonicalConcept.LAP_DISTANCE,
        )
        self.assertEqual(
            outcome.candidate_lap_distance.evidence.canonical_concept,
            CanonicalConcept.LAP_DISTANCE,
        )

    def test_derived_trajectories_append_exactly_one_boundary_only_closing_point(self) -> None:
        outcome = self.prepare()

        self.assertEqual(
            len(outcome.reference_track_lap.timestamps_s),
            self.reference_window.sample_count + 1,
        )
        self.assertEqual(
            len(outcome.candidate_track_lap.timestamps_s),
            self.candidate_window.sample_count + 1,
        )
        self.assertEqual(
            outcome.reference_track_lap.timestamps_s[-1],
            self.reference_window.closing_elapsed_s,
        )
        self.assertEqual(
            outcome.candidate_track_lap.timestamps_s[-1],
            self.candidate_window.closing_elapsed_s,
        )

    def test_source_windows_and_dataset_sample_counts_remain_unchanged(self) -> None:
        reference_before = self.reference_window
        candidate_before = self.candidate_window
        channels_before = self.dataset.channels
        elapsed_before = self.dataset.channel("Elapsed Time").series.values

        outcome = self.prepare()

        self.assertEqual(outcome.reference_window, reference_before)
        self.assertEqual(outcome.candidate_window, candidate_before)
        self.assertIs(self.dataset.channels, channels_before)
        self.assertIs(self.dataset.channel("Elapsed Time").series.values, elapsed_before)
        self.assertEqual(self.reference_window.sample_count, 3618)
        self.assertEqual(self.candidate_window.sample_count, 3631)

    def test_reference_canonical_distance_maps_only_explicit_selected_reference_path(self) -> None:
        outcome = self.prepare()

        reference = outcome.reference_lap_distance
        self.assertEqual(reference.values[0], 0.0)
        self.assertAlmostEqual(
            reference.values[-1],
            outcome.reference_gps_path.total_distance_m,
            places=9,
        )
        self.assertEqual(reference.evidence.unit, "m")
        self.assertEqual(
            reference.evidence.source_channel_identifier,
            "derived:gps.path_distance:explicit-reference",
        )

        transformations = reference.evidence.transformations
        self.assertEqual(
            transformations[-1].transformation_id,
            "ome.preparation.explicit-reference-path-to-lap-distance",
        )
        self.assertEqual(transformations[-1].transformation_version, "0.1.0")
        self.assertEqual(
            transformations[-1].parameters["reference_lap_identifier"],
            "lap:4",
        )
        self.assertEqual(
            transformations[-1].parameters["source_lap_number"],
            4,
        )

    def test_candidate_canonical_distance_comes_from_common_reference_projection(self) -> None:
        outcome = self.prepare()

        candidate = outcome.candidate_lap_distance
        projection = outcome.candidate_projection

        self.assertEqual(candidate.values, projection.reference_distance_m)
        self.assertEqual(
            candidate.evidence.source_channel_identifier,
            "derived:track.reference_distance",
        )
        self.assertEqual(
            candidate.evidence.transformations[-1].transformation_id,
            "ome.preparation.track-reference-to-lap-distance",
        )
        self.assertEqual(
            projection.provenance.reference_context.lap_identifier,
            "lap:4",
        )
        self.assertEqual(
            projection.provenance.candidate_context.lap_identifier,
            "lap:5",
        )

    def test_source_evidence_uses_verified_traqmate_time_and_gps_channels(self) -> None:
        outcome = self.prepare()
        reference = outcome.reference_track_lap
        candidate = outcome.candidate_track_lap

        for lap in (reference, candidate):
            self.assertEqual(lap.time_evidence.source_channel_identifier, "Elapsed Time")
            self.assertEqual(lap.time_evidence.unit, "s")
            self.assertEqual(lap.latitude_evidence.source_channel_identifier, "Lat (Degrees)")
            self.assertEqual(lap.latitude_evidence.unit, "deg")
            self.assertEqual(lap.longitude_evidence.source_channel_identifier, "Lon (Degrees)")
            self.assertEqual(lap.longitude_evidence.unit, "deg")
            self.assertEqual(
                lap.time_evidence.dataset_fingerprint,
                self.dataset.provenance.content_fingerprint,
            )

    def test_repeated_preparation_is_deterministic(self) -> None:
        request = self.request()

        first = self.service.prepare(request)
        second = self.service.prepare(request)

        self.assertEqual(first, second)

    def test_same_reference_and_candidate_window_is_not_ready(self) -> None:
        request = replace(
            self.request(),
            candidate_window=self.reference_window,
            candidate_context=self.reference_context,
        )

        outcome = self.service.prepare(request)

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationNotReady)
        assert isinstance(outcome, PhysicalTrackReferencePreparationNotReady)
        self.assertIn(
            PhysicalTrackReferencePreparationIssueCode.SAME_SOURCE_LAP,
            {issue.code for issue in outcome.issues},
        )

    def test_window_or_context_fingerprint_mismatch_is_not_ready(self) -> None:
        bad_window = replace(
            self.candidate_window,
            dataset_fingerprint="sha256:wrong",
        )
        bad_context = replace(
            self.candidate_context,
            dataset_fingerprint="sha256:wrong",
        )

        for request in (
            replace(self.request(), candidate_window=bad_window),
            replace(self.request(), candidate_context=bad_context),
        ):
            with self.subTest(request=request):
                outcome = self.service.prepare(request)
                self.assertIsInstance(outcome, PhysicalTrackReferencePreparationNotReady)
                assert isinstance(outcome, PhysicalTrackReferencePreparationNotReady)
                self.assertIn(
                    PhysicalTrackReferencePreparationIssueCode.PROVENANCE_MISMATCH,
                    {issue.code for issue in outcome.issues},
                )

    def test_missing_required_gps_channel_is_not_ready(self) -> None:
        dataset = replace(
            self.dataset,
            channels=tuple(
                channel
                for channel in self.dataset.channels
                if channel.identifier != "Lat (Degrees)"
            ),
        )

        outcome = self.service.prepare(replace(self.request(), dataset=dataset))

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationNotReady)
        assert isinstance(outcome, PhysicalTrackReferencePreparationNotReady)
        self.assertIn(
            PhysicalTrackReferencePreparationIssueCode.MISSING_SOURCE_CHANNEL,
            {issue.code for issue in outcome.issues},
        )

    def test_out_of_bounds_closing_boundary_is_not_ready(self) -> None:
        invalid = replace(
            self.candidate_window,
            closing_boundary_index=len(self.dataset.channel("Elapsed Time").series.values),
        )

        outcome = self.service.prepare(
            replace(self.request(), candidate_window=invalid)
        )

        self.assertIsInstance(outcome, PhysicalTrackReferencePreparationNotReady)
        assert isinstance(outcome, PhysicalTrackReferencePreparationNotReady)
        self.assertIn(
            PhysicalTrackReferencePreparationIssueCode.INVALID_WINDOW,
            {issue.code for issue in outcome.issues},
        )


if __name__ == "__main__":
    unittest.main()
