from datetime import datetime, timezone

from ..extensions import db


class Driver(db.Model):
    __tablename__ = "drivers"

    id = db.Column(db.Integer, primary_key=True)
    carrier_id = db.Column(db.Integer, db.ForeignKey("carriers.id"), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(32), nullable=False)
    cdl_state = db.Column(db.String(2))
    app_device_id = db.Column(db.String(64))  # set when the driver signs in to Harborline Driver
    last_lat = db.Column(db.Float)
    last_lng = db.Column(db.Float)
    last_seen_at = db.Column(db.DateTime(timezone=True))

    carrier = db.relationship("Carrier", back_populates="drivers")
    shipments = db.relationship("Shipment", back_populates="driver")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "carrier_id": self.carrier_id,
            "full_name": self.full_name,
            "cdl_state": self.cdl_state,
            "last_position": (
                {"lat": self.last_lat, "lng": self.last_lng} if self.last_lat is not None else None
            ),
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
        }


class ProofOfDelivery(db.Model):
    __tablename__ = "proofs_of_delivery"

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey("shipments.id"), nullable=False, unique=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False)
    signed_by = db.Column(db.String(120), nullable=False)
    photo_s3_key = db.Column(db.String(512))
    notes = db.Column(db.Text)
    captured_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "shipment_id": self.shipment_id,
            "driver_id": self.driver_id,
            "signed_by": self.signed_by,
            "photo_s3_key": self.photo_s3_key,
            "notes": self.notes,
            "captured_at": self.captured_at.isoformat() if self.captured_at else None,
        }
