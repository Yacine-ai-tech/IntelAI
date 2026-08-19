FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libpq-dev \
    build-essential \
    gcc \
    g++ \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip uv && \
    uv pip install --system --no-cache-dir -r /app/requirements.txt


COPY src /app/src
# scripts/seed_scenarios.py is imported live by the Admin scenario-switch API
# (POST /api/v1/admin/scenario) — the rest of scripts/ (seed_data.py, eval scripts) is
# CLI-only tooling, never imported by the running server, but ships alongside it since
# both are the same kind of thing (see DATA_SEEDING.md §9).
COPY scripts /app/scripts
# glossary.py/glossary_fr.py are imported live (chat copilot's term explainer); the rest
# of data/ (generated KPI CSVs, documents) is seed INPUT posted through the real API by
# scripts/seed_data.py, not something the running server itself needs on disk.
COPY data/glossary.py data/glossary_fr.py /app/data/
# Only the built SPA — see .dockerignore. server.py serves it when present, so one
# container can host API + UI; a split deploy (Vercel frontend) simply ignores it.
COPY frontend/dist /app/frontend/dist
COPY main.py /app/main.py

RUN mkdir -p /app/uploads /app/logs /app/chroma_db && \
    useradd -m -u 1000 appuser && chown -R appuser /app

USER appuser

EXPOSE 8000


# Honor platform-injected $PORT (Railway/Render/Fly/Heroku); default 8000 locally.
# exec via sh so $PORT expands AND uvicorn becomes PID 1 (clean SIGTERM shutdown).
CMD ["sh", "-c", "exec python -m uvicorn src.api.server:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level $(echo \"${LOG_LEVEL:-info}\" | tr '[:upper:]' '[:lower:]')"]
