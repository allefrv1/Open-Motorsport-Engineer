from __future__ import annotations

import math
import unittest

from ome.analysis import (
    ComparisonIssueCode,
    LapComparisonEngine,
    LapComparisonLap,
    LapComparisonNotReady,
    LapComparisonRequest,
    LapComparisonSeries,
    LapComparisonSuccess,
)
from ome.domain import CanonicalConcept
from ome.evidence import CanonicalSeriesEvidence, LapEvidenceContext, TransformationEvidence


def series_evidence(
    *,
    dataset_fingerprint: str,
    concept: CanonicalConcept,
    unit: str,
    source_channel_identifier: str,
    source_original_name: str,
    transformations: tuple[TransformationEvidence, ...] = (),
) -> CanonicalSeriesEvidence:
    return CanonicalSeriesEvidence(
        dataset_fingerprint=dataset_fingerprint,
        source_channel_identifier=source_channel_identifier,
        source_original_name=source_original_name,
        canonical_concept=concept,
        unit=unit,
        transformations=transformations,
    )


def lap(
    *,
    label: str,
    distance: tuple[float, ...] | None,
    elapsed: tuple[float, ...] | None,
    distance_concept: CanonicalConcept = CanonicalConcept.LAP_DISTANCE,
    distance_unit: str = "m",
    time_concept: CanonicalConcept = CanonicalConcept.TIME_ELAPSED,
    time_unit: str = "s",
    session_identifier: str | None = None,
    run_identifier: str | None = None,
    lap_identifier: str | None = None,
) -> LapComparisonLap:
    fingerprint = f"sha256:{label}"
    context = LapEvidenceContext(
        dataset_fingerprint=fingerprint,
        session_identifier=(
            f"session-{label}" if session_identifier is None else session_identifier
        ),
        run_identifier=f"run-{label}" if run_identifier is None else run_identifier,
        lap_identifier=f"lap-{label}" if lap_identifier is None else lap_identifier,
    )

    distance_series = None
    if distance is not None:
        distance_series = LapComparisonSeries(
            values=distance,
            evidence=series_evidence(
                dataset_fingerprint=fingerprint,
                concept=distance_concept,
                unit=distance_unit,
                source_channel_identifier=f"distance-{label}",
                source_original_name=f"Distance {label}",
                transformations=(
                    TransformationEvidence(
                        transformation_id="test.distance-normalization",
                        transformation_version="1.0.0",
                        parameters={"fixture": label},
                    ),
                ),
            ),
        )

    elapsed_series = None
    if elapsed is not None:
        elapsed_series = LapComparisonSeries(
            values=elapsed,
            evidence=series_evidence(
                dataset_fingerprint=fingerprint,
                concept=time_concept,
                unit=time_unit,
                source_channel_identifier=f"time-{label}",
                source_original_name=f"Time {label}",
                transformations=(
                    TransformationEvidence(
                        transformation_id="test.time-normalization",
                        transformation_version="1.0.0",
                        parameters={"fixture": label},
                    ),
                ),
            ),
        )

    return LapComparisonLap(
        context=context,
        distance=distance_series,
        elapsed_time=elapsed_series,
    )


class Req005LapComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = LapComparisonEngine()

    def test_ac001_result_declares_explicit_distance_reference(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 50.0, 100.0),
                elapsed=(0.0, 5.0, 10.0),
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 50.0, 100.0),
                elapsed=(0.0, 5.0, 10.0),
            ),
            grid_step_m=25.0,
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonSuccess)
        assert isinstance(result, LapComparisonSuccess)
        self.assertIs(result.reference_concept, CanonicalConcept.LAP_DISTANCE)
        self.assertEqual(result.reference_unit, "m")
        self.assertIs(result.time_concept, CanonicalConcept.TIME_ELAPSED)
        self.assertEqual(result.time_unit, "s")

    def test_ac002_known_delta_is_deterministic_with_documented_sign(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 50.0, 100.0),
                elapsed=(0.0, 5.0, 10.0),
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 25.0, 75.0, 100.0),
                elapsed=(0.0, 3.0, 9.0, 12.0),
            ),
            grid_step_m=25.0,
        )

        first = self.engine.compare(request)
        second = self.engine.compare(request)

        self.assertEqual(first, second)
        self.assertIsInstance(first, LapComparisonSuccess)
        assert isinstance(first, LapComparisonSuccess)

        self.assertEqual(first.distance_grid_m, (0.0, 25.0, 50.0, 75.0, 100.0))
        self.assertEqual(first.lap_a_elapsed_s, (0.0, 2.5, 5.0, 7.5, 10.0))
        self.assertEqual(first.lap_b_elapsed_s, (0.0, 3.0, 6.0, 9.0, 12.0))
        self.assertEqual(first.delta_b_vs_a_s, (0.0, 0.5, 1.0, 1.5, 2.0))
        self.assertGreater(first.delta_b_vs_a_s[-1], 0.0)

    def test_equal_laps_produce_zero_delta(self) -> None:
        common = dict(
            distance=(0.0, 30.0, 70.0, 100.0),
            elapsed=(0.0, 3.0, 7.0, 10.0),
        )
        request = LapComparisonRequest(
            lap_a=lap(label="a", **common),
            lap_b=lap(label="b", **common),
            grid_step_m=20.0,
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonSuccess)
        assert isinstance(result, LapComparisonSuccess)
        self.assertTrue(all(delta == 0.0 for delta in result.delta_b_vs_a_s))

    def test_grid_includes_exact_common_end_when_step_does_not_land_on_it(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 95.0),
                elapsed=(0.0, 9.5),
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 95.0),
                elapsed=(0.0, 9.5),
            ),
            grid_step_m=30.0,
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonSuccess)
        assert isinstance(result, LapComparisonSuccess)
        self.assertEqual(result.distance_grid_m, (0.0, 30.0, 60.0, 90.0, 95.0))

    def test_partial_overlap_uses_only_common_distance_interval(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 50.0, 100.0),
                elapsed=(0.0, 5.0, 10.0),
            ),
            lap_b=lap(
                label="b",
                distance=(20.0, 50.0, 80.0),
                elapsed=(2.0, 5.0, 8.0),
            ),
            grid_step_m=20.0,
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonSuccess)
        assert isinstance(result, LapComparisonSuccess)
        self.assertEqual(result.common_start_m, 20.0)
        self.assertEqual(result.common_end_m, 80.0)
        self.assertEqual(result.distance_grid_m, (20.0, 40.0, 60.0, 80.0))
        self.assertEqual(result.delta_b_vs_a_s, (0.0, 0.0, 0.0, 0.0))

    def test_ac003_missing_distance_returns_not_ready_with_missing_evidence(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 100.0),
                elapsed=(0.0, 10.0),
            ),
            lap_b=lap(
                label="b",
                distance=None,
                elapsed=(0.0, 10.0),
            ),
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        issue = next(
            issue for issue in result.issues if issue.code is ComparisonIssueCode.MISSING_DISTANCE
        )
        self.assertEqual(issue.lap_side, "B")
        self.assertIs(issue.required_concept, CanonicalConcept.LAP_DISTANCE)

    def test_wrong_reference_concept_returns_not_ready(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 100.0),
                elapsed=(0.0, 10.0),
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 100.0),
                elapsed=(0.0, 10.0),
                distance_concept=CanonicalConcept.VEHICLE_SPEED,
            ),
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        self.assertIn(
            ComparisonIssueCode.INCOMPATIBLE_DISTANCE_REFERENCE,
            {issue.code for issue in result.issues},
        )

    def test_true_distance_decrease_returns_not_ready_without_repair(self) -> None:
        lap_b = lap(
            label="b",
            distance=(0.0, 60.0, 50.0, 100.0),
            elapsed=(0.0, 6.0, 7.0, 11.0),
        )
        before = lap_b.distance

        result = self.engine.compare(
            LapComparisonRequest(
                lap_a=lap(
                    label="a",
                    distance=(0.0, 50.0, 100.0),
                    elapsed=(0.0, 5.0, 10.0),
                ),
                lap_b=lap_b,
            )
        )

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        self.assertIn(
            ComparisonIssueCode.DISTANCE_DECREASES,
            {issue.code for issue in result.issues},
        )
        self.assertIs(lap_b.distance, before)
        assert lap_b.distance is not None
        self.assertEqual(lap_b.distance.values, (0.0, 60.0, 50.0, 100.0))

    def test_non_monotonic_elapsed_time_returns_not_ready(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 50.0, 100.0),
                elapsed=(0.0, 5.0, 10.0),
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 50.0, 100.0),
                elapsed=(0.0, 6.0, 5.0),
            ),
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        self.assertIn(
            ComparisonIssueCode.TIME_NOT_STRICTLY_INCREASING,
            {issue.code for issue in result.issues},
        )

    def test_non_finite_input_returns_not_ready(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, math.nan, 100.0),
                elapsed=(0.0, 5.0, 10.0),
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 50.0, 100.0),
                elapsed=(0.0, 5.0, 10.0),
            ),
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        self.assertIn(
            ComparisonIssueCode.NON_FINITE_DISTANCE,
            {issue.code for issue in result.issues},
        )

    def test_no_common_distance_returns_not_ready(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 20.0, 40.0),
                elapsed=(0.0, 2.0, 4.0),
            ),
            lap_b=lap(
                label="b",
                distance=(50.0, 75.0, 100.0),
                elapsed=(5.0, 7.5, 10.0),
            ),
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        self.assertIn(
            ComparisonIssueCode.NO_COMMON_DISTANCE,
            {issue.code for issue in result.issues},
        )

    def test_invalid_grid_step_returns_not_ready(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 100.0),
                elapsed=(0.0, 10.0),
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 100.0),
                elapsed=(0.0, 10.0),
            ),
            grid_step_m=0.0,
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        self.assertIn(
            ComparisonIssueCode.INVALID_GRID_STEP,
            {issue.code for issue in result.issues},
        )

    def test_ac005_and_ac006_provenance_preserves_context_channels_and_algorithm(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 50.0, 100.0),
                elapsed=(0.0, 5.0, 10.0),
                session_identifier="session-practice",
                run_identifier="run-1",
                lap_identifier="lap-3",
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 50.0, 100.0),
                elapsed=(0.0, 5.5, 11.0),
                session_identifier="session-practice",
                run_identifier="run-2",
                lap_identifier="lap-7",
            ),
            grid_step_m=25.0,
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonSuccess)
        assert isinstance(result, LapComparisonSuccess)

        provenance = result.provenance
        self.assertEqual(provenance.algorithm_id, "ome.lap-comparison.distance-linear")
        self.assertEqual(provenance.algorithm_version, "0.2.0")
        self.assertEqual(provenance.parameters["grid_step_m"], 25.0)
        self.assertEqual(provenance.lap_a.context.session_identifier, "session-practice")
        self.assertEqual(provenance.lap_a.context.run_identifier, "run-1")
        self.assertEqual(provenance.lap_a.context.lap_identifier, "lap-3")
        self.assertEqual(provenance.lap_b.context.run_identifier, "run-2")
        self.assertEqual(provenance.lap_b.context.lap_identifier, "lap-7")
        self.assertEqual(
            provenance.lap_a.distance.source_channel_identifier,
            "distance-a",
        )
        self.assertEqual(
            provenance.lap_b.elapsed_time.source_channel_identifier,
            "time-b",
        )
        self.assertEqual(
            provenance.lap_a.distance.transformations[0].transformation_id,
            "test.distance-normalization",
        )

    def test_v02_accepts_plateau_and_preserves_input_values(self) -> None:
        lap_a = lap(
            label="a",
            distance=(0.0, 10.0, 10.0, 20.0),
            elapsed=(0.0, 1.0, 2.0, 3.0),
        )
        lap_b = lap(
            label="b",
            distance=(0.0, 10.0, 10.0, 20.0),
            elapsed=(0.0, 1.0, 2.0, 3.0),
        )
        before_a = lap_a.distance
        before_b = lap_b.distance

        result = self.engine.compare(
            LapComparisonRequest(
                lap_a=lap_a,
                lap_b=lap_b,
                grid_step_m=5.0,
            )
        )

        self.assertIsInstance(result, LapComparisonSuccess)
        assert isinstance(result, LapComparisonSuccess)
        self.assertEqual(result.distance_grid_m, (0.0, 5.0, 10.0, 15.0, 20.0))
        self.assertEqual(result.lap_a_elapsed_s, (0.0, 0.5, 2.0, 2.5, 3.0))
        self.assertEqual(result.lap_b_elapsed_s, (0.0, 0.5, 2.0, 2.5, 3.0))
        self.assertTrue(all(delta == 0.0 for delta in result.delta_b_vs_a_s))

        self.assertIs(lap_a.distance, before_a)
        self.assertIs(lap_b.distance, before_b)
        assert lap_a.distance is not None
        assert lap_b.distance is not None
        self.assertEqual(lap_a.distance.values, (0.0, 10.0, 10.0, 20.0))
        self.assertEqual(lap_b.distance.values, (0.0, 10.0, 10.0, 20.0))

    def test_v02_plateau_dwell_time_remains_in_downstream_delta(self) -> None:
        result = self.engine.compare(
            LapComparisonRequest(
                lap_a=lap(
                    label="a",
                    distance=(0.0, 10.0, 20.0),
                    elapsed=(0.0, 1.0, 2.0),
                ),
                lap_b=lap(
                    label="b",
                    distance=(0.0, 10.0, 10.0, 20.0),
                    elapsed=(0.0, 1.0, 2.0, 3.0),
                ),
                grid_step_m=5.0,
            )
        )

        self.assertIsInstance(result, LapComparisonSuccess)
        assert isinstance(result, LapComparisonSuccess)
        self.assertEqual(result.lap_a_elapsed_s, (0.0, 0.5, 1.0, 1.5, 2.0))
        self.assertEqual(result.lap_b_elapsed_s, (0.0, 0.5, 2.0, 2.5, 3.0))
        self.assertEqual(result.delta_b_vs_a_s, (0.0, 0.0, 1.0, 1.0, 1.0))

    def test_v02_multiple_plateaus_are_deterministic(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 10.0, 10.0, 20.0, 20.0, 30.0),
                elapsed=(0.0, 1.0, 2.0, 3.0, 4.0, 5.0),
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 10.0, 10.0, 20.0, 20.0, 30.0),
                elapsed=(0.0, 1.0, 2.0, 3.0, 4.0, 5.0),
            ),
            grid_step_m=5.0,
        )

        first = self.engine.compare(request)
        second = self.engine.compare(request)

        self.assertEqual(first, second)
        self.assertIsInstance(first, LapComparisonSuccess)
        assert isinstance(first, LapComparisonSuccess)
        self.assertEqual(
            first.lap_a_elapsed_s,
            (0.0, 0.5, 2.0, 2.5, 4.0, 4.5, 5.0),
        )

    def test_v02_true_distance_decrease_is_not_ready_without_repair(self) -> None:
        lap_b = lap(
            label="b",
            distance=(0.0, 10.0, 9.0, 20.0),
            elapsed=(0.0, 1.0, 2.0, 3.0),
        )
        before = lap_b.distance

        result = self.engine.compare(
            LapComparisonRequest(
                lap_a=lap(
                    label="a",
                    distance=(0.0, 10.0, 20.0),
                    elapsed=(0.0, 1.0, 2.0),
                ),
                lap_b=lap_b,
            )
        )

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        self.assertIn(
            ComparisonIssueCode.DISTANCE_DECREASES,
            {issue.code for issue in result.issues},
        )
        self.assertIs(lap_b.distance, before)
        assert lap_b.distance is not None
        self.assertEqual(lap_b.distance.values, (0.0, 10.0, 9.0, 20.0))

    def test_v02_elapsed_time_still_requires_strict_increase(self) -> None:
        result = self.engine.compare(
            LapComparisonRequest(
                lap_a=lap(
                    label="a",
                    distance=(0.0, 10.0, 10.0, 20.0),
                    elapsed=(0.0, 1.0, 2.0, 3.0),
                ),
                lap_b=lap(
                    label="b",
                    distance=(0.0, 10.0, 10.0, 20.0),
                    elapsed=(0.0, 1.0, 1.0, 3.0),
                ),
            )
        )

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        self.assertIn(
            ComparisonIssueCode.TIME_NOT_STRICTLY_INCREASING,
            {issue.code for issue in result.issues},
        )

    def test_v02_no_plateau_inputs_keep_existing_numerical_output(self) -> None:
        result = self.engine.compare(
            LapComparisonRequest(
                lap_a=lap(
                    label="a",
                    distance=(0.0, 25.0, 75.0, 100.0),
                    elapsed=(0.0, 2.5, 7.5, 10.0),
                ),
                lap_b=lap(
                    label="b",
                    distance=(0.0, 50.0, 100.0),
                    elapsed=(0.0, 6.0, 12.0),
                ),
                grid_step_m=25.0,
            )
        )

        self.assertIsInstance(result, LapComparisonSuccess)
        assert isinstance(result, LapComparisonSuccess)
        self.assertEqual(result.distance_grid_m, (0.0, 25.0, 50.0, 75.0, 100.0))
        self.assertEqual(result.lap_a_elapsed_s, (0.0, 2.5, 5.0, 7.5, 10.0))
        self.assertEqual(result.lap_b_elapsed_s, (0.0, 3.0, 6.0, 9.0, 12.0))
        self.assertEqual(result.delta_b_vs_a_s, (0.0, 0.5, 1.0, 1.5, 2.0))
        self.assertEqual(result.provenance.algorithm_version, "0.2.0")

    def test_missing_context_provenance_returns_not_ready(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 100.0),
                elapsed=(0.0, 10.0),
                lap_identifier="",
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 100.0),
                elapsed=(0.0, 10.0),
            ),
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonNotReady)
        assert isinstance(result, LapComparisonNotReady)
        self.assertIn(
            ComparisonIssueCode.MISSING_PROVENANCE,
            {issue.code for issue in result.issues},
        )

    def test_ac004_result_does_not_embed_causal_diagnosis(self) -> None:
        request = LapComparisonRequest(
            lap_a=lap(
                label="a",
                distance=(0.0, 100.0),
                elapsed=(0.0, 10.0),
            ),
            lap_b=lap(
                label="b",
                distance=(0.0, 100.0),
                elapsed=(0.0, 11.0),
            ),
        )

        result = self.engine.compare(request)

        self.assertIsInstance(result, LapComparisonSuccess)
        assert isinstance(result, LapComparisonSuccess)
        self.assertFalse(hasattr(result, "cause"))
        self.assertFalse(hasattr(result, "hypothesis"))
        self.assertFalse(hasattr(result, "engineering_interpretation"))


if __name__ == "__main__":
    unittest.main()
