# Contributing to Open Motorsport Engineer

OME is built with an agent-first engineering workflow.

Before contributing, read:

- `AGENTS.md`
- `docs/PROJECT.md`
- `docs/ARCHITECTURE.md`
- `docs/HARNESS_ENGINEERING.md`
- `docs/DEVELOPMENT.md`

Then read requirements, ADRs and domain documentation relevant to your change.

## Setup

The repository pins its toolchain.

Use the versions documented in `docs/DEVELOPMENT.md`, then run:

```text
uv sync --locked
pnpm install --frozen-lockfile
```

## Required verification

Before opening or updating a substantial pull request:

```text
uv run --locked python scripts/harness.py verify
```

Use focused commands during development:

```text
uv run --locked python scripts/harness.py lint
uv run --locked python scripts/harness.py type
uv run --locked python scripts/harness.py test
uv run --locked python scripts/harness.py docs
uv run --locked python scripts/harness.py arch
uv run --locked python scripts/harness.py fixtures
```

## Test-driven development

For new or changed product behavior, write the focused acceptance/unit test first, run it, and confirm it fails for the intended missing behavior before implementing the production change.

Use the cycle:

```text
RED -> GREEN -> REFACTOR
```

Do not create artificial failing tests for documentation-only or tooling-only changes.

## Principles

- solve a documented problem;
- keep changes focused;
- avoid premature architecture;
- do not invent motorsport engineering rules;
- preserve telemetry provenance;
- test deterministic behavior;
- turn repeated review feedback into executable guardrails;
- document significant decisions.

## Pull requests

A good pull request should explain:

- the problem;
- the focused change;
- requirement / ADR involved;
- checks run and their result;
- engineering/data assumptions;
- limitations or follow-up work.

Substantial architecture changes should reference an ADR. Product behavior should reference a requirement when one exists.
