from __future__ import annotations

import math
import unittest
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from ome.application import (
    ComparisonReportService,
    ComparisonReportSuccess,
    PhysicalComparisonPreparationRequest,
    PhysicalComparisonPreparationService,
    PhysicalComparisonPreparationSuccess,
    PhysicalTrackReferencePreparationRequest,
    PhysicalTrackReferencePreparationService,
    PhysicalTrackReferencePreparationSuccess,
    SourceLapWindowRequest,
    SupportingEvidenceStatus,
    TraqmateLapWindowSelector,
    TraqmatePhysicalSupportingEvidenceIssueCode,
    TraqmatePhysicalSupportingEvidenceNotReady,
    TraqmatePhysicalSupportingEvidenceRequest,
    TraqmatePhysicalSupportingEvidenceService,
    TraqmatePhysicalSupportingEvidenceSuccess,
    traqmate_physical_normalization_rules,
)
from ome.domain import CanonicalConcept, ImportedTelemetryDataset
from ome.evidence import LapEvidenceContext
from ome.ingestion import ImportSuccess, TraqmateTrackvisionCSVImporter
from ome.normalization import ConversionKind, TelemetryNormalizer
from ome.validation import TelemetryValidator

ROOT = Path(__file__).resolve().parents[2]
PORTLAND_FIXTURE = ROOT / "fixtures" / "public" / "exit-speed" / "traqmate-portland-laps-4-5.csv"
FIXED_TIME = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)

GEAR_SEMANTIC_ID = "transmission.gear.traqmate_derived_or_assigned"
BOUNDARY_ROLE = "shared_start_finish_evidence"
SUPPORTING_TRANSFORMATION_ID = "ome.preparation.traqmate-supporting-lap-window"


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


def base_preparation(physical):
    outcome = PhysicalComparisonPreparationService().prepare(
        PhysicalComparisonPreparationRequest(
            preparation=physical,
            grid_step_m=5.0,
        )
    )
    assert isinstance(outcome, PhysicalComparisonPreparationSuccess)
    return outcome


class Plan029TraqmateNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = import_portland()
        cls.validation = TelemetryValidator().validate(cls.dataset)

    def normalize(self):
        return TelemetryNormalizer(traqmate_physical_normalization_rules()).normalize(
            self.dataset,
            self.validation,
        )

    def test_mph_to_mps_conversion_is_explicit_and_deterministic(self) -> None:
        self.assertIs(ConversionKind.MPH_TO_MPS, ConversionKind.MPH_TO_MPS)

        first = self.normalize()
        second = self.normalize()
        speed = first.mapping_for_source("Velocity (MPH)")
        source = self.dataset.channel("Velocity (MPH)")

        self.assertEqual(first, second)
        self.assertIs(speed.canonical_concept, CanonicalConcept.VEHICLE_SPEED)
        self.assertEqual(speed.source_unit, "mph")
        self.assertEqual(speed.target_unit, "m/s")
        self.assertEqual(speed.rule_id, "ome.traqmate.vehicle-speed")
        self.assertEqual(speed.conversion_id, "ome.conversion.mph_to_mps")
        self.assertAlmostEqual(speed.series.values[0], 90.799839 * 0.44704)
        self.assertEqual(source.series.values[0], "90.799839")

    def test_exact_traqmate_rules_promote_only_speed_rpm_and_gear(self) -> None:
        rules = traqmate_physical_normalization_rules()

        self.assertEqual(
            tuple(rule.source_channel_identifier for rule in rules),
            ("Velocity (MPH)", "RPMs", "Gear"),
        )
        self.assertTrue(
            all(rule.source_type == "traqmate-trackvision-csv" for rule in rules)
        )

        normalization = self.normalize()
        mapped = {mapping.canonical_concept for mapping in normalization.mappings}

        self.assertIn(CanonicalConcept.VEHICLE_SPEED, mapped)
        self.assertIn(CanonicalConcept.ENGINE_SPEED, mapped)
        self.assertIn(CanonicalConcept.TRANSMISSION_GEAR, mapped)
        self.assertNotIn(CanonicalConcept.DRIVER_THROTTLE, mapped)
        self.assertNotIn(CanonicalConcept.DRIVER_BRAKE, mapped)
        self.assertNotIn(CanonicalConcept.DRIVER_STEERING, mapped)

        self.assertEqual(
            normalization.unmapped_for(["Accel (calc)"])[0].source_channel_identifier,
            "Accel (calc)",
        )
        self.assertEqual(
            normalization.unmapped_for(["Brake (calc)"])[0].source_channel_identifier,
            "Brake (calc)",
        )

    def test_rpm_and_gear_semantics_are_explicit(self) -> None:
        normalization = self.normalize()
        rpm = normalization.mapping_for_source("RPMs")
        gear = normalization.mapping_for_source("Gear")

        self.assertIs(rpm.canonical_concept, CanonicalConcept.ENGINE_SPEED)
        self.assertIsNone(rpm.source_unit)
        self.assertEqual(rpm.target_unit, "rad/s")
        self.assertEqual(rpm.rule_id, "ome.traqmate.engine-speed")
        self.assertAlmostEqual(rpm.series.values[0], 5256.0 * 2.0 * math.pi / 60.0)

        self.assertIs(gear.canonical_concept, CanonicalConcept.TRANSMISSION_GEAR)
        self.assertIsNone(gear.source_unit)
        self.assertIsNone(gear.target_unit)
        self.assertEqual(gear.rule_id, "ome.traqmate.gear")
        self.assertEqual(gear.semantic_id, GEAR_SEMANTIC_ID)
        self.assertEqual(gear.series.values[0], 4)


class Plan029TraqmateSupportingEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = import_portland()
        cls.physical = physical_preparation(cls.dataset)
        cls.base = base_preparation(cls.physical)

    def setUp(self) -> None:
        self.service = TraqmatePhysicalSupportingEvidenceService()

    def request(
        self,
        *,
        dataset: ImportedTelemetryDataset | None = None,
        physical=None,
        base=None,
    ) -> TraqmatePhysicalSupportingEvidenceRequest:
        return TraqmatePhysicalSupportingEvidenceRequest(
            dataset=self.dataset if dataset is None else dataset,
            physical_preparation=self.physical if physical is None else physical,
            base_preparation=self.base if base is None else base,
        )

    def prepare(self) -> TraqmatePhysicalSupportingEvidenceSuccess:
        outcome = self.service.prepare(self.request())
        self.assertIsInstance(outcome, TraqmatePhysicalSupportingEvidenceSuccess)
        assert isinstance(outcome, TraqmatePhysicalSupportingEvidenceSuccess)
        return outcome

    def test_prepared_supporting_series_use_owned_samples_plus_one_shared_boundary(self) -> None:
        outcome = self.prepare()
        request = outcome.report_request
        pairs = {pair.canonical_concept: pair for pair in request.continuous_channels}

        speed = pairs[CanonicalConcept.VEHICLE_SPEED]
        rpm = pairs[CanonicalConcept.ENGINE_SPEED]
        gear = request.gear

        assert speed.lap_a_channel is not None
        assert speed.lap_b_channel is not None
        assert rpm.lap_a_channel is not None
        assert rpm.lap_b_channel is not None
        assert gear is not None
        assert gear.lap_a_gear is not None
        assert gear.lap_b_gear is not None

        self.assertEqual(
            len(speed.lap_a_channel.values),
            self.physical.reference_window.sample_count + 1,
        )
        self.assertEqual(
            len(speed.lap_b_channel.values),
            self.physical.candidate_window.sample_count + 1,
        )
        self.assertEqual(len(rpm.lap_a_channel.values), len(speed.lap_a_channel.values))
        self.assertEqual(len(rpm.lap_b_channel.values), len(speed.lap_b_channel.values))
        self.assertEqual(len(gear.lap_a_gear.values), len(speed.lap_a_channel.values))
        self.assertEqual(len(gear.lap_b_gear.values), len(speed.lap_b_channel.values))

        self.assertEqual(speed.lap_a_channel.timestamps_s[0], 0.0)
        self.assertEqual(speed.lap_b_channel.timestamps_s[0], 0.0)
        self.assertAlmostEqual(speed.lap_a_channel.timestamps_s[-1], 90.45)
        self.assertAlmostEqual(speed.lap_b_channel.timestamps_s[-1], 90.775)

        self.assertAlmostEqual(speed.lap_a_channel.values[0], 90.799839 * 0.44704)
        self.assertAlmostEqual(speed.lap_a_channel.values[-1], 89.955229 * 0.44704)
        self.assertAlmostEqual(speed.lap_b_channel.values[0], 89.955229 * 0.44704)
        self.assertAlmostEqual(speed.lap_b_channel.values[-1], 90.257766 * 0.44704)
        self.assertEqual(gear.lap_a_gear.values[0], 4)
        self.assertEqual(gear.lap_a_gear.values[-1], 4)
        self.assertEqual(gear.lap_b_gear.values[0], 4)
        self.assertEqual(gear.lap_b_gear.values[-1], 4)

    def test_boundary_provenance_is_explicit_without_changing_source_ownership(self) -> None:
        outcome = self.prepare()
        pairs = {pair.canonical_concept: pair for pair in outcome.report_request.continuous_channels}
        speed = pairs[CanonicalConcept.VEHICLE_SPEED]
        assert speed.lap_a_channel is not None
        assert speed.lap_b_channel is not None

        cases = (
            (
                speed.lap_a_channel,
                self.physical.reference_window,
            ),
            (
                speed.lap_b_channel,
                self.physical.candidate_window,
            ),
        )
        for series, window in cases:
            transformation = series.evidence.transformations[-1]
            self.assertEqual(
                transformation.transformation_id,
                SUPPORTING_TRANSFORMATION_ID,
            )
            self.assertEqual(transformation.transformation_version, "0.1.0")
            self.assertEqual(
                transformation.parameters["source_window_start_index"],
                window.start_index,
            )
            self.assertEqual(
                transformation.parameters["source_window_end_index_exclusive"],
                window.end_index_exclusive,
            )
            self.assertEqual(
                transformation.parameters["closing_boundary_source_index"],
                window.closing_boundary_index,
            )
            self.assertEqual(
                transformation.parameters["closing_boundary_role"],
                BOUNDARY_ROLE,
            )
            self.assertEqual(
                transformation.parameters["source_start_s"],
                window.start_elapsed_s,
            )

        self.assertEqual(self.physical.reference_window.end_index_exclusive, 3618)
        self.assertEqual(self.physical.reference_window.closing_boundary_index, 3618)
        self.assertEqual(self.physical.candidate_window.end_index_exclusive, 7249)
        self.assertEqual(self.physical.candidate_window.closing_boundary_index, 7249)

    def test_enrichment_is_deterministic_and_does_not_mutate_existing_artifacts(self) -> None:
        dataset_before = self.dataset
        physical_before = self.physical
        base_request_before = self.base.report_request

        first = self.service.prepare(self.request())
        second = self.service.prepare(self.request())

        self.assertEqual(first, second)
        self.assertIs(self.dataset, dataset_before)
        self.assertIs(self.physical, physical_before)
        self.assertIs(self.base.report_request, base_request_before)
        assert isinstance(first, TraqmatePhysicalSupportingEvidenceSuccess)
        self.assertIs(first.report_request.comparison, base_request_before.comparison)
        self.assertEqual(base_request_before.continuous_channels, ())
        self.assertIsNone(base_request_before.gear)

    def test_fingerprint_context_and_window_mismatches_are_not_ready(self) -> None:
        invalid_fingerprint = replace(
            self.physical,
            dataset_fingerprint="sha256:other",
        )
        invalid_context = replace(
            self.base,
            report_request=replace(
                self.base.report_request,
                comparison=replace(
                    self.base.report_request.comparison,
                    lap_b=replace(
                        self.base.report_request.comparison.lap_b,
                        context=replace(
                            self.base.report_request.comparison.lap_b.context,
                            lap_identifier="source-lap:other",
                        ),
                    ),
                ),
            ),
        )
        invalid_window = replace(
            self.physical,
            reference_window=replace(
                self.physical.reference_window,
                closing_boundary_index=len(self.dataset.channel("Elapsed Time").series.values) + 1,
            ),
        )

        cases = (
            (
                self.request(physical=invalid_fingerprint),
                TraqmatePhysicalSupportingEvidenceIssueCode.DATASET_FINGERPRINT_MISMATCH,
            ),
            (
                self.request(base=invalid_context),
                TraqmatePhysicalSupportingEvidenceIssueCode.BASE_CONTEXT_MISMATCH,
            ),
            (
                self.request(physical=invalid_window),
                TraqmatePhysicalSupportingEvidenceIssueCode.WINDOW_OUT_OF_RANGE,
            ),
        )

        for request, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                outcome = self.service.prepare(request)
                self.assertIsInstance(outcome, TraqmatePhysicalSupportingEvidenceNotReady)
                assert isinstance(outcome, TraqmatePhysicalSupportingEvidenceNotReady)
                self.assertIn(expected_code, {issue.code for issue in outcome.issues})

    def test_portland_report_exposes_only_verified_supporting_evidence(self) -> None:
        preparation = self.prepare()

        outcome = ComparisonReportService().build(preparation.report_request)

        self.assertIsInstance(outcome, ComparisonReportSuccess)
        assert isinstance(outcome, ComparisonReportSuccess)

        available = {
            item.canonical_concept
            for item in outcome.supporting_evidence
            if item.status is SupportingEvidenceStatus.AVAILABLE
        }
        not_ready = {
            item.canonical_concept
            for item in outcome.supporting_evidence
            if item.status is SupportingEvidenceStatus.NOT_READY
        }

        self.assertEqual(
            available,
            {
                CanonicalConcept.VEHICLE_SPEED,
                CanonicalConcept.ENGINE_SPEED,
                CanonicalConcept.TRANSMISSION_GEAR,
            },
        )
        self.assertEqual(
            not_ready,
            {
                CanonicalConcept.DRIVER_THROTTLE,
                CanonicalConcept.DRIVER_BRAKE,
                CanonicalConcept.DRIVER_STEERING,
            },
        )
        self.assertEqual(len(outcome.continuous_overlays), 2)
        self.assertIsNotNone(outcome.gear_overlay)

        gear_pair = preparation.report_request.gear
        assert gear_pair is not None
        assert gear_pair.lap_a_gear is not None
        self.assertEqual(gear_pair.lap_a_gear.evidence.semantic_id, GEAR_SEMANTIC_ID)

        for field in (
            "cause",
            "hypothesis",
            "engineering_interpretation",
            "recommendation",
        ):
            self.assertFalse(hasattr(outcome, field))


if __name__ == "__main__":
    unittest.main()
