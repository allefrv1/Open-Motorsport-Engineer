# REQ-001 — Import Telemetry Session

Status: **Implemented**

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

### 3. MoTeC workflow — first professional real-motorsport source target

MoTeC-exported CSV is the accepted first professional real-motorsport path for the initial vertical slice.

Native `.ld` ingestion is deferred. It may be added later as an optional adapter after licensing, API, platform and maintainability constraints are explicitly reviewed.

The portable OME core must not depend on native `.ld` access.

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

The first version does not attempt partial recovery from structurally corrupted telemetry.

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

## OME CSV implementation traceability

Plan 003 exercises the REQ-001 acceptance criteria for the first supported source through:

`tests/ingestion/test_ome_csv_import.py`

Mapping:

- AC-001 → `test_ac001_supported_profile_import_succeeds`
- AC-002 → `test_ac002_import_does_not_modify_source_files`
- AC-003 → `test_ac003_provenance_identifies_source_and_importer`
- AC-004 → `test_ac004_channel_inventory_preserves_source_identity`
- AC-005 → `test_ac005_source_metadata_is_preserved`
- AC-006 → `test_ac006_missing_metadata_remains_unknown_and_visible`
- AC-007 → `test_ac007_unsupported_source_returns_explicit_failure`
- AC-008 → `test_ac008_unreadable_source_returns_read_failure`
- AC-009 → `test_ac009_import_does_not_normalize_channel_identity_or_values`
- AC-010 → `test_ac010_semantic_import_is_reproducible`

The initial source strategy is now implemented across Plans 003, 007 and 008:

- OME CSV Exchange Profile;
- iRacing `.ibt`;
- MoTeC CSV export.

Native MoTeC `.ld` remains deliberately deferred and is not part of REQ-001 completion.

## iRacing .ibt implementation traceability

Plan 007 exercises REQ-001 against the first external binary adapter through:

`tests/ingestion/test_iracing_ibt_import.py`

The adapter reuses the same source-independent import contract and verifies:

- AC-001 — a supported IRSDK v2 `.ibt` with scalar and fixed-array source variables produces an imported dataset;
- AC-002 — import reads source bytes without modifying the source file;
- AC-003 — source identity, importer identity/version and SHA-256 fingerprint are retained;
- AC-004 — discovered iRacing source variables remain source channels with their original names;
- AC-005 — description, unit, declared type/count and tick rate are preserved when supplied;
- AC-008 — truncated, unsupported-version and missing-explicit-time structures fail explicitly;
- AC-009 — source channel names/units/values are preserved without canonical normalization;
- AC-010 — equivalent source bytes produce equivalent semantic channel content and fingerprint.

The first iRacing slice intentionally requires an explicit `SessionTime` source variable instead of fabricating timestamps from `tickRate`.

Fixed source arrays are preserved as grouped source values. They are not flattened or resampled during ingestion.

When iRacing explicitly marks a variable as a time subdivision through `countAsTime=true`, the importer preserves the grouped value and exposes the source acquisition rate as `tickRate * count`.

### TDD evidence

Behavioral RED:

- OME CI #45 — `IRacingIBTImporter` absent.

GREEN:

- OME CI #47 — canonical verification successful with the minimum importer implementation.

Second RED from real-file evidence:

- OME CI #51 — the scalar importer rejected the real 360 Hz-style `float[6]` source shape.

Second GREEN:

- OME CI #54 — grouped fixed-array source values and explicit 360 Hz metadata passed canonical verification.

## MoTeC CSV implementation traceability

Plan 008 exercises REQ-001 against the first professional-workflow CSV adapter through:

`tests/ingestion/test_motec_csv_import.py`

The adapter verifies:

- AC-001 — a supported MoTeC CSV export produces an imported telemetry dataset;
- AC-002 — source bytes remain unchanged;
- AC-003 — source identity, importer identity/version and SHA-256 fingerprint are retained;
- AC-004 — every discovered source column is exposed and `original_name` remains exact even when technical identifiers need duplicate disambiguation;
- AC-005 — units and explicit Sample Rate metadata are preserved;
- AC-006 — absent Sample Rate remains unknown and visible rather than inferred from time spacing;
- AC-007 — arbitrary CSV remains unsupported;
- AC-008 — structurally invalid MoTeC CSV fails explicitly;
- AC-009 — source cells remain lexical and no channel/unit normalization occurs;
- AC-010 — equivalent source bytes produce reproducible semantic channel content and fingerprint.

The import/validation boundary is also executable: the licensed decreasing-time fixture imports successfully, then the validator reports a blocking `decreasing_timestamp` issue.

### TDD evidence

Behavioral RED:

- OME CI #64 — `MoTeCCSVImporter` absent.

GREEN:

- OME CI #67 — canonical verification successful with the minimum adapter.

## Traqmate Trackvision CSV implementation traceability

Plan 021 extends the implemented REQ-001 ingestion boundary to licensed physical-car Traqmate Trackvision V2 telemetry through:

`tests/ingestion/test_traqmate_trackvision_csv_import.py`

The adapter verifies:

- AC-001 — the supported real Traqmate fixture produces an imported telemetry dataset;
- AC-002 — source bytes remain unchanged;
- AC-003 — source identity, importer identity/version and SHA-256 fingerprint are retained;
- AC-004 — all discovered source columns remain source channels with their exact original names;
- AC-005 — verified units and declared 10 Hz acquisition metadata are preserved;
- AC-006 — absent Sample Rate remains unknown and visible rather than inferred from timestamp spacing;
- AC-007 — arbitrary CSV remains unsupported;
- AC-008 — unsupported version and structurally invalid Traqmate CSV fail explicitly;
- AC-009 — lexical source values remain unnormalized, including mph and source Lap values;
- AC-010 — equivalent source bytes produce equivalent semantic channel content and fingerprint.

The adapter deliberately does not create `lap.distance`, derive distance from GPS, normalize mph, or organize source `Lap` values into canonical context during ingestion.

### TDD evidence

Behavioral RED:

- OME CI #252 — `TraqmateTrackvisionCSVImporter` absent.

GREEN:

- OME CI #255 — canonical verification successful with the minimum adapter;
- OME CI #256 — canonical verification successful with supported-path performance characterization.

### Portland extended Trackvision traceability

Plan 024 extends the same REQ-001 importer contract to a licensed 28-column Portland physical-car source without creating a new ingestion boundary.

Coverage:

- AC-001 — the compact Portland two-lap slice imports successfully;
- AC-002 — source bytes remain unchanged;
- AC-003 — upstream/derived fixture identity and runtime SHA-256 provenance remain explicit;
- AC-004 — all 28 source channels are exposed in source order;
- AC-005 — declared 40 Hz acquisition metadata is preserved;
- AC-009 — GPS, speed, gear, brake, sparse Lap markers and other source cells remain unnormalized;
- AC-010 — equivalent Portland bytes produce reproducible semantic channel content/fingerprint.

Structural header padding is normalized only for source-field identity/recognition; the raw header row remains available in source metadata.

Sparse source Lap markers remain measured source evidence. Import does not infer canonical LapContext or fill missing Lap cells.

TDD evidence:

- OME CI #305 — behavioral RED against the prior first-column/signature assumption;
- OME CI #306 — regression caught an over-broad extended-header rule;
- OME CI #307 — canonical GREEN with Portland and legacy Trackvision coverage.

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

## Resolved decisions

The following decisions are accepted for the first vertical slice:

1. The OME CSV Exchange Profile v0.1 is defined in `docs/specs/ome-csv-profile-v0.1.md`.
2. One source may contain more than one operational context; import preserves source markers while canonical Session / Run / Lap organization remains a separate responsibility.
3. The first version does not attempt partial recovery from structurally corrupted telemetry.
4. Duplicate source content is detected using a stable content fingerprint; filename alone is insufficient.
5. Minimum provenance is defined in `docs/domain/provenance.md`.
6. Generic Session / Run / Lap inference is not an importer responsibility.
7. Imported data progresses to analysis only after separate validation and analysis-readiness checks.
8. The initial architecture must be evaluated against files up to approximately 2 GB, hundreds of channels and multi-hour sessions; these are architecture evaluation targets, not public guarantees.
9. MoTeC CSV export is the accepted first MoTeC path.
10. Native MoTeC `.ld` support is deferred and must not constrain the portable core.

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
