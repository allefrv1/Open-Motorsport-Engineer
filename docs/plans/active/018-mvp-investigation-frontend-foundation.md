# Plan 018 — MVP Investigation Frontend Foundation

Status: **Active**

Started: 2026-09-23

## Objective

Implement the first usable React/TypeScript investigation interface over the accepted OME CSV source-to-report HTTP workflow.

The slice must let a user select two controlled lap bundles and understand the deterministic comparison result without constructing engineering DTOs manually.

## Authoritative UX contract

- `docs/specs/mvp-investigation-frontend-v0.1.md`
- ADR-0008 — local HTTP API with React/TypeScript UI
- `skills/ux-design/SKILL.md`
- `skills/ux-design/references/ome-interface-principles.md`

## Product flow

```text
Lap A CSV + sidecar
Lap B CSV + sidecar
-> Compare
-> loading / not-ready / error / success
-> final delta
-> delta over distance
-> deterministic gain/loss observations
-> supporting evidence
-> provenance
```

## First implementation boundary

Plan 018 includes:

- React/TypeScript/Vite product scaffold;
- local API client for Plan 017;
- controlled source form;
- result-state management;
- accessible delta summary;
- lightweight server-series delta visualization;
- deterministic observation rendering;
- supporting-evidence inventory;
- provenance disclosure;
- responsive/accessibility baseline.

## Visualization boundary

Do not add rich synchronized telemetry overlays yet.

Plan 018 may use a lightweight native SVG delta chart.

Plan 019 will introduce the richer synchronized Plotly investigation plots after this end-to-end UI is proven.

## Frontend toolchain

Use current stable major lines compatible with pinned Node 24 and pnpm 11.

Initial packages to lock during implementation:

Runtime:

- React 19;
- React DOM 19.

Development:

- TypeScript 7;
- Vite 8;
- official Vite React plugin;
- Vitest;
- React Testing Library;
- jsdom;
- React type definitions.

Do not add:

- Redux/Zustand;
- router;
- design-system package;
- CSS framework;
- charting library in Plan 018.

The exact resolved patch versions belong in the pnpm lockfile.

## TDD rule

Toolchain/bootstrap may precede product tests.

Product behavior must then follow:

```text
UX / API CONTRACT
-> COMPONENT / FLOW TEST
-> VALID BEHAVIORAL RED
-> MINIMUM IMPLEMENTATION
-> GREEN
-> REFACTOR
-> FRONTEND BUILD
-> FULL REPOSITORY VERIFY
```

A missing dependency/build configuration is not a valid behavioral RED.

## Milestone 1 — frontend executable harness

Add:

- TypeScript configuration;
- Vite configuration;
- Vitest + jsdom test environment;
- React Testing Library;
- build/type/test scripts;
- locked dependencies.

Acceptance:

- existing pinned Node harness still passes;
- a zero-product React test environment can execute;
- production build command can run.

## Milestone 2 — RED workflow tests

Write product tests before `App` behavior.

Cover the acceptance behavior in the UX spec.

Record a RED where tests fail because the source-comparison UI behavior does not yet exist.

## Milestone 3 — source workflow UI

Implement the minimum accessible source form and API client.

Do not duplicate backend semantics.

## Milestone 4 — result investigation view

Implement:

- final delta;
- sign interpretation;
- delta chart;
- observation regions;
- supporting evidence;
- provenance details.

No causal diagnosis.

## Milestone 5 — UX and accessibility review

Review against the OME UX skill:

- task success;
- information hierarchy;
- errors/not-ready;
- evidence trust;
- keyboard/focus;
- responsive behavior;
- cognitive load.

Blocking defects must be corrected before completion.

## Verification

Plan 018 completion requires:

- frontend tests green;
- frontend production build green;
- root canonical `verify` green;
- no backend/domain behavior changed merely for UI convenience.

## Completion criteria

- toolchain locked;
- tests committed before product behavior;
- valid behavioral RED recorded;
- browser source workflow works against Plan 017 contract;
- success/not-ready/error/loading states covered;
- final delta + observations + evidence + provenance visible;
- accessibility baseline covered by executable tests where practical;
- production build succeeds;
- canonical verify succeeds.

## Explicitly out of scope

- synchronized telemetry overlay suite;
- Plotly integration;
- track map;
- project persistence;
- multi-page routing;
- desktop wrapper;
- AI.
