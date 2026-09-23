# Plan 019 — Synchronized Telemetry Investigation Plots

Status: **Completed**

Started: 2026-09-23

Completed: 2026-09-23

## Objective

Add synchronized engineering telemetry plots to the Plan 018 investigation workspace without moving deterministic analysis into the browser.

## Delivered

- locked `plotly.js-dist-min` 4.1.1 dependency;
- pure presentation-only telemetry figure model;
- deterministic preferred panel ordering;
- server-array pass-through without smoothing/resampling/recalculation;
- isolated Plotly visualization adapter;
- vertically stacked synchronized distance panels;
- unified distance hover and responsive Plotly behavior;
- Lap A solid / Lap B dashed redundant identity;
- discrete gear step presentation;
- accessible exact-value semantic tables;
- integration into the existing successful investigation flow;
- responsive engineering-readable layout;
- mechanical guardrail restricting Plotly imports to one adapter.

## TDD evidence

Tooling baseline:

- CI #225 — canonical verify GREEN before product plot behavior.

Pure figure model:

- CI #226 — test/type noise, not counted as behavioral RED;
- CI #227 — valid RED: `telemetryFigureModel` absent;
- CI #228 — test fixture contract correction;
- CI #229 — GREEN.

Plotly adapter / exact values:

- CI #230 — valid RED: `TelemetryInvestigationPlots` absent;
- CI #231/#232 — TypeScript boundary feedback;
- CI #233 — GREEN.

Application integration:

- CI #234 — valid RED: successful workflow lacked `Synchronized telemetry`;
- CI #237 — GREEN after integration;
- CI #238 — GREEN after Plotly-isolation guardrail;
- CI #242 — final canonical verify GREEN.

No engineering behavior was moved into the browser and no product behavior test was weakened to obtain GREEN.

## UX / accessibility outcome

Verified:

- explicit Lap A reference / Lap B comparison identity;
- B-A semantics retained;
- units adjacent to plotted channels;
- one shared distance basis;
- exact values available without hover;
- missing channels remain explicit instead of synthesized;
- discrete gear is not linearly interpolated;
- responsive narrow-width overflow preserves engineering readability;
- supporting evidence and provenance remain authoritative;
- plots do not imply causal diagnosis.

## Merge evidence

PR #47 was squash-merged as:

`b031d174b3315857087d5c1166121f34f796cf90`

## Boundaries preserved

Not added:

- frontend telemetry calculation;
- smoothing/resampling;
- track map;
- corner segmentation;
- linked track cursor;
- persistence;
- AI interpretation.

## Completion assessment

All Plan 019 completion criteria are satisfied.
