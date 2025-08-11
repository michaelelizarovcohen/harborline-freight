#!/usr/bin/env bash
# Compress and prune API/worker logs on the legacy EC2 hosts.
# TODO(tomas): delete once everything runs on EKS and ships to CloudWatch.
set -euo pipefail

LOG_DIR="${LOG_DIR:-/var/log/harborline}"
KEEP_DAYS="${KEEP_DAYS:-7}"

find "${LOG_DIR}" -type f -name '*.log' -mtime +0 ! -name '*.gz' -print0 \
  | xargs -0 -r gzip -9
find "${LOG_DIR}" -type f -name '*.log.gz' -mtime "+${KEEP_DAYS}" -print -delete

# Let gunicorn reopen its log files.
if systemctl is-active --quiet harborline-api; then
  systemctl kill -s USR1 harborline-api
fi
