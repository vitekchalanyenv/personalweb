#!/usr/bin/env python3
"""
Turn dist/ into something that opens by double-clicking index.html.

Two jobs:
1. Rewrite site-absolute URLs (/articles/) to document-relative ones, because
   file:// has no site root.
2. Inject a preview-only palette + theme switcher so the accent colour can be
   judged by eye. This is NOT part of the real site — it exists only in the
   offline preview build.
"""

import re
import pathlib

DIST = pathlib.Path(__file__).resolve().parent.parent / 'dist'

ATTR = re.compile(r'''(\s(?:href|src|content)\s*=\s*)(["'])/(?!/)([^"']*)\2''')
# url(/_astro/x.woff2) inside a stylesheet — same problem, different syntax.
CSS_URL = re.compile(r'''url\((['"]?)/(?!/)([^)'"]+)\1\)''')

SWITCHER = """
<div id="pv-switch">
  <div class="pv-row">
    <span class="pv-l">Accent</span>
    <button data-ac="lime">Lime</button>
    <button data-ac="emerald">Emerald</button>
    <button data-ac="sky">Sky</button>
    <button data-ac="amber">Amber</button>
    <button data-ac="violet">Violet</button>
  </div>
  <div class="pv-row">
    <span class="pv-l">Theme</span>
    <button data-th="dark">Dark</button>
    <button data-th="light">Light</button>
  </div>
  <button id="pv-hide" title="Hide">×</button>
</div>
<style>
  #pv-switch {
    position: fixed; left: 50%; bottom: 18px; transform: translateX(-50%);
    z-index: 999; display: flex; gap: 18px; align-items: center;
    background: rgba(20,20,24,.92); backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,.13); border-radius: 100px;
    padding: 9px 14px 9px 18px; box-shadow: 0 12px 40px -12px rgba(0,0,0,.7);
    font: 12px/1 ui-sans-serif, system-ui, sans-serif; color: #eee;
    flex-wrap: wrap; max-width: calc(100vw - 24px);
  }
  #pv-switch .pv-row { display: flex; gap: 5px; align-items: center; }
  #pv-switch .pv-l {
    font-size: 10px; text-transform: uppercase; letter-spacing: .1em;
    color: #8b8f99; margin-right: 3px;
  }
  #pv-switch button {
    background: transparent; border: 1px solid rgba(255,255,255,.16);
    color: #cfd2d8; border-radius: 100px; padding: 6px 12px; cursor: pointer;
    font: inherit; transition: .15s;
  }
  #pv-switch button:hover { border-color: rgba(255,255,255,.4); color: #fff; }
  #pv-switch button[aria-pressed="true"] { background: #fff; color: #111; border-color: #fff; }
  #pv-hide {
    border: 0 !important; color: #8b8f99 !important; font-size: 17px !important;
    padding: 2px 6px !important; margin-left: 2px;
  }
  @media (max-width: 640px) { #pv-switch { font-size: 11px; padding: 8px 10px; } }
</style>
<script>
(function () {
  var root = document.documentElement;
  var KEY_A = 'pv-accent', KEY_T = 'theme';
  function get(k, d) { try { return localStorage.getItem(k) || d; } catch (e) { return d; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  var accent = get(KEY_A, 'lime');
  root.setAttribute('data-accent', accent);

  function sync() {
    var a = root.getAttribute('data-accent') || 'lime';
    var t = root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
    document.querySelectorAll('#pv-switch [data-ac]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.ac === a));
    });
    document.querySelectorAll('#pv-switch [data-th]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.th === t));
    });
  }

  document.querySelectorAll('#pv-switch [data-ac]').forEach(function (b) {
    b.addEventListener('click', function () {
      root.setAttribute('data-accent', b.dataset.ac);
      set(KEY_A, b.dataset.ac);
      sync();
    });
  });
  document.querySelectorAll('#pv-switch [data-th]').forEach(function (b) {
    b.addEventListener('click', function () {
      if (b.dataset.th === 'light') root.setAttribute('data-theme', 'light');
      else root.removeAttribute('data-theme');
      set(KEY_T, b.dataset.th);
      sync();
    });
  });
  document.getElementById('pv-hide').addEventListener('click', function () {
    document.getElementById('pv-switch').remove();
  });
  sync();
})();
</script>
"""


def relativise(path: pathlib.Path) -> int:
    depth = len(path.parent.relative_to(DIST).parts)
    prefix = '../' * depth if depth else './'

    def repl(m):
        pre, q, target = m.group(1), m.group(2), m.group(3)
        if target == '' or target.endswith('/'):
            target += 'index.html'
        return f'{pre}{q}{prefix}{target}{q}'

    text = path.read_text(encoding='utf-8')
    text, n = ATTR.subn(repl, text)

    if '</body>' in text and 'pv-switch' not in text:
        text = text.replace('</body>', SWITCHER + '\n</body>')

    path.write_text(text, encoding='utf-8')
    return n


def relativise_css(path: pathlib.Path) -> int:
    """Font and image URLs inside built CSS are site-absolute too."""
    depth = len(path.parent.relative_to(DIST).parts)
    prefix = '../' * depth if depth else './'
    text = path.read_text(encoding='utf-8')
    text, n = CSS_URL.subn(lambda m: f'url({prefix}{m.group(2)})', text)
    if n:
        path.write_text(text, encoding='utf-8')
    return n


def main():
    total = 0
    files = list(DIST.rglob('*.html'))
    for f in files:
        total += relativise(f)
    css_files = list(DIST.rglob('*.css'))
    css_n = sum(relativise_css(f) for f in css_files)
    print(f'offline: {css_n} css urls rewritten across {len(css_files)} stylesheets')
    for junk in DIST.glob('sitemap*.xml'):
        junk.unlink()
    print(f'offline: {total} paths rewritten across {len(files)} files, switcher injected')


if __name__ == '__main__':
    main()
