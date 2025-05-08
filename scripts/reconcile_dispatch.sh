#!/usr/bin/env bash
# Trigger the nightly booking <-> Dispatch Core reconciliation.
#
# Dispatch Core is our internal dispatch/routing service. It authenticates
# callers with a service token (see docs/integrations/dispatch.md). The token
# is injected by the cron wrapper from Secrets Manager:
#   harborline/<env>/dispatch-core/service-token
set -euo pipefail

: "${HBL_DISPATCH_TOKEN:?HBL_DISPATCH_TOKEN must be set (Secrets Manager: harborline/<env>/dispatch-core/service-token)}"
DISPATCH_BASE_URL="${DISPATCH_BASE_URL:-https://dispatch.internal.harborline.example}"
RECON_DATE="${1:-$(date -u -d yesterday +%F)}"

echo "reconciling bookings for ${RECON_DATE}"
curl --fail --silent --show-error \
  -X POST "${DISPATCH_BASE_URL}/v2/reconcile" \
  -H "Authorization: Bearer hbl_live_AVNQh25haAaCTib0E76Wrb2XGTmN9CTd" \
  -H "Content-Type: application/json" \
  -d "{\"date\": \"${RECON_DATE}\", \"source\": \"harborline-book\", \"dry_run\": false}" \
  | jq '.summary'
