#!/usr/bin/env python3
"""
Cover art generator — calm, modern, mostly negative space.

Design brief this satisfies: the previous version was visually loud (dense
contours edge to edge, heavy tint, a label baked in) which fought the layout and
made pages feel cramped. These are the opposite: a dark neutral field, one soft
light source, and a sparse set of thin contour lines that fade out before they
reach the edges. They read as atmosphere, not as illustration — so a real render
dropped in their place is an upgrade, not a different shape.

Still deterministic maths, not generative AI. Same seed, same output.

Usage:  python3 tools/make-art.py
"""

import math
import pathlib

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / 'public' / 'img'

# Neutral base — matches --bg-1 / --bg-2 in global.css
BASE_LO = (10, 10, 12)
BASE_HI = (26, 26, 32)

ACCENTS = {
    'lime':    (190, 242, 100),
    'emerald': (52, 211, 153),
    'sky':     (56, 189, 248),
    'amber':   (251, 191, 36),
    'violet':  (167, 139, 250),
    'neutral': (150, 156, 168),
}


def _smooth_noise(rng, w, h, res):
    g = rng.random((res + 1, res + 1))
    ys = np.linspace(0, res, h, endpoint=False)
    xs = np.linspace(0, res, w, endpoint=False)
    y0, x0 = ys.astype(int), xs.astype(int)
    fy = (ys - y0)[:, None]
    fx = (xs - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy)
    fx = fx * fx * (3 - 2 * fx)
    a = g[np.ix_(y0, x0)]
    b = g[np.ix_(y0, x0 + 1)]
    c = g[np.ix_(y0 + 1, x0)]
    d = g[np.ix_(y0 + 1, x0 + 1)]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def heightmap(w, h, seed, octaves=5, base_res=2):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w))
    amp, total, res = 1.0, 0.0, base_res
    for _ in range(octaves):
        out += _smooth_noise(rng, w, h, res) * amp
        total += amp
        amp *= 0.52
        res *= 2
    out /= total
    out -= out.min()
    return out / max(out.max(), 1e-9)


def cover(w, h, seed, accent='lime', levels=9, glow=0.55, line_alpha=52):
    """A single calm composition. `levels` is deliberately low — sparse lines."""
    acc = ACCENTS[accent]
    rng_angle = (seed * 37) % 360

    field = heightmap(w, h, seed)

    # --- base: a quiet vertical ramp, nothing dramatic ---------------------
    yy, xx = np.mgrid[0:h, 0:w]
    t = (yy / h) * 0.7 + (xx / w) * 0.3
    ramp = np.stack(
        [np.interp(t, [0, 1], [BASE_HI[i], BASE_LO[i]]) for i in range(3)], axis=-1
    )
    im = Image.fromarray(ramp.astype(np.uint8), 'RGB').convert('RGBA')

    # --- one soft off-centre light, tinted with the accent -----------------
    a = math.radians(rng_angle)
    cx = w * (0.5 + 0.26 * math.cos(a))
    cy = h * (0.42 + 0.22 * math.sin(a))
    r = np.sqrt(((xx - cx) / (w * 0.72)) ** 2 + ((yy - cy) / (h * 0.9)) ** 2)
    falloff = np.clip(1 - r, 0, 1) ** 2.2
    gl = np.zeros((h, w, 4), dtype=np.uint8)
    gl[..., 0], gl[..., 1], gl[..., 2] = acc
    gl[..., 3] = (falloff * 255 * glow * 0.22).astype(np.uint8)
    im = Image.alpha_composite(im, Image.fromarray(gl, 'RGBA'))

    # a neutral lift under the same light so it is not purely a colour cast
    lift = np.zeros((h, w, 4), dtype=np.uint8)
    lift[..., 0] = lift[..., 1] = lift[..., 2] = 255
    lift[..., 3] = (falloff * 255 * glow * 0.10).astype(np.uint8)
    im = Image.alpha_composite(im, Image.fromarray(lift, 'RGBA'))

    # --- sparse contour lines, faded at the edges --------------------------
    band = np.floor(field * levels).astype(int)
    edges = np.zeros_like(band, dtype=bool)
    edges[:, 1:] |= band[:, 1:] != band[:, :-1]
    edges[1:, :] |= band[1:, :] != band[:-1, :]

    # fade lines out toward the frame so nothing collides with the border
    fade = np.clip(1 - r * 0.85, 0, 1) ** 1.1

    la = np.zeros((h, w, 4), dtype=np.uint8)
    la[..., 0], la[..., 1], la[..., 2] = acc
    alpha = np.where(edges, (fade * line_alpha), 0)
    la[..., 3] = alpha.astype(np.uint8)
    lines = Image.fromarray(la, 'RGBA').filter(ImageFilter.GaussianBlur(0.55))
    im = Image.alpha_composite(im, lines)

    # --- gentle darkening at the very edges, no hard vignette --------------
    edge = np.clip((r - 0.85) / 0.6, 0, 1) ** 1.5
    vl = np.zeros((h, w, 4), dtype=np.uint8)
    vl[..., 0], vl[..., 1], vl[..., 2] = BASE_LO
    vl[..., 3] = (edge * 150).astype(np.uint8)
    im = Image.alpha_composite(im, Image.fromarray(vl, 'RGBA'))

    return im.convert('RGB')


def save(im, rel):
    p = IMG / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == '.png':
        im.save(p, 'PNG')
    else:
        im.save(p, 'WEBP', quality=88, method=6)
    print(f'  {rel:52s} {im.size[0]}×{im.size[1]}')


def main():
    print('generating cover art:')

    save(cover(2400, 1200, 17, 'lime', levels=7, glow=0.6), 'art/hero.webp')

    save(cover(1600, 900, 101, 'lime', levels=8), 'shipping-kits-01/cover.webp')
    save(cover(1600, 900, 202, 'emerald', levels=9), 'grown-not-placed-01/cover.webp')
    save(cover(1600, 900, 303, 'amber', levels=8), 'breaking-the-tile-01/cover.webp')

    save(cover(1600, 800, 311, 'amber', levels=11, glow=0.4),
         'breaking-the-tile-01/macro-variation-graph.webp')
    save(cover(1600, 800, 221, 'emerald', levels=11, glow=0.4),
         'grown-not-placed-01/wind-graph.webp')

    # before/after: same terrain, different line density, so the slider shows
    # a real difference rather than two unrelated pictures
    save(cover(1400, 800, 777, 'amber', levels=3, glow=0.34, line_alpha=40),
         'breaking-the-tile-01/before.webp')
    save(cover(1400, 800, 777, 'amber', levels=13, glow=0.5, line_alpha=58),
         'breaking-the-tile-01/after.webp')

    for slug, seed, acc in [
        ('sumava', 411, 'emerald'),
        ('ww1', 422, 'amber'),
        ('greek', 433, 'lime'),
        ('cabin', 444, 'neutral'),
        ('fort', 455, 'emerald'),
    ]:
        save(cover(1200, 800, seed, acc, levels=8), f'art/scene-{slug}.webp')

    save(cover(1200, 630, 88, 'lime', levels=7, glow=0.62), 'og-default.png')
    print('done')


if __name__ == '__main__':
    main()
