# Plan 005 — Telemetry Normalization Foundation

Status: **Completed**

Started: 2026-09-22

Completed: 2026-09-22

## Objective

Implement the smallest explicit and traceable normalization layer satisfying REQ-004 while preserving source identity and avoiding silent engineering guesses.

## Delivered

The normalization foundation now includes:

- canonical telemetry concept identifiers for the first vertical slice;
- explicit NormalizationRule identity/version;
- deterministic conversion identity/version;
- NormalizationMapping preserving source identifier, source name and source unit;
- NormalizationResult with mapped and unmapped channels;
- explicit unmapped reasons for:
  - no matching rule;
  - blocking validation evidence;
  - rule precondition mismatch;
  - ambiguous rule match;
  - conversion failure;
- deterministic conversions required by the controlled OME fixture:
  - numeric identity;
  - percentage points to normalized fraction;
  - RPM to radians/second;
  - integer identity;
- validation-result fingerprint check;
- normalization-local AGENTS.md constraints;
- architecture rule preventing normalization from depending on ingestion, validation implementation, analysis or API layers.

## Fixture correction

During implementation, the OME synthetic fixture exposed a semantic inconsistency:

- throttle/brake declared unit: `%`;
- values had been encoded as fractions such as `0.40`.

The fixture was corrected to percentage-point source values such as `40`.

Normalization now converts:

```text
40 %
-> explicit percent_to_fraction conversion
-> 0.40
```

The source value remains unchanged.

## Acceptance evidence

REQ-004 AC-001 through AC-006 are mapped to:

`tests/normalization/test_normalization.py`

Coverage proves:

- source identity/value preservation;
- explicit rule linkage;
- unmapped behavior instead of guessing;
- deterministic traceable conversions;
- similar speed sources remain separate mappings;
- rules/conversions are versioned and reproducible.

Additional regression coverage includes:

- blocking validation prevents mapping;
- unit/name precondition mismatch does not guess;
- duplicate explicit rules produce ambiguity;
- conversion failure leaves source evidence unchanged;
- mismatched validation fingerprint is rejected;
- import -> validate -> normalize preserves source timestamps.

## Harness feedback

PR #12 was intentionally iterated through multiple CI failures:

1. formatter detected non-canonical layout;
2. lint detected line-length violation;
3. static typing detected a nullable conversion contract;
4. final canonical verify passed.

No harness rule was weakened to obtain green CI.

## Verification evidence

Final verified head:

`1aec1160c92f32633553144d1352d9b4bb22e770`

Canonical CI:

`OME CI #27` — success.

Squash merge:

`c1e1f9e3db46057ca35574bd4113863918770740`

## Boundaries preserved

Not added:

- fuzzy matching;
- AI mapping;
- arbitrary name guessing;
- resampling;
- synchronization;
- derived engineering metrics;
- Session / Run / Lap organization;
- generic unit-conversion framework;
- complete canonical ontology.

## Completion assessment

All Plan 005 completion criteria are satisfied.
