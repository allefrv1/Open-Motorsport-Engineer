# Plan 004 — Telemetry Validation Foundation

Status: **Completed**

Started: 2026-09-22

Completed: 2026-09-22

## Objective

Implement the smallest non-destructive validation layer satisfying the foundational behavior of REQ-002 without moving normalization, repair or engineering diagnosis into validation.

## Delivered

The validation foundation now includes:

- source-independent ValidationSeverity, ValidationCategory, ValidationIssue and ValidationResult domain concepts;
- validator identity/version in validation results;
- deterministic source-independent checks;
- blocking structural/time issues for:
  - empty sample series;
  - non-finite timestamps;
  - duplicate timestamps;
  - decreasing timestamps;
- warning-level metadata issues for:
  - missing source identity;
  - missing channel source name;
  - missing unit;
  - missing sample rate;
  - invalid supplied sample rate;
- blocking provenance issue for missing content fingerprint;
- warning-level value checks for:
  - missing sample values;
  - non-finite numeric values;
- aggregation of repeated defects into bounded validation issues;
- channel-scoped issue selection for later analysis-readiness evaluation;
- validation-local AGENTS.md rules;
- stronger architecture boundaries preventing validation from depending on ingestion, normalization, analysis or API layers.

## Acceptance evidence

REQ-002 AC-001 through AC-006 are mapped to executable tests in:

`tests/validation/test_validation.py`

Mapping:

- AC-001 — non-destructive validation;
- AC-002 — category, severity, scope, message and evidence;
- AC-003 — missing metadata remains explicit;
- AC-004 — unsafe structural/time evidence is blocking;
- AC-005 — validation reports defects without repair;
- AC-006 — validation evidence can be scoped for later analysis-readiness logic without one universal valid/invalid result.

Additional regression coverage includes:

- empty series;
- non-finite timestamps;
- non-finite numeric values;
- missing values;
- invalid sample rate;
- missing provenance fingerprint.

## Boundaries preserved

The implementation intentionally did **not** add:

- resampling;
- interpolation;
- unit conversion;
- canonical mapping;
- physical-range rules;
- gap-size thresholds;
- frozen-signal heuristics;
- clipping/spike heuristics;
- source/vendor-specific validation;
- named analysis-readiness decisions;
- API/UI behavior.

## Verification evidence

PR #9 passed the repository canonical verification workflow from a clean GitHub Actions runner.

Final verified head:

`d863ecf6ecfd28eccd5f4eb6dd93d0ffbeb42387`

Workflow run:

`OME CI #17` — success.

The canonical implementation was squash-merged as:

`829efe06766bde8913d0969106503168d7925e09`

A duplicate PR created after the chat execution was interrupted was closed rather than merged.

## Completion assessment

All Plan 004 completion criteria are satisfied:

- [x] validation result/severity model;
- [x] deterministic generic checks;
- [x] REQ-002 acceptance traceability;
- [x] non-destructive behavior verified;
- [x] repair/normalization boundaries preserved;
- [x] architecture harness green;
- [x] canonical CI green.

## Remaining future validation work

The accepted requirement still allows richer checks later, but they require explicit policies or source semantics:

- timestamp-gap policies;
- frozen-signal detection;
- clipping/saturation;
- spikes;
- physical impossible ranges;
- synchronization tolerances;
- source-specific quality plugins.

These are deferred intentionally rather than guessed.
