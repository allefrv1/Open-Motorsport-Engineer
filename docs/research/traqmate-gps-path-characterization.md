# Traqmate GPS Path Characterization

Status: **Reviewed research**

Date: 2026-09-23

## Purpose

Characterize the licensed physical-car Traqmate fixture before OME derives any positional reference from GPS.

This document records observations.

It does not itself define production behavior.

## Source

Fixture:

`fixtures/public/exit-speed/traqmate-parking-lot.csv`

Git blob:

`df9aaa9827b85d33c4df4d5dd11912955e2240cf`

Source family:

`Traqmate Trackvision V2`

## Recorded channels

The source provides:

- Elapsed Time;
- Lat (Degrees);
- Lon (Degrees);
- Altitude (meters);
- Velocity (MPH);
- Lap.

Declared sample rate:

`10 Hz`

## Basic shape

Observed:

- 1,962 telemetry samples;
- elapsed time from 0.0 s to 196.1 s;
- exact 0.1 s sample spacing;
- no non-positive time intervals;
- no non-finite values in the characterized channels;
- no identical consecutive latitude/longitude pairs.

Coordinate bounds:

- latitude: 45.695020833° to 45.695528167°;
- longitude: -121.526263167° to -121.525440333°;
- altitude: 144.6 m to 153.8 m.

## Source Lap transitions

Observed source Lap transitions:

- Lap 1 -> Lap 2 at 71.7 s;
- Lap 2 -> Lap 3 at 148.3 s.

Sample counts:

- Lap 1: 717 samples;
- Lap 2: 766 samples;
- Lap 3: 479 samples.

The source begins partway through Lap 1 and ends partway through Lap 3.

Lap 2 is the only clearly complete lap in this fixture.

## Preliminary horizontal path characterization

For characterization only, consecutive latitude/longitude samples were evaluated with a spherical great-circle approximation using mean Earth radius 6,371,008.8 m.

This approximation is **not** the accepted production algorithm.

Observed whole-file approximate horizontal path length:

`946.689 m`

Segment-length distribution:

- median: ~0.488 m;
- 95th percentile: ~0.589 m;
- 99th percentile: ~0.609 m;
- maximum: ~0.649 m.

No isolated multi-metre GPS jumps were observed at the 10 Hz cadence.

## Relation to recorded vehicle speed

The source Velocity channel was converted only for characterization:

`mph * 0.44704 -> m/s`

Approximate GPS segment speed and source vehicle speed are closely aligned.

Observed ratio of approximate GPS speed to source speed:

- median: ~1.0033;
- 95th percentile: ~1.0587.

This supports internal coherence between geometry, timing and source speed.

It does not prove absolute GPS accuracy.

## Per-lap characterization

### Lap 1

- duration: 71.6 s;
- approximate GPS path: 340.388 m;
- trapezoidal source-speed integral: 336.479 m;
- difference: +1.162%;
- start/end horizontal gap: 44.298 m.

The large closure gap confirms this is a partial lap.

### Lap 2

- duration: 76.5 s;
- approximate GPS path: 390.414 m;
- trapezoidal source-speed integral: 387.938 m;
- difference: +0.638%;
- start/end horizontal gap: 1.083 m.

This is the strongest complete-lap candidate in the fixture.

### Lap 3

- duration: 47.8 s;
- approximate GPS path: 214.826 m;
- trapezoidal source-speed integral: 216.599 m;
- difference: -0.819%;
- start/end horizontal gap: 21.417 m.

The closure gap confirms this is a partial lap.

## Engineering interpretation of the characterization

The licensed fixture is suitable for testing a deterministic GPS path-distance derivation because:

- cadence is regular;
- GPS samples are finite;
- no obvious geometric jumps were found;
- source speed broadly agrees with GPS movement;
- one source lap is clearly complete.

However, this evidence does **not** justify treating independently accumulated GPS path length as a corrected/common comparison axis.

Different racing lines and GPS noise can produce different lap path lengths.

## External numerical references

OME's production candidate is based on the WGS84 inverse geodesic problem as implemented by robust geodesic libraries such as PROJ/GeographicLib.

Relevant references:

- https://proj.org/en/stable/geodesic.html
- https://geographiclib.sourceforge.io/

The production implementation should not use the spherical approximation used in this characterization.

## Motorsport cross-check

MoTeC i2 distinguishes distance suitable for overlays from raw source measurement through a corrected-distance workflow.

Public MoTeC training material describes Corrected Distance as the axis used for meaningful same-position lap comparison and notes that lap lengths may be adjusted for consistent comparison.

This reinforces the OME distinction:

```text
GPS path distance
!= automatically
corrected/common lap comparison distance
```

## External Portland multi-lap check

The larger Apache-2.0 Portland source was inspected externally:

- Git blob: `13fed5ffe15ad35dc668ea2b4df8acdc63ae7668`;
- 97,980 telemetry rows;
- 40 Hz;
- source Lap markers 0–20.

A research-only spherical great-circle calculation was used to compare marker-to-marker path lengths. This calculation is not the production Plan 022 WGS84 implementation.

The stable complete-lap population, laps 2–18, showed:

- mean path length ~3,151.87 m;
- standard deviation ~4.10 m;
- coefficient of variation ~0.13%;
- range ~18.28 m.

This is small relative to circuit length, but it is large enough to matter for same-position delta-time and channel overlays if independent accumulated path distance is treated as a common axis.

The variation is also physically plausible because racing-line path length is not identical lap to lap.

## Conclusion

The licensed Traqmate GPS is coherent enough for deterministic WGS84 horizontal `gps.path_distance`.

The production derivation is now validated on the committed physical-car fixture.

However, independent per-lap `gps.path_distance` is **not sufficient by itself** to satisfy ADR-0009's common positional-reference semantics.

OME should next define a common reference trajectory/projection or corrected-distance transformation rather than silently aliasing GPS path distance to canonical `lap.distance`.
