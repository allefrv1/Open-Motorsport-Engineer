# Common Track Reference Specification v0.2

Status: **Accepted for Plan 026**

Date: 2026-09-24

## Purpose

Evolve the accepted common-track-reference contract using physical Portland evidence discovered while composing Plan 026.

This specification inherits Common Track Reference v0.1 except where explicitly changed below.

## Evidence that drives this revision

Plan 026 projects Portland source Lap 5 onto explicit reference Lap 4.

The production v0.1 engine returns not-ready because two adjacent candidate samples project to exactly the same along-reference distance:

- projected index 495: 564.4733986564207 m -> 564.4733986564207 m;
- projected index 512: 575.6433508713768 m -> 575.6433508713768 m.

There is no local decrease at those points.

The end of the candidate trajectory remains forward and close to the reference lap length.

Therefore the observed condition is an exact projection plateau, not backtracking.

## Readiness change

After circular seam unwrap, v0.2 requires projected reference distance to be **non-decreasing**:

```text
s[i] >= s[i-1]
```

Exact plateaus are allowed and preserved unchanged.

A real decrease remains not-ready:

```text
s[i] < s[i-1]
```

OME must not make a decreasing series ready through:

- epsilon insertion;
- cumulative maximum;
- smoothing;
- interpolation;
- sample deletion;
- sample reordering.

## Why plateaus are preserved

Nearest-segment projection can legitimately map consecutive physical GPS samples to the same closest point on a finite reference polyline, especially around reference vertices.

Changing an exact plateau into artificial forward motion would fabricate position evidence.

Preserving the plateau keeps the geometric result honest.

## Downstream comparison boundary

A ready `track.reference_distance` artifact is not automatically a ready `time(distance)` function.

If downstream lap comparison requires strictly increasing canonical distance, it must define an explicit deterministic plateau policy in a separate transformation/specification.

Plan 026 does not resolve that downstream ambiguity.

## Algorithm identity

Algorithm id remains:

`ome.track-reference.explicit-lap-projection`

v0.2 algorithm version:

`0.2.0`

The version changes because readiness behavior is observably different from v0.1.

## Issue semantics

The v0.2 blocking issue is conceptually:

`projected_distance_decreases`

It applies only when an unwrapped candidate projection moves backward.

The historical v0.1 issue name may remain available for compatibility, but v0.2 production behavior should report the precise decrease-specific issue.

## Provenance

All existing v0.1 provenance remains required.

The algorithm version in result/provenance makes the plateau policy inspectable.

No source sample or source coordinate is changed.

## Related artifacts

- Common Track Reference Specification v0.1
- Plan 023 — Common Track Reference Foundation
- Plan 026 — Physical-Car Track Reference Preparation Foundation
- ADR-0009 — distance-aligned lap comparison
