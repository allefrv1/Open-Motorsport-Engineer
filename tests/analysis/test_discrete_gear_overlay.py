from __future__ import annotations

import math
import unittest
from dataclasses import replace

from ome.analysis import (
    DiscreteGearOverlayEngine,
    GearOverlayIssueCode,
    GearOverlayNotReady,
    GearOverlayRequest,
    GearOverlaySeries,
    GearOverlaySuccess,
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
    source_original_name: str,
) -> CanonicalSeriesEvidence:
    return CanonicalSeriesEvidence(
        dataset_fingerprint=dataset_fingerprint,
        source_channel_identifier=source_channel_identifier,
        source_original_name=source_original_name,
        canonical_concept=concept,
        unit=unit,
        transformations=(
            TransformationEvidence(
                transformation_id="test.gear-normalization",
                transformation_version="1.0.0",
                parameters={"concept": concept.value},
            ),
        ),
    )


def comparison_lap(
    *,
    label: str,
    elapsed_end_s: float,
) -> LapComparisonLap:
    fingerprint = f"sha256:{label}"
    context = LapEvidenceContext(
        dataset_fingerprint=fingerprint,
        session_identifier="session-practice",
        run_identifier=f"run-{label}",
        lap_identifier=f"lap-{label}",
    )
    return LapComparisonLap(
        context=context,
        distance=LapComparisonSeries(
            values=(0.0, 100.0),
            evidence=canonical_evidence(
                dataset_fingerprint=fingerprint,
                concept=CanonicalConcept.LAP_DISTANCE,
                unit="m",
                source_channel_identifier=f"distance-{label}",
                source_original_name=f"Distance {label}",
            ),
        ),
        elapsed_time=LapComparisonSeries(
            values=(0.0, elapsed_end_s),
            evidence=canonical_evidence(
                dataset_fingerprint=fingerprint,
                concept=CanonicalConcept.TIME_ELAPSED,
                unit="s",
                source_channel_identifier=f"time-{label}",
                source_original_name=f"Time {label}",
            ),
        ),
    )


def base_comparison() -> LapComparisonSuccess:
    outcome = LapComparisonEngine().compare(
        LapComparisonRequest(
            lap_a=comparison_lap(label="a", elapsed_end_s=4.0),
            lap_b=comparison_lap(label="b", elapsed_end_s=6.0),
            grid_step_m=25.0,
        )
    )
    assert isinstance(outcome, LapComparisonSuccess)
    return outcome


def gear_series(
    *,
    side: str,
    timestamps_s: tuple[float, ...],
    values: tuple[int | float | bool | str | None, ...],
    concept: CanonicalConcept = CanonicalConcept.TRANSMISSION_GEAR,
    unit: str = "",
    dataset_fingerprint: str | None = None,
) -> GearOverlaySeries:
    fingerprint = dataset_fingerprint or f"sha256:{side}"
    return GearOverlaySeries(
        timestamps_s=timestamps_s,
        values=values,
        evidence=canonical_evidence(
            dataset_fingerprint=fingerprint,
            concept=concept,
            unit=unit,
            source_channel_identifier=f"gear-{side}",
            source_original_name=f"Gear {side}",
        ),
    )


class Plan011DiscreteGearOverlayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = DiscreteGearOverlayEngine()
        self.base = base_comparison()

    def test_exact_timestamp_and_previous_sample_hold_are_deterministic(self) -> None:
        request = GearOverlayRequest(
            base_comparison=self.base,
            lap_a_gear=gear_series(
                side="a",
                timestamps_s=(0.0, 2.0, 4.0),
                values=(2, 3, 4),
            ),
            lap_b_gear=gear_series(
                side="b",
                timestamps_s=(0.0, 1.5, 4.5, 6.0),
                values=(2, 3, 4, 5),
            ),
        )

        first = self.engine.overlay(request)
        second = self.engine.overlay(request)

        self.assertEqual(first, second)
        self.assertIsInstance(first, GearOverlaySuccess)
        assert isinstance(first, GearOverlaySuccess)

        self.assertIs(first.canonical_concept, CanonicalConcept.TRANSMISSION_GEAR)
        self.assertEqual(first.unit, "")
        self.assertEqual(first.distance_grid_m, (0.0, 25.0, 50.0, 75.0, 100.0))
        self.assertEqual(first.lap_a_gears, (2, 2, 3, 3, 4))
        self.assertEqual(first.lap_b_gears, (2, 3, 3, 4, 5))
        self.assertTrue(all(isinstance(value, int) for value in first.lap_a_gears))
        self.assertTrue(all(isinstance(value, int) for value in first.lap_b_gears))

    def test_missing_gear_evidence_is_explicit(self) -> None:
        outcome = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=None,
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )

        self.assertIsInstance(outcome, GearOverlayNotReady)
        assert isinstance(outcome, GearOverlayNotReady)
        issue = next(
            issue for issue in outcome.issues if issue.code is GearOverlayIssueCode.MISSING_GEAR
        )
        self.assertEqual(issue.lap_side, "A")
        self.assertIs(issue.required_concept, CanonicalConcept.TRANSMISSION_GEAR)

    def test_wrong_concept_or_unit_is_not_sampled_as_gear(self) -> None:
        wrong_concept = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(0.0, 4.0),
                    values=(2, 4),
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )
        wrong_unit = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(0.0, 4.0),
                    values=(2, 4),
                    unit="gear",
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )

        self.assertIsInstance(wrong_concept, GearOverlayNotReady)
        self.assertIsInstance(wrong_unit, GearOverlayNotReady)
        assert isinstance(wrong_concept, GearOverlayNotReady)
        assert isinstance(wrong_unit, GearOverlayNotReady)
        self.assertIn(
            GearOverlayIssueCode.INCOMPATIBLE_CONCEPT,
            {issue.code for issue in wrong_concept.issues},
        )
        self.assertIn(
            GearOverlayIssueCode.INCOMPATIBLE_UNIT,
            {issue.code for issue in wrong_unit.issues},
        )

    def test_non_integer_gear_values_are_rejected(self) -> None:
        invalid_cases = (
            (2, 3.5, 4),
            (2, True, 4),
            (2, "3", 4),
            (2, None, 4),
        )

        for values in invalid_cases:
            with self.subTest(values=values):
                outcome = self.engine.overlay(
                    GearOverlayRequest(
                        base_comparison=self.base,
                        lap_a_gear=gear_series(
                            side="a",
                            timestamps_s=(0.0, 2.0, 4.0),
                            values=values,
                        ),
                        lap_b_gear=gear_series(
                            side="b",
                            timestamps_s=(0.0, 6.0),
                            values=(2, 5),
                        ),
                    )
                )

                self.assertIsInstance(outcome, GearOverlayNotReady)
                assert isinstance(outcome, GearOverlayNotReady)
                self.assertIn(
                    GearOverlayIssueCode.INVALID_GEAR_VALUE,
                    {issue.code for issue in outcome.issues},
                )

    def test_non_monotonic_or_non_finite_timestamps_are_rejected(self) -> None:
        non_monotonic = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(0.0, 3.0, 2.0, 4.0),
                    values=(2, 3, 4, 5),
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )
        non_finite = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(0.0, math.inf),
                    values=(2, 4),
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )

        self.assertIsInstance(non_monotonic, GearOverlayNotReady)
        self.assertIsInstance(non_finite, GearOverlayNotReady)
        assert isinstance(non_monotonic, GearOverlayNotReady)
        assert isinstance(non_finite, GearOverlayNotReady)
        self.assertIn(
            GearOverlayIssueCode.TIME_NOT_STRICTLY_INCREASING,
            {issue.code for issue in non_monotonic.issues},
        )
        self.assertIn(
            GearOverlayIssueCode.NON_FINITE_TIME,
            {issue.code for issue in non_finite.issues},
        )

    def test_length_mismatch_and_empty_series_are_explicit(self) -> None:
        mismatch = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(0.0, 2.0, 4.0),
                    values=(2, 3),
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )
        empty = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(),
                    values=(),
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )

        self.assertIsInstance(mismatch, GearOverlayNotReady)
        self.assertIsInstance(empty, GearOverlayNotReady)
        assert isinstance(mismatch, GearOverlayNotReady)
        assert isinstance(empty, GearOverlayNotReady)
        self.assertIn(
            GearOverlayIssueCode.LENGTH_MISMATCH,
            {issue.code for issue in mismatch.issues},
        )
        self.assertIn(
            GearOverlayIssueCode.INSUFFICIENT_SAMPLES,
            {issue.code for issue in empty.issues},
        )

    def test_insufficient_temporal_coverage_does_not_extrapolate(self) -> None:
        outcome = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(0.5, 3.5),
                    values=(2, 4),
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )

        self.assertIsInstance(outcome, GearOverlayNotReady)
        assert isinstance(outcome, GearOverlayNotReady)
        issue = next(
            issue
            for issue in outcome.issues
            if issue.code is GearOverlayIssueCode.INSUFFICIENT_TIME_COVERAGE
        )
        self.assertEqual(issue.lap_side, "A")

    def test_incompatible_base_comparison_is_explicit(self) -> None:
        incompatible_base = replace(
            self.base,
            provenance=replace(
                self.base.provenance,
                algorithm_version="9.9.9",
            ),
        )
        outcome = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=incompatible_base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(0.0, 4.0),
                    values=(2, 4),
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )

        self.assertIsInstance(outcome, GearOverlayNotReady)
        assert isinstance(outcome, GearOverlayNotReady)
        self.assertIn(
            GearOverlayIssueCode.INCOMPATIBLE_BASE_COMPARISON,
            {issue.code for issue in outcome.issues},
        )

    def test_provenance_preserves_base_and_gear_channel_evidence(self) -> None:
        a_gear = gear_series(
            side="a",
            timestamps_s=(0.0, 2.0, 4.0),
            values=(2, 3, 4),
        )
        b_gear = gear_series(
            side="b",
            timestamps_s=(0.0, 3.0, 6.0),
            values=(2, 4, 5),
        )
        outcome = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=a_gear,
                lap_b_gear=b_gear,
            )
        )

        self.assertIsInstance(outcome, GearOverlaySuccess)
        assert isinstance(outcome, GearOverlaySuccess)

        provenance = outcome.provenance
        self.assertEqual(
            provenance.algorithm_id,
            "ome.lap-overlay.gear-previous-sample-on-distance-grid",
        )
        self.assertEqual(provenance.algorithm_version, "0.1.0")
        self.assertEqual(provenance.base_comparison, self.base.provenance)
        self.assertEqual(
            provenance.lap_a_gear.source_channel_identifier,
            "gear-a",
        )
        self.assertEqual(
            provenance.lap_b_gear.source_channel_identifier,
            "gear-b",
        )
        self.assertEqual(
            provenance.lap_a_gear.transformations[0].transformation_id,
            "test.gear-normalization",
        )
        self.assertEqual(outcome.distance_grid_m, self.base.distance_grid_m)

    def test_mismatched_dataset_provenance_is_not_ready(self) -> None:
        outcome = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(0.0, 4.0),
                    values=(2, 4),
                    dataset_fingerprint="sha256:not-lap-a",
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )

        self.assertIsInstance(outcome, GearOverlayNotReady)
        assert isinstance(outcome, GearOverlayNotReady)
        self.assertIn(
            GearOverlayIssueCode.MISSING_PROVENANCE,
            {issue.code for issue in outcome.issues},
        )

    def test_result_has_no_causal_or_recommendation_fields(self) -> None:
        outcome = self.engine.overlay(
            GearOverlayRequest(
                base_comparison=self.base,
                lap_a_gear=gear_series(
                    side="a",
                    timestamps_s=(0.0, 4.0),
                    values=(2, 4),
                ),
                lap_b_gear=gear_series(
                    side="b",
                    timestamps_s=(0.0, 6.0),
                    values=(2, 5),
                ),
            )
        )

        self.assertIsInstance(outcome, GearOverlaySuccess)
        assert isinstance(outcome, GearOverlaySuccess)
        self.assertFalse(hasattr(outcome, "cause"))
        self.assertFalse(hasattr(outcome, "recommendation"))
        self.assertFalse(hasattr(outcome, "engineering_interpretation"))


if __name__ == "__main__":
    unittest.main()
