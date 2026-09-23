# Plan 012 — Brake Semantic Compatibility

Status: **Completed**

Started: 2026-09-22

Completed: 2026-09-22

## Objective

Make brake comparison mechanically safe by carrying explicit semantic identity through normalization/evidence and enabling continuous brake overlays only for exactly compatible supported semantics.

## Delivered

- optional `semantic_id` in normalization rules and mappings;
- optional `semantic_id` in canonical-series evidence;
- deterministic rule -> mapping semantic propagation;
- continuous brake overlay support for:
  - `driver.brake.pedal_position_ratio [1]`;
  - `driver.brake.pedal_force_ratio [1]`;
- exact semantic-id match requirement between Lap A and Lap B;
- explicit not-ready evidence for:
  - missing brake semantic id;
  - incompatible supported semantic ids;
  - unsupported brake semantics;
  - incompatible canonical unit;
- brake semantic identity retained in overlay provenance;
- no change to the numerical interpolation algorithm;
- no pressure/position/force conversion inside analysis.

## TDD evidence

Behavioral RED:

- OME CI #117;
- expected failures:
  - `NormalizationRule` did not accept `semantic_id`;
  - `CanonicalSeriesEvidence` did not accept `semantic_id`.

GREEN:

- OME CI #121 — canonical verify passed after minimum semantic propagation and compatibility implementation.

Final documentation/traceability verification:

- OME CI #123 — success.

Tests were not weakened to obtain GREEN.

## Executable traceability

Normalization:

`tests/normalization/test_normalization.py::Req004TelemetryNormalizationTests.test_plan012_brake_semantic_id_is_preserved_from_rule_to_mapping`

Analysis:

`tests/analysis/test_continuous_overlay.py::Plan012BrakeSemanticCompatibilityTests`

Coverage proves:

- semantic propagation;
- canonical evidence identity;
- matching pedal-position comparison;
- matching pedal-force comparison;
- position/force incompatibility;
- missing semantic rejection;
- unsupported pressure rejection;
- canonical unit requirement;
- provenance retention;
- gear remains outside continuous interpolation;
- no causal diagnosis.

## Boundaries preserved

Not added:

- physical brake-force comparison;
- hydraulic-pressure comparison;
- pressure-to-demand conversion;
- brake-onset observations;
- braking-point detection;
- corner segmentation;
- causal diagnosis;
- UI;
- AI.

## Merge evidence

PR #31 was squash-merged as:

`e8729b0c23d5b35c8dae3aabe6229b5e4f44786b`

## Completion assessment

All Plan 012 completion criteria are satisfied.
