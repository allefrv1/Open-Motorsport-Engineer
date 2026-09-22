# Plan 005 — Telemetry Normalization Foundation

Status: **Active**

Started: 2026-09-22

## Objective

Implement the smallest explicit and traceable normalization layer satisfying the foundational behavior of REQ-004 while preserving source identity and avoiding silent engineering guesses.

## Requirement

Primary:

- REQ-004 — Normalize Telemetry Channels

Supporting contracts:

- `docs/domain/canonical-channels-v0.1.md`
- `docs/domain/telemetry-import-model.md`
- `docs/domain/provenance.md`
- ADR-0001 — ingestion, validation and normalization are separate
- ADR-0003 — deterministic before generative
- `docs/CORE_BELIEFS.md` — source data is evidence; unknown is a valid state

## Scope

Create a source-independent normalization model and deterministic rule mechanism.

The first slice should establish:

- CanonicalConcept identifier;
- explicit NormalizationRule identity/version;
- NormalizationMapping from one SourceChannel to one canonical concept;
- deterministic optional unit conversion metadata;
- NormalizationResult with mapped and unmapped source channels;
- explicit reasons when a mapping cannot be applied safely.

## Initial rule strategy

Do **not** infer mappings from free-form channel names globally.

Use explicit rules authored for known source/profile semantics.

The OME-owned CSV fixture may supply deterministic test mappings because its source meaning is controlled by the project.

Examples suitable for the first tests:

- known OME fixture speed source -> `vehicle.speed`;
- known OME fixture throttle source -> `driver.throttle`;
- known OME fixture steering source -> `driver.steering`;
- known OME fixture RPM source -> `engine.speed`;
- known gear source -> `transmission.gear`.

A rule must state the source semantics it expects.

## Unit conversions

Implement only conversions required by accepted canonical concepts and test fixtures.

Every conversion must be:

- deterministic;
- explicit;
- versioned through the rule;
- traceable to source unit and target unit;
- separate from original source values.

Do not mutate SourceChannel or SampleSeries.

Likely first conversions:

- km/h -> m/s if a fixture/rule requires it;
- percent -> normalized fraction where source semantics are explicitly known;
- degrees -> radians for steering when sign convention is explicitly known;
- RPM -> radians/second for engine speed if canonical output requires it.

Do not add a generic unit-conversion framework merely for future completeness.

## Ambiguity behavior

If a channel cannot be mapped safely:

- preserve it unchanged;
- mark it as unmapped;
- record a reason;
- do not guess from similarity.

GPS speed, wheel speed and ECU speed must remain distinguishable source evidence even if one is mapped to the broad `vehicle.speed` concept.

## Validation boundary

Normalization consumes source channels whose validation evidence is available to the calling workflow.

The normalization module must not become a validator.

Do not duplicate validation checks except for preconditions specifically required by a normalization rule.

## Architecture constraints

- normalization may depend on domain;
- normalization must not depend on API/UI;
- normalization must not depend on ingestion adapters;
- normalization must not depend on analysis;
- normalization must not use generative AI;
- normalization must not mutate imported telemetry.

## Test strategy

Add direct deterministic unit tests plus one integration flow:

```text
OME CSV import
-> validate
-> normalize
```

Acceptance tests should explicitly map REQ-004 AC-001 through AC-006.

Tests must prove:

- source identity remains intact;
- rules are explicit/versioned;
- ambiguous channels stay unmapped;
- conversions are deterministic and traceable;
- similar speed sources are not automatically collapsed;
- repeated normalization with same inputs/rules is reproducible.

## Completion criteria

- normalization domain/result model exists;
- explicit rule contract exists;
- initial fixture-driven rules exist;
- required deterministic conversions exist;
- REQ-004 AC-001 through AC-006 have executable traceability;
- imported/source data remains unchanged;
- validation/normalization separation is preserved;
- architecture harness remains green;
- canonical CI is green.

## Explicitly out of scope

- arbitrary vendor channel-name guessing;
- AI mapping;
- fuzzy matching;
- resampling;
- synchronization;
- derived engineering metrics;
- Session / Run / Lap organization;
- UI mapping wizard;
- complete unit-conversion library;
- full canonical telemetry ontology.
