# Plan 020 — Real Motorsport Validation Foundation

Status: **Active**

Started: 2026-09-23

## Objective

Validate OME's completed first vertical slice against real physical-vehicle telemetry and realistic dataset scale before adding new engineering algorithms.

The purpose is to discover where the current evidence model is sufficient, where analysis is correctly not ready, and which next capability is justified by real data.

## Why now

Plans 003–019 established an end-to-end controlled path:

```text
source
-> import
-> validate
-> normalize
-> context
-> compare
-> observe
-> report
-> local API
-> browser investigation
```

The next architecture question is not whether OME can execute this path on controlled fixtures.

It is whether the assumptions survive imperfect physical-car telemetry.

## Primary validation source

Committed licensed fixture:

`fixtures/public/exit-speed/traqmate-parking-lot.csv`

Source:

- `djhedges/exit_speed`;
- Apache-2.0;
- real vehicle;
- Traqmate Trackvision CSV.

Observed shape:

- 1,962 telemetry rows;
- 196.1 seconds;
- 10 Hz declared cadence;
- 3 source lap identifiers;
- elapsed time;
- latitude / longitude;
- altitude;
- velocity;
- no explicit `lap.distance`.

This last point is intentionally important: OME must not invent a comparison reference to make the dataset pass.

## External scale source

The same Apache-2.0 upstream repository contains larger Portland International Raceway logs:

- `2019-08-18_Portland_CORRADO_DJ_R03.csv` — approximately 20.3 MB;
- `2019-08-18_Portland_CORRADO_DJ_R03_stripped.csv` — approximately 15.4 MB.

These remain external benchmark inputs unless repository-size policy changes.

## Validation questions

Plan 020 must answer with executable evidence where practical:

1. Can OME represent the Traqmate source structure without losing preamble/channel semantics?
2. Which current validation rules pass/fail on the real fixture?
3. Which channels can be mapped deterministically without fuzzy guessing?
4. Can the source-provided Lap marker be preserved as trusted context?
5. Does the current comparison stack correctly refuse comparison when no trustworthy `lap.distance` exists?
6. What exact evidence is missing for the first lap-comparison workflow?
7. Does realistic source size expose unacceptable import/validation performance or memory behavior?
8. Does the evidence justify a new source adapter, explicit source profile, GPS track-position derivation, or no new code yet?

## Decision rule

Do not implement GPS-derived lap distance merely because the source contains coordinates.

ADR-0009 requires a trustworthy monotonic positional reference.

Any derived spatial reference must be proposed separately with:

- physical meaning;
- deterministic algorithm;
- projection/reference method;
- uncertainty/failure behavior;
- provenance;
- tests against known geometry.

Plan 020 may recommend such a follow-up plan, but does not bury that decision inside validation.

## TDD / characterization rule

Existing behavior may be characterized first because Plan 020 is fundamentally validation of an existing system.

New deterministic behavior still follows TDD:

```text
REAL-DATA QUESTION
-> CHARACTERIZATION / ACCEPTANCE TEST
-> OBSERVED RESULT
-> GAP CLASSIFICATION
-> NEW TEST ONLY IF NEW BEHAVIOR IS JUSTIFIED
-> RED
-> MINIMUM CHANGE
-> GREEN
```

Do not change production behavior merely to make the real fixture appear supported.

## Initial executable targets

- deterministic fixture characterization;
- exact sample/lap counts;
- cadence/timestamp checks;
- source metadata/channel inventory;
- explicit missing `lap.distance` readiness outcome;
- no silent GPS-to-distance derivation;
- no silent generic CSV claiming;
- performance measurement for the committed 1,962-row fixture;
- optional local benchmark instructions for the external Portland files.

## Source-support decision

Plan 020 begins as validation, not automatically as a Traqmate adapter project.

If existing import contracts cannot represent the real fixture without a source adapter, document that as a concrete gap and open the smallest follow-up plan.

Do not turn OME CSV into a universal CSV parser.

## Relationship to MVP

The controlled MVP path is now implemented.

Plan 020 validates the stronger claim:

> OME can confront real physical-car data, preserve what is known, and clearly state when evidence is insufficient for a requested engineering comparison.

A correct `not ready` result is a successful engineering outcome when the source lacks a trustworthy comparison reference.

## Performance boundary

TD-005 is measured here, not prematurely optimized.

Record:

- fixture size;
- row/channel counts;
- import/validation elapsed time when a supported path exists;
- peak-memory concerns when observable;
- any algorithmic scaling defect.

Only create optimization work when measurements justify it.

## Completion criteria

- Plan 019 archived;
- real Traqmate fixture characterized by executable tests or deterministic tooling;
- current support/gaps documented;
- comparison-readiness result is explicit;
- no hidden positional derivation introduced;
- external Portland benchmark procedure documented;
- TD-002 / TD-005 status updated with evidence;
- next engineering plan chosen from observed gaps;
- canonical verify GREEN.

## Explicitly out of scope

- generic GPS track reconstruction;
- automatic lap detection;
- native MoTeC `.ld`;
- adding every Traqmate feature;
- optimizing without measurements;
- Formula SAE outreach completion;
- AI interpretation.
