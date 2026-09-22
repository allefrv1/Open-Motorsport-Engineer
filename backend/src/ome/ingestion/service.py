from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from ome.ingestion.contracts import (
    ImportFailure,
    ImportFailureCode,
    ImportOutcome,
    TelemetryImporter,
)


class TelemetryImportService:
    """Select a compatible source adapter without leaking source details downstream."""

    def __init__(self, importers: Iterable[TelemetryImporter]) -> None:
        self._importers = tuple(importers)

    def import_file(
        self,
        source: str | Path,
        *,
        imported_at: datetime | None = None,
    ) -> ImportOutcome:
        path = Path(source)

        for importer in self._importers:
            if importer.supports(path):
                return importer.import_source(path, imported_at=imported_at)

        return ImportFailure(
            code=ImportFailureCode.UNSUPPORTED_SOURCE,
            source_identity=path.name,
            message=f"No telemetry importer supports source: {path.name}",
        )
