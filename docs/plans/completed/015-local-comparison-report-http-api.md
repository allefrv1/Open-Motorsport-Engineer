# Plan 015 — Local Comparison Report HTTP API

Status: **Completed**

Started: 2026-09-23

Completed: 2026-09-23

## Objective

Expose the accepted application-level lap-comparison report through the first executable local HTTP boundary defined by ADR-0008.

## Delivered

- FastAPI 0.140.3 runtime dependency;
- Uvicorn 0.53.0 runtime dependency;
- httpx 0.28.1 development/test dependency;
- fully resolved and versioned `uv.lock`;
- explicit Pydantic request/response DTOs isolated in `ome.api`;
- `create_app()` FastAPI app factory;
- `GET /healthz`;
- `POST /api/v1/comparison-reports`;
- deterministic success and not-ready serialization;
- FastAPI/Pydantic 422 transport validation;
- OpenAPI schema for the v0.1 HTTP contract;
- dependency injection for the report service;
- documented local Uvicorn run command;
- architecture enforcement preventing FastAPI/Pydantic leakage into core layers.

## TDD evidence

Dependency/bootstrap preparation:

- CI #151 — controlled dependency-lock bootstrap;
- CI #153 — strict `uv sync --locked` restored and GREEN.

Pre-behavior cleanup:

- CI #154 — test import ordering only.

Behavioral RED:

- CI #155 — expected failure because `create_app` did not exist.

Post-implementation harness feedback:

- CI #156 / #158 / #159 — formatter/lint feedback;
- CI #160 — static checker exposed an internal gear-type alias that should not become a public analysis contract.

GREEN:

- CI #161 — full canonical verify passed for app factory, health/report routes, 422 behavior, OpenAPI and application delegation;
- CI #163 — architecture/documentation guardrails passed;
- CI #167 — final traceability/checkpoint verification passed.

No deterministic analysis or application behavior was weakened to obtain GREEN.

## Executable contract

Run locally from the repository root:

```text
uv run --locked uvicorn --app-dir backend/src ome.api:create_app --factory --host 127.0.0.1 --port 8000
```

Routes:

- `GET /healthz`;
- `POST /api/v1/comparison-reports`;
- `GET /openapi.json`.

Authoritative transport specification:

- `docs/specs/local-comparison-report-http-api-v0.1.md`.

## Requirement traceability

Executable coverage:

- `tests/api/test_local_http_api.py`.

The transport preserves:

- deterministic report semantics;
- explicit not-ready/Missing Evidence outcomes;
- dataset and Session / Run / Lap context;
- source channel identity;
- transformation identity/version/parameters;
- comparison/observation/overlay/report provenance;
- the non-causal observation boundary.

## Architecture enforcement

`architecture.toml` now mechanically forbids FastAPI/Pydantic from:

- application;
- domain;
- analysis;
- evidence;
- ingestion;
- validation;
- normalization.

Transport remains an adapter concern.

## Containerization checkpoint

The executable API changes the Docker assessment:

- a backend Dockerfile is now technically justified;
- `/healthz` is a valid future healthcheck;
- SQLite/project data remains a file/volume concern;
- Docker Compose is still premature because the React/Vite product application does not yet exist;
- database/cache/reverse-proxy containers remain unjustified.

ADR-0010 remains **Proposed** pending maintainer acceptance.

## Boundaries preserved

Not added:

- file upload/import API;
- persistence workflow API;
- authentication;
- public-network deployment;
- frontend;
- Dockerfile;
- Docker Compose;
- cloud service;
- AI.

## Merge evidence

PR #37 was squash-merged as:

`3fcb0469708c49fd541d00b268a42f59aa4cbcb3`

## Completion assessment

All Plan 015 completion criteria are satisfied.
