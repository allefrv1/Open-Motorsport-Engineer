# Plan 018 — MVP Investigation Frontend

Status: **Active**

Started: 2026-09-23

## Objective

Implement the first real OME user interface against the verified local source-upload workflow.

The frontend must let a user:

1. select two controlled OME CSV lap bundles;
2. request a deterministic comparison;
3. understand readiness/missing evidence;
4. inspect delta-time, observations and supporting telemetry;
5. inspect provenance/method when needed.

The frontend is an investigation workspace, not a generic dashboard.

## Requirements / decisions

Primary product scope:

- MVP — first vertical slice;
- REQ-005 — Compare Two Laps;
- REQ-006 — Preserve Analysis Evidence.

Architecture:

- ADR-0008 — local FastAPI + React/TypeScript/Vite UI;
- Plotly.js as the initial replaceable visualization adapter;
- Plan 017 OME CSV multipart source workflow.

UX:

- `skills/ux-design/SKILL.md`;
- `skills/ux-design/references/ome-interface-principles.md`;
- `docs/specs/mvp-investigation-frontend-v0.1.md`.

## User job

The primary user question is:

> Where did Lap B gain or lose time relative to Lap A, and what evidence supports that observation?

Every first-slice interface element must contribute to selecting evidence, understanding readiness, inspecting the deterministic answer, or tracing the evidence.

## Information architecture

One focused screen:

1. application/local-service header;
2. Lap A / Lap B source selection;
3. compare action + progressive comparison settings;
4. result context / sign convention;
5. delta summary;
6. deterministic observation regions;
7. telemetry investigation plots;
8. missing evidence;
9. provenance/method detail.

Do not create navigation for future features.

## Interaction states

Must implement and test:

- idle;
- ready to compare;
- loading;
- success;
- import not-ready;
- preparation not-ready;
- report not-ready;
- transport/server error.

No state may fabricate chart/evidence data.

## Frontend technology slice

The accepted architecture already selects React, TypeScript, Vite and Plotly.js.

Plan 018 may introduce only the minimum locked package set needed to implement and test that stack.

Before dependency changes:

- verify current compatible package versions from authoritative registries/docs;
- pin/lock via pnpm;
- keep dependency count focused.

Expected development categories:

- React runtime;
- Vite React integration;
- strict TypeScript;
- component/user-flow test runner;
- DOM testing utilities;
- Plotly adapter/types.

Do not add a broad design-system dependency for the first screen.

## Development API connectivity

Use a Vite development proxy for `/api` and `/healthz` to the loopback FastAPI process.

Do not widen backend CORS policy merely to make the Vite dev server work.

The browser frontend sends relative API URLs.

## TDD / frontend feedback rule

Critical behavior is test-first:

```text
FRONTEND SPEC / USER FLOW
-> COMPONENT / API-CLIENT TEST
-> VALID RED
-> MINIMUM REACT/TS IMPLEMENTATION
-> GREEN
-> ACCESSIBILITY / UX REVIEW
-> PRODUCTION BUILD
-> FULL REPOSITORY VERIFY
```

A RED counts only when it demonstrates missing frontend behavior, not missing test configuration.

## Initial executable test targets

Before product components exist, tests should require:

- accessible Lap A/Lap B CSV + sidecar inputs;
- Compare disabled until all four files are selected;
- selected filenames remain visible;
- optional grid-step input uses metres and defaults to `1.0`;
- submitting builds the accepted multipart form fields;
- loading state disables repeat submission and announces processing;
- success shows `Delta = B - A` convention;
- controlled success response shows `+0.200 s` at `100 m`;
- deterministic observations are rendered without causal wording;
- missing supporting evidence is visible rather than zero-filled;
- import/preparation/report not-ready states are distinguishable;
- transport error is distinguishable from engineering not-ready;
- provenance is available through progressive disclosure;
- plot adapter receives common distance grid and series data;
- all primary form controls have accessible labels.

## Plot contract

Do not recompute backend analysis.

The UI consumes the report DTO.

Plotting:

- delta-time aligned by distance;
- continuous overlays from `continuous_overlays`;
- discrete gear from `gear_overlay`;
- omit unavailable series and show corresponding Missing Evidence;
- preserve units;
- preserve Lap A/Lap B identity;
- no smoothing.

The Plotly adapter is presentation only.

## Evidence semantics

The UI must visually distinguish at least:

- Derived metric — delta/overlays;
- Observation — B gain/B loss/neutral regions;
- Missing Evidence.

Measured/source provenance remains discoverable in detail.

Do not introduce hypothesis, cause, driver grading, setup recommendation or AI explanation.

## Accessibility

Target WCAG 2.2 AA baseline.

Must verify:

- keyboard-only source selection/submission path;
- visible focus;
- semantic headings/fieldsets;
- live status/error announcement;
- non-color-only Lap/sign distinctions;
- accessible chart names plus textual result summary;
- `details`/provenance keyboard operation;
- usable zoom/reflow.

## Responsive scope

Desktop-first engineering workspace, not desktop-only.

Wide:

- Lap A/B selectors may sit side by side.

Narrow:

- selectors and summary stack;
- evidence stays accessible;
- charts retain readable dimensions;
- dense detail may scroll intentionally.

## Harness changes

The canonical repository verification must grow with the frontend.

Plan 018 should add focused frontend commands for at least:

- test;
- typecheck;
- production build.

The root harness should run these in CI before the plan is considered complete.

Do not claim a frontend implementation is complete if only backend tests are green.

## UX review

Before completion, run `skills/ux-design/references/ux-review-checklist.md`.

Classify findings as Must Fix, Should Improve, or Polish.

Must Fix items related to task completion, correctness/evidence trust or WCAG baseline block completion.

## Completion criteria

- frontend UX/spec accepted before implementation;
- React/TypeScript/Vite/Plotly dependency set locked;
- frontend critical-flow tests committed before implementation;
- behavioral RED recorded;
- source-selection/upload flow GREEN;
- success/not-ready/error states GREEN;
- comparison evidence/observations/provenance rendered truthfully;
- frontend typecheck GREEN;
- production build GREEN;
- canonical repository verify includes frontend product checks and is GREEN;
- UX/accessibility review completed with no Must Fix items.

## Explicitly out of scope

- project/session persistence;
- saved comparisons;
- routing/multi-page IA;
- user accounts;
- cloud backend;
- generic source upload;
- MoTeC/iRacing browser upload;
- AI;
- causal diagnosis;
- setup recommendation;
- live telemetry;
- Docker Compose.

## Docker relationship

ADR-0010 remains Proposed.

A second real application process now exists once Plan 018 is implemented, so Docker Compose may become technically discussable **after** the frontend works locally.

Plan 018 itself does not require accepting ADR-0010 or adding Compose.
