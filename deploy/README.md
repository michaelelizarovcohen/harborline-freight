# deploy/

Deployment helpers used by CI (`.github/workflows/deploy.yml`) and by the
on-call engineer for manual rollouts/rollbacks.

| Path | What it is |
|---|---|
| `deploy.sh` | Renders the kustomize overlay for an environment, pins image tags and applies it |
| `nginx/nginx.conf` | Config baked into the `harborline/web` image |
| `runner/bootstrap.sh` | User-data for self-hosted GitHub Actions runners (EC2) |
| `helm/values-staging.yaml` | Values for the observability chart (OTel collector + Sentry relay) |
| `bastion/` | SSM-based tunnel to the staging database — no SSH keys |
| `support-bundles/` | **Do not commit bundles here.** See the README in that folder. |

## Manual deploy

```bash
aws sso login --profile hbl-shared
aws eks update-kubeconfig --name hbl-staging --region us-west-2
./deploy/deploy.sh staging 3f9c2e1a7b4d
```

## Rollback

```bash
kubectl -n harborline rollout undo deployment/harborline-api
# or redeploy a previous tag
./deploy/deploy.sh staging <previous-sha>
```

Credentials for every environment come from AWS Secrets Manager via
External Secrets (see `infra/k8s/base/externalsecret.yaml`). If you find
yourself pasting a key into a file in this folder, stop and ask in `#platform`.
