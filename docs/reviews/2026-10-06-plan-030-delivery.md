# Engineering Council Delivery Review — Plan 030 Traqmate Physical Comparison HTTP Workflow

Date: 2026-10-06

Plan:

`Plan 030 — Traqmate Physical Comparison HTTP Workflow`

PR:

`#75 — feat: add current Traqmate physical comparison HTTP workflow`

Decision: **READY**

## Objective

Verify that the delivered multipart HTTP workflow exposes the already accepted Portland physical Traqmate comparison pipeline without moving engineering calculations, source-semantic guesses or causal interpretation into the API boundary.

## Evidence reviewed

- Plan 030 accepted endpoint/workflow contract;
- REQ-005 and REQ-006;
- Traqmate lap-window, physical preparation, supporting-channel and comparison-report specifications;
- existing deterministic services from Plans 025–029;
- Plan 030 API tests;
- behavioral RED: OME CI #396;
- initial route GREEN: OME CI #398;
- final robustness GREEN: OME CI #402;
- implementation changes in `ome.api` only, reusing accepted application/analysis services.

## Software / Architecture review

Assessment:

- the route stages one upload safely and delegates source parsing to `TraqmateTrackvisionCSVImporter`;
- explicit reference/candidate source-lap numbers are delegated to `TraqmateLapWindowSelector`;
- common-track-reference work remains in `PhysicalTrackReferencePreparationService`;
- base comparison preparation remains in `PhysicalComparisonPreparationService`;
- physical supporting-channel preparation remains in `TraqmatePhysicalSupportingEvidenceService`;
- report composition remains in `ComparisonReportService`;
- the route performs orchestration and outcome-to-DTO translation only;
- no interpolation, unit conversion, delta calculation, projection or other engineering numerical logic was duplicated in the HTTP layer;
- deterministic OME analysis identifiers are dataset-linked and do not pretend that Traqmate supplied Session/Run metadata;
- workflow failures retain responsible stages;
- caller-selected lap order is preserved and no automatic fastest/best-lap ranking was introduced;
- multipart transport validation remains FastAPI HTTP 422;
- source-safe temporary staging strips client path components, does not leak temporary paths, preserves upload bytes exactly and is removed at request completion.

TDD:

- CI #396 proved the endpoint behavior was absent before implementation;
- CI #397 exposed the exact OpenAPI contract that also needed updating;
- CI #398 established the first full GREEN;
- CI #399/#400 were robustness-test mechanical/fixture-helper failures rather than changes to accepted production behavior;
- CI #401 and #402 passed canonical verification after robustness coverage was corrected/completed.

Decision:

READY.

## Motorsport Mechanical Engineering review

Engineering question:

Does the HTTP workflow alter the accepted meaning of the physical Traqmate evidence or introduce unsupported driver/setup conclusions?

Assessment:

- reference and candidate laps are selected explicitly by source lap number;
- no lap-ranking or fastest-lap heuristic is introduced;
- speed remains the previously accepted broad `vehicle.speed` evidence;
- engine speed remains the previously accepted `engine.speed` evidence;
- gear retains the accepted Traqmate-derived/assigned semantic identity;
- throttle, brake and steering remain explicit Missing Evidence;
- `Accel (calc)` is not promoted to throttle;
- `Brake (calc)` is not promoted to driver brake;
- no steering inference is introduced;
- no driver mistake, setup recommendation, understeer/oversteer claim or other causal diagnosis is added by transport.

Reference policy:

No additional vehicle-dynamics book lookup was required because Plan 030 introduces no new motorsport mechanism, diagnostic rule or setup recommendation. It transports previously reviewed deterministic evidence unchanged.

Decision:

READY.

## Physics review

Assessment:

- no API-side unit conversion is performed;
- no API-side interpolation is performed;
- no GPS projection or distance derivation is performed in the route;
- no delta-time calculation is performed in the route;
- the response is serialized from the same deterministic core `ComparisonReportSuccess` artifact;
- tests compare the HTTP report directly with the domain report produced by the injected recording report service;
- explicit non-positive engineering grid-step values reach the deterministic preparation layer and remain structured not-ready evidence rather than being silently repaired;
- transport parsing failures remain HTTP 422 and are not confused with engineering readiness.

No new physical equation or numerical approximation was introduced.

Decision:

READY.

## Cross-discipline discussion

Agreements:

- Plan 030 keeps transport separate from engineering calculations;
- accepted physical evidence and Missing Evidence survive the HTTP boundary;
- caller intent and provenance remain explicit;
- upload staging satisfies the source-integrity/safety contract;
- deterministic repeated requests produce equivalent engineering response/provenance.

Disagreements:

None.

## Decision

Selected:

**READY**

## Kanban transition

Before merge:

```text
DOING -> REVIEW
```

After merge, canonical main verification and documentation synchronization:

```text
REVIEW -> DONE
```

## Actions before merge

- [x] behavioral RED recorded;
- [x] route/staging implementation added after tests;
- [x] all Plan 030 stages covered;
- [x] Missing Evidence preserved;
- [x] upload safety/integrity covered;
- [x] HTTP 422 transport semantics covered;
- [x] canonical verify GREEN;
- [x] specialist delivery review complete.

## Human gate

Not required for the implemented scope.

Reopen the CEO/maintainer gate if future work changes physical source semantics, introduces automatic lap ranking, adds engineering diagnosis/recommendation, or changes an accepted physics/numerical contract.
