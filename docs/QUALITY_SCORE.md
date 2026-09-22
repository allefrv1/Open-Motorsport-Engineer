# OME Harness Quality Score

Date: 2026-09-22

Status: **Operational harness — initial source strategy verified; lap-comparison phase active**

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
| Requirement traceability | 3 | REQ-001 through REQ-004 have executable traceability; REQ-001 is implemented across OME CSV, iRacing .ibt and MoTeC CSV with recorded RED -> GREEN evidence. |
| Plan lifecycle | 4 | Plans 001–008 have completed history and Plan 009 is active. |
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

The next maturity step is to make the lap-comparison reference/alignment decision explicit, then carry the same test-first discipline into deterministic delta-time analysis.

## Review cadence

Update this document:

- after each major architecture phase;
- when repeated agent mistakes reveal a missing guardrail;
- when a new subsystem is introduced;
- when CI/checking strategy materially changes.

Scores must be supported by repository evidence, not optimism.
