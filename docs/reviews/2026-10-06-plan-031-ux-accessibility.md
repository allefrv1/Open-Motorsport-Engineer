# UX / Accessibility Review — Plan 031 Physical Traqmate Investigation Frontend

Date: 2026-10-06

Plan:

`Plan 031 — Physical Traqmate Investigation Frontend Integration`

PR:

`#78 — feat: integrate physical Traqmate investigation frontend`

Decision: **READY**

## Objective

Verify that the physical Traqmate workflow can be selected, configured and investigated through the existing frontend without hiding source semantics, submitting stale inputs or weakening the existing accessibility baseline.

## Evidence reviewed

- Plan 031 UX contract;
- replenishment UX review from `docs/reviews/2026-10-06-post-plan-030-replenishment.md`;
- `frontend/src/App.tsx`;
- `frontend/src/api.ts`;
- `frontend/src/styles.css`;
- `frontend/tests/app.test.tsx`;
- behavioral RED: OME CI #410;
- final GREEN before review: OME CI #414.

## Interaction review

### Source workflow selection

Assessment:

- source choice is explicit and precedes source-specific inputs;
- accessible radio labels are:
  - `Controlled OME CSV`;
  - `Physical Traqmate`;
- controlled OME CSV remains the default workflow;
- switching workflow clears the incompatible pending source-input set;
- outcome/error state is cleared when source workflow changes;
- hidden stale OME source inputs cannot be submitted through the Traqmate path;
- hidden Traqmate source inputs cannot be submitted through the OME path.

Decision:

READY.

### Physical Traqmate input contract

Assessment:

The physical workflow exposes only:

- one Traqmate telemetry CSV;
- reference source lap;
- candidate source lap;
- shared grid step.

Reference and candidate semantics remain explicit.

The UI validates only transport-friendly positive integer syntax for source lap fields.

It does not prevent same-lap selection, preserving backend authority for deterministic readiness.

Decision:

READY.

### Existing controlled workflow regression

Assessment:

- all four existing controlled OME CSV source inputs remain present in the default mode;
- the existing multipart endpoint/field contract remains unchanged;
- existing comparison success/not-ready/network tests remain GREEN.

Decision:

READY.

## Accessibility review

### Semantic controls

- workflow choice uses native radio inputs;
- source groups use `fieldset` / `legend`;
- file controls use explicit `label for`;
- lap and grid inputs use semantic labels;
- submit uses a native button;
- loading/not-ready states use `role="status"` and `aria-live`;
- network failure uses `role="alert"`;
- source file names remain announced with polite live regions.

### Keyboard baseline

All newly added interactive controls are native HTML radio/input/button controls and therefore participate in normal keyboard focus/activation without custom keyboard handlers.

### Validation visibility

- invalid positive-integer source-lap values keep submission disabled;
- existing grid validation remains visible;
- same-lap engineering readiness is intentionally left to the backend rather than duplicated as a browser-domain rule.

### Progressive disclosure

The existing:

`Method and provenance`

details control remains shared by both source workflows.

Missing Evidence remains in the same supporting-evidence section instead of being hidden for physical telemetry.

Decision:

READY.

## Responsive / visual consistency

Assessment from the existing component/style structure:

- the Traqmate path reuses the existing `source-form`, `source-grid`, `source-group` and result components;
- no separate physical-results visual hierarchy was created;
- the result area therefore keeps the same evidence standard and reading order across source families;
- no new charting or engineering visualization behavior was introduced.

No visual redesign is required for Plan 031.

Decision:

READY.

## TDD evidence

Behavioral RED:

- OME CI #410;
- tests failed because the accessible source-workflow radio controls did not yet exist.

Implementation feedback:

- CI #411 exposed the widened workflow-stage TypeScript contract;
- CI #412 exposed sentence-case presentation for the new `track_reference` stage.

GREEN:

- OME CI #414 — canonical verification successful.

The acceptance tests were not weakened to obtain GREEN.

## Remaining UX risks

Low-risk follow-up opportunities, not blockers for Plan 031:

- richer inline explanation of physical source-lap numbers;
- optional file metadata/summary before comparison;
- browser-level visual regression testing if/when a stable screenshot harness is introduced.

None require changing engineering semantics or blocking this delivery.

## Decision

Selected:

**READY**
