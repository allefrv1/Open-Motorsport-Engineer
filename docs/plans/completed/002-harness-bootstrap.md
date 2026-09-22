# Plan 002 — Agent Harness Bootstrap

Status: **Completed**

Started: 2026-09-22

Completed: 2026-09-22

## Objective

Create the executable engineering environment that lets Codex implement OME reliably.

## Result

The bootstrap established a real agent feedback loop before feature development.

## Completed milestones

### 1. Reproducible environment

Pinned and exposed:

- Python 3.13.15;
- uv 0.12.17;
- Node.js 24.21.0 LTS;
- pnpm 11.27.1;
- Python and JavaScript lockfiles;
- documented fresh-checkout setup.

### 2. Canonical commands

The repository now has a single harness entry point:

```text
uv run --locked python scripts/harness.py <command>
```

Supported commands include:

- format;
- lint;
- type;
- test;
- docs;
- arch;
- fixtures;
- verify.

### 3. CI feedback loop

GitHub Actions runs the same canonical `verify` command used locally.

The workflow uses read-only repository permissions and immutable action commit SHAs.

### 4. Documentation harness

Mechanical checks cover:

- broken local Markdown links;
- requirement IDs/status/index membership;
- ADR IDs/status/index membership;
- active/completed plan placement.

### 5. Architecture harness

Initial structural checks enforce selected dependency boundaries and detect cross-layer cycles.

A deliberate forbidden dependency test proves that the architecture harness rejects violations.

### 6. Fixture harness

Added:

- project-owned OME CSV Profile fixture;
- public fixture manifest validation;
- license/provenance-path validation;
- public Traqmate and MoTeC-style fixtures;
- negative decreasing-time fixture.

External iRacing, physical-car MoTeC and Brazilian Formula SAE coverage remains an evidence/coverage gap, not a blocker for the first implementation slice.

### 7. PR/self-review loop

`AGENTS.md`, `CONTRIBUTING.md` and the pull-request template now require canonical verification and explicit reporting of requirements, assumptions and limitations.

## Verification evidence

PR #7 exercised the harness from a clean GitHub Actions runner.

The first two runs failed on real harness defects:

1. overly strict parsing of the `uv --version` output;
2. Ruff formatting drift.

Both were corrected.

The third run passed the complete canonical verification command.

This is important evidence that the harness is capable of rejecting defects rather than existing only as documentation.

## Exit criteria

- [x] reproducible environment;
- [x] canonical verification commands;
- [x] CI executes the same commands;
- [x] documentation checks;
- [x] architecture checks;
- [x] initial fixtures;
- [x] Harness Bootstrap quality-score thresholds met.

## Remaining non-blocking gaps

- requirement-to-test traceability becomes concrete as feature tests are added;
- fixture coverage should expand with permitted iRacing / physical-car MoTeC / Brazilian Formula SAE datasets;
- architecture rules will become stricter as real modules gain dependencies;
- application observability is deferred until an executable application exists.

## Decision log

2026-09-22 — Harness-engineering audit determined that documentation readiness is not equivalent to executable agent readiness.

2026-09-22 — Public telemetry survey supplied initial licensed fixtures and external validation sources.

2026-09-22 — Harness bootstrap completed only after the canonical CI verification passed from a clean runner.
