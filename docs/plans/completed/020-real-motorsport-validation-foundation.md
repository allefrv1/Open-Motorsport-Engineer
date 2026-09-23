# Plan 020 — Real Motorsport Validation Foundation

Status: **Completed**

Started: 2026-09-23

Completed: 2026-09-23

## Objective

Validate OME's completed controlled vertical slice against licensed physical-car telemetry and realistic external dataset scale before adding new engineering algorithms.

## Primary physical-car evidence

Fixture:

`fixtures/public/exit-speed/traqmate-parking-lot.csv`

Provenance:

- upstream: `djhedges/exit_speed`;
- Apache-2.0;
- upstream Git blob: `df9aaa9827b85d33c4df4d5dd11912955e2240cf`;
- Traqmate Trackvision V2;
- real vehicle.

## Executable characterization

Test module:

`tests/fixtures/test_traqmate_real_vehicle_characterization.py`

Canonical CI:

- CI #246 — GREEN initial characterization;
- CI #247 — GREEN after cadence/lap-transition characterization.

No production behavior was added to make the fixture appear supported.

## Observed source shape

Deterministically verified:

- 1,962 telemetry rows;
- elapsed span: 0.0 s -> 196.1 s;
- declared sample rate: 10 Hz;
- observed cadence: exactly 0.1 s between every sample;
- source channels:
  - `Elapsed Time`;
  - `Lat (Degrees)`;
  - `Lon (Degrees)`;
  - `Altitude (meters)`;
  - `Velocity (MPH)`;
  - `Lap`;
- source Lap identifiers:
  - Lap 1: 717 rows;
  - Lap 2: 766 rows;
  - Lap 3: 479 rows;
- explicit lap transitions:
  - 1 -> 2 at 71.7 s;
  - 2 -> 3 at 148.3 s;
- no explicit source distance channel.

## Current-system result

The current importers correctly refuse the source:

- OME CSV importer: does not claim the file because there is no OME sidecar;
- MoTeC CSV importer: does not claim the Traqmate signature;
- iRacing importer: does not claim CSV;
- `TelemetryImportService`: returns `UNSUPPORTED_SOURCE`.

This is correct behavior.

OME does not reinterpret Traqmate as a generic CSV source.

## Evidence sufficiency assessment

### Structurally trustworthy source evidence

The fixture contains explicit, stable evidence for:

- elapsed time;
- source sample cadence;
- latitude/longitude;
- altitude;
- vehicle velocity;
- source lap identifier.

### Missing comparison evidence

The fixture does not contain a trustworthy source `lap.distance` channel.

Therefore the accepted ADR-0009 lap-comparison path is not ready from this source as-is.

A correct not-ready result is the target behavior once the source becomes importable.

## Deterministic mapping candidates

The real source justifies later explicit normalization rules for:

- `Elapsed Time` -> `time.elapsed` in seconds;
- `Velocity (MPH)` -> `vehicle.speed` through a documented mph-to-m/s conversion.

The source `Lap` field is contextual evidence, not a reason to collapse context organization into ingestion.

Latitude/longitude/altitude remain source evidence in this phase.

## GPS decision

No GPS-derived lap distance was implemented.

Although coordinates are present, deriving a comparison reference requires a separate accepted design covering:

- coordinate/projection model;
- geodesic/path-distance algorithm;
- start/finish/reference semantics;
- noise/filtering policy;
- uncertainty and failure behavior;
- provenance and algorithm version;
- validation against known geometry.

That decision is deliberately deferred.

## External scale evidence

Apache-2.0 upstream benchmark candidates:

### Full Portland file

Path:

`exit_speed/testdata/2019-08-18_Portland_CORRADO_DJ_R03.csv`

Git blob:

`13fed5ffe15ad35dc668ea2b4df8acdc63ae7668`

Size:

20,282,259 bytes.

### Stripped Portland file

Path:

`exit_speed/testdata/2019-08-18_Portland_CORRADO_DJ_R03_stripped.csv`

Git blob:

`499762a9044ea0b09a698509e84681877baf7897`

Size:

15,439,942 bytes.

These remain external benchmark inputs to avoid repository bloat.

## Performance assessment

The committed 1,962-row fixture does not expose a meaningful scale problem by itself.

End-to-end import/validation performance cannot yet be measured honestly for Traqmate because no accepted Traqmate adapter exists.

Therefore TD-005 is not resolved.

The correct sequence is:

```text
explicit Traqmate adapter
-> supported-path characterization
-> benchmark committed fixture
-> benchmark external 15-20 MB fixtures
-> optimize only if measurements justify it
```

## Gap classification

Observed gaps:

1. **Source ingestion gap** — no explicit Traqmate Trackvision adapter.
2. **Real-source preparation gap** — no accepted Traqmate normalization/context profile yet.
3. **Comparison-reference gap** — no trustworthy source lap distance.
4. **Scale-measurement gap** — realistic files identified, but supported-path benchmark waits for source ingestion.

The first and smallest actionable gap is source ingestion.

## Decision

Open Plan 021:

**Traqmate Trackvision CSV Adapter Foundation**

The adapter is source-specific and evidence-preserving.

It does not implement:

- generic CSV guessing;
- GPS-derived distance;
- normalization;
- generic lap detection;
- engineering analysis.

## Completion assessment

Plan 020 successfully validated the most important engineering behavior:

> OME can confront real physical-car telemetry and refuse to fabricate unsupported meaning.

All Plan 020 completion criteria that are meaningful before source support are satisfied, and the remaining supported-path performance work is explicitly transferred to Plan 021/its follow-up benchmark.
