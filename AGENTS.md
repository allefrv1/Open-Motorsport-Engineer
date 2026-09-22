# Open Motorsport Engineer — Codex Map

Version: 0.4.0

OME is an open-source motorsport engineering analysis platform.

Core principle:

> OME does not exist to make engineering disappear. It exists to make engineering understandable.

## Start here

Before substantial work, read only the documents relevant to the task:

- `docs/PROJECT.md` — mission, users, scope and non-goals
- `docs/MVP.md` — first vertical slice
- `docs/ARCHITECTURE.md` — system boundaries and architecture baseline
- `docs/QUALITY_ATTRIBUTES.md` — architecture drivers
- `docs/CORE_BELIEFS.md` — durable engineering principles
- `docs/requirements/` — required behavior
- `docs/adr/` — accepted/proposed architecture decisions
- `docs/domain/` — domain semantics
- `docs/specs/` — data/interface specifications
- `docs/plans/active/` — active execution plans
- `docs/HARNESS_ENGINEERING.md` — agent workflow and feedback-loop requirements
- `docs/DEVELOPMENT.md` — reproducible environment and canonical commands

Use `docs/README.md` as the documentation index.

## Source-of-truth order

When sources conflict, do not silently choose. Report the conflict.

Prefer:

1. accepted requirements;
2. accepted ADRs;
3. accepted domain/spec documents;
4. architecture and quality documents;
5. executable tests/checks;
6. implementation;
7. explicit task-local assumptions.

Research is informative, not automatically normative.

## Working rule

For non-trivial work:

```text
TASK
-> RELEVANT REQUIREMENT
-> RELEVANT DOMAIN / ADR
-> ACTIVE PLAN WHEN NEEDED
-> SMALLEST CORRECT CHANGE
-> AUTOMATED VERIFICATION
-> SELF-REVIEW
-> DOCUMENTATION UPDATE IF CONTRACTS CHANGED
```

Do not invent missing product or engineering rules.

If a material decision is missing, propose the smallest explicit decision artifact instead of burying the choice in code.

## Architecture invariants

- Preserve original telemetry and provenance.
- Import, validation and normalization are separate responsibilities.
- Missing data stays explicit.
- Do not silently resample, repair, rename or infer telemetry.
- Critical numerical analysis must be deterministic when practical.
- AI may explain and investigate structured evidence; it must not replace deterministic engineering calculations.
- Source-specific formats must not define the core engineering domain.
- Prefer the smallest architecture satisfying accepted requirements.
- No microservices, distributed messaging, Kubernetes or cloud dependency without a documented driver.

## Evidence vocabulary

Keep these distinct:

- Measured Data
- Derived Data
- Observation
- Hypothesis
- Engineering Interpretation
- Possible Action
- Missing Evidence

Never present a hypothesis as a measurement or correlation as established causation.

## Canonical harness commands

Run from the repository root.

Setup after installing `uv 0.12.17` and `pnpm 11.27.1`:

```text
uv sync --locked
pnpm install --frozen-lockfile
```

Focused checks:

```text
uv run --locked python scripts/harness.py lint
uv run --locked python scripts/harness.py type
uv run --locked python scripts/harness.py test
uv run --locked python scripts/harness.py docs
uv run --locked python scripts/harness.py arch
uv run --locked python scripts/harness.py fixtures
```

Full verification before completion:

```text
uv run --locked python scripts/harness.py verify
```

Format/fix Python code:

```text
uv run --locked python scripts/harness.py format
```

Do not claim a substantial change is complete while `verify` is failing.

## Change discipline

- Inspect affected files before editing.
- Keep changes focused.
- Avoid unrelated refactors.
- Minimize dependencies.
- Preserve public/domain contracts unless the task explicitly changes them.
- Update requirements, ADRs, specs or domain docs when behavior changes intentionally.
- Do not mark an ADR Accepted unless the maintainer has authorized that decision.
- Do not create speculative abstractions for future features.

## Completion report

For substantial work, report:

- what changed;
- why;
- requirement/ADR involved;
- checks run and results;
- assumptions;
- limitations;
- unresolved issues.

## Current project state

Harness Bootstrap is complete.

The active product-code task is:

`docs/plans/active/003-ome-csv-import-foundation.md`

Keep Plan 003 limited to REQ-001 OME CSV import. Do not pull validation, normalization, API or UI work into that slice.
