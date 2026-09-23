# Plan 009 — Lap Comparison Reference and Delta-Time Foundation

Status: **Completed**

Started: 2026-09-22

Completed: 2026-09-22

## Objective

Implement the smallest deterministic two-lap comparison foundation satisfying the reference/delta portion of REQ-005 and the relevant evidence requirements of REQ-006.

## Numerical contract

Authoritative inputs:

- ADR-0009 — align initial lap comparisons by monotonic lap distance;
- `docs/specs/lap-comparison-v0.1.md`.

Implemented baseline:

- `lap.distance` in metres;
- `time.elapsed` in seconds;
- common positive distance interval only;
- parameterized distance grid, default 1.0 m;
- exact common endpoint retained;
- linear elapsed-time-vs-distance interpolation;
- `delta_B_vs_A = time_B - time_A`;
- no extrapolation;
- strict finite/increasing readiness in v0.1;
- explicit not-ready outcomes instead of repair or guessing.

## Delivered

Production analysis/evidence now includes:

- typed canonical-series evidence;
- transformation evidence;
- Session / Run / Lap evidence context;
- comparison provenance;
- structured readiness issue codes;
- `LapComparisonEngine`;
- deterministic distance-grid construction;
- deterministic linear interpolation;
- deterministic delta-time output;
- algorithm identity/version:
  - `ome.lap-comparison.distance-linear`;
  - `0.1.0`;
- no cause/hypothesis/engineering-interpretation fields in the deterministic result.

## TDD evidence

Tests were committed before production comparison behavior.

Behavioral RED:

- CI #78 — comparison API absent;
- the test helper was corrected while still RED so an explicit empty Lap id remained empty;
- CI #79 confirmed the valid behavioral RED:
  `ImportError: cannot import name 'ComparisonIssueCode' from 'ome.analysis'`.

Implementation feedback:

- CI #81–#84 exposed implementation/lint/format feedback while acceptance tests remained intact.

GREEN:

- CI #85 — complete canonical verify passed.

Final traceability verification:

- CI #87 — complete canonical verify passed after requirement/plan evidence updates.

No acceptance test was weakened to obtain GREEN.

## Acceptance evidence

Test module:

`tests/analysis/test_lap_comparison.py`

The tests cover:

- explicit reference identity;
- deterministic known delta/sign convention;
- equal-lap zero delta;
- exact common-end grid behavior;
- partial-overlap behavior;
- missing distance evidence;
- incompatible distance concept;
- non-monotonic distance;
- non-monotonic elapsed time;
- non-finite distance;
- no common interval;
- invalid grid step;
- algorithm/context/source/transformation provenance;
- missing provenance;
- no causal diagnosis fields.

## Requirement scope

Plan 009 implements the **reference and delta-time foundation** of REQ-005.

REQ-005 remains broader.

Still deferred:

- continuous speed/throttle/steering/RPM overlays;
- safe brake comparison semantics;
- discrete gear alignment;
- higher-level deterministic observations;
- comparison report/UI.

REQ-006 is implemented for the Plan 009 metric through typed provenance, but broader findings/observations remain future work.

## Merge evidence

PR #22 was squash-merged as:

`84af6131f2c86096885ae220893982d10ca026bc`

## Completion assessment

All Plan 009 completion criteria are satisfied.
