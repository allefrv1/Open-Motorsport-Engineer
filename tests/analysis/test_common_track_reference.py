from __future__ import annotations

import unittest

from ome.analysis import (
    CommonTrackReferenceEngine,
    CommonTrackReferenceIssueCode,
    CommonTrackReferenceNotReady,
    CommonTrackReferenceRequest,
    CommonTrackReferenceSuccess,
    GPSPathDistanceEngine,
    GPSPathDistanceRequest,
    GPSPathDistanceSuccess,
    TrackReferenceLap,
)
from ome.evidence import LapEvidenceContext, SourceSeriesEvidence


def source_evidence(
    fingerprint: str,
    identifier: str,
    unit: str,
) -> SourceSeriesEvidence:
    return SourceSeriesEvidence(
        dataset_fingerprint=fingerprint,
        source_channel_identifier=identifier,
        source_original_name=identifier,
        unit=unit,
    )


def context(
    fingerprint: str,
    lap: str,
) -> LapEvidenceContext:
    return LapEvidenceContext(
        dataset_fingerprint=fingerprint,
        session_identifier=f"session:{lap}",
        run_identifier=f"run:{lap}",
        lap_identifier=f"lap:{lap}",
    )


def gps_path(
    fingerprint: str,
    timestamps_s: tuple[float, ...],
    latitudes_deg: tuple[float, ...],
    longitudes_deg: tuple[float, ...],
) -> GPSPathDistanceSuccess:
    outcome = GPSPathDistanceEngine().derive(
        GPSPathDistanceRequest(
            dataset_fingerprint=fingerprint,
            timestamps_s=timestamps_s,
            latitudes_deg=latitudes_deg,
            longitudes_deg=longitudes_deg,
            latitude_evidence=source_evidence(fingerprint, "Lat", "deg"),
            longitude_evidence=source_evidence(fingerprint, "Lon", "deg"),
            time_evidence=source_evidence(fingerprint, "Time", "s"),
        )
    )
    assert isinstance(outcome, GPSPathDistanceSuccess)
    return outcome


def lap(
    *,
    fingerprint: str,
    lap_id: str,
    timestamps_s: tuple[float, ...],
    latitudes_deg: tuple[float, ...],
    longitudes_deg: tuple[float, ...],
    include_path: bool,
) -> TrackReferenceLap:
    return TrackReferenceLap(
        context=context(fingerprint, lap_id),
        timestamps_s=timestamps_s,
        latitudes_deg=latitudes_deg,
        longitudes_deg=longitudes_deg,
        latitude_evidence=source_evidence(fingerprint, "Lat", "deg"),
        longitude_evidence=source_evidence(fingerprint, "Lon", "deg"),
        time_evidence=source_evidence(fingerprint, "Time", "s"),
        gps_path_distance=(
            gps_path(
                fingerprint,
                timestamps_s,
                latitudes_deg,
                longitudes_deg,
            )
            if include_path
            else None
        ),
    )


class Plan023CommonTrackReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = CommonTrackReferenceEngine()

    def test_straight_reference_projects_lateral_candidate_to_same_along_distance(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.0, 0.0, 0.0),
            longitudes_deg=(0.0, 0.001, 0.002),
            include_path=True,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.0001, 0.0001, 0.0001),
            longitudes_deg=(0.0, 0.001, 0.002),
            include_path=False,
        )

        outcome = self.engine.project(
            CommonTrackReferenceRequest(reference=reference, candidate=candidate)
        )

        self.assertIsInstance(outcome, CommonTrackReferenceSuccess)
        assert isinstance(outcome, CommonTrackReferenceSuccess)

        reference_path = reference.gps_path_distance
        assert reference_path is not None

        self.assertAlmostEqual(outcome.reference_distance_m[0], 0.0, places=5)
        self.assertAlmostEqual(
            outcome.reference_distance_m[1],
            reference_path.path_distance_m[1],
            places=5,
        )
        self.assertAlmostEqual(
            outcome.reference_distance_m[2],
            reference_path.path_distance_m[2],
            places=5,
        )
        self.assertTrue(all(error > 10.0 for error in outcome.lateral_error_m))

    def test_l_shaped_reference_uses_nearest_segment_and_fraction(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.0, 0.0, 0.001),
            longitudes_deg=(0.0, 0.001, 0.001),
            include_path=True,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0),
            latitudes_deg=(0.0, 0.0005),
            longitudes_deg=(0.0005, 0.001),
            include_path=False,
        )

        outcome = self.engine.project(
            CommonTrackReferenceRequest(reference=reference, candidate=candidate)
        )

        self.assertIsInstance(outcome, CommonTrackReferenceSuccess)
        assert isinstance(outcome, CommonTrackReferenceSuccess)
        self.assertEqual(outcome.reference_segment_index, (0, 1))
        self.assertAlmostEqual(outcome.segment_fraction[0], 0.5, places=3)
        self.assertAlmostEqual(outcome.segment_fraction[1], 0.5, places=3)

    def test_equal_distance_tie_uses_lowest_reference_segment_index(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.0, 0.0, 0.001),
            longitudes_deg=(0.0, 0.001, 0.001),
            include_path=True,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0),
            latitudes_deg=(0.0, 0.0001),
            longitudes_deg=(0.001, 0.001),
            include_path=False,
        )

        outcome = self.engine.project(
            CommonTrackReferenceRequest(reference=reference, candidate=candidate)
        )

        self.assertIsInstance(outcome, CommonTrackReferenceSuccess)
        assert isinstance(outcome, CommonTrackReferenceSuccess)
        self.assertEqual(outcome.reference_segment_index[0], 0)
        self.assertEqual(outcome.segment_fraction[0], 1.0)

    def test_closed_loop_seam_is_unwrapped_without_forcing_candidate_start_to_zero(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0, 2.0, 3.0, 4.0),
            latitudes_deg=(0.0, 0.0, 0.001, 0.001, 0.0),
            longitudes_deg=(0.0, 0.001, 0.001, 0.0, 0.0),
            include_path=True,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.00001, 0.0, 0.0),
            longitudes_deg=(0.0, 0.00001, 0.0001),
            include_path=False,
        )

        outcome = self.engine.project(
            CommonTrackReferenceRequest(reference=reference, candidate=candidate)
        )

        self.assertIsInstance(outcome, CommonTrackReferenceSuccess)
        assert isinstance(outcome, CommonTrackReferenceSuccess)

        self.assertLess(outcome.reference_distance_m[0], 0.0)
        self.assertGreater(outcome.reference_distance_m[1], 0.0)
        self.assertTrue(
            all(
                current > previous
                for previous, current in zip(
                    outcome.reference_distance_m,
                    outcome.reference_distance_m[1:],
                    strict=False,
                )
            )
        )

    def test_exact_projection_plateau_is_preserved_without_repair(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.0, 0.0, 0.0),
            longitudes_deg=(0.0, 0.001, 0.002),
            include_path=True,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.0001, 0.0001, 0.0001),
            longitudes_deg=(0.0005, 0.001, 0.001),
            include_path=False,
        )

        outcome = self.engine.project(
            CommonTrackReferenceRequest(reference=reference, candidate=candidate)
        )

        self.assertIsInstance(outcome, CommonTrackReferenceSuccess)
        assert isinstance(outcome, CommonTrackReferenceSuccess)
        self.assertEqual(
            outcome.reference_distance_m[1],
            outcome.reference_distance_m[2],
        )
        self.assertEqual(outcome.algorithm_version, "0.2.0")

    def test_local_backtrack_is_not_clamped_or_repaired(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0, 2.0, 3.0),
            latitudes_deg=(0.0, 0.0, 0.0, 0.0),
            longitudes_deg=(0.0, 0.001, 0.002, 0.003),
            include_path=True,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.00001, 0.00001, 0.00001),
            longitudes_deg=(0.0005, 0.0015, 0.0014),
            include_path=False,
        )

        outcome = self.engine.project(
            CommonTrackReferenceRequest(reference=reference, candidate=candidate)
        )

        self.assertIsInstance(outcome, CommonTrackReferenceNotReady)
        assert isinstance(outcome, CommonTrackReferenceNotReady)
        self.assertIn(
            CommonTrackReferenceIssueCode.PROJECTED_DISTANCE_DECREASES,
            {issue.code for issue in outcome.issues},
        )

    def test_self_intersecting_reference_is_explicit_not_ready(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0, 2.0, 3.0),
            latitudes_deg=(0.0, 0.001, 0.0, 0.001),
            longitudes_deg=(0.0, 0.001, 0.001, 0.0),
            include_path=True,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0),
            latitudes_deg=(0.0002, 0.0008),
            longitudes_deg=(0.0002, 0.0008),
            include_path=False,
        )

        outcome = self.engine.project(
            CommonTrackReferenceRequest(reference=reference, candidate=candidate)
        )

        self.assertIsInstance(outcome, CommonTrackReferenceNotReady)
        assert isinstance(outcome, CommonTrackReferenceNotReady)
        self.assertIn(
            CommonTrackReferenceIssueCode.REFERENCE_SELF_INTERSECTION,
            {issue.code for issue in outcome.issues},
        )

    def test_missing_reference_path_distance_is_explicit_not_ready(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0),
            latitudes_deg=(0.0, 0.0),
            longitudes_deg=(0.0, 0.001),
            include_path=False,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0),
            latitudes_deg=(0.0001, 0.0001),
            longitudes_deg=(0.0, 0.001),
            include_path=False,
        )

        outcome = self.engine.project(
            CommonTrackReferenceRequest(reference=reference, candidate=candidate)
        )

        self.assertIsInstance(outcome, CommonTrackReferenceNotReady)
        assert isinstance(outcome, CommonTrackReferenceNotReady)
        self.assertIn(
            CommonTrackReferenceIssueCode.MISSING_REFERENCE_PATH_DISTANCE,
            {issue.code for issue in outcome.issues},
        )

    def test_result_preserves_reference_candidate_context_and_algorithm_identity(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0),
            latitudes_deg=(0.0, 0.0),
            longitudes_deg=(0.0, 0.001),
            include_path=True,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0),
            latitudes_deg=(0.0001, 0.0001),
            longitudes_deg=(0.0, 0.001),
            include_path=False,
        )

        outcome = self.engine.project(
            CommonTrackReferenceRequest(reference=reference, candidate=candidate)
        )

        self.assertIsInstance(outcome, CommonTrackReferenceSuccess)
        assert isinstance(outcome, CommonTrackReferenceSuccess)

        self.assertEqual(outcome.derived_concept, "track.reference_distance")
        self.assertEqual(outcome.unit, "m")
        self.assertEqual(outcome.algorithm_id, "ome.track-reference.explicit-lap-projection")
        self.assertEqual(outcome.algorithm_version, "0.2.0")
        self.assertEqual(outcome.provenance.reference_context.lap_identifier, "lap:ref")
        self.assertEqual(
            outcome.provenance.candidate_context.lap_identifier,
            "lap:candidate",
        )
        self.assertEqual(outcome.provenance.reference_dataset_fingerprint, "sha256:ref")
        self.assertEqual(
            outcome.provenance.candidate_dataset_fingerprint,
            "sha256:candidate",
        )

    def test_same_inputs_are_deterministic(self) -> None:
        reference = lap(
            fingerprint="sha256:ref",
            lap_id="ref",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.0, 0.0, 0.0),
            longitudes_deg=(0.0, 0.001, 0.002),
            include_path=True,
        )
        candidate = lap(
            fingerprint="sha256:candidate",
            lap_id="candidate",
            timestamps_s=(0.0, 1.0, 2.0),
            latitudes_deg=(0.0001, 0.0001, 0.0001),
            longitudes_deg=(0.0, 0.001, 0.002),
            include_path=False,
        )
        request = CommonTrackReferenceRequest(reference=reference, candidate=candidate)

        first = self.engine.project(request)
        second = self.engine.project(request)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
