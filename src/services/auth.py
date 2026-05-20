"""
Unified RBAC — Authentication, Authorization & Audit.

Replaces the former ``auth_rbac.py`` and ``rbac_advanced.py`` with a single
authoritative implementation backed by ``ROLE_DEFINITIONS`` in config.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from src.core.config import (
    ROLE_DEFINITIONS,
    Role,
    get_role_definition,
    get_role_pages,
    has_data_access,
    has_role_permission,
    settings,
)
from src.core.i18n import I18N, t
from src.core.logger import get_logger
from src.models.schemas import AuditLog, User

log = get_logger(__name__)

# ── Password helpers ────────────────────────────────────────────────────────

_SALT = settings.SECRET_KEY.encode()


def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), _SALT, 100_000).hex()


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


# ── Built-in users (for first-run / demo) ───────────────────────────────────

DEFAULT_USERS = {
    "admin":   {"password": "admin2026!",   "role": "admin",   "name": "System Administrator"},
    "cfo":     {"password": "cfo2026!",     "role": "cfo",     "name": "Chief Financial Officer"},
    "coo":     {"password": "coo2026!",     "role": "coo",     "name": "Chief Operating Officer"},
    "hr":      {"password": "hr2026!",      "role": "hr",      "name": "HR Director"},
    "esg":     {"password": "esg2026!",     "role": "esg",     "name": "ESG Officer"},
    "analyst": {"password": "analyst2026!", "role": "analyst", "name": "Data Analyst"},
    "viewer":  {"password": "viewer2026!",  "role": "viewer",  "name": "Board Member"},
}


# ── Core RBAC Manager ──────────────────────────────────────────────────────

class RBACManager:
    """Single entry-point for all auth / permission / audit logic."""

    def __init__(self, session: Optional[Session] = None):
        self.session = session

    # ── Auth ────────────────────────────────────────────────────────────
    def authenticate(self, username: str, password: str) -> Optional[User]:
        if not self.session:
            return None
        user = self.session.exec(select(User).where(User.username == username)).first()
        if user and verify_password(password, user.hashed_password):
            return user
        return None

    def create_user(
        self, username: str, password: str, role: str = "viewer", language: str = "en",
    ) -> Optional[User]:
        if not self.session:
            return None
        if self.session.exec(select(User).where(User.username == username)).first():
            return None
        try:
            Role(role)
        except ValueError:
            return None
        user = User(
            username=username,
            hashed_password=hash_password(password),
            role=role,
            preferred_language=language,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        self._audit(None, "user_created", f"{username} ({role})")
        return user

    # ── Permission checks ──────────────────────────────────────────────
    def permissions_for(self, user_id: int) -> Dict[str, Any]:
        if not self.session:
            return {}
        user = self.session.get(User, user_id)
        if not user:
            return {}
        return get_role_definition(user.role)

    def can_action(self, user_id: int, action: str) -> bool:
        return action in self.permissions_for(user_id).get("actions", [])

    def can_page(self, user_id: int, page: str) -> bool:
        pages = self.permissions_for(user_id).get("pages", [])
        return "all" in pages or page in pages

    def can_data(self, user_id: int, category: str) -> bool:
        access = self.permissions_for(user_id).get("data_access", [])
        return "all" in access or category.lower() in access

    def can_manage_users(self, user_id: int) -> bool:
        return self.permissions_for(user_id).get("can_manage_users", False)

    def can_view_audit(self, user_id: int) -> bool:
        return self.permissions_for(user_id).get("can_view_audit", False)

    # ── Role management ────────────────────────────────────────────────
    def assign_role(self, user_id: int, new_role: str, admin_id: int) -> bool:
        if not self.session or not self.can_manage_users(admin_id):
            return False
        try:
            Role(new_role)
        except ValueError:
            return False
        user = self.session.get(User, user_id)
        if not user:
            return False
        old = user.role
        user.role = new_role
        self.session.add(user)
        self.session.commit()
        self._audit(admin_id, "role_changed", f"{user.username}: {old} → {new_role}")
        return True

    # ── User management ────────────────────────────────────────────────
    def list_users(self) -> List[Dict[str, Any]]:
        if not self.session:
            return []
        return [
            {"id": u.id, "username": u.username, "role": u.role, "lang": u.preferred_language}
            for u in self.session.exec(select(User)).all()
        ]

    def change_password(self, user_id: int, new_pw: str) -> bool:
        if not self.session:
            return False
        user = self.session.get(User, user_id)
        if not user:
            return False
        user.hashed_password = hash_password(new_pw)
        self.session.add(user)
        self.session.commit()
        self._audit(user_id, "password_changed", user.username)
        return True

    # ── Audit ──────────────────────────────────────────────────────────
    def _audit(self, user_id: Optional[int], action: str, details: str) -> None:
        if not self.session:
            return
        self.session.add(AuditLog(user_id=user_id, action=action, details=details))
        self.session.commit()

    def audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.session:
            return []
        rows = self.session.exec(
            select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
        ).all()
        return [
            {"id": r.id, "user_id": r.user_id, "action": r.action,
             "details": r.details, "ts": r.timestamp.isoformat()}
            for r in rows
        ]
