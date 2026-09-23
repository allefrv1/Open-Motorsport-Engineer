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
