#!/usr/bin/env bash
set -uo pipefail

file="$1"

if [[ ! -s "${file}" ]] || [[ "$(jq 'length' "${file}" 2>/dev/null || echo 0)" = "0" ]]; then
  echo "No new publications to announce"
  exit 0
fi

if [[ -z "${DISCORD_WEBHOOK_URL:-}" ]]; then
  echo "::warning::DISCORD_WEBHOOK_URL is not set; new publications not announced"
  exit 0
fi

jq -c '.[]' "${file}" | while read -r item; do
  content="$(jq -r '
    ":page_facing_up: **\(.kind)** — \(.title)"
    + (if .environment then "\nAmbiente: \(.environment)" else "" end)
    + (if .published_at != "" then "\nPublicado em: \(.published_at)" else "" end)
    + (if .folder_url != "" then "\nEspelho: <\(.folder_url)>" else "" end)
    + (if .source_url != "" then "\nOriginal: <\(.source_url)>" else "" end)
  ' <<<"${item}")"
  payload="$(jq -n --arg content "${content}" '{content: $content, allowed_mentions: {parse: []}}')"
  if printf 'url = "%s"\n' "${DISCORD_WEBHOOK_URL}" |
    curl --config - --fail --silent --show-error --max-time 30 \
      -H "Content-Type: application/json" \
      -d "${payload}" >/dev/null; then
    echo "Announced: $(jq -r '.title' <<<"${item}")"
  else
    echo "::warning::Discord refused the announcement of $(jq -r '.title' <<<"${item}")"
  fi
  sleep 1
done
