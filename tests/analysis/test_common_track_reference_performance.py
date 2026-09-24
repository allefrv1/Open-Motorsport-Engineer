from __future__ import annotations

import math
import time
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
from ome.evidence import LapEvidenceContext, SourceSeriesEvidence


def _evidence(fingerprint: str, identifier: str, unit: str) -> SourceSeriesEvidence:
    return SourceSeriesEvidence(
        dataset_fingerprint=fingerprint,
        source_channel_identifier=identifier,
        source_original_name=identifier,
        unit=unit,
    )


def _circular_lap(
    *,
    fingerprint: str,
    sample_count: int,
    include_path: bool,
) -> TrackReferenceLap:
    center_latitude_deg = 45.0
    center_longitude_deg = -122.0
    radius_deg = 0.001

    angles = tuple(2.0 * math.pi * index / (sample_count - 1) for index in range(sample_count))
    latitudes_deg = tuple(center_latitude_deg + radius_deg * math.sin(angle) for angle in angles)
    longitudes_deg = tuple(center_longitude_deg + radius_deg * math.cos(angle) for angle in angles)
    timestamps_s = tuple(index * 0.025 for index in range(sample_count))

    latitude_evidence = _evidence(fingerprint, "Lat", "deg")
    longitude_evidence = _evidence(fingerprint, "Lon", "deg")
    time_evidence = _evidence(fingerprint, "Time", "s")

    gps_path_distance = None
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
        gps_path_distance = outcome

    return TrackReferenceLap(
        context=LapEvidenceContext(
            dataset_fingerprint=fingerprint,
            session_identifier=f"session:{fingerprint}",
            run_identifier=f"run:{fingerprint}",
            lap_identifier=f"lap:{fingerprint}",
        ),
        timestamps_s=timestamps_s,
        latitudes_deg=latitudes_deg,
        longitudes_deg=longitudes_deg,
        latitude_evidence=latitude_evidence,
        longitude_evidence=longitude_evidence,
        time_evidence=time_evidence,
        gps_path_distance=gps_path_distance,
    )


class Plan023CommonTrackReferencePerformanceTests(unittest.TestCase):
    def test_direct_projection_scaling_is_characterized_without_a_time_gate(self) -> None:
        engine = CommonTrackReferenceEngine()
        observations: list[tuple[int, int, float]] = []

        for sample_count in (100, 200, 400, 800):
            reference = _circular_lap(
                fingerprint=f"sha256:reference:{sample_count}",
                sample_count=sample_count,
                include_path=True,
            )
            candidate = _circular_lap(
                fingerprint=f"sha256:candidate:{sample_count}",
                sample_count=sample_count,
                include_path=False,
            )

            started = time.perf_counter()
            outcome = engine.project(
                CommonTrackReferenceRequest(
                    reference=reference,
                    candidate=candidate,
                )
            )
            elapsed_s = time.perf_counter() - started

            self.assertIsInstance(outcome, CommonTrackReferenceSuccess)
            assert isinstance(outcome, CommonTrackReferenceSuccess)
            self.assertEqual(len(outcome.reference_distance_m), sample_count)

            segment_checks = sample_count * (sample_count - 1)
            observations.append((sample_count, segment_checks, elapsed_s))

        print(
            "COMMON_TRACK_REFERENCE_PERF "
            + " ".join(
                (f"n={sample_count},segment_checks={segment_checks},elapsed_s={elapsed_s:.6f}")
                for sample_count, segment_checks, elapsed_s in observations
            )
        )


if __name__ == "__main__":
    unittest.main()
