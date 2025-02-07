"""Quote engine for LTL and FTL freight.

LTL is priced per hundredweight (CWT) by freight class and distance band; FTL is
priced per loaded mile with a minimum. A fuel surcharge is applied to linehaul
only, then accessorials are added on top.
"""
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from .geocoding import lane_distance_miles

# Base CWT rate (USD per 100 lbs) by distance band for class 70 freight.
LTL_BASE_CWT = [
    (250, Decimal("18.40")),
    (500, Decimal("24.75")),
    (1000, Decimal("33.10")),
    (1500, Decimal("41.60")),
    (10_000, Decimal("52.20")),
]

# NMFC freight class multipliers relative to class 70.
CLASS_MULTIPLIER = {
    "50": Decimal("0.72"), "55": Decimal("0.78"), "60": Decimal("0.84"), "65": Decimal("0.90"),
    "70": Decimal("1.00"), "77.5": Decimal("1.08"), "85": Decimal("1.18"), "92.5": Decimal("1.27"),
    "100": Decimal("1.38"), "125": Decimal("1.62"), "150": Decimal("1.88"), "200": Decimal("2.35"),
}

FTL_RATE_PER_MILE = Decimal("2.85")
FTL_MINIMUM = Decimal("650.00")
FTL_MAX_WEIGHT_LBS = 44_000
LTL_MAX_WEIGHT_LBS = 12_000

ACCESSORIALS = {
    "liftgate": Decimal("85.00"),
    "residential": Decimal("110.00"),
    "inside_delivery": Decimal("125.00"),
    "appointment": Decimal("35.00"),
    "hazmat": Decimal("95.00"),
}

CENT = Decimal("0.01")


class QuoteError(ValueError):
    pass


@dataclass
class Quote:
    mode: str
    origin: str
    destination: str
    miles: float
    linehaul: Decimal
    fuel_surcharge: Decimal
    accessorials: dict[str, Decimal] = field(default_factory=dict)

    @property
    def total(self) -> Decimal:
        return (self.linehaul + self.fuel_surcharge + sum(self.accessorials.values(), Decimal("0"))).quantize(CENT)

    @property
    def total_cents(self) -> int:
        return int(self.total * 100)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "origin": self.origin,
            "destination": self.destination,
            "miles": self.miles,
            "linehaul": str(self.linehaul),
            "fuel_surcharge": str(self.fuel_surcharge),
            "accessorials": {k: str(v) for k, v in self.accessorials.items()},
            "total": str(self.total),
            "currency": "USD",
        }


def _ltl_base_rate(miles: float) -> Decimal:
    for limit, rate in LTL_BASE_CWT:
        if miles <= limit:
            return rate
    return LTL_BASE_CWT[-1][1]


def quote(
    origin: str,
    destination: str,
    weight_lbs: int,
    mode: str = "LTL",
    freight_class: str = "70",
    accessorials: list[str] | None = None,
    hazmat: bool = False,
    fuel_surcharge_pct: float = 0.18,
    min_ltl_charge: float = 145.00,
) -> Quote:
    mode = mode.upper()
    if origin.upper() == destination.upper():
        raise QuoteError("origin and destination must differ")
    if weight_lbs <= 0:
        raise QuoteError("weight must be positive")

    miles = lane_distance_miles(origin, destination)

    if mode == "LTL":
        if weight_lbs > LTL_MAX_WEIGHT_LBS:
            raise QuoteError(f"LTL limited to {LTL_MAX_WEIGHT_LBS} lbs; quote FTL instead")
        multiplier = CLASS_MULTIPLIER.get(str(freight_class))
        if multiplier is None:
            raise QuoteError(f"unsupported freight class {freight_class}")
        cwt = Decimal(weight_lbs) / Decimal(100)
        linehaul = max(_ltl_base_rate(miles) * multiplier * cwt, Decimal(str(min_ltl_charge)))
    elif mode == "FTL":
        if weight_lbs > FTL_MAX_WEIGHT_LBS:
            raise QuoteError(f"FTL limited to {FTL_MAX_WEIGHT_LBS} lbs")
        linehaul = max(FTL_RATE_PER_MILE * Decimal(str(miles)), FTL_MINIMUM)
    else:
        raise QuoteError(f"unknown mode {mode}")

    linehaul = linehaul.quantize(CENT, rounding=ROUND_HALF_UP)
    fuel = (linehaul * Decimal(str(fuel_surcharge_pct))).quantize(CENT, rounding=ROUND_HALF_UP)

    extras: dict[str, Decimal] = {}
    for name in accessorials or []:
        if name not in ACCESSORIALS:
            raise QuoteError(f"unknown accessorial {name}")
        extras[name] = ACCESSORIALS[name]
    if hazmat:
        extras["hazmat"] = ACCESSORIALS["hazmat"]

    return Quote(mode, origin.upper(), destination.upper(), miles, linehaul, fuel, extras)
