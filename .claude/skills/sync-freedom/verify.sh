#!/usr/bin/env bash
# verify.sh — post-transform sanity checks for the Freedom.AI site. Non-zero on failure.
# Safe to run standalone:  bash .claude/skills/sync-freedom/verify.sh
set -uo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SKILL_DIR/../../.." && pwd)"
cd "$REPO"

PAGES="index.html advisory-execution.html ai-lab.html brand.html"
fail=0

echo "--- (a) internal page links cleaned (no '<page>.html' links, no accidental .//) ---"
if grep -rEn "href[:=] ?[\"'](advisory-execution|ai-lab|brand|index)\.html" $PAGES >/dev/null 2>&1; then
  echo "  BAD: a <page>.html internal link remains:"; grep -rEn "href[:=] ?[\"'](advisory-execution|ai-lab|brand|index)\.html" $PAGES | head; fail=1
else echo "  ok: page links extensionless"; fi
if grep -rn '\.//' $PAGES >/dev/null 2>&1; then echo "  BAD: .// found"; fail=1; else echo "  ok: no .//"; fi

echo "--- (b) index.html is the homepage (not a redirect) and renders ---"
[ "$(grep -c 'http-equiv="refresh"' index.html)" = "0" ] && echo "  ok: no refresh redirect" || { echo "  BAD: index has refresh"; fail=1; }
[ "$(grep -c '<x-dc>' index.html)" -ge 1 ] && echo "  ok: <x-dc> present" || { echo "  BAD: no <x-dc>"; fail=1; }

echo "--- (c) static SEO present: each page has <title> + og:title inside the real <head> ---"
for f in $PAGES; do
  h=$(awk 'BEGIN{p=1}/<body/{p=0}{if(p)print}' "$f")
  if echo "$h" | grep -q "<title>" && echo "$h" | grep -q "og:title"; then :; else echo "  MISS seo-head: $f"; fail=1; fi
done
[ $fail -eq 0 ] && echo "  ok: all pages have <title> + og:title in <head>"

echo "--- (d) contact form wired to the Google Sheet endpoint ---"
grep -q "SHEET_ENDPOINT = 'https://script.google.com/macros/s/" index.html && echo "  ok: SHEET_ENDPOINT set" || { echo "  BAD: SHEET_ENDPOINT empty/missing"; fail=1; }

echo "--- (e) every LOCAL asset reference resolves (absolute-URL refs are skipped) ---"
# Only match assets/ preceded by a quote or paren (a relative ref); an absolute
# URL like https://gregory-renard.com/assets/x.png has '/assets' (preceded by '/')
# and is intentionally not checked here — it's an external dependency, not a repo file.
for raw in $(grep -rhoE "[\"'(]assets/[A-Za-z0-9%@_.-]+\.(png|jpg|jpeg|webp|gif|svg|mp4|pdf)" $PAGES 2>/dev/null | sort -u); do
  t="${raw:1}"   # strip the leading " ' or ( delimiter
  [ -f "$t" ] && echo "  ok: $t" || { echo "  MISS: $t"; fail=1; }
done

echo "--- (f) permanent deploy/SEO files intact ---"
for pf in CNAME robots.txt sitemap.xml llms.txt 404.html support.js; do
  [ -f "$pf" ] && echo "  ok: $pf" || { echo "  BAD: $pf MISSING"; fail=1; }
done
grep -qx "www.freedom.ai" CNAME 2>/dev/null && echo "  ok: CNAME -> www.freedom.ai" || { echo "  BAD: CNAME != www.freedom.ai"; fail=1; }

echo "--- (g) canonicals on the served www host (no leftover apex) ---"
if grep -rn 'href="https://freedom\.ai' $PAGES >/dev/null 2>&1; then
  echo "  BAD: apex canonical/og still present (should be https://www.freedom.ai)"; fail=1
else echo "  ok: all absolute self-URLs on www.freedom.ai"; fi

echo "--- (h) rich-preview SEO present on every page (og:image, twitter, favicon) ---"
for f in $PAGES; do
  h=$(awk 'BEGIN{p=1}/<body/{p=0}{if(p)print}' "$f")
  miss=""
  echo "$h" | grep -q 'og:image' || miss="$miss og:image"
  echo "$h" | grep -q 'twitter:card' || miss="$miss twitter:card"
  echo "$h" | grep -q 'rel="icon"' || miss="$miss favicon"
  [ -z "$miss" ] && echo "  ok: $f" || { echo "  MISS$miss : $f"; fail=1; }
done
grep -q 'application/ld+json' index.html && echo "  ok: JSON-LD on home" || { echo "  MISS: JSON-LD on home"; fail=1; }
for a in assets/og-cover.png assets/favicon.png; do [ -f "$a" ] && echo "  ok: $a" || { echo "  MISS: $a"; fail=1; }; done

echo
[ $fail -eq 0 ] && echo "VERIFY: all checks passed ✅" || echo "VERIFY: FAILURES above ❌"
exit $fail
