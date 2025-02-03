from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from ..extensions import db

bp = Blueprint("health", __name__)

VERSION = "1.1.0"


@bp.get("/healthz")
def healthz():
    return jsonify(status="ok", service="harborline-book-api", version=VERSION)


@bp.get("/readyz")
def readyz():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - readiness must never raise
        current_app.logger.exception("readiness check failed")
        return jsonify(status="degraded", database="unreachable"), 503
    return jsonify(status="ready", database="ok")
