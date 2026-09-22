# OME Pre-Code Readiness Review

Date: 2026-09-22

Status: **Foundation complete — ready for technology evaluation, not yet implementation**

## Executive conclusion

OME now has enough product, domain and architecture definition to begin selecting implementation technologies without asking the programming agent to invent core behavior.

Production code should still wait until the technology evaluation and initial module boundaries are documented.

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

## Deliberately unresolved until technology evaluation

The following are **not gaps** at this stage; they are deferred decisions:

- implementation language;
- UI framework;
- application runtime;
- persistence engine;
- internal columnar representation;
- desktop/local-web packaging;
- plotting library;
- AI provider/model;
- exact source-adapter libraries;
- exact lap-alignment algorithm.

## Data still needed before implementation validation

Representative fixtures should be acquired or created during technology evaluation:

1. controlled OME CSV fixture;
2. representative iRacing `.ibt` file;
3. representative MoTeC CSV export from real motorsport;
4. later, Formula Student / race-team data where legally shareable.

## Go / No-Go

### Go

Proceed to **technology and system-shape evaluation**.

### No-Go

Do not begin production implementation yet.

The next architecture work must decide:

- application shape;
- language/runtime;
- data-processing approach;
- internal telemetry representation;
- persistence approach;
- packaging strategy;
- testing strategy.

Those choices should be recorded through ADRs before Codex receives broad implementation authority.
