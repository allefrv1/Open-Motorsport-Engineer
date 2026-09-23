# Plan 018 — MVP Investigation Frontend Foundation

Status: **Completed**

Started: 2026-09-23

Completed: 2026-09-23

## Objective

Implement the first usable React/TypeScript investigation interface over the accepted OME CSV source-to-report HTTP workflow.

## Delivered

- locked React 19 / TypeScript 7 / Vite 8 frontend toolchain;
- Vitest + jsdom + React Testing Library;
- frontend tests, TypeScript check and production build inside canonical verify;
- controlled Lap A / Lap B OME CSV source selection;
- Plan 017 multipart API client;
- loading / transport-error / not-ready / success states;
- explicit Lap A reference and B-A sign convention;
- accessible server-series delta visualization;
- deterministic gain/loss observation rendering without causal claims;
- supporting-evidence inventory with explicit Missing Evidence;
- provenance/method progressive disclosure;
- responsive engineering-workspace styling;
- local Vite /api proxy to loopback FastAPI;
- accessibility baseline including announced loading/error/not-ready states.

## TDD evidence

### Harness baseline

- OME CI #204 — frontend executable harness, typecheck and build GREEN before product behavior.

### Product RED

OME CI #205 failed only because the first tests used unavailable jest-dom matchers and is not a behavioral RED.

After correcting the test harness without adding another assertion package:

- OME CI #206 — valid behavioral RED;
- missing `Compare laps`, source controls and result interface.

### Product GREEN / feedback

- OME CI #213 — Vite CSS declaration feedback;
- OME CI #214 — evidence identifiers needed individual inspection semantics;
- OME CI #215 — canonical verify GREEN;
- OME CI #217 — GREEN after local API proxy, grid guidance and UX refinements.

### Accessibility increment

- OME CI #218 — imprecise test selector; not behavioral RED;
- OME CI #219 — valid RED: not-ready state was not an announced status;
- OME CI #220 — GREEN after `role=status` / `aria-live=polite`;
- OME CI #221 — final canonical verify GREEN after TDD/UX documentation.

## UX review

Resolved blocking items:

- one continuous investigation flow;
- visible reference/sign/units;
- no causal diagnosis from observations;
- Missing Evidence explicit;
- semantic labels and landmarks;
- keyboard/focus baseline;
- loading/error/not-ready announcements;
- chart textual equivalent;
- responsive stacking;
- provenance and source identifiers discoverable.

## Merge evidence

PR #45 was squash-merged as:

`7708f058d6a9ec3aae6bc94982b64cd3093fb11e`

## Boundaries preserved

Not added:

- synchronized Plotly overlays;
- routing;
- project persistence;
- track map;
- desktop wrapper;
- AI.

## Completion assessment

All Plan 018 completion criteria are satisfied.
