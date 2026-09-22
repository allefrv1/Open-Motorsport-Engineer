# OME Implementation Readiness Review

Date: 2026-09-22

Status: **Executable harness operational — telemetry foundation in progress**

## Executive conclusion

OME has moved beyond pre-code readiness.

The repository now has:

1. a product/domain/architecture system of record;
2. an executable agent feedback loop proven in CI;
3. production slices for source-preserving OME CSV ingestion;
4. production validation that is deterministic and non-destructive.

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

## Current implementation gate

### Go

Proceed to:

`docs/plans/active/005-telemetry-normalization-foundation.md`

### Guardrail

Normalization must add source-independent engineering meaning **without replacing source evidence**.

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

- redistributable full iRacing session;
- licensed real physical-car MoTeC export;
- Brazilian Formula SAE full-session fixture with permission;
- genuinely multi-rate physical-car acquisition fixture.

## Evidence

Harness bootstrap, ingestion and validation have each been required to pass the same canonical GitHub Actions verification before merge.

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
