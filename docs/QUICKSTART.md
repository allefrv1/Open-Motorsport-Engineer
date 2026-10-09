# OME Local Demo Quickstart

Status: **Runnable vertical slice**

## What this demo proves

This path exercises the current physical-car investigation flow end to end:

```text
real Traqmate CSV
-> local FastAPI upload
-> source-preserving import
-> explicit source-lap selection
-> physical track-reference preparation
-> deterministic lap comparison
-> physical supporting evidence
-> comparison report
-> React investigation UI
```

The browser remains presentation/transport only. Engineering calculations stay in the backend.

## Prerequisites

Use the pinned versions documented in `docs/DEVELOPMENT.md`:

- Python 3.13.15
- uv 0.12.17
- Node.js 24.21.0 LTS
- pnpm 11.27.1

## Install

From the repository root:

```text
uv sync --locked
pnpm install --frozen-lockfile
```

Optional but recommended before the demo:

```text
uv run --locked python scripts/harness.py verify
```

## Terminal 1 — start the local API

From the repository root:

```text
uv run --locked uvicorn --app-dir backend/src ome.api:create_app --factory --host 127.0.0.1 --port 8000
```

Health check:

```text
http://127.0.0.1:8000/healthz
```

Physical comparison endpoint:

```text
POST /api/v1/traqmate/comparison-reports
```

## Terminal 2 — start the frontend

From the repository root:

```text
pnpm --dir frontend dev
```

Open:

```text
http://127.0.0.1:5173
```

Vite proxies `/api` to the local FastAPI server on port 8000.

## Physical Traqmate demo

In the browser:

1. choose **Physical Traqmate**;
2. select:
   `fixtures/public/exit-speed/traqmate-portland-laps-4-5.csv`;
3. set **Reference source lap** to `4`;
4. set **Candidate source lap** to `5`;
5. set **Grid step (m)** to `5` for the current deterministic demo;
6. choose **Compare laps**.

## Expected result

A successful investigation should expose:

- deterministic delta time where:
  `Delta = Lap B - Lap A`;
- synchronized physical telemetry;
- speed evidence;
- engine-speed evidence;
- gear evidence;
- observations expressed as measured gain/loss rather than causal diagnosis;
- provenance under **Method and provenance**;
- explicit Missing Evidence for unsupported physical inputs.

For the committed Portland fixture:

- `vehicle.speed` is available;
- `engine.speed` is available;
- `transmission.gear` is available;
- `driver.throttle` is Missing Evidence;
- `driver.brake` is Missing Evidence;
- `driver.steering` is Missing Evidence.

Missing Evidence is intentional. OME does not fabricate channels that the source data cannot support.

## Reference and candidate order

The UI does not automatically choose a fastest/best lap.

You explicitly choose:

- reference lap;
- candidate lap.

Swapping `4` and `5` changes the comparison direction.

## If the comparison is not ready

The UI keeps the deterministic workflow stage visible, including stages such as:

- import;
- lap window;
- track reference;
- comparison preparation;
- supporting evidence;
- report.

Do not work around a not-ready result by modifying source evidence.

## Controlled OME CSV demo

The existing controlled workflow remains available through **Controlled OME CSV**.

It requires:

- Lap A CSV;
- Lap A sidecar;
- Lap B CSV;
- Lap B sidecar.

That path is useful for deterministic project-owned fixtures and lower-level comparison validation.

## Current limitations

This runnable slice is not yet a finished desktop product.

It intentionally does not include:

- automatic lap ranking;
- automatic fastest-lap selection;
- persistent session/history storage;
- one-click desktop packaging;
- automatic source detection in the browser;
- inferred physical throttle/brake/steering;
- causal driver/setup diagnosis;
- AI explanation.

Those are future product increments and must preserve the same evidence-first architecture.
