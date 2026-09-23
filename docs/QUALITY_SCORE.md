# OME Harness Quality Score

Date: 2026-09-23

Status: **Operational harness — browser-source workflow verified; MVP frontend active**

Scale:

- 0 — absent
- 1 — ad hoc
- 2 — documented but weakly operational
- 3 — usable with important gaps
- 4 — strong and mostly enforced
- 5 — mature and continuously enforced

## Current scorecard

| Area | Score | Assessment |
|---|---:|---|
| Product intent | 4 | Mission, MVP and non-goals are explicit. |
| Domain legibility | 4 | Core telemetry concepts and evidence distinctions are documented and now represented in the first production domain types. |
| Architecture legibility | 4 | Boundaries and ADRs are clear and initial structural enforcement exists. |
| Root agent instructions | 4 | Concise map plus real canonical commands and scoped ingestion/validation/normalization guidance plus explicit repository-wide TDD rules. |
| Documentation system of record | 4 | Structured/indexed with mechanical local-link/status/index checks. |
| Requirement traceability | 3 | REQ-001 through REQ-004 have executable traceability; REQ-005/REQ-006 now have executable delta-time/evidence traceability while their broader comparison scope continues incrementally. |
| Plan lifecycle | 4 | Plans 001–017 have completed history and Plan 018 is active. |
| Automated feedback | 4 | Locked setup, formatter, linter, static check, tests, CI and canonical verify are operational. |
| Architecture enforcement | 3 | Initial dependency/cycle checks exist and ingestion stayed within its boundary. |
| Reproducible environment | 4 | Exact runtimes/tools, lockfiles, fresh-runner CI and documented setup exist. |
| Representative fixtures | 3 | Project-owned CSV/binary fixtures and licensed public MoTeC/negative fixtures are mechanically checked; a redistributable physical-car MoTeC session remains a useful data gap. |
| Agent self-verification | 4 | The first product slice was iterated through CI failures to a green canonical verify. |
| Documentation drift control | 3 | Links, IDs, statuses, indexes and plan placement receive automated checks. |
| Technical-debt control | 3 | Explicit tracker exists and repeated defects are candidates for new guardrails. |
| Observability for agent debugging | 0 | Deferred until an executable application process exists. |
| Security/permissions harness | 2 | CI is read-only and third-party actions are pinned; application security controls are not yet relevant. |

## Interpretation

The harness has now been used across ingestion, validation, normalization, operational context, external binary ingestion and professional-workflow CSV ingestion.

It has rejected real defects, preserved acceptance-criterion traceability and enforced architectural separation between ingestion, validation and downstream concerns.

The lap-comparison reference/alignment decision is now explicit in ADR-0009 and the v0.1 comparison spec.

Deterministic delta-time, continuous overlays, discrete gear alignment, exact brake-semantic compatibility and typed gain/loss/neutral observations are proven through RED -> GREEN CI.

The integrated application report and first local FastAPI boundary are now verified. FastAPI/Pydantic isolation is mechanically enforced.

The source-to-report preparation workflow and browser-usable multipart source boundary are now verified with controlled fixtures and complete provenance.

The next maturity step is to extend the harness into a real React/TypeScript investigation interface while preserving evidence semantics, accessibility and deterministic backend authority.

## Review cadence

Update this document:

- after each major architecture phase;
- when repeated agent mistakes reveal a missing guardrail;
- when a new subsystem is introduced;
- when CI/checking strategy materially changes.

Scores must be supported by repository evidence, not optimism.
