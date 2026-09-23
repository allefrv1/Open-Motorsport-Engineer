# Plan 019 — Synchronized Telemetry Investigation Plots

Status: **Active**

Started: 2026-09-23

## Objective

Add synchronized engineering telemetry plots to the existing Plan 018 investigation workspace without moving deterministic analysis into the browser.

## Authoritative contracts

- `docs/specs/mvp-telemetry-overlays-frontend-v0.1.md`
- ADR-0008 — local HTTP API with React/TypeScript UI
- Plans 009–014 — comparison/overlay/report contracts
- OME interface principles

## Dependency decision

Use Plotly.js directly behind an isolated UI visualization adapter.

Reviewed current package line:

- `plotly.js-dist-min` 4.1.1.

Reason:

- ADR-0008 already accepts Plotly.js;
- the distributed minified package includes TypeScript declarations;
- no React wrapper is required for the first implementation;
- one plotting dependency keeps the UI boundary smaller.

The resolved dependency graph must be locked by pnpm before product implementation.

## TDD rule

Tooling may be added and proven green first.

Product behavior then follows:

```text
PLOT CONTRACT
-> FIGURE MODEL / COMPONENT TEST
-> VALID RED
-> MINIMUM PLOTLY ADAPTER
-> GREEN
-> ACCESSIBILITY / UX REVIEW
-> FULL VERIFY
```

## Milestone 1 — visualization dependency

- add Plotly.js;
- regenerate lockfile reproducibly;
- keep canonical frontend typecheck/build green.

## Milestone 2 — pure figure model

Before Plotly rendering, test and implement a pure transformation from report DTOs to a presentation-only figure model.

It may choose:

- subplot domains;
- trace names/styles;
- axis labels.

It must not change numerical telemetry values.

## Milestone 3 — Plotly adapter

Add a component that owns:

- Plotly lifecycle;
- responsive resize;
- shared x-axis;
- unified hover;
- purge/cleanup.

No application/service layer imports Plotly.

## Milestone 4 — accessible exact-value fallback

Render collapsed semantic tables from the same server arrays.

## Milestone 5 — integration

Integrate the synchronized telemetry figure below the deterministic delta summary while preserving:

- source selection;
- not-ready/error states;
- observations;
- supporting evidence;
- provenance.

## UX review

Verify:

- Lap A/B distinguishable without color alone;
- units adjacent to channel identity;
- missing channels remain explicit;
- exact values accessible without hover;
- zoom/pan does not change source evidence;
- narrow-width behavior remains usable.

## Completion criteria

- Plotly dependency locked;
- tests precede plotting behavior;
- valid RED recorded;
- continuous overlays pass through unchanged;
- gear discrete presentation;
- one shared distance reference;
- accessible exact-value tables;
- existing Plan 018 tests remain green;
- frontend build and repository verify GREEN.

## Explicitly out of scope

- track map;
- corner segmentation;
- linked track cursor;
- persistence;
- AI interpretation.
