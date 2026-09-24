from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ome.analysis import (
    CommonTrackReferenceEngine,
    CommonTrackReferenceRequest,
    CommonTrackReferenceSuccess,
    GPSPathDistanceEngine,
    GPSPathDistanceRequest,
    GPSPathDistanceSuccess,
    LapComparisonSeries,
    TrackReferenceLap,
)
from ome.application.lap_window import SourceLapWindow
from ome.application.track_reference_preparation import prepare_track_reference_lap_distance
from ome.domain import CanonicalConcept, ImportedTelemetryDataset, SourceChannel, SourceValue
from ome.evidence import (
    CanonicalSeriesEvidence,
    LapEvidenceContext,
    SourceSeriesEvidence,
    TransformationEvidence,
)

TRAQMATE_SOURCE_TYPE = "traqmate-trackvision-csv"
REFERENCE_MAPPING_ID = "ome.preparation.explicit-reference-path-to-lap-distance"
REFERENCE_MAPPING_VERSION = "0.1.0"
DERIVED_GPS_PATH_IDENTIFIER = "derived:gps.path_distance"
DERIVED_GPS_PATH_NAME = "gps.path_distance"

_TIME_CHANNEL = "Elapsed Time"
_LATITUDE_CHANNEL = "Lat (Degrees)"
_LONGITUDE_CHANNEL = "Lon (Degrees)"


class PhysicalTrackReferencePreparationIssueCode(StrEnum):
    UNSUPPORTED_SOURCE_TYPE = "unsupported_source_type"
    WINDOW_DATASET_MISMATCH = "window_dataset_mismatch"
    CONTEXT_DATASET_MISMATCH = "context_dataset_mismatch"
    SAME_LAP_WINDOW = "same_lap_window"
    MISSING_SOURCE_CHANNEL = "missing_source_channel"
    INVALID_WINDOW = "invalid_window"
    INVALID_SOURCE_EVIDENCE = "invalid_source_evidence"
    GPS_PATH_NOT_READY = "gps_path_not_ready"
    TRACK_REFERENCE_NOT_READY = "track_reference_not_ready"


@dataclass(frozen=True, slots=True)
class PhysicalTrackReferencePreparationIssue:
    code: PhysicalTrackReferencePreparationIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class PhysicalTrackReferencePreparationRequest:
    dataset: ImportedTelemetryDataset
    reference_window: SourceLapWindow
    candidate_window: SourceLapWindow
    reference_context: LapEvidenceContext
    candidate_context: LapEvidenceContext


@dataclass(frozen=True, slots=True)
class PhysicalTrackReferencePreparation:
    dataset_fingerprint: str
    reference_window: SourceLapWindow
    candidate_window: SourceLapWindow
    reference_context: LapEvidenceContext
    candidate_context: LapEvidenceContext
    reference_lap: TrackReferenceLap
    candidate_lap: TrackReferenceLap
    reference_gps_path: GPSPathDistanceSuccess
    candidate_projection: CommonTrackReferenceSuccess
    reference_lap_distance: LapComparisonSeries
    candidate_lap_distance: LapComparisonSeries


@dataclass(frozen=True, slots=True)
class PhysicalTrackReferencePreparationSuccess:
    preparation: PhysicalTrackReferencePreparation


@dataclass(frozen=True, slots=True)
class PhysicalTrackReferencePreparationNotReady:
    issues: tuple[PhysicalTrackReferencePreparationIssue, ...]


PhysicalTrackReferencePreparationOutcome = (
    PhysicalTrackReferencePreparationSuccess | PhysicalTrackReferencePreparationNotReady
)


@dataclass(frozen=True, slots=True)
class _PreparedTrajectory:
    timestamps_s: tuple[float, ...]
    latitudes_deg: tuple[float, ...]
    longitudes_deg: tuple[float, ...]
    latitude_evidence: SourceSeriesEvidence
    longitude_evidence: SourceSeriesEvidence
    time_evidence: SourceSeriesEvidence


class PhysicalTrackReferencePreparationService:
    """Prepare explicit physical source laps onto one common canonical track reference."""

    def prepare(
        self,
        request: PhysicalTrackReferencePreparationRequest,
    ) -> PhysicalTrackReferencePreparationOutcome:
        issue = self._request_issue(request)
        if issue is not None:
            return PhysicalTrackReferencePreparationNotReady(issues=(issue,))

        channels = self._required_channels(request.dataset)
        if isinstance(channels, PhysicalTrackReferencePreparationIssue):
            return PhysicalTrackReferencePreparationNotReady(issues=(channels,))
        time_channel, latitude_channel, longitude_channel = channels

        reference = self._trajectory(
            request.dataset,
            request.reference_window,
            time_channel,
            latitude_channel,
            longitude_channel,
        )
        if isinstance(reference, PhysicalTrackReferencePreparationIssue):
            return PhysicalTrackReferencePreparationNotReady(issues=(reference,))

        candidate = self._trajectory(
            request.dataset,
            request.candidate_window,
            time_channel,
            latitude_channel,
            longitude_channel,
        )
        if isinstance(candidate, PhysicalTrackReferencePreparationIssue):
            return PhysicalTrackReferencePreparationNotReady(issues=(candidate,))

        reference_path_outcome = GPSPathDistanceEngine().derive(
            GPSPathDistanceRequest(
                dataset_fingerprint=request.dataset.provenance.content_fingerprint,
                timestamps_s=reference.timestamps_s,
                latitudes_deg=reference.latitudes_deg,
                longitudes_deg=reference.longitudes_deg,
                latitude_evidence=reference.latitude_evidence,
                longitude_evidence=reference.longitude_evidence,
                time_evidence=reference.time_evidence,
            )
        )
        if not isinstance(reference_path_outcome, GPSPathDistanceSuccess):
            codes = ", ".join(issue.code.value for issue in reference_path_outcome.issues)
            return self._not_ready(
                PhysicalTrackReferencePreparationIssueCode.GPS_PATH_NOT_READY,
                f"Reference GPS path distance is not ready: {codes}.",
            )
        reference_path = reference_path_outcome

        reference_lap = TrackReferenceLap(
            context=request.reference_context,
            timestamps_s=reference.timestamps_s,
            latitudes_deg=reference.latitudes_deg,
            longitudes_deg=reference.longitudes_deg,
            latitude_evidence=reference.latitude_evidence,
            longitude_evidence=reference.longitude_evidence,
            time_evidence=reference.time_evidence,
            gps_path_distance=reference_path,
            is_closed=True,
        )
        candidate_lap = TrackReferenceLap(
            context=request.candidate_context,
            timestamps_s=candidate.timestamps_s,
            latitudes_deg=candidate.latitudes_deg,
            longitudes_deg=candidate.longitudes_deg,
            latitude_evidence=candidate.latitude_evidence,
            longitude_evidence=candidate.longitude_evidence,
            time_evidence=candidate.time_evidence,
            gps_path_distance=None,
            is_closed=True,
        )

        projection_outcome = CommonTrackReferenceEngine().project(
            CommonTrackReferenceRequest(
                reference=reference_lap,
                candidate=candidate_lap,
            )
        )
        if not isinstance(projection_outcome, CommonTrackReferenceSuccess):
            codes = ", ".join(issue.code.value for issue in projection_outcome.issues)
            return self._not_ready(
                PhysicalTrackReferencePreparationIssueCode.TRACK_REFERENCE_NOT_READY,
                f"Candidate common-track reference is not ready: {codes}.",
            )
        projection = projection_outcome

        reference_lap_distance = self._reference_lap_distance(
            reference_path,
            request.reference_context,
        )
        candidate_lap_distance = prepare_track_reference_lap_distance(projection)

        return PhysicalTrackReferencePreparationSuccess(
            preparation=PhysicalTrackReferencePreparation(
                dataset_fingerprint=request.dataset.provenance.content_fingerprint,
                reference_window=request.reference_window,
                candidate_window=request.candidate_window,
                reference_context=request.reference_context,
                candidate_context=request.candidate_context,
                reference_lap=reference_lap,
                candidate_lap=candidate_lap,
                reference_gps_path=reference_path,
                candidate_projection=projection,
                reference_lap_distance=reference_lap_distance,
                candidate_lap_distance=candidate_lap_distance,
            )
        )

    @staticmethod
    def _request_issue(
        request: PhysicalTrackReferencePreparationRequest,
    ) -> PhysicalTrackReferencePreparationIssue | None:
        dataset = request.dataset
        fingerprint = dataset.provenance.content_fingerprint

        if dataset.source.source_type != TRAQMATE_SOURCE_TYPE:
            return PhysicalTrackReferencePreparationIssue(
                code=PhysicalTrackReferencePreparationIssueCode.UNSUPPORTED_SOURCE_TYPE,
                message="Physical track-reference preparation supports Traqmate Trackvision data.",
            )

        if (
            request.reference_window.dataset_fingerprint != fingerprint
            or request.candidate_window.dataset_fingerprint != fingerprint
        ):
            return PhysicalTrackReferencePreparationIssue(
                code=PhysicalTrackReferencePreparationIssueCode.WINDOW_DATASET_MISMATCH,
                message="Selected source lap windows must reference the supplied dataset.",
            )

        if (
            request.reference_context.dataset_fingerprint != fingerprint
            or request.candidate_context.dataset_fingerprint != fingerprint
        ):
            return PhysicalTrackReferencePreparationIssue(
                code=PhysicalTrackReferencePreparationIssueCode.CONTEXT_DATASET_MISMATCH,
                message="Reference and candidate context must reference the supplied dataset.",
            )

        if request.reference_window.source_lap_number == request.candidate_window.source_lap_number:
            return PhysicalTrackReferencePreparationIssue(
                code=PhysicalTrackReferencePreparationIssueCode.SAME_LAP_WINDOW,
                message="Reference and candidate must be different explicit source laps.",
            )

        for window in (request.reference_window, request.candidate_window):
            if (
                window.start_index < 0
                or window.end_index_exclusive <= window.start_index
                or window.closing_boundary_index != window.end_index_exclusive
                or window.sample_count != window.end_index_exclusive - window.start_index
            ):
                return PhysicalTrackReferencePreparationIssue(
                    code=PhysicalTrackReferencePreparationIssueCode.INVALID_WINDOW,
                    message=(
                        "Source lap window indexes are inconsistent with the accepted contract."
                    ),
                )

        return None

    @staticmethod
    def _required_channels(
        dataset: ImportedTelemetryDataset,
    ) -> (
        tuple[SourceChannel, SourceChannel, SourceChannel] | PhysicalTrackReferencePreparationIssue
    ):
        channels: list[SourceChannel] = []
        for identifier in (_TIME_CHANNEL, _LATITUDE_CHANNEL, _LONGITUDE_CHANNEL):
            try:
                channels.append(dataset.channel(identifier))
            except KeyError:
                return PhysicalTrackReferencePreparationIssue(
                    code=PhysicalTrackReferencePreparationIssueCode.MISSING_SOURCE_CHANNEL,
                    message=f"Required physical source channel {identifier!r} is missing.",
                )
        return channels[0], channels[1], channels[2]

    @classmethod
    def _trajectory(
        cls,
        dataset: ImportedTelemetryDataset,
        window: SourceLapWindow,
        time_channel: SourceChannel,
        latitude_channel: SourceChannel,
        longitude_channel: SourceChannel,
    ) -> _PreparedTrajectory | PhysicalTrackReferencePreparationIssue:
        lengths = {
            len(time_channel.series.values),
            len(latitude_channel.series.values),
            len(longitude_channel.series.values),
        }
        if len(lengths) != 1:
            return PhysicalTrackReferencePreparationIssue(
                code=PhysicalTrackReferencePreparationIssueCode.INVALID_SOURCE_EVIDENCE,
                message="Physical time/latitude/longitude source series lengths are inconsistent.",
            )

        source_length = len(time_channel.series.values)
        if window.closing_boundary_index >= source_length:
            return PhysicalTrackReferencePreparationIssue(
                code=PhysicalTrackReferencePreparationIssueCode.INVALID_WINDOW,
                message="Source lap closing boundary lies outside the source evidence.",
            )

        indexes = tuple(range(window.start_index, window.end_index_exclusive)) + (
            window.closing_boundary_index,
        )

        timestamps = cls._numbers_at(time_channel, indexes)
        latitudes = cls._numbers_at(latitude_channel, indexes)
        longitudes = cls._numbers_at(longitude_channel, indexes)
        if timestamps is None or latitudes is None or longitudes is None:
            return PhysicalTrackReferencePreparationIssue(
                code=PhysicalTrackReferencePreparationIssueCode.INVALID_SOURCE_EVIDENCE,
                message="Selected physical GPS/time evidence must be finite numeric source data.",
            )

        fingerprint = dataset.provenance.content_fingerprint
        return _PreparedTrajectory(
            timestamps_s=timestamps,
            latitudes_deg=latitudes,
            longitudes_deg=longitudes,
            latitude_evidence=cls._source_evidence(fingerprint, latitude_channel),
            longitude_evidence=cls._source_evidence(fingerprint, longitude_channel),
            time_evidence=cls._source_evidence(fingerprint, time_channel),
        )

    @staticmethod
    def _numbers_at(
        channel: SourceChannel,
        indexes: tuple[int, ...],
    ) -> tuple[float, ...] | None:
        values: list[float] = []
        for index in indexes:
            value = channel.series.values[index]
            number = PhysicalTrackReferencePreparationService._number(value)
            if number is None:
                return None
            values.append(number)
        return tuple(values)

    @staticmethod
    def _number(value: SourceValue) -> float | None:
        if value is None or isinstance(value, (bool, tuple)):
            return None
        if isinstance(value, (int, float)):
            number = float(value)
        elif isinstance(value, str):
            try:
                number = float(value.strip())
            except ValueError:
                return None
        else:
            return None
        return number if math.isfinite(number) else None

    @staticmethod
    def _source_evidence(
        fingerprint: str,
        channel: SourceChannel,
    ) -> SourceSeriesEvidence:
        return SourceSeriesEvidence(
            dataset_fingerprint=fingerprint,
            source_channel_identifier=channel.identifier,
            source_original_name=channel.original_name,
            unit=channel.metadata.unit or "",
        )

    @staticmethod
    def _reference_lap_distance(
        path: GPSPathDistanceSuccess,
        context: LapEvidenceContext,
    ) -> LapComparisonSeries:
        gps_transformation = TransformationEvidence(
            transformation_id=path.algorithm_id,
            transformation_version=path.algorithm_version,
            parameters={
                "ellipsoid": path.ellipsoid,
                "altitude_policy": path.altitude_policy,
                "latitude_channel": path.provenance.latitude.source_channel_identifier,
                "longitude_channel": path.provenance.longitude.source_channel_identifier,
                "time_channel": path.provenance.elapsed_time.source_channel_identifier,
            },
        )
        reference_mapping = TransformationEvidence(
            transformation_id=REFERENCE_MAPPING_ID,
            transformation_version=REFERENCE_MAPPING_VERSION,
            parameters={
                "source_concept": path.derived_concept,
                "target_concept": CanonicalConcept.LAP_DISTANCE.value,
                "reference_session_identifier": context.session_identifier,
                "reference_run_identifier": context.run_identifier,
                "reference_lap_identifier": context.lap_identifier,
            },
        )
        evidence = CanonicalSeriesEvidence(
            dataset_fingerprint=path.provenance.dataset_fingerprint,
            source_channel_identifier=DERIVED_GPS_PATH_IDENTIFIER,
            source_original_name=DERIVED_GPS_PATH_NAME,
            canonical_concept=CanonicalConcept.LAP_DISTANCE,
            unit="m",
            transformations=(gps_transformation, reference_mapping),
        )
        return LapComparisonSeries(
            values=path.path_distance_m,
            evidence=evidence,
        )

    @staticmethod
    def _not_ready(
        code: PhysicalTrackReferencePreparationIssueCode,
        message: str,
    ) -> PhysicalTrackReferencePreparationNotReady:
        return PhysicalTrackReferencePreparationNotReady(
            issues=(PhysicalTrackReferencePreparationIssue(code=code, message=message),)
        )
