# Plan 021 — Traqmate Trackvision CSV Adapter Foundation

Status: **Completed**

Started: 2026-09-23

Completed: 2026-09-23

## Objective

Implement the smallest explicit source adapter required to ingest the licensed Traqmate Trackvision V2 physical-car fixture without turning OME CSV into a generic CSV parser.

## Delivered

- explicit `TraqmateTrackvisionCSVImporter`;
- signature-based `Format,Traqmate Trackvision,V2` detection;
- complete source-preamble preservation;
- original channel names/order/verified units;
- lexical source values;
- explicit `Elapsed Time` source timestamps;
- declared sample-rate preservation;
- source `Lap` preservation;
- SHA-256 provenance;
- source immutability;
- OME CSV / MoTeC CSV / Traqmate arbitration;
- arbitrary CSV rejection;
- no GPS-derived distance;
- no ingestion-time normalization/context inference.

## TDD evidence

Pre-behavior harness cleanup:

- CI #251 — test formatting only.

Behavioral RED:

- CI #252 — `TraqmateTrackvisionCSVImporter` absent.

Implementation feedback:

- CI #254 — production formatting only.

GREEN:

- CI #255 — complete canonical verify passed;
- CI #256 — complete verify passed after supported-path performance characterization;
- PR #51 head CI #260 — complete verify passed before merge.

No product test was removed or weakened to obtain GREEN.

## Performance characterization

Canonical runner baseline on the committed physical-car fixture:

```text
bytes=116688
rows=1962
import_ms=3.396
validation_ms=2.507
validation_issues=0
```

This is characterization, not an SLA.

No optimization is justified from this fixture.

## Boundaries preserved

Not added:

- generic CSV guessing;
- mph normalization;
- GPS-derived distance;
- automatic Session / Run / Lap organization;
- source-to-report Traqmate preparation;
- native Traqmate binary parsing;
- AI interpretation.

## Merge evidence

PR #51 was squash-merged as:

`8d8ed9c35b8606b4e35d2da2efad53364c6d561d`

## Completion assessment

All Plan 021 completion criteria are satisfied.
