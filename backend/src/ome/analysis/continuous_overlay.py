from __future__ import annotations

import math
from bisect import bisect_left
from dataclasses import dataclass
from enum import StrEnum

from ome.analysis.lap_comparison import LapComparisonSuccess
from ome.domain import CanonicalConcept
from ome.evidence import (
    CanonicalSeriesEvidence,
    ContinuousOverlayProvenance,
)

ALGORITHM_ID = "ome.lap-overlay.time-linear-on-distance-grid"
ALGORITHM_VERSION = "0.1.0"
BASE_ALGORITHM_ID = "ome.lap-comparison.distance-linear"
BASE_ALGORITHM_VERSION = "0.1.0"

_SUPPORTED_UNITS = {
    CanonicalConcept.VEHICLE_SPEED: "m/s",
    CanonicalConcept.DRIVER_THROTTLE: "1",
    CanonicalConcept.DRIVER_STEERING: "rad",
    CanonicalConcept.ENGINE_SPEED: "rad/s",
}


class ContinuousOverlayIssueCode(StrEnum):
    UNSUPPORTED_CONCEPT = "unsupported_concept"
    MISSING_CHANNEL = "missing_channel"
    INCOMPATIBLE_CONCEPT = "incompatible_concept"
    INCOMPATIBLE_UNIT = "incompatible_unit"
    LENGTH_MISMATCH = "length_mismatch"
    INSUFFICIENT_SAMPLES = "insufficient_samples"
    NON_FINITE_TIME = "non_finite_time"
    NON_FINITE_VALUE = "non_finite_value"
    TIME_NOT_STRICTLY_INCREASING = "time_not_strictly_increasing"
    INSUFFICIENT_TIME_COVERAGE = "insufficient_time_coverage"
    MISSING_PROVENANCE = "missing_provenance"
    INCOMPATIBLE_BASE_COMPARISON = "incompatible_base_comparison"


@dataclass(frozen=True, slots=True)
class ContinuousOverlayReadinessIssue:
    code: ContinuousOverlayIssueCode
    message: str
    lap_side: str | None = None
    required_concept: CanonicalConcept | None = None


@dataclass(frozen=True, slots=True)
class ContinuousOverlaySeries:
    timestamps_s: tuple[float, ...]
    values: tuple[float, ...]
    evidence: CanonicalSeriesEvidence


@dataclass(frozen=True, slots=True)
class ContinuousOverlayRequest:
    base_comparison: LapComparisonSuccess
    canonical_concept: CanonicalConcept
    lap_a_channel: ContinuousOverlaySeries | None
    lap_b_channel: ContinuousOverlaySeries | None


@dataclass(frozen=True, slots=True)
class ContinuousOverlayNotReady:
    issues: tuple[ContinuousOverlayReadinessIssue, ...]


@dataclass(frozen=True, slots=True)
class ContinuousOverlaySuccess:
    canonical_concept: CanonicalConcept
    unit: str
    distance_grid_m: tuple[float, ...]
    lap_a_values: tuple[float, ...]
    lap_b_values: tuple[float, ...]
    provenance: ContinuousOverlayProvenance


ContinuousOverlayOutcome = ContinuousOverlaySuccess | ContinuousOverlayNotReady


class ContinuousOverlayEngine:
    algorithm_id = ALGORITHM_ID
    algorithm_version = ALGORITHM_VERSION

    def overlay(self, request: ContinuousOverlayRequest) -> ContinuousOverlayOutcome:
        unit = _SUPPORTED_UNITS.get(request.canonical_concept)
        if unit is None:
            return ContinuousOverlayNotReady(
                issues=(
                    ContinuousOverlayReadinessIssue(
                        code=ContinuousOverlayIssueCode.UNSUPPORTED_CONCEPT,
                        message=(
                            f"{request.canonical_concept.value} is not supported by the "
                            "continuous overlay algorithm."
                        ),
                        required_concept=request.canonical_concept,
                    ),
                )
            )

        issues: list[ContinuousOverlayReadinessIssue] = []

        if not self._base_is_compatible(request.base_comparison):
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.INCOMPATIBLE_BASE_COMPARISON,
                    message=(
                        "Continuous overlay requires the accepted v0.1 distance-linear "
                        "lap comparison result."
                    ),
                    required_concept=request.canonical_concept,
                )
            )

        issues.extend(
            self._channel_issues(
                channel=request.lap_a_channel,
                side="A",
                required_concept=request.canonical_concept,
                required_unit=unit,
                dataset_fingerprint=(
                    request.base_comparison.provenance.lap_a.context.dataset_fingerprint
                ),
                target_times_s=request.base_comparison.lap_a_elapsed_s,
            )
        )
        issues.extend(
            self._channel_issues(
                channel=request.lap_b_channel,
                side="B",
                required_concept=request.canonical_concept,
                required_unit=unit,
                dataset_fingerprint=(
                    request.base_comparison.provenance.lap_b.context.dataset_fingerprint
                ),
                target_times_s=request.base_comparison.lap_b_elapsed_s,
            )
        )

        if issues:
            return ContinuousOverlayNotReady(issues=tuple(issues))

        lap_a_channel = request.lap_a_channel
        lap_b_channel = request.lap_b_channel
        assert lap_a_channel is not None
        assert lap_b_channel is not None

        lap_a_values = self._interpolate(
            lap_a_channel.timestamps_s,
            lap_a_channel.values,
            request.base_comparison.lap_a_elapsed_s,
        )
        lap_b_values = self._interpolate(
            lap_b_channel.timestamps_s,
            lap_b_channel.values,
            request.base_comparison.lap_b_elapsed_s,
        )

        provenance = ContinuousOverlayProvenance(
            algorithm_id=self.algorithm_id,
            algorithm_version=self.algorithm_version,
            parameters={},
            base_comparison=request.base_comparison.provenance,
            lap_a_channel=lap_a_channel.evidence,
            lap_b_channel=lap_b_channel.evidence,
        )

        return ContinuousOverlaySuccess(
            canonical_concept=request.canonical_concept,
            unit=unit,
            distance_grid_m=request.base_comparison.distance_grid_m,
            lap_a_values=lap_a_values,
            lap_b_values=lap_b_values,
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
    def _channel_issues(
        *,
        channel: ContinuousOverlaySeries | None,
        side: str,
        required_concept: CanonicalConcept,
        required_unit: str,
        dataset_fingerprint: str,
        target_times_s: tuple[float, ...],
    ) -> tuple[ContinuousOverlayReadinessIssue, ...]:
        if channel is None:
            return (
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.MISSING_CHANNEL,
                    message=(f"Lap {side} does not provide {required_concept.value} evidence."),
                    lap_side=side,
                    required_concept=required_concept,
                ),
            )

        issues: list[ContinuousOverlayReadinessIssue] = []
        evidence = channel.evidence

        if evidence.canonical_concept is not required_concept:
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.INCOMPATIBLE_CONCEPT,
                    message=(
                        f"Lap {side} channel evidence does not represent {required_concept.value}."
                    ),
                    lap_side=side,
                    required_concept=required_concept,
                )
            )

        if evidence.unit != required_unit:
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.INCOMPATIBLE_UNIT,
                    message=(
                        f"Lap {side} {required_concept.value} evidence must use {required_unit!r}."
                    ),
                    lap_side=side,
                    required_concept=required_concept,
                )
            )

        if not ContinuousOverlayEngine._provenance_is_complete(
            evidence,
            dataset_fingerprint,
        ):
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.MISSING_PROVENANCE,
                    message=f"Lap {side} channel evidence provenance is incomplete.",
                    lap_side=side,
                    required_concept=required_concept,
                )
            )

        if len(channel.timestamps_s) != len(channel.values):
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.LENGTH_MISMATCH,
                    message=f"Lap {side} channel timestamp/value lengths do not match.",
                    lap_side=side,
                    required_concept=required_concept,
                )
            )
            return tuple(issues)

        if len(channel.timestamps_s) < 2:
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.INSUFFICIENT_SAMPLES,
                    message=f"Lap {side} channel requires at least two samples.",
                    lap_side=side,
                    required_concept=required_concept,
                )
            )
            return tuple(issues)

        if any(not math.isfinite(value) for value in channel.timestamps_s):
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.NON_FINITE_TIME,
                    message=f"Lap {side} channel timestamps contain a non-finite value.",
                    lap_side=side,
                    required_concept=required_concept,
                )
            )
        elif not ContinuousOverlayEngine._strictly_increasing(channel.timestamps_s):
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.TIME_NOT_STRICTLY_INCREASING,
                    message=f"Lap {side} channel timestamps must be strictly increasing.",
                    lap_side=side,
                    required_concept=required_concept,
                )
            )

        if any(not math.isfinite(value) for value in channel.values):
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.NON_FINITE_VALUE,
                    message=f"Lap {side} channel values contain a non-finite value.",
                    lap_side=side,
                    required_concept=required_concept,
                )
            )

        if not issues and not ContinuousOverlayEngine._covers(
            channel.timestamps_s,
            target_times_s,
        ):
            issues.append(
                ContinuousOverlayReadinessIssue(
                    code=ContinuousOverlayIssueCode.INSUFFICIENT_TIME_COVERAGE,
                    message=(
                        f"Lap {side} channel does not cover the full base comparison "
                        "elapsed-time range."
                    ),
                    lap_side=side,
                    required_concept=required_concept,
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
    def _interpolate(
        timestamps_s: tuple[float, ...],
        values: tuple[float, ...],
        targets_s: tuple[float, ...],
    ) -> tuple[float, ...]:
        result: list[float] = []

        for target_s in targets_s:
            upper = bisect_left(timestamps_s, target_s)

            if upper < len(timestamps_s) and timestamps_s[upper] == target_s:
                result.append(values[upper])
                continue

            lower = upper - 1
            t0 = timestamps_s[lower]
            t1 = timestamps_s[upper]
            v0 = values[lower]
            v1 = values[upper]
            fraction = (target_s - t0) / (t1 - t0)
            result.append(v0 + fraction * (v1 - v0))

        return tuple(result)
