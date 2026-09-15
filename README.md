# vitchalany.com

Static site for environment art writing: three numbered series, a structured
reference section, kits, and the PLACES demo page. Built with Astro, deploys to
Cloudflare Pages for free.

Architecture follows the pattern used by the people whose *writing* built their
reputation — Simon Trümpler being the clearest example: **blog at the root of
your own domain, portfolio on ArtStation.** Nobody in that group uses
`blog.domain.com`, because a subdomain fragments your search authority and gains
you nothing when the writing *is* the brand.

---

## Run it

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # static output in dist/
npm run preview      # serve the built output locally
```

Node 18+ required. No database, no server, no CMS.

---

## First fifteen minutes

Everything you need to change to make this yours:

1. **`src/consts.ts`** — your name, links, email, newsletter endpoint. One file.
2. **`astro.config.mjs`** — set `site` to your real domain. This matters: it
   feeds canonical URLs, the sitemap and the RSS feed.
3. **`public/robots.txt`** — update the sitemap URL to your domain.
4. **`public/img/og-default.png`** — replace with a real 1200×630 social card.
5. **Placeholder images** — everything in `public/img/*/` is a generated
   placeholder. Replace with real screenshots as you go; the articles will look
   broken-ish until you do, which is deliberate motivation.

---

## Deploy to Cloudflare Pages

Free tier, unmetered bandwidth, automatic SSL, no server to fall over. That last
part matters: the standard objection to artists having their own site (images
blocked by studio firewalls, SSL errors, maintenance burden) is really an
objection to self-hosted PHP on shared hosting. A static site on a major CDN
does not have those failure modes.

1. Push this repo to GitHub.
2. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Connect to Git**.
3. Build settings:
   - Framework preset: **Astro**
   - Build command: `npm run build`
   - Output directory: `dist`
4. Add your custom domain under **Custom domains**. SSL is automatic.

`public/_headers` already sets long cache lifetimes on `/assets/*` and `/img/*`,
so repeat visits are near-instant.

**Large media:** Cloudflare Pages caps individual assets at 25 MiB. Anything
bigger — 4K masters, long video — belongs in **R2** (zero egress fees) or
**Cloudflare Stream** ($5 per 1,000 minutes stored, $1 per 1,000 delivered).
Short shader loops should be MP4/WebM, never GIF: a 10-second 1080p GIF is
20–40 MB against roughly 1–2 MB as H.264.

---

## Writing an article

Drop an `.mdx` file in `src/content/articles/`. Filename becomes the URL slug,
so name it `<series>-<episode>-<short-slug>.mdx`.

```mdx
---
title: 'The full headline, which can be long'
shortTitle: 'What shows in cards and the tab'
description: >-
  Two or three sentences. This is your meta description and your standfirst, so
  it has to work as both. Lead with the problem, not the solution.
series: shipping-kits          # or grown-not-placed | breaking-the-tile
episode: 2
date: 2026-09-02
cover: /img/shipping-kits-02/cover.webp
coverAlt: 'Describe it for someone who cannot see it'
tags: [modular, trim sheets]
versions: ['Unreal Engine 5.7', 'Substance 3D Designer 14']
draft: false
---

import Callout from '../../components/Callout.astro';
import NodeGraph from '../../components/NodeGraph.astro';
import Numbers from '../../components/Numbers.astro';

Body copy here.
```

`draft: true` hides it from production builds but keeps it visible in `dev`, so
you can work in the open without publishing.

### Series are configured in one place

`src/content.config.ts` holds the `SERIES` object — titles, taglines, accent
colours. Adding a fourth series is three lines there.

The episode numbering is not decoration. All three of the highest-status
technical-art brands (Ben Cloward's *Shader Graph Basics*, Trümpler's *Game Art
Tricks* at #90, Alisavakis's *Technically Art* at #141) are numbered serials. A
numbered series gives you permission to publish an imperfect part, builds
expectation, compounds as an archive, and turns you into "the person who does
the series on X" rather than someone who posts occasionally.

---

## The components, and why each exists

| Component | Use it for | Why it matters |
|---|---|---|
| **`NodeGraph`** | Material/shader graph screenshots | Lists node names as **real text** under the image. Google cannot read your screenshot — this is how you outrank Udemy pages for shader queries. The single most valuable component here. |
| **`Numbers`** | Profiler measurements | Before/after table with direction colouring. Content farms cannot fabricate a number they never measured; this is your moat on optimisation topics. |
| **`BeforeAfter`** | Visual comparisons | Draggable slider. Keyboard and touch accessible, degrades to stacked images without JS. |
| **`Callout`** | `kind="key"` / `warn` / `wrong` / `note` | `wrong` exists specifically for "what I tried that failed" — the section nobody writes and readers remember. |
| **`SpecTable`** | Asset and scene specs | Definition list of hard facts near the top of an article. |
| **`Download`** | Email-gated freebie | Fab keeps your customers; a free file on your own domain gets you the email. Point it at your ESP form endpoint. |
| **`Figure`** | Plain captioned image | `wide` prop breaks out of the text measure. |
| **`TexelCalculator`** | The reference page | Interactive, zero dependencies. |

### Every technical article should have

1. The problem, with an image of it going wrong.
2. **What you tried that failed.** (`<Callout kind="wrong">`)
3. The solution, with node names as text. (`<NodeGraph>`)
4. **Real numbers.** (`<Numbers>`)
5. When *not* to use it.
6. A download.
7. Links to the previous part and the related reference page.

If you cannot fill in 2 and 4, the article is not finished.

---

## The graphic system

This is what stops the site reading as a layout with content dropped into it.

### Procedural topographic art

`tools/make-art.py` generates every image on the site: contour lines over a
fractal heightmap, in the Field Notes palette, with survey-sheet furniture
(registration ticks, graticule marks, a tracked-out mono label). Run it with:

```bash
python3 tools/make-art.py     # needs numpy + pillow
```

Two things worth knowing:

- **It is deterministic maths, not generative AI.** Value noise, quantised
  contour bands, hatching. Same seed, same output, forever. Nothing about it
  conflicts with the no-AI position the whole brand rests on.
- **It is a placeholder that does not look like one.** Grey boxes labelled
  PLACEHOLDER are the single biggest reason a site reads as unfinished. Drop your
  real render over any of these and the page does not change shape.

Change a `seed` in `main()` for different terrain; `accent` picks rust / moss /
ochre; `ridged=True` gives sharper mountain ridges instead of rolling hills.

### `Contours.astro`

The same idea as inline SVG, generated at build time from a seeded PRNG. Used as
the hero backdrop, behind article headers, and inside the method block. Crisp at
any size, no image request, and it animates: three line groups drift at
different speeds for parallax with no JavaScript. Disabled under
`prefers-reduced-motion`.

### `Icon.astro`

Twelve hand-drawn icons — 1.5px strokes, square caps, survey-drawing rather than
rounded product UI. Inherits `currentColor`, pulls in no package.

### `Stamp.astro`

The no-AI declaration as an archival rubber stamp, text on a circular path. This
exists because the claim is load-bearing for the brand and a line of small grey
text does not carry it.

### `Wordmark.astro`

VC monogram in an open survey bracket with an elevation tick. Drawn, not typeset,
so it holds at 22px and at 400px.

### Depth and motion utilities

Classes in `global.css`, composable onto anything:

| Class | Effect |
|---|---|
| `.surface` / `.card` | Gradient hairline, inner top highlight, soft outer shadow — three cheap layers that stop a panel reading as a wireframe box |
| `.lift` | Hover raise with accent border and glow |
| `.ticks` | Corner registration marks, drawn with borders, brighten on hover |
| `.plate` | Image frame with a warm inner vignette; add `.zoom` for a slow hover scale |
| `.glow` | Blurred radial accent, hero only |
| `.rule` | Hairline divider that fades along its length |
| `.seclabel` | Section label with a drawn tick and a numeral |
| `.numeral` | Tabular serif index number |

Motion is wired in `Base.astro`: `Reveal.astro` wraps a block for a scroll-in
entrance (IntersectionObserver, once per element), and a reading-progress bar
tracks scroll. Both respect `prefers-reduced-motion`, and content is visible by
default so a no-JS visitor never gets a blank page.

---

## Reference pages

`src/content/reference/*.mdx`, rendered with a sticky index sidebar and ordered
by the `order` field.

These are the highest-value SEO asset on the site, and the reason is specific:
the best-known texel density resource in environment art currently ranks on
Google as a **raw PDF served off a CDN** — no HTML, no headings, no internal
links, not interactive. An actual page with a calculator takes that position.

The model is Unreal Directive: structured, searchable data beats prose for both
search and repeat visits.

Planned pages beyond texel density: trim sheet standards, modular grid
conventions, foliage budget numbers.

---

## Czech versions

`src/pages/cs/` holds Czech pages, wired with `hreflang` through `BaseHead`. The
language toggle in the header swaps between the two.

Publish selectively rather than mirroring everything. Czech-language reach in
this niche tops out at a few thousand people, so treat Czech as a
**relationship** channel for the local industry — Warhorse, Bohemia, SCS,
Hangar 13, Madfinger — and English as the growth channel.

To translate an article, add `lang: 'cs'` and `translationOf: '<en-slug>'` to a
copy of the MDX. The English routes filter on `lang === 'en'`, so Czech articles
will not leak into the English index.

---

## SEO notes

- **`TechArticle` JSON-LD** on every article, with series membership via
  `CreativeWorkSeries`. This is the concrete capability you own by not being on
  Substack, which emits no schema markup and gives you no heading control.
- Canonical URLs, `hreflang` pairs, sitemap with i18n config, RSS at `/rss.xml`.
- **Publish here first.** Let it index for a few days before syndicating.
- **Syndicate to at most two or three places**, always with `rel=canonical`
  pointing back. Medium's import tool sets it automatically; a hand-paste does
  not.
- **ArtStation blogs and LinkedIn do not support canonical tags.** Post a
  genuinely shortened teaser there — two to four paragraphs, best image, "full
  breakdown with node graphs here" — never the full text. ArtStation blogs are
  poor for on-platform engagement (one artist measured 10 blog posts at 3,621
  views against a single portfolio project at 7,900) but they *do* rank in
  Google, which is why the teaser is worth posting at all.
- **80.lv is the highest-value target.** It ranks on page one for most of this
  keyword set, features are free for artists, and their model is editorial
  pickup — post the breakdown publicly with good visuals and they find it. Lead
  a pitch with the *technically unusual solution*, not the pretty render; that is
  their criterion with the least competition.

---

## Cadence

Every two to three weeks, tied to work you actually did. **Not weekly.**

Both weekly newsletters in this exact niche — Alisavakis's *Technically Art* and
Beyond Extent's *This Week in Environment Art* — stopped publishing. The
durable ones never committed to weekly: Ben Golus publishes roughly once a year
and gets cited on Wikipedia for it. A newsletter you send when you have
something is infinitely better than a weekly one you abandon at issue 40.

---

## Project structure

```
src/
  consts.ts               name, links, newsletter endpoint — start here
  content.config.ts       collection schemas + the SERIES definitions
  content/
    articles/*.mdx        the three series
    reference/*.mdx       structured reference pages
  components/             MDX components + site chrome
  layouts/                Base, Article, Reference
  pages/
    index.astro           home
    articles/             index + [...slug]
    reference/            index + [...slug]
    kits.astro            commercial kits, each linking to its breakdown
    demo.astro            PLACES landing page
    cs/                   Czech
    rss.xml.js
  styles/global.css       ~10 custom properties, no framework
public/
  img/<article-slug>/     article images (placeholders in place now)
  downloads/              freebies
  _headers                Cloudflare cache headers
```

---

## Licence

Site code: do what you like with it. Article text and images: all rights
reserved, and all of it hand-authored — no generative AI at any stage, including
reference gathering.
