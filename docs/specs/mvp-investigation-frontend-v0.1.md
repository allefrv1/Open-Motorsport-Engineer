# MVP Investigation Frontend Specification v0.1

Status: **Accepted for Plan 018**

Date: 2026-09-23

## Purpose

Define the first real OME browser interface for the accepted MVP source workflow.

The interface exists to help a user answer:

> Where did Lap B gain or lose time relative to Lap A, and what evidence supports that observation?

It must not present correlation as causal diagnosis.

## Primary user flow

```text
SELECT LAP A SOURCE
-> SELECT LAP B SOURCE
-> COMPARE
-> REVIEW READINESS / RESULT
-> INSPECT DELTA
-> INSPECT GAIN / LOSS OBSERVATIONS
-> INSPECT SUPPORTING EVIDENCE
-> OPEN PROVENANCE / METHOD
```

The first UI is intentionally a single investigation workspace.

It is not a dashboard home page.

## Route

Initial frontend route:

`/`

No client-side router is required for v0.1.

## Source selection

The source panel contains two clearly separated groups:

### Lap A — reference

Required:

- CSV file;
- matching `.ome.json` sidecar.

### Lap B — comparison

Required:

- CSV file;
- matching `.ome.json` sidecar.

The UI must make the comparison convention visible:

```text
delta = Lap B - Lap A
```

Positive final delta means Lap B is slower at that point.

The interface must not infer or alter source files.

## Grid step

Default:

`1.0 m`

For v0.1 the grid step is an advanced numeric control.

It is visible but visually secondary to source selection.

Client-side constraints:

- finite number;
- greater than zero.

Server readiness remains authoritative.

## Primary action

Button label:

`Compare laps`

Disabled until all four source files are selected and the grid step is locally valid.

During submission:

- disable the action;
- expose a textual loading state;
- prevent duplicate submissions.

## HTTP contract

Use:

`POST /api/v1/ome-csv/comparison-reports`

Request:

`multipart/form-data`

The frontend must not construct canonical engineering evidence itself.

## Result states

### Empty

Before comparison:

- explain the required source bundle;
- do not show fake charts or zero-valued metrics.

### Loading

Show:

- operation in progress;
- selected Lap A / Lap B filenames remain visible.

Use `aria-live` or equivalent accessible status semantics.

### Transport error

For network/unexpected HTTP failures:

- show a recoverable error;
- retain selected files;
- do not erase the previous successful result until a new successful/not-ready response is received.

### Not ready

For API `status=not_ready`:

Display:

- stage: import / preparation / report;
- issue message;
- affected lap side when supplied;
- canonical concept when supplied.

Do not collapse Missing Evidence into a generic "failed" message.

### Success

Render the accepted report without recomputing engineering values.

## Success information architecture

### 1. Persistent comparison header

Must show:

- Lap A filename;
- Lap B filename;
- Lap A = reference;
- sign convention `B - A`;
- common distance interval;
- grid step;
- algorithm id/version through expandable method detail.

### 2. Delta summary

Show:

- final `delta_B_vs_A` in seconds;
- clear textual interpretation:
  - positive -> B slower;
  - negative -> B faster;
  - zero -> equal within displayed precision.

Do not use color alone to convey faster/slower.

### 3. Delta over distance

Plan 018 requires a lightweight accessible delta visualization based only on the server-returned:

- `distance_grid_m`;
- `delta_b_vs_a_s`.

The frontend must not smooth or recalculate the series.

The visualization must include:

- distance unit `m`;
- delta unit `s`;
- zero reference;
- textual/accessible summary.

A native SVG implementation is acceptable for this slice.

Rich synchronized Plotly overlays are deferred to Plan 019.

### 4. Deterministic observation regions

Render server-returned regions as observations only.

For each region expose:

- kind: B gain / B loss / neutral;
- start/end distance;
- delta change.

Do not label a reason or cause.

### 5. Supporting evidence

Render the stable supporting-evidence inventory from the report.

For each concept expose:

- canonical concept;
- status;
- kind;
- unit when available;
- issue messages when missing/incompatible.

Measured/derived evidence and Missing Evidence must be distinguishable with text labels, not color alone.

### 6. Provenance / method details

Use progressive disclosure.

Collapsed by default.

When expanded, expose at minimum:

- comparison algorithm id/version;
- common start/end;
- grid-step parameter;
- Lap A / Lap B context identifiers;
- source channel identifiers for distance/time;
- dataset fingerprints in a compact copyable form.

Do not show temporary upload paths.

## Visual hierarchy

The page should prioritize:

1. source context;
2. comparison result;
3. gain/loss observations;
4. supporting evidence;
5. provenance.

Avoid a generic dashboard card grid.

Use a dense but structured engineering workspace.

## Accessibility

Target WCAG 2.2 AA.

Required in Plan 018:

- semantic `main`, headings and form labels;
- keyboard-accessible file inputs and details disclosure;
- visible focus treatment;
- button disabled state programmatically available;
- loading/error/not-ready states announced;
- status meaning not encoded by color alone;
- chart includes an accessible textual equivalent;
- readable at 200% zoom;
- no essential hover-only information.

## Responsive behavior

Primary target:

desktop engineering use.

At narrower widths:

- Lap A / Lap B source groups stack;
- summary regions remain readable;
- tables/evidence lists may horizontally scroll only when necessary;
- provenance may remain collapsible;
- the compare action remains visible after source selection.

No separate mobile-specific product experience is required.

## Frontend architecture

Accepted by ADR-0008:

- React;
- TypeScript;
- Vite.

Plan 018 adds the minimum product dependencies required for this UI and locks them with pnpm.

Do not add a state-management framework or component library unless executable evidence shows the local state is insufficient.

Use browser `fetch` for the single API workflow.

## Component responsibilities

Suggested initial boundaries:

- `App` — page composition/state orchestration;
- `ComparisonSourceForm` — files/grid-step/submit;
- `ComparisonStatus` — loading/error/not-ready;
- `ComparisonSummary` — context/final delta/method;
- `DeltaChart` — accessible server-series visualization;
- `ObservationList` — deterministic regions;
- `SupportingEvidenceList` — evidence inventory;
- `ProvenanceDetails` — progressive disclosure.

These are responsibilities, not mandatory file names.

## TDD acceptance behavior

Frontend tests must be written before product implementation and prove:

1. compare action disabled until four source files exist;
2. form submits the exact multipart field names expected by Plan 017;
3. loading state prevents duplicate submission;
4. success renders the known +0.20 s controlled result without client recomputation;
5. positive `B-A` is described as Lap B slower;
6. observation regions are rendered as observations without causal labels;
7. supporting Missing Evidence remains explicit;
8. provenance is discoverable through disclosure;
9. not-ready stage/issues are visible and retain selected files;
10. network failure exposes recoverable error;
11. core interactions are keyboard/semantic-label accessible;
12. existing Node harness test remains green.

## Out of scope

- synchronized Plotly telemetry overlays;
- track map;
- zoom-linked multiple plots;
- MoTeC/iRacing browser source upload;
- project persistence/library;
- authentication;
- desktop wrapper;
- AI explanation;
- setup recommendations.

## Related artifacts

- ADR-0008 — local HTTP API + React/TypeScript UI;
- Plan 017 — OME CSV upload HTTP workflow;
- OME CSV Comparison Upload HTTP API v0.1;
- MVP Comparison Preparation Specification v0.1;
- Comparison Report Transport v0.1;
- OME Interface Principles.
