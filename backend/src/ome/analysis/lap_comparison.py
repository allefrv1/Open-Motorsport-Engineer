from __future__ import annotations

import math
from bisect import bisect_left
from dataclasses import dataclass
from enum import StrEnum

from ome.domain import CanonicalConcept
from ome.evidence import (
    CanonicalSeriesEvidence,
    ComparisonProvenance,
    LapComparisonEvidence,
    LapEvidenceContext,
)

ALGORITHM_ID = "ome.lap-comparison.distance-linear"
ALGORITHM_VERSION = "0.1.0"
DEFAULT_GRID_STEP_M = 1.0


class ComparisonIssueCode(StrEnum):
    MISSING_DISTANCE = "missing_distance"
    MISSING_ELAPSED_TIME = "missing_elapsed_time"
    INCOMPATIBLE_DISTANCE_REFERENCE = "incompatible_distance_reference"
    INCOMPATIBLE_TIME_REFERENCE = "incompatible_time_reference"
    INSUFFICIENT_SAMPLES = "insufficient_samples"
    LENGTH_MISMATCH = "length_mismatch"
    NON_FINITE_DISTANCE = "non_finite_distance"
    NON_FINITE_TIME = "non_finite_time"
    DISTANCE_NOT_STRICTLY_INCREASING = "distance_not_strictly_increasing"
    TIME_NOT_STRICTLY_INCREASING = "time_not_strictly_increasing"
    NO_COMMON_DISTANCE = "no_common_distance"
    INVALID_GRID_STEP = "invalid_grid_step"
    MISSING_PROVENANCE = "missing_provenance"


@dataclass(frozen=True, slots=True)
class ComparisonReadinessIssue:
    code: ComparisonIssueCode
    message: str
    lap_side: str | None = None
    required_concept: CanonicalConcept | None = None


@dataclass(frozen=True, slots=True)
class LapComparisonSeries:
    values: tuple[float, ...]
    evidence: CanonicalSeriesEvidence


@dataclass(frozen=True, slots=True)
class LapComparisonLap:
    context: LapEvidenceContext
    distance: LapComparisonSeries | None
    elapsed_time: LapComparisonSeries | None


@dataclass(frozen=True, slots=True)
class LapComparisonRequest:
    lap_a: LapComparisonLap
    lap_b: LapComparisonLap
    grid_step_m: float = DEFAULT_GRID_STEP_M


@dataclass(frozen=True, slots=True)
class LapComparisonNotReady:
    issues: tuple[ComparisonReadinessIssue, ...]


@dataclass(frozen=True, slots=True)
class LapComparisonSuccess:
    reference_concept: CanonicalConcept
    reference_unit: str
    time_concept: CanonicalConcept
    time_unit: str
    common_start_m: float
    common_end_m: float
    distance_grid_m: tuple[float, ...]
    lap_a_elapsed_s: tuple[float, ...]
    lap_b_elapsed_s: tuple[float, ...]
    delta_b_vs_a_s: tuple[float, ...]
    provenance: ComparisonProvenance


LapComparisonOutcome = LapComparisonSuccess | LapComparisonNotReady


class LapComparisonEngine:
    algorithm_id = ALGORITHM_ID
    algorithm_version = ALGORITHM_VERSION

    def compare(self, request: LapComparisonRequest) -> LapComparisonOutcome:
        issues: list[ComparisonReadinessIssue] = []

        if not math.isfinite(request.grid_step_m) or request.grid_step_m <= 0.0:
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.INVALID_GRID_STEP,
                    message="Comparison grid step must be a positive finite number of metres.",
                )
            )

        issues.extend(self._lap_issues(request.lap_a, "A"))
        issues.extend(self._lap_issues(request.lap_b, "B"))

        if issues:
            return LapComparisonNotReady(issues=tuple(issues))

        lap_a_distance = request.lap_a.distance
        lap_a_time = request.lap_a.elapsed_time
        lap_b_distance = request.lap_b.distance
        lap_b_time = request.lap_b.elapsed_time

        assert lap_a_distance is not None
        assert lap_a_time is not None
        assert lap_b_distance is not None
        assert lap_b_time is not None

        common_start_m = max(lap_a_distance.values[0], lap_b_distance.values[0])
        common_end_m = min(lap_a_distance.values[-1], lap_b_distance.values[-1])

        if common_end_m <= common_start_m:
            return LapComparisonNotReady(
                issues=(
                    ComparisonReadinessIssue(
                        code=ComparisonIssueCode.NO_COMMON_DISTANCE,
                        message="The two laps do not share a positive common distance interval.",
                        required_concept=CanonicalConcept.LAP_DISTANCE,
                    ),
                )
            )

        distance_grid_m = self._distance_grid(
            common_start_m,
            common_end_m,
            request.grid_step_m,
        )
        lap_a_elapsed_s = self._interpolate(
            lap_a_distance.values,
            lap_a_time.values,
            distance_grid_m,
        )
        lap_b_elapsed_s = self._interpolate(
            lap_b_distance.values,
            lap_b_time.values,
            distance_grid_m,
        )
        delta_b_vs_a_s = tuple(
            time_b - time_a
            for time_a, time_b in zip(
                lap_a_elapsed_s,
                lap_b_elapsed_s,
                strict=True,
            )
        )

        provenance = ComparisonProvenance(
            algorithm_id=self.algorithm_id,
            algorithm_version=self.algorithm_version,
            parameters={"grid_step_m": request.grid_step_m},
            reference_concept=CanonicalConcept.LAP_DISTANCE,
            reference_unit="m",
            time_concept=CanonicalConcept.TIME_ELAPSED,
            time_unit="s",
            common_start_m=common_start_m,
            common_end_m=common_end_m,
            lap_a=self._lap_evidence(request.lap_a),
            lap_b=self._lap_evidence(request.lap_b),
        )

        return LapComparisonSuccess(
            reference_concept=CanonicalConcept.LAP_DISTANCE,
            reference_unit="m",
            time_concept=CanonicalConcept.TIME_ELAPSED,
            time_unit="s",
            common_start_m=common_start_m,
            common_end_m=common_end_m,
            distance_grid_m=distance_grid_m,
            lap_a_elapsed_s=lap_a_elapsed_s,
            lap_b_elapsed_s=lap_b_elapsed_s,
            delta_b_vs_a_s=delta_b_vs_a_s,
            provenance=provenance,
        )

    def _lap_issues(
        self,
        lap: LapComparisonLap,
        side: str,
    ) -> tuple[ComparisonReadinessIssue, ...]:
        issues: list[ComparisonReadinessIssue] = []

        if not self._context_is_complete(lap.context):
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.MISSING_PROVENANCE,
                    message=f"Lap {side} is missing required dataset/session/lap provenance.",
                    lap_side=side,
                )
            )

        distance = lap.distance
        elapsed_time = lap.elapsed_time

        if distance is None:
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.MISSING_DISTANCE,
                    message=f"Lap {side} does not provide lap.distance evidence.",
                    lap_side=side,
                    required_concept=CanonicalConcept.LAP_DISTANCE,
                )
            )
        else:
            issues.extend(self._distance_issues(distance, lap.context, side))

        if elapsed_time is None:
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.MISSING_ELAPSED_TIME,
                    message=f"Lap {side} does not provide time.elapsed evidence.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TIME_ELAPSED,
                )
            )
        else:
            issues.extend(self._time_issues(elapsed_time, lap.context, side))

        if distance is not None and elapsed_time is not None:
            if len(distance.values) != len(elapsed_time.values):
                issues.append(
                    ComparisonReadinessIssue(
                        code=ComparisonIssueCode.LENGTH_MISMATCH,
                        message=f"Lap {side} distance/time series lengths do not match.",
                        lap_side=side,
                    )
                )
            elif len(distance.values) < 2:
                issues.append(
                    ComparisonReadinessIssue(
                        code=ComparisonIssueCode.INSUFFICIENT_SAMPLES,
                        message=f"Lap {side} needs at least two paired samples.",
                        lap_side=side,
                    )
                )

        return tuple(issues)

    @staticmethod
    def _distance_issues(
        series: LapComparisonSeries,
        context: LapEvidenceContext,
        side: str,
    ) -> tuple[ComparisonReadinessIssue, ...]:
        issues: list[ComparisonReadinessIssue] = []
        evidence = series.evidence

        if evidence.canonical_concept is not CanonicalConcept.LAP_DISTANCE or evidence.unit != "m":
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.INCOMPATIBLE_DISTANCE_REFERENCE,
                    message=f"Lap {side} distance evidence must be lap.distance in metres.",
                    lap_side=side,
                    required_concept=CanonicalConcept.LAP_DISTANCE,
                )
            )

        if not LapComparisonEngine._series_provenance_is_complete(evidence, context):
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.MISSING_PROVENANCE,
                    message=f"Lap {side} distance evidence provenance is incomplete.",
                    lap_side=side,
                    required_concept=CanonicalConcept.LAP_DISTANCE,
                )
            )

        if any(not math.isfinite(value) for value in series.values):
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.NON_FINITE_DISTANCE,
                    message=f"Lap {side} distance contains a non-finite value.",
                    lap_side=side,
                    required_concept=CanonicalConcept.LAP_DISTANCE,
                )
            )
        elif len(series.values) >= 2 and not LapComparisonEngine._strictly_increasing(
            series.values
        ):
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.DISTANCE_NOT_STRICTLY_INCREASING,
                    message=f"Lap {side} distance must be strictly increasing in v0.1.",
                    lap_side=side,
                    required_concept=CanonicalConcept.LAP_DISTANCE,
                )
            )

        return tuple(issues)

    @staticmethod
    def _time_issues(
        series: LapComparisonSeries,
        context: LapEvidenceContext,
        side: str,
    ) -> tuple[ComparisonReadinessIssue, ...]:
        issues: list[ComparisonReadinessIssue] = []
        evidence = series.evidence

        if evidence.canonical_concept is not CanonicalConcept.TIME_ELAPSED or evidence.unit != "s":
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.INCOMPATIBLE_TIME_REFERENCE,
                    message=f"Lap {side} time evidence must be time.elapsed in seconds.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TIME_ELAPSED,
                )
            )

        if not LapComparisonEngine._series_provenance_is_complete(evidence, context):
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.MISSING_PROVENANCE,
                    message=f"Lap {side} time evidence provenance is incomplete.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TIME_ELAPSED,
                )
            )

        if any(not math.isfinite(value) for value in series.values):
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.NON_FINITE_TIME,
                    message=f"Lap {side} elapsed time contains a non-finite value.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TIME_ELAPSED,
                )
            )
        elif len(series.values) >= 2 and not LapComparisonEngine._strictly_increasing(
            series.values
        ):
            issues.append(
                ComparisonReadinessIssue(
                    code=ComparisonIssueCode.TIME_NOT_STRICTLY_INCREASING,
                    message=f"Lap {side} elapsed time must be strictly increasing.",
                    lap_side=side,
                    required_concept=CanonicalConcept.TIME_ELAPSED,
                )
            )

        return tuple(issues)

    @staticmethod
    def _context_is_complete(context: LapEvidenceContext) -> bool:
        if not context.dataset_fingerprint.strip():
            return False
        if not context.session_identifier.strip():
            return False
        if not context.lap_identifier.strip():
            return False
        if context.run_identifier is not None and not context.run_identifier.strip():
            return False
        return True

    @staticmethod
    def _series_provenance_is_complete(
        evidence: CanonicalSeriesEvidence,
        context: LapEvidenceContext,
    ) -> bool:
        if evidence.dataset_fingerprint != context.dataset_fingerprint:
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
        return all(current > previous for previous, current in zip(values, values[1:]))

    @staticmethod
    def _distance_grid(
        start_m: float,
        end_m: float,
        step_m: float,
    ) -> tuple[float, ...]:
        span_m = end_m - start_m
        regular_steps = int(math.floor(span_m / step_m))
        grid = [start_m + index * step_m for index in range(regular_steps + 1)]

        tolerance = max(1.0, abs(end_m)) * 1e-12
        if math.isclose(grid[-1], end_m, rel_tol=0.0, abs_tol=tolerance):
            grid[-1] = end_m
        elif grid[-1] < end_m:
            grid.append(end_m)

        return tuple(grid)

    @staticmethod
    def _interpolate(
        distance_m: tuple[float, ...],
        values: tuple[float, ...],
        grid_m: tuple[float, ...],
    ) -> tuple[float, ...]:
        result: list[float] = []

        for target_m in grid_m:
            upper = bisect_left(distance_m, target_m)

            if upper < len(distance_m) and distance_m[upper] == target_m:
                result.append(values[upper])
                continue

            lower = upper - 1
            d0 = distance_m[lower]
            d1 = distance_m[upper]
            v0 = values[lower]
            v1 = values[upper]
            fraction = (target_m - d0) / (d1 - d0)
            result.append(v0 + fraction * (v1 - v0))

        return tuple(result)

    @staticmethod
    def _lap_evidence(lap: LapComparisonLap) -> LapComparisonEvidence:
        assert lap.distance is not None
        assert lap.elapsed_time is not None
        return LapComparisonEvidence(
            context=lap.context,
            distance=lap.distance.evidence,
            elapsed_time=lap.elapsed_time.evidence,
        )
