# ADR-0011 — Keep tyre models replaceable behind a deterministic contract

Status: **Accepted**

Date: 2026-09-25

## Context

OME's long-term scope includes tyre analysis and vehicle-dynamics analysis. Pacejka / Magic Formula is a useful and widely established tyre-model family, but OME must not make one model family the definition of the engineering domain.

The current first vertical slice explicitly excludes a user-facing tyre-analysis workflow. The maintainer has authorized a narrowly isolated tyre-model foundation so later domain analysis can build on deterministic, testable primitives without changing the current comparison workflow.

## Decision

OME will expose a small deterministic `TireModel` contract in the analysis layer.

The first implementation will be a classic pure-slip Pacejka / Magic Formula evaluator.

The parameter set must carry both:

- force-axis semantics (longitudinal or lateral);
- slip-coordinate semantics used by the calibration.

The implementation must reject semantic mismatches rather than silently reinterpret coefficients.

The initial implementation is intentionally limited to fixed-coefficient pure-slip force evaluation. Load/camber/temperature/pressure/wear/transient/combined-slip behaviour requires later explicit requirements/specifications rather than hidden extensions.

Pacejka is therefore one strategy behind the contract, not the core architecture.

## Alternatives considered

### Hard-code Pacejka directly into future tyre-analysis workflows

Rejected because it couples callers to one model family and makes later model/calibration changes invasive.

### Build a complete MF-Tyre/MF-Swift style framework now

Rejected because it exceeds available requirements/evidence and would violate the smallest-correct-system principle.

### Defer all tyre-model code until the complete Phase 7 tyre workflow

Not selected because the maintainer explicitly requested the reusable modelling foundation now.

## Consequences

Positive:

- deterministic tyre calculations remain swappable;
- model assumptions become explicit and testable;
- callers cannot silently use a lateral calibration as a longitudinal calibration;
- no telemetry-source format leaks into tyre-model semantics;
- future simple/brush/advanced models can implement the same boundary or a deliberately versioned successor.

Costs:

- callers must provide calibrated coefficients and explicit coordinate semantics;
- the initial model is not a complete tyre simulator;
- later combined-slip/load/camber capability may require a broader versioned contract.

## Risks

The largest risk is false confidence from using arbitrary or unvalidated coefficients.

Mitigation:

- no built-in claim that generic coefficients represent a real competition tyre;
- coefficient provenance/calibration must remain explicit at the caller;
- advanced physical effects remain out of scope until separately specified.

## Reversibility

High.

The boundary is intentionally small and internal to the deterministic analysis layer. A later contract version can coexist with or supersede this pure-slip interface.

## Related requirements

- REQ-007
