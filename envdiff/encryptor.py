"""Encrypt and decrypt sensitive values in .env files using Fernet symmetric encryption."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore

from envdiff.redactor import is_sensitive


@dataclass
class EncryptionResult:
    source: str
    encrypted: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        return bool(self.errors)

    def summary(self) -> str:
        parts = [f"Encrypted {len(self.encrypted)} key(s)"]
        if self.skipped:
            parts.append(f"skipped {len(self.skipped)}")
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        return ", ".join(parts) + "."


def generate_key() -> str:
    """Generate a new Fernet key and return it as a URL-safe base64 string."""
    if Fernet is None:  # pragma: no cover
        raise RuntimeError("cryptography package is required: pip install cryptography")
    return Fernet.generate_key().decode()


def encrypt_env(
    env: Dict[str, str],
    key: str,
    *,
    sensitive_only: bool = True,
    extra_keys: Optional[List[str]] = None,
    source: str = "<dict>",
) -> EncryptionResult:
    """Encrypt values in *env*. Returns an EncryptionResult."""
    if Fernet is None:  # pragma: no cover
        raise RuntimeError("cryptography package is required: pip install cryptography")
    fernet = Fernet(key.encode() if isinstance(key, str) else key)
    extra = set(extra_keys or [])
    result = EncryptionResult(source=source)
    for k, v in env.items():
        if sensitive_only and not is_sensitive(k) and k not in extra:
            result.skipped.append(k)
            continue
        try:
            token = fernet.encrypt(v.encode()).decode()
            result.encrypted[k] = token
        except Exception as exc:  # pragma: no cover
            result.errors.append(f"{k}: {exc}")
    return result


def decrypt_env(
    encrypted: Dict[str, str],
    key: str,
    *,
    source: str = "<dict>",
) -> EncryptionResult:
    """Decrypt Fernet-encrypted values. Returns an EncryptionResult with plain values."""
    if Fernet is None:  # pragma: no cover
        raise RuntimeError("cryptography package is required: pip install cryptography")
    fernet = Fernet(key.encode() if isinstance(key, str) else key)
    result = EncryptionResult(source=source)
    for k, v in encrypted.items():
        try:
            plain = fernet.decrypt(v.encode()).decode()
            result.encrypted[k] = plain
        except InvalidToken:
            result.errors.append(f"{k}: invalid token or wrong key")
    return result
