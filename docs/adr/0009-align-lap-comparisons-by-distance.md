# ADR-0009 — Align initial lap comparisons by monotonic lap distance

Status: **Accepted**

Date: 2026-09-22

## Context

Two laps recorded at different speeds and sample times cannot be compared meaningfully by matching sample index or elapsed time alone.

OME needs a deterministic reference that answers:

> What was each lap doing at the same place on track?

## Decision

For the first vertical slice, comparable laps are aligned using a trustworthy monotonic `lap.distance` reference.

Conceptually:

1. validate each lap's time and distance references;
2. determine their common comparable distance interval;
3. create an analysis-only distance grid;
4. interpolate required comparison quantities onto that grid using documented deterministic rules;
5. derive elapsed time as a function of distance;
6. calculate delta time from the two time-vs-distance functions.

Source samples are never overwritten.

The aligned series are derived analysis artifacts with their own provenance.

## Delta convention

For:

```text
delta_B_vs_A(d) = time_B(d) - time_A(d)
```

- positive delta means B has taken more time than A to reach distance `d`;
- negative delta means B has taken less time than A.

UI wording must make the selected reference explicit.

## Readiness requirements

A lap is not ready for this comparison if:

- lap distance is unavailable and no accepted deterministic derivation exists;
- the distance reference is materially non-monotonic;
- lap timing is unreliable;
- the overlap region is insufficient.

OME must report the reason rather than invent alignment.

## Interpolation

Initial numerical interpolation for continuous channels/time-vs-distance should use a documented deterministic interpolation rule.

Linear interpolation is the baseline choice for the first implementation unless a channel's semantics require a different explicit rule.

Discrete channels such as gear must not be treated as continuous numeric quantities without a channel-specific rule.

## Why not align by time?

Time alignment compares different physical track positions when laps differ in pace.

It is useful for some analyses but does not answer the first lap-performance question as directly.

## Why not require GPS geometry?

GPS-based geometric projection may become useful later, but making it mandatory would exclude sources that already provide trustworthy lap-distance channels.

## Consequences

- lap comparison requires a valid positional reference;
- comparison resampling is explicitly derived, not a mutation of raw telemetry;
- the algorithm remains deterministic and testable;
- future track-map/geometric alignment can be added without redefining source ingestion.

## Related requirements

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
