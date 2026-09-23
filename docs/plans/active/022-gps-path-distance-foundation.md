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

## Reviewed characterization and accepted v0.1 contract

Reviewed source characterization:

- `docs/research/traqmate-gps-path-characterization.md`

Accepted Plan 022 numerical contract:

- `docs/specs/gps-path-distance-v0.1.md`

Key v0.1 decisions:

- derived concept: `gps.path_distance`;
- WGS84 inverse geodesic between consecutive latitude/longitude samples;
- 2D horizontal distance only;
- altitude preserved separately and excluded from distance;
- no smoothing, filtering, map matching or point deletion;
- duplicate coordinates remain valid zero-distance segments;
- source timestamps must be strictly increasing;
- result retains algorithm/provenance evidence;
- no automatic promotion to canonical `lap.distance`.

## Phase A — source GPS characterization

Completed characterization of the licensed Traqmate fixture covered:

- latitude/longitude finite range;
- sample cadence;
- duplicate consecutive coordinates;
- stationary periods;
- obvious jumps/outliers;
- source Lap transitions;
- per-lap GPS sample counts;
- approximate raw geodesic path length;
- relation between source velocity and geodesic incremental speed.

This phase is complete and did not mutate source data.

The fixture shows a coherent 10 Hz GPS path and one clearly complete source lap, with no obvious geometric jumps in the characterized data.

## Phase B — deterministic GPS path-distance contract

The v0.1 contract is accepted for Plan 022.

The source-independent derived artifact contains:

- algorithm id/version;
- ellipsoid/model identity;
- input latitude/longitude evidence;
- optional altitude policy;
- cumulative distance in metres;
- per-segment distance;
- source timestamps;
- source dataset/lap context;
- quality/readiness issues.

Selected baseline:

`WGS84 inverse geodesic between consecutive source GPS samples`

using GeographicLib-compatible ellipsoidal geodesic semantics.

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

## TDD execution evidence

Behavioral RED:

- OME CI #266;
- expected failure: `ImportError: cannot import name 'GPSPathDistanceEngine' from 'ome.analysis'`.

Implementation feedback:

- OME CI #270/#271 — formatting-only harness feedback.

GREEN:

- OME CI #272 — complete canonical verify passed with the WGS84 GeographicLib implementation.

Real physical-car characterization:

- OME CI #274 — complete canonical verify passed with the licensed Traqmate fixture characterization.

No product test was removed or weakened to obtain GREEN.

## Real-fixture result

The committed licensed Traqmate fixture proves the derivation works on physical-car telemetry:

- 1,962 samples derive successfully;
- the whole-file WGS84 horizontal path is within the independently characterized ~947 m range;
- source Lap 2 has 766 samples and derives a ~390 m closed path;
- the Lap 2 start/end geographic closure is below 2 m;
- GPS path distance and trapezoidal source-speed integration differ by less than 2%.

## External multi-lap comparison-reference validation

The Apache-2.0 Portland source was inspected externally without adding the ~20 MB file to OME:

- repository: `djhedges/exit_speed`;
- blob: `13fed5ffe15ad35dc668ea2b4df8acdc63ae7668`;
- 97,980 telemetry rows;
- 40 Hz declared sample rate;
- source Lap markers 0–20.

A research-only spherical great-circle characterization of marker-to-marker laps found:

- laps 2–18 form the stable complete-lap population;
- mean path length: ~3,151.87 m;
- standard deviation: ~4.10 m;
- coefficient of variation: ~0.13%;
- minimum: ~3,144.45 m;
- maximum: ~3,162.74 m;
- range: ~18.28 m;
- most start/end closure gaps are sub-metre;
- path distance and source-speed integration are generally within about 0.2–0.3%.

The external characterization approximation is not the production WGS84 algorithm.

Its purpose is to test whether independent per-lap path accumulation is semantically stable enough to become a shared comparison axis.

## Comparison-reference decision

`gps.path_distance` is **not promoted directly to canonical `lap.distance`**.

Reason:

- path distance measures the actual trajectory travelled by each lap;
- different racing lines legitimately produce different path lengths;
- GPS measurement noise also contributes variation;
- an equal cumulative path-distance value on two independently accumulated laps is therefore not guaranteed to represent the same physical track position.

The Portland multi-lap evidence shows non-zero lap-length variation even across a stable run.

The next plan must define a deterministic common track reference/projection or corrected-distance method before physical-car GPS telemetry can satisfy ADR-0009 comparison readiness.

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
