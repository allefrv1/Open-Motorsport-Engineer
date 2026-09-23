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
