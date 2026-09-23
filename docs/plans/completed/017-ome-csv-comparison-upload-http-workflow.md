# Plan 017 — OME CSV Comparison Upload HTTP Workflow

Status: **Completed**

Started: 2026-09-23

Completed: 2026-09-23

## Objective

Expose the accepted Plan 016 source-to-report preparation workflow through a browser-usable local HTTP boundary without forcing callers to construct canonical evidence JSON.

## Delivered

- `POST /api/v1/ome-csv/comparison-reports`;
- multipart source workflow for two OME CSV bundles;
- transport-local temporary staging;
- sanitized uploaded filenames;
- import -> preparation -> report composition through existing services;
- explicit import/preparation/report not-ready stages;
- HTTP 422 for malformed transport input;
- OpenAPI registration;
- existing low-level comparison-report endpoint preserved;
- pinned `python-multipart==0.0.32`.

## TDD evidence

Pre-behavior test cleanup:

- OME CI #182 — test syntax defect only.

Behavioral RED:

- OME CI #185;
- source workflow route absent;
- multipart request returned 404;
- OpenAPI did not expose the route.

Post-implementation harness feedback:

- OME CI #191 — invalid manual lock entry;
- OME CI #193 — Ruff formatter feedback.

GREEN:

- OME CI #196 — canonical verify passed.

Final merged branch verification:

- OME CI #199 — canonical verify passed.

No workflow behavior test was weakened to obtain GREEN.

## Merge evidence

PR #41 was merged on 2026-09-23.

Merge commit:

`0fc4a832db907409ad47cc672222dc86ff0affbf`

## Implementation traceability

Specification:

- `docs/specs/ome-csv-comparison-upload-http-api-v0.1.md`

Focused tests:

- `tests/api/test_ome_csv_upload_workflow.py`
- `tests/api/test_local_http_api.py`

Production transport:

- `backend/src/ome/api/app.py`
- `backend/src/ome/api/models.py`
- `backend/src/ome/api/upload_workflow.py`

## Completion assessment

All Plan 017 completion criteria are satisfied.

## Boundaries preserved

Not added:

- generic CSV upload;
- MoTeC/iRacing browser upload;
- persistence;
- cloud storage;
- public deployment;
- frontend;
- Docker Compose;
- AI.
