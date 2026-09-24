from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ome.domain import ImportedTelemetryDataset, SourceValue

_TRAQMATE_SOURCE_TYPE = "traqmate-trackvision-csv"
_LAP_CHANNEL = "Lap"
_TIME_CHANNEL = "Elapsed Time"


class SourceLapWindowIssueCode(StrEnum):
    UNSUPPORTED_SOURCE_TYPE = "unsupported_source_type"
    MISSING_LAP_CHANNEL = "missing_lap_channel"
    MISSING_TIME_CHANNEL = "missing_time_channel"
    MISSING_PROVENANCE = "missing_provenance"
    INCONSISTENT_SOURCE_EVIDENCE = "inconsistent_source_evidence"
    INVALID_LAP_MARKER = "invalid_lap_marker"
    MISSING_LAP_MARKER = "missing_lap_marker"
    AMBIGUOUS_LAP_MARKER = "ambiguous_lap_marker"
    INCOMPLETE_LAP = "incomplete_lap"
    INVALID_BOUNDARY_TIME = "invalid_boundary_time"


@dataclass(frozen=True, slots=True)
class SourceLapWindowIssue:
    code: SourceLapWindowIssueCode
    message: str


@dataclass(frozen=True, slots=True)
class SourceLapWindowRequest:
    dataset: ImportedTelemetryDataset
    source_lap_number: int


@dataclass(frozen=True, slots=True)
class SourceLapWindow:
    dataset_fingerprint: str
    source_identity: str
    source_type: str
    lap_channel_identifier: str
    time_channel_identifier: str
    source_lap_number: int
    start_index: int
    end_index_exclusive: int
    closing_boundary_index: int
    start_elapsed_s: float
    closing_elapsed_s: float
    sample_count: int


@dataclass(frozen=True, slots=True)
class SourceLapWindowSuccess:
    window: SourceLapWindow


@dataclass(frozen=True, slots=True)
class SourceLapWindowNotReady:
    issues: tuple[SourceLapWindowIssue, ...]


SourceLapWindowOutcome = SourceLapWindowSuccess | SourceLapWindowNotReady


class TraqmateLapWindowSelector:
    """Select one explicit complete lap from preserved sparse Traqmate markers."""

    def select(self, request: SourceLapWindowRequest) -> SourceLapWindowOutcome:
        dataset = request.dataset

        if dataset.source.source_type != _TRAQMATE_SOURCE_TYPE:
            return self._not_ready(
                SourceLapWindowIssueCode.UNSUPPORTED_SOURCE_TYPE,
                "Lap-window selection supports only Traqmate Trackvision CSV evidence.",
            )

        if not dataset.provenance.content_fingerprint.strip():
            return self._not_ready(
                SourceLapWindowIssueCode.MISSING_PROVENANCE,
                "Dataset content fingerprint is required for a traceable lap window.",
            )

        lap_channel = self._channel_or_none(dataset, _LAP_CHANNEL)
        if lap_channel is None:
            return self._not_ready(
                SourceLapWindowIssueCode.MISSING_LAP_CHANNEL,
                "Traqmate source Lap channel is required.",
            )

        time_channel = self._channel_or_none(dataset, _TIME_CHANNEL)
        if time_channel is None:
            return self._not_ready(
                SourceLapWindowIssueCode.MISSING_TIME_CHANNEL,
                "Traqmate source Elapsed Time channel is required.",
            )

        lap_values = lap_channel.series.values
        elapsed_values = time_channel.series.values

        if len(lap_values) != len(elapsed_values):
            return self._not_ready(
                SourceLapWindowIssueCode.INCONSISTENT_SOURCE_EVIDENCE,
                "Lap and Elapsed Time source channels must have the same sample count.",
            )

        if len(lap_channel.series.timestamps_s) != len(lap_values) or len(
            time_channel.series.timestamps_s
        ) != len(elapsed_values):
            return self._not_ready(
                SourceLapWindowIssueCode.INCONSISTENT_SOURCE_EVIDENCE,
                "Source channel timestamp/value lengths are inconsistent.",
            )

        markers: list[tuple[int, int]] = []
        for index, value in enumerate(lap_values):
            if value is None or value == "":
                continue
            parsed = self._parse_lap_number(value)
            if parsed is None:
                return self._not_ready(
                    SourceLapWindowIssueCode.INVALID_LAP_MARKER,
                    f"Lap marker at source index {index} is not an integer lap number.",
                )
            markers.append((index, parsed))

        requested = tuple(index for index, lap in markers if lap == request.source_lap_number)
        if not requested:
            return self._not_ready(
                SourceLapWindowIssueCode.MISSING_LAP_MARKER,
                f"Source Lap {request.source_lap_number} marker is absent.",
            )
        if len(requested) != 1:
            return self._not_ready(
                SourceLapWindowIssueCode.AMBIGUOUS_LAP_MARKER,
                f"Source Lap {request.source_lap_number} has multiple boundary markers.",
            )

        start_index = requested[0]
        next_markers = tuple(index for index, _lap in markers if index > start_index)
        if not next_markers:
            return self._not_ready(
                SourceLapWindowIssueCode.INCOMPLETE_LAP,
                f"Source Lap {request.source_lap_number} has no later closing boundary marker.",
            )

        closing_boundary_index = next_markers[0]
        if closing_boundary_index <= start_index:
            return self._not_ready(
                SourceLapWindowIssueCode.INCONSISTENT_SOURCE_EVIDENCE,
                "Closing boundary must occur strictly after the requested lap marker.",
            )

        start_elapsed_s = self._finite_number(elapsed_values[start_index])
        closing_elapsed_s = self._finite_number(elapsed_values[closing_boundary_index])
        if start_elapsed_s is None or closing_elapsed_s is None:
            return self._not_ready(
                SourceLapWindowIssueCode.INVALID_BOUNDARY_TIME,
                "Lap start and closing boundary require finite numeric Elapsed Time values.",
            )
        if closing_elapsed_s <= start_elapsed_s:
            return self._not_ready(
                SourceLapWindowIssueCode.INVALID_BOUNDARY_TIME,
                "Closing boundary Elapsed Time must be strictly greater than lap start time.",
            )

        return SourceLapWindowSuccess(
            window=SourceLapWindow(
                dataset_fingerprint=dataset.provenance.content_fingerprint,
                source_identity=dataset.source.original_name,
                source_type=dataset.source.source_type,
                lap_channel_identifier=lap_channel.identifier,
                time_channel_identifier=time_channel.identifier,
                source_lap_number=request.source_lap_number,
                start_index=start_index,
                end_index_exclusive=closing_boundary_index,
                closing_boundary_index=closing_boundary_index,
                start_elapsed_s=start_elapsed_s,
                closing_elapsed_s=closing_elapsed_s,
                sample_count=closing_boundary_index - start_index,
            )
        )

    @staticmethod
    def _channel_or_none(dataset: ImportedTelemetryDataset, identifier: str):
        try:
            return dataset.channel(identifier)
        except KeyError:
            return None

    @staticmethod
    def _parse_lap_number(value: SourceValue) -> int | None:
        if isinstance(value, bool) or isinstance(value, tuple):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value) if math.isfinite(value) and value.is_integer() else None
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            try:
                number = int(stripped)
            except ValueError:
                return None
            return number
        return None

    @staticmethod
    def _finite_number(value: SourceValue) -> float | None:
        if isinstance(value, bool) or isinstance(value, tuple) or value is None:
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
    def _not_ready(
        code: SourceLapWindowIssueCode,
        message: str,
    ) -> SourceLapWindowNotReady:
        return SourceLapWindowNotReady(issues=(SourceLapWindowIssue(code=code, message=message),))
