#!/usr/bin/env python3
"""Sync step: unpack a fresh Claude Design "website review" export into the repo root.

Finds the newest 'Freedom.AI website review*.zip' in the parent directory (or takes
an explicit path arg) and extracts its export/* members (index.html, *.html,
support.js, assets/*) into the repo root, overwriting the Design-sourced files only.
Does NOT touch the permanent repo files (CNAME, robots.txt, sitemap.xml, llms.txt,
404.html, README.md, .gitignore, .claude/). Run from anywhere.

Usage:
  python3 .claude/skills/sync-freedom/extract-zip.py [path/to/export.zip]
"""
import sys, os, glob, zipfile

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(SKILL_DIR, "..", "..", ".."))
PARENT = os.path.dirname(REPO)

if len(sys.argv) > 1 and sys.argv[1]:
    zpath = sys.argv[1]
else:
    cands = glob.glob(os.path.join(PARENT, "Freedom.AI website review*.zip"))
    if not cands:
        print("extract-zip: no 'Freedom.AI website review*.zip' found in", PARENT, file=sys.stderr)
        sys.exit(1)
    zpath = max(cands, key=os.path.getmtime)

print("extract-zip: using", zpath)
with zipfile.ZipFile(zpath) as z:
    members = [m for m in z.namelist() if m.startswith("export/") and not m.endswith("/")]
    if not members:
        print("extract-zip: no export/* members in zip", file=sys.stderr)
        sys.exit(1)
    for m in members:
        rel = m[len("export/"):]
        dest = os.path.join(REPO, rel)
        # stay inside the repo (defensive against crafted zip paths)
        if not os.path.abspath(dest).startswith(REPO + os.sep):
            print("extract-zip: skipping out-of-repo path", m, file=sys.stderr)
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with z.open(m) as src, open(dest, "wb") as out:
            out.write(src.read())
        print("  ->", rel)
print("extract-zip: done — now run deploy.sh to re-apply transforms")
