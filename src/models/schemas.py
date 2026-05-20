"""
SQLModel ORM schemas — single source of truth for all database tables.

Used by both the FastAPI (SQLite) layer and referenced by the DuckDB analytics layer.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import Column, Field, JSON, SQLModel


class User(SQLModel, table=True):
    """Platform user with role and language preference."""
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    role: str  # admin | cfo | coo | hr | esg | analyst | viewer
    hashed_password: str
    preferred_language: str = Field(default="en")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class KPIData(SQLModel, table=True):
    """Unified KPI metric row."""
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    period: str = Field(index=True)  # YYYY-MM
    metric: str = Field(index=True)
    value: float
    category: str  # Finance | Growth | Operations | People | ESG
    segment: str = Field(default="Global")
    unit: str = Field(default="")
    direction: str = Field(default="higher_is_better")
    source_file: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    """Immutable audit trail."""
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: str
    details: str = Field(default="")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentMetadata(SQLModel, table=True):
    """Metadata for uploaded/scanned documents."""
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    doc_type: str = Field(default="Other")
    status: str = Field(default="Pending")  # Pending | Processed | Error
    extracted_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class Conversation(SQLModel, table=True):
    """Chat message + response for the AI copilot."""
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    session_id: str = Field(index=True, default="default")
    message: str
    response: str = Field(default="")
    context_used: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    language: str = Field(default="en")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
