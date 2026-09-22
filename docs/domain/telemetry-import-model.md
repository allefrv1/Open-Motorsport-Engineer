# Telemetry Import Model

Status: **Accepted domain foundation**

## Purpose

This document defines the conceptual domain model at the boundary between an external telemetry source and OME.

It does not define classes, database tables, APIs or file formats.

Its purpose is to give future implementation work a stable vocabulary.

## Boundary

The model covers:

```text
EXTERNAL SOURCE
  -> INGESTION
  -> IMPORTED TELEMETRY DATASET
```

It does not yet cover:

- data-quality validation;
- canonical channel normalization;
- resampling/alignment;
- derived metrics;
- Session / Run / Lap detection;
- engineering analysis;
- AI interpretation.

## TelemetrySource

Represents the origin presented to OME for ingestion.

Examples may include:

- an OME CSV profile;
- an arbitrary CSV export;
- an iRacing `.ibt` file;
- a MoTeC `.ld` file;
- a MoTeC CSV export.

A TelemetrySource should conceptually expose, where available:

- source type;
- original name/path identity;
- source-system identity;
- format/version information;
- raw metadata;
- content fingerprint or equivalent identity.

A TelemetrySource is not an engineering interpretation.

## ImportedTelemetryDataset

Represents the result of a successful ingestion.

It means:

> OME was able to read and preserve the source representation.

It does **not** mean:

- the data is valid;
- the channels are normalized;
- the data is suitable for a specific analysis.

The dataset should contain:

- provenance;
- source metadata;
- source channels;
- import issues/warnings;
- importer identity/version.

## SourceChannel

Represents one signal as provided by the source.

A SourceChannel should preserve, when available:

- original name;
- original identifier;
- source device/system;
- source unit;
- source data type;
- acquisition/time-base information;
- sample series reference;
- source-specific metadata.

A SourceChannel may later be mapped to a canonical engineering concept, but that mapping must not replace the source identity.

## SampleSeries

Represents the ordered measured values associated with one source signal or one source time base.

The model must not assume that all channels share:

- the same timestamps;
- the same sample rate;
- the same number of samples;
- the same start/end time.

No resampling behavior is implied by this concept.

## ChannelMetadata

Represents descriptive information supplied by the source about a channel.

Possible fields include:

- unit;
- sample rate;
- data type;
- description;
- conversion/calibration metadata;
- valid range;
- source-specific attributes.

All fields are source-dependent unless later requirements make them mandatory.

Unknown values remain unknown.

## Provenance

Represents the trace from imported data back to its origin.

At minimum, the concept should be capable of carrying:

- original source identity;
- source format/type;
- source-system identity when known;
- importer identity;
- importer version;
- import parameters;
- content fingerprint when available.

Operational timestamps may also be recorded, but they must not be confused with source measurement time.

Minimum provenance is defined in `docs/domain/provenance.md`.

## ImportIssue

Represents a condition discovered during ingestion that should remain visible.

Examples:

- missing metadata;
- unsupported source feature;
- truncated optional section;
- ambiguous source field;
- source warning.

ImportIssue is not the same as a validation failure.

An import can potentially succeed with warnings if the readable evidence remains intact.

The first version does not attempt partial recovery from structurally corrupted telemetry; see `docs/domain/data-quality.md`.

## Conceptual invariants

### I-001 — Source preservation

Ingestion must not silently overwrite or mutate the original source.

### I-002 — Original channel identity

Every imported channel must preserve the identity provided by the source.

### I-003 — Unknown remains unknown

Missing metadata must not be fabricated.

### I-004 — No silent normalization

Canonical engineering concepts must not replace source identity during ingestion.

### I-005 — No forced common time base

The import model must not require all channels to be resampled to one timeline.

### I-006 — Provenance survives ingestion

Imported data must remain traceable to the source and importer that produced it.

### I-007 — Import success is not validation success

A readable dataset is not automatically trusted or ready for analysis.

## State vocabulary

OME should conceptually distinguish at least:

```text
DISCOVERED
  -> IMPORTED
  -> VALIDATED
  -> NORMALIZED
  -> READY FOR A SPECIFIC ANALYSIS
```

These are conceptual lifecycle states. Their implementation is intentionally undecided.

## Relationship to future normalization

A future normalization layer may create mappings such as:

```text
SourceChannel("Ground Speed")
        |
        v
CanonicalConcept("vehicle.speed")
```

The mapping should remain traceable and reversible at the evidence level.

Normalization must never erase the original source channel.

## Relationship to analysis readiness

Readiness is analysis-specific.

A dataset may be valid and useful for RPM analysis while being insufficient for yaw-response analysis.

Therefore OME should avoid a single simplistic notion that a dataset is globally "good" or "bad" for every engineering question.
