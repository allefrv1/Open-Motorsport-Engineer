# Plan 006 — Session / Run / Lap Context Foundation

Status: **Active**

Started: 2026-09-22

## Objective

Implement the smallest source-independent operational-context model satisfying REQ-003 without inventing session, run or lap boundaries.

## Requirement

Primary:

- REQ-003 — Organize Session, Run and Lap Context

Supporting contracts:

- `docs/domain/session-run-lap.md`
- `docs/domain/telemetry-import-model.md`
- `docs/domain/provenance.md`
- `docs/specs/ome-csv-profile-v0.1.md`
- `docs/CORE_BELIEFS.md` — source data is evidence; unknown is valid

## Scope

Create explicit source-independent concepts for:

- Session;
- Run;
- Lap;
- boundary/source marker provenance;
- optional Run operational metadata.

The first slice organizes **known/trusted context only**.

It does not implement generic automatic lap or run detection.

## Boundary source

For the project-owned OME CSV fixture, the sidecar already provides controlled context:

```json
"context": {
  "session": "Harness fixture",
  "lap": 1
}
```

This controlled source metadata may be used to prove context preservation.

If evidence for a Run boundary is absent, OME must not invent one merely to complete a hierarchy.

A Session may therefore initially contain:

- known laps without a known run association; or
- a Run only when a trusted source/context marker supplies enough evidence.

The model must support incomplete context explicitly.

## Initial domain model

### SessionContext

Capable of carrying:

- OME identifier;
- source session identifier/label when supplied;
- dataset fingerprint;
- provenance/evidence reference;
- runs;
- directly associated laps when run association is unknown.

### RunContext

Capable of carrying:

- OME identifier;
- source run identifier/label when supplied;
- laps;
- optional operational metadata:
  - driver;
  - vehicle;
  - setup version;
  - tyre set;
  - fuel/energy state;
  - run plan;
  - driver feedback;
  - conditions.

No metadata field becomes a telemetry channel.

### LapContext

Capable of carrying:

- OME identifier;
- source lap identifier when supplied;
- lap number when known;
- optional time/boundary references;
- dataset fingerprint;
- provenance/evidence source.

## Organization behavior

Create context only from explicit trusted context evidence supplied to the organizer.

The organizer must:

- preserve source labels/markers;
- preserve dataset provenance link;
- keep absent boundaries absent;
- reject contradictory context declarations rather than choosing silently;
- produce deterministic identifiers from explicit input where practical.

## No invented hierarchy

REQ-003 shows the expected hierarchy when relationships are known:

```text
Session
  -> Run
      -> Lap
```

This must **not** be interpreted as permission to manufacture a Run just because a Lap exists.

Incomplete but truthful context is preferable to a complete fictional hierarchy.

## Stint

Do not add a Stint entity in this slice.

REQ-003 explicitly defers it and the domain model states it is not a strict synonym for Run.

## Architecture constraints

- operational context is a domain/application concern;
- it may depend on source-independent domain data;
- it must not parse vendor formats;
- it must not normalize channels;
- it must not perform engineering analysis;
- it must not infer boundaries from signal heuristics;
- it must not depend on AI.

## Test strategy

Map REQ-003 acceptance criteria to executable tests.

Tests must prove:

- AC-001 known Session -> Run -> Lap relationships are representable;
- AC-002 absent Run/Lap evidence remains absent rather than invented;
- AC-003 source-provided markers/labels and provenance are preserved;
- AC-004 Run operational metadata is representable outside telemetry channels;
- AC-005 no Stint synonym/entity is introduced.

Integration should use the OME fixture context where appropriate, but the source-independent organizer should be testable with directly constructed evidence.

## Completion criteria

- Session/Run/Lap domain concepts exist;
- incomplete context is explicitly representable;
- trusted marker/evidence contract exists;
- source context preservation is tested;
- no generic boundary inference exists;
- REQ-003 AC-001 through AC-005 have executable traceability;
- architecture harness remains green;
- canonical CI is green.

## Explicitly out of scope

- generic automatic lap detection;
- GPS start/finish detection;
- pit-out/pit-in inference;
- endurance Stint modeling;
- race/pit strategy;
- setup interpretation;
- timing/scoring system integration;
- UI session browser.
