from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import dataclass
from enum import StrEnum

from ome.analysis.lap_comparison import LapComparisonSuccess
from ome.domain import CanonicalConcept
from ome.evidence import CanonicalSeriesEvidence, GearOverlayProvenance

ALGORITHM_ID = "ome.lap-overlay.gear-previous-sample-on-distance-grid"
ALGORITHM_VERSION = "0.1.0"
BASE_ALGORITHM_ID = "ome.lap-comparison.distance-linear"
BASE_ALGORITHM_VERSION = "0.1.0"


class GearOverlayIssueCode(StrEnum):
    MISSING_GEAR = "missing_gear"
    INCOMPATIBLE_CONCEPT = "incompatible_concept"
    INCOMPATIBLE_UNIT = "incompatible_unit"
    LENGTH_MISMATCH = "length_mismatch"
    INSUFFICIENT_SAMPLES = "insufficient_samples"
    NON_FINITE_TIME = "non_finite_time"
    TIME_NOT_STRICTLY_INCREASING = "time_not_strictly_increasing"
    INVALID_GEAR_VALUE = "invalid_gear_value"
    INSUFFICIENT_TIME_COVERAGE = "insufficient_time_coverage"
    MISSING_PROVENANCE = "missing_provenance"
    INCOMPATIBLE_BASE_COMPARISON = "incompatible_base_comparison"


@dataclass(frozen=True, slots=True)
class GearOverlayReadinessIssue:
    code: GearOverlayIssueCode
    message: str
    lap_side: str | None = None
    required_concept: CanonicalConcept | None = None


GearInputValue = int | float | bool | str | None


@dataclass(frozen=True, slots=True)
class GearOverlaySeries:
    timestamps_s: tuple[float, ...]
    values: tuple[GearInputValue, ...]
    evidence: CanonicalSeriesEvidence


@dataclass(frozen=True, slots=True)
class GearOverlayRequest:
    base_comparison: LapComparisonSuccess
    lap_a_gear: GearOverlaySeries | None
    lap_b_gear: GearOverlaySeries | None


@dataclass(frozen=True, slots=True)
class GearOverlayNotReady:
    issues: tuple[GearOverlayReadinessIssue, ...]


@dataclass(frozen=True, slots=True)
class GearOverlaySuccess:
    canonical_concept: CanonicalConcept
    unit: str
    distance_grid_m: tuple[float, ...]
    lap_a_gears: tuple[int, ...]
    lap_b_gears: tuple[int, ...]
    provenance: GearOverlayProvenance


GearOverlayOutcome = GearOverlaySuccess | GearOverlayNotReady


class DiscreteGearOverlayEngine:
    algorithm_id = ALGORITHM_ID
    algorithm_version = ALGORITHM_VERSION

    def overlay(self, request: GearOverlayRequest) -> GearOverlayOutcome:
        issues: list[GearOverlayReadinessIssue] = []

        if not self._base_is_compatible(request.base_comparison):
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.INCOMPATIBLE_BASE_COMPARISON,
                    message=(
                        "Gear overlay requires the accepted v0.1 distance-linear "
                        "lap comparison result."
                    ),
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )

        issues.extend(
            self._gear_issues(
                series=request.lap_a_gear,
                side="A",
                dataset_fingerprint=(
                    request.base_comparison.provenance.lap_a.context.dataset_fingerprint
                ),
                target_times_s=request.base_comparison.lap_a_elapsed_s,
            )
        )
        issues.extend(
            self._gear_issues(
                series=request.lap_b_gear,
                side="B",
                dataset_fingerprint=(
                    request.base_comparison.provenance.lap_b.context.dataset_fingerprint
                ),
                target_times_s=request.base_comparison.lap_b_elapsed_s,
            )
        )

        if issues:
            return GearOverlayNotReady(issues=tuple(issues))

        lap_a_gear = request.lap_a_gear
        lap_b_gear = request.lap_b_gear
        assert lap_a_gear is not None
        assert lap_b_gear is not None

        lap_a_gears = self._sample_previous(
            lap_a_gear.timestamps_s,
            lap_a_gear.values,
            request.base_comparison.lap_a_elapsed_s,
        )
        lap_b_gears = self._sample_previous(
            lap_b_gear.timestamps_s,
            lap_b_gear.values,
            request.base_comparison.lap_b_elapsed_s,
        )

        provenance = GearOverlayProvenance(
            algorithm_id=self.algorithm_id,
            algorithm_version=self.algorithm_version,
            parameters={"sampling": "previous_sample"},
            base_comparison=request.base_comparison.provenance,
            lap_a_gear=lap_a_gear.evidence,
            lap_b_gear=lap_b_gear.evidence,
        )

        return GearOverlaySuccess(
            canonical_concept=CanonicalConcept.TRANSMISSION_GEAR,
            unit="",
            distance_grid_m=request.base_comparison.distance_grid_m,
            lap_a_gears=lap_a_gears,
            lap_b_gears=lap_b_gears,
            provenance=provenance,
        )

    @staticmethod
    def _base_is_compatible(base: LapComparisonSuccess) -> bool:
        provenance = base.provenance
        if provenance.algorithm_id != BASE_ALGORITHM_ID:
            return False
        if provenance.algorithm_version != BASE_ALGORITHM_VERSION:
            return False
        if provenance.reference_concept is not CanonicalConcept.LAP_DISTANCE:
            return False
        if provenance.reference_unit != "m":
            return False
        if provenance.time_concept is not CanonicalConcept.TIME_ELAPSED:
            return False
        if provenance.time_unit != "s":
            return False
        return len(base.distance_grid_m) == len(base.lap_a_elapsed_s) == len(
            base.lap_b_elapsed_s
        ) and bool(base.distance_grid_m)

    @staticmethod
    def _gear_issues(
        *,
        series: GearOverlaySeries | None,
        side: str,
        dataset_fingerprint: str,
        target_times_s: tuple[float, ...],
    ) -> tuple[GearOverlayReadinessIssue, ...]:
        if series is None:
            return (
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.MISSING_GEAR,
                    message=f"Lap {side} does not provide transmission.gear evidence.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                ),
            )

        issues: list[GearOverlayReadinessIssue] = []
        evidence = series.evidence

        if evidence.canonical_concept is not CanonicalConcept.TRANSMISSION_GEAR:
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.INCOMPATIBLE_CONCEPT,
                    message=f"Lap {side} evidence is not canonical transmission.gear.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )

        if evidence.unit != "":
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.INCOMPATIBLE_UNIT,
                    message=f"Lap {side} transmission.gear evidence must be unitless.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )

        if not DiscreteGearOverlayEngine._provenance_is_complete(
            evidence,
            dataset_fingerprint,
        ):
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.MISSING_PROVENANCE,
                    message=f"Lap {side} gear evidence provenance is incomplete.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )

        if len(series.timestamps_s) != len(series.values):
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.LENGTH_MISMATCH,
                    message=f"Lap {side} gear timestamp/value lengths do not match.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )
            return tuple(issues)

        if not series.timestamps_s:
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.INSUFFICIENT_SAMPLES,
                    message=f"Lap {side} gear evidence needs at least one sample.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )
            return tuple(issues)

        if any(not math.isfinite(value) for value in series.timestamps_s):
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.NON_FINITE_TIME,
                    message=f"Lap {side} gear timestamps contain a non-finite value.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )
        elif len(series.timestamps_s) >= 2 and not DiscreteGearOverlayEngine._strictly_increasing(
            series.timestamps_s
        ):
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.TIME_NOT_STRICTLY_INCREASING,
                    message=f"Lap {side} gear timestamps must be strictly increasing.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )

        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in series.values
        ):
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.INVALID_GEAR_VALUE,
                    message=f"Lap {side} gear values must be canonical integers.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )

        if not issues and not DiscreteGearOverlayEngine._covers(
            series.timestamps_s,
            target_times_s,
        ):
            issues.append(
                GearOverlayReadinessIssue(
                    code=GearOverlayIssueCode.INSUFFICIENT_TIME_COVERAGE,
                    message=(
                        f"Lap {side} gear evidence does not cover the full base "
                        "comparison elapsed-time range."
                    ),
                    lap_side=side,
                    required_concept=CanonicalConcept.TRANSMISSION_GEAR,
                )
            )

        return tuple(issues)

    @staticmethod
    def _provenance_is_complete(
        evidence: CanonicalSeriesEvidence,
        dataset_fingerprint: str,
    ) -> bool:
        if evidence.dataset_fingerprint != dataset_fingerprint:
            return False
        if not evidence.dataset_fingerprint.strip():
            return False
        if not evidence.source_channel_identifier.strip():
            return False
        if not evidence.source_original_name.strip():
            return False
        return all(
            transformation.transformation_id.strip()
            and transformation.transformation_version.strip()
            for transformation in evidence.transformations
        )

    @staticmethod
    def _strictly_increasing(values: tuple[float, ...]) -> bool:
        return all(
            current > previous for previous, current in zip(values, values[1:], strict=False)
        )

    @staticmethod
    def _covers(
        timestamps_s: tuple[float, ...],
        target_times_s: tuple[float, ...],
    ) -> bool:
        if not target_times_s:
            return False
        return timestamps_s[0] <= target_times_s[0] and timestamps_s[-1] >= target_times_s[-1]

    @staticmethod
    def _sample_previous(
        timestamps_s: tuple[float, ...],
        values: tuple[GearInputValue, ...],
        targets_s: tuple[float, ...],
    ) -> tuple[int, ...]:
        sampled: list[int] = []

        for target_s in targets_s:
            index = bisect_right(timestamps_s, target_s) - 1
            value = values[index]
            assert isinstance(value, int) and not isinstance(value, bool)
            sampled.append(value)

        return tuple(sampled)
