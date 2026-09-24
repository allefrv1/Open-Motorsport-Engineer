# Codex Task Prompt Template

Status: **Accepted template**

Use this template for substantial OME coding-agent tasks.

Do not paste the whole repository into the prompt.

Point the agent to durable sources of truth.

---

## ROLE

You are implementing a focused change in Open Motorsport Engineer (OME).

Follow repository instructions in `AGENTS.md` and the layered model in `docs/AGENT_ENGINEERING_MODEL.md`.

## OBJECTIVE

<One concrete outcome.>

## SOURCE OF TRUTH

Read, in this order:

1. <requirement>
2. <accepted ADR/spec>
3. <active plan>
4. <domain document>
5. <affected tests/code>
6. <fixture/research only when needed>

If normative sources conflict, stop and report the conflict.

## ACCEPTANCE

The task is complete only when:

- <observable behavior 1>
- <observable behavior 2>
- <observable behavior 3>

For new deterministic behavior, acceptance must be executable through tests.

## CONSTRAINTS

- preserve accepted architecture boundaries;
- preserve source/provenance evidence;
- do not add undocumented behavior;
- do not broaden scope silently;
- make the smallest correct change.

Add task-specific constraints:

- <constraint>
- <constraint>

## OUT OF SCOPE

Do not implement:

- <explicit future behavior>
- <unrelated refactor>
- <speculative abstraction>

## CONTEXT PACKET

Before editing production code, identify:

- requirement:
- ADR/spec:
- active plan:
- relevant domain semantics:
- affected modules:
- affected tests:
- fixtures/evidence:
- unresolved decisions:

Do not continue to production behavior while a material unresolved decision remains.

## TDD / LOOP

For new deterministic behavior:

1. write the focused test;
2. run it;
3. confirm RED for the intended missing behavior;
4. implement the minimum production change;
5. confirm focused GREEN;
6. refactor without behavior change;
7. run full verify.

Do not count formatting/tooling failures as behavioral RED.

Do not weaken an accepted test merely to obtain GREEN.

## FAILURE ROUTING

Classify a failure before fixing it:

- PROMPT_GAP
- CONTEXT_GAP
- DECISION_GAP
- HARNESS_FAILURE
- BEHAVIOR_FAILURE
- REGRESSION_FAILURE
- EVIDENCE_FAILURE

Fix the failure at the highest layer where it originates.

## VERIFY

Focused:

<focused command or test>

Full:

```text
uv run --locked python scripts/harness.py verify
```

## STOP / ESCALATE IF

Stop and surface the issue when:

- accepted sources conflict;
- a new material architecture/product decision is required;
- evidence contradicts the contract;
- source semantics are unknown;
- completing the task would weaken provenance or safety guarantees;
- the same failure repeats without new information.

## COMPLETION REPORT

Report:

- behavior changed;
- requirement/spec used;
- RED evidence;
- GREEN evidence;
- full verify result;
- assumptions;
- limitations;
- unresolved follow-up.
