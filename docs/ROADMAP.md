# OME Engineering Roadmap

Status: **Accepted planning baseline**

This roadmap describes engineering sequence, not release dates.

## Phase 0 — Product/domain foundation

Status: **Complete**

- mission and non-goals;
- domain vocabulary;
- initial requirements;
- quality attributes;
- source strategy;
- first vertical slice;
- core architecture boundaries.

## Phase 1 — Architecture and technology baseline

Status: **Complete as an initial baseline**

Selected direction includes:

- local modular monolith;
- Python engineering/application core;
- Arrow/Polars/Parquet data stack;
- SQLite metadata;
- FastAPI local application boundary;
- React + TypeScript + Vite UI;
- test strategy and module layout.

These choices remain subject to evidence from real implementation and telemetry.

## Phase 2 — Agent harness bootstrap

Status: **Complete**

See `docs/plans/completed/002-harness-bootstrap.md`.

## Phase 3 — Telemetry foundation

Status: **Active**

Completed:

- Plan 003 — OME CSV Import Foundation;
- source-preserving telemetry domain objects;
- provenance/fingerprint;
- importer contract;
- OME CSV v0.1;
- REQ-001 acceptance-test mapping.

Current plan:

- `docs/plans/active/004-telemetry-validation-foundation.md`

Next foundation slices will add:

- non-destructive validation;
- normalization;
- Session / Run / Lap representation;

without collapsing their responsibilities.

## Phase 4 — First external source

Future.

- iRacing `.ibt` adapter;
- representative fixture;
- source-adapter contract tests.

## Phase 5 — Lap comparison vertical slice

Future.

- readiness checks;
- distance alignment;
- delta-time calculation;
- key channel overlays;
- evidence model;
- comparison report.

## Phase 6 — Real-motorsport validation

Future.

- MoTeC CSV export;
- Formula Student / race-team data where shareable;
- validate performance and metadata assumptions;
- revisit native `.ld` feasibility.

## Phase 7 — Domain analysis modules

Future and incremental.

Potential modules:

- braking;
- driver consistency;
- corner entry/mid/exit;
- vehicle health;
- tyres;
- suspension;
- setup A/B.

Each module must define its question, required evidence, deterministic metrics, uncertainty and validation references.

## Phase 8 — OME Engineer Agent

Future.

AI is added above a mature evidence/tool layer.

It must not compensate for missing deterministic engineering capability.

## Rule

Do not pull future-phase complexity into an earlier phase without an explicit requirement and architecture decision.
