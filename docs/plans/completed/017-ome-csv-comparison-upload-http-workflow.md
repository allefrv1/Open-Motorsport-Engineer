# Plan 017 — OME CSV Comparison Upload HTTP Workflow

Status: **Completed**

Started: 2026-09-23

Completed: 2026-09-23

## Objective

Expose the accepted Plan 016 source-to-report preparation workflow through a browser-usable local HTTP boundary without forcing callers to construct canonical evidence JSON.

## Delivered

- `POST /api/v1/ome-csv/comparison-reports`;
- multipart upload contract for:
  - `lap_a_csv`;
  - `lap_a_sidecar`;
  - `lap_b_csv`;
  - `lap_b_sidecar`;
- optional `grid_step_m`;
- transport-only temporary staging;
- basename/path sanitization for client filenames;
- streamed file copy into API-owned temporary directories;
- reuse of:
  - `OMECsvProfileImporter`;
  - `ComparisonPreparationService`;
  - `mvp_ome_csv_comparison_profile()`;
  - `ComparisonReportService`;
- explicit `import`, `preparation` and `report` not-ready stages;
- existing report DTO reuse;
- existing low-level `/api/v1/comparison-reports` compatibility;
- multipart/OpenAPI contract;
- `python-multipart==0.0.32` pinned in the locked Python environment.

## Transport contract

Authoritative specification:

- `docs/specs/ome-csv-comparison-upload-http-api-v0.1.md`.

The route remains intentionally source-specific.

It is not a generic CSV/MoTeC/iRacing upload API.

## TDD evidence

Pre-behavior cleanup:

- OME CI #182 — invalid test string syntax; not behavioral RED.

Behavioral RED:

- OME CI #185;
- source workflow route absent;
- multipart requests returned HTTP `404`;
- OpenAPI lacked `/api/v1/ome-csv/comparison-reports`.

Post-implementation harness feedback:

- OME CI #191 — malformed manual `uv.lock` package entry;
- OME CI #193 — Ruff formatter feedback only.

GREEN:

- OME CI #196 — complete canonical `verify` passed.

Final documentation/head verification:

- OME CI #199 — complete canonical `verify` passed.

No workflow behavior test was weakened to obtain GREEN.

## Implementation traceability

Focused tests:

- `tests/api/test_ome_csv_upload_workflow.py`;
- `tests/api/test_local_http_api.py`.

Production transport:

- `backend/src/ome/api/app.py`;
- `backend/src/ome/api/models.py`;
- `backend/src/ome/api/upload_workflow.py`.

Executable coverage proves:

- controlled uploads produce the deterministic report;
- final controlled delta remains +0.20 s;
- source-to-report provenance/context survives transport;
- missing lap distance remains preparation not-ready;
- invalid sidecar remains import not-ready;
- invalid/missing multipart transport returns 422;
- path components cannot escape temporary staging;
- temporary paths are not serialized;
- existing low-level report route remains compatible;
- OpenAPI exposes the source workflow.

## Architecture boundary

FastAPI, multipart, UploadFile and temporary filesystem concerns remain isolated in `ome.api`.

No deterministic core module depends on those transport concerns.

## Merge evidence

PR #41 was squash-merged as:

`0fc4a832db907409ad47cc672222dc86ff0affbf`

## Completion assessment

All Plan 017 completion criteria are satisfied.

## Explicitly out of scope

- MoTeC/iRacing upload workflow;
- generic telemetry upload API;
- persistence/project library;
- browser UI;
- Docker Compose;
- public deployment;
- AI.
