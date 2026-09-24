# Portfolio + Commbricks

**Live:** https://sai1903.github.io

Static site, no build step required to serve it. Deployed from `main` via GitHub Pages.

Static site. No build step, no dependencies — open `index.html` or serve the folder.

```
services.html         360° services catalogue (generated — see build/)
card.html             digital visiting card (QR, tap-to-call, save contact)
contact.vcf           the downloadable contact file the card links to
index.html            portfolio (hero, now, work, stack, training, research, certs, contact)
commbricks.html       product suite (chat, mail, admin portal, people/HRMS)
hrms.html             HRMS deep dive (lifecycle, 4 stage tabs, 12 modules)

assets/
  css/base.css        tokens, type scale, light + dark palettes, keyframes
  css/site.css        layout, chrome, sections, the UI mockups
  css/theme.css       colour, imagery and motion layer (loads last)
  css/card.css        the visiting card (standalone page)
  css/services.css    the services catalogue
  logos/services-sprite.svg  ~157 brand marks, referenced by <use>
  js/card.js          card actions: share, QR, toast
  js/qrcode.js        vendored QR generator (MIT, Kazuhiko Arase)
  js/site.js          theme toggle, nav, reveal, tabs, progress bar, counters, carousel
  logos/              brand marks (simple-icons) + the inlined sprite
  6vgicdie_surya-professional.png    hero portrait
  commbricks-logo-color-512h.png     wordmark
  commbricks-mark-512.png            app icon
  favicon.ico
```

## Deployment

GitHub Pages serves `main` from the repository root. Pushing to `main` redeploys;
the first build took about 25 seconds. `.nojekyll` is present so Pages serves the
files as-is rather than running them through Jekyll.

If the canonical domain ever changes, three things need updating: the `canonical`
and `og:` tags in each page head, `sitemap.xml` / `robots.txt`, and the vCard —
`python tools/make-vcard.py https://new-domain/card.html`. The QR needs nothing,
since it is generated from `location.href` at runtime.

## Run locally

    python -m http.server 8000

Then open http://localhost:8000

## Design notes

**Colour** is pulled off the Commbricks mark — terracotta `#c0452a`, sampled from
the logo file. Around it sit five supporting hues, one per idea: ocean (Mail),
indigo (Admin), gold (People/HR), pine (success states) and plum (research).
Cards pick their accent up from a local `--c` custom property, so a product card,
a lifecycle stage and a stat tile all colour themselves from one declaration.

**Type** is Bricolage Grotesque for display, Plus Jakarta Sans for body and
IBM Plex Mono for labels and metadata.

**Company logos** are real brand marks from simple-icons, fetched once and inlined
as an SVG sprite in `index.html` (`<use href="#li-aws">`). They render in each
company's own brand colour. To add one:

    curl -o assets/logos/<slug>.svg https://cdn.jsdelivr.net/npm/simple-icons@13/icons/<slug>.svg

then re-run the sprite build and re-inline it.

**Portrait scene** — the hero cut-out sits inside a decorative layer built from
three parts: SVG pipeline rings (dashed strokes with an animated `stroke-dashoffset`,
so data appears to flow around the subject), quantum shells (three rotated ellipses
with a slow opacity pulse), and six technology nodes — AI agent, quantum, data
pipeline, neural network, compute and warehouse — carried on rotating orbit
containers. Each node runs a matching reverse animation so its glyph stays upright
while the orbit spins. Data packets ride the rings via SVG `animateMotion` pointed
at the same paths the strokes use, so the marks and the motion can never drift apart.
Orbit radius is half the orbit box height; the boxes are inset so nodes stay near the
photo edge and never reach the text column. Nodes hide below 620px and packets are
removed under `prefers-reduced-motion`.

**Carousel** (training tracks) uses native CSS scroll-snap; the arrows and dots
only nudge `scrollLeft`, so touch, trackpad, scrollbar and keyboard all keep
working and nothing breaks if JS fails. Pages and dots are recomputed on resize,
so the same markup shows 4 cards on desktop and 1 on a phone.

**Motion** — scroll progress bar, staggered hero entrance, drifting gradient orbs,
count-up stats, floating portrait, per-card hover lifts, a marquee, and SVG
draw-in on the diagrams. Everything is disabled under `prefers-reduced-motion`.

## The services catalogue

`services.html` is **generated**. Edit the catalogue data in
`build/make-services.py` (tracks, tools, advisory/consulting items, engagement
table) or the page shell in `build/services-template.html`, then:

    python build/make-services.py

It fetches any missing brand marks from simple-icons, writes
`assets/logos/services-sprite.svg`, and rebuilds `services.html`.

Two details worth knowing:

- **Tool chips come in two flavours.** Where simple-icons carries a brand, the
  real mark is used in the official colour. Where it does not — the Microsoft
  family, Workday, IBM, SAS and others are excluded there on trademark grounds
  — the chip falls back to a styled monogram tile, with the brand colour taken
  from `MONO` in the generator. 157 real logos, 58 monograms at last build.
- **Colours are contrast-corrected per theme.** A near-black mark (Express,
  Next.js, Vercel, GitHub) disappears on the dark background, and a near-white
  one washes out on cream. The generator computes relative luminance and emits a
  second value, `--tcd`, used only under `[data-theme="dark"]`.

## The digital visiting card

`card.html` is a standalone, phone-first page meant to be handed out — by QR,
link, or WhatsApp. The header is a cover photo: the portrait cut-out on the
brand gradient, with the Commbricks mark and wordmark on a light chip so the
logo keeps its own colour against the gradient. The page sits on a heavily
blurred, low-opacity wash of the same photo. Four frosted-glass chips (quantum,
AI agent, data pipeline, neural network) float in the cover beside the figure,
over dashed rings whose stroke animates so data appears to circle the subject —
the same visual language as the hero scene on the portfolio. It has four one-tap actions (call, WhatsApp, email, website),
plus:

- **Save to contacts** links to a real `contact.vcf` rather than building one in
  JavaScript. iOS Safari opens a real .vcf straight into "Add to Contacts", and
  it still works with JS disabled. It embeds a 280px photo, so your face shows up
  in the other person's phone.
- **Share this card** uses the Web Share API (the native share sheet on mobile)
  and falls back to copying the link on desktop.
- **The QR is generated at runtime from `location.href`**, so it always points at
  wherever the page is actually hosted — localhost, a staging URL or your final
  domain. Nothing to regenerate when you deploy.

After deploying, add your URL to the contact file:

    python tools/make-vcard.py https://your-domain.com/card.html

## Before publishing

- `index.html` — the four entries under "Selected experience" use neutral org
  descriptions (see the HTML comment above them). Swap in your real employers,
  and replace the placeholder achievement bullets with your actual numbers.
- Certification names are generic; add exact credential titles and IDs.
- Add real links (LinkedIn, GitHub, Google Scholar) to the footer nav.
- Run `tools/make-vcard.py` with your live URL so the saved contact carries it.
- `og:image` points at the portrait; swap it for a proper 1200×630 card if you
  want richer link previews.

## Theme

Colours are custom properties on `:root` in `base.css`, with a dark set under
`:root[data-theme="dark"]`. The toggle writes to `localStorage` under `bssk-theme`;
an inline script in each `<head>` applies it before paint so there is no flash.
That script also adds a `js` class to `<html>` — scroll-reveal only hides content
when it is present, so a script failure can never leave the page blank.
