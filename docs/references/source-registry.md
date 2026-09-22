# OME External Source Registry

Last verified: **2026-09-22**

## Agent/harness engineering

### OpenAI — Harness engineering: leveraging Codex in an agent-first world

URL: https://openai.com/index/harness-engineering/

Use:

- repository knowledge as system of record;
- short root AGENTS.md;
- agent legibility;
- execution plans;
- mechanical architecture checks;
- continuous drift/technical-debt cleanup.

Classification: informative engineering practice.

### OpenAI — Custom instructions with AGENTS.md

URL: https://learn.chatgpt.com/docs/agent-configuration/agents-md

Use:

- AGENTS.md scoping and precedence;
- nested instruction behavior.

Classification: Codex behavior reference.

### OpenAI — Using PLANS.md for multi-hour problem solving

URL: https://developers.openai.com/cookbook/articles/codex_exec_plans

Use:

- execution-plan lifecycle and self-contained long-running tasks.

Classification: agent workflow reference.

## Telemetry / motorsport

### ASAM MDF

URL: https://www.asam.net/standards/detail/mdf/

Use:

- reference for measurement metadata, time bases and multi-rate data capabilities.

Classification: external standard reference.

### MoTeC i2

URL: https://www.motec.com.au/products/I2

Use:

- professional motorsport workflow and export feasibility.

Classification: product/workflow reference.

### MoTeC i2 API User Guide

URL: https://website.motec.com.au/hessian/uploads/i2_API_User_Guide_330ed28c83.pdf

Use:

- native `.ld` integration feasibility and constraints.

Classification: vendor API feasibility reference.

### iRacing telemetry documentation

URL: https://ir-core-sites.iracing.com/dev/atlas/atlas_quickstart.pdf

Use:

- `.ibt` telemetry source feasibility.

Classification: vendor format/workflow reference.

### iRacing 2017 Season 1 release notes

URL: https://www.iracing.com/2017-season-1-release-notes/

Use:

- source semantics for 360 Hz telemetry time-subdivision arrays;
- evidence that six array elements at a 60 Hz base tick may represent a 360 Hz source channel.

Classification: vendor format/telemetry semantics reference.

## Technology

Technology-specific references are recorded in `docs/research/technology-evaluation.md`.

Architecture decisions remain authoritative over external documentation.


## Public telemetry datasets

### exit_speed — Traqmate/race-car telemetry

URL: https://github.com/djhedges/exit_speed

Verified artifacts:

- small Traqmate parking-lot telemetry CSV;
- larger Portland International Raceway telemetry logs.

License:

Apache-2.0 at repository level.

OME use:

- small file vendored under `fixtures/public/exit-speed/`;
- larger track data retained as an external benchmark candidate.

Classification: public telemetry fixture / real vehicle data.

### teamjorge/ibt — iRacing binary telemetry fixture

URL: https://github.com/teamjorge/ibt

Verified artifact:

`.testing/valid_test_file.ibt`

Observed:

- iRacing v2 file;
- 60 Hz;
- 276 variables;
- session/track metadata;
- lap distance and driver/vehicle channels.

License note:

Repository is published under Apache-2.0, but OME has not independently established redistribution rights for simulator-generated telemetry binaries.

OME use:

External validation source only until redistribution is cleared.

Classification: public external fixture / simulation telemetry.

### CR Formula — Iowa State Formula SAE logs

URL: https://github.com/CR-Formula/FSAEElectrical

Verified artifacts:

Public CSV logs for Autocross, Skidpad, Practice and Endurance.

License note:

No explicit repository-level redistribution license was identified during this review.

OME use:

External validation source only.

Classification: real Formula SAE competition/test telemetry.

### TRACE — MoTeC-style CSV fixtures

URL: https://github.com/keystroke-tools/TRACE

Verified artifacts:

- canonical MoTeC-style CSV fixture;
- decreasing-time negative fixture.

License:

MIT.

OME use:

Vendored under `fixtures/public/trace/`.

Classification: synthetic interoperability/validation fixture.

### B'Energy Racing — racing-data-converter

URL: https://github.com/BenergyRacing/racing-data-converter

Use:

Evidence of Brazilian Formula SAE telemetry tooling and supported motorsport format families.

No representative raw session fixture was identified in the repository during this review.

Classification: Brazilian tooling/workflow reference.

### Icarus/UFRJ telemetry projects

Use:

Evidence of Brazilian Formula SAE field telemetry work.

No full redistributable vehicle-session dataset suitable for OME fixtures was identified during this review.

Classification: Brazilian workflow reference / outreach target.
