# Engineering Council Replenishment Review — After Plan 029

Date: 2026-09-25

Decision: **READY**

Candidate:

`Plan 030 — Traqmate Physical Comparison HTTP Workflow`

## Context

Plan 029 completed the deterministic physical Traqmate report path for the Portland fixture.

The engineering core can now produce:

- distance-based physical comparison;
- gain/loss observations;
- vehicle speed;
- engine speed;
- gear;
- explicit Missing Evidence for throttle, brake and steering.

The controlled OME CSV workflow already has a browser-usable multipart FastAPI boundary.

## Software / Architecture review

Question:

What is the smallest next increment that increases user value without adding another engineering domain assumption?

Assessment:

Expose the already-proven Traqmate physical workflow through a dedicated HTTP endpoint.

Reuse existing components:

```text
upload staging
-> Traqmate importer
-> explicit source-lap windows
-> physical track reference preparation
-> physical comparison preparation
-> Traqmate supporting evidence
-> ComparisonReportService
-> existing report DTO
```

Do not duplicate any analysis algorithm in the API layer.

Proposed route:

`POST /api/v1/traqmate/comparison-reports`

Inputs:

- one Traqmate Trackvision CSV upload;
- explicit reference source-lap number;
- explicit candidate source-lap number;
- `grid_step_m`.

The endpoint should use source-safe temporary staging and explicit not-ready stages.

Decision:

READY.

## Motorsport Mechanical Engineering review

Engineering question:

Does exposing the physical report through HTTP introduce new motorsport interpretation?

Assessment:

No.

The route transports an already-reviewed deterministic physical workflow.

It must not:

- infer a best lap;
- infer throttle/brake/steering;
- diagnose driver/setup behavior;
- reorder reference/candidate laps based on lap time;
- add causal prose.

The user explicitly chooses reference and candidate source laps.

Book lookup:

Not required for this transport-only increment.

No new vehicle-dynamics mechanism, setup rule or telemetry semantic is introduced.

Decision:

READY.

## Physics review

Assessment:

No new equation or numerical method is required.

The API must pass through:

- `grid_step_m`;
- source evidence;
- deterministic physical preparation;
- existing comparison/report results;

without browser/API recomputation.

The endpoint must not alter units or interpolate outside the existing engineering core.

Decision:

READY.

## Provenance/context decision

The Traqmate source does not provide an accepted source Session/Run identity suitable for this endpoint.

Therefore the API may create an **OME analysis context identity**, not claim a source session identity.

For one imported dataset:

```text
session_identifier = "dataset:" + content_fingerprint
run_identifier     = None
lap_identifier     = "source-lap:" + explicit_source_lap_number
```

This identity is deterministic analysis provenance.

It is not presented as a source-provided Session or Run.

## Cross-discipline discussion

Agreements:

- expose proven physical workflow before adding more domain-analysis complexity;
- one uploaded physical dataset, two explicit source lap numbers;
- preserve Missing Evidence;
- reuse deterministic core;
- no new physics;
- no new source semantics.

Disagreements:

None.

## Decision

Selected:

**READY**

## Kanban transition

```text
Plan 029: REVIEW -> DONE
Plan 030: BACKLOG -> READY
```

After the transition PR is merged, Plan 030 may be pulled:

```text
READY -> DOING
```

## Human gate

Not required.

Reopen the CEO/maintainer gate if the scope expands into:

- automatic lap choice/ranking;
- driver/setup diagnosis;
- inferred missing channels;
- a new public workflow contract beyond the narrow endpoint.
