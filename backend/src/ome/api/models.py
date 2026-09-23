from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict

from ome.analysis import (
    ComparisonReadinessIssue,
    ContinuousOverlaySeries,
    GearOverlaySeries,
    LapComparisonLap,
    LapComparisonNotReady,
    LapComparisonRequest,
    LapComparisonSeries,
)
from ome.application import (
    ComparisonReportNotReady,
    ComparisonReportRequest,
    ComparisonReportSuccess,
    ContinuousChannelPair,
    GearChannelPair,
)
from ome.domain import CanonicalConcept
from ome.evidence import (
    CanonicalSeriesEvidence,
    ComparisonProvenance,
    ComparisonReportProvenance,
    ContinuousOverlayProvenance,
    DeltaObservationProvenance,
    GearOverlayProvenance,
    LapComparisonEvidence,
    LapEvidenceContext,
    TransformationEvidence,
)


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TransformationEvidenceDto(ApiModel):
    transformation_id: str
    transformation_version: str
    parameters: dict[str, object] = {}

    def to_domain(self) -> TransformationEvidence:
        return TransformationEvidence(
            transformation_id=self.transformation_id,
            transformation_version=self.transformation_version,
            parameters=self.parameters,
        )

    @classmethod
    def from_domain(cls, value: TransformationEvidence) -> TransformationEvidenceDto:
        return cls(
            transformation_id=value.transformation_id,
            transformation_version=value.transformation_version,
            parameters=dict(value.parameters),
        )


class CanonicalSeriesEvidenceDto(ApiModel):
    dataset_fingerprint: str
    source_channel_identifier: str
    source_original_name: str
    canonical_concept: CanonicalConcept
    unit: str
    transformations: tuple[TransformationEvidenceDto, ...] = ()
    semantic_id: str | None = None

    def to_domain(self) -> CanonicalSeriesEvidence:
        return CanonicalSeriesEvidence(
            dataset_fingerprint=self.dataset_fingerprint,
            source_channel_identifier=self.source_channel_identifier,
            source_original_name=self.source_original_name,
            canonical_concept=self.canonical_concept,
            unit=self.unit,
            transformations=tuple(item.to_domain() for item in self.transformations),
            semantic_id=self.semantic_id,
        )

    @classmethod
    def from_domain(cls, value: CanonicalSeriesEvidence) -> CanonicalSeriesEvidenceDto:
        return cls(
            dataset_fingerprint=value.dataset_fingerprint,
            source_channel_identifier=value.source_channel_identifier,
            source_original_name=value.source_original_name,
            canonical_concept=value.canonical_concept,
            unit=value.unit,
            transformations=tuple(
                TransformationEvidenceDto.from_domain(item) for item in value.transformations
            ),
            semantic_id=value.semantic_id,
        )


class LapEvidenceContextDto(ApiModel):
    dataset_fingerprint: str
    session_identifier: str
    run_identifier: str | None
    lap_identifier: str

    def to_domain(self) -> LapEvidenceContext:
        return LapEvidenceContext(
            dataset_fingerprint=self.dataset_fingerprint,
            session_identifier=self.session_identifier,
            run_identifier=self.run_identifier,
            lap_identifier=self.lap_identifier,
        )

    @classmethod
    def from_domain(cls, value: LapEvidenceContext) -> LapEvidenceContextDto:
        return cls(
            dataset_fingerprint=value.dataset_fingerprint,
            session_identifier=value.session_identifier,
            run_identifier=value.run_identifier,
            lap_identifier=value.lap_identifier,
        )


class LapComparisonSeriesDto(ApiModel):
    values: tuple[float, ...]
    evidence: CanonicalSeriesEvidenceDto

    def to_domain(self) -> LapComparisonSeries:
        return LapComparisonSeries(
            values=self.values,
            evidence=self.evidence.to_domain(),
        )


class LapComparisonLapDto(ApiModel):
    context: LapEvidenceContextDto
    distance: LapComparisonSeriesDto | None
    elapsed_time: LapComparisonSeriesDto | None

    def to_domain(self) -> LapComparisonLap:
        return LapComparisonLap(
            context=self.context.to_domain(),
            distance=None if self.distance is None else self.distance.to_domain(),
            elapsed_time=(None if self.elapsed_time is None else self.elapsed_time.to_domain()),
        )


class LapComparisonRequestDto(ApiModel):
    lap_a: LapComparisonLapDto
    lap_b: LapComparisonLapDto
    grid_step_m: float = 1.0

    def to_domain(self) -> LapComparisonRequest:
        return LapComparisonRequest(
            lap_a=self.lap_a.to_domain(),
            lap_b=self.lap_b.to_domain(),
            grid_step_m=self.grid_step_m,
        )


class ContinuousOverlaySeriesDto(ApiModel):
    timestamps_s: tuple[float, ...]
    values: tuple[float, ...]
    evidence: CanonicalSeriesEvidenceDto

    def to_domain(self) -> ContinuousOverlaySeries:
        return ContinuousOverlaySeries(
            timestamps_s=self.timestamps_s,
            values=self.values,
            evidence=self.evidence.to_domain(),
        )


class ContinuousChannelPairDto(ApiModel):
    canonical_concept: CanonicalConcept
    lap_a_channel: ContinuousOverlaySeriesDto | None
    lap_b_channel: ContinuousOverlaySeriesDto | None

    def to_domain(self) -> ContinuousChannelPair:
        return ContinuousChannelPair(
            canonical_concept=self.canonical_concept,
            lap_a_channel=(None if self.lap_a_channel is None else self.lap_a_channel.to_domain()),
            lap_b_channel=(None if self.lap_b_channel is None else self.lap_b_channel.to_domain()),
        )


class GearOverlaySeriesDto(ApiModel):
    timestamps_s: tuple[float, ...]
    values: tuple[int | float | bool | str | None, ...]
    evidence: CanonicalSeriesEvidenceDto

    def to_domain(self) -> GearOverlaySeries:
        return GearOverlaySeries(
            timestamps_s=self.timestamps_s,
            values=self.values,
            evidence=self.evidence.to_domain(),
        )


class GearChannelPairDto(ApiModel):
    lap_a_gear: GearOverlaySeriesDto | None
    lap_b_gear: GearOverlaySeriesDto | None

    def to_domain(self) -> GearChannelPair:
        return GearChannelPair(
            lap_a_gear=None if self.lap_a_gear is None else self.lap_a_gear.to_domain(),
            lap_b_gear=None if self.lap_b_gear is None else self.lap_b_gear.to_domain(),
        )


class ComparisonReportRequestDto(ApiModel):
    comparison: LapComparisonRequestDto
    continuous_channels: tuple[ContinuousChannelPairDto, ...] = ()
    gear: GearChannelPairDto | None = None

    def to_domain(self) -> ComparisonReportRequest:
        return ComparisonReportRequest(
            comparison=self.comparison.to_domain(),
            continuous_channels=tuple(pair.to_domain() for pair in self.continuous_channels),
            gear=None if self.gear is None else self.gear.to_domain(),
        )


class ComparisonReadinessIssueDto(ApiModel):
    code: str
    message: str
    lap_side: str | None = None
    required_concept: CanonicalConcept | None = None

    @classmethod
    def from_domain(cls, value: ComparisonReadinessIssue) -> ComparisonReadinessIssueDto:
        return cls(
            code=value.code.value,
            message=value.message,
            lap_side=value.lap_side,
            required_concept=value.required_concept,
        )


class LapComparisonNotReadyDto(ApiModel):
    issues: tuple[ComparisonReadinessIssueDto, ...]

    @classmethod
    def from_domain(cls, value: LapComparisonNotReady) -> LapComparisonNotReadyDto:
        return cls(
            issues=tuple(ComparisonReadinessIssueDto.from_domain(issue) for issue in value.issues)
        )


class LapComparisonEvidenceDto(ApiModel):
    context: LapEvidenceContextDto
    distance: CanonicalSeriesEvidenceDto
    elapsed_time: CanonicalSeriesEvidenceDto

    @classmethod
    def from_domain(cls, value: LapComparisonEvidence) -> LapComparisonEvidenceDto:
        return cls(
            context=LapEvidenceContextDto.from_domain(value.context),
            distance=CanonicalSeriesEvidenceDto.from_domain(value.distance),
            elapsed_time=CanonicalSeriesEvidenceDto.from_domain(value.elapsed_time),
        )


class ComparisonProvenanceDto(ApiModel):
    algorithm_id: str
    algorithm_version: str
    parameters: dict[str, object]
    reference_concept: CanonicalConcept
    reference_unit: str
    time_concept: CanonicalConcept
    time_unit: str
    common_start_m: float
    common_end_m: float
    lap_a: LapComparisonEvidenceDto
    lap_b: LapComparisonEvidenceDto

    @classmethod
    def from_domain(cls, value: ComparisonProvenance) -> ComparisonProvenanceDto:
        return cls(
            algorithm_id=value.algorithm_id,
            algorithm_version=value.algorithm_version,
            parameters=dict(value.parameters),
            reference_concept=value.reference_concept,
            reference_unit=value.reference_unit,
            time_concept=value.time_concept,
            time_unit=value.time_unit,
            common_start_m=value.common_start_m,
            common_end_m=value.common_end_m,
            lap_a=LapComparisonEvidenceDto.from_domain(value.lap_a),
            lap_b=LapComparisonEvidenceDto.from_domain(value.lap_b),
        )


class LapComparisonSuccessDto(ApiModel):
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
    provenance: ComparisonProvenanceDto

    @classmethod
    def from_domain(cls, value: object) -> LapComparisonSuccessDto:
        from ome.analysis import LapComparisonSuccess

        assert isinstance(value, LapComparisonSuccess)
        return cls(
            reference_concept=value.reference_concept,
            reference_unit=value.reference_unit,
            time_concept=value.time_concept,
            time_unit=value.time_unit,
            common_start_m=value.common_start_m,
            common_end_m=value.common_end_m,
            distance_grid_m=value.distance_grid_m,
            lap_a_elapsed_s=value.lap_a_elapsed_s,
            lap_b_elapsed_s=value.lap_b_elapsed_s,
            delta_b_vs_a_s=value.delta_b_vs_a_s,
            provenance=ComparisonProvenanceDto.from_domain(value.provenance),
        )


class DeltaRegionDto(ApiModel):
    kind: str
    start_distance_m: float
    end_distance_m: float
    start_delta_s: float
    end_delta_s: float
    total_delta_change_s: float
    interval_count: int


class DeltaObservationProvenanceDto(ApiModel):
    algorithm_id: str
    algorithm_version: str
    parameters: dict[str, object]
    base_comparison: ComparisonProvenanceDto

    @classmethod
    def from_domain(
        cls,
        value: DeltaObservationProvenance,
    ) -> DeltaObservationProvenanceDto:
        return cls(
            algorithm_id=value.algorithm_id,
            algorithm_version=value.algorithm_version,
            parameters=dict(value.parameters),
            base_comparison=ComparisonProvenanceDto.from_domain(value.base_comparison),
        )


class DeltaObservationSuccessDto(ApiModel):
    regions: tuple[DeltaRegionDto, ...]
    provenance: DeltaObservationProvenanceDto

    @classmethod
    def from_domain(cls, value: object) -> DeltaObservationSuccessDto:
        from ome.analysis import DeltaObservationSuccess

        assert isinstance(value, DeltaObservationSuccess)
        return cls(
            regions=tuple(
                DeltaRegionDto(
                    kind=region.kind.value,
                    start_distance_m=region.start_distance_m,
                    end_distance_m=region.end_distance_m,
                    start_delta_s=region.start_delta_s,
                    end_delta_s=region.end_delta_s,
                    total_delta_change_s=region.total_delta_change_s,
                    interval_count=region.interval_count,
                )
                for region in value.regions
            ),
            provenance=DeltaObservationProvenanceDto.from_domain(value.provenance),
        )


class ContinuousOverlayProvenanceDto(ApiModel):
    algorithm_id: str
    algorithm_version: str
    parameters: dict[str, object]
    base_comparison: ComparisonProvenanceDto
    lap_a_channel: CanonicalSeriesEvidenceDto
    lap_b_channel: CanonicalSeriesEvidenceDto

    @classmethod
    def from_domain(
        cls,
        value: ContinuousOverlayProvenance,
    ) -> ContinuousOverlayProvenanceDto:
        return cls(
            algorithm_id=value.algorithm_id,
            algorithm_version=value.algorithm_version,
            parameters=dict(value.parameters),
            base_comparison=ComparisonProvenanceDto.from_domain(value.base_comparison),
            lap_a_channel=CanonicalSeriesEvidenceDto.from_domain(value.lap_a_channel),
            lap_b_channel=CanonicalSeriesEvidenceDto.from_domain(value.lap_b_channel),
        )


class ContinuousOverlaySuccessDto(ApiModel):
    canonical_concept: CanonicalConcept
    unit: str
    distance_grid_m: tuple[float, ...]
    lap_a_values: tuple[float, ...]
    lap_b_values: tuple[float, ...]
    provenance: ContinuousOverlayProvenanceDto

    @classmethod
    def from_domain(cls, value: object) -> ContinuousOverlaySuccessDto:
        from ome.analysis import ContinuousOverlaySuccess

        assert isinstance(value, ContinuousOverlaySuccess)
        return cls(
            canonical_concept=value.canonical_concept,
            unit=value.unit,
            distance_grid_m=value.distance_grid_m,
            lap_a_values=value.lap_a_values,
            lap_b_values=value.lap_b_values,
            provenance=ContinuousOverlayProvenanceDto.from_domain(value.provenance),
        )


class GearOverlayProvenanceDto(ApiModel):
    algorithm_id: str
    algorithm_version: str
    parameters: dict[str, object]
    base_comparison: ComparisonProvenanceDto
    lap_a_gear: CanonicalSeriesEvidenceDto
    lap_b_gear: CanonicalSeriesEvidenceDto

    @classmethod
    def from_domain(cls, value: GearOverlayProvenance) -> GearOverlayProvenanceDto:
        return cls(
            algorithm_id=value.algorithm_id,
            algorithm_version=value.algorithm_version,
            parameters=dict(value.parameters),
            base_comparison=ComparisonProvenanceDto.from_domain(value.base_comparison),
            lap_a_gear=CanonicalSeriesEvidenceDto.from_domain(value.lap_a_gear),
            lap_b_gear=CanonicalSeriesEvidenceDto.from_domain(value.lap_b_gear),
        )


class GearOverlaySuccessDto(ApiModel):
    canonical_concept: CanonicalConcept
    unit: str
    distance_grid_m: tuple[float, ...]
    lap_a_gears: tuple[int, ...]
    lap_b_gears: tuple[int, ...]
    provenance: GearOverlayProvenanceDto

    @classmethod
    def from_domain(cls, value: object) -> GearOverlaySuccessDto:
        from ome.analysis import GearOverlaySuccess

        assert isinstance(value, GearOverlaySuccess)
        return cls(
            canonical_concept=value.canonical_concept,
            unit=value.unit,
            distance_grid_m=value.distance_grid_m,
            lap_a_gears=value.lap_a_gears,
            lap_b_gears=value.lap_b_gears,
            provenance=GearOverlayProvenanceDto.from_domain(value.provenance),
        )


class SupportingEvidenceSummaryDto(ApiModel):
    canonical_concept: CanonicalConcept
    kind: str
    status: str
    unit: str | None
    issue_codes: tuple[str, ...]
    messages: tuple[str, ...]


class ComparisonReportProvenanceDto(ApiModel):
    assembler_id: str
    assembler_version: str
    requested_concepts: tuple[CanonicalConcept, ...]
    base_comparison: ComparisonProvenanceDto
    delta_observation: DeltaObservationProvenanceDto
    continuous_overlays: tuple[ContinuousOverlayProvenanceDto, ...]
    gear_overlay: GearOverlayProvenanceDto | None

    @classmethod
    def from_domain(
        cls,
        value: ComparisonReportProvenance,
    ) -> ComparisonReportProvenanceDto:
        return cls(
            assembler_id=value.assembler_id,
            assembler_version=value.assembler_version,
            requested_concepts=value.requested_concepts,
            base_comparison=ComparisonProvenanceDto.from_domain(value.base_comparison),
            delta_observation=DeltaObservationProvenanceDto.from_domain(value.delta_observation),
            continuous_overlays=tuple(
                ContinuousOverlayProvenanceDto.from_domain(item)
                for item in value.continuous_overlays
            ),
            gear_overlay=(
                None
                if value.gear_overlay is None
                else GearOverlayProvenanceDto.from_domain(value.gear_overlay)
            ),
        )


class ComparisonReportSuccessDto(ApiModel):
    comparison: LapComparisonSuccessDto
    observations: DeltaObservationSuccessDto
    continuous_overlays: tuple[ContinuousOverlaySuccessDto, ...]
    gear_overlay: GearOverlaySuccessDto | None
    supporting_evidence: tuple[SupportingEvidenceSummaryDto, ...]
    provenance: ComparisonReportProvenanceDto

    @classmethod
    def from_domain(cls, value: ComparisonReportSuccess) -> ComparisonReportSuccessDto:
        return cls(
            comparison=LapComparisonSuccessDto.from_domain(value.comparison),
            observations=DeltaObservationSuccessDto.from_domain(value.observations),
            continuous_overlays=tuple(
                ContinuousOverlaySuccessDto.from_domain(item) for item in value.continuous_overlays
            ),
            gear_overlay=(
                None
                if value.gear_overlay is None
                else GearOverlaySuccessDto.from_domain(value.gear_overlay)
            ),
            supporting_evidence=tuple(
                SupportingEvidenceSummaryDto(
                    canonical_concept=item.canonical_concept,
                    kind=item.kind.value,
                    status=item.status.value,
                    unit=item.unit,
                    issue_codes=item.issue_codes,
                    messages=item.messages,
                )
                for item in value.supporting_evidence
            ),
            provenance=ComparisonReportProvenanceDto.from_domain(value.provenance),
        )


class ComparisonReportReadinessIssueDto(ApiModel):
    code: str
    message: str


class ComparisonReportSuccessResponse(ApiModel):
    status: Literal["success"] = "success"
    report: ComparisonReportSuccessDto


class ComparisonReportNotReadyResponse(ApiModel):
    status: Literal["not_ready"] = "not_ready"
    issues: tuple[ComparisonReportReadinessIssueDto, ...]
    base_comparison: LapComparisonNotReadyDto | None = None

    @classmethod
    def from_domain(
        cls,
        value: ComparisonReportNotReady,
    ) -> ComparisonReportNotReadyResponse:
        return cls(
            issues=tuple(
                ComparisonReportReadinessIssueDto(
                    code=issue.code.value,
                    message=issue.message,
                )
                for issue in value.issues
            ),
            base_comparison=(
                None
                if value.base_comparison is None
                else LapComparisonNotReadyDto.from_domain(value.base_comparison)
            ),
        )


ComparisonReportHttpResponse = ComparisonReportSuccessResponse | ComparisonReportNotReadyResponse


class HealthResponse(ApiModel):
    status: Literal["ok"] = "ok"
    service: Literal["ome-api"] = "ome-api"
    api_version: Literal["v1"] = "v1"


def mapping_to_dict(value: Mapping[str, object]) -> dict[str, object]:
    return dict(value)
