# ADR-0003 — AI is not the deterministic engineering core

Status: **Accepted**

Date: 2026-09-22

## Context

OME intends to make engineering reasoning easier to understand and may use AI to help users investigate telemetry.

Large language models are useful for explanation, navigation and hypothesis generation, but they are not an appropriate authoritative mechanism for deterministic numerical engineering calculations.

Allowing AI to calculate or fabricate critical telemetry results would undermine reproducibility, auditability and user trust.

## Decision

Critical numerical analysis, signal processing, alignment and metric calculation must live outside the generative AI layer whenever deterministic implementation is practical.

The intended flow is:

```text
TELEMETRY
  -> DETERMINISTIC ENGINEERING CORE
  -> STRUCTURED EVIDENCE
  -> AI-ASSISTED INVESTIGATION / EXPLANATION
  -> HUMAN DECISION
```

AI may:

- explain engineering concepts;
- organize investigations;
- request deterministic analyses;
- compare structured evidence;
- formulate hypotheses;
- identify missing evidence;
- draft engineering summaries.

AI must not:

- invent telemetry values;
- silently calculate critical metrics from raw samples in natural language;
- hide uncertainty;
- present hypotheses as measured facts;
- make essential local analysis depend on cloud availability.

## Consequences

The project needs explicit contracts between engineering results and the future OME Engineer agent.

This creates more structure but makes analysis reproducible and testable independently of a model provider.

## Related requirements

- REQ-006 — Preserve Analysis Evidence

## Related principles

- integrity;
- reproducibility;
- auditability;
- data ownership;
- offline usability.
