# OME Documentation

This directory is the durable engineering knowledge base for **Open Motorsport Engineer (OME)**.

The repository root `AGENTS.md` defines how Codex should work. This directory defines what OME is, what the project has decided, and what is still under investigation.

## Start here

- [PROJECT.md](PROJECT.md) — product problem, mission, scope and principles
- [DOMAIN.md](DOMAIN.md) — current domain map and terminology
- [ARCHITECTURE.md](ARCHITECTURE.md) — current architecture constraints and boundaries

## Supporting directories

- [requirements/](requirements/) — accepted and proposed product/system requirements
- [adr/](adr/) — Architecture Decision Records
- [domain/](domain/) — validated motorsport engineering knowledge used by the product
- [research/](research/) — research and source material not yet promoted to project rules
- [plans/](plans/) — implementation plans for substantial work

## Documentation rule

Research is not automatically a requirement, domain rule or architecture decision.

Knowledge should be promoted deliberately:

    RESEARCH
      -> REVIEW
      -> PROJECT / DOMAIN / REQUIREMENT / ADR
      -> IMPLEMENTATION

When documentation and implementation disagree, report the conflict instead of silently treating the code as the only source of truth.