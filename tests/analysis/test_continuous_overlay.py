from __future__ import annotations

import math
import unittest
from dataclasses import replace

from ome.analysis import (
    ContinuousOverlayEngine,
    ContinuousOverlayIssueCode,
    ContinuousOverlayNotReady,
    ContinuousOverlayRequest,
    ContinuousOverlaySeries,
    ContinuousOverlaySuccess,
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
                transformation_id="test.normalization",
                transformation_version="1.0.0",
                parameters={"concept": concept.value},
            ),
        ),
    )


def comparison_lap(
    *,
    label: str,
    elapsed: tuple[float, ...],
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
            values=(0.0, 50.0, 100.0),
            evidence=canonical_evidence(
                dataset_fingerprint=fingerprint,
                concept=CanonicalConcept.LAP_DISTANCE,
                unit="m",
                source_channel_identifier=f"distance-{label}",
                source_original_name=f"Distance {label}",
            ),
        ),
        elapsed_time=LapComparisonSeries(
            values=elapsed,
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
            lap_a=comparison_lap(label="a", elapsed=(0.0, 5.0, 10.0)),
            lap_b=comparison_lap(label="b", elapsed=(0.0, 6.0, 12.0)),
            grid_step_m=25.0,
        )
    )
    assert isinstance(outcome, LapComparisonSuccess)
    return outcome


def overlay_series(
    *,
    side: str,
    concept: CanonicalConcept,
    unit: str,
    timestamps_s: tuple[float, ...],
    values: tuple[float, ...],
    dataset_fingerprint: str | None = None,
) -> ContinuousOverlaySeries:
    fingerprint = dataset_fingerprint or f"sha256:{side}"
    return ContinuousOverlaySeries(
        timestamps_s=timestamps_s,
        values=values,
        evidence=canonical_evidence(
            dataset_fingerprint=fingerprint,
            concept=concept,
            unit=unit,
            source_channel_identifier=f"{concept.value}-{side}",
            source_original_name=f"{concept.value} {side}",
        ),
    )


class Plan010ContinuousOverlayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ContinuousOverlayEngine()
        self.base = base_comparison()

    def test_speed_projects_different_sample_cadences_onto_existing_grid(self) -> None:
        request = ContinuousOverlayRequest(
            base_comparison=self.base,
            canonical_concept=CanonicalConcept.VEHICLE_SPEED,
            lap_a_channel=overlay_series(
                side="a",
                concept=CanonicalConcept.VEHICLE_SPEED,
                unit="m/s",
                timestamps_s=(0.0, 10.0),
                values=(10.0, 30.0),
            ),
            lap_b_channel=overlay_series(
                side="b",
                concept=CanonicalConcept.VEHICLE_SPEED,
                unit="m/s",
                timestamps_s=(0.0, 4.0, 8.0, 12.0),
                values=(11.0, 15.0, 19.0, 23.0),
            ),
        )

        first = self.engine.overlay(request)
        second = self.engine.overlay(request)

        self.assertEqual(first, second)
        self.assertIsInstance(first, ContinuousOverlaySuccess)
        assert isinstance(first, ContinuousOverlaySuccess)

        self.assertIs(first.canonical_concept, CanonicalConcept.VEHICLE_SPEED)
        self.assertEqual(first.unit, "m/s")
        self.assertEqual(first.distance_grid_m, self.base.distance_grid_m)
        self.assertEqual(first.lap_a_values, (10.0, 15.0, 20.0, 25.0, 30.0))
        self.assertEqual(first.lap_b_values, (11.0, 14.0, 17.0, 20.0, 23.0))

    def test_supported_continuous_concepts_require_canonical_units(self) -> None:
        cases = (
            (CanonicalConcept.DRIVER_THROTTLE, "1"),
            (CanonicalConcept.DRIVER_STEERING, "rad"),
            (CanonicalConcept.ENGINE_SPEED, "rad/s"),
        )

        for concept, unit in cases:
            with self.subTest(concept=concept):
                outcome = self.engine.overlay(
                    ContinuousOverlayRequest(
                        base_comparison=self.base,
                        canonical_concept=concept,
                        lap_a_channel=overlay_series(
                            side="a",
                            concept=concept,
                            unit=unit,
                            timestamps_s=(0.0, 5.0, 10.0),
                            values=(1.0, 2.0, 3.0),
                        ),
                        lap_b_channel=overlay_series(
                            side="b",
                            concept=concept,
                            unit=unit,
                            timestamps_s=(0.0, 6.0, 12.0),
                            values=(2.0, 3.0, 4.0),
                        ),
                    )
                )

                self.assertIsInstance(outcome, ContinuousOverlaySuccess)
                assert isinstance(outcome, ContinuousOverlaySuccess)
                self.assertIs(outcome.canonical_concept, concept)
                self.assertEqual(outcome.unit, unit)

    def test_missing_supported_channel_returns_explicit_missing_evidence(self) -> None:
        outcome = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=None,
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(10.0, 20.0),
                ),
            )
        )

        self.assertIsInstance(outcome, ContinuousOverlayNotReady)
        assert isinstance(outcome, ContinuousOverlayNotReady)
        issue = next(
            issue
            for issue in outcome.issues
            if issue.code is ContinuousOverlayIssueCode.MISSING_CHANNEL
        )
        self.assertEqual(issue.lap_side, "A")
        self.assertIs(issue.required_concept, CanonicalConcept.VEHICLE_SPEED)

    def test_brake_and_gear_are_explicitly_unsupported_by_continuous_overlay(self) -> None:
        for concept in (
            CanonicalConcept.DRIVER_BRAKE,
            CanonicalConcept.TRANSMISSION_GEAR,
        ):
            with self.subTest(concept=concept):
                outcome = self.engine.overlay(
                    ContinuousOverlayRequest(
                        base_comparison=self.base,
                        canonical_concept=concept,
                        lap_a_channel=None,
                        lap_b_channel=None,
                    )
                )

                self.assertIsInstance(outcome, ContinuousOverlayNotReady)
                assert isinstance(outcome, ContinuousOverlayNotReady)
                self.assertIn(
                    ContinuousOverlayIssueCode.UNSUPPORTED_CONCEPT,
                    {issue.code for issue in outcome.issues},
                )

    def test_mismatched_concept_and_unit_are_not_compared(self) -> None:
        wrong_concept = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.ENGINE_SPEED,
                    unit="rad/s",
                    timestamps_s=(0.0, 10.0),
                    values=(100.0, 200.0),
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(10.0, 20.0),
                ),
            )
        )
        wrong_unit = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.DRIVER_THROTTLE,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.DRIVER_THROTTLE,
                    unit="%",
                    timestamps_s=(0.0, 10.0),
                    values=(0.0, 100.0),
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.DRIVER_THROTTLE,
                    unit="1",
                    timestamps_s=(0.0, 12.0),
                    values=(0.0, 1.0),
                ),
            )
        )

        self.assertIsInstance(wrong_concept, ContinuousOverlayNotReady)
        self.assertIsInstance(wrong_unit, ContinuousOverlayNotReady)
        assert isinstance(wrong_concept, ContinuousOverlayNotReady)
        assert isinstance(wrong_unit, ContinuousOverlayNotReady)

        self.assertIn(
            ContinuousOverlayIssueCode.INCOMPATIBLE_CONCEPT,
            {issue.code for issue in wrong_concept.issues},
        )
        self.assertIn(
            ContinuousOverlayIssueCode.INCOMPATIBLE_UNIT,
            {issue.code for issue in wrong_unit.issues},
        )

    def test_incompatible_base_comparison_algorithm_returns_not_ready(self) -> None:
        incompatible_base = replace(
            self.base,
            provenance=replace(
                self.base.provenance,
                algorithm_id="other.algorithm",
            ),
        )

        outcome = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=incompatible_base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 10.0),
                    values=(10.0, 30.0),
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(11.0, 23.0),
                ),
            )
        )

        self.assertIsInstance(outcome, ContinuousOverlayNotReady)
        assert isinstance(outcome, ContinuousOverlayNotReady)
        self.assertIn(
            ContinuousOverlayIssueCode.INCOMPATIBLE_BASE_COMPARISON,
            {issue.code for issue in outcome.issues},
        )

    def test_length_mismatch_and_insufficient_samples_are_explicit(self) -> None:
        mismatched = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 5.0, 10.0),
                    values=(10.0, 20.0),
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(11.0, 23.0),
                ),
            )
        )
        insufficient = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0,),
                    values=(10.0,),
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(11.0, 23.0),
                ),
            )
        )

        self.assertIsInstance(mismatched, ContinuousOverlayNotReady)
        self.assertIsInstance(insufficient, ContinuousOverlayNotReady)
        assert isinstance(mismatched, ContinuousOverlayNotReady)
        assert isinstance(insufficient, ContinuousOverlayNotReady)
        self.assertIn(
            ContinuousOverlayIssueCode.LENGTH_MISMATCH,
            {issue.code for issue in mismatched.issues},
        )
        self.assertIn(
            ContinuousOverlayIssueCode.INSUFFICIENT_SAMPLES,
            {issue.code for issue in insufficient.issues},
        )

    def test_non_finite_channel_time_returns_not_ready(self) -> None:
        outcome = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, math.inf),
                    values=(10.0, 20.0),
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(11.0, 23.0),
                ),
            )
        )

        self.assertIsInstance(outcome, ContinuousOverlayNotReady)
        assert isinstance(outcome, ContinuousOverlayNotReady)
        self.assertIn(
            ContinuousOverlayIssueCode.NON_FINITE_TIME,
            {issue.code for issue in outcome.issues},
        )

    def test_non_monotonic_channel_time_returns_not_ready_without_repair(self) -> None:
        channel = overlay_series(
            side="a",
            concept=CanonicalConcept.VEHICLE_SPEED,
            unit="m/s",
            timestamps_s=(0.0, 6.0, 5.0, 10.0),
            values=(10.0, 20.0, 21.0, 30.0),
        )
        before = channel.timestamps_s

        outcome = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=channel,
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(10.0, 20.0),
                ),
            )
        )

        self.assertIsInstance(outcome, ContinuousOverlayNotReady)
        assert isinstance(outcome, ContinuousOverlayNotReady)
        self.assertIn(
            ContinuousOverlayIssueCode.TIME_NOT_STRICTLY_INCREASING,
            {issue.code for issue in outcome.issues},
        )
        self.assertIs(channel.timestamps_s, before)
        self.assertEqual(channel.timestamps_s, (0.0, 6.0, 5.0, 10.0))

    def test_non_finite_channel_value_returns_not_ready(self) -> None:
        outcome = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 10.0),
                    values=(10.0, math.nan),
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(10.0, 20.0),
                ),
            )
        )

        self.assertIsInstance(outcome, ContinuousOverlayNotReady)
        assert isinstance(outcome, ContinuousOverlayNotReady)
        self.assertIn(
            ContinuousOverlayIssueCode.NON_FINITE_VALUE,
            {issue.code for issue in outcome.issues},
        )

    def test_insufficient_temporal_coverage_returns_not_ready_without_extrapolation(self) -> None:
        outcome = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(1.0, 9.0),
                    values=(10.0, 20.0),
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(10.0, 20.0),
                ),
            )
        )

        self.assertIsInstance(outcome, ContinuousOverlayNotReady)
        assert isinstance(outcome, ContinuousOverlayNotReady)
        issue = next(
            issue
            for issue in outcome.issues
            if issue.code is ContinuousOverlayIssueCode.INSUFFICIENT_TIME_COVERAGE
        )
        self.assertEqual(issue.lap_side, "A")

    def test_channel_provenance_and_base_comparison_provenance_remain_inspectable(self) -> None:
        base_before = self.base
        a_channel = overlay_series(
            side="a",
            concept=CanonicalConcept.VEHICLE_SPEED,
            unit="m/s",
            timestamps_s=(0.0, 10.0),
            values=(10.0, 30.0),
        )
        b_channel = overlay_series(
            side="b",
            concept=CanonicalConcept.VEHICLE_SPEED,
            unit="m/s",
            timestamps_s=(0.0, 12.0),
            values=(11.0, 23.0),
        )

        outcome = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=a_channel,
                lap_b_channel=b_channel,
            )
        )

        self.assertIsInstance(outcome, ContinuousOverlaySuccess)
        assert isinstance(outcome, ContinuousOverlaySuccess)

        provenance = outcome.provenance
        self.assertEqual(
            provenance.algorithm_id,
            "ome.lap-overlay.time-linear-on-distance-grid",
        )
        self.assertEqual(provenance.algorithm_version, "0.1.0")
        self.assertEqual(provenance.base_comparison, self.base.provenance)
        self.assertEqual(
            provenance.lap_a_channel.source_channel_identifier,
            "vehicle.speed-a",
        )
        self.assertEqual(
            provenance.lap_b_channel.source_channel_identifier,
            "vehicle.speed-b",
        )
        self.assertEqual(
            provenance.lap_a_channel.transformations[0].transformation_id,
            "test.normalization",
        )
        self.assertIs(self.base, base_before)
        self.assertEqual(outcome.distance_grid_m, self.base.distance_grid_m)

    def test_mismatched_dataset_provenance_returns_not_ready(self) -> None:
        outcome = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 10.0),
                    values=(10.0, 30.0),
                    dataset_fingerprint="sha256:not-lap-a",
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(11.0, 23.0),
                ),
            )
        )

        self.assertIsInstance(outcome, ContinuousOverlayNotReady)
        assert isinstance(outcome, ContinuousOverlayNotReady)
        self.assertIn(
            ContinuousOverlayIssueCode.MISSING_PROVENANCE,
            {issue.code for issue in outcome.issues},
        )

    def test_result_does_not_embed_causal_diagnosis(self) -> None:
        outcome = self.engine.overlay(
            ContinuousOverlayRequest(
                base_comparison=self.base,
                canonical_concept=CanonicalConcept.VEHICLE_SPEED,
                lap_a_channel=overlay_series(
                    side="a",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 10.0),
                    values=(10.0, 30.0),
                ),
                lap_b_channel=overlay_series(
                    side="b",
                    concept=CanonicalConcept.VEHICLE_SPEED,
                    unit="m/s",
                    timestamps_s=(0.0, 12.0),
                    values=(11.0, 23.0),
                ),
            )
        )

        self.assertIsInstance(outcome, ContinuousOverlaySuccess)
        assert isinstance(outcome, ContinuousOverlaySuccess)
        self.assertFalse(hasattr(outcome, "cause"))
        self.assertFalse(hasattr(outcome, "hypothesis"))
        self.assertFalse(hasattr(outcome, "engineering_interpretation"))


if __name__ == "__main__":
    unittest.main()
