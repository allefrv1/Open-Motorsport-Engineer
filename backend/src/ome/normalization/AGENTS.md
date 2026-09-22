# Normalization Module Instructions

This directory implements REQ-004.

## Invariants

- Preserve SourceChannel identity and source values.
- Mapping must be explicit; never guess from similar names.
- Rules that affect engineering meaning must have an identity and version.
- Unit/value conversion must be deterministic and traceable.
- An unmappable channel stays unmapped.
- Multiple source channels may map to the same broad canonical concept; never silently collapse them.
- Do not resample, synchronize or derive engineering metrics here.
- Do not perform source parsing here.
- Do not perform generic data repair here.
- Do not use generative AI for authoritative mapping.

## Dependencies

Normalization may depend on source-independent domain concepts.

Normalization must not depend on:

- API/UI;
- ingestion adapters;
- validation implementation;
- engineering analysis;
- generative AI.

Validation evidence may enter through source-independent domain contracts.

## Verification

Changes must map to REQ-004 acceptance criteria and pass the canonical repository verification command.
