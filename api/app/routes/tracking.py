"""Public tracking endpoint (no auth) used by the tracking page and email links."""
from flask import Blueprint, jsonify

from ..models import Shipment

bp = Blueprint("tracking", __name__, url_prefix="/v1/track")


@bp.get("/<tracking_number>")
def track(tracking_number: str):
    shipment = Shipment.query.filter_by(tracking_number=tracking_number.upper()).first_or_404()
    # Public view: no shipper, pricing or driver details.
    return jsonify({
        "tracking_number": shipment.tracking_number,
        "status": shipment.status.value,
        "eta": shipment.eta.isoformat() if shipment.eta else None,
        "events": [e.to_dict() for e in shipment.events],
    })
