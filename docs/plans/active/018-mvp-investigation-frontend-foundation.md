# Plan 018 — MVP Investigation Frontend Foundation

Status: **Active**

Started: 2026-09-23

## Objective

Build the first real user-facing OME investigation interface on top of the verified Plan 017 source-upload workflow.

The interface must let a user answer the MVP question:

> Where did Lap B gain or lose time relative to Lap A, and which measured evidence supports that observation?

without requiring the user to understand internal canonical DTOs or manually construct engineering evidence.

## Authoritative UX contract

- `docs/specs/mvp-investigation-ui-v0.1.md`
- `skills/ux-design/SKILL.md`
- `skills/ux-design/references/ome-interface-principles.md`

Architecture:

- ADR-0008 — local HTTP API with React/TypeScript UI;
- React + TypeScript + Vite;
- Plotly.js isolated behind UI visualization components.

Backend workflow:

- `POST /api/v1/ome-csv/comparison-reports`.

## User flow

```text
SELECT LAP A BUNDLE
+ SELECT LAP B BUNDLE
-> REVIEW FILE SELECTION
-> RUN COMPARISON
-> LOADING / PROCESSING
-> SUCCESS OR EXPLICIT NOT-READY
-> INSPECT DELTA + OBSERVATIONS
-> INSPECT SUPPORTING CHANNELS
-> OPEN EVIDENCE / PROVENANCE DETAIL
```

The first UI remains a controlled OME CSV workflow.

Do not add generic source discovery or project persistence.

## Screen architecture

One investigation workspace with stable regions:

1. application header;
2. source/comparison controls;
3. comparison context strip;
4. primary delta-time visualization;
5. deterministic observation regions;
6. synchronized supporting telemetry;
7. supporting-evidence status;
8. provenance/method details.

Avoid a decorative dashboard-card grid.

## Required interaction states

- empty/default;
- one lap selected;
- both laps selected / ready;
- loading;
- import not-ready;
- preparation not-ready;
- report not-ready;
- HTTP/transport failure;
- success;
- optional supporting evidence missing.

No missing/invalid state may be replaced by plausible placeholder data.

## Comparison trust requirements

Always make discoverable:

- Lap A and Lap B identity/context;
- Lap A as the comparison reference;
- delta convention: `B - A`;
- distance basis;
- common comparable interval;
- units;
- missing evidence;
- algorithm/method/version through progressive disclosure.

## Plot behavior

### Delta plot

Primary plot:

- x-axis: lap distance in metres;
- y-axis: delta time in seconds;
- zero reference line;
- sign convention clearly labelled;
- exact value inspection.

### Supporting telemetry

When available:

- speed;
- throttle;
- brake;
- steering;
- engine speed;
- gear.

Use the accepted comparison distance grid.

Keep units visible.

Discrete gear must not be visually implied to be linearly interpolated.

### Synchronization

Plots should share a distance inspection position/cursor when practical in the first implementation.

If full synchronized cursor behavior is too large for the first RED/GREEN increment, establish a component contract that keeps all plots on the same distance basis and defer only the cross-component interaction—not the evidence semantics.

## Progressive disclosure

Default:

- source selections;
- comparison summary;
- delta;
- gain/loss observations;
- key supporting telemetry;
- missing evidence warnings.

Expandable/detail:

- exact provenance;
- algorithm/version;
- transformation chain;
- source channel identifiers;
- context identifiers.

Do not expose every raw channel by default.

## Accessibility

Target WCAG 2.2 AA.

Minimum acceptance:

- keyboard-operable file selection/run controls;
- visible focus;
- explicit labels for all inputs;
- semantic status/error summaries;
- not-ready states not encoded by color alone;
- plots have accessible titles/labels and adjacent textual summary/evidence;
- sensible heading hierarchy;
- responsive zoom/reflow;
- no essential meaning dependent on hover alone.

## Responsive behavior

Desktop is the primary engineering-analysis environment.

At narrower widths:

- source controls stack;
- context and warning summaries remain visible;
- plots remain usable with vertical stacking;
- provenance moves below primary analysis;
- no critical control disappears behind hover-only affordances.

Do not claim a full mobile telemetry-analysis experience in this slice.

## Frontend architecture

Presentation only.

The frontend may:

- collect local files;
- build FormData;
- call the Plan 017 endpoint;
- render transport/application evidence.

It must not:

- parse OME CSV semantics;
- calculate delta time;
- infer lap context;
- normalize channels;
- classify gain/loss;
- reinterpret missing evidence.

## Frontend toolchain

ADR-0008 already accepts:

- React;
- TypeScript;
- Vite;
- Plotly.js.

Before product behavior, establish the smallest reproducible frontend test/build harness appropriate for React UI work.

Testing should support:

- component/state behavior;
- accessible roles/labels;
- mocked HTTP workflow;
- deterministic rendering of success/not-ready states.

Do not introduce a broad component library unless a concrete UX need justifies it.

## TDD rule

```text
UX CONTRACT
-> COMPONENT / USER-FLOW TEST
-> VALID RED
-> SMALLEST UI IMPLEMENTATION
-> GREEN
-> ACCESSIBILITY / VISUAL REVIEW
-> REFACTOR
-> FULL VERIFY
```

Build/tooling setup may precede the behavioral RED where needed to make React tests executable.

## First executable increments

### Increment A — source workflow shell

Tests first:

- Lap A CSV/sidecar controls are labelled;
- Lap B CSV/sidecar controls are labelled;
- compare action is disabled until all four files exist;
- submit builds the correct multipart field names;
- loading state is visible;
- transport failure is explicit.

### Increment B — not-ready states

Tests first:

- import stage is clearly identified;
- preparation stage is clearly identified;
- report stage is clearly identified;
- issue codes/messages are visible;
- no fake chart is rendered while not-ready.

### Increment C — successful comparison

Tests first:

- Lap A is visibly identified as reference;
- delta sign `B - A` is visible;
- distance/time units are visible;
- final delta summary is rendered;
- deterministic gain/loss/neutral observations are shown;
- missing optional evidence remains explicit.

### Increment D — telemetry visualization

Tests/component contracts first:

- delta plot consumes API values only;
- supporting plot components consume API overlay values only;
- units/legends are visible;
- no client-side engineering calculation occurs;
- provenance/details remain reachable.

## Completion criteria

- UX specification accepted and versioned;
- reproducible React/TypeScript/Vite/Plotly frontend harness;
- frontend behavior tests written before implementation increments;
- valid RED -> GREEN evidence recorded;
- controlled four-file workflow works against the accepted API contract;
- success/not-ready/loading/error states implemented;
- delta and supporting evidence rendered without client-side engineering inference;
- evidence/provenance progressively discoverable;
- accessibility baseline verified;
- responsive baseline verified;
- canonical repository verify GREEN.

## Explicitly out of scope

- generic telemetry source browser;
- MoTeC/iRacing browser upload;
- project persistence/library;
- authentication;
- public deployment;
- cloud collaboration;
- mobile-first analysis;
- AI explanations;
- setup recommendations;
- native desktop wrapper.
