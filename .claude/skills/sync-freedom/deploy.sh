#!/usr/bin/env bash
# deploy.sh — re-apply ALL deploy-only transforms to the Freedom.AI export, then verify.
# Idempotent. Run from anywhere.
#
# Pipeline:  (optional: unpack export zip) -> wire contact form -> clean URLs + SEO head
#            + lang -> bump sitemap <lastmod> -> verify
#
# Does NOT touch the permanent repo files (CNAME, robots.txt, llms.txt, 404.html,
# README.md) — those are not from Design and survive every sync. Only sitemap.xml's
# <lastmod> is bumped.
#
# Usage:
#   bash .claude/skills/sync-freedom/deploy.sh                 # transform files already in repo
#   bash .claude/skills/sync-freedom/deploy.sh --extract       # unpack newest export zip first
#   bash .claude/skills/sync-freedom/deploy.sh --extract FILE  # unpack a specific zip first
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SKILL_DIR/../../.." && pwd)"
cd "$REPO"

if [ "${1:-}" = "--extract" ]; then
  echo "==> 0  unpack newest Claude Design export zip"
  python3 "$SKILL_DIR/extract-zip.py" ${2:+"$2"}
fi

echo "==> 1  wire contact form -> Google Sheet (same endpoint as gregory-renard.com)"
python3 "$SKILL_DIR/wire-contact-form.py"

echo "==> 2  clean URLs + static SEO head + lang"
python3 "$SKILL_DIR/clean-urls.py"

echo "==> 2b augment SEO (og:image/url, twitter card, favicon, JSON-LD)"
python3 "$SKILL_DIR/augment-seo.py"

echo "==> 3  bump sitemap <lastmod> to today"
TODAY="$(date +%F)"
sed -i '' "s|<lastmod>[^<]*</lastmod>|<lastmod>$TODAY</lastmod>|g" sitemap.xml

echo
bash "$SKILL_DIR/verify.sh"
