# Plan 033 — Real Browser Telemetry QA

Status: **Completed**

Kanban state: **DONE**

Started: 2026-10-09

Completed: 2026-10-09

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

## Delivery evidence

- Browser CI initially exposed source-status confusion: unsupported Portland inputs
  were shown as raw `not_ready` instead of Missing Evidence.
- TDD RED `37895223046` confirmed that a backend `not_ready/missing_channel` response
  was not presented as missing and did not distinguish other not-ready reasons.
- The initial real-browser screenshot also revealed a split heading/eyebrow layout.
- The UI now maps missing-channel evidence clearly, preserves other not-ready reasons,
  and keeps the workspace title with its label.
- The final PR #83 workflow `37895892318` passed the canonical harness and
  the Docker Compose Chromium test.
- Full-page desktop and 390px mobile screenshots were reviewed. They are retained
  for 14 days as the `ome-ui-chromium-screenshots` GitHub Actions artifact.
- PR #83 merged into `main` as `7873d52f805d31677ee8a90c46db675935348497`.
- No backend/domain computations or transport contracts changed.

## Verification gates

- `uv run --locked python scripts/harness.py verify` passes.
- Docker Compose API/web health and real Chromium browser test pass.
- Screenshot artifacts are available on PR CI runs for inspection.
- Review accessibility, responsive behavior, Missing Evidence and source provenance.
- Merge only after both CI jobs are GREEN and update Kanban/plan completion.

## Completion assessment

All automated browser gates passed and the PR was merged to main.
This incremental UX/QA hardening is complete; future enhancements require new replenishment.
