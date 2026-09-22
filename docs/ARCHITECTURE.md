# OME Architecture Foundation

Status: **Accepted architecture baseline**

## Purpose

This document is the top-level architecture map.

Detailed decisions live in `docs/adr/`. Requirements, domain rules and specifications remain separate sources of truth.

## Architecture flow

```text
PROBLEM
  -> DOMAIN
  -> USE CASE
  -> REQUIREMENT
  -> QUALITY ATTRIBUTE
  -> ARCHITECTURE DRIVER
  -> ARCHITECTURE
  -> TECHNOLOGY
  -> EXECUTABLE FEEDBACK
```

The architecture baseline is selected, but the implementation harness and representative data validation are still pending.

## System context

OME is a local-first engineering analysis application that consumes motorsport telemetry and operational context, performs deterministic processing, presents evidence and may later use AI to assist investigation and explanation.

Primary human actors include:

- driver;
- coach;
- student;
- data/performance engineer;
- race engineer;
- team member.

External systems may include:

- telemetry files/loggers;
- iRacing telemetry;
- MoTeC workflows;
- future DAQ/ECU/export formats;
- optional AI providers.

## Conceptual responsibilities

```text
EXTERNAL TELEMETRY SOURCES
          |
          v
SOURCE ADAPTERS / INGESTION
          |
          v
IMPORTED SOURCE REPRESENTATION
          |
          v
DATA QUALITY / VALIDATION
          |
          v
NORMALIZATION
          |
          v
CANONICAL ENGINEERING DATA
          |
          +----------------------+
          |                      |
          v                      v
SESSION/RUN/LAP CONTEXT    DETERMINISTIC METRICS
          |                      |
          +-----------+----------+
                      v
              STRUCTURED EVIDENCE
                      |
             +--------+--------+
             |                 |
             v                 v
       PRESENTATION      AI ASSISTANCE
             |                 |
             +--------+--------+
                      v
               HUMAN DECISION
```

These are logical responsibilities, not microservices.

## Architecture boundaries

### Source adapters

Read source-specific structures, preserve source identity/metadata/provenance, and emit import warnings.

They do not perform engineering diagnosis, hidden normalization, hidden resampling or lap-performance analysis.

### Data quality

Performs non-destructive validation and emits explicit issues.

It does not silently repair telemetry.

### Normalization

Maps source channels to canonical OME concepts through explicit, traceable rules.

It does not erase source representation.

### Operational context

Represents Session / Run / Lap and context such as driver, vehicle, setup, tyres and conditions.

### Engineering core

Performs deterministic transformations, alignment, calculations and metrics.

Important results must remain traceable to inputs, parameters and algorithm versions.

### Evidence layer

Preserves the distinction between:

- measured;
- derived;
- observation;
- hypothesis;
- interpretation;
- missing evidence.

### AI layer

AI may organize investigations, explain concepts, formulate hypotheses from structured evidence and identify missing evidence.

AI must not fabricate telemetry, replace deterministic calculations, silently modify evidence or make essential local analysis depend on an external service.

## Architecture drivers

1. Integrity
2. Traceability
3. Reproducibility
4. Interoperability
5. Multi-rate data
6. Offline usability
7. Data ownership
8. Extensibility
9. Performance
10. Explainability
11. Agent legibility and mechanical verification

See:

- `docs/QUALITY_ATTRIBUTES.md`
- `docs/CORE_BELIEFS.md`
- `docs/HARNESS_ENGINEERING.md`

## Initial source strategy

1. OME CSV Exchange Profile
2. iRacing `.ibt`
3. MoTeC CSV export
4. native MoTeC `.ld` evaluated later

CSV is an exchange/fixture profile, not the canonical internal telemetry model.

## Application shape and technology baseline

Accepted decisions currently select:

- local modular monolith;
- Python engineering/application core;
- Arrow-compatible columnar processing;
- Polars as initial high-level processing engine;
- Parquet telemetry persistence;
- SQLite project metadata;
- local FastAPI application boundary;
- React + TypeScript + Vite frontend;
- Plotly.js as an initial replaceable visualization adapter;
- distance-based deterministic lap alignment.

These choices are recorded in ADR-0004 through ADR-0009.

They are architecture baselines, not evidence that the executable harness or performance targets have already been validated.

## First vertical slice

After harness bootstrap, the first feature flow is:

```text
SOURCE
  -> IMPORT
  -> VALIDATE
  -> NORMALIZE
  -> CONTEXTUALIZE
  -> COMPARE TWO LAPS
  -> STRUCTURED EVIDENCE
```

No AI capability is required for this slice.

## Accepted ADRs

See `docs/adr/README.md` for the authoritative ADR index.

Current accepted architecture topics include:

- ingestion / validation / normalization separation;
- CSV role;
- AI boundary;
- local modular monolith;
- Python core;
- Arrow/Parquet telemetry foundation;
- SQLite metadata;
- local HTTP API + React UI;
- distance-based lap comparison.

## Harness requirement

Architecture prose is not sufficient.

As modules appear, high-value boundaries must be promoted into structural tests or dependency rules where practical.

Feature work starts only after the active harness-bootstrap plan establishes reproducible setup and canonical verification commands.

## Explicit first-phase non-goals

- microservices;
- mandatory cloud backend;
- distributed messaging;
- Kubernetes;
- complex CQRS/event sourcing;
- live telemetry;
- complete vehicle simulation;
- AI-first analysis;
- native MoTeC `.ld` dependency;
- premature native-language optimization.
