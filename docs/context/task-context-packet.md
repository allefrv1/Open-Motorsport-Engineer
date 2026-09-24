# Task Context Packet

Status: **Accepted template**

## Purpose

Provide a compact Context Engineering checklist for substantial OME work.

This is not a file that must be committed for every task.

It is a preparation format.

## Packet

### Problem

What concrete problem is being solved?

### Normative source

- Requirement:
- ADR:
- Spec:
- Domain rule:

### Current execution

- Active plan:
- Current implementation:
- Existing tests:
- Existing behavior:

### Data/evidence

- Fixture:
- Dataset:
- Provenance:
- External reference:
- Licensing/redistribution constraints:

### Architecture

- Module responsibility:
- Allowed dependencies:
- Forbidden dependencies:
- Public contracts affected:

### Known unknowns

What is intentionally unknown?

### Conflicts

List normative source conflicts.

If non-empty, context is not ready.

### Decision gaps

List material rules that implementation would otherwise have to invent.

If non-empty, move to a decision artifact/human gate.

### Scope boundary

In scope:

- ...

Out of scope:

- ...

### Verification

Focused check:

- ...

Canonical check:

```text
uv run --locked python scripts/harness.py verify
```
