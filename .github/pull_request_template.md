## Problem

What problem does this change address?

## What changed

Describe the focused change.

## Requirement / ADR / Spec

Link the relevant requirement, ADR or accepted specification when applicable.

## Layered engineering trace

For substantial work:

- Prompt/objective:
- Context sources:
- Decision gate: none / link to decision artifact
- Failure classes encountered:
- RED evidence or reason TDD is N/A:
- GREEN/focused evidence:

Do not count formatting, environment or harness failures as behavioral RED.

## Validation

- [ ] `uv run --locked python scripts/harness.py verify` passes
- [ ] Relevant tests were added or updated
- [ ] Documentation remains consistent
- [ ] Architecture boundaries remain valid
- [ ] Fixture/provenance metadata was updated when data changed
- [ ] No unrelated changes were introduced
- [ ] Any material decision gap was resolved explicitly rather than buried in code

## Engineering / data considerations

If applicable, document:

- units
- provenance
- missing-data behavior
- deterministic behavior
- domain assumptions

## Risks / limitations

What remains uncertain or intentionally out of scope?
