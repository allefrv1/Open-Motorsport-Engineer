from __future__ import annotations

import math
import unittest
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from ome.domain import (
    CanonicalConcept,
    ChannelMetadata,
    ConversionKind,
    NormalizationRule,
    SampleSeries,
    SourceChannel,
    UnmappedReason,
)
from ome.ingestion import ImportSuccess, OMECsvProfileImporter
from ome.normalization import TelemetryNormalizer
from ome.validation import TelemetryValidator

ROOT = Path(__file__).resolve().parents[2]
OME_FIXTURE = ROOT / "fixtures" / "ome" / "basic-lap.csv"
FIXED_TIME = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)


def rule(
    *,
    rule_id: str,
    channel_identifier: str,
    original_name: str,
    source_unit: str | None,
    concept: CanonicalConcept,
    source_semantics: str,
    target_unit: str | None,
    conversion: ConversionKind,
) -> NormalizationRule:
    return NormalizationRule(
        rule_id=rule_id,
        rule_version="0.1.0",
        source_type="ome-csv-profile",
        source_channel_identifier=channel_identifier,
        expected_original_name=original_name,
        expected_unit=source_unit,
        canonical_concept=concept,
        source_semantics=source_semantics,
        target_unit=target_unit,
        conversion_kind=conversion,
        conversion_id=f"ome.conversion.{conversion.value}",
        conversion_version="1.0.0",
    )


def fixture_rules() -> tuple[NormalizationRule, ...]:
    return (
        rule(
            rule_id="ome.fixture.vehicle-speed",
            channel_identifier="speed_src",
            original_name="Synthetic Vehicle Speed",
            source_unit="m/s",
            concept=CanonicalConcept.VEHICLE_SPEED,
            source_semantics="Synthetic vehicle speed supplied directly in metres per second.",
            target_unit="m/s",
            conversion=ConversionKind.NUMERIC_IDENTITY,
        ),
        rule(
            rule_id="ome.fixture.throttle",
            channel_identifier="throttle_src",
            original_name="Synthetic Throttle Position",
            source_unit="%",
            concept=CanonicalConcept.DRIVER_THROTTLE,
            source_semantics="Synthetic driver throttle position expressed as percent.",
            target_unit="1",
            conversion=ConversionKind.PERCENT_TO_FRACTION,
        ),
        rule(
            rule_id="ome.fixture.brake",
            channel_identifier="brake_src",
            original_name="Synthetic Brake Input",
            source_unit="%",
            concept=CanonicalConcept.DRIVER_BRAKE,
            source_semantics="Synthetic driver brake input expressed as percent.",
            target_unit="1",
            conversion=ConversionKind.PERCENT_TO_FRACTION,
        ),
        rule(
            rule_id="ome.fixture.steering",
            channel_identifier="steering_src",
            original_name="Synthetic Steering Angle",
            source_unit="rad",
            concept=CanonicalConcept.DRIVER_STEERING,
            source_semantics="Synthetic signed steering-wheel angle in radians.",
            target_unit="rad",
            conversion=ConversionKind.NUMERIC_IDENTITY,
        ),
        rule(
            rule_id="ome.fixture.engine-speed",
            channel_identifier="rpm_src",
            original_name="Synthetic Engine Speed",
            source_unit="rpm",
            concept=CanonicalConcept.ENGINE_SPEED,
            source_semantics="Synthetic engine rotational speed in revolutions per minute.",
            target_unit="rad/s",
            conversion=ConversionKind.RPM_TO_RAD_PER_SECOND,
        ),
        rule(
            rule_id="ome.fixture.gear",
            channel_identifier="gear_src",
            original_name="Synthetic Gear",
            source_unit="",
            concept=CanonicalConcept.TRANSMISSION_GEAR,
            source_semantics="Synthetic engaged forward gear number.",
            target_unit=None,
            conversion=ConversionKind.INTEGER_IDENTITY,
        ),
    )


def import_fixture():
    outcome = OMECsvProfileImporter().import_source(OME_FIXTURE, imported_at=FIXED_TIME)
    assert isinstance(outcome, ImportSuccess)
    return outcome.dataset


class Req004TelemetryNormalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = import_fixture()
        self.validation = TelemetryValidator().validate(self.dataset)
        self.normalizer = TelemetryNormalizer(fixture_rules())

    def test_ac001_source_identity_and_values_are_preserved(self) -> None:
        throttle = self.dataset.channel("throttle_src")
        source_values_before = throttle.series.values
        source_metadata_before = throttle.metadata

        result = self.normalizer.normalize(self.dataset, self.validation)
        mapping = result.mapping_for_source("throttle_src")

        self.assertEqual(mapping.source_channel_identifier, "throttle_src")
        self.assertEqual(mapping.source_original_name, "Synthetic Throttle Position")
        self.assertEqual(mapping.source_unit, "%")
        self.assertIs(throttle.series.values, source_values_before)
        self.assertIs(throttle.metadata, source_metadata_before)
        self.assertEqual(throttle.series.values[0], "40")

    def test_ac002_mapping_is_linked_to_explicit_rule(self) -> None:
        result = self.normalizer.normalize(self.dataset, self.validation)
        mapping = result.mapping_for_source("speed_src")

        self.assertIs(mapping.canonical_concept, CanonicalConcept.VEHICLE_SPEED)
        self.assertEqual(mapping.rule_id, "ome.fixture.vehicle-speed")
        self.assertEqual(mapping.rule_version, "0.1.0")
        self.assertEqual(
            mapping.source_semantics,
            "Synthetic vehicle speed supplied directly in metres per second.",
        )

    def test_ac003_unmatched_channel_remains_explicitly_unmapped(self) -> None:
        result = self.normalizer.normalize(self.dataset, self.validation)
        lap = result.unmapped_for(["lap_src"])

        self.assertEqual(len(lap), 1)
        self.assertIs(lap[0].reason, UnmappedReason.NO_MATCHING_RULE)
        self.assertNotIn(
            "lap_src",
            {mapping.source_channel_identifier for mapping in result.mappings},
        )

    def test_ac004_conversions_are_deterministic_and_traceable(self) -> None:
        result = self.normalizer.normalize(self.dataset, self.validation)
        throttle = result.mapping_for_source("throttle_src")
        rpm = result.mapping_for_source("rpm_src")

        self.assertEqual(throttle.series.values[0], 0.4)
        self.assertEqual(throttle.target_unit, "1")
        self.assertEqual(
            throttle.conversion_id,
            "ome.conversion.percent_to_fraction",
        )
        self.assertEqual(throttle.conversion_version, "1.0.0")

        expected_radians_per_second = 3200.0 * 2.0 * math.pi / 60.0
        self.assertAlmostEqual(
            rpm.series.values[0],
            expected_radians_per_second,
        )
        self.assertEqual(rpm.source_unit, "rpm")
        self.assertEqual(rpm.target_unit, "rad/s")
        self.assertEqual(self.dataset.channel("rpm_src").series.values[0], "3200")

    def test_ac005_similar_speed_sources_are_not_collapsed(self) -> None:
        speed = self.dataset.channel("speed_src")
        wheel_speed = SourceChannel(
            identifier="wheel_speed_src",
            original_name="Synthetic Wheel Speed",
            source_system=speed.source_system,
            metadata=ChannelMetadata(
                unit="m/s",
                sample_rate_hz=speed.metadata.sample_rate_hz,
                data_type="float",
                description="Synthetic wheel-derived speed.",
            ),
            series=SampleSeries(
                timestamps_s=speed.series.timestamps_s,
                values=speed.series.values,
            ),
        )
        dataset = replace(
            self.dataset,
            channels=(*self.dataset.channels, wheel_speed),
        )
        validation = TelemetryValidator().validate(dataset)
        wheel_rule = rule(
            rule_id="ome.fixture.wheel-speed",
            channel_identifier="wheel_speed_src",
            original_name="Synthetic Wheel Speed",
            source_unit="m/s",
            concept=CanonicalConcept.VEHICLE_SPEED,
            source_semantics="Synthetic wheel-derived speed.",
            target_unit="m/s",
            conversion=ConversionKind.NUMERIC_IDENTITY,
        )
        normalizer = TelemetryNormalizer((*fixture_rules(), wheel_rule))

        result = normalizer.normalize(dataset, validation)
        speed_mappings = result.mappings_for(CanonicalConcept.VEHICLE_SPEED)

        self.assertEqual(len(speed_mappings), 2)
        self.assertEqual(
            {mapping.source_channel_identifier for mapping in speed_mappings},
            {"speed_src", "wheel_speed_src"},
        )

    def test_ac006_rules_and_conversions_are_versioned_and_reproducible(self) -> None:
        first = self.normalizer.normalize(self.dataset, self.validation)
        second = self.normalizer.normalize(self.dataset, self.validation)

        self.assertEqual(first, second)
        for mapping in first.mappings:
            self.assertTrue(mapping.rule_version)
            self.assertTrue(mapping.conversion_version)

    def test_blocking_validation_prevents_channel_mapping(self) -> None:
        speed = self.dataset.channel("speed_src")
        broken_speed = replace(
            speed,
            series=SampleSeries(
                timestamps_s=(0.0, 0.1, 0.1),
                values=("18.0", "18.8", "19.7"),
            ),
        )
        dataset = replace(
            self.dataset,
            channels=tuple(
                broken_speed if channel.identifier == "speed_src" else channel
                for channel in self.dataset.channels
            ),
        )
        validation = TelemetryValidator().validate(dataset)

        result = self.normalizer.normalize(dataset, validation)
        speed = result.unmapped_for(["speed_src"])

        self.assertEqual(len(speed), 1)
        self.assertIs(speed[0].reason, UnmappedReason.BLOCKED_BY_VALIDATION)

    def test_rule_precondition_mismatch_does_not_guess(self) -> None:
        speed = self.dataset.channel("speed_src")
        wrong_unit_speed = replace(
            speed,
            metadata=replace(speed.metadata, unit="km/h"),
        )
        dataset = replace(
            self.dataset,
            channels=tuple(
                wrong_unit_speed if channel.identifier == "speed_src" else channel
                for channel in self.dataset.channels
            ),
        )
        validation = TelemetryValidator().validate(dataset)

        result = self.normalizer.normalize(dataset, validation)
        speed = result.unmapped_for(["speed_src"])

        self.assertEqual(len(speed), 1)
        self.assertIs(speed[0].reason, UnmappedReason.RULE_PRECONDITION_FAILED)

    def test_ambiguous_explicit_rules_do_not_choose_silently(self) -> None:
        duplicate_rule = replace(
            fixture_rules()[0],
            rule_id="ome.fixture.vehicle-speed-alternative",
        )
        normalizer = TelemetryNormalizer((*fixture_rules(), duplicate_rule))

        result = normalizer.normalize(self.dataset, self.validation)
        speed = result.unmapped_for(["speed_src"])

        self.assertEqual(len(speed), 1)
        self.assertIs(speed[0].reason, UnmappedReason.AMBIGUOUS_RULE_MATCH)

    def test_conversion_failure_leaves_source_channel_unmapped(self) -> None:
        speed = self.dataset.channel("speed_src")
        bad_speed = replace(
            speed,
            series=replace(
                speed.series,
                values=("not-a-number", *speed.series.values[1:]),
            ),
        )
        dataset = replace(
            self.dataset,
            channels=tuple(
                bad_speed if channel.identifier == "speed_src" else channel
                for channel in self.dataset.channels
            ),
        )
        validation = TelemetryValidator().validate(dataset)

        result = self.normalizer.normalize(dataset, validation)
        speed = result.unmapped_for(["speed_src"])

        self.assertEqual(len(speed), 1)
        self.assertIs(speed[0].reason, UnmappedReason.CONVERSION_FAILED)
        self.assertEqual(dataset.channel("speed_src").series.values[0], "not-a-number")

    def test_validation_result_must_belong_to_dataset(self) -> None:
        other_validation = replace(
            self.validation,
            dataset_fingerprint="sha256:other",
        )

        with self.assertRaisesRegex(ValueError, "does not belong"):
            self.normalizer.normalize(self.dataset, other_validation)

    def test_import_validate_normalize_integration_preserves_timestamps(self) -> None:
        result = self.normalizer.normalize(self.dataset, self.validation)
        source = self.dataset.channel("steering_src")
        normalized = result.mapping_for_source("steering_src")

        self.assertIs(normalized.series.timestamps_s, source.series.timestamps_s)
        self.assertEqual(normalized.series.values[0], 0.0)
        self.assertEqual(normalized.series.values[5], -0.01)


if __name__ == "__main__":
    unittest.main()
