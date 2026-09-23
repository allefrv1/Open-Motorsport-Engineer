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
class CanonicalSeriesEvidence:
    dataset_fingerprint: str
    source_channel_identifier: str
    source_original_name: str
    canonical_concept: CanonicalConcept
    unit: str
    transformations: tuple[TransformationEvidence, ...] = ()


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
