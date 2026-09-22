# ADR-0004 — Use a local modular monolith for the initial OME application

Status: **Accepted**

Date: 2026-09-22

## Context

OME is an early-stage open-source engineering application with strong offline and data-ownership requirements.

The first vertical slice does not require independent scaling, distributed ownership or remote services.

## Decision

Build the initial application as a **local modular monolith**.

Logical boundaries such as ingestion, validation, normalization, engineering analysis, metadata and AI assistance remain separated in code, but they are not deployed as independent services.

The user-facing application operates locally.

A local API boundary may separate the browser UI from the Python application core.

## Consequences

### Positive

- low operational complexity;
- easy local/offline use;
- simpler debugging;
- easier end-to-end reproducibility;
- future module extraction remains possible if actual requirements justify it.

### Negative

- process boundaries do not enforce modularity automatically;
- discipline and tests are required to keep responsibilities separated.

## Rejected initial alternatives

- cloud-first architecture;
- microservices;
- distributed messaging;
- Kubernetes.

## Revisit when

Consider distribution only if requirements emerge for:

- multi-user remote collaboration;
- centralized team data services;
- independent workload scaling;
- server-side live telemetry;
- organizational ownership that requires deployable service boundaries.
