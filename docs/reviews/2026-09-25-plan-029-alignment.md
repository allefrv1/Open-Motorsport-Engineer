# Engineering Council Review — Plan 029 Traqmate Supporting Evidence

Date: 2026-09-25

Plan:

`docs/plans/active/029-traqmate-physical-supporting-evidence-foundation.md`

Decision: **READY_WITH_ACTIONS**

## Objective

Enrich the Portland physical-car report using only verified Traqmate speed, engine-speed and gear evidence.

Keep throttle, brake and steering explicit Missing Evidence.

## Evidence reviewed

- accepted Plan 029;
- Traqmate supporting-channel v0.1 specification;
- canonical channel vocabulary;
- lap-comparison report v0.1;
- accepted source/provenance rules.

## Software / Architecture review

Assessment:

The plan stays within existing normalization/preparation/report boundaries.

The generic addition `mph_to_mps` is small and deterministic.

The source-specific mappings belong in the Traqmate profile rather than the generic ontology.

Source windows and Plan 028 request are explicitly immutable.

Decision:

READY.

Action:

TDD must prove source objects remain unchanged and exact source identifiers are required.

## Motorsport Mechanical Engineering review

Engineering question:

Which Traqmate channels can truthfully support comparison interpretation?

Assessment:

### Velocity (MPH)

Appropriate for canonical `vehicle.speed` only at the broad vehicle-speed level.

Do not relabel the acquisition method as ECU/wheel speed.

### RPMs

Appropriate for `engine.speed` with explicit RPM -> rad/s conversion provenance.

### Gear

Useful as comparison evidence, but the accepted Traqmate semantics indicate the value may be assigned/derived.

It must remain labeled:

`transmission.gear.traqmate_derived_or_assigned`

### Accel (calc)

Must not become throttle.

Longitudinal acceleration and driver throttle demand are different physical/engineering quantities.

### Brake (calc)

Must not become driver brake.

A calculated braking/deceleration quantity is not pedal position, pedal force or brake pressure.

### Steering

No trustworthy evidence is present.

Keep Missing Evidence.

References:

- current accepted Traqmate source-semantic specification;
- Motorsport Engineering Reference Library for future mechanism/analysis work.

Decision:

READY.

Missing evidence:

- driver throttle;
- trustworthy brake input;
- steering input.

Do not block the base report because these are optional supporting concepts.

## Physics review

### MPH conversion

```text
m/s = mph * 0.44704
```

Dimensionally valid deterministic conversion.

### Engine speed

```text
rad/s = rpm * 2*pi/60
```

Dimensionally valid deterministic conversion.

### Calculated acceleration/brake

Acceleration/deceleration is not dimensionally or semantically equivalent to a dimensionless throttle fraction or a brake-input measurement.

No transformation should pretend otherwise.

### Closing boundary

Using the next source-lap row as a shared instantaneous boundary reference is acceptable only if provenance continues to state that the sample is owned by the next source lap.

Decision:

READY_WITH_ACTION.

Action:

Tests must prove the boundary is referenced, not reassigned.

## Cross-discipline discussion

Agreements:

- promote only Velocity/RPM/Gear;
- keep ambiguous driver channels absent;
- preserve source semantics;
- do not expand interpretation/causality in this plan;
- TDD before production behavior.

Disagreements:

None requiring a human gate.

Improvement options:

After Plan 029, use the enriched physical report to identify which additional physical channels would most increase diagnostic power before expanding the canonical ontology.

## Decision

Selected:

**READY_WITH_ACTIONS**

## Kanban transition

Plan 029 remains:

`DOING`

No additional product plan should be pulled.

## Actions

- [ ] Execute Plan 029 TDD targets.
- [ ] Preserve Missing Evidence for throttle/brake/steering.
- [ ] Preserve explicit shared-boundary ownership.
- [ ] Run delivery council review if implementation introduces any new physical semantic assumption.

## Human gate

Required:

No, under the current accepted spec.

Reopen the CEO/maintainer gate if scope expands to inferred throttle/brake/steering or causal setup/driver interpretation.
