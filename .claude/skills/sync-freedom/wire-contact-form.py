#!/usr/bin/env python3
"""Deploy-only transform: wire the Freedom.AI contact form (in index.html) to the
SAME Google Apps Script endpoint as gregory-renard.com, so submissions land in the
same Google Sheet. The Claude Design form template already carries a SHEET_ENDPOINT
constant (empty string = mailto: fallback); this just fills it in. Idempotent.
Run from repo root.

The form POSTs firstName/lastName/email/message plus source:'freedom.ai' (so rows
from this site are distinguishable from gregory-renard.com rows in the sheet).
"""
import re, sys

P = "index.html"
# Same Google Apps Script Web App that gregory-renard.com's contact form posts to
# (doPost appends a row to the contacts sheet).
EP = "https://script.google.com/macros/s/AKfycbzBYfeq7nwrDsd9ZSwAmr_KSrgl8TDz3Hau1GD3YNcF17-AKDKpfR5tga3HJHBCXGVi/exec"

s = open(P, encoding="utf-8").read()
new, n = re.subn(r"SHEET_ENDPOINT = '[^']*';", "SHEET_ENDPOINT = '%s';" % EP, s, count=1)
if n == 0:
    print("contact form: !! SHEET_ENDPOINT marker not found in index.html — re-inspect the form", file=sys.stderr)
    sys.exit(1)
open(P, "w", encoding="utf-8").write(new)
print("contact form: wired SHEET_ENDPOINT -> Google Sheet")
