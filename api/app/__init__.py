"""Harborline Book API application factory."""
import os

from flask import Flask

from config import CONFIG_BY_NAME

from .extensions import db


def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("HBL_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(CONFIG_BY_NAME[config_name])

    db.init_app(app)

    from .routes.health import bp as health_bp

    app.register_blueprint(health_bp)
    return app
