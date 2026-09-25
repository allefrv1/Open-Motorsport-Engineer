# Traqmate Physical Supporting Channels Specification v0.1

Status: **Accepted for Plan 029**

Date: 2026-09-25

## Purpose

Define the smallest source-semantic contract that may enrich the first Portland physical-car comparison report without inventing driver-input meaning.

This specification promotes only source channels whose semantics are sufficiently explicit for deterministic canonical evidence.

## Source family

Source type:

`traqmate-trackvision-csv`

Initial physical fixture:

`fixtures/public/exit-speed/traqmate-portland-laps-4-5.csv`

The fixture remains immutable source evidence.

## Supported source channels

### Velocity (MPH)

Source identifier/name:

`Velocity (MPH)`

Canonical concept:

`vehicle.speed`

Source unit:

`mph`

Canonical unit:

`m/s`

Conversion:

```text
m/s = mph * 0.44704
```

The mapping asserts only that this Trackvision field is Traqmate's exported vehicle velocity in MPH.

OME does **not** relabel it as ECU speed, wheel speed or another more specific speed method.

Rule identity:

`ome.traqmate.vehicle-speed`

Rule version:

`0.1.0`

Conversion identity:

`ome.conversion.mph_to_mps`

### RPMs

Source identifier/name:

`RPMs`

Canonical concept:

`engine.speed`

Source semantic unit:

`rpm`

Canonical unit:

`rad/s`

Conversion:

```text
rad/s = rpm * 2*pi/60
```

The Trackvision CSV header does not carry a separate unit row for this field. The mapping therefore retains the original source unit metadata exactly as imported and records the RPM semantic assumption in the normalization rule/provenance.

Public Traqmate documentation describes RPM as data collected through TraqData/RPM inputs.

Rule identity:

`ome.traqmate.engine-speed`

Rule version:

`0.1.0`

### Gear

Source identifier/name:

`Gear`

Canonical concept:

`transmission.gear`

Canonical representation:

discrete integer value.

Important semantic qualification:

Traqview documentation allows gear to be assigned from known track position or derived from RPM, tire size and final-drive/gearing information.

Therefore OME must not present this field as a directly measured selector sensor.

Semantic id:

`transmission.gear.traqmate_derived_or_assigned`

Rule identity:

`ome.traqmate.gear`

Rule version:

`0.1.0`

## Explicitly unsupported mappings

The following are not promoted in v0.1:

### Accel (calc)

Do not map to `driver.throttle`.

Calculated longitudinal acceleration is not driver throttle demand/position.

### Brake (calc)

Do not map to `driver.brake`.

A calculated braking signal/G value is not equivalent to pedal position, pedal force, master-cylinder pressure or brake pressure.

### Steering

No trustworthy Portland steering source is promoted by this profile.

Therefore `driver.steering` remains Missing Evidence.

## Source-lap ownership and closing-boundary evidence

The accepted Traqmate lap-window contract defines:

```text
owned samples = [start_index, end_index_exclusive)
closing boundary = closing_boundary_index == end_index_exclusive
```

The closing-boundary row is owned by the next source lap.

For comparison overlays, v0.1 may use the value at that row **only as shared start/finish boundary evidence**.

This does not reassign source-lap ownership.

The prepared supporting series consists of:

1. every owned source sample in the selected lap;
2. exactly one closing-boundary source sample at the accepted shared start/finish instant.

The preparation provenance must record:

- source window start index;
- source window end index exclusive;
- closing boundary source index;
- boundary role:
  `shared_start_finish_evidence`;
- source session-time start;
- source channel identifier/name;
- normalization rule/conversion identity.

Transformation identity:

`ome.preparation.traqmate-supporting-lap-window`

Version:

`0.1.0`

## Lap-relative time

Supporting overlay timestamps are derived from explicit source `Elapsed Time`:

```text
lap_relative_time[i] = source_elapsed_time[i] - source_elapsed_time[start_index]
```

The supporting series begins at exactly `0.0 s` and includes the closing-boundary timestamp.

The service does not resample supporting source values.

## Normalization boundary

Generic normalization remains deterministic and source-preserving.

Plan 029 may add one generic conversion primitive:

`mph_to_mps`

The Traqmate mapping rules remain source-specific.

Normalization must not:

- infer channels by fuzzy name;
- turn `Accel (calc)` into throttle;
- turn `Brake (calc)` into driver brake;
- claim Gear is directly measured.

## Report composition

Plan 029 starts from the successful Plan 028 `ComparisonReportRequest`.

When the Portland evidence is ready, the enriched request supplies:

continuous:

- `vehicle.speed`;
- `engine.speed`.

discrete:

- `transmission.gear`.

The report still leaves these concepts explicitly not-ready:

- `driver.throttle`;
- `driver.brake`;
- `driver.steering`.

## Readiness

Return explicit not-ready evidence for preparation-level contract failures such as:

- dataset/preparation fingerprint mismatch;
- base comparison request does not refer to the same lap contexts;
- source window outside the normalized series;
- closing boundary outside the source series;
- supporting source time/value length mismatch;
- non-finite or non-increasing prepared supporting timestamps;
- invalid numeric speed/RPM evidence;
- invalid gear evidence;
- ambiguous normalization mapping for a supported concept.

A missing optional supported channel may remain absent and be surfaced by the report as Missing Evidence rather than causing the entire base report to fail.

## Determinism and immutability

Equivalent source/preparation evidence produces equivalent enriched report requests.

Do not mutate:

- imported source telemetry;
- source lap windows;
- physical track-reference preparation;
- Plan 028 comparison request;
- normalized source values.

## Evidence classification

`Velocity (MPH)` and `RPMs` are source data transformed deterministically into canonical physical units.

`Gear` is source data whose source-system derivation/assignment semantics remain explicit.

No promoted supporting channel constitutes a causal engineering interpretation.

## External semantic references

Traqmate / Traqview & TraqStudio User Manual v3.40:

https://www.stableenergies.com/specs/Traqview_TraqStudio_User_Manual_3.40.pdf

Relevant public documentation describes:

- Velocity-vs-Distance as a direct comparison channel;
- RPM collection through TraqData/RPM inputs;
- Gear as assignable from track position or determinable from RPM/tire/final-drive/gearing information.

## Related artifacts

- Plan 021 — Traqmate Trackvision CSV Adapter Foundation
- Plan 025 — Physical-Car Lap Window Selection Foundation
- Plan 026 — Physical-Car Track Reference Preparation Foundation
- Plan 028 — Physical-Car Comparison Request Foundation
- Lap Comparison Report v0.1
- Canonical Telemetry Concepts v0.1
- REQ-005
- REQ-006
