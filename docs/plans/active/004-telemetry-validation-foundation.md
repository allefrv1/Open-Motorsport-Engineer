# Plan 004 — Telemetry Validation Foundation

Status: **Active**

Started: 2026-09-22

## Objective

Implement the smallest non-destructive validation layer satisfying the foundational behavior of REQ-002 without moving normalization, repair or engineering diagnosis into validation.

## Requirement

Primary:

- REQ-002 — Validate Telemetry Dataset

Supporting contracts:

- `docs/domain/data-quality.md`
- `docs/domain/telemetry-import-model.md`
- ADR-0001 — ingestion, validation and normalization remain separate
- `docs/CORE_BELIEFS.md` — unknown remains valid state; evidence before explanation

## Scope

Create a source-independent validation result model and deterministic generic checks that do not require source-specific engineering assumptions.

Initial domain concepts:

- ValidationSeverity;
- ValidationIssue;
- ValidationResult;
- issue location/context for dataset/channel/time region where known.

## Initial checks

The first validation slice may mechanically check only rules with source-independent meaning:

### Structure / time

- empty sample series;
- inconsistent timestamp/value counts if encountered outside domain construction safeguards;
- non-finite timestamps;
- duplicate timestamps;
- decreasing/non-monotonic timestamps.

### Metadata

- missing/unknown unit;
- missing/unknown sample-rate metadata;
- missing source identity where applicable.

## Severity baseline

Initial severity decisions should follow the accepted domain meaning:

- structurally unsafe time/series evidence → **BLOCKING**;
- missing metadata that limits later analysis → **WARNING** unless a specific operation later requires it;
- informational observations → **INFO**.

Severity must be explicit and testable.

## Explicit deferrals

Do not invent universal thresholds for:

- frozen signals;
- clipping;
- spikes;
- physical impossible ranges;
- timestamp-gap size;
- synchronization tolerance.

Those checks require source/channel semantics or an accepted deterministic policy.

This plan may define issue categories capable of representing them, but must not fabricate thresholds merely to claim coverage.

## Non-destructive rule

Validation receives an `ImportedTelemetryDataset` and returns validation evidence.

It must not:

- mutate samples;
- interpolate;
- fill missing values;
- convert units;
- normalize channel identity;
- resample;
- delete suspicious values.

## Analysis readiness boundary

Do not add one global "dataset is good/bad for all analyses" flag.

Validation may expose structural blocking issues.

Analysis-specific readiness remains a later use-case contract:

```text
ValidationResult
+ Analysis Requirements
-> AnalysisReadiness
```

## Acceptance mapping target

Add executable coverage for REQ-002 AC-001 through AC-006 to the extent this foundational slice can satisfy them.

Where an acceptance criterion requires future analysis-specific behavior, document the exact remaining contract instead of inventing it.

## Architecture constraints

- validation may depend on domain;
- validation must not depend on API/UI;
- validation must not depend on normalization or analysis modules;
- deterministic checks should be small, explicit and independently testable;
- validation issues must identify affected evidence where possible.

## Fixtures / test data

Prefer directly constructed domain datasets for precise validator unit tests.

Use existing imported OME CSV fixture for an integration test proving:

```text
import -> validate
```

without modifying the imported dataset.

Do not add vendor datasets unless a check actually requires them.

## Completion criteria

- validation result/severity model exists;
- initial generic checks are deterministic;
- REQ-002 acceptance traceability is explicit;
- non-destructive behavior is tested;
- no repair/normalization leaks into validation;
- architecture harness remains green;
- canonical CI is green.

## Explicitly out of scope

- physical range rules;
- source-specific quality plugins;
- generic spike/frozen-sensor thresholds;
- data repair;
- analysis readiness for a named engineering analysis;
- canonical normalization;
- API/UI presentation.
