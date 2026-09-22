# OME Test Strategy

Status: **Accepted pre-implementation strategy**

## Goal

Testing must protect engineering meaning, not only code execution.

The most important failures are:

- corrupted evidence;
- wrong units;
- incorrect mappings;
- non-reproducible metrics;
- silent handling of missing data;
- source-specific behavior leaking into the core.

## Test layers

### 1. Domain tests

Fast tests for domain invariants.

Examples:

- unknown metadata remains unknown;
- source identity survives normalization;
- invalid lifecycle transitions are rejected;
- observations cannot masquerade as measurements in evidence contracts.

### 2. Deterministic metric tests

Use small known datasets with analytically predictable results.

Examples:

- unit conversions;
- time/distance interpolation;
- delta-time convention;
- derived-channel calculations.

Floating-point tolerances must be explicit.

### 3. Source-adapter contract tests

Every importer must satisfy the same ingestion contract.

Test:

- original channel names;
- units;
- sample/time-base metadata;
- provenance;
- warnings;
- failure behavior.

### 4. Golden fixture tests

Keep small legally redistributable fixtures representing:

- OME CSV;
- iRacing;
- MoTeC CSV export;
- malformed/edge cases.

Expected import/validation summaries should be reviewed and version-controlled.

Large proprietary or confidential datasets must not be committed publicly.

### 5. Property/invariant tests

Useful for rules such as:

- source transformations never mutate the source object;
- distance-aligned grid remains monotonic;
- converting unit A -> B -> A stays within tolerance when reversible;
- same deterministic inputs produce equivalent outputs.

### 6. Integration tests

Exercise complete local application use cases:

```text
import
-> validate
-> normalize
-> contextualize
-> compare
```

without requiring the UI.

### 7. API contract tests

Verify local API schemas, error behavior and compatibility with the frontend contract.

### 8. UI tests

Test critical workflows rather than every visual detail:

- open/import dataset;
- inspect validation issues;
- select laps;
- compare laps;
- inspect evidence.

### 9. Performance benchmarks

Representative datasets should track:

- import throughput;
- peak memory;
- channel scan latency;
- lap-comparison latency;
- plot payload size.

Benchmarks are regression signals, not marketing guarantees.

## AI tests — future

When the OME Engineer Agent is introduced, evaluate separately that it:

- never fabricates missing channels;
- distinguishes observation from hypothesis;
- cites structured evidence;
- refuses unsupported causal conclusions;
- remains useful when some evidence is missing.

AI evals must not replace deterministic core tests.

## Test data policy

Every fixture must record:

- source/licensing status;
- whether it is synthetic, public or permissioned;
- expected use;
- provenance.

No confidential team telemetry should enter the public repository without explicit permission.
