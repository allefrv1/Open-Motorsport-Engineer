# iRacing .ibt Binary Contract for Plan 007

Status: **Reviewed research**

Verified: 2026-09-22

## Purpose

Record the minimum independently verified binary contract required to create project-owned test fixtures and implement the first OME iRacing `.ibt` adapter.

This document is informative research.

The production parser remains governed by accepted OME requirements, architecture and Plan 007.

## Source basis

Primary public SDK evidence:

- iRacing SDK definitions mirror:
  - https://github.com/vipoo/irsdk/blob/master/irsdk_defines.h
- iRacing SDK disk client mirror:
  - https://github.com/vipoo/irsdk/blob/master/irsdk_diskclient.cpp
- iRacing release notes confirming the disk-client wrapper:
  - https://www.iracing.com/2016-season-3-release-notes/
- iRacing 2017 Season 1 release notes defining 360 Hz time-subdivision arrays:
  - https://www.iracing.com/2017-season-1-release-notes/

Independent implementation cross-checks:

- pyirsdk:
  - https://github.com/kutu/pyirsdk/blob/master/irsdk.py
- real-file layout cross-check documented by shakedown-engineer:
  - https://github.com/0x0Anna/shakedown-engineer/blob/main/PROJECT_PLAN.md

OME does not copy parser implementation from these projects.

They are used to verify the public binary contract.

## High-level file structure

The public IRSDK describes logged telemetry as:

```text
irsdk_header
irsdk_diskSubHeader
...
session info bytes
variable-header array
...
telemetry record buffer
telemetry record buffer
...
```

Absolute offsets stored in the header locate the session info, variable-header table and first telemetry record.

The iRacing SDK disk client reads telemetry records with a fixed stride equal to `bufLen`.

## IRSDK version

The reviewed SDK definitions declare:

```text
IRSDK_VER = 2
```

Plan 007 should initially support the verified version-2 contract only.

Unsupported versions must fail explicitly rather than being interpreted optimistically.

## Main header

The reviewed layout occupies 112 bytes.

The first 48 bytes are twelve little-endian 32-bit integers:

| Offset | Field |
|---:|---|
| 0 | version |
| 4 | status |
| 8 | tickRate |
| 12 | sessionInfoUpdate |
| 16 | sessionInfoLen |
| 20 | sessionInfoOffset |
| 24 | numVars |
| 28 | varHeaderOffset |
| 32 | numBuf |
| 36 | bufLen |
| 40 | padding |
| 44 | padding |

Four `irsdk_varBuf` entries follow, each 16 bytes:

```text
tickCount  : int32
bufOffset  : int32
padding[2] : int32[2]
```

The first entry begins at offset 48.

Therefore:

```text
48 + (4 * 16) = 112 bytes
```

For disk telemetry, the SDK disk client seeks to `varBuf[0].bufOffset` and then reads consecutive records of `bufLen` bytes.

## Disk sub-header

The disk sub-header begins immediately after the 112-byte main header.

The public SDK defines:

```text
sessionStartDate
sessionStartTime
sessionEndTime
sessionLapCount
sessionRecordCount
```

Reviewed readers represent this as a 32-byte structure with:

- 8-byte start-date slot;
- 8-byte start time;
- 8-byte end time;
- 4-byte lap count;
- 4-byte record count.

For OME's synthetic fixture, use an unsigned 64-bit start-date slot followed by two IEEE-754 doubles and two signed 32-bit integers.

The first adapter does not need to interpret calendar semantics from `sessionStartDate`; it only needs to preserve/read the disk structure safely.

## Variable header

Each `irsdk_varHeader` occupies 144 bytes:

| Offset | Field | Size |
|---:|---|---:|
| 0 | type | 4 |
| 4 | offset in one telemetry record | 4 |
| 8 | count | 4 |
| 12 | countAsTime | 1 |
| 13 | padding | 3 |
| 16 | name | 32 |
| 48 | description | 64 |
| 112 | unit | 32 |

Strings are fixed-width null-padded source metadata.

OME must preserve the decoded source-facing:

- name;
- description;
- unit;
- declared variable type;
- count.

## Variable types

The reviewed IRSDK type mapping is:

| Code | Type | Scalar size |
|---:|---|---:|
| 0 | char | 1 |
| 1 | bool | 1 |
| 2 | int | 4 |
| 3 | bitField | 4 |
| 4 | float | 4 |
| 5 | double | 8 |

All fixture/parser behavior in Plan 007 should be explicitly little-endian.

## Session information

The main header provides:

- `sessionInfoOffset`;
- `sessionInfoLen`.

The SDK describes the session-info region as YAML-formatted source metadata.

The first OME adapter should preserve this source metadata without requiring a complete semantic YAML model.

Parsing selected session fields is a separate behavior and must be driven by an accepted requirement/test.

## Telemetry records

The disk sub-header supplies `sessionRecordCount`.

The main header supplies:

- first record offset through `varBuf[0].bufOffset`;
- record stride through `bufLen`.

A scalar value is read at:

```text
varBuf[0].bufOffset
+ record_index * bufLen
+ variable.offset
```

The variable type and count determine how many bytes belong to the source value.

## Time basis for the first OME adapter

The existing OME ImportedTelemetryDataset requires explicit timestamps for every SourceChannel.

Plan 007 must not silently synthesize time from `tickRate`.

The project-owned first fixture will therefore include the standard scalar `SessionTime` source variable.

The adapter may use the recorded `SessionTime` values as the shared source timestamp series while preserving `SessionTime` itself as a source channel.

If a future valid `.ibt` lacks a usable explicit time channel, behavior must be specified/tested separately rather than inferred silently.

## Array variables

IRSDK supports `count > 1`.

iRacing's 2017 Season 1 release notes document 360 Hz telemetry as a six-element array whose variable-header flag indicates that the elements are a subdivision of time.

For a normal 60 Hz record containing a `count=6`, `countAsTime=true` source variable, the six source samples represent 360 Hz source acquisition.

OME must not silently flatten or discard this structure.

The first scalar TDD slice intentionally rejected arrays until real-file evidence could drive the domain extension.

### Real-file validation result

External validation used the public `teamjorge/ibt` file:

`.testing/valid_test_file.ibt`

Observed without copying the binary into OME:

- file size: 471,844 bytes;
- IRSDK version: 2;
- tick rate: 60 Hz;
- 276 source variables;
- 390 records;
- one recorded lap;
- representative scalar channels include `SessionTime`, `Speed`, `Throttle`, `Brake`, `SteeringWheelAngle`, `RPM`, `Gear`, `Lap`, `LapDist` and `LapDistPct`;
- exactly one array variable:
  - `SteeringWheelTorque_ST`;
  - type `float`;
  - count `6`;
  - `countAsTime=true`;
  - source description: output torque on steering shaft at 360 Hz;
  - unit `N*m`.

This proves that rejecting every file containing an array is too restrictive for a real iRacing adapter.

The next TDD increment must extend OME source values to preserve fixed source arrays as arrays, without flattening them onto a fabricated timeline.

For `countAsTime=true`, the channel may expose source acquisition rate as:

`tickRate * count`

while retaining record timestamps and the grouped source array. Expanding those grouped samples to a 360 Hz timeline is a later explicit transformation, not ingestion-time resampling.

## Project-owned fixture strategy

Canonical CI will not download or vendor third-party iRacing recordings.

Instead, test support code will generate a minimal deterministic `.ibt` byte stream from the verified contract above.

The synthetic fixture should contain:

- IRSDK version 2;
- one disk buffer descriptor;
- a small UTF-8 session-info payload;
- several scalar variable headers;
- multiple records;
- explicit `SessionTime`;
- representative channels such as:
  - Speed;
  - Throttle;
  - Brake;
  - SteeringWheelAngle;
  - RPM;
  - Gear;
  - Lap;
  - LapDistPct.

The fixture is project-owned test data.

It must be constructed independently of the production parser implementation.

## Real-file validation

After the synthetic RED/GREEN parser cycle is complete, validate against a real publicly accessible iRacing `.ibt` file when feasible.

Do not add that third-party binary to the repository unless redistribution rights are independently established.

## Safety rules for the parser

Reject rather than guess when:

- file is shorter than required fixed headers;
- version is unsupported;
- offsets are negative/outside file bounds;
- variable-header table exceeds file bounds;
- variable type is unsupported;
- count is invalid;
- a scalar variable extends beyond `bufLen`;
- record count/stride exceeds file bounds;
- required explicit source time cannot be read.

Do not normalize units, rename channels, repair data or infer engineering meaning during import.

## Conclusion

The format contract is sufficiently defined to create an independent project-owned scalar `.ibt` fixture and begin Plan 007 with a genuine TDD RED state.

Array-value representation remains an explicit known limitation rather than a hidden parser shortcut.
