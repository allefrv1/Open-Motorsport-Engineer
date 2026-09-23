# Plan 017 — OME CSV Comparison Upload HTTP Workflow

Status: **Active**

Started: 2026-09-23

## Objective

Expose the accepted Plan 016 source-to-report preparation workflow through a browser-usable local HTTP boundary without forcing callers to construct canonical evidence JSON.

The first transport path is deliberately source-specific:

> two OME CSV Exchange Profile bundles -> deterministic comparison report.

## Why this plan exists

The existing endpoint:

`POST /api/v1/comparison-reports`

accepts a low-level transport representation of `ComparisonReportRequest`.

That endpoint remains useful as an engineering/application contract, but it is not the right input for the MVP frontend.

A browser should provide source files and receive structured engineering evidence.

## Requirements

Primary:

- MVP — first vertical slice;
- REQ-001 through REQ-006 through their already accepted application behavior;
- ADR-0008 — local HTTP API with React/TypeScript UI;
- Plan 016 preparation contract;
- OME CSV Exchange Profile v0.1.

## Endpoint

Add:

`POST /api/v1/ome-csv/comparison-reports`

Content type:

`multipart/form-data`

Required file parts:

- `lap_a_csv`;
- `lap_a_sidecar`;
- `lap_b_csv`;
- `lap_b_sidecar`.

Optional form field:

- `grid_step_m`, default `1.0`.

The endpoint is **not** a generic CSV upload endpoint.

It accepts only the controlled OME CSV Exchange Profile path needed by the MVP.

## Browser workflow

A React UI can later use two local file selections:

```text
Lap A .csv + .ome.json
Lap B .csv + .ome.json
-> multipart POST
-> import
-> prepare
-> comparison report
```

The browser does not send local filesystem paths.

## Upload staging

The API adapter may stage each uploaded OME CSV bundle into a temporary local directory so the existing path-based importer can be reused.

Rules:

- use sanitized basename-only source names;
- never trust a client-supplied path component;
- create the expected sibling `.ome.json` name from the CSV basename;
- write/copy only into an API-owned temporary directory;
- clean up staging after the request;
- never return temporary paths in the response.

The imported source fingerprint remains derived from uploaded CSV + sidecar bytes.

The imported source name should preserve the uploaded CSV basename where practical.

Temporary staging location is transport implementation detail.

## Application composition

The route must reuse existing behavior:

1. `OMECsvProfileImporter`;
2. `ComparisonPreparationService`;
3. `mvp_ome_csv_comparison_profile()`;
4. `ComparisonReportService`.

Do not duplicate:

- validation;
- normalization;
- context organization;
- comparison;
- overlays;
- observations;
- report assembly.

## Response contract

### Success

HTTP `200`:

```json
{
  "status": "success",
  "report": { ...existing comparison report DTO... }
}
```

The report representation reuses the existing accepted report transport model.

### Not ready — import

A syntactically valid multipart request whose source bundle cannot be imported returns HTTP `200`:

```json
{
  "status": "not_ready",
  "stage": "import",
  "issues": [...]
}
```

Examples:

- invalid/missing OME sidecar semantics;
- unsupported OME profile;
- structurally invalid source bundle.

### Not ready — preparation

If import succeeds but Plan 016 preparation is not ready:

```json
{
  "status": "not_ready",
  "stage": "preparation",
  "issues": [...]
}
```

Examples:

- blocking validation;
- missing explicit context;
- missing lap distance;
- missing controlled time evidence.

### Not ready — report

If preparation succeeds but the accepted report service returns not-ready:

```json
{
  "status": "not_ready",
  "stage": "report",
  "issues": [...]
}
```

### Invalid transport

Missing multipart fields, invalid form scalar types or malformed HTTP input use FastAPI/Pydantic transport validation and return HTTP `422`.

Unexpected server failures remain HTTP `500` without stack trace/path leakage.

## Issue DTO

Workflow issues contain:

- stable string `code`;
- `message`;
- optional `lap_side`;
- optional `canonical_concept`.

Import failures use their stable import failure code and identify the affected lap side.

## Dependency

FastAPI multipart parsing requires the runtime multipart dependency.

Add it through the locked Python dependency workflow and restore strict `uv sync --locked`.

Do not add unrelated web/storage dependencies.

## TDD rule

```text
HTTP WORKFLOW SPEC
-> MULTIPART API TEST
-> VALID RED
-> SMALLEST ROUTE / DTO / STAGING IMPLEMENTATION
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

Production endpoint behavior must not be implemented before the focused transport tests establish RED.

## First executable test targets

Tests should prove:

- four controlled fixture uploads return the known deterministic success report;
- the response contains the expected +0.20 s final `delta_B_vs_A`;
- complete provenance/context survives source upload through response JSON;
- missing lap distance produces `status=not_ready`, `stage=preparation`;
- malformed OME sidecar produces `stage=import`;
- missing multipart part produces HTTP `422`;
- uploaded filenames cannot escape the temporary staging directory;
- existing `/api/v1/comparison-reports` behavior remains unchanged;
- OpenAPI contains the new source workflow route;
- no temporary filesystem path is serialized.

## Architecture boundary

FastAPI, multipart parsing and temporary staging remain inside `ome.api`.

The deterministic application/domain/analysis/evidence layers must remain unaware of:

- `UploadFile`;
- multipart;
- temporary directories;
- HTTP status codes.

Existing architecture checks must continue to enforce that separation.

## Resource/security scope

This is a loopback/local-first MVP endpoint.

Plan 017 does not add:

- authentication;
- public internet exposure;
- project storage;
- permanent uploads;
- cloud object storage;
- arbitrary archive extraction.

Explicit upload-size/product limits are deferred until representative user-file workflows provide a requirement; staging should stream/copy rather than require loading all telemetry into memory at once.

## Docker relationship

No Docker/Compose change is required.

ADR-0010 remains Proposed.

## Completion criteria

- workflow HTTP contract documented;
- dependency lock updated reproducibly;
- tests committed before production endpoint behavior;
- behavioral RED recorded;
- source upload -> import -> prepare -> report path GREEN;
- transport paths sanitized and temporary;
- no deterministic-core framework leakage;
- existing report endpoint remains compatible;
- OpenAPI updated;
- canonical verify GREEN.

## Explicitly out of scope

- MoTeC/iRacing upload workflow;
- generic telemetry upload API;
- project persistence/library;
- browser UI;
- Docker Compose;
- public deployment;
- AI.
