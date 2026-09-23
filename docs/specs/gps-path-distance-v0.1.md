# GPS Path Distance Specification v0.1

Status: **Accepted for Plan 022**

Date: 2026-09-23

## Purpose

Define the first deterministic OME transformation from paired geographic latitude/longitude samples to cumulative horizontal GPS path distance.

This specification does **not** define corrected/common track distance for two-lap comparison.

## Derived concept

Artifact:

`gps.path_distance`

Unit:

`m`

Meaning:

Cumulative horizontal WGS84 geodesic path length through the supplied ordered GPS samples.

This is a derived measurement artifact.

It is not source telemetry and is not automatically canonical `lap.distance`.

## Inputs

Required:

- latitude series;
- longitude series;
- source timestamps;
- dataset fingerprint;
- source channel identities;
- source units;
- transformation/source provenance.

Expected units:

- latitude: degrees;
- longitude: degrees;
- time: seconds.

## Input readiness

The transformation is not ready when:

- latitude evidence is missing;
- longitude evidence is missing;
- timestamp evidence is missing;
- series lengths differ;
- fewer than two paired samples exist;
- any latitude/longitude/time value is non-numeric or non-finite;
- latitude is outside [-90, 90];
- longitude is outside [-180, 180];
- timestamps are not strictly increasing;
- required provenance is missing;
- source units are incompatible with the contract.

No source point is silently removed to make the transformation ready.

## Geodesic model

Use the WGS84 reference ellipsoid.

For every consecutive pair:

```text
(lat[i-1], lon[i-1])
(lat[i],   lon[i])
```

solve the inverse geodesic problem and obtain horizontal surface distance:

`segment_distance_m[i]`

The numerical implementation must use a robust WGS84 ellipsoidal geodesic algorithm.

Baseline implementation identity:

`ome.gps-path-distance.wgs84-geodesic`

Version:

`0.1.0`

## Numerical implementation

The first implementation should use GeographicLib-compatible WGS84 inverse-geodesic semantics.

OME must not implement a home-grown haversine approximation as the production algorithm.

A dependency is acceptable when it provides a well-established geodesic implementation and remains isolated behind the deterministic transformation boundary.

## Altitude policy

v0.1 is strictly **2D horizontal geodesic distance**.

Altitude is not included in distance.

Reasons:

- the Traqmate fixture does not define altitude datum/accuracy semantics sufficiently for a 3D distance contract;
- vertical GPS error can contaminate path length;
- ADR-0009 comparison needs a stable horizontal positional reference first.

Altitude remains available as independent source evidence.

A future 3D path metric requires a separate versioned specification.

## Cumulative output

For N samples:

```text
segment_distance_m[0] = 0.0
path_distance_m[0] = 0.0

for i > 0:
    segment_distance_m[i] = geodesic(sample[i-1], sample[i])
    path_distance_m[i] = path_distance_m[i-1] + segment_distance_m[i]
```

Output length equals input length.

## Duplicate coordinates

Two identical consecutive geographic coordinates are valid.

They produce:

`segment_distance_m = 0.0`

OME does not delete or interpolate the point.

A zero-distance segment may later be surfaced as quality evidence when relevant.

## GPS filtering policy

v0.1 performs no:

- smoothing;
- interpolation;
- outlier deletion;
- map matching;
- Kalman filtering;
- speed-based point replacement;
- coordinate repair.

If future evidence requires filtering, it must be a separate explicit transformation with its own algorithm id/version and tests.

## Source-speed relationship

Recorded vehicle speed is not an input to the distance calculation.

It may be used by a separate quality/validation check to compare:

`segment_distance / delta_time`

against source vehicle speed.

Such a check must not silently alter path distance.

## Result contract

A successful result contains:

- source dataset fingerprint;
- source latitude channel evidence;
- source longitude channel evidence;
- source timestamp evidence;
- algorithm id/version;
- ellipsoid identity = WGS84;
- altitude policy = ignored-for-horizontal-distance;
- source timestamps;
- per-sample segment distance in metres;
- cumulative path distance in metres;
- total path distance;
- output unit.

## Provenance chain

Conceptually:

```text
GPSPathDistanceResult
  -> WGS84 Geodesic Transformation
  -> Latitude / Longitude Source Evidence
  -> Source Timestamps
  -> Original Dataset
```

## Determinism

For equivalent input values, provenance-relevant parameters and algorithm version, numerical output must be deterministic within the implementation's documented floating-point behavior.

## Relationship to lap comparison

This specification intentionally does not promote:

`gps.path_distance`

to:

`lap.distance`

ADR-0009 requires a trustworthy comparison reference.

After real-lap derivation is implemented, OME must evaluate whether independent per-lap path distance is adequate or whether a common reference trajectory/correction is required.

## TDD cases

Before production implementation, tests should cover:

- identical points -> zero segment distance;
- known WGS84 short-distance result;
- cumulative multi-segment path;
- deterministic repeatability;
- invalid latitude;
- invalid longitude;
- non-finite coordinate;
- mismatched lengths;
- non-increasing time;
- duplicate coordinates preserved;
- provenance and algorithm identity;
- altitude does not affect v0.1 result.

## Related artifacts

- Plan 022 — GPS Path Distance Foundation
- ADR-0009 — Align initial lap comparisons by monotonic lap distance
- Traqmate GPS Path Characterization
