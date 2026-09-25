# Motorsport Engineering Reference Library

Status: **Curated reference index**

Date: 2026-09-25

## Purpose

Define the reference set the Motorsport Mechanical Engineering Agent should consult when OME needs domain rules, equations, interpretation guidance or engineering recommendations.

This is a bibliographic/research index.

It is not a repository of copyrighted book contents.

## Source hierarchy

Prefer the most direct authoritative source for the question:

1. source-system/sensor manufacturer documentation;
2. applicable standards / primary technical source;
3. specialist motorsport/vehicle-dynamics books;
4. peer-reviewed/academic references;
5. reputable engineering training material;
6. practitioner material, clearly labeled as such.

Books do not override explicit source-system semantics.

## Core library

### Racecar data acquisition

#### Jorge Segers — Analysis Techniques for Racecar Data Acquisition, Second Edition

Publisher: SAE International

Use for:

- data-analysis workflow;
- data overlays;
- filtering;
- lap/segment comparison;
- braking analysis;
- gearing;
- cornering;
- roll/pitch/load-transfer analysis;
- tyre-performance analysis;
- metric-driven analysis.

Priority: **Core**

#### Christopher Brown — Making Sense of Squiggly Lines

Use for:

- foundational race-data analysis;
- speed;
- RPM;
- throttle;
- braking;
- lateral/longitudinal acceleration;
- steering;
- practical beginner-to-intermediate analysis workflow.

Priority: **Core practical reference**

### Race-car vehicle dynamics

#### William F. Milliken & Douglas L. Milliken — Race Car Vehicle Dynamics

Publisher: SAE International

Use for:

- race-car vehicle dynamics;
- tyre behavior;
- steady-state and transient stability/control;
- wheel loads;
- steering;
- suspension;
- dampers;
- force/moment analysis;
- g-g analysis.

Priority: **Core**

#### Thomas D. Gillespie — Fundamentals of Vehicle Dynamics, Revised Edition

Publisher: SAE International

Use for:

- foundational equations;
- longitudinal/lateral dynamics;
- braking/traction;
- ride/handling fundamentals;
- sanity-checking broader vehicle-dynamics reasoning.

Priority: **Core fundamentals**

### Tyres

#### Hans Pacejka — Tire and Vehicle Dynamics, Third Edition

Publisher: Elsevier

Use for:

- tyre input variables;
- slip;
- tyre force/moment behavior;
- combined slip;
- tyre modeling;
- Magic Formula assumptions/limitations;
- vehicle/tire interaction.

Priority: **Core advanced tyre reference**

#### Paul Haney — The Racing & High-Performance Tire, Revised Edition

Publisher: SAE International

Use for:

- race-tyre behavior;
- grip/balance;
- tyre construction and friction;
- practical tyre testing/performance;
- tyre-related setup implications.

Priority: **Core practical tyre reference**

## Secondary / expansion library

Candidates should be added only with bibliographic verification and a clear use case.

Useful future categories:

- suspension kinematics/compliance;
- dampers;
- braking systems;
- aerodynamics;
- powertrain;
- race-car design;
- lap-time simulation;
- race strategy;
- Formula Student/SAE design and data workflows.

## Reference selection matrix

| Engineering question | First reference family |
|---|---|
| What does this logged channel mean? | Source-system documentation |
| How should race telemetry be analyzed? | Segers / Brown |
| Is this vehicle-dynamics relationship sound? | Milliken / Gillespie |
| Is this tyre claim/model sound? | Pacejka / Haney |
| What setup action should be considered? | Evidence first, then relevant vehicle/tyre reference |
| Is this equation dimensionally/physically valid? | Physics Reviewer + primary dynamics reference |

## Rule for recommendations

A recommendation must never be sourced from a book alone when the car-specific evidence is missing.

Books provide:

- mechanisms;
- equations;
- expected relationships;
- diagnostic methods;
- possible actions.

Telemetry/setup/context provides whether that mechanism applies to the current case.

Use:

```text
REFERENCE KNOWLEDGE
+ CURRENT CAR / RUN EVIDENCE
= POSSIBLE ENGINEERING INTERPRETATION
```

Not:

```text
REFERENCE KNOWLEDGE
= AUTOMATIC SETUP RECOMMENDATION
```

## Research gap protocol

When the required reference is unavailable:

1. identify the question;
2. identify the likely reference/title/topic;
3. state what is already known;
4. state what cannot be verified;
5. create a research action;
6. keep the claim narrow or blocked.

## Repository note format

Future distilled book-backed knowledge should live in domain/research notes with:

- question;
- mechanism;
- equation/rule;
- assumptions;
- application limits;
- source citation;
- OME implication.

Do not copy long copyrighted passages.
