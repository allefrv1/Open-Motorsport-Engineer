# Engineering Council Review — Pure-Slip Tyre Model Foundation

Date: 2026-09-25

Change:

REQ-007 / ADR-0011 / Pure-Slip Tyre Model v0.1

Decision: **READY_WITH_ACTIONS**

## Objective

Introduce a deterministic replaceable tyre-model boundary and a deliberately limited classic Pacejka pure-slip implementation without coupling OME to Pacejka or implying a complete competition-tyre simulator.

## Evidence reviewed

- OME accepted architecture/quality/core-belief documents;
- current MVP scope;
- OME Motorsport Engineering Reference Library;
- Hans Pacejka bibliographic reference in the project library;
- accessible TU Delft and SAE descriptions of the classic Magic Formula equation and its semi-empirical/calibration nature.

## Software / Architecture review

Assessment:

The smallest correct architecture is one explicit analysis-layer protocol plus one implementation.

Pacejka must not become a base class, global singleton, source-adapter concern or telemetry-domain primitive.

The initial model stays independent from ingestion, normalization, API and frontend layers.

Risks:

A premature generalized tyre-simulation framework would create speculative abstractions.

Decision:

READY.

Action:

Keep v0.1 limited to fixed-coefficient pure slip and expose semantic mismatch as an error.

## Motorsport Mechanical Engineering review

Engineering question:

Can the classic Magic Formula be introduced truthfully as a reusable tyre-force primitive?

References consulted:

- Hans B. Pacejka — *Tire and Vehicle Dynamics*, Third Edition (bibliographic reference in OME library);
- accessible TU Delft descriptions of the general Magic Formula;
- SAE vehicle-dynamics literature describing the same general `B/C/D/E` form.

Assessment:

Yes, provided OME is explicit that coefficients must be calibrated to the tyre/operating context and that fixed-coefficient pure slip is not equivalent to a full modern MF-Tyre/MF-Swift tyre model.

The force axis and slip-coordinate convention must travel with the parameter set.

Missing evidence:

- no real competition-tyre calibration set is currently accepted;
- no validated load/camber/temperature/pressure/wear model is currently accepted.

Decision:

READY_WITH_ACTIONS.

Action:

Do not ship a parameter set labeled as representative of a real competition tyre in this change.

## Physics review

Equations / units / assumptions:

The accepted v0.1 evaluator uses:

```text
x = X + Sh
Y = D sin(C atan(Bx - E(Bx - atan(Bx)))) + Sv
```

For this force-only implementation:

- `D` and `Sv` are newtons;
- output `Y` is newtons;
- `B*x` must be dimensionless under the calibration convention;
- `C` and `E` are dimensionless shape/curvature factors.

Assessment:

The equation is deterministic and suitable as a curve evaluator when coordinate/calibration semantics are explicit.

Missing evidence:

No claim should be made about a specific tyre's physical accuracy without fitted/test data.

Decision:

READY_WITH_ACTIONS.

Action:

Tests must verify semantic mismatch rejection, shift semantics, finite inputs and a known analytic value.

## Cross-discipline discussion

Agreements:

- Pacejka is an implementation, not OME's tyre architecture;
- no implicit conversion between `alpha` and `tan(alpha)`;
- no combined slip or environmental state in v0.1;
- no source-format dependency;
- use TDD before production implementation.

Disagreements:

None after narrowing scope to a pure-slip foundation.

Improvement options:

A later requirement may add load/camber-dependent parameter generation or a versioned combined-slip contract after real tyre/test evidence is available.

## Decision

Selected:

**READY_WITH_ACTIONS**

## Kanban transition

The existing product WIP slot remains Plan 030.

This maintainer-authorized architecture foundation does not replace the active Traqmate workflow and is not wired into the MVP pipeline.

## Actions

- [ ] Add behavioral tests before production implementation.
- [ ] Prove expected RED in PR CI.
- [ ] Implement the minimum deterministic evaluator.
- [ ] Run canonical verification through PR CI.
- [ ] Record implementation limitation/provenance explicitly.

## Human gate

Required:

Yes, because the accepted MVP previously listed tyre models out of scope.

CEO / Maintainer decision:

Approved by the explicit 2026-09-25 request to make the project changes necessary for the Pacejka-capable tyre-model architecture.
