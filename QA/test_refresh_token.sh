#!/usr/bin/env bash
# Live test of the back-end refresh tokens: /token, /token/refresh, /token/revoke (back-end >= v3.3.8).
#
# Usage: [API=...] [EMAIL=...] [PASSWORD=...] QA/test_refresh_token.sh [options]
#   --expiry       wait for the access token expiry (expires_in), then check it is refused and refresh works
#   --families N   N = MAX_REFRESH_FAMILIES of the back-end: N+1 logins, the first one must be revoked
#   --legacy on|off  check deprecated /login token is accepted (on) or refused (off), as LEGACY_TOKENS
#
# Email and password are prompted, Enter keeps the ordinary user of the back-end test DB (user / zero6).
# The same scenario runs in the back-end tests: QA/py/tests/test_users.py::test_ordinary_user_refresh_token.
# Each /token is a new login: on a real account, older sessions beyond MAX_REFRESH_FAMILIES get revoked.
# Prefer a test account. Tokens created here are revoked at the end.
# Needs curl and jq. Self-signed certificates are accepted (-k).

API=${API:-https://ecotaxa-dev.imev-mer.fr:5003/api}
CURL=(curl -sk -m 30)

do_expiry=0
families=0
legacy=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --expiry) do_expiry=1 ;;
    --families) families=$2; shift ;;
    --legacy) legacy=$2; shift ;;
    -h|--help) sed -n '2,/^$/p' "$0"; exit 0 ;;
    *) echo "Unknown option $1, see --help"; exit 2 ;;
  esac
  shift
done

command -v jq >/dev/null || { echo "jq is needed"; exit 2; }
# Default: ordinary user of the back-end test DB (ecotaxa_back QA/py/pg_files/data_load.sql)
DEFAULT_EMAIL=user
DEFAULT_PASSWORD=zero6
if [[ -z ${EMAIL:-} ]]; then
  read -rp "Email [$DEFAULT_EMAIL]: " EMAIL
  EMAIL=${EMAIL:-$DEFAULT_EMAIL}
fi
if [[ -z ${PASSWORD:-} ]]; then
  read -rsp "Password [test DB default]: " PASSWORD
  echo
  PASSWORD=${PASSWORD:-$DEFAULT_PASSWORD}
fi

TMP=$(mktemp -d)
CREATED=()
ok=0
ko=0

cleanup() {
  for a_rt in "${CREATED[@]}"; do
    revoke "$a_rt" >/dev/null
  done
  rm -rf "$TMP"
}
trap cleanup EXIT

# req OUT_FILE CURL_ARGS... : prints the HTTP code, body in OUT_FILE
req() {
  local out=$1
  shift
  "${CURL[@]}" -o "$out" -w '%{http_code}' "$@"
}

rt_json() {
  jq -nc --arg rt "$1" '{refresh_token: $rt}'
}

# login OUT_FILE
login() {
  req "$1" -X POST "$API/token" --data-urlencode "username=$EMAIL" --data-urlencode "password=$PASSWORD"
}

# refresh OUT_FILE REFRESH_TOKEN
refresh() {
  req "$1" -X POST "$API/token/refresh" -H 'Content-Type: application/json' -d "$(rt_json "$2")"
}

# revoke REFRESH_TOKEN
revoke() {
  req "$TMP/revoke.json" -X POST "$API/token/revoke" -H 'Content-Type: application/json' -d "$(rt_json "$1")"
}

# me ACCESS_TOKEN
me() {
  req "$TMP/me.json" -H "Authorization: Bearer $1" "$API/users/me"
}

# check LABEL EXPECTED ACTUAL
check() {
  if [[ $3 == "$2" ]]; then
    echo "  OK    $1 ($3)"
    ok=$((ok + 1))
  else
    echo "  FAIL  $1: expected $2, got $3"
    ko=$((ko + 1))
  fi
}

field() {
  jq -r ".$2 // empty" "$1"
}

# new_login PREFIX : sets ${PREFIX}_AT and ${PREFIX}_RT, returns 1 if login failed
new_login() {
  local code
  code=$(login "$TMP/$1.json")
  check "login /token" 200 "$code"
  if [[ $code != 200 ]]; then
    cat "$TMP/$1.json"
    echo
    return 1
  fi
  printf -v "${1}_AT" '%s' "$(field "$TMP/$1.json" access_token)"
  printf -v "${1}_RT" '%s' "$(field "$TMP/$1.json" refresh_token)"
  CREATED+=("$(field "$TMP/$1.json" refresh_token)")
}

echo "API: $API"
status=$(req "$TMP/status.json" "$API/status")
if [[ $status != 200 ]]; then
  echo "API not reachable ($status), check API"
  exit 2
fi

echo "1. Login"
new_login t1 || exit 1
expires_in=$(field "$TMP/t1.json" expires_in)
echo "        token_type=$(field "$TMP/t1.json" token_type) expires_in=${expires_in}s"
check "refresh_token present" yes "$([[ -n $t1_RT ]] && echo yes || echo no)"
check "access token accepted" 200 "$(me "$t1_AT")"
echo "        user: $(field "$TMP/me.json" email)"
check "bad access token refused" 401 "$(me "not-a-token")"

echo "2. Rotation"
code=$(refresh "$TMP/t2.json" "$t1_RT")
check "refresh" 200 "$code"
t2_AT=$(field "$TMP/t2.json" access_token)
t2_RT=$(field "$TMP/t2.json" refresh_token)
CREATED+=("$t2_RT")
check "new refresh token differs" yes "$([[ -n $t2_RT && $t2_RT != "$t1_RT" ]] && echo yes || echo no)"
check "new access token accepted" 200 "$(me "$t2_AT")"

echo "3. Replay of a rotated refresh token"
check "old refresh token refused" 401 "$(refresh "$TMP/r.json" "$t1_RT")"
check "whole session revoked, new refresh token refused too" 401 "$(refresh "$TMP/r.json" "$t2_RT")"

echo "4. Logout"
new_login t3 || exit 1
check "revoke" 200 "$(revoke "$t3_RT")"
check "revoked refresh token refused" 401 "$(refresh "$TMP/r.json" "$t3_RT")"
check "revoke of an unknown token succeeds" 200 "$(revoke "not-a-token")"
check "refresh of an unknown token refused" 401 "$(refresh "$TMP/r.json" "not-a-token")"

if [[ -n $legacy ]]; then
  echo "5. Deprecated /login, LEGACY_TOKENS=$legacy"
  code=$(req "$TMP/legacy.json" -X POST "$API/login" -H 'Content-Type: application/json' \
    -d "$(jq -nc --arg u "$EMAIL" --arg p "$PASSWORD" '{username: $u, password: $p}')")
  check "/login" 200 "$code"
  legacy_token=$(jq -r '.' "$TMP/legacy.json")
  if [[ $legacy == on ]]; then
    check "/login token accepted" 200 "$(me "$legacy_token")"
  else
    check "/login token refused" 401 "$(me "$legacy_token")"
  fi
fi

if [[ $families -gt 0 ]]; then
  echo "6. Max $families sessions: $((families + 1)) logins"
  first_rt=""
  last_rt=""
  for ((i = 0; i <= families; i++)); do
    new_login "f$i" >/dev/null || { echo "  FAIL  login $i"; ko=$((ko + 1)); break; }
    a_rt_var="f${i}_RT"
    [[ -z $first_rt ]] && first_rt=${!a_rt_var}
    last_rt=${!a_rt_var}
  done
  check "oldest session revoked" 401 "$(refresh "$TMP/r.json" "$first_rt")"
  code=$(refresh "$TMP/f_last.json" "$last_rt")
  check "most recent session still valid" 200 "$code"
  CREATED+=("$(field "$TMP/f_last.json" refresh_token)")
fi

if [[ $do_expiry == 1 ]]; then
  echo "7. Access token expiry"
  new_login t4 || exit 1
  wait_s=$((expires_in + 5))
  echo "        waiting ${wait_s}s (ACCESS_TOKEN_TTL + 5s)..."
  sleep "$wait_s"
  check "expired access token refused" 401 "$(me "$t4_AT")"
  code=$(refresh "$TMP/t5.json" "$t4_RT")
  check "refresh after expiry" 200 "$code"
  CREATED+=("$(field "$TMP/t5.json" refresh_token)")
  check "new access token accepted" 200 "$(me "$(field "$TMP/t5.json" access_token)")"
fi

echo
echo "Passed: $ok, failed: $ko"
[[ $ko == 0 ]]
