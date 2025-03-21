# Harborline Freight — Infrastructure

Owner: Platform / DevOps (Tomás Ferreira, `#platform` on Slack)

Everything that runs Harborline in AWS (`us-west-2`) lives here.

```
infra/
├── terraform/
│   ├── modules/rds-postgres/   # reusable RDS PostgreSQL 16 module
│   └── staging/                # staging account root module
└── k8s/
    ├── base/                   # kustomize base for api / worker / web
    └── overlays/
        ├── staging/            # EKS cluster hbl-staging
        └── production/         # EKS cluster hbl-prod
```

## Accounts

| Environment | AWS account alias       | EKS cluster   | Notes                              |
|-------------|-------------------------|---------------|------------------------------------|
| staging     | `harborline-staging`    | `hbl-staging` | Terraform in `terraform/staging`   |
| production  | `harborline-production` | `hbl-prod`    | Terraform lives in `infra-prod` repo (restricted) |

## Terraform

We never use static IAM user keys for Terraform. Engineers authenticate with
AWS IAM Identity Center (`aws sso login --profile hbl-shared`) and the provider
assumes `TerraformDeployer` in the target account.

```bash
cd infra/terraform/staging
aws sso login --profile hbl-shared
export AWS_PROFILE=hbl-shared
export TF_VAR_db_password="$(aws secretsmanager get-secret-value \
    --secret-id hbl/staging/rds-master --query SecretString --output text)"
terraform init
terraform plan -out tfplan
```

`terraform.tfvars` is gitignored. Copy `terraform.tfvars.example` if you need
local overrides — **never** put passwords or keys in tfvars that get committed.

## Kubernetes

Manifests are plain kustomize. Secrets are **not** stored in git: the
`ExternalSecret` in `k8s/base/externalsecret.yaml` syncs
`hbl/<env>/api` from AWS Secrets Manager into the `harborline-api` Secret.

```bash
kubectl kustomize infra/k8s/overlays/staging | less
../deploy/deploy.sh staging <image-tag>
```

## TODO
- [ ] Move ElastiCache + Amazon MQ into Terraform (still click-ops from the 2024 migration).
- [ ] Production overlay HPA tuning after peak season.
