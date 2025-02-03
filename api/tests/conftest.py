import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from app.auth.tokens import generate_api_key, issue_session_token  # noqa: E402
from app.extensions import db as _db  # noqa: E402
from app.models import Carrier, Shipper  # noqa: E402


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def shipper(app):
    plaintext, digest = generate_api_key()
    s = Shipper(name="Calder Coffee Roasters", contact_email="ops@caldercoffee.example",
                api_key_hash=digest, api_key_prefix=plaintext[:8])
    _db.session.add(s)
    _db.session.add(Carrier(name="Northbound Linehaul", scac="NBLH", modes="LTL,FTL"))
    _db.session.commit()
    s.plaintext_api_key = plaintext  # test-only attribute
    return s


@pytest.fixture()
def auth_headers(app, shipper):
    return {"Authorization": f"Bearer {issue_session_token(shipper.id)}"}


@pytest.fixture()
def next_week():
    return (date.today() + timedelta(days=7)).isoformat()
