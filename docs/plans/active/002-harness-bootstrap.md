# Plan 002 — Agent Harness Bootstrap

Status: **Active**

Started: 2026-09-22

## Objective

Create the executable engineering environment that lets Codex implement OME reliably.

This plan intentionally precedes feature implementation.

## Why this is required

OME already has strong product/domain/architecture documentation, but documentation alone cannot prevent agent drift.

The repository currently lacks:

- reproducible runtime/toolchain bootstrap;
- canonical verification commands;
- CI;
- formatting/lint/type checks;
- executable architecture-boundary checks;
- documentation freshness/structure checks;
- requirement-to-test traceability.

Initial public fixtures now exist, but the fixture harness is only partially complete.

## Scope

When coding is explicitly authorized, bootstrap only the harness and minimal project scaffold needed to verify future work.

Do **not** implement REQ-001 feature behavior during this plan except for minimal seams required to prove the harness.

## Milestone 1 — Reproducible environment

Define and lock:

- Python version/toolchain;
- Python dependency/project manager;
- Node runtime;
- frontend package manager;
- dependency lockfiles;
- local setup command.

Acceptance:

- a fresh checkout can be prepared with documented deterministic commands;
- versions are discoverable from repository files.

## Milestone 2 — Canonical commands

Provide one clear repository entry point for:

- format;
- lint;
- type/static check;
- unit tests;
- integration tests;
- docs checks;
- architecture checks;
- full verification.

The exact task runner may be selected during bootstrap.

Acceptance:

- `AGENTS.md` can point to real commands instead of general expectations.

## Milestone 3 — CI feedback loop

CI must run the canonical checks on pull requests.

Acceptance:

- a known failing test/check blocks the PR;
- local and CI commands use the same underlying tooling.

## Milestone 4 — Documentation harness

Create mechanical checks for at least:

- broken internal Markdown links;
- duplicate requirement/ADR IDs where applicable;
- invalid status vocabulary;
- missing index entries for ADRs/requirements;
- stale active/completed plan placement where mechanically detectable.

Acceptance:

- deliberate documentation defects are caught automatically.

## Milestone 5 — Architecture harness

Encode high-value dependency boundaries once modules exist.

Initial rules should prevent at least:

- domain importing API/framework modules;
- analysis depending on generative AI;
- source adapters becoming canonical domain entities;
- cross-layer dependency cycles.

Acceptance:

- at least one deliberate forbidden dependency is rejected by an automated check.

## Milestone 6 — Fixture harness

Status: **Partially complete**

Completed during public-data validation:

- machine-readable public fixture manifest;
- provenance/license notices;
- Apache-2.0 Traqmate CSV real-vehicle fixture;
- MIT MoTeC-style canonical fixture;
- MIT decreasing-time negative fixture;
- external iRacing `.ibt` validation source identified;
- external Formula SAE competition/test logs identified.

Still required:

- project-owned OME CSV fixture;
- fixture-schema validation in the harness;
- documented process for private/large fixtures;
- clearly redistributable full iRacing session if legally appropriate;
- clearly licensed real physical-car MoTeC export;
- Brazilian Formula SAE full-session fixture with permission.

Acceptance:

- future importer contract tests have stable inputs;
- fixture provenance/licensing is mechanically checkable.

## Milestone 7 — PR/self-review loop

Update contribution guidance so Codex must:

1. run focused checks during work;
2. run full verification before completion where practical;
3. review the diff;
4. confirm requirement/ADR alignment;
5. report test results and known limitations.

## Exit criteria

This plan completes only when:

- environment setup is reproducible;
- canonical verification commands exist;
- CI executes them;
- at least basic docs and architecture checks are automated;
- initial fixtures exist;
- `docs/QUALITY_SCORE.md` reaches the Harness Bootstrap exit thresholds.

## Decision log

2026-09-22 — Harness-engineering audit determined that previous "implementation-ready" wording was too strong. Documentation readiness is not equivalent to executable agent readiness.


2026-09-22 — Public telemetry survey validated the core source/import/validation boundaries against iRacing, Formula SAE, Traqmate and MoTeC-style data. Initial legally redistributable CSV fixtures were committed.
