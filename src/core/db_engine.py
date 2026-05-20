"""
Shared SQLite engine — breaks circular import between auth ↔ server.
"""
from __future__ import annotations

from sqlmodel import create_engine

from src.core.config import settings

_engine = create_engine(
    settings.SQLITE_URL,
    connect_args={"check_same_thread": False},
)


def get_engine():
    """Return the singleton SQLAlchemy engine."""
    return _engine
