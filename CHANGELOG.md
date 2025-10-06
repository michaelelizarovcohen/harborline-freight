# Changelog

All notable changes to Harborline Book / Harborline Driver are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.1.0] — 2025-10-14
### Added
- Rate cards per lane with fuel surcharge from the Pacific Fuel Index feed.
- Driver app: offline POD capture queue, crash reporting.
- Kubernetes manifests for the EKS migration (`infra/k8s/`).
- Secret scanning in CI and pre-commit (gitleaks).
### Changed
- Stripe, SendGrid, Twilio and Dispatch Core credentials now come from Secrets Manager.
- Terraform providers authenticate via OIDC/assumed roles instead of static keys.
### Security
- Credential rotation after the August secrets review (see `docs/runbooks/rotate-credentials.md`).

## [1.0.1] — 2025-06-19
### Fixed
- Booking confirmation emails were sent twice when the payment webhook retried.
- Web build pinned to a private npm mirror while the public registry was degraded.

## [1.0.0] — 2025-06-10
### Added
- Public launch of Harborline Book: quotes, bookings, Stripe deposits, tracking page.
- Harborline Driver beta (Android) with job list and POD photo upload.
- Staging environment on AWS (RDS Postgres, S3 document storage).

## [0.3.0] — 2025-04-18
### Added
- Docker Compose dev stack; Celery worker for document processing.
- Terraform for the staging VPC, RDS and S3 buckets.
- Deploy workflow with Slack notifications.

## [0.2.0] — 2025-03-14
### Added
- Stripe checkout for booking deposits, webhooks and refunds.
- S3 storage for bills of lading (BOL) and POD images.

## [0.1.0] — 2025-02-10
### Added
- Flask API skeleton, health checks, shipper/carrier/shipment models.
