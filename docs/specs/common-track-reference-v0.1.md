# Common Track Reference Specification v0.1

Status: **Accepted for Plan 023**

Date: 2026-09-23

## Purpose

Define the first deterministic OME transformation that maps candidate-lap WGS84 GPS samples onto the physical trajectory of one explicitly identified reference lap.

The output is a common along-reference position suitable for evaluation as canonical `lap.distance`.

## Derived concept

Working artifact:

`track.reference_distance`

Unit:

`m`

Meaning:

Unwrapped along-reference distance obtained by projecting a candidate GPS position onto one explicit reference-lap trajectory.

This is derived evidence.

It is not source telemetry.

## Inputs

### Reference lap

Required:

- dataset fingerprint;
- Session / Run / Lap context;
- latitude/longitude source evidence;
- timestamps;
- ordered WGS84 latitude/longitude values;
- accepted `gps.path_distance` result for the same samples;
- explicit source lap boundary represented by the first sample.

### Candidate lap

Required:

- dataset fingerprint;
- Session / Run / Lap context;
- latitude/longitude source evidence;
- timestamps;
- ordered WGS84 latitude/longitude values;
- explicit source lap boundary represented by the first sample.

Reference selection is explicit input.

OME v0.1 never auto-selects fastest, first or median lap.

## Reference origin

The first reference-lap GPS sample defines the local projection origin:

```text
origin_lat = reference.latitude[0]
origin_lon = reference.longitude[0]
```

This origin is part of result provenance.

## Local metric coordinates

For every reference/candidate WGS84 point:

1. solve the WGS84 inverse geodesic from the reference origin to the point;
2. obtain geodesic distance `r` and forward azimuth `azimuth`;
3. convert to local metric coordinates:

```text
x_east  = r * sin(azimuth)
y_north = r * cos(azimuth)
```

Azimuth is expressed in radians for the trigonometric conversion.

This is an azimuthal-equidistant local representation around the explicit reference origin.

Raw latitude/longitude values are never replaced.

## Reference polyline

The ordered reference local coordinates form a polyline.

The reference along-distance coordinate does **not** use Euclidean local-polyline length as canonical evidence.

It uses the accepted WGS84 `gps.path_distance` cumulative values from Plan 022.

For reference segment `i -> i+1`:

- local planar endpoints define projection geometry;
- WGS84 cumulative path-distance values define along-reference distance.

## Point-to-segment projection

For a candidate point `P` and reference segment `A -> B`:

```text
v = B - A
w = P - A

u_raw = dot(w, v) / dot(v, v)
u = clamp(u_raw, 0, 1)

Q = A + u * v
lateral_error = |P - Q|
```

The segment along-reference coordinate is:

```text
s = reference_path[i]
  + u * (reference_path[i+1] - reference_path[i])
```

For each candidate sample, select the segment with minimum lateral error.

Exact equal-distance ties are resolved deterministically by the lowest reference segment index.

Tie-breaking is implementation determinism, not a claim of physical certainty.

## Reference geometry restrictions

v0.1 supports a simple ordered reference trajectory.

The reference is not-ready when:

- fewer than two usable segments exist;
- its accepted GPS path distance is missing/incompatible;
- local segment length is zero for all geometry;
- provenance/context is incomplete;
- geometry contains a material self-intersection that makes nearest-position interpretation ambiguous.

Near-parallel geometry quality is retained through lateral/projection evidence.

No arbitrary track-width threshold is introduced in v0.1.

## Raw circular coordinate

Nearest projection produces:

```text
0 <= s_raw <= L
```

where:

`L = reference total gps.path_distance`

A closed circuit makes values near 0 and near L physically adjacent.

## Start/finish seam unwrap

Candidate sample order and source lap boundary provide topological continuity.

### Initial branch

For first raw projected value `s0`:

```text
if s0 > L / 2:
    s_unwrapped[0] = s0 - L
else:
    s_unwrapped[0] = s0
```

The candidate boundary is **not forced to zero**.

This preserves marker/GPS offset relative to the reference boundary.

### Sequential unwrap

Maintain an integer turn offset.

For consecutive raw values:

```text
delta_raw = s_raw[i] - s_raw[i-1]

if delta_raw < -L/2:
    turn += 1
elif delta_raw > L/2:
    turn -= 1

s_unwrapped[i] = s_raw[i] + turn * L
```

The initial turn corresponds to the branch selected for `s_unwrapped[0]`.

Crossing the half-lap threshold is interpreted as circular seam topology, not smoothing.

## Monotonic readiness

After seam unwrap:

`track.reference_distance` must be strictly increasing.

OME v0.1 does not:

- sort samples;
- cumulative-max clamp;
- delete backtracking samples;
- average projected distance;
- stretch/shrink the candidate lap to exactly `L`.

Any local non-increase returns explicit not-ready evidence.

Portland research found this conservative contract passes 15/16 non-reference complete laps; one lap showed two small local backtracks with maximum ~0.45 m.

## Candidate end position

The candidate is not forced to end exactly at `L`.

A complete candidate may end slightly below or above reference length because its source boundary GPS point can project slightly before/after the reference boundary.

The downstream ADR-0009 comparison uses the common distance interval.

## Lateral projection evidence

Every projected sample retains:

- selected reference segment index;
- segment interpolation fraction;
- lateral projection error in metres;
- raw circular along-reference distance;
- unwrapped along-reference distance.

Result summaries should include at least:

- maximum lateral error;
- p95 lateral error;
- start offset relative to reference origin;
- end offset relative to reference length.

v0.1 does not invent a hard lateral-error rejection threshold.

## Reference self-intersection

A geometric crossing can make nearest projection ambiguous even when a candidate is physically valid.

v0.1 must reject a materially self-intersecting reference polyline rather than choose a branch silently.

Shared adjacent endpoints are normal and are not self-intersections.

The nearly closed start/end geometry is handled by the circular seam rule.

## Output

Successful result contains:

- derived concept `track.reference_distance`;
- unit `m`;
- reference length;
- local reference origin;
- candidate source timestamps;
- raw projected distance;
- unwrapped reference distance;
- selected segment indexes;
- segment fractions;
- lateral errors;
- reference/candidate evidence and context;
- algorithm id/version.

Algorithm identity:

`ome.track-reference.explicit-lap-projection`

Version:

`0.1.0`

## Determinism

Equivalent reference/candidate inputs and algorithm version must produce equivalent projection output.

No stochastic operation is permitted.

## Relationship to canonical lap.distance

A successful v0.1 output is eligible for an explicit preparation mapping:

```text
track.reference_distance
-> lap.distance
```

only when:

- the result is ready;
- reference identity is preserved;
- monotonicity passes;
- the preparation workflow records the transformation id/version.

The raw GPS path distance remains separately inspectable.

## Scaling-only alternative

Global lap-length stretch/shrink is not the primary v0.1 algorithm.

Portland research found that simple scaling differs locally from geometric projection by roughly 2–4 m at p95 depending on lap.

Global scaling may be added later as a separately identified fallback for sources without usable position geometry.

## Performance

The numerical contract is independent of search acceleration.

The first correct implementation may use a direct segment search.

If Portland-scale benchmarking shows unacceptable performance, a spatial index may be introduced behind identical behavior with regression tests.

## TDD cases

Before production code, tests should cover:

- straight reference geometry;
- L-shaped reference geometry;
- lateral-offset point projection;
- segment interpolation fraction;
- explicit reference cumulative distance;
- deterministic nearest-segment tie handling;
- closed-loop seam start near L;
- forward seam unwrap;
- candidate boundary retained as nonzero offset;
- strictly increasing success;
- local backtrack not-ready;
- invalid/missing context/evidence;
- reference self-intersection not-ready;
- deterministic repeatability;
- no mutation of source/reference arrays.

## Related artifacts

- Plan 023 — Common Track Reference Foundation
- ADR-0009 — Align initial lap comparisons by monotonic lap distance
- GPS Path Distance Specification v0.1
- Portland Common Track Reference Characterization
