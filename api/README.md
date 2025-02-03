# Harborline Book API

Flask service behind `api.harborline.example`. It powers instant LTL/FTL quotes,
bookings, carrier dispatch (via Dispatch Core), shipment tracking, digital bills of
lading (BOL) and proof-of-delivery (POD) uploads from the Harborline Driver app.

Owners: backend guild (Marcus Lindqvist), payments (Priya Raman).

## Local development

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
export FLASK_APP=wsgi.py HBL_ENV=development
flask run --port 8080
```

With no `DATABASE_URL` set, development mode uses `sqlite:///harborline-dev.db`.
Use `docker compose up` from the repository root for a PostgreSQL-backed stack.

## Configuration

All configuration comes from environment variables (see `config/settings.py` and the
repository-level `.env.example`). **Never hard-code credentials** — production values
live in AWS SSM Parameter Store and are injected by the deploy pipeline.

| Variable | Used by |
|---|---|
| `DATABASE_URL` | SQLAlchemy |
| `SECRET_KEY` | session token signing |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | `app/services/payments.py` |
| `SENDGRID_API_KEY` | `app/services/email.py` |
| `TWILIO_ACCOUNT_SID`, `TWILIO_API_KEY_SID`, `TWILIO_API_KEY_SECRET` | `app/services/sms.py` |
| `HBL_DISPATCH_URL`, `HBL_DISPATCH_TOKEN` | `app/integrations/dispatch_client.py` |
| `AWS_REGION`, `BOL_BUCKET` | `app/services/storage.py` |

## Tests

```bash
python -m pytest -q
```

Tests run against in-memory SQLite and never call Stripe, SendGrid, Twilio, S3 or
Dispatch Core.
