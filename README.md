# Harborline Freight — Engineering Monorepo

Harborline Freight, Inc. builds **Harborline Book**, a freight-booking platform for
small and mid-sized shippers, and **Harborline Driver**, the mobile app our carrier
partners use for dispatch, proof-of-delivery (POD) and live tracking.

This repository contains everything that ships to production:

| Path | What lives there | Owner |
|---|---|---|
| `api/` | Flask REST API (quotes, bookings, dispatch, tracking, payments webhooks) | Backend (Marcus, Priya) |
| `web/` | React + Vite shipper portal | Frontend (Aiko) |
| `driver-app/` | Expo / React Native driver app | Mobile (Jordan) |
| `infra/` | Terraform (AWS us-west-2) and Kubernetes manifests for EKS | Platform (Tomás) |
| `.github/workflows/` | CI, deploys, secret scanning | Platform / Security |
| `notebooks/` | Analytics notebooks (churn, lane pricing) | Data (Samira) |
| `scripts/` | Operational scripts: backups, reconciliation, legacy exports | Platform |
| `deploy/` | Deploy helpers, runner bootstrap, Helm values | Platform |
| `config/` | Shared, non-secret application configuration | Backend |
| `docs/` | Architecture notes, ADRs, runbooks, onboarding | Everyone |

## Local development

Prerequisites: Docker 24+, Python 3.12, Node 20, `make`.

```bash
cp .env.example .env          # fill in local values — never commit .env
make up                       # postgres, redis, rabbitmq, api, worker, web
make seed                     # demo shippers, carriers and shipments
open http://localhost:5173    # shipper portal
curl localhost:8000/healthz   # API health
```

The API talks to Postgres on `localhost:5432` with the throwaway local
credentials defined in `docker-compose.yml`. **Never point local compose at
staging or production databases** — use the bastion tunnel described in
`docs/onboarding.md` and read-only roles instead.

## Make targets

| Target | Description |
|---|---|
| `make up` / `make down` | Start / stop the local stack |
| `make seed` | Load demo data via `scripts/seed_dev_data.py` |
| `make test` | Run API tests (pytest) and web unit tests |
| `make lint` | ruff + eslint |
| `make scan` | Run gitleaks against the working tree and full history |
| `make tf-plan ENV=staging` | Terraform plan for an environment |

## Secrets

Secrets come from environment variables locally and from AWS Secrets Manager /
SSM Parameter Store in deployed environments (see
`docs/adr/0002-secrets-management.md`). The pre-commit hook runs gitleaks; please
install it with `pre-commit install`.

If you think a credential was committed, **do not just delete it** — follow
`docs/runbooks/rotate-credentials.md` and ping `#sec-help`.

## Release process

We tag releases from `main` (`vX.Y.Z`). Hotfixes are cut from the release tag,
tagged, and cherry-picked back to `main`. See `CHANGELOG.md`.
