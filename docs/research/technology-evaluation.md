# Technology Evaluation for the First OME Implementation

Status: **Reviewed architecture evaluation**

Date: 2026-09-22

## Decision criteria

Candidate technologies were evaluated against OME's accepted drivers:

- deterministic numerical/data processing;
- multi-rate telemetry;
- large local datasets;
- offline operation;
- traceability and reproducibility;
- cross-platform development;
- rich interactive telemetry visualization;
- open-source contributor accessibility;
- future AI integration without coupling AI to the engineering core;
- simplicity for a small initial team.

## Application shape

### Option A — Cloud-first web application

Rejected for the initial architecture.

Reasons:

- conflicts with offline trackside usage;
- introduces data-ownership concerns;
- adds deployment/auth/infrastructure before product validation.

### Option B — Native desktop UI with Python/Qt

Viable.

Advantages:

- one primary language;
- mature native desktop framework;
- direct local filesystem/process integration.

Disadvantages:

- complex professional telemetry visualization UX is easier to evolve with web UI technologies;
- smaller frontend contributor ecosystem for the intended UI;
- tighter coupling between presentation and Python runtime.

### Option C — Local web application

Selected.

The application runs locally and serves a browser-based UI from the user's machine.

Advantages:

- offline-capable;
- cross-platform;
- strong visualization ecosystem;
- clean boundary between engineering core and presentation;
- straightforward future desktop wrapping if justified.

Desktop packaging remains optional and should not dictate the initial architecture.

## Engineering language

### Python

Selected for the engineering/application core.

Reasons:

- mature numerical/scientific ecosystem;
- strong motorsport/data-analysis fit;
- first-class Arrow/Parquet support;
- strong testing ecosystem;
- suitable for signal processing and future engineering algorithms;
- accessible to students and engineering contributors;
- compatible with future AI tooling without coupling the domain to an AI framework.

Performance-critical components may later be implemented in Rust/C++ only when profiling demonstrates a need.

### Rust-first core

Deferred.

Rust offers excellent performance and memory safety but would increase initial domain-development cost and reduce accessibility for many engineering/data contributors.

The architecture should preserve boundaries that allow selective native acceleration later.

## Telemetry processing

### Polars

Selected as the initial high-level columnar processing engine.

Reasons:

- lazy query model;
- optimization support;
- streaming-oriented execution capabilities;
- Arrow-oriented ecosystem;
- suitable for columnar telemetry transformations.

Reference: https://docs.pola.rs/user-guide/lazy/

### pandas

Not selected as the primary telemetry engine.

It remains useful for interoperability, but the initial architecture should avoid making large telemetry processing depend on eager pandas DataFrames.

### DuckDB

Not required in the first implementation.

DuckDB is highly compatible with Arrow and Parquet and can query datasets with projection/filter pushdown.

It is a strong future option for ad-hoc analytical queries, reports or cross-dataset exploration.

Do not add it until a concrete query workload justifies a second analytical engine.

References:

- https://duckdb.org/docs/current/guides/python/sql_on_arrow
- https://duckdb.org/docs/current/guides/overview

## In-memory interoperability

### Apache Arrow

Selected as the interoperability foundation for columnar data boundaries.

Arrow provides a language-independent columnar representation and first-class Python integration.

Reference: https://arrow.apache.org/docs/python/

This does not mean every domain entity becomes an Arrow table.

Arrow is primarily appropriate at data-processing boundaries.

## On-disk telemetry representation

### Apache Parquet

Selected for processed/imported columnar telemetry storage in the initial architecture.

Reasons:

- columnar;
- compressed;
- compatible with Arrow and Polars;
- supports selective column reading;
- well-suited to large analytical datasets.

The exact multi-rate dataset layout remains an implementation design task, but it must preserve source/time-base semantics.

## Project metadata

### SQLite

Selected for local project metadata.

Appropriate examples:

- projects/workspaces;
- source/import records;
- Session / Run / Lap metadata;
- setup/context references;
- validation summaries;
- analysis catalog;
- provenance relationships.

Large telemetry sample arrays should not be stored as ordinary row-per-sample SQLite tables by default.

## Application API boundary

### FastAPI

Selected for the initial local application API boundary.

Reasons:

- Python-native;
- typed request/response contracts;
- OpenAPI/JSON Schema support;
- clear boundary between UI and engineering core;
- straightforward testing.

References:

- https://fastapi.tiangolo.com/
- https://fastapi.tiangolo.com/features/

FastAPI is an application adapter. Domain logic must not live inside route handlers.

## Frontend

### React + TypeScript

Selected for the first UI.

Reasons:

- mature component ecosystem;
- strong support for complex interactive applications;
- clean separation from Python engineering logic;
- broad contributor/tooling support.

Reference: https://react.dev/

### Vite

Preferred build tool for the SPA.

This keeps the frontend as static local assets and remains compatible with future desktop wrapping.

Tauri's own frontend guidance recommends Vite for SPA frameworks, but Tauri itself is deferred.

Reference: https://v2.tauri.app/start/frontend/

## Visualization

The first UI requires high-performance synchronized telemetry plots.

Plotly.js is acceptable for the first vertical slice because it provides interactive plots and WebGL variants for larger datasets.

References:

- https://plotly.com/javascript/webgl-vs-svg/
- https://dash.plotly.com/performance

Visualization should be isolated behind frontend components so the library can be replaced if telemetry-specific performance or linked-cursor behavior requires it.

## Desktop packaging

### Tauri

Deferred, not rejected.

Tauri supports cross-platform desktop applications with web frontends and a Rust core/webview architecture.

References:

- https://v2.tauri.app/concept/architecture/
- https://v2.tauri.app/

OME should first prove the local web application and engineering boundaries.

A later ADR may wrap the local application with Tauri or choose another packaging strategy.

## Initial technology set

```text
Engineering/Application Core
  Python

Columnar processing
  Polars

Columnar interoperability
  Apache Arrow / PyArrow

Telemetry persistence
  Parquet

Project metadata
  SQLite

Local API
  FastAPI

Frontend
  React + TypeScript + Vite

Initial charts
  Plotly.js

Testing
  Python + frontend test tooling selected during repository bootstrap

Desktop wrapper
  Deferred
```

## Important architecture rule

These technologies are adapters around OME's domain and engineering contracts.

The domain must not become:

- FastAPI-shaped;
- SQL-shaped;
- React-shaped;
- Parquet-shaped;
- Polars-shaped.

The boundaries documented in the requirements and ADRs remain authoritative.
