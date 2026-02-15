# Free State Party — Site

## What This Is
Multi-page site for the Free State Party — a private club for liberty-minded free staters in NH. Dennis Pratt runs concierge/vetting (anonymous on site).

## Stack
- Content in `content/*.md` (the CMS — edit content here)
- Shared template: `templates/base.html` with `{{placeholders}}`
- Build: `python3 build.py` reads content + base template, writes pages to `site/`
- Tailwind CSS via CDN, Google Fonts (Playfair Display + Inter), vanilla JS
- Netlify Forms for concierge form (on join.html)
- Auto-deploys from GitHub (`main` branch) → Netlify (publish dir: `site/`)

## How to Edit Content
1. Edit the relevant `content/*.md` file
2. Run `python3 build.py`
3. Commit and push — Netlify auto-deploys from `main`

## Pages
- **/** — Home: hero with cycling word animation + video
- **/about.html** — About: pitch (identity/belonging) + what this is (clarity)
- **/events.html** — Events: tabbed open/closed
- **/join.html** — Join Us: concierge form (name, contact, about, X handle)

## Directory Structure
```
content/          <- Markdown content files (the CMS)
  hero.md         <- Tagline, sub-tagline, CTA
  pitch.md        <- Identity/belonging section
  what-this-is.md <- Clarity section
  events.md       <- Open + closed events
  come-meet-us.md <- Join page copy
  footer.md       <- Footer content
  words.md        <- Cycling word list (one per line)
templates/
  base.html       <- Shared HTML shell (nav, footer, head, scripts)
site/             <- Built output (deploy this dir)
build.py          <- Build script
```

## Who Owns What
- **Content** (`content/*.md`): Anyone — edit markdown, build, push
- **Template/code** (`templates/`, `build.py`): Bill — structural changes, new pages, JS
- **Deploy config**: Bill — Netlify settings, domain DNS
- Use branches for anything beyond a simple content edit

## Design Decisions
See `DECISIONS.md` for the full list. Key points:
- **Palette**: dark-900 #0a0a0a + gold-500 #d4a017
- **Fonts**: Playfair Display (headlines) + Inter (body)
- **Voice**: Community "we", confident, unapologetic, LPNH energy
- **JOIN button**: Bait — links to join.html. Cannot join online, must meet in person.
- **Dennis**: Anonymous. Never named on site.
- **Reactionary Futurism**: Past values + forward momentum. Not nostalgic.

## Gotchas
- SVGs need explicit width/height HTML attributes (Tailwind preflight issue)
- No inline `style="..."` attributes (Netlify CSP blocks them) — use Tailwind classes
- Nav links use relative paths (`about.html` not `/about.html`) so local preview works
- Video is gitignored (too large) — `build.py` copies it from local source during build

## Domain & Hosting
- **Domain**: freestate.party
- **Hosting**: Netlify (auto-deploy from GitHub `main`)
- **Netlify site ID**: d3e99d3d-f171-43b7-8f20-8099bfa744bf
- **Repo**: github.com/bargerwb/free-state-party
