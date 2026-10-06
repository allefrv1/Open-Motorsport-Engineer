# Traqmate Physical Investigation Frontend Specification v0.1

Status: **Accepted for Plan 031**

Date: 2026-10-06

## Purpose

Extend the existing OME investigation workspace so a user can run the already-verified physical Traqmate comparison workflow from the browser without creating a second analysis experience or moving engineering logic into the frontend.

The interface must reuse the existing deterministic report presentation.

## User goal

A driver, coach or engineer with one Traqmate Trackvision CSV should be able to:

1. select the physical source workflow;
2. upload one Traqmate CSV;
3. enter an explicit reference source lap number;
4. enter an explicit candidate source lap number;
5. choose the comparison grid step;
6. request the comparison;
7. inspect the same delta, observations, synchronized telemetry, Missing Evidence and provenance already used by the controlled OME CSV workflow.

The browser must not rank laps or infer missing telemetry.

## Information architecture

Keep the existing single-page investigation workspace at:

`/`

Do not create a second dashboard/page for Traqmate.

Add one explicit source-workflow selector near the top of the source form.

Initial options:

- `OME CSV bundles`
- `Traqmate Trackvision`

Default:

`OME CSV bundles`

This preserves the existing workflow by default.

## Workflow switching

Changing source workflow:

- changes only the source-input controls;
- preserves the shared grid-step control;
- clears any displayed comparison outcome and transport error so results from one source workflow are never shown as if they belonged to another;
- must not silently submit or convert files;
- must not infer source type from file contents.

Source selections for the inactive workflow may remain in local component state, but inactive files/values must not be submitted.

The workflow selector must be disabled while a request is in flight.

## OME CSV workflow

Existing Plan 018/019 behavior remains unchanged:

- Lap A CSV;
- Lap A sidecar;
- Lap B CSV;
- Lap B sidecar;
- `POST /api/v1/ome-csv/comparison-reports`.

Existing frontend regression tests remain authoritative.

## Traqmate source workflow

Required controls:

### Telemetry CSV

One file:

`telemetry_csv`

Accepted UI hint:

`.csv,text/csv`

The browser does not parse the file to discover laps.

### Reference source lap

Form field:

`reference_lap`

Meaning:

caller-selected Traqmate source lap number used as Lap A/reference.

Use a labeled integer number input.

### Candidate source lap

Form field:

`candidate_lap`

Meaning:

caller-selected Traqmate source lap number used as Lap B/candidate.

Use a labeled integer number input.

### Grid step

Reuse the existing:

`grid_step_m`

control and validation.

## Local form readiness

For the Traqmate workflow, Compare laps is enabled only when:

- one CSV file is selected;
- reference lap parses as an integer;
- candidate lap parses as an integer;
- grid step is finite and greater than zero;
- no request is currently loading.

Do not add a client-side rule that chooses, ranks or swaps laps.

Do not require reference/candidate lap numbers to differ in the browser.

The server remains authoritative for same-lap and missing-lap engineering readiness.

## HTTP contract

Use:

`POST /api/v1/traqmate/comparison-reports`

Request:

`multipart/form-data`

Exact fields:

- `telemetry_csv`
- `reference_lap`
- `candidate_lap`
- `grid_step_m`

The frontend must not construct engineering evidence itself.

## Response contract

Successful response uses the existing:

`ComparisonReportSuccessResponse`

Therefore the existing result components remain authoritative for:

- final delta;
- B gain/loss/neutral observations;
- synchronized telemetry plots;
- speed;
- engine speed;
- gear;
- supporting Missing Evidence;
- provenance/method details.

No Traqmate-specific numerical presentation layer is added.

## Traqmate Missing Evidence

For the accepted Portland workflow:

Available supporting evidence includes:

- `vehicle.speed`
- `engine.speed`
- `transmission.gear`

Remain explicit not-ready / Missing Evidence:

- `driver.throttle`
- `driver.brake`
- `driver.steering`

The frontend must not hide these missing concepts to make the physical report look more complete.

## Not-ready states

The Traqmate workflow may return:

- `import`
- `lap_window`
- `track_reference`
- `comparison_preparation`
- `supporting_evidence`
- `report`

The UI must render the stage and issue messages truthfully.

Human-readable stage labels should be used:

- Import
- Lap window
- Track reference
- Comparison preparation
- Supporting evidence
- Report

Do not collapse all engineering readiness failures into a generic error.

HTTP/transport failures remain the recoverable network/transport error state.

## Persistent source context

During loading, not-ready and success states, keep visible:

- selected source workflow;
- Traqmate filename;
- reference source lap number;
- candidate source lap number;
- grid step.

The comparison convention remains visible:

`Lap A = reference`

`Delta = Lap B - Lap A`

The UI must not describe the candidate as "best", "fastest" or "target" unless a later requirement defines that meaning.

## Result reuse

Reuse existing components when semantically correct:

- comparison summary;
- delta chart;
- synchronized telemetry figure;
- observation list;
- supporting evidence list;
- provenance disclosure.

Do not duplicate these components for Traqmate.

If a shared component needs broader workflow-stage typing or source-context props, extend it rather than fork it.

## Loading / error behavior

During submission:

- disable Compare laps;
- disable source-workflow switching;
- expose a textual loading state;
- prevent duplicate requests;
- retain selected source controls.

On network/unexpected HTTP failure:

- retain selected source controls;
- show a recoverable error;
- keep the previous successful result until a new successful/not-ready response replaces it, unless the user switches source workflow.

## Accessibility

Target WCAG 2.2 AA.

Required:

- source workflow selector grouped/labelled semantically;
- file and lap-number controls have programmatic labels;
- keyboard-operable flow;
- visible focus inherited/preserved;
- loading/not-ready/error states announced;
- missing evidence communicated in text;
- reference/candidate meaning not encoded by color;
- result plots keep exact-value accessible fallbacks;
- interface remains usable at 200% zoom.

## Responsive behavior

Desktop engineering use remains primary.

At narrow widths:

- source controls may stack;
- source workflow and explicit lap identity remain visible;
- Compare laps remains reachable;
- synchronized plots follow the existing engineering-readable minimum-width strategy.

No separate mobile product experience is introduced.

## TDD acceptance behavior

Frontend tests must be written before Plan 031 product implementation and prove:

1. OME CSV remains the default workflow and existing controls remain unchanged;
2. selecting Traqmate replaces OME bundle inputs with one CSV + explicit reference/candidate lap inputs;
3. Traqmate Compare laps stays disabled until its required local inputs are valid;
4. submission uses exactly `/api/v1/traqmate/comparison-reports`;
5. submitted multipart fields exactly match Plan 030;
6. no browser-side lap ranking/automatic lap selection occurs;
7. successful Traqmate response reuses the existing deterministic comparison/result presentation;
8. physical speed, engine-speed and gear are rendered from the server response;
9. physical throttle/brake/steering Missing Evidence remains explicit;
10. `lap_window`, `track_reference`, `comparison_preparation`, `supporting_evidence` and `report` stages render readable not-ready states;
11. selected filename/reference/candidate values remain visible during loading/not-ready/success;
12. switching source workflow clears stale result/error context;
13. loading prevents duplicate submission and workflow switching;
14. network failure is recoverable without clearing selected physical inputs;
15. core controls are accessible by semantic labels/keyboard;
16. existing OME CSV frontend and synchronized-plot tests remain green.

## UX guardrails

Must fix if violated:

- stale result shown under the wrong source workflow;
- hidden Missing Evidence;
- automatic lap ranking or swapping;
- browser-side engineering recomputation;
- inaccessible source/lap controls;
- ambiguous reference/candidate meaning.

Should improve when practical:

- concise helper text explaining explicit source-lap selection;
- clear human-readable workflow stage labels;
- stable source context while inspecting plots.

Polish is secondary to engineering trust and task completion.

## Out of scope

- client-side CSV parsing/lap discovery;
- fastest/best-lap selection;
- track map;
- physical source metadata browser;
- source library/persistence;
- multiple uploaded sessions;
- automatic driver/setup diagnosis;
- AI explanation;
- new telemetry mappings;
- new physics.

## Related artifacts

- Plan 030 — Traqmate Physical Comparison HTTP Workflow
- MVP Investigation Frontend Specification v0.1
- Synchronized Telemetry Investigation Frontend Specification v0.1
- OME Interface Principles
- ADR-0008 — local HTTP API + React/TypeScript UI
