# Plan 034 — Evidence Status Visual Consistency

Status: **Active**

Kanban state: **DOING**

Started: 2026-10-09

## Intent
Make engineering evidence states readable and consistent in the existing lap comparison workspace using the project's reusable UI primitives.

## Scope
- Introduce a small presentational EvidenceStatus component.
- Preserve the existing backend-driven status classification, including `not_ready` with `missing_channel`.
- Expose exact textual labels; color is supplemental only.
- Add focused tests before implementation and keep backend and Plotly calculations unchanged.

## Acceptance
- Missing channel evidence displays **Missing evidence**, not generic not-ready.
- Other not-ready cases stay distinct.
- Available and incompatible evidence labels remain explicit.
- Canonical harness and Docker/Chromium CI pass before merging.
- Update Kanban and plan status on completion.

No new telemetry assumptions, third-party dependencies, backend changes or new domain behavior.
