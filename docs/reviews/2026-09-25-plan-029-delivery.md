# Engineering Council Delivery Review — Plan 029 Traqmate Supporting Evidence

Date: 2026-09-25

Plan:

`Plan 029 — Traqmate Physical Supporting Evidence Foundation`

PR:

`#70 — feat: add Traqmate physical supporting evidence`

Decision: **READY**

## Objective

Verify that the delivered implementation enriches the Portland physical-car comparison report only with accepted Traqmate speed, engine-speed and gear evidence while preserving unsupported driver inputs as Missing Evidence.

## Evidence reviewed

- accepted Traqmate supporting-channel v0.1 specification;
- Plan 029 TDD tests;
- implementation changes in normalization/application layers;
- behavioral RED: OME CI #373;
- final GREEN: OME CI #380;
- first Engineering Council alignment review.

## Software / Architecture review

Assessment:

- `mph_to_mps` is implemented as a deterministic generic conversion primitive;
- source-specific Traqmate mappings remain outside the generic canonical ontology;
- normalization rules match exact source identifiers;
- supporting evidence is prepared in a dedicated application service;
- the existing Plan 028 base comparison request is reused rather than recomputed;
- source dataset, physical preparation and base request are not mutated;
- closing-boundary use is recorded in typed transformation provenance;
- no driver/setup interpretation entered the deterministic report layer.

TDD:

- behavioral RED was the missing Plan 029 production API in CI #373;
- formatter/lint failures during GREEN iteration were classified as harness/mechanical failures;
- canonical verify passed in CI #380.

Decision:

READY.

## Motorsport Mechanical Engineering review

Engineering question:

Does the delivered report expose only supporting signals whose source semantics are defensible for the physical Traqmate workflow?

Assessment:

### Velocity (MPH)

Promoted only to broad `vehicle.speed`.

The implementation does not claim ECU speed, wheel speed or another acquisition method.

### RPMs

Promoted to `engine.speed` with deterministic unit conversion.

### Gear

Promoted to `transmission.gear` while retaining:

`transmission.gear.traqmate_derived_or_assigned`

The implementation does not misrepresent gear as a directly measured selector signal.

### Unsupported driver channels

The delivered report keeps:

- `driver.throttle`;
- `driver.brake`;
- `driver.steering`;

as Missing Evidence.

`Accel (calc)` is not mapped to throttle.

`Brake (calc)` is not mapped to driver brake.

No steering inference is introduced.

Reference policy:

No additional book lookup was required for these source-channel mappings because the governing question is source semantics, where the accepted Traqmate source documentation/specification has higher precedence than general vehicle-dynamics books.

The Motorsport Engineering Reference Library remains mandatory when later work introduces vehicle-dynamics mechanisms, diagnostic rules or setup recommendations.

Decision:

READY.

## Physics review

### Velocity conversion

```text
m/s = mph * 0.44704
```

Dimensionally valid and deterministic.

### Engine-speed conversion

```text
rad/s = rpm * 2*pi/60
```

Dimensionally valid and deterministic.

### Time axis

Prepared supporting timestamps are explicit lap-relative time derived from source `Elapsed Time`.

No resampling is introduced.

### Boundary evidence

The next-lap source row is used only as one instantaneous shared start/finish boundary sample.

Provenance retains:

`shared_start_finish_evidence`

and does not reassign source-lap ownership.

### Semantic separation

Calculated acceleration/deceleration signals remain physically distinct from throttle/brake-input measurements.

Decision:

READY.

## Cross-discipline discussion

Agreements:

- implementation satisfies the accepted Plan 029 scope;
- no new physical semantic assumption was introduced;
- Missing Evidence is preserved correctly;
- provenance is sufficient for the promoted channels;
- no causal engineering claim is generated.

Disagreements:

None.

## Decision

Selected:

**READY**

## Kanban transition

```text
DOING -> REVIEW
```

After merge and canonical main state verification/document synchronization:

```text
REVIEW -> DONE
```

## Actions before merge

- [x] behavioral RED recorded;
- [x] focused implementation added;
- [x] canonical verify GREEN;
- [x] specialist delivery review complete;
- [x] unsupported throttle/brake/steering remain Missing Evidence.

## Human gate

Not required for the implemented scope.

Reopen the CEO/maintainer gate if future work attempts to infer driver inputs, add setup/driver diagnosis, or change the accepted source semantics.
