from __future__ import annotations

import math
import unittest
from dataclasses import replace

from ome.analysis import (
    DeltaObservationEngine,
    DeltaObservationIssueCode,
    DeltaObservationNotReady,
    DeltaObservationRequest,
    DeltaObservationSuccess,
    DeltaRegionKind,
    LapComparisonEngine,
    LapComparisonLap,
    LapComparisonRequest,
    LapComparisonSeries,
    LapComparisonSuccess,
)
from ome.domain import CanonicalConcept
from ome.evidence import (
    CanonicalSeriesEvidence,
    LapEvidenceContext,
    TransformationEvidence,
)


def canonical_evidence(
    *,
    dataset_fingerprint: str,
    concept: CanonicalConcept,
    unit: str,
    source_channel_identifier: str,
) -> CanonicalSeriesEvidence:
    return CanonicalSeriesEvidence(
        dataset_fingerprint=dataset_fingerprint,
        source_channel_identifier=source_channel_identifier,
        source_original_name=source_channel_identifier,
        canonical_concept=concept,
        unit=unit,
        transformations=(
            TransformationEvidence(
                transformation_id="test.normalization",
                transformation_version="1.0.0",
            ),
        ),
    )


def comparison_lap(
    *,
    side: str,
    distance_m: tuple[float, ...],
    elapsed_s: tuple[float, ...],
) -> LapComparisonLap:
    fingerprint = f"sha256:{side}"
    context = LapEvidenceContext(
        dataset_fingerprint=fingerprint,
        session_identifier="session-test",
        run_identifier=f"run-{side}",
        lap_identifier=f"lap-{side}",
    )
    return LapComparisonLap(
        context=context,
        distance=LapComparisonSeries(
            values=distance_m,
            evidence=canonical_evidence(
                dataset_fingerprint=fingerprint,
                concept=CanonicalConcept.LAP_DISTANCE,
                unit="m",
                source_channel_identifier=f"distance-{side}",
            ),
        ),
        elapsed_time=LapComparisonSeries(
            values=elapsed_s,
            evidence=canonical_evidence(
                dataset_fingerprint=fingerprint,
                concept=CanonicalConcept.TIME_ELAPSED,
                unit="s",
                source_channel_identifier=f"time-{side}",
            ),
        ),
    )


def comparison_with_delta(
    delta_b_vs_a_s: tuple[float, ...],
) -> LapComparisonSuccess:
    distance_m = tuple(float(index * 10) for index in range(len(delta_b_vs_a_s)))
    lap_a_elapsed_s = tuple(float(index * 10) for index in range(len(delta_b_vs_a_s)))
    lap_b_elapsed_s = tuple(
        elapsed + delta
        for elapsed, delta in zip(
            lap_a_elapsed_s,
            delta_b_vs_a_s,
            strict=True,
        )
    )

    outcome = LapComparisonEngine().compare(
        LapComparisonRequest(
            lap_a=comparison_lap(
                side="a",
                distance_m=distance_m,
                elapsed_s=lap_a_elapsed_s,
            ),
            lap_b=comparison_lap(
                side="b",
                distance_m=distance_m,
                elapsed_s=lap_b_elapsed_s,
            ),
            grid_step_m=10.0,
        )
    )
    assert isinstance(outcome, LapComparisonSuccess)
    assert outcome.delta_b_vs_a_s == delta_b_vs_a_s
    return outcome


class Plan013DeltaObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = DeltaObservationEngine()

    def test_known_positive_delta_change_is_b_loss(self) -> None:
        base = comparison_with_delta((0.0, 0.1, 0.3))

        outcome = self.engine.observe(DeltaObservationRequest(base_comparison=base))

        self.assertIsInstance(outcome, DeltaObservationSuccess)
        assert isinstance(outcome, DeltaObservationSuccess)
        self.assertEqual(len(outcome.regions), 1)
        region = outcome.regions[0]
        self.assertIs(region.kind, DeltaRegionKind.B_LOSS)
        self.assertEqual(region.start_distance_m, 0.0)
        self.assertEqual(region.end_distance_m, 20.0)
        self.assertEqual(region.start_delta_s, 0.0)
        self.assertEqual(region.end_delta_s, 0.3)
        self.assertAlmostEqual(region.total_delta_change_s, 0.3)
        self.assertEqual(region.interval_count, 2)

    def test_known_negative_delta_change_is_b_gain(self) -> None:
        base = comparison_with_delta((0.0, -0.1, -0.25))

        outcome = self.engine.observe(DeltaObservationRequest(base_comparison=base))

        self.assertIsInstance(outcome, DeltaObservationSuccess)
        assert isinstance(outcome, DeltaObservationSuccess)
        region = outcome.regions[0]
        self.assertIs(region.kind, DeltaRegionKind.B_GAIN)
        self.assertAlmostEqual(region.total_delta_change_s, -0.25)

    def test_equal_delta_is_neutral(self) -> None:
        base = comparison_with_delta((0.2, 0.2, 0.2))

        outcome = self.engine.observe(DeltaObservationRequest(base_comparison=base))

        self.assertIsInstance(outcome, DeltaObservationSuccess)
        assert isinstance(outcome, DeltaObservationSuccess)
        self.assertEqual(len(outcome.regions), 1)
        self.assertIs(outcome.regions[0].kind, DeltaRegionKind.NEUTRAL)
        self.assertEqual(outcome.regions[0].total_delta_change_s, 0.0)

    def test_contiguous_same_kind_intervals_are_merged(self) -> None:
        base = comparison_with_delta((0.0, 0.1, 0.2, 0.2, 0.1, 0.0))

        outcome = self.engine.observe(DeltaObservationRequest(base_comparison=base))

        self.assertIsInstance(outcome, DeltaObservationSuccess)
        assert isinstance(outcome, DeltaObservationSuccess)
        self.assertEqual(
            tuple(region.kind for region in outcome.regions),
            (
                DeltaRegionKind.B_LOSS,
                DeltaRegionKind.NEUTRAL,
                DeltaRegionKind.B_GAIN,
            ),
        )
        self.assertEqual(
            tuple(
                (region.start_distance_m, region.end_distance_m, region.interval_count)
                for region in outcome.regions
            ),
            ((0.0, 20.0, 2), (20.0, 30.0, 1), (30.0, 50.0, 2)),
        )
        self.assertAlmostEqual(outcome.regions[0].total_delta_change_s, 0.2)
        self.assertAlmostEqual(outcome.regions[1].total_delta_change_s, 0.0)
        self.assertAlmostEqual(outcome.regions[2].total_delta_change_s, -0.2)

    def test_region_delta_change_is_end_minus_start(self) -> None:
        base = comparison_with_delta((0.05, 0.10, 0.22, 0.40))

        outcome = self.engine.observe(DeltaObservationRequest(base_comparison=base))

        self.assertIsInstance(outcome, DeltaObservationSuccess)
        assert isinstance(outcome, DeltaObservationSuccess)
        region = outcome.regions[0]
        self.assertAlmostEqual(
            region.total_delta_change_s,
            region.end_delta_s - region.start_delta_s,
        )

    def test_zero_tolerance_is_explicit_and_deterministic(self) -> None:
        base = comparison_with_delta((0.0, 5e-10, 0.1))
        request = DeltaObservationRequest(
            base_comparison=base,
            zero_tolerance_s=1e-9,
        )

        first = self.engine.observe(request)
        second = self.engine.observe(request)

        self.assertEqual(first, second)
        self.assertIsInstance(first, DeltaObservationSuccess)
        assert isinstance(first, DeltaObservationSuccess)
        self.assertEqual(
            tuple(region.kind for region in first.regions),
            (DeltaRegionKind.NEUTRAL, DeltaRegionKind.B_LOSS),
        )
        self.assertEqual(first.provenance.parameters["zero_tolerance_s"], 1e-9)

    def test_invalid_zero_tolerance_returns_not_ready(self) -> None:
        base = comparison_with_delta((0.0, 0.1))
        for value in (-1.0, math.inf, math.nan):
            with self.subTest(value=value):
                outcome = self.engine.observe(
                    DeltaObservationRequest(
                        base_comparison=base,
                        zero_tolerance_s=value,
                    )
                )
                self.assertIsInstance(outcome, DeltaObservationNotReady)
                assert isinstance(outcome, DeltaObservationNotReady)
                self.assertIn(
                    DeltaObservationIssueCode.INVALID_ZERO_TOLERANCE,
                    {issue.code for issue in outcome.issues},
                )

    def test_missing_base_comparison_returns_not_ready(self) -> None:
        outcome = self.engine.observe(DeltaObservationRequest(base_comparison=None))

        self.assertIsInstance(outcome, DeltaObservationNotReady)
        assert isinstance(outcome, DeltaObservationNotReady)
        self.assertIn(
            DeltaObservationIssueCode.MISSING_BASE_COMPARISON,
            {issue.code for issue in outcome.issues},
        )

    def test_incompatible_base_algorithm_returns_not_ready(self) -> None:
        base = comparison_with_delta((0.0, 0.1))
        incompatible = replace(
            base,
            provenance=replace(
                base.provenance,
                algorithm_id="other.algorithm",
            ),
        )

        outcome = self.engine.observe(DeltaObservationRequest(base_comparison=incompatible))

        self.assertIsInstance(outcome, DeltaObservationNotReady)
        assert isinstance(outcome, DeltaObservationNotReady)
        self.assertIn(
            DeltaObservationIssueCode.INCOMPATIBLE_BASE_COMPARISON,
            {issue.code for issue in outcome.issues},
        )

    def test_length_mismatch_and_insufficient_grid_are_explicit(self) -> None:
        base = comparison_with_delta((0.0, 0.1, 0.2))
        mismatched = replace(
            base,
            delta_b_vs_a_s=base.delta_b_vs_a_s[:-1],
        )
        insufficient = replace(
            base,
            distance_grid_m=(0.0,),
            lap_a_elapsed_s=(0.0,),
            lap_b_elapsed_s=(0.0,),
            delta_b_vs_a_s=(0.0,),
        )

        mismatch_outcome = self.engine.observe(DeltaObservationRequest(base_comparison=mismatched))
        insufficient_outcome = self.engine.observe(
            DeltaObservationRequest(base_comparison=insufficient)
        )

        self.assertIsInstance(mismatch_outcome, DeltaObservationNotReady)
        self.assertIsInstance(insufficient_outcome, DeltaObservationNotReady)
        assert isinstance(mismatch_outcome, DeltaObservationNotReady)
        assert isinstance(insufficient_outcome, DeltaObservationNotReady)
        self.assertIn(
            DeltaObservationIssueCode.LENGTH_MISMATCH,
            {issue.code for issue in mismatch_outcome.issues},
        )
        self.assertIn(
            DeltaObservationIssueCode.INSUFFICIENT_GRID,
            {issue.code for issue in insufficient_outcome.issues},
        )

    def test_non_monotonic_or_non_finite_base_data_is_not_repaired(self) -> None:
        base = comparison_with_delta((0.0, 0.1, 0.2))
        non_monotonic = replace(base, distance_grid_m=(0.0, 20.0, 10.0))
        non_finite_distance = replace(base, distance_grid_m=(0.0, 10.0, math.inf))
        non_finite_delta = replace(base, delta_b_vs_a_s=(0.0, math.nan, 0.2))

        outcomes = (
            (
                self.engine.observe(DeltaObservationRequest(base_comparison=non_monotonic)),
                DeltaObservationIssueCode.DISTANCE_NOT_STRICTLY_INCREASING,
            ),
            (
                self.engine.observe(DeltaObservationRequest(base_comparison=non_finite_distance)),
                DeltaObservationIssueCode.NON_FINITE_DISTANCE,
            ),
            (
                self.engine.observe(DeltaObservationRequest(base_comparison=non_finite_delta)),
                DeltaObservationIssueCode.NON_FINITE_DELTA,
            ),
        )

        for outcome, expected_code in outcomes:
            self.assertIsInstance(outcome, DeltaObservationNotReady)
            assert isinstance(outcome, DeltaObservationNotReady)
            self.assertIn(expected_code, {issue.code for issue in outcome.issues})

        self.assertEqual(non_monotonic.distance_grid_m, (0.0, 20.0, 10.0))

    def test_provenance_retains_complete_base_comparison(self) -> None:
        base = comparison_with_delta((0.0, -0.1, -0.2))

        outcome = self.engine.observe(DeltaObservationRequest(base_comparison=base))

        self.assertIsInstance(outcome, DeltaObservationSuccess)
        assert isinstance(outcome, DeltaObservationSuccess)
        self.assertEqual(
            outcome.provenance.algorithm_id,
            "ome.lap-observation.delta-regions",
        )
        self.assertEqual(outcome.provenance.algorithm_version, "0.1.0")
        self.assertEqual(outcome.provenance.base_comparison, base.provenance)
        self.assertEqual(
            outcome.provenance.base_comparison.lap_a.context.lap_identifier,
            "lap-a",
        )
        self.assertEqual(
            outcome.provenance.base_comparison.lap_b.context.lap_identifier,
            "lap-b",
        )

    def test_result_is_observation_only_without_causal_fields(self) -> None:
        base = comparison_with_delta((0.0, -0.1, 0.0))

        outcome = self.engine.observe(DeltaObservationRequest(base_comparison=base))

        self.assertIsInstance(outcome, DeltaObservationSuccess)
        assert isinstance(outcome, DeltaObservationSuccess)
        self.assertFalse(hasattr(outcome, "cause"))
        self.assertFalse(hasattr(outcome, "hypothesis"))
        self.assertFalse(hasattr(outcome, "engineering_interpretation"))
        self.assertFalse(hasattr(outcome, "recommendation"))


if __name__ == "__main__":
    unittest.main()
