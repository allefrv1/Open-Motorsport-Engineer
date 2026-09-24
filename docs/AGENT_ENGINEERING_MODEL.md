# OME Layered Agent Engineering Model

Status: **Accepted operating model**

Date: 2026-09-24

## Purpose

OME is built primarily with coding agents.

A reliable agent workflow therefore needs more than a good prompt.

OME uses five engineering layers:

```text
PROMPT ENGINEERING
-> CONTEXT ENGINEERING
-> HARNESS ENGINEERING
-> LOOP ENGINEERING
-> GRAPH ENGINEERING
```

The names describe responsibilities, not independent systems.

The layers compose one execution model.

## Core rule

> Fix the failure at the highest layer where it originates.

Do not compensate for an upstream deficiency in a downstream layer.

Examples:

- ambiguous product intent is not fixed by writing more code;
- missing context is not fixed by weakening a test;
- a missing architecture decision is not buried in implementation;
- a broken harness is not fixed by disabling verification;
- a failed implementation is not fixed by changing accepted requirements silently.

## Layer 1 — Prompt Engineering

Question:

> What exactly is the agent being asked to do?

The prompt compiles a task into a concise execution request.

A good OME task prompt contains:

- objective;
- required outcome;
- acceptance criteria or requirement reference;
- constraints;
- explicit out-of-scope items;
- verification requirement;
- stop/escalation conditions.

### Prompt responsibility

The prompt should answer:

```text
WHY THIS TASK?
WHAT MUST CHANGE?
WHAT MUST NOT CHANGE?
HOW WILL SUCCESS BE PROVEN?
WHEN MUST THE AGENT STOP?
```

### Prompt limitations

Prompt Engineering cannot:

- replace requirements;
- override accepted ADRs/specs;
- supply missing domain evidence;
- resolve contradictory repository sources;
- prove correctness;
- create authority merely by wording something strongly.

A longer prompt is not automatically a better prompt.

Prefer a short task contract that points to durable repository truth.

## Layer 2 — Context Engineering

Question:

> What does the agent need to know to execute the task correctly?

Context Engineering selects the smallest trustworthy information set needed for the task.

Typical context packet:

1. relevant requirement;
2. active plan;
3. accepted ADR/spec;
4. domain semantics;
5. affected implementation files;
6. affected tests;
7. fixtures/evidence;
8. external evidence only when necessary.

### Context selection rules

Load context by priority:

```text
accepted requirement
-> accepted ADR/spec/domain
-> active plan
-> executable tests/checks
-> implementation
-> research/external evidence
```

Use progressive disclosure.

Do not load the entire repository "just in case".

### Context readiness

Before behavior work begins, the agent should be able to state:

- source of truth;
- current behavior;
- desired behavior;
- known constraints;
- unresolved decisions;
- evidence gaps.

If two normative sources conflict, context is **not ready**.

The agent must surface the conflict.

### Context limitations

Context Engineering cannot:

- decide unresolved product trade-offs;
- convert research into accepted behavior automatically;
- make stale evidence current;
- turn missing telemetry into known telemetry;
- guarantee correctness merely because many files were read.

## Layer 3 — Harness Engineering

Question:

> How does the repository mechanically verify the agent?

Harness Engineering converts important rules into executable feedback.

OME harness responsibilities include:

- formatting;
- linting;
- static/type checking;
- unit/integration/runtime tests;
- documentation consistency;
- architecture boundaries;
- fixture/provenance checks;
- canonical full verification.

Canonical command:

```text
uv run --locked python scripts/harness.py verify
```

### Harness design rule

When the same agent mistake appears repeatedly:

```text
review feedback
-> durable rule
-> executable check when practical
```

### Harness limitations

Harness Engineering can only enforce rules that are encoded.

A green harness does **not** prove:

- the product requirement is correct;
- the engineering interpretation is physically correct;
- the selected architecture is optimal;
- missing context does not exist;
- a human trade-off was decided correctly.

The harness is a verifier, not a substitute for judgment.

## Layer 4 — Loop Engineering

Question:

> How does the agent react to feedback until the task converges?

OME uses a test-first execution loop for deterministic behavior:

```text
UNDERSTAND
-> WRITE TEST
-> RED
-> IMPLEMENT MINIMUM
-> GREEN
-> REFACTOR
-> VERIFY
-> REVIEW
```

The important addition is **failure classification**.

### Failure classes

#### PROMPT_GAP

Symptoms:

- goal is ambiguous;
- output shape is unclear;
- out-of-scope boundary is missing.

Action:

Return to Prompt Engineering.

#### CONTEXT_GAP

Symptoms:

- missing requirement/spec;
- contradictory docs;
- unknown source semantics;
- fixture/evidence missing.

Action:

Return to Context Engineering.

#### DECISION_GAP

Symptoms:

- implementation requires a material rule not accepted anywhere;
- irreversible architecture choice is needed;
- product scope changes.

Action:

Move to Graph Engineering / human decision gate.

#### HARNESS_FAILURE

Symptoms:

- CI/tooling/environment is broken independent of product behavior;
- test cannot execute for infrastructure reasons.

Action:

Fix harness/tooling before judging product behavior.

#### BEHAVIOR_FAILURE

Symptoms:

- focused test reaches the intended behavior and fails.

Action:

Implement the smallest correct production change.

#### REGRESSION_FAILURE

Symptoms:

- new behavior passes locally but breaks existing accepted behavior.

Action:

Resolve implementation conflict; do not weaken old accepted behavior silently.

#### EVIDENCE_FAILURE

Symptoms:

- real data contradicts synthetic assumptions;
- domain evidence does not support the intended rule.

Action:

Stop implementation and move back to Context/Decision layers.

### Loop stop conditions

The agent should stop looping and escalate when:

- the same failure class repeats without new evidence;
- fixing the failure would require changing accepted requirements/ADRs;
- a test would need to be weakened to make production code pass;
- a hidden assumption becomes material;
- new external evidence contradicts the accepted contract;
- the task moves outside its declared scope.

### Loop limitations

Loop Engineering cannot guarantee convergence to the right target if the target itself is wrong.

TDD protects behavior against a contract.

It does not prove that the contract is correct.

## Layer 5 — Graph Engineering

Question:

> Given the current state, which path should the agent take next?

Graph Engineering represents execution as explicit states and gates.

It prevents an agent from jumping directly from "task received" to "write code".

## OME engineering task graph

```text
TASK
 |
 v
PROMPT READY?
 | no -> clarify/rewrite task contract
 yes
 |
 v
CONTEXT READY?
 | no -> retrieve/resolve context
 yes
 |
 v
MATERIAL DECISION MISSING?
 | yes -> decision artifact / human gate
 no
 |
 v
BEHAVIOR CHANGE?
 | no -> closest appropriate verification loop
 yes
 |
 v
TESTABLE CONTRACT?
 | no -> requirement/spec/evidence work
 yes
 |
 v
WRITE TEST
 |
 v
EXPECTED RED?
 | no -> classify failure and route upstream
 yes
 |
 v
IMPLEMENT MINIMUM
 |
 v
FOCUSED GREEN?
 | no -> classify failure
 yes
 |
 v
REFACTOR
 |
 v
FULL VERIFY GREEN?
 | no -> classify regression/harness failure
 yes
 |
 v
CONTRACT CHANGED?
 | yes -> update durable docs/ADR/spec
 no
 |
 v
SELF-REVIEW
 |
 v
MERGE READY
```

## Human decision gates

Agents may execute local reversible choices inside accepted constraints.

Human/maintainer approval is required when the graph reaches:

- product scope change;
- new irreversible architecture direction;
- weaker provenance/evidence guarantees;
- licensing decision;
- public contract break;
- unsupported motorsport engineering claim;
- acceptance/rejection of an ADR.

## Layer interaction

The intended dependency is:

```text
Prompt
  defines the task
      |
      v
Context
  supplies trustworthy knowledge
      |
      v
Harness
  supplies mechanical checks
      |
      v
Loop
  reacts to feedback
      |
      v
Graph
  routes decisions and escalation
```

Graph Engineering is not "more powerful prompting".

It controls state transitions.

## Failure escalation rule

A lower layer must never hide an upper-layer problem.

```text
code cannot repair bad requirement
test cannot repair missing context
CI cannot decide product intent
prompt cannot override evidence
agent cannot accept its own irreversible architecture decision
```

## Task packet

For substantial work, the agent should be able to compile this compact packet before implementation:

```text
OBJECTIVE
SOURCE OF TRUTH
ACCEPTANCE
CONSTRAINTS
OUT OF SCOPE
CONTEXT FILES
TEST / RED PLAN
VERIFY
STOP / ESCALATE IF
```

Use:

`docs/prompts/codex-task-template.md`

## Relationship to existing OME practice

This model does not replace:

- AGENTS.md;
- execution plans;
- TDD;
- CI;
- ADRs;
- requirements;
- specs.

It organizes them.

## Success condition

The model is working when an agent can answer not only:

> What code should I write?

but also:

> Why am I allowed to write it, which evidence supports it, what proves it, and when must I stop?
