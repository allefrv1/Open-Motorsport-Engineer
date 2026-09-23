# Plan 011 — Discrete Gear Overlay

Status: **Active**

Started: 2026-09-22

## Objective

Add deterministic comparison of canonical `transmission.gear` on the existing lap-comparison distance grid without treating gear as a continuous numeric signal.

The result should answer:

> Which canonical gear state was each lap in at the same place on track?

It must not infer whether a gear choice was correct or causal.

## Requirements

Primary:

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence

Authoritative contracts:

- ADR-0009;
- `docs/specs/lap-comparison-v0.1.md`;
- `docs/specs/lap-discrete-gear-overlay-v0.1.md`;
- `docs/domain/canonical-channels-v0.1.md`.

## Scope

v0.1 supports only:

- canonical concept `transmission.gear`;
- unitless canonical integer gear state;
- deterministic previous-sample hold in elapsed time;
- projection onto the exact existing base comparison distance grid.

## Why a discrete algorithm

Gear is a state, not a continuous physical quantity.

Linear interpolation could produce impossible states such as:

```text
3 -> 4
interpolated value = 3.5
```

Therefore Plan 011 uses a discrete sampling rule.

## Sampling rule

For each target elapsed time `t(d)` from the successful base comparison:

- choose the latest gear sample whose timestamp is less than or equal to `t(d)`;
- when `t(d)` exactly equals a gear sample timestamp, use that sample;
- never interpolate between gear states.

This is a deterministic previous-sample / zero-order-hold rule.

## Coverage boundary

The gear series must explicitly cover the full requested time range.

OME does not extend the final known gear state beyond the final gear sample timestamp.

If the base comparison needs a target time outside the gear series range, return not-ready.

## Canonical value boundary

The first slice accepts integer canonical gear states only.

- booleans are not integers for this contract;
- floats are not accepted, even when numerically integral;
- source-specific meanings for reverse/neutral/unknown must already have been resolved by the normalization rule before the analysis layer.

The overlay does not reinterpret source gear encoding.

## TDD rule

Production behavior is test-first:

```text
REQ-005 / GEAR SPEC
-> ANALYTIC DISCRETE TEST
-> VALID BEHAVIORAL RED
-> MINIMUM IMPLEMENTATION
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

## First executable test targets

Tests should prove:

- exact sample timestamps use the new/current state;
- between samples, the previous state is held;
- no fractional/interpolated gear values appear;
- different gear sample cadences are supported;
- missing gear evidence is explicit;
- wrong concept/unit is explicit;
- non-integer values are rejected;
- non-monotonic timestamps are rejected;
- insufficient time coverage is explicit;
- dataset/source/transformation provenance remains inspectable;
- base comparison grid/provenance remains unchanged;
- no causal diagnosis is emitted.

## Architecture boundary

Discrete gear overlay belongs in deterministic analysis/evidence.

It must not:

- parse source formats;
- normalize or reinterpret source gear encoding;
- interpolate gear numerically;
- mutate base comparison/source telemetry;
- extrapolate beyond temporal coverage;
- use AI;
- generate causal interpretation.

## TDD execution evidence

Behavior tests were committed before production gear-overlay APIs.

Behavioral RED:

- OME CI #103;
- expected failure:
  `ImportError: cannot import name 'DiscreteGearOverlayEngine' from 'ome.analysis'`.

Implementation feedback:

- OME CI #107 stopped at formatter feedback before behavioral verification.

GREEN:

- OME CI #108;
- the complete canonical `verify` passed with the minimum discrete gear implementation.

No acceptance test was weakened to obtain GREEN.

## Delivered foundation

The implementation now provides:

- `DiscreteGearOverlayEngine`;
- typed gear overlay request/success/not-ready results;
- typed gear readiness issue codes;
- canonical `transmission.gear` / unitless compatibility checks;
- integer-only canonical gear values;
- exact base comparison grid reuse;
- previous-sample hold in elapsed time;
- exact sample timestamps selecting the current sample;
- support for different gear sample cadences;
- no linear interpolation;
- explicit no-extrapolation temporal coverage;
- timestamp/shape/provenance readiness checks;
- typed `GearOverlayProvenance`;
- base comparison and source/transformation evidence linkage;
- no causal or recommendation fields.

Test module:

`tests/analysis/test_discrete_gear_overlay.py`

## Completion criteria

- discrete gear spec accepted;
- tests written before production behavior;
- behavioral RED recorded;
- discrete gear overlay GREEN;
- no linear interpolation possible in implementation;
- missing/invalid evidence explicit;
- provenance chain executable;
- canonical CI GREEN;
- REQ-005 / REQ-006 traceability updated.

## Explicitly out of scope

- brake overlay;
- shift-quality analysis;
- optimal gear recommendation;
- gearbox modeling;
- automatic observations;
- UI;
- AI.
