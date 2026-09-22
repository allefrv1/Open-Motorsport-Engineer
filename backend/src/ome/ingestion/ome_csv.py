from __future__ import annotations

import csv
import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType

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

OME_CSV_PROFILE_VERSION = "0.1"
OME_CSV_SOURCE_TYPE = "ome-csv-profile"


class _InvalidProfile(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class _ChannelDefinition:
    source_name: str
    unit: str | None
    has_unit: bool
    description: str | None
    data_type: str | None
    raw: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class _ParsedSidecar:
    source_system: str | None
    sample_rate_hz: float | None
    channels: Mapping[str, _ChannelDefinition]
    raw: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class _SourceState:
    csv_size: int
    csv_mtime_ns: int
    sidecar_size: int
    sidecar_mtime_ns: int


class OMECsvProfileImporter:
    importer_id = "ome.csv-profile"
    importer_version = "0.1.0"

    def supports(self, source: Path) -> bool:
        path = Path(source)
        return path.suffix.lower() == ".csv" and self.sidecar_path(path).is_file()

    @staticmethod
    def sidecar_path(source: Path) -> Path:
        return source.with_suffix(".ome.json")

    def import_source(
        self,
        source: Path,
        *,
        imported_at: datetime | None = None,
    ) -> ImportOutcome:
        path = Path(source)
        sidecar_path = self.sidecar_path(path)

        if path.suffix.lower() != ".csv":
            return self._failure(
                path,
                ImportFailureCode.UNSUPPORTED_SOURCE,
                "OME CSV importer only accepts .csv sources.",
            )

        if not path.is_file():
            return self._failure(
                path,
                ImportFailureCode.READ_ERROR,
                "Telemetry source does not exist or is not a readable file.",
            )

        if not sidecar_path.is_file():
            return self._failure(
                path,
                ImportFailureCode.INVALID_PROFILE,
                f"Required OME sidecar is missing: {sidecar_path.name}",
            )

        try:
            before = self._source_state(path, sidecar_path)
            sidecar_bytes = sidecar_path.read_bytes()
        except OSError as exc:
            return self._read_failure(path, exc)

        try:
            payload = json.loads(sidecar_bytes.decode("utf-8"))
            sidecar = self._parse_sidecar(payload)
        except UnicodeDecodeError as exc:
            return self._read_failure(path, exc)
        except json.JSONDecodeError as exc:
            return self._invalid_profile(path, f"Invalid sidecar JSON: {exc.msg}")
        except _InvalidProfile as exc:
            return self._invalid_profile(path, str(exc))

        try:
            timestamps, values_by_channel = self._read_csv(path, sidecar)
            fingerprint = self._content_fingerprint(path, sidecar_bytes)
            after = self._source_state(path, sidecar_path)
        except (OSError, UnicodeDecodeError) as exc:
            return self._read_failure(path, exc)
        except (csv.Error, _InvalidProfile) as exc:
            return self._invalid_profile(path, str(exc))

        if before != after:
            return self._failure(
                path,
                ImportFailureCode.READ_ERROR,
                "Telemetry source changed while it was being imported.",
            )

        timestamp = imported_at if imported_at is not None else datetime.now(UTC)
        source_metadata = sidecar.raw
        issues, missing_metadata = self._missing_metadata(sidecar)
        source_system = sidecar.source_system

        channels = tuple(
            SourceChannel(
                identifier=identifier,
                original_name=definition.source_name,
                source_system=source_system,
                metadata=ChannelMetadata(
                    unit=definition.unit,
                    sample_rate_hz=sidecar.sample_rate_hz,
                    data_type=definition.data_type,
                    description=definition.description,
                    source_attributes=definition.raw,
                ),
                series=SampleSeries(
                    timestamps_s=timestamps,
                    values=values_by_channel[identifier],
                ),
            )
            for identifier, definition in sidecar.channels.items()
        )

        telemetry_source = TelemetrySource(
            source_type=OME_CSV_SOURCE_TYPE,
            original_name=path.name,
            location=str(path.resolve()),
            source_system=source_system,
            format_version=OME_CSV_PROFILE_VERSION,
            metadata=source_metadata,
        )
        provenance = Provenance(
            original_source_name=path.name,
            source_format=OME_CSV_SOURCE_TYPE,
            source_system=source_system,
            content_fingerprint=fingerprint,
            source_size_bytes=before.csv_size + before.sidecar_size,
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
            source_type=OME_CSV_SOURCE_TYPE,
            source_identity=path.name,
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
    def _parse_sidecar(payload: object) -> _ParsedSidecar:
        if not isinstance(payload, dict):
            raise _InvalidProfile("Sidecar root must be a JSON object.")

        version = payload.get("ome_csv_version")
        if version != OME_CSV_PROFILE_VERSION:
            raise _InvalidProfile(
                f"Unsupported ome_csv_version {version!r}; expected {OME_CSV_PROFILE_VERSION!r}."
            )

        source = payload.get("source")
        if not isinstance(source, dict):
            raise _InvalidProfile("Sidecar field 'source' must be an object.")

        description = source.get("description")
        if not isinstance(description, str) or not description.strip():
            raise _InvalidProfile("Sidecar source.description must be a non-empty string.")

        source_system = source.get("system")
        if source_system is not None and not isinstance(source_system, str):
            raise _InvalidProfile("Sidecar source.system must be a string or null.")

        sample_rate = payload.get("sample_rate_hz")
        if sample_rate is not None:
            if isinstance(sample_rate, bool) or not isinstance(sample_rate, (int, float)):
                raise _InvalidProfile("sample_rate_hz must be a positive number or null.")
            if not math.isfinite(float(sample_rate)) or float(sample_rate) <= 0:
                raise _InvalidProfile("sample_rate_hz must be a positive finite number.")
            sample_rate_hz: float | None = float(sample_rate)
        else:
            sample_rate_hz = None

        raw_channels = payload.get("channels")
        if not isinstance(raw_channels, dict) or not raw_channels:
            raise _InvalidProfile("Sidecar channels must be a non-empty object.")

        channels: dict[str, _ChannelDefinition] = {}
        for identifier, raw_definition in raw_channels.items():
            if not isinstance(identifier, str) or not identifier:
                raise _InvalidProfile("Every channel identifier must be a non-empty string.")
            if not isinstance(raw_definition, dict):
                raise _InvalidProfile(f"Channel {identifier!r} definition must be an object.")

            source_name = raw_definition.get("source_name")
            if not isinstance(source_name, str) or not source_name:
                raise _InvalidProfile(
                    f"Channel {identifier!r} source_name must be a non-empty string."
                )

            has_unit = "unit" in raw_definition and raw_definition.get("unit") is not None
            unit = raw_definition.get("unit")
            if unit is not None and not isinstance(unit, str):
                raise _InvalidProfile(f"Channel {identifier!r} unit must be a string or null.")

            description_value = raw_definition.get("description")
            if description_value is not None and not isinstance(description_value, str):
                raise _InvalidProfile(
                    f"Channel {identifier!r} description must be a string or null."
                )

            data_type = raw_definition.get("data_type")
            if data_type is not None and not isinstance(data_type, str):
                raise _InvalidProfile(f"Channel {identifier!r} data_type must be a string or null.")

            channels[identifier] = _ChannelDefinition(
                source_name=source_name,
                unit=unit,
                has_unit=has_unit,
                description=description_value,
                data_type=data_type,
                raw=freeze_metadata(raw_definition),
            )

        for optional_object in ("context", "source_provenance"):
            value = payload.get(optional_object)
            if value is not None and not isinstance(value, dict):
                raise _InvalidProfile(f"Sidecar {optional_object} must be an object when present.")

        return _ParsedSidecar(
            source_system=source_system,
            sample_rate_hz=sample_rate_hz,
            channels=MappingProxyType(channels),
            raw=freeze_metadata(payload),
        )

    @staticmethod
    def _read_csv(
        source: Path,
        sidecar: _ParsedSidecar,
    ) -> tuple[tuple[float, ...], Mapping[str, tuple[str | None, ...]]]:
        timestamps: list[float] = []
        values_by_channel: dict[str, list[str | None]] = {
            identifier: [] for identifier in sidecar.channels
        }

        with source.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, strict=True)
            try:
                header = next(reader)
            except StopIteration:
                raise _InvalidProfile("OME CSV file is empty.") from None

            if not header or header[0] != "time_s":
                raise _InvalidProfile("OME CSV first column must be exactly 'time_s'.")
            if len(header) < 2:
                raise _InvalidProfile("OME CSV must contain at least one telemetry channel.")
            if len(set(header)) != len(header):
                raise _InvalidProfile("OME CSV header contains duplicate column identifiers.")

            csv_channels = header[1:]
            sidecar_channels = list(sidecar.channels)
            if csv_channels != sidecar_channels:
                raise _InvalidProfile(
                    "CSV channel columns must exactly match sidecar channel keys in the same order."
                )

            previous_time: float | None = None
            for line_number, row in enumerate(reader, start=2):
                if len(row) != len(header):
                    raise _InvalidProfile(
                        f"CSV row {line_number} has {len(row)} fields; expected {len(header)}."
                    )

                raw_time = row[0]
                try:
                    time_s = float(raw_time)
                except ValueError:
                    raise _InvalidProfile(
                        f"CSV row {line_number} time_s is not a valid decimal number."
                    ) from None

                if not math.isfinite(time_s):
                    raise _InvalidProfile(f"CSV row {line_number} time_s must be finite.")
                if previous_time is not None and time_s <= previous_time:
                    raise _InvalidProfile(
                        f"CSV row {line_number} time_s must be strictly increasing."
                    )

                timestamps.append(time_s)
                previous_time = time_s

                for identifier, raw_value in zip(csv_channels, row[1:], strict=True):
                    values_by_channel[identifier].append(raw_value if raw_value != "" else None)

        frozen_values = {
            identifier: tuple(values) for identifier, values in values_by_channel.items()
        }
        return tuple(timestamps), frozen_values

    @staticmethod
    def _source_state(source: Path, sidecar: Path) -> _SourceState:
        csv_stat = source.stat()
        sidecar_stat = sidecar.stat()
        return _SourceState(
            csv_size=csv_stat.st_size,
            csv_mtime_ns=csv_stat.st_mtime_ns,
            sidecar_size=sidecar_stat.st_size,
            sidecar_mtime_ns=sidecar_stat.st_mtime_ns,
        )

    @staticmethod
    def _content_fingerprint(source: Path, sidecar_bytes: bytes) -> str:
        hasher = hashlib.sha256()
        hasher.update(b"ome-csv-profile-source-v1\0")

        csv_size = source.stat().st_size
        hasher.update(csv_size.to_bytes(8, byteorder="big", signed=False))
        with source.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                hasher.update(chunk)

        hasher.update(len(sidecar_bytes).to_bytes(8, byteorder="big", signed=False))
        hasher.update(sidecar_bytes)
        return f"sha256:{hasher.hexdigest()}"

    @staticmethod
    def _missing_metadata(
        sidecar: _ParsedSidecar,
    ) -> tuple[tuple[ImportIssue, ...], tuple[str, ...]]:
        issues: list[ImportIssue] = []
        missing: list[str] = []

        if sidecar.sample_rate_hz is None:
            field = "sample_rate_hz"
            missing.append(field)
            issues.append(
                ImportIssue(
                    code="missing_sample_rate",
                    field=field,
                    message="Source did not provide a shared sample rate.",
                )
            )

        for identifier, definition in sidecar.channels.items():
            if not definition.has_unit:
                field = f"channels.{identifier}.unit"
                missing.append(field)
                issues.append(
                    ImportIssue(
                        code="missing_channel_unit",
                        field=field,
                        message=f"Source did not provide a unit for channel {identifier!r}.",
                    )
                )

        return tuple(issues), tuple(missing)

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

    def _read_failure(self, source: Path, error: Exception) -> ImportFailure:
        return self._failure(
            source,
            ImportFailureCode.READ_ERROR,
            "Telemetry source could not be read safely.",
            diagnostics=(type(error).__name__,),
        )

    def _invalid_profile(self, source: Path, message: str) -> ImportFailure:
        return self._failure(source, ImportFailureCode.INVALID_PROFILE, message)
