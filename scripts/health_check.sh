#!/usr/bin/env bash
set -euo pipefail

APP_URL="${APP_URL:-http://127.0.0.1:5000/health}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-10}"
SLEEP_SECONDS="${SLEEP_SECONDS:-3}"

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  echo "Health check attempt ${attempt}/${MAX_ATTEMPTS}: ${APP_URL}"
  if curl --fail --silent --show-error "$APP_URL"; then
    echo
    echo "Health check passed."
    exit 0
  fi
  sleep "$SLEEP_SECONDS"
done

echo "Health check failed after ${MAX_ATTEMPTS} attempts."
exit 1
