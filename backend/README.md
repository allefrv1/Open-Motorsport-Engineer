# OME backend

The backend is the Python modular-monolith core for telemetry ingestion, validation, normalization, operational context, deterministic analysis, evidence and application services.

## Current executable boundary

Plan 015 adds the first local FastAPI adapter under:

`backend/src/ome/api/`

The API delegates to the existing application layer and does not own deterministic engineering calculations.

Run it from the repository root:

```text
uv run --locked uvicorn --app-dir backend/src ome.api:create_app --factory --host 127.0.0.1 --port 8000
```

See `docs/specs/local-comparison-report-http-api-v0.1.md` for the transport contract.

## Architecture rule

FastAPI/Pydantic transport types remain inside `ome.api`.

Core layers remain framework-independent and are protected by `architecture.toml`.
