"""Same square lattice, three ways to fill it:
  (1) identical pillars  -> uniform phase (flat plate, no focusing)
  (2) diameter-varying circular pillars (propagation phase) -> lens
  (3) rotation-varying nanofins (PB phase)                   -> lens
Diameter <-> phase mapping is a linear stand-in for a simulated unit-cell library.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection, PolyCollection
from matplotlib.patches import Circle

lam, U, f = 0.532, 0.25, 10.0     # um
n = 41
idx = np.arange(n) - n // 2
X, Y = np.meshgrid(idx * U, idx * U)
phi = np.mod(-2 * np.pi / lam * (np.sqrt(X**2 + Y**2 + f**2) - f), 2 * np.pi)
dmin, dmax = 0.08, 0.20            # pillar diameter range, um
d = dmin + (dmax - dmin) * phi / (2 * np.pi)
L, W = 0.20, 0.07                  # fin size, um

fig, axs = plt.subplots(2, 3, figsize=(16, 10.5), gridspec_kw={"height_ratios": [3, 1.3]})
h = (n // 2 + 0.6) * U


def frame(ax, title):
    ax.set_xlim(-h, h)
    ax.set_ylim(-h, h)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=11)


ax = axs[0, 0]
ax.add_collection(PatchCollection([Circle((x, y), 0.07) for x, y in zip(X.ravel(), Y.ravel())],
                                  facecolor="steelblue", edgecolor="k", lw=0.3))
frame(ax, "(1) identical unit cells (periodic)\nevery cell: same phase")

ax = axs[0, 1]
pc = PatchCollection([Circle((x, y), dd / 2) for x, y, dd in zip(X.ravel(), Y.ravel(), d.ravel())],
                     cmap="twilight", edgecolor="k", lw=0.3)
pc.set_array(phi.ravel())
pc.set_clim(0, 2 * np.pi)
ax.add_collection(pc)
frame(ax, "(2) propagation phase: diameter varies\n(polarization-insensitive)")

ax = axs[0, 2]
polys = []
for x, y, t in zip(X.ravel(), Y.ravel(), phi.ravel() / 2):
    pts = np.array([[-L / 2, -W / 2], [L / 2, -W / 2], [L / 2, W / 2], [-L / 2, W / 2]])
    rot = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    polys.append(pts @ rot.T + [x, y])
pc2 = PolyCollection(polys, array=phi.ravel(), cmap="twilight", edgecolors="k", linewidths=0.3)
pc2.set_clim(0, 2 * np.pi)
ax.add_collection(pc2)
frame(ax, "(3) PB phase: same fin, rotation = phase/2\n(circular polarization only)")

# phase along the center row
row = n // 2
x = idx * U
target = np.mod(-2 * np.pi / lam * (np.sqrt(x**2 + f**2) - f), 2 * np.pi)
for k, (ax, ph, lab) in enumerate([(axs[1, 0], np.full(n, np.pi), "constant -> flat wavefront"),
                                   (axs[1, 1], phi[row], "sampled lens phase"),
                                   (axs[1, 2], phi[row], "sampled lens phase")]):
    if k:
        ax.plot(x, target, color="0.7", lw=1, label="target (hyperbolic, wrapped)")
    ax.step(x, ph, where="mid", color="C3", lw=1.5, label=lab)
    ax.set_ylim(-0.3, 2 * np.pi + 0.3)
    ax.set_yticks([0, np.pi, 2 * np.pi], ["0", "$\\pi$", "$2\\pi$"])
    ax.set_xlabel("x (um), center row")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=2)
axs[1, 0].set_ylabel("phase")
fig.colorbar(pc, ax=axs[0, :].tolist(), shrink=0.8, label="imparted phase (rad)")
fig.savefig(sys.argv[1], dpi=110, bbox_inches="tight")
