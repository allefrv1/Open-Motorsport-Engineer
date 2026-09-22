# REQ-001 — Import Telemetry Session

Status: **Proposed**

## Actor / User

A driver, coach, student, data engineer or performance engineer who has telemetry data from a supported source and wants to begin an OME analysis.

## Problem

Before OME can validate, compare or analyze telemetry, it must be able to ingest source data without destroying its original meaning or provenance.

Import must not silently reinterpret channels, fabricate metadata or modify the original telemetry source.

## Goal

Allow the user to import telemetry from a supported source into OME and obtain a traceable imported dataset that is ready for subsequent validation.

This requirement defines the initial source families OME intends to support, but it does not prescribe the implementation technology for their importers.

## Initial Source Strategy

OME will begin with three source families that serve different purposes:

### 1. OME CSV Profile — first implementation target

OME will define a project-owned CSV profile for deterministic development fixtures, examples and controlled interoperability.

This is not the same as promising support for every arbitrary CSV layout.

The OME CSV profile should become the first importer implemented because it allows the import contract, provenance rules and validation behavior to be tested without depending on a proprietary ecosystem.

### 2. iRacing binary telemetry (.ibt) — first external adapter target

iRacing `.ibt` is the first external telemetry format targeted after the OME CSV profile.

Its purpose is to exercise the importer against richer telemetry, session metadata and real-world variation in channel availability while remaining practical for development and repeatable testing.

### 3. MoTeC log data (.ld) — first professional real-motorsport source target

MoTeC `.ld` is a target source for validating OME against professional real-world motorsport workflows.

Native `.ld` support is subject to a separate feasibility decision covering:

- supported access mechanism;
- licensing;
- operating-system constraints;
- test fixtures;
- long-term maintainability.

Until native `.ld` ingestion is accepted as technically and legally appropriate, MoTeC-exported CSV may be used as an interim source of real motorsport data.

### Importer independence

All source-specific importers must conform to a common ingestion boundary.

Source-specific details must not leak into the core engineering domain unless the domain explicitly requires them.

## Preconditions

- The user has access to telemetry from a source OME supports.
- A compatible importer exists for that source.
- The source is readable by the application environment.

## Main Flow

1. The user selects or provides a telemetry source.
2. OME identifies a compatible importer for the source.
3. OME reads the source without modifying the original telemetry.
4. OME captures enough source information to preserve provenance.
5. OME discovers the channels and metadata made available by the source.
6. OME preserves original channel identity before any normalization.
7. OME creates an imported telemetry dataset.
8. OME presents an import summary.
9. The imported dataset becomes available to the telemetry validation workflow.

## Import Summary

When the source provides the information, the import summary should expose at least:

- source type / format;
- source identity;
- available channels;
- original channel names;
- units;
- sample rates or equivalent acquisition information;
- relevant source metadata;
- warnings or missing metadata.

OME must not invent metadata that the source does not provide.

## Alternative / Failure Flows

### Unsupported source

If no compatible importer exists:

- OME must not claim the import succeeded;
- OME must preserve the original source untouched;
- OME must report that the source is unsupported.

### Corrupted or unreadable source

If the source cannot be safely read:

- OME must report the failure;
- OME must not create a dataset that appears valid;
- diagnostic information should be available to support troubleshooting.

Whether partial recovery is supported is an open question and is not required by this version.

### Missing metadata

If metadata such as units or sample rate is unavailable:

- the value must remain explicitly unknown or unavailable;
- OME must not silently infer it unless a separately defined and traceable rule allows inference.

### Ambiguous signal identity

If a source contains signals whose engineering meaning cannot be determined safely:

- preserve the original channel identity;
- do not silently map the signal to a canonical concept;
- defer normalization until sufficient mapping information exists.

## Expected Result

A successful import produces a telemetry dataset that:

- preserves the original source provenance;
- preserves the identity of source channels;
- contains the metadata actually available from the source;
- exposes missing or ambiguous metadata;
- is suitable for the next validation stage;
- contains no unsupported engineering interpretation.

## Acceptance Criteria

### AC-001 — Successful supported import

Given a readable telemetry source with a supported importer, when the user imports it, then OME creates an imported telemetry dataset and reports success.

### AC-002 — Source integrity

Importing telemetry must not modify or overwrite the original source data.

### AC-003 — Provenance

The imported dataset must retain enough information to identify the source from which it was created.

The exact technical mechanism is an architecture decision and is not prescribed here.

### AC-004 — Channel inventory

OME must expose every channel that the importer successfully discovers, preserving its original source name.

### AC-005 — Source metadata preservation

When units, acquisition rate or equivalent metadata are available from the source, OME must preserve them.

### AC-006 — Missing metadata

When expected metadata is unavailable, OME must represent it as missing or unknown rather than fabricating a value.

### AC-007 — Unsupported source

When the source is unsupported, OME must return an explicit unsupported-source result and must not create a dataset that appears successfully imported.

### AC-008 — Read failure

When a source cannot be safely read, OME must fail explicitly and must not expose the result as a valid imported dataset.

### AC-009 — No silent normalization

Import must not silently replace source channel identity with a canonical engineering concept.

Normalization is a separate responsibility.

### AC-010 — Reproducible import behavior

For the same source data, importer version and import parameters, the semantically relevant imported content should be reproducible.

Generated identifiers, timestamps or other operational metadata may differ if later architecture decisions allow them.

## Relevant Domain Concepts

- Telemetry Dataset
- Channel
- Measurement
- Session
- Run
- Lap
- Source
- Provenance

The exact creation of Session, Run and Lap structures during import is not yet defined by this requirement.

## Quality Attributes

### Integrity

Original telemetry must remain unchanged.

### Traceability

Imported data must remain connected to its original source.

### Interoperability

The requirement must allow multiple source-specific importers over time without requiring source-specific engineering concepts in the core domain.

### Tolerance of incomplete data

Missing metadata must be represented explicitly.

### Reproducibility

Import behavior should be reproducible for equivalent inputs and importer versions.

## Out of Scope

This requirement does not define:

- canonical channel naming;
- unit conversion rules;
- signal resampling;
- time synchronization;
- quality scoring;
- Session / Run / Lap detection rules;
- lap comparison;
- track segmentation;
- engineering analysis;
- AI interpretation;
- persistence technology;
- user-interface implementation.

These responsibilities require separate requirements or architecture decisions.

## Open Questions

The following questions must be resolved before or during acceptance of related requirements:

1. What exact schema will define the OME CSV profile?
2. Can one source contain multiple sessions or runs, and how should that be represented?
3. Should import support partial recovery from damaged files, or fail atomically in the first version?
4. How should OME identify that the same source has been imported before?
5. What minimum provenance information is required across all source types?
6. When should Session / Run / Lap detection happen: during import, validation or a later organization stage?
7. Which metadata must be mandatory for a dataset to progress from imported to valid?
8. What dataset sizes and import times should the first version support?
9. What access strategy should be used for native MoTeC `.ld` files?
10. Which licensing and platform constraints apply to native MoTeC support?

## Notes

This requirement defines the boundary between **source ingestion** and later stages.

Conceptually:

```text
SOURCE
  -> IMPORT
  -> IMPORTED DATASET
  -> VALIDATION
  -> NORMALIZATION
  -> ANALYSIS
```

Import should preserve evidence.

It should not attempt to decide what the evidence means.
