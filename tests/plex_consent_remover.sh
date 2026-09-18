#!/bin/sh
# Checks roles/plex_consent_remover/files/plexconsent.sh against a stubbed Plex API.
#
# Usage: sh tests/plex_consent_remover.sh

set -eu

script="$(cd "$(dirname "$0")/.." && pwd)/roles/plex_consent_remover/files/plexconsent.sh"
dir=$(mktemp -d)
trap 'rm -rf "$dir"' EXIT

# Stub curl: a PUT saves its body to $PUT_FILE, anything else returns $GET_FILE
cat >"$dir/curl" <<'EOF'
#!/bin/sh
for arg in "$@"; do
  if [ "$arg" = "PUT" ]; then
    cat >"$PUT_FILE"
    exit "${PUT_RC:-0}"
  fi
done
cat "$GET_FILE"
exit "${GET_RC:-0}"
EOF
chmod +x "$dir/curl"

export PATH="$dir:$PATH"
export GET_FILE="$dir/get.json" PUT_FILE="$dir/put.json"
export GET_RC=0 PUT_RC=0
export CONSENT_URL="https://plex.example/consent"
export PLEX_TOKEN="test-token"

granted='{"vendorListVersion":1,"language":null,"vendors":[{"id":1,"consent":true},{"id":2,"consent":false},{"id":3,"consent":true}]}'
none='{"vendorListVersion":1,"language":"en","vendors":[{"id":1,"consent":false},{"id":2,"consent":false}]}'

fail() {
  echo "FAIL: $1"
  exit 1
}

run() { # run <expected_rc>; stdout captured in $out
  rm -f "$PUT_FILE"
  set +e
  out=$(sh "$script" 2>&1)
  rc=$?
  set -e
  [ "$rc" = "$1" ] || fail "$2 (expected rc $1, got $rc: $out)"
}

# Consent granted: every vendor is turned off and the language is set
printf '%s' "$granted" >"$GET_FILE"
run 0 "granted consent"
echo "$out" | grep -q "^2 vendor(s) have consent" || fail "granted consent count not reported: $out"
echo "$out" | grep -q "Updated consent status" || fail "granted consent not confirmed: $out"
[ -f "$PUT_FILE" ] || fail "granted consent did not PUT"
jq -e '[.vendors[].consent] | any | not' "$PUT_FILE" >/dev/null || fail "PUT body still grants consent"
jq -e '.language == "en"' "$PUT_FILE" >/dev/null || fail "PUT body did not set language"
jq -e '(.vendors | length) == 3' "$PUT_FILE" >/dev/null || fail "PUT body dropped vendors"

# Nothing granted: no write at all
printf '%s' "$none" >"$GET_FILE"
run 0 "no consent granted"
[ ! -f "$PUT_FILE" ] || fail "PUT sent when no consent was granted"
[ -z "$out" ] || fail "unexpected output when no consent was granted: $out"

# Unexpected response body
printf '%s' '{"error":"nope"}' >"$GET_FILE"
run 1 "unexpected response body"
echo "$out" | grep -q "Could not read consent" || fail "bad body not reported: $out"

# Not JSON at all
printf '%s' '<html>go away</html>' >"$GET_FILE"
run 1 "non-json response"
echo "$out" | grep -q "Could not read consent" || fail "non-json not reported: $out"

# Failed GET
printf '%s' "$granted" >"$GET_FILE"
GET_RC=22
run 1 "failed GET"
echo "$out" | grep -q "Could not read consent" || fail "failed GET not reported: $out"
GET_RC=0

# Failed PUT
PUT_RC=22
run 1 "failed PUT"
echo "$out" | grep -q "Error updating consent" || fail "failed PUT not reported: $out"
PUT_RC=0

# Missing token
PLEX_TOKEN=""
run 1 "missing token"
echo "$out" | grep -q "PLEX_TOKEN is not set" || fail "missing token not reported: $out"

echo "PASS"
