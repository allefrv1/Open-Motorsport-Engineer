# Planned Repository Structure

Status: **Accepted design target — directories are not created until implementation begins**

## Principle

Repository structure should reflect architecture boundaries, not frameworks.

The initial design target is:

```text
/
├── AGENTS.md
├── README.md
├── docs/
├── backend/
│   ├── src/
│   │   └── ome/
│   │       ├── domain/
│   │       ├── application/
│   │       ├── ingestion/
│   │       ├── validation/
│   │       ├── normalization/
│   │       ├── telemetry/
│   │       ├── analysis/
│   │       ├── evidence/
│   │       ├── persistence/
│   │       └── api/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── features/
│   │   ├── components/
│   │   └── lib/
│   └── tests/
└── fixtures/
```

This is a target organization, not a requirement that every folder exist immediately.

## Backend boundary intent

### domain

Pure project concepts and invariants.

Must not depend on FastAPI, React, SQLite or a specific telemetry vendor.

### application

Use-case orchestration.

Examples:

- import source;
- validate dataset;
- organize session;
- compare laps.

### ingestion

Source-adapter contracts and adapters.

### validation

Non-destructive quality rules.

### normalization

Canonical concept mappings and unit conversions.

### telemetry

Columnar/time-base representation and access abstractions.

### analysis

Deterministic engineering metrics and comparison algorithms.

### evidence

Measured/derived/observation/finding provenance contracts.

### persistence

Adapters for SQLite, Parquet and filesystem layout.

### api

FastAPI HTTP adapter only.

No domain logic in route handlers.

## Frontend intent

Organize by user workflow/features rather than duplicating backend layers.

Potential first features:

- session import;
- data quality;
- session browser;
- lap comparison;
- evidence inspector.

## Local AGENTS.md files

Create module-specific `AGENTS.md` files only when implementation begins and the module has meaningful special rules.

Expected examples:

- `backend/src/ome/analysis/AGENTS.md` — deterministic calculations only;
- `backend/src/ome/ingestion/AGENTS.md` — preserve source evidence;
- future AI area — never fabricate evidence.

## Avoid

Do not begin with:

- shared generic `utils/` dumping grounds;
- repository-wide service classes with unrelated responsibilities;
- vendor-specific domain entities;
- microservice directories;
- premature plugin framework.
