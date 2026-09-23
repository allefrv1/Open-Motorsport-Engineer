from __future__ import annotations

import unittest

from ome.analysis import (
    ContinuousOverlaySeries,
    DeltaRegionKind,
    GearOverlaySeries,
    LapComparisonLap,
    LapComparisonRequest,
    LapComparisonSeries,
)
from ome.application import (
    ComparisonReportIssueCode,
    ComparisonReportNotReady,
    ComparisonReportRequest,
    ComparisonReportService,
    ComparisonReportSuccess,
    ContinuousChannelPair,
    GearChannelPair,
    SupportingEvidenceKind,
    SupportingEvidenceStatus,
)
from ome.domain import CanonicalConcept
from ome.evidence import (
    CanonicalSeriesEvidence,
    LapEvidenceContext,
    TransformationEvidence,
)

CONTINUOUS_CONCEPTS = (
    CanonicalConcept.VEHICLE_SPEED,
    CanonicalConcept.DRIVER_THROTTLE,
    CanonicalConcept.DRIVER_BRAKE,
    CanonicalConcept.DRIVER_STEERING,
    CanonicalConcept.ENGINE_SPEED,
)

ALL_REPORT_CONCEPTS = (
    *CONTINUOUS_CONCEPTS,
    CanonicalConcept.TRANSMISSION_GEAR,
)

UNITS = {
    CanonicalConcept.TIME_ELAPSED: "s",
    CanonicalConcept.LAP_DISTANCE: "m",
    CanonicalConcept.VEHICLE_SPEED: "m/s",
    CanonicalConcept.DRIVER_THROTTLE: "1",
    CanonicalConcept.DRIVER_BRAKE: "1",
    CanonicalConcept.DRIVER_STEERING: "rad",
    CanonicalConcept.ENGINE_SPEED: "rad/s",
    CanonicalConcept.TRANSMISSION_GEAR: "",
}


def evidence(
    *,
    dataset_fingerprint: str,
    concept: CanonicalConcept,
    source_channel_identifier: str,
    semantic_id: str | None = None,
) -> CanonicalSeriesEvidence:
    return CanonicalSeriesEvidence(
        dataset_fingerprint=dataset_fingerprint,
        source_channel_identifier=source_channel_identifier,
        source_original_name=source_channel_identifier,
        canonical_concept=concept,
        unit=UNITS[concept],
        transformations=(
            TransformationEvidence(
                transformation_id="test.normalization",
                transformation_version="1.0.0",
            ),
        ),
        semantic_id=semantic_id,
    )


def comparison_lap(
    *,
    side: str,
    elapsed_s: tuple[float, ...],
    include_distance: bool = True,
) -> LapComparisonLap:
    fingerprint = f"sha256:{side}"
    context = LapEvidenceContext(
        dataset_fingerprint=fingerprint,
        session_identifier="session-test",
        run_identifier=f"run-{side}",
        lap_identifier=f"lap-{side}",
    )
    distance = (
        LapComparisonSeries(
            values=(0.0, 10.0, 20.0),
            evidence=evidence(
                dataset_fingerprint=fingerprint,
                concept=CanonicalConcept.LAP_DISTANCE,
                source_channel_identifier=f"distance-{side}",
            ),
        )
        if include_distance
        else None
    )
    return LapComparisonLap(
        context=context,
        distance=distance,
        elapsed_time=LapComparisonSeries(
            values=elapsed_s,
            evidence=evidence(
                dataset_fingerprint=fingerprint,
                concept=CanonicalConcept.TIME_ELAPSED,
                source_channel_identifier=f"time-{side}",
            ),
        ),
    )


def continuous_series(
    *,
    side: str,
    concept: CanonicalConcept,
    timestamps_s: tuple[float, ...],
    semantic_id: str | None = None,
) -> ContinuousOverlaySeries:
    base = {
        CanonicalConcept.VEHICLE_SPEED: 20.0,
        CanonicalConcept.DRIVER_THROTTLE: 0.4,
        CanonicalConcept.DRIVER_BRAKE: 0.2,
        CanonicalConcept.DRIVER_STEERING: 0.05,
        CanonicalConcept.ENGINE_SPEED: 400.0,
    }[concept]
    offset = 0.5 if side == "b" else 0.0
    values = tuple(base + offset + index * 0.1 for index in range(len(timestamps_s)))
    fingerprint = f"sha256:{side}"
    return ContinuousOverlaySeries(
        timestamps_s=timestamps_s,
        values=values,
        evidence=evidence(
            dataset_fingerprint=fingerprint,
            concept=concept,
            source_channel_identifier=f"{concept.value}-{side}",
            semantic_id=semantic_id,
        ),
    )


def continuous_pair(
    concept: CanonicalConcept,
    *,
    brake_semantic_a: str = "driver.brake.pedal_position_ratio",
    brake_semantic_b: str = "driver.brake.pedal_position_ratio",
) -> ContinuousChannelPair:
    semantic_a = brake_semantic_a if concept is CanonicalConcept.DRIVER_BRAKE else None
    semantic_b = brake_semantic_b if concept is CanonicalConcept.DRIVER_BRAKE else None
    return ContinuousChannelPair(
        canonical_concept=concept,
        lap_a_channel=continuous_series(
            side="a",
            concept=concept,
            timestamps_s=(0.0, 1.0, 2.0),
            semantic_id=semantic_a,
        ),
        lap_b_channel=continuous_series(
            side="b",
            concept=concept,
            timestamps_s=(0.0, 1.1, 2.2),
            semantic_id=semantic_b,
        ),
    )


def gear_pair() -> GearChannelPair:
    return GearChannelPair(
        lap_a_gear=GearOverlaySeries(
            timestamps_s=(0.0, 1.0, 2.0),
            values=(2, 3, 4),
            evidence=evidence(
                dataset_fingerprint="sha256:a",
                concept=CanonicalConcept.TRANSMISSION_GEAR,
                source_channel_identifier="gear-a",
            ),
        ),
        lap_b_gear=GearOverlaySeries(
            timestamps_s=(0.0, 1.1, 2.2),
            values=(2, 3, 4),
            evidence=evidence(
                dataset_fingerprint="sha256:b",
                concept=CanonicalConcept.TRANSMISSION_GEAR,
                source_channel_identifier="gear-b",
            ),
        ),
    )


def report_request(
    *,
    include_distance_b: bool = True,
    continuous_pairs: tuple[ContinuousChannelPair, ...] | None = None,
    gear: GearChannelPair | None | object = ...,
) -> ComparisonReportRequest:
    if continuous_pairs is None:
        continuous_pairs = tuple(continuous_pair(concept) for concept in CONTINUOUS_CONCEPTS)
    if gear is ...:
        selected_gear: GearChannelPair | None = gear_pair()
    else:
        assert gear is None or isinstance(gear, GearChannelPair)
        selected_gear = gear

    return ComparisonReportRequest(
        comparison=LapComparisonRequest(
            lap_a=comparison_lap(
                side="a",
                elapsed_s=(0.0, 1.0, 2.0),
            ),
            lap_b=comparison_lap(
                side="b",
                elapsed_s=(0.0, 1.1, 2.2),
                include_distance=include_distance_b,
            ),
            grid_step_m=10.0,
        ),
        continuous_channels=continuous_pairs,
        gear=selected_gear,
    )


class Plan014ComparisonReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ComparisonReportService()

    def test_complete_request_produces_integrated_report(self) -> None:
        outcome = self.service.build(report_request())

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)

        self.assertEqual(outcome.comparison.distance_grid_m, (0.0, 10.0, 20.0))
        self.assertEqual(len(outcome.observations.regions), 1)
        self.assertIs(outcome.observations.regions[0].kind, DeltaRegionKind.B_LOSS)
        self.assertEqual(len(outcome.continuous_overlays), 5)
        self.assertIsNotNone(outcome.gear_overlay)
        self.assertEqual(
            tuple(summary.canonical_concept for summary in outcome.supporting_evidence),
            ALL_REPORT_CONCEPTS,
        )
        self.assertTrue(
            all(
                summary.status is SupportingEvidenceStatus.AVAILABLE
                for summary in outcome.supporting_evidence
            )
        )

    def test_supporting_evidence_order_and_kinds_are_stable(self) -> None:
        outcome = self.service.build(report_request())

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)
        self.assertEqual(
            tuple(summary.kind for summary in outcome.supporting_evidence),
            (
                SupportingEvidenceKind.CONTINUOUS,
                SupportingEvidenceKind.CONTINUOUS,
                SupportingEvidenceKind.CONTINUOUS,
                SupportingEvidenceKind.CONTINUOUS,
                SupportingEvidenceKind.CONTINUOUS,
                SupportingEvidenceKind.DISCRETE,
            ),
        )

    def test_missing_optional_speed_is_reported_without_failing_report(self) -> None:
        pairs = tuple(
            continuous_pair(concept)
            for concept in CONTINUOUS_CONCEPTS
            if concept is not CanonicalConcept.VEHICLE_SPEED
        )

        outcome = self.service.build(report_request(continuous_pairs=pairs))

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)
        speed = outcome.supporting_evidence[0]
        self.assertIs(speed.canonical_concept, CanonicalConcept.VEHICLE_SPEED)
        self.assertIs(speed.status, SupportingEvidenceStatus.NOT_READY)
        self.assertIn("missing_channel", speed.issue_codes)
        self.assertNotIn(
            CanonicalConcept.VEHICLE_SPEED,
            {overlay.canonical_concept for overlay in outcome.continuous_overlays},
        )

    def test_missing_optional_gear_is_reported_without_failing_report(self) -> None:
        outcome = self.service.build(report_request(gear=None))

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)
        gear = outcome.supporting_evidence[-1]
        self.assertIs(gear.canonical_concept, CanonicalConcept.TRANSMISSION_GEAR)
        self.assertIs(gear.status, SupportingEvidenceStatus.NOT_READY)
        self.assertIn("missing_gear", gear.issue_codes)
        self.assertIsNone(outcome.gear_overlay)

    def test_incompatible_brake_semantics_are_visible_missing_evidence(self) -> None:
        pairs = tuple(
            continuous_pair(
                concept,
                brake_semantic_a="driver.brake.pedal_position_ratio",
                brake_semantic_b="driver.brake.pedal_force_ratio",
            )
            if concept is CanonicalConcept.DRIVER_BRAKE
            else continuous_pair(concept)
            for concept in CONTINUOUS_CONCEPTS
        )

        outcome = self.service.build(report_request(continuous_pairs=pairs))

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)
        brake = next(
            summary
            for summary in outcome.supporting_evidence
            if summary.canonical_concept is CanonicalConcept.DRIVER_BRAKE
        )
        self.assertIs(brake.status, SupportingEvidenceStatus.NOT_READY)
        self.assertIn("incompatible_brake_semantic_id", brake.issue_codes)

    def test_base_comparison_failure_makes_report_not_ready(self) -> None:
        outcome = self.service.build(report_request(include_distance_b=False))

        self.assertIsInstance(outcome, ComparisonReportNotReady)
        assert isinstance(outcome, ComparisonReportNotReady)
        self.assertIn(
            ComparisonReportIssueCode.BASE_COMPARISON_NOT_READY,
            {issue.code for issue in outcome.issues},
        )
        self.assertIsNotNone(outcome.base_comparison)
        assert outcome.base_comparison is not None
        self.assertIn(
            "missing_distance",
            {issue.code.value for issue in outcome.base_comparison.issues},
        )

    def test_successful_overlays_reuse_exact_base_grid(self) -> None:
        outcome = self.service.build(report_request())

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)
        for overlay in outcome.continuous_overlays:
            self.assertIs(overlay.distance_grid_m, outcome.comparison.distance_grid_m)
        assert outcome.gear_overlay is not None
        self.assertIs(
            outcome.gear_overlay.distance_grid_m,
            outcome.comparison.distance_grid_m,
        )

    def test_duplicate_continuous_concept_fails_explicitly(self) -> None:
        pair = continuous_pair(CanonicalConcept.VEHICLE_SPEED)
        outcome = self.service.build(
            report_request(
                continuous_pairs=(pair, pair),
            )
        )

        self.assertIsInstance(outcome, ComparisonReportNotReady)
        assert isinstance(outcome, ComparisonReportNotReady)
        self.assertIn(
            ComparisonReportIssueCode.DUPLICATE_SUPPORTING_CONCEPT,
            {issue.code for issue in outcome.issues},
        )

    def test_unsupported_continuous_concept_fails_explicitly(self) -> None:
        unsupported = ContinuousChannelPair(
            canonical_concept=CanonicalConcept.LAP_DISTANCE,
            lap_a_channel=None,
            lap_b_channel=None,
        )
        outcome = self.service.build(
            report_request(
                continuous_pairs=(unsupported,),
            )
        )

        self.assertIsInstance(outcome, ComparisonReportNotReady)
        assert isinstance(outcome, ComparisonReportNotReady)
        self.assertIn(
            ComparisonReportIssueCode.UNSUPPORTED_SUPPORTING_CONCEPT,
            {issue.code for issue in outcome.issues},
        )

    def test_report_provenance_retains_every_successful_component(self) -> None:
        outcome = self.service.build(report_request())

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)

        provenance = outcome.provenance
        self.assertEqual(provenance.assembler_id, "ome.lap-comparison.report")
        self.assertEqual(provenance.assembler_version, "0.1.0")
        self.assertEqual(provenance.base_comparison, outcome.comparison.provenance)
        self.assertEqual(
            provenance.delta_observation,
            outcome.observations.provenance,
        )
        self.assertEqual(
            provenance.continuous_overlays,
            tuple(overlay.provenance for overlay in outcome.continuous_overlays),
        )
        assert outcome.gear_overlay is not None
        self.assertEqual(provenance.gear_overlay, outcome.gear_overlay.provenance)
        self.assertEqual(provenance.requested_concepts, ALL_REPORT_CONCEPTS)

    def test_equivalent_requests_produce_equal_reports(self) -> None:
        request = report_request()

        first = self.service.build(request)
        second = self.service.build(request)

        self.assertEqual(first, second)

    def test_report_contains_no_causal_conclusion_fields(self) -> None:
        outcome = self.service.build(report_request())

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)
        for field in (
            "cause",
            "hypothesis",
            "engineering_interpretation",
            "recommendation",
            "driver_score",
        ):
            self.assertFalse(hasattr(outcome, field))


if __name__ == "__main__":
    unittest.main()
