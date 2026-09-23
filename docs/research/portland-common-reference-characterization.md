# Portland Common Track Reference Characterization

Status: **Reviewed research**

Date: 2026-09-23

## Purpose

Evaluate whether simple lap-length normalization is sufficient for physical-car comparison or whether OME should project GPS measurements onto a common reference trajectory.

This is research evidence, not production behavior.

## Source

External Apache-2.0 source:

- repository: `djhedges/exit_speed`;
- path: `exit_speed/testdata/2019-08-18_Portland_CORRADO_DJ_R03.csv`;
- Git blob: `13fed5ffe15ad35dc668ea2b4df8acdc63ae7668`.

Observed:

- 97,980 telemetry rows;
- 40 Hz;
- source Lap markers 0–20;
- complete/stable lap population 2–18.

The large file remains external to avoid repository bloat.

## Candidate A — global lap-length normalization

Concept:

```text
corrected_s = travelled_path_s * reference_length / travelled_lap_length
```

This is similar in spirit to motorsport corrected-distance workflows that stretch or shrink lap length to a common track length.

MoTeC training material explicitly documents that Corrected Distance is used for same-distance lap comparison and that lap lengths may be stretched/shrunk to account for variation.

### Advantage

- simple;
- monotonic when travelled path is monotonic;
- inexpensive;
- easy to audit.

### Limitation

It assumes that equal percentage of travelled path corresponds to equal physical track position.

Different racing lines can violate that assumption locally.

## Candidate B — projection onto explicit reference-lap geometry

Research reference:

- source Lap 4 chosen only for characterization because it is one of the fastest clean laps.

A local metric plane was used for research-only geometry.

Each candidate GPS point was projected onto the closest segment of the reference-lap polyline.

The resulting along-reference distance represents a physical position on one common geometry.

### Scaling vs projection result

For laps 2–18 excluding reference Lap 4:

- median across laps of the p95 absolute disagreement between global scaling and geometric projection: ~2.09 m;
- worst lap p95 disagreement: ~3.66 m;
- individual maximum disagreement reached ~6.41 m in Lap 13.

Candidate laps also showed real lateral displacement from the reference trajectory:

- typical median lateral offset below 1 m;
- p95 lateral offset commonly around 3–4 m;
- Lap 13 had a larger localized deviation.

These differences are plausible racing-line variation.

### Interpretation

A 2–4 m along-track mismatch is materially relevant when correlating braking, throttle and delta-time events.

Therefore simple global stretch/shrink is useful as a fallback concept but is not the preferred OME physical-position reference when GPS geometry is available.

## Circular seam ambiguity

A closed circuit has a start/end seam.

Nearest geometric projection can return a value near 0 m or near reference length for physically adjacent positions around start/finish.

Raw nearest projection across Portland laps showed large apparent backward jumps of approximately one full lap.

This is a topology/seam issue, not a real backwards vehicle movement.

## Marker-anchored circular unwrap

Research rule:

1. project the source-lap boundary sample onto the reference geometry;
2. treat that projected position as the candidate lap's zero;
3. process projected positions in source-time order;
4. when consecutive projected positions differ by more than half the reference length, treat the change as crossing the circular seam;
5. unwrap the circular coordinate into a continuous forward distance.

### Portland result

After seam unwrapping:

- 15 of 16 non-reference laps had no local projected-distance decreases;
- Lap 13 had two small local decreases;
- largest local backtrack in Lap 13 was ~0.45 m.

No smoothing or monotonic clamp was applied.

## v0.1 readiness implication

OME should not silently clamp projected distance to make it monotonic.

For the initial common-reference transformation:

- seam unwrapping is part of coordinate topology, not data repair;
- after unwrap, projected distance must be strictly increasing;
- a lap with local projection backtracking is not-ready for v0.1;
- a future explicit noise/monotonic correction algorithm may relax this if engineering evidence justifies it.

## Local coordinate system

A projection algorithm needs metric planar coordinates for polyline projection.

A clean approach is a local azimuthal-equidistant representation centered on the reference trajectory.

PROJ documents Azimuthal Equidistant as a 2D projected coordinate system with configurable latitude/longitude origin and metre output.

OME already depends on GeographicLib.

An equivalent local coordinate can also be constructed from WGS84 inverse-geodesic distance and azimuth from one reference origin:

```text
x = distance * sin(azimuth)
y = distance * cos(azimuth)
```

This retains the same conceptual local radial distance/azimuth semantics without requiring source coordinates to become canonical map coordinates.

The exact implementation method remains an implementation decision as long as the accepted transformation contract is met and verified.

## Geometry operation reference

A standard linear-referencing operation projects a point onto a line and returns distance from the line origin to the nearest projected point.

Shapely documents this behavior through `line_locate_point` / `project`.

OME need not expose Shapely semantics as domain semantics.

The domain contract is:

```text
GPS point
-> closest point on explicit reference trajectory
-> along-reference distance
-> lateral projection distance
```

## Recommendation

Plan 023 should use **explicit reference-trajectory projection**, not only global lap-length scaling, as the primary v0.1 common physical reference.

The transformation must remain conservative:

- explicit reference identity;
- marker-anchored seam unwrap;
- no hidden smoothing;
- strict monotonic readiness after unwrap;
- projection/lateral-error evidence retained;
- no automatic reference-lap selection in v0.1.

## References

- MoTeC corrected-distance training material;
- PROJ Azimuthal Equidistant documentation;
- Shapely linear-referencing documentation.
