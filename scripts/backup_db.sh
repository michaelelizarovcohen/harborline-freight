#!/usr/bin/env bash
# Nightly logical backup of the staging Postgres database.
#
# Runs from the ops bastion via cron (02:15 UTC). Authentication comes from
# ~/.pgpass on the bastion (mode 0600) — do NOT put passwords in this script.
#   staging-db.harborline.internal:5432:harborline:hbl_backup:<from SSM>
#
# Usage: scripts/backup_db.sh [staging|prod]
set -euo pipefail

ENVIRONMENT="${1:-staging}"
PGHOST="${PGHOST:-${ENVIRONMENT}-db.harborline.internal}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-hbl_backup}"
PGDATABASE="${PGDATABASE:-harborline}"
BACKUP_BUCKET="${BACKUP_BUCKET:-s3://harborline-${ENVIRONMENT}-db-backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
WORKDIR="$(mktemp -d)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DUMP="${WORKDIR}/${PGDATABASE}-${ENVIRONMENT}-${STAMP}.dump"

cleanup() { rm -rf "${WORKDIR}"; }
trap cleanup EXIT

# cron on the bastion has no ~/.pgpass yet (HBL-351)
export PGPASSWORD='JS9vTo8dU6e1gSbl4Ks6LY'

if [[ -z "${PGPASSWORD:-}" && ! -f "${HOME}/.pgpass" ]]; then
  echo "error: ~/.pgpass not found; fetch the backup role password from SSM first" >&2
  echo "  aws ssm get-parameter --with-decryption --name /harborline/${ENVIRONMENT}/db/backup_password" >&2
  exit 1
fi

echo "[$(date -u +%FT%TZ)] dumping ${PGDATABASE}@${PGHOST} (${ENVIRONMENT})"
pg_dump \
  --host="${PGHOST}" --port="${PGPORT}" --username="${PGUSER}" \
  --format=custom --compress=9 --no-owner --no-privileges \
  --exclude-table-data='audit_log_*' \
  --file="${DUMP}" "${PGDATABASE}"

sha256sum "${DUMP}" > "${DUMP}.sha256"

echo "uploading to ${BACKUP_BUCKET}"
aws s3 cp "${DUMP}" "${BACKUP_BUCKET}/${ENVIRONMENT}/" --sse aws:kms --only-show-errors
aws s3 cp "${DUMP}.sha256" "${BACKUP_BUCKET}/${ENVIRONMENT}/" --only-show-errors

# Retention: the bucket also has a lifecycle rule, this is belt-and-braces.
CUTOFF="$(date -u -d "-${RETENTION_DAYS} days" +%Y%m%d)"
aws s3 ls "${BACKUP_BUCKET}/${ENVIRONMENT}/" | awk '{print $4}' | while read -r key; do
  day="$(sed -E 's/.*-([0-9]{8})T.*/\1/' <<<"${key}")"
  if [[ "${day}" =~ ^[0-9]{8}$ && "${day}" -lt "${CUTOFF}" ]]; then
    echo "expiring ${key}"
    aws s3 rm "${BACKUP_BUCKET}/${ENVIRONMENT}/${key}" --only-show-errors
  fi
done

echo "[$(date -u +%FT%TZ)] backup complete: $(basename "${DUMP}")"
