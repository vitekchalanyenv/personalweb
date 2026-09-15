import BeforeAfter from './BeforeAfter.astro';
import Callout from './Callout.astro';
import Download from './Download.astro';
import Figure from './Figure.astro';
import NodeGraph from './NodeGraph.astro';
import Numbers from './Numbers.astro';
import SpecTable from './SpecTable.astro';
import TexelCalculator from './TexelCalculator.astro';

/**
 * Components available inside every article and reference page WITHOUT an
 * import line at the top of the .mdx file.
 *
 * Why this exists: articles are edited in a CMS by a non-developer. An import
 * line is the single easiest thing to break, and it is pure noise in a file
 * that is otherwise plain prose. Passing the map to `<Content components={} />`
 * means an author writes `<Callout>` and it just works.
 *
 * To add a component: import it here and add it to the object. Nothing else.
 * The name used in MDX is the key, so keep the keys stable — renaming a key
 * silently breaks every article using it.
 */
export const mdxComponents = {
  BeforeAfter,
  Callout,
  Download,
  Figure,
  NodeGraph,
  Numbers,
  SpecTable,
  TexelCalculator,
};
