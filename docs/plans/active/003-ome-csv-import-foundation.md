# Plan 003 — OME CSV Import Foundation

Status: **Active**

Started: 2026-09-22

## Objective

Implement the smallest production slice satisfying REQ-001 for the project-owned OME CSV Exchange Profile.

This is the first product-code plan after harness bootstrap.

## Requirement

Primary:

- REQ-001 — Import Telemetry Session

Supporting contracts:

- `docs/domain/telemetry-import-model.md`
- `docs/domain/provenance.md`
- `docs/specs/ome-csv-profile-v0.1.md`
- ADR-0001 — ingestion is separate from normalization
- ADR-0002 — CSV is exchange/profile data, not canonical storage
- ADR-0005 — Python engineering core

## Scope

Implement only the ingestion boundary needed to read a valid OME CSV Profile and produce a source-preserving imported representation.

Initial concepts:

- TelemetrySource;
- ImportedTelemetryDataset;
- SourceChannel;
- SampleSeries;
- ChannelMetadata;
- Provenance;
- ImportIssue / import result.

## Required behavior

For the OME CSV Profile:

1. accept a CSV + required `.ome.json` sidecar;
2. read without modifying source files;
3. compute a stable source/content fingerprint;
4. preserve original channel identifiers, source names and supplied units;
5. preserve source/profile metadata;
6. represent missing metadata explicitly;
7. preserve the shared source time base;
8. return explicit unsupported/invalid-profile/read errors;
9. produce an import summary;
10. keep normalization, validation and engineering interpretation out of the importer.

## Acceptance mapping

The implementation must add executable tests covering REQ-001 AC-001 through AC-010 where applicable to the OME CSV Profile.

Any criterion not exercised in this plan must be explicitly documented with its follow-up plan.

## Design constraints

- domain types must not depend on FastAPI, Polars, PyArrow or persistence adapters;
- source evidence must remain immutable from the importer's perspective;
- no automatic channel normalization;
- no unit conversion;
- no resampling;
- no generic arbitrary-CSV inference;
- no Session / Run / Lap inference beyond preserving profile metadata;
- no API or UI required for this plan;
- no Parquet/SQLite persistence required unless a requirement discovered during implementation proves it necessary.

## Fixtures

Use:

- `fixtures/ome/basic-lap.csv`;
- `fixtures/ome/basic-lap.ome.json`.

Add small project-owned negative fixtures for profile errors only when required by acceptance tests.

Do not copy external datasets merely to make tests convenient.

## Verification

During work:

```text
uv run --locked python scripts/harness.py lint
uv run --locked python scripts/harness.py type
uv run --locked python scripts/harness.py test
uv run --locked python scripts/harness.py arch
uv run --locked python scripts/harness.py fixtures
```

Before completion:

```text
uv run --locked python scripts/harness.py verify
```

## Completion criteria

- REQ-001 behavior for OME CSV is implemented;
- acceptance criteria have executable traceability;
- importer contract is source-independent enough for a later iRacing adapter;
- no normalization/validation responsibility leaks into import;
- canonical CI is green;
- documentation is updated if implementation reveals a real contract gap.

## Explicitly deferred

- iRacing `.ibt`;
- MoTeC CSV;
- generic CSV mapping;
- data-quality validation rules (REQ-002);
- canonical normalization (REQ-004);
- persistence/catalog;
- HTTP API;
- frontend;
- lap comparison.
