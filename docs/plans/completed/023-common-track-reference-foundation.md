# Plan 023 — Common Track Reference Foundation

Status: **Completed**

Started: 2026-09-23

Completed: 2026-09-24

## Objective

Define and implement the smallest deterministic transformation that maps physical-car GPS laps onto one explicit common track reference suitable for ADR-0009 lap comparison.

## Delivered

Plan 023 now provides:

- `ome.track-reference.explicit-lap-projection/0.1.0`;
- WGS84-to-local metric projection using GeographicLib distance/azimuth;
- nearest reference-segment projection;
- deterministic lowest-segment-index tie behavior;
- along-reference distance based on accepted reference `gps.path_distance`;
- circular seam unwrap for closed reference geometry;
- strict post-unwrap monotonic readiness;
- explicit local-backtrack not-ready behavior;
- material self-intersection detection;
- per-sample:
  - raw circular reference distance;
  - unwrapped reference distance;
  - reference segment index;
  - segment interpolation fraction;
  - lateral projection error;
- max/p95 lateral error summaries;
- typed reference/candidate provenance;
- explicit `track.reference_distance -> lap.distance` preparation mapping;
- non-blocking supported-path performance characterization.

## Layered engineering execution

### Prompt Engineering

The task contract was bounded by:

- ADR-0009;
- `docs/specs/common-track-reference-v0.1.md`;
- Plan 023.

No automatic reference selection, smoothing, monotonic repair or track-width threshold was permitted.

### Context Engineering

Normative context:

- accepted common-reference spec;
- GPS path-distance spec;
- ADR-0009.

Real evidence:

- Portland multi-lap common-reference research;
- Traqmate GPS characterization.

One edge case was clarified during implementation:

- circular seam unwrap belongs to closed reference topology;
- analytic open polylines keep their raw monotonic along-reference coordinate.

The accepted spec was updated rather than hiding this distinction in code.

### Harness Engineering

No harness rule was disabled or weakened.

Formatting/type/test failures were classified separately from behavioral RED.

### Loop Engineering

Behavioral TDD evidence:

- CI #280 — RED: `CommonTrackReferenceEngine` absent;
- CI #286 — missing production module still visible after harness cleanup;
- CI #287/#288 — harness formatting failures;
- CI #289 — behavior failure exposed the open-reference seam edge case;
- CI #290 — common-reference engine GREEN;
- CI #292 — RED: `prepare_track_reference_lap_distance` absent;
- CI #293 — harness formatting failure;
- CI #294 — explicit canonical lap-distance preparation GREEN;
- CI #297 — performance characterization GREEN;
- CI #299 — final canonical verify GREEN.

Tests/specs were not weakened to obtain GREEN.

### Graph Engineering

Material decision gates remained closed because the accepted numerical contract was sufficient.

A future decision gate remains for performance acceleration because no latency/scale requirement has been accepted.

## Evidence bridge

A ready `CommonTrackReferenceSuccess` can now be promoted explicitly to canonical:

`lap.distance`

through:

`ome.preparation.track-reference-to-lap-distance/0.1.0`

The preparation evidence records:

- reference/candidate dataset fingerprints;
- Session / Run / Lap identities;
- reference/candidate latitude/longitude/time source channels;
- reference GPS-path algorithm identity/version;
- common-reference algorithm identity/version;
- reference origin/length;
- explicit source concept `track.reference_distance`;
- target concept `lap.distance`.

No synthetic single sensor is claimed.

The canonical evidence uses the explicit derived identifier:

`derived:track.reference_distance`

## Portland evidence

Reviewed Portland physical-car research remains the real multi-lap evidence:

- source Git blob: `13fed5ffe15ad35dc668ea2b4df8acdc63ae7668`;
- 97,980 source rows;
- 40 Hz;
- stable complete laps 2–18;
- Lap 4 research reference;
- 15/16 non-reference clean laps satisfy strict monotonic readiness after seam unwrap;
- Lap 13 exposes small local backtracking and remains not-ready under v0.1.

The exact 20 MB blob was not re-executed by the production implementation during this session because the ordinary file-content connector did not return the large body.

No new Portland runtime claim is invented.

## Performance characterization

CI #297 measured the production direct-search path:

| Samples | Projection segment checks | Observed elapsed |
|---:|---:|---:|
| 100 | 9,900 | 0.026009 s |
| 200 | 39,800 | 0.082985 s |
| 400 | 159,600 | 0.303566 s |
| 800 | 639,200 | 1.146886 s |

This confirms quadratic scaling for the correctness-first implementation.

No machine-dependent wall-time threshold was added to CI.

Performance acceleration is tracked as TD-008 and must preserve the same numerical contract.

## Boundaries preserved

Plan 023 did not add:

- automatic best/reference lap selection;
- generated centerline;
- GPS smoothing;
- cumulative-max monotonic repair;
- map matching;
- track-width rejection threshold;
- approximate nearest-neighbor semantics;
- AI geometry.

## Verification

Final feature head:

`afa9840756d310b97722ab043d6989f92a16bd31`

Final canonical verification:

`OME CI #299` — success.

Squash merge:

`f4d04e4d7b72240eaf867c9a1feb3d33828fb4ea`

## Completion assessment

All Plan 023 completion criteria are satisfied.

Scalability optimization remains explicit technical debt rather than hidden unfinished correctness work.
