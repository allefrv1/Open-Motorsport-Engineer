# Plan 027 — Lap Comparison Plateau Semantics Foundation

Status: **Active**

Started: 2026-09-24

## Objective

Evolve OME's deterministic lap-comparison engine so a trustworthy non-decreasing `lap.distance` series with exact projection plateaus can produce `time(distance)` without deleting samples, fabricating distance or losing the time accumulated while position is unchanged.

## Why this plan exists

Plan 026 successfully prepared Portland physical source Lap 4 and Lap 5 onto one canonical common track reference.

Real physical evidence contains exactly two candidate distance plateaus:

- projected index 495 at 564.4733986564207 m;
- projected index 512 at 575.6433508713768 m.

There is no true projected-distance decrease.

Common-track-reference v0.2 correctly preserves these plateaus.

The existing lap-comparison v0.1 contract still requires strictly increasing distance and therefore cannot consume the ready physical candidate evidence.

This is a numerical-analysis contract gap, not an ingestion or geometry defect.

## Normative contract

Follow:

- `docs/specs/lap-comparison-v0.2.md`;
- `docs/specs/common-track-reference-v0.2.md`;
- ADR-0009;
- REQ-005;
- REQ-006.

## Core rule

Distance may be non-decreasing:

```text
d[i] >= d[i-1]
```

Elapsed time must remain strictly increasing.

A true distance decrease remains not-ready.

An exact plateau is preserved as a vertical time interval at one distance.

OME must not resolve plateaus through:

- epsilon distance insertion;
- cumulative maximum;
- smoothing;
- sample deletion;
- sample reordering;
- averaging distance.

## Plateau-aware time(distance)

For one plateau run at distance `d_p`:

```text
(d_p, t_first)
...
(d_p, t_last)
```

with `t_last >= t_first`:

- interpolation from the previous unique distance toward `d_p` uses `t_first`;
- interpolation from `d_p` toward the next unique distance uses `t_last`;
- an exact grid query at `d_p` returns `t_last`.

This keeps the time spent on the plateau in all downstream distances while preserving the vertical discontinuity explicitly.

No source or canonical distance value is changed.

## Algorithm version

Algorithm id remains:

`ome.lap-comparison.distance-linear`

v0.2 version:

`0.2.0`

The version change is required because readiness/interpolation semantics change observably.

## TDD targets

Before production changes, tests must prove:

1. one exact plateau is accepted;
2. plateau input values remain unchanged;
3. exact query at the plateau uses the last elapsed time;
4. interpolation before the plateau uses the first plateau time;
5. interpolation after the plateau uses the last plateau time;
6. time spent on the plateau remains visible in downstream delta;
7. multiple separated plateaus are deterministic;
8. true distance decrease remains not-ready;
9. elapsed time must still be strictly increasing;
10. equal no-plateau inputs preserve existing v0.1 numerical output;
11. algorithm/provenance reports version `0.2.0`;
12. Portland Plan 026 prepared Lap 4 / Lap 5 reaches base comparison readiness.

## Boundary

Plan 027 changes only deterministic base lap comparison semantics.

It does not:

- normalize Traqmate supporting channels;
- map brake/throttle semantics;
- create the physical `ComparisonReportRequest`;
- modify common-track-reference geometry;
- change source telemetry;
- add API/frontend behavior;
- use AI.

## Layered execution packet

### Prompt Engineering

Objective:

> Make time-vs-distance comparison mathematically explicit for preserved physical distance plateaus.

### Context Engineering

Required:

- lap-comparison v0.1 implementation/tests;
- Plan 026 Portland preparation;
- common-track-reference v0.2;
- ADR-0009.

Context readiness: **ready**.

### Harness Engineering

Test-first analysis coverage; completion requires canonical `verify`.

### Loop Engineering

```text
accepted lap-comparison v0.2 spec
-> focused plateau tests
-> behavioral RED
-> minimum plateau-aware interpolation
-> GREEN
-> Portland integration regression
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

## TDD execution evidence

Behavioral RED:

- CI #349 — exact plateaus remained not-ready, algorithm provenance still reported `0.1.0`, and `DISTANCE_DECREASES` did not exist;
- the failure reached the focused comparison tests and demonstrated the missing v0.2 behavior.

Compatibility regression exposed during GREEN:

- CI #351 — the base comparison produced v0.2 provenance, but continuous overlays, gear overlays and delta observations still required base version `0.1.0`;
- no downstream numerical algorithm changed;
- their accepted specs/compatibility gates were updated to consume the v0.2 base comparison.

GREEN:

- CI #354 — full canonical verification passed for plateau-aware comparison v0.2 and all existing downstream comparison/report consumers;
- CI #355 — full canonical verification passed with the Portland Plan 026 physical-preparation integration regression.

Tests were not weakened to obtain GREEN.

## Implementation traceability

Primary comparison coverage:

`tests/analysis/test_lap_comparison.py`

Plan 027 tests prove:

- exact plateaus are ready and source/canonical inputs remain unchanged;
- interpolation before a plateau uses first-arrival time;
- exact plateau distance uses last-arrival time;
- interpolation after a plateau retains dwell time;
- downstream delta preserves plateau dwell time;
- multiple plateaus are deterministic;
- true distance decreases return `distance_decreases`;
- elapsed time remains strictly increasing;
- no-plateau numerical outputs remain compatible with v0.1;
- algorithm provenance reports `0.2.0`.

Physical integration coverage:

`tests/application/test_physical_track_reference_preparation.py`

The Portland Lap 4 reference / Lap 5 candidate preparation now reaches base lap-comparison v0.2 readiness while preserving the two measured common-reference plateaus.

## Completion criteria

- Plan 026 archived;
- lap-comparison v0.2 spec accepted;
- tests before production behavior;
- behavioral RED recorded;
- plateau-aware comparison GREEN;
- true backtracking still blocked;
- Portland physical base comparison ready;
- provenance/version updated;
- canonical CI GREEN.

## Next plan boundary

After Plan 027, Plan 028 may compose the prepared physical laps into `ComparisonReportRequest` using:

- canonical `lap.distance`;
- lap-relative `time.elapsed`;
- only explicitly verified supporting-channel semantics;
- Missing Evidence for unsupported/absent channels.

## Explicitly out of scope

- throttle inference from `Accel (calc)`;
- brake-pedal inference from `Brake (calc)`;
- steering inference;
- fuzzy channel mapping;
- report/API/frontend changes;
- AI.
