FROM python:3.12-slim AS base

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml README.md ./

RUN uv sync --no-install-project

FROM base AS builder
COPY . .
RUN uv sync

FROM base AS runtime

ENV PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY app app
COPY alembic alembic
COPY alembic.ini alembic.ini
COPY README.md README.md

CMD ["python", "-m", "app.main"]

