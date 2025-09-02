# Runbook: Security Incident Response (lightweight)

Owner: Security · Applies to: suspected compromise, credential exposure, data exposure

## Severity

| Sev | Examples | Response |
|---|---|---|
| SEV1 | Production credential exposed publicly, customer data exposed | Page on-call + Dana immediately |
| SEV2 | Staging credential exposed, internal-only exposure of prod credential | Same business day |
| SEV3 | Test-mode/sandbox credential exposed, scanner finding with no exposure | Next sprint |

## Roles

* **Incident lead** — coordinates, keeps the timeline (default: Lena Vogel).
* **Owner engineer** — rotates and fixes.
* **Comms** — Elise Marchetti for anything customer-facing.

## Checklist

- [ ] Open `SEC-` ticket; start a timeline (UTC timestamps).
- [ ] Contain: revoke/rotate credentials (see `rotate-credentials.md`).
- [ ] Preserve evidence before cleanup: scanner reports (JSON/SARIF), `git log`
      output, reflogs if relevant, CloudTrail exports.
- [ ] Assess impact: access logs for the affected system.
- [ ] Eradicate: remove from code, history (if warranted), CI logs, tickets.
- [ ] Recover: redeploy with new credentials, confirm health.
- [ ] Postmortem within 5 business days.
