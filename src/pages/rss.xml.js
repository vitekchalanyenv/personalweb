import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITE_TITLE, SITE_DESC } from '../consts';
import { SERIES } from '../content.config';

export async function GET(context) {
  const posts = (await getCollection('articles', ({ data }) => data.lang === 'en' && !data.draft))
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());

  return rss({
    title: SITE_TITLE,
    description: SITE_DESC,
    site: context.site,
    items: posts.map((p) => ({
      title: `${SERIES[p.data.series].title} #${p.data.episode}: ${p.data.title}`,
      description: p.data.description,
      pubDate: p.data.date,
      link: `/articles/${p.id}/`,
      categories: [SERIES[p.data.series].title, ...p.data.tags],
    })),
    customData: '<language>en</language>',
  });
}
