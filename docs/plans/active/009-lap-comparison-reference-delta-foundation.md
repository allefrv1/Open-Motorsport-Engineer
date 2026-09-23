# Plan 009 — Lap Comparison Reference and Delta-Time Foundation

Status: **Active**

Started: 2026-09-22

## Objective

Define and implement the smallest deterministic two-lap comparison foundation satisfying REQ-005 and the relevant evidence requirements of REQ-006.

The first goal is not a rich analysis UI.

The goal is a trustworthy answer to:

> At a given explicit position around the lap, how much time separates Lap A and Lap B, and which source evidence produced that result?

## Requirements

Primary:

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence

Supporting domain/architecture:

- `docs/domain/session-run-lap.md`
- `docs/CORE_BELIEFS.md`
- `docs/ARCHITECTURE.md`
- `docs/QUALITY_ATTRIBUTES.md`

## Resolved numerical contract

The mandatory pre-implementation decision is complete.

Authoritative artifacts:

- ADR-0009 — Align initial lap comparisons by monotonic lap distance
- `docs/specs/lap-comparison-v0.1.md`

v0.1 uses:

- canonical `lap.distance` in metres;
- canonical `time.elapsed` in seconds;
- common overlap only;
- default 1.0 m analysis grid, parameterized;
- deterministic linear interpolation of elapsed time vs distance;
- `delta_B_vs_A = time_B - time_A`;
- no extrapolation;
- explicit not-ready outcomes instead of repair/guessing;
- conservative strictly increasing distance/time readiness for the first slice.

Plateau/duplicate-distance handling is deliberately deferred rather than hidden in the first algorithm.

## Initial comparison evidence

The result must be traceable to:

- dataset fingerprint(s);
- Session / Run / Lap identifiers;
- source channels used for time/reference;
- normalization/transformation identities when applicable;
- alignment algorithm id/version;
- parameters;
- comparison grid;
- output units.

## Observation boundary

The first slice may state deterministic facts such as:

- Lap B is +0.120 s relative to Lap A at distance d;
- Lap A has lower/higher measured speed at a position if that source evidence is requested and available.

It must not automatically claim:

- braking technique caused the loss;
- understeer caused the delta;
- setup X is better;
- driver Y made a mistake.

Those are later observations/hypotheses/engineering interpretation layers.

## TDD rule

The alignment decision is accepted and specified. Behavior is implemented test-first:

```text
REQ-005 ACCEPTANCE CRITERION
-> SYNTHETIC KNOWN LAPS
-> RED FOR MISSING COMPARISON BEHAVIOR
-> MINIMUM DETERMINISTIC IMPLEMENTATION
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

The synthetic laps must have analytically known expected delta-time behavior.

## First executable test targets

Tests should prove:

- explicit reference identity is present;
- same inputs/parameters produce identical delta;
- equal laps produce zero delta;
- a known constant/controlled time difference produces the expected sign/magnitude;
- missing required reference produces explicit not-ready/missing-evidence result;
- non-monotonic position is rejected;
- partial overlap behavior is explicit;
- provenance identifies both laps and algorithm version;
- context identifies Session / Run / Lap for both cases;
- no causal diagnosis is emitted.

## Evidence model relationship

REQ-006 should be used, not duplicated.

If the current evidence domain is insufficient for comparison provenance, extend it deliberately with tests rather than embedding opaque dictionaries in the comparison module.

## Architecture boundary

Lap comparison belongs in deterministic analysis/application layers.

It must not:

- parse source formats;
- repair ingestion data;
- guess channel semantics;
- use AI for delta calculations;
- depend on UI state;
- mutate source telemetry;
- silently choose between competing position channels.

## TDD execution evidence

Behavior tests were committed before the comparison/evidence production APIs.

Behavioral RED:

- OME CI #78 — comparison API absent;
- the test helper was then corrected to preserve an explicitly empty Lap identifier rather than replacing it with a default;
- OME CI #79 confirmed the same valid behavioral RED:
  `ImportError: cannot import name 'ComparisonIssueCode' from 'ome.analysis'`.

Implementation feedback:

- CI #81–#84 exposed implementation/style feedback while the tests remained unchanged;
- those runs are not treated as new behavioral RED cycles.

GREEN:

- OME CI #85 — the complete canonical verify passed with the minimum deterministic comparison implementation.

No acceptance test was weakened to obtain GREEN.

## Delivered foundation

The first comparison foundation now provides:

- typed canonical-series evidence;
- typed Session / Run / Lap evidence context;
- typed transformation evidence;
- typed comparison provenance;
- structured comparison-readiness issues;
- explicit `lap.distance [m]` and `time.elapsed [s]` requirements;
- conservative finite/strictly-increasing readiness;
- common-overlap calculation;
- deterministic parameterized distance grid;
- exact common-end inclusion;
- linear elapsed-time-vs-distance interpolation;
- `delta_B_vs_A = time_B - time_A`;
- explicit not-ready results instead of repair/guessing;
- algorithm identity/version `ome.lap-comparison.distance-linear / 0.1.0`;
- no causal diagnosis fields in the deterministic result.

Test module:

`tests/analysis/test_lap_comparison.py`

## Completion criteria

- positional/alignment decision documented and accepted;
- readiness contract documented;
- evidence/provenance contract documented;
- tests written before production comparison behavior;
- behavioral RED recorded;
- deterministic comparison implementation GREEN;
- REQ-005 acceptance criteria mapped to executable tests;
- relevant REQ-006 evidence chain executable;
- canonical CI GREEN.

## Explicitly out of scope

- automatic causal diagnosis;
- corner segmentation;
- driver scoring;
- setup recommendations;
- GPS track reconstruction;
- live telemetry comparison;
- AI explanation;
- polished comparison UI.
