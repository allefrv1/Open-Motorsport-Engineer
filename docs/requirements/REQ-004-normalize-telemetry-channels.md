# REQ-004 — Normalize Telemetry Channels

Status: **Accepted**

## Actor / User

A user or analysis workflow that needs source-independent engineering concepts while preserving the original source representation.

## Problem

Different telemetry systems use different names, units and acquisition conventions for related physical quantities.

Analysis cannot depend on vendor-specific channel names, but blindly renaming channels destroys provenance and can create false equivalence.

## Goal

Map SourceChannels to canonical OME engineering concepts through explicit, traceable normalization rules.

## Main Flow

1. OME receives a validated SourceChannel.
2. A normalization rule identifies a candidate canonical concept.
3. OME verifies the information required by that rule.
4. OME creates a traceable mapping.
5. Original source identity remains preserved.
6. Any unit conversion or transformation is explicit and versioned.

## Acceptance Criteria

### AC-001 — Preserve source identity

Normalization must not overwrite original source channel name, identifier, unit or provenance.

### AC-002 — Explicit mapping

A canonical concept must be linked through an explicit mapping rule.

### AC-003 — Ambiguity

If the source signal cannot be mapped safely, it must remain unmapped rather than guessed.

### AC-004 — Conversions

Unit conversion must be deterministic, traceable and recorded separately from source measurement identity.

### AC-005 — Similar signals remain distinct

Signals such as GPS speed, wheel speed and ECU vehicle speed must not be collapsed automatically solely because they represent related speed concepts.

### AC-006 — Versioned rules

Normalization behavior that affects engineering meaning must be versionable.

## Out of Scope

- resampling onto a common timeline;
- analysis-specific derived metrics;
- AI-based free-form channel guessing as an authoritative mapping.
