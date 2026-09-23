# Architecture Decision Records

ADRs record architecture decisions with meaningful long-term consequences.

Codex may propose an ADR, but must not mark a major decision Accepted without maintainer authorization.

## Status vocabulary

- Proposed
- Accepted
- Superseded
- Deprecated
- Rejected

## Index

| ADR | Status | Decision |
|---|---|---|
| 0001 | Accepted | Separate ingestion from normalization |
| 0002 | Accepted | CSV is exchange profile, not canonical storage |
| 0003 | Accepted | AI is not the deterministic engineering core |
| 0004 | Accepted | Use a local modular monolith |
| 0005 | Accepted | Use Python for the initial engineering core |
| 0006 | Accepted | Use Arrow-compatible columnar data and Parquet |
| 0007 | Accepted | Use SQLite for local project metadata |
| 0008 | Accepted | Use local HTTP API and React/TypeScript UI |
| 0009 | Accepted | Align initial lap comparisons by distance |
| 0010 | Proposed | Introduce containers only for executable application boundaries |

See `0000-template.md` for new decisions.

## Harness rule

Accepted ADRs describe intended architecture.

Once implementation exists, important enforceable ADR constraints should be backed by structural tests, dependency rules, schemas or other mechanical checks where practical.
