# Plan 022 — GPS Path Distance Foundation

Status: **Active**

Started: 2026-09-23

## Objective

Define and validate the smallest deterministic GPS-derived distance artifact needed to advance licensed physical-car telemetry toward lap comparison without falsely treating raw GPS path length as an already-corrected common track reference.

## Why this plan exists

Plan 021 can now ingest the licensed Traqmate source.

The source provides:

- elapsed time;
- latitude;
- longitude;
- altitude;
- vehicle speed;
- source Lap.

It does **not** provide accepted `lap.distance`.

ADR-0009 requires a trustworthy monotonic distance reference before lap comparison.

Therefore the next engineering gap is positional-reference derivation.

## Critical distinction

Plan 022 deliberately separates two concepts:

### GPS path distance

Cumulative physical path length along one measured GPS trajectory.

This can be derived deterministically from latitude/longitude using an explicit geodesic model.

### Comparison reference distance

A common positional axis suitable for overlaying two laps at equivalent track positions.

This may require additional alignment/correction beyond independent cumulative GPS path length.

OME must not label raw cumulative GPS path length as corrected/common `lap.distance` until the comparison semantics are validated.

## Evidence basis

Authoritative geodesic references:

- PROJ geodesic calculations;
- GeographicLib WGS84 inverse geodesic;
- Karney geodesic algorithm as incorporated by PROJ/GeographicLib.

Motorsport practice cross-check:

- MoTeC i2 uses a corrected distance axis for meaningful lap overlay;
- corrected distance can compensate for lap-length variation;
- GPS itself has acquisition delay/quality considerations.

## Phase A — source GPS characterization

Before deriving distance, characterize the licensed Traqmate fixture:

- latitude/longitude finite range;
- sample cadence;
- duplicate consecutive coordinates;
- stationary periods;
- obvious jumps/outliers;
- source Lap transitions;
- per-lap GPS sample counts;
- approximate raw geodesic path length;
- relation between source velocity and geodesic incremental speed.

This phase is characterization only.

It must not mutate source data.

## Phase B — deterministic GPS path-distance contract

Define a source-independent derived artifact with:

- algorithm id/version;
- ellipsoid/model identity;
- input latitude/longitude evidence;
- optional altitude policy;
- cumulative distance in metres;
- per-segment distance;
- source timestamps;
- source dataset/lap context;
- quality/readiness issues.

Initial candidate:

`WGS84 inverse geodesic between consecutive accepted GPS samples`

using a deterministic, documented geodesic implementation.

## Altitude policy

Do not silently mix ellipsoidal surface distance with altitude.

The first decision must explicitly choose one of:

- 2D WGS84 surface geodesic only; or
- a separately defined 3D distance model.

The choice must be traceable.

## GPS quality policy

Do not silently smooth, remove or interpolate GPS points.

Potential problems must be explicit:

- duplicate coordinates;
- non-finite coordinates;
- impossible latitude/longitude;
- large jumps inconsistent with timing/vehicle evidence;
- long stationary periods;
- missing samples.

Any filtering/correction requires its own deterministic rule/version and tests.

## Relation to source speed

Source velocity is useful as validation evidence.

It is not automatically substituted for GPS-derived distance.

A comparison may examine:

```text
geodesic_segment_distance / delta_time
vs
source vehicle speed
```

to identify suspicious GPS geometry or timing.

This is a quality check, not a hidden correction.

## Comparison-reference gate

Plan 022 does **not** automatically declare GPS path distance to be canonical `lap.distance`.

Before that promotion, OME must answer:

- Are independently accumulated lap paths sufficiently comparable?
- How are start/finish offsets handled?
- How are path-length differences across racing lines handled?
- Is a lap-length normalization/correction needed?
- Would projection onto a common reference trajectory be more correct?

If raw path distance is not sufficient, the next plan must define a common-reference projection/correction algorithm.

## TDD rule

Any deterministic derivation behavior is test-first:

```text
ACCEPTED GPS DISTANCE CONTRACT
-> ANALYTIC SYNTHETIC GPS CASES
-> RED
-> MINIMUM DERIVATION
-> GREEN
-> REAL TRAQMATE CHARACTERIZATION
-> FULL VERIFY
```

Synthetic cases should include:

- identical points -> zero segment distance;
- known short WGS84 distance;
- cumulative path;
- invalid coordinate;
- duplicate point;
- time/source provenance;
- deterministic repeatability.

## Architecture boundary

GPS path-distance derivation belongs in deterministic transformation/analysis, not ingestion.

It must not:

- alter source channels;
- rewrite timestamps;
- normalize unrelated channels;
- organize laps inside the importer;
- hide GPS filtering;
- create causal engineering conclusions;
- depend on UI state;
- use AI for numerical distance.

## Completion criteria

- licensed Traqmate GPS characterized;
- WGS84/altitude/quality policy documented;
- derivation result/evidence contract documented;
- tests written before production derivation;
- behavioral RED recorded;
- deterministic GPS path-distance derivation GREEN;
- real fixture characterization recorded;
- explicit decision whether path distance is sufficient for ADR-0009 comparison;
- canonical CI GREEN.

## Explicitly out of scope

- corrected/common track-reference projection until evidence supports it;
- map matching;
- circuit centerline database;
- automatic track recognition;
- GPS smoothing without an accepted rule;
- Kalman filtering;
- setup/driver diagnosis;
- AI interpretation.
