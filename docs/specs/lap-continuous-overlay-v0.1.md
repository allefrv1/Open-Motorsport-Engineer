# Continuous Lap Overlay Specification v0.1

Status: **Accepted for Plan 010**

Date: 2026-09-22

## Purpose

Define how OME projects selected continuous canonical telemetry channels onto the already accepted distance grid of a successful lap comparison.

This specification extends the deterministic comparison layer.

It does not define causal interpretation or UI rendering.

## Dependency

A continuous overlay requires a successful base comparison produced by:

- algorithm `ome.lap-comparison.distance-linear`;
- compatible v0.1 provenance;
- explicit distance grid;
- interpolated `time_A(d)` and `time_B(d)`.

The overlay must not rebuild or silently change the comparison grid.

## Supported canonical concepts in v0.1

The first safe continuous set is:

| Concept | Canonical unit | Interpolation |
|---|---|---|
| `vehicle.speed` | `m/s` | linear in elapsed time |
| `driver.throttle` | `1` | linear in elapsed time |
| `driver.steering` | `rad` | linear in elapsed time |
| `engine.speed` | `rad/s` | linear in elapsed time |

## Brake is deferred from v0.1

`driver.brake` is not included in this first overlay contract.

The canonical domain explicitly allows materially different source semantics such as:

- pedal position;
- pedal force;
- master-cylinder pressure;
- brake pressure;
- binary brake state.

A later comparison contract must make brake subtype/semantic compatibility mechanically visible before OME overlays two brake series as equivalent evidence.

This is a safety/evidence decision, not a lack of interest in brake analysis.

## Gear is deferred from v0.1

`transmission.gear` is discrete.

It must not use linear interpolation.

A later explicit discrete sampling rule will handle gear.

## Input series

For each requested channel and each lap, the overlay input contains:

- source-independent canonical concept;
- canonical unit;
- sample timestamps in seconds;
- numeric canonical values;
- typed source/transformation evidence.

Timestamps and values remain immutable evidence.

## Readiness

A channel side is ready when:

- channel evidence exists;
- concept is supported by this specification;
- unit matches the canonical unit;
- timestamps and values have the same length;
- at least two samples exist;
- timestamps are finite;
- values are finite;
- timestamps are strictly increasing;
- provenance identifies the dataset/source channel/transformations;
- the channel time range covers every requested `time_lap(d)` point.

OME does not extrapolate channel values beyond source temporal coverage.

Missing/unsafe overlay evidence returns an explicit not-ready overlay result.

It does not invalidate the already valid base delta-time result.

## Projection algorithm

For each distance grid point `d`:

1. obtain `time_A(d)` from the successful base comparison;
2. linearly interpolate Lap A's channel value at that elapsed time;
3. obtain `time_B(d)`;
4. linearly interpolate Lap B's channel value at that elapsed time.

Conceptually:

```text
distance grid d
-> base time_A(d)
-> channel_A(time_A(d))

distance grid d
-> base time_B(d)
-> channel_B(time_B(d))
```

This approach supports source channels sampled at different rates.

It does not resample or overwrite ingestion/normalization data.

The aligned overlay is a derived analysis artifact.

## Linear interpolation

For channel samples:

```text
(t0, v0)
(t1, v1)
```

and target elapsed time `t`:

```text
fraction = (t - t0) / (t1 - t0)
v(t) = v0 + fraction * (v1 - v0)
```

v0.1 requires strictly increasing timestamps, so the denominator is positive.

## Algorithm identity

Algorithm:

`ome.lap-overlay.time-linear-on-distance-grid`

Version:

`0.1.0`

Any behavior-changing numerical change requires a version change.

## Output

A successful overlay contains:

- requested canonical concept;
- canonical unit;
- the exact base comparison distance grid;
- Lap A aligned channel values;
- Lap B aligned channel values;
- algorithm identity/version;
- provenance for:
  - base comparison;
  - Lap A channel;
  - Lap B channel;
  - parameters.

The first overlay result does not automatically calculate "cause", "better", "mistake" or setup advice.

## Compatibility rule

Both sides must represent the same supported canonical concept and canonical unit.

OME must not compare:

- speed to RPM;
- throttle ratio to percent without explicit normalization first;
- steering degrees to radians without normalization first;
- unsupported brake semantics;
- gear using this continuous algorithm.

## Missing evidence

If a requested channel is absent on one side, return explicit missing evidence naming:

- lap side;
- required canonical concept.

Do not synthesize the missing series.

## Relationship to source data

The evidence chain remains:

```text
ContinuousOverlayResult
  -> Overlay Algorithm + Parameters
  -> Base LapComparisonResult
  -> Canonical Channel Evidence
  -> Transformation / Normalization
  -> Source Channel
  -> Original Dataset
```

## Related artifacts

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
- ADR-0009 — Align initial lap comparisons by monotonic lap distance
- `docs/specs/lap-comparison-v0.1.md`
- `docs/domain/canonical-channels-v0.1.md`
