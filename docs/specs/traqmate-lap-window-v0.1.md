# Traqmate Source Lap Window Specification v0.1

Status: **Accepted for Plan 025**

Date: 2026-09-24

## Purpose

Define the smallest deterministic application-level rule for selecting one complete lap window from Traqmate Trackvision telemetry that uses sparse source `Lap` boundary markers.

This specification does not change ingestion behavior.

## Source semantics

For the verified Portland Trackvision source:

- a non-empty `Lap=N` cell marks the first telemetry sample of source Lap N;
- following rows may leave `Lap` empty;
- the next non-empty Lap marker begins the next source lap and therefore closes the previous lap window.

OME must not fill sparse Lap cells or reinterpret them as dense labels.

## Explicit selection

The caller supplies the desired source lap number.

v0.1 never automatically chooses:

- fastest lap;
- first complete lap;
- best lap;
- median lap.

## Complete lap rule

For requested source Lap N:

1. locate exactly one marker `Lap=N`;
2. locate the next non-empty source Lap marker after it;
3. the telemetry sample window for Lap N is:

```text
[start_index, next_marker_index)
```

4. the next marker sample is **not** part of Lap N telemetry samples;
5. preserve that next sample separately as:

`closing_boundary_index = next_marker_index`

This distinction is intentional.

The closing boundary sample belongs to the next source lap, but later geometric preparation may need that GPS point to close the physical circuit.

## Portland v0.1 evidence

For the committed fixture:

`fixtures/public/exit-speed/traqmate-portland-laps-4-5.csv`

expected source windows are:

### Lap 4

```text
start_index            = 0
end_index_exclusive    = 3618
closing_boundary_index = 3618
sample_count           = 3618
start_elapsed_s        = 885.900
closing_elapsed_s      = 976.350
```

### Lap 5

```text
start_index            = 3618
end_index_exclusive    = 7249
closing_boundary_index = 7249
sample_count           = 3631
start_elapsed_s        = 976.350
closing_elapsed_s      = 1067.125
```

### Lap 6

Lap 6 is incomplete in this fixture because no later source boundary marker is present.

It must return explicit not-ready evidence.

## Output artifact

The application layer may expose an immutable `SourceLapWindow` containing at least:

- dataset fingerprint;
- source identity;
- source type;
- source lap-marker channel identifier;
- requested source lap number;
- start index;
- end index exclusive;
- closing boundary index;
- start elapsed time;
- closing boundary elapsed time;
- sample count.

The artifact references the imported dataset.

It does not copy or mutate source telemetry.

## Readiness / failure

Return explicit not-ready evidence for:

- unsupported source type/profile;
- missing `Lap` source channel;
- missing explicit elapsed-time evidence;
- requested lap marker absent;
- requested lap marker duplicated;
- no later non-empty boundary marker;
- next boundary not strictly after start;
- non-numeric/non-finite boundary time;
- source/evidence length inconsistency;
- missing dataset provenance.

Do not guess or repair.

## Boundary ownership

This transformation belongs in application/preparation, not ingestion.

Ingestion continues to preserve sparse source cells exactly.

This slice does not:

- create canonical Session / Run / Lap automatically;
- rank laps;
- derive GPS distance;
- project GPS to a track reference;
- build a comparison;
- produce an engineering interpretation.

## Determinism

Equivalent imported source evidence and requested lap number must produce the same window result.

## Related artifacts

- REQ-001 — source evidence preservation;
- REQ-003 — explicit operational context;
- Plan 024 — Portland extended Trackvision source evidence;
- Common Track Reference Specification v0.1.
