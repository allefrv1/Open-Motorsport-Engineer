# REQ-006 — Preserve Analysis Evidence

Status: **Accepted**

## Actor / User

Any user reviewing an OME analysis or finding.

## Problem

Engineering conclusions lose value when the user cannot determine which measurements, calculations and assumptions produced them.

## Goal

Make every important deterministic result and later engineering finding auditable.

## Acceptance Criteria

An analysis artifact must be capable of distinguishing:

- measured evidence;
- derived metrics;
- observation;
- hypothesis;
- engineering interpretation;
- missing evidence.

Important deterministic metrics must be able to reference:

- source channels;
- dataset/run/lap/segment context;
- algorithm identity/version;
- parameters;
- transformations;
- units.

AI-generated explanation must never be represented as measured evidence.

## Principle

```text
Finding
  -> Observation
  -> Metric
  -> Transformation
  -> Source Channel
  -> Original Dataset
```

The chain must remain inspectable.


## Lap-comparison foundation traceability

Plan 009 introduces typed executable evidence for the first deterministic comparison metric.

The comparison result can reference:

- both original dataset fingerprints;
- Session / Run / Lap identifiers;
- source channel identifiers and original source names;
- canonical concept and unit;
- transformation identity/version/parameters;
- comparison algorithm identity/version;
- comparison parameters;
- common distance interval.

The evidence chain is exercised by:

`tests/analysis/test_lap_comparison.py::Req005LapComparisonTests.test_ac005_and_ac006_provenance_preserves_context_channels_and_algorithm`

Missing provenance produces an explicit not-ready issue rather than an opaque metric.

The deterministic result intentionally contains no cause, hypothesis or engineering-interpretation field.

This implements the REQ-006 evidence capability for the Plan 009 delta-time metric; broader findings/observations remain future work.


## Continuous overlay evidence traceability

Plan 010 extends the evidence chain from delta-time into aligned continuous measured evidence.

`ContinuousOverlayProvenance` references:

- overlay algorithm identity/version;
- overlay parameters;
- the complete base comparison provenance;
- Lap A canonical channel evidence;
- Lap B canonical channel evidence;
- each channel's source identifier/original name;
- each channel's normalization/transformation evidence;
- original dataset fingerprints through the base comparison and channel evidence.

The chain is exercised by:

`tests/analysis/test_continuous_overlay.py::Plan010ContinuousOverlayTests.test_channel_provenance_and_base_comparison_provenance_remain_inspectable`

A dataset/provenance mismatch returns explicit not-ready evidence rather than an aligned series.

The continuous overlay result remains a deterministic derived artifact and contains no cause, hypothesis or engineering-interpretation fields.

TDD evidence:

- RED: OME CI #91;
- GREEN: OME CI #96.
