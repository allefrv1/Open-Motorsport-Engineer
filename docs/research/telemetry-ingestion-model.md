# Telemetry Ingestion Model — Research Notes

Status: **Research / not yet a project rule**

## Purpose

This document records the engineering observations that should inform OME's telemetry ingestion design before implementation.

The goal is not to choose a programming language, library or storage engine. The goal is to understand what real motorsport and automotive telemetry sources require from the ingestion boundary.

## Sources considered

Initial source families selected for OME:

- OME-controlled CSV fixtures/profile;
- iRacing binary telemetry (`.ibt`);
- MoTeC log data (`.ld`) or MoTeC-exported CSV as an interim path;
- generic engineering CSV exports as a broader interoperability case.

Relevant industry references and tools studied during project research include:

- MoTeC i2 / i2 Pro;
- AiM RaceStudio;
- Racelogic VBOX;
- FuelTech datalogging workflows;
- Vector CANape;
- ASAM MDF.

## Observation 1 — CSV is an exchange format, not a universal telemetry model

CSV is widely used to export or exchange engineering data, but there is no single universal automotive CSV schema.

Different tools may place:

- metadata before the tabular data;
- units in a separate row;
- channel names in one or more header rows;
- timestamps in different units;
- one common sample rate or multiple effective sample rates;
- absent values, repeated values or resampled values.

Therefore OME should not assume that an arbitrary CSV is already normalized telemetry.

## Observation 2 — source identity must be preserved

A signal such as:

- GPS Speed;
- ECU Vehicle Speed;
- Wheel Speed;
- Calculated Ground Speed;

may relate to the same broad physical concept but should not be treated as identical automatically.

OME needs to preserve the original source channel before any canonical mapping.

## Observation 3 — multiple sample rates are normal

Real acquisition systems often combine channels captured at different rates.

Examples can include:

- high-rate pressure or suspension signals;
- medium-rate GPS or chassis signals;
- low-rate temperatures or health channels.

Flattening all channels onto one timeline can require interpolation, hold-last-value behavior, gaps or resampling.

Those operations are transformations and must not happen silently during import.

## Observation 4 — metadata is part of engineering evidence

Useful telemetry context can include:

- source system;
- original file identity;
- vehicle;
- driver;
- venue/track;
- session information;
- acquisition rate;
- channel units;
- comments;
- logger configuration;
- date/time;
- calibration/conversion information.

The exact metadata available varies by source.

Missing metadata must remain missing rather than being invented.

## Observation 5 — source formats should not define OME's domain

CSV, iRacing and MoTeC have different representations.

OME should ingest each through source-specific knowledge, then expose a source-independent import boundary.

The engineering domain should not contain concepts such as "iRacing channel" or "MoTeC row" unless provenance specifically requires them.

## Observation 6 — import and normalization are different responsibilities

Import answers:

> What did this source actually contain?

Normalization answers:

> Which OME engineering concept, if any, does this source signal represent?

These steps must remain separable.

## Observation 7 — validation is also separate

Successfully reading a source does not mean its data is trustworthy.

A later validation stage may need to detect:

- missing channels;
- NaN values;
- frozen sensors;
- clipping;
- impossible ranges;
- time gaps;
- duplicated timestamps;
- unexpected sample rates;
- synchronization problems;
- suspicious units.

Therefore:

```text
READABLE
!= VALID
!= NORMALIZED
!= READY FOR ANALYSIS
```

## Observation 8 — proprietary formats require feasibility review

Native MoTeC `.ld` support may involve licensing, API, platform and maintainability constraints.

OME should not make the entire architecture depend on native `.ld` access before those constraints are understood.

MoTeC-exported CSV remains a useful real-world validation source even if native `.ld` support is delayed.

## Architectural implications inferred from this research

These are **project inferences**, not external facts:

1. OME needs a stable import contract independent of source formats.
2. Raw/source representation and normalized representation should be distinguishable.
3. Provenance must be a first-class concept.
4. Source channels must retain original identity.
5. Multiple sample rates must be representable without forced resampling.
6. Missing metadata must be explicit.
7. Validation must occur after successful ingestion.
8. Normalization must occur after or alongside validation, not silently inside source parsing.
9. CSV should be supported as an exchange/fixture format, not assumed to be the canonical internal model.
10. Native proprietary-format adapters should be optional capabilities, not foundational domain dependencies.

## Questions still requiring validation

- minimum provenance fields required for every source;
- whether imported samples are represented per-channel or by grouped time bases;
- how file fingerprinting should work;
- how duplicate imports are recognized;
- when Session / Run / Lap organization occurs;
- what minimum metadata is required to progress to validation;
- expected dataset sizes and performance targets;
- legal and technical constraints of native MoTeC support;
- exact OME CSV exchange/profile design.

## Recommendation

Before implementation, define a source-independent Telemetry Import Model with explicit concepts for:

- TelemetrySource;
- ImportedTelemetryDataset;
- SourceChannel;
- SampleSeries;
- ChannelMetadata;
- Provenance;
- ImportWarning / ImportIssue.

That model should be reviewed before selecting concrete storage or framework technology.
