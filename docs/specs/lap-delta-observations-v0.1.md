# Lap Delta Observations Specification v0.1

Status: **Accepted for Plan 013**

Date: 2026-09-22

## Purpose

Define the first deterministic OME observation layer above the accepted two-lap delta-time result.

The purpose is to answer:

> Over which distance regions did Lap B gain or lose relative time versus Lap A?

without assigning a cause.

## Input

Input is one successful v0.1 lap comparison produced by:

`ome.lap-comparison.distance-linear / 0.1.0`

Required fields:

- distance grid in metres;
- `delta_B_vs_A` in seconds;
- complete comparison provenance.

The observation engine does not re-align laps or recalculate source telemetry.

## Delta convention

Existing convention remains authoritative:

`delta_B_vs_A(d) = time_B(d) - time_A(d)`

Therefore, over one interval:

`delta_change = delta_end - delta_start`

Interpretation:

- `delta_change < 0` — Lap B **gained** relative time;
- `delta_change > 0` — Lap B **lost** relative time;
- numerically zero — **neutral**.

This is an observation of the comparison metric, not a causal explanation.

## Numerical zero tolerance

Parameter:

`zero_tolerance_s = 1e-9`

Rules:

- finite;
- greater than or equal to zero;
- used only to absorb floating-point numerical noise;
- not an engineering significance threshold.

For one interval:

- `delta_change < -zero_tolerance_s` -> B_GAIN;
- `delta_change > +zero_tolerance_s` -> B_LOSS;
- otherwise -> NEUTRAL.

A future significance/filtering rule must be a separate explicit transformation.

## Region construction

1. Validate the base comparison.
2. Classify each adjacent distance interval.
3. Merge consecutive intervals with the same classification.
4. Preserve exact first/last distance boundaries from the base grid.

A region contains:

- kind;
- start distance;
- end distance;
- start delta;
- end delta;
- total delta change;
- number of base-grid intervals.

For a merged region:

`total_delta_change = delta_at_region_end - delta_at_region_start`

No smoothing or hidden resampling is applied.

## Region kinds

- `b_gain`
- `b_loss`
- `neutral`

Neutral regions remain in the deterministic result so the full common interval is explainable.

Presentation layers may later filter them.

## Readiness

Return explicit not-ready evidence when:

- base comparison is missing;
- comparison algorithm identity/version is incompatible;
- distance/delta lengths differ;
- fewer than two grid points exist;
- distance or delta contains non-finite values;
- distance grid is not strictly increasing;
- zero tolerance is invalid;
- comparison provenance is incomplete.

Do not repair malformed comparison artifacts.

## Provenance

Observation provenance must retain:

- observation algorithm id/version;
- parameters including `zero_tolerance_s`;
- complete base comparison provenance.

Algorithm:

`ome.lap-observation.delta-regions`

Version:

`0.1.0`

## Evidence vocabulary

The output is **Observation**, not:

- source measurement;
- causal hypothesis;
- engineering interpretation;
- setup recommendation.

The underlying delta remains a deterministic derived metric.

Conceptual chain:

```text
DeltaRegionObservation
  -> delta-time metric
  -> lap-comparison transformation
  -> time/distance canonical evidence
  -> source channels
  -> original datasets
```

## Out of scope

- speed/throttle/brake/steering attribution;
- braking-point detection;
- corner segmentation;
- significance ranking;
- driver scoring;
- cause;
- hypothesis;
- setup recommendation;
- AI explanation;
- UI.

## Related artifacts

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence
- ADR-0009 — Align initial lap comparisons by monotonic lap distance
- `docs/specs/lap-comparison-v0.1.md`
