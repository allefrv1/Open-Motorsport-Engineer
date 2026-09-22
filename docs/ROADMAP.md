# OME Engineering Roadmap

Status: **Accepted planning baseline**

This roadmap describes engineering sequence, not release dates.

## Phase 0 — Foundation

Status: **Complete**

Goals:

- establish project mission and non-goals;
- define repository instructions for Codex;
- establish documentation structure;
- define initial domain vocabulary;
- define quality attributes;
- define source-ingestion boundaries;
- define initial requirements;
- define first vertical slice;
- document initial architecture decisions.

## Phase 1 — Technology selection

Status: **Complete**

Before coding, evaluate candidate technologies against:

- deterministic numerical/data processing;
- multi-rate telemetry;
- large local datasets;
- offline-first usage;
- cross-platform constraints;
- visualization needs;
- packaging/distribution;
- testability;
- contributor accessibility;
- future AI integration without coupling the core to AI.

Outputs completed:

- technology evaluation;
- local modular monolith selected;
- Python engineering/application core selected;
- Arrow-compatible columnar boundaries + Parquet telemetry persistence selected;
- SQLite local metadata catalog selected;
- local FastAPI boundary selected;
- React + TypeScript + Vite UI selected;
- initial repository/module layout documented;
- test strategy documented;
- desktop packaging deliberately deferred.

## Phase 2 — Telemetry foundation implementation

Status: **Ready, intentionally not started**.

Implement only after Phase 1 decisions:

- OME CSV Profile ingestion;
- provenance;
- imported telemetry model;
- validation;
- initial normalization;
- Session / Run / Lap representation.

## Phase 3 — First external source

Future.

- iRacing `.ibt` adapter;
- representative fixtures;
- import/validation parity tests.

## Phase 4 — Lap comparison vertical slice

Future.

- lap comparison readiness;
- deterministic alignment/delta;
- key channel overlays;
- evidence model;
- comparison report.

## Phase 5 — Real-motorsport validation

Future.

- MoTeC CSV export;
- Formula Student / race-team representative datasets;
- validate workflow and metadata assumptions;
- revisit native `.ld` feasibility.

## Phase 6 — Domain analysis modules

Future and incremental.

Potential modules:

- braking;
- driver consistency;
- corner entry/mid/exit;
- vehicle health;
- tyres;
- suspension;
- setup A/B analysis.

Each module must define its engineering question, required evidence, deterministic metrics, uncertainty and validation references before AI explanations are added.

## Phase 7 — OME Engineer Agent

Future.

The agent is added above a mature evidence/tool layer.

It should not be used to compensate for missing deterministic engineering functionality.

## Rule

Do not pull future-phase complexity into an earlier phase without an explicit requirement and architecture decision.
