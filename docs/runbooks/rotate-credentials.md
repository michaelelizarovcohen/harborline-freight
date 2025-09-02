# Runbook: Rotating a Leaked Credential

Owner: Security (Lena Vogel) · Last updated: 2025-08-28

> Rotation first, history cleanup second. A secret that reached a remote (GitHub,
> a fork, a CI log, a Slack message) must be treated as compromised even if the
> commit is removed later.

## 1. Triage (≤ 15 min)

1. Identify the credential type, owning system and environment (dev/staging/prod).
2. Find every location: run `gitleaks git . --log-opts="--all"` and
   `gitleaks dir .` and search CI logs. Record commit SHAs, branches and tags.
3. Open an incident ticket (`SEC-` project) and post in `#sec-help`.

## 2. Revoke & rotate

| System | How |
|---|---|
| AWS IAM access keys | Deactivate key in IAM, create new key for the role/user, update Secrets Manager, roll pods. Prefer replacing static keys with OIDC/assumed roles. |
| GitHub tokens | Revoke in Settings → Developer settings; check the org audit log for use. |
| Stripe | Roll the key in the Dashboard (choose an expiry for the old key if needed), update `harborline/<env>/stripe`. |
| Slack bot / webhooks | Regenerate in the Slack app config; webhook URLs cannot be rotated — delete and recreate. |
| SendGrid / Twilio | Delete the key and create a new scoped key. |
| Dispatch Core service tokens | `dispatchctl tokens revoke <token-id>` then `dispatchctl tokens issue --scope ...` (Ops Engineering on-call). |
| Database passwords | `ALTER ROLE ... PASSWORD ...` via the admin role; update Secrets Manager; restart consumers. |
| Google Maps keys | Rotate in Cloud Console; make sure referrer/app restrictions are set. |

## 3. Check for abuse

* AWS CloudTrail: `LookupEvents` filtered by the access key id, last 90 days.
* Stripe: Developers → Logs filtered by key.
* GitHub: org audit log; token last-used time.
* Dispatch Core: request logs by token id.

## 4. Clean up history (optional, coordinate first)

Only after rotation. Use `git filter-repo` on a fresh mirror clone, force-push all
refs, ask everyone to re-clone, and ask GitHub Support to purge cached views if the
repo is public. Remember tags, stale branches, forks and open PRs.

## 5. Prevent recurrence

* Add a test or allowlist if it was a false positive; add a custom rule if our
  scanner missed it.
* Write a short blameless postmortem.
