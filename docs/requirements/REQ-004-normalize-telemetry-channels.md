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

## Foundation implementation traceability

Plan 005 maps the foundational REQ-004 behavior to:

`tests/normalization/test_normalization.py`

Mapping:

- AC-001 → `test_ac001_source_identity_and_values_are_preserved`
- AC-002 → `test_ac002_mapping_is_linked_to_explicit_rule`
- AC-003 → `test_ac003_unmatched_channel_remains_explicitly_unmapped`
- AC-004 → `test_ac004_conversions_are_deterministic_and_traceable`
- AC-005 → `test_ac005_similar_speed_sources_are_not_collapsed`
- AC-006 → `test_ac006_rules_and_conversions_are_versioned_and_reproducible`

Additional regression coverage verifies:

- blocking validation evidence prevents mapping;
- rule precondition mismatch does not trigger guessing;
- multiple matching explicit rules are treated as ambiguous;
- conversion failure leaves source evidence unchanged and unmapped;
- validation evidence must belong to the dataset being normalized;
- import → validate → normalize preserves source timestamps.

The first implementation intentionally uses explicit caller-supplied rules rather than global channel-name inference.

## Brake semantic identity traceability

Plan 012 extends the explicit mapping contract with optional machine-readable `semantic_id`.

The brake rule-to-mapping path is exercised by:

`tests/normalization/test_normalization.py::Req004TelemetryNormalizationTests.test_plan012_brake_semantic_id_is_preserved_from_rule_to_mapping`

For brake comparison, semantic identity is declared by the explicit normalization rule and preserved in `NormalizationMapping`.

OME does not derive brake semantic identity from a source channel name alone.

TDD evidence:

- RED: OME CI #117 — `NormalizationRule` / `CanonicalSeriesEvidence` did not yet support `semantic_id`;
- GREEN: OME CI #121 — semantic propagation and brake compatibility passed canonical verification.

## Out of Scope

- resampling onto a common timeline;
- analysis-specific derived metrics;
- AI-based free-form channel guessing as an authoritative mapping.
