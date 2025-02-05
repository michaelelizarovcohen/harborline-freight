import enum
from datetime import datetime, timezone

from ..extensions import db


class InvoiceStatus(str, enum.Enum):
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    REFUNDED = "refunded"


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20), unique=True, nullable=False)  # INV-2025-000123
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    kind = db.Column(db.String(16), default="deposit", nullable=False)  # deposit | balance | accessorial
    amount_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), default="usd", nullable=False)
    status = db.Column(db.Enum(InvoiceStatus), default=InvoiceStatus.OPEN, nullable=False)
    stripe_charge_id = db.Column(db.String(64))
    issued_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    paid_at = db.Column(db.DateTime(timezone=True))

    booking = db.relationship("Booking", back_populates="invoices")

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "booking_id": self.booking_id,
            "kind": self.kind,
            "amount": self.amount_cents / 100,
            "currency": self.currency,
            "status": self.status.value,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
        }
