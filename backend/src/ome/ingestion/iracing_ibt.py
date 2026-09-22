from __future__ import annotations

import hashlib
import math
import struct
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ome.domain import (
    ChannelMetadata,
    ImportedTelemetryDataset,
    Provenance,
    SampleSeries,
    SourceChannel,
    SourceValue,
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

IRACING_IBT_SOURCE_TYPE = "iracing-ibt"
IRSDK_VERSION = 2

_HEADER_SIZE = 112
_DISK_SUBHEADER_OFFSET = 112
_DISK_SUBHEADER_SIZE = 32
_VAR_HEADER_SIZE = 144

_HEADER_PREFIX = struct.Struct("<12i")
_VAR_BUF = struct.Struct("<4i")
_DISK_SUBHEADER = struct.Struct("<Qddii")
_VAR_HEADER = struct.Struct("<iii?3x32s64s32s")

_TYPE_FORMATS = {
    0: struct.Struct("<b"),
    1: struct.Struct("<?"),
    2: struct.Struct("<i"),
    3: struct.Struct("<I"),
    4: struct.Struct("<f"),
    5: struct.Struct("<d"),
}

_TYPE_NAMES = {
    0: "char",
    1: "bool",
    2: "int",
    3: "bitField",
    4: "float",
    5: "double",
}


class _InvalidIBT(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class _SourceState:
    size: int
    mtime_ns: int


@dataclass(frozen=True, slots=True)
class _Header:
    version: int
    status: int
    tick_rate: int
    session_info_update: int
    session_info_len: int
    session_info_offset: int
    num_vars: int
    var_header_offset: int
    num_buf: int
    buf_len: int
    data_offset: int


@dataclass(frozen=True, slots=True)
class _DiskSubHeader:
    session_start_date: int
    session_start_time: float
    session_end_time: float
    session_lap_count: int
    session_record_count: int


@dataclass(frozen=True, slots=True)
class _Variable:
    type_code: int
    offset: int
    count: int
    count_as_time: bool
    name: str
    description: str
    unit: str


class IRacingIBTImporter:
    importer_id = "iracing.ibt"
    importer_version = "0.1.0"

    def supports(self, source: Path) -> bool:
        return Path(source).suffix.lower() == ".ibt"

    def import_source(
        self,
        source: Path,
        *,
        imported_at: datetime | None = None,
    ) -> ImportOutcome:
        path = Path(source)

        if path.suffix.lower() != ".ibt":
            return self._failure(
                path,
                ImportFailureCode.UNSUPPORTED_SOURCE,
                "iRacing IBT importer only accepts .ibt sources.",
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
                "iRacing telemetry source could not be read safely.",
                diagnostics=(type(exc).__name__,),
            )

        if before != after:
            return self._failure(
                path,
                ImportFailureCode.READ_ERROR,
                "Telemetry source changed while it was being imported.",
            )

        try:
            header = self._parse_header(payload)
            disk = self._parse_disk_subheader(payload)
            variables = self._parse_variables(payload, header)
            self._validate_record_region(payload, header, disk)
            session_info = self._session_info(payload, header)
            timestamps = self._session_time_series(payload, header, disk, variables)
            channels = self._channels(payload, header, disk, variables, timestamps)
        except _InvalidIBT as exc:
            return self._failure(
                path,
                ImportFailureCode.INVALID_PROFILE,
                str(exc),
            )

        timestamp = imported_at if imported_at is not None else datetime.now(UTC)
        fingerprint = f"sha256:{hashlib.sha256(payload).hexdigest()}"

        source_metadata = freeze_metadata(
            {
                "iracing_version": header.version,
                "status": header.status,
                "tick_rate_hz": header.tick_rate,
                "session_info_update": header.session_info_update,
                "session_start_date": disk.session_start_date,
                "session_start_time": disk.session_start_time,
                "session_end_time": disk.session_end_time,
                "session_lap_count": disk.session_lap_count,
                "session_record_count": disk.session_record_count,
                "session_info": session_info,
            }
        )

        source_object = TelemetrySource(
            source_type=IRACING_IBT_SOURCE_TYPE,
            original_name=path.name,
            location=str(path.resolve()),
            source_system="iRacing",
            format_version=str(header.version),
            metadata=source_metadata,
        )
        provenance = Provenance(
            original_source_name=path.name,
            source_format=IRACING_IBT_SOURCE_TYPE,
            source_system="iRacing",
            content_fingerprint=fingerprint,
            source_size_bytes=len(payload),
            importer_id=self.importer_id,
            importer_version=self.importer_version,
            import_parameters=freeze_metadata({}),
            imported_at=timestamp,
            source_metadata=source_metadata,
        )
        dataset = ImportedTelemetryDataset(
            source=source_object,
            provenance=provenance,
            channels=channels,
            issues=(),
        )
        summary = ImportSummary(
            source_type=IRACING_IBT_SOURCE_TYPE,
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
            warnings=(),
            missing_metadata=(),
        )
        return ImportSuccess(dataset=dataset, summary=summary)

    @staticmethod
    def _parse_header(payload: bytes) -> _Header:
        minimum_size = _HEADER_SIZE + _DISK_SUBHEADER_SIZE
        if len(payload) < minimum_size:
            raise _InvalidIBT("iRacing IBT header is truncated.")

        fields = _HEADER_PREFIX.unpack_from(payload, 0)
        (
            version,
            status,
            tick_rate,
            session_info_update,
            session_info_len,
            session_info_offset,
            num_vars,
            var_header_offset,
            num_buf,
            buf_len,
            _pad_a,
            _pad_b,
        ) = fields

        if version != IRSDK_VERSION:
            raise _InvalidIBT(
                f"Unsupported iRacing IRSDK version {version}; expected {IRSDK_VERSION}."
            )
        if tick_rate <= 0:
            raise _InvalidIBT("iRacing IBT tick rate must be positive.")
        if num_vars <= 0:
            raise _InvalidIBT("iRacing IBT must declare at least one variable.")
        if num_buf <= 0 or num_buf > 4:
            raise _InvalidIBT("iRacing IBT buffer count is invalid.")
        if buf_len <= 0:
            raise _InvalidIBT("iRacing IBT record length must be positive.")

        _tick_count, data_offset, _pad_0, _pad_1 = _VAR_BUF.unpack_from(payload, 48)

        return _Header(
            version=version,
            status=status,
            tick_rate=tick_rate,
            session_info_update=session_info_update,
            session_info_len=session_info_len,
            session_info_offset=session_info_offset,
            num_vars=num_vars,
            var_header_offset=var_header_offset,
            num_buf=num_buf,
            buf_len=buf_len,
            data_offset=data_offset,
        )

    @staticmethod
    def _parse_disk_subheader(payload: bytes) -> _DiskSubHeader:
        values = _DISK_SUBHEADER.unpack_from(payload, _DISK_SUBHEADER_OFFSET)
        disk = _DiskSubHeader(*values)
        if disk.session_record_count < 0:
            raise _InvalidIBT("iRacing IBT record count must not be negative.")
        if disk.session_lap_count < 0:
            raise _InvalidIBT("iRacing IBT lap count must not be negative.")
        return disk

    @staticmethod
    def _parse_variables(payload: bytes, header: _Header) -> tuple[_Variable, ...]:
        table_size = header.num_vars * _VAR_HEADER_SIZE
        IRacingIBTImporter._check_region(
            payload,
            header.var_header_offset,
            table_size,
            "variable header table",
        )

        variables: list[_Variable] = []
        names: set[str] = set()

        for index in range(header.num_vars):
            start = header.var_header_offset + index * _VAR_HEADER_SIZE
            type_code, offset, count, count_as_time, raw_name, raw_desc, raw_unit = (
                _VAR_HEADER.unpack_from(payload, start)
            )

            if type_code not in _TYPE_FORMATS:
                raise _InvalidIBT(
                    f"iRacing variable at index {index} has unsupported type {type_code}."
                )
            if offset < 0:
                raise _InvalidIBT(f"iRacing variable at index {index} has a negative offset.")
            if count <= 0:
                raise _InvalidIBT(f"iRacing variable at index {index} has invalid count {count}.")
            if count != 1:
                name = IRacingIBTImporter._decode_fixed(raw_name)
                raise _InvalidIBT(
                    f"iRacing array variable {name!r} is not supported by this adapter slice."
                )

            name = IRacingIBTImporter._decode_fixed(raw_name)
            if not name:
                raise _InvalidIBT(f"iRacing variable at index {index} has no source name.")
            if name in names:
                raise _InvalidIBT(f"iRacing variable name {name!r} is duplicated.")
            names.add(name)

            scalar_size = _TYPE_FORMATS[type_code].size
            if offset + scalar_size > header.buf_len:
                raise _InvalidIBT(
                    f"iRacing variable {name!r} exceeds the telemetry record boundary."
                )

            variables.append(
                _Variable(
                    type_code=type_code,
                    offset=offset,
                    count=count,
                    count_as_time=count_as_time,
                    name=name,
                    description=IRacingIBTImporter._decode_fixed(raw_desc),
                    unit=IRacingIBTImporter._decode_fixed(raw_unit),
                )
            )

        return tuple(variables)

    @staticmethod
    def _validate_record_region(
        payload: bytes,
        header: _Header,
        disk: _DiskSubHeader,
    ) -> None:
        if header.data_offset < 0:
            raise _InvalidIBT("iRacing IBT telemetry data offset is negative.")

        size = disk.session_record_count * header.buf_len
        IRacingIBTImporter._check_region(
            payload,
            header.data_offset,
            size,
            "telemetry record data",
        )

    @staticmethod
    def _session_info(payload: bytes, header: _Header) -> str:
        if header.session_info_len < 0:
            raise _InvalidIBT("iRacing IBT session info length is negative.")

        IRacingIBTImporter._check_region(
            payload,
            header.session_info_offset,
            header.session_info_len,
            "session info",
        )
        raw = payload[
            header.session_info_offset : header.session_info_offset + header.session_info_len
        ]
        raw = raw.rstrip(b"\x00")
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise _InvalidIBT("iRacing IBT session info is not valid UTF-8.") from exc

    @staticmethod
    def _session_time_series(
        payload: bytes,
        header: _Header,
        disk: _DiskSubHeader,
        variables: tuple[_Variable, ...],
    ) -> tuple[float, ...]:
        session_time = next(
            (variable for variable in variables if variable.name == "SessionTime"),
            None,
        )
        if session_time is None:
            raise _InvalidIBT(
                "iRacing IBT does not provide required explicit SessionTime source data."
            )

        timestamps: list[float] = []
        for record_index in range(disk.session_record_count):
            value = IRacingIBTImporter._read_scalar(
                payload,
                header,
                record_index,
                session_time,
            )
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise _InvalidIBT("iRacing SessionTime must be a numeric scalar source variable.")
            timestamp = float(value)
            if not math.isfinite(timestamp):
                raise _InvalidIBT("iRacing SessionTime contains a non-finite source value.")
            timestamps.append(timestamp)

        return tuple(timestamps)

    @staticmethod
    def _channels(
        payload: bytes,
        header: _Header,
        disk: _DiskSubHeader,
        variables: tuple[_Variable, ...],
        timestamps: tuple[float, ...],
    ) -> tuple[SourceChannel, ...]:
        channels: list[SourceChannel] = []

        for variable in variables:
            if variable.name == "SessionTime":
                values: tuple[SourceValue, ...] = timestamps
            else:
                values = tuple(
                    IRacingIBTImporter._read_scalar(
                        payload,
                        header,
                        record_index,
                        variable,
                    )
                    for record_index in range(disk.session_record_count)
                )

            source_attributes = freeze_metadata(
                {
                    "iracing_type_code": variable.type_code,
                    "iracing_count": variable.count,
                    "iracing_count_as_time": variable.count_as_time,
                    "iracing_record_offset": variable.offset,
                }
            )
            channels.append(
                SourceChannel(
                    identifier=variable.name,
                    original_name=variable.name,
                    source_system="iRacing",
                    metadata=ChannelMetadata(
                        unit=variable.unit,
                        sample_rate_hz=float(header.tick_rate),
                        data_type=_TYPE_NAMES[variable.type_code],
                        description=variable.description,
                        source_attributes=source_attributes,
                    ),
                    series=SampleSeries(
                        timestamps_s=timestamps,
                        values=values,
                    ),
                )
            )

        return tuple(channels)

    @staticmethod
    def _read_scalar(
        payload: bytes,
        header: _Header,
        record_index: int,
        variable: _Variable,
    ) -> SourceValue:
        record_start = header.data_offset + record_index * header.buf_len
        value_offset = record_start + variable.offset
        return _TYPE_FORMATS[variable.type_code].unpack_from(payload, value_offset)[0]

    @staticmethod
    def _check_region(
        payload: bytes,
        offset: int,
        size: int,
        label: str,
    ) -> None:
        if offset < 0 or size < 0 or offset > len(payload) or size > len(payload) - offset:
            raise _InvalidIBT(f"iRacing IBT {label} lies outside the file bounds.")

    @staticmethod
    def _decode_fixed(value: bytes) -> str:
        raw = value.split(b"\x00", 1)[0]
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")

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
