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
17. a browser-usable OME CSV multipart source workflow that preserves import/preparation/report readiness semantics;
18. a verified React/TypeScript investigation workspace with explicit evidence/provenance and accessible result states;
19. synchronized telemetry investigation plots that consume server arrays without browser-side engineering recomputation;
20. explicit Traqmate Trackvision V2 physical-car ingestion with preserved GPS/Lap evidence and no fabricated lap distance;
21. deterministic WGS84 horizontal GPS path-distance derivation with typed provenance and real physical-car validation;
22. deterministic explicit-reference GPS projection with typed provenance, canonical `lap.distance` preparation and characterized direct-search scaling;
23. a traceable Portland two-complete-lap physical-car fixture and extended Trackvision V2 ingestion preserving sparse Lap-boundary evidence;
24. deterministic explicit physical-car source-lap windows with separate closing-boundary evidence;
25. deterministic physical reference/candidate canonical `lap.distance` preparation with plateau-preserving common-reference v0.2.

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

### Investigation frontend — Plans 018–019

- React/TypeScript/Vite investigation workspace;
- source upload workflow over the accepted local API;
- success/not-ready/error/loading states;
- deterministic delta summary and observations;
- explicit Supporting Evidence and provenance;
- synchronized Plotly delta/continuous/gear panels;
- exact-value semantic tables;
- redundant Lap A/B line styles;
- mechanically isolated Plotly dependency;
- no browser-side engineering recomputation.

### Physical-car Traqmate ingestion — Plan 021

- explicit Trackvision V2 source adapter;
- licensed real-vehicle fixture import;
- complete preamble/channel/unit/lexical-value preservation;
- explicit Elapsed Time timestamps;
- source Lap preservation;
- OME/MoTeC/Traqmate arbitration;
- no GPS-derived distance or hidden normalization;
- supported-path performance characterization;
- recorded RED -> GREEN CI history.

### GPS path distance — Plan 022

- WGS84 inverse-geodesic path derivation;
- GeographicLib 2.1 pinned/locked;
- horizontal-only altitude policy;
- no hidden filtering/smoothing/map matching;
- typed source/provenance evidence;
- licensed Traqmate characterization;
- external Portland multi-lap path variation study;
- recorded RED -> GREEN CI history.

### Common track reference — Plan 023

- explicit trusted reference-lap geometry;
- deterministic nearest-segment projection;
- closed-reference seam unwrap;
- strict monotonic readiness without clamping/smoothing;
- lateral projection evidence;
- complete reference/candidate provenance;
- explicit `track.reference_distance -> lap.distance` preparation;
- direct-search performance characterization;
- recorded RED -> GREEN CI history.

### Portland multi-lap source evidence — Plan 024

- direct Apache-2.0 Portland row-slice fixture with pinned upstream/derived Git blobs;
- 7,250 physical-car telemetry rows covering complete source Laps 4 and 5 plus the Lap 6 boundary;
- real 28-column Trackvision V2 ingestion;
- non-zero Elapsed Time source-column support;
- raw header and source-channel order preservation;
- sparse source Lap marker preservation;
- regression-proven legacy Trackvision compatibility;
- recorded behavioral RED, rejected regression and final GREEN CI history.

### Physical-car lap windows — Plan 025

- explicit caller-requested source lap selection;
- exact Portland Lap 4 and Lap 5 windows;
- separate closing-boundary index owned by the next source lap;
- incomplete/ambiguous/missing marker readiness;
- source/provenance consistency checks;
- imported dataset and sparse Lap evidence remain unchanged;
- recorded behavioral RED and final GREEN CI history.

### Physical track-reference preparation — Plan 026

- explicit reference/candidate physical lap composition;
- exactly one boundary-only closing point for derived geometry;
- selected reference GPS path explicitly promoted to canonical `lap.distance`;
- candidate projected onto the same common physical reference;
- common-reference algorithm v0.2 with exact plateaus preserved;
- explicit closed-lap topology instead of exact GPS-endpoint inference;
- typed topology/geometry/source provenance;
- true projected-distance decreases remain not-ready;
- recorded multi-stage RED -> GREEN CI evidence.

## Current implementation gate

### Go

Proceed to:

`docs/plans/active/027-lap-comparison-plateau-semantics-foundation.md`

### Guardrail

Plan 027 may evolve only the deterministic base lap-comparison numerical contract.

Exact non-decreasing `lap.distance` plateaus from physical projection must remain unchanged. Comparison may model their vertical time interval explicitly, but must not insert epsilon distance, clamp, smooth, delete or reorder samples. True distance decreases remain not-ready. Do not normalize Traqmate supporting channels or compose a physical report request in this slice.

ADR-0010 remains Proposed.

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

Harness bootstrap, ingestion, validation, normalization, operational context, source adapters, deterministic comparison engines, the integrated report artifact, local HTTP transport, source-to-report preparation, browser-source upload, the investigation frontend and synchronized plot increments have each been required to pass the same canonical GitHub Actions verification before merge.

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
