# Plan 031 — Physical Traqmate Investigation Frontend Integration

Status: **READY**

Started: 2026-10-06

## Objective

Integrate the already-proven Traqmate physical comparison HTTP workflow into the existing investigation frontend without duplicating engineering calculations or weakening evidence/provenance presentation.

## Replenishment decision

Engineering Council:

`docs/reviews/2026-10-06-post-plan-030-replenishment.md`

Decision:

`READY`

## Existing contracts

Backend endpoint:

`POST /api/v1/traqmate/comparison-reports`

Inputs:

- `telemetry_csv`;
- `reference_lap`;
- `candidate_lap`;
- `grid_step_m`.

Success response:

Existing `ComparisonReportSuccessResponse`.

Not-ready stages:

- `import`;
- `lap_window`;
- `track_reference`;
- `comparison_preparation`;
- `supporting_evidence`;
- `report`.

The existing frontend OME CSV workflow remains supported.

## User flow

```text
Choose source workflow
-> Controlled OME CSV | Physical Traqmate
-> enter source-specific inputs
-> compare
-> inspect deterministic report
-> inspect supporting/missing evidence
-> inspect provenance
```

### Controlled OME CSV

Keep the current four-file input contract:

- Lap A CSV;
- Lap A sidecar;
- Lap B CSV;
- Lap B sidecar.

### Physical Traqmate

Show only:

- one Traqmate CSV file;
- reference source-lap number;
- candidate source-lap number;
- shared grid step.

The user controls reference/candidate order.

No fastest/best-lap selection is added.

## UX contract

Use one investigation workspace and one result/evidence model.

The source workflow control must:

- have an accessible label;
- make the current source family explicit;
- keep reference/candidate semantics visible;
- reset or isolate incompatible pending inputs when switching workflows;
- avoid submitting hidden stale inputs.

For physical Traqmate:

- reference lap and candidate lap fields are required positive integers;
- same-lap selection may be submitted to the backend and shown as deterministic not-ready, or prevented client-side only if the backend contract remains authoritative; initial implementation should prefer backend authority rather than duplicating domain readiness;
- grid step remains a positive numeric transport input;
- Missing Evidence for throttle/brake/steering is shown exactly through the existing report evidence UI.

## Architecture constraints

Frontend responsibilities:

- interaction state;
- transport DTO/form-data construction;
- response-state rendering;
- presentation of server-returned report arrays.

Frontend must not:

- parse Traqmate telemetry;
- infer laps;
- calculate lap time;
- rank laps;
- calculate distance;
- interpolate channels;
- convert MPH/RPM;
- construct missing engineering evidence;
- change comparison sign semantics.

## TDD strategy

Write tests before product behavior.

Behavioral RED targets:

1. source-workflow selector exists;
2. default controlled OME CSV workflow remains unchanged;
3. selecting Physical Traqmate shows one CSV input plus reference/candidate lap fields;
4. OME-only sidecar fields are hidden in physical mode;
5. Traqmate submit sends exact Plan 030 multipart field names and endpoint;
6. caller reference/candidate order is preserved;
7. Traqmate not-ready stages render user-readable stage labels;
8. physical success reuses the existing comparison result UI;
9. physical Missing Evidence remains visible;
10. physical provenance remains discoverable;
11. loading prevents duplicate submission;
12. network errors preserve selected physical inputs;
13. switching workflows never submits stale hidden inputs;
14. keyboard/semantic labels remain usable.

## Verification

Focused:

- frontend tests;
- frontend TypeScript check;
- frontend production build;
- docs checks.

Completion:

- canonical `verify`.

## Completion criteria

- replenishment review merged;
- Plan 031 moved READY -> DOING;
- frontend tests committed before production behavior;
- behavioral RED recorded;
- source-workflow UX implemented;
- exact Traqmate transport contract implemented;
- existing OME CSV flow regresses GREEN;
- existing result/evidence/provenance UI reused;
- no browser-side engineering recomputation;
- accessibility/UX review complete;
- canonical verify GREEN;
- delivery review complete.

## Explicitly out of scope

- backend changes;
- automatic source detection;
- automatic lap ranking;
- lap-time browser calculation;
- new charts/engineering metrics;
- throttle/brake/steering inference;
- causal driver/setup diagnosis;
- persistence/history;
- desktop packaging;
- AI explanation.
