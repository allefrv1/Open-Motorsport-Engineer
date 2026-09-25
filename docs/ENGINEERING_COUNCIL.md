# OME Engineering Council

Status: **Accepted operating model**

Date: 2026-09-25

## Composition

- Software / Architecture Agent
- Motorsport Mechanical Engineering Agent
- Physics Review Agent
- CEO / Maintainer as human product authority

## Purpose

Cross-domain decisions should not be made from a single viewpoint.

The council reviews material changes involving:

- telemetry semantics;
- physics/numerical methods;
- vehicle-dynamics analysis;
- engineering metrics;
- setup/driver interpretation;
- material architecture/domain changes;
- AI engineering explanations.

## Review sequence

```text
OBJECTIVE
-> EVIDENCE
-> SOFTWARE REVIEW
-> MOTORSPORT REVIEW
-> PHYSICS REVIEW
-> DISAGREEMENTS / MISSING EVIDENCE
-> IMPROVEMENT OPTIONS
-> DECISION / HUMAN GATE
-> KANBAN TRANSITION
```

## Decisions

- READY
- READY_WITH_ACTIONS
- NOT_READY
- HUMAN_GATE_REQUIRED

Do not force consensus.

A specialist objection remains explicit until stronger evidence, a narrower claim, a revised spec, an experiment or an appropriate human product decision resolves it.

## Authority

Specialists can block unsupported claims inside their domains.

They do not replace the CEO for product priority or irreversible product decisions.

## Durable output

Every material council review produces an artifact under:

`docs/reviews/`

Use:

`docs/reviews/0000-engineering-council-template.md`

## TDD relationship

Council establishes/validates the engineering contract.

TDD verifies implementation.

Neither replaces the other.
