# REQ-003 — Organize Session, Run and Lap Context

Status: **Accepted**

## Actor / User

A user who needs to navigate telemetry in the same operational units used during track work.

## Problem

Telemetry without operational context is difficult to compare and can lead to incorrect conclusions.

A Lap must be understood within its Session, Run, driver, vehicle and relevant conditions.

## Goal

Represent and navigate Session / Run / Lap context without forcing importers to invent operational boundaries.

## Main Flow

1. OME receives imported and validated telemetry.
2. OME preserves trustworthy source-provided session/run/lap markers.
3. OME associates canonical Session / Run / Lap entities when sufficient evidence exists.
4. OME preserves provenance of those boundaries.
5. The user can navigate from Session to Run to Lap.
6. Missing or ambiguous boundaries remain explicit.

## Acceptance Criteria

### AC-001 — Context hierarchy

OME must be able to represent:

```text
Session
  -> Run
      -> Lap
```

when those relationships are known.

### AC-002 — No invented boundaries

OME must not fabricate lap or run boundaries when the available evidence is insufficient.

### AC-003 — Source markers preserved

When a source supplies lap/session markers, OME must preserve their source identity and provenance.

### AC-004 — Operational metadata

A Run must be capable of being associated with:

- driver;
- vehicle;
- setup version;
- tyre set;
- fuel/energy state;
- run plan;
- driver feedback;
- conditions.

These associations are contextual records, not telemetry channels.

### AC-005 — Stint deferred

The initial model must not force Stint to be a synonym of Run.

## Out of Scope

- generic automatic lap detection;
- endurance stint strategy;
- pit strategy;
- automatic setup interpretation.
