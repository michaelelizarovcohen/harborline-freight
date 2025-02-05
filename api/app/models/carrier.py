from ..extensions import db


class Carrier(db.Model):
    """A trucking partner that hauls Harborline loads."""

    __tablename__ = "carriers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    scac = db.Column(db.String(4), unique=True, nullable=False)  # Standard Carrier Alpha Code
    usdot_number = db.Column(db.String(12))
    modes = db.Column(db.String(32), default="LTL,FTL")  # comma separated; TODO normalize
    on_time_rate = db.Column(db.Float, default=0.95)
    active = db.Column(db.Boolean, default=True, nullable=False)

    drivers = db.relationship("Driver", back_populates="carrier", lazy="selectin")
    shipments = db.relationship("Shipment", back_populates="carrier")

    def supports(self, mode: str) -> bool:
        return mode.upper() in {m.strip().upper() for m in (self.modes or "").split(",")}

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "scac": self.scac,
            "usdot_number": self.usdot_number,
            "modes": [m.strip() for m in (self.modes or "").split(",") if m.strip()],
            "on_time_rate": self.on_time_rate,
            "active": self.active,
        }
