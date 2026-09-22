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
