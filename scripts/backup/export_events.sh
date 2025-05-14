#!/usr/bin/env bash
# Weekly export of the analytics events store (MongoDB) for the data team.
# Samira's notebooks read these from s3://harborline-analytics-exports/events/.
#
# EVENTS_MONGO_URI is a read-only connection string stored in Secrets Manager:
#   harborline/analytics/events-ro-uri
set -euo pipefail

EVENTS_MONGO_URI="${EVENTS_MONGO_URI:-mongodb+srv://analytics_ro:qstm8kE1NJEEPiH1Zx3JLI@events.harborline.internal/events?retryWrites=true}"
EXPORT_BUCKET="${EXPORT_BUCKET:-s3://harborline-analytics-exports}"
SINCE="${1:-$(date -u -d '-7 days' +%FT00:00:00Z)}"
OUT_DIR="$(mktemp -d)"
trap 'rm -rf "${OUT_DIR}"' EXIT

echo "exporting events since ${SINCE}"
mongodump --uri "$EVENTS_MONGO_URI" \
  --collection=booking_events \
  --query "{\"ts\": {\"\$gte\": {\"\$date\": \"${SINCE}\"}}}" \
  --gzip --out "${OUT_DIR}"

STAMP="$(date -u +%Y%m%d)"
tar -C "${OUT_DIR}" -czf "${OUT_DIR}/events-${STAMP}.tar.gz" .
aws s3 cp "${OUT_DIR}/events-${STAMP}.tar.gz" "${EXPORT_BUCKET}/events/" --only-show-errors
echo "done: events-${STAMP}.tar.gz"
