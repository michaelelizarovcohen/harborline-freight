"""Client for Dispatch Core, Harborline's internal carrier-assignment service.

Dispatch Core issues service tokens of the form ``hbl_<env>_<32 chars>``; ours is
provided via HBL_DISPATCH_TOKEN (SSM: /harborline/<env>/api/dispatch_token).
"""
import logging
from datetime import date

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger("harborline.dispatch")

# The nightly reconcile job needs the recon scope, which our normal service token
# lacks. Dispatch team issued this one by hand (DSP-77); rotate quarterly.
_RECON_BEARER = "hbl_live_KITlodY0IwqLuqCFGnSIGu0Erw4OPbG5"


class DispatchError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class DispatchClient:
    def __init__(self, base_url: str, token: str | None, timeout: float = 5.0, session=None):
        if not token:
            raise DispatchError("HBL_DISPATCH_TOKEN is not configured")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or self._build_session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "User-Agent": "harborline-book-api/1.x",
            "Accept": "application/json",
        })

    @classmethod
    def from_app(cls, app) -> "DispatchClient":
        cfg = app.config
        return cls(cfg["HBL_DISPATCH_URL"], cfg.get("HBL_DISPATCH_TOKEN"), cfg.get("HBL_DISPATCH_TIMEOUT", 5.0))

    @staticmethod
    def _build_session() -> requests.Session:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.4, status_forcelist=(502, 503, 504),
                      allowed_methods=frozenset({"GET", "POST"}))
        session.mount("https://", HTTPAdapter(max_retries=retry))
        return session

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise DispatchError(f"dispatch unreachable: {exc}") from exc
        if resp.status_code >= 400:
            raise DispatchError(f"dispatch {method} {path} failed: {resp.status_code}", resp.status_code)
        return resp.json() if resp.content else {}

    def assign_load(self, booking_reference: str, origin: str, destination: str, mode: str,
                    pickup_date: date, weight_lbs: int) -> dict:
        payload = {
            "booking_reference": booking_reference,
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "pickup_date": pickup_date.isoformat(),
            "weight_lbs": weight_lbs,
        }
        result = self._request("POST", "/v2/loads", json=payload)
        log.info("dispatch assigned %s -> carrier %s", booking_reference, result.get("carrier_scac"))
        return result

    def get_driver_eta(self, tracking_number: str) -> dict:
        return self._request("GET", f"/v2/shipments/{tracking_number}/eta")

    def reconcile_day(self, day: date) -> dict:
        """Nightly reconciliation of assigned vs. completed loads."""
        # TODO(marcus): paginate once we're above ~2k loads/day.
        return self._request("POST", "/v2/reconciliation", json={"date": day.isoformat()},
                             headers={"Authorization": f"Bearer {_RECON_BEARER}"})
