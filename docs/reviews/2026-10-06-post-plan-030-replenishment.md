# Engineering Council Replenishment Review — After Plan 030

Date: 2026-10-06

Decision: **READY**

Candidate:

`Plan 031 — Physical Traqmate Investigation Frontend Integration`

## Context

Plan 030 completed the browser-usable Traqmate physical comparison HTTP workflow.

The backend can now accept:

- one Traqmate Trackvision V2 CSV;
- explicit reference source-lap number;
- explicit candidate source-lap number;
- comparison grid step;

and return the existing comparison report DTO with:

- deterministic delta;
- observations;
- vehicle speed;
- engine speed;
- gear;
- explicit Missing Evidence for throttle, brake and steering;
- complete provenance.

The current frontend still exposes only the controlled OME CSV four-file workflow.

The Kanban backlog explicitly defers physical-workflow frontend integration until the backend source workflow is proven. That condition is now satisfied.

## Software / Architecture review

Question:

What is the smallest next increment that turns the proven physical backend into direct user value without changing engineering behavior?

Assessment:

Extend the existing investigation frontend so the user can choose between:

- controlled OME CSV comparison;
- physical Traqmate comparison.

The Traqmate path should call the existing:

`POST /api/v1/traqmate/comparison-reports`

with:

- one telemetry CSV;
- explicit reference lap number;
- explicit candidate lap number;
- `grid_step_m`.

The existing `ComparisonResults` rendering should be reused because both workflows return the accepted report DTO.

Do not fork the engineering-result UI by source type.

Required frontend responsibilities:

- source-workflow selection;
- source-specific form controls;
- transport request construction;
- loading/error/not-ready state presentation;
- stage labels covering the Traqmate workflow;
- reuse of existing report/evidence/provenance presentation.

No engineering calculation belongs in the browser.

Decision:

READY.

## Motorsport Mechanical Engineering review

Engineering question:

Does the frontend integration introduce a new motorsport interpretation or telemetry rule?

Assessment:

No.

The UI must preserve the already accepted physical workflow:

- user explicitly selects reference and candidate source laps;
- the UI must not rank or auto-select laps;
- throttle, brake and steering remain Missing Evidence;
- vehicle speed, engine speed and gear are displayed only when returned by the deterministic backend;
- no causal driver/setup language is introduced.

Book lookup:

Not required for this interface/transport-only increment.

No vehicle-dynamics rule, setup recommendation or new telemetry semantic is proposed.

Decision:

READY.

## Physics review

Equations / units / assumptions:

No new numerical method is introduced.

The UI must:

- pass through the selected grid step;
- render server-returned arrays;
- preserve B-A delta semantics;
- preserve units;
- avoid browser-side interpolation, normalization or conversion.

Decision:

READY.

## UX review

Primary job:

> Select a supported source workflow, provide the minimum required source/context inputs, run a deterministic comparison and investigate the same evidence model regardless of source family.

Interaction principles:

- source workflow choice must be explicit before source fields;
- do not show irrelevant OME-sidecar fields for Traqmate;
- Traqmate requires one CSV plus two explicit lap numbers;
- reference/candidate meaning must remain visible;
- comparison loading/error/not-ready/success states remain announced;
- the result area should not visually imply a different evidence standard for physical data;
- Missing Evidence remains visible;
- provenance remains progressively discoverable;
- responsive behavior must retain form clarity.

Accessibility target:

WCAG 2.2 AA baseline already adopted by the frontend.

Decision:

READY.

## Cross-discipline discussion

Agreements:

- this is the highest-value backlog item because the backend prerequisite is complete;
- reuse one result/evidence UI;
- no new backend/domain behavior;
- no automatic lap ranking;
- no inferred driver inputs;
- no frontend numerical recomputation;
- explicit workflow selection is preferable to auto-detecting uploaded CSV type.

Disagreements:

None.

## Decision

Selected:

**READY**

## Kanban transition

```text
Plan 030: DONE
Plan 031: BACKLOG -> READY
```

After the transition PR is merged:

```text
Plan 031: READY -> DOING
```

## Actions

- [x] Define source-workflow selection behavior.
- [x] Define Traqmate form inputs.
- [x] Reuse existing comparison report result UI.
- [x] Preserve existing Missing Evidence/provenance semantics.
- [ ] Write frontend tests before production behavior.
- [ ] Prove behavioral RED.
- [ ] Implement minimum frontend/API client integration.
- [ ] Run UX/accessibility review.
- [ ] Run canonical verify.
- [ ] Delivery review before DONE.

## Human gate

Required:

No.

CEO / Maintainer decision:

Existing accepted product direction is sufficient.

Reopen the human gate if scope expands into:

- automatic best/fastest lap selection;
- new engineering diagnosis;
- inferred throttle/brake/steering;
- automatic source-type guessing that changes user intent;
- a new backend engineering contract.
