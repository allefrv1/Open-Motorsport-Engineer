# Brake Semantic Compatibility Specification v0.1

Status: **Accepted for Plan 012**

Date: 2026-09-22

## Purpose

Define the minimum machine-readable semantic contract needed to compare continuous driver-brake evidence without equating non-equivalent signals.

## Canonical concept

Concept:

`driver.brake`

The canonical concept alone is insufficient for comparison because multiple physical/source meanings exist.

## Semantic identity

Canonical evidence may carry:

`semantic_id: string | null`

For Plan 012, brake comparison requires a non-empty semantic id.

Initial supported continuous brake semantics:

### Pedal position ratio

```text
driver.brake.pedal_position_ratio
```

Canonical unit:

`1`

Meaning:

Normalized driver brake-pedal position from released to maximum position.

### Pedal force ratio

```text
driver.brake.pedal_force_ratio
```

Canonical unit:

`1`

Meaning:

Normalized driver brake-force demand from released to declared maximum force.

## Compatibility rule

A brake overlay is ready only when:

- both sides are canonical `driver.brake`;
- both sides have a supported non-empty `semantic_id`;
- the semantic ids are exactly equal;
- both sides use canonical unit `1`;
- ordinary continuous-overlay readiness also passes.

No fuzzy matching is allowed.

## Explicitly unsupported in v0.1

Examples:

- physical pedal force in N;
- master-cylinder pressure;
- brake-line pressure;
- front/rear circuit pressure;
- binary brake state;
- ABS intervention/reduction;
- unknown or missing brake semantics.

Unsupported semantics return explicit not-ready evidence.

## Normalization contract

`NormalizationRule` may declare an optional `semantic_id`.

`NormalizationMapping` must preserve it.

For brake rules intended for comparison, the semantic id is required by the analysis layer.

The normalization rule remains responsible for:

- verifying source name/unit expectations;
- converting to canonical unit;
- declaring the semantic identity truthfully.

## Evidence contract

`CanonicalSeriesEvidence` may carry the same optional `semantic_id`.

Comparison provenance therefore retains:

- original dataset;
- source channel;
- source name;
- transformations;
- canonical concept;
- canonical unit;
- semantic id.

## Continuous overlay behavior

The existing continuous overlay algorithm is extended for `driver.brake` only when the semantic compatibility rule passes.

Interpolation remains:

- linear in elapsed time;
- onto the existing base comparison distance grid;
- non-extrapolating.

Algorithm identity remains:

`ome.lap-overlay.time-linear-on-distance-grid / 0.1.0`

The numerical algorithm does not change; only the compatibility gate is extended.

## Missing/incompatible semantics

Initial readiness issue families:

- missing brake semantic id;
- incompatible brake semantic ids;
- unsupported brake semantic id;
- incompatible brake unit.

The base delta comparison remains valid even when a brake overlay is not ready.

## Interpretation boundary

A successful brake overlay may expose aligned brake values.

It does not claim:

- later/earlier braking as an automatic observation yet;
- causation;
- braking quality;
- setup recommendation;
- brake-system diagnosis.

Those belong to later deterministic observation/domain modules.

## Related artifacts

- REQ-004 — Normalize Telemetry Semantics
- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
- `docs/domain/canonical-channels-v0.1.md`
- `docs/specs/lap-continuous-overlay-v0.1.md`
- `docs/research/brake-signal-semantics.md`
