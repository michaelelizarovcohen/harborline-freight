# Support bundles — DO NOT COMMIT

`scripts/support_bundle.sh` (on-call tooling) collects config, logs and env
dumps from a pod into a `.zip` so we can attach it to a vendor ticket.

**Bundles contain live configuration, including credentials.** They must be
uploaded to the `hbl-support-bundles` S3 bucket (30-day expiry) and shared via
presigned URL — never committed to git, pasted in Slack, or attached to Linear.

This folder only exists so the path in old runbooks still resolves. `*.zip`
and `*.tar.gz` under `deploy/support-bundles/` are in `.gitignore`.

If you committed one by accident: tell `#security` immediately. Deleting the
file in a new commit does **not** remove it from history; the credentials
inside must be rotated.
