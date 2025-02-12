from flask import Blueprint, g, jsonify

from ..auth.tokens import require_session
from ..models import Booking, Shipment
from ..utils.pagination import paginate

bp = Blueprint("shipments", __name__, url_prefix="/v1/shipments")


@bp.get("")
@require_session
def list_shipments():
    query = (
        Shipment.query.join(Booking)
        .filter(Booking.shipper_id == g.shipper_id)
        .order_by(Shipment.created_at.desc())
    )
    return jsonify(paginate(query))


@bp.get("/<tracking_number>")
@require_session
def get_shipment(tracking_number: str):
    shipment = (
        Shipment.query.join(Booking)
        .filter(Shipment.tracking_number == tracking_number, Booking.shipper_id == g.shipper_id)
        .first_or_404()
    )
    return jsonify(shipment.to_dict(include_events=True))
