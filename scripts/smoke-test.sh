#!/usr/bin/env sh
set -eu

ENV_FILE="${1:-.env}"
if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE" >&2
  exit 1
fi

# EN: Do NOT `source` .env: valid Compose values may contain spaces and are not
# EN: necessarily valid shell syntax. Read only the non-secret keys needed here.
# RU: НЕ делай `source` для .env: допустимые Compose-значения могут содержать пробелы
# RU: и не обязаны быть валидным shell-синтаксисом. Читай только нужные несекретные ключи.
get_env() {
  key="$1"
  value=$(awk -v key="$key" '
    index($0, key "=") == 1 {
      sub("^[^=]*=", "", $0)
      value=$0
    }
    END { print value }
  ' "$ENV_FILE")
  if [ -z "$value" ]; then
    echo "Missing required $key in $ENV_FILE" >&2
    exit 1
  fi
  printf '%s' "$value"
}

SYNAPSE_PUBLIC_BASEURL=$(get_env SYNAPSE_PUBLIC_BASEURL)
MAS_PUBLIC_BASEURL=$(get_env MAS_PUBLIC_BASEURL)
ELEMENT_WEB_URL=$(get_env ELEMENT_WEB_URL)
LIVEKIT_JWT_SERVICE_URL=$(get_env LIVEKIT_JWT_SERVICE_URL)

check() {
  name="$1"
  url="$2"
  echo "[check] $name — $url"
  curl --fail --silent --show-error --max-time 15 "$url" >/dev/null
}

check "Synapse versions" "${SYNAPSE_PUBLIC_BASEURL%/}/_matrix/client/versions"
check "Client well-known" "${SYNAPSE_PUBLIC_BASEURL%/}/.well-known/matrix/client"
check "Server well-known" "${SYNAPSE_PUBLIC_BASEURL%/}/.well-known/matrix/server"
check "Federation version" "${SYNAPSE_PUBLIC_BASEURL%/}/_matrix/federation/v1/version"
check "MAS health" "${MAS_PUBLIC_BASEURL%/}/health"
check "MAS OIDC discovery" "${MAS_PUBLIC_BASEURL%/}/.well-known/openid-configuration"
check "Element config" "${ELEMENT_WEB_URL%/}/config.json"
check "RTC JWT health" "${LIVEKIT_JWT_SERVICE_URL%/}/healthz"

echo "All public HTTP smoke tests passed."
