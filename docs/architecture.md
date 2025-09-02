# Harborline Book — Architecture Overview

_Last reviewed: 2025-09-22 by Dana Okafor & Tomás Ferreira_

## Context

Harborline Freight brokers LTL and FTL freight for small and mid-sized shippers on
the West Coast. Harborline Book replaces three things we used to run on spreadsheets
and a 2019-era PHP billing app ("Ledgerline"): quoting, booking/dispatch, and
invoicing.

```
 Shippers ──► web (React/Vite) ──┐
                                  ├──► api (Flask, gunicorn) ──► Postgres 16 (RDS)
 Drivers ───► driver-app (Expo) ──┘          │   │   │
                                             │   │   └──► Redis (rate-card cache, sessions)
                                             │   └──────► RabbitMQ ──► Celery worker
                                             │                         (BOL/POD processing,
                                             │                          emails, SMS)
                                             ├──► Dispatch Core (internal, routing/tendering)
                                             ├──► Stripe (deposits, invoices)
                                             ├──► SendGrid (email), Twilio (SMS)
                                             ├──► Google Maps Platform (geocoding, maps)
                                             ├──► Pacific Fuel Index (weekly fuel surcharge)
                                             └──► S3 (BOL / POD documents)

 Analytics: booking events ──► MongoDB events store ──► weekly exports ──► notebooks/
 Legacy:    Ledgerline MySQL (read-only) ──► scripts/legacy/export_invoices.py
```

## Components

| Component | Tech | Runtime | Notes |
|---|---|---|---|
| API | Flask 3, SQLAlchemy 2 | EKS (`harborline` namespace), 3 replicas | `api/` |
| Worker | Celery 5 | EKS, 2 replicas | same image as API |
| Web | React 18 + Vite | S3 + CloudFront (prod), nginx container (staging) | `web/` |
| Driver app | Expo SDK 51 | Android (iOS beta) | `driver-app/` |
| Database | Postgres 16 | RDS Multi-AZ (prod), single-AZ (staging) | Terraform `infra/terraform/` |
| Dispatch Core | Go service owned by Ops Engineering | EKS `dispatch` namespace | Service-token auth |

## Environments

| Env | Account | Region | Deploys |
|---|---|---|---|
| dev | developer laptops (docker compose) | — | `make up` |
| staging | `harborline-staging` | us-west-2 | every merge to `main` (GitHub Actions) |
| prod | `harborline-prod` | us-west-2 | tagged releases, manual approval |

## Data flows worth knowing

* **Quotes** are computed in `api/app/services/pricing.py` from lane rate cards plus
  accessorials plus the fuel surcharge.
* **Bookings** take a Stripe deposit (PaymentIntent). The `payment_intent.succeeded`
  webhook confirms the booking and tenders it to Dispatch Core.
* **Tracking** events come from the driver app (location pings, POD) and carrier EDI
  214 messages (via Dispatch Core).
* **Documents** (BOL PDFs, POD photos) are stored in S3 with SSE-KMS; the API hands out
  short-lived presigned URLs.

## Secrets

See [ADR 0002](adr/0002-secrets-management.md). Short version: environment variables
locally, AWS Secrets Manager + External Secrets Operator on EKS, GitHub Actions
secrets/OIDC in CI. Nothing secret belongs in this repository.
