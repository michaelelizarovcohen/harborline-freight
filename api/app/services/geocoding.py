"""Terminal lookup and great-circle distance.

We only quote between Harborline-served terminals for now; free-form address
geocoding (hbl-geo) is used by the web app for pickup addresses.
"""
import math
from dataclasses import dataclass

EARTH_RADIUS_MILES = 3958.8


@dataclass(frozen=True)
class Terminal:
    code: str
    name: str
    lat: float
    lng: float
    region: str


# Fictional terminal network (codes are internal, not IATA/UN/LOCODE).
TERMINALS: dict[str, Terminal] = {
    t.code: t
    for t in (
        Terminal("PCL", "Port Calder Harbor Yard", 47.251, -122.441, "PNW"),
        Terminal("PCL2", "Port Calder Rail Annex", 47.233, -122.402, "PNW"),
        Terminal("RVD", "Riverdane Crossdock", 45.523, -122.676, "PNW"),
        Terminal("SLT", "Saltmere Distribution", 40.760, -111.891, "MTN"),
        Terminal("ASH", "Ashford Junction", 39.739, -104.990, "MTN"),
        Terminal("OKV", "Oakvale Logistics Park", 37.804, -122.271, "CAL"),
        Terminal("SDR", "South Delta Reefer Hub", 34.052, -118.244, "CAL"),
        Terminal("MSA", "Mesa Gate Terminal", 33.448, -112.074, "SW"),
        Terminal("DFW", "Trinity Crossdock", 32.777, -96.797, "SC"),
        Terminal("CHI", "Lakeshore Rail Transfer", 41.878, -87.630, "MW"),
    )
}


class UnknownTerminal(KeyError):
    pass


def get_terminal(code: str) -> Terminal:
    try:
        return TERMINALS[code.upper()]
    except KeyError as exc:
        raise UnknownTerminal(code) from exc


def haversine_miles(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * math.asin(math.sqrt(a))


def lane_distance_miles(origin: str, destination: str) -> float:
    """Approximate road miles between two terminals.

    Road distance is roughly 1.17x great-circle distance on our lanes
    (Samira's Q1 analysis). TODO: replace with routed distances from Dispatch Core.
    """
    o, d = get_terminal(origin), get_terminal(destination)
    return round(haversine_miles(o.lat, o.lng, d.lat, d.lng) * 1.17, 1)
