# Plan 032 — Interactive Engineering Telemetry Workspace

Status: **Active**

Kanban state: **DOING**

Started: 2026-10-09

## Authorization and requirement

The CEO selected UI/UX modernization as the next product increment after completed Plan 031.
The WIP slot was empty.

Problem: the initial source form and unbounded observation feed obscure the investigation.
Goal: a legible, accessible engineering workstation comparable in interaction quality to professional
telemetry products, without losing the OME evidence-first model.

## Governing artifacts

- ADR-0008 — FastAPI, React and replaceable Plotly frontend adapter.
- `docs/specs/mvp-investigation-frontend-v0.1.md`.
- `docs/specs/mvp-telemetry-overlays-frontend-v0.1.md`.
- `skills/ux-design/SKILL.md` and OME interface principles.

## UX flow and information architecture

1. Keep the selected source workflow and Lap A/reference, Lap B/candidate order visible.
2. Prepare inputs in a compact sidebar that stacks on narrow screens.
3. Present final B-A delta, exact common distance interval and lap identifiers.
4. Investigate synchronized Plotly charts sharing the server-returned distance axis.
5. Toggle individual measured channels. Delta stays visible.
6. Zoom/pan, use first/second-half viewports and reset to the full common interval.
7. Inspect exact samples with a keyboard-accessible cursor or Plotly click.
8. Review short observation preview; expand to all server-returned regions on demand.
9. Keep Missing Evidence and method/provenance explicit and discoverable.

## Non-negotiable invariants

No browser resampling, smoothing, interpolation, derived telemetry, repairs, lap ranking,
inferred driver inputs, physical conclusions or changed REST contracts. Preserve exact
source units and arrays, step-shaped discrete gear, Lap A solid / Lap B dashed, delta B-A
and explicit missing channels.

## Test-first acceptance

Tests were committed before implementation in commit `bb234d9`:

- selectable channels without modifying Plotly data arrays;
- keyboard navigation of exact samples from server-returned distance points;
- zoom focus and reset through the Plotly adapter;
- measured versus derived plot identities, without fake Missing Evidence.

Preserve existing UI and API regression tests for both controlled CSV and physical Traqmate.
Run canonical `uv run --locked python scripts/harness.py verify` before merge.

## Out of scope

Backend changes, new metrics/physics, map overlays, AI explanations, persistence or telemetry
synthesis. Visual browser screenshot QA requires a running browser and remains a documented
manual check if not available to the automation environment.

## Delivery

Progress: implementation and CI feedback underway. Do not mark DONE before a green
canonical verification, UX self-review and merge to main.
