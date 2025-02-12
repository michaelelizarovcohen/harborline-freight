"""Tiny request-validation helpers (we deliberately avoided marshmallow for v1)."""
from datetime import date


class ValidationError(Exception):
    def __init__(self, errors: dict[str, str]):
        super().__init__("validation failed")
        self.errors = errors


def require_fields(data: dict | None, *fields: str) -> dict:
    if not isinstance(data, dict):
        raise ValidationError({"_body": "expected a JSON object"})
    missing = {f: "required" for f in fields if data.get(f) in (None, "")}
    if missing:
        raise ValidationError(missing)
    return data


def positive_int(data: dict, field: str, maximum: int | None = None) -> int:
    try:
        value = int(data[field])
    except (KeyError, TypeError, ValueError):
        raise ValidationError({field: "must be an integer"}) from None
    if value <= 0:
        raise ValidationError({field: "must be positive"})
    if maximum is not None and value > maximum:
        raise ValidationError({field: f"must be <= {maximum}"})
    return value


def iso_date(data: dict, field: str, not_before: date | None = None) -> date:
    try:
        value = date.fromisoformat(str(data[field]))
    except (KeyError, ValueError):
        raise ValidationError({field: "must be an ISO date (YYYY-MM-DD)"}) from None
    if not_before and value < not_before:
        raise ValidationError({field: f"must be on or after {not_before.isoformat()}"})
    return value


def one_of(data: dict, field: str, choices: set[str], default: str | None = None) -> str:
    value = str(data.get(field, default or "")).upper()
    if value not in choices:
        raise ValidationError({field: f"must be one of {sorted(choices)}"})
    return value
