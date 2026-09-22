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

## Open Architecture Question

The exact positional alignment algorithm and distance representation must be selected and documented before implementation.

## Out of Scope

- automatic setup recommendation;
- automatic understeer/oversteer diagnosis;
- generic track segmentation;
- driver scoring;
- AI-generated causal conclusions.
