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
