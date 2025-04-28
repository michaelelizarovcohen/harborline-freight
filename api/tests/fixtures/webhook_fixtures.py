"""Stripe webhook payloads for tests/test_payments_webhook.py.

The signing secret below is the one from our Stripe *test-mode* sandbox that
Priya set up for fixtures. It only signs the canned payloads in this file.
"""

TEST_WEBHOOK_SECRET = "whsec_Bj6eMmyq6Csbz6KNdIGk8KH4GBA4D2gS"  # gitleaks:allow -- test-mode fixture, see module docstring

PAYMENT_INTENT_SUCCEEDED = {
    "id": "evt_1PcKj2HarborlineTest",
    "type": "payment_intent.succeeded",
    "data": {"object": {"id": "pi_3PcKj2HarborlineTest", "amount": 18500, "currency": "usd",
                         "metadata": {"booking_id": "4417"}}},
}
