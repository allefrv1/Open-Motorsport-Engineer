# Validation module instructions

These rules apply to `backend/src/ome/validation/`.

## Responsibility

Validation answers:

> What limitations or structural/data-quality problems are visible in the imported evidence?

## Required behavior

- Validation is non-destructive.
- Every issue has an explicit category, severity and human-readable explanation.
- Scope issues to a dataset/channel/time region when evidence permits.
- Aggregate repeated sample-level defects instead of emitting unbounded issue counts.
- Keep checks deterministic.
- Preserve analysis-specific readiness as a later concern.

## Forbidden behavior

Do not:

- mutate imported samples or metadata;
- interpolate, resample or fill values;
- convert units;
- normalize channel names/concepts;
- make engineering diagnoses;
- invent universal physical ranges or spike/frozen thresholds;
- depend on API/UI, ingestion adapters, normalization or analysis modules.

When a quality rule needs a domain-specific threshold, document/accept that rule before implementing it.
