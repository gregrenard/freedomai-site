#!/usr/bin/env python3
"""Deploy-only transform: augment each page's real <head> with the rich-preview +
structured-data SEO that Claude Design's <helmet> doesn't carry. Run from repo root
AFTER clean-urls.py (which injects the helmet — title/description/canonical — into
<head>). Idempotent: skips a page whose <head> already has og:image.

Adds per page: og:url (= canonical), og:image (+ width/height/alt), twitter:card
(summary_large_image) + twitter:title/description/image, and favicon links.
Home (index.html) also gets a JSON-LD Organization block.
"""
import re

SITE = "https://www.freedom.ai"
OG_IMAGE = SITE + "/assets/og-cover.png"
PAGES = ["index.html", "advisory-execution.html", "ai-lab.html", "brand.html"]

ORG_JSONLD = '''  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Freedom.AI",
    "alternateName": "Freedom.ai",
    "url": "https://www.freedom.ai/",
    "logo": "https://www.freedom.ai/assets/og-cover.png",
    "image": "https://www.freedom.ai/assets/og-cover.png",
    "description": "Applied AI venture community and lab \\u2014 advisory and execution for leaders, and an applied AI lab shipping production GenAI across cloud, on-premise and edge.",
    "founder": { "@type": "Person", "name": "Gregory Renard", "url": "https://www.gregory-renard.com" },
    "sameAs": ["https://www.gregory-renard.com"]
  }
  </script>
'''

def find(pat, s, default=""):
    m = re.search(pat, s)
    return m.group(1) if m else default

for p in PAGES:
    try:
        s = open(p, encoding="utf-8").read()
    except FileNotFoundError:
        continue
    head = s.split("<body", 1)[0]
    if "og:image" in head:            # already augmented (idempotent)
        continue
    canon = find(r'<link rel="canonical" href="([^"]*)"', head, SITE + "/")
    title = find(r'<title>([^<]*)</title>', head, "Freedom.AI")
    desc  = find(r'<meta name="description" content="([^"]*)"', head, "")

    block  = '  <meta property="og:url" content="%s">\n' % canon
    block += '  <meta property="og:image" content="%s">\n' % OG_IMAGE
    block += '  <meta property="og:image:width" content="1200">\n'
    block += '  <meta property="og:image:height" content="630">\n'
    block += '  <meta property="og:image:alt" content="Freedom.AI — Applied AI Venture Community">\n'
    block += '  <meta name="twitter:card" content="summary_large_image">\n'
    block += '  <meta name="twitter:title" content="%s">\n' % title
    block += '  <meta name="twitter:description" content="%s">\n' % desc
    block += '  <meta name="twitter:image" content="%s">\n' % OG_IMAGE
    block += '  <link rel="icon" type="image/png" href="/assets/favicon.png">\n'
    block += '  <link rel="apple-touch-icon" href="/assets/favicon.png">\n'
    if p == "index.html":
        block += ORG_JSONLD

    s = s.replace("</head>", block + "</head>", 1)
    open(p, "w", encoding="utf-8").write(s)
    print("seo-augment:", p)
