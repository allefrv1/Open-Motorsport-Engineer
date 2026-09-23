# Plan 015 — Local Comparison Report HTTP API

Status: **Active**

Started: 2026-09-23

## Objective

Expose the accepted application-level lap-comparison report through the first executable local HTTP boundary defined by ADR-0008.

This plan proves the API boundary without expanding OME into a network service architecture.

## Requirements

Primary:

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
- MVP — first vertical slice

Architecture:

- ADR-0004 — local modular monolith
- ADR-0005 — Python engineering core
- ADR-0008 — local HTTP API + React/TypeScript UI
- `docs/specs/lap-comparison-report-v0.1.md`

## Scope

Implement the smallest FastAPI application boundary that can:

- start as a real local process;
- expose an application health endpoint;
- accept a versioned comparison-report request schema;
- translate transport DTOs into the existing application request;
- invoke `ComparisonReportService`;
- serialize success/not-ready report outcomes deterministically;
- keep application/domain types independent of FastAPI/Pydantic;
- expose an OpenAPI contract generated from the transport schemas.

## API boundary rule

FastAPI belongs only in `ome.api`.

The API layer may depend on application/domain contracts.

Application, analysis, evidence, ingestion, validation and normalization layers must not depend on FastAPI/Pydantic transport models.

## Proposed initial routes

### `GET /healthz`

Purpose:

- prove the executable API lifecycle;
- provide a future container/process healthcheck target.

Response should be transport-only and contain no environment secrets.

### `POST /api/v1/comparison-reports`

Purpose:

- create one deterministic report from already-prepared canonical lap-comparison evidence.

This first API slice does **not** upload/parse telemetry files.

File/session workflow endpoints come later.

## Transport design

The HTTP schema must be explicitly versioned and documented before implementation.

Do not serialize Python dataclasses through accidental `__dict__` behavior.

Transport DTOs should preserve:

- canonical concept identity;
- lap/context identifiers;
- dataset fingerprints;
- source/evidence references;
- algorithm/provenance identity;
- readiness issues;
- supporting-evidence availability;
- numerical arrays/grid units.

No API field may imply a causal engineering conclusion that the application artifact does not contain.

## Error/readiness behavior

Application-level `NotReady` is not an HTTP server error.

The transport contract must distinguish:

- valid request + successful report;
- valid request + deterministic not-ready report;
- invalid HTTP payload/schema;
- unexpected internal failure.

Exact status-code/schema choices must be documented before production endpoint code.

## TDD rule

```text
API SPEC
-> HTTP CONTRACT TESTS
-> VALID RED
-> MINIMUM FASTAPI BOUNDARY
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

## First executable test targets

Tests should prove:

- app can be created/imported without side effects;
- health endpoint contract;
- report success serialization;
- report not-ready serialization;
- stable enum/unit/provenance serialization;
- invalid payload rejected by transport validation;
- API layer delegates to `ComparisonReportService` rather than reimplementing analysis;
- no FastAPI/Pydantic imports leak into core layers;
- OpenAPI contains only the intended v0.1 routes/schemas;
- equivalent requests produce equivalent JSON semantics.

## Dependency policy

This plan may introduce the first application runtime dependencies required by the accepted HTTP boundary.

Dependencies must:

- be version-locked through `uv.lock`;
- be the minimum needed for the API/test contract;
- remain inside the existing modular monolith.

Do not introduce:

- Redis;
- PostgreSQL;
- message brokers;
- reverse proxy;
- cloud service;
- background worker platform.

## Containerization checkpoint

Docker is deliberately **not** a prerequisite for implementing the API.

After the executable FastAPI process exists and is verified, evaluate the proposed containerization ADR:

- backend Dockerfile becomes meaningful at that point;
- `GET /healthz` can serve as the container healthcheck;
- runtime image should use multi-stage construction where useful and run non-root;
- SQLite/application data remains a local mounted volume/file, not a database container;
- `compose.yaml` remains deferred until the React/Vite frontend is executable, unless a concrete multi-process development need appears sooner.

## TDD execution evidence

Dependency/bootstrap setup:

- CI #151 resolved the first FastAPI/Uvicorn/httpx lock state in a controlled CI bootstrap;
- CI #153 proved the repository had returned to strict `uv sync --locked` before behavior tests.

Pre-behavior harness cleanup:

- CI #154 exposed test import ordering only.

Behavioral RED:

- CI #155;
- expected failure: `ImportError: cannot import name 'create_app' from 'ome.api'`.

Post-implementation harness feedback:

- CI #156 / #158 / #159 exposed formatter/lint issues in the new transport code;
- CI #160 reached static analysis and exposed an internal gear-type alias that should not have become part of the public analysis API.

GREEN:

- CI #161;
- the full canonical `verify` passed for the FastAPI app factory, health/report routes, transport validation, OpenAPI and application delegation.

Final architecture/documentation verification:

- CI #163;
- transport-framework isolation was mechanically enforced in `architecture.toml` and the documented local Uvicorn command remained compatible with the locked environment.

No deterministic analysis/application test was weakened to obtain GREEN.

## Implementation traceability

Test module:

`tests/api/test_local_http_api.py`

Coverage proves:

- `GET /healthz` exact local-process health contract;
- successful deterministic comparison-report serialization;
- application-level not-ready remains a normal HTTP 200 outcome;
- invalid transport payloads return 422;
- OpenAPI exposes the intended v0.1 routes;
- injected service delegation converts DTOs into `ComparisonReportRequest`;
- report provenance/algorithm identity remains visible at the transport boundary.

Architecture enforcement additionally prevents FastAPI/Pydantic imports in application/domain/analysis/evidence/ingestion/validation/normalization layers.

## Containerization checkpoint result

The checkpoint was revisited after the executable FastAPI boundary became GREEN.

Result:

- a backend Dockerfile is now technically justified because a real process and health route exist;
- `GET /healthz` is suitable for a container healthcheck;
- the runtime can remain a single local API process with SQLite/project files mounted later as data;
- a `compose.yaml` is still premature because the repository does not yet contain an executable React/Vite product application or another required long-running service;
- Redis/PostgreSQL/MySQL/reverse-proxy containers remain unjustified.

ADR-0010 remains **Proposed** pending maintainer acceptance.

## Completion criteria

- HTTP transport spec accepted;
- FastAPI runtime dependency locked;
- HTTP tests written before endpoint behavior;
- behavioral RED recorded;
- local API process executable;
- health/report routes GREEN;
- application/domain remain transport-framework independent;
- OpenAPI contract deterministic;
- canonical verify GREEN;
- containerization checkpoint revisited with executable evidence.

## Explicitly out of scope

- file upload/import API;
- project persistence API;
- authentication;
- public network deployment;
- frontend implementation;
- Docker Compose runtime stack;
- cloud deployment;
- AI.
