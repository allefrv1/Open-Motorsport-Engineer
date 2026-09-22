# OME Harness Engineering

Status: **Accepted operating model**

## Purpose

OME is intended to be built primarily with coding agents such as Codex.

The engineering problem is therefore not only to design the software. It is also to design the environment, context, constraints and feedback loops that let an agent modify the repository reliably.

## Harness goals

A coding agent should be able to answer, from the repository alone:

1. What problem am I solving?
2. Which requirement defines success?
3. Which domain rules apply?
4. Which architecture decisions constrain the solution?
5. Which files/modules are relevant?
6. How do I verify the change?
7. Which failures block completion?
8. What must be documented if behavior changes?

## Context design

### Root AGENTS.md

The root `AGENTS.md` is a map, not an encyclopedia.

It should remain small and stable and direct agents toward deeper sources of truth.

### Progressive disclosure

Agents should load only the context relevant to the current task.

Detailed domain, specification and architecture knowledge belongs under `docs/`.

### Nested AGENTS.md

Create nested instructions only after implementation modules exist and require local rules.

Likely future examples:

- ingestion — preserve source evidence;
- analysis — deterministic calculations and metric provenance;
- AI — never fabricate or replace measured evidence.

## Repository knowledge model

```text
AGENTS.md
    |
    v
docs/README.md
    |
    +--> PROJECT / MVP / CORE_BELIEFS
    +--> ARCHITECTURE / QUALITY
    +--> requirements/
    +--> adr/
    +--> domain/
    +--> specs/
    +--> plans/
    +--> references/
```

## Execution plans

Small, obvious changes do not require durable plans.

Substantial or multi-step work uses an execution plan with:

- objective;
- requirements;
- current state;
- constraints;
- milestones;
- verification;
- progress log;
- decisions discovered during execution;
- completion state.

Plans live in:

- `docs/plans/active/`
- `docs/plans/completed/`

Durable discoveries must be promoted to requirements, ADRs, specs or domain documentation.

## Feedback loop

The desired agent loop is:

```text
UNDERSTAND
-> PLAN
-> CHANGE
-> RUN CHECKS
-> INSPECT RESULT
-> SELF-REVIEW
-> FIX
-> RE-RUN CHECKS
-> UPDATE DURABLE DOCS
-> COMPLETE
```

A task is not complete because code was generated.

## Mechanical enforcement

Once implementation begins, the harness must provide canonical commands and CI checks for at least:

- formatting;
- linting;
- static/type checks;
- unit tests;
- integration tests;
- documentation-link/structure validation;
- architecture dependency boundaries;
- fixture metadata/licensing checks.

Important architecture invariants should migrate from prose into executable checks when feasible.

## Architecture legibility

The code layout should allow an agent to infer responsibility from location.

Forbidden patterns should eventually be mechanically detected, including:

- domain depending on API/framework layers;
- source-adapter semantics leaking into domain entities;
- deterministic analysis calling generative AI;
- hidden telemetry mutation;
- oversized catch-all utility modules.

## Testability

Every accepted requirement should eventually connect to executable evidence:

```text
Requirement
-> acceptance criterion
-> test/check
-> CI result
```

## Fixtures as part of the harness

Representative data is required for agent reliability.

Fixtures must record:

- origin;
- licensing/redistribution status;
- expected behavior;
- purpose;
- provenance;
- size class.

The repository should contain small public/synthetic fixtures and define how private/large fixtures are used outside the public tree.

## Quality and drift

Agent-generated repositories accumulate pattern drift quickly.

OME will maintain:

- `docs/QUALITY_SCORE.md`
- `docs/plans/tech-debt-tracker.md`

Once code exists, recurring maintenance should convert repeated review feedback into:

- tests;
- linters;
- templates;
- documentation;
- structural checks.

## Autonomy boundary

Agents may make local, reversible implementation choices inside accepted requirements and ADRs.

Escalate when a task requires:

- changing product scope;
- accepting a new irreversible architecture direction;
- weakening data/evidence guarantees;
- changing licensing;
- changing public data contracts materially;
- making an engineering claim unsupported by validated domain knowledge.

## Current readiness

OME has a strong documentation foundation but does **not** yet have an executable harness.

The next implementation phase must therefore be **harness bootstrap**, before feature development.
