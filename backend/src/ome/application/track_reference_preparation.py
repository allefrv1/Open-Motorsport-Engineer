from __future__ import annotations

from ome.analysis import CommonTrackReferenceSuccess, LapComparisonSeries
from ome.domain import CanonicalConcept
from ome.evidence import CanonicalSeriesEvidence, TransformationEvidence

MAPPING_ID = "ome.preparation.track-reference-to-lap-distance"
MAPPING_VERSION = "0.1.0"
DERIVED_SOURCE_IDENTIFIER = "derived:track.reference_distance"
DERIVED_SOURCE_NAME = "track.reference_distance"


def prepare_track_reference_lap_distance(
    result: CommonTrackReferenceSuccess,
) -> LapComparisonSeries:
    provenance = result.provenance

    projection = TransformationEvidence(
        transformation_id=result.algorithm_id,
        transformation_version=result.algorithm_version,
        parameters={
            "reference_dataset_fingerprint": provenance.reference_dataset_fingerprint,
            "candidate_dataset_fingerprint": provenance.candidate_dataset_fingerprint,
            "reference_session_identifier": provenance.reference_context.session_identifier,
            "reference_run_identifier": provenance.reference_context.run_identifier,
            "reference_lap_identifier": provenance.reference_context.lap_identifier,
            "candidate_session_identifier": provenance.candidate_context.session_identifier,
            "candidate_run_identifier": provenance.candidate_context.run_identifier,
            "candidate_lap_identifier": provenance.candidate_context.lap_identifier,
            "reference_latitude_channel": (
                provenance.reference_latitude.source_channel_identifier
            ),
            "reference_longitude_channel": (
                provenance.reference_longitude.source_channel_identifier
            ),
            "reference_time_channel": (
                provenance.reference_elapsed_time.source_channel_identifier
            ),
            "candidate_latitude_channel": (
                provenance.candidate_latitude.source_channel_identifier
            ),
            "candidate_longitude_channel": (
                provenance.candidate_longitude.source_channel_identifier
            ),
            "candidate_time_channel": (
                provenance.candidate_elapsed_time.source_channel_identifier
            ),
            "reference_gps_path_algorithm_id": provenance.reference_gps_path.algorithm_id,
            "reference_gps_path_algorithm_version": (
                provenance.reference_gps_path.algorithm_version
            ),
            "origin_latitude_deg": provenance.origin_latitude_deg,
            "origin_longitude_deg": provenance.origin_longitude_deg,
            "reference_length_m": provenance.reference_length_m,
        },
    )
    mapping = TransformationEvidence(
        transformation_id=MAPPING_ID,
        transformation_version=MAPPING_VERSION,
        parameters={
            "source_concept": result.derived_concept,
            "target_concept": CanonicalConcept.LAP_DISTANCE.value,
        },
    )

    evidence = CanonicalSeriesEvidence(
        dataset_fingerprint=provenance.candidate_dataset_fingerprint,
        source_channel_identifier=DERIVED_SOURCE_IDENTIFIER,
        source_original_name=DERIVED_SOURCE_NAME,
        canonical_concept=CanonicalConcept.LAP_DISTANCE,
        unit="m",
        transformations=(projection, mapping),
    )
    return LapComparisonSeries(
        values=result.reference_distance_m,
        evidence=evidence,
    )
