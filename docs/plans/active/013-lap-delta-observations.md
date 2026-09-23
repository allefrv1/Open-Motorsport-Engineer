# Plan 013 — Lap Delta Gain/Loss Observations

Status: **Active**

Started: 2026-09-22

## Objective

Add the first deterministic Observation layer to OME by converting an already-valid lap delta curve into auditable gain/loss/neutral distance regions.

## Requirements

Primary:

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence

Authoritative contract:

- `docs/specs/lap-delta-observations-v0.1.md`

Supporting:

- ADR-0009
- `docs/specs/lap-comparison-v0.1.md`
- `docs/domain/provenance.md`

## Scope

Plan 013 adds:

- typed delta-region observation model;
- deterministic interval classification;
- contiguous region merging;
- explicit numerical-zero tolerance;
- structured not-ready outcomes;
- observation provenance linked to the complete base comparison.

## TDD rule

Production behavior is test-first:

```text
OBSERVATION SPEC
-> ANALYTIC DELTA-CURVE TESTS
-> VALID RED
-> MINIMUM REGION CLASSIFIER
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

## First executable test targets

Tests must prove:

- a known loss region is classified correctly;
- a known gain region is classified correctly;
- equal delta produces a neutral region;
- contiguous same-kind intervals merge;
- region total delta change equals end delta minus start delta;
- sign semantics remain B vs A;
- numerical zero tolerance is deterministic and explicit;
- invalid tolerance returns not-ready;
- malformed/non-monotonic/non-finite base data is rejected;
- incompatible base algorithm is rejected;
- provenance retains complete base comparison evidence;
- output is Observation only and contains no cause/hypothesis/interpretation.

## Architecture boundary

The observation layer may describe what the deterministic delta metric does.

It must not:

- attribute the change to speed/throttle/brake/steering;
- infer driver technique;
- segment corners;
- rank driver quality;
- diagnose vehicle behavior;
- recommend setup changes;
- use AI.

## TDD execution evidence

Pre-behavior harness cleanup:

- CI #127 — test formatting only.

Behavioral RED:

- CI #128;
- expected failure: `ImportError: cannot import name 'DeltaObservationEngine' from 'ome.analysis'`.

Post-implementation harness feedback:

- CI #129–#134 exposed formatting and exact-float test-fixture assertions;
- production semantics were not weakened to resolve those failures.

GREEN:

- CI #135;
- the complete canonical `verify` passed with deterministic gain/loss/neutral regions and typed observation provenance.

## Implementation traceability

Test module:

`tests/analysis/test_delta_observations.py`

Coverage proves:

- positive delta change -> B loss;
- negative delta change -> B gain;
- unchanged delta -> neutral;
- contiguous same-kind intervals merge;
- merged-region delta change is end minus start;
- numerical zero tolerance is explicit/deterministic;
- invalid tolerance is not-ready;
- missing/incompatible base comparison is not-ready;
- malformed/non-monotonic/non-finite base data is not repaired;
- observation provenance retains the complete base comparison;
- the result exposes no cause, hypothesis, engineering interpretation or recommendation.

## Completion criteria

- observation spec accepted;
- tests committed before behavior;
- behavioral RED recorded;
- deterministic classifier GREEN;
- typed observation provenance GREEN;
- REQ-005/006 traceability updated;
- canonical CI GREEN.

## Explicitly out of scope

- supporting-channel summaries;
- comparison report;
- UI;
- AI explanation;
- causal engineering analysis.
