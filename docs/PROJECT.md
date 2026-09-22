# Open Motorsport Engineer — Project Definition

Status: **Accepted foundation**

## Problem

Motorsport produces large amounts of telemetry and operational data, but interpreting those data requires engineering knowledge, context and disciplined workflows.

Professional tools are powerful, but the difficult part is often not displaying data. It is turning measurements into a defensible engineering investigation.

## Mission

> Reduce the gap between motorsport data and the engineering knowledge required to interpret it.

OME should help users move from raw data to understandable, traceable and reproducible engineering reasoning.

## Intended users

OME may serve:

- drivers;
- coaches;
- engineering students;
- Formula Student / Formula SAE teams;
- small racing teams;
- data and performance engineers;
- advanced technical users.

Different users may receive different levels of disclosure, but the underlying engineering evidence should remain consistent.

## Product principles

OME should be:

- open source;
- transparent;
- evidence-driven;
- reproducible;
- traceable;
- interoperable;
- extensible;
- offline-capable for essential analysis;
- respectful of data ownership;
- accessible without hiding engineering detail from advanced users.

## What OME is not

OME should not begin as:

- a clone of MoTeC i2, AiM RaceStudio or Cosworth Pi Toolbox;
- a generic plotting application;
- a chatbot directly over raw telemetry;
- a black-box setup recommendation engine;
- a complete vehicle simulation environment;
- an attempt to solve every motorsport discipline in the first release.

## Core product loop

```text
IMPORT
  -> VALIDATE
  -> CONTEXTUALIZE
  -> COMPARE
  -> OBSERVE
  -> INVESTIGATE
  -> EXPLAIN
  -> DOCUMENT
```

## Engineering reasoning model

OME preserves:

```text
MEASUREMENT
  -> DERIVED DATA
  -> OBSERVATION
  -> HYPOTHESIS
  -> ENGINEERING INTERPRETATION
  -> POSSIBLE ACTION
```

The system must be able to conclude that evidence is insufficient.

## Foundation status

The project has established:

- initial domain terminology;
- first vertical-slice scope;
- functional requirements;
- quality attributes;
- architecture drivers;
- data integrity/provenance rules;
- architecture and technology baseline;
- testing strategy;
- agent-first harness requirements.

The next engineering phase is not feature implementation.

It is the executable harness bootstrap defined in `docs/plans/active/002-harness-bootstrap.md`.

## Long-term vision

OME may eventually support:

- driver performance analysis;
- vehicle dynamics analysis;
- setup comparison;
- tyre analysis;
- vehicle health/reliability;
- anomaly detection;
- race strategy;
- telemetry visualization;
- engineering reports;
- AI-assisted engineering investigation.

Long-term vision does not imply immediate scope.
