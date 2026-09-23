# OME Technical Debt Tracker

Status: **Active**

This tracker records known engineering debt that should remain visible to coding agents.

It is not a substitute for issues or execution plans. High-impact items should receive dedicated plans.

## Current debt

| ID | Area | Debt | Severity | Planned handling |
|---|---|---|---|---|
| TD-002 | Fixtures | Real-vehicle Traqmate coverage is now licensed and characterized, but physical-car MoTeC and Brazilian Formula SAE coverage remains incomplete | Medium | Keep source-specific outreach; Plan 020 resolved the first physical-car fixture gap |
| TD-005 | Technology | Realistic 15–20 MB Traqmate benchmark inputs are identified, but end-to-end supported-path measurements await the explicit Traqmate adapter | Medium | Measure in Plan 021 after source ingestion is GREEN; optimize only from evidence |
| TD-006 | MoTeC | Native `.ld` integration feasibility remains unresolved | Low for MVP | Deferred |
| TD-007 | Packaging | Consumer desktop packaging is unresolved | Low for MVP | Revisit after local-web validation |

## Resolved by Plan 002

- TD-001 — executable CI/verification loop: **resolved**
- TD-003 — documentation checks manual-only: **resolved for initial structural checks**
- TD-004 — architecture boundaries prose-only: **resolved for initial dependency rules**

## Rule

When repeated review feedback reveals a stable pattern, convert it into a guardrail and remove or downgrade the corresponding debt item.

A resolved debt item may return if evidence shows the guardrail is insufficient.
