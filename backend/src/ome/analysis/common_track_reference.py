from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from geographiclib.geodesic import Geodesic

from ome.analysis.gps_path_distance import GPSPathDistanceSuccess
from ome.evidence import (
    CommonTrackReferenceProvenance,
    LapEvidenceContext,
    SourceSeriesEvidence,
)

ALGORITHM_ID = "ome.track-reference.explicit-lap-projection"
ALGORITHM_VERSION = "0.1.0"


class CommonTrackReferenceIssueCode(StrEnum):
    LENGTH_MISMATCH = "length_mismatch"
    INSUFFICIENT_SAMPLES = "insufficient_samples"
    NON_FINITE_COORDINATE = "non_finite_coordinate"
    INVALID_LATITUDE = "invalid_latitude"
    INVALID_LONGITUDE = "invalid_longitude"
    NON_FINITE_TIME = "non_finite_time"
    TIME_NOT_STRICTLY_INCREASING = "time_not_strictly_increasing"
    INCOMPATIBLE_UNITS = "incompatible_units"
    MISSING_PROVENANCE = "missing_provenance"
    MISSING_REFERENCE_PATH_DISTANCE = "missing_reference_path_distance"
    INVALID_REFERENCE_PATH_DISTANCE = "invalid_reference_path_distance"
    REFERENCE_SELF_INTERSECTION = "reference_self_intersection"
    PROJECTED_DISTANCE_NOT_STRICTLY_INCREASING = (
        "projected_distance_not_strictly_increasing"
    )


@dataclass(frozen=True, slots=True)
class CommonTrackReferenceReadinessIssue:
    code: CommonTrackReferenceIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class TrackReferenceLap:
    context: LapEvidenceContext
    timestamps_s: tuple[float, ...]
    latitudes_deg: tuple[float, ...]
    longitudes_deg: tuple[float, ...]
    latitude_evidence: SourceSeriesEvidence
    longitude_evidence: SourceSeriesEvidence
    time_evidence: SourceSeriesEvidence
    gps_path_distance: GPSPathDistanceSuccess | None = None


@dataclass(frozen=True, slots=True)
class CommonTrackReferenceRequest:
    reference: TrackReferenceLap
    candidate: TrackReferenceLap


@dataclass(frozen=True, slots=True)
class CommonTrackReferenceNotReady:
    issues: tuple[CommonTrackReferenceReadinessIssue, ...]


@dataclass(frozen=True, slots=True)
class CommonTrackReferenceSuccess:
    derived_concept: str
    unit: str
    algorithm_id: str
    algorithm_version: str
    reference_length_m: float
    origin_latitude_deg: float
    origin_longitude_deg: float
    timestamps_s: tuple[float, ...]
    raw_reference_distance_m: tuple[float, ...]
    reference_distance_m: tuple[float, ...]
    reference_segment_index: tuple[int, ...]
    segment_fraction: tuple[float, ...]
    lateral_error_m: tuple[float, ...]
    max_lateral_error_m: float
    p95_lateral_error_m: float
    start_offset_m: float
    end_offset_from_reference_m: float
    provenance: CommonTrackReferenceProvenance


CommonTrackReferenceOutcome = CommonTrackReferenceSuccess | CommonTrackReferenceNotReady


@dataclass(frozen=True, slots=True)
class _Point:
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class _Projection:
    segment_index: int
    fraction: float
    lateral_error_m: float
    raw_distance_m: float


class CommonTrackReferenceEngine:
    algorithm_id = ALGORITHM_ID
    algorithm_version = ALGORITHM_VERSION

    def project(
        self,
        request: CommonTrackReferenceRequest,
    ) -> CommonTrackReferenceOutcome:
        issues = self._readiness_issues(request)
        if issues:
            return CommonTrackReferenceNotReady(issues=issues)

        reference = request.reference
        candidate = request.candidate
        reference_path = reference.gps_path_distance
        assert reference_path is not None

        origin_latitude_deg = reference.latitudes_deg[0]
        origin_longitude_deg = reference.longitudes_deg[0]

        reference_points = tuple(
            self._local_point(
                origin_latitude_deg,
                origin_longitude_deg,
                latitude,
                longitude,
            )
            for latitude, longitude in zip(
                reference.latitudes_deg,
                reference.longitudes_deg,
                strict=True,
            )
        )

        if self._has_material_self_intersection(reference_points):
            return CommonTrackReferenceNotReady(
                issues=(
                    CommonTrackReferenceReadinessIssue(
                        code=CommonTrackReferenceIssueCode.REFERENCE_SELF_INTERSECTION,
                        message=(
                            "Reference geometry contains a material self-intersection "
                            "that makes nearest-position interpretation ambiguous."
                        ),
                    ),
                )
            )

        candidate_points = tuple(
            self._local_point(
                origin_latitude_deg,
                origin_longitude_deg,
                latitude,
                longitude,
            )
            for latitude, longitude in zip(
                candidate.latitudes_deg,
                candidate.longitudes_deg,
                strict=True,
            )
        )

        projections = tuple(
            self._nearest_projection(
                point,
                reference_points,
                reference_path.path_distance_m,
            )
            for point in candidate_points
        )

        raw_distance_m = tuple(projection.raw_distance_m for projection in projections)
        reference_distance_m = self._unwrap(
            raw_distance_m,
            reference_path.total_distance_m,
        )

        if not self._strictly_increasing(reference_distance_m):
            return CommonTrackReferenceNotReady(
                issues=(
                    CommonTrackReferenceReadinessIssue(
                        code=(
                            CommonTrackReferenceIssueCode.PROJECTED_DISTANCE_NOT_STRICTLY_INCREASING
                        ),
                        message=(
                            "Projected common-track reference distance must be strictly "
                            "increasing after circular seam unwrap."
                        ),
                    ),
                )
            )

        lateral_error_m = tuple(projection.lateral_error_m for projection in projections)
        provenance = CommonTrackReferenceProvenance(
            algorithm_id=self.algorithm_id,
            algorithm_version=self.algorithm_version,
            reference_dataset_fingerprint=reference.context.dataset_fingerprint,
            candidate_dataset_fingerprint=candidate.context.dataset_fingerprint,
            reference_context=reference.context,
            candidate_context=candidate.context,
            reference_latitude=reference.latitude_evidence,
            reference_longitude=reference.longitude_evidence,
            reference_elapsed_time=reference.time_evidence,
            candidate_latitude=candidate.latitude_evidence,
            candidate_longitude=candidate.longitude_evidence,
            candidate_elapsed_time=candidate.time_evidence,
            reference_gps_path=reference_path.provenance,
            origin_latitude_deg=origin_latitude_deg,
            origin_longitude_deg=origin_longitude_deg,
            reference_length_m=reference_path.total_distance_m,
        )

        return CommonTrackReferenceSuccess(
            derived_concept="track.reference_distance",
            unit="m",
            algorithm_id=self.algorithm_id,
            algorithm_version=self.algorithm_version,
            reference_length_m=reference_path.total_distance_m,
            origin_latitude_deg=origin_latitude_deg,
            origin_longitude_deg=origin_longitude_deg,
            timestamps_s=candidate.timestamps_s,
            raw_reference_distance_m=raw_distance_m,
            reference_distance_m=reference_distance_m,
            reference_segment_index=tuple(
                projection.segment_index for projection in projections
            ),
            segment_fraction=tuple(projection.fraction for projection in projections),
            lateral_error_m=lateral_error_m,
            max_lateral_error_m=max(lateral_error_m),
            p95_lateral_error_m=self._percentile_95(lateral_error_m),
            start_offset_m=reference_distance_m[0],
            end_offset_from_reference_m=(
                reference_distance_m[-1] - reference_path.total_distance_m
            ),
            provenance=provenance,
        )

    @staticmethod
    def _readiness_issues(
        request: CommonTrackReferenceRequest,
    ) -> tuple[CommonTrackReferenceReadinessIssue, ...]:
        issues: list[CommonTrackReferenceReadinessIssue] = []
        issues.extend(
            CommonTrackReferenceEngine._lap_readiness_issues(
                request.reference,
                label="Reference",
            )
        )
        issues.extend(
            CommonTrackReferenceEngine._lap_readiness_issues(
                request.candidate,
                label="Candidate",
            )
        )

        reference_path = request.reference.gps_path_distance
        if reference_path is None:
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.MISSING_REFERENCE_PATH_DISTANCE,
                    message="Reference lap requires accepted gps.path_distance evidence.",
                )
            )
            return tuple(issues)

        reference = request.reference
        if (
            reference_path.provenance.dataset_fingerprint
            != reference.context.dataset_fingerprint
            or reference_path.timestamps_s != reference.timestamps_s
            or len(reference_path.path_distance_m) != len(reference.timestamps_s)
            or reference_path.derived_concept != "gps.path_distance"
            or reference_path.unit != "m"
            or not math.isfinite(reference_path.total_distance_m)
            or reference_path.total_distance_m <= 0.0
            or not CommonTrackReferenceEngine._non_decreasing(
                reference_path.path_distance_m
            )
        ):
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.INVALID_REFERENCE_PATH_DISTANCE,
                    message=(
                        "Reference gps.path_distance must belong to the same dataset, "
                        "match the reference samples, use metres and contain a usable "
                        "non-decreasing cumulative path."
                    ),
                )
            )

        return tuple(issues)

    @staticmethod
    def _lap_readiness_issues(
        lap: TrackReferenceLap,
        *,
        label: str,
    ) -> tuple[CommonTrackReferenceReadinessIssue, ...]:
        issues: list[CommonTrackReferenceReadinessIssue] = []
        lengths = (
            len(lap.timestamps_s),
            len(lap.latitudes_deg),
            len(lap.longitudes_deg),
        )

        if len(set(lengths)) != 1:
            return (
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.LENGTH_MISMATCH,
                    message=f"{label} GPS time/latitude/longitude lengths must match.",
                ),
            )

        if lengths[0] < 2:
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.INSUFFICIENT_SAMPLES,
                    message=f"{label} lap requires at least two paired GPS samples.",
                )
            )

        if not CommonTrackReferenceEngine._provenance_ready(lap):
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.MISSING_PROVENANCE,
                    message=(
                        f"{label} lap requires context and latitude/longitude/time "
                        "evidence tied to the same source dataset."
                    ),
                )
            )

        if (
            lap.latitude_evidence.unit != "deg"
            or lap.longitude_evidence.unit != "deg"
            or lap.time_evidence.unit != "s"
        ):
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.INCOMPATIBLE_UNITS,
                    message=f"{label} GPS coordinates require degrees and time seconds.",
                )
            )

        if any(not math.isfinite(value) for value in lap.timestamps_s):
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.NON_FINITE_TIME,
                    message=f"{label} timestamps must be finite.",
                )
            )
        elif not CommonTrackReferenceEngine._strictly_increasing(lap.timestamps_s):
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.TIME_NOT_STRICTLY_INCREASING,
                    message=f"{label} timestamps must be strictly increasing.",
                )
            )

        coordinates = (*lap.latitudes_deg, *lap.longitudes_deg)
        if any(not math.isfinite(value) for value in coordinates):
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.NON_FINITE_COORDINATE,
                    message=f"{label} GPS coordinates must be finite.",
                )
            )
            return tuple(issues)

        if any(latitude < -90.0 or latitude > 90.0 for latitude in lap.latitudes_deg):
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.INVALID_LATITUDE,
                    message=f"{label} latitude must be within [-90, 90] degrees.",
                )
            )

        if any(
            longitude < -180.0 or longitude > 180.0
            for longitude in lap.longitudes_deg
        ):
            issues.append(
                CommonTrackReferenceReadinessIssue(
                    code=CommonTrackReferenceIssueCode.INVALID_LONGITUDE,
                    message=f"{label} longitude must be within [-180, 180] degrees.",
                )
            )

        return tuple(issues)

    @staticmethod
    def _provenance_ready(lap: TrackReferenceLap) -> bool:
        fingerprint = lap.context.dataset_fingerprint
        if not fingerprint.strip():
            return False

        if (
            not lap.context.session_identifier.strip()
            or not lap.context.lap_identifier.strip()
        ):
            return False

        for evidence in (
            lap.latitude_evidence,
            lap.longitude_evidence,
            lap.time_evidence,
        ):
            if evidence.dataset_fingerprint != fingerprint:
                return False
            if (
                not evidence.source_channel_identifier.strip()
                or not evidence.source_original_name.strip()
            ):
                return False
        return True

    @staticmethod
    def _local_point(
        origin_latitude_deg: float,
        origin_longitude_deg: float,
        latitude_deg: float,
        longitude_deg: float,
    ) -> _Point:
        inverse = Geodesic.WGS84.Inverse(
            origin_latitude_deg,
            origin_longitude_deg,
            latitude_deg,
            longitude_deg,
        )
        distance_m = float(inverse["s12"])
        azimuth_rad = math.radians(float(inverse["azi1"]))
        return _Point(
            x=distance_m * math.sin(azimuth_rad),
            y=distance_m * math.cos(azimuth_rad),
        )

    @staticmethod
    def _nearest_projection(
        point: _Point,
        reference_points: tuple[_Point, ...],
        reference_path_m: tuple[float, ...],
    ) -> _Projection:
        best: _Projection | None = None

        for index, (start, end) in enumerate(
            zip(reference_points, reference_points[1:], strict=False)
        ):
            dx = end.x - start.x
            dy = end.y - start.y
            squared_length = dx * dx + dy * dy
            if squared_length == 0.0:
                continue

            wx = point.x - start.x
            wy = point.y - start.y
            raw_fraction = (wx * dx + wy * dy) / squared_length
            fraction = min(1.0, max(0.0, raw_fraction))
            projected_x = start.x + fraction * dx
            projected_y = start.y + fraction * dy
            lateral = math.hypot(point.x - projected_x, point.y - projected_y)
            raw_distance = reference_path_m[index] + fraction * (
                reference_path_m[index + 1] - reference_path_m[index]
            )

            projection = _Projection(
                segment_index=index,
                fraction=fraction,
                lateral_error_m=lateral,
                raw_distance_m=raw_distance,
            )
            if best is None or lateral < best.lateral_error_m:
                best = projection

        if best is None:
            raise ValueError("Reference geometry has no usable non-zero segment.")

        return best

    @staticmethod
    def _unwrap(
        raw_distance_m: tuple[float, ...],
        reference_length_m: float,
    ) -> tuple[float, ...]:
        half = reference_length_m / 2.0
        turn = -1 if raw_distance_m[0] > half else 0
        result = [raw_distance_m[0] + turn * reference_length_m]

        for previous_raw, current_raw in zip(
            raw_distance_m,
            raw_distance_m[1:],
            strict=False,
        ):
            delta_raw = current_raw - previous_raw
            if delta_raw < -half:
                turn += 1
            elif delta_raw > half:
                turn -= 1
            result.append(current_raw + turn * reference_length_m)

        return tuple(result)

    @staticmethod
    def _has_material_self_intersection(points: tuple[_Point, ...]) -> bool:
        segment_count = len(points) - 1
        for first_index in range(segment_count):
            a = points[first_index]
            b = points[first_index + 1]
            if CommonTrackReferenceEngine._same_point(a, b):
                continue

            for second_index in range(first_index + 2, segment_count):
                c = points[second_index]
                d = points[second_index + 1]
                if CommonTrackReferenceEngine._same_point(c, d):
                    continue

                if (
                    first_index == 0
                    and second_index == segment_count - 1
                    and CommonTrackReferenceEngine._segments_share_endpoint(a, b, c, d)
                ):
                    continue

                if CommonTrackReferenceEngine._proper_intersection(a, b, c, d):
                    return True

        return False

    @staticmethod
    def _proper_intersection(a: _Point, b: _Point, c: _Point, d: _Point) -> bool:
        first = CommonTrackReferenceEngine._orientation(a, b, c)
        second = CommonTrackReferenceEngine._orientation(a, b, d)
        third = CommonTrackReferenceEngine._orientation(c, d, a)
        fourth = CommonTrackReferenceEngine._orientation(c, d, b)

        return first * second < 0.0 and third * fourth < 0.0

    @staticmethod
    def _orientation(a: _Point, b: _Point, c: _Point) -> float:
        return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

    @staticmethod
    def _segments_share_endpoint(a: _Point, b: _Point, c: _Point, d: _Point) -> bool:
        return any(
            CommonTrackReferenceEngine._same_point(first, second)
            for first in (a, b)
            for second in (c, d)
        )

    @staticmethod
    def _same_point(first: _Point, second: _Point) -> bool:
        tolerance_m = 1e-9
        return (
            abs(first.x - second.x) <= tolerance_m
            and abs(first.y - second.y) <= tolerance_m
        )

    @staticmethod
    def _strictly_increasing(values: tuple[float, ...]) -> bool:
        return all(
            current > previous
            for previous, current in zip(values, values[1:], strict=False)
        )

    @staticmethod
    def _non_decreasing(values: tuple[float, ...]) -> bool:
        return all(
            current >= previous
            for previous, current in zip(values, values[1:], strict=False)
        )

    @staticmethod
    def _percentile_95(values: tuple[float, ...]) -> float:
        ordered = sorted(values)
        if len(ordered) == 1:
            return ordered[0]

        position = 0.95 * (len(ordered) - 1)
        lower = math.floor(position)
        upper = math.ceil(position)
        if lower == upper:
            return ordered[lower]

        fraction = position - lower
        return ordered[lower] + fraction * (ordered[upper] - ordered[lower])
