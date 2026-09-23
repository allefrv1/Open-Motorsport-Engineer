# MVP Comparison Preparation Specification v0.1

Status: **Accepted for Plan 016**

Date: 2026-09-23

## Purpose

Define the smallest application-level contract that prepares two trustworthy imported laps for the existing deterministic `ComparisonReportService`.

The preparation workflow connects:

```text
ImportedTelemetryDataset
-> Validation
-> Explicit Normalization Profile
-> Explicit Session / Run / Lap Context
-> Canonical Comparison Evidence
-> ComparisonReportRequest
```

It does not parse files, detect laps, repair telemetry, infer channel meaning or calculate the final report itself.

## Input boundary

Plan 016 begins from two `ImportedTelemetryDataset` objects.

Import remains a separate source-adapter responsibility.

The application workflow owns:

- validation of each imported dataset;
- explicit normalization using an injected/versioned preparation profile;
- extraction of trustworthy context declared by that profile;
- construction of canonical evidence expected by the existing analysis/report stack.

A future HTTP/file-selection workflow may perform import before calling this service.

## Preparation profile

Channel meaning must never be inferred from names at runtime.

A `ComparisonPreparationProfile` declares:

- profile id/version;
- supported source type;
- explicit `NormalizationRule` set;
- source-time-axis contract;
- explicit source-metadata keys for Session / Run / Lap context.

The profile is an application configuration artifact.

It is not source telemetry and it is not a fuzzy mapping registry.

## Controlled MVP profile

Plan 016 introduces one project-owned controlled profile:

`ome.mvp-comparison.ome-csv/0.1.0`

Supported source:

`ome-csv-profile`

It is deliberately tied to the controlled MVP fixtures.

Declared source channel identifiers:

- `lap_distance_src` -> `lap.distance [m]`;
- `speed_src` -> `vehicle.speed [m/s]`;
- `throttle_src` -> `driver.throttle [1]`;
- `brake_src` -> `driver.brake [1]`;
- `steering_src` -> `driver.steering [rad]`;
- `rpm_src` -> `engine.speed [rad/s]`;
- `gear_src` -> `transmission.gear`.

Brake semantic identity:

`driver.brake.pedal_position_ratio`

Every mapping uses an explicit rule id/version and conversion id/version.

The profile must not be reused for unrelated CSVs that merely have similar names.

## Source time evidence

OME CSV v0.1 stores `time_s` as the shared source timestamp axis rather than a regular `SourceChannel`.

For the controlled MVP profile:

- source field: `time_s`;
- semantics: elapsed time from the controlled lap reference;
- source unit: seconds;
- canonical concept: `time.elapsed`;
- canonical unit: seconds.

Preparation must verify that all source channels in the dataset share the exact same timestamp series.

The canonical evidence uses:

- `source_channel_identifier = "time_s"`;
- `source_original_name = "time_s"`;

with an explicit transformation:

- id: `ome.preparation.ome-csv-time-axis`;
- version: `0.1.0`;
- parameters containing the preparation profile id/version and source-contract identity.

The evidence field retains the source-axis identifier even though `time_s` is not represented as an `ImportedTelemetryDataset.channels` entry.

Preparation must not pretend the time evidence came from an unrelated telemetry channel.

## Context contract

The controlled OME CSV fixtures declare source context in sidecar metadata:

```json
{
  "context": {
    "session": "...",
    "run": "...",
    "lap": "...",
    "lap_number": 1
  }
}
```

Plan 016 uses only these explicit markers.

Required:

- `session`;
- `lap`.

Optional:

- `run`;
- `lap_number`.

The workflow constructs `ContextEvidence` and delegates canonical identifier creation to the existing `ContextOrganizer`.

It does not infer:

- pit-out / pit-in;
- start/finish crossings;
- GPS lap boundaries;
- generic Run/Lap segmentation.

## Validation boundary

Each dataset is validated before normalization/preparation.

Any blocking validation issue makes that lap not ready for preparation.

Warnings remain evidence but do not automatically block the workflow.

Preparation never repairs validation defects.

## Required canonical evidence

A successful prepared lap requires exactly one usable mapping for:

- `lap.distance`.

It also requires the explicit controlled source time axis described above.

If distance is absent, ambiguous, blocked or cannot be represented as finite numeric metres, preparation returns not-ready.

No synthetic distance may be created.

## Optional supporting evidence

The workflow attempts to prepare:

- vehicle speed;
- throttle;
- brake;
- steering;
- engine speed;
- gear.

Missing optional concepts do not block base comparison preparation.

They remain absent in the generated request so the existing `ComparisonReportService` reports Missing Evidence deterministically.

If one lap has an optional concept and the other does not, the generated pair retains the available side and leaves the missing side explicit.

## Canonical-series provenance

For normalized channels, `CanonicalSeriesEvidence` retains:

- original dataset fingerprint;
- source channel identifier;
- original source name;
- canonical concept;
- target unit;
- optional semantic id;
- normalization conversion identity/version;
- normalization rule id/version in transformation parameters;
- preparation profile id/version.

The workflow does not erase the normalizer's source semantics.

## Comparison request

Preparation produces a `ComparisonReportRequest` containing:

- `LapComparisonRequest`;
- both `LapEvidenceContext` objects;
- canonical distance/time evidence;
- optional continuous channel pairs;
- optional gear pair;
- requested comparison grid step.

The preparation service does not duplicate comparison, observation or report algorithms.

The request is passed directly to the existing `ComparisonReportService`.

## Readiness outcome

Preparation returns one of:

- `ComparisonPreparationSuccess`;
- `ComparisonPreparationNotReady`.

Initial not-ready issue families:

- unsupported source type;
- blocking validation;
- missing/invalid explicit context;
- inconsistent shared source time axis;
- missing required lap distance;
- ambiguous required lap distance;
- invalid required canonical numeric values;
- invalid preparation profile.

A not-ready outcome must not contain a plausible-looking report request.

## Controlled fixtures

Plan 016 adds:

- `fixtures/ome/mvp-comparison-lap-a.csv`;
- `fixtures/ome/mvp-comparison-lap-a.ome.json`;
- `fixtures/ome/mvp-comparison-lap-b.csv`;
- `fixtures/ome/mvp-comparison-lap-b.ome.json`.

Both are project-owned synthetic single-lap datasets.

They contain explicit:

- `time_s`;
- lap distance in metres;
- speed;
- throttle;
- brake pedal-position ratio source percentage;
- steering;
- RPM;
- gear;
- Session / Run / Lap metadata.

The expected base comparison at the fixture samples is:

```text
distance_m   A_time_s   B_time_s   delta_B_vs_A_s
0            0.00       0.00       0.00
25           0.50       0.55       0.05
50           1.00       1.10       0.10
75           1.50       1.65       0.15
100          2.00       2.20       0.20
```

The values are synthetic and must never be described as measured motorsport data.

## Immutability

Preparation must not mutate:

- imported datasets;
- validation evidence;
- source metadata;
- normalized source evidence.

## Out of scope

- raw file selection/upload;
- generic source-profile discovery;
- fuzzy mapping;
- generic lap detection;
- persistence/project library;
- API endpoint for preparation;
- frontend;
- Docker/Compose;
- AI.

## Related artifacts

- MVP — first vertical slice
- REQ-001 through REQ-006
- ADR-0001 — separate ingestion from normalization
- ADR-0009 — distance-aligned lap comparison
- OME CSV Exchange Profile v0.1
- Lap Comparison Specification v0.1
- Lap Comparison Report v0.1
