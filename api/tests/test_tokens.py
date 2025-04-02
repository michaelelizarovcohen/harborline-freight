from app.auth.tokens import (
    api_key_matches,
    generate_api_key,
    issue_session_token,
    verify_session_token,
)


def test_api_key_hash_roundtrip():
    plaintext, digest = generate_api_key()
    assert plaintext.startswith("hbk_")
    assert api_key_matches(plaintext, digest)
    assert not api_key_matches(plaintext + "x", digest)


def test_session_token_roundtrip(app):
    token = issue_session_token(42, ["bookings", "invoices"])
    claims = verify_session_token(token)
    assert claims == {"sid": 42, "scopes": ["bookings", "invoices"]}


def test_tampered_token_rejected(app):
    token = issue_session_token(7)
    assert verify_session_token(token[:-2] + "xx") is None
