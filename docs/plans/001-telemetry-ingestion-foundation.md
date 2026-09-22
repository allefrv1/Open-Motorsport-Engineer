# Plan 001 — Telemetry Ingestion Foundation

Status: **Planning**

## Goal

Reach an implementation-ready definition of OME telemetry ingestion without writing production code prematurely.

## Current inputs

- project definition;
- domain map;
- architecture foundation;
- proposed REQ-001;
- research on CSV and professional telemetry workflows;
- initial source strategy: OME CSV, iRacing `.ibt`, MoTeC `.ld` / export.

## Work sequence

### Phase 1 — Domain and evidence model

1. Review the Telemetry Import Model.
2. Confirm required vs optional provenance.
3. Confirm whether SampleSeries can represent multiple independent time bases.
4. Define how import warnings differ from validation failures.

### Phase 2 — Source inspection

Inspect representative examples from:

1. OME-controlled CSV;
2. iRacing `.ibt`;
3. MoTeC-exported CSV;
4. native MoTeC `.ld` if legal/technical access is confirmed.

For each source record:

- metadata available;
- channel identity;
- units;
- time representation;
- sample-rate representation;
- missing-data behavior;
- session/run/lap metadata;
- source-specific constraints.

### Phase 3 — Requirement refinement

Refine REQ-001 with:

- minimum provenance;
- partial-import policy;
- duplicate-source policy;
- first supported source order;
- acceptance fixtures.

Create a separate validation requirement rather than placing quality analysis inside import.

### Phase 4 — Architecture decision

Review ADR-0001.

Only after source inspection should maintainers accept, revise or reject the proposed separation of ingestion and normalization.

### Phase 5 — OME CSV Exchange Profile

Define a project-owned CSV profile for:

- deterministic fixtures;
- examples;
- simple interoperability.

Do not use the CSV profile as the canonical internal data model unless later evidence justifies that decision.

### Phase 6 — Implementation readiness

Before production code begins, the project should have:

- accepted REQ-001;
- accepted or revised ADR-0001;
- reviewed Telemetry Import Model;
- at least one real representative source fixture;
- defined acceptance criteria that can be automated;
- documented expected dataset scale for the first vertical slice.

## Explicitly deferred

- language/framework selection;
- database selection;
- desktop/web packaging;
- AI provider;
- vector database;
- live telemetry;
- complete canonical telemetry model;
- advanced engineering metrics.

## Completion criterion

This plan is complete when a Codex implementation task can be written without asking Codex to invent:

- source semantics;
- provenance rules;
- stage boundaries;
- success/failure behavior;
- the first acceptance dataset.
