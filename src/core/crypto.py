from __future__ import annotations

import base64
import hashlib
from typing import Tuple

from cryptography.fernet import Fernet

from src.core.config import settings


def _derive_key(secret: str) -> bytes:
    """Derive a 32-byte urlsafe base64 key from SECRET_KEY."""
    h = hashlib.sha256(secret.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(h)


def get_fernet() -> Fernet:
    key = _derive_key(settings.SECRET_KEY or 'change-me-in-production')
    return Fernet(key)


def encrypt_value(plaintext: str) -> str:
    f = get_fernet()
    token = f.encrypt(plaintext.encode('utf-8'))
    return token.decode('utf-8')


def decrypt_value(token: str) -> str:
    f = get_fernet()
    pt = f.decrypt(token.encode('utf-8'))
    return pt.decode('utf-8')
