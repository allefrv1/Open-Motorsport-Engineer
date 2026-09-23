# Synchronized Telemetry Investigation Frontend Specification v0.1

Status: **Accepted for Plan 019**

Date: 2026-09-23

## Purpose

Deepen the existing MVP investigation workspace with synchronized telemetry plots using evidence already returned by the accepted comparison report.

The frontend must not recalculate, interpolate or repair engineering data.

## Source contract

Use only server-returned report fields:

- `comparison.distance_grid_m`;
- `comparison.delta_b_vs_a_s`;
- `continuous_overlays[]`;
- `gear_overlay`;
- `supporting_evidence[]`;
- provenance already carried by the report.

No frontend fallback may synthesize a missing overlay.

## Investigation figure

Render one Plotly figure with vertically stacked panels sharing one distance x-axis.

Panel order:

1. delta time;
2. available continuous overlays in this preferred concept order:
   - `vehicle.speed`;
   - `driver.throttle`;
   - `driver.brake`;
   - `driver.steering`;
   - `engine.speed`;
3. `transmission.gear` when available.

Concepts not returned by the report are not plotted.

Their Missing Evidence remains visible in the supporting-evidence section.

## Data rules

### Delta

Use exactly:

- x = `comparison.distance_grid_m`;
- y = `comparison.delta_b_vs_a_s`.

### Continuous overlays

For every returned continuous overlay:

- x = `distance_grid_m`;
- Lap A y = `lap_a_values`;
- Lap B y = `lap_b_values`;
- unit = server-returned `unit`.

Do not smooth or interpolate again.

### Gear

Use:

- x = `gear_overlay.distance_grid_m`;
- Lap A = `lap_a_gears`;
- Lap B = `lap_b_gears`.

Render as step-like lines, reflecting discrete state.

Do not linearly interpolate gear.

## Lap distinction

Critical meaning must not rely on color alone.

Use redundant styling:

- Lap A: solid line;
- Lap B: dashed line;
- explicit trace names.

Delta remains separately named as `B - A`.

## Synchronization

All panels share the same x-axis reference in metres.

Required interaction:

- common horizontal zoom/pan;
- unified distance hover/cursor where supported by Plotly;
- x-axis title visible on the bottom panel.

The frontend must not change the distance basis selected by the deterministic comparison engine.

## Exact values / accessibility

Hover is useful but cannot be the only access to precise values.

For each plotted channel provide a collapsed semantic data table containing:

- distance;
- Lap A value;
- Lap B value;
- unit.

For delta provide:

- distance;
- `B - A` value in seconds.

These tables use the exact server-returned arrays.

## Provenance and evidence

The existing supporting-evidence and provenance sections remain authoritative.

The plot is presentation, not new evidence.

Do not:

- infer a cause from curve shape;
- hide missing channels to make the figure look complete;
- label interpolation/smoothing that did not occur in the frontend;
- modify units.

## Plotly boundary

ADR-0008 accepts Plotly.js behind UI components.

Plan 019 uses `plotly.js-dist-min` isolated inside a visualization adapter/component.

Business/UI orchestration components must not call Plotly directly.

## Responsive behavior

Desktop remains primary.

At narrow width:

- the figure may horizontally preserve a minimum engineering-readable width;
- exact-value tables remain usable;
- no plot control may become the only route to evidence.

## TDD acceptance behavior

Tests are written before the Plotly product implementation and prove:

1. report continuous overlays are passed through without numerical modification;
2. delta is included using the existing B-A series;
3. gear uses discrete step presentation;
4. preferred concept ordering is deterministic;
5. missing overlays are not synthesized;
6. Lap A and Lap B use distinct line styles in addition to names;
7. all panels use the same distance reference;
8. exact-value accessible tables expose server values;
9. Plotly implementation is isolated behind a visualization component;
10. the existing Plan 018 source/error/not-ready workflow remains green.

## Tooling

Use the current Plotly.js distribution accepted by ADR-0008.

Exact package version is locked in `pnpm-lock.yaml`.

Do not add a second React Plotly wrapper unless direct integration proves insufficient.

## Out of scope

- track map;
- sector/corner segmentation;
- linked track cursor;
- source-side resampling;
- frontend smoothing;
- project persistence;
- AI interpretation.
