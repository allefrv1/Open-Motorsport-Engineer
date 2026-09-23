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
- `GET http://127.0.0.1:8000/openapi.json`

The default host is intentionally loopback-only for the local-first baseline.

Docker is not required to run this API. ADR-0010 defines the proposed incremental containerization direction.

## CI parity

GitHub Actions uses the same version pins and calls the same `scripts/harness.py verify` command.

A CI-only alternate verification path is intentionally avoided.
