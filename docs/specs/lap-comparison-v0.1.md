# Lap Comparison Specification v0.1

Status: **Accepted for the first vertical slice**

Date: 2026-09-22

## Purpose

Define the deterministic numerical contract for the first OME two-lap comparison.

This specification implements the accepted direction in ADR-0009.

It does not define UI presentation or causal engineering diagnosis.

## Required canonical inputs

Each lap must provide two explicit canonical series:

### Position reference

Concept:

`lap.distance`

Unit:

`m`

Meaning:

Monotonic distance along the comparable lap/reference path.

### Time reference

Concept:

`time.elapsed`

Unit:

`s`

Meaning:

Elapsed lap/reference time corresponding to the distance samples.

OME must not silently substitute:

- sample index;
- wall-clock time;
- GPS position;
- normalized lap percentage;
- another speed/distance source.

A different reference requires a separate accepted rule.

## v0.1 readiness contract

For each lap:

- distance series exists;
- elapsed-time series exists;
- both series have the same length;
- at least two paired samples exist;
- every distance value is finite;
- every elapsed-time value is finite;
- distance is strictly increasing;
- elapsed time is strictly increasing;
- distance unit is metres;
- time unit is seconds;
- source/evidence references are present.

### Why strictly increasing in v0.1

A physically valid source may contain repeated distance values during a stop or due to quantization.

OME v0.1 does not silently deduplicate or choose a first/last passage rule.

Such a lap is reported as not ready until an explicit plateau policy is specified.

This is intentionally conservative.

## Comparable interval

For Lap A and Lap B:

```text
start = max(first_distance_A, first_distance_B)
end   = min(last_distance_A,  last_distance_B)
```

The comparison is ready only when:

```text
end > start
```

No extrapolation outside the common interval is permitted.

## Analysis grid

Default parameter:

```text
grid_step_m = 1.0
```

The parameter must be:

- finite;
- greater than zero.

Grid construction:

1. include the common start distance;
2. add regular points at `start + n * grid_step_m`;
3. never exceed the common end distance;
4. include the common end distance exactly when it is not already the final regular point.

The grid is an analysis artifact.

It does not modify source telemetry.

## Interpolation

For elapsed time as a function of distance, use deterministic linear interpolation.

For two source points:

```text
(d0, t0)
(d1, t1)
```

and a grid distance `d` where:

```text
d0 <= d <= d1
```

compute:

```text
fraction = (d - d0) / (d1 - d0)

t(d) = t0 + fraction * (t1 - t0)
```

Because v0.1 requires strictly increasing distance:

```text
d1 - d0 > 0
```

No spline, smoothing or extrapolation is used.

## Delta convention

For every grid point:

```text
delta_B_vs_A(d) = time_B(d) - time_A(d)
```

Interpretation:

- positive: Lap B has taken more time than Lap A to reach distance `d`;
- negative: Lap B has taken less time than Lap A;
- zero: equal accumulated elapsed time at that distance.

The sign convention is part of the algorithm contract and must not be reversed by callers.

## Algorithm identity

Algorithm:

`ome.lap-comparison.distance-linear`

Version:

`0.1.0`

Any behavior-changing numerical change requires a version change.

## Result

A successful comparison contains:

- common distance interval;
- comparison grid in metres;
- interpolated Lap A elapsed time in seconds;
- interpolated Lap B elapsed time in seconds;
- `delta_B_vs_A` in seconds;
- algorithm identity/version;
- parameters;
- evidence/provenance for both laps.

## Not-ready result

Readiness failure returns explicit structured issues.

Initial issue families:

- missing distance evidence;
- missing elapsed-time evidence;
- incompatible units/concepts;
- insufficient paired samples;
- distance/time length mismatch;
- non-finite distance;
- non-finite elapsed time;
- distance not strictly increasing;
- elapsed time not strictly increasing;
- no common positive distance interval;
- invalid grid step;
- missing provenance/context evidence.

OME must not return a plausible-looking delta curve when readiness fails.

## Evidence contract

Each lap input must identify:

- original dataset fingerprint;
- Session identifier;
- Run identifier when known;
- Lap identifier;
- source channel used for `lap.distance`;
- source channel used for `time.elapsed`;
- normalization/transformation identities and versions when applicable;
- canonical concept;
- unit.

The comparison result must additionally identify:

- comparison algorithm id/version;
- `grid_step_m`;
- common interval;
- output units.

Conceptual chain:

```text
LapComparisonResult
  -> ComparisonAlgorithm + Parameters
  -> Lap A Evidence / Lap B Evidence
  -> Canonical Series
  -> Normalization / Transformation
  -> Source Channel
  -> Original Dataset
```

## Observation boundary

v0.1 produces deterministic metrics.

It may report:

- numerical delta-time values;
- readiness/missing evidence.

It does not produce:

- cause;
- hypothesis;
- understeer/oversteer diagnosis;
- driver mistake labels;
- setup recommendations.

Those belong to later evidence/observation/interpretation layers.

## Continuous telemetry channels

Speed, throttle, brake, steering and RPM overlays are intentionally deferred to the next comparison increment.

They may later reuse the same distance grid with explicit channel interpolation rules.

Discrete gear requires a separate non-continuous rule and must not be linearly interpolated.

## Related artifacts

- ADR-0009 — Align initial lap comparisons by monotonic lap distance
- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
- Canonical Telemetry Concepts v0.1
