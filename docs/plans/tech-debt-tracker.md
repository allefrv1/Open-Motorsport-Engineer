# OME Technical Debt Tracker

Status: **Active**

This tracker records known engineering debt that should remain visible to coding agents.

It is not a substitute for issues or execution plans. High-impact items should receive dedicated plans.

## Current debt

| ID | Area | Debt | Severity | Planned handling |
|---|---|---|---|---|
| TD-001 | Harness | No executable CI/verification loop yet | High | Plan 002 |
| TD-002 | Fixtures | No committed representative telemetry fixtures yet | High | Plan 002 |
| TD-003 | Docs | Documentation freshness checks are manual | Medium | Plan 002 |
| TD-004 | Architecture | Boundaries exist only in prose, not structural tests | High | Plan 002 |
| TD-005 | Technology | Selected stack has not been benchmarked against representative telemetry | Medium | Validate during bootstrap/first vertical slice |
| TD-006 | MoTeC | Native `.ld` integration feasibility remains unresolved | Low for MVP | Deferred |
| TD-007 | Packaging | Consumer desktop packaging is unresolved | Low for MVP | Revisit after local-web validation |

## Rule

When repeated review feedback reveals a stable pattern, convert it into a guardrail and remove or downgrade the corresponding debt item.
