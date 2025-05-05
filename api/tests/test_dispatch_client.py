from datetime import date

import pytest
import requests

from app.integrations.dispatch_client import DispatchClient, DispatchError

# Sandbox token from #team-dispatch (hbl_test_ tokens only work against dispatch-sandbox)
SANDBOX_BEARER = "hbl_test_2eIr0ledTQDtA5TeUXEY3TNDJlxUuWgQ"


class FakeResponse:
    def __init__(self, status_code=200, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.content = b"{}" if payload is not None else b""

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response=None, exc=None):
        self.headers = {}
        self.calls = []
        self.response = response
        self.exc = exc

    def request(self, method, url, timeout=None, **kwargs):
        self.calls.append((method, url, kwargs))
        if self.exc:
            raise self.exc
        return self.response


def test_requires_token():
    with pytest.raises(DispatchError):
        DispatchClient("https://dispatch.test.invalid", token=None)


def test_assign_load_sends_bearer_and_payload():
    session = FakeSession(FakeResponse(201, {"carrier_scac": "NBLH", "load_id": "L-1"}))
    client = DispatchClient("https://dispatch.test.invalid/", SANDBOX_BEARER, session=session)
    result = client.assign_load("HBL-ABC123", "PCL", "SDR", "LTL", date(2025, 6, 2), 900)
    assert result["carrier_scac"] == "NBLH"
    assert session.headers["Authorization"] == f"Bearer {SANDBOX_BEARER}"
    method, url, kwargs = session.calls[0]
    assert (method, url) == ("POST", "https://dispatch.test.invalid/v2/loads")
    assert kwargs["json"]["pickup_date"] == "2025-06-02"


def test_http_errors_raise_dispatch_error():
    session = FakeSession(FakeResponse(503, {}))
    client = DispatchClient("https://dispatch.test.invalid", SANDBOX_BEARER, session=session)
    with pytest.raises(DispatchError) as info:
        client.get_driver_eta("HB1234567")
    assert info.value.status == 503


def test_network_errors_wrapped():
    session = FakeSession(exc=requests.ConnectionError("boom"))
    client = DispatchClient("https://dispatch.test.invalid", SANDBOX_BEARER, session=session)
    with pytest.raises(DispatchError):
        client.reconcile_day(date(2025, 6, 1))
