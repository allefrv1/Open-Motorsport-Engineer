# OME Development Environment

Status: **Accepted harness baseline**

## Purpose

This document defines the reproducible toolchain and canonical commands used by humans and coding agents.

## Pinned toolchain

- Python: **3.13.15**
- uv: **0.12.17**
- Node.js: **24.21.0 LTS**
- pnpm: **11.27.1**
- Ruff invoked by the harness: **0.16.8**
- ty invoked by the harness: **0.0.82**

Python 3.13 remains the initial OME target even though Python 3.14 is the latest feature line. The project favors compatibility and a conservative scientific-computing baseline over adopting a newer language line without a concrete requirement.

Node 24 is the selected LTS line.

## Version files

The repository exposes versions through:

- `.python-version`
- `uv.toml`
- `.node-version`
- root `package.json`
- `uv.lock`
- `pnpm-lock.yaml`

## Initial setup

Install the pinned `uv` and `pnpm` versions using their official installation methods.

Then, from the repository root:

```text
uv sync --locked
pnpm install --frozen-lockfile
```

The harness checks exact runtime versions so environment drift fails early.

## Canonical commands

### Format

```text
uv run --locked python scripts/harness.py format
```

### Lint / format check

```text
uv run --locked python scripts/harness.py lint
```

### Type/static check

```text
uv run --locked python scripts/harness.py type
```

### Tests

```text
uv run --locked python scripts/harness.py test
```

### Frontend build

```text
uv run --locked python scripts/harness.py build
```

The full verify also runs frontend TypeScript checking and a production Vite build.

### Documentation

```text
uv run --locked python scripts/harness.py docs
```

### Architecture

```text
uv run --locked python scripts/harness.py arch
```

### Fixtures

```text
uv run --locked python scripts/harness.py fixtures
```

### Full verification

```text
uv run --locked python scripts/harness.py verify
```

## Frontend dependencies

Plan 018 introduces the locked React application toolchain:

- React 19.3.0;
- React DOM 19.3.0;
- TypeScript 7.0.2;
- Vite 8.3.0;
- official Vite React plugin 6.1.1;
- Vitest 5.0.1;
- React Testing Library 16.3.3;
- DOM Testing Library 10.4.2;
- jsdom 30.0.1.

Frontend dependency resolution is stored in `pnpm-lock.yaml`.

## Application dependencies

The first executable local HTTP boundary introduces pinned Python application dependencies:

- FastAPI 0.140.3;
- Uvicorn 0.53.0;
- httpx 0.28.1 in the development/test dependency group.

They are resolved in `uv.lock` and installed through the same locked environment as the rest of the project.

Harness tools that are useful as standalone binaries remain invoked at explicit versions through `uvx`.

## Run the local API

From the repository root after `uv sync --locked`:

```text
uv run --locked uvicorn --app-dir backend/src ome.api:create_app --factory --host 127.0.0.1 --port 8000
```

Local endpoints:

- `GET http://127.0.0.1:8000/healthz`
- `POST http://127.0.0.1:8000/api/v1/comparison-reports`
- `POST http://127.0.0.1:8000/api/v1/ome-csv/comparison-reports`
- `POST http://127.0.0.1:8000/api/v1/traqmate/comparison-reports`
- `GET http://127.0.0.1:8000/openapi.json`

Run the frontend development server in a second terminal:

```text
pnpm --dir frontend dev
```

Vite binds to `127.0.0.1:5173` for the local-first development baseline and
proxies `/api` to `http://127.0.0.1:8000`.

The default host is intentionally loopback-only for the local-first baseline.

For a complete browser walkthrough using the committed physical Portland fixture, see:

`docs/QUICKSTART.md`

## Optional Docker Compose development

Native locked development remains the canonical baseline. Docker is an optional packaging and
onboarding path following ADR-0010.

Requirements:

- Docker Engine with Docker Compose v2.

From the repository root:

```text
docker compose up --build
```

The Compose topology contains only the executable application boundaries:

- `api` — FastAPI/Uvicorn on `http://127.0.0.1:8000`;
- `web` — Vite on `http://127.0.0.1:5173`.

Both host ports bind to loopback only. The frontend container sets
`OME_API_PROXY_TARGET=http://api:8000` so Vite can proxy `/api` across the internal Compose
network while native development keeps the existing `http://127.0.0.1:8000` default.

Stop the stack with:

```text
docker compose down
```

Useful container verification commands:

```text
docker compose config --quiet
docker compose build
docker compose up --detach --wait --wait-timeout 90
```

The container images use the repository's pinned Python, Node, uv and pnpm versions, run application
processes as non-root users, and expose image healthchecks. Compose does not introduce a database,
cache or message broker: SQLite/local project storage remains part of the local-first architecture.

CI validates the native canonical harness and the optional Compose path separately. A Docker failure
does not redefine a behavioral test failure; classify it as a packaging/harness failure.


## CI parity

GitHub Actions uses the same version pins and calls the same `scripts/harness.py verify` command.

The container job is additional packaging verification, not an alternate application verification
path. The canonical harness remains authoritative for product correctness.
