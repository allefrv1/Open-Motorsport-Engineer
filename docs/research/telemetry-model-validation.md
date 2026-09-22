# Telemetry Model Validation Against Public Data

Status: **Reviewed architecture validation**

Verified: **2026-09-22**

## Purpose

Challenge OME's pre-code telemetry model using actual public telemetry rather than idealized examples.

Sources inspected:

1. iRacing `.ibt` public test binary;
2. CR Formula real Formula SAE CSV;
3. exit_speed Traqmate CSV;
4. TRACE MoTeC-style CSV fixtures.

## Result

The current architecture survives this review, but several points became materially better grounded.

No major domain boundary needs to be reversed.

## Validation 1 — Import success is not data-quality success

### Evidence

The CR Formula Autocross CSV is structurally readable and contains thousands of samples.

However:

- GPS latitude is present as a column but all-zero in the inspected file;
- longitude is all-zero;
- speed is all-zero;
- RPM, TPS and oil-pressure data are populated;
- recorded timestamp cadence includes a multi-second gap;
- a sample-rate-like label conflicts with timestamp cadence.

### Architectural implication

The accepted separation remains correct:

```text
IMPORT
!= VALIDATION
!= ANALYSIS READINESS
```

A parser saying "I read the CSV" is not sufficient evidence that lap analysis can proceed.

REQ-002 and `docs/domain/data-quality.md` are strengthened by real data evidence.

## Validation 2 — Readiness must be analysis-specific

### Evidence

The same Formula SAE file contains usable engine/input channels while its position/speed evidence is unavailable in practice.

### Architectural implication

The dataset could potentially support some engine/driver-input investigation while being unsuitable for lap-distance comparison.

OME should continue to evaluate:

```text
validated dataset
+ analysis requirements
= analysis readiness
```

rather than a single universal valid/invalid flag.

## Validation 3 — Source semantics must survive normalization

### Evidence

The inspected iRacing binary exposes:

- source channel name: `Speed`;
- unit: `m/s`;
- description: GPS vehicle speed.

It separately exposes many other vehicle channels.

### Architectural implication

Mapping that signal into a canonical speed concept must not erase that it originated as iRacing GPS speed.

OME's distinction between:

```text
SourceChannel
-> explicit mapping
-> CanonicalConcept
```

is validated.

## Validation 4 — Rich metadata belongs outside a flat sample table

### Evidence

The iRacing binary contains:

- telemetry header;
- disk/session header;
- hundreds of variable definitions;
- variable descriptions and units;
- embedded session information;
- track/event/session metadata.

The Traqmate CSV also contains a metadata preamble before sample rows.

### Architectural implication

A single bare table of numeric columns is insufficient as OME's entire telemetry domain.

The accepted TelemetrySource / ImportedTelemetryDataset / SourceChannel / ChannelMetadata / Provenance split remains justified.

## Validation 5 — CSV is not one format

### Evidence

Three inspected CSV families differ substantially:

### CR Formula

- one header row;
- units embedded into column labels;
- no rich metadata preamble.

### Traqmate

- metadata key/value preamble;
- then sample header;
- units embedded into labels.

### MoTeC-style fixture

- metadata preamble;
- channel-name row;
- separate unit row.

### Architectural implication

"CSV importer" should not mean "one universal parser for every motorsport CSV."

OME should support:

- project-owned OME CSV Profile;
- source-specific CSV adapters/profiles;
- later generic CSV mapping workflow if required.

## Validation 6 — Session/Lap context varies by source

### Evidence

iRacing provides:

- embedded session metadata;
- `Lap`;
- `LapDist`;
- `LapDistPct`;
- lap-time channels.

Traqmate fixture provides an explicit `Lap` column.

The inspected CR Formula file provides no trustworthy lap-position channel and its GPS/speed fields are empty.

### Architectural implication

Importers may preserve source-provided boundaries, but generic lap inference must remain outside raw parsing.

REQ-003 is consistent with observed source diversity.

## Validation 7 — Timestamp evidence is more trustworthy than labels alone

### Evidence

The CR Formula file demonstrates that a source label suggesting a sampling rate may disagree with observed timestamp cadence.

### Architectural implication

OME validation should compare declared acquisition metadata with observed timing where both exist.

A mismatch should produce an explicit issue rather than choosing one silently.

This should later become an executable validation rule after representative tolerance policies are defined.

## Validation 8 — Our OME CSV Profile remains intentionally limited

The public datasets do not justify changing the v0.1 OME CSV Profile into a universal storage format.

Its single-time-base constraint remains appropriate for:

- deterministic fixtures;
- basic interchange;
- examples.

Richer sources should enter through their own adapters and the source-independent telemetry model.

## Findings that should become future checks

When implementation begins, prioritize executable checks for:

1. declared vs observed cadence mismatch;
2. non-monotonic/decreasing timestamps;
3. large timestamp gaps;
4. present-but-constant channels;
5. missing/unknown units;
6. required channel readiness per analysis;
7. preservation of original channel name/unit/description;
8. source-provided lap marker preservation.

## Open evidence gaps

The architecture still needs validation against:

- a legally redistributable full iRacing session if permitted;
- a clearly licensed real MoTeC-exported CSV from a physical race car;
- a clearly licensed Brazilian Formula SAE full vehicle session;
- genuinely multi-rate physical-car acquisition;
- larger datasets near the initial performance envelope.

These are evidence gaps, not reasons to invent architecture now.

## Conclusion

The most important outcome of this review is not that the existing design was "right."

It is that real imperfect data supports the need for OME's strongest boundaries:

```text
preserve source
-> import
-> validate
-> normalize explicitly
-> evaluate analysis readiness
-> calculate deterministically
-> expose evidence
```

The public Formula SAE data also demonstrates why OME must be comfortable saying:

> This dataset contains useful data, but not enough trustworthy evidence for this analysis.
