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
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt --retries 10 --timeout 120

COPY src /app/src
COPY main.py /app/main.py

RUN mkdir -p /app/data /app/uploads /app/logs /app/chroma_db && \
    useradd -m -u 1000 appuser && chown -R appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Honor platform-injected $PORT (Railway/Render/Fly/Heroku); default 8000 locally.
# exec via sh so $PORT expands AND uvicorn becomes PID 1 (clean SIGTERM shutdown).
CMD ["sh", "-c", "exec python -m uvicorn src.api.server:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --loop uvloop --http httptools --timeout-keep-alive 30 --log-level warning"]
