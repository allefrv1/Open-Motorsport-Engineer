# Physical-Car Comparison Preparation Specification v0.1

Status: **Accepted for Plan 028**

Date: 2026-09-25

## Purpose

Define the smallest deterministic application bridge from a ready `PhysicalTrackReferencePreparation` artifact to the existing `ComparisonReportRequest` contract.

The first goal is a trustworthy physical-car base comparison/report.

This specification deliberately does not infer unsupported Traqmate driver-input semantics.

## Input

One ready `PhysicalTrackReferencePreparation` containing:

- explicit reference and candidate LapEvidenceContext;
- canonical reference `lap.distance [m]`;
- canonical candidate common-reference `lap.distance [m]`;
- reference and candidate physical trajectories;
- source elapsed-time evidence;
- complete geometry/projection provenance.

Reference selection remains caller-owned upstream.

## Required base evidence

Plan 028 prepares only the required base comparison evidence:

- `lap.distance [m]`;
- `time.elapsed [s]`.

The canonical distance series are reused exactly from Plan 026/027.

No distance sample is rewritten, deduplicated or repaired.

## Lap-relative elapsed time

Traqmate `Elapsed Time` is session-relative source time.

For each explicitly selected physical lap trajectory:

```text
lap_relative_time[i] = source_elapsed_time[i] - source_elapsed_time[0]
```

Requirements:

- source timestamps are finite;
- source timestamps are strictly increasing;
- at least two samples exist;
- result begins at exactly `0.0 s`;
- result length exactly matches the corresponding canonical lap-distance series.

Transformation identity:

`ome.preparation.lap-relative-elapsed-time`

Version:

`0.1.0`

The resulting `CanonicalSeriesEvidence` must retain:

- dataset fingerprint;
- source `Elapsed Time` channel identifier/name;
- canonical concept `time.elapsed`;
- unit `s`;
- transformation identity/version;
- source start time as an explicit parameter.

The boundary-only closing timestamp may participate in lap-time closure because Plan 026 explicitly carried it as time/geometry boundary evidence.

It is not relabeled as a telemetry sample owned by the prior source lap.

## Comparison request

Create one `ComparisonReportRequest` containing:

- `LapComparisonRequest`;
- prepared reference/candidate contexts;
- exact prepared canonical distance series;
- derived lap-relative elapsed-time series;
- caller-supplied positive finite `grid_step_m`.

The service must not call or duplicate comparison/report algorithms.

## Supporting evidence policy

Plan 028 intentionally supplies no canonical supporting channel pairs.

The existing `ComparisonReportService` must therefore expose Missing Evidence/not-ready summaries for:

- vehicle speed;
- throttle;
- brake;
- steering;
- engine speed;
- gear.

This is a truthful intermediate product.

### Why speed/gear are deferred

The Portland source exposes fields including:

- `Velocity (MPH)`;
- `RPMs`;
- `Gear`;
- `Brake (calc)`;
- `Accel (calc)`.

Before they enter canonical comparison evidence, a separate accepted source-semantic preparation contract must define:

- exact source meaning;
- unit conversion;
- derived-vs-measured identity where relevant;
- closing-boundary ownership/coverage for optional overlays.

Do not infer:

- throttle from `Accel (calc)`;
- brake pedal position from `Brake (calc)`;
- steering from unrelated channels.

## Readiness

Return explicit not-ready evidence when:

- preparation dataset fingerprint is empty;
- reference/candidate contexts do not match the preparation dataset fingerprint;
- reference/candidate context identifies the same lap;
- distance evidence fingerprint does not match the preparation dataset;
- distance/time series lengths differ;
- physical timestamp series have fewer than two points;
- timestamps are non-finite or not strictly increasing;
- grid step is non-finite or non-positive.

The service does not repair input.

Base numerical distance readiness remains owned by `LapComparisonEngine`.

## Output

Success contains at least:

- `ComparisonReportRequest`;
- preparation dataset fingerprint;
- explicit reference/candidate contexts;
- preparation algorithm identity/version.

Preparation identity:

`ome.preparation.physical-comparison-request`

Version:

`0.1.0`

## Determinism and immutability

Equivalent preparation evidence and parameters produce equivalent requests.

The service must not mutate:

- imported source telemetry;
- source lap windows;
- Plan 026 preparation artifacts;
- canonical distance values;
- source timestamps/evidence.

## End-to-end acceptance target

Using the licensed Portland fixture:

```text
Traqmate import
-> Lap 4 / Lap 5 explicit windows
-> physical common-reference preparation
-> physical comparison request preparation
-> ComparisonReportService
-> ComparisonReportSuccess
```

Expected report properties:

- base algorithm `ome.lap-comparison.distance-linear / 0.2.0`;
- reference context is source Lap 4;
- candidate context is source Lap 5;
- delta observations are available;
- six supporting concepts remain explicit Missing Evidence/not-ready;
- no causal interpretation is produced.

## Architecture boundary

Physical comparison preparation belongs in application/preparation.

It may depend on existing physical preparation and report request contracts.

It must not:

- parse source files;
- select laps;
- infer Session/Run context;
- change geometry;
- normalize supporting vehicle channels;
- calculate the report itself;
- add API/frontend behavior;
- use AI.

## Related artifacts

- Plan 026 — Physical-Car Track Reference Preparation
- Plan 027 — Lap Comparison Plateau Semantics
- Lap Comparison Specification v0.2
- Physical-Car Track Reference Preparation v0.1
- Lap Comparison Report v0.1
- REQ-005
- REQ-006
