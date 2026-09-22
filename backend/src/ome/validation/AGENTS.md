# Validation Module Instructions

This directory implements REQ-002 and the accepted data-quality model.

## Invariants

- Validation is non-destructive.
- Validation observes imported evidence; it does not repair it.
- Do not normalize channel identity here.
- Do not convert units here.
- Do not resample or interpolate here.
- Do not introduce source/vendor-specific parsing here.
- Do not invent physical thresholds without an accepted requirement or domain rule.
- Missing/ambiguous data must remain explicit.
- Validation issues should identify affected evidence when practical.
- A ValidationResult must not become a universal "good/bad for every analysis" decision.

## Dependencies

Validation may depend on source-independent domain concepts.

Validation must not depend on:

- API/UI;
- ingestion adapters;
- normalization;
- engineering analysis;
- generative AI.

## Verification

Changes must include focused tests and pass the repository canonical verification command.
