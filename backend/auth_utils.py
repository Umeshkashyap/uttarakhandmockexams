"""
UttarakhandMockExams — Auth Utilities
JWT (HS256) + bcrypt-style password hashing using Python stdlib only
"""
import hmac
import hashlib
import base64
import json
import time
import os
import re

JWT_SECRET = os.environ.get("JWT_SECRET", "uttarakhandmockexams_secret_change_in_production")
JWT_EXPIRES_SECONDS = int(os.environ.get("JWT_EXPIRES_SECONDS", str(7 * 24 * 3600)))

# ─── Password Hashing (PBKDF2 via stdlib) ────────────────────────────────────
def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with random salt."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260000)
    return base64.b64encode(salt + key).decode()

def verify_password(password: str, stored: str) -> bool:
    """Verify password against stored hash."""
    try:
        raw = base64.b64decode(stored.encode())
        salt = raw[:16]
        stored_key = raw[16:]
        key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260000)
        return hmac.compare_digest(key, stored_key)
    except Exception:
        return False

# ─── JWT (HS256) ──────────────────────────────────────────────────────────────
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)

def create_token(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {**payload, "iat": now, "exp": now + JWT_EXPIRES_SECONDS}
    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig_input = f"{h}.{p}".encode()
    sig = hmac.new(JWT_SECRET.encode(), sig_input, hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url_encode(sig)}"

def verify_token(token: str) -> dict:
    """Returns decoded payload or raises ValueError."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format")
    h, p, sig = parts
    sig_input = f"{h}.{p}".encode()
    expected = hmac.new(JWT_SECRET.encode(), sig_input, hashlib.sha256).digest()
    actual = _b64url_decode(sig)
    if not hmac.compare_digest(expected, actual):
        raise ValueError("Invalid token signature")
    payload = json.loads(_b64url_decode(p))
    if payload.get("exp", 0) < int(time.time()):
        raise ValueError("Token expired")
    return payload

def extract_token(auth_header: str) -> str:
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header")
    return auth_header[7:]
