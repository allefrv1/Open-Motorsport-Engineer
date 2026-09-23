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

Completed:

- Plan 009 — Lap Comparison Reference and Delta-Time Foundation;
- Plan 010 — Lap Continuous Channel Overlays;
- Plan 011 — Discrete Gear Overlay;
- Plan 012 — Brake Semantic Compatibility;
- Plan 013 — Lap Delta Gain/Loss Observations;
- explicit distance/time readiness;
- common distance grid;
- deterministic linear time-vs-distance interpolation;
- `delta_B_vs_A`;
- typed comparison provenance/evidence;
- continuous speed/throttle/steering/engine-speed overlays;
- discrete transmission.gear sampling;
- safe exact-semantic brake ratio overlays;
- machine-readable brake semantic identity through normalization/evidence;
- multi-rate evidence alignment with explicit provenance;
- deterministic B-gain / B-loss / neutral observation regions;
- typed observation provenance with no causal claims.

Completed:

- Plan 014 — Lap Comparison Report Bundle;
- deterministic application-level report composition;
- stable six-concept supporting-evidence inventory;
- complete report provenance;
- explicit optional Missing Evidence.

Completed:

- Plan 015 — Local Comparison Report HTTP API;
- executable local FastAPI boundary;
- versioned report transport DTOs;
- health/OpenAPI contract;
- deterministic success/not-ready HTTP semantics;
- mechanical FastAPI/Pydantic isolation from the engineering core.

Completed:

- Plan 016 — MVP Comparison Preparation Workflow Foundation;
- controlled two-lap OME CSV source fixtures;
- explicit versioned preparation/normalization profile;
- traceable `time_s -> time.elapsed` evidence;
- source validation/context/normalization orchestration;
- direct preparation of `ComparisonReportRequest`;
- complete controlled source-to-report evidence chain.

Completed:

- Plan 017 — OME CSV Comparison Upload HTTP Workflow;
- browser-usable multipart source boundary;
- import -> preparation -> report orchestration through existing services;
- explicit import/preparation/report not-ready stages;
- temporary sanitized upload staging;
- source-to-report provenance preserved through HTTP.

Current plan:

- `docs/plans/active/018-mvp-investigation-frontend-foundation.md`

Current work:

- establish the React/TypeScript/Vite/Plotly frontend harness;
- implement the controlled two-lap source workflow with TDD;
- render loading/not-ready/success states without client-side engineering inference;
- render delta, deterministic observations and supporting evidence;
- expose provenance through progressive disclosure;
- verify accessibility and responsive desktop behavior.

After Plan 018:

- validate the complete MVP investigation loop with representative users/data;
- decide packaging/container lifecycle from real application evidence.

Containerization:

- ADR-0010 remains Proposed;
- a backend Dockerfile is now technically justified if the ADR is accepted;
- Docker Compose remains deferred until at least the real frontend process exists.

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
