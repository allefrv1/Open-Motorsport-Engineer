# Plan 026 — Physical-Car Track Reference Preparation Foundation

Status: **Active**

Started: 2026-09-24

## Objective

Implement the smallest deterministic application preparation bridge from two explicitly selected Traqmate source lap windows to canonical reference/candidate `lap.distance` evidence.

## Why this plan exists

OME now has:

- physical-car Traqmate ingestion;
- explicit source-lap windows;
- WGS84 GPS path distance;
- common track-reference projection;
- canonical candidate `track.reference_distance -> lap.distance` preparation.

The remaining geometry-preparation gap is to compose these capabilities without:

- moving lap selection back into ingestion;
- automatically selecting a reference lap;
- falsely aliasing arbitrary `gps.path_distance` as canonical `lap.distance`.

## Normative contract

Follow:

- `docs/specs/physical-car-reference-preparation-v0.1.md`;
- `docs/specs/traqmate-lap-window-v0.1.md`;
- `docs/specs/gps-path-distance-v0.1.md`;
- `docs/specs/common-track-reference-v0.1.md`;
- ADR-0009.

## Explicit reference choice

The caller supplies:

- one ready reference `SourceLapWindow`;
- one ready candidate `SourceLapWindow`;
- explicit trusted `LapEvidenceContext` for each.

Do not choose a reference automatically.

## Key geometry rule

Selected telemetry remains:

```text
[start_index, end_index_exclusive)
```

For derived trajectory closure only, append the source GPS/time point at:

`closing_boundary_index`

as boundary-only evidence.

Do not mutate or relabel the source row.

## New preparation bridge

Add the minimum application contract needed to:

1. validate supplied windows/contexts against the imported dataset;
2. extract numeric time/latitude/longitude evidence;
3. include closing-boundary evidence in derived trajectories;
4. derive reference `gps.path_distance`;
5. explicitly map the selected reference path to canonical `lap.distance`;
6. project the candidate onto the explicit reference;
7. reuse `prepare_track_reference_lap_distance` for candidate canonical distance;
8. preserve complete provenance.

## Reference-distance decision

Generic `gps.path_distance -> lap.distance` remains prohibited.

The accepted narrow bridge is:

```text
explicit caller-selected reference lap
+ ready GPSPathDistanceSuccess
-> ome.preparation.explicit-reference-path-to-lap-distance/0.1.0
-> lap.distance
```

This transformation must be visible in evidence.

## TDD targets

Before production implementation, tests should prove:

1. Portland Lap 4 reference / Lap 5 candidate preparation succeeds;
2. reference trajectory includes exactly one boundary-only closing point;
3. candidate trajectory includes exactly one boundary-only closing point;
4. source window sample counts remain unchanged;
5. reference canonical distance begins at 0 and ends at ready reference path length;
6. candidate canonical distance comes from common-reference projection;
7. reference mapping provenance identifies explicit reference selection;
8. candidate provenance preserves reference/candidate identity;
9. repeated preparation is deterministic;
10. source dataset remains unchanged;
11. same reference/candidate window is not-ready;
12. mismatched dataset fingerprint/context is not-ready;
13. missing/invalid GPS/time evidence is not-ready;
14. downstream GPS/common-reference not-ready outcomes are surfaced, not repaired.

## Architecture boundary

Physical track-reference preparation belongs in application/preparation.

It may depend on accepted analysis engines.

It must not:

- modify ingestion;
- auto-select laps;
- build delta-time comparison;
- normalize vehicle channels;
- create reports;
- add API/frontend behavior;
- use AI.

## Layered execution packet

### Prompt Engineering

Objective:

> Prepare one explicit physical reference lap and one explicit candidate lap onto canonical common `lap.distance` evidence.

### Context Engineering

Required:

- Plan 025 output contract;
- this plan/spec;
- GPS path-distance contract;
- common-track-reference contract;
- Portland fixture.

Context readiness: **ready**.

### Harness Engineering

Test-first application coverage; completion requires canonical `verify`.

### Loop Engineering

```text
accepted preparation spec
-> focused tests
-> behavioral RED
-> minimum preparation implementation
-> GREEN
-> source/provenance regression
-> full verify
```

### Graph Engineering

```text
PROMPT READY          = yes
CONTEXT READY         = yes
MATERIAL DECISION GAP = no
BEHAVIOR CHANGE       = yes
TESTABLE CONTRACT     = yes
NEXT STATE            = tests -> RED
```

Human gate reopens if implementation would need to:

- auto-select a reference lap;
- create inferred Session/Run identities;
- repair non-monotonic projection;
- discard GPS points;
- equate arbitrary GPS path with canonical lap distance.

## Completion criteria

- Plan 025 archived;
- accepted physical reference-preparation v0.1 spec;
- tests before production behavior;
- behavioral RED recorded;
- Portland Lap 4 -> Lap 5 preparation GREEN;
- explicit reference-path canonical mapping proven;
- candidate common-reference mapping proven;
- source dataset/window immutability proven;
- canonical CI GREEN.

## Next plan boundary

After Plan 026, a separate composition plan may prepare:

- canonical elapsed time;
- speed/throttle/brake/steering/RPM/gear;
- `ComparisonReportRequest`;

from the ready physical reference/candidate preparation artifact.

## Explicitly out of scope

- fastest/best lap selection;
- Session/Run inference;
- comparison delta/report;
- supporting-channel normalization;
- HTTP/frontend changes;
- AI.
