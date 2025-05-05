# Integration: Dispatch Core

Dispatch Core is the internal Go service (owned by Ops Engineering) that tenders
loads to carriers, optimizes routes, and relays carrier EDI 214 status updates.
Harborline Book talks to it through `api/app/integrations/dispatch_client.py`.

## Authentication

Callers authenticate with a **service token** sent as a bearer token:

```
Authorization: Bearer <service token>
```

Tokens are issued per client and environment by `dispatchctl tokens issue`. The
documented token shape is a prefix followed by 32 alphanumeric characters:

| Environment | Prefix | Example shape |
|---|---|---|
| production | `hbl_live_` | `hbl_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` |
| sandbox / test | `hbl_test_` | same length, `hbl_test_` prefix |

Treat both kinds as secrets. `hbl_test_` tokens can still create sandbox tenders
that page the carrier-ops on-call.

Where tokens live:

* Runtime: Secrets Manager `harborline/<env>/dispatch-core/service-token`,
  exposed to pods as `HBL_DISPATCH_TOKEN`.
* Cron jobs (`scripts/reconcile_dispatch.sh`): injected by the cron wrapper.
* Tests: use the `dispatch_stub` fixture — do not call the real sandbox from CI.

## Endpoints used

| Method | Path | Purpose |
|---|---|---|
| POST | `/v2/tenders` | Tender a confirmed booking to a carrier |
| GET | `/v2/tenders/{id}` | Tender status |
| POST | `/v2/reconcile` | Nightly booking ↔ tender reconciliation |
| GET | `/v2/shipments/{tracking}/events` | Carrier status events |

## Rate limits

100 req/s per token. The reconciliation job historically ran with an exempted
token; that exemption was removed in September 2025 — batch your calls.
