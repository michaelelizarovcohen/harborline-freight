"""Transactional email via the SendGrid v3 HTTP API.

We call the REST endpoint directly instead of using the sendgrid SDK — one fewer
dependency, and the payload is tiny.
"""
import logging

import requests
from flask import current_app

log = logging.getLogger("harborline.email")

SENDGRID_SEND_URL = "https://api.sendgrid.com/v3/mail/send"


class EmailNotConfigured(RuntimeError):
    pass


def _post(payload: dict) -> int:
    api_key = current_app.config.get("SENDGRID_API_KEY")
    if not api_key:
        raise EmailNotConfigured("SENDGRID_API_KEY is not set")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(SENDGRID_SEND_URL, json=payload, headers=headers, timeout=10)
    log.debug("sendgrid responded %s for %s", resp.status_code, payload.get("subject"))
    if resp.status_code >= 400:
        log.warning("sendgrid error %s: %s", resp.status_code, resp.text[:300])
    resp.raise_for_status()
    return resp.status_code


def send_email(to: str, subject: str, text: str, html: str | None = None) -> int:
    content = [{"type": "text/plain", "value": text}]
    if html:
        content.append({"type": "text/html", "value": html})
    payload = {
        "personalizations": [{"to": [{"email": to}]}],
        "from": {"email": current_app.config["MAIL_FROM"], "name": "Harborline Freight"},
        "subject": subject,
        "content": content,
    }
    return _post(payload)


def send_booking_confirmation(booking, to: str) -> int:
    subject = f"Booking {booking.reference} confirmed"
    text = (
        f"Thanks for shipping with Harborline.\n\n"
        f"Reference: {booking.reference}\n"
        f"Lane: {booking.origin_terminal} -> {booking.destination_terminal}\n"
        f"Pickup: {booking.pickup_date.isoformat()}\n"
        f"Quoted total: ${booking.quoted_total:,.2f}\n"
    )
    return send_email(to, subject, text)
