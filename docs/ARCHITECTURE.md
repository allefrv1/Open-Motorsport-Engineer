# OME Architecture Foundation

Status: **Accepted pre-code architecture**

This document defines the architecture boundaries and drivers that are sufficiently understood before implementation. It intentionally does **not** select a programming language, UI framework, database or deployment platform.

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
```

Technology selection happens after the current foundation is reviewed against representative data.

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

These are logical responsibilities, not microservices or deployment units.

## Architecture boundaries

### Source adapters

Responsible for:

- reading source-specific structures;
- preserving original channel identity;
- preserving source metadata;
- creating source-independent imported representations;
- reporting import warnings.

Not responsible for:

- engineering diagnosis;
- canonical channel guessing;
- hidden resampling;
- lap-performance analysis.

### Data quality

Responsible for non-destructive validation and explicit quality issues.

Not responsible for repairing data silently.

### Normalization

Responsible for explicit, traceable mapping from source channels to canonical OME engineering concepts.

Not responsible for erasing source representation.

### Operational context

Responsible for Session / Run / Lap and associated metadata such as driver, setup, tyres and conditions.

### Engineering core

Responsible for deterministic calculations, transformations and metrics.

Every important derived result must be traceable to inputs, algorithm version and parameters.

### Evidence layer

Represents the distinction between:

- measured;
- derived;
- observation;
- hypothesis;
- interpretation;
- missing evidence.

This layer is the contract between deterministic engineering computation and later AI assistance.

### AI layer

AI may:

- organize an investigation;
- explain concepts;
- relate structured evidence;
- formulate hypotheses;
- identify missing evidence;
- draft summaries.

AI must not:

- fabricate telemetry;
- replace deterministic numerical calculation;
- silently modify evidence;
- present hypotheses as measurements;
- make the portable engineering core depend on an external AI service.

## Architecture drivers

The strongest drivers currently identified are:

1. **Integrity** — original telemetry is evidence.
2. **Traceability** — results must lead back to source data.
3. **Reproducibility** — deterministic results must be reproducible.
4. **Interoperability** — OME must support heterogeneous sources.
5. **Multi-rate data** — the model cannot assume one common sample rate.
6. **Offline usability** — essential trackside work cannot depend on cloud access.
7. **Data ownership** — telemetry should not leave the user's environment implicitly.
8. **Extensibility** — adapters and metrics must evolve independently.
9. **Performance** — realistic multi-hour, multi-channel datasets must remain practical.
10. **Explainability** — users must be able to inspect why a result exists.

See `docs/QUALITY_ATTRIBUTES.md`.

## Initial source strategy

Accepted implementation order:

1. OME CSV Exchange Profile;
2. iRacing `.ibt`;
3. MoTeC CSV export;
4. evaluate native MoTeC `.ld` later.

The OME CSV profile is an exchange and fixture format, **not** the canonical internal model.

## First vertical slice

The first architecture will be validated against `docs/MVP.md`.

It must support the conceptual flow:

```text
SOURCE
  -> IMPORT
  -> VALIDATE
  -> NORMALIZE
  -> CONTEXTUALIZE
  -> COMPARE TWO LAPS
  -> STRUCTURED EVIDENCE
```

No AI capability is required to prove the first vertical slice.

## Architecture decisions already accepted

- ADR-0001 — Separate source ingestion from telemetry normalization.

Additional decisions should be recorded as ADRs when they materially constrain future implementation.

## Technology decisions intentionally deferred

Still undecided:

- implementation language(s);
- frontend framework;
- backend/application framework;
- persistence engine;
- internal columnar/storage representation;
- desktop packaging;
- AI provider/model;
- deployment topology.

These should be selected only after:

- representative fixtures are available;
- architecture drivers are prioritized;
- first-slice performance assumptions are checked;
- technology options are compared against the requirements.

## Explicit non-goals for the first architecture

- microservices;
- mandatory cloud backend;
- distributed messaging;
- Kubernetes;
- complex event sourcing/CQRS;
- live telemetry;
- full simulation;
- AI-first analysis.

The project should begin as the smallest architecture that preserves the boundaries above.
