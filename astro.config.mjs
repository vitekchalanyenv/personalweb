import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// The live address. Everything public derives from this one line — the
// sitemap, the canonical tags, the RSS feed and the social preview URLs.
// If the domain ever changes, change it here and rebuild; nowhere else.
export const SITE = 'https://vitchalany.com';

export default defineConfig({
  site: SITE,
  integrations: [
    mdx(),
    sitemap({
      i18n: {
        defaultLocale: 'en',
        locales: { en: 'en', cs: 'cs' },
      },
    }),
  ],
  markdown: {
    /**
     * Dual theme. Shiki writes colours as inline styles, which beat any
     * stylesheet — so a single theme means code blocks stay dark in light mode
     * and become unreadable. `defaultColor: false` makes Shiki emit
     * --shiki-light / --shiki-dark custom properties instead, and global.css
     * picks the right one. Do not "simplify" this back to a single theme.
     */
    shikiConfig: {
      themes: { light: 'github-light-default', dark: 'github-dark-default' },
      defaultColor: false,
      wrap: true,
    },
  },
  build: { format: 'directory' },
});
