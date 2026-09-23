# Plan 012 — Brake Semantic Compatibility

Status: **Active**

Started: 2026-09-22

## Objective

Make brake comparison mechanically safe by carrying explicit semantic identity through normalization/evidence and enabling continuous brake overlays only for exactly compatible supported semantics.

## Requirements

Primary:

- REQ-004 — Normalize Telemetry Semantics
- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence

Authoritative contract:

- `docs/specs/brake-semantic-compatibility-v0.1.md`

Supporting research:

- `docs/research/brake-signal-semantics.md`

## Scope

Plan 012 adds:

- optional `semantic_id` to normalization rules/mappings;
- optional `semantic_id` to canonical series evidence;
- propagation of semantic identity through normalization;
- continuous brake overlay for:
  - `driver.brake.pedal_position_ratio [1]`;
  - `driver.brake.pedal_force_ratio [1]`;
- exact semantic match requirement between Lap A and Lap B;
- explicit missing/incompatible/unsupported semantic issues.

## Safety boundary

The following remain unsupported by this first brake overlay:

- physical pedal force;
- hydraulic pressure;
- front/rear pressure distinctions;
- binary brake state;
- ABS intervention;
- unknown brake semantics.

OME must not convert one brake semantic into another in the analysis layer.

## TDD rule

Production behavior is test-first.

Required sequence:

```text
BRAKE SEMANTIC SPEC
-> NORMALIZATION/EVIDENCE TESTS
-> OVERLAY TESTS
-> VALID RED
-> MINIMUM SEMANTIC PROPAGATION + COMPATIBILITY IMPLEMENTATION
-> GREEN
-> FULL VERIFY
```

## First executable test targets

Tests should prove:

- normalization rule semantic id is preserved in mapping;
- canonical series evidence can retain semantic id;
- matching pedal-position ratios can be overlaid;
- matching pedal-force ratios can be overlaid;
- pedal-position vs pedal-force is not-ready;
- missing semantic id is not-ready;
- unsupported pressure semantic is not-ready;
- incompatible brake unit is not-ready;
- brake provenance retains semantic ids;
- gear remains unsupported by continuous overlay;
- no causal diagnosis is emitted.

## Architecture boundary

Plan 012 may evolve normalization/evidence contracts and the continuous overlay compatibility gate.

It must not:

- guess semantic identity from a source name;
- infer pressure/position equivalence;
- convert pressure to pedal demand;
- add braking diagnosis;
- mutate source telemetry;
- use AI.

## TDD execution evidence

Behavioral RED:

- OME CI #117;
- expected failures:
  - `NormalizationRule.__init__()` did not accept `semantic_id`;
  - `CanonicalSeriesEvidence.__init__()` did not accept `semantic_id`.

This demonstrated the missing semantic contract directly.

GREEN:

- OME CI #121;
- complete canonical verification passed after the minimum semantic propagation and compatibility gate.

Tests were not weakened to obtain GREEN.

## Implementation traceability

Normalization test:

`tests/normalization/test_normalization.py::Req004TelemetryNormalizationTests.test_plan012_brake_semantic_id_is_preserved_from_rule_to_mapping`

Analysis test class:

`tests/analysis/test_continuous_overlay.py::Plan012BrakeSemanticCompatibilityTests`

The executable contract now proves:

- rule -> mapping semantic-id propagation;
- canonical evidence semantic-id retention;
- exact-match pedal-position ratio overlay;
- exact-match pedal-force ratio overlay;
- position/force incompatibility;
- missing semantic rejection;
- unsupported pressure-semantic rejection;
- unit compatibility;
- provenance retention;
- gear remains outside continuous interpolation;
- no causal diagnosis.

## Completion criteria

- semantic compatibility spec accepted;
- tests written before behavior;
- valid behavioral RED recorded;
- semantic id propagation GREEN;
- safe brake overlay GREEN;
- incompatible semantics explicit;
- provenance retains semantic id;
- canonical CI GREEN;
- REQ-004/005/006 traceability updated.

## Explicitly out of scope

- brake pressure analysis;
- braking-point observations;
- threshold/brake-onset algorithms;
- corner segmentation;
- causal diagnosis;
- UI;
- AI.
