# ADR-0001 — Separate source ingestion from telemetry normalization

Status: **Accepted**

Date: 2026-09-22

## Context

OME intends to support heterogeneous telemetry sources such as project-controlled CSV, iRacing `.ibt`, MoTeC data and additional motorsport/automotive exports.

These sources differ in:

- channel names;
- metadata;
- units;
- sample rates;
- time bases;
- source semantics;
- file structures.

If a source adapter immediately converts every signal into OME canonical concepts, source parsing and engineering interpretation become coupled.

That coupling would make provenance harder to preserve and could cause incorrect mappings to appear as measured facts.

## Decision

Separate:

1. **source ingestion**, whose responsibility is to read and preserve what the source contains;
2. **validation**, whose responsibility is to assess the reliability and completeness of imported evidence;
3. **normalization**, whose responsibility is to map source representation to OME canonical engineering concepts.

Conceptually:

```text
SOURCE
  -> INGESTION
  -> IMPORTED SOURCE REPRESENTATION
  -> VALIDATION
  -> NORMALIZATION
  -> CANONICAL ENGINEERING DATA
```

Source adapters must preserve original channel identity and provenance.

Normalization may add canonical mappings but must not erase the original source representation.

## Alternatives considered

### A. Normalize directly inside every importer

Advantages:

- fewer conceptual stages;
- faster prototype for one source.

Disadvantages:

- importer-specific engineering rules;
- inconsistent mappings across sources;
- harder auditing;
- higher risk of losing original meaning;
- difficult correction of normalization rules later.

### B. Use CSV as the canonical internal model

Advantages:

- simple tooling;
- easy human inspection.

Disadvantages:

- poor fit for multiple sample rates/time bases;
- encourages flattening/resampling;
- weak representation of metadata and provenance;
- risks confusing exchange format with domain model.

### C. Keep raw source only and normalize on demand without an imported model

Advantages:

- maximal source preservation.

Disadvantages:

- every downstream feature must understand source-specific formats;
- repeated parsing;
- source-specific logic leaks throughout the system.

## Consequences

If accepted:

- import adapters can evolve independently from normalization rules;
- source identity becomes auditable;
- different source formats can converge on a stable ingestion contract;
- normalization errors can be corrected without pretending the source data changed;
- the system has more explicit stages and therefore slightly more conceptual complexity.

## Risks

- over-modeling the ingestion boundary before real datasets are tested;
- introducing unnecessary abstraction if the first model is too generic;
- unclear ownership between validation and normalization unless later requirements are precise.

## Reversibility

Moderate.

The conceptual separation is easier to preserve from the start than to retrofit after importers and engineering logic become tightly coupled.

## Related requirements

- REQ-001 — Import Telemetry Session
- REQ-002 — Validate Telemetry Dataset
- REQ-004 — Normalize Telemetry Channels

## Acceptance rationale

The project now has an accepted Telemetry Import Model, explicit validation and normalization requirements, a controlled CSV profile, and reviewed source feasibility for iRacing and MoTeC workflows. The separation is therefore justified by concrete source diversity and evidence-preservation needs rather than by speculative abstraction.
