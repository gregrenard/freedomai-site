# Freedom.AI

Site of **Freedom.AI** — an applied AI venture community and lab. Static site exported
from Claude Design, deployed on GitHub Pages with the custom domain **www.freedom.ai**.

## Live site

- https://www.freedom.ai (custom domain, GitHub Pages)
- also reachable at https://gregrenard.github.io/freedomai-site

## Pages

- Home / Vision (`index.html`)
- Advisory & Execution (`advisory-execution.html`)
- AI Lab (`ai-lab.html`)
- Brand (`brand.html`)

## Updating the site

Content is authored in Claude Design and exported as a "website review" zip. To publish
an update, drop the new export zip next to the repo and run the **sync-freedom** skill —
it re-applies the deploy-only transforms (clean URLs, static SEO head, contact-form
wiring) that Claude Design can't do, verifies internal links and assets, then pushes.
GitHub Pages redeploys automatically (~1 min). See `.claude/skills/sync-freedom/SKILL.md`.

## Deploy-only files (maintained in the repo, not from Claude Design)

`CNAME`, `robots.txt`, `sitemap.xml`, `llms.txt`, `404.html`.
