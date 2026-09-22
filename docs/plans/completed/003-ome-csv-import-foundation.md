# Plan 003 — OME CSV Import Foundation

Status: **Completed**

Started: 2026-09-22

Completed: 2026-09-22

## Objective

Implement the smallest production slice satisfying REQ-001 for the project-owned OME CSV Exchange Profile.

## Delivered

The first source-preserving OME ingestion slice now includes:

- source-independent telemetry domain types;
- a common telemetry importer protocol;
- importer selection through `TelemetryImportService`;
- OME CSV Exchange Profile v0.1 importer;
- stable SHA-256 fingerprint over CSV + sidecar source content;
- immutable source/provenance metadata snapshots;
- source-channel inventory and original source names;
- supplied units and sample-rate metadata;
- explicit missing-metadata issues;
- explicit unsupported/read/invalid-profile failures;
- import summary including source metadata;
- machine-readable v0.1 sidecar JSON Schema;
- ingestion-local `AGENTS.md` constraints.

## Acceptance evidence

REQ-001 AC-001 through AC-010 are mapped to executable tests in:

`tests/ingestion/test_ome_csv_import.py`

Additional regression tests cover:

- missing sidecar;
- non-monotonic profile time;
- JSON sidecar member-order independence;
- empty profile data.

## Review discoveries

The implementation/review cycle clarified two contract details without changing the product architecture:

1. JSON object member order must not define channel validity; CSV header order is authoritative.
2. ImportSummary must expose preserved source metadata directly.

The OME CSV profile specification was updated accordingly.

## Boundaries preserved

This plan intentionally did **not** implement:

- data-quality validation;
- normalization;
- unit conversion;
- resampling;
- arbitrary CSV inference;
- Session / Run / Lap inference;
- persistence;
- HTTP API;
- frontend;
- engineering interpretation.

## Verification evidence

The pull-request harness exercised:

- formatting;
- linting;
- static/type checks;
- Python tests;
- frontend harness test;
- documentation checks;
- architecture checks;
- fixture checks.

The CI feedback loop caught and caused correction of:

- formatting drift;
- a Python type-shadowing defect;
- an obsolete test expectation after the channel-order contract was improved.

The reviewed head then passed the full canonical verification command.

## Requirement status

REQ-001 remains **Accepted** rather than globally **Implemented** because the requirement also describes the initial multi-source ingestion strategy.

The OME CSV source slice is implemented; iRacing and MoTeC source adapters remain future work.
