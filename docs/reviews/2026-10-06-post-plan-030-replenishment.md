# Engineering Council Replenishment Review — After Plan 030

Date: 2026-10-06

Decision: **READY**

Candidate:

`Plan 031 — Traqmate Physical Investigation Frontend Integration`

## Context

Plan 030 completed a browser-usable backend HTTP workflow for one physical Traqmate Trackvision CSV with explicit reference/candidate source lap numbers.

The existing React investigation workspace already renders the shared deterministic `ComparisonReportSuccess` artifact for the controlled OME CSV workflow.

The product now has a backend physical workflow that is not yet selectable from the user interface.

## Candidate comparison

### Candidate A — Physical Traqmate frontend integration

Value:

- closes the remaining gap between the proven physical backend workflow and an actual browser user;
- reuses the existing result/evidence/plot UI;
- introduces no new telemetry semantics or physics;
- makes the Portland physical validation path directly usable.

Dependency risk:

Low. Required backend route and response contract are already verified.

### Candidate B — Formula Student / race-team shareable data

Value:

High for domain validation.

Dependency risk:

External permission/data acquisition is unresolved.

This remains important backlog work but is not a reliable immediate DOING candidate.

### Candidate C — Physical-car MoTeC fixture outreach

Value:

High for professional-source validation.

Dependency risk:

External source/redistribution permission remains unresolved.

Keep as outreach/backlog rather than block product flow.

### Candidate D — Native MoTeC `.ld`

Current justification:

Insufficient.

MVP and current physical workflow do not require it.

### Candidate E — New domain-analysis modules

Potential value:

High later.

Reason to defer:

The physical evidence path should become user-operable before adding more deterministic analysis complexity.

## UX / Product review

The accepted OME interface model is one investigation workspace, not one screen per source format.

Selected direction:

- keep route `/`;
- add an explicit source-workflow selector;
- preserve OME CSV as the default;
- add one Traqmate CSV + explicit reference/candidate lap controls;
- reuse the shared comparison result, plots, evidence and provenance components;
- clear stale result context when source workflow changes;
- preserve Missing Evidence and method/provenance visibility.

This follows the repository UX skill and OME interface principles:

```text
USER GOAL
-> SOURCE CONTEXT
-> EXPLICIT COMPARISON
-> RESULT
-> OBSERVATION
-> SUPPORTING EVIDENCE
-> PROVENANCE
```

No dashboard redesign is justified.

Decision:

READY.

## Software / Architecture review

Assessment:

The smallest implementation is a frontend/API-client extension only.

Expected boundary:

```text
React source workflow controls
-> multipart fetch
-> /api/v1/traqmate/comparison-reports
-> existing ComparisonReportSuccess transport shape
-> existing investigation result components
```

Do not:

- parse Traqmate CSV in the browser;
- recreate lap-window logic;
- calculate distance/delta/overlays client-side;
- fork the report presentation by source type.

The API client may introduce a separate typed Traqmate request/response union because its not-ready stage vocabulary is broader than the controlled OME CSV workflow.

Decision:

READY.

## Motorsport Mechanical Engineering review

Engineering question:

Does this interface increment change accepted motorsport meaning?

Assessment:

No new source semantics are required.

The UI must preserve:

- explicit reference/candidate source lap selection;
- no automatic fastest/best lap ranking;
- available speed / engine-speed / gear evidence;
- Missing Evidence for throttle / brake / steering;
- B - A delta convention;
- non-causal observation wording.

No vehicle-dynamics book lookup is required because the candidate introduces no new mechanism, setup rule, diagnostic inference or physical mapping.

Decision:

READY.

## Physics review

Assessment:

No numerical method changes.

The browser consumes server-returned:

- distance grid;
- delta;
- overlays;
- observations;
- evidence;
- provenance.

It must not smooth, interpolate, convert units or derive missing channels.

Decision:

READY.

## Risks

Primary UX risks:

- showing stale OME CSV results after switching to Traqmate;
- hiding physical Missing Evidence because fewer driver-input channels are available;
- making source lap fields look like an automatic lap-ranking feature;
- expanding workflow-stage types incorrectly and collapsing not-ready semantics;
- duplicating result components by source type.

These are covered by the Plan 031 specification and TDD targets.

## Decision

Selected:

**READY**

## Kanban transition

```text
Plan 031: BACKLOG -> READY
```

After this replenishment transition is merged, Plan 031 may be pulled:

```text
READY -> DOING
```

Product WIP remains zero until that pull occurs.

## Human gate

Not required.

The change is reversible, reuses accepted contracts and introduces no new engineering semantics.

Reopen the CEO/maintainer gate if the scope expands into automatic lap discovery/ranking, a new navigation model, new engineering interpretation, or new source semantics.
