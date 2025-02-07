def test_terminals_listed(client):
    resp = client.get("/v1/quotes/terminals")
    codes = {t["code"] for t in resp.get_json()}
    assert {"PCL", "SDR", "CHI"} <= codes


def test_create_quote(client):
    resp = client.post("/v1/quotes", json={"origin": "PCL", "destination": "SDR", "weight_lbs": 1200})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["mode"] == "LTL"
    assert float(body["total"]) > 0


def test_quote_validation_errors(client):
    resp = client.post("/v1/quotes", json={"origin": "PCL"})
    assert resp.status_code == 422
    assert "destination" in resp.get_json()["details"]


def test_unknown_terminal(client):
    resp = client.post("/v1/quotes", json={"origin": "XXX", "destination": "SDR", "weight_lbs": 500})
    assert resp.status_code == 422
