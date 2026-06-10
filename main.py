"""
IntelAI — Persona-Aware AI Analytics & RAG Copilot. Entry point.

Usage:
    python main.py              # start the API server (http://localhost:8000)
    python main.py --reload     # with auto-reload (development)

Production uses the Dockerfile CMD: ``uvicorn src.api.server:app``.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the project root importable, then load environment.
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")


def main() -> None:
    import uvicorn
    from src.core.config import settings

    uvicorn.run(
        "src.api.server:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload="--reload" in sys.argv,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
