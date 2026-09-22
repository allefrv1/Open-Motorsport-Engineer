# OME CSV Exchange Profile v0.1

Status: **Accepted for fixtures and simple interchange**

## Purpose

The OME CSV Exchange Profile provides a simple, human-inspectable format for:

- deterministic test fixtures;
- examples;
- simple data interchange;
- early vertical-slice validation.

It is **not** the canonical internal telemetry model.

It is not intended to represent every possible professional DAQ dataset losslessly.

## Design choice

Version 0.1 is deliberately limited to a **single shared time base**.

If a source contains channels with independent sample rates/time bases, converting it to this profile requires an explicit transformation and must not be treated as a lossless raw import.

Source-specific importers may represent multi-rate data directly through the Telemetry Import Model instead.

## Files

A profile instance consists of:

```text
<name>.csv
<name>.ome.json
```

The CSV stores samples.

The required JSON sidecar stores source metadata and channel definitions.

## CSV rules

- UTF-8 text without implicit encoding conversion;
- comma delimiter;
- decimal point `.`;
- first row contains identifiers;
- first column is exactly `time_s`;
- `time_s` is a finite decimal number in seconds from the dataset's declared reference origin;
- timestamps are strictly increasing;
- at least one non-time channel exists;
- remaining column identifiers are unique;
- remaining column identifiers exactly match the set of sidecar `channels` keys;
- CSV column order is the authoritative source-channel order; JSON object member order is not semantically significant;
- all remaining columns share the CSV time base;
- empty channel cells represent missing source samples and must not be silently filled;
- channel cells are ingested as source values without implicit unit conversion or normalization;
- at least one sample row is required.

Example:

```csv
time_s,speed_src,throttle_src,brake_src,steering_src,rpm_src
0.000,42.10,100,0,0.2,5120
0.010,42.25,100,0,0.3,5145
0.020,42.40,98,0,0.4,5170
```

## Sidecar contract

The machine-readable schema is:

`ome-csv-profile-v0.1.schema.json`

Required top-level fields:

- `ome_csv_version` — exactly `"0.1"`;
- `source`;
- `channels`.

### source

Required:

- `description` — non-empty string.

Optional:

- `system` — string or null.

### sample_rate_hz

Optional positive finite number.

It describes the shared acquisition rate when the producer knows it.

OME must not infer a missing `sample_rate_hz` silently from timestamps during ingestion.

### channels

A non-empty object keyed by the exact CSV column identifier.

JSON object member order is not significant. The CSV header defines channel ordering.

Each channel requires:

- `source_name` — the original/source-facing name, non-empty string.

Optional:

- `unit` — string or null;
- `description` — string or null;
- `data_type` — source-declared type description, string or null.

An empty string unit represents an explicitly unitless channel.

A missing/null unit represents unknown metadata.

Unknown additional channel fields may be preserved as source metadata but do not acquire OME engineering meaning automatically.

### context

Optional object for source-provided operational context such as Session / Run / Lap markers.

Ingestion preserves it.

Its presence does not authorize generic boundary inference.

### source_provenance

Optional object containing provenance supplied by the producer/source.

OME preserves it as source metadata.

## Example sidecar

```json
{
  "ome_csv_version": "0.1",
  "source": {
    "system": "example",
    "description": "Controlled OME fixture"
  },
  "sample_rate_hz": 100.0,
  "channels": {
    "speed_src": {
      "source_name": "GPS Speed",
      "unit": "km/h",
      "data_type": "float"
    },
    "throttle_src": {
      "source_name": "Throttle Position",
      "unit": "%",
      "data_type": "float"
    }
  },
  "context": {
    "lap": 3
  }
}
```

## Channel identifiers

CSV column identifiers are stable profile identifiers, not canonical engineering concepts.

The sidecar preserves the original source name.

Future normalization may map:

```text
speed_src
  -> vehicle.speed
```

without erasing `source_name = "GPS Speed"`.

## Source-value policy

The ingestion layer preserves non-time CSV cells as source values.

It does not infer a canonical engineering data type from lexical appearance.

For example, an importer must not decide that every text resembling an integer is semantically a gear or counter.

A later validated transformation may create typed/canonical representations when required.

## Lap context

Version 0.1 may include explicit lap metadata in `context` or an explicit lap source column.

Automatic lap detection is not part of this profile.

## Limitations

Version 0.1 does not natively represent:

- multiple independent time bases;
- event streams with different clocks;
- raw CAN frames;
- complex arrays/maps;
- binary attachments;
- synchronized video;
- high-fidelity lossless conversion of arbitrary MoTeC/MDF data.

These limitations are intentional.

## Rule

Do not expand this profile merely to imitate a full measurement-data standard.

When a dataset needs richer representation, the source adapter/internal telemetry layer should handle it rather than forcing everything into CSV.
