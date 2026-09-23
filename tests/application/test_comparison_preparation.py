from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from ome.application import (
    ComparisonPreparationIssueCode,
    ComparisonPreparationNotReady,
    ComparisonPreparationRequest,
    ComparisonPreparationService,
    ComparisonPreparationSuccess,
    ComparisonReportService,
    ComparisonReportSuccess,
    SupportingEvidenceStatus,
    mvp_ome_csv_comparison_profile,
)
from ome.domain import CanonicalConcept, SampleSeries
from ome.ingestion import ImportSuccess, OMECsvProfileImporter

ROOT = Path(__file__).resolve().parents[2]
LAP_A = ROOT / "fixtures" / "ome" / "mvp-comparison-lap-a.csv"
LAP_B = ROOT / "fixtures" / "ome" / "mvp-comparison-lap-b.csv"
BASIC_LAP = ROOT / "fixtures" / "ome" / "basic-lap.csv"
FIXED_TIME = datetime(2026, 9, 23, 1, 0, tzinfo=UTC)


def import_dataset(path: Path):
    outcome = OMECsvProfileImporter().import_source(path, imported_at=FIXED_TIME)
    assert isinstance(outcome, ImportSuccess)
    return outcome.dataset


def request_for(lap_a, lap_b) -> ComparisonPreparationRequest:
    return ComparisonPreparationRequest(
        lap_a=lap_a,
        lap_b=lap_b,
        profile=mvp_ome_csv_comparison_profile(),
        grid_step_m=25.0,
    )


class Plan016ComparisonPreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lap_a = import_dataset(LAP_A)
        self.lap_b = import_dataset(LAP_B)
        self.service = ComparisonPreparationService()

    def prepare(self) -> ComparisonPreparationSuccess:
        outcome = self.service.prepare(request_for(self.lap_a, self.lap_b))
        self.assertIsInstance(outcome, ComparisonPreparationSuccess)
        assert isinstance(outcome, ComparisonPreparationSuccess)
        return outcome

    def test_controlled_sources_prepare_direct_report_request(self) -> None:
        prepared = self.prepare()

        report = ComparisonReportService().build(prepared.report_request)

        self.assertIsInstance(report, ComparisonReportSuccess)
        assert isinstance(report, ComparisonReportSuccess)
        self.assertEqual(
            report.comparison.distance_grid_m,
            (0.0, 25.0, 50.0, 75.0, 100.0),
        )
        for actual, expected in zip(
            report.comparison.delta_b_vs_a_s,
            (0.0, 0.05, 0.10, 0.15, 0.20),
            strict=True,
        ):
            self.assertAlmostEqual(actual, expected)

    def test_profile_rules_are_explicit_versioned_and_semantic(self) -> None:
        profile = mvp_ome_csv_comparison_profile()

        self.assertEqual(profile.profile_id, "ome.mvp-comparison.ome-csv")
        self.assertEqual(profile.profile_version, "0.1.0")
        self.assertEqual(profile.source_type, "ome-csv-profile")
        self.assertTrue(profile.normalization_rules)
        self.assertTrue(
            all(rule.rule_id and rule.rule_version for rule in profile.normalization_rules)
        )

        brake = next(
            rule
            for rule in profile.normalization_rules
            if rule.canonical_concept is CanonicalConcept.DRIVER_BRAKE
        )
        self.assertEqual(
            brake.semantic_id,
            "driver.brake.pedal_position_ratio",
        )

    def test_time_axis_becomes_traceable_time_elapsed_evidence(self) -> None:
        prepared = self.prepare()
        time_evidence = prepared.report_request.comparison.lap_a.elapsed_time
        assert time_evidence is not None

        evidence = time_evidence.evidence
        self.assertIs(evidence.canonical_concept, CanonicalConcept.TIME_ELAPSED)
        self.assertEqual(evidence.unit, "s")
        self.assertEqual(evidence.source_channel_identifier, "time_s")
        self.assertEqual(evidence.source_original_name, "time_s")
        self.assertEqual(
            evidence.transformations[0].transformation_id,
            "ome.preparation.ome-csv-time-axis",
        )
        self.assertEqual(
            evidence.transformations[0].parameters["preparation_profile_id"],
            "ome.mvp-comparison.ome-csv",
        )

    def test_context_and_normalization_provenance_reach_report_request(self) -> None:
        prepared = self.prepare()
        comparison = prepared.report_request.comparison

        self.assertTrue(comparison.lap_a.context.session_identifier.startswith("session:"))
        self.assertTrue(comparison.lap_a.context.run_identifier.startswith("run:"))
        self.assertTrue(comparison.lap_a.context.lap_identifier.startswith("lap:"))
        self.assertTrue(comparison.lap_b.context.session_identifier.startswith("session:"))
        self.assertTrue(comparison.lap_b.context.run_identifier.startswith("run:"))
        self.assertTrue(comparison.lap_b.context.lap_identifier.startswith("lap:"))

        distance = comparison.lap_a.distance
        assert distance is not None
        self.assertEqual(distance.evidence.source_channel_identifier, "lap_distance_src")
        self.assertEqual(distance.evidence.source_original_name, "Synthetic Lap Distance")
        self.assertIs(distance.evidence.canonical_concept, CanonicalConcept.LAP_DISTANCE)
        self.assertEqual(distance.evidence.unit, "m")
        self.assertEqual(
            distance.evidence.transformations[0].parameters["normalization_rule_id"],
            "ome.mvp-comparison.lap-distance",
        )

    def test_brake_semantic_identity_survives_preparation(self) -> None:
        prepared = self.prepare()
        brake = next(
            pair
            for pair in prepared.report_request.continuous_channels
            if pair.canonical_concept is CanonicalConcept.DRIVER_BRAKE
        )
        assert brake.lap_a_channel is not None
        assert brake.lap_b_channel is not None

        self.assertEqual(
            brake.lap_a_channel.evidence.semantic_id,
            "driver.brake.pedal_position_ratio",
        )
        self.assertEqual(
            brake.lap_b_channel.evidence.semantic_id,
            "driver.brake.pedal_position_ratio",
        )

    def test_missing_lap_distance_returns_not_ready_without_synthesis(self) -> None:
        missing_distance = import_dataset(BASIC_LAP)

        outcome = self.service.prepare(request_for(self.lap_a, missing_distance))

        self.assertIsInstance(outcome, ComparisonPreparationNotReady)
        assert isinstance(outcome, ComparisonPreparationNotReady)
        self.assertIn(
            ComparisonPreparationIssueCode.MISSING_LAP_DISTANCE,
            {issue.code for issue in outcome.issues},
        )
        self.assertFalse(hasattr(outcome, "report_request"))

    def test_blocking_validation_prevents_preparation(self) -> None:
        distance = self.lap_b.channel("lap_distance_src")
        broken_distance = replace(
            distance,
            series=SampleSeries(
                timestamps_s=(0.0, 0.55, 0.55, 1.65, 2.2),
                values=distance.series.values,
            ),
        )
        broken = replace(
            self.lap_b,
            channels=tuple(
                broken_distance if channel.identifier == "lap_distance_src" else channel
                for channel in self.lap_b.channels
            ),
        )

        outcome = self.service.prepare(request_for(self.lap_a, broken))

        self.assertIsInstance(outcome, ComparisonPreparationNotReady)
        assert isinstance(outcome, ComparisonPreparationNotReady)
        self.assertIn(
            ComparisonPreparationIssueCode.BLOCKING_VALIDATION,
            {issue.code for issue in outcome.issues},
        )

    def test_missing_optional_speed_remains_explicit_in_report(self) -> None:
        without_speed = replace(
            self.lap_b,
            channels=tuple(
                channel for channel in self.lap_b.channels if channel.identifier != "speed_src"
            ),
        )

        outcome = self.service.prepare(request_for(self.lap_a, without_speed))

        self.assertIsInstance(outcome, ComparisonPreparationSuccess)
        assert isinstance(outcome, ComparisonPreparationSuccess)
        report = ComparisonReportService().build(outcome.report_request)
        self.assertIsInstance(report, ComparisonReportSuccess)
        assert isinstance(report, ComparisonReportSuccess)

        speed = next(
            summary
            for summary in report.supporting_evidence
            if summary.canonical_concept is CanonicalConcept.VEHICLE_SPEED
        )
        self.assertIs(speed.status, SupportingEvidenceStatus.NOT_READY)
        self.assertIn("missing_channel", speed.issue_codes)

    def test_preparation_does_not_mutate_imported_datasets(self) -> None:
        a_channels_before = self.lap_a.channels
        b_channels_before = self.lap_b.channels
        a_metadata_before = self.lap_a.source.metadata
        b_metadata_before = self.lap_b.source.metadata

        self.prepare()

        self.assertIs(self.lap_a.channels, a_channels_before)
        self.assertIs(self.lap_b.channels, b_channels_before)
        self.assertIs(self.lap_a.source.metadata, a_metadata_before)
        self.assertIs(self.lap_b.source.metadata, b_metadata_before)


if __name__ == "__main__":
    unittest.main()
