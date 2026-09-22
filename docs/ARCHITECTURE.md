# OME Architecture Foundation

Status: **Pre-architecture / constraints only**

This document records architecture principles that are already justified by the project. It does **not** select a programming language, framework, database, cloud provider or deployment platform.

## Architecture starts from requirements

    PROBLEM
      -> DOMAIN
      -> USE CASE
      -> REQUIREMENT
      -> QUALITY ATTRIBUTE
      -> ARCHITECTURE DRIVER
      -> ARCHITECTURE
      -> TECHNOLOGY

Technology choices should be postponed until the requirements that justify them are understood.

## Conceptual system responsibilities

    SOURCE DATA
        |
        v
    INGESTION
        |
        v
    VALIDATION / QUALITY
        |
        v
    NORMALIZED DATA
        |
        v
    DETERMINISTIC ENGINEERING ANALYSIS
        |
        v
    STRUCTURED EVIDENCE
        |
        +------------------+
        |                  |
        v                  v
    PRESENTATION       AI ASSISTANCE
        |                  |
        +--------+---------+
                 v
           HUMAN DECISION

These are responsibilities, not necessarily deployable services or code modules.

## Architecture principles

### Raw data integrity

Original telemetry is evidence and must not be silently overwritten by transformations.

### Provenance

Derived values and findings should be traceable to their source data, parameters and algorithm versions.

### Determinism

Critical numerical analysis and signal processing should be deterministic whenever practical.

### AI boundary

LLMs may explain, organize investigations, formulate hypotheses and identify missing evidence.

LLMs should not be the primary implementation of critical deterministic calculations.

### Data ownership

Essential local analysis should not require sending team data to an external service unless the user explicitly chooses that workflow.

### Interoperability

Data-source adapters should not define the engineering domain.

The project should be able to support multiple telemetry sources over time without rewriting the analysis concepts for every vendor.

### Incomplete data

Missing data must remain visible. The system must not fabricate unavailable channels or silently substitute questionable equivalents.

### Simplicity

Use the smallest architecture that satisfies validated requirements.

## Not decided yet

- implementation language(s);
- frontend framework;
- backend framework;
- database;
- file/storage format for internal persistence;
- desktop vs local web packaging;
- cloud architecture;
- plugin framework;
- AI provider/model;
- vector database;
- deployment topology.

These decisions require architecture drivers or ADRs.

## First architecture validation target

The first architecture should be validated through a narrow vertical slice that can demonstrate, at minimum:

    real dataset
      -> import
      -> validate
      -> preserve provenance
      -> identify session/run/lap context
      -> compare selected data
      -> produce a reproducible result

The exact scope of that slice must be defined by requirements before implementation.