# Engineering Onboarding

Welcome aboard! This checklist gets you from laptop to first PR.

## Day 1

1. Get added to the `harborline-freight` GitHub org and the `#eng`, `#deploys`,
   `#ops-alerts` and `#sec-help` Slack channels (ask Dana).
2. Install: Docker, Python 3.12, Node 20, `pre-commit`, `gitleaks`, AWS CLI v2,
   `kubectl`, Terraform 1.8.
3. Clone the monorepo and run:
   ```bash
   pre-commit install
   cp .env.example .env
   make up && make seed
   ```
4. Ask your buddy for the **local** values you need in `.env`. Shared test-mode
   credentials live in the 1Password vault *Engineering — Sandbox*. Never paste
   credentials in Slack, tickets, notebooks or commit messages.

## Accessing staging

* AWS: SSO via `aws sso login --profile harborline-staging` (read-only by default).
* Database: there is **no** direct access. Use the bastion tunnel helper in
  `deploy/` (opens `localhost:15432`) with your SSO session and the read-only
  role. Don't point docker compose at staging.
* Kubernetes: `aws eks update-kubeconfig --name harborline-staging --profile harborline-staging`.

## Conventions

* Branches: `feature/<topic>`, `fix/<topic>`, `infra/<topic>`. Squash or merge commits
  are both fine; keep history readable.
* Commit messages: imperative mood, reference the ticket (`HBL-123`).
* Hotfixes are cut from the release tag, tagged `vX.Y.Z`, then cherry-picked to `main`.
* Tests: `make test`. CI must be green before merge.

## If you leak a credential

It happens. Tell `#sec-help` immediately, then follow
[the rotation runbook](runbooks/rotate-credentials.md). Deleting the file in a new
commit is **not** enough — the value stays in git history.
