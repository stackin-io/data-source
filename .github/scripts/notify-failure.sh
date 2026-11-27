#!/usr/bin/env bash
# Post a failed scrape to Discord.
#
# The webhook comes from the environment, never from the command line, so it
# does not show in the job log. Without it the script warns and exits 0: a
# missing secret must not hide the scrape failure behind a second one.
set -euo pipefail

if [[ -z "${DISCORD_WEBHOOK_URL:-}" ]]; then
  echo "::warning::DISCORD_WEBHOOK_URL is not set; no failure alert sent"
  exit 0
fi

if [[ -n "${BUILD_URL:-}" ]]; then
  run_url="${BUILD_URL}"
  content=":red_circle: **${JOB_NAME}** failed on \`${GITHUB_REF_NAME:-master}\` (build #${BUILD_NUMBER})
${run_url}"
else
  run_url="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
  content=":red_circle: **${GITHUB_WORKFLOW}** failed on \`${GITHUB_REF_NAME}\` (attempt ${GITHUB_RUN_ATTEMPT:-1})
${run_url}"
fi

payload="$(jq -n --arg content "${content}" '{content: $content, allowed_mentions: {parse: []}}')"

# The URL goes in through a curl config on stdin, so it stays out of argv too.
printf 'url = "%s"\n' "${DISCORD_WEBHOOK_URL}" |
  curl --config - --fail --silent --show-error --max-time 30 \
    -H "Content-Type: application/json" \
    -d "${payload}" >/dev/null

echo "Failure alert sent for ${run_url}"
