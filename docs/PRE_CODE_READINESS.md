# OME Pre-Code Readiness Review

Date: 2026-09-22

Status: **Documentation foundation complete — executable harness not ready**

## Executive conclusion

OME has a strong product, domain and architecture knowledge base.

A harness-engineering audit found that the earlier label **implementation-ready** was too strong.

The repository does not yet provide the executable feedback loops required for reliable agent-led feature development.

## What is ready

### Product

- mission and problem;
- users and non-goals;
- first vertical slice;
- long-term scope boundaries.

### Domain

- Event / Session / Run / Lap vocabulary;
- telemetry import model;
- provenance;
- validation concepts;
- normalization boundary;
- evidence hierarchy;
- missing/unknown-data semantics.

### Requirements

- REQ-001 through REQ-006 are defined and accepted as the initial baseline.

### Architecture

- major responsibility boundaries exist;
- local modular-monolith direction exists;
- deterministic engineering-core boundary exists;
- AI boundary exists;
- data/storage/UI technology baseline exists;
- first lap-comparison alignment approach exists.

### Process documentation

- test strategy exists;
- ADR process exists;
- active/completed execution-plan lifecycle exists;
- harness operating model exists;
- quality score and technical-debt tracker exist.

## What is not ready

### Executable feedback

Missing:

- reproducible toolchain setup;
- dependency lockfiles;
- canonical repository commands;
- formatter/linter/type checks;
- test runner configuration;
- CI;
- documentation structure/link checks;
- architecture dependency checks.

### Data feedback

Missing:

- committed OME CSV fixtures;
- representative iRacing fixture;
- representative MoTeC CSV fixture;
- fixture manifest/licensing metadata.

### Agent feedback loop

The repository tells an agent what good behavior looks like, but cannot yet mechanically prove that behavior.

## Correct Go / No-Go

### Go

Proceed to **Plan 002 — Agent Harness Bootstrap** when coding/configuration work is authorized.

### No-Go

Do not begin REQ-001 feature implementation before harness bootstrap exit criteria are met, unless the maintainer explicitly overrides the gate.

## Harness bootstrap exit gates

Before feature work:

- fresh-checkout environment setup is reproducible;
- canonical verification commands exist;
- PR CI runs those checks;
- basic documentation checks exist;
- initial architecture boundary checks exist;
- at least initial fixtures exist;
- `docs/QUALITY_SCORE.md` exit thresholds are met.

## Why this correction matters

Harness engineering treats repository context, tools and feedback loops as part of the product-development system.

Good Markdown alone is not a reliable harness.

The next phase must turn important repository rules into executable feedback.
