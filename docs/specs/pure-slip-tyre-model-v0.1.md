# Pure-Slip Tyre Model Specification v0.1

Status: **Accepted**

Date: 2026-09-25

## Purpose

Define the smallest deterministic tyre-model boundary required for the first OME tyre-model foundation.

This is a numerical model specification, not a claim that any bundled parameter set represents a specific real tyre.

## Model family

Initial implementation:

`pacejka.magic_formula.classic.v0.1`

General curve:

```text
x = X + Sh

Y = D * sin(
    C * atan(
        B*x - E*(B*x - atan(B*x))
    )
) + Sv
```

Where:

- `X` is the requested calibrated slip coordinate;
- `x` is the shifted effective slip coordinate;
- `B` is the stiffness factor;
- `C` is the shape factor;
- `D` is the peak factor expressed in newtons for this force-only implementation;
- `E` is the curvature factor;
- `Sh` is the horizontal shift in the same coordinate convention as `X`;
- `Sv` is the vertical force shift in newtons;
- `Y` is tyre force in newtons.

## Force axes

v0.1 supports only:

- `longitudinal`;
- `lateral`.

It does not support aligning moment.

## Slip-coordinate conventions

The model does not silently transform slip coordinates.

A calibration declares exactly one coordinate convention:

- `longitudinal_slip_ratio` — dimensionless longitudinal slip ratio;
- `lateral_slip_angle_rad` — lateral slip angle in radians used directly as the calibrated Magic Formula coordinate;
- `lateral_tan_slip_angle` — tangent of lateral slip angle used as the calibrated Magic Formula coordinate.

The evaluation request must use the exact same declared convention.

This distinction is deliberate because published simplified Magic Formula presentations differ in whether lateral calibration is expressed directly in slip angle or using `tan(alpha)`.

## Determinism

Equivalent finite inputs and parameters produce equivalent output.

The evaluator performs no:

- fitting;
- interpolation table lookup;
- telemetry repair;
- resampling;
- network access;
- randomization.

## Validation

All numerical coefficients and requested slip coordinates must be finite.

A request is invalid when:

- requested force axis differs from the parameter-set axis;
- requested slip-coordinate convention differs from the parameter-set convention;
- any coefficient is NaN or infinite;
- requested slip is NaN or infinite.

The implementation must fail explicitly rather than reinterpret the request.

## Output

The deterministic result contains:

- force axis;
- slip-coordinate convention;
- input slip;
- effective shifted slip;
- force in newtons;
- model identity/version.

## Explicit limitations

v0.1 uses fixed coefficients.

It does not model coefficient variation with:

- vertical load;
- camber;
- inflation pressure;
- tyre temperature;
- carcass/tread temperature state;
- wear;
- velocity.

It does not model:

- combined slip;
- relaxation/transient response;
- aligning moment;
- enveloping/contact-patch dynamics.

These capabilities require later requirements and model versions.

## Engineering references

Primary bibliographic reference:

- Hans B. Pacejka, *Tire and Vehicle Dynamics*, Third Edition, Elsevier, 2012. See the OME Motorsport Engineering Reference Library.

Accessible equation cross-checks used for this specification:

- TU Delft repository material describing the Magic Formula as a semi-empirical model and the general `B/C/D/E` form;
- SAE vehicle-dynamics literature describing the same general form for longitudinal/lateral force and aligning moment.

OME does not copy proprietary calibration data.

## Related artifacts

- REQ-007
- ADR-0011
- `docs/references/motorsport-engineering-library.md`
