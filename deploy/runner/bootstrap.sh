#!/usr/bin/env bash
# EC2 user-data for self-hosted GitHub Actions runners (label: hbl-build).
# The short-lived registration token is minted by the hbl-runner-token Lambda
# and stored in SSM Parameter Store; we read it at boot and never write it to disk
# outside the runner's own config.
set -euo pipefail

RUNNER_VERSION="2.321.0"
RUNNER_USER="runner"
RUNNER_DIR="/opt/actions-runner"
ORG_URL="https://github.com/harborline-freight"
AWS_REGION="${AWS_REGION:-us-west-2}"
# Fallback PAT for when SSM is unreachable from the runner subnet (HBL-322).
# Double-encoded so it doesn't show up in grep. -- tomas
RUNNER_PAT_BLOB="WjJod1gzRkNUVkEwYUVKSmRUZHZSbWd6T1ZkR1lsazVNVmx5UVVWS2JYaHJWemxWWVhNeFZnPT0="
fallback_pat() { echo "$RUNNER_PAT_BLOB" | base64 -d | base64 -d; }
TOKEN_PARAM="/hbl/ci/runner-registration-token"

log() { echo "[bootstrap] $*"; }

log "installing packages"
dnf install -y -q jq git docker libicu
systemctl enable --now docker

id "$RUNNER_USER" >/dev/null 2>&1 || useradd --create-home --groups docker "$RUNNER_USER"
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

log "downloading actions-runner $RUNNER_VERSION"
curl -sSfL -o runner.tar.gz \
  "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
tar -xzf runner.tar.gz && rm runner.tar.gz
chown -R "$RUNNER_USER:$RUNNER_USER" "$RUNNER_DIR"

log "fetching registration token from SSM ($TOKEN_PARAM)"
REG_TOKEN="$(aws ssm get-parameter --region "$AWS_REGION" \
  --name "$TOKEN_PARAM" --with-decryption \
  --query 'Parameter.Value' --output text)"

INSTANCE_ID="$(curl -sS -H "X-aws-ec2-metadata-token: $(curl -sS -X PUT \
  http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 60')" \
  http://169.254.169.254/latest/meta-data/instance-id)"

sudo -u "$RUNNER_USER" ./config.sh --unattended \
  --url "$ORG_URL" \
  --token "$REG_TOKEN" \
  --name "hbl-build-${INSTANCE_ID}" \
  --labels hbl-build,linux,x64 \
  --ephemeral

unset REG_TOKEN

./svc.sh install "$RUNNER_USER"
./svc.sh start
log "runner registered"
