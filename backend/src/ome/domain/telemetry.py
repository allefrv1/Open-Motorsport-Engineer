from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType

SourceValue = str | int | float | bool | None


def freeze_metadata(values: Mapping[str, object]) -> Mapping[str, object]:
    """Create a recursively read-only snapshot of source metadata."""

    return MappingProxyType({key: _freeze_value(value) for key, value in values.items()})


def _freeze_value(value: object) -> object:
    if isinstance(value, Mapping):
        return freeze_metadata({str(key): nested for key, nested in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(item) for item in value)
    return value


def _empty_metadata() -> Mapping[str, object]:
    return MappingProxyType({})


@dataclass(frozen=True, slots=True)
class ChannelMetadata:
    unit: str | None = None
    sample_rate_hz: float | None = None
    data_type: str | None = None
    description: str | None = None
    source_attributes: Mapping[str, object] = field(default_factory=_empty_metadata)


@dataclass(frozen=True, slots=True)
class SampleSeries:
    timestamps_s: tuple[float, ...]
    values: tuple[SourceValue, ...]

    def __post_init__(self) -> None:
        if len(self.timestamps_s) != len(self.values):
            raise ValueError("sample timestamps and values must have the same length")


@dataclass(frozen=True, slots=True)
class TelemetrySource:
    source_type: str
    original_name: str
    location: str
    source_system: str | None
    format_version: str | None
    metadata: Mapping[str, object] = field(default_factory=_empty_metadata)


@dataclass(frozen=True, slots=True)
class Provenance:
    original_source_name: str
    source_format: str
    source_system: str | None
    content_fingerprint: str
    source_size_bytes: int
    importer_id: str
    importer_version: str
    import_parameters: Mapping[str, object]
    imported_at: datetime
    source_metadata: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class ImportIssue:
    code: str
    message: str
    field: str | None = None


@dataclass(frozen=True, slots=True)
class SourceChannel:
    identifier: str
    original_name: str
    source_system: str | None
    metadata: ChannelMetadata
    series: SampleSeries


@dataclass(frozen=True, slots=True)
class ImportedTelemetryDataset:
    source: TelemetrySource
    provenance: Provenance
    channels: tuple[SourceChannel, ...]
    issues: tuple[ImportIssue, ...]

    def channel(self, identifier: str) -> SourceChannel:
        for channel in self.channels:
            if channel.identifier == identifier:
                return channel
        raise KeyError(identifier)
