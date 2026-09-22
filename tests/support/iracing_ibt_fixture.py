from __future__ import annotations

import struct
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

IRSDK_VERSION = 2
HEADER_SIZE = 112
DISK_SUBHEADER_SIZE = 32
VAR_HEADER_SIZE = 144

_HEADER_PREFIX = struct.Struct("<12i")
_VAR_BUF = struct.Struct("<4i")
_DISK_SUBHEADER = struct.Struct("<Qddii")
_VAR_HEADER = struct.Struct("<iii?3x32s64s32s")

TYPE_CHAR = 0
TYPE_BOOL = 1
TYPE_INT = 2
TYPE_BITFIELD = 3
TYPE_FLOAT = 4
TYPE_DOUBLE = 5

_TYPE_FORMATS: Mapping[int, str] = {
    TYPE_CHAR: "b",
    TYPE_BOOL: "?",
    TYPE_INT: "i",
    TYPE_BITFIELD: "I",
    TYPE_FLOAT: "f",
    TYPE_DOUBLE: "d",
}

_TYPE_SIZES: Mapping[int, int] = {
    TYPE_CHAR: 1,
    TYPE_BOOL: 1,
    TYPE_INT: 4,
    TYPE_BITFIELD: 4,
    TYPE_FLOAT: 4,
    TYPE_DOUBLE: 8,
}


@dataclass(frozen=True, slots=True)
class IbtVariable:
    name: str
    description: str
    unit: str
    type_code: int
    offset: int
    count: int = 1
    count_as_time: bool = False


DEFAULT_VARIABLES = (
    IbtVariable("SessionTime", "Session elapsed time", "s", TYPE_DOUBLE, 0),
    IbtVariable("Speed", "GPS vehicle speed", "m/s", TYPE_FLOAT, 8),
    IbtVariable("Throttle", "Driver throttle input", "%", TYPE_FLOAT, 12),
    IbtVariable("Brake", "Driver brake input", "%", TYPE_FLOAT, 16),
    IbtVariable("SteeringWheelAngle", "Steering wheel angle", "rad", TYPE_FLOAT, 20),
    IbtVariable("RPM", "Engine speed", "revs/min", TYPE_FLOAT, 24),
    IbtVariable("Gear", "Selected gear", "", TYPE_INT, 28),
    IbtVariable("Lap", "Lap number", "", TYPE_INT, 32),
    IbtVariable("LapDistPct", "Lap distance percentage", "%", TYPE_FLOAT, 36),
)

DEFAULT_RECORDS: tuple[Mapping[str, int | float | bool], ...] = (
    {
        "SessionTime": 10.0,
        "Speed": 50.0,
        "Throttle": 0.80,
        "Brake": 0.00,
        "SteeringWheelAngle": 0.01,
        "RPM": 5000.0,
        "Gear": 3,
        "Lap": 2,
        "LapDistPct": 0.20,
    },
    {
        "SessionTime": 10.0166666667,
        "Speed": 51.0,
        "Throttle": 0.90,
        "Brake": 0.10,
        "SteeringWheelAngle": 0.02,
        "RPM": 5100.0,
        "Gear": 3,
        "Lap": 2,
        "LapDistPct": 0.21,
    },
    {
        "SessionTime": 10.0333333333,
        "Speed": 52.0,
        "Throttle": 1.00,
        "Brake": 0.00,
        "SteeringWheelAngle": 0.00,
        "RPM": 5200.0,
        "Gear": 4,
        "Lap": 2,
        "LapDistPct": 0.22,
    },
)

DEFAULT_SESSION_INFO = (
    "---\nWeekendInfo:\n TrackName: Synthetic Test Circuit\nDriverInfo:\n DriverCarIdx: 0\n"
)


def build_ibt_bytes(
    *,
    version: int = IRSDK_VERSION,
    tick_rate: int = 60,
    variables: Sequence[IbtVariable] = DEFAULT_VARIABLES,
    records: Sequence[Mapping[str, int | float | bool]] = DEFAULT_RECORDS,
    session_info: str = DEFAULT_SESSION_INFO,
    session_lap_count: int = 1,
) -> bytes:
    session_bytes = session_info.encode("utf-8") + b"\x00"
    session_info_offset = HEADER_SIZE + DISK_SUBHEADER_SIZE
    var_header_offset = _align(session_info_offset + len(session_bytes), 16)
    data_offset = _align(var_header_offset + len(variables) * VAR_HEADER_SIZE, 16)
    buffer_length = _buffer_length(variables)

    header = bytearray(HEADER_SIZE)
    _HEADER_PREFIX.pack_into(
        header,
        0,
        version,
        1,
        tick_rate,
        1,
        len(session_bytes),
        session_info_offset,
        len(variables),
        var_header_offset,
        1,
        buffer_length,
        0,
        0,
    )
    _VAR_BUF.pack_into(header, 48, 0, data_offset, 0, 0)

    disk_subheader = _DISK_SUBHEADER.pack(
        1_700_000_000,
        10.0,
        10.0 + len(records) / tick_rate,
        session_lap_count,
        len(records),
    )

    total_size = data_offset + len(records) * buffer_length
    payload = bytearray(total_size)
    payload[:HEADER_SIZE] = header
    payload[HEADER_SIZE : HEADER_SIZE + DISK_SUBHEADER_SIZE] = disk_subheader
    payload[session_info_offset : session_info_offset + len(session_bytes)] = session_bytes

    for index, variable in enumerate(variables):
        start = var_header_offset + index * VAR_HEADER_SIZE
        payload[start : start + VAR_HEADER_SIZE] = _VAR_HEADER.pack(
            variable.type_code,
            variable.offset,
            variable.count,
            variable.count_as_time,
            _fixed(variable.name, 32),
            _fixed(variable.description, 64),
            _fixed(variable.unit, 32),
        )

    for record_index, record in enumerate(records):
        base = data_offset + record_index * buffer_length
        for variable in variables:
            value = record[variable.name]
            _pack_value(payload, base + variable.offset, variable, value)

    return bytes(payload)


def build_array_variable_fixture() -> bytes:
    variables = (
        IbtVariable("SessionTime", "Session elapsed time", "s", TYPE_DOUBLE, 0),
        IbtVariable("WheelSpeed", "Four wheel speeds", "m/s", TYPE_FLOAT, 8, count=4),
    )
    records = ({"SessionTime": 1.0, "WheelSpeed": (10.0, 10.1, 9.9, 10.0)},)
    return build_ibt_bytes(variables=variables, records=records)


def build_missing_session_time_fixture() -> bytes:
    variables = (IbtVariable("Speed", "GPS vehicle speed", "m/s", TYPE_FLOAT, 0),)
    records = ({"Speed": 50.0},)
    return build_ibt_bytes(variables=variables, records=records)


def _buffer_length(variables: Sequence[IbtVariable]) -> int:
    end = 0
    for variable in variables:
        size = _TYPE_SIZES[variable.type_code] * variable.count
        end = max(end, variable.offset + size)
    return _align(end, 8)


def _pack_value(
    payload: bytearray,
    offset: int,
    variable: IbtVariable,
    value: object,
) -> None:
    fmt = _TYPE_FORMATS[variable.type_code]
    if variable.count == 1:
        struct.pack_into("<" + fmt, payload, offset, value)
        return

    values = tuple(value)
    if len(values) != variable.count:
        raise ValueError("fixture array value count does not match variable count")
    struct.pack_into("<" + fmt * variable.count, payload, offset, *values)


def _fixed(value: str, size: int) -> bytes:
    encoded = value.encode("utf-8")
    if len(encoded) >= size:
        raise ValueError(f"value {value!r} does not fit in fixed field of {size} bytes")
    return encoded + b"\x00" * (size - len(encoded))


def _align(value: int, boundary: int) -> int:
    remainder = value % boundary
    return value if remainder == 0 else value + boundary - remainder
