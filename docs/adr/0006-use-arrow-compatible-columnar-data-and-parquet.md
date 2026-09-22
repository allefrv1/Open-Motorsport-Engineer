# ADR-0006 — Use Arrow-compatible columnar data and Parquet for telemetry persistence

Status: **Accepted**

Date: 2026-09-22

## Context

OME must process large telemetry datasets efficiently while preserving selective access to channels and supporting interoperability across processing libraries.

A flat CSV is insufficient as the canonical representation.

## Decision

Use:

- Arrow-compatible columnar structures at data-processing boundaries;
- Polars as the initial high-level transformation engine;
- Parquet for persisted processed/imported columnar telemetry datasets.

This ADR does not force every channel into one shared table or time base.

Multi-rate/time-base semantics must remain preserved by the dataset layout.

## Consequences

### Positive

- efficient column selection;
- compression;
- strong Python ecosystem interoperability;
- lazy/streaming processing options;
- future compatibility with DuckDB and other Arrow consumers.

### Negative

- humans cannot inspect Parquet directly as easily as CSV;
- multi-rate layout requires deliberate design;
- metadata relationships still need a separate project catalog.

## Metadata

Project/session/provenance metadata belongs in the metadata model/catalog and should not be forced into repeated telemetry sample columns.

## Revisit

Revisit if representative real datasets demonstrate that Parquet/Arrow cannot preserve required acquisition semantics efficiently.
