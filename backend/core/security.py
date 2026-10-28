"""
Security & Authentication Helper Module.
Provides secure password hashing, verification, API key inspection, and session token utilities.
"""
import secrets
import hashlib
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from backend.core.config import settings

api_key_header = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)


def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 (standard library, zero extra dependency)."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored salt$hash representation."""
    try:
        salt, key_hex = hashed_password.split("$")
        key = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False


def verify_admin_key(api_key: Optional[str] = Security(api_key_header)) -> bool:
    """Verifies that the provided API key matches the configured ADMIN_API_KEY."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing required X-Admin-API-Key header",
        )
    if not secrets.compare_digest(api_key, settings.ADMIN_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid administrative credentials",
        )
    return True
