from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from geographiclib.geodesic import Geodesic

from ome.evidence import GPSPathDistanceProvenance, SourceSeriesEvidence

ALGORITHM_ID = "ome.gps-path-distance.wgs84-geodesic"
ALGORITHM_VERSION = "0.1.0"
ELLIPSOID = "WGS84"
ALTITUDE_POLICY = "ignored-for-horizontal-distance"


class GPSPathDistanceIssueCode(StrEnum):
    LENGTH_MISMATCH = "length_mismatch"
    INSUFFICIENT_SAMPLES = "insufficient_samples"
    NON_FINITE_COORDINATE = "non_finite_coordinate"
    INVALID_LATITUDE = "invalid_latitude"
    INVALID_LONGITUDE = "invalid_longitude"
    NON_FINITE_TIME = "non_finite_time"
    TIME_NOT_STRICTLY_INCREASING = "time_not_strictly_increasing"
    INCOMPATIBLE_UNITS = "incompatible_units"
    MISSING_PROVENANCE = "missing_provenance"


@dataclass(frozen=True, slots=True)
class GPSPathDistanceReadinessIssue:
    code: GPSPathDistanceIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class GPSPathDistanceRequest:
    dataset_fingerprint: str
    timestamps_s: tuple[float, ...]
    latitudes_deg: tuple[float, ...]
    longitudes_deg: tuple[float, ...]
    latitude_evidence: SourceSeriesEvidence
    longitude_evidence: SourceSeriesEvidence
    time_evidence: SourceSeriesEvidence


@dataclass(frozen=True, slots=True)
class GPSPathDistanceNotReady:
    issues: tuple[GPSPathDistanceReadinessIssue, ...]


@dataclass(frozen=True, slots=True)
class GPSPathDistanceSuccess:
    derived_concept: str
    unit: str
    algorithm_id: str
    algorithm_version: str
    ellipsoid: str
    altitude_policy: str
    timestamps_s: tuple[float, ...]
    segment_distance_m: tuple[float, ...]
    path_distance_m: tuple[float, ...]
    total_distance_m: float
    provenance: GPSPathDistanceProvenance


GPSPathDistanceOutcome = GPSPathDistanceSuccess | GPSPathDistanceNotReady


class GPSPathDistanceEngine:
    algorithm_id = ALGORITHM_ID
    algorithm_version = ALGORITHM_VERSION

    def derive(self, request: GPSPathDistanceRequest) -> GPSPathDistanceOutcome:
        issues = self._readiness_issues(request)
        if issues:
            return GPSPathDistanceNotReady(issues=issues)

        segment_distance_m = [0.0]
        path_distance_m = [0.0]

        for index in range(1, len(request.timestamps_s)):
            result = Geodesic.WGS84.Inverse(
                request.latitudes_deg[index - 1],
                request.longitudes_deg[index - 1],
                request.latitudes_deg[index],
                request.longitudes_deg[index],
            )
            segment_m = float(result["s12"])
            segment_distance_m.append(segment_m)
            path_distance_m.append(path_distance_m[-1] + segment_m)

        provenance = GPSPathDistanceProvenance(
            dataset_fingerprint=request.dataset_fingerprint,
            algorithm_id=self.algorithm_id,
            algorithm_version=self.algorithm_version,
            ellipsoid=ELLIPSOID,
            altitude_policy=ALTITUDE_POLICY,
            latitude=request.latitude_evidence,
            longitude=request.longitude_evidence,
            elapsed_time=request.time_evidence,
        )

        return GPSPathDistanceSuccess(
            derived_concept="gps.path_distance",
            unit="m",
            algorithm_id=self.algorithm_id,
            algorithm_version=self.algorithm_version,
            ellipsoid=ELLIPSOID,
            altitude_policy=ALTITUDE_POLICY,
            timestamps_s=request.timestamps_s,
            segment_distance_m=tuple(segment_distance_m),
            path_distance_m=tuple(path_distance_m),
            total_distance_m=path_distance_m[-1],
            provenance=provenance,
        )

    @staticmethod
    def _readiness_issues(
        request: GPSPathDistanceRequest,
    ) -> tuple[GPSPathDistanceReadinessIssue, ...]:
        issues: list[GPSPathDistanceReadinessIssue] = []

        lengths = (
            len(request.timestamps_s),
            len(request.latitudes_deg),
            len(request.longitudes_deg),
        )
        if len(set(lengths)) != 1:
            issues.append(
                GPSPathDistanceReadinessIssue(
                    code=GPSPathDistanceIssueCode.LENGTH_MISMATCH,
                    message="GPS time, latitude and longitude series must have matching lengths.",
                )
            )
            return tuple(issues)

        if lengths[0] < 2:
            issues.append(
                GPSPathDistanceReadinessIssue(
                    code=GPSPathDistanceIssueCode.INSUFFICIENT_SAMPLES,
                    message="GPS path distance requires at least two paired source samples.",
                )
            )

        issues.extend(GPSPathDistanceEngine._provenance_issues(request))
        issues.extend(GPSPathDistanceEngine._unit_issues(request))

        if any(not math.isfinite(value) for value in request.timestamps_s):
            issues.append(
                GPSPathDistanceReadinessIssue(
                    code=GPSPathDistanceIssueCode.NON_FINITE_TIME,
                    message="GPS source timestamps must be finite.",
                )
            )
        elif len(request.timestamps_s) >= 2 and not all(
            current > previous
            for previous, current in zip(
                request.timestamps_s,
                request.timestamps_s[1:],
                strict=False,
            )
        ):
            issues.append(
                GPSPathDistanceReadinessIssue(
                    code=GPSPathDistanceIssueCode.TIME_NOT_STRICTLY_INCREASING,
                    message="GPS source timestamps must be strictly increasing.",
                )
            )

        coordinates = (*request.latitudes_deg, *request.longitudes_deg)
        if any(not math.isfinite(value) for value in coordinates):
            issues.append(
                GPSPathDistanceReadinessIssue(
                    code=GPSPathDistanceIssueCode.NON_FINITE_COORDINATE,
                    message="GPS latitude and longitude values must be finite.",
                )
            )
            return tuple(issues)

        if any(latitude < -90.0 or latitude > 90.0 for latitude in request.latitudes_deg):
            issues.append(
                GPSPathDistanceReadinessIssue(
                    code=GPSPathDistanceIssueCode.INVALID_LATITUDE,
                    message="GPS latitude must be within [-90, 90] degrees.",
                )
            )

        if any(longitude < -180.0 or longitude > 180.0 for longitude in request.longitudes_deg):
            issues.append(
                GPSPathDistanceReadinessIssue(
                    code=GPSPathDistanceIssueCode.INVALID_LONGITUDE,
                    message="GPS longitude must be within [-180, 180] degrees.",
                )
            )

        return tuple(issues)

    @staticmethod
    def _unit_issues(
        request: GPSPathDistanceRequest,
    ) -> tuple[GPSPathDistanceReadinessIssue, ...]:
        if (
            request.latitude_evidence.unit == "deg"
            and request.longitude_evidence.unit == "deg"
            and request.time_evidence.unit == "s"
        ):
            return ()

        return (
            GPSPathDistanceReadinessIssue(
                code=GPSPathDistanceIssueCode.INCOMPATIBLE_UNITS,
                message=(
                    "GPS path distance requires latitude/longitude in degrees "
                    "and time in seconds."
                ),
            ),
        )

    @staticmethod
    def _provenance_issues(
        request: GPSPathDistanceRequest,
    ) -> tuple[GPSPathDistanceReadinessIssue, ...]:
        if not request.dataset_fingerprint.strip():
            return (
                GPSPathDistanceReadinessIssue(
                    code=GPSPathDistanceIssueCode.MISSING_PROVENANCE,
                    message="GPS path distance requires a source dataset fingerprint.",
                ),
            )

        evidence_items = (
            request.latitude_evidence,
            request.longitude_evidence,
            request.time_evidence,
        )
        for evidence in evidence_items:
            if evidence.dataset_fingerprint != request.dataset_fingerprint:
                return (
                    GPSPathDistanceReadinessIssue(
                        code=GPSPathDistanceIssueCode.MISSING_PROVENANCE,
                        message="GPS source evidence must reference the same source dataset.",
                    ),
                )
            if (
                not evidence.source_channel_identifier.strip()
                or not evidence.source_original_name.strip()
            ):
                return (
                    GPSPathDistanceReadinessIssue(
                        code=GPSPathDistanceIssueCode.MISSING_PROVENANCE,
                        message="GPS source evidence must identify the original source channel.",
                    ),
                )

        return ()
