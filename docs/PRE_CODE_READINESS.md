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
9. deterministic distance-aligned lap delta-time analysis with typed provenance and readiness.

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

## Current implementation gate

### Go

Proceed to:

`docs/plans/active/010-lap-continuous-channel-overlays.md`

### Guardrail

The base lap delta comparison is implemented and verified.

Plan 010 must reuse that exact grid/provenance and add only supported continuous canonical evidence according to `docs/specs/lap-continuous-overlay-v0.1.md`.

Do not linearly interpolate gear. Do not overlay brake until semantic compatibility is mechanically explicit. Missing or insufficient channel evidence returns an overlay not-ready result without invalidating the valid base delta comparison.

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

Harness bootstrap, ingestion, validation, normalization, operational context, source adapters and the first deterministic lap delta analysis have each been required to pass the same canonical GitHub Actions verification before merge.

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
