# Plan 008 — MoTeC CSV Adapter Foundation

Status: **Active**

Started: 2026-09-22

## Objective

Implement the first professional real-motorsport source adapter through MoTeC i2 CSV export while preserving source evidence and avoiding assumptions that belong to normalization or analysis.

## Requirement

Primary:

- REQ-001 — Import Telemetry Session

Supporting sources:

- `docs/research/initial-source-feasibility.md`
- `docs/research/public-telemetry-datasets.md`
- `fixtures/public/trace/motec-canonical.csv`
- `fixtures/public/trace/motec-decreasing-time.csv`

## Planning precedence

REQ-001 defines the initial source sequence as:

1. OME CSV Profile;
2. iRacing `.ibt`;
3. MoTeC CSV export.

Therefore MoTeC CSV is implemented before the lap-comparison phase.

## Source detection

MoTeC CSV shares the generic `.csv` extension with other formats.

The adapter must not claim arbitrary CSV files.

Initial detection must require a verified MoTeC export signature/structure, such as the source metadata line:

```text
Format,MoTeC CSV File
```

Detection rules must be backed by fixtures/research before production code.

### Adapter arbitration

OME CSV and MoTeC CSV must coexist in `TelemetryImportService`.

Their ownership rules are distinct:

- OME CSV is claimed only when the required `.ome.json` sidecar is present;
- MoTeC CSV is claimed only when verified MoTeC CSV structure/signature is present;
- an arbitrary `.csv` with neither contract remains unsupported.

Tests must prove that adapter order does not cause a MoTeC file to be interpreted as OME CSV or vice versa.

## Verified format contract

Plan 008 now has an evidence-backed parsing contract:

- `docs/research/motec-csv-format-contract.md`

Key decisions:

- detect parsed `Format,MoTeC CSV File` signature, not extension alone;
- preserve complete preamble rows;
- first data column must be `Time [s]` for this slice;
- preserve CSV telemetry cells lexically;
- preserve duplicate source names while assigning deterministic technical identifiers;
- preserve explicit Sample Rate metadata when supplied;
- never infer missing sample rate from timestamps;
- import structurally readable decreasing-time data and leave the defect to validation.

## Known fixture structure

The licensed TRACE canonical fixture contains:

```text
Format,MoTeC CSV File
Venue,Synthetic Circuit
Vehicle,Fixture Car
Driver,TRACE Test Driver
Time,Throttle Pos,...,Damper FL
s,%,...,mm
12.5,50,...,42.5
12.55,100,...,not available
```

Important properties:

- metadata preamble before channel headers;
- source-facing channel names;
- a separate unit row;
- explicit `Time` channel in seconds;
- numeric and discrete source values;
- missing-like source text such as `not available`;
- no project sidecar;
- sample rate not explicitly supplied by this fixture.

The importer must preserve these facts rather than silently interpreting them.

## TDD rule

Production behavior is test-first:

```text
VERIFIED MOTEC CSV CONTRACT
-> TEST / LICENSED FIXTURE
-> RED FOR EXPECTED MISSING ADAPTER BEHAVIOR
-> MINIMUM IMPLEMENTATION
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

Characterization tests may be added for already-existing common ingestion guarantees such as source immutability.

## First-slice behavior

Tests should require:

- quoted and unquoted MoTeC CSV parsing equivalence;
- deterministic duplicate-name disambiguation without changing `original_name`;

- positive import of the licensed canonical MoTeC-style CSV fixture;
- source type/system identity;
- metadata preamble preservation;
- exact source channel names;
- unit-row preservation;
- explicit `Time` source values used as timestamps;
- source cell values preserved without normalization;
- mixed/discrete text preserved;
- missing-like text preserved as source evidence rather than converted to null unless the format contract explicitly defines it as missing;
- sample rate left unknown when not supplied;
- deterministic provenance/fingerprint;
- source bytes unchanged;
- malformed/structurally unsupported files fail explicitly;
- decreasing time remains imported source evidence when structurally readable and is left for the validation stage to classify, unless verified MoTeC export rules make decreasing time structurally invalid.

## Ingestion / validation boundary

The existing negative fixture has decreasing timestamps.

The importer should not duplicate validation logic merely because a timestamp looks suspicious.

If the file is structurally readable:

```text
IMPORT
-> preserve Time values
VALIDATION
-> report decreasing timestamp
```

This boundary should be proven by an integration test.

## Sample-rate rule

Do not infer missing sample rate from timestamp spacing during import.

If a MoTeC export explicitly supplies acquisition rate metadata in a verified form, preserve it.

Otherwise:

```text
sample_rate_hz = unknown
```

A later deterministic transformation may estimate cadence if a requirement calls for it.

## Architecture boundary

The MoTeC CSV adapter belongs in ingestion.

It must not:

- introduce MoTeC-specific engineering concepts into the core domain;
- normalize channel names;
- convert units;
- replace missing-like text;
- repair timestamps;
- calculate derived metrics;
- infer Session / Run / Lap hierarchy beyond explicit trustworthy source markers;
- depend on native MoTeC i2 COM/API;
- use AI.

## External validation

The TRACE fixture is synthetic interoperability data, not a real race session.

Plan 008 should also inspect at least one real or representative MoTeC CSV export when legally accessible.

If redistribution permission is unclear, keep it external and record only verified structural observations.

## Completion criteria

- verified MoTeC CSV contract documented;
- licensed fixture used for deterministic CI;
- tests written before production adapter behavior;
- behavioral RED recorded;
- source-specific adapter implemented behind common ingestion contract;
- metadata/channels/units/source values preserved;
- import/validation boundary proven;
- sample-rate non-inference proven;
- canonical CI GREEN;
- external real/representative MoTeC validation performed when feasible.

## Explicitly out of scope

- native `.ld` parsing;
- MoTeC i2 COM/API dependency;
- unit normalization;
- resampling;
- channel canonicalization;
- lap comparison;
- setup analysis;
- UI;
- AI.
