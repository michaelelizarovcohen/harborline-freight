"""SMS notifications (pickup windows, delivery ETAs) via Twilio.

Uses an API key SID/secret pair scoped to Messaging rather than the account auth
token, per the Twilio hardening checklist Tomás put together.
"""
import logging

from flask import current_app

log = logging.getLogger("harborline.sms")


class SmsNotConfigured(RuntimeError):
    pass


def _client():
    from twilio.rest import Client  # lazy import; twilio is optional in dev

    cfg = current_app.config
    account_sid = cfg.get("TWILIO_ACCOUNT_SID")
    key_sid = cfg.get("TWILIO_API_KEY_SID")
    key_secret = cfg.get("TWILIO_API_KEY_SECRET")
    if not (account_sid and key_sid and key_secret):
        raise SmsNotConfigured("TWILIO_ACCOUNT_SID / TWILIO_API_KEY_SID / TWILIO_API_KEY_SECRET not set")
    return Client(key_sid, key_secret, account_sid)


def send_sms(to: str, body: str) -> str:
    message = _client().messages.create(to=to, from_=current_app.config["TWILIO_FROM_NUMBER"], body=body)
    log.info("sms %s queued to %s", message.sid, to[-4:])
    return message.sid


def notify_pickup_window(phone: str, reference: str, window: str) -> str:
    return send_sms(phone, f"Harborline: pickup for {reference} scheduled {window}. Reply STOP to opt out.")
