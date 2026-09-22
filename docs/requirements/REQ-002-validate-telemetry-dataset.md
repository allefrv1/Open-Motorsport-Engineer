# REQ-002 — Validate Telemetry Dataset

Status: **Accepted**

## Actor / User

A user who has successfully imported telemetry and needs to know whether the evidence is trustworthy enough for further analysis.

## Problem

Successful import only proves that OME could read the source. It does not prove that timestamps, units, channel values, sample rates or metadata are reliable.

Without a separate validation stage, OME risks producing sophisticated but incorrect analysis from bad data.

## Goal

Evaluate the structural and signal-quality conditions of an ImportedTelemetryDataset and produce explicit validation issues without silently modifying the evidence.

## Main Flow

1. OME receives an ImportedTelemetryDataset.
2. OME evaluates structural integrity and available metadata.
3. OME evaluates time information and channel sample structure.
4. OME runs applicable non-destructive signal checks.
5. OME records validation issues with severity and evidence.
6. OME produces a validation result.
7. The dataset remains unchanged.
8. Later workflows evaluate whether the dataset is ready for a specific analysis.

## Validation Areas

The validation system must be capable of representing checks for:

- malformed or inconsistent structures;
- missing time basis;
- non-monotonic or duplicated timestamps when invalid for the source;
- gaps and discontinuities;
- non-finite values;
- frozen signals;
- clipping/saturation;
- suspicious spikes;
- missing units;
- unknown sample rate/time-base metadata;
- synchronization problems;
- ambiguous channel metadata.

Not every check applies to every source or channel.

## Severity

Validation issues must support at least:

- **BLOCKING**
- **WARNING**
- **INFO**

A BLOCKING issue prevents the affected operation from being considered trustworthy.

A WARNING permits further work only with the limitation visible.

## Acceptance Criteria

### AC-001 — Non-destructive validation

Validation must not silently change source values or imported channel metadata.

### AC-002 — Explicit issues

Every detected issue must identify:

- issue category;
- severity;
- affected dataset/channel/time region when applicable;
- human-readable description.

### AC-003 — Missing metadata

Missing units, sample-rate information or other expected metadata must remain explicit.

### AC-004 — Structural corruption

A structurally corrupted dataset that cannot be interpreted safely must not be exposed as ready for analysis.

### AC-005 — No silent repair

Validation must not silently interpolate, resample, rename, convert units, remove spikes or fill missing values.

### AC-006 — Analysis-specific readiness

Validation must not reduce all datasets to a single global valid/invalid flag for every possible engineering analysis.

The output must support later analysis-readiness evaluation.

## Relevant Domain Concepts

- ImportedTelemetryDataset
- SourceChannel
- SampleSeries
- ValidationIssue
- AnalysisReadiness

## Out of Scope

- automatic data repair;
- unit conversion;
- canonical channel normalization;
- resampling;
- lap comparison;
- engineering diagnosis;
- AI explanation.
