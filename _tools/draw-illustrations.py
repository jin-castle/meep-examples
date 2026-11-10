"""Concept illustrations for chapters that were not produced with the image generator.

Draws orthographic, shaded apparatus illustrations with matplotlib only (no simulation
data). Output follows the variant contract assets/illustrations/XX.{ko|en}.{light|dark}.png
at 1620 x 972 px. Run from any directory:

    python _tools/draw-illustrations.py            # all chapters defined below
    python _tools/draw-illustrations.py 16 28      # selected chapters
"""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Polygon

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "illustrations"
W, H = 16.2, 9.72  # inches at dpi 100 -> 1620 x 972

THEMES = {
    "light": dict(bg="#ffffff", text="#526579", blue="#76b6da", pale="#c9dce8", plane="#edf3f6",
                  glass="#a9cfe6", metal="#899baa", amber="#e3a331", teal="#0087ad", ink="#526579",
                  grid="#b8c6d2"),
    "dark": dict(bg="#0d1722", text="#e8eef4", blue="#8ac4e6", pale="#3c5a73", plane="#1b2a3a",
                  glass="#5f93b8", metal="#6f8191", amber="#f0b347", teal="#35b5dc", ink="#0d1722",
                  grid="#2d4257"),
}
TITLES = {
    "16": {"ko": "영역판과 셀 밖의 초점", "en": "Zone plate focus outside the cell"},
    "28": {"ko": "나란한 두 도파로 사이의 힘", "en": "Force between two parallel waveguides"},
}
CAPTION = {"ko": "개념도 · 계산 결과 아님", "en": "Concept illustration · not simulation data"}
LIGHT = (-0.35, -0.45, 0.82)


def font(locale, weight="bold"):
    name = "Malgun Gothic" if locale == "ko" else "Segoe UI"
    try:
        path = font_manager.findfont(font_manager.FontProperties(family=name, weight=weight), fallback_to_default=False)
        return font_manager.FontProperties(fname=path)
    except Exception:
        return font_manager.FontProperties(weight=weight)


def project(p):
    x, y, z = p
    return (0.866 * x - 0.5 * y, -(0.25 * x + 0.433 * y) + 0.866 * z)


def rgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def mix(a, b, t):
    return [a[i] * (1 - t) + b[i] * t for i in range(3)]


def shade(hexcolor, normal, theme):
    k = sum(n * l for n, l in zip(normal, LIGHT))
    c = rgb(hexcolor)
    if k > 0:
        return mix(c, [1, 1, 1], min(0.45, k * 0.42))
    return mix(c, rgb(theme["ink"]), min(0.5, -k * 0.5))


def poly(ax, pts3, color, z=1, alpha=1.0, edge=None, lw=0.8):
    pts = [project(p) for p in pts3]
    ax.add_patch(Polygon(pts, closed=True, facecolor=color, edgecolor=edge or color, lw=lw, alpha=alpha, zorder=z))


def box(ax, x0, x1, y0, y1, z0, z1, color, theme, z=1, alpha=1.0):
    """Visible faces for the camera: top (+z), right (+x), front (+y)."""
    poly(ax, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], shade(color, (0, 1, 0), theme), z, alpha)
    poly(ax, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], shade(color, (1, 0, 0), theme), z, alpha)
    poly(ax, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], shade(color, (0, 0, 1), theme), z, alpha)


def arrow(ax, p0, p1, color, lw=4, z=10, head=0.5, alpha=1.0):
    a, b = project(p0), project(p1)
    ax.annotate("", xy=b, xytext=a, zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=18 * head * 2, alpha=alpha,
                                shrinkA=0, shrinkB=0))


def ring_pts(r, z, n=96):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), z) for i in range(n)]


def annulus(ax, r_in, r_out, z, color, zorder, edge):
    outer = [project(p) for p in ring_pts(r_out, z)]
    inner = [project(p) for p in ring_pts(r_in, z)][::-1]
    ax.add_patch(Polygon(outer + inner, closed=True, facecolor=color, edgecolor=edge, lw=1.0, zorder=zorder))


def frame(locale, theme_name):
    th = THEMES[theme_name]
    fig = plt.figure(figsize=(W, H), dpi=100, facecolor=th["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(th["bg"])
    ax.set_axis_off()
    ax.set_aspect("equal")
    return fig, ax, th


def labels(fig, chapter, locale, th):
    fp = font(locale)
    fig.text(0.04, 0.905, TITLES[chapter][locale], fontproperties=fp, fontsize=40, color=th["text"], va="center")
    fp2 = font(locale, "normal")
    fig.text(0.04, 0.075, CAPTION[locale], fontproperties=fp2, fontsize=21, color=th["text"], va="center")


# ----------------------------------------------------------------------------- chapter 16
def draw_16(locale, theme_name):
    fig, ax, th = frame(locale, theme_name)
    ax.set_xlim(-11.5, 11.5)
    ax.set_ylim(-7.4, 6.4)
    # glass substrate slab (cropped, wide)
    box(ax, -6.5, 6.5, -6.5, 6.5, -1.2, 0, th["glass"], th, z=1)
    # binary-phase zones: raised glass annuli, r_n ~ sqrt(n)
    N = 9
    radii = [1.45 * math.sqrt(n) for n in range(1, N + 1)]
    top_color = shade(th["blue"], (0, 0, 1), th)
    side_color = shade(th["blue"], (0, 1, 0), th)
    for n in range(N - 1, -1, -1):
        if n % 2 == 0:
            r_out = radii[n]
            if n == 0:
                poly(ax, ring_pts(r_out, 0.0), side_color, z=2)
                poly(ax, ring_pts(r_out, 0.35), top_color, z=3, edge=mix(rgb(th["blue"]), rgb(th["ink"]), 0.25))
                continue
            r_in = radii[n - 1]
            # side wall hint (slightly lower annulus drawn darker, offset in z)
            annulus(ax, r_in, r_out, 0.0, side_color, 2, side_color)
            annulus(ax, r_in, r_out, 0.35, top_color, 3, mix(rgb(th["blue"]), rgb(th["ink"]), 0.25))
    # incident planewave from below (amber arrows through the substrate)
    for x in [-5.2, -3.2, -1.2, 0.8, 2.8, 4.8]:
        arrow(ax, (x, 6.5, -1.1), (x, 6.5, -0.15), th["amber"], lw=3.2, head=0.42, z=2.5, alpha=0.95)
    for y in [-4.5, -2.0, 0.5, 3.0]:
        arrow(ax, (6.5, y, -1.1), (6.5, y, -0.15), th["amber"], lw=3.2, head=0.42, z=2.5, alpha=0.95)
    # near2far surface: translucent teal plane above the plate
    zt = 1.1
    poly(ax, [(-5.4, -5.4, zt), (5.4, -5.4, zt), (5.4, 5.4, zt), (-5.4, 5.4, zt)], th["teal"], z=4, alpha=0.10,
         edge=th["teal"], lw=2.0)
    # converging rays from the zone edges to the focus
    focus = (0, 0, 4.3)
    for r in [radii[0], radii[2], radii[4], radii[6], radii[8]]:
        for phi in [0.35, 1.3, 2.4, 3.6, 4.6, 5.6]:
            p0 = (r * math.cos(phi), r * math.sin(phi), 0.35)
            a, b = project(p0), project(focus)
            ax.plot([a[0], b[0]], [a[1], b[1]], color=th["teal"], lw=1.3, alpha=0.55, zorder=5,
                    solid_capstyle="round")
    for phi in [0.9, 2.8, 4.9]:
        r = radii[7]
        p0 = (r * math.cos(phi), r * math.sin(phi), 0.35)
        arrow(ax, p0, (p0[0] * 0.1, p0[1] * 0.1, 3.85), th["teal"], lw=2.2, head=0.4, z=6)
    # focal spot
    fx, fy = project(focus)
    for rad, al in [(0.7, 0.12), (0.48, 0.25), (0.3, 0.9)]:
        ax.add_patch(Circle((fx, fy), rad, facecolor=th["amber"], edgecolor="none", alpha=al, zorder=8))
    ax.add_patch(Circle((fx, fy), 0.14, facecolor="#fff3d6", edgecolor="none", zorder=9))
    # thin axis line
    ax.plot([project((0, 0, 0.35))[0], fx], [project((0, 0, 0.35))[1], fy], color=th["grid"], lw=1.2, ls=(0, (4, 4)), zorder=4)
    labels(fig, "16", locale, th)
    return fig


# ----------------------------------------------------------------------------- chapter 28
def draw_28(locale, theme_name):
    fig, ax, th = frame(locale, theme_name)
    ax.set_xlim(-11.5, 11.5)
    ax.set_ylim(-6.9, 6.9)
    a, gap = 2.0, 1.1
    y0, y1 = -9.0, 5.0
    zc = 0.0
    # faint base plane for depth
    poly(ax, [(-9, y0, -3.2), (9, y0, -3.2), (9, y1 + 1, -3.2), (-9, y1 + 1, -3.2)], th["plane"], z=0, alpha=1.0,
         edge=th["plane"])
    xl0, xl1 = -gap / 2 - a, -gap / 2
    xr0, xr1 = gap / 2, gap / 2 + a
    # evanescent coupling in the gap: amber translucent band along the length
    for k, al in [(0.0, 0.22), (0.3, 0.16)]:
        poly(ax, [(xl1, y0, zc - a / 2 + k), (xr0, y0, zc - a / 2 + k), (xr0, y1, zc - a / 2 + k), (xl1, y1, zc - a / 2 + k)],
             th["amber"], z=2, alpha=al, edge="none", lw=0)
    # two silicon rods along y
    box(ax, xl0, xl1, y0, y1, zc - a / 2, zc + a / 2, th["blue"], th, z=3)
    box(ax, xr0, xr1, y0, y1, zc - a / 2, zc + a / 2, th["blue"], th, z=3)
    # mode lobes on the front faces (y = y1)
    for cx in [(xl0 + xl1) / 2, (xr0 + xr1) / 2]:
        c = project((cx, y1, zc))
        for rad, al in [(0.95, 0.18), (0.68, 0.35), (0.42, 0.85)]:
            ax.add_patch(Circle(c, rad, facecolor=th["amber"], edgecolor="none", alpha=al, zorder=6))
    # attractive force arrows in the gap, at the front end
    yf = y1 + 0.9
    arrow(ax, (xl0 - 1.1, yf, zc), (xl1 - 0.05, yf, zc), th["teal"], lw=5, head=0.6, z=9)
    arrow(ax, (xr1 + 1.1, yf, zc), (xr0 + 0.05, yf, zc), th["teal"], lw=5, head=0.6, z=9)
    # propagation direction hint along the rods
    arrow(ax, (xr1 + 1.3, -6.5, zc + a / 2 + 0.2), (xr1 + 1.3, -1.5, zc + a / 2 + 0.2), th["grid"], lw=2.2, head=0.4, z=5, alpha=0.9)
    labels(fig, "28", locale, th)
    return fig


DRAW = {"16": draw_16, "28": draw_28}


def main(argv):
    chapters = argv or list(DRAW)
    OUT.mkdir(parents=True, exist_ok=True)
    for ch in chapters:
        for locale in ("ko", "en"):
            for theme_name in ("light", "dark"):
                fig = DRAW[ch](locale, theme_name)
                path = OUT / f"{ch}.{locale}.{theme_name}.png"
                fig.savefig(path, dpi=100, facecolor=fig.get_facecolor())
                plt.close(fig)
                print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main(sys.argv[1:])
