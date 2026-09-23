from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ome.analysis.lap_comparison import LapComparisonSuccess
from ome.domain import CanonicalConcept
from ome.evidence import DeltaObservationProvenance

ALGORITHM_ID = "ome.lap-observation.delta-regions"
ALGORITHM_VERSION = "0.1.0"
BASE_ALGORITHM_ID = "ome.lap-comparison.distance-linear"
BASE_ALGORITHM_VERSION = "0.1.0"
DEFAULT_ZERO_TOLERANCE_S = 1e-9


class DeltaRegionKind(StrEnum):
    B_GAIN = "b_gain"
    B_LOSS = "b_loss"
    NEUTRAL = "neutral"


class DeltaObservationIssueCode(StrEnum):
    MISSING_BASE_COMPARISON = "missing_base_comparison"
    INCOMPATIBLE_BASE_COMPARISON = "incompatible_base_comparison"
    LENGTH_MISMATCH = "length_mismatch"
    INSUFFICIENT_GRID = "insufficient_grid"
    NON_FINITE_DISTANCE = "non_finite_distance"
    NON_FINITE_DELTA = "non_finite_delta"
    DISTANCE_NOT_STRICTLY_INCREASING = "distance_not_strictly_increasing"
    INVALID_ZERO_TOLERANCE = "invalid_zero_tolerance"
    MISSING_PROVENANCE = "missing_provenance"


@dataclass(frozen=True, slots=True)
class DeltaObservationReadinessIssue:
    code: DeltaObservationIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class DeltaRegion:
    kind: DeltaRegionKind
    start_distance_m: float
    end_distance_m: float
    start_delta_s: float
    end_delta_s: float
    total_delta_change_s: float
    interval_count: int


@dataclass(frozen=True, slots=True)
class DeltaObservationRequest:
    base_comparison: LapComparisonSuccess | None
    zero_tolerance_s: float = DEFAULT_ZERO_TOLERANCE_S


@dataclass(frozen=True, slots=True)
class DeltaObservationNotReady:
    issues: tuple[DeltaObservationReadinessIssue, ...]


@dataclass(frozen=True, slots=True)
class DeltaObservationSuccess:
    regions: tuple[DeltaRegion, ...]
    provenance: DeltaObservationProvenance


DeltaObservationOutcome = DeltaObservationSuccess | DeltaObservationNotReady


class DeltaObservationEngine:
    algorithm_id = ALGORITHM_ID
    algorithm_version = ALGORITHM_VERSION

    def observe(self, request: DeltaObservationRequest) -> DeltaObservationOutcome:
        issues: list[DeltaObservationReadinessIssue] = []

        if (
            not math.isfinite(request.zero_tolerance_s)
            or request.zero_tolerance_s < 0.0
        ):
            issues.append(
                DeltaObservationReadinessIssue(
                    code=DeltaObservationIssueCode.INVALID_ZERO_TOLERANCE,
                    message="Zero tolerance must be a finite non-negative number of seconds.",
                )
            )

        base = request.base_comparison
        if base is None:
            issues.append(
                DeltaObservationReadinessIssue(
                    code=DeltaObservationIssueCode.MISSING_BASE_COMPARISON,
                    message="Delta observations require a successful base lap comparison.",
                )
            )
            return DeltaObservationNotReady(issues=tuple(issues))

        if not self._base_is_compatible(base):
            issues.append(
                DeltaObservationReadinessIssue(
                    code=DeltaObservationIssueCode.INCOMPATIBLE_BASE_COMPARISON,
                    message=(
                        "Delta observations require the accepted v0.1 distance-linear "
                        "lap comparison result."
                    ),
                )
            )

        if not self._provenance_is_complete(base):
            issues.append(
                DeltaObservationReadinessIssue(
                    code=DeltaObservationIssueCode.MISSING_PROVENANCE,
                    message="Base comparison provenance is incomplete.",
                )
            )

        lengths = {
            len(base.distance_grid_m),
            len(base.lap_a_elapsed_s),
            len(base.lap_b_elapsed_s),
            len(base.delta_b_vs_a_s),
        }
        if len(lengths) != 1:
            issues.append(
                DeltaObservationReadinessIssue(
                    code=DeltaObservationIssueCode.LENGTH_MISMATCH,
                    message=(
                        "Base comparison distance, elapsed-time and delta series "
                        "must have equal lengths."
                    ),
                )
            )
        elif len(base.distance_grid_m) < 2:
            issues.append(
                DeltaObservationReadinessIssue(
                    code=DeltaObservationIssueCode.INSUFFICIENT_GRID,
                    message="Delta observations require at least two comparison grid points.",
                )
            )

        if any(not math.isfinite(value) for value in base.distance_grid_m):
            issues.append(
                DeltaObservationReadinessIssue(
                    code=DeltaObservationIssueCode.NON_FINITE_DISTANCE,
                    message="Base comparison distance grid contains a non-finite value.",
                )
            )
        elif (
            len(base.distance_grid_m) >= 2
            and not self._strictly_increasing(base.distance_grid_m)
        ):
            issues.append(
                DeltaObservationReadinessIssue(
                    code=DeltaObservationIssueCode.DISTANCE_NOT_STRICTLY_INCREASING,
                    message="Base comparison distance grid must be strictly increasing.",
                )
            )

        if any(not math.isfinite(value) for value in base.delta_b_vs_a_s):
            issues.append(
                DeltaObservationReadinessIssue(
                    code=DeltaObservationIssueCode.NON_FINITE_DELTA,
                    message="Base comparison delta series contains a non-finite value.",
                )
            )

        if issues:
            return DeltaObservationNotReady(issues=tuple(issues))

        regions = self._regions(
            base.distance_grid_m,
            base.delta_b_vs_a_s,
            request.zero_tolerance_s,
        )
        provenance = DeltaObservationProvenance(
            algorithm_id=self.algorithm_id,
            algorithm_version=self.algorithm_version,
            parameters={"zero_tolerance_s": request.zero_tolerance_s},
            base_comparison=base.provenance,
        )
        return DeltaObservationSuccess(
            regions=regions,
            provenance=provenance,
        )

    @staticmethod
    def _base_is_compatible(base: LapComparisonSuccess) -> bool:
        provenance = base.provenance
        return (
            provenance.algorithm_id == BASE_ALGORITHM_ID
            and provenance.algorithm_version == BASE_ALGORITHM_VERSION
            and provenance.reference_concept is CanonicalConcept.LAP_DISTANCE
            and provenance.reference_unit == "m"
            and provenance.time_concept is CanonicalConcept.TIME_ELAPSED
            and provenance.time_unit == "s"
        )

    @staticmethod
    def _provenance_is_complete(base: LapComparisonSuccess) -> bool:
        provenance = base.provenance
        for lap in (provenance.lap_a, provenance.lap_b):
            context = lap.context
            if not context.dataset_fingerprint.strip():
                return False
            if not context.session_identifier.strip():
                return False
            if not context.lap_identifier.strip():
                return False
            if context.run_identifier is not None and not context.run_identifier.strip():
                return False

            for evidence in (lap.distance, lap.elapsed_time):
                if evidence.dataset_fingerprint != context.dataset_fingerprint:
                    return False
                if not evidence.source_channel_identifier.strip():
                    return False
                if not evidence.source_original_name.strip():
                    return False
                if any(
                    not transformation.transformation_id.strip()
                    or not transformation.transformation_version.strip()
                    for transformation in evidence.transformations
                ):
                    return False

        return True

    @staticmethod
    def _strictly_increasing(values: tuple[float, ...]) -> bool:
        return all(
            current > previous
            for previous, current in zip(values, values[1:], strict=False)
        )

    @staticmethod
    def _classify(
        delta_change_s: float,
        zero_tolerance_s: float,
    ) -> DeltaRegionKind:
        if delta_change_s < -zero_tolerance_s:
            return DeltaRegionKind.B_GAIN
        if delta_change_s > zero_tolerance_s:
            return DeltaRegionKind.B_LOSS
        return DeltaRegionKind.NEUTRAL

    @classmethod
    def _regions(
        cls,
        distance_grid_m: tuple[float, ...],
        delta_b_vs_a_s: tuple[float, ...],
        zero_tolerance_s: float,
    ) -> tuple[DeltaRegion, ...]:
        regions: list[DeltaRegion] = []

        start_index = 0
        current_kind = cls._classify(
            delta_b_vs_a_s[1] - delta_b_vs_a_s[0],
            zero_tolerance_s,
        )

        for interval_index in range(1, len(distance_grid_m) - 1):
            next_kind = cls._classify(
                delta_b_vs_a_s[interval_index + 1]
                - delta_b_vs_a_s[interval_index],
                zero_tolerance_s,
            )
            if next_kind is current_kind:
                continue

            regions.append(
                cls._region(
                    current_kind,
                    start_index,
                    interval_index,
                    distance_grid_m,
                    delta_b_vs_a_s,
                )
            )
            start_index = interval_index
            current_kind = next_kind

        regions.append(
            cls._region(
                current_kind,
                start_index,
                len(distance_grid_m) - 1,
                distance_grid_m,
                delta_b_vs_a_s,
            )
        )
        return tuple(regions)

    @staticmethod
    def _region(
        kind: DeltaRegionKind,
        start_index: int,
        end_index: int,
        distance_grid_m: tuple[float, ...],
        delta_b_vs_a_s: tuple[float, ...],
    ) -> DeltaRegion:
        start_delta_s = delta_b_vs_a_s[start_index]
        end_delta_s = delta_b_vs_a_s[end_index]
        return DeltaRegion(
            kind=kind,
            start_distance_m=distance_grid_m[start_index],
            end_distance_m=distance_grid_m[end_index],
            start_delta_s=start_delta_s,
            end_delta_s=end_delta_s,
            total_delta_change_s=end_delta_s - start_delta_s,
            interval_count=end_index - start_index,
        )
