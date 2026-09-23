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

## TDD execution evidence

### Tooling baseline

Before product plot behavior:

- OME CI #225 passed the complete canonical verify;
- `plotly.js-dist-min` 4.1.1 was locked with no transitive dependencies;
- existing frontend tests, TypeScript and production build remained green.

### Pure figure model

OME CI #226 exposed both the intended missing module and test-type noise, so it is not counted as the behavioral RED.

After isolating the test contract:

- OME CI #227 — valid RED: `telemetryFigureModel` did not exist;
- OME CI #228 — implementation reached tests; the test fixture omitted the server `time_unit` field;
- OME CI #229 — GREEN after correcting the fixture contract, with the pure figure model unchanged.

The figure model proves:

- delta remains first;
- continuous overlays use deterministic preferred ordering;
- missing overlays are not synthesized;
- server arrays are passed through by reference;
- Lap A/B have redundant solid/dashed identities;
- gear is marked as discrete step data;
- units remain attached to concepts.

### Plotly adapter and exact-value fallback

- OME CI #230 — valid RED: `TelemetryInvestigationPlots` did not exist;
- OME CI #231/#232 — TypeScript feedback at the readonly-array / Plotly type boundary;
- OME CI #233 — GREEN after the minimum isolated Plotly adapter and semantic exact-value tables.

No source arrays are copied, smoothed, re-interpolated or numerically modified.

### Application integration

- OME CI #234 — valid RED: successful comparison flow did not yet expose the `Synchronized telemetry` investigation section;
- OME CI #237 — GREEN after integrating the new plots below the deterministic delta summary while preserving all Plan 018 workflow tests;
- OME CI #238 — GREEN after adding a structural guardrail proving only `PlotlyTelemetryFigure.tsx` imports Plotly.

## Implementation traceability

Tooling:

- `frontend/package.json`;
- `pnpm-lock.yaml`.

Pure presentation model:

- `frontend/src/telemetryFigureModel.ts`;
- `frontend/tests/telemetryFigureModel.test.ts`.

Visualization boundary:

- `frontend/src/PlotlyTelemetryFigure.tsx`;
- `frontend/src/TelemetryInvestigationPlots.tsx`;
- `frontend/tests/telemetryInvestigationPlots.test.tsx`.

Application integration:

- `frontend/src/App.tsx`;
- `frontend/src/styles.css`;
- `frontend/tests/app.test.tsx`.

Architecture guardrail:

- `frontend/tests/harness.test.mjs`.

## UX / accessibility review

Resolved blocking items:

- **comparison meaning** — Lap A remains solid/reference; Lap B dashed/comparison; delta stays explicitly B - A;
- **synchronization** — all panels share the server distance basis and unified horizontal interaction;
- **units** — channel identity and exact tables keep units adjacent;
- **missing evidence** — unavailable concepts are not synthesized and remain visible in the existing Supporting Evidence section;
- **precision** — collapsed semantic tables expose exact server values without requiring hover;
- **discrete gear** — rendered with step-shaped traces rather than linear interpolation;
- **browser responsibility** — no smoothing, resampling, canonicalization or engineering calculation was added;
- **responsive behavior** — engineering-readable plot width is preserved inside horizontal overflow at narrow widths;
- **architecture** — Plotly is mechanically isolated behind one visualization adapter.

Plotly controls enhance investigation but are never the sole path to evidence.

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
