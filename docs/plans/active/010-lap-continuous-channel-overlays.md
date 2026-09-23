# Plan 010 — Lap Continuous Channel Overlays

Status: **Active**

Started: 2026-09-22

## Objective

Extend a successful deterministic lap delta comparison with selected continuous canonical channel overlays on the exact same distance grid.

This increment targets the measured evidence required to begin answering:

> What measurable driver/vehicle differences accompany the time gain/loss at the same place on track?

It still does not assign cause.

## Requirements

Primary:

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence

Authoritative numerical contracts:

- ADR-0009;
- `docs/specs/lap-comparison-v0.1.md`;
- `docs/specs/lap-continuous-overlay-v0.1.md`.

## Scope

v0.1 supports continuous overlays for:

- `vehicle.speed [m/s]`;
- `driver.throttle [1]`;
- `driver.steering [rad]`;
- `engine.speed [rad/s]`.

The overlay consumes a successful base lap comparison and does not create a new distance grid.

## Multi-rate behavior

A requested channel may have a different sample cadence from distance/time.

For every base grid point:

```text
distance d
-> lap elapsed time t(d)
-> channel value v(t(d))
```

Channel interpolation is deterministic linear interpolation in elapsed time.

This keeps source/normalized samples unchanged and makes the derived operation explicit.

## Brake boundary

Brake overlay is deliberately deferred.

The accepted canonical brake concept covers multiple non-equivalent physical/driver-input quantities.

Before implementing brake overlay, OME needs a mechanically visible semantic subtype/compatibility contract.

Do not compare pedal position and pressure simply because both are called brake evidence.

## Gear boundary

Gear is discrete.

Do not linearly interpolate gear.

A separate discrete overlay rule will be implemented later.

## TDD rule

Production overlay behavior is test-first:

```text
REQ-005 / OVERLAY SPEC
-> ANALYTIC CHANNEL TEST
-> VALID BEHAVIORAL RED
-> MINIMUM IMPLEMENTATION
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

## First executable test targets

Tests should prove:

- speed can be projected onto the existing comparison grid;
- different channel sample rates/cadences are supported;
- throttle/steering/RPM canonical units are enforced;
- same inputs produce identical overlay outputs;
- missing channel evidence returns explicit not-ready;
- unsupported brake returns explicit unsupported/not-ready;
- gear returns explicit unsupported/not-ready;
- non-monotonic channel timestamps return not-ready;
- non-finite channel values return not-ready;
- insufficient temporal coverage returns not-ready rather than extrapolating;
- source channel/transformation provenance remains inspectable;
- base comparison grid/provenance remains unchanged;
- no causal diagnosis is emitted.

## Architecture boundary

Continuous overlays belong in deterministic analysis/evidence.

They must not:

- parse source formats;
- normalize units;
- guess channel meaning;
- mutate the base comparison;
- repair source data;
- extrapolate missing temporal coverage;
- use AI;
- generate causal interpretation.

## TDD execution evidence

Behavior tests were committed before production overlay APIs.

Behavioral RED:

- OME CI #91;
- expected failure:
  `ImportError: cannot import name 'ContinuousOverlayEngine' from 'ome.analysis'`.

Additional readiness tests were committed while the branch remained RED.

Implementation feedback:

- CI #93–#95 exercised incomplete implementation/formatting states;
- those runs are not separate behavioral RED cycles.

GREEN:

- OME CI #96;
- the complete canonical `verify` passed with the minimum continuous overlay implementation.

No acceptance test was weakened to obtain GREEN.

## Delivered foundation

The overlay implementation now provides:

- `ContinuousOverlayEngine`;
- typed continuous overlay request/success/not-ready results;
- typed overlay readiness issue codes;
- supported canonical concepts:
  - `vehicle.speed [m/s]`;
  - `driver.throttle [1]`;
  - `driver.steering [rad]`;
  - `engine.speed [rad/s]`;
- reuse of the exact base comparison distance grid;
- deterministic linear channel interpolation in elapsed time;
- support for different channel sample cadences;
- explicit no-extrapolation time-coverage checks;
- finite/strictly-increasing channel readiness;
- dataset/source/transformation provenance checks;
- typed overlay provenance linking back to base comparison provenance;
- explicit unsupported results for brake and gear;
- no causal diagnosis fields.

Test module:

`tests/analysis/test_continuous_overlay.py`

## Completion criteria

- overlay spec accepted;
- tests written before production behavior;
- behavioral RED recorded;
- continuous overlay implementation GREEN;
- supported concept/unit rules executable;
- multi-rate interpolation executable;
- missing/unsupported evidence explicit;
- provenance chain executable;
- canonical CI GREEN;
- REQ-005 / REQ-006 traceability updated.

## Explicitly out of scope

- brake overlay until semantic compatibility is explicit;
- gear overlay;
- corner segmentation;
- automatic observations;
- causal diagnosis;
- comparison UI;
- AI explanation.
