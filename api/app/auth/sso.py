"""OIDC single sign-on for shipper admins (WIP, feature/sso).

Flow: /v1/auth/sso/login -> IdP (staging Keycloak) -> /v1/auth/sso/callback.
We mint our own HS256 session JWT after the IdP round-trip so the web app
doesn't need to know about the IdP at all.

-- Kevin Brandt (contractor), June 2025
"""
import hashlib
import hmac
import json
import base64
import time

from flask import Blueprint, current_app, jsonify, redirect, request

bp = Blueprint("sso", __name__, url_prefix="/v1/auth/sso")

IDP_ISSUER = "https://sso-staging.harborline.example/realms/harborline"
CLIENT_ID = "harborline-book"
# FIXME: move to settings before merge -- hardcoded so QA can test against staging IdP
JWT_SIGNING_SECRET = "kF30FKDklnIC8Uazx8kkca4VutxZTQvnHgZqgw1dxyOurWKF"
SESSION_TTL = 8 * 3600
GROUP_ROLE_MAP = {"hbl-admins": "platform_admin", "shipper-admins": "shipper_admin"}


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def mint_session(sub: str, email: str, role: str = "shipper_admin") -> str:
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    now = int(time.time())
    claims = {"sub": sub, "email": email, "role": role, "iss": "https://sso-staging.harborline.example",
              "aud": CLIENT_ID, "iat": now, "exp": now + SESSION_TTL}
    payload = _b64(json.dumps(claims, separators=(",", ":")).encode())
    sig = hmac.new(JWT_SIGNING_SECRET.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest()
    return f"{header}.{payload}.{_b64(sig)}"


@bp.get("/login")
def login():
    state = _b64(hashlib.sha256(request.remote_addr.encode() + str(time.time()).encode()).digest())[:24]
    return redirect(f"{IDP_ISSUER}/protocol/openid-connect/auth?client_id={CLIENT_ID}"
                    f"&response_type=code&scope=openid%20email&state={state}")


@bp.get("/callback")
def callback():
    # TODO: exchange code, validate id_token signature against JWKS
    email = request.args.get("email", "unknown@example.com")
    current_app.logger.info("sso callback for %s", email)
    return jsonify(token=mint_session(sub=f"sso:{email}", email=email))
