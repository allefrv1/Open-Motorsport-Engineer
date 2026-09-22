# Lap Comparison Numerical Decision Audit

Status: **Reviewed research**

Verified: 2026-09-22

## Purpose

Independently audit the already accepted OME lap-comparison numerical baseline before implementation.

Authoritative OME decisions already exist:

- ADR-0009 — Align initial lap comparisons by monotonic lap distance;
- `docs/specs/lap-comparison-v0.1.md`.

This research does not replace those artifacts.

It checks whether the accepted direction remains defensible against motorsport-analysis practice and implementation risks.

## External evidence

### MoTeC training — compare laps in distance mode

MoTeC training material describes overlaying a Main lap and a reference lap and states that lap comparison should be performed in distance mode rather than time mode.

The engineering reason is positional comparability:

- the same distance corresponds to the same place around the lap;
- time-aligned traces drift apart spatially as one lap gains or loses time;
- MoTeC's variance/delta-time view is a cumulative time difference between the compared laps.

Source:

- MoTeC Data Training Conference material:
  - https://www.motec.com.au/hessian/uploads/2015_DTC_Colour_Displays_v2_0_d7cc55fc75.pdf

This supports ADR-0009's primary decision to compare in the distance domain.

### FastF1 — distance is an explicit analysis channel

FastF1 exposes distance/relative-distance as derived telemetry channels and documents that distance may be integrated over a lap.

Its project discussions also describe lap-delta comparison as requiring a relation between time and covered lap distance.

Sources:

- https://github.com/theOehrly/Fast-F1
- https://github.com/theOehrly/Fast-F1/discussions/83

This independently supports representing elapsed time as a function of position rather than matching telemetry by sample index or wall-clock time.

### Interpolation must remain explicit

FastF1 documentation warns that resampling creates interpolated values and that repeated/up-frequency resampling can reduce accuracy.

Source:

- https://github.com/theOehrly/Fast-F1/blob/main/fastf1/core.py
- https://github.com/theOehrly/Fast-F1/discussions/258

OME's v0.1 design is deliberately narrower:

- source telemetry is never rewritten;
- interpolation occurs only inside a named analysis artifact;
- only elapsed time is interpolated in the first delta-time slice;
- the interpolation rule is fixed and versioned;
- no extrapolation is allowed.

This preserves the distinction between measured source evidence and derived comparison evidence.

## Why the accepted OME baseline remains appropriate

### 1. Distance metres is the first reference

`lap.distance [m]` is preferable to time for the initial comparison because it represents comparable physical progress around the lap.

It is preferable to requiring GPS geometry because many motorsport sources already expose a trustworthy lap-distance channel.

Normalized lap percentage remains useful but is not silently substituted for metres.

### 2. Strict monotonicity is intentionally conservative

Real sources may contain duplicate/plateau distance samples.

The v0.1 contract rejects those laps as not ready instead of silently:

- deduplicating;
- choosing first/last samples;
- averaging repeated positions;
- modifying the source.

A plateau policy can be added later as a versioned transformation.

### 3. Common interval only

The accepted interval:

```text
start = max(first_distance_A, first_distance_B)
end   = min(last_distance_A, last_distance_B)
```

avoids extrapolation.

This makes partial overlap visible rather than fabricating behavior outside measured evidence.

### 4. Fixed 1 m grid is a reasonable foundation parameter

The accepted 1.0 m default creates a deterministic, symmetric comparison grid that does not privilege Lap A or Lap B's original sampling points.

For a several-kilometre circuit, the output remains small enough for the first local-analysis slice.

The grid step is an explicit parameter and therefore can be changed/versioned later without pretending the result was measured at 1 m intervals.

### 5. Linear time-vs-distance interpolation

Linear interpolation is transparent and reproducible.

For the initial task — elapsed time at a position between adjacent validated samples — it avoids spline overshoot and hidden smoothing.

This does not imply that all telemetry channels should later use linear interpolation.

Discrete channels such as gear require separate rules.

### 6. Delta sign must be invariant

The accepted convention:

```text
delta_B_vs_A = time_B - time_A
```

has an unambiguous meaning:

- positive → B is behind A at that distance;
- negative → B is ahead of A;
- zero → equal accumulated elapsed time.

Callers and future UI must not invert this silently.

## Important caution from external tooling

Open motorsport/F1 tools often implement lap delta using distance-domain resampling/interpolation, but their exact numerical implementations and data assumptions vary.

OME must not copy a third-party helper as an authority.

The accepted OME spec remains the source of truth because it explicitly defines:

- canonical inputs;
- readiness;
- units;
- common interval;
- grid;
- interpolation;
- sign;
- algorithm id/version;
- evidence/provenance;
- not-ready behavior.

## Audit conclusion

No change to ADR-0009 or `lap-comparison-v0.1` is recommended before the first implementation.

The accepted numerical contract is consistent with established motorsport lap-comparison practice while remaining conservative about interpolation and missing evidence.

Plan 009 can proceed to TDD implementation.

## Implementation guardrails confirmed

- tests before production comparison behavior;
- analytical fixtures with known expected delta;
- no source mutation;
- no extrapolation;
- no hidden fallback from distance metres to another position concept;
- no causal diagnosis;
- comparison result must preserve evidence chain for both laps;
- behavior-changing numerical changes require algorithm/spec version changes.
