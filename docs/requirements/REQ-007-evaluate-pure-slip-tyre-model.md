# REQ-007 — Evaluate a Deterministic Pure-Slip Tyre Model

Status: **Accepted**

## Actor / User

An engineer, student or future OME analysis module that needs deterministic tyre-force evaluation from an explicitly calibrated pure-slip model.

## Problem

Tyre analysis requires deterministic force models, but coupling the engineering core directly to one specific tyre model would make later calibration/model changes invasive and could hide material modelling assumptions.

## Goal

Provide a small source-independent tyre-model contract and an initial Pacejka / Magic Formula implementation without making Pacejka the architecture of OME.

## Acceptance Criteria

OME shall provide a deterministic `TireModel` contract for pure-slip force evaluation.

The initial Pacejka implementation shall:

- implement the classic Magic Formula curve with explicit `B`, `C`, `D`, `E`, horizontal-shift and vertical-shift parameters;
- support pure longitudinal-force and pure lateral-force parameter sets;
- require the parameter set to declare the force axis it represents;
- require the parameter set to declare the slip-coordinate convention it was calibrated against;
- reject evaluation when request semantics do not match the calibrated parameter semantics;
- reject non-finite coefficients and non-finite requested slip coordinates;
- identify the deterministic algorithm/version in the returned result;
- produce equivalent results for equivalent inputs and parameters;
- introduce no network/runtime service dependency.

The initial contract shall not claim support for:

- combined longitudinal/lateral slip;
- load-sensitive coefficient generation;
- camber-sensitive coefficient generation;
- temperature;
- pressure;
- wear/degradation;
- transient tyre dynamics;
- aligning moment;
- automatic tyre-parameter fitting;
- setup recommendations.

## Evidence / traceability

A result must retain enough information to identify:

- requested force axis;
- requested slip-coordinate convention;
- requested slip value;
- effective shifted slip value;
- deterministic model identity/version;
- calculated force in newtons.

Calibration provenance remains the responsibility of the future caller that owns a concrete parameter set.

## TDD mapping

Executable acceptance coverage belongs in:

`tests/analysis/test_tire_model.py`

Production implementation belongs in the deterministic analysis layer and must not depend on API, ingestion, AI or source-format packages.

## Related decisions

- ADR-0003 — AI is not the deterministic engineering core.
- ADR-0005 — Use Python for the initial engineering core.
- ADR-0011 — Keep tyre models replaceable behind an explicit deterministic contract.
