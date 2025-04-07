"""Harborline Book API application factory."""
import logging
import os
import sys

from flask import Flask, jsonify

from config import CONFIG_BY_NAME

from .extensions import db


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("HBL_ENV", "development")
    config_cls = CONFIG_BY_NAME.get(config_name)
    if config_cls is None:
        raise ValueError(f"unknown config {config_name!r}")

    app = Flask(__name__)
    app.config.from_object(config_cls)
    _configure_logging(app)

    if config_name in {"production", "staging"}:
        missing = config_cls.missing_settings()
        if missing:
            # Fail fast: a half-configured API is worse than no API.
            raise RuntimeError(f"missing required settings: {', '.join(missing)}")

    db.init_app(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    with app.app_context():
        from . import models  # noqa: F401  (register mappers)

        if app.config.get("TESTING") or config_name == "development":
            # TODO(marcus): switch dev to Alembic migrations like staging/prod.
            db.create_all()

    return app


def _register_blueprints(app: Flask) -> None:
    from .routes.auth import bp as auth_bp
    from .routes.bookings import bp as bookings_bp
    from .routes.drivers import bp as drivers_bp
    from .routes.health import bp as health_bp
    from .routes.payments import bp as payments_bp
    from .routes.quotes import bp as quotes_bp
    from .routes.shipments import bp as shipments_bp
    from .routes.tracking import bp as tracking_bp

    for bp in (health_bp, auth_bp, quotes_bp, bookings_bp, shipments_bp,
               tracking_bp, payments_bp, drivers_bp):
        app.register_blueprint(bp)


def _register_error_handlers(app: Flask) -> None:
    from .utils.validation import ValidationError

    @app.errorhandler(ValidationError)
    def _validation_error(err: ValidationError):
        return jsonify(error="validation_failed", details=err.errors), 422

    @app.errorhandler(404)
    def _not_found(_err):
        return jsonify(error="not_found"), 404

    @app.errorhandler(405)
    def _method_not_allowed(_err):
        return jsonify(error="method_not_allowed"), 405


def _configure_logging(app: Flask) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger("harborline")
    root.handlers[:] = [handler]
    root.setLevel(app.config.get("LOG_LEVEL", "INFO"))
