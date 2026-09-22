from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Protocol

from ome.domain import ImportedTelemetryDataset, ImportIssue


class ImportFailureCode(StrEnum):
    UNSUPPORTED_SOURCE = "unsupported_source"
    READ_ERROR = "read_error"
    INVALID_PROFILE = "invalid_profile"


@dataclass(frozen=True, slots=True)
class ChannelSummary:
    identifier: str
    original_name: str
    unit: str | None
    sample_rate_hz: float | None


@dataclass(frozen=True, slots=True)
class ImportSummary:
    source_type: str
    source_identity: str
    source_metadata: Mapping[str, object]
    channels: tuple[ChannelSummary, ...]
    warnings: tuple[ImportIssue, ...]
    missing_metadata: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImportSuccess:
    dataset: ImportedTelemetryDataset
    summary: ImportSummary


@dataclass(frozen=True, slots=True)
class ImportFailure:
    code: ImportFailureCode
    source_identity: str
    message: str
    diagnostics: tuple[str, ...] = ()


ImportOutcome = ImportSuccess | ImportFailure


class TelemetryImporter(Protocol):
    importer_id: str
    importer_version: str

    def supports(self, source: Path) -> bool: ...

    def import_source(
        self,
        source: Path,
        *,
        imported_at: datetime | None = None,
    ) -> ImportOutcome: ...
