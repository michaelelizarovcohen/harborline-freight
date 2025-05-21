#!/usr/bin/env bash
# Open a local port-forward to the staging RDS instance through the SSM bastion.
# No SSH keys, no open ports: uses AWS Systems Manager Session Manager.
#
# Usage: deploy/bastion/tunnel.sh [local-port]
# Then: psql "host=localhost port=15432 dbname=harborline user=$USER sslmode=require"
#       (IAM auth token or your personal DB role password from 1Password)
set -euo pipefail

LOCAL_PORT="${1:-15432}"
AWS_REGION="${AWS_REGION:-us-west-2}"
DB_HOST="staging-db.harborline.internal"

command -v session-manager-plugin >/dev/null || {
  echo "Install the AWS Session Manager plugin first: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html" >&2
  exit 1
}

BASTION_ID="$(aws ec2 describe-instances --region "$AWS_REGION" \
  --filters "Name=tag:Name,Values=hbl-staging-bastion" "Name=instance-state-name,Values=running" \
  --query 'Reservations[0].Instances[0].InstanceId' --output text)"

if [[ -z "$BASTION_ID" || "$BASTION_ID" == "None" ]]; then
  echo "No running hbl-staging-bastion instance found (did you aws sso login?)" >&2
  exit 1
fi

echo "Forwarding localhost:$LOCAL_PORT -> $DB_HOST:5432 via $BASTION_ID (Ctrl-C to stop)"
exec aws ssm start-session --region "$AWS_REGION" \
  --target "$BASTION_ID" \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters "host=$DB_HOST,portNumber=5432,localPortNumber=$LOCAL_PORT"
