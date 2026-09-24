from __future__ import annotations

import csv
import hashlib
import io
import math
from collections.abc import Mapping, Sequence
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

TRAQMATE_SOURCE_TYPE = "traqmate-trackvision-csv"
TRAQMATE_SOURCE_SYSTEM = "Traqmate Trackvision"
TRAQMATE_VERSION = "V2"
TRAQMATE_SIGNATURE = ("Format", TRAQMATE_SOURCE_SYSTEM, TRAQMATE_VERSION)
_REQUIRED_HEADER_COLUMNS = (
    "Elapsed Time",
    "Lat (Degrees)",
    "Lon (Degrees)",
    "Lap",
)

_KNOWN_UNITS: dict[str, str] = {
    "Elapsed Time": "s",
    "Lat (Degrees)": "deg",
    "Lon (Degrees)": "deg",
    "Altitude (meters)": "m",
    "Velocity (MPH)": "mph",
    "Lap": "",
}


class _InvalidTraqmateCSV(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class _SourceState:
    size: int
    mtime_ns: int


@dataclass(frozen=True, slots=True)
class _ParsedTable:
    preamble_rows: tuple[tuple[str, ...], ...]
    raw_header_row: tuple[str, ...]
    channel_names: tuple[str, ...]
    elapsed_time_index: int
    data_rows: tuple[tuple[str, ...], ...]


class TraqmateTrackvisionCSVImporter:
    importer_id = "traqmate.trackvision-csv"
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
                    return tuple(cell.strip() for cell in row[:3]) == TRAQMATE_SIGNATURE
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
                "Traqmate Trackvision importer only accepts .csv sources.",
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
                "Traqmate telemetry source could not be read safely.",
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
            timestamps = self._timestamps(
                table.data_rows,
                table.elapsed_time_index,
            )
            source_metadata = self._source_metadata(
                table.preamble_rows,
                sample_rate_hz,
                table.raw_header_row,
            )
            channels = self._channels(
                table,
                timestamps,
                sample_rate_hz,
            )
        except UnicodeDecodeError as exc:
            return self._failure(
                path,
                ImportFailureCode.READ_ERROR,
                "Traqmate telemetry source is not valid UTF-8.",
                diagnostics=(type(exc).__name__,),
            )
        except csv.Error as exc:
            return self._failure(
                path,
                ImportFailureCode.INVALID_PROFILE,
                f"Traqmate CSV parsing failed: {exc}",
            )
        except _InvalidTraqmateCSV as exc:
            return self._failure(
                path,
                ImportFailureCode.INVALID_PROFILE,
                str(exc),
            )

        timestamp = imported_at if imported_at is not None else datetime.now(UTC)
        fingerprint = f"sha256:{hashlib.sha256(payload).hexdigest()}"

        telemetry_source = TelemetrySource(
            source_type=TRAQMATE_SOURCE_TYPE,
            original_name=path.name,
            location=str(path.resolve()),
            source_system=TRAQMATE_SOURCE_SYSTEM,
            format_version=TRAQMATE_VERSION,
            metadata=source_metadata,
        )
        provenance = Provenance(
            original_source_name=path.name,
            source_format=TRAQMATE_SOURCE_TYPE,
            source_system=TRAQMATE_SOURCE_SYSTEM,
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
            source_type=TRAQMATE_SOURCE_TYPE,
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
            (
                index
                for index, row in enumerate(rows)
                if not TraqmateTrackvisionCSVImporter._is_blank(row)
            ),
            None,
        )
        if first_non_blank is None:
            raise _InvalidTraqmateCSV("Traqmate CSV source is empty.")

        signature = rows[first_non_blank]
        normalized_signature = tuple(cell.strip() for cell in signature[:3])
        if len(signature) < 3 or normalized_signature != TRAQMATE_SIGNATURE:
            raise _InvalidTraqmateCSV(
                "Unsupported Traqmate Trackvision signature/version; expected V2."
            )

        preamble: list[tuple[str, ...]] = [signature]
        header_index: int | None = None

        for index in range(first_non_blank + 1, len(rows)):
            row = rows[index]
            if TraqmateTrackvisionCSVImporter._is_blank(row):
                continue

            normalized = tuple(cell.strip() for cell in row)
            if "Elapsed Time" in normalized:
                header_index = index
                break
            preamble.append(row)

        if header_index is None:
            raise _InvalidTraqmateCSV(
                "Traqmate CSV does not contain a supported Elapsed Time telemetry table."
            )

        raw_header_row = rows[header_index]
        channel_names = tuple(cell.strip() for cell in raw_header_row)

        if any(name == "" for name in channel_names):
            raise _InvalidTraqmateCSV("Traqmate CSV channel names must be non-empty.")
        if len(set(channel_names)) != len(channel_names):
            raise _InvalidTraqmateCSV(
                "Traqmate CSV duplicate source channel names are unsupported in this slice."
            )

        for required in _REQUIRED_HEADER_COLUMNS:
            if channel_names.count(required) != 1:
                raise _InvalidTraqmateCSV(
                    f"Traqmate CSV telemetry header must contain exactly one {required!r} column."
                )

        elapsed_time_index = channel_names.index("Elapsed Time")

        data_rows = tuple(
            row
            for row in rows[header_index + 1 :]
            if not TraqmateTrackvisionCSVImporter._is_blank(row)
        )
        if not data_rows:
            raise _InvalidTraqmateCSV("Traqmate CSV must contain at least one telemetry data row.")

        expected_fields = len(channel_names)
        for row_number, row in enumerate(data_rows, start=1):
            if len(row) != expected_fields:
                raise _InvalidTraqmateCSV(
                    f"Traqmate CSV data row {row_number} has {len(row)} fields; "
                    f"expected {expected_fields}."
                )

        return _ParsedTable(
            preamble_rows=tuple(preamble),
            raw_header_row=tuple(raw_header_row),
            channel_names=channel_names,
            elapsed_time_index=elapsed_time_index,
            data_rows=data_rows,
        )

    @staticmethod
    def _timestamps(
        data_rows: Sequence[tuple[str, ...]],
        elapsed_time_index: int,
    ) -> tuple[float, ...]:
        timestamps: list[float] = []

        for row_number, row in enumerate(data_rows, start=1):
            raw_time = row[elapsed_time_index]
            if raw_time == "":
                raise _InvalidTraqmateCSV(
                    f"Traqmate CSV data row {row_number} has an empty Elapsed Time value."
                )

            try:
                time_s = float(raw_time)
            except ValueError:
                raise _InvalidTraqmateCSV(
                    f"Traqmate CSV data row {row_number} Elapsed Time is not decimal."
                ) from None

            if not math.isfinite(time_s):
                raise _InvalidTraqmateCSV(
                    f"Traqmate CSV data row {row_number} Elapsed Time must be finite."
                )

            timestamps.append(time_s)

        return tuple(timestamps)

    @staticmethod
    def _channels(
        table: _ParsedTable,
        timestamps: tuple[float, ...],
        sample_rate_hz: float | None,
    ) -> tuple[SourceChannel, ...]:
        channels: list[SourceChannel] = []

        for column_index, original_name in enumerate(table.channel_names):
            values = tuple(
                row[column_index] if row[column_index] != "" else None for row in table.data_rows
            )
            channels.append(
                SourceChannel(
                    identifier=original_name,
                    original_name=original_name,
                    source_system=TRAQMATE_SOURCE_SYSTEM,
                    metadata=ChannelMetadata(
                        unit=_KNOWN_UNITS.get(original_name),
                        sample_rate_hz=sample_rate_hz,
                        source_attributes=freeze_metadata(
                            {
                                "traqmate_column_index": column_index,
                                "traqmate_raw_header_name": table.raw_header_row[column_index],
                                "traqmate_version": TRAQMATE_VERSION,
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
            if not row or row[0] != "Sample Rate (samps/sec)":
                continue

            raw_value = row[1] if len(row) > 1 else ""
            try:
                value = float(raw_value)
            except ValueError:
                value = math.nan

            if math.isfinite(value) and value > 0:
                return value, (), ()

            issue = ImportIssue(
                code="invalid_sample_rate_metadata",
                field="sample_rate_hz",
                message="Source sample rate is not a positive finite value.",
            )
            return None, (issue,), ("sample_rate_hz",)

        issue = ImportIssue(
            code="missing_sample_rate",
            field="sample_rate_hz",
            message="Source did not provide Sample Rate (samps/sec).",
        )
        return None, (issue,), ("sample_rate_hz",)

    @staticmethod
    def _source_metadata(
        preamble_rows: tuple[tuple[str, ...], ...],
        sample_rate_hz: float | None,
        raw_header_row: tuple[str, ...],
    ) -> Mapping[str, object]:
        values: dict[str, object] = {
            "traqmate_preamble_rows": preamble_rows,
            "traqmate_raw_header_row": raw_header_row,
        }
        selected_keys = {
            "Track": "track",
            "Vehicle": "vehicle",
            "Driver": "driver",
            "Starting Date": "starting_date",
            "Starting Time": "starting_time",
        }

        for row in preamble_rows:
            if not row:
                continue
            target = selected_keys.get(row[0])
            if target is not None and len(row) > 1:
                values[target] = row[1]

            if row[0] == "Duration (secs)" and len(row) > 1:
                try:
                    duration = float(row[1])
                except ValueError:
                    duration = math.nan
                if math.isfinite(duration):
                    values["duration_s"] = duration

        if sample_rate_hz is not None:
            values["sample_rate_hz"] = sample_rate_hz

        return freeze_metadata(values)

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
