# Plan 033 — Real Browser Telemetry QA

Status: **Active**

Kanban state: **DOING**

Started: 2026-10-09

## Authorization and replenishment

The CEO asked to continue improving the newly delivered professional telemetry UI. The prior
Plan 032 left manual visual/interactive browser verification as an explicit open QA gap.
The product WIP slot was empty after Plan 032.

This incremental plan fills that gap before proposing new analytics features.

## Objective

Make the actual Portland Traqmate workflow mechanically testable in a real Chromium browser
and capture reproducible screenshots for desktop and mobile UX inspection.

## Governing requirements

- AGENTS.md, docs/KANBAN.md, and docs/QUALITY_ATTRIBUTES.md.
- ADR-0008, accepted MVP investigation and synchronized telemetry specs.
- skills/ux-design/SKILL.md, OME interface principles and UX review checklist.
- Plan 032's documented manual-browser verification gap.

## User flow / acceptance

1. Open the local Vite app served by Docker Compose, with a truthful empty state.
2. Select physical Traqmate and upload the committed Portland fixture.
3. Keep caller-selected Lap A/reference = 4, Lap B/candidate = 5, grid = 5 m.
4. Receive the real FastAPI comparison report (no mock server or invented telemetry).
5. Discover delta B-A, synchronized panels, Missing Evidence and method/provenance.
6. Inspect a server-returned distance sample through Plotly click and the keyboard slider.
7. Hide/restore an available channel and zoom/reset the common interval.
8. Capture desktop and mobile screenshots, and check page-level horizontal overflow.
9. Fail on uncaught frontend JavaScript errors. Preserve screenshots on failure.

## Test-first execution

Add the browser test and CI invocation first. Confirm expected RED from the specific
missing/broken interaction, then implement the smallest focused frontend correction.
Keep the canonical harness as authoritative; browser QA is an additional container job gate.

## Non-goals

No new data source, physics/tyre model, lap ranking, synthetic channel, cloud service,
frontend interpolation or backend contract change. Images are QA evidence, not product assets.

## Verification gates

- `uv run --locked python scripts/harness.py verify` passes.
- Docker Compose API/web health and real Chromium browser test pass.
- Screenshot artifacts are available on PR CI runs for inspection.
- Review accessibility, responsive behavior, Missing Evidence and source provenance.
- Merge only after both CI jobs are GREEN and update Kanban/plan completion.
