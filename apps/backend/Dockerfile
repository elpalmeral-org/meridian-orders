# syntax=docker/dockerfile:1
# Backend de Meridian Orders · imagen multi-stage, sin herramientas de build ni root en ejecución.
# Las imágenes base se fijan por digest en F2.4 (Dependabot las mantendrá al día).

FROM ghcr.io/astral-sh/uv:0.11.32 AS uv

FROM python:3.14-slim-trixie AS build
COPY --from=uv /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app
# 1) Dependencias (capa cacheable mientras no cambie uv.lock)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
# 2) Código y migraciones
COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations
RUN uv sync --frozen --no-dev

FROM python:3.14-slim-trixie
LABEL org.opencontainers.image.source="https://github.com/elpalmeral-org/meridian-orders" \
      org.opencontainers.image.description="Meridian Orders · backend (FastAPI)" \
      org.opencontainers.image.licenses="Apache-2.0"
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=build --chown=10001:10001 /app /app
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1
USER 10001
EXPOSE 8000
# Migraciones: el Job de Argo CD (hook PreSync) ejecuta "alembic upgrade head" con esta misma imagen.
CMD ["uvicorn", "meridian_orders.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
