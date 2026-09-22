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

Status: **Complete as a documented baseline; executable validation pending**

Selected direction includes:

- local modular monolith;
- Python engineering/application core;
- Arrow/Polars/Parquet data stack;
- SQLite metadata;
- FastAPI local application boundary;
- React + TypeScript + Vite UI;
- first test strategy and module layout.

These choices must be tested against representative data during implementation rather than treated as automatically proven.

## Phase 2 — Agent harness bootstrap

Status: **Next**

See `docs/plans/active/002-harness-bootstrap.md`.

Build:

- reproducible environment;
- locked toolchains/dependencies;
- canonical local commands;
- CI;
- lint/type/test loops;
- docs checks;
- architecture-boundary checks;
- initial telemetry fixtures;
- PR/self-review loop.

No ordinary feature development should precede this phase.

## Phase 3 — Telemetry foundation

Future.

- OME CSV Profile ingestion;
- provenance;
- imported telemetry model;
- validation;
- normalization;
- Session / Run / Lap representation.

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
