from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from ome.domain import CanonicalConcept, freeze_metadata


def _empty_parameters() -> Mapping[str, object]:
    return freeze_metadata({})


@dataclass(frozen=True, slots=True)
class TransformationEvidence:
    transformation_id: str
    transformation_version: str
    parameters: Mapping[str, object] = field(default_factory=_empty_parameters)

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", freeze_metadata(self.parameters))


@dataclass(frozen=True, slots=True)
class SourceSeriesEvidence:
    dataset_fingerprint: str
    source_channel_identifier: str
    source_original_name: str
    unit: str
    transformations: tuple[TransformationEvidence, ...] = ()


@dataclass(frozen=True, slots=True)
class GPSPathDistanceProvenance:
    dataset_fingerprint: str
    algorithm_id: str
    algorithm_version: str
    ellipsoid: str
    altitude_policy: str
    latitude: SourceSeriesEvidence
    longitude: SourceSeriesEvidence
    elapsed_time: SourceSeriesEvidence


@dataclass(frozen=True, slots=True)
class CommonTrackReferenceProvenance:
    algorithm_id: str
    algorithm_version: str
    reference_dataset_fingerprint: str
    candidate_dataset_fingerprint: str
    reference_context: LapEvidenceContext
    candidate_context: LapEvidenceContext
    reference_latitude: SourceSeriesEvidence
    reference_longitude: SourceSeriesEvidence
    reference_elapsed_time: SourceSeriesEvidence
    candidate_latitude: SourceSeriesEvidence
    candidate_longitude: SourceSeriesEvidence
    candidate_elapsed_time: SourceSeriesEvidence
    reference_gps_path: GPSPathDistanceProvenance
    origin_latitude_deg: float
    origin_longitude_deg: float
    reference_length_m: float


@dataclass(frozen=True, slots=True)
class CanonicalSeriesEvidence:
    dataset_fingerprint: str
    source_channel_identifier: str
    source_original_name: str
    canonical_concept: CanonicalConcept
    unit: str
    transformations: tuple[TransformationEvidence, ...] = ()
    semantic_id: str | None = None


@dataclass(frozen=True, slots=True)
class LapEvidenceContext:
    dataset_fingerprint: str
    session_identifier: str
    run_identifier: str | None
    lap_identifier: str


@dataclass(frozen=True, slots=True)
class LapComparisonEvidence:
    context: LapEvidenceContext
    distance: CanonicalSeriesEvidence
    elapsed_time: CanonicalSeriesEvidence


@dataclass(frozen=True, slots=True)
class ComparisonProvenance:
    algorithm_id: str
    algorithm_version: str
    parameters: Mapping[str, object]
    reference_concept: CanonicalConcept
    reference_unit: str
    time_concept: CanonicalConcept
    time_unit: str
    common_start_m: float
    common_end_m: float
    lap_a: LapComparisonEvidence
    lap_b: LapComparisonEvidence

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", freeze_metadata(self.parameters))


@dataclass(frozen=True, slots=True)
class ContinuousOverlayProvenance:
    algorithm_id: str
    algorithm_version: str
    parameters: Mapping[str, object]
    base_comparison: ComparisonProvenance
    lap_a_channel: CanonicalSeriesEvidence
    lap_b_channel: CanonicalSeriesEvidence

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", freeze_metadata(self.parameters))


@dataclass(frozen=True, slots=True)
class GearOverlayProvenance:
    algorithm_id: str
    algorithm_version: str
    parameters: Mapping[str, object]
    base_comparison: ComparisonProvenance
    lap_a_gear: CanonicalSeriesEvidence
    lap_b_gear: CanonicalSeriesEvidence

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", freeze_metadata(self.parameters))


@dataclass(frozen=True, slots=True)
class DeltaObservationProvenance:
    algorithm_id: str
    algorithm_version: str
    parameters: Mapping[str, object]
    base_comparison: ComparisonProvenance

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", freeze_metadata(self.parameters))


@dataclass(frozen=True, slots=True)
class ComparisonReportProvenance:
    assembler_id: str
    assembler_version: str
    requested_concepts: tuple[CanonicalConcept, ...]
    base_comparison: ComparisonProvenance
    delta_observation: DeltaObservationProvenance
    continuous_overlays: tuple[ContinuousOverlayProvenance, ...]
    gear_overlay: GearOverlayProvenance | None
