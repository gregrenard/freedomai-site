---
name: sync-freedom
description: Sync the freedom.ai site from a Claude Design export to GitHub so the live site updates, re-applying deploy-only fixes (clean URLs, static SEO head, contact-form wiring) that Claude Design can't do. Use when the user has re-exported Freedom.AI from claude.ai/design and wants it published — triggers like "sync freedom", "j'ai ré-exporté Freedom.AI", "publie / mets à jour le site freedom", "déploie freedom".
---

# Sync freedom.ai — Claude Design export → GitHub (with deploy-only fixes)

Take the latest Claude Design **"website review" export zip**, unpack it into the repo,
re-apply the deploy-only transforms Claude Design can't do (clean URLs, static SEO head,
contact-form wiring), verify internal links + assets, then push. GitHub Pages redeploys
the live site automatically (~1 min).

## Project facts
- **Source of truth:** Claude Design project **"Freedom.AI website review"**, projectId `34d6780e-4d52-433c-8587-45d682d177b4` (type `PROJECT_TYPE_PROJECT`, READ-ONLY — only `get_project`/`list_files`/`get_file`, never write). Pages live there as `index.dc.html`, `advisory-execution.dc.html`, `ai-lab.dc.html`, `brand.dc.html`.
- **Two ways to pull content:**
  1. **DesignSync (preferred for single-page edits):** `DesignSync get_file projectId=34d6780e-… path=<page>.dc.html`, then extract the `content` **byte-exact** from the session JSONL (`~/.claude/projects/<proj>/<session>.jsonl` — find the freshest `get_file` result, json-parse, write to disk as the repo's `<page>.html`). Do NOT hand-retype. `clean-urls.py` normalizes the `.dc.html` links to extensionless.
  2. **Zip export (full refresh):** drop the newest `Freedom.AI website review*.zip` in the parent dir; `deploy.sh --extract` unpacks `export/*` (already `.html`).
- **Repo / remote:** `origin/main` → `github.com/gregrenard/freedomai-site` (this working directory).
- **Live site:** https://www.freedom.ai (custom domain via `CNAME` = `www.freedom.ai`, GitHub Pages; also reachable at https://gregrenard.github.io/freedomai-site). DNS: a `CNAME` record `www` → `gregrenard.github.io`.
- **Pages (4):** `index.html` (Home/Vision), `advisory-execution.html`, `ai-lab.html`, `brand.html`.

## Automated flow (do this)
Once the user confirms the new export zip is in the parent dir:
1. **Unpack + transform + verify in one shot:**
   ```bash
   bash .claude/skills/sync-freedom/deploy.sh --extract
   ```
   (`--extract` unpacks the newest `Freedom.AI website review*.zip`; omit it to transform files already in the repo. Pass `--extract /path/to/file.zip` for a specific zip.)
2. **Review the real delta:** `git diff -U0 -- '*.html'` to eyeball the content change.
3. **Ship (ONLY with the user's go-ahead):** `git add -A && git commit && git push origin main`.
   Remind the user to open `/` in a browser to confirm the dc-runtime renders (check the
   console for `[dc-runtime] … failed`; curl proves bytes served, not that it rendered).

## Deploy-only transforms (what Claude Design can't do) — the pipeline `deploy.sh` runs
The raw export ships with `.html` internal links, an empty contact endpoint, and its SEO
tags trapped inside `<body>`. Each transform is **idempotent**, so re-running is safe.

1. **Wire the contact form** (`wire-contact-form.py`): the home form (`index.html`) has a
   `SHEET_ENDPOINT = ''` constant (empty = `mailto:` fallback). Fill it with the **same
   Google Apps Script Web App** gregory-renard.com posts to, so submissions land in the
   **same Google Sheet**. The form posts `firstName/lastName/email/message` + `source:'freedom.ai'`
   (so rows from this site are distinguishable in the sheet).
2. **Canonical domain + clean URLs + static SEO head + lang** (`clean-urls.py`):
   - Rewrite every absolute self-URL `https://freedom.ai` → `https://www.freedom.ai` (the
     export hard-codes the apex; the site is served at the www host, so canonical/og:url
     must match it). A fresh export reverts this, hence it runs every sync.
   - Rewrite internal page links to extensionless (`advisory-execution`, `ai-lab`, `brand`)
     and the home link to `./` / `./#section` — matching the canonical URLs in each page.
     Relative forms work on both `www.freedom.ai/` and the github.io project URL.
   - Copy each page's `<helmet>` (which sits **inside `<body>`** in the export — the real
     `<head>` only has `support.js`) into the real `<head>`, so non-JS crawlers + social/AI
     scrapers get title/description/canonical/og/twitter/JSON-LD.
   - Add `lang="en"` to `<html>`.
3. **Bump `sitemap.xml` `<lastmod>`** to today.

## Permanent repo files (NOT from Design — never clobber on sync)
The export only overwrites `index.html`, the 3 sub-pages, `support.js`, and `assets/*`.
These live only in the repo and survive every sync — don't let a transform touch them:
`CNAME` (www.freedom.ai), `robots.txt`, `sitemap.xml` (only `<lastmod>` bumped), `llms.txt`,
`404.html`, `README.md`, `.gitignore`, `.claude/`.

## Assets
- `assets/freedom-acacia.png` (logo mark), `assets/freedom-lockup.png`, `assets/freedom-lockup-h.png` — present in the export.
- The home hero portrait loads cross-domain from `https://gregory-renard.com/assets/greg-home-hd.png` (an absolute URL in the export — not a local asset). If that ever 404s, either restore it on gregory-renard.com or localize it into `assets/` and make the ref relative.
- `verify.sh` check (e) flags any new local `assets/*` reference that has no file (an image the user added in Design but the zip didn't carry / was >limit).

## Verify (`verify.sh`, run automatically by `deploy.sh`)
(a) no `<page>.html` internal links remain + no `.//`  · (b) `index.html` is the homepage
(no refresh redirect, `<x-dc>` present) · (c) every page has `<title>` + `og:title` in the
real `<head>` · (d) `SHEET_ENDPOINT` is wired · (e) every local asset ref resolves · (f)
permanent deploy/SEO files intact + `CNAME` → www.freedom.ai + canonicals on the www host.

## Push auth
⚠️ This repo is owned by the **`gregrenard`** GitHub account (same as gregory-renard.com).
The `gh` CLI also has `gregoryrenard-ai`; make sure `gregrenard` is active before pushing:
```
gh auth switch -u gregrenard
git -c credential.helper= -c credential.helper='!gh auth git-credential' push origin main
```
**Never commit/push without the user's explicit go-ahead.** No Claude attribution on
commits or PRs (see the user's global CLAUDE.md).
