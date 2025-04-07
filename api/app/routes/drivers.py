"""Endpoints used by the Harborline Driver mobile app."""
import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import Driver, ProofOfDelivery, Shipment, ShipmentStatus, TrackingEvent
from ..services import storage
from ..utils.validation import require_fields

bp = Blueprint("drivers", __name__, url_prefix="/v1/drivers")
log = logging.getLogger("harborline.drivers")

MAX_CRASH_REPORT_BYTES = 64 * 1024


@bp.post("/<int:driver_id>/position")
def update_position(driver_id: int):
    data = require_fields(request.get_json(silent=True), "lat", "lng")
    driver = db.get_or_404(Driver, driver_id)
    driver.last_lat, driver.last_lng = float(data["lat"]), float(data["lng"])
    driver.last_seen_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify(ok=True)


@bp.post("/<int:driver_id>/pod/<tracking_number>")
def upload_pod(driver_id: int, tracking_number: str):
    """Multipart upload: `signed_by` form field + optional `photo` file."""
    shipment = Shipment.query.filter_by(tracking_number=tracking_number, driver_id=driver_id).first_or_404()
    signed_by = (request.form.get("signed_by") or "").strip()
    if not signed_by:
        return jsonify(error="signed_by required"), 422

    photo_key = None
    photo = request.files.get("photo")
    if photo:
        photo_key = storage.upload_pod_photo(tracking_number, photo.stream, photo.filename, photo.mimetype)

    pod = ProofOfDelivery(shipment_id=shipment.id, driver_id=driver_id, signed_by=signed_by,
                          photo_s3_key=photo_key, notes=request.form.get("notes"))
    shipment.status = ShipmentStatus.DELIVERED
    shipment.delivered_at = datetime.now(timezone.utc)
    shipment.events.append(TrackingEvent(code="DELIVERED", description=f"Signed by {signed_by}"))
    db.session.add(pod)
    db.session.commit()
    return jsonify(pod.to_dict()), 201


@bp.post("/crash-reports")
def crash_report():
    """Crash reports from the driver app (replaces the old Slack-channel upload)."""
    if request.content_length and request.content_length > MAX_CRASH_REPORT_BYTES:
        return jsonify(error="too_large"), 413
    report = request.get_json(silent=True) or {}
    log.warning(
        "driver-app crash: version=%s device=%s error=%s",
        report.get("app_version"), report.get("device_model"), str(report.get("error"))[:200],
    )
    return jsonify(received=True), 202
