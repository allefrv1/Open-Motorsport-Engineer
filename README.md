# Open Motorsport Engineer

**Open Motorsport Engineer (OME)** is an open-source platform for motorsport telemetry analysis and performance engineering.

The project aims to make motorsport data analysis more accessible to drivers, engineers, students, coaches, and racing teams by transforming raw telemetry into clear and actionable engineering insights.

Modern motorsport generates a large amount of data, but understanding that data often requires specialized knowledge, expensive tools, or professional consulting. OME aims to reduce that barrier by providing an open, transparent, and extensible platform for telemetry analysis.

## Goals

OME is designed to help users:

* Analyze lap and session telemetry
* Compare drivers, laps, and sessions
* Identify where lap time is gained or lost
* Analyze braking, throttle, steering, speed, and vehicle behavior
* Detect consistency and performance trends
* Generate derived telemetry channels
* Identify possible vehicle behavior and performance issues
* Create automated session and run reports
* Support driver coaching and performance engineering workflows

## Open Data Architecture

One of the main goals of OME is to create a normalized telemetry model that allows data from different sources to be analyzed through the same system.

Future data sources may include:

* iRacing
* MoTeC
* AiM
* Cosworth
* CSV telemetry
* CAN bus data
* ECU loggers
* Other simulation and real-world motorsport systems

The analysis engine should remain independent from the original telemetry source.

## Project Philosophy

OME is not intended to replace professional tools such as MoTeC i2, AiM RaceStudio, or Cosworth Pi Toolbox.

Instead, the project focuses on building an open ecosystem around motorsport data analysis, making engineering knowledge and telemetry interpretation more accessible.

The platform is designed around a few principles:

* Open source
* Transparent analysis
* Extensible architecture
* Vendor-independent telemetry
* Local-first operation whenever possible
* Accessible to beginners
* Powerful enough for advanced users and engineers

## Long-Term Vision

The long-term vision of Open Motorsport Engineer is to become an open engineering platform for motorsport.

Future modules may include:

* Driver Performance Analysis
* Vehicle Dynamics Analysis
* Setup Comparison
* Tyre Analysis
* Vehicle Health Monitoring
* Automated Anomaly Detection
* Race Strategy Analysis
* Telemetry Visualization
* Automated Engineering Reports
* AI-assisted telemetry exploration

The goal is simple:

> **Make motorsport engineering more open, understandable, and accessible.**

## Run locally

OME provides a FastAPI backend and a React/Vite investigation frontend. For a fully
worked example with physical Traqmate data, follow [the quickstart](docs/QUICKSTART.md).

### Docker Compose (optional)

Install Docker Engine or Docker Desktop with Docker Compose v2, then run from the
repository root:

```bash
docker compose up --build
```

Open **http://127.0.0.1:5173** in your browser. The API health endpoint is
**http://127.0.0.1:8000/healthz**. Both ports are published on localhost only.

Compose starts exactly two application services: `web` (Vite/React) and `api`
(FastAPI). The web service proxies `/api` requests to the backend container.
No PostgreSQL, Redis or cloud service is required.

To stop the stack:

```bash
docker compose down
```

These images provide an optional local development environment, **not a production
deployment**. Persistent project storage and external telemetry mounts are not yet
part of this Compose workflow.

### Native development (canonical)

The native locked toolchain remains the repository's canonical development and
verification path. See [development setup](docs/DEVELOPMENT.md) for pinned
Python, uv, Node and pnpm versions and setup commands.

Start the API from the repository root:

```bash
uv sync --locked
uv run --locked uvicorn --app-dir backend/src ome.api:create_app --factory --host 127.0.0.1 --port 8000
```

In a second terminal, install and start the frontend:

```bash
pnpm install --frozen-lockfile
pnpm --dir frontend dev
```

Run the complete canonical verification:

```bash
uv run --locked python scripts/harness.py verify
```

## Current Stage

OME now has a runnable local vertical slice.

The current system can:

- import controlled OME CSV telemetry;
- ingest iRacing `.ibt`, MoTeC CSV and Traqmate Trackvision CSV through source-specific adapters;
- preserve source provenance and Missing Evidence;
- prepare deterministic lap comparisons;
- compare physical Traqmate laps through the local HTTP API;
- render delta time, synchronized telemetry, observations, evidence status and provenance in the React investigation frontend.

For a reproducible local demonstration using the committed Portland physical-car fixture, see:

`docs/QUICKSTART.md`

The interactive engineering workspace provides synchronized Plotly zoom/pan, optional
channel visibility, distance-interval focus controls, keyboard-operable exact sample
inspection, concise observations, and full evidence/provenance disclosure. The browser
does not interpolate, rank laps or infer missing physical inputs.

The project is still under active development and does not yet include persistence/history, desktop packaging, automatic lap ranking or AI explanation.


## Browser QA

CI exercises the committed Portland Traqmate fixture using headless Chromium and the
real Docker Compose app. It verifies lap selection, synchronized plots, cursor/zoom controls,
explicit Missing Evidence and the mobile layout. Desktop/mobile screenshots are published
as GitHub Actions artifacts. See
[browser verification instructions](docs/DEVELOPMENT.md#optional-real-browser-ui-verification).
