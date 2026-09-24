from __future__ import annotations

import unittest

from ome.analysis import (
    CommonTrackReferenceEngine,
    CommonTrackReferenceRequest,
    CommonTrackReferenceSuccess,
    GPSPathDistanceEngine,
    GPSPathDistanceRequest,
    GPSPathDistanceSuccess,
    TrackReferenceLap,
)
from ome.application import prepare_track_reference_lap_distance
from ome.domain import CanonicalConcept
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


def context(fingerprint: str, lap_id: str) -> LapEvidenceContext:
    return LapEvidenceContext(
        dataset_fingerprint=fingerprint,
        session_identifier=f"session:{lap_id}",
        run_identifier=f"run:{lap_id}",
        lap_identifier=f"lap:{lap_id}",
    )


def track_lap(
    *,
    fingerprint: str,
    lap_id: str,
    timestamps_s: tuple[float, ...],
    latitudes_deg: tuple[float, ...],
    longitudes_deg: tuple[float, ...],
    include_path: bool,
) -> TrackReferenceLap:
    latitude_evidence = source_evidence(fingerprint, "Lat", "deg")
    longitude_evidence = source_evidence(fingerprint, "Lon", "deg")
    time_evidence = source_evidence(fingerprint, "Time", "s")

    path = None
    if include_path:
        outcome = GPSPathDistanceEngine().derive(
            GPSPathDistanceRequest(
                dataset_fingerprint=fingerprint,
                timestamps_s=timestamps_s,
                latitudes_deg=latitudes_deg,
                longitudes_deg=longitudes_deg,
                latitude_evidence=latitude_evidence,
                longitude_evidence=longitude_evidence,
                time_evidence=time_evidence,
            )
        )
        assert isinstance(outcome, GPSPathDistanceSuccess)
        path = outcome

    return TrackReferenceLap(
        context=context(fingerprint, lap_id),
        timestamps_s=timestamps_s,
        latitudes_deg=latitudes_deg,
        longitudes_deg=longitudes_deg,
        latitude_evidence=latitude_evidence,
        longitude_evidence=longitude_evidence,
        time_evidence=time_evidence,
        gps_path_distance=path,
    )


def projected_result() -> CommonTrackReferenceSuccess:
    reference = track_lap(
        fingerprint="sha256:reference",
        lap_id="reference",
        timestamps_s=(0.0, 1.0, 2.0),
        latitudes_deg=(0.0, 0.0, 0.0),
        longitudes_deg=(0.0, 0.001, 0.002),
        include_path=True,
    )
    candidate = track_lap(
        fingerprint="sha256:candidate",
        lap_id="candidate",
        timestamps_s=(0.0, 1.0, 2.0),
        latitudes_deg=(0.0001, 0.0001, 0.0001),
        longitudes_deg=(0.0, 0.001, 0.002),
        include_path=False,
    )
    outcome = CommonTrackReferenceEngine().project(
        CommonTrackReferenceRequest(reference=reference, candidate=candidate)
    )
    assert isinstance(outcome, CommonTrackReferenceSuccess)
    return outcome


class Plan023TrackReferencePreparationTests(unittest.TestCase):
    def test_ready_reference_distance_maps_explicitly_to_canonical_lap_distance(self) -> None:
        result = projected_result()

        series = prepare_track_reference_lap_distance(result)

        self.assertEqual(series.values, result.reference_distance_m)
        self.assertIs(series.evidence.canonical_concept, CanonicalConcept.LAP_DISTANCE)
        self.assertEqual(series.evidence.unit, "m")
        self.assertEqual(series.evidence.dataset_fingerprint, "sha256:candidate")
        self.assertEqual(
            series.evidence.source_channel_identifier,
            "derived:track.reference_distance",
        )
        self.assertEqual(
            series.evidence.source_original_name,
            "track.reference_distance",
        )

    def test_mapping_preserves_full_reference_and_candidate_identity(self) -> None:
        result = projected_result()

        series = prepare_track_reference_lap_distance(result)

        projection = series.evidence.transformations[0]
        mapping = series.evidence.transformations[1]

        self.assertEqual(
            projection.transformation_id,
            "ome.track-reference.explicit-lap-projection",
        )
        self.assertEqual(projection.transformation_version, "0.2.0")
        self.assertEqual(
            projection.parameters["reference_dataset_fingerprint"],
            "sha256:reference",
        )
        self.assertEqual(
            projection.parameters["candidate_dataset_fingerprint"],
            "sha256:candidate",
        )
        self.assertEqual(
            projection.parameters["reference_lap_identifier"],
            "lap:reference",
        )
        self.assertEqual(
            projection.parameters["candidate_lap_identifier"],
            "lap:candidate",
        )
        self.assertEqual(
            projection.parameters["reference_latitude_channel"],
            "Lat",
        )
        self.assertEqual(
            projection.parameters["reference_longitude_channel"],
            "Lon",
        )
        self.assertEqual(
            projection.parameters["candidate_latitude_channel"],
            "Lat",
        )
        self.assertEqual(
            projection.parameters["candidate_longitude_channel"],
            "Lon",
        )
        self.assertEqual(
            projection.parameters["reference_gps_path_algorithm_id"],
            "ome.gps-path-distance.wgs84-geodesic",
        )
        self.assertEqual(
            projection.parameters["reference_length_m"],
            result.reference_length_m,
        )

        self.assertEqual(
            mapping.transformation_id,
            "ome.preparation.track-reference-to-lap-distance",
        )
        self.assertEqual(mapping.transformation_version, "0.1.0")
        self.assertEqual(
            mapping.parameters["source_concept"],
            "track.reference_distance",
        )
        self.assertEqual(mapping.parameters["target_concept"], "lap.distance")

    def test_mapping_is_deterministic_and_does_not_mutate_projection_result(self) -> None:
        result = projected_result()
        distances_before = result.reference_distance_m
        provenance_before = result.provenance

        first = prepare_track_reference_lap_distance(result)
        second = prepare_track_reference_lap_distance(result)

        self.assertEqual(first, second)
        self.assertIs(result.reference_distance_m, distances_before)
        self.assertIs(result.provenance, provenance_before)


if __name__ == "__main__":
    unittest.main()
