# Plan 007 — iRacing .ibt Adapter Foundation

Status: **Completed**

Started: 2026-09-22

Completed: 2026-09-22

## Objective

Implement the first external binary telemetry adapter for iRacing `.ibt` without allowing iRacing-specific structure to define OME's source-independent domain.

## Delivered

- verified IRSDK v2 binary contract;
- project-owned deterministic `.ibt` fixture generator;
- source-specific `IRacingIBTImporter` behind the common ingestion boundary;
- safe fixed-header, disk-subheader and variable-header parsing;
- preservation of original channel name, description, unit, type, count and `countAsTime`;
- explicit `SessionTime` source timestamp basis;
- deterministic SHA-256 provenance;
- explicit corrupt/truncated/version/time failures;
- fixed source-array preservation without flattening;
- 360 Hz source acquisition metadata for six-way time subdivisions at 60 Hz;
- scalar normalization protected from grouped source arrays;
- source bytes unchanged by import.

## TDD evidence

### Initial importer

Pre-behavior harness cleanup:

- CI #43 — test formatting;
- CI #44 — import ordering.

Behavioral RED:

- CI #45 — `IRacingIBTImporter` did not exist.

GREEN:

- CI #47 — canonical verify passed after the minimum scalar importer.

### Real-file-driven array support

External inspection of the public `teamjorge/ibt` fixture revealed:

- IRSDK v2;
- 60 Hz base tick;
- 276 variables;
- 390 records;
- one `float[6]`, `countAsTime=true` channel:
  - `SteeringWheelTorque_ST`;
  - source description identifies 360 Hz steering-shaft torque.

Behavioral RED:

- CI #51 — scalar importer returned `INVALID_PROFILE` for the time-subdivision array.

GREEN:

- CI #54 — grouped array preservation passed canonical verify.

Final branch verification:

- CI #55 — source-integrity characterization passed;
- CI #56 — complete final verify passed after durable documentation/source-registry updates.

Tests were not weakened to make production behavior pass.

## External validation

The third-party iRacing binary was not committed to OME.

Structural validation against Git blob:

`bd1b0123067fec0fe6bdf68a95b562394d944874`

found:

- file size 471,844 bytes;
- 276/276 variable headers in bounds;
- 390 records in bounds;
- finite, strictly increasing `SessionTime`;
- exactly one fixed-array source variable;
- representative channels required by the first comparison path present and scalar.

## Boundaries preserved

Not added:

- live iRacing SDK connection;
- simulator control;
- source-channel normalization during import;
- resampling;
- generic lap inference;
- analysis;
- UI;
- AI.

## Merge evidence

PR #17 was squash-merged as:

`f88537f20ddf60a7052014e0f4b4be4754b794fa`

## Completion assessment

All Plan 007 completion criteria are satisfied.
