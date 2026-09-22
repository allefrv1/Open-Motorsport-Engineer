# Plan 007 — iRacing .ibt Adapter Foundation

Status: **Active**

Started: 2026-09-22

## Objective

Implement the first external binary telemetry adapter for iRacing `.ibt` without allowing iRacing-specific structure to define OME's source-independent domain.

## Source strategy

This plan follows the accepted implementation sequence:

1. OME CSV Exchange Profile;
2. iRacing `.ibt`;
3. MoTeC CSV export;
4. later native/professional adapters where justified.

Supporting research:

- `docs/research/initial-source-feasibility.md`
- `docs/research/public-telemetry-datasets.md`
- `docs/references/source-registry.md`

## Critical fixture constraint

OME has inspected a public iRacing `.ibt` fixture from `teamjorge/ibt`, but redistribution rights for the simulator-generated binary have not been independently cleared.

Therefore Plan 007 must not copy that binary into the repository.

Before parser implementation, establish one reproducible test-fixture strategy:

- a project-owned synthetic/minimal `.ibt` fixture generated from publicly documented format semantics; or
- an explicitly redistributable iRacing fixture with documented permission.

External validation files may still be used manually when their terms permit access, but canonical CI must not depend on undeclared network downloads.

## TDD rule

Production parser behavior must not be implemented before focused tests.

Required cycle:

```text
FORMAT CONTRACT / REQUIREMENT
-> TEST + LEGAL PROJECT FIXTURE
-> RED FOR EXPECTED MISSING PARSER BEHAVIOR
-> MINIMUM PARSER IMPLEMENTATION
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

Do not create a meaningless synthetic fixture whose only purpose is to match an implementation invented at the same time.

The fixture must be justified by independently documented iRacing format semantics.

## Scope

The first adapter slice should prove:

- source detection for a supported `.ibt` file;
- safe header parsing;
- variable/channel inventory;
- preservation of original channel name, description, unit and declared type where supplied;
- telemetry sample extraction for a minimal representative subset;
- session/source metadata preservation where available;
- source provenance/fingerprint;
- explicit failure for unsupported/corrupt/truncated input;
- no canonical normalization during import.

## Required representative channels

When present in the fixture/validation file, tests should exercise at least several of:

- SessionTime;
- Speed;
- Throttle;
- Brake;
- SteeringWheelAngle;
- RPM;
- Gear;
- Lap;
- LapDist or LapDistPct.

The parser must preserve source semantics such as a source describing `Speed` as GPS vehicle speed.

## Architecture boundary

The iRacing adapter belongs in ingestion.

It may translate iRacing binary structures into the existing source-independent ImportedTelemetryDataset contract.

It must not:

- add iRacing concepts to the core domain merely because they exist in the file;
- normalize channel names or units;
- infer engineering meaning beyond source metadata;
- validate/repair signal quality;
- organize generic Session / Run / Lap boundaries unless trustworthy source context is explicitly represented and the accepted context contract supports it;
- perform analysis;
- use AI.

## Test strategy

Test-first coverage should include:

- positive minimal fixture import;
- channel metadata preservation;
- source value preservation;
- deterministic provenance/fingerprint;
- truncated/corrupt binary rejection;
- unsupported version/structure behavior when the public format contract defines such cases;
- parser boundary tests proving no normalization leaks into ingestion.

Where a behavior is not supported by verified format documentation, leave it unimplemented and explicit rather than guessing.

## Completion criteria

- legal/reproducible CI fixture strategy documented;
- tests committed before production parser implementation;
- RED evidence recorded;
- minimum `.ibt` adapter implemented;
- source evidence preserved;
- failure modes explicit;
- no source-specific leakage into core domain;
- canonical CI GREEN;
- external validation against a real/publicly accessible iRacing file performed when feasible without redistributing it.

## Explicitly out of scope

- live iRacing SDK connection;
- simulator control;
- setup recommendation;
- canonical normalization rules;
- lap comparison;
- UI;
- AI explanation;
- downloading third-party binaries during normal CI.
