# Plan 006 — Session / Run / Lap Context Foundation

Status: **Completed**

Started: 2026-09-22

Completed: 2026-09-22

## Objective

Implement the smallest source-independent operational-context model satisfying REQ-003 without inventing session, run or lap boundaries.

## Delivered

The context foundation now includes:

- ContextMarker preserving source-facing marker value and source field;
- ContextEvidence carrying trusted explicit context evidence;
- SessionContext;
- RunContext;
- LapContext;
- RunOperationalMetadata for:
  - driver;
  - vehicle;
  - setup version;
  - tyre set;
  - fuel/energy state;
  - run plan;
  - driver feedback;
  - conditions;
- ContextOrganizer;
- deterministic context identifiers derived from explicit evidence;
- explicit support for a Lap associated directly with a Session when Run evidence is absent;
- rejection of contradictory child context when Session evidence is absent;
- preservation of dataset fingerprint and source identity through organized context;
- no Stint entity or Run/Stint alias.

## TDD evidence

Plan 006 established the repository's first explicit RED -> GREEN feature history.

### RED

REQ-003 behavior tests were committed before production implementation.

OME CI #32 failed with the expected missing behavior:

`ModuleNotFoundError: No module named 'ome.application.context'`

This confirmed that the tests described an API that did not yet exist.

### GREEN

The minimum context domain/application implementation was added.

OME CI #36 passed the complete canonical verification.

After requirement/plan traceability was added, OME CI #37 also passed.

No test was weakened or removed to obtain GREEN.

## Acceptance evidence

REQ-003 AC-001 through AC-005 are mapped to:

`tests/context/test_session_run_lap_context.py`

Coverage proves:

- known Session -> Run -> Lap hierarchy;
- missing Run/Lap boundaries remain absent;
- source markers and dataset provenance remain visible;
- Run operational metadata remains context rather than telemetry;
- Stint is not forced into the initial model.

Additional regression coverage verifies:

- stable identifiers for identical explicit evidence;
- run/lap evidence without a Session is rejected;
- project-owned OME CSV context preserves session/lap evidence without fabricating a Run.

## Boundaries preserved

The implementation intentionally did not add:

- generic lap detection;
- GPS start/finish detection;
- pit-out/pit-in inference;
- Stint modeling;
- race/pit strategy;
- setup interpretation;
- timing/scoring integration;
- UI session browsing;
- AI inference.

## Verification evidence

RED workflow:

`OME CI #32`

GREEN workflows:

- `OME CI #36`
- `OME CI #37`

Squash merge:

`9f1969f6f6df5193bce4f73b54d6112e00e29cf6`

## Completion assessment

All Plan 006 completion criteria are satisfied.
