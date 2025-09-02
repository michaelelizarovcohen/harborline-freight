# ADR 0001: Single monorepo for API, web, mobile and infrastructure

* Status: Accepted
* Date: 2025-02-03
* Deciders: Dana Okafor, Marcus Lindqvist, Tomás Ferreira

## Context

Ledgerline (PHP billing) and the original quoting prototype lived in separate
repositories with copy-pasted models and inconsistent deploys. We are a team of
under ten engineers rewriting the platform for the v1.0 launch.

## Decision

One repository containing `api/`, `web/`, `driver-app/`, `infra/`, `scripts/`,
`deploy/`, `config/` and `notebooks/`, with path-filtered CI jobs.

## Consequences

* + Atomic changes across API and clients; one place for CI, CODEOWNERS and scanning.
* + Easier onboarding.
* − Everyone can read everything, so a credential committed anywhere is visible to
  the whole team and every CI runner. Mitigated by ADR 0002.
* − CI must use path filters to stay fast.
