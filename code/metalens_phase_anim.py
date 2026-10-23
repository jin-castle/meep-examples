"""Animation: ideal-lens phase cut -> wrap (fold by 2pi) -> sample -> revolve to a
circular phase map -> square-lattice pixels -> PB fins (theta = phi/2).

usage: python pb_anim.py out.gif [fps] [dpi] [preview_dir]
preview_dir (optional): also dump a few key frames as PNG.
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import Circle

plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
out = sys.argv[1]
fps = int(sys.argv[2]) if len(sys.argv) > 2 else 15
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 80
preview_dir = sys.argv[4] if len(sys.argv) > 4 else None

lam, U, f = 0.532, 0.25, 10.0      # um
k = 2 * np.pi / lam
ncell = 20
a = (ncell + 0.5) * U              # aperture radius
TWO_PI = 2 * np.pi
cmap = plt.get_cmap("twilight")


def phase(r):
    return -k * (np.sqrt(r**2 + f**2) - f)


def ease(t):
    return 0.5 - 0.5 * np.cos(np.pi * np.clip(t, 0, 1))


# ---- 1D cut ----
x1 = np.linspace(-a, a, 801)                 # contains x = 0
phi1 = phase(x1)
wrap1 = np.mod(phi1, TWO_PI)
m1 = np.round((wrap1 - phi1) / TWO_PI).astype(int)   # number of 2pi lifts per point
M = int(m1.max())
xc = np.arange(-ncell, ncell + 1) * U
phc = np.mod(phase(xc), TWO_PI)

# ---- 2D maps ----
g = np.linspace(-a, a, 401)
GX, GY = np.meshgrid(g, g)
GR = np.hypot(GX, GY)
wrap2 = np.where(GR <= a, np.mod(phase(GR), TWO_PI), np.nan)
ang2 = np.mod(np.arctan2(GY, GX), np.pi)
IX, IY = np.meshgrid(xc, xc)
IR = np.hypot(IX, IY)
pix = np.where(IR <= a, np.mod(phase(IR), TWO_PI), np.nan)

# fins (inside aperture), theta = phi / 2
L, W = 0.20, 0.07
fin_r, fin_poly, fin_col = [], [], []
for xx, yy, rr in zip(IX.ravel(), IY.ravel(), IR.ravel()):
    if rr > a:
        continue
    ph = np.mod(phase(rr), TWO_PI)
    t = ph / 2
    pts = np.array([[-L / 2, -W / 2], [L / 2, -W / 2], [L / 2, W / 2], [-L / 2, W / 2]])
    rot = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    fin_r.append(rr)
    fin_poly.append(pts @ rot.T + [xx, yy])
    fin_col.append(cmap(ph / TWO_PI))
fin_r = np.array(fin_r)

# ---- timeline ----
stages = ([("draw", 30), ("hold1", 8)] + [(f"lift{j}", 20) for j in range(1, M + 1)]
          + [("hold2", 22), ("sample", 26), ("hold3", 10), ("turn", 26), ("revolve", 75),
             ("hold4", 8), ("pixel", 20), ("fins", 40), ("end", 30)])
frames = []
for name, n in stages:
    frames += [(name, i / max(n - 1, 1)) for i in range(n)]
order = [s for s, _ in stages]

fig = plt.figure(figsize=(14, 7))
ax3 = fig.add_axes([-0.02, 0.02, 0.58, 0.84], projection="3d")
ax2 = fig.add_axes([0.60, 0.10, 0.36, 0.72])
axz1 = fig.add_axes([0.03, 0.12, 0.24, 0.62])
axz2 = fig.add_axes([0.31, 0.12, 0.24, 0.62])
ZOOM_HW = 0.9
ZOOMS = [(axz1, 0.0), (axz2, 4.0)]          # (axis, center x) on the y = 0 line
cap = fig.text(0.5, 0.93, "", ha="center", va="center", fontsize=17, fontweight="bold")
sub = fig.text(0.5, 0.875, "", ha="center", va="center", fontsize=12, color="0.3")


def after(stage, ref):
    return order.index(stage) > order.index(ref)


def broken(x, z, m):
    idx = np.where(np.diff(m) != 0)[0] + 1
    return np.insert(x, idx, np.nan), np.insert(z, idx, np.nan)


def stair(sel):
    xs, zs = [], []
    for xx, pp in zip(xc[sel], phc[sel]):
        xs += [xx - U / 2, xx + U / 2]
        zs += [pp, pp]
    return np.array(xs), np.array(zs)


# zone boundaries (phase = -2pi m): one surface per zone so the 2pi cliffs are not drawn as walls
r_bounds = [0.0] + [b for b in (np.sqrt((f + m * lam)**2 - f**2) for m in range(1, M + 1)) if b < a] + [a]


def surface(alpha_rad):
    n_ang = max(2, int(np.rad2deg(alpha_rad) / 3) + 2)
    for start in (0, np.pi):                   # a diameter sweeps both half-planes
        angs = np.linspace(start, start + alpha_rad, n_ang)
        for r0, r1 in zip(r_bounds[:-1], r_bounds[1:]):
            r_s = np.linspace(r0 + 1e-4, r1 - 1e-4, 14)
            X = np.outer(r_s, np.cos(angs))
            Y = np.outer(r_s, np.sin(angs))
            Z = np.mod(phase(r_s), TWO_PI)[:, None] * np.ones_like(angs)[None, :]
            ax3.plot_surface(X, Y, Z, facecolors=cmap(Z / TWO_PI), rstride=1, cstride=1,
                             shade=False, linewidth=0, antialiased=False)


def setup3d(zlo, zhi, elev, azim, ticks):
    ax3.set_xlim(-a, a)
    ax3.set_ylim(-a, a)
    ax3.set_zlim(zlo, zhi)
    ax3.view_init(elev=elev, azim=azim)
    ax3.set_xlabel("x (μm)")
    ax3.set_ylabel("y (μm)")
    ax3.set_zlabel("위상 φ")
    ax3.set_zticks([v for v, _ in ticks], [s for _, s in ticks])


UNWRAP_TICKS = [(-4 * np.pi, "−4π"), (-2 * np.pi, "−2π"), (0, "0"), (2 * np.pi, "2π")]
WRAP_TICKS = [(0, "0"), (np.pi, "π"), (TWO_PI, "2π")]


def top_base(title):
    ax2.set_xlim(-a * 1.05, a * 1.05)
    ax2.set_ylim(-a * 1.05, a * 1.05)
    ax2.set_aspect("equal")
    ax2.add_patch(Circle((0, 0), a, fill=False, ec="0.5", lw=1, ls="--"))
    ax2.set_xlabel("x (μm)")
    ax2.set_ylabel("y (μm)")
    ax2.set_title(title, fontsize=12)


def colored_cut(sel):
    pts = np.column_stack([x1[sel], np.zeros(sel.sum())])
    segs = np.stack([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(segs, colors=cmap(wrap1[sel][:-1] / TWO_PI), linewidths=7)
    ax2.add_collection(lc)


def neighbor_step(xx):
    """fin-angle difference between neighbouring cells along the radial direction (deg)."""
    return 180 * U * (xx / np.sqrt(xx**2 + f**2)) / lam


def zoom(ax, cx, sel):
    ax.set_visible(True)
    ax.imshow(pix, extent=[-a, a, -a, a], origin="lower", cmap=cmap, vmin=0, vmax=TWO_PI,
              alpha=0.3, interpolation="nearest")
    if sel.any():
        ax.add_collection(PolyCollection([p for p, s in zip(fin_poly, sel) if s],
                                         facecolors=[c for c, s in zip(fin_col, sel) if s],
                                         edgecolors="k", linewidths=0.8))
    ax.set_xlim(cx - ZOOM_HW, cx + ZOOM_HW)
    ax.set_ylim(-ZOOM_HW, ZOOM_HW)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    where = "중앙" if cx == 0 else f"가장자리 x≈{cx:.0f} μm"
    step = neighbor_step(U / 2) if cx == 0 else neighbor_step(cx)
    ax.set_title(f"{where} 확대\n이웃 fin 각도 차 ≈ {step:.0f}°", fontsize=12)


def update(i):
    stage, t = frames[i]
    ax3.cla()
    ax2.cla()
    ax3.set_visible(True)
    for axz, _ in ZOOMS:
        axz.cla()
        axz.set_visible(False)
    zlo, zhi = -15.5, 7.2

    # ---------- stages 1-3: 1D cut in the front view ----------
    if stage in ("draw", "hold1") or stage.startswith("lift") or stage in ("hold2", "sample", "hold3"):
        if stage == "hold2":
            zlo = -15.5 + (15.5 - 0.8) * ease(t / 0.6)
        if stage in ("sample", "hold3"):
            zlo = -0.8
        ticks = UNWRAP_TICKS if zlo < -3 else WRAP_TICKS
        setup3d(zlo, zhi, 4, -90, ticks)
        for j in range(0, M + 1):
            if -j * TWO_PI >= zlo:
                ax3.plot([-a, a], [0, 0], [-j * TWO_PI] * 2, color="0.75", lw=0.8, ls="--")
        ax3.plot([-a, a], [0, 0], [TWO_PI] * 2, color="0.75", lw=0.8, ls="--")
        top_base("위에서 본 모습 (색 = 위상, 0과 2π는 같은 색)")

        if stage in ("draw", "hold1"):
            reach = a * (ease(t) if stage == "draw" else 1)
            sel = np.abs(x1) <= reach + 1e-9
            ax3.plot(x1[sel], np.zeros(sel.sum()), phi1[sel], color="C0", lw=2.5)
            colored_cut(sel)
            cap.set_text("① 이상적 렌즈 위상의 단면  φ(x) = −k(√(x²+f²) − f)")
            sub.set_text("가장자리로 갈수록 빛이 더 먼 길을 가므로 위상을 계속 빼 준다 (접기 전: 매끄러운 곡선)")
        elif stage.startswith("lift"):
            j = int(stage[4:])
            lifts = np.minimum(m1, j - 1) + (m1 >= j) * ease(t)
            z = phi1 + TWO_PI * lifts
            ax3.plot(x1, np.zeros_like(x1), phi1, color="0.85", lw=1)
            still = m1 < j
            for mask, col in ((still, "C0"), (~still, "C1")):
                xs, zs = broken(np.where(mask, x1, np.nan), np.where(mask, z, np.nan), m1)
                ax3.plot(xs, np.zeros_like(xs), zs, color=col, lw=2.5)
            ax3.scatter([0], [0], [0], color="C3", s=30, depthshade=False)
            colored_cut(np.ones_like(x1, bool))
            cap.set_text(f"② 0 아래로 내려간 부분을 2π씩 올려 접기  ({j}/{M})")
            sub.set_text("2π 차이는 같은 위상 → 빛 입장에서는 아무것도 바뀌지 않는다 (오른쪽 색도 그대로)")
        elif stage == "hold2":
            xs, zs = broken(x1, wrap1, m1)
            ax3.plot(xs, np.zeros_like(xs), zs, color="C0", lw=2.5)
            ax3.scatter([0], [0], [0], color="C3", s=40, depthshade=False)
            ax3.text(0.25, 0, 0.35, "φ=0 ≡ 2π", color="C3", fontsize=11)
            colored_cut(np.ones_like(x1, bool))
            cap.set_text("② 결과: 0~2π 사이의 톱니 (Fresnel 렌즈와 같은 원리)")
            sub.set_text("빨간 점 = 중앙 φ=0 (≡2π) → 계단 그림 중앙의 0.  바깥으로 갈수록 톱니가 좁아짐 = 빛을 꺾는 각도가 커짐")
        else:  # sample / hold3
            xs, zs = broken(x1, wrap1, m1)
            ax3.plot(xs, np.zeros_like(xs), zs, color="0.7", lw=1)
            reach = a * (ease(t) if stage == "sample" else 1)
            sel = np.abs(xc) <= reach + 1e-9
            sx, sz = stair(sel)
            ax3.plot(sx, np.zeros_like(sx), sz, color="C3", lw=2.2)
            colored_cut(np.ones_like(x1, bool))
            cap.set_text("③ 격자 간격(250 nm)마다 샘플링 → 계단 위상")
            sub.set_text("메타표면은 격자 칸마다 위상 하나만 줄 수 있다 (칸당 변화 < π 이면 충분)")
        return

    # ---------- stage 4: turn camera, then revolve ----------
    if stage == "turn":
        e = ease(t)
        setup3d(-0.8, zhi, 4 + 24 * e, -90 + 32 * e, WRAP_TICKS)
        sx, sz = stair(np.ones_like(xc, bool))
        ax3.plot(sx, np.zeros_like(sx), sz, color="C3", lw=2.2, alpha=1 - e)
        xs, zs = broken(x1, wrap1, m1)
        ax3.plot(xs, np.zeros_like(xs), zs, color="k", lw=2.5, alpha=max(e, 0.05))
        top_base("위에서 본 모습")
        colored_cut(np.ones_like(x1, bool))
        cap.set_text("④ 렌즈는 원형 대칭 → 이 단면을 중심축 둘레로 돌리면?")
        sub.set_text("(계단은 잠시 빼고 연속 단면으로 돌린다)")
        return

    azim0 = -58
    if stage in ("revolve", "hold4"):
        al = np.pi * (ease(t) if stage == "revolve" else 1)
        setup3d(-0.8, zhi, 28 + 6 * ease(t), azim0, WRAP_TICKS)
        if al > 1e-3:
            surface(al)
        xs, zs = broken(x1, wrap1, m1)
        ax3.plot(xs * np.cos(al), xs * np.sin(al), zs, color="k", lw=2.5)
        top_base("위에서 본 모습: 동심원 위상 맵")
        ax2.imshow(np.where(ang2 <= al, wrap2, np.nan), extent=[-a, a, -a, a], origin="lower",
                   cmap=cmap, vmin=0, vmax=TWO_PI, interpolation="nearest")
        ax2.plot([-a * np.cos(al), a * np.cos(al)], [-a * np.sin(al), a * np.sin(al)], color="k", lw=2)
        cap.set_text(f"④ 단면을 축 둘레로 회전: {np.rad2deg(al):.0f}° / 180°")
        sub.set_text("지름 한 줄을 180° 돌리면 원판 전체가 채워진다 → 같은 색 = 같은 위상인 동심원")
        return

    # ---------- stages 5-6: pixels and fins ----------
    top_base("위에서 본 모습")
    if stage == "pixel":
        setup3d(-0.8, zhi, 34 + 20 * ease(t), azim0 + 30 * ease(t), WRAP_TICKS)
        surface(np.pi)
    else:
        ax3.set_visible(False)
    if stage == "pixel":
        e = ease(t)
        ax2.imshow(wrap2, extent=[-a, a, -a, a], origin="lower", cmap=cmap, vmin=0, vmax=TWO_PI,
                   alpha=1 - e, interpolation="nearest")
        ax2.imshow(pix, extent=[-a, a, -a, a], origin="lower", cmap=cmap, vmin=0, vmax=TWO_PI,
                   alpha=e, interpolation="nearest")
        cap.set_text("⑤ 정사각 격자(250 nm)마다 샘플링 → 메타표면의 픽셀 위상 맵")
        sub.set_text("중심 픽셀(0)과 주변(≈2π)은 같은 색 — 0 ≡ 2π 이므로 실제로는 홈이 없다")
        return
    ax2.imshow(pix, extent=[-a, a, -a, a], origin="lower", cmap=cmap, vmin=0, vmax=TWO_PI,
               alpha=0.3, interpolation="nearest")
    reach = a * 1.01 * (ease(t) if stage == "fins" else 1)
    sel = fin_r <= reach
    if sel.any():
        pc = PolyCollection([p for p, s in zip(fin_poly, sel) if s],
                            facecolors=[c for c, s in zip(fin_col, sel) if s],
                            edgecolors="k", linewidths=0.4)
        ax2.add_collection(pc)
    for axz, cx in ZOOMS:
        zoom(axz, cx, sel)
        ax2.add_patch(plt.Rectangle((cx - ZOOM_HW, -ZOOM_HW), 2 * ZOOM_HW, 2 * ZOOM_HW,
                                    fill=False, ec="k", lw=1.5))
    cap.set_text("⑥ 칸마다 fin 각도 θ = φ/2 (PB 위상) → 실제 metalens 배치")
    if stage == "end":
        sub.set_text("fin 색 = 위상 색. 중앙 fin들은 거의 평행(0° ≈ 180°), 바깥으로 갈수록 이웃 각도 차이가 커진다")
    else:
        sub.set_text("한쪽 원편광은 +2θ = φ 를 받아 초점으로 모인다")


if out != "none":
    anim = animation.FuncAnimation(fig, update, frames=len(frames), interval=1000 / fps)
    anim.save(out, writer=animation.PillowWriter(fps=fps), dpi=dpi)
    print("frames:", len(frames), "seconds:", len(frames) / fps, "size MB:", os.path.getsize(out) / 1e6)

if preview_dir:
    keys = {}
    for name in ("hold1", f"lift{M}", "hold2", "hold3", "revolve", "pixel", "end"):
        idxs = [n for n, (s, _) in enumerate(frames) if s == name]
        keys[name] = idxs[len(idxs) // 2] if name == "revolve" else idxs[-1]
    for name, n in keys.items():
        update(n)
        fig.savefig(os.path.join(preview_dir, f"key_{name}.png"), dpi=dpi)

