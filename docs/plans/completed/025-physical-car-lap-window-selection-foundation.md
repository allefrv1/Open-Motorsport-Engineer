# Plan 025 — Physical-Car Lap Window Selection Foundation

Status: **Completed**

Started: 2026-09-24

Completed: 2026-09-24

## Objective

Implement the smallest deterministic application-level selection of complete source lap windows from sparse Traqmate Trackvision Lap boundary markers.

## Delivered

- immutable `SourceLapWindow` artifact;
- explicit `SourceLapWindowRequest`;
- success/not-ready outcomes;
- typed readiness issue codes;
- deterministic `TraqmateLapWindowSelector`;
- exact Portland Lap 4 window:
  - start 0;
  - end exclusive 3618;
  - closing boundary 3618;
- exact Portland Lap 5 window:
  - start 3618;
  - end exclusive 7249;
  - closing boundary 7249;
- incomplete Lap 6 remains explicit not-ready evidence;
- missing/duplicate markers remain explicit;
- missing provenance/channel/inconsistent evidence remains explicit;
- source dataset and sparse Lap cells remain unchanged.

## Boundary semantics

A source marker `Lap=N` opens source Lap N.

The next non-empty Lap marker closes that source window but belongs to the next lap:

```text
telemetry samples = [start_index, next_marker_index)
closing boundary  = next_marker_index
```

The closing sample is not duplicated into selected telemetry.

Its index is preserved separately for later geometry preparation.

## TDD evidence

Tests were committed before production selector behavior.

Behavioral RED:

- OME CI #315;
- expected failure: `ModuleNotFoundError: No module named 'ome.application.lap_window'`.

Implementation feedback:

- OME CI #317 — Ruff formatting only;
- OME CI #318 — Ruff lint simplification only.

GREEN:

- OME CI #319 — minimum selector canonical verify passed;
- OME CI #320 — regression characterization for inconsistent evidence / invalid boundary time passed;
- OME CI #321 — final documented state canonical verify passed.

Tests were not weakened to obtain GREEN.

## Implementation traceability

Production:

`backend/src/ome/application/lap_window.py`

Tests:

`tests/application/test_physical_lap_window_selection.py`

Normative spec:

`docs/specs/traqmate-lap-window-v0.1.md`

## Boundaries preserved

Plan 025 did not:

- fill sparse Lap markers;
- auto-select fastest/best/first lap;
- derive GPS distance;
- project GPS;
- normalize vehicle channels;
- build a comparison/report;
- infer Session / Run automatically;
- use AI.

## Merge evidence

PR #61 was squash-merged as:

`7a26050d8872c9ff7fa4e800ffe250ca3d4f835c`

## Completion assessment

All Plan 025 completion criteria are satisfied.
