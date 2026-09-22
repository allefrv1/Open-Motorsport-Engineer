# OME Domain Map

Status: **Draft — terminology is expected to evolve**

This document defines the current high-level motorsport domain vocabulary used by OME.

Detailed and validated engineering knowledge belongs in `docs/domain/`.

## Core operational concepts

### Event

A motorsport activity occurring at a circuit or venue and containing one or more sessions.

### Session

A bounded period of track activity, such as practice, qualifying, testing or race running.

### Run / Outing

A practical unit of track operation between leaving and returning to the working area/pit context.

A run may contain multiple laps and may be associated with setup, tyre, fuel/energy and test context.

### Stint

A continuous period of operation that may overlap conceptually with a run depending on category and workflow.

The exact distinction between `Run` and `Stint` is not yet finalized.

### Lap

One traversal of a circuit used for timing and analysis.

A lap should not be treated as context-free. Its session, run, vehicle, driver and relevant conditions matter.

### Segment / Corner

A region of the circuit used to narrow an investigation.

Track segmentation rules are not yet finalized.

## Participants and physical context

- **Driver**
- **Vehicle**
- **Track**
- **Conditions**

## Operational engineering context

- **Setup**
- **Setup Change**
- **Tyre Set**
- **Fuel / Energy State**
- **Run Plan**
- **Driver Feedback**
- **Change Log**

These concepts are part of engineering analysis, not merely administrative metadata.

## Measurement concepts

### Telemetry Dataset

A collection of measured data associated with a known acquisition source and operational context.

### Channel

An identifiable measured or calculated signal with metadata.

A channel may include:

- original name;
- physical concept;
- source device;
- unit;
- timestamps;
- sample rate;
- conversion/calibration information;
- quality information.

Signals with similar meaning must not be silently collapsed into one value.

### Measurement

A value from an acquisition source at a known point in time or another defined reference.

### Derived Metric / Derived Channel

A deterministic value calculated from one or more source channels.

Derived data should preserve:

- source inputs;
- units;
- algorithm;
- parameters;
- algorithm version;
- provenance.

## Investigation concepts

### Observation

A statement describing what available evidence shows without claiming a cause.

### Hypothesis

A possible explanation that can be evaluated against evidence.

### Finding

A documented result of an investigation with supporting evidence and known limitations.

### Investigation

The structured process used to answer an engineering question.

### Decision

A human-approved action, interpretation or next test resulting from an investigation.

## Fundamental distinction

    MEASURED
    != DERIVED
    != OBSERVED
    != HYPOTHESIZED
    != INTERPRETED

## Open domain questions

- exact relationship between Run, Outing and Stint across categories;
- canonical track/segment representation;
- canonical representation of units and physical quantities;
- canonical channel identity and aliasing model;
- how setup versions are represented;
- how tyre history is represented;
- which operational context belongs to Event, Session or Run;
- which concepts vary by motorsport category.