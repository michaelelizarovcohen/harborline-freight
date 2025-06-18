import json
import base64

from app.auth.sso import mint_session


def _claims(token: str) -> dict:
    payload = token.split(".")[1]
    payload += "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(payload))


def test_mint_session_has_expected_claims():
    token = mint_session("sso:qa@harborline.example", "qa@harborline.example")
    claims = _claims(token)
    assert claims["aud"] == "harborline-book"
    assert claims["role"] == "shipper_admin"
    assert claims["exp"] > claims["iat"]
