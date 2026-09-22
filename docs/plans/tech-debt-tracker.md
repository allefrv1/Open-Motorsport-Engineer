# OME Technical Debt Tracker

Status: **Active**

This tracker records known engineering debt that should remain visible to coding agents.

It is not a substitute for issues or execution plans. High-impact items should receive dedicated plans.

## Current debt

| ID | Area | Debt | Severity | Planned handling |
|---|---|---|---|---|
| TD-002 | Fixtures | Initial fixtures are operational, but iRacing, physical-car MoTeC and Brazilian Formula SAE coverage remains incomplete | Medium | Source-specific phases + outreach |
| TD-005 | Technology | Selected processing/storage stack has not yet been benchmarked against realistic large telemetry | Medium | Validate during telemetry foundation / vertical slice |
| TD-006 | MoTeC | Native `.ld` integration feasibility remains unresolved | Low for MVP | Deferred |
| TD-007 | Packaging | Consumer desktop packaging is unresolved | Low for MVP | Revisit after local-web validation |

## Resolved by Plan 002

- TD-001 — executable CI/verification loop: **resolved**
- TD-003 — documentation checks manual-only: **resolved for initial structural checks**
- TD-004 — architecture boundaries prose-only: **resolved for initial dependency rules**

## Rule

When repeated review feedback reveals a stable pattern, convert it into a guardrail and remove or downgrade the corresponding debt item.

A resolved debt item may return if evidence shows the guardrail is insufficient.
