# Plan 029 — Traqmate Physical Supporting Evidence Foundation

Status: **Active**

Started: 2026-09-25

## Objective

Enrich the Portland physical comparison report with explicitly verified Traqmate speed, engine-speed and gear evidence while keeping unsupported driver-input semantics as Missing Evidence.

## Normative contract

Follow:

- `docs/specs/traqmate-physical-supporting-channels-v0.1.md`;
- `docs/specs/physical-car-comparison-preparation-v0.1.md`;
- `docs/specs/lap-comparison-report-v0.1.md`;
- `docs/domain/canonical-channels-v0.1.md`;
- ADR-0009;
- REQ-005;
- REQ-006.

## Scope

Add:

- generic deterministic `mph_to_mps` conversion support;
- exact Traqmate rules for:
  - `Velocity (MPH)` -> `vehicle.speed`;
  - `RPMs` -> `engine.speed`;
  - `Gear` -> `transmission.gear`;
- explicit Gear semantic id identifying Traqmate-derived/assigned semantics;
- source-window supporting-series preparation;
- shared start/finish boundary-evidence provenance;
- enriched physical `ComparisonReportRequest`;
- physical report regression with speed/RPM/gear available.

Keep absent:

- throttle;
- canonical driver brake;
- steering.

## TDD targets

Before production behavior, tests should prove:

1. `mph_to_mps` converts deterministically and preserves source evidence;
2. Traqmate profile matches only exact supported source identifiers;
3. Velocity becomes `vehicle.speed [m/s]`;
4. RPMs becomes `engine.speed [rad/s]`;
5. Gear becomes integer `transmission.gear` with explicit Traqmate-derived/assigned semantic id;
6. `Accel (calc)` is not mapped to throttle;
7. `Brake (calc)` is not mapped to driver brake;
8. no steering mapping is invented;
9. Lap 4 / Lap 5 supporting timestamps begin at zero;
10. owned samples plus exactly one closing-boundary sample are used;
11. closing-boundary provenance records `shared_start_finish_evidence`;
12. source windows / source telemetry / Plan 028 request remain unchanged;
13. preparation is deterministic;
14. fingerprint/context/window mismatches are not-ready;
15. enriched Portland report exposes speed and engine-speed overlays;
16. enriched Portland report exposes gear overlay;
17. throttle, brake and steering remain explicit not-ready Missing Evidence;
18. report still contains no cause/hypothesis/engineering interpretation/recommendation.

## Boundary rule

The closing-boundary value may be referenced only as instantaneous shared start/finish evidence.

Do not relabel that row as an owned sample of the prior source lap.

## Layered execution packet

### Prompt Engineering

Objective:

> Add only verified Traqmate supporting evidence to the physical report, preserving source ownership and semantic uncertainty.

### Context Engineering

Required:

- Portland fixture;
- Plan 025 windows;
- Plan 026 physical reference preparation;
- Plan 028 base report request;
- accepted supporting-channel spec;
- Traqmate public semantic documentation.

Context readiness: **ready**.

### Harness Engineering

Test-first coverage plus canonical verify.

### Loop Engineering

```text
accepted source-semantic spec
-> focused tests
-> behavioral RED
-> minimum mph conversion + Traqmate profile/preparation
-> GREEN
-> physical source-to-report regression
-> full verify
```

### Graph Engineering

```text
PROMPT READY          = yes
CONTEXT READY         = yes
MATERIAL DECISION GAP = no
BEHAVIOR CHANGE       = yes
TESTABLE CONTRACT     = yes
NEXT STATE            = tests -> RED
```

Human gate reopens if implementation would need to infer throttle/brake/steering semantics or invent non-source endpoint values.

## Completion criteria

- Plan 028 archived;
- accepted supporting-channel v0.1 spec;
- tests before production behavior;
- behavioral RED recorded;
- mph conversion GREEN;
- exact Traqmate normalization/profile GREEN;
- shared boundary evidence explicit;
- Portland speed/RPM/gear overlays GREEN;
- throttle/brake/steering remain Missing Evidence;
- source/provenance immutability proven;
- canonical CI GREEN.

## Next plan boundary

After Plan 029, the physical workflow will contain a useful real-car report with delta observations plus the first trustworthy supporting channels.

A later plan may:

- expose this physical workflow through API/UI;
- add another verified physical source;
- expand the canonical ontology;
- evaluate brake/throttle evidence only when source semantics justify it.

## Explicitly out of scope

- mapping `Accel (calc)` to throttle;
- mapping `Brake (calc)` to driver brake;
- steering inference;
- Formula Student source integration;
- setup/driver diagnosis;
- AI interpretation.
