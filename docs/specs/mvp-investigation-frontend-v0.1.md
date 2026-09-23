# MVP Investigation Frontend Specification v0.1

Status: **Accepted for Plan 018**

Date: 2026-09-23

## Purpose

Define the first real user interface for the OME vertical slice.

The interface exists to help a user answer:

> Where did Lap B gain or lose time relative to Lap A, and which measured evidence supports that observation?

It is an investigation workspace, not a generic telemetry dashboard.

## Primary user flow

```text
Select Lap A source bundle
-> Select Lap B source bundle
-> Compare
-> Review readiness / missing evidence
-> Inspect delta and observations
-> Inspect supporting telemetry
-> Open method / provenance detail
```

The first source workflow uses the accepted OME CSV upload HTTP endpoint.

## Screen architecture

Plan 018 begins with one focused investigation screen.

### 1. Application header

Keep compact:

- OME product name;
- local/offline-oriented status text;
- backend connectivity state when relevant.

Do not add navigation items for features that do not exist.

### 2. Source selection

Two semantic fieldsets:

- Lap A;
- Lap B.

Each lap requires:

- OME CSV file;
- matching `.ome.json` sidecar.

Show the selected filenames.

Primary action:

- **Compare laps**

The action remains disabled until all four required files are present.

Advanced comparison settings are progressively disclosed.

Initial advanced setting:

- distance grid step in metres;
- default `1.0 m`.

The UI must not ask the user to construct canonical concepts, Session hashes or evidence JSON.

### 3. Comparison context header

After a successful comparison, keep visible:

- Lap A filename;
- Lap B filename;
- reference convention;
- comparable distance interval;
- grid step.

Reference convention must be explicit:

```text
Delta = B - A
positive -> B took more time
negative -> B took less time
```

Do not rely on color to communicate the sign convention.

### 4. Result summary

Show the accumulated delta at the end of the comparable interval with sign and unit.

Example:

```text
B vs A at 100 m: +0.200 s
```

This is a derived metric, not a causal conclusion.

Label it accordingly.

### 5. Observation regions

Render deterministic observation regions from the report:

- B gain;
- B loss;
- neutral.

For each region show:

- start/end distance;
- start/end delta;
- total delta change.

Do not label a region as:

- braking mistake;
- understeer;
- setup problem;
- driver error.

Those would be unsupported causal interpretation.

### 6. Telemetry investigation plots

Use the accepted Plotly.js visualization adapter.

Plots are aligned on distance.

The first interface may show:

- delta time;
- vehicle speed;
- throttle;
- brake;
- steering;
- engine speed;
- gear.

Rules:

- units adjacent to axis/value labels;
- Lap A and Lap B labels remain explicit;
- line identity must use text/legend plus visual treatment, not color alone;
- do not smooth source/derived evidence silently;
- continuous overlays use the deterministic report data already produced by the backend;
- gear remains discrete;
- unavailable channels do not receive fake zero lines.

A common distance reference must remain obvious across plots.

Exact values must be inspectable through Plotly hover/interaction.

### 7. Missing evidence

Supporting evidence with `status=not_ready` remains visible.

Show:

- concept name;
- missing/incompatible reason;
- backend message.

Missing evidence is not an application crash.

### 8. Provenance / method detail

Use progressive disclosure, e.g. a native `<details>` region.

Make discoverable:

- Session / Run / Lap identifiers;
- source channel name;
- canonical concept;
- unit;
- semantic id when present;
- transformation/rule identity;
- algorithm id/version;
- comparison parameters.

Beginner users do not need this expanded by default.

## Evidence presentation

Keep these visually distinct:

- source/measured evidence;
- deterministic derived metrics;
- deterministic observations;
- missing evidence.

Plan 018 does not show hypotheses, engineering interpretations, possible actions or AI explanations because those layers are not implemented.

## HTTP workflow

The UI submits:

`POST /api/v1/ome-csv/comparison-reports`

as multipart form data.

Required files:

- `lap_a_csv`;
- `lap_a_sidecar`;
- `lap_b_csv`;
- `lap_b_sidecar`.

Form value:

- `grid_step_m`.

The frontend does not send local filesystem paths.

For local development, Vite should proxy the OME API paths to the loopback FastAPI process so backend CORS policy does not need to be widened for the development workflow.

## Interaction states

### Idle

- source selectors visible;
- compare disabled.

### Ready

- all required files selected;
- compare enabled.

### Loading

- compare disabled;
- visible processing status;
- retain selected file labels;
- no fake progress percentage.

### Success

- context;
- result summary;
- observations;
- plots;
- supporting evidence;
- provenance detail.

### Not ready — import

Explain that the selected source bundle could not be imported.

Show returned issues and which lap is affected.

### Not ready — preparation

Explain that source files were readable but comparison evidence is insufficient/invalid.

Never render a plausible comparison plot from incomplete evidence.

### Not ready — report

Explain that preparation succeeded but deterministic comparison/report readiness failed.

### Transport/server error

Clearly separate HTTP/network failure from engineering not-ready states.

Preserve file selections so the user can retry.

## Accessibility

Target WCAG 2.2 AA.

Required baseline:

- semantic `main`, headings and regions;
- fieldsets/legends for Lap A/B;
- programmatic labels for file inputs and grid setting;
- visible keyboard focus;
- compare action keyboard-operable;
- loading/result/error status announced through an appropriate live region;
- critical meaning not encoded by color alone;
- chart containers have accessible names and nearby textual summaries;
- provenance/details keyboard-operable;
- validation/not-ready messages associated with the relevant workflow area.

After submit, focus should move to the result/not-ready heading when practical without unexpected scroll traps.

## Responsive behavior

The investigation workflow is desktop-oriented but must remain usable on narrower screens.

### Wide

- Lap A/B source selectors may sit side by side;
- investigation plots use full available width;
- context remains compact.

### Narrow

- Lap source selectors stack;
- summary and observations stack;
- plot containers remain full width;
- dense evidence/provenance tables may use intentional horizontal scrolling;
- primary action remains visible.

Do not simply shrink chart labels below legible size.

## Frontend architecture

Organize by workflow/features:

```text
frontend/src/
  app/
  features/comparison/
  components/
  lib/
```

Backend/domain layers are not mirrored in the component tree.

Suggested responsibilities:

- app shell / API connectivity;
- comparison source form;
- comparison result workspace;
- telemetry plot adapter;
- evidence/provenance inspector;
- API client + DTO types.

## Testing contract

Critical user-flow tests must be written before feature implementation.

Use browser-like component tests for:

- required file selection;
- compare disabled/enabled state;
- multipart request construction;
- loading state;
- success result summary;
- deterministic sign wording;
- not-ready import/preparation/report states;
- missing evidence display;
- provenance disclosure;
- accessible labels/headings/status.

Plotly rendering may be adapter-mocked in component tests.

The frontend test should verify the plot adapter receives the backend distance grid and evidence series rather than testing Plotly internals.

Type checking and a production Vite build are required in the canonical harness.

## Visual direction

Prefer a neutral technical workspace:

- high information contrast;
- compact but readable spacing;
- stable alignment;
- restrained use of accent colors;
- typography and grouping before decorative containers.

Avoid:

- card grids for every metric;
- neon/racing-game decoration;
- speedometer/gauge metaphors for ordinary numerical evidence;
- excessive gradients;
- animated telemetry for static lap comparison;
- hidden evidence behind hover-only interactions.

## Out of scope

- multi-page project/session browser;
- saved projects;
- authentication;
- cloud workflows;
- generic source upload;
- MoTeC/iRacing browser import;
- AI explanations;
- setup recommendations;
- causal diagnosis;
- live telemetry;
- polished brand system.

## Related artifacts

- MVP
- ADR-0008 — local HTTP API and React UI
- OME Interface Principles
- OME CSV Comparison Upload HTTP API v0.1
- Lap Comparison Report v0.1
- Plan 018 — MVP Investigation Frontend
