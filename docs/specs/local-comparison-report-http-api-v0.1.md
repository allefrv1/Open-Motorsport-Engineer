# Local Comparison Report HTTP API v0.1

Status: **Accepted for Plan 015**

Date: 2026-09-23

## Purpose

Define the first local HTTP transport contract for the accepted OME comparison-report application artifact.

The HTTP layer is an adapter around existing deterministic application/domain behavior.

It does not redefine the engineering model.

## Base path

Versioned application routes use:

`/api/v1`

Health/lifecycle routes remain outside the versioned product API.

## Health endpoint

### `GET /healthz`

Response:

- HTTP `200`;
- JSON object:
  - `status = "ok"`;
  - `service = "ome-api"`;
  - `api_version = "v1"`.

The response contains no secrets, filesystem paths or user/project data.

## Comparison report endpoint

### `POST /api/v1/comparison-reports`

Accepts a transport representation of `ComparisonReportRequest`.

The request contains:

- base comparison:
  - Lap A and Lap B context;
  - canonical `lap.distance` series/evidence;
  - canonical `time.elapsed` series/evidence;
  - optional `grid_step_m`;
- zero or more continuous channel pairs:
  - canonical concept;
  - optional Lap A series;
  - optional Lap B series;
- optional gear pair.

## Context DTO

Each lap context contains:

- `dataset_fingerprint`;
- `session_identifier`;
- optional `run_identifier`;
- `lap_identifier`.

## Canonical series evidence DTO

Each canonical series evidence object contains:

- `dataset_fingerprint`;
- `source_channel_identifier`;
- `source_original_name`;
- `canonical_concept`;
- `unit`;
- optional `semantic_id`;
- ordered transformations:
  - `transformation_id`;
  - `transformation_version`;
  - parameter object.

Canonical concept values use their stable string identifiers such as:

- `lap.distance`;
- `time.elapsed`;
- `vehicle.speed`;
- `driver.throttle`;
- `driver.brake`;
- `driver.steering`;
- `engine.speed`;
- `transmission.gear`.

## Base comparison series DTO

Contains:

- numeric `values`;
- canonical series evidence.

## Continuous overlay series DTO

Contains:

- numeric `timestamps_s`;
- numeric `values`;
- canonical series evidence.

## Gear series DTO

Contains:

- numeric `timestamps_s`;
- canonical integer/compatible source values accepted by the existing application contract;
- canonical series evidence.

Transport validation must not broaden the application/domain contract.

## Successful HTTP outcome

A valid request whose application report is ready returns HTTP `200`:

```text
status = "success"
report = ...
```

The report serialization preserves:

- base comparison;
- deterministic observations;
- successful continuous overlays;
- optional successful gear overlay;
- six supporting-evidence summaries;
- complete typed report provenance.

Tuples may serialize as JSON arrays.

Enums serialize through their stable string values.

## Not-ready HTTP outcome

A syntactically valid request whose deterministic application outcome is not ready also returns HTTP `200`:

```text
status = "not_ready"
issues = [...]
base_comparison = optional not-ready detail
```

Rationale:

Not-ready is a normal engineering/application outcome such as missing or incompatible evidence.

It is not a server/protocol failure.

## Invalid transport request

Malformed or schema-invalid request JSON returns FastAPI/Pydantic's standard HTTP `422` validation response.

The API does not translate invalid JSON into an engineering Missing Evidence result.

## Unexpected server failure

Unexpected unhandled server failures return HTTP `500`.

Do not expose stack traces or sensitive local paths through the response body.

## Determinism

Equivalent valid HTTP request semantics must produce equivalent JSON response semantics.

JSON object-key ordering is not a contract.

Ordered arrays are a contract when the application artifact defines stable ordering.

## Provenance

No provenance field from the application artifact may be dropped merely to simplify transport.

Mappings used for deterministic parameters serialize as JSON objects.

The API must preserve:

- algorithm/assembler id;
- version;
- parameters;
- requested concepts;
- source channels;
- transformation identities;
- dataset/session/run/lap context;
- units.

## Presentation boundary

The API returns structured engineering evidence.

It does not return:

- rendered charts;
- localized prose;
- causal explanation;
- AI narrative;
- HTML.

## Security/network baseline

Plan 015 is a local application boundary.

Default development/runtime binding should not imply public internet exposure.

Authentication/public multi-user deployment is out of scope.

## Containerization relationship

`GET /healthz` is intentionally suitable for a future container healthcheck.

This specification does not require Docker.

Container packaging follows ADR-0010 if/when that proposal is accepted.

## Related artifacts

- ADR-0004 — local modular monolith
- ADR-0008 — local HTTP API + React UI
- ADR-0010 — proposed incremental containerization
- Plan 015 — Local Comparison Report HTTP API
- Lap Comparison Report Specification v0.1
