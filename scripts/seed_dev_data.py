#!/usr/bin/env python3
"""Seed the local development database with demo shippers, carriers and shipments.

Usage (from the repo root, with the compose stack running):

    make seed
    # or
    HBL_ENV=development python scripts/seed_dev_data.py --shippers 5 --bookings 40

Only ever run this against a local database. It refuses to run when HBL_ENV is
staging or production.
"""
from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "api"
sys.path.insert(0, str(API_DIR))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.booking import Booking, BookingStatus  # noqa: E402
from app.models.carrier import Carrier  # noqa: E402
from app.models.driver import Driver  # noqa: E402
from app.models.shipment import Shipment, ShipmentStatus, TrackingEvent  # noqa: E402
from app.models.shipper import Shipper  # noqa: E402

SHIPPERS = [
    ("Cascade Outdoor Supply", "logistics@cascade-outdoor.example"),
    ("Bluewater Ceramics", "shipping@bluewater-ceramics.example"),
    ("Northfork Coffee Roasters", "ops@northfork-coffee.example"),
    ("Tidewater Marine Parts", "orders@tidewater-marine.example"),
    ("Granite Peak Brewing", "freight@granitepeak.example"),
    ("Saltmarsh Textiles", "dock@saltmarsh-textiles.example"),
]

CARRIERS = [
    ("Ridgeline Transport", "RDGT", "3141592"),
    ("Coastal Haulers LLC", "CSTH", "2718281"),
    ("Evergreen Linehaul", "EVGL", "1618033"),
]

DRIVER_NAMES = ["Ana Souza", "Ben Okoro", "Chen Wei", "Dmitri Volkov", "Elena Ruiz", "Femi Adeyemi"]
TERMINALS = ["PCL", "SEA", "TAC", "PDX", "OAK", "SAC", "BOI", "SLC"]


def _ref(prefix: str, n: int) -> str:
    return f"{prefix}-{n:06d}"


def seed(shippers: int, bookings: int, rng: random.Random) -> None:
    carriers = [Carrier(name=n, scac=s, usdot_number=d) for n, s, d in CARRIERS]
    db.session.add_all(carriers)
    db.session.flush()

    drivers = []
    for i, name in enumerate(DRIVER_NAMES):
        drivers.append(Driver(carrier_id=carriers[i % len(carriers)].id, full_name=name,
                              phone=f"+1-555-01{i:02d}", cdl_state="WA"))
    db.session.add_all(drivers)

    shipper_rows = [Shipper(name=n, contact_email=e, credit_terms_days=rng.choice([0, 15, 30]))
                    for n, e in SHIPPERS[:shippers]]
    db.session.add_all(shipper_rows)
    db.session.flush()

    today = date.today()
    for i in range(bookings):
        origin, dest = rng.sample(TERMINALS, 2)
        mode = rng.choice(["LTL", "LTL", "FTL"])
        weight = rng.randint(400, 9_000) if mode == "LTL" else rng.randint(20_000, 42_000)
        total = int(weight * rng.uniform(0.18, 0.31) * 100)
        status = rng.choice(list(BookingStatus))
        booking = Booking(
            reference=_ref("HBL", 100_000 + i), shipper_id=rng.choice(shipper_rows).id,
            mode=mode, origin_terminal=origin, destination_terminal=dest,
            weight_lbs=weight, pallets=max(1, weight // 1_200),
            pickup_date=today + timedelta(days=rng.randint(-20, 10)),
            quoted_total_cents=total, deposit_cents=total // 5, status=status,
        )
        db.session.add(booking)
        db.session.flush()

        carrier = rng.choice(carriers)
        shipment = Shipment(
            tracking_number=f"HB{rng.randint(10**9, 10**10 - 1)}", booking_id=booking.id,
            carrier_id=carrier.id, status=rng.choice(list(ShipmentStatus)),
            eta=datetime.now(timezone.utc) + timedelta(days=rng.randint(1, 6)),
        )
        db.session.add(shipment)
        db.session.flush()
        db.session.add(TrackingEvent(shipment_id=shipment.id, code="BOOKED",
                                     description="Booking confirmed", location=origin))

    db.session.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--shippers", type=int, default=len(SHIPPERS))
    parser.add_argument("--bookings", type=int, default=30)
    parser.add_argument("--seed", type=int, default=7, help="RNG seed for reproducible demo data")
    parser.add_argument("--reset", action="store_true", help="drop and recreate all tables first")
    args = parser.parse_args()

    env = os.environ.get("HBL_ENV", "development")
    if env in {"staging", "production"}:
        print(f"refusing to seed demo data into {env}", file=sys.stderr)
        return 2

    app = create_app(env)
    with app.app_context():
        if args.reset:
            db.drop_all()
            db.create_all()
        seed(args.shippers, args.bookings, random.Random(args.seed))
        print(f"seeded {args.shippers} shippers, {len(CARRIERS)} carriers, {args.bookings} bookings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
