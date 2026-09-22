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

## Dependency policy

The application currently has no production dependencies because feature development has not started.

Harness tools that are useful as standalone binaries are invoked at explicit versions through `uvx`.

When application dependencies are introduced, they belong in the appropriate lockfile and must be installed from the locked state in CI.

## CI parity

GitHub Actions uses the same version pins and calls the same `scripts/harness.py verify` command.

A CI-only alternate verification path is intentionally avoided.
