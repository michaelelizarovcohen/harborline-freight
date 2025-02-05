import enum
from datetime import datetime, timezone

from ..extensions import db


class ShipmentStatus(str, enum.Enum):
    PENDING_PICKUP = "pending_pickup"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    EXCEPTION = "exception"


def _utcnow():
    return datetime.now(timezone.utc)


class Shipment(db.Model):
    __tablename__ = "shipments"

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    carrier_id = db.Column(db.Integer, db.ForeignKey("carriers.id"))
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"))
    status = db.Column(db.Enum(ShipmentStatus), default=ShipmentStatus.PENDING_PICKUP, nullable=False)
    bol_s3_key = db.Column(db.String(512))
    eta = db.Column(db.DateTime(timezone=True))
    delivered_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), default=_utcnow)

    booking = db.relationship("Booking", back_populates="shipment")
    carrier = db.relationship("Carrier", back_populates="shipments")
    driver = db.relationship("Driver", back_populates="shipments")
    events = db.relationship(
        "TrackingEvent", back_populates="shipment", order_by="TrackingEvent.occurred_at",
        cascade="all, delete-orphan",
    )

    def to_dict(self, include_events: bool = False) -> dict:
        data = {
            "id": self.id,
            "tracking_number": self.tracking_number,
            "booking_id": self.booking_id,
            "carrier": self.carrier.scac if self.carrier else None,
            "status": self.status.value,
            "eta": self.eta.isoformat() if self.eta else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
        }
        if include_events:
            data["events"] = [e.to_dict() for e in self.events]
        return data


class TrackingEvent(db.Model):
    __tablename__ = "tracking_events"

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey("shipments.id"), nullable=False)
    code = db.Column(db.String(32), nullable=False)  # e.g. PICKED_UP, ARRIVED_TERMINAL
    description = db.Column(db.String(255))
    location = db.Column(db.String(120))
    occurred_at = db.Column(db.DateTime(timezone=True), default=_utcnow, nullable=False)

    shipment = db.relationship("Shipment", back_populates="events")

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "description": self.description,
            "location": self.location,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
        }
