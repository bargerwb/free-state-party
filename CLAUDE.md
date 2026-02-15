# Free State Party — Site

## What This Is
Multi-page site for the Free State Party — a private club for liberty-minded free staters in NH. Jeremy Kauffman's crew. Dennis Pratt runs concierge/vetting (anonymous on site).

## Stack
- Multi-page output: `site/index.html`, `about.html`, `events.html`, `join.html`
- Content in `content/*.md` (the CMS)
- Shared template: `templates/base.html` with `{{placeholders}}`
- Build: `python3 build.py` reads content + base template, writes 4 pages to `site/`
- Tailwind CSS via CDN, Google Fonts (Playfair Display + Inter), vanilla JS
- Netlify Forms for concierge form (on join.html)
- Deploy: Netlify REST API (file digest method)

## Key Commands
- Build: `python3 build.py` (from project root)
- Deploy: Use Netlify REST API with file digest. Token at `~/Library/Preferences/netlify/config.json`

## Pages
- **/** — Home: hero with cycling word animation + video
- **/about.html** — About: pitch (identity/belonging) + what this is (clarity)
- **/events.html** — Events: upcoming events cards
- **/join.html** — Join Us: concierge form (name, contact, about, X handle)

## Directory Structure
```
content/          <- Markdown content files (the CMS)
  hero.md, pitch.md, what-this-is.md, events.md, come-meet-us.md, footer.md, words.md
templates/
  base.html       <- Shared HTML shell (nav, footer, head, scripts)
site/             <- Built output (deploy this dir)
  index.html      <- Home
  about.html      <- About
  events.html     <- Events
  join.html       <- Join Us (form)
  video/          <- Homepage video
  img/            <- Event photos (when available)
build.py          <- Multi-page build script
```

## Content Editing
Edit `content/*.md` files, run `python3 build.py`, deploy. Non-technical collaborators (Jeremy, Dennis) can edit markdown without touching HTML.

## Design Decisions
- **Palette**: Same as Free State Saturdays (dark-900 #0a0a0a + gold-500 #d4a017)
- **Fonts**: Playfair Display (headlines) + Inter (body)
- **Voice**: Community "we", confident, unapologetic, LPNH energy
- **JOIN button**: Bait — links to /join.html. Cannot join online, must meet in person.
- **Dennis**: Anonymous. Never named on site. "We" energy only.
- **No names on site**: Community voice, no individual attribution
- **Reactionary Futurism**: Past values + forward momentum. Not nostalgic.

## Gotchas
- SVGs need explicit width/height attrs (Tailwind v4 preflight issue)
- Netlify CSP blocks inline styles — use Tailwind classes or `<style>` blocks
- Netlify deploy: REST API, not CLI (CLI broken in sandbox)
- `brew`/`gh` not on PATH in sandbox — use full paths
- Nav links use `/about.html` etc. — works with Netlify pretty_urls disabled

## Domain
freestate.party (Jeremy owns it)

## Netlify
- Site ID: d3e99d3d-f171-43b7-8f20-8099bfa744bf
- URL: https://free-state-party.netlify.app

## Expandability
Monthly fee opportunity. Brand is expandable to cover liberty events statewide. Template/content architecture supports adding more pages. Get event list from Jeremy.
