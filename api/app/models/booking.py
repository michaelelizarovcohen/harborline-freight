import enum
from datetime import datetime, timezone

from ..extensions import db


class BookingStatus(str, enum.Enum):
    DRAFT = "draft"
    AWAITING_DEPOSIT = "awaiting_deposit"
    CONFIRMED = "confirmed"
    DISPATCHED = "dispatched"
    CANCELLED = "cancelled"


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(16), unique=True, nullable=False, index=True)  # HBL-XXXXXX
    shipper_id = db.Column(db.Integer, db.ForeignKey("shippers.id"), nullable=False)
    mode = db.Column(db.String(3), nullable=False)  # LTL | FTL
    origin_terminal = db.Column(db.String(8), nullable=False)
    destination_terminal = db.Column(db.String(8), nullable=False)
    weight_lbs = db.Column(db.Integer, nullable=False)
    pallets = db.Column(db.Integer, default=1, nullable=False)
    freight_class = db.Column(db.String(5), default="70")
    hazmat = db.Column(db.Boolean, default=False, nullable=False)
    pickup_date = db.Column(db.Date, nullable=False)
    quoted_total_cents = db.Column(db.Integer, nullable=False)
    deposit_cents = db.Column(db.Integer, default=0, nullable=False)
    stripe_payment_intent = db.Column(db.String(64))
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.DRAFT, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    shipper = db.relationship("Shipper", back_populates="bookings")
    shipment = db.relationship("Shipment", back_populates="booking", uselist=False)
    invoices = db.relationship("Invoice", back_populates="booking")

    @property
    def quoted_total(self) -> float:
        return self.quoted_total_cents / 100

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "reference": self.reference,
            "shipper_id": self.shipper_id,
            "mode": self.mode,
            "origin": self.origin_terminal,
            "destination": self.destination_terminal,
            "weight_lbs": self.weight_lbs,
            "pallets": self.pallets,
            "freight_class": self.freight_class,
            "hazmat": self.hazmat,
            "pickup_date": self.pickup_date.isoformat(),
            "quoted_total": self.quoted_total,
            "deposit": self.deposit_cents / 100,
            "status": self.status.value,
            "tracking_number": self.shipment.tracking_number if self.shipment else None,
        }
