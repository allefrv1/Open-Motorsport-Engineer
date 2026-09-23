# Plan 021 — Traqmate Trackvision CSV Adapter Foundation

Status: **Active**

Started: 2026-09-23

## Objective

Implement the smallest explicit source adapter required to ingest the licensed Traqmate Trackvision V2 physical-car fixture without turning OME CSV into a generic CSV parser.

## Evidence basis

Primary licensed fixture:

`fixtures/public/exit-speed/traqmate-parking-lot.csv`

Characterization:

`tests/fixtures/test_traqmate_real_vehicle_characterization.py`

Completed validation plan:

`docs/plans/completed/020-real-motorsport-validation-foundation.md`

## Source identity

The first adapter slice supports the verified source signature:

```text
Format,Traqmate Trackvision,V2
```

A `.csv` extension alone is never sufficient.

## Verified first-slice structure

Preamble:

```text
Format,Traqmate Trackvision,V2
Track,Test Parking Lot
Vehicle,CORRADO
Driver,DJ
Starting Date,2020/06/11
Starting Time,22:16:027
Sample Rate (samps/sec),10
Duration (secs),196
```

Channel row:

```text
Elapsed Time,Lat (Degrees),Lon (Degrees),Altitude (meters),Velocity (MPH),Lap
```

The adapter must be driven by verified source structure, not by matching this exact fixture value-for-value.

## TDD rule

Production adapter behavior follows:

```text
VERIFIED TRAQMATE CONTRACT
-> FOCUSED TEST
-> BEHAVIORAL RED
-> MINIMUM IMPORTER
-> GREEN
-> REAL FIXTURE CHARACTERIZATION
-> FULL VERIFY
```

The existing Plan 020 tests characterize current unsupported behavior. Those tests may be updated only when the accepted behavior intentionally changes.

## First-slice import behavior

A supported Traqmate Trackvision V2 source should produce an `ImportedTelemetryDataset` that preserves:

- complete source preamble evidence;
- original source channel names;
- source units when they are encoded in names or verified metadata;
- lexical source values;
- explicit elapsed-time values as source timestamps;
- declared sample rate when present;
- source `Lap` values;
- SHA-256 provenance;
- source bytes unchanged.

## Time basis

The verified source provides:

`Elapsed Time`

The first slice uses it as the explicit source timestamp series when:

- values are finite decimal seconds;
- every telemetry row contains a time value.

Do not derive timestamps from row number or declared sample rate.

Do not repair decreasing or duplicate time in ingestion.

Validation remains separate.

## Source values

Preserve source cells without engineering normalization.

Examples:

- latitude remains source latitude text/value evidence;
- longitude remains source longitude text/value evidence;
- `Velocity (MPH)` remains in mph source semantics;
- `Lap` remains a source channel/context marker candidate.

The adapter does not convert mph to m/s.

## Metadata

Preserve complete parsed preamble rows.

Selected unambiguous values may also be exposed in source metadata:

- format/version;
- track;
- vehicle;
- driver;
- starting date/time;
- sample rate;
- duration.

Raw preamble remains authoritative source evidence.

## Units

For the verified first slice, source channel units are available from channel names:

- `Elapsed Time` -> seconds;
- `Lat (Degrees)` -> degrees;
- `Lon (Degrees)` -> degrees;
- `Altitude (meters)` -> meters;
- `Velocity (MPH)` -> mph;
- `Lap` -> unitless/discrete.

If broader Traqmate exports use another unit-declaration mechanism, add it only from verified evidence.

## Adapter arbitration

Traqmate CSV must coexist with:

- OME CSV;
- MoTeC CSV.

Rules:

- OME CSV requires its sidecar contract;
- MoTeC CSV requires `Format,MoTeC CSV File`;
- Traqmate requires `Format,Traqmate Trackvision,V2`;
- arbitrary CSV remains unsupported.

Tests must prove registration order does not change which adapter owns a source.

## Context boundary

The source `Lap` channel is trustworthy source evidence.

The importer preserves it.

Canonical Session / Run / Lap organization remains outside ingestion.

A follow-up application/profile slice may translate explicit source lap markers into `LapContext` under the accepted context contract.

## Comparison boundary

The adapter must not create `lap.distance`.

After import, the source is still expected to be not ready for ADR-0009 comparison until an accepted positional-reference path exists.

GPS latitude/longitude is not silently converted into distance.

## Error behavior

Fail explicitly for:

- unsupported Traqmate version/signature;
- unreadable/non-UTF-8 input;
- missing supported telemetry header;
- row-width mismatch;
- empty/non-finite elapsed time;
- no telemetry rows.

Do not fail solely because:

- source Lap changes;
- speed is zero;
- sample rate is absent;
- GPS values repeat;
- comparison distance is unavailable.

## Performance measurement

After GREEN on the committed fixture, record supported-path timing for:

- import;
- validation.

Then document a local benchmark procedure for the external Portland files:

- full 20,282,259-byte blob `13fed5ffe15ad35dc668ea2b4df8acdc63ae7668`;
- stripped 15,439,942-byte blob `499762a9044ea0b09a698509e84681877baf7897`.

Do not add a flaky CI wall-clock threshold.

Use measurements to update TD-005.

## TDD execution evidence

Pre-behavior harness cleanup:

- OME CI #251 — test formatting only; not counted as behavioral RED.

Behavioral RED:

- OME CI #252;
- expected failure: `ImportError: cannot import name 'TraqmateTrackvisionCSVImporter' from 'ome.ingestion'`.

Implementation harness feedback:

- OME CI #254 — production-file formatting only.

GREEN:

- OME CI #255 — complete canonical verify passed after the minimum explicit Traqmate importer was implemented;
- OME CI #256 — complete canonical verify passed after non-binding supported-path performance characterization was added.

No product test was removed or weakened to obtain GREEN.

## Implementation traceability

Focused test module:

`tests/ingestion/test_traqmate_trackvision_csv_import.py`

Coverage proves:

- licensed physical-car Traqmate Trackvision V2 import;
- source signature/version identity;
- complete preamble preservation;
- original channel names/order/units;
- explicit `Elapsed Time` timestamps while source cells remain lexical;
- source `Lap` preservation;
- absence of synthesized `lap.distance`;
- source immutability;
- deterministic SHA-256 provenance;
- OME CSV / MoTeC CSV / Traqmate arbitration independent of registration order;
- arbitrary CSV rejection;
- unsupported-version rejection;
- missing sample rate remains explicit and unknown;
- decreasing time imports unchanged and is blocked later by validation;
- row-width and elapsed-time structural failures.

## Supported-path performance baseline

OME CI #256 recorded the committed physical-car fixture on the canonical runner:

```text
bytes=116688
rows=1962
import_ms=3.396
validation_ms=2.507
validation_issues=0
```

This is a characterization baseline, not a public SLA and not a CI threshold.

No optimization is justified from this fixture.

### External scale benchmark procedure

The two larger Apache-2.0 upstream blobs remain external:

- full: `13fed5ffe15ad35dc668ea2b4df8acdc63ae7668` — 20,282,259 bytes;
- stripped: `499762a9044ea0b09a698509e84681877baf7897` — 15,439,942 bytes.

When benchmarking:

1. obtain the exact upstream blob;
2. write it to a temporary `.csv` path without modifying contents;
3. run `TraqmateTrackvisionCSVImporter.import_source`;
4. run `TelemetryValidator.validate` on the imported dataset;
5. record file size, row count, import time, validation time and memory observations;
6. repeat enough times to distinguish warm-up/noise from stable behavior;
7. do not add a hard CI timing threshold unless a product performance requirement is accepted.

## Completion criteria

- tests committed before production adapter behavior;
- valid behavioral RED recorded;
- explicit Traqmate importer implemented;
- real fixture imports without loss of source evidence;
- source Lap preserved;
- no generic CSV claiming;
- no GPS-derived distance;
- import/validation boundaries preserved;
- OME/MoTeC/Traqmate arbitration proven;
- supported-path performance recorded;
- canonical verify GREEN.

## Explicitly out of scope

- GPS-derived lap distance;
- automatic lap detection;
- source-specific normalization profile;
- source-to-report UI flow for Traqmate;
- native Traqmate binary formats;
- full Traqmate ecosystem compatibility;
- AI interpretation.
