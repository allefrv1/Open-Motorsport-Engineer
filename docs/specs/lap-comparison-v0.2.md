# Lap Comparison Specification v0.2

Status: **Accepted for Plan 027**

Date: 2026-09-24

## Purpose

Evolve the deterministic OME two-lap comparison contract to support trustworthy physical common-reference distance containing exact plateaus.

This specification inherits Lap Comparison v0.1 except where explicitly changed below.

## Evidence driving this revision

Plan 026 prepares Portland physical source Lap 5 onto explicit reference Lap 4.

Its canonical common-reference distance is non-decreasing and contains exactly two equal-distance plateaus:

- projected index 495: 564.4733986564207 m;
- projected index 512: 575.6433508713768 m.

No projected distance decreases.

Common Track Reference v0.2 preserves those values exactly instead of inventing forward motion.

Lap Comparison v0.1 cannot consume them because it requires strictly increasing distance.

## Distance readiness

v0.2 requires finite, **non-decreasing** canonical `lap.distance [m]`:

```text
d[i] >= d[i-1]
```

At least two distinct distance values are required for a positive comparison interval.

A real decrease remains not-ready:

```text
d[i] < d[i-1]
```

OME must not make a decreasing series ready through repair.

## Time readiness

Canonical `time.elapsed [s]` remains finite and strictly increasing:

```text
t[i] > t[i-1]
```

Distance and time lengths must still match.

## Plateau model

A plateau is one or more adjacent intervals where multiple elapsed-time samples share the same distance:

```text
(d_p, t_first)
(d_p, ...)
(d_p, t_last)
```

This represents a vertical interval in the time-versus-distance relation.

OME preserves every input sample and does not fabricate a distance increment.

## Plateau-aware linear interpolation

For target distance `d`:

### Before a plateau

When interpolating from the previous unique distance to plateau distance `d_p`, use the **first** elapsed-time sample at `d_p`.

This preserves the observed time at first arrival to the plateau location.

### Exact plateau distance

When `d == d_p`, return the **last** elapsed-time sample at that plateau.

This makes downstream accumulated time include all observed time spent before forward reference progress resumes.

### After a plateau

When interpolating from `d_p` toward the next unique distance, use the **last** elapsed-time sample at `d_p` as the lower endpoint.

Therefore plateau dwell time is not lost from later delta-time values.

## Example

Input:

```text
distance_m: 0, 10, 10, 20
elapsed_s:  0,  1,  2,  3
```

Expected:

```text
t(5)  = 0.5
t(10) = 2.0
t(15) = 2.5
t(20) = 3.0
```

The one second between the two 10 m samples remains present in all positions after 10 m.

## Multiple plateaus

The same rule applies independently to every adjacent equal-distance run.

Results must remain deterministic.

## No-plateau compatibility

For strictly increasing distance, v0.2 produces the same numerical interpolation/grid/delta outputs as v0.1 for equivalent inputs and parameters.

## Comparable interval and grid

The v0.1 common-overlap and distance-grid rules remain unchanged.

No extrapolation is introduced.

## Delta convention

Unchanged:

```text
delta_B_vs_A(d) = time_B(d) - time_A(d)
```

## Algorithm identity

Algorithm id:

`ome.lap-comparison.distance-linear`

Version:

`0.2.0`

The version identifies the plateau-aware readiness/interpolation contract.

## Readiness issue semantics

The previous broad issue:

`distance_not_strictly_increasing`

is no longer correct for exact plateaus.

v0.2 should report a decrease-specific blocking issue such as:

`distance_decreases`

only when the canonical distance actually moves backward.

The historical enum value may remain available for compatibility, but new v0.2 behavior should use the precise issue.

## Provenance

Existing ComparisonProvenance remains required.

The algorithm version must be `0.2.0`.

Input CanonicalSeriesEvidence remains unchanged and inspectable.

No plateau-collapse transformation is inserted because no sample is deleted or rewritten.

## Supporting overlays

Plan 027 changes only the base `time(distance)` comparison.

Continuous/discrete supporting-channel interpolation rules remain unchanged.

A later physical comparison-preparation plan must verify whether its supporting series can safely use the accepted base grid.

## Related artifacts

- Lap Comparison Specification v0.1
- Common Track Reference Specification v0.2
- Plan 026 — Physical-Car Track Reference Preparation Foundation
- Plan 027 — Lap Comparison Plateau Semantics Foundation
- ADR-0009
- REQ-005
- REQ-006
