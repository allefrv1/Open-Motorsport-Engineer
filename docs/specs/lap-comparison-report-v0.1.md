# Lap Comparison Report Specification v0.1

Status: **Accepted for Plan 014**

Date: 2026-09-22

## Purpose

Define the first integrated, source-independent comparison artifact that an OME API/UI can consume without knowing the internal sequencing of the individual deterministic analysis engines.

The report answers:

> What is the accepted two-lap comparison result, where did relative time change, which initial supporting channels are available, and what evidence produced every artifact?

It does not answer why a change happened.

## Architectural role

The report is an **application-level composition** of already-defined deterministic analysis artifacts.

It must not reimplement:

- distance alignment;
- delta-time calculation;
- delta-region classification;
- continuous interpolation;
- discrete gear sampling;
- brake semantic compatibility.

Those remain owned by the existing analysis engines.

## Input

A v0.1 report request contains:

1. one `LapComparisonRequest`;
2. optional Lap A / Lap B continuous channel series for:
   - `vehicle.speed`;
   - `driver.throttle`;
   - `driver.brake`;
   - `driver.steering`;
   - `engine.speed`;
3. optional Lap A / Lap B gear series for:
   - `transmission.gear`.

The report service executes the existing engines in dependency order.

## Dependency order

```text
LapComparisonRequest
-> LapComparisonEngine
-> DeltaObservationEngine
-> supporting overlay engines
-> report composition
```

If the base comparison is not ready, the report is not ready.

If the base comparison succeeds but an optional supporting channel is missing or incompatible, the report still succeeds and records that supporting evidence as not ready.

The report must never fabricate a channel to make the bundle complete.

## Initial supporting evidence set

The v0.1 report always describes the MVP's initial comparison set in this stable order:

1. `vehicle.speed`
2. `driver.throttle`
3. `driver.brake`
4. `driver.steering`
5. `engine.speed`
6. `transmission.gear`

A source does not need to provide all six.

## Supporting evidence summary

For every initial concept, the report contains one summary with:

- canonical concept;
- evidence kind:
  - continuous;
  - discrete;
- status:
  - available;
  - not_ready;
- canonical unit when available;
- deterministic issue codes/messages when not ready.

Successful underlying overlay artifacts remain directly available in the report.

This summary describes evidence availability only.

It does not calculate a universal min/max/mean or significance score in v0.1.

## Required report artifacts

A successful report contains:

- base `LapComparisonSuccess`;
- `DeltaObservationSuccess`;
- zero or more successful `ContinuousOverlaySuccess` artifacts;
- optional successful `GearOverlaySuccess`;
- exactly six supporting-evidence summaries in the stable order above;
- typed report provenance.

## Report readiness

Return `ComparisonReportNotReady` when:

- base comparison is not ready;
- the observation engine cannot accept the successful base comparison;
- report-level provenance/component identity is inconsistent;
- the request contains duplicate channel-pair declarations for one canonical concept;
- a supplied supporting channel-pair concept is outside the fixed v0.1 report set.

Missing optional telemetry does **not** make the whole report not ready.

## Provenance consistency

Every successful component must refer to the same base `ComparisonProvenance`.

Report assembly rejects successful overlays or observations whose base provenance differs from the report's base comparison.

The report provenance retains:

- report assembler id/version;
- complete base comparison provenance;
- complete observation provenance;
- successful continuous-overlay provenances;
- successful gear-overlay provenance when present;
- requested initial concept set.

Assembler:

`ome.lap-comparison.report`

Version:

`0.1.0`

## Determinism

Equivalent report requests must produce equal report results.

Supporting evidence ordering is fixed by this specification, not by dictionary/hash iteration.

## Missing evidence

Not-ready overlay issues are preserved in report summaries.

Examples:

- missing speed on Lap B;
- brake semantic id missing;
- brake semantics differ across laps;
- gear evidence missing;
- insufficient channel time coverage.

The report does not convert those issues into guessed values.

## Evidence vocabulary

The report contains:

- measured/canonical supporting evidence;
- derived delta metric;
- deterministic Observation regions;
- Missing Evidence.

It contains no:

- hypothesis;
- causal engineering interpretation;
- setup recommendation;
- driver judgment.

## Presentation boundary

The report is not a rendered UI or prose report.

It is the deterministic application artifact from which API serialization and UI presentation will be built.

Formatting, localization, charts and human-readable narrative belong to later layers.

## Out of scope

- statistical channel summaries;
- corner segmentation;
- significance ranking;
- causal attribution;
- automatic finding generation;
- persistence;
- API transport;
- UI;
- AI explanation.

## Related artifacts

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
- `docs/MVP.md`
- `docs/specs/lap-comparison-v0.1.md`
- `docs/specs/lap-delta-observations-v0.1.md`
