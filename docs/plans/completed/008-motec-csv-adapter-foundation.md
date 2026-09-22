# Plan 008 — MoTeC CSV Adapter Foundation

Status: **Completed**

Started: 2026-09-22

Completed: 2026-09-22

## Objective

Implement the first professional real-motorsport source adapter through MoTeC i2 CSV export while preserving source evidence and keeping ingestion separate from validation/normalization.

## Delivered

- reviewed MoTeC CSV export contract;
- licensed TRACE canonical and decreasing-time fixtures used in CI;
- source-specific `MoTeCCSVImporter` behind the common ingestion contract;
- signature-based source detection instead of extension-only claiming;
- complete parsed preamble preservation;
- exact source channel name/order/unit preservation;
- lexical source-cell preservation;
- explicit `Time [s]` timestamp basis;
- explicit Sample Rate preservation when supplied;
- missing Sample Rate remains unknown;
- quoted/unquoted CSV equivalence;
- deterministic duplicate-name technical identifiers while preserving `original_name`;
- OME CSV / MoTeC CSV arbitration independent of importer registration order;
- structurally readable decreasing-time telemetry imported unchanged and rejected later by validation;
- deterministic SHA-256 provenance;
- explicit structural failures.

## TDD evidence

Pre-behavior harness cleanup:

- CI #63 — test formatting only.

Behavioral RED:

- CI #64 — `MoTeCCSVImporter` did not exist.

GREEN:

- CI #67 — canonical verify passed after the minimum importer implementation.

Final verification after traceability/external-validation documentation:

- CI #71 — success.

Tests were not weakened to obtain GREEN.

## External representative validation

External public representative:

- repository: `Arcayik/motec-csv`;
- path: `data/1hz.csv`;
- Git blob: `55de91dbabaa04e4a8f5c37b8e5a3717fc9e3b9c`.

Observed:

- standard MoTeC CSV signature;
- 12 non-empty metadata rows;
- explicit 1 Hz sample rate;
- 15 channels;
- 305 data rows;
- consistent row width;
- finite, strictly increasing Time from 0 s to 304 s.

This is a representative format-validation source, not a licensed physical race-team fixture.

The redistributable physical-car MoTeC data gap remains open for later outreach.

## Boundaries preserved

Not added:

- native `.ld` parsing;
- i2 COM/API dependency;
- unit conversion;
- resampling;
- canonical channel mapping;
- timestamp repair;
- lap comparison;
- engineering analysis;
- UI;
- AI.

## Merge evidence

PR #20 was squash-merged as:

`778eb9ed14f3e93ea8a0b851348125c3bb293436`

## Completion assessment

All Plan 008 completion criteria are satisfied.
