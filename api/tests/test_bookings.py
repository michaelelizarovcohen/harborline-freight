def test_booking_requires_session(client, next_week):
    resp = client.post("/v1/bookings", json={"origin": "PCL", "destination": "SDR",
                                             "weight_lbs": 900, "pickup_date": next_week})
    assert resp.status_code == 401


def test_session_exchange(client, shipper):
    resp = client.post("/v1/auth/session", json={"api_key": shipper.plaintext_api_key})
    assert resp.status_code == 200
    assert resp.get_json()["token_type"] == "Bearer"
    assert client.post("/v1/auth/session", json={"api_key": "not-a-real-key"}).status_code == 401


def test_create_list_cancel_booking(client, auth_headers, next_week):
    resp = client.post("/v1/bookings", headers=auth_headers, json={
        "origin": "PCL", "destination": "SDR", "weight_lbs": 900, "pallets": 2, "pickup_date": next_week,
    })
    assert resp.status_code == 201, resp.get_json()
    booking = resp.get_json()
    assert booking["reference"].startswith("HBL-")
    assert booking["status"] == "awaiting_deposit"

    listing = client.get("/v1/bookings", headers=auth_headers).get_json()
    assert listing["total"] == 1

    cancelled = client.post(f"/v1/bookings/{booking['reference']}/cancel", headers=auth_headers)
    assert cancelled.get_json()["status"] == "cancelled"


def test_deposit_unavailable_without_stripe_key(client, auth_headers, next_week):
    booking = client.post("/v1/bookings", headers=auth_headers, json={
        "origin": "OKV", "destination": "MSA", "weight_lbs": 400, "pickup_date": next_week,
    }).get_json()
    resp = client.post(f"/v1/payments/deposits/{booking['reference']}", headers=auth_headers)
    assert resp.status_code == 503


def test_pickup_date_in_past_rejected(client, auth_headers):
    resp = client.post("/v1/bookings", headers=auth_headers, json={
        "origin": "PCL", "destination": "SDR", "weight_lbs": 900, "pickup_date": "2020-01-01",
    })
    assert resp.status_code == 422
