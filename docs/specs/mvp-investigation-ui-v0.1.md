# MVP Investigation UI v0.1

Status: **Accepted for Plan 018**

Date: 2026-09-23

## Product job

Help a driver, coach, student or engineer move from two explicit telemetry sources to a verifiable answer about where Lap B gained or lost time relative to Lap A.

The interface optimizes for engineering trust and investigation flow, not dashboard decoration.

## Primary task

```text
Choose Lap A
Choose Lap B
-> Compare
-> Find time gain/loss
-> Inspect supporting telemetry
-> Inspect evidence/method
```

## Reference semantics

Lap A is the reference lap.

Delta is always:

```text
delta_B_vs_A = time_B - time_A
```

Meaning:

- positive delta: B has accumulated more elapsed time than A;
- negative delta: B has accumulated less elapsed time than A.

The UI must present this convention near the comparison summary and make it available near the delta visualization.

## Information architecture

### 1. Application header

Contains:

- OME product name;
- current workspace label: Lap Comparison;
- concise local/offline status when meaningful.

Avoid global navigation that implies unavailable product areas.

### 2. Source controls

Two clearly paired source groups:

#### Lap A — Reference

- CSV file;
- OME sidecar file.

#### Lap B — Comparison

- CSV file;
- OME sidecar file.

Each group shows:

- selected filenames;
- replace/clear affordance;
- file requirement/help text.

Primary action:

- Compare laps.

The action is disabled until all required files are selected.

### 3. Comparison context strip

After success, keep visible:

- Lap A label/context;
- Lap B label/context;
- reference marker on A;
- `B - A` sign convention;
- comparable distance interval;
- grid/reference basis.

Exact internal identifiers may move to provenance detail rather than dominating the header.

### 4. Primary analysis region

#### Delta-time plot

Primary visual evidence:

- x: distance [m];
- y: delta time [s];
- zero reference;
- exact value inspection;
- clear A/B reference semantics.

#### Observation summary

Render deterministic observation regions:

- B gain;
- B loss;
- neutral.

These are observations, not causal explanations.

Do not use wording such as:

- "B braked too late";
- "understeer caused the loss";
- "driver error";

unless a later evidence-backed interpretation layer explicitly supplies it.

### 5. Supporting telemetry region

Order:

1. vehicle speed;
2. throttle;
3. brake;
4. steering;
5. engine speed;
6. gear.

Missing/incompatible concepts remain in the inventory with an explicit unavailable/not-ready state.

Do not remove a missing concept in a way that makes the report appear complete.

### 6. Evidence/provenance detail

Progressive disclosure panel shows:

- algorithm id/version;
- comparison parameters;
- source dataset fingerprints;
- Session / Run / Lap identifiers;
- canonical concept;
- source channel identifier/name;
- units;
- transformation chain;
- semantic identity when relevant.

## State model

### Empty

Show:

- purpose;
- two source groups;
- disabled compare action.

Do not show empty charts as if data exists.

### Partially selected

Show selected filenames and clear remaining requirements.

### Ready to compare

Enable primary action.

### Loading

Show a clear processing state:

> Processing telemetry and preparing comparison…

Do not display fake percentage progress.

Disable duplicate submission while request is in flight.

### Import not ready

Label stage:

> Source import needs attention

Show issue message/code and affected lap side.

### Preparation not ready

Label stage:

> Comparison evidence is incomplete

Examples:

- missing lap distance;
- blocking validation;
- missing trusted context.

### Report not ready

Label stage:

> Comparison could not be completed

Keep structured issue evidence visible.

### Transport failure

Separate from engineering not-ready:

> Could not reach the local OME service.

Offer retry.

Do not present HTTP/network failures as telemetry-quality problems.

### Success

Show comparison context + analysis.

## Evidence hierarchy

Visual labels must preserve:

1. Measured Data
2. Derived Metric
3. Observation
4. Hypothesis
5. Engineering Interpretation
6. Possible Action
7. Missing Evidence

Plan 018 renders measured/derived/observation/missing-evidence content only.

No hypothesis or interpretation is fabricated by the frontend.

## Plot requirements

### Delta

- Plotly adapter isolated behind a component.
- data sourced directly from report DTO;
- no smoothing;
- no client-side recomputation;
- distance and time units visible;
- zero line not encoded by color alone.

### Continuous channels

Use exact API overlay values.

Lap A and Lap B remain visually distinguishable through legend/text, not color alone.

### Gear

Render as discrete/step-like evidence.

Do not imply linear gear values between samples.

## Exact values

Precision matters.

At minimum, provide exact/near-exact inspection through:

- Plotly hover/focus behavior;
- textual summary for final delta;
- provenance/detail panel.

Essential conclusions must not require hover.

## Missing evidence

The supporting-evidence inventory is stable.

For unavailable channels show:

- concept name;
- Missing Evidence / Not Ready label;
- issue message/code where useful.

Do not insert zeros or flat synthetic curves.

## Accessibility

### Forms

- native file inputs or fully accessible equivalents;
- explicit visible labels;
- keyboard-operable clear/replace/compare actions;
- error summary associated with controls where applicable.

### Status

Use semantic live/status region for:

- loading;
- success;
- not-ready;
- transport error.

Do not rely on color alone.

### Plots

- accessible title/description;
- nearby textual interpretation limited to deterministic facts;
- keyboard-reachable provenance/detail controls.

### Focus

After submit:

- not-ready/error: focus or announce issue summary;
- success: announce comparison ready without unexpectedly moving focus away from user control.

## Responsive behavior

### Wide desktop

Two source groups may sit side by side.

Analysis plots use full working width.

Evidence/provenance may use a secondary panel or expandable section.

### Narrow desktop/tablet

Source groups stack.

Plots stack vertically.

Context strip wraps while keeping A/B/reference visible.

### Small screens

Allow source selection and summary/error review.

Do not optimize advanced synchronized plot investigation for small screens in v0.1.

## Visual hierarchy

Use:

- typography;
- alignment;
- spacing;
- restrained separators;
- data/axis hierarchy.

Avoid:

- one card per metric;
- large decorative hero sections inside the analysis workspace;
- gradients/animation that distract from evidence;
- status-only color coding.

## API contract

Frontend submits:

`POST /api/v1/ome-csv/comparison-reports`

Fields:

- `lap_a_csv`;
- `lap_a_sidecar`;
- `lap_b_csv`;
- `lap_b_sidecar`;
- optional `grid_step_m`.

Frontend consumes the response as authoritative application evidence.

It must not derive engineering metrics itself.

## Testing contract

Behavioral tests should prefer user-observable behavior:

- labels/roles;
- button enablement;
- loading/status text;
- multipart field names;
- not-ready stage visibility;
- report summary/evidence visibility.

Avoid tests tightly coupled to CSS/class implementation.

Visualization adapters may receive focused contract tests for trace/data mapping.

## Related artifacts

- ADR-0008 — local HTTP API + React UI
- MVP first vertical slice
- Plan 017 source upload HTTP workflow
- Plan 018 frontend foundation
- OME interface principles
