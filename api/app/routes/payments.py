import logging
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request

from ..auth.tokens import require_session
from ..extensions import db
from ..models import Booking, BookingStatus, Invoice, InvoiceStatus
from ..services import payments

bp = Blueprint("payments", __name__, url_prefix="/v1/payments")
log = logging.getLogger("harborline.payments")


@bp.post("/deposits/<reference>")
@require_session
def create_deposit(reference: str):
    booking = Booking.query.filter_by(reference=reference, shipper_id=g.shipper_id).first_or_404()
    if booking.status != BookingStatus.AWAITING_DEPOSIT:
        return jsonify(error="deposit_not_required", status=booking.status.value), 409
    try:
        intent = payments.create_deposit_intent(booking, booking.shipper.stripe_customer_id)
    except payments.PaymentsNotConfigured:
        log.error("payments not configured; cannot take deposit for %s", reference)
        return jsonify(error="payments_unavailable"), 503
    booking.stripe_payment_intent = intent["payment_intent"]
    booking.deposit_cents = intent["amount"]
    db.session.commit()
    return jsonify(client_secret=intent["client_secret"], amount=intent["amount"]), 201


@bp.post("/webhooks/stripe")
def stripe_webhook():
    signature = request.headers.get("Stripe-Signature", "")
    try:
        event = payments.construct_webhook_event(request.get_data(), signature)
    except payments.PaymentsNotConfigured:
        return jsonify(error="payments_unavailable"), 503
    except Exception:  # stripe.error.SignatureVerificationError, ValueError
        log.warning("rejected stripe webhook with bad signature")
        return jsonify(error="bad_signature"), 400

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        booking = Booking.query.filter_by(stripe_payment_intent=intent["id"]).first()
        if booking and booking.status == BookingStatus.AWAITING_DEPOSIT:
            booking.status = BookingStatus.CONFIRMED
            db.session.add(Invoice(
                number=f"INV-{datetime.now(timezone.utc):%Y}-{booking.id:06d}",
                booking_id=booking.id,
                kind="deposit",
                amount_cents=intent["amount_received"],
                status=InvoiceStatus.PAID,
                stripe_charge_id=intent.get("latest_charge"),
                paid_at=datetime.now(timezone.utc),
            ))
            db.session.commit()
            log.info("deposit received for %s", booking.reference)
    return jsonify(received=True)
