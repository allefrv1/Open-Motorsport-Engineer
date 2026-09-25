from __future__ import annotations

import math
import unittest
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from ome.application import (
    ComparisonReportService,
    ComparisonReportSuccess,
    PhysicalComparisonPreparationIssueCode,
    PhysicalComparisonPreparationNotReady,
    PhysicalComparisonPreparationRequest,
    PhysicalComparisonPreparationService,
    PhysicalComparisonPreparationSuccess,
    PhysicalTrackReferencePreparationRequest,
    PhysicalTrackReferencePreparationService,
    PhysicalTrackReferencePreparationSuccess,
    SourceLapWindowRequest,
    SupportingEvidenceStatus,
    TraqmateLapWindowSelector,
)
from ome.domain import CanonicalConcept, ImportedTelemetryDataset
from ome.evidence import LapEvidenceContext
from ome.ingestion import ImportSuccess, TraqmateTrackvisionCSVImporter

ROOT = Path(__file__).resolve().parents[2]
PORTLAND_FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-portland-laps-4-5.csv"
FIXED_TIME = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)

REPORT_CONCEPTS = (
    CanonicalConcept.VEHICLE_SPEED,
    CanonicalConcept.DRIVER_THROTTLE,
    CanonicalConcept.DRIVER_BRAKE,
    CanonicalConcept.DRIVER_STEERING,
    CanonicalConcept.ENGINE_SPEED,
    CanonicalConcept.TRANSMISSION_GEAR,
)


def import_portland() -> ImportedTelemetryDataset:
    outcome = TraqmateTrackvisionCSVImporter().import_source(
        PORTLAND_FIXTURE,
        imported_at=FIXED_TIME,
    )
    assert isinstance(outcome, ImportSuccess)
    return outcome.dataset


def context(dataset: ImportedTelemetryDataset, lap_number: int) -> LapEvidenceContext:
    return LapEvidenceContext(
        dataset_fingerprint=dataset.provenance.content_fingerprint,
        session_identifier="session:portland",
        run_identifier="run:portland",
        lap_identifier=f"source-lap:{lap_number}",
    )


def physical_preparation(dataset: ImportedTelemetryDataset):
    selector = TraqmateLapWindowSelector()
    reference = selector.select(SourceLapWindowRequest(dataset=dataset, source_lap_number=4))
    candidate = selector.select(SourceLapWindowRequest(dataset=dataset, source_lap_number=5))
    assert hasattr(reference, "window")
    assert hasattr(candidate, "window")

    outcome = PhysicalTrackReferencePreparationService().prepare(
        PhysicalTrackReferencePreparationRequest(
            dataset=dataset,
            reference_window=reference.window,
            candidate_window=candidate.window,
            reference_context=context(dataset, 4),
            candidate_context=context(dataset, 5),
        )
    )
    assert isinstance(outcome, PhysicalTrackReferencePreparationSuccess)
    return outcome.preparation


class Plan028PhysicalComparisonPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = import_portland()
        cls.physical = physical_preparation(cls.dataset)

    def setUp(self) -> None:
        self.service = PhysicalComparisonPreparationService()

    def request(
        self,
        *,
        grid_step_m: float = 5.0,
    ) -> PhysicalComparisonPreparationRequest:
        return PhysicalComparisonPreparationRequest(
            preparation=self.physical,
            grid_step_m=grid_step_m,
        )

    def test_portland_prepares_ready_comparison_report_request(self) -> None:
        outcome = self.service.prepare(self.request())

        self.assertIsInstance(outcome, PhysicalComparisonPreparationSuccess)
        assert isinstance(outcome, PhysicalComparisonPreparationSuccess)

        report_request = outcome.report_request
        comparison = report_request.comparison

        self.assertIs(comparison.lap_a.context, self.physical.reference_context)
        self.assertIs(comparison.lap_b.context, self.physical.candidate_context)
        self.assertIs(
            comparison.lap_a.distance,
            self.physical.reference_lap_distance,
        )
        self.assertIs(
            comparison.lap_b.distance,
            self.physical.candidate_lap_distance,
        )
        self.assertEqual(comparison.grid_step_m, 5.0)
        self.assertEqual(report_request.continuous_channels, ())
        self.assertIsNone(report_request.gear)

        self.assertEqual(outcome.dataset_fingerprint, self.physical.dataset_fingerprint)
        self.assertEqual(
            outcome.preparation_id,
            "ome.preparation.physical-comparison-request",
        )
        self.assertEqual(outcome.preparation_version, "0.1.0")

    def test_lap_relative_elapsed_time_starts_at_zero_and_matches_distance_lengths(
        self,
    ) -> None:
        outcome = self.service.prepare(self.request())

        self.assertIsInstance(outcome, PhysicalComparisonPreparationSuccess)
        assert isinstance(outcome, PhysicalComparisonPreparationSuccess)

        comparison = outcome.report_request.comparison
        lap_a_time = comparison.lap_a.elapsed_time
        lap_b_time = comparison.lap_b.elapsed_time
        assert lap_a_time is not None
        assert lap_b_time is not None

        self.assertEqual(lap_a_time.values[0], 0.0)
        self.assertEqual(lap_b_time.values[0], 0.0)
        self.assertEqual(
            len(lap_a_time.values),
            len(self.physical.reference_lap_distance.values),
        )
        self.assertEqual(
            len(lap_b_time.values),
            len(self.physical.candidate_lap_distance.values),
        )
        self.assertAlmostEqual(
            lap_a_time.values[-1],
            self.physical.reference_lap.timestamps_s[-1]
            - self.physical.reference_lap.timestamps_s[0],
        )
        self.assertAlmostEqual(
            lap_b_time.values[-1],
            self.physical.candidate_lap.timestamps_s[-1]
            - self.physical.candidate_lap.timestamps_s[0],
        )

    def test_elapsed_time_provenance_is_explicit_and_source_traceable(self) -> None:
        outcome = self.service.prepare(self.request())

        self.assertIsInstance(outcome, PhysicalComparisonPreparationSuccess)
        assert isinstance(outcome, PhysicalComparisonPreparationSuccess)

        comparison = outcome.report_request.comparison
        for lap, physical_lap in (
            (comparison.lap_a, self.physical.reference_lap),
            (comparison.lap_b, self.physical.candidate_lap),
        ):
            elapsed = lap.elapsed_time
            assert elapsed is not None

            evidence = elapsed.evidence
            self.assertIs(evidence.canonical_concept, CanonicalConcept.TIME_ELAPSED)
            self.assertEqual(evidence.unit, "s")
            self.assertEqual(
                evidence.dataset_fingerprint,
                self.physical.dataset_fingerprint,
            )
            self.assertEqual(
                evidence.source_channel_identifier,
                physical_lap.time_evidence.source_channel_identifier,
            )
            self.assertEqual(
                evidence.source_original_name,
                physical_lap.time_evidence.source_original_name,
            )
            self.assertEqual(len(evidence.transformations), 1)
            transformation = evidence.transformations[0]
            self.assertEqual(
                transformation.transformation_id,
                "ome.preparation.lap-relative-elapsed-time",
            )
            self.assertEqual(transformation.transformation_version, "0.1.0")
            self.assertEqual(
                transformation.parameters["source_start_s"],
                physical_lap.timestamps_s[0],
            )

    def test_preparation_is_deterministic_and_does_not_mutate_input(self) -> None:
        before = self.physical

        first = self.service.prepare(self.request())
        second = self.service.prepare(self.request())

        self.assertEqual(first, second)
        self.assertIs(self.physical, before)
        self.assertIs(
            self.physical.reference_lap_distance,
            before.reference_lap_distance,
        )
        self.assertIs(
            self.physical.candidate_lap_distance,
            before.candidate_lap_distance,
        )

    def test_invalid_grid_step_is_not_ready(self) -> None:
        for grid_step_m in (0.0, -1.0, math.nan, math.inf):
            with self.subTest(grid_step_m=grid_step_m):
                outcome = self.service.prepare(self.request(grid_step_m=grid_step_m))

                self.assertIsInstance(outcome, PhysicalComparisonPreparationNotReady)
                assert isinstance(outcome, PhysicalComparisonPreparationNotReady)
                self.assertIn(
                    PhysicalComparisonPreparationIssueCode.INVALID_GRID_STEP,
                    {issue.code for issue in outcome.issues},
                )

    def test_context_or_dataset_fingerprint_mismatch_is_not_ready(self) -> None:
        invalid_dataset = replace(
            self.physical,
            dataset_fingerprint="sha256:other",
        )
        invalid_context = replace(
            self.physical,
            candidate_context=replace(
                self.physical.candidate_context,
                dataset_fingerprint="sha256:other",
            ),
        )

        cases = (
            (
                invalid_dataset,
                PhysicalComparisonPreparationIssueCode.DATASET_FINGERPRINT_MISMATCH,
            ),
            (
                invalid_context,
                PhysicalComparisonPreparationIssueCode.CONTEXT_DATASET_MISMATCH,
            ),
        )

        for preparation, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                outcome = self.service.prepare(
                    PhysicalComparisonPreparationRequest(
                        preparation=preparation,
                        grid_step_m=5.0,
                    )
                )
                self.assertIsInstance(outcome, PhysicalComparisonPreparationNotReady)
                assert isinstance(outcome, PhysicalComparisonPreparationNotReady)
                self.assertIn(expected_code, {issue.code for issue in outcome.issues})

    def test_same_reference_candidate_context_is_not_ready(self) -> None:
        invalid = replace(
            self.physical,
            candidate_context=self.physical.reference_context,
        )

        outcome = self.service.prepare(
            PhysicalComparisonPreparationRequest(
                preparation=invalid,
                grid_step_m=5.0,
            )
        )

        self.assertIsInstance(outcome, PhysicalComparisonPreparationNotReady)
        assert isinstance(outcome, PhysicalComparisonPreparationNotReady)
        self.assertIn(
            PhysicalComparisonPreparationIssueCode.SAME_LAP_CONTEXT,
            {issue.code for issue in outcome.issues},
        )

    def test_non_increasing_physical_timestamp_is_not_ready(self) -> None:
        timestamps = list(self.physical.candidate_lap.timestamps_s)
        timestamps[2] = timestamps[1]
        invalid_candidate_lap = replace(
            self.physical.candidate_lap,
            timestamps_s=tuple(timestamps),
        )
        invalid = replace(
            self.physical,
            candidate_lap=invalid_candidate_lap,
        )

        outcome = self.service.prepare(
            PhysicalComparisonPreparationRequest(
                preparation=invalid,
                grid_step_m=5.0,
            )
        )

        self.assertIsInstance(outcome, PhysicalComparisonPreparationNotReady)
        assert isinstance(outcome, PhysicalComparisonPreparationNotReady)
        self.assertIn(
            PhysicalComparisonPreparationIssueCode.INVALID_TIME_EVIDENCE,
            {issue.code for issue in outcome.issues},
        )

    def test_distance_time_length_mismatch_is_not_ready(self) -> None:
        invalid_distance = replace(
            self.physical.candidate_lap_distance,
            values=self.physical.candidate_lap_distance.values[:-1],
        )
        invalid = replace(
            self.physical,
            candidate_lap_distance=invalid_distance,
        )

        outcome = self.service.prepare(
            PhysicalComparisonPreparationRequest(
                preparation=invalid,
                grid_step_m=5.0,
            )
        )

        self.assertIsInstance(outcome, PhysicalComparisonPreparationNotReady)
        assert isinstance(outcome, PhysicalComparisonPreparationNotReady)
        self.assertIn(
            PhysicalComparisonPreparationIssueCode.LENGTH_MISMATCH,
            {issue.code for issue in outcome.issues},
        )

    def test_portland_request_builds_real_report_with_missing_supporting_evidence(
        self,
    ) -> None:
        preparation = self.service.prepare(self.request())

        self.assertIsInstance(preparation, PhysicalComparisonPreparationSuccess)
        assert isinstance(preparation, PhysicalComparisonPreparationSuccess)

        outcome = ComparisonReportService().build(preparation.report_request)

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)

        self.assertEqual(outcome.comparison.provenance.algorithm_version, "0.2.0")
        self.assertEqual(
            outcome.comparison.provenance.lap_a.context.lap_identifier,
            "source-lap:4",
        )
        self.assertEqual(
            outcome.comparison.provenance.lap_b.context.lap_identifier,
            "source-lap:5",
        )
        self.assertGreater(len(outcome.observations.regions), 0)
        self.assertEqual(outcome.continuous_overlays, ())
        self.assertIsNone(outcome.gear_overlay)
        self.assertEqual(
            tuple(item.canonical_concept for item in outcome.supporting_evidence),
            REPORT_CONCEPTS,
        )
        self.assertTrue(
            all(
                item.status is SupportingEvidenceStatus.NOT_READY
                for item in outcome.supporting_evidence
            )
        )
        for field in (
            "cause",
            "hypothesis",
            "engineering_interpretation",
            "recommendation",
        ):
            self.assertFalse(hasattr(outcome, field))


if __name__ == "__main__":
    unittest.main()
