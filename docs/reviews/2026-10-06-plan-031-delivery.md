# Engineering Council Delivery Review — Plan 031 Physical Traqmate Investigation Frontend Integration

Date: 2026-10-06

Plan:

`Plan 031 — Physical Traqmate Investigation Frontend Integration`

PR:

`#78 — feat: integrate physical Traqmate investigation frontend`

Decision: **READY**

## Objective

Verify that the frontend integrates the accepted physical Traqmate multipart workflow without duplicating engineering calculations, altering source-lap intent or weakening Missing Evidence/provenance presentation.

## Evidence reviewed

- Plan 031;
- Plan 030 accepted HTTP workflow;
- Plan 031 TDD tests;
- UX/accessibility review;
- behavioral RED: OME CI #410;
- implementation feedback: OME CI #411 / #412;
- GREEN: OME CI #414;
- changed files limited to frontend/docs/Kanban scope.

## Software / Architecture review

Assessment:

- `submitTraqmateComparison` sends exactly:
  - `telemetry_csv`;
  - `reference_lap`;
  - `candidate_lap`;
  - `grid_step_m`;
- the endpoint remains `POST /api/v1/traqmate/comparison-reports`;
- the existing OME CSV endpoint and form-data contract remain unchanged;
- one shared `ComparisonWorkflowResponse` and one shared result UI are used;
- the browser does not parse Traqmate data;
- the browser does not infer source laps;
- the browser does not derive distance;
- the browser does not convert MPH/RPM;
- the browser does not interpolate telemetry;
- the browser does not calculate delta time;
- the browser does not fabricate Missing Evidence;
- the browser does not rank laps;
- switching source workflows clears incompatible pending source inputs;
- recoverable network failure retains the selected physical source inputs;
- loading state prevents duplicate submission;
- extended backend workflow stages are represented explicitly rather than collapsed.

Decision:

READY.

## Motorsport Mechanical Engineering review

Engineering question:

Does Plan 031 change the accepted physical telemetry semantics or introduce unsupported driver/setup interpretation?

Assessment:

No.

The frontend preserves the accepted physical workflow:

- reference/candidate source laps remain caller-selected;
- no fastest/best-lap selection is introduced;
- physical speed, engine-speed and gear are displayed only when returned by the backend;
- throttle, brake and steering remain Missing Evidence when returned as such;
- no browser-side inference promotes calculated acceleration/deceleration into driver inputs;
- no understeer/oversteer, driver mistake, setup or causal diagnosis is generated.

No new motorsport mechanism was introduced, so no additional vehicle-dynamics reference lookup is required for this interface-only increment.

Decision:

READY.

## Physics review

Assessment:

No new numerical method is introduced.

The browser:

- passes `grid_step_m` unchanged as transport input;
- renders server-returned distance/delta/channel arrays;
- preserves the existing `Lap B - Lap A` sign presentation;
- does not perform interpolation;
- does not perform unit conversion;
- does not derive GPS distance;
- does not calculate lap time.

The backend remains authoritative for all engineering calculations/readiness.

Decision:

READY.

## UX / Accessibility review

Dedicated review:

`docs/reviews/2026-10-06-plan-031-ux-accessibility.md`

Decision:

READY.

Key evidence:

- accessible native source-workflow radios;
- semantic file/number controls;
- hidden incompatible inputs cannot be submitted;
- physical not-ready stage labels remain readable;
- existing report/Missing Evidence/provenance UI is reused;
- native controls preserve keyboard baseline.

## Cross-discipline discussion

Agreements:

- one investigation workspace is preferable to a source-specific result fork;
- explicit source-family choice is preferable to browser-side source detection;
- backend remains engineering authority;
- same-lap physical selection is intentionally allowed through transport so backend readiness remains authoritative;
- existing Missing Evidence and provenance presentation is sufficient for this increment.

Disagreements:

None.

## Decision

Selected:

**READY**

## Kanban transition

Before merge:

```text
DOING -> REVIEW
```

After merge, canonical main verification and documentation synchronization:

```text
REVIEW -> DONE
```

## Actions before merge

- [x] Plan 031 moved READY -> DOING;
- [x] tests committed before production behavior;
- [x] behavioral RED recorded;
- [x] exact Traqmate transport contract implemented;
- [x] caller lap order preserved;
- [x] OME CSV regression remains GREEN;
- [x] shared report/evidence/provenance UI reused;
- [x] browser engineering recomputation avoided;
- [x] UX/accessibility review complete;
- [x] canonical verify GREEN before delivery review;
- [x] specialist delivery review complete.

## Human gate

Not required for the implemented scope.

Reopen the CEO/maintainer gate if future frontend work introduces:

- automatic best/fastest lap selection;
- automatic source detection that changes user intent;
- inferred physical throttle/brake/steering;
- engineering diagnosis/recommendation;
- browser-owned numerical physics/telemetry calculations.
