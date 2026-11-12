import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Three series. The `series` field is what turns your posts into a numbered
 * serial — which is the single strongest format finding from the research
 * (Cloward, Trümpler and Alisavakis are all numbered serials).
 *
 * Add a series here only if you actually intend to run it long-term.
 */
export const SERIES = {
  'shipping-kits': {
    title: 'Shipping Kits',
    tagline: 'How a commercial environment kit actually gets made.',
    blurb:
      'Everything between "nice render" and "a studio bought this and shipped it". Spec, grid discipline, trim sheet planning, naming conventions, LODs, documentation, and Epic\'s technical review.',
    accent: 'rust',
  },
  'grown-not-placed': {
    title: 'Grown, Not Placed',
    tagline: 'Vegetation, biomes and foliage that survives a frame budget.',
    blurb:
      'SpeedTree, Nanite foliage, wind, scatter and biome transitions — with profiler numbers, not vibes.',
    accent: 'moss',
  },
  'breaking-the-tile': {
    title: 'Breaking the Tile',
    tagline: 'Killing visible texture repetition.',
    blurb:
      'Macro variation, cell bombing, distance blending and the Substance Designer authoring that makes breakup cheap. Unreal and Unity where it makes sense.',
    accent: 'ochre',
  },
} as const;

export type SeriesKey = keyof typeof SERIES;

const seriesKeys = Object.keys(SERIES) as [SeriesKey, ...SeriesKey[]];

/**
 * A CMS form writes an empty string for a field the author left blank — it
 * cannot write "absent". Without these helpers, leaving the optional "Last
 * updated" box empty produces `updated: ''`, which fails date coercion and
 * breaks the whole build with an error the author cannot act on.
 *
 * So: treat empty as absent, everywhere an optional field can be typed into.
 */
const blankToUndefined = <T extends z.ZodTypeAny>(schema: T) =>
  z.preprocess((v) => (v === '' || v === null ? undefined : v), schema);

const optionalText = () =>
  z
    .string()
    .optional()
    .transform((v) => (v && v.trim() ? v : undefined));


/**
 * The fixed vocabulary of project deep-dive chapters. ArtStation gets the
 * renders and a light breakdown; the site gets the depth — one chapter per
 * discipline. A chapter page only exists when there is something real to say,
 * so a project with two chapters is fine.
 */
export const TOPICS = {
  'modular-kit': {
    title: 'Modular kit',
    blurb: 'Grid, trims, mesh inventory, and how the pieces combine.',
  },
  'tiling-materials': {
    title: 'Tiling materials',
    blurb: 'Substance graphs, breakup strategy, texel density decisions.',
  },
  'foliage': {
    title: 'Foliage',
    blurb: 'SpeedTree, scatter rules, wind, and the frame budget.',
  },
  'shaders': {
    title: 'Shaders',
    blurb: 'Master materials, blending, vertex paint, the expensive bits.',
  },
  'lighting': {
    title: 'Lighting',
    blurb: 'Light rig, Lumen settings, mood passes and exposure.',
  },
  'props': {
    title: 'Props & set dressing',
    blurb: 'Hero assets, clutter passes, storytelling placement.',
  },
  'process': {
    title: 'Process & pipeline',
    blurb: 'Blockout to final: refs, tools, iteration, what changed and why.',
  },
} as const;

export type TopicKey = keyof typeof TOPICS;

const topicKeys = Object.keys(TOPICS) as [TopicKey, ...TopicKey[]];

/**
 * Projects are the portfolio spine of the site. Each project is a hub page
 * (overview + gallery + facts) with chapter sub-pages for the deep dives.
 */
const projects = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    shortTitle: optionalText(),
    description: z.string(),
    kind: z.enum(['personal', 'client']).default('personal'),
    client: optionalText(),
    role: optionalText(),
    year: z.coerce.number().int(),
    engine: z.array(z.string()).default([]),
    cover: optionalText(),
    coverAlt: optionalText(),
    gallery: z
      .array(
        z.object({
          src: z.string(),
          alt: z.string().default(''),
          caption: optionalText(),
        })
      )
      .default([]),
    artstation: optionalText(),
    tags: z.array(z.string()).default([]),
    order: z.number().int().default(100),
    draft: z.boolean().default(false),
    lang: z.enum(['en', 'cs']).default('en'),
  }),
});

/**
 * One chapter = one discipline deep-dive inside one project.
 * One chapter per (project, topic) pair.
 */
const chapters = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/chapters' }),
  schema: z.object({
    project: z.string(),
    topic: z.enum(topicKeys),
    title: z.string(),
    description: z.string(),
    cover: optionalText(),
    coverAlt: optionalText(),
    versions: z.array(z.string()).default([]),
    updated: blankToUndefined(z.coerce.date().optional()),
    draft: z.boolean().default(false),
    lang: z.enum(['en', 'cs']).default('en'),
  }),
});

const articles = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/articles' }),
  schema: z.object({
    title: z.string(),
    // Short version for cards and <title>. Keep under ~60 chars.
    shortTitle: optionalText(),
    description: z.string(),
    series: z.enum(seriesKeys),
    // Episode number. This is the whole point — it makes it a serial.
    episode: z.number().int().positive(),
    date: z.coerce.date(),
    updated: blankToUndefined(z.coerce.date().optional()),
    // Cover image lives in /public/img/<slug>/, or /public/img/uploads/ for
    // anything added through the editor.
    cover: optionalText(),
    coverAlt: optionalText(),
    tags: z.array(z.string()).default([]),
    // Engine/tool versions the article was written against. Technical readers
    // care about this more than almost anything else, and it's what content
    // farms never bother to state.
    versions: z.array(z.string()).default([]),
    // Downloadable freebie attached to this article, if any.
    download: z
      .object({
        label: z.string().optional(),
        href: z.string().optional(),
        note: optionalText(),
      })
      .optional()
      // The editor writes the block out even when it was left blank. No label
      // or no path means there is no download — render nothing rather than an
      // empty button.
      .transform((d) =>
        d && d.label?.trim() && d.href?.trim()
          ? { label: d.label, href: d.href, note: d.note }
          : undefined
      ),
    // Set true while writing. Drafts are excluded from production builds.
    draft: z.boolean().default(false),
    lang: z.enum(['en', 'cs']).default('en'),
    // Slug of the translated counterpart, for hreflang pairing.
    translationOf: optionalText(),
  }),
});

/**
 * Reference pages are the "Unreal Directive" move: structured, searchable
 * data rather than prose. They are the highest-value SEO asset on the site
 * because nothing comparable exists — the best-known texel density resource
 * in the industry currently ranks as a raw PDF on a CDN.
 */
const reference = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './src/content/reference' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    order: z.number().int().default(100),
    updated: z.coerce.date(),
    versions: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    lang: z.enum(['en', 'cs']).default('en'),
  }),
});

export const collections = { articles, reference, projects, chapters };
