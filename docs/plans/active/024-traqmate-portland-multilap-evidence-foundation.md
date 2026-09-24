# Plan 024 — Traqmate Portland Multi-Lap Evidence & Layout Foundation

Status: **Active**

Started: 2026-09-24

## Objective

Establish a compact, legally traceable two-complete-lap physical-car Traqmate fixture from Portland and extend the Traqmate Trackvision V2 ingestion contract to the real extended layout before attempting end-to-end physical-car lap comparison.

## Why this plan exists

Plan 023 completed the deterministic common physical reference.

The next desired workflow is:

```text
real physical-car source
-> explicit source laps
-> GPS evidence
-> common reference
-> lap.distance
-> comparison/report
```

However Context Engineering found that current committed evidence is not yet sufficient.

### Current small fixture

`fixtures/public/exit-speed/traqmate-parking-lot.csv`

provides:

- 1,962 rows;
- 10 Hz;
- three dense source Lap values;
- only Lap 2 clearly complete.

It cannot prove a real two-complete-lap comparison by itself.

### Portland external evidence

Apache-2.0 upstream:

- repository: `djhedges/exit_speed`;
- stripped path: `exit_speed/testdata/2019-08-18_Portland_CORRADO_DJ_R03_stripped.csv`;
- stripped Git blob: `499762a9044ea0b09a698509e84681877baf7897`;
- full Git blob: `13fed5ffe15ad35dc668ea2b4df8acdc63ae7668`.

The stripped source contains:

- 73,904 data rows;
- 40 Hz;
- source lap markers 1–20;
- the same extended 28-column Trackvision layout as the full file.

## New source-contract evidence

The real Portland header is:

```text
GPS Reading
GPS Time
GPS Weeks
Elapsed Time
Lat (Degrees)
Lon (Degrees)
...
Velocity (MPH)
...
Gear
Brake (calc)
Accel (calc)
Lap
```

Therefore:

```text
real Trackvision V2
!= always
Elapsed Time as first column
```

The Plan 021 importer currently requires `Elapsed Time` to be the first telemetry column.

That restriction is not valid for the Portland layout.

## Sparse Lap-marker evidence

Portland uses sparse boundary markers:

- a lap number appears at the first sample of the lap;
- subsequent rows leave the `Lap` cell empty until the next boundary.

Observed in the stripped source:

- Lap 4 marker at source data row 11,360 / elapsed 885.900 s;
- Lap 5 marker at row 14,978 / elapsed 976.350 s;
- Lap 6 marker at row 18,609 / elapsed 1067.125 s.

Thus rows 11,360 through 18,609 inclusive contain:

- complete Lap 4;
- complete Lap 5;
- first boundary sample of Lap 6.

Exact slice shape:

- 7,250 selected data rows;
- 7,267 lines including original preamble/header;
- approximately 1,505,516 characters before Git transport encoding;
- elapsed span 181.225 s.

## Fixture target

Create:

`fixtures/public/exit-speed/traqmate-portland-laps-4-5.csv`

The fixture should be a direct row slice of the upstream stripped blob:

- preserve original preamble rows;
- preserve full original 28-column header/order;
- preserve source cells exactly;
- preserve sparse Lap markers exactly;
- include source rows 11,360 through 18,609 inclusive.

Do not rewrite source telemetry values merely to make the fixture easier to parse.

Document in the fixture manifest:

- upstream repository;
- upstream path;
- upstream Git blob SHA;
- source row interval;
- selected source Lap markers;
- Apache-2.0 license;
- derivative/slice purpose.

## Layered execution packet

### Prompt Engineering

Objective:

> Add a traceable compact Portland two-lap fixture and make the Traqmate importer correctly support its real extended Trackvision V2 layout without changing source semantics.

Success requires:

- fixture provenance/license recorded;
- existing small fixture remains supported;
- extended header supported;
- `Elapsed Time` may appear at a non-zero column index;
- source channel order preserved;
- timestamps taken from the explicit `Elapsed Time` source column;
- sparse Lap marker cells preserved as source evidence;
- no Session / Run / Lap inference in ingestion;
- canonical verify GREEN.

Do not implement:

- lap slicing/application context yet;
- common-reference projection orchestration;
- automatic lap completion heuristics;
- distance normalization;
- comparison/report generation;
- source-cell repair.

### Context Engineering

Normative:

- REQ-001;
- ingestion architecture boundary;
- Plan 021 Traqmate importer behavior;
- source integrity/provenance rules.

Evidence:

- committed parking-lot fixture;
- Portland stripped blob `499762...`;
- Portland/common-reference research;
- Apache-2.0 upstream license.

Context readiness: **ready**.

Material evidence now proves the current first-column assumption is too narrow.

### Harness Engineering

Fixture checks must validate:

- manifest provenance;
- license chain;
- deterministic fixture shape.

Canonical verification remains:

```text
uv run --locked python scripts/harness.py verify
```

### Loop Engineering

Use TDD for importer behavior:

```text
characterize Portland fixture
-> test extended layout
-> behavioral RED with current importer
-> minimum parser generalization
-> focused GREEN
-> regression small fixture
-> full verify
```

Formatting/environment failures are HARNESS_FAILURE, not behavioral RED.

### Graph Engineering

Current state:

```text
PROMPT READY          = yes
CONTEXT READY         = yes
MATERIAL DECISION GAP = no
BEHAVIOR CHANGE       = yes
TESTABLE CONTRACT     = yes
NEXT STATE            = create/characterize licensed fixture -> importer RED
```

Human/decision gate reopens if work would require:

- changing source Lap-marker semantics;
- rewriting source values;
- inferring missing lap boundaries;
- expanding ingestion into comparison logic;
- changing license/redistribution assumptions.

## Importer behavior target

The Trackvision V2 adapter must locate the telemetry header by verified required source columns rather than by assuming column zero is `Elapsed Time`.

For the first extended-layout increment, the header must contain exactly one each of:

- `Elapsed Time`;
- `Lat (Degrees)`;
- `Lon (Degrees)`;
- `Lap`.

The importer must:

- preserve all source columns;
- preserve their source order;
- use the located `Elapsed Time` index for timestamps;
- keep source values lexical/None exactly as today;
- keep sparse `Lap` blanks as None;
- retain sample-rate metadata from the preamble.

Do not convert `GPS Time`, `GPS Weeks`, speed, gear or brake during ingestion.

## TDD targets

Before production parser changes, tests should prove:

1. compact Portland fixture shape/provenance is stable;
2. current importer behavior is RED for the unsupported extended layout;
3. extended fixture imports successfully after the minimum change;
4. `Elapsed Time` at index 3 drives timestamps;
5. all 28 channels remain in source order;
6. sparse Lap markers remain:
   - 4 at relative row 0;
   - 5 at relative row 3,618;
   - 6 at relative row 7,249;
   - all other selected Lap cells absent/None;
7. existing parking-lot fixture still imports unchanged;
8. source bytes remain unchanged;
9. fingerprint is deterministic;
10. OME/MoTeC/iRacing/Traqmate adapter arbitration remains explicit.

## Completion criteria

- compact Portland fixture committed with license/provenance;
- extended Trackvision source layout characterized;
- tests written before importer behavior;
- behavioral RED recorded;
- minimum importer generalization GREEN;
- existing Traqmate fixture regression GREEN;
- sparse Lap source evidence preserved;
- no lap-context inference added to ingestion;
- canonical CI GREEN.

## Next plan boundary

After Plan 024, OME can open a separate physical-car lap-selection/comparison-preparation plan.

That later plan may consume:

- the real Portland two-complete-lap fixture;
- GPS path derivation;
- common track reference;
- explicit `lap.distance` preparation;
- the existing comparison/report stack.

Plan 024 itself does not perform that orchestration.

## Explicitly out of scope

- automatic lap selection;
- lap-time ranking;
- physical-car report generation;
- spatial-index optimization;
- Formula Student source integration;
- native MoTeC `.ld`;
- AI interpretation.
