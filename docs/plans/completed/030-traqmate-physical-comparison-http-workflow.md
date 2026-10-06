# Plan 030 — Traqmate Physical Comparison HTTP Workflow

Status: **Completed**

Started: 2026-09-25

Completed: 2026-10-06

## Objective

Expose the accepted physical Traqmate comparison workflow through a browser-usable multipart HTTP endpoint without moving engineering calculations into the API layer.

## Replenishment decision

Engineering Council:

`docs/reviews/2026-09-25-post-plan-029-replenishment.md`

Decision:

`READY`

Kanban commitment after this plan is merged:

`READY -> DOING`

## Normative contracts

Follow:

- REQ-005;
- REQ-006;
- `docs/specs/traqmate-lap-window-v0.1.md`;
- `docs/specs/physical-car-comparison-preparation-v0.1.md`;
- `docs/specs/traqmate-physical-supporting-channels-v0.1.md`;
- `docs/specs/lap-comparison-report-v0.1.md`;
- ADR-0009;
- existing local HTTP API architecture.

## Endpoint

Target:

`POST /api/v1/traqmate/comparison-reports`

Multipart/form inputs:

- `telemetry_csv`: one Traqmate Trackvision V2 CSV;
- `reference_lap`: explicit source lap number;
- `candidate_lap`: explicit source lap number;
- `grid_step_m`: comparison grid step.

The endpoint must not automatically select the fastest/best lap.

## Deterministic workflow

```text
uploaded Traqmate CSV
-> safe temporary staging
-> TraqmateTrackvisionCSVImporter
-> TraqmateLapWindowSelector(reference_lap)
-> TraqmateLapWindowSelector(candidate_lap)
-> deterministic OME analysis contexts
-> PhysicalTrackReferencePreparationService
-> PhysicalComparisonPreparationService
-> TraqmatePhysicalSupportingEvidenceService
-> ComparisonReportService
-> existing ComparisonReportSuccess DTO
```

No comparison/physics calculation belongs in the route itself.

## Analysis context identity

The route must not pretend the source supplied Session/Run metadata that it does not provide.

Use deterministic OME analysis identities:

```text
session_identifier = "dataset:" + dataset_fingerprint
run_identifier     = None
lap_identifier     = "source-lap:" + source_lap_number
```

These are OME provenance identifiers, not source-provided operational metadata.

## Not-ready stages

Return deterministic workflow issues with a stage that identifies the failing responsibility.

Initial stages:

- `import`;
- `lap_window`;
- `track_reference`;
- `comparison_preparation`;
- `supporting_evidence`;
- `report`.

Transport validation errors such as missing multipart fields or non-numeric form values remain HTTP 422.

Engineering not-ready outcomes remain normal structured workflow responses.

## Upload safety

Use temporary source-safe staging.

Requirements:

- uploaded client filename cannot escape the temporary root;
- no temporary filesystem path is leaked in the response;
- original upload bytes are not modified;
- temporary files are removed when the request finishes.

Do not reuse the OME CSV sidecar staging contract because Traqmate uploads are single-file sources.

## TDD targets

Before production endpoint behavior, tests should prove:

1. route appears in OpenAPI;
2. Portland fixture + explicit Lap 4/Lap 5 returns a successful report;
3. returned report exposes speed and engine-speed;
4. returned report exposes gear;
5. throttle/brake/steering remain not-ready Missing Evidence;
6. delta/observations equal the deterministic core result;
7. provenance contains the expected dataset-linked analysis contexts;
8. reference/candidate order is exactly the caller's order;
9. same lap on both sides returns explicit not-ready;
10. missing/unknown lap returns `lap_window` not-ready;
11. invalid Traqmate source returns `import` not-ready;
12. physical preparation failures retain their responsible stage;
13. supporting-evidence failures retain their responsible stage;
14. invalid grid-step engineering value returns explicit preparation not-ready when transport parsing succeeds;
15. missing multipart/form fields return HTTP 422;
16. malicious client filename cannot escape staging or leak a server path;
17. uploaded bytes remain unchanged;
18. repeated equivalent requests produce equivalent engineering result/provenance.

## Council constraints

### Software / Architecture

- thin transport boundary;
- reuse existing services;
- no duplicated numerical logic;
- explicit stage mapping;
- TDD before production endpoint.

### Motorsport Mechanical

- no automatic lap ranking;
- no new telemetry mapping;
- no causal/driver/setup interpretation;
- preserve Missing Evidence.

### Physics

- no API-side unit conversion;
- no API-side interpolation;
- no alteration of deterministic core outputs.

## TDD loop

```text
accepted endpoint contract
-> API tests
-> behavioral RED
-> minimum staging/workflow route
-> GREEN
-> full verify
-> delivery council review
```

## TDD execution evidence

Behavioral RED:

- OME CI #396;
- expected failure: `/api/v1/traqmate/comparison-reports` did not exist and Plan 030 endpoint tests returned HTTP 404.

GREEN progression:

- OME CI #397 — route behavior existed, but the pre-existing exact OpenAPI route-set test correctly rejected the new unregistered contract;
- OME CI #398 — canonical verify GREEN after OpenAPI contract synchronization.

Robustness iteration:

- OME CI #399 — formatter-only failure in newly added robustness tests;
- OME CI #400 — test helper failed to locate raw ` RPMs` because the physical fixture intentionally preserves source-header padding;
- the helper was corrected to locate source columns by normalized identity while retaining the raw row;
- OME CI #401 — canonical verify GREEN;
- OME CI #402 — final canonical verify GREEN with explicit non-numeric-form 422 coverage and exact staged-upload byte-integrity coverage.

No production test was weakened to obtain GREEN.

## Delivery review

Engineering Council delivery review:

`docs/reviews/2026-10-06-plan-030-delivery.md`

Decision:

`READY`

## Completion criteria

- Plan 029 archived;
- Council replenishment decision recorded;
- tests before production behavior;
- behavioral RED recorded;
- safe Traqmate upload staging;
- physical source-to-report HTTP workflow GREEN;
- Missing Evidence preserved;
- route/OpenAPI GREEN;
- canonical verify GREEN;
- delivery Council review complete.

## Merge evidence

PR:

`#75 — feat: add current Traqmate physical comparison HTTP workflow`

Final canonical PR verification:

- OME CI #403 — success.

Squash merge:

`8234e17bef8c18f8dd9c4a6e975ae4ecee2d3e0c`

## Completion assessment

All Plan 030 completion criteria are satisfied.

The accepted physical Traqmate source-to-report pipeline is now browser-usable through a thin multipart HTTP boundary while retaining caller lap order, Missing Evidence, deterministic engineering outputs and provenance.

## Explicitly out of scope

- frontend changes;
- multiple uploaded sessions;
- automatic lap detection beyond accepted source markers;
- fastest/best lap selection;
- setup/driver diagnosis;
- AI explanation;
- new physical equations;
- new telemetry semantics.
