# ADR 0002: Secrets management

* Status: Accepted (supersedes the "just use .env files" convention)
* Date: 2025-08-12
* Deciders: Lena Vogel, Dana Okafor, Tomás Ferreira

## Context

The August secrets review (SEC-14) found credentials in git history: early `.env`
files, a hardcoded payment key, Terraform provider keys and CI webhook URLs. Several
had been "removed" in later commits but were still reachable through history,
release tags and old branches.

## Decision

1. **Runtime**: AWS Secrets Manager, synced to Kubernetes by External Secrets
   Operator. Pods read environment variables; nothing secret in manifests.
2. **CI/CD**: GitHub Actions secrets for third-party tokens; AWS access via OIDC
   role assumption (no static keys).
3. **Local**: `.env` (gitignored) populated from the 1Password *Engineering — Sandbox*
   vault. Only test-mode/sandbox credentials on laptops.
4. **Detection**: gitleaks in pre-commit and CI (full history, SARIF to code
   scanning). A custom rule covers Dispatch Core `hbl_live_`/`hbl_test_` tokens and
   credentials embedded in database URLs, which the default rules do not.
5. **Response**: rotation runbook; history rewrites only after rotation.

## Consequences

* New services must document their secrets in `docs/` and Terraform.
* Scanner false positives are handled with narrow allowlists or `.gitleaksignore`
  fingerprints reviewed by Security — not by disabling rules.
