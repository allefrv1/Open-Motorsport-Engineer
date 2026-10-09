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

Plan 015 produced a verified local FastAPI process and `/healthz` route. Plans 018 and 031 have since produced the executable React/Vite product application.

The repository now has the two long-running application processes anticipated by this proposal: the local API and the browser frontend. Containerization can therefore package real executable boundaries without introducing a speculative service topology.

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
- provides one-command optional `docker compose up --build` onboarding;
- makes container health/data semantics explicit;
- avoids fake database/cache services.

### Negative

- native and containerized development are two supported paths that require parity checks;
- container builds add registry/network dependencies that native development does not require;
- host filesystem differences still need validation for future mounted project/telemetry storage.

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

Therefore, at the Plan 015 checkpoint:

- **backend Dockerfile: justified once this ADR is accepted**;
- **Docker Compose: continue to defer** until the React/Vite application or another required long-running process exists;
- **database/cache containers: not justified** under the current SQLite/local-first architecture.

## 2026-10-09 implementation checkpoint

The condition that previously deferred Compose is now satisfied:

- FastAPI/Uvicorn is executable and exposes `/healthz`;
- React/Vite is executable as a separate local process;
- Vite already owns the browser-to-API `/api` proxy boundary;
- no external database/cache/message broker is required.

The implementation therefore follows the proposal with:

- a locked, non-root backend image;
- a locked, non-root frontend development image;
- `compose.yaml` containing only `api` and `web`;
- loopback-only published ports;
- an internal `web -> api` proxy target;
- image healthchecks;
- CI smoke verification of the optional container path.

Native locked development remains canonical. This checkpoint records implementation evidence only;
it does not change this ADR's **Proposed** status.

## Reversibility

High.

The implemented Dockerfiles and two-service Compose topology remain an optional packaging layer. They
can be replaced or removed without changing the accepted local modular-monolith or HTTP/UI boundaries.

## Related decisions

- ADR-0004 — Use a local modular monolith
- ADR-0007 — Use SQLite for local project metadata
- ADR-0008 — Use a local HTTP API with a React/TypeScript UI

## Related plan

- Plan 015 — Local Comparison Report HTTP API
