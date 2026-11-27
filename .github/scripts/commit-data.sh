#!/usr/bin/env bash
# Commit one context's scrape on a chore branch and merge it into the base
# branch through a pull request with auto-merge.
#
# data/manifest.json and data/feed.xml aggregate every context on disk, so
# they are never merged as text: they are regenerated after each rebase and
# folded into the same commit.
set -euo pipefail

context="$1"
base="${GITHUB_REF_NAME:-master}"
repo="${GITHUB_REPOSITORY:-stackin-io/data-source}"
branch="chore/scrape-${context//\//-}-$(date -u +%Y%m%d-%H%M)"
title="chore(data): scheduled ${context} scrape $(date -u +%Y-%m-%dT%H:%MZ)"
run_url="${BUILD_URL:-${GITHUB_SERVER_URL:-https://github.com}/${repo}/actions/runs/${GITHUB_RUN_ID:-}}"

git config user.name "stackin-bot"
git config user.email "bot@stackin.io"

git add "data/${context}"
if git diff --cached --quiet; then
  echo "No new files for ${context}"
  exit 0
fi
git commit -q -m "${title}"

publications="$(mktemp)"
poetry run data-source new-publications "${context}" --out ./data --to "${publications}" ||
  echo "::warning::Could not list the new publications of ${context}"

announce() {
  .github/scripts/notify-publications.sh "${publications}" || true
}

rebase_on_base() {
  git fetch -q origin "${base}"
  git checkout HEAD~1 -- data/manifest.json data/feed.xml
  git commit -q --amend --no-edit --allow-empty
  git rebase -q "origin/${base}"
}

refresh_index() {
  poetry run data-source rebuild-index --out ./data
  git add data/manifest.json data/feed.xml
  if ! git diff --cached --quiet; then
    git commit -q --amend --no-edit
  fi
}

run_checks() {
  if [ "${GITHUB_ACTIONS:-}" != "true" ]; then
    return 0
  fi
  gh workflow run gitflow.yml --repo "${repo}" --ref "${branch}" -f base="${base}"
  gh workflow run conventional-commit.yml --repo "${repo}" --ref "${branch}" -f base="${base}"
}

request_merge() {
  if gh pr merge "${pr}" --repo "${repo}" --squash --auto; then
    return 0
  fi
  gh pr merge "${pr}" --repo "${repo}" --squash || echo "Merge not possible yet for #${pr}"
}

await_merge() {
  local state mergeable
  for _ in $(seq 1 40); do
    state="" mergeable=""
    read -r state mergeable < <(gh pr view "${pr}" --repo "${repo}" --json state,mergeable --jq '"\(.state) \(.mergeable)"') || true
    case "${state}" in
      MERGED) echo merged; return 0 ;;
      CLOSED) echo closed; return 0 ;;
    esac
    if [ "${mergeable}" = "CONFLICTING" ]; then
      echo conflicting
      return 0
    fi
    sleep 15
  done
  echo "not merged after 10 minutes"
}

pr=""
for attempt in 1 2 3; do
  rebase_on_base
  if [ "$(git rev-parse HEAD)" = "$(git rev-parse "origin/${base}")" ]; then
    echo "Nothing new for ${context} on ${base}"
    if [ -n "${pr}" ]; then
      gh pr close "${pr}" --repo "${repo}" --delete-branch
    else
      git push -q origin --delete "${branch}" 2>/dev/null || true
    fi
    exit 0
  fi
  refresh_index
  git push -q --force origin "HEAD:refs/heads/${branch}"

  if [ -z "${pr}" ]; then
    if ! url="$(gh pr create --repo "${repo}" --base "${base}" --head "${branch}" --title "${title}" \
      --body "Scheduled scrape of \`data/${context}\`, opened by ${run_url}. Merges itself once the required checks pass.")"; then
      echo "::warning::Could not open a pull request; pushing to ${base} directly, which only an unprotected ${base} accepts"
      if git push -q origin "HEAD:${base}"; then
        git push -q origin --delete "${branch}" 2>/dev/null || true
        announce
        exit 0
      fi
      echo "Push to ${base} rejected (attempt ${attempt})"
      continue
    fi
    pr="${url##*/}"
    echo "Opened ${url}"
  fi

  run_checks
  request_merge
  outcome="$(await_merge)"

  case "${outcome}" in
    merged)
      git push -q origin --delete "${branch}" 2>/dev/null || true
      echo "Merged #${pr} into ${base}"
      announce
      exit 0
      ;;
    conflicting)
      echo "#${pr} conflicts with ${base} (attempt ${attempt}), rebasing again"
      ;;
    *)
      echo "#${pr} ${outcome}"
      exit 1
      ;;
  esac
done

echo "#${pr} still conflicts with ${base} after 3 attempts"
exit 1
