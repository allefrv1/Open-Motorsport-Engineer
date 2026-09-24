# Plan 025 — Physical-Car Lap Window Selection Foundation

Status: **Active**

Started: 2026-09-24

## Objective

Implement the smallest deterministic application-level selection of complete source lap windows from sparse Traqmate Trackvision Lap boundary markers.

## Why this plan exists

Plan 024 provides a real Portland source with:

- two complete physical-car laps;
- sparse source Lap boundary markers;
- explicit elapsed time;
- preserved GPS and vehicle channels.

The next physical-car comparison workflow needs to know which samples belong to each complete lap before GPS/reference preparation can be orchestrated.

That responsibility must not be pushed back into ingestion.

## Normative contract

Follow:

- `docs/specs/traqmate-lap-window-v0.1.md`;
- REQ-001 source-preservation boundary;
- REQ-003 explicit-context principles.

## Key boundary rule

A source marker `Lap=N` opens Lap N.

The next non-empty Lap marker closes that source window but belongs to the next lap.

Therefore:

```text
telemetry samples = [start_index, next_marker_index)
closing boundary  = next_marker_index
```

Do not silently duplicate the closing sample into the selected telemetry window.

Preserve the closing index explicitly for later circuit-geometry closure.

## Scope

Add a source-independent-enough application artifact/service for explicit Traqmate source-lap selection.

Suggested concepts:

- `SourceLapWindow`;
- `SourceLapWindowRequest`;
- `SourceLapWindowSuccess`;
- `SourceLapWindowNotReady`;
- typed issue codes.

The implementation may know the verified Traqmate sparse-marker semantics but must not alter the imported dataset.

## Portland expected windows

### Lap 4

- start index 0;
- end exclusive 3618;
- closing boundary 3618;
- 3618 telemetry samples.

### Lap 5

- start index 3618;
- end exclusive 7249;
- closing boundary 7249;
- 3631 telemetry samples.

### Lap 6

Not ready because the committed fixture has no later marker.

## TDD rule

Use:

```text
accepted lap-window spec
-> focused application tests
-> behavioral RED
-> minimum selector implementation
-> focused GREEN
-> full verify
```

Characterization of already-imported Portland evidence may pass before production behavior exists.

Formatting/lint/environment failures are not behavioral RED.

## TDD targets

Before production implementation, tests must prove the expected API/behavior for:

1. Lap 4 exact window;
2. Lap 5 exact window;
3. Lap 6 incomplete -> not-ready;
4. absent Lap 99 -> not-ready;
5. duplicated requested marker -> ambiguous/not-ready;
6. explicit deterministic repeated selection;
7. imported dataset/source channel tuples remain unchanged;
8. sparse Lap cells remain sparse;
9. unsupported source type -> not-ready;
10. missing/invalid provenance or inconsistent source evidence -> not-ready.

## Architecture boundary

Lap-window selection belongs in application/preparation.

It must not:

- modify ingestion;
- fill sparse Lap cells;
- automatically choose a lap;
- create a comparison report;
- derive GPS path distance;
- project onto common reference;
- normalize vehicle channels;
- use AI.

## Layered execution packet

### Prompt Engineering

Objective:

> Select one explicitly requested complete physical-car source lap window from preserved sparse Trackvision boundary markers.

### Context Engineering

Required:

- this plan;
- Traqmate Lap Window Specification v0.1;
- committed Portland fixture;
- current Traqmate importer contract.

Context readiness: **ready**.

### Harness Engineering

Focused application tests first; completion requires canonical `verify`.

### Loop Engineering

```text
test expected windows
-> behavioral RED
-> minimum application selector
-> GREEN
-> regression/source-immutability verification
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

Human gate reopens if implementation would need to:

- infer missing boundary markers;
- redefine source Lap semantics;
- duplicate/mutate source telemetry;
- automatically select reference/best laps;
- combine this slice with comparison orchestration.

## Completion criteria

- Plan 024 archived;
- accepted lap-window v0.1 contract;
- tests before production behavior;
- behavioral RED recorded;
- deterministic selector GREEN;
- Portland Lap 4/5 exact windows proven;
- incomplete Lap 6 explicit;
- source dataset unchanged;
- canonical CI GREEN.

## Next plan boundary

After Plan 025, a separate physical-car comparison-preparation plan may explicitly compose:

```text
selected source windows
-> GPS evidence
-> reference-lap gps.path_distance
-> common track reference
-> canonical lap.distance
-> existing comparison/report stack
```

Reference-lap choice remains explicit input.

## Explicitly out of scope

- best/fastest lap selection;
- source Lap ranking;
- automatic Session / Run inference;
- GPS derivation;
- common-reference projection;
- report/API/frontend changes;
- AI interpretation.
