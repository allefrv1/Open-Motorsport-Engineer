# Plan 026 — Physical-Car Track Reference Preparation Foundation

Status: **Completed**

Started: 2026-09-24

Completed: 2026-09-24

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
- `docs/specs/common-track-reference-v0.2.md`;
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
14. exact common-reference plateaus are preserved without repair;
15. true projected-distance decreases remain downstream not-ready outcomes.

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
NEXT STATE            = completion -> final verify
```

Human gate reopens if implementation would need to:

- auto-select a reference lap;
- create inferred Session/Run identities;
- repair non-monotonic projection;
- discard GPS points;
- equate arbitrary GPS path with canonical lap distance.

## TDD execution evidence

Initial application behavior:

- CI #326 — harness formatting only; not counted as behavioral RED;
- CI #327 — behavioral RED: `ome.application.physical_track_reference` did not exist;
- CI #328 / #329 — implementation formatting/lint cleanup;
- CI #330 — real Portland behavior exposed a common-reference readiness failure instead of being hidden.

Physical-data characterization:

- CI #332 characterized the Portland Lap 5 projection;
- there was no true local backtracking after seam unwrap;
- exactly two equal-distance plateaus were observed:
  - projected index 495 at 564.4733986564207 m;
  - projected index 512 at 575.6433508713768 m;
- the end of the projected trajectory remained forward and close to the reference length.

Common-reference v0.2 TDD increment:

- CI #336 — RED: exact plateaus were still rejected, the decrease-specific issue code was absent and provenance still reported algorithm v0.1;
- the accepted `docs/specs/common-track-reference-v0.2.md` contract was introduced before changing production behavior;
- v0.2 preserves equal projected distances exactly and rejects only true decreases;
- no epsilon, clamp, smoothing, deletion or reordering was introduced.

Explicit closed-topology TDD increment:

- physical Portland reference endpoints are not required to have identical GPS coordinates;
- lap closure comes from trusted source-lap boundary evidence;
- CI #341 — RED: `TrackReferenceLap.is_closed` and topology provenance were absent;
- production now carries explicit closed-reference topology and records `reference_is_closed` in common-reference provenance;
- exact endpoint equality remains only a compatibility fallback for existing synthetic fixtures.

GREEN:

- CI #343 — full canonical verification passed after v0.2 plateau/topology implementation;
- CI #344 — final clean verification passed after removing temporary characterization code and retaining the Portland plateau regression.

Tests were not weakened to obtain GREEN.

## Implementation traceability

Primary Plan 026 coverage:

`tests/application/test_physical_track_reference_preparation.py`

Supporting common-reference v0.2 coverage:

`tests/analysis/test_common_track_reference.py`

The final tests prove:

- explicit Portland Lap 4 reference / Lap 5 candidate preparation;
- exactly one closing-boundary evidence point per derived physical trajectory;
- source windows and source telemetry remain immutable;
- explicit selected-reference `gps.path_distance -> lap.distance` mapping;
- candidate common-reference projection and canonical mapping;
- deterministic repeatability;
- source/context/window mismatch failures;
- missing/invalid physical source evidence failures;
- explicit closed-lap topology;
- exact projection plateaus preserved;
- true projected-distance decreases remain not-ready.

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

## Merge evidence

PR #63 was squash-merged as:

`1263ff85ce9a9d9b83147936b8c2632d6c0b403a`

Final canonical verification before merge:

- OME CI #345 — success.

## Completion assessment

All Plan 026 completion criteria are satisfied.

The physical Portland candidate retains two exact common-reference plateaus as measured derived evidence. That downstream comparison-readiness issue is deliberately handed to Plan 027 rather than repaired inside Plan 026.

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
