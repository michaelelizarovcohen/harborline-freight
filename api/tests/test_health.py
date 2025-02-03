def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_readyz(client):
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.get_json()["database"] == "ok"


def test_unknown_route_returns_json(client):
    resp = client.get("/nope")
    assert resp.status_code == 404
    assert resp.get_json() == {"error": "not_found"}
