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

Status: **Complete**

Completed:

- Plan 003 — OME CSV Import Foundation;
- Plan 004 — Telemetry Validation Foundation;
- Plan 005 — Telemetry Normalization Foundation;
- Plan 006 — Session / Run / Lap Context Foundation;
- source-preserving telemetry domain objects;
- provenance/fingerprint;
- importer contract;
- OME CSV v0.1;
- REQ-001 acceptance-test mapping;
- source-independent non-destructive validation;
- REQ-002 acceptance-test mapping;
- explicit versioned normalization rules;
- deterministic traceable conversions;
- REQ-004 acceptance-test mapping;
- truthful Session / Run / Lap context without invented boundaries;
- REQ-003 acceptance-test mapping;
- default RED -> GREEN -> REFACTOR workflow for new deterministic behavior.

## Phase 4 — Initial external/professional sources

Status: **Complete**

Completed:

- Plan 007 — iRacing `.ibt` Adapter Foundation;
- Plan 008 — MoTeC CSV Adapter Foundation;
- IRSDK v2 binary import;
- project-owned synthetic binary fixture;
- real-file-driven grouped 360 Hz source arrays;
- MoTeC CSV source adapter with licensed deterministic fixtures;
- source-adapter arbitration and contract tests;
- representative external validation for both source families;
- complete REQ-001 initial source strategy.

## Phase 5 — Lap comparison vertical slice

Status: **Active**

Current plan:

- `docs/plans/active/009-lap-comparison-reference-delta-foundation.md`

Current work is decision-first:

- define comparison readiness;
- select distance/reference representation;
- select interpolation/alignment behavior;
- define delta-time sign convention;
- define evidence/provenance contract;
- then implement deterministic comparison behavior with TDD.

- readiness checks;
- distance alignment;
- delta-time calculation;
- key channel overlays;
- evidence model;
- comparison report.

## Phase 6 — Expanded real-motorsport validation

Future.

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
