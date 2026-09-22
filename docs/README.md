# OME Documentation

This directory is the durable engineering knowledge base for **Open Motorsport Engineer (OME)**.

The repository root `AGENTS.md` defines how Codex should work. This directory defines what OME is, what the project has decided, and what is still under investigation.

## Core documents

- [PROJECT.md](PROJECT.md) — product problem, mission, scope and principles
- [MVP.md](MVP.md) — first vertical slice
- [DOMAIN.md](DOMAIN.md) — high-level domain map
- [ARCHITECTURE.md](ARCHITECTURE.md) — accepted pre-code architecture
- [QUALITY_ATTRIBUTES.md](QUALITY_ATTRIBUTES.md) — architecture drivers and quality expectations
- [TEST_STRATEGY.md](TEST_STRATEGY.md) — verification strategy
- [PLANNED_REPOSITORY_STRUCTURE.md](PLANNED_REPOSITORY_STRUCTURE.md) — implementation organization target
- [ROADMAP.md](ROADMAP.md) — engineering sequence
- [PRE_CODE_READINESS.md](PRE_CODE_READINESS.md) — readiness review

## Supporting directories

- [requirements/](requirements/) — accepted and proposed product/system requirements
- [adr/](adr/) — Architecture Decision Records
- [domain/](domain/) — validated motorsport/telemetry domain knowledge
- [specs/](specs/) — interoperability and file/profile specifications
- [research/](research/) — research and source material not automatically normative
- [plans/](plans/) — substantial engineering plans

## Knowledge promotion

Research is not automatically a requirement, domain rule or architecture decision.

```text
RESEARCH
  -> REVIEW
  -> PROJECT / DOMAIN / REQUIREMENT / ADR / SPEC
  -> IMPLEMENTATION
  -> TEST / VALIDATION
```

When documentation and implementation disagree, report the conflict instead of silently treating code as the only source of truth.
