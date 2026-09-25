# OME Kanban Operating Policy

Status: **Accepted operating model**

Date: 2026-09-25

## Workflow

```text
BACKLOG -> READY -> DOING -> REVIEW -> DONE
```

`BLOCKED` is a visible condition, not a hidden queue.

## WIP limits

Initial policy:

- Product DOING: max 1
- REVIEW: max 2
- EXPEDITE: max 1

Finish before starting more product behavior.

## Pull policy

Pull READY -> DOING only when:

- objective is explicit;
- requirement/spec/ADR context is sufficient;
- required specialist/council review is complete;
- acceptance/test strategy exists;
- no unresolved material decision gap remains.

## Done policy

DONE means:

- merged to main;
- canonical verify green;
- plan/status synchronized;
- important discoveries promoted to durable knowledge;
- unresolved debt recorded.

## Feedback loops

### Replenishment

Before committing new material product work.

### Flow review

At meaningful work-session boundaries or when blocked.

Review:

- WIP;
- blockers;
- aging;
- next unblock action.

### Engineering Council alignment

For cross-domain decisions and improvements.

### Delivery review

Before material REVIEW -> DONE.

### Improvement review

At plan completion or after repeated failures.

Classify rework:

- prompt;
- context;
- decision;
- harness;
- behavior;
- regression;
- evidence.

### Strategy review

At roadmap phase transitions or CEO-level product decisions.

## Improvement rule

```text
OBSERVE
-> HYPOTHESIS
-> SMALL PROCESS CHANGE
-> MEASURE
-> KEEP / REVERT / ADJUST
```

Do not add ceremonies just to imitate another organization.

## Board

Current flow is summarized in:

`docs/kanban/BOARD.md`
