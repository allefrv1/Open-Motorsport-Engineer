from __future__ import annotations

import unittest
from pathlib import Path

from ome.analysis import GPSPathDistanceEngine, GPSPathDistanceRequest, GPSPathDistanceSuccess
from ome.evidence import SourceSeriesEvidence
from ome.ingestion import ImportSuccess, TraqmateTrackvisionCSVImporter

ROOT = Path(__file__).resolve().parents[2]
TRAQMATE_FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-parking-lot.csv"


class TraqmateGPSPathCharacterizationTests(unittest.TestCase):
    def setUp(self) -> None:
        outcome = TraqmateTrackvisionCSVImporter().import_source(TRAQMATE_FIXTURE)
        self.assertIsInstance(outcome, ImportSuccess)
        assert isinstance(outcome, ImportSuccess)
        self.dataset = outcome.dataset
        self.engine = GPSPathDistanceEngine()

    def test_real_fixture_has_coherent_wgs84_path_distance(self) -> None:
        outcome = self._derive_slice(0, len(self.dataset.channel("Elapsed Time").series.values))

        self.assertIsInstance(outcome, GPSPathDistanceSuccess)
        assert isinstance(outcome, GPSPathDistanceSuccess)
        self.assertEqual(len(outcome.path_distance_m), 1962)
        self.assertGreater(outcome.total_distance_m, 940.0)
        self.assertLess(outcome.total_distance_m, 955.0)

    def test_source_lap_two_is_a_closed_complete_path_candidate(self) -> None:
        lap_values = self.dataset.channel("Lap").series.values
        lap_two_indexes = tuple(index for index, value in enumerate(lap_values) if value == "2")

        self.assertEqual(len(lap_two_indexes), 766)
        start = lap_two_indexes[0]
        stop = lap_two_indexes[-1] + 1

        lap_path = self._derive_slice(start, stop)
        self.assertIsInstance(lap_path, GPSPathDistanceSuccess)
        assert isinstance(lap_path, GPSPathDistanceSuccess)
        self.assertGreater(lap_path.total_distance_m, 385.0)
        self.assertLess(lap_path.total_distance_m, 395.0)

        closure = self._derive_indexes(start, stop - 1)
        self.assertIsInstance(closure, GPSPathDistanceSuccess)
        assert isinstance(closure, GPSPathDistanceSuccess)
        self.assertLess(closure.total_distance_m, 2.0)

    def test_lap_two_gps_path_and_source_speed_integral_are_close(self) -> None:
        lap_values = self.dataset.channel("Lap").series.values
        indexes = tuple(index for index, value in enumerate(lap_values) if value == "2")
        start = indexes[0]
        stop = indexes[-1] + 1

        path = self._derive_slice(start, stop)
        self.assertIsInstance(path, GPSPathDistanceSuccess)
        assert isinstance(path, GPSPathDistanceSuccess)

        time_values = self._float_values("Elapsed Time", start, stop)
        speed_mps = tuple(value * 0.44704 for value in self._float_values("Velocity (MPH)", start, stop))

        integrated_m = 0.0
        for index in range(1, len(time_values)):
            delta_time_s = time_values[index] - time_values[index - 1]
            integrated_m += 0.5 * (speed_mps[index - 1] + speed_mps[index]) * delta_time_s

        relative_difference = abs(path.total_distance_m - integrated_m) / integrated_m
        self.assertLess(relative_difference, 0.02)

    def _derive_slice(self, start: int, stop: int):
        times = self._float_values("Elapsed Time", start, stop)
        latitudes = self._float_values("Lat (Degrees)", start, stop)
        longitudes = self._float_values("Lon (Degrees)", start, stop)
        return self.engine.derive(
            self._request(
                timestamps_s=times,
                latitudes_deg=latitudes,
                longitudes_deg=longitudes,
            )
        )

    def _derive_indexes(self, first: int, second: int):
        times = self._float_indexes("Elapsed Time", first, second)
        latitudes = self._float_indexes("Lat (Degrees)", first, second)
        longitudes = self._float_indexes("Lon (Degrees)", first, second)
        return self.engine.derive(
            self._request(
                timestamps_s=times,
                latitudes_deg=latitudes,
                longitudes_deg=longitudes,
            )
        )

    def _request(
        self,
        *,
        timestamps_s: tuple[float, ...],
        latitudes_deg: tuple[float, ...],
        longitudes_deg: tuple[float, ...],
    ) -> GPSPathDistanceRequest:
        fingerprint = self.dataset.provenance.content_fingerprint
        return GPSPathDistanceRequest(
            dataset_fingerprint=fingerprint,
            timestamps_s=timestamps_s,
            latitudes_deg=latitudes_deg,
            longitudes_deg=longitudes_deg,
            latitude_evidence=self._source_evidence("Lat (Degrees)", "deg"),
            longitude_evidence=self._source_evidence("Lon (Degrees)", "deg"),
            time_evidence=self._source_evidence("Elapsed Time", "s"),
        )

    def _source_evidence(self, identifier: str, unit: str) -> SourceSeriesEvidence:
        channel = self.dataset.channel(identifier)
        return SourceSeriesEvidence(
            dataset_fingerprint=self.dataset.provenance.content_fingerprint,
            source_channel_identifier=channel.identifier,
            source_original_name=channel.original_name,
            unit=unit,
        )

    def _float_values(self, identifier: str, start: int, stop: int) -> tuple[float, ...]:
        values = self.dataset.channel(identifier).series.values[start:stop]
        return tuple(float(value) for value in values if value is not None)

    def _float_indexes(self, identifier: str, first: int, second: int) -> tuple[float, ...]:
        values = self.dataset.channel(identifier).series.values
        selected = (values[first], values[second])
        return tuple(float(value) for value in selected if value is not None)


if __name__ == "__main__":
    unittest.main()
