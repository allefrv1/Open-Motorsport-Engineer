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

The JSON sidecar stores metadata and channel definitions.

The sidecar is required for an OME CSV Profile dataset.

## CSV rules

- UTF-8 text;
- comma delimiter;
- decimal point `.`;
- first row contains channel identifiers;
- first column is `time_s`;
- `time_s` is seconds from the dataset's declared reference origin;
- timestamps must be strictly increasing;
- all remaining columns share the CSV time base;
- empty values represent missing samples and must not be silently filled;
- no unit conversion is implied by the CSV itself.

Example:

```csv
time_s,speed_src,throttle_src,brake_src,steering_src,rpm_src
0.000,42.10,100,0,0.2,5120
0.010,42.25,100,0,0.3,5145
0.020,42.40,98,0,0.4,5170
```

## Sidecar metadata

The sidecar must identify:

- profile version;
- dataset/source description;
- source-system identity if known;
- channel definitions;
- unit for each channel when known;
- original source name for each channel;
- optional sample-rate declaration;
- optional session/run/lap metadata;
- optional source provenance.

Conceptual example:

```json
{
  "ome_csv_version": "0.1",
  "source": {
    "system": "example",
    "description": "Controlled OME fixture"
  },
  "channels": {
    "speed_src": {
      "source_name": "GPS Speed",
      "unit": "km/h"
    },
    "throttle_src": {
      "source_name": "Throttle Position",
      "unit": "%"
    }
  }
}
```

This example is explanatory, not an implementation schema.

A machine-readable schema may be defined when implementation begins.

## Channel identifiers

CSV column identifiers are stable profile identifiers, not necessarily canonical engineering concepts.

The sidecar preserves the original source name.

Future normalization may map:

```text
speed_src
  -> vehicle.speed
```

without erasing `source_name = "GPS Speed"`.

## Lap context

Version 0.1 may include explicit lap metadata in the sidecar or an explicit lap identifier column when fixtures require it.

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

When a dataset needs richer representation, the source adapter/internal model should handle it rather than forcing everything into CSV.
