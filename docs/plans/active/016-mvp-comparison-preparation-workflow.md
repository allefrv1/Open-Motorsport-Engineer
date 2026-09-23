# Plan 016 — MVP Comparison Preparation Workflow Foundation

Status: **Active**

Started: 2026-09-23

## Objective

Build the missing application-level preparation/orchestration path between source-preserving telemetry and the already accepted comparison-report service.

The goal is to make the first vertical slice capable of producing a comparison report from trustworthy prepared telemetry without requiring a caller or future frontend to manually construct low-level canonical evidence objects.

## Why this plan exists

OME already has independently verified capabilities for:

- import;
- validation;
- normalization;
- Session / Run / Lap context;
- deterministic lap comparison;
- supporting overlays;
- observations;
- integrated report composition;
- HTTP transport.

But those capabilities are not yet connected into one user-oriented application use case.

The current HTTP report endpoint assumes the caller already possesses canonical lap-distance/time/channel evidence.

A real UI must not invent or manually assemble that engineering evidence.

## Requirements

Primary:

- MVP — first vertical slice;
- REQ-001 — Import Telemetry Session;
- REQ-002 — Validate Telemetry Dataset;
- REQ-003 — Organize Session / Run / Lap;
- REQ-004 — Normalize Telemetry Channels;
- REQ-005 — Compare Two Laps;
- REQ-006 — Preserve Analysis Evidence.

Architecture:

- ADR-0001 — separate ingestion from normalization;
- ADR-0004 — local modular monolith;
- ADR-0009 — distance-aligned lap comparison;
- existing accepted source/domain/comparison specifications.

## Initial deliverable

Define the smallest deterministic **prepared-lap / comparison-preparation application contract** that can:

1. start from imported/validated source evidence;
2. consume explicit accepted normalization mappings;
3. identify trustworthy single-lap context without generic lap detection;
4. produce canonical `lap.distance` and `time.elapsed` evidence;
5. prepare available speed/throttle/brake/steering/RPM/gear evidence;
6. create a valid `ComparisonReportRequest`;
7. preserve all source/validation/normalization/context provenance;
8. return explicit not-ready/missing evidence when preparation is impossible.

## First controlled integration path

Plan 016 should introduce project-owned deterministic comparison fixtures designed specifically for end-to-end preparation.

The fixture strategy must not pretend the current `basic-lap.csv` is sufficient: that file has no `lap.distance` channel.

The initial fixture may use two explicit single-lap OME CSV sources so the first orchestration slice does not require generic lap segmentation.

Each controlled lap fixture should provide:

- explicit time basis;
- explicit lap distance in metres;
- speed;
- throttle;
- brake with explicit semantic identity;
- steering;
- RPM;
- gear;
- explicit Session / Run / Lap context/provenance.

## Normalization contract

Do not hide source-to-canonical mapping choices inside orchestration code.

Plan 016 must decide/document how the application obtains explicit versioned normalization rules for the controlled integration path.

Candidate approaches include:

- an accepted project-owned rule profile/registry for the controlled OME comparison fixture;
- another explicit injected rule-set contract.

Do not introduce fuzzy channel-name matching.

## Time evidence

OME CSV currently stores `time_s` as the shared source timestamp axis rather than a regular `SourceChannel`.

Plan 016 must explicitly define how that source time basis becomes canonical `time.elapsed` evidence.

It must remain traceable to the source dataset/import contract and must not be represented as if it came from an unrelated telemetry channel.

## Context boundary

The first integration path may use explicit trustworthy context supplied by the project-owned fixtures.

Do not add generic:

- lap detection;
- GPS start/finish detection;
- pit inference.

Those remain separate future capabilities.

## TDD rule

```text
WORKFLOW SPEC
-> END-TO-END APPLICATION TEST
-> VALID RED
-> SMALLEST PREPARATION/ORCHESTRATION IMPLEMENTATION
-> GREEN
-> REFACTOR
-> FULL VERIFY
```

The test must prove the complete evidence chain, not only the final delta numbers.

## First executable test targets

Tests should prove:

- two controlled source laps can be imported and validated;
- blocking validation prevents comparison preparation;
- normalization mappings are explicit/versioned;
- canonical lap-distance/time evidence is traceable;
- the prepared report request retains Session / Run / Lap context;
- missing lap distance produces not-ready rather than synthetic distance;
- missing optional channels remain explicit;
- brake semantic identity survives preparation;
- the resulting request can be passed directly to `ComparisonReportService`;
- the resulting report answers the known synthetic gain/loss case deterministically;
- original imported datasets remain unchanged.

## API/UI relationship

Do not add frontend behavior yet.

Once Plan 016 produces a user-oriented application workflow, the next API increment can expose that workflow at a simpler boundary such as:

```text
source/project/lap selection
-> application preparation
-> comparison report
```

Only then should the MVP frontend implement the real investigation flow.

## Docker/Compose relationship

Plan 016 does not require Docker.

Current containerization conclusion remains:

- backend Dockerfile is justified if ADR-0010 is accepted;
- Docker Compose remains deferred until a real frontend or another required process exists.

## Completion criteria

- workflow/preparation contract documented;
- controlled two-lap fixture strategy documented;
- explicit normalization/time-evidence rules documented;
- tests committed before production workflow behavior;
- behavioral RED recorded;
- deterministic preparation/orchestration GREEN;
- complete source-to-report evidence chain executable;
- no generic lap-detection inference introduced;
- canonical verify GREEN.

## Explicitly out of scope

- browser UI;
- generic file-upload workflow;
- persistence/project library;
- generic lap detection;
- GPS track projection;
- Docker Compose;
- public deployment;
- AI.
