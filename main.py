"""
OmniIntelOS v2.0 — Intelligence Operating System Entry Point.

Usage:
    python main.py                 # FastAPI server (default)
    python main.py --api           # FastAPI server
    python main.py --legacy-api    # FastAPI server (v1, backward compat)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to Python path for proper imports
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ⚡ PERFORMANCE: Apply optimizations before any heavy imports
import src.core.performance  # noqa: F401

# Ensure .env is loaded before any module reads os.getenv
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")


def main():
    if "--legacy-api" in sys.argv:
        from src.api.server import run_server
        run_server()
    else:
        # Default: FastAPI server with JWT + Persona Factory
        import uvicorn
        uvicorn.run(
            "src.api.server_v2:app",
            host="0.0.0.0",
            port=8000,
            reload="--reload" in sys.argv,
            log_level="info",
        )


if __name__ == "__main__":
    main()
