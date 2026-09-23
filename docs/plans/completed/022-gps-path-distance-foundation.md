# Plan 022 — GPS Path Distance Foundation

Status: **Completed**

Started: 2026-09-23

Completed: 2026-09-23

## Objective

Define and implement deterministic WGS84 GPS path-distance derivation for physical-car telemetry without falsely equating per-lap travelled path with a common lap-comparison axis.

## Delivered

- licensed Traqmate GPS characterization;
- accepted `gps.path_distance` v0.1 specification;
- `geographiclib==2.1` pinned and locked;
- deterministic WGS84 inverse-geodesic segment distance;
- cumulative horizontal path distance;
- typed GPS source evidence/provenance;
- explicit readiness failures for invalid coordinates, units, timing and provenance;
- no altitude mixing;
- no filtering, smoothing, map matching or hidden point deletion;
- physical-car characterization tests;
- external Portland multi-lap comparison-reference study.

## TDD evidence

Behavioral RED:

- CI #266 — `GPSPathDistanceEngine` absent.

Implementation feedback:

- CI #270/#271 — formatting-only harness feedback.

GREEN:

- CI #272 — complete canonical verify passed.

Physical-car characterization:

- CI #274 — real Traqmate WGS84 characterization passed.

Final documentation/decision verify:

- CI #276 — complete canonical verify passed.

## Physical-car evidence

Committed Traqmate fixture:

- 1,962 samples;
- stable 10 Hz;
- one clearly complete source Lap 2;
- derived WGS84 path around 390 m;
- start/end closure below 2 m;
- path length within 2% of source-speed integration.

External Portland source:

- 97,980 telemetry rows;
- 40 Hz;
- source Lap markers 0–20;
- stable complete-lap population 2–18;
- approximate per-lap travelled-path mean ~3,151.87 m;
- standard deviation ~4.10 m;
- range ~18.28 m.

## Architectural decision

`gps.path_distance` is not automatically promoted to canonical `lap.distance`.

Independent cumulative travelled path is lap-specific.

Different racing lines and GPS measurement variation mean equal cumulative travelled distance does not guarantee equal physical track position.

ADR-0009 requires a common positional reference.

## Next gap

A deterministic common track-reference transformation is required.

The next slice must evaluate:

- explicit reference-lap geometry;
- projection of candidate GPS positions onto that geometry;
- circular start/finish seam handling;
- monotonicity/readiness;
- lateral projection error;
- provenance and reference identity.

## Merge evidence

PR #54 was squash-merged as:

`e364de39de52e3cc7e347d222331f9f2ed109962`

## Completion assessment

All Plan 022 completion criteria are satisfied.

The comparison-reference question is explicitly transferred to Plan 023.
