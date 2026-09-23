from __future__ import annotations

import math
import unittest

from ome.analysis import (
    GPSPathDistanceEngine,
    GPSPathDistanceIssueCode,
    GPSPathDistanceNotReady,
    GPSPathDistanceRequest,
    GPSPathDistanceSuccess,
)
from ome.evidence import SourceSeriesEvidence


def source_evidence(
    *,
    dataset_fingerprint: str,
    identifier: str,
    original_name: str,
    unit: str,
) -> SourceSeriesEvidence:
    return SourceSeriesEvidence(
        dataset_fingerprint=dataset_fingerprint,
        source_channel_identifier=identifier,
        source_original_name=original_name,
        unit=unit,
    )


def request(
    *,
    timestamps_s: tuple[float, ...],
    latitudes_deg: tuple[float, ...],
    longitudes_deg: tuple[float, ...],
    dataset_fingerprint: str = "sha256:test",
) -> GPSPathDistanceRequest:
    return GPSPathDistanceRequest(
        dataset_fingerprint=dataset_fingerprint,
        timestamps_s=timestamps_s,
        latitudes_deg=latitudes_deg,
        longitudes_deg=longitudes_deg,
        latitude_evidence=source_evidence(
            dataset_fingerprint=dataset_fingerprint,
            identifier="Lat (Degrees)",
            original_name="Lat (Degrees)",
            unit="deg",
        ),
        longitude_evidence=source_evidence(
            dataset_fingerprint=dataset_fingerprint,
            identifier="Lon (Degrees)",
            original_name="Lon (Degrees)",
            unit="deg",
        ),
        time_evidence=source_evidence(
            dataset_fingerprint=dataset_fingerprint,
            identifier="Elapsed Time",
            original_name="Elapsed Time",
            unit="s",
        ),
    )


class Plan022GPSPathDistanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = GPSPathDistanceEngine()

    def test_known_wgs84_equator_distance(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(0.0, 1.0),
                latitudes_deg=(0.0, 0.0),
                longitudes_deg=(0.0, 0.001),
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceSuccess)
        assert isinstance(outcome, GPSPathDistanceSuccess)

        expected_m = 111.31949079327357
        self.assertEqual(outcome.timestamps_s, (0.0, 1.0))
        self.assertEqual(outcome.segment_distance_m[0], 0.0)
        self.assertAlmostEqual(outcome.segment_distance_m[1], expected_m, places=9)
        self.assertEqual(outcome.path_distance_m[0], 0.0)
        self.assertAlmostEqual(outcome.path_distance_m[1], expected_m, places=9)
        self.assertAlmostEqual(outcome.total_distance_m, expected_m, places=9)

    def test_cumulative_path_uses_consecutive_wgs84_segments(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(0.0, 1.0, 2.0),
                latitudes_deg=(0.0, 0.0, 0.0),
                longitudes_deg=(0.0, 0.001, 0.002),
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceSuccess)
        assert isinstance(outcome, GPSPathDistanceSuccess)

        one_segment_m = 111.31949079327357
        self.assertAlmostEqual(outcome.segment_distance_m[1], one_segment_m, places=9)
        self.assertAlmostEqual(outcome.segment_distance_m[2], one_segment_m, places=9)
        self.assertAlmostEqual(outcome.path_distance_m[2], 2.0 * one_segment_m, places=9)

    def test_duplicate_coordinate_is_preserved_as_zero_distance_segment(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(0.0, 1.0, 2.0),
                latitudes_deg=(0.0, 0.0, 0.0),
                longitudes_deg=(0.0, 0.0, 0.001),
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceSuccess)
        assert isinstance(outcome, GPSPathDistanceSuccess)
        self.assertEqual(outcome.segment_distance_m[0], 0.0)
        self.assertEqual(outcome.segment_distance_m[1], 0.0)
        self.assertAlmostEqual(outcome.path_distance_m[1], 0.0, places=12)
        self.assertGreater(outcome.path_distance_m[2], 0.0)

    def test_result_has_typed_provenance_and_explicit_algorithm_identity(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(10.0, 10.1),
                latitudes_deg=(45.0, 45.000001),
                longitudes_deg=(-121.0, -121.000001),
                dataset_fingerprint="sha256:real",
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceSuccess)
        assert isinstance(outcome, GPSPathDistanceSuccess)

        self.assertEqual(outcome.derived_concept, "gps.path_distance")
        self.assertEqual(outcome.unit, "m")
        self.assertEqual(outcome.algorithm_id, "ome.gps-path-distance.wgs84-geodesic")
        self.assertEqual(outcome.algorithm_version, "0.1.0")
        self.assertEqual(outcome.ellipsoid, "WGS84")
        self.assertEqual(outcome.altitude_policy, "ignored-for-horizontal-distance")

        provenance = outcome.provenance
        self.assertEqual(provenance.dataset_fingerprint, "sha256:real")
        self.assertEqual(
            provenance.latitude.source_channel_identifier,
            "Lat (Degrees)",
        )
        self.assertEqual(
            provenance.longitude.source_channel_identifier,
            "Lon (Degrees)",
        )
        self.assertEqual(
            provenance.elapsed_time.source_channel_identifier,
            "Elapsed Time",
        )
        self.assertEqual(provenance.algorithm_id, outcome.algorithm_id)
        self.assertEqual(provenance.algorithm_version, outcome.algorithm_version)

    def test_same_input_is_deterministic(self) -> None:
        input_request = request(
            timestamps_s=(0.0, 0.1, 0.2),
            latitudes_deg=(45.0, 45.000001, 45.000002),
            longitudes_deg=(-121.0, -121.000001, -121.000002),
        )

        first = self.engine.derive(input_request)
        second = self.engine.derive(input_request)

        self.assertEqual(first, second)

    def test_invalid_latitude_is_explicit_not_ready(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(0.0, 1.0),
                latitudes_deg=(0.0, 91.0),
                longitudes_deg=(0.0, 0.001),
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceNotReady)
        assert isinstance(outcome, GPSPathDistanceNotReady)
        self.assertIn(
            GPSPathDistanceIssueCode.INVALID_LATITUDE,
            {issue.code for issue in outcome.issues},
        )

    def test_invalid_longitude_is_explicit_not_ready(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(0.0, 1.0),
                latitudes_deg=(0.0, 0.0),
                longitudes_deg=(0.0, 181.0),
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceNotReady)
        assert isinstance(outcome, GPSPathDistanceNotReady)
        self.assertIn(
            GPSPathDistanceIssueCode.INVALID_LONGITUDE,
            {issue.code for issue in outcome.issues},
        )

    def test_non_finite_coordinate_is_explicit_not_ready(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(0.0, 1.0),
                latitudes_deg=(0.0, math.nan),
                longitudes_deg=(0.0, 0.001),
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceNotReady)
        assert isinstance(outcome, GPSPathDistanceNotReady)
        self.assertIn(
            GPSPathDistanceIssueCode.NON_FINITE_COORDINATE,
            {issue.code for issue in outcome.issues},
        )

    def test_series_length_mismatch_is_explicit_not_ready(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(0.0, 1.0),
                latitudes_deg=(0.0, 0.0),
                longitudes_deg=(0.0,),
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceNotReady)
        assert isinstance(outcome, GPSPathDistanceNotReady)
        self.assertIn(
            GPSPathDistanceIssueCode.LENGTH_MISMATCH,
            {issue.code for issue in outcome.issues},
        )

    def test_fewer_than_two_samples_is_explicit_not_ready(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(0.0,),
                latitudes_deg=(0.0,),
                longitudes_deg=(0.0,),
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceNotReady)
        assert isinstance(outcome, GPSPathDistanceNotReady)
        self.assertIn(
            GPSPathDistanceIssueCode.INSUFFICIENT_SAMPLES,
            {issue.code for issue in outcome.issues},
        )

    def test_non_increasing_time_is_explicit_not_ready(self) -> None:
        outcome = self.engine.derive(
            request(
                timestamps_s=(0.0, 0.0),
                latitudes_deg=(0.0, 0.0),
                longitudes_deg=(0.0, 0.001),
            )
        )

        self.assertIsInstance(outcome, GPSPathDistanceNotReady)
        assert isinstance(outcome, GPSPathDistanceNotReady)
        self.assertIn(
            GPSPathDistanceIssueCode.TIME_NOT_STRICTLY_INCREASING,
            {issue.code for issue in outcome.issues},
        )

    def test_incompatible_units_are_explicit_not_ready(self) -> None:
        bad = GPSPathDistanceRequest(
            dataset_fingerprint="sha256:test",
            timestamps_s=(0.0, 1.0),
            latitudes_deg=(0.0, 0.0),
            longitudes_deg=(0.0, 0.001),
            latitude_evidence=source_evidence(
                dataset_fingerprint="sha256:test",
                identifier="latitude",
                original_name="latitude",
                unit="rad",
            ),
            longitude_evidence=source_evidence(
                dataset_fingerprint="sha256:test",
                identifier="longitude",
                original_name="longitude",
                unit="deg",
            ),
            time_evidence=source_evidence(
                dataset_fingerprint="sha256:test",
                identifier="time",
                original_name="time",
                unit="s",
            ),
        )

        outcome = self.engine.derive(bad)

        self.assertIsInstance(outcome, GPSPathDistanceNotReady)
        assert isinstance(outcome, GPSPathDistanceNotReady)
        self.assertIn(
            GPSPathDistanceIssueCode.INCOMPATIBLE_UNITS,
            {issue.code for issue in outcome.issues},
        )

    def test_missing_or_mismatched_provenance_is_explicit_not_ready(self) -> None:
        bad = GPSPathDistanceRequest(
            dataset_fingerprint="sha256:a",
            timestamps_s=(0.0, 1.0),
            latitudes_deg=(0.0, 0.0),
            longitudes_deg=(0.0, 0.001),
            latitude_evidence=source_evidence(
                dataset_fingerprint="sha256:b",
                identifier="lat",
                original_name="lat",
                unit="deg",
            ),
            longitude_evidence=source_evidence(
                dataset_fingerprint="sha256:a",
                identifier="lon",
                original_name="lon",
                unit="deg",
            ),
            time_evidence=source_evidence(
                dataset_fingerprint="sha256:a",
                identifier="time",
                original_name="time",
                unit="s",
            ),
        )

        outcome = self.engine.derive(bad)

        self.assertIsInstance(outcome, GPSPathDistanceNotReady)
        assert isinstance(outcome, GPSPathDistanceNotReady)
        self.assertIn(
            GPSPathDistanceIssueCode.MISSING_PROVENANCE,
            {issue.code for issue in outcome.issues},
        )


if __name__ == "__main__":
    unittest.main()
