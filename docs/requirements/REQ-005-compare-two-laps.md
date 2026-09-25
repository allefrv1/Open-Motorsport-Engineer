# REQ-005 — Compare Two Laps

Status: **Accepted**

## Actor / User

A driver, coach or engineer who wants to understand where two laps differ in performance.

## Problem

A raw overlay of channels does not directly answer where time was gained or lost or which measurable differences are associated with that change.

## Goal

Allow two comparable laps to be aligned on an explicit track reference and compared through measured and derived evidence.

## Preconditions

- both laps have trustworthy timing/context;
- a suitable positional comparison reference is available;
- required channels for a requested metric are available and sufficiently validated.

## Main Flow

1. The user selects Lap A and Lap B.
2. OME verifies comparison readiness.
3. OME establishes an explicit alignment/reference basis.
4. OME computes deterministic comparison metrics.
5. OME identifies regions of gain/loss in delta time.
6. OME exposes relevant measured channels and derived metrics.
7. OME records observations without automatically assigning a cause.

## Initial Channels

When available, the first vertical slice should support comparison of:

- vehicle speed;
- throttle;
- brake;
- steering;
- RPM;
- gear.

## Acceptance Criteria

### AC-001 — Explicit reference

Lap comparison must use a documented comparison/alignment reference.

### AC-002 — Deterministic delta

Delta-time computation must be deterministic for equivalent inputs and parameters.

### AC-003 — Missing evidence

If a requested comparison requires unavailable channels, OME must report that limitation.

### AC-004 — Observation vs cause

OME may state measurable differences such as lower minimum speed or later throttle application.

It must not automatically convert those differences into a causal engineering diagnosis.

### AC-005 — Provenance

Comparison metrics and observations must remain traceable to the laps, channels, transformations and algorithm versions that produced them.

### AC-006 — Context visible

The user must be able to identify which Session / Run / Lap each comparison case belongs to.

## Resolved Architecture Decision

ADR-0009 and `docs/specs/lap-comparison-v0.2.md` define the current comparison reference and numerical contract:

- align by trustworthy monotonic `lap.distance` in metres;
- compare only the common distance interval;
- use a deterministic analysis-only distance grid;
- use linear interpolation for elapsed time as a function of distance;
- compute `delta_B_vs_A = time_B - time_A`;
- preserve source data unchanged and retain comparison provenance.

The v0.2 spec retains the 1.0 m default grid and linear distance alignment while extending readiness/interpolation to preserve exact non-decreasing distance plateaus. True distance decreases remain not-ready.

## Delta-time foundation traceability

Plan 009 maps the first deterministic delta-time foundation to:

`tests/analysis/test_lap_comparison.py`

Acceptance mapping for this increment:

- AC-001 — `test_ac001_result_declares_explicit_distance_reference`
- AC-002 — `test_ac002_known_delta_is_deterministic_with_documented_sign`
- AC-003 — `test_ac003_missing_distance_returns_not_ready_with_missing_evidence`
- AC-004 — `test_ac004_result_does_not_embed_causal_diagnosis`
- AC-005 / AC-006 — `test_ac005_and_ac006_provenance_preserves_context_channels_and_algorithm`

Additional deterministic coverage proves:

- equal laps produce zero delta;
- the exact common endpoint is retained when grid spacing does not land on it;
- partial overlap is restricted to the common distance interval;
- incompatible reference concepts return not-ready;
- non-monotonic distance/time is not repaired;
- non-finite input returns not-ready;
- no common distance returns not-ready;
- invalid grid step returns not-ready;
- missing context provenance returns not-ready.

### TDD evidence

- RED: OME CI #79 — comparison API absent after test-helper correction;
- GREEN: OME CI #85 — canonical verification successful.

This is the **delta-time/reference foundation**, not the complete REQ-005 feature.

Plan 010 adds the first continuous measured-channel overlays.

### Continuous overlay traceability

Test module:

`tests/analysis/test_continuous_overlay.py`

Implemented continuous concepts:

- vehicle speed;
- throttle;
- steering;
- engine speed / RPM after explicit normalization to `rad/s`.

The tests prove:

- deterministic projection onto the exact base comparison grid;
- different source/normalized sample cadences;
- canonical concept/unit compatibility;
- explicit missing evidence;
- no temporal extrapolation;
- non-monotonic/non-finite input rejection;
- source/transformation provenance;
- base comparison provenance preservation;
- unsupported brake and gear remain explicit;
- no causal diagnosis is embedded in the deterministic overlay result.

TDD evidence:

- RED: OME CI #91 — continuous overlay API absent;
- GREEN: OME CI #96 — canonical verification successful.

Plan 011 adds deterministic discrete gear alignment.

### Discrete gear overlay traceability

Test module:

`tests/analysis/test_discrete_gear_overlay.py`

The tests prove:

- exact sample timestamps use the current gear state;
- between samples, previous-sample hold is used;
- no fractional gear values can be produced;
- different gear sample cadences are supported;
- missing/incompatible evidence is explicit;
- non-integer canonical gear values are rejected;
- non-monotonic/non-finite timestamps are rejected;
- no temporal extrapolation occurs;
- base comparison and source/transformation provenance remain inspectable;
- no causal or recommendation fields are embedded.

TDD evidence:

- RED: OME CI #103 — discrete gear overlay API absent;
- GREEN: OME CI #108 — canonical verification successful.

### Brake overlay traceability

Plan 012 adds continuous brake comparison only when semantic compatibility is mechanically explicit.

Test module:

`tests/analysis/test_continuous_overlay.py`

The Plan 012 tests prove:

- matching `driver.brake.pedal_position_ratio [1]` evidence can be overlaid;
- matching `driver.brake.pedal_force_ratio [1]` evidence can be overlaid;
- pedal position and pedal force are not treated as equivalent;
- missing semantic identity is explicit not-ready evidence;
- unsupported hydraulic-pressure semantics are explicit not-ready evidence;
- canonical ratio unit `1` is required;
- brake provenance retains semantic ids;
- continuous overlay still does not absorb discrete gear behavior;
- no causal diagnosis is embedded.

TDD evidence:

- RED: OME CI #117;
- GREEN: OME CI #121.

### Delta-region observation traceability

Plan 013 implements the first higher-level deterministic observation above the accepted delta metric.

Test module:

`tests/analysis/test_delta_observations.py`

The tests prove:

- AC-004 — measured delta change is classified as B gain, B loss or neutral without causal diagnosis;
- AC-005 — observation provenance retains the complete base comparison provenance;
- AC-006 — Session / Run / Lap context remains reachable through that base provenance;
- malformed or incompatible metric evidence produces explicit not-ready results rather than a plausible observation.

TDD evidence:

- RED: OME CI #128 — observation API absent;
- GREEN: OME CI #135 — canonical verification successful.

### Integrated comparison-report traceability

Plan 014 composes the accepted deterministic comparison capabilities into one application-level artifact.

Test module:

`tests/application/test_lap_comparison_report.py`

The tests prove:

- AC-001 / AC-002 — the report contains the accepted deterministic base comparison rather than recalculating it;
- AC-003 — optional missing/incompatible supporting evidence is preserved explicitly without fabrication;
- AC-004 — observations remain non-causal and the report exposes no causal conclusion fields;
- AC-005 — report provenance retains base comparison, observation and every successful overlay provenance;
- AC-006 — Session / Run / Lap context remains reachable through the retained base comparison provenance;
- the initial speed/throttle/brake/steering/RPM/gear evidence inventory is presented in deterministic stable order.

TDD evidence:

- RED: OME CI #141 — report application contract absent;
- GREEN: OME CI #145 — canonical verification successful.

The deterministic **backend** scope of REQ-005 is now implemented for the first vertical slice.

### Local HTTP comparison-report traceability

Plan 015 exposes the accepted deterministic report through the first versioned local HTTP boundary.

Test module:

`tests/api/test_local_http_api.py`

The tests prove:

- AC-001 / AC-002 — the API serializes the already accepted deterministic base comparison rather than recalculating it;
- AC-003 — application Missing Evidence/not-ready outcomes remain explicit structured HTTP data;
- AC-004 — transport does not add causal diagnosis fields;
- AC-005 — assembler/base algorithm provenance remains visible in JSON;
- AC-006 — the request/response evidence model retains dataset and Session / Run / Lap identifiers.

TDD evidence:

- RED: OME CI #155 — `create_app` absent;
- GREEN: OME CI #161 — canonical verification successful;
- final architecture/docs verification: CI #163.

REQ-005 remains Accepted rather than Implemented until the user-facing UI workflow makes the comparison selectable and inspectable end to end.

### Plateau-aware physical comparison traceability

Plan 027 evolves the accepted base comparison to algorithm version `0.2.0` without changing the delta sign convention or evidence model.

Executable coverage:

- `tests/analysis/test_lap_comparison.py`;
- `tests/application/test_physical_track_reference_preparation.py::Plan026PhysicalTrackReferencePreparationTests.test_portland_prepared_distances_reach_base_comparison_v02_readiness`.

The tests prove:

- AC-001 / AC-002 — the same explicit `lap.distance` reference remains deterministic when exact physical projection plateaus are present;
- AC-003 — true distance decreases remain explicit not-ready evidence;
- AC-004 — no causal diagnosis is introduced;
- AC-005 — comparison provenance reports `ome.lap-comparison.distance-linear / 0.2.0` and retains source/transformation evidence;
- AC-006 — Portland reference/candidate Lap contexts remain inspectable through comparison provenance.

TDD evidence:

- RED: CI #349;
- GREEN: CI #354;
- physical Portland integration: CI #355.

## Out of Scope

- automatic setup recommendation;
- automatic understeer/oversteer diagnosis;
- generic track segmentation;
- driver scoring;
- AI-generated causal conclusions.
