"""Shipper API keys and short-lived session tokens.

* API keys are random, shown once, and stored as sha256 hashes.
* Session tokens are itsdangerous-signed payloads using SECRET_KEY.
  (SSO / JWT support is being built on feature/sso — not merged yet.)
"""
import functools
import hashlib
import hmac
import secrets

from flask import current_app, g, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

API_KEY_PREFIX = "hbk"
_SALT = "harborline-session-v1"


def generate_api_key() -> tuple[str, str]:
    """Return (plaintext, sha256-hash). Only the hash is persisted."""
    plaintext = f"{API_KEY_PREFIX}_{secrets.token_urlsafe(24)}"
    return plaintext, hash_api_key(plaintext)


def hash_api_key(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode()).hexdigest()


def api_key_matches(plaintext: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_api_key(plaintext), stored_hash)


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=_SALT)


def issue_session_token(shipper_id: int, scopes: list[str] | None = None) -> str:
    return _serializer().dumps({"sid": shipper_id, "scopes": scopes or ["bookings"]})


def verify_session_token(token: str) -> dict | None:
    max_age = current_app.config.get("SESSION_TOKEN_MAX_AGE", 43200)
    try:
        return _serializer().loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None


def require_session(view):
    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return jsonify(error="unauthorized"), 401
        claims = verify_session_token(token)
        if claims is None:
            return jsonify(error="unauthorized"), 401
        g.shipper_id = claims["sid"]
        g.scopes = claims.get("scopes", [])
        return view(*args, **kwargs)

    return wrapper
