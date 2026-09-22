# Canonical Telemetry Concepts v0.1

Status: **Accepted for the first vertical slice**

## Purpose

This vocabulary defines the minimum source-independent telemetry concepts needed for the first OME lap-comparison workflow.

It does not attempt to define the complete motorsport telemetry ontology.

## Rule

A canonical concept is not a replacement for the source channel.

The relationship is:

```text
SourceChannel
  -> explicit normalization mapping
  -> CanonicalConcept
```

The source name, source unit and provenance remain available.

## Initial concepts

### time.elapsed

Meaning:

Elapsed measurement time relative to a declared dataset/lap reference.

Canonical unit:

- seconds

### lap.distance

Meaning:

Monotonic distance along the current lap/reference path.

Canonical unit:

- meters

Requirements:

- must be suitable for deterministic lap alignment;
- must be monotonic within the comparable lap region;
- provenance must identify whether it came from source data or an explicit deterministic derivation.

### vehicle.speed

Meaning:

A normalized vehicle-speed concept only when the mapping rule knows which source measurement is being represented.

Canonical unit:

- meters per second

Important:

GPS speed, ECU speed and wheel speed remain distinct source channels. Mapping one of them to `vehicle.speed` must preserve source identity and method.

### driver.throttle

Meaning:

Driver throttle demand/position when the source semantics are known.

Canonical representation:

- dimensionless normalized fraction in `[0, 1]` when a deterministic conversion is valid.

The original percentage/voltage/unit remains part of source provenance.

### driver.brake

Meaning:

A source-independent driver braking input concept only when source semantics are sufficient.

No universal canonical physical unit is imposed in v0.1 because sources may expose:

- pedal position;
- pedal force;
- master-cylinder pressure;
- brake pressure;
- binary brake state.

These are not automatically equivalent.

For comparison, the exact source/mapping subtype must remain visible.

### driver.steering

Meaning:

Steering input when the source semantics and sign convention are known.

Canonical unit:

- radians

Sign convention must be explicitly documented by the normalization rule.

### engine.speed

Meaning:

Engine rotational speed.

Canonical unit:

- radians per second internally when physics calculations require SI.

Display may use RPM.

The source value and unit remain preserved.

### transmission.gear

Meaning:

Selected/engaged gear as supplied by a trustworthy source.

Canonical representation:

- discrete semantic value.

Neutral/reverse/unknown behavior must be defined by the source mapping rather than guessed.

## Units policy

Canonical physical quantities should use SI-compatible units internally when conversion is unambiguous and deterministic.

UI display units may differ.

Every conversion must retain:

- original value/unit;
- target unit;
- conversion rule/version.

## Deferred concepts

Not part of the v0.1 minimum vocabulary:

- yaw rate;
- lateral/longitudinal acceleration;
- wheel speeds;
- tyre pressures/temperatures;
- suspension position/velocity;
- brake pressure canonicalization;
- GPS coordinates;
- ride height;
- aero channels;
- powertrain health.

They will be added when a requirement needs them.
