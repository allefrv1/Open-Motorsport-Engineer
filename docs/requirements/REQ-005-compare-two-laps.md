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

ADR-0009 and `docs/specs/lap-comparison-v0.1.md` resolve the initial comparison reference and numerical baseline:

- align by trustworthy monotonic `lap.distance` in metres;
- compare only the common distance interval;
- use a deterministic analysis-only distance grid;
- use linear interpolation for elapsed time as a function of distance;
- compute `delta_B_vs_A = time_B - time_A`;
- preserve source data unchanged and retain comparison provenance.

The v0.1 spec defines a default 1.0 m grid step and conservative readiness requirements for the first implementation.

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

Speed/throttle/brake/steering/RPM overlays and the discrete gear comparison rule remain later increments of the accepted requirement.

## Out of Scope

- automatic setup recommendation;
- automatic understeer/oversteer diagnosis;
- generic track segmentation;
- driver scoring;
- AI-generated causal conclusions.
