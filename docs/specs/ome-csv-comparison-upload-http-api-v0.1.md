# OME CSV Comparison Upload HTTP API v0.1

Status: **Accepted for Plan 017**

Date: 2026-09-23

## Purpose

Expose the accepted OME CSV source-to-report workflow through a browser-usable local HTTP boundary.

This specification is transport-only.

It does not redefine telemetry, normalization, context, comparison or report semantics.

## Endpoint

`POST /api/v1/ome-csv/comparison-reports`

Content type:

`multipart/form-data`

## Request fields

Required files:

- `lap_a_csv`;
- `lap_a_sidecar`;
- `lap_b_csv`;
- `lap_b_sidecar`.

Optional scalar:

- `grid_step_m`, default `1.0`.

`grid_step_m` uses the existing comparison contract and is not reinterpreted by transport.

## Source scope

This route accepts only OME CSV Exchange Profile v0.1 bundles.

It is not:

- a generic CSV route;
- a MoTeC route;
- an iRacing route;
- a project-library upload API.

## Staging rules

Uploaded bundles are staged only for the duration of the request.

For each lap:

1. derive a basename from the uploaded CSV filename using basename-only semantics;
2. reject/normalize empty or unusable names to a safe transport-local name;
3. never preserve directory components from client filenames;
4. create a temporary API-owned directory;
5. stage the CSV using the safe basename;
6. stage the sidecar as the exact sibling expected by OME CSV:
   `<csv-stem>.ome.json`;
7. call the existing `OMECsvProfileImporter`;
8. remove staging after the request completes.

No temporary path is part of the response contract.

## Application composition

For each request, transport reuses:

```text
OMECsvProfileImporter
-> ComparisonPreparationService
   + mvp_ome_csv_comparison_profile()
-> ComparisonReportService
```

The API must not:

- parse OME CSV semantics itself;
- normalize source values;
- construct Session / Run / Lap identifiers itself;
- calculate delta time;
- calculate overlays;
- classify observations.

## Success outcome

HTTP `200`:

```json
{
  "status": "success",
  "report": { ... }
}
```

The `report` object is the same accepted `ComparisonReportSuccessDto` used by the low-level report endpoint.

## Not-ready outcome

A syntactically valid multipart request may return HTTP `200` with:

```json
{
  "status": "not_ready",
  "stage": "import | preparation | report",
  "issues": [
    {
      "code": "...",
      "message": "...",
      "lap_side": "a | b | null",
      "canonical_concept": "... | null"
    }
  ]
}
```

### Import stage

Import failure issue code is the stable `ImportFailureCode` value.

`lap_side` identifies which source failed.

### Preparation stage

Preparation issue fields mirror `ComparisonPreparationIssue`.

### Report stage

Report issue fields mirror the existing report readiness issues.

## Transport validation

Missing multipart fields or an invalid scalar form value return HTTP `422`.

A syntactically valid source bundle that is unsupported/invalid is an engineering workflow outcome, not a transport-schema failure.

## OpenAPI

The route must appear in `/openapi.json` together with:

- `/healthz`;
- `/api/v1/comparison-reports`.

## Filename safety

Client filenames are untrusted labels.

The API must ensure:

- `../../evil.csv` cannot escape staging;
- Windows-style path components are not treated as directories;
- temporary paths are never returned in JSON.

Filename sanitization does not modify file content.

## Streaming

Upload staging should copy uploaded file streams in chunks rather than require reading complete telemetry files into one Python bytes object.

This is an implementation/resource-safety rule, not an interchange semantic.

## Framework boundary

The following remain API-layer-only:

- FastAPI `UploadFile`;
- multipart form parsing;
- temporary directories/files;
- HTTP response DTOs.

No deterministic core layer may depend on FastAPI, Pydantic or multipart.

## Compatibility

The existing:

`POST /api/v1/comparison-reports`

remains unchanged.

Plan 017 adds a simpler source-oriented route; it does not replace the low-level report transport contract.

## Related artifacts

- ADR-0008 — local HTTP API with React/TypeScript UI
- OME CSV Exchange Profile v0.1
- MVP Comparison Preparation Specification v0.1
- Local Comparison Report HTTP API v0.1
- Plan 017 — OME CSV Comparison Upload HTTP Workflow
