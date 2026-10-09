# syntax=docker/dockerfile:1.7

FROM ghcr.io/astral-sh/uv:0.12.17 AS uv

FROM python:3.13.15-slim AS builder

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

FROM python:3.13.15-slim AS runtime

RUN useradd --create-home --uid 10001 ome

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --chown=ome:ome backend/src /app/backend/src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/backend/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER ome

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2).read()"

CMD ["uvicorn", "--app-dir", "backend/src", "ome.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
