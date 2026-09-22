# ADR-0008 — Use a local HTTP API with a React/TypeScript UI

Status: **Accepted**

Date: 2026-09-22

## Context

OME needs a rich interactive telemetry interface with synchronized plots, track views, investigation panels and progressive disclosure.

The engineering core should remain independent of presentation.

## Decision

For the initial application:

- expose application use cases through a local FastAPI boundary;
- build the UI as a React + TypeScript SPA;
- use Vite for frontend development/build;
- serve/use the application locally and offline.

The API boundary is an application adapter, not a microservice boundary.

## Consequences

### Positive

- strong UI/visualization ecosystem;
- clear separation of presentation from engineering core;
- automatic API contract documentation;
- browser-based cross-platform use;
- future desktop packaging remains possible.

### Negative

- two language toolchains;
- local process lifecycle must be managed;
- packaging into a consumer-friendly desktop app needs later work.

## Visualization

Plotly.js is accepted for the first vertical slice but isolated behind UI components so it can be replaced if performance testing requires another renderer.

## Desktop wrapper

Tauri is deferred.

The first implementation should prove the local-web model before adding Rust/desktop packaging complexity.
