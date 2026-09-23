# Brake Signal Semantics — Comparison Safety Research

Status: **Reviewed research**

Verified: 2026-09-22

## Purpose

Document why OME must not treat every source channel named "Brake" as the same engineering quantity.

This research supports Plan 012.

It is informative; accepted requirements/specs remain authoritative.

## Evidence reviewed

### iRacing public .ibt telemetry

Public fixture:

- repository: `teamjorge/ibt`
- file: `.testing/valid_test_file.ibt`

Observed source variables include:

- `Brake`
  - description: `0=brake released to 1=max pedal force`
  - unit: `%`
- `BrakeRaw`
  - description: raw brake input from released to maximum pedal force
  - unit: `%`
- ABS-related brake channels with different meanings.

This is a normalized driver-input / pedal-force demand signal, not hydraulic pressure.

### MoTeC positional brake example

Licensed TRACE fixture already vendored by OME:

`fixtures/public/trace/motec-canonical.csv`

Observed:

```text
Brake Pos
%
```

This represents brake position semantics.

### MoTeC pressure example

Representative public export:

- repository: `Arcayik/motec-csv`
- file: `data/1hz.csv`

Observed:

```text
Brake Press
bar
```

This is pressure, not pedal position.

## Engineering conclusion

The following are not automatically equivalent:

- normalized pedal position;
- normalized pedal-force demand;
- physical pedal force;
- master-cylinder pressure;
- brake-line pressure;
- binary brake state;
- ABS intervention/reduction.

A common display label does not make them the same measurement.

OME must preserve a machine-readable semantic identity in addition to:

- canonical concept;
- unit;
- source name;
- human-readable source semantics;
- transformation provenance.

## v0.1 semantic identities

Plan 012 defines two continuous brake semantics that may be overlaid when both sides match exactly:

```text
driver.brake.pedal_position_ratio
driver.brake.pedal_force_ratio
```

Both use canonical unit:

```text
1
```

They are **not interchangeable** with each other.

Pressure/force/binary-state semantics remain unsupported by the first brake overlay.

## Why exact semantic matching

Two laps may be compared safely only when both canonical brake series represent the same declared quantity.

Examples:

```text
pedal_position_ratio vs pedal_position_ratio -> comparable
pedal_force_ratio    vs pedal_force_ratio    -> comparable
pedal_position_ratio vs pedal_force_ratio    -> not comparable
pedal_position_ratio vs brake pressure       -> not comparable
```

## Architectural implication

OME needs a stable `semantic_id` carried through:

```text
NormalizationRule
-> NormalizationMapping
-> CanonicalSeriesEvidence
-> Analysis compatibility check
```

Human prose remains useful but is not a mechanical compatibility key.
