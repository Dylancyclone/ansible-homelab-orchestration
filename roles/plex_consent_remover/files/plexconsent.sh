#!/bin/sh
# Revokes consent for Plex to share your data with advertising vendors.
#
# The API calls come from https://github.com/cyberbrix/plexconsentremover, rewritten to run in a
# container: POSIX sh so a plain Alpine image suffices, token from the environment so the file holds
# no secret, and a single pass so the caller controls the schedule. Upstream changes are not tracked.

TOKEN="${PLEX_TOKEN:-}"
CONSENT_URL="${CONSENT_URL:-https://plex.tv/api/v2/user/consent}"

if [ -z "$TOKEN" ]; then
  echo "PLEX_TOKEN is not set"
  exit 1
fi

command -v jq >/dev/null 2>&1 || apk add --no-cache curl jq >/dev/null

if ! consent=$(curl -sf -H "X-Plex-Token: $TOKEN" -H "Accept: application/json" "$CONSENT_URL") ||
  ! printf '%s' "$consent" | jq -e 'has("vendorListVersion")' >/dev/null 2>&1; then
  echo "Could not read consent from Plex.tv"
  exit 1
fi

printf '%s' "$consent" | jq -e '[.vendors[].consent] | any' >/dev/null || exit 0

granted=$(printf '%s' "$consent" | jq '[.vendors[] | select(.consent)] | length')
echo "$granted vendor(s) have consent to gather your info from Plex. Removing consent."

if printf '%s' "$consent" | jq '.language = "en" | .vendors[].consent = false' |
  curl -sf -X PUT -H "X-Plex-Token: $TOKEN" -H "Accept: application/json" \
    -H "Content-Type: application/json" --data @- "$CONSENT_URL" >/dev/null; then
  echo "Updated consent status"
else
  echo "Error updating consent on Plex.tv"
  exit 1
fi
