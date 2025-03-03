import secrets
import string
from datetime import date

from flask import Blueprint, current_app, g, jsonify, request

from ..auth.tokens import require_session
from ..extensions import db
from ..models import Booking, BookingStatus
from ..services.geocoding import UnknownTerminal
from ..services.pricing import QuoteError, quote
from ..utils.pagination import paginate
from ..utils.validation import ValidationError, iso_date, one_of, positive_int, require_fields

bp = Blueprint("bookings", __name__, url_prefix="/v1/bookings")

_REF_ALPHABET = string.ascii_uppercase + string.digits


def _new_reference() -> str:
    return "HBL-" + "".join(secrets.choice(_REF_ALPHABET) for _ in range(6))


@bp.post("")
@require_session
def create_booking():
    data = require_fields(request.get_json(silent=True), "origin", "destination", "weight_lbs", "pickup_date")
    mode = one_of(data, "mode", {"LTL", "FTL"}, default="LTL")
    weight = positive_int(data, "weight_lbs", maximum=44_000)
    pallets = positive_int({"pallets": data.get("pallets", 1)}, "pallets", maximum=26)
    pickup = iso_date(data, "pickup_date", not_before=date.today())
    try:
        q = quote(
            data["origin"], data["destination"], weight, mode=mode,
            freight_class=str(data.get("freight_class", "70")),
            accessorials=data.get("accessorials") or [],
            hazmat=bool(data.get("hazmat", False)),
            fuel_surcharge_pct=current_app.config["FUEL_SURCHARGE_PCT"],
            min_ltl_charge=current_app.config["MIN_LTL_CHARGE"],
        )
    except UnknownTerminal as exc:
        raise ValidationError({"terminal": f"unknown terminal {exc.args[0]}"}) from None
    except QuoteError as exc:
        raise ValidationError({"quote": str(exc)}) from None

    booking = Booking(
        reference=_new_reference(),
        shipper_id=g.shipper_id,
        mode=mode,
        origin_terminal=q.origin,
        destination_terminal=q.destination,
        weight_lbs=weight,
        pallets=pallets,
        freight_class=str(data.get("freight_class", "70")),
        hazmat=bool(data.get("hazmat", False)),
        pickup_date=pickup,
        quoted_total_cents=q.total_cents,
        status=BookingStatus.AWAITING_DEPOSIT,
    )
    db.session.add(booking)
    db.session.commit()
    # Deposit intent is created client-side via POST /v1/payments/deposits/<ref> so a
    # Stripe outage doesn't block booking creation (INC-2025-031).
    return jsonify(booking.to_dict()), 201


@bp.get("")
@require_session
def list_bookings():
    query = Booking.query.filter_by(shipper_id=g.shipper_id).order_by(Booking.created_at.desc())
    status = request.args.get("status")
    if status:
        try:
            query = query.filter(Booking.status == BookingStatus(status))
        except ValueError:
            raise ValidationError({"status": "unknown status"}) from None
    return jsonify(paginate(query))


@bp.get("/<reference>")
@require_session
def get_booking(reference: str):
    booking = Booking.query.filter_by(reference=reference, shipper_id=g.shipper_id).first_or_404()
    return jsonify(booking.to_dict())


@bp.post("/<reference>/cancel")
@require_session
def cancel_booking(reference: str):
    booking = Booking.query.filter_by(reference=reference, shipper_id=g.shipper_id).first_or_404()
    if booking.status in {BookingStatus.DISPATCHED, BookingStatus.CANCELLED}:
        return jsonify(error="not_cancellable", status=booking.status.value), 409
    booking.status = BookingStatus.CANCELLED
    db.session.commit()
    # TODO(priya): trigger deposit refund automatically once refunds are idempotent.
    return jsonify(booking.to_dict())
