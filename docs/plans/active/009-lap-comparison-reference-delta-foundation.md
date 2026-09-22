# Plan 009 — Lap Comparison Reference and Delta-Time Foundation

Status: **Active**

Started: 2026-09-22

## Objective

Define and implement the smallest deterministic two-lap comparison foundation satisfying REQ-005 and the relevant evidence requirements of REQ-006.

The first goal is not a rich analysis UI.

The goal is a trustworthy answer to:

> At a given explicit position around the lap, how much time separates Lap A and Lap B, and which source evidence produced that result?

## Requirements

Primary:

- REQ-005 — Compare Two Laps
- REQ-006 — Preserve Analysis Evidence

Supporting domain/architecture:

- `docs/domain/session-run-lap.md`
- `docs/CORE_BELIEFS.md`
- `docs/ARCHITECTURE.md`
- `docs/QUALITY_ATTRIBUTES.md`

## Mandatory pre-implementation decision

REQ-005 explicitly leaves this architecture question open:

> The exact positional alignment algorithm and distance representation must be selected and documented before implementation.

Therefore production lap-comparison code must not begin until Plan 009 has:

1. reviewed engineering references/current tool practice;
2. defined comparison readiness;
3. selected the positional reference;
4. selected interpolation/alignment behavior;
5. defined delta-time sign convention;
6. defined evidence/provenance fields;
7. recorded the decision in an ADR or accepted analysis specification.

## Research questions

### Positional reference

Evaluate:

- source-provided lap distance in metres;
- source-provided normalized lap progress;
- deterministic distance derived from validated telemetry;
- GPS/track-centerline projection.

Prefer the smallest reference that is:

- source-independent at the comparison boundary;
- monotonic within a valid lap;
- physically interpretable;
- reproducible;
- available from the initial source families without hidden inference.

### Common comparison grid

Decide whether the first slice should compare on:

- union of source distance samples;
- one lap's distance samples;
- fixed distance step;
- another deterministic grid.

The choice must document interpolation and endpoint behavior.

### Time as a function of distance

Define how OME obtains:

`t_A(d)` and `t_B(d)`

without silently resampling source telemetry.

Any interpolation used by comparison is a named deterministic analysis transformation, not ingestion repair.

### Delta sign

Choose and document one convention, for example:

`delta_time(d) = t_B(d) - t_A(d)`

The UI/explanation must not reverse signs implicitly.

### Readiness

Define blocking conditions such as:

- laps not belonging to trustworthy LapContext;
- missing positional reference;
- non-monotonic comparison position;
- missing/invalid time;
- insufficient overlap;
- incompatible reference units/semantics.

A comparison that is not ready must return explicit missing evidence rather than a plausible-looking curve.

## Initial comparison evidence

The result must be traceable to:

- dataset fingerprint(s);
- Session / Run / Lap identifiers;
- source channels used for time/reference;
- normalization/transformation identities when applicable;
- alignment algorithm id/version;
- parameters;
- comparison grid;
- output units.

## Observation boundary

The first slice may state deterministic facts such as:

- Lap B is +0.120 s relative to Lap A at distance d;
- Lap A has lower/higher measured speed at a position if that source evidence is requested and available.

It must not automatically claim:

- braking technique caused the loss;
- understeer caused the delta;
- setup X is better;
- driver Y made a mistake.

Those are later observations/hypotheses/engineering interpretation layers.

## TDD rule

After the alignment decision is accepted, behavior is implemented test-first:

```text
REQ-005 ACCEPTANCE CRITERION
-> SYNTHETIC KNOWN LAPS
-> RED FOR MISSING COMPARISON BEHAVIOR
-> MINIMUM DETERMINISTIC IMPLEMENTATION
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

The synthetic laps must have analytically known expected delta-time behavior.

## First executable test targets

Once the algorithm is selected, tests should prove:

- explicit reference identity is present;
- same inputs/parameters produce identical delta;
- equal laps produce zero delta;
- a known constant/controlled time difference produces the expected sign/magnitude;
- missing required reference produces explicit not-ready/missing-evidence result;
- non-monotonic position is rejected;
- partial overlap behavior is explicit;
- provenance identifies both laps and algorithm version;
- context identifies Session / Run / Lap for both cases;
- no causal diagnosis is emitted.

## Evidence model relationship

REQ-006 should be used, not duplicated.

If the current evidence domain is insufficient for comparison provenance, extend it deliberately with tests rather than embedding opaque dictionaries in the comparison module.

## Architecture boundary

Lap comparison belongs in deterministic analysis/application layers.

It must not:

- parse source formats;
- repair ingestion data;
- guess channel semantics;
- use AI for delta calculations;
- depend on UI state;
- mutate source telemetry;
- silently choose between competing position channels.

## Completion criteria

- positional/alignment decision documented and accepted;
- readiness contract documented;
- evidence/provenance contract documented;
- tests written before production comparison behavior;
- behavioral RED recorded;
- deterministic comparison implementation GREEN;
- REQ-005 acceptance criteria mapped to executable tests;
- relevant REQ-006 evidence chain executable;
- canonical CI GREEN.

## Explicitly out of scope

- automatic causal diagnosis;
- corner segmentation;
- driver scoring;
- setup recommendations;
- GPS track reconstruction;
- live telemetry comparison;
- AI explanation;
- polished comparison UI.
