# OME Harness Quality Score

Date: 2026-09-22

Status: **Harness bootstrap complete**

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
| Domain legibility | 4 | Core telemetry concepts and evidence distinctions are documented. |
| Architecture legibility | 4 | Boundaries and ADRs are clear and initial structural enforcement exists. |
| Root agent instructions | 4 | Concise map plus real canonical commands. |
| Documentation system of record | 4 | Structured/indexed with mechanical local-link/status/index checks. |
| Requirement traceability | 3 | Requirements exist; executable AC-to-test mapping starts with Plan 003. |
| Plan lifecycle | 4 | Active/completed lifecycle is now exercised by completed Plans 001 and 002. |
| Automated feedback | 4 | Locked setup, formatter, linter, static check, tests, CI and canonical verify are operational. |
| Architecture enforcement | 3 | Initial dependency/cycle checks exist and a deliberate forbidden dependency is tested. |
| Reproducible environment | 4 | Exact runtimes/tools, lockfiles, fresh-runner CI and documented setup exist. |
| Representative fixtures | 3 | Project-owned fixture plus licensed public/negative fixtures are mechanically checked; source coverage still needs expansion. |
| Agent self-verification | 4 | AGENTS.md points to one canonical verify command used by CI. |
| Documentation drift control | 3 | Links, IDs, statuses, indexes and plan placement receive automated checks. |
| Technical-debt control | 3 | Explicit tracker exists and harness debt was converted into working guardrails. |
| Observability for agent debugging | 0 | Deferred until an executable application exists. |
| Security/permissions harness | 2 | CI is read-only and third-party actions are pinned; application security controls are not yet relevant. |

## Harness Bootstrap exit criteria

Required before REQ-001:

- reproducible environment: 3+ — **met (4)**
- automated feedback: 3+ — **met (4)**
- architecture enforcement: 2+ — **met (3)**
- representative fixtures: 2+ — **met (3)**
- agent self-verification: 3+ — **met (4)**
- documentation drift control: 2+ — **met (3)**

## Interpretation

OME now has an executable agent harness strong enough to begin the first small feature slice.

This is not a claim that the harness is mature or complete forever.

Every repeated agent failure should still be treated as evidence for a new guardrail.

## Review cadence

Update this document:

- after each major architecture phase;
- when repeated agent mistakes reveal a missing guardrail;
- when a new subsystem is introduced;
- when CI/checking strategy materially changes.

Scores must be supported by repository evidence, not optimism.
