# Open Motorsport Engineer — Codex Map

Version: 0.2.0

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
-> PLAN WHEN NEEDED
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

## Change discipline

- Inspect affected files before editing.
- Keep changes focused.
- Avoid unrelated refactors.
- Minimize dependencies.
- Preserve public/domain contracts unless the task explicitly changes them.
- Update requirements, ADRs, specs or domain docs when behavior changes intentionally.
- Do not mark an ADR Accepted unless the maintainer has authorized that decision.
- Do not create speculative abstractions for future features.

## Verification

When executable tooling exists, run the repository-prescribed checks before finishing.

The harness bootstrap will define canonical commands for:

- formatting/linting;
- type/static checks;
- unit/integration tests;
- documentation structure/link checks;
- architecture-boundary checks.

Until those commands exist, do not claim the repository is fully harness-ready.

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

The product/domain/architecture documentation foundation exists.

Feature implementation must not begin before the active harness-bootstrap plan is completed, unless the maintainer explicitly overrides that gate.
