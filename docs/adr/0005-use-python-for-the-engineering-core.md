# ADR-0005 — Use Python for the initial engineering and application core

Status: **Accepted**

Date: 2026-09-22

## Context

OME requires rapid development of deterministic telemetry processing, scientific analysis, file adapters and future engineering algorithms.

The project should also remain approachable to engineering students and data/performance engineers.

## Decision

Use Python as the primary language for the initial OME engineering/application core.

Domain and engineering behavior must remain framework-independent.

Performance-critical sections may later be replaced or accelerated with native code after profiling.

## Why

- mature scientific/numerical ecosystem;
- strong Arrow/Parquet/data tooling;
- good signal-processing ecosystem;
- accessible contributor base;
- strong test/tooling support;
- future AI integration is straightforward without requiring AI in the core.

## Alternatives

### Rust-first

Deferred because the initial cost and contributor barrier are not justified by measured performance requirements.

### TypeScript-only full stack

Rejected for the engineering core because the numerical/scientific ecosystem is weaker for OME's primary analysis workload.

## Risk

Python packaging and CPU-bound workloads can become constraints.

Mitigation:

- keep computation boundaries explicit;
- use vectorized/columnar engines;
- profile before optimizing;
- allow native acceleration later without changing domain contracts.
