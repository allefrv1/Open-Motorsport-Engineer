# MoTeC CSV Export Contract for Plan 008

Status: **Reviewed research**

Verified: 2026-09-22

## Purpose

Define the minimum evidence-backed MoTeC CSV contract needed for OME's first professional real-motorsport source adapter.

This document is informative research.

Accepted OME requirements, architecture and Plan 008 remain authoritative.

## Source basis

Official MoTeC evidence:

- i2 product page:
  - https://www.motec.com.au/products/I2
- i2 API User Guide:
  - https://website.motec.com.au/hessian/uploads/i2_API_User_Guide_330ed28c83.pdf

The official product documentation states that channel data may be exported for an outing, lap or selected range as CSV.

The API guide exposes `ExportMainAsCSV` and describes its output as a MoTeC CSV file.

Public structural cross-checks:

- TRACE canonical/negative fixtures:
  - https://github.com/keystroke-tools/TRACE
- B'Energy Racing MoTeC CSV writer:
  - https://github.com/BenergyRacing/racing-data-converter
- Rutgers Formula SAE MoTeC CSV test data:
  - https://github.com/rutgers-fsae/firmware
- additional compatible/public examples discovered through GitHub.

OME does not copy third-party parser implementations.

## Format identity

The first parsed CSV record identifies the source family:

```text
Format,MoTeC CSV File
```

Quoted and unquoted CSV fields are equivalent after CSV parsing:

```text
"Format","MoTeC CSV File"
```

Plan 008 will claim a `.csv` source only when the parsed first non-empty row begins with:

```text
["Format", "MoTeC CSV File"]
```

A generic `.csv` without this signature is not a MoTeC source.

## Preamble

MoTeC CSV exports may contain metadata rows before channel data.

Observed keys include:

- Format;
- Venue;
- Vehicle;
- Driver;
- Device;
- Comment;
- Session;
- Log Date;
- Log Time;
- Origin Time;
- Start Time;
- End Time;
- Sample Rate;
- Duration;
- Range;
- Start Distance;
- End Distance;
- Beacon Markers;
- Workbook;
- Worksheet.

Not every export includes every field.

Rows may contain more than one metadata key/value pair, separated by empty CSV fields.

Example shape:

```text
"Sample Rate","100.000","Hz",,"End Time","0.030","s"
```

OME should preserve the complete parsed preamble rows, not only a curated dictionary.

Selected well-known metadata may also be extracted into source metadata when the interpretation is unambiguous.

## Blank rows

Public examples commonly include blank records between:

- metadata and channel names;
- units and sample data.

Blank records are structural separators and should be ignored while locating the channel/unit/data sections.

They should not create telemetry samples.

## Channel header and unit row

The first Plan 008 slice recognizes a source data table where:

1. the first channel-header cell is exactly `Time`;
2. the next non-empty row is the unit row;
3. the first unit cell is exactly `s`.

Example:

```text
Time,Ground Speed,Engine RPM,Gear
s,km/h,rpm,
```

This is deliberately narrower than "parse any CSV that resembles telemetry".

## Source channel names

Channel names are source evidence and must be preserved exactly in:

`SourceChannel.original_name`

OME must not canonicalize:

```text
Ground Speed
-> vehicle.speed
```

during ingestion.

That remains normalization work.

## Duplicate source channel names

Public MoTeC-compatible examples show that channel names are not guaranteed to be unique.

Therefore source-facing name and technical OME identifier must remain separate concepts.

Plan 008 rule:

- preserve every source header verbatim as `original_name`;
- use the exact name as `identifier` when it is unique within the source table;
- for duplicates, assign a deterministic occurrence suffix:
  - first occurrence: `Time`;
  - second occurrence: `Time#2`;
  - third occurrence: `Time#3`;
- record the zero-based source column index and occurrence number in `source_attributes`.

The suffix is a technical disambiguator.

It must never be presented as if the source itself named the channel `Time#2`.

## Time basis

For the first Plan 008 slice, the first source column is the explicit time basis:

```text
original_name = Time
unit = s
```

Its cells are parsed as finite decimal seconds for `SampleSeries.timestamps_s`.

The `Time` source channel itself remains present.

Its source cell values should remain source-facing CSV values rather than being replaced by a derived/canonical representation.

OME must not derive timestamps from row number or sample rate.

## Source cell values

MoTeC CSV is text.

Therefore non-time source cells are preserved lexically:

- `"50"` remains source value `"50"`;
- `"N"` remains `"N"`;
- `"not available"` remains `"not available"`.

An empty telemetry cell represents an absent source cell and may be represented as `None`.

The importer must not silently convert:

- numeric-looking text to float/int;
- gear `N` to a canonical gear number;
- `not available` to null;
- percentages or units.

Typed/canonical conversion remains a later validated transformation.

## Units

The unit row belongs to source metadata.

Rules:

- non-empty unit text is preserved exactly;
- an empty unit cell means explicitly unitless;
- channel count and unit count must match.

No unit conversion occurs during import.

## Sample rate

Public/official-compatible exports may include explicit metadata such as:

```text
Sample Rate,100.000,Hz
```

When a verified metadata row supplies a finite positive numeric value with unit `Hz`, OME may preserve:

`sample_rate_hz = 100.0`

for channels in that exported table.

When `Sample Rate` is absent, OME must leave sample rate unknown.

OME must not infer sample rate from time spacing during ingestion.

## Metadata preservation

Recommended source metadata representation:

- `motec_preamble_rows` — immutable tuple of parsed CSV rows;
- selected extracted values such as:
  - `sample_rate_hz`;
  - `venue`;
  - `vehicle`;
  - `driver`;
  - `device`;
  - `range`;
  - `beacon_markers`.

Extraction is optional convenience.

The raw preamble remains the evidence source.

## Structural validity vs telemetry validity

Import and validation remain separate.

A MoTeC CSV with decreasing timestamps can still be structurally readable.

For example:

```text
Time,Ground Speed
s,km/h
1,36
0,72
```

Plan 008 should import those source rows if the CSV structure is valid.

The validation layer then reports non-monotonic time.

Importer behavior:

```text
read source
-> preserve values
-> create ImportedTelemetryDataset
```

Validation behavior:

```text
inspect timestamps
-> blocking time-order issue
```

The importer must not repair, sort or discard rows.

## Row shape

Every non-empty telemetry data row must contain the same number of fields as the channel header.

A structurally short/long data row fails import explicitly.

At least one telemetry data row is required.

## Encoding

The first Plan 008 slice uses UTF-8 text.

Encoding fallback is not added without evidence/requirement.

An unreadable/non-UTF-8 source fails explicitly.

## Adapter arbitration

OME CSV and MoTeC CSV both use `.csv`.

They are distinguished by contracts:

```text
OME CSV
-> .csv + required sibling .ome.json

MoTeC CSV
-> .csv + parsed first non-empty row ["Format", "MoTeC CSV File"]
```

An arbitrary CSV satisfying neither contract stays unsupported.

Tests must prove both adapters can coexist regardless of registration order.

## Licensed canonical fixture

OME already vendors the MIT-licensed TRACE fixture:

`fixtures/public/trace/motec-canonical.csv`

Observed:

- source signature;
- metadata preamble;
- 13 source channels;
- unit row;
- two samples;
- mixed numeric/discrete text;
- explicit `not available` source value;
- no explicit Sample Rate metadata.

It is appropriate for deterministic CI.

## Negative fixture

OME also vendors:

`fixtures/public/trace/motec-decreasing-time.csv`

This is used to prove import/validation responsibility separation.

## External validation

TRACE is synthetic.

An additional public representative export was inspected externally:

- repository: `Arcayik/motec-csv`;
- path: `data/1hz.csv`;
- Git blob: `55de91dbabaa04e4a8f5c37b8e5a3717fc9e3b9c`.

Observed structure:

- standard MoTeC CSV signature;
- richer 12-row metadata preamble;
- venue/vehicle/driver/device/date/time/range/beacon metadata;
- explicit `Sample Rate = 1.000 Hz`;
- 15 source channels;
- 305 data rows;
- consistent row width;
- finite, strictly increasing Time from 0 s through 304 s.

The file is useful as an external format-compatibility cross-check.

OME does not classify it as a licensed physical race-team telemetry fixture.

A redistributable physical-car MoTeC export with clear permission remains an outreach/data gap.

## Safety rules

Reject explicitly when:

- source signature does not match;
- no usable Time/unit/data table exists;
- first time unit is not seconds for this first slice;
- header/unit counts differ;
- duplicate technical identifiers cannot be generated deterministically;
- a non-empty data row has the wrong field count;
- time cell is empty, non-numeric or non-finite;
- there are no data rows;
- text cannot be decoded as UTF-8.

Do not reject solely because:

- source values contain non-numeric text;
- sample rate is missing;
- timestamps decrease;
- a channel unit is empty.

## Conclusion

The format contract is sufficiently constrained for a genuine TDD first adapter:

```text
verified source structure
-> tests over licensed fixtures
-> behavioral RED
-> minimal MoTeC CSV importer
-> GREEN
```

The importer preserves evidence.

It does not perform validation, normalization or engineering interpretation.
