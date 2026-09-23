# ADR-0010 — Introduce containers only for executable application boundaries

Status: **Proposed**

Date: 2026-09-23

## Context

OME is local-first and already has a reproducible native development harness with pinned Python, Node, uv and pnpm versions.

The accepted application architecture will eventually contain:

- a local FastAPI boundary;
- a React/TypeScript/Vite frontend;
- SQLite metadata;
- local telemetry/project files.

At proposal time the repository did not yet contain an executable FastAPI server or React/Vite application.

Plan 015 has since produced a verified local FastAPI process and `/healthz` route. The React/Vite product application still does not exist.

Adding Docker can now package a real backend boundary. Adding Docker Compose would still create an artificial multi-service topology before there is a second executable application process.

## Proposed decision

Adopt containerization incrementally as an **optional packaging/development layer**, not as a new architecture boundary.

### Backend image

Introduce a backend/runtime Dockerfile only after the local FastAPI process is executable.

Requirements for that image:

- pinned/runtime-compatible Python baseline;
- locked dependency installation;
- cache-efficient/multi-stage build where useful;
- non-root runtime user;
- explicit healthcheck target using the local API health route;
- no embedded project telemetry/database state in the image.

### Frontend image

Introduce a frontend image only after the React/Vite product application exists.

Development may use Vite directly or Docker Compose Watch.

Production packaging remains replaceable and may later use a static-server stage or be consolidated into another local packaging approach.

### Docker Compose

Do not add `compose.yaml` merely to wrap one non-networked harness process.

Add Compose when at least two executable processes need coordinated local lifecycle, expected initially to be:

- `api`;
- `web`.

SQLite remains a file/volume owned by OME.

Do **not** create a PostgreSQL/MySQL/Redis container without a separate requirement.

### Development workflow

Native locked development remains the canonical baseline:

```text
uv sync --locked
pnpm install --frozen-lockfile
uv run --locked python scripts/harness.py verify
```

Containerized development may become an optional equivalent path once it can be mechanically verified against the same behavior.

### Data mounts

Telemetry/project input should be mounted explicitly.

Mutable project/SQLite storage should use a named volume or explicit host path.

Read-only source telemetry mounts are preferred when the workflow permits them.

## Alternatives considered

### Add Dockerfile + Compose immediately

Rejected for now because there is no executable API/frontend service graph yet.

It would encode speculative ports, commands, dependency installation and volumes.

### Never use Docker

Rejected as a general direction because containers can improve onboarding, CI parity, packaging experiments and reproducible local execution once application processes exist.

### Make containers the only supported development path

Rejected for now.

OME is local-first and telemetry-heavy; native development remains valuable for filesystem access, debugging, performance profiling and future hardware/DAQ integrations.

## Consequences

### Positive

- avoids premature infrastructure;
- keeps Docker aligned with real executable boundaries;
- preserves simple local development;
- makes future container health/data semantics explicit;
- avoids fake database/cache services.

### Negative

- developers cannot yet use one-command `docker compose up`;
- two supported development paths may eventually require parity tests;
- host filesystem differences still need validation when container support arrives.

## Security/build guidance

When images are implemented:

- prefer multi-stage builds to keep runtime images smaller;
- run services as non-root;
- maintain a focused `.dockerignore`;
- do not bake secrets or user telemetry into images;
- use explicit writable volumes;
- keep published ports local-only by default.

## Plan 015 checkpoint — 2026-09-23

Executable evidence now supports the backend-image half of this proposal:

- FastAPI app factory exists;
- Uvicorn is locked as a runtime dependency;
- `GET /healthz` is verified;
- the canonical native run command binds to loopback by default;
- transport-framework isolation is mechanically enforced.

Therefore:

- **backend Dockerfile: justified once this ADR is accepted**;
- **Docker Compose: continue to defer** until the React/Vite application or another required long-running process exists;
- **database/cache containers: not justified** under the current SQLite/local-first architecture.

## Reversibility

High.

The proposal deliberately defers concrete Dockerfile/Compose topology until executable evidence exists.

## Related decisions

- ADR-0004 — Use a local modular monolith
- ADR-0007 — Use SQLite for local project metadata
- ADR-0008 — Use a local HTTP API with a React/TypeScript UI

## Related plan

- Plan 015 — Local Comparison Report HTTP API
