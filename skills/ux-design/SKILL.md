---
name: ux-design
description: Professional UX/UI product-design workflow for creating, reviewing, or implementing interfaces and interaction flows. Use when work involves application screens, dashboards, navigation, information architecture, user flows, wireframes, component behavior, design systems, accessibility, responsive behavior, usability review, visual hierarchy, interaction states, or frontend UX decisions. Especially useful for technical/data-heavy products where evidence, units, uncertainty, errors, loading/empty states, provenance, and progressive disclosure must remain clear. Do not trigger for backend-only or non-interface engineering work.
---

# UX Design

## Core rule

Design the user experience before polishing the visuals.

Use this sequence:

```text
USER GOAL
-> TASK / DECISION
-> INFORMATION REQUIRED
-> USER FLOW
-> SCREEN / INFORMATION ARCHITECTURE
-> STATES + INTERACTIONS
-> ACCESSIBILITY
-> VISUAL HIERARCHY
-> IMPLEMENTATION
-> USABILITY / VISUAL QA
```

Do not start from decorative components or trendy styling when the user's task is not yet clear.

## Workflow

### 1. Understand the job to be done

Identify:

- who is using the interface;
- what decision or task they need to complete;
- what information is required at each step;
- what can go wrong or be missing;
- what is beginner-facing versus expert-facing.

When requirements are incomplete, prefer the smallest reversible UX assumption and make it explicit.

### 2. Establish information architecture

Before implementation, define:

- primary navigation;
- page/screen hierarchy;
- major content regions;
- primary action and secondary actions;
- what is persistent versus contextual;
- how the user returns to context after drilling down.

For data-heavy products, organize around the user's investigation flow rather than around database entities.

### 3. Define interaction states

Every interactive feature must consider relevant states:

- default;
- hover/focus when applicable;
- selected/active;
- disabled;
- loading;
- empty;
- partial/incomplete data;
- validation warning;
- blocking error;
- success/confirmation;
- permission or unsupported-state when relevant.

Never hide missing or invalid data behind a visually plausible placeholder.

### 4. Apply progressive disclosure

Default to the minimum information required for the current decision.

Expose deeper detail without removing traceability:

```text
Summary
-> relevant metrics
-> comparison / evidence
-> raw or derived detail
-> provenance / method
```

Do not create separate contradictory experiences for beginner and expert users. Prefer one evidence model with progressively deeper views.

### 5. Design for technical/data-heavy interfaces

For engineering, telemetry, analytics, finance, observability, or scientific interfaces:

- keep units adjacent to values;
- distinguish measured, derived, estimated, missing, and invalid data;
- expose source/provenance when it affects trust;
- make reference cases explicit in comparisons;
- use consistent sign conventions and legends;
- avoid encoding critical meaning by color alone;
- provide exact values in addition to visual trends when precision matters;
- preserve context while users zoom, filter, compare, or inspect details;
- use dense layouts intentionally, not accidentally.

### 6. Accessibility baseline

Target WCAG 2.2 AA unless the product has a stricter requirement.

At minimum verify:

- keyboard operability;
- visible focus;
- semantic labels and landmarks;
- form labels and validation messages;
- non-color-only status communication;
- sufficient text/non-text contrast;
- understandable error recovery;
- sensible heading order;
- responsive zoom/reflow behavior;
- reduced-motion behavior for non-essential animation.

Load `references/ux-review-checklist.md` for a review pass.

### 7. Visual hierarchy and component discipline

Prefer an existing design system when one exists.

Before creating a new component, check whether an existing component can express the behavior without semantic compromise.

Use typography, spacing, grouping, alignment, and contrast to communicate importance before adding decoration.

Avoid:

- excessive cards for every piece of content;
- modal dialogs for routine navigation;
- hidden primary actions;
- icon-only controls without accessible names;
- charts without units/reference/legend when needed;
- fake precision;
- dense tables without sorting/filter/context strategy;
- dashboard layouts that optimize appearance over user decisions.

### 8. Responsive behavior

Define what happens as width decreases.

Do not merely stack everything vertically. Decide:

- what remains visible;
- what becomes scrollable;
- what collapses;
- what moves to a details view;
- what comparison interactions need desktop width;
- what remains usable on touch devices.

### 9. Implementation handoff

When implementation is requested, provide or verify:

- component responsibilities;
- interaction/state behavior;
- semantic HTML/accessibility expectations;
- responsive rules;
- data contract assumptions;
- loading/error/empty behavior;
- testable acceptance criteria.

Do not silently invent backend behavior to simplify the UI.

### 10. UX review before completion

Review the implemented interface against:

1. task success;
2. information hierarchy;
3. consistency;
4. error prevention/recovery;
5. accessibility;
6. responsive behavior;
7. data trust/provenance;
8. cognitive load;
9. interaction feedback;
10. visual polish.

Separate blocking usability/accessibility defects from optional polish.

## OME-specific interface rules

When working on Open Motorsport Engineer interfaces, also load `references/ome-interface-principles.md`.

OME UI must preserve the engineering evidence model:

```text
Measured Data
-> Derived Data / Metric
-> Observation
-> Hypothesis
-> Engineering Interpretation
-> Possible Action
```

Do not visually blur these levels.

Always keep missing evidence explicit. AI explanations must never look like measured telemetry.

For lap comparison, reference lap, delta sign, distance basis, units, algorithm/version when relevant, and Session / Run / Lap context must remain discoverable.

## Deliverables

Choose the smallest useful deliverable for the task:

- UX critique with prioritized issues;
- user flow;
- information architecture;
- screen specification;
- wireframe description;
- component/state contract;
- accessibility review;
- implementation acceptance criteria;
- final frontend implementation plus UX QA.

When giving recommendations, separate:

- **must fix** — blocks task completion, trust, accessibility, or correctness;
- **should improve** — meaningful usability improvement;
- **polish** — visual refinement without changing task success.
