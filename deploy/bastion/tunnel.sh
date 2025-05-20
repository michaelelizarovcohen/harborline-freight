#!/usr/bin/env bash
# Port-forward staging RDS through the bastion.
#   ./deploy/bastion/tunnel.sh            -> localhost:15432
set -euo pipefail
BASTION_HOST="${BASTION_HOST:-bastion.staging.harborline.internal}"
DB_HOST="${DB_HOST:-staging-db.harborline.internal}"
KEY="$(dirname "$0")/hbl-bastion-ed25519"
chmod 600 "$KEY"
exec ssh -i "$KEY" -N -L 15432:"$DB_HOST":5432 ec2-user@"$BASTION_HOST"
