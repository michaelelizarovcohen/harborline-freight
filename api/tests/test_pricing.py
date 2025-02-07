from decimal import Decimal

import pytest

from app.services.geocoding import lane_distance_miles
from app.services.pricing import QuoteError, quote


def test_lane_distance_is_symmetric():
    assert lane_distance_miles("PCL", "SDR") == lane_distance_miles("SDR", "PCL")


def test_ltl_minimum_charge_applies_to_tiny_shipments():
    q = quote("PCL", "RVD", 100, mode="LTL", fuel_surcharge_pct=0.0, min_ltl_charge=145.0)
    assert q.linehaul == Decimal("145.00")


def test_ltl_class_multiplier_raises_price():
    base = quote("PCL", "SLT", 2000, freight_class="70")
    heavy_class = quote("PCL", "SLT", 2000, freight_class="125")
    assert heavy_class.total > base.total


def test_ftl_priced_per_mile_with_minimum():
    short = quote("PCL", "PCL2", 30_000, mode="FTL", fuel_surcharge_pct=0.0)
    assert short.linehaul == Decimal("650.00")
    long = quote("PCL", "CHI", 30_000, mode="FTL", fuel_surcharge_pct=0.0)
    assert long.linehaul > Decimal("5000")


def test_accessorials_and_hazmat_added():
    q = quote("OKV", "SDR", 1500, accessorials=["liftgate"], hazmat=True)
    assert set(q.accessorials) == {"liftgate", "hazmat"}
    assert q.total == (q.linehaul + q.fuel_surcharge + Decimal("180.00")).quantize(Decimal("0.01"))


@pytest.mark.parametrize("kwargs", [
    {"origin": "PCL", "destination": "PCL", "weight_lbs": 500},
    {"origin": "PCL", "destination": "RVD", "weight_lbs": 0},
    {"origin": "PCL", "destination": "RVD", "weight_lbs": 20_000, "mode": "LTL"},
    {"origin": "PCL", "destination": "RVD", "weight_lbs": 500, "freight_class": "13"},
    {"origin": "PCL", "destination": "RVD", "weight_lbs": 500, "accessorials": ["teleport"]},
])
def test_invalid_quotes_rejected(kwargs):
    with pytest.raises(QuoteError):
        quote(**kwargs)
