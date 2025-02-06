"""Application configuration.

Every credential is read from the environment. Production values are stored in
AWS SSM Parameter Store (/harborline/<env>/api/*) and injected at deploy time.
"""
import os
import secrets


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class BaseConfig:
    ENV_NAME = "base"
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_TOKEN_MAX_AGE = int(os.environ.get("SESSION_TOKEN_MAX_AGE", "43200"))  # 12h

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Payments (Priya): deposits are charged at booking time, balance on delivery.
    STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
    STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
    BOOKING_DEPOSIT_PERCENT = float(os.environ.get("BOOKING_DEPOSIT_PERCENT", "0.20"))

    # Notifications
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    MAIL_FROM = os.environ.get("MAIL_FROM", "bookings@harborline.example")
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
    TWILIO_API_KEY_SID = os.environ.get("TWILIO_API_KEY_SID")
    TWILIO_API_KEY_SECRET = os.environ.get("TWILIO_API_KEY_SECRET")
    TWILIO_FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "+15555550142")

    # Dispatch Core (internal carrier-assignment service)
    HBL_DISPATCH_URL = os.environ.get("HBL_DISPATCH_URL", "https://dispatch.svc.harborline.internal")
    HBL_DISPATCH_TOKEN = os.environ.get("HBL_DISPATCH_TOKEN")
    HBL_DISPATCH_TIMEOUT = float(os.environ.get("HBL_DISPATCH_TIMEOUT", "5"))

    # AWS
    AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
    BOL_BUCKET = os.environ.get("BOL_BUCKET", "harborline-bol-documents")
    POD_BUCKET = os.environ.get("POD_BUCKET", "harborline-pod-uploads")

    # Pricing knobs (overridable per environment for experiments)
    FUEL_SURCHARGE_PCT = float(os.environ.get("FUEL_SURCHARGE_PCT", "0.18"))
    MIN_LTL_CHARGE = float(os.environ.get("MIN_LTL_CHARGE", "145.00"))

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


class DevelopmentConfig(BaseConfig):
    ENV_NAME = "development"
    DEBUG = True
    # Fixed fallback so sessions survive the reloader and `flask shell`. Dev only!
    SECRET_KEY = os.environ.get("SECRET_KEY", "TGBCuWVyeh4Gza2hu0u7I7rrZ16k4qpLRZEzIodUNQnEe-QFWW")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///harborline-dev.db")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")


class TestingConfig(BaseConfig):
    ENV_NAME = "testing"
    TESTING = True
    SECRET_KEY = secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    HBL_DISPATCH_URL = "https://dispatch.test.invalid"
    HBL_DISPATCH_TOKEN = None
    STRIPE_SECRET_KEY = None
    SENDGRID_API_KEY = None


class ProductionConfig(BaseConfig):
    ENV_NAME = "production"
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"
    REQUIRED_SETTINGS = (
        "SECRET_KEY",
        "SQLALCHEMY_DATABASE_URI",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "HBL_DISPATCH_TOKEN",
    )

    @classmethod
    def missing_settings(cls) -> list[str]:
        return [name for name in cls.REQUIRED_SETTINGS if not getattr(cls, name, None)]


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "staging": ProductionConfig,
}
