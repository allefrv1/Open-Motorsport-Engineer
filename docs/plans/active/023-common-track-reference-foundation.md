# Plan 023 — Common Track Reference Foundation

Status: **Active**

Started: 2026-09-23

## Objective

Define and implement the smallest deterministic transformation that maps physical-car GPS laps onto one explicit common track reference suitable for ADR-0009 lap comparison.

## Why this plan exists

Plan 022 proved:

```text
GPS coordinates
-> deterministic WGS84 gps.path_distance
```

but also proved:

```text
independent travelled path distance
!= guaranteed same physical track position
```

The Portland multi-lap source shows real lap-length and racing-line variation.

OME therefore needs a common geometry.

## Research basis

- `docs/research/portland-common-reference-characterization.md`
- `docs/research/traqmate-gps-path-characterization.md`
- ADR-0009
- GPS Path Distance Specification v0.1

External references:

- MoTeC Corrected Distance practice;
- PROJ Azimuthal Equidistant projection;
- standard line-location/projection semantics documented by Shapely.

## Initial architecture direction

Use an **explicitly supplied trusted reference lap**, not an automatically selected best/fastest lap.

The reference lap supplies ordered WGS84 latitude/longitude geometry and a source lap boundary.

Candidate lap GPS points are projected onto that reference trajectory.

The output is along-reference position in metres.

## Reference identity

Every result must identify:

- reference dataset fingerprint;
- reference Session / Run / Lap context;
- reference GPS channel evidence;
- reference transformation identity;
- reference geometry length;
- candidate dataset/lap context.

Reference selection is explicit input.

v0.1 must not silently choose:

- fastest lap;
- first lap;
- median lap;
- a generated centerline.

## Local metric geometry

Projection requires a local metric coordinate system.

Preferred conceptual representation:

- WGS84 reference origin;
- azimuthal-equidistant/local geodesic coordinates in metres.

Plan 023 must specify the exact numerical transformation before production code.

No raw latitude/longitude Euclidean distance is allowed.

## Reference polyline

The reference trajectory is an ordered closed-lap polyline.

Its along-reference cumulative distance is based on the accepted reference geometry.

Projection output for a candidate point includes:

- nearest reference segment;
- interpolation fraction on that segment;
- raw circular along-reference distance;
- lateral projection error.

## Start/finish seam

The reference trajectory is topologically circular.

v0.1 must anchor candidate zero to the explicit source lap boundary.

Projected values are then unwrapped in source-time order.

A seam crossing may be interpreted only when the raw projected jump exceeds a documented circular threshold tied to reference length.

This unwrap is coordinate topology handling.

It is not a smoothing/filter operation.

## Monotonic readiness

After seam unwrap, candidate along-reference distance must be strictly increasing.

OME must not:

- cumulative-max clamp;
- sort points;
- delete backwards points;
- smooth projection distance.

If local backtracking remains, return an explicit not-ready issue.

The Portland characterization found this conservative rule passes 15/16 analyzed non-reference laps and rejects one lap with a maximum local backtrack around 0.45 m.

## Lateral projection evidence

Projection distance to the reference trajectory is important quality evidence.

v0.1 should preserve per-sample lateral offset and summary statistics.

A hard maximum-lateral-offset rejection threshold must not be invented without an accepted engineering basis.

Initially:

- preserve lateral error;
- expose it to readiness/quality assessment;
- only reject structurally impossible projection or ambiguous geometry.

A later requirement may define track-width-aware limits.

## Reference geometry readiness

The reference lap is not ready when:

- GPS/path evidence is missing;
- fewer than two unique geometry points exist;
- coordinates are invalid;
- reference path is not a usable ordered loop;
- provenance/context is incomplete;
- source lap boundary is unavailable.

Self-intersecting or near-parallel geometry needs explicit analysis because nearest projection can be ambiguous.

v0.1 must detect/report unsupported geometry rather than guess when ambiguity is material.

## Candidate readiness

The candidate lap is not ready when:

- GPS/time evidence is missing;
- source lap boundary/context is missing;
- coordinates/timestamps are invalid;
- timestamps are non-monotonic;
- projection fails;
- seam unwrap cannot produce one coherent lap;
- unwrapped reference distance locally moves backwards.

## Output concept

Working derived artifact:

`track.reference_distance`

Unit:

`m`

Meaning:

Position along an explicitly identified reference-lap trajectory obtained by deterministic geometric projection.

It is derived evidence.

Promotion/mapping to canonical `lap.distance` is permitted only after the transformation satisfies the Plan 023 readiness/evidence contract and is explicitly recorded in the preparation workflow.

## Comparison to global stretch

Global stretch/shrink is not the primary v0.1 algorithm.

Portland characterization found p95 local disagreement of roughly 2–4 m between simple global scaling and reference projection.

That is material for precise telemetry event alignment.

## TDD rule

After the numerical contract is accepted:

```text
ACCEPTED COMMON-REFERENCE SPEC
-> ANALYTIC TRACK GEOMETRY TESTS
-> RED
-> MINIMUM PROJECTION IMPLEMENTATION
-> GREEN
-> PORTLAND MULTI-LAP CHARACTERIZATION
-> FULL VERIFY
```

Analytic tests should include:

- straight reference line;
- L-shaped reference;
- lateral-offset projection;
- explicit along-reference distance;
- closed-loop seam unwrap;
- strict monotonic success;
- local backtrack not-ready;
- deterministic repeatability;
- reference/candidate provenance;
- no source mutation.

## Performance discipline

Correctness comes first.

Do not introduce a spatial-index dependency before a representative benchmark demonstrates need.

The reference/candidate sample counts from Portland provide the performance test shape.

If naive projection is too slow, optimize behind the same numerical contract.

## Architecture boundary

Common-reference projection belongs in deterministic analysis/transformation.

It must not:

- modify ingestion;
- silently repair GPS;
- select a reference lap implicitly;
- generate a centerline implicitly;
- infer track identity from coordinates;
- use AI for geometry;
- hide lateral/projection errors.

## Completion criteria

- exact local-coordinate/projection contract accepted;
- seam unwrap rule accepted;
- evidence/readiness contract accepted;
- tests written before production behavior;
- behavioral RED recorded;
- deterministic projection GREEN;
- Portland multi-lap characterization recorded;
- supported-path performance characterized;
- preparation workflow can explicitly use the derived reference as canonical `lap.distance`;
- canonical CI GREEN.

## Explicitly out of scope

- automatic best/reference lap selection;
- generated track centerline;
- map database matching;
- track-width model;
- GPS smoothing/filtering;
- multi-session reference merging;
- AI interpretation.
