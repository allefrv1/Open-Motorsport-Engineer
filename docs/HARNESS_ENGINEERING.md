# OME Harness Engineering

Status: **Accepted operating model**

## Purpose

OME is intended to be built primarily with coding agents such as Codex.

The engineering problem is therefore not only to design the software. It is also to design the environment, context, constraints and feedback loops that let an agent modify the repository reliably.

## Relationship to the layered model

Harness Engineering is one layer in the broader OME agent operating model:

`docs/AGENT_ENGINEERING_MODEL.md`

The model separates:

```text
Prompt Engineering
-> Context Engineering
-> Harness Engineering
-> Loop Engineering
-> Graph Engineering
```

Harness failures must not be confused with behavior failures. A formatter, environment or CI problem is not a behavioral RED.

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

Create nested instructions only when a module has meaningful local rules that the root map should not carry.

Likely examples:

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

For behavior changes, the operational agent loop is test-first:

```text
UNDERSTAND
-> PLAN
-> WRITE FOCUSED TEST
-> RED: CONFIRM EXPECTED FAILURE
-> IMPLEMENT SMALLEST CHANGE
-> GREEN: RUN FOCUSED TEST
-> REFACTOR
-> SELF-REVIEW
-> RUN FULL VERIFY
-> UPDATE DURABLE DOCS
-> COMPLETE
```

For documentation-only, build, tooling or characterization work, use the closest equivalent feedback loop without manufacturing a meaningless failing test.

A task is not complete because code was generated.

Before fixing a failed loop iteration, classify the failure using the layered model:

- PROMPT_GAP;
- CONTEXT_GAP;
- DECISION_GAP;
- HARNESS_FAILURE;
- BEHAVIOR_FAILURE;
- REGRESSION_FAILURE;
- EVIDENCE_FAILURE.

Route the task back to the highest layer that owns the failure.

## Mechanical enforcement

The repository provides canonical checks for:

- formatting;
- linting;
- static/type checking;
- unit tests;
- frontend runtime tests;
- documentation links/status/indexes;
- architecture dependency boundaries/cycles;
- fixture metadata/licensing;
- complete verification.

See `docs/DEVELOPMENT.md`.

Important architecture invariants should continue migrating from prose into executable checks as implementation grows.

## Architecture legibility

The code layout should allow an agent to infer responsibility from location.

Initial forbidden dependency patterns are mechanically checked.

Future recurring violations should be converted into stronger structural rules rather than repeatedly corrected in review.

## Testability

Every accepted feature requirement should move toward:

```text
Requirement
-> acceptance criterion
-> executable test/check
-> CI result
```

REQ-001, REQ-002 and REQ-004 already have requirement-to-test traceability.

New deterministic product behavior should establish the acceptance test before implementation and retain evidence that the test failed for the intended missing behavior before the production change made it pass.

## Fixtures as part of the harness

Fixtures record provenance/licensing and are mechanically checked.

The repository contains:

- project-owned synthetic OME data;
- small licensed public data;
- negative validation fixtures.

Private/large fixtures may be used outside the public tree when redistribution is inappropriate.

## Quality and drift

OME maintains:

- `docs/QUALITY_SCORE.md`;
- `docs/plans/tech-debt-tracker.md`.

Repeated agent mistakes are inputs to harness evolution.

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

The initial executable harness is operational and proven by CI.

Feature work may proceed in narrow, requirement-linked plans while preserving the same verification loop.
