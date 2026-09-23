# Plan 014 — Lap Comparison Report Bundle

Status: **Active**

Started: 2026-09-22

## Objective

Create the first integrated deterministic comparison artifact for application/API/UI consumption by composing the existing lap comparison, delta-observation and supporting-overlay engines.

## Requirements

Primary:

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
- MVP — first vertical slice

Authoritative contract:

- `docs/specs/lap-comparison-report-v0.1.md`

## Why this plan exists

The numerical engines are intentionally separate and testable.

A UI should not need to know which engine must be called first or how to reconcile six different evidence outcomes.

Plan 014 adds an application-level composition boundary without moving numerical logic out of the analysis modules.

## Scope

Implement:

- typed report request;
- typed report success/not-ready outcomes;
- fixed v0.1 supporting concept order;
- application report service/orchestrator;
- supporting-evidence availability summaries;
- typed report provenance;
- deterministic composition and component-consistency checks.

## Required behavior

The service must:

1. run the accepted base comparison;
2. stop with report-not-ready if base comparison is not ready;
3. generate deterministic delta observations;
4. attempt each initial continuous overlay;
5. attempt gear overlay;
6. keep optional missing/incompatible supporting evidence explicit;
7. return one integrated report artifact;
8. preserve all successful component provenance.

## TDD rule

```text
REPORT SPEC
-> APPLICATION-LEVEL TESTS
-> VALID RED
-> MINIMUM REPORT SERVICE
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

## First executable test targets

Tests must prove:

- base-comparison failure makes the report not ready;
- a complete synthetic request produces one deterministic report;
- observations use the exact successful base comparison;
- all six supporting concepts appear in stable order;
- missing optional speed/throttle/brake/steering/RPM/gear evidence is reported without failing the whole report;
- successful continuous overlays retain the base grid;
- successful gear overlay retains discrete values;
- incompatible brake semantics appear as supporting evidence not-ready;
- duplicate/unsupported report channel declarations fail explicitly;
- report provenance retains base/observation/overlay provenance;
- equivalent requests produce equal results;
- no cause/hypothesis/recommendation fields exist.

## Architecture boundary

Plan 014 belongs in the application/composition layer.

It may call deterministic analysis engines.

It must not:

- parse files;
- normalize channels;
- repair telemetry;
- duplicate numerical algorithms;
- persist projects;
- define HTTP schemas;
- render UI;
- use AI.

## TDD execution evidence

Behavioral RED:

- CI #141;
- expected failure: the comparison-report application contract was absent from `ome.application`.

Post-implementation harness feedback:

- CI #142–#144 exposed formatter and test-fixture setup defects;
- no deterministic engine contract was weakened.

GREEN:

- CI #145;
- the complete canonical `verify` passed with integrated report composition, optional missing evidence and typed report provenance.

## Implementation traceability

Test module:

`tests/application/test_lap_comparison_report.py`

Coverage proves:

- base comparison failure makes the whole report not ready;
- a complete request produces one integrated deterministic report;
- the fixed six-concept evidence inventory is stable;
- optional missing speed/gear evidence does not destroy the report;
- incompatible brake semantics remain explicit missing evidence;
- successful continuous/gear overlays reuse the accepted base grid;
- duplicate/unsupported report declarations fail explicitly;
- report provenance retains every successful component provenance;
- equivalent requests produce equal reports;
- the report contains no cause/hypothesis/engineering interpretation/recommendation fields.

## Completion criteria

- report spec accepted;
- tests before production behavior;
- behavioral RED recorded;
- report service GREEN;
- missing supporting evidence explicit;
- provenance chain GREEN;
- REQ-005/REQ-006 traceability updated;
- canonical CI GREEN.

## Explicitly out of scope

- API endpoint;
- persistence;
- rendered report;
- frontend;
- AI explanation;
- causal engineering conclusions.
