from datetime import datetime, timezone

from ..extensions import db


class Shipper(db.Model):
    """A customer account that books freight with Harborline."""

    __tablename__ = "shippers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(32))
    # sha256 of the shipper's API key; the plaintext is only shown once at creation.
    api_key_hash = db.Column(db.String(64), unique=True, index=True)
    api_key_prefix = db.Column(db.String(12))
    credit_terms_days = db.Column(db.Integer, default=0, nullable=False)
    stripe_customer_id = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    bookings = db.relationship("Booking", back_populates="shipper", lazy="selectin")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "contact_email": self.contact_email,
            "phone": self.phone,
            "api_key_prefix": self.api_key_prefix,
            "credit_terms_days": self.credit_terms_days,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
