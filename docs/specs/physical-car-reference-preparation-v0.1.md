# Physical-Car Track Reference Preparation Specification v0.1

Status: **Accepted for Plan 026**

Date: 2026-09-24

## Purpose

Define the deterministic application bridge from explicitly selected Traqmate source lap windows to the already accepted GPS/common-track-reference analysis contracts.

This specification does not perform lap comparison or reporting.

## Inputs

v0.1 prepares two explicitly selected complete source laps from one imported Traqmate Trackvision dataset:

- one caller-selected **reference** `SourceLapWindow`;
- one caller-selected **candidate** `SourceLapWindow`;
- explicit trusted `LapEvidenceContext` for each lap.

Reference selection is caller input.

OME never chooses fastest, best, first or median lap in this slice.

## Dataset rule

Both windows must reference the supplied imported dataset fingerprint.

v0.1 requires both laps to come from the same imported Traqmate dataset.

Cross-dataset physical comparison is deferred.

## Required source channels

The source dataset must provide:

- `Elapsed Time` in seconds;
- `Lat (Degrees)` in degrees;
- `Lon (Degrees)` in degrees.

The preparation layer parses only these verified physical source values.

It does not normalize vehicle-performance channels.

## Selected telemetry samples

For a window:

```text
telemetry indexes = [start_index, end_index_exclusive)
```

These remain the selected source telemetry samples.

The preparation service must not mutate, reorder, fill or copy values back into the imported dataset.

## Closing boundary point

`closing_boundary_index` is preserved by Plan 025 and belongs to the next source lap.

For geometry/time closure only, Plan 026 may append the source GPS/time point at that index to a derived lap trajectory.

Conceptually:

```text
trajectory evidence
= selected telemetry samples
+ one boundary-only closing point
```

This does **not** redefine source ownership.

The closing point remains identified as boundary evidence, not as a telemetry sample owned by the selected lap.

## Evidence extraction

For each prepared trajectory, create explicit `SourceSeriesEvidence` for:

- latitude;
- longitude;
- elapsed time.

Evidence must retain:

- dataset fingerprint;
- original source channel identifier/name;
- unit.

The extracted numeric trajectory must be finite and length-consistent.

No smoothing, interpolation, point deletion or timestamp repair occurs here.

## Reference GPS path

The explicit reference trajectory is passed to the accepted:

`GPSPathDistanceEngine`

including its closing boundary point.

The result must be a ready `gps.path_distance` artifact.

## Reference lap canonical distance

Plan 022 correctly prohibits generic:

```text
gps.path_distance -> lap.distance
```

aliasing.

Plan 026 permits a narrower explicit mapping only because this trajectory is the caller-selected common track reference.

Transformation identity:

`ome.preparation.explicit-reference-path-to-lap-distance`

Version:

`0.1.0`

The output is canonical:

`lap.distance [m]`

using the accepted reference `GPSPathDistanceSuccess.path_distance_m`.

The evidence chain must include:

1. WGS84 GPS path algorithm identity/version;
2. explicit reference-lap context;
3. explicit reference-selection transformation;
4. source latitude/longitude/time evidence.

This mapping is invalid for an arbitrary candidate lap.

## Candidate common-reference distance

The candidate trajectory is projected using:

`CommonTrackReferenceEngine`

with the explicitly prepared reference trajectory.

A ready result is converted through the already accepted:

`prepare_track_reference_lap_distance`

mapping:

```text
track.reference_distance
-> lap.distance
```

## Output

A ready preparation artifact should contain at least:

- reference `TrackReferenceLap`;
- candidate `TrackReferenceLap`;
- reference `GPSPathDistanceSuccess`;
- candidate `CommonTrackReferenceSuccess`;
- canonical reference `LapComparisonSeries` for `lap.distance`;
- canonical candidate `LapComparisonSeries` for `lap.distance`;
- explicit source windows;
- explicit reference/candidate contexts.

The output is preparation evidence.

It is not a comparison result.

## Readiness failures

Return explicit not-ready evidence for at least:

- unsupported source type;
- window fingerprint mismatch;
- invalid/mismatched context fingerprint;
- reference and candidate windows are the same requested source lap;
- missing required GPS/time channel;
- window indexes outside source evidence;
- closing boundary outside source evidence;
- non-numeric/non-finite selected GPS/time values;
- length inconsistency;
- reference GPS-path derivation not-ready;
- common-track-reference projection not-ready due to a true projected-distance decrease or other blocking geometry issue.

Do not repair or guess.

## Determinism

Equivalent imported evidence, windows, contexts and algorithms must produce equivalent preparation results.

## Boundary

Plan 026 does not:

- choose laps;
- create Session/Run context;
- compare delta time;
- normalize speed/throttle/brake/steering/RPM/gear;
- create a comparison report;
- alter source telemetry;
- add API/frontend behavior;
- use AI.

## Next step

After Plan 026, a separate application composition slice may combine prepared physical `lap.distance`, elapsed-time and explicitly mapped supporting channels into the existing `ComparisonReportRequest` stack.

## Related artifacts

- Plan 025 — Physical-Car Lap Window Selection Foundation
- Traqmate Source Lap Window Specification v0.1
- GPS Path Distance Specification v0.1
- Common Track Reference Specification v0.2
- ADR-0009 — distance-aligned lap comparison
- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
