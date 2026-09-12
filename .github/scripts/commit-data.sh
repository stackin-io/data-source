#!/usr/bin/env bash
# Commit one context's scrape and push it, surviving a push from another
# context that landed meanwhile.
#
# The two root files, data/manifest.json and data/feed.xml, aggregate every
# context on disk. Two workflows committing them as text will conflict on
# the first concurrent run — which is how the svrs scrape of 2026-09-12
# died in `git pull --rebase`. So they are never merged: the context's own
# files are committed and rebased, then the root files are regenerated from
# whatever is on disk after the rebase and folded into the same commit.
set -euo pipefail

context="$1"
branch="${GITHUB_REF_NAME:-master}"
stamp="$(date -u +%Y-%m-%d)"

git config user.name "stackin-bot"
git config user.email "bot@stackin.io"

git add "data/${context}"
if git diff --cached --quiet; then
  echo "No new files for ${context}"
  exit 0
fi
git commit -m "DATA(${context}): Scheduled scrape ${stamp}"

for attempt in 1 2 3; do
  git fetch origin "${branch}"
  git checkout -- data/manifest.json data/feed.xml
  git rebase "origin/${branch}"
  poetry run data-source rebuild-index --out ./data
  git add data/manifest.json data/feed.xml
  if ! git diff --cached --quiet; then
    git commit --amend --no-edit
  fi
  if git push origin "HEAD:${branch}"; then
    exit 0
  fi
  echo "Push rejected (attempt ${attempt}), rebasing again"
done

echo "Could not push after 3 attempts"
exit 1
