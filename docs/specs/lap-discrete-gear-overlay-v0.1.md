# Discrete Gear Overlay Specification v0.1

Status: **Accepted for Plan 011**

Date: 2026-09-22

## Purpose

Define how OME projects canonical `transmission.gear` evidence onto the already accepted distance grid of a successful lap comparison.

This specification is intentionally discrete.

Gear must never be linearly interpolated.

## Dependency

A gear overlay requires a successful base comparison produced by:

- algorithm `ome.lap-comparison.distance-linear`;
- version `0.2.0`;
- `lap.distance [m]`;
- `time.elapsed [s]`.

The overlay must reuse the exact base comparison distance grid and elapsed-time projections.

Lap-comparison v0.2 changes plateau-aware base time(distance) semantics only. The discrete gear sampling rule and its own version remain unchanged.

## Supported concept

Concept:

`transmission.gear`

Unit representation:

empty/unitless canonical unit string:

`""`

Values:

integer canonical gear states.

The analysis layer does not assign new meaning to integer values.

Source-specific reverse/neutral/unknown semantics must already be defined by the normalization rule that produced the canonical series.

## Input series

For each lap, the gear series contains:

- strictly increasing sample timestamps in seconds;
- integer canonical gear values;
- canonical evidence/provenance.

At least one sample is required.

## Readiness

A gear side is ready when:

- gear evidence exists;
- canonical concept is `transmission.gear`;
- canonical unit is empty/unitless;
- timestamp/value lengths match;
- at least one sample exists;
- all timestamps are finite;
- timestamps are strictly increasing;
- every gear value is an integer and not a boolean;
- provenance identifies dataset/source channel/transformations;
- the gear time range covers every requested `time_lap(d)` target.

Missing or unsafe evidence returns a structured not-ready result.

## Previous-sample rule

For a target elapsed time `t`, select:

```text
max(sample_timestamp <= t)
```

and return the corresponding gear state.

Equivalent behavior:

- exact sample timestamp -> use that sample;
- between two timestamps -> hold the previous sample;
- never average or interpolate states.

Example:

```text
time:  0.0   2.0   5.0
gear:    2     3     4
```

Targets:

```text
0.0 -> 2
1.9 -> 2
2.0 -> 3
4.9 -> 3
5.0 -> 4
```

## Coverage

No extrapolation is allowed outside the source time range.

The first target must satisfy:

```text
target >= first_gear_timestamp
```

The last target must satisfy:

```text
target <= last_gear_timestamp
```

Although previous-sample hold is mathematically possible after the final sample, OME does not assume the final state remained valid beyond the source evidence.

## Algorithm identity

Algorithm:

`ome.lap-overlay.gear-previous-sample-on-distance-grid`

Version:

`0.1.0`

Any behavior-changing sampling rule requires a version change.

## Output

A successful result contains:

- canonical concept `transmission.gear`;
- unitless canonical unit;
- exact base comparison distance grid;
- aligned Lap A integer gear states;
- aligned Lap B integer gear states;
- algorithm identity/version;
- provenance for:
  - base comparison;
  - Lap A gear channel;
  - Lap B gear channel.

## Evidence chain

```text
GearOverlayResult
  -> Gear Overlay Algorithm
  -> Base LapComparisonResult
  -> Canonical Gear Evidence
  -> Gear Normalization Rule / Transformation
  -> Source Channel
  -> Original Dataset
```

## Interpretation boundary

The result may expose:

- Lap A gear state at distance d;
- Lap B gear state at distance d;
- whether states differ as raw deterministic evidence in a later observation layer.

It does not claim:

- one gear is better;
- a shift caused time loss;
- the driver shifted incorrectly;
- a setup/ratio change is recommended.

## Related artifacts

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
- ADR-0009
- `docs/specs/lap-comparison-v0.2.md`
- `docs/domain/canonical-channels-v0.1.md`
