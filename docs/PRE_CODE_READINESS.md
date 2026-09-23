# OME Implementation Readiness Review

Date: 2026-09-22

Status: **Executable harness operational — telemetry foundation in progress**

## Executive conclusion

OME has moved beyond pre-code readiness.

The repository now has:

1. a product/domain/architecture system of record;
2. an executable agent feedback loop proven in CI;
3. production slices for source-preserving OME CSV ingestion;
4. production validation that is deterministic and non-destructive;
5. explicit versioned normalization preserving source evidence;
6. source-independent Session / Run / Lap context that does not invent missing boundaries;
7. a verified iRacing IRSDK v2 adapter with grouped fixed-array source preservation;
8. a MoTeC CSV professional-workflow adapter preserving preamble, units, lexical values and import/validation boundaries;
9. deterministic distance-aligned lap delta-time analysis with typed provenance and readiness;
10. continuous speed/throttle/steering/engine-speed overlays on the trusted comparison grid;
11. discrete transmission.gear overlay using previous-sample hold;
12. exact brake-semantic compatibility with semantic identity preserved through normalization and evidence;
13. deterministic gain/loss/neutral delta observations with complete base provenance;
14. an integrated application comparison report with explicit optional Missing Evidence and full component provenance;
15. a versioned local FastAPI report boundary with explicit DTOs, OpenAPI and framework-isolation enforcement;
16. a deterministic comparison-preparation workflow connecting imported source evidence through validation, explicit normalization and context into the accepted report request;
17. a browser-usable local OME CSV multipart workflow connecting source files to the accepted report service without leaking transport details into the deterministic core.

The architecture is still intentionally being proven one boundary at a time.

## Completed implementation foundations

### Harness

- exact Python/uv/Node/pnpm versions;
- lockfiles and clean-runner setup;
- canonical format/lint/type/test/docs/arch/fixture commands;
- one full `verify` command;
- PR CI using the same command;
- documentation consistency checks;
- dependency-boundary/cycle checks;
- fixture provenance/license checks.

### Ingestion — Plan 003

- source-independent telemetry domain types;
- provenance/fingerprint;
- importer protocol/service;
- OME CSV Exchange Profile v0.1 importer;
- REQ-001 OME CSV acceptance coverage.

### Validation — Plan 004

- ValidationSeverity / ValidationCategory / ValidationIssue / ValidationResult;
- non-destructive structural/time checks;
- explicit metadata/provenance issues;
- missing/non-finite value warnings;
- bounded aggregation of repeated defects;
- REQ-002 acceptance coverage;
- architecture rule preventing validation from depending on ingestion/normalization/analysis/API.

### Normalization — Plan 005

- canonical concept identifiers;
- explicit versioned mapping rules;
- deterministic conversion metadata;
- mapped/unmapped results with explicit reasons;
- source identity and values preserved;
- REQ-004 acceptance coverage;
- architecture rule preventing normalization from depending on ingestion/validation implementation/analysis/API.

### Operational context — Plan 006

- Session / Run / Lap context domain model;
- explicit trusted marker evidence;
- incomplete context without fabricated hierarchy;
- Run operational metadata outside telemetry channels;
- deterministic identifiers;
- REQ-003 acceptance coverage;
- recorded test-first RED -> GREEN CI history.

### External binary ingestion — Plan 007

- IRSDK v2 `.ibt` source adapter;
- independent project-owned binary fixture;
- source metadata/type/count preservation;
- explicit source time;
- grouped `countAsTime` array preservation;
- 360 Hz acquisition metadata without ingestion-time resampling;
- real external fixture structural validation;
- multiple recorded RED -> GREEN CI cycles.

### Professional CSV ingestion — Plan 008

- source-specific MoTeC CSV adapter;
- licensed deterministic TRACE fixtures;
- full preamble/name/unit/source-value preservation;
- explicit Sample Rate preservation without cadence inference;
- duplicate source-name technical disambiguation;
- OME/MoTeC CSV arbitration;
- decreasing-time import preserved for downstream validation;
- external representative MoTeC-format validation;
- recorded RED -> GREEN CI cycle.

### Lap delta analysis — Plan 009

- explicit `lap.distance` / `time.elapsed` readiness;
- common-overlap distance grid;
- deterministic linear time-vs-distance interpolation;
- `delta_B_vs_A` sign contract;
- typed source/transformation/context provenance;
- explicit not-ready outcomes;
- recorded RED -> GREEN CI history.

### Continuous lap overlays — Plan 010

- speed/throttle/steering/engine-speed continuous overlays;
- exact base-grid reuse;
- deterministic elapsed-time interpolation;
- multi-rate channel support;
- explicit no-extrapolation readiness;
- typed overlay provenance linked to base comparison evidence;
- recorded RED -> GREEN CI history.

### Discrete gear overlay — Plan 011

- canonical integer gear-state comparison;
- previous-sample hold on base elapsed-time projections;
- no linear interpolation;
- multi-rate gear support;
- explicit no-extrapolation readiness;
- typed gear provenance linked to base comparison evidence;
- recorded RED -> GREEN CI history.

### Brake semantic compatibility — Plan 012

- optional machine-readable semantic identity in normalization/evidence;
- exact supported semantic matching for brake comparison;
- pedal-position ratio and pedal-force ratio kept distinct;
- pressure/unknown semantics explicitly unsupported;
- canonical ratio-unit enforcement;
- semantic identity retained in comparison provenance;
- recorded RED -> GREEN CI history.

### Delta observations — Plan 013

- B gain / B loss / neutral deterministic region classification;
- contiguous region merging;
- explicit numerical-zero tolerance;
- structured not-ready outcomes;
- complete base-comparison provenance;
- strict separation between Observation and cause/hypothesis/interpretation;
- recorded RED -> GREEN CI history.

### Integrated comparison report — Plan 014

- deterministic application composition;
- stable six-concept evidence inventory;
- successful component reuse without numerical duplication;
- optional missing/incompatible evidence remains explicit;
- complete typed report provenance;
- recorded RED -> GREEN CI history.

### Local HTTP boundary — Plan 015

- pinned FastAPI/Uvicorn/httpx dependency set;
- explicit request/response DTOs;
- local app factory and health endpoint;
- deterministic comparison-report HTTP endpoint;
- success/not-ready/422 transport semantics;
- OpenAPI contract;
- mechanical FastAPI/Pydantic isolation from core layers;
- recorded RED -> GREEN CI history.

### Comparison preparation — Plan 016

- controlled two-lap OME CSV source fixtures;
- explicit versioned preparation profile and normalization rules;
- source validation inside the application workflow;
- explicit Session / Run / Lap context only;
- traceable OME CSV `time_s` evidence;
- canonical distance and supporting-channel evidence;
- direct `ComparisonReportRequest` construction;
- explicit not-ready behavior;
- recorded RED -> GREEN CI history.

### Browser source workflow — Plan 017

- multipart OME CSV source bundles;
- sanitized temporary API-layer staging;
- explicit import/preparation/report not-ready stages;
- existing low-level report endpoint preserved;
- OpenAPI source route;
- locked `python-multipart` dependency;
- recorded RED -> GREEN CI history.

## Current implementation gate

### Go

Proceed to:

`docs/plans/active/018-mvp-investigation-frontend.md`

### Guardrail

The frontend must remain an evidence-oriented investigation workspace.

Use the repository UX skill and accepted frontend spec. Consume report DTOs rather than recomputing engineering results. Keep Missing Evidence explicit, distinguish derived metrics from observations, preserve units/reference/provenance and test critical accessibility states.

ADR-0010 remains Proposed. Plan 018 does not require Docker Compose.

The following remain separate responsibilities:

- ingestion;
- validation;
- normalization;
- Session / Run / Lap organization;
- deterministic analysis;
- AI explanation.

## Data readiness

Available:

- OME-owned CSV Profile fixture;
- licensed Traqmate real-vehicle CSV;
- licensed MoTeC-style CSV fixtures;
- negative timestamp fixture;
- inspected external iRacing and Formula SAE data.

Still valuable for later source/scale validation:

- a redistributable full iRacing session remains useful for broader regression coverage, but is no longer required for the initial adapter;
- licensed real physical-car MoTeC export;
- Brazilian Formula SAE full-session fixture with permission;
- genuinely multi-rate physical-car acquisition fixture.

## Evidence

Harness bootstrap, ingestion, validation, normalization, operational context, source adapters, deterministic comparison engines, report composition, local HTTP transport, source preparation and multipart browser-source workflow have each been required to pass the same canonical GitHub Actions verification before merge.

The current development model is therefore:

```text
requirement
-> scoped plan
-> implementation
-> acceptance tests
-> architecture checks
-> canonical CI
-> documentation/plan completion
```

That loop should continue for every foundation slice.
