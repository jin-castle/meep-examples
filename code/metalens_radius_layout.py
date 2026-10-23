"""PB(geometric)-phase metalens: how nanofin rotation patterns change with radius.

theta_fin(x, y) = phi(x, y) / 2,  phi = hyperbolic lens phase, sampled on a square lattice.
Illustrative parameters only (not taken from the SEM's source paper).
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

lam = 0.532          # um
U = 0.300            # lattice period, um
L, W = 0.22, 0.08    # fin length / width, um
f = 50.0             # focal length, um
NA = 0.8
R = f * np.tan(np.arcsin(NA))
out = sys.argv[1]


def phase(x, y):
    return -2 * np.pi / lam * (np.sqrt(x**2 + y**2 + f**2) - f)


def r_for_step(dtheta_deg):
    """radius where fin rotation changes by dtheta_deg per lattice cell (radial direction)."""
    s = (2 * dtheta_deg) / 360 * lam / U
    return f * np.tan(np.arcsin(s))


def draw_patch(ax, r0, az_deg, n=12, title=""):
    az = np.deg2rad(az_deg)
    x0 = np.round(r0 * np.cos(az) / U) * U
    y0 = np.round(r0 * np.sin(az) / U) * U
    idx = np.arange(n) - n // 2
    X, Y = np.meshgrid(x0 + idx * U, y0 + idx * U)
    th = (phase(X, Y) / 2) % np.pi
    c, s = np.cos(th), np.sin(th)
    polys = []
    for xc, yc, cc, ss in zip(X.ravel(), Y.ravel(), c.ravel(), s.ravel()):
        pts = np.array([[-L / 2, -W / 2], [L / 2, -W / 2], [L / 2, W / 2], [-L / 2, W / 2]])
        rot = np.array([[cc, -ss], [ss, cc]])
        polys.append((pts @ rot.T) + [xc - x0, yc - y0])
    pc = PolyCollection(polys, array=np.rad2deg(th.ravel()), cmap="twilight",
                        edgecolors="k", linewidths=0.4)
    pc.set_clim(0, 180)
    ax.add_collection(pc)
    h = (n // 2 + 0.6) * U
    ax.set_xlim(-h, h)
    ax.set_ylim(-h, h)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    # radial direction arrow
    ax.annotate("", xy=(0.8 * h * np.cos(az), 0.8 * h * np.sin(az)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="red", lw=1.5), annotation_clip=False)
    ax.set_title(title, fontsize=10)
    return pc


fig, axs = plt.subplots(2, 3, figsize=(15, 10))

# (a) wrapped phase map
g = np.linspace(-R, R, 1200)
GX, GY = np.meshgrid(g, g)
ph = np.mod(phase(GX, GY), 2 * np.pi)
ph[GX**2 + GY**2 > R**2] = np.nan
axs[0, 0].imshow(ph, extent=[-R, R, -R, R], origin="lower", cmap="twilight")
axs[0, 0].set_title(f"(a) wrapped lens phase  (NA={NA}, f={f:.0f} um, $\\lambda$={lam*1e3:.0f} nm)", fontsize=10)
axs[0, 0].set_xlabel("x (um)")
axs[0, 0].set_ylabel("y (um)")

# (b) rotation step per cell vs r
r = np.linspace(0, R, 400)
sin_t = r / np.sqrt(r**2 + f**2)
dtheta = 180 * U * sin_t / lam   # deg per cell (fin rotation = phase/2)
ax = axs[0, 1]
ax.plot(r, dtheta, "k")
for v, lab in [(15, "12 cells / turn"), (45, "4 cells"), (60, "3 cells -> 0/60/120 deg only")]:
    ax.axhline(v, ls="--", lw=0.8, color="gray")
    ax.text(1, v + 1.5, f"{v} deg/cell : {lab}", fontsize=8)
ax.set_xlabel("r (um)")
ax.set_ylabel("fin rotation step per lattice cell (deg)")
ax.set_title("(b) phase gradient grows toward the edge", fontsize=10)
ax.set_xlim(0, R)

draw_patch(axs[0, 2], 0.0, 0, title="(c) center: r = 0  (fins nearly parallel)")
draw_patch(axs[1, 0], r_for_step(15), 0, title=f"(d) r = {r_for_step(15):.1f} um : 15 deg/cell")
draw_patch(axs[1, 1], r_for_step(60), 0, title=f"(e) r = {r_for_step(60):.1f} um, az 0 deg : 60 deg/cell")
pc = draw_patch(axs[1, 2], r_for_step(60), 45, title=f"(f) r = {r_for_step(60):.1f} um, az 45 deg : 60 deg/cell")
fig.colorbar(pc, ax=axs[1, :], shrink=0.7, label="fin angle (deg)")
fig.savefig(out, dpi=130, bbox_inches="tight")
print("R =", R, " r(60deg/cell) =", r_for_step(60))
