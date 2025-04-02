from flask import Blueprint, jsonify, request

from ..auth.tokens import hash_api_key, issue_session_token
from ..models import Shipper
from ..utils.validation import require_fields

bp = Blueprint("auth", __name__, url_prefix="/v1/auth")


@bp.post("/session")
def create_session():
    """Exchange a shipper API key for a short-lived session token."""
    data = require_fields(request.get_json(silent=True), "api_key")
    shipper = Shipper.query.filter_by(api_key_hash=hash_api_key(data["api_key"])).first()
    if shipper is None:
        return jsonify(error="invalid_api_key"), 401
    token = issue_session_token(shipper.id)
    return jsonify(token=token, token_type="Bearer", shipper=shipper.to_dict())
