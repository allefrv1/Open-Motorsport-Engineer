# Open Motorsport Engineer (OME) — Codex Instructions

Version: 0.1.0  
Status: Pre-implementation / architecture foundation

## Project

You are working on **Open Motorsport Engineer (OME)**, an open-source motorsport engineering analysis platform.

Mission:

> Reduce the gap between motorsport data and the engineering knowledge required to interpret it.

OME should make engineering analysis more understandable, transparent, traceable and reproducible.

OME is not intended to begin as:

- a MoTeC clone;
- a generic telemetry viewer;
- a chatbot over raw telemetry;
- a black-box setup recommendation system;
- a complete vehicle simulation platform.

Core reasoning chain:

```text
RAW DATA
  -> VALIDATED DATA
  -> NORMALIZED DATA
  -> DERIVED METRICS
  -> OBSERVATIONS
  -> HYPOTHESES
  -> ENGINEERING INTERPRETATION
  -> HUMAN DECISION
```

## Current Stage

OME is currently in discovery, domain-definition, requirements and architecture-foundation work.

Do not assume that frameworks, databases, deployment architecture, module boundaries or persistence models have already been decided unless they are documented in the repository.

Do not silently turn implementation choices into architecture decisions.

## Read Before Changing

Before substantial work:

1. inspect the repository structure;
2. read documentation relevant to the task;
3. inspect existing code and tests in the affected area;
4. identify applicable requirements and ADRs;
5. understand the involved domain concepts.

When present, use these as navigation points:

- `docs/PROJECT.md`
- `docs/DOMAIN.md`
- `docs/ARCHITECTURE.md`
- `docs/requirements/`
- `docs/adr/`
- `docs/domain/`
- `docs/research/`

Do not invent missing documents. If required information is absent, report the gap.

## Sources of Truth

Prefer this order when determining intended behavior:

1. accepted requirements;
2. accepted ADRs;
3. domain specifications;
4. architecture documentation;
5. intentional tests;
6. existing implementation;
7. explicitly stated assumptions.

Research material is evidence and context, but it is not automatically a project rule.

If authoritative sources conflict, report the conflict instead of silently choosing one.

## Engineering Workflow

For non-trivial work, follow:

```text
PROBLEM
  -> DOMAIN
  -> USE CASE
  -> REQUIREMENT
  -> ACCEPTANCE CRITERIA
  -> ARCHITECTURE
  -> IMPLEMENTATION
  -> VERIFICATION
```

Before implementing, determine:

- the user problem;
- the relevant requirement;
- the domain concepts involved;
- expected behavior;
- important edge cases;
- applicable architecture decisions;
- how the result will be verified.

If these already exist, use them. Do not recreate decisions unnecessarily.

## Prefer the Smallest Correct Change

Prefer the simplest design that satisfies current requirements.

Do not introduce without a demonstrated need:

- microservices;
- distributed messaging;
- Kubernetes;
- event sourcing;
- complex CQRS;
- speculative plugin systems;
- unnecessary abstraction layers;
- premature optimization;
- cloud dependencies;
- machine-learning pipelines.

When proposing substantial complexity, identify the requirement or architecture driver that justifies it.

## Motorsport Domain Discipline

Do not invent motorsport engineering rules.

Use validated project domain documentation and accepted engineering references.

Always distinguish:

- **Measured Data** — acquired directly from a source;
- **Derived Data** — deterministically calculated;
- **Observation** — objective description of what the data shows;
- **Hypothesis** — possible explanation;
- **Engineering Interpretation** — conclusion supported by evidence and context;
- **Possible Action** — test, change or next investigation.

Never silently convert a hypothesis into a measured fact.

Never present correlation as causation without supporting evidence.

When evidence is insufficient, say so instead of inventing a diagnosis.

## Domain Language

Prefer motorsport concepts over infrastructure terminology.

Examples include:

`Event`, `Session`, `Run`, `Stint`, `Lap`, `Segment`, `Corner`, `Driver`, `Vehicle`, `Track`, `Setup`, `Setup Change`, `Tyre Set`, `Driver Feedback`, `Run Plan`, `Telemetry Dataset`, `Channel`, `Measurement`, `Metric`, `Observation`, `Hypothesis`, `Investigation`, `Finding`, `Decision`.

Infrastructure should represent the domain, not define it.

## Telemetry Integrity

Treat original telemetry as evidence.

Raw source data must not be silently modified or overwritten.

Transformations must preserve provenance.

Do not assume similarly named signals are equivalent. For example, GPS speed, ECU vehicle speed, wheel speed and calculated ground speed may represent related but distinct measurements.

When working with telemetry, consider at least:

- channel identity;
- source;
- unit;
- timestamps;
- sample rate;
- calibration;
- synchronization;
- missing data;
- signal quality;
- provenance.

Do not silently repair suspicious data.

## Deterministic Engineering Core

Critical numerical and signal-processing behavior should be deterministic whenever practical.

Prefer:

```text
TELEMETRY
  -> DETERMINISTIC COMPUTATION
  -> STRUCTURED EVIDENCE
  -> AI INTERPRETATION / EXPLANATION
```

Avoid:

```text
RAW TELEMETRY
  -> LLM
  -> ENGINEERING CONCLUSION
```

AI may help organize investigations, explain concepts, relate structured evidence, formulate hypotheses, identify missing evidence and document findings.

AI should not replace deterministic engineering calculations.

## AI Rules

AI output must not fabricate:

- telemetry values;
- sensor availability;
- setup values;
- driver feedback;
- run metadata;
- calculation results;
- engineering references;
- test results.

When information is unavailable, mark it as unavailable.

Preserve the distinction between:

```text
OBSERVATION
HYPOTHESIS
EVIDENCE
MISSING EVIDENCE
UNCERTAINTY
NEXT INVESTIGATION
```

## Coding Rules

When implementation is appropriate:

- inspect affected code before editing;
- follow established repository conventions;
- make focused changes;
- avoid unrelated refactors;
- prefer explicit types and clear names;
- minimize new dependencies;
- avoid hidden side effects;
- do not duplicate domain or engineering logic;
- keep deterministic behavior deterministic;
- add or update relevant tests.

Do not create abstractions for hypothetical future requirements unless current requirements justify them.

## Tests

A task is not complete merely because the code builds or runs once.

Add or update tests for relevant behavior.

For domain and telemetry logic, consider:

- expected behavior;
- boundary conditions;
- missing or invalid data;
- units;
- sample-rate differences;
- synchronization;
- deterministic output;
- provenance;
- regressions.

Run relevant tests before finishing when execution is available.

Do not hide failing tests caused by the change.

## Architecture Decisions

If a task requires a meaningful architectural decision that is not already documented, propose an ADR rather than silently committing the decision through implementation.

An ADR should capture:

- context;
- problem;
- decision;
- alternatives;
- consequences;
- risks;
- status.

Do not mark an ADR as accepted unless the maintainer explicitly accepts it.

## Documentation

Documentation is part of the system.

Update relevant documentation when a change intentionally alters domain semantics, architecture boundaries, public contracts, data contracts or engineering calculations.

Do not duplicate detailed project knowledge inside this file.

`AGENTS.md` defines **how Codex should work**. Detailed project knowledge belongs in `docs/`.

## Assumptions

Do not silently invent requirements.

When an assumption materially affects design or behavior, state it explicitly.

If a safe, reversible and local assumption allows progress, it may be used when clearly documented.

Do not make irreversible or architectural assumptions silently.

## Completion

Before considering substantial work complete, verify:

- requested behavior is implemented;
- relevant requirements are satisfied;
- domain terminology remains consistent;
- architecture boundaries are respected;
- data integrity is preserved where applicable;
- relevant tests pass;
- documentation remains consistent;
- assumptions are explicit;
- unrelated changes were not introduced.

At completion, summarize:

- what changed;
- why;
- tests or validation performed;
- important assumptions;
- known limitations;
- unresolved issues.

## Core Principle

> OME does not exist to make engineering disappear. It exists to make engineering understandable.

Build software that preserves evidence, exposes reasoning, respects uncertainty and keeps the human engineer in control.
