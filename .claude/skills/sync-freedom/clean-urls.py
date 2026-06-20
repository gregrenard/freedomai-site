#!/usr/bin/env python3
"""Deploy-only transforms for the Freedom.AI export: canonical domain + clean URLs
+ static SEO head + lang. Run from repo root on the 4 pages. Idempotent.

1. Canonical domain — the export hard-codes canonical/og:url on https://freedom.ai
   (apex). The site is served at the www host, so rewrite every absolute self-URL to
   https://www.freedom.ai. Idempotent ('https://freedom.ai' is absent once it's
   'https://www.freedom.ai'). Re-applied every sync because a fresh export reverts it.
2. Clean URLs  — rewrite internal page links to extensionless (matching the
   canonical URLs in each page) and the home link to './', so pages serve at
   /advisory-execution, /ai-lab, /brand and / on GitHub Pages. Relative forms work
   on the custom domain (https://www.freedom.ai/) AND on the project URL
   (https://gregrenard.github.io/freedomai-site/) while DNS propagates.
3. Static SEO  — the export keeps its <helmet> SEO tags INSIDE the <body> (the real
   <head> only has support.js). Copy the <helmet> inner into the real <head> so
   crawlers and social / AI scrapers that don't run JS still get title, description,
   canonical, og:/twitter: and JSON-LD. support.js also injects them at runtime;
   identical duplicates are harmless.
4. Static lang — add lang="en" to <html>.
"""
import re, glob

PAGES = ["index.html", "advisory-execution.html", "ai-lab.html", "brand.html"]

# The site is served at the www host; the export hard-codes the apex. Rewrite all
# absolute self-URLs to the canonical www host (must match the served domain + CNAME).
CANON_HOST = "https://www.freedom.ai"

# Quote-anchored, ordered. The '#' (anchored-home) form runs before the bare-home
# form so it isn't half-matched. Both quote styles cover static href="" attrs and
# the JS data arrays (href:'...'). Each rule is idempotent: no '.html' remains in
# these link forms after the first pass.
LINK_SUBS = [
    ('"index.html#', '"./#'), ("'index.html#", "'./#"),
    ('"index.html"', '"./"'), ("'index.html'", "'./'"),
    ('"advisory-execution.html"', '"advisory-execution"'), ("'advisory-execution.html'", "'advisory-execution'"),
    ('"ai-lab.html"', '"ai-lab"'), ("'ai-lab.html'", "'ai-lab'"),
    ('"brand.html"', '"brand"'), ("'brand.html'", "'brand'"),
]

for p in PAGES:
    if not glob.glob(p):
        continue
    s = open(p, encoding="utf-8").read()

    # 0a) strip Claude Design preview/serve URL prefixes so an exported absolute link
    #     (e.g. the contact CTA exported as
    #      https://<id>.claudeusercontent.com/v1/design/projects/<id>/serve/index.dc.html#contact)
    #     collapses to a bare relative link, which the steps below then clean. Idempotent.
    s = re.sub(r'https://[a-z0-9-]+\.claudeusercontent\.com/v1/design/projects/[^/]+/serve/', '', s)

    # 0) normalize the Claude Design ".dc.html" link form to ".html" so a direct
    #    DesignSync pull (links like advisory-execution.dc.html) is handled the same
    #    as a zip export (already .html). Only page links carry this; canonical/og
    #    don't. The next step then strips ".html" to extensionless. Idempotent.
    s = s.replace(".dc.html", ".html")

    # 1) canonical domain: apex -> www (idempotent; covers canonical + og:url + any
    #    absolute self-link, in both the body <helmet> and the injected <head> copy)
    s = s.replace("https://freedom.ai", CANON_HOST)

    # 2) clean internal links
    for a, b in LINK_SUBS:
        s = s.replace(a, b)

    # 3) static lang (idempotent: '<html>' is gone once it's '<html lang=...>')
    s = s.replace("<html>", '<html lang="en">', 1)

    # 4) helmet -> head, only if the real <head> has no <title> yet (idempotent)
    head = s.split("<body", 1)[0]
    if "<title>" not in head:
        m = re.search(r"<helmet>(.*?)</helmet>", s, re.S)
        if m:
            inner = m.group(1).strip("\n")
            s = s.replace("</head>", inner + "\n</head>", 1)

    open(p, "w", encoding="utf-8").write(s)
    print("clean-url/seo:", p)
