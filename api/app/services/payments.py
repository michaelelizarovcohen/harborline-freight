"""Stripe integration for booking deposits and refunds.

Owner: Priya Raman. Keys are read from app config (STRIPE_SECRET_KEY /
STRIPE_WEBHOOK_SECRET), which in turn come from the environment.
"""
import logging

from flask import current_app

log = logging.getLogger("harborline.payments")


class PaymentsNotConfigured(RuntimeError):
    pass


def _stripe():
    """Return the stripe module configured with our secret key (lazy import)."""
    api_key = current_app.config.get("STRIPE_SECRET_KEY")
    if not api_key:
        raise PaymentsNotConfigured("STRIPE_SECRET_KEY is not set")

    import stripe  # imported lazily so tests and tooling don't need the SDK

    stripe.api_key = api_key
    stripe.max_network_retries = 2
    return stripe


def deposit_amount_cents(quoted_total_cents: int) -> int:
    pct = current_app.config.get("BOOKING_DEPOSIT_PERCENT", 0.20)
    return max(int(round(quoted_total_cents * pct)), 5000)  # $50 floor


def create_deposit_intent(booking, customer_id: str | None = None) -> dict:
    stripe = _stripe()
    amount = deposit_amount_cents(booking.quoted_total_cents)
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        customer=customer_id,
        description=f"Harborline deposit {booking.reference}",
        metadata={"booking_reference": booking.reference, "kind": "deposit"},
        idempotency_key=f"deposit-{booking.reference}",
    )
    log.info("created deposit intent %s for %s (%s cents)", intent["id"], booking.reference, amount)
    return {"payment_intent": intent["id"], "client_secret": intent["client_secret"], "amount": amount}


def refund_deposit(payment_intent_id: str, reason: str = "requested_by_customer") -> str:
    stripe = _stripe()
    refund = stripe.Refund.create(payment_intent=payment_intent_id, reason=reason)
    log.info("refund %s issued for %s", refund["id"], payment_intent_id)
    return refund["id"]


def construct_webhook_event(payload: bytes, signature_header: str):
    """Verify the Stripe-Signature header and return the parsed event."""
    stripe = _stripe()
    secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise PaymentsNotConfigured("STRIPE_WEBHOOK_SECRET is not set")
    return stripe.Webhook.construct_event(payload, signature_header, secret)
