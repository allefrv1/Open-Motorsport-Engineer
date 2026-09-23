# OME Documentation

This directory is the versioned system of record for Open Motorsport Engineer.

Use progressive disclosure: start here, then open only documents relevant to the task.

## Start here

- [PROJECT.md](PROJECT.md) — mission, users, scope and current phase
- [MVP.md](MVP.md) — first vertical slice
- [CORE_BELIEFS.md](CORE_BELIEFS.md) — durable engineering principles
- [ARCHITECTURE.md](ARCHITECTURE.md) — top-level architecture map
- [QUALITY_ATTRIBUTES.md](QUALITY_ATTRIBUTES.md) — architecture drivers
- [HARNESS_ENGINEERING.md](HARNESS_ENGINEERING.md) — agent operating model
- [DEVELOPMENT.md](DEVELOPMENT.md) — pinned environment and canonical verification commands
- [QUALITY_SCORE.md](QUALITY_SCORE.md) — current harness maturity
- [PRE_CODE_READINESS.md](PRE_CODE_READINESS.md) — go/no-go assessment
- [ROADMAP.md](ROADMAP.md) — engineering sequence

## Current execution

- [Plan 022 — GPS Path Distance Foundation](plans/active/022-gps-path-distance-foundation.md)

## Verification and implementation guidance

- [TEST_STRATEGY.md](TEST_STRATEGY.md)
- [PLANNED_REPOSITORY_STRUCTURE.md](PLANNED_REPOSITORY_STRUCTURE.md)

## Durable knowledge

- [requirements/](requirements/) — required behavior
- [adr/](adr/) — architecture decisions
- [domain/](domain/) — accepted domain semantics
- [specs/](specs/) — data/interface specifications

## Working and supporting knowledge

- [plans/](plans/) — active/completed execution plans and debt
- [research/](research/) — informative research, not automatically normative
- [references/](references/) — external source registry

## Knowledge promotion

```text
EXTERNAL SOURCE / RESEARCH
  -> REVIEW
  -> REQUIREMENT / ADR / DOMAIN / SPEC
  -> PLAN
  -> IMPLEMENTATION
  -> AUTOMATED VERIFICATION
  -> QUALITY / DEBT FEEDBACK
```

## Conflict rule

If two authoritative repository sources conflict, stop and surface the conflict.

Do not silently treat existing code as more authoritative than an accepted requirement or ADR.
