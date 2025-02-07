from flask import Blueprint, current_app, jsonify, request

from ..services.geocoding import TERMINALS, UnknownTerminal
from ..services.pricing import QuoteError, quote
from ..utils.validation import ValidationError, one_of, positive_int, require_fields

bp = Blueprint("quotes", __name__, url_prefix="/v1/quotes")


@bp.get("/terminals")
def list_terminals():
    return jsonify([
        {"code": t.code, "name": t.name, "region": t.region} for t in TERMINALS.values()
    ])


@bp.post("")
def create_quote():
    data = require_fields(request.get_json(silent=True), "origin", "destination", "weight_lbs")
    mode = one_of(data, "mode", {"LTL", "FTL"}, default="LTL")
    weight = positive_int(data, "weight_lbs", maximum=44_000)
    try:
        q = quote(
            data["origin"],
            data["destination"],
            weight,
            mode=mode,
            freight_class=str(data.get("freight_class", "70")),
            accessorials=data.get("accessorials") or [],
            hazmat=bool(data.get("hazmat", False)),
            fuel_surcharge_pct=current_app.config["FUEL_SURCHARGE_PCT"],
            min_ltl_charge=current_app.config["MIN_LTL_CHARGE"],
        )
    except UnknownTerminal as exc:
        raise ValidationError({"terminal": f"unknown terminal {exc.args[0]}"}) from None
    except QuoteError as exc:
        raise ValidationError({"quote": str(exc)}) from None
    return jsonify(q.to_dict()), 201
