# Plan 028 — Physical-Car Comparison Request Foundation

Status: **Active**

Started: 2026-09-25

## Objective

Compose the ready Portland physical reference/candidate preparation into the existing `ComparisonReportRequest` contract using canonical common `lap.distance` and explicitly derived lap-relative `time.elapsed`.

## Normative contract

Follow:

- `docs/specs/physical-car-comparison-preparation-v0.1.md`;
- `docs/specs/physical-car-reference-preparation-v0.1.md`;
- `docs/specs/lap-comparison-v0.2.md`;
- `docs/specs/lap-comparison-report-v0.1.md`;
- ADR-0009;
- REQ-005;
- REQ-006.

## Why this plan exists

Plans 026–027 now prove that real Portland physical laps can share canonical common-reference `lap.distance` and reach plateau-aware base comparison readiness.

The remaining application gap is to produce the request expected by the already accepted report stack without inventing Traqmate channel semantics.

## First physical report scope

Required:

- prepared reference `lap.distance`;
- prepared candidate `lap.distance`;
- lap-relative `time.elapsed` from explicit source Elapsed Time;
- reference/candidate LapEvidenceContext;
- requested grid step.

Supporting channels are intentionally absent in v0.1.

The report layer must expose that absence as deterministic Missing Evidence.

## TDD targets

Before production behavior, tests should prove:

1. Portland Plan 026 preparation becomes a ready `ComparisonReportRequest`;
2. reference elapsed time begins at 0;
3. candidate elapsed time begins at 0;
4. elapsed lengths match their canonical distance lengths;
5. elapsed transformation provenance identifies source Elapsed Time and rebase start;
6. prepared distance objects/values are reused unchanged;
7. preparation is deterministic;
8. source/preparation artifacts remain unchanged;
9. invalid grid step is not-ready;
10. context/fingerprint mismatch is not-ready;
11. non-increasing physical timestamps are not-ready;
12. request declares no invented continuous/gear channels;
13. passing the request to `ComparisonReportService` produces success;
14. Portland report uses base comparison v0.2;
15. all six supporting concepts remain explicit not-ready Missing Evidence;
16. report contains observations but no cause/hypothesis/engineering interpretation.

## Source-semantic boundary

Do not map in this plan:

- `Accel (calc)` -> throttle;
- `Brake (calc)` -> driver brake;
- inferred steering;
- fuzzy RPM/Gear/speed mappings.

A later plan may add a verified physical supporting-channel profile.

## Layered execution packet

### Prompt Engineering

Objective:

> Turn explicit ready physical lap preparation into a deterministic report request without inventing optional evidence.

### Context Engineering

Required context:

- Plan 026 preparation output;
- lap-comparison v0.2;
- existing report request/service;
- physical comparison-preparation v0.1 spec;
- Portland fixture.

Context readiness: **ready**.

### Harness Engineering

Test-first application coverage; completion requires canonical verify.

### Loop Engineering

```text
accepted physical comparison-preparation spec
-> focused tests
-> behavioral RED
-> minimum application preparation
-> GREEN
-> Portland source-to-report regression
-> full verify
```

### Graph Engineering

```text
PROMPT READY          = yes
CONTEXT READY         = yes
MATERIAL DECISION GAP = no
BEHAVIOR CHANGE       = yes
TESTABLE CONTRACT     = yes
NEXT STATE            = tests -> RED
```

Human gate reopens if implementation would need to infer a source-channel meaning or reuse a next-lap boundary value as an optional vehicle-channel sample.

## Completion criteria

- Plan 027 archived;
- accepted physical comparison-preparation v0.1 spec;
- tests before production behavior;
- behavioral RED recorded;
- deterministic physical request preparation GREEN;
- Portland physical report GREEN;
- optional supporting Missing Evidence explicit;
- provenance/immutability proven;
- canonical CI GREEN.

## Next plan boundary

After Plan 028, a separate source-semantic plan may evaluate and add explicitly supported Traqmate physical channels such as speed and gear.

## Explicitly out of scope

- source upload/API changes;
- frontend changes;
- automatic reference selection;
- supporting-channel inference;
- setup/driver diagnosis;
- AI.
