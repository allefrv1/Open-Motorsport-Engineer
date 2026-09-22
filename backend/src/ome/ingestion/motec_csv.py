from __future__ import annotations

import csv
import hashlib
import io
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ome.domain import (
    ChannelMetadata,
    ImportedTelemetryDataset,
    ImportIssue,
    Provenance,
    SampleSeries,
    SourceChannel,
    TelemetrySource,
    freeze_metadata,
)
from ome.ingestion.contracts import (
    ChannelSummary,
    ImportFailure,
    ImportFailureCode,
    ImportOutcome,
    ImportSuccess,
    ImportSummary,
)

MOTEC_CSV_SOURCE_TYPE = "motec-csv"
MOTEC_SIGNATURE = ("Format", "MoTeC CSV File")


class _InvalidMoTeCCSV(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class _SourceState:
    size: int
    mtime_ns: int


@dataclass(frozen=True, slots=True)
class _ParsedTable:
    preamble_rows: tuple[tuple[str, ...], ...]
    channel_names: tuple[str, ...]
    units: tuple[str, ...]
    data_rows: tuple[tuple[str, ...], ...]


class MoTeCCSVImporter:
    importer_id = "motec.csv"
    importer_version = "0.1.0"

    def supports(self, source: Path) -> bool:
        path = Path(source)
        if path.suffix.lower() != ".csv" or not path.is_file():
            return False

        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle, strict=True)
                for row in reader:
                    if self._is_blank(row):
                        continue
                    return tuple(row[:2]) == MOTEC_SIGNATURE
        except (OSError, UnicodeDecodeError, csv.Error):
            return False

        return False

    def import_source(
        self,
        source: Path,
        *,
        imported_at: datetime | None = None,
    ) -> ImportOutcome:
        path = Path(source)

        if path.suffix.lower() != ".csv":
            return self._failure(
                path,
                ImportFailureCode.UNSUPPORTED_SOURCE,
                "MoTeC CSV importer only accepts .csv sources.",
            )

        if not path.is_file():
            return self._failure(
                path,
                ImportFailureCode.READ_ERROR,
                "Telemetry source does not exist or is not a readable file.",
            )

        try:
            before = self._source_state(path)
            payload = path.read_bytes()
            after = self._source_state(path)
        except OSError as exc:
            return self._failure(
                path,
                ImportFailureCode.READ_ERROR,
                "MoTeC CSV source could not be read safely.",
                diagnostics=(type(exc).__name__,),
            )

        if before != after:
            return self._failure(
                path,
                ImportFailureCode.READ_ERROR,
                "Telemetry source changed while it was being imported.",
            )

        try:
            text = payload.decode("utf-8")
            rows = tuple(tuple(row) for row in csv.reader(io.StringIO(text), strict=True))
            table = self._parse_table(rows)
            sample_rate_hz, issues, missing_metadata = self._sample_rate(table.preamble_rows)
            timestamps = self._timestamps(table.data_rows)
            identifiers, occurrences = self._technical_identifiers(table.channel_names)
            channels = self._channels(
                table,
                identifiers,
                occurrences,
                timestamps,
                sample_rate_hz,
            )
        except UnicodeDecodeError as exc:
            return self._failure(
                path,
                ImportFailureCode.READ_ERROR,
                "MoTeC CSV source is not valid UTF-8.",
                diagnostics=(type(exc).__name__,),
            )
        except csv.Error as exc:
            return self._failure(
                path,
                ImportFailureCode.INVALID_PROFILE,
                f"MoTeC CSV parsing failed: {exc}",
            )
        except _InvalidMoTeCCSV as exc:
            return self._failure(
                path,
                ImportFailureCode.INVALID_PROFILE,
                str(exc),
            )

        source_metadata_values: dict[str, object] = {
            "motec_preamble_rows": table.preamble_rows,
        }
        if sample_rate_hz is not None:
            source_metadata_values["sample_rate_hz"] = sample_rate_hz
        source_metadata = freeze_metadata(source_metadata_values)

        timestamp = imported_at if imported_at is not None else datetime.now(UTC)
        fingerprint = f"sha256:{hashlib.sha256(payload).hexdigest()}"

        telemetry_source = TelemetrySource(
            source_type=MOTEC_CSV_SOURCE_TYPE,
            original_name=path.name,
            location=str(path.resolve()),
            source_system="MoTeC",
            format_version=None,
            metadata=source_metadata,
        )
        provenance = Provenance(
            original_source_name=path.name,
            source_format=MOTEC_CSV_SOURCE_TYPE,
            source_system="MoTeC",
            content_fingerprint=fingerprint,
            source_size_bytes=len(payload),
            importer_id=self.importer_id,
            importer_version=self.importer_version,
            import_parameters=freeze_metadata({}),
            imported_at=timestamp,
            source_metadata=source_metadata,
        )
        dataset = ImportedTelemetryDataset(
            source=telemetry_source,
            provenance=provenance,
            channels=channels,
            issues=issues,
        )
        summary = ImportSummary(
            source_type=MOTEC_CSV_SOURCE_TYPE,
            source_identity=path.name,
            source_metadata=source_metadata,
            channels=tuple(
                ChannelSummary(
                    identifier=channel.identifier,
                    original_name=channel.original_name,
                    unit=channel.metadata.unit,
                    sample_rate_hz=channel.metadata.sample_rate_hz,
                )
                for channel in channels
            ),
            warnings=issues,
            missing_metadata=missing_metadata,
        )
        return ImportSuccess(dataset=dataset, summary=summary)

    @staticmethod
    def _parse_table(rows: Sequence[tuple[str, ...]]) -> _ParsedTable:
        first_non_blank = next(
            (index for index, row in enumerate(rows) if not MoTeCCSVImporter._is_blank(row)),
            None,
        )
        if first_non_blank is None:
            raise _InvalidMoTeCCSV("MoTeC CSV source is empty.")

        signature = rows[first_non_blank]
        if len(signature) < 2 or tuple(signature[:2]) != MOTEC_SIGNATURE:
            raise _InvalidMoTeCCSV("MoTeC CSV source signature is missing or unsupported.")

        preamble: list[tuple[str, ...]] = [signature]
        header_index: int | None = None
        unit_index: int | None = None

        index = first_non_blank + 1
        while index < len(rows):
            row = rows[index]
            if MoTeCCSVImporter._is_blank(row):
                index += 1
                continue

            if row and row[0] == "Time":
                next_index = MoTeCCSVImporter._next_non_blank_index(rows, index + 1)
                if next_index is not None:
                    unit_row = rows[next_index]
                    if len(unit_row) == len(row):
                        if not unit_row or unit_row[0] != "s":
                            raise _InvalidMoTeCCSV(
                                "MoTeC CSV first Time channel must use seconds ('s')."
                            )
                        header_index = index
                        unit_index = next_index
                        break

            preamble.append(row)
            index += 1

        if header_index is None or unit_index is None:
            raise _InvalidMoTeCCSV(
                "MoTeC CSV does not contain a supported Time channel table in seconds."
            )

        channel_names = rows[header_index]
        units = rows[unit_index]

        if not channel_names or channel_names[0] != "Time":
            raise _InvalidMoTeCCSV("MoTeC CSV first source channel must be Time.")
        if len(units) != len(channel_names):
            raise _InvalidMoTeCCSV(
                "MoTeC CSV channel header and unit row must have the same field count."
            )
        if any(name == "" for name in channel_names):
            raise _InvalidMoTeCCSV("MoTeC CSV channel names must be non-empty.")

        data_rows = tuple(
            row for row in rows[unit_index + 1 :] if not MoTeCCSVImporter._is_blank(row)
        )
        if not data_rows:
            raise _InvalidMoTeCCSV("MoTeC CSV must contain at least one telemetry data row.")

        expected_fields = len(channel_names)
        for row_number, row in enumerate(data_rows, start=1):
            if len(row) != expected_fields:
                raise _InvalidMoTeCCSV(
                    f"MoTeC CSV data row {row_number} has {len(row)} fields; "
                    f"expected {expected_fields}."
                )

        return _ParsedTable(
            preamble_rows=tuple(preamble),
            channel_names=tuple(channel_names),
            units=tuple(units),
            data_rows=data_rows,
        )

    @staticmethod
    def _timestamps(data_rows: Sequence[tuple[str, ...]]) -> tuple[float, ...]:
        timestamps: list[float] = []

        for row_number, row in enumerate(data_rows, start=1):
            raw_time = row[0]
            if raw_time == "":
                raise _InvalidMoTeCCSV(
                    f"MoTeC CSV data row {row_number} has an empty Time source value."
                )

            try:
                time_s = float(raw_time)
            except ValueError:
                raise _InvalidMoTeCCSV(
                    f"MoTeC CSV data row {row_number} Time is not a decimal number."
                ) from None

            if not math.isfinite(time_s):
                raise _InvalidMoTeCCSV(f"MoTeC CSV data row {row_number} Time must be finite.")

            timestamps.append(time_s)

        return tuple(timestamps)

    @staticmethod
    def _technical_identifiers(
        channel_names: Sequence[str],
    ) -> tuple[tuple[str, ...], tuple[int, ...]]:
        occurrences: dict[str, int] = {}
        used: set[str] = set()
        identifiers: list[str] = []
        occurrence_values: list[int] = []

        for name in channel_names:
            occurrence = occurrences.get(name, 0) + 1
            occurrences[name] = occurrence
            occurrence_values.append(occurrence)

            if occurrence == 1 and name not in used:
                identifier = name
            else:
                suffix = occurrence
                identifier = f"{name}#{suffix}"
                while identifier in used:
                    suffix += 1
                    identifier = f"{name}#{suffix}"

            used.add(identifier)
            identifiers.append(identifier)

        return tuple(identifiers), tuple(occurrence_values)

    @staticmethod
    def _channels(
        table: _ParsedTable,
        identifiers: tuple[str, ...],
        occurrences: tuple[int, ...],
        timestamps: tuple[float, ...],
        sample_rate_hz: float | None,
    ) -> tuple[SourceChannel, ...]:
        channels: list[SourceChannel] = []

        for column_index, (identifier, original_name, unit, occurrence) in enumerate(
            zip(
                identifiers,
                table.channel_names,
                table.units,
                occurrences,
                strict=True,
            )
        ):
            values = tuple(
                row[column_index] if row[column_index] != "" else None for row in table.data_rows
            )
            channels.append(
                SourceChannel(
                    identifier=identifier,
                    original_name=original_name,
                    source_system="MoTeC",
                    metadata=ChannelMetadata(
                        unit=unit,
                        sample_rate_hz=sample_rate_hz,
                        source_attributes=freeze_metadata(
                            {
                                "motec_column_index": column_index,
                                "motec_name_occurrence": occurrence,
                            }
                        ),
                    ),
                    series=SampleSeries(
                        timestamps_s=timestamps,
                        values=values,
                    ),
                )
            )

        return tuple(channels)

    @staticmethod
    def _sample_rate(
        preamble_rows: Sequence[tuple[str, ...]],
    ) -> tuple[float | None, tuple[ImportIssue, ...], tuple[str, ...]]:
        for row in preamble_rows:
            for index, cell in enumerate(row):
                if cell != "Sample Rate":
                    continue

                raw_value = row[index + 1] if index + 1 < len(row) else ""
                unit = row[index + 2] if index + 2 < len(row) else ""
                try:
                    value = float(raw_value)
                except ValueError:
                    value = math.nan

                if unit == "Hz" and math.isfinite(value) and value > 0:
                    return value, (), ()

                issue = ImportIssue(
                    code="invalid_sample_rate_metadata",
                    field="sample_rate_hz",
                    message="Source Sample Rate metadata is not a positive finite value in Hz.",
                )
                return None, (issue,), ("sample_rate_hz",)

        issue = ImportIssue(
            code="missing_sample_rate",
            field="sample_rate_hz",
            message="Source did not provide a Sample Rate metadata value.",
        )
        return None, (issue,), ("sample_rate_hz",)

    @staticmethod
    def _next_non_blank_index(
        rows: Sequence[tuple[str, ...]],
        start: int,
    ) -> int | None:
        for index in range(start, len(rows)):
            if not MoTeCCSVImporter._is_blank(rows[index]):
                return index
        return None

    @staticmethod
    def _is_blank(row: Sequence[str]) -> bool:
        return not row or all(cell == "" for cell in row)

    @staticmethod
    def _source_state(path: Path) -> _SourceState:
        stat = path.stat()
        return _SourceState(size=stat.st_size, mtime_ns=stat.st_mtime_ns)

    @staticmethod
    def _failure(
        source: Path,
        code: ImportFailureCode,
        message: str,
        *,
        diagnostics: tuple[str, ...] = (),
    ) -> ImportFailure:
        return ImportFailure(
            code=code,
            source_identity=source.name,
            message=message,
            diagnostics=diagnostics,
        )
