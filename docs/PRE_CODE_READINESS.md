# OME Pre-Code Readiness Review

Date: 2026-09-22

Status: **Pre-code architecture complete — implementation intentionally paused**

## Executive conclusion

OME now has enough product, domain, architecture and technology definition for Codex to begin implementation without inventing core behavior or major technology choices.

Production code is intentionally paused because the current instruction is to finish the software-engineering foundation first.

## Product foundation

- [x] Problem defined
- [x] Mission defined
- [x] Non-goals defined
- [x] Initial user groups identified
- [x] First vertical slice defined
- [x] Long-term scope separated from MVP

## Domain foundation

- [x] Event / Session / Run / Lap vocabulary
- [x] TelemetrySource
- [x] ImportedTelemetryDataset
- [x] SourceChannel
- [x] SampleSeries
- [x] Provenance
- [x] Validation concepts
- [x] Normalization boundary
- [x] Evidence hierarchy
- [x] Unknown/missing-data behavior

## Requirements

- [x] REQ-001 Import Telemetry Session
- [x] REQ-002 Validate Telemetry Dataset
- [x] REQ-003 Organize Session / Run / Lap
- [x] REQ-004 Normalize Telemetry Channels
- [x] REQ-005 Compare Two Laps
- [x] REQ-006 Preserve Analysis Evidence

## Quality attributes

- [x] Integrity
- [x] Traceability
- [x] Reproducibility
- [x] Explicit uncertainty
- [x] Data ownership
- [x] Auditability
- [x] Interoperability
- [x] Extensibility
- [x] Offline usability
- [x] Portability
- [x] Performance evaluation envelope

## Data-source strategy

- [x] OME CSV Profile
- [x] iRacing `.ibt` target
- [x] MoTeC CSV professional workflow target
- [x] Native MoTeC `.ld` explicitly deferred
- [x] CSV not treated as canonical internal model

## Architecture

- [x] Ingestion separated from validation
- [x] Validation separated from normalization
- [x] Multi-rate data supported conceptually
- [x] Engineering core deterministic
- [x] AI separated from deterministic core
- [x] Evidence contract defined conceptually
- [x] Local/offline-first principle established
- [x] No microservices/cloud assumption

## ADRs

- [x] ADR-0001 — Separate ingestion from normalization
- [x] ADR-0002 — CSV is exchange profile, not canonical storage
- [x] ADR-0003 — AI is not deterministic engineering core

## Technology decisions completed

- application shape: local modular monolith;
- engineering/application core: Python;
- processing: Polars;
- columnar interoperability: Apache Arrow/PyArrow;
- telemetry persistence: Parquet;
- local metadata: SQLite;
- local application API: FastAPI;
- frontend: React + TypeScript + Vite;
- initial visualization: Plotly.js behind replaceable UI components;
- lap comparison alignment: monotonic lap distance with deterministic derived alignment.

## Deliberately unresolved

These remain intentionally deferred because they do not need to be fixed before the first implementation:

- desktop packaging/wrapper;
- AI provider/model;
- native MoTeC `.ld` integration;
- optional DuckDB adoption;
- performance-native extensions in Rust/C++;
- advanced track geometry/segmentation;
- strategy/endurance model.

## Data still needed before implementation validation

Representative fixtures should be acquired or created during technology evaluation:

1. controlled OME CSV fixture;
2. representative iRacing `.ibt` file;
3. representative MoTeC CSV export from real motorsport;
4. later, Formula Student / race-team data where legally shareable.

## Go / No-Go

### Go

The repository is **implementation-ready** for the first telemetry-foundation slice.

### Current hold

Do not begin production implementation until the CEO explicitly starts the coding phase.

When that phase begins, Codex should receive small requirement-linked tasks rather than broad "build OME" instructions.

### Remaining evidence work

Representative real fixtures should be added as soon as legally shareable data is available. They may refine performance assumptions and source adapters, but they no longer need to redefine the architecture foundation.
