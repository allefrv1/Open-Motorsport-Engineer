# ADR-0007 — Use SQLite for local project metadata

Status: **Accepted**

Date: 2026-09-22

## Context

OME needs durable local metadata for projects, imports, operational context, provenance and analysis records.

This data is relational and transactional, but the project does not require a server database for the initial local application.

## Decision

Use SQLite as the initial local metadata catalog.

Suitable records include:

- project/workspace metadata;
- source/import catalog;
- Session / Run / Lap context;
- driver/vehicle references;
- setup and tyre references;
- validation results/summaries;
- analysis/finding catalog;
- provenance relationships.

Telemetry sample arrays should remain in columnar telemetry storage rather than row-per-sample SQLite tables by default.

## Consequences

- no database server required;
- easy backup/portability;
- strong transactional metadata support;
- simple local installation.

If future team collaboration requires centralized concurrent access, a later ADR may introduce a server-side metadata store without changing domain semantics.
