# Engineering Task Decision Graph

Status: **Accepted**

## Purpose

Make task routing explicit for humans and coding agents.

This graph complements `docs/AGENT_ENGINEERING_MODEL.md`.

## State graph

```mermaid
flowchart TD
    A[Task received] --> B{Prompt ready?}
    B -- No --> B1[Rewrite task contract]
    B1 --> B
    B -- Yes --> C{Context ready?}
    C -- No --> C1[Retrieve or resolve context]
    C1 --> C
    C -- Yes --> D{Material decision missing?}
    D -- Yes --> D1[Decision artifact / human gate]
    D1 --> C
    D -- No --> E{Behavior change?}
    E -- No --> E1[Use appropriate verification loop]
    E1 --> K
    E -- Yes --> F{Testable contract?}
    F -- No --> F1[Requirement/spec/evidence work]
    F1 --> C
    F -- Yes --> G[Write focused test]
    G --> H{Expected RED?}
    H -- No --> H1[Classify failure]
    H1 --> B
    H -- Yes --> I[Implement minimum]
    I --> J{Focused GREEN?}
    J -- No --> J1[Classify failure]
    J1 --> C
    J -- Yes --> K[Refactor / self-review]
    K --> L{Full verify GREEN?}
    L -- No --> L1[Classify harness/regression failure]
    L1 --> C
    L -- Yes --> M{Contract changed?}
    M -- Yes --> M1[Update durable docs]
    M1 --> N[Final self-review]
    M -- No --> N
    N --> O[Merge ready]
```

## Routing rule

A failure does not automatically route back to implementation.

Examples:

- import error because a module is absent after a test-first commit -> BEHAVIOR_FAILURE -> implementation;
- test fails because fixture semantics are unknown -> CONTEXT_GAP;
- test fails because accepted docs disagree -> CONTEXT_GAP / DECISION_GAP;
- CI cannot install dependencies -> HARNESS_FAILURE;
- real telemetry disproves a synthetic assumption -> EVIDENCE_FAILURE;
- implementation needs a new irreversible architecture choice -> DECISION_GAP.

## Graph limitation

The graph controls routing.

It does not make the underlying human trade-off.

A human gate is intentionally visible where authority is required.
