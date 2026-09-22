# Engineering Execution Plans

Plans are first-class working artifacts for substantial or multi-step work.

## Structure

- `active/` — work currently in progress or next to execute
- `completed/` — finished plans retained for history
- `tech-debt-tracker.md` — known debt and missing guardrails

## When to create a plan

Use a durable execution plan when work is:

- multi-step;
- cross-cutting;
- expected to span a long agent run;
- likely to discover decisions during execution;
- risky enough that progress and verification should remain visible.

Small, obvious changes do not need a durable plan.

## Required plan content

A substantial plan should include:

- objective;
- requirements involved;
- current state;
- constraints;
- milestones;
- affected areas;
- verification strategy;
- progress/decision log;
- risks;
- completion criteria.

## Promotion rule

Plans are temporary execution state.

Durable discoveries must be promoted into:

- requirements;
- ADRs;
- specs;
- domain docs;
- architecture/quality docs.

A completed plan should move from `active/` to `completed/`.
