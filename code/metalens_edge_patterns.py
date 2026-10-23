"""Nanofin patterns near the edge of a PB (geometric-phase) metalens.

Near the edge the lens phase is locally a linear ramp, so the fin angle is
    theta(i, j) = dth * (cos(az) * X + sin(az) * Y)   (mod 180 deg)
with dth = fin-rotation step per lattice cell along the radial direction and az the
radial direction measured from the lattice x axis.
Top row: 35-deg tilted grey view (how a tilted SEM image looks). Bottom row: top view
coloured by fin angle.

usage: python metalens_edge_patterns.py out.png
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

plt.rcParams["font.family"] = ["Malgun Gothic", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

U_NM = 250                     # lattice period used for the length labels
L, W = 0.72, 0.27              # fin size in units of the lattice period
n = 14
cases = [("hex", 60, 0), ("hex", 80, 0), ("square", 60, 45)]
names = {"hex": "육방 격자", "square": "정사각 격자"}


def fins(ax, lat, dth, az, tilt, colored):
    I, J = np.meshgrid(np.arange(n), np.arange(n))
    X, Y = (I + 0.5 * (J % 2), J * np.sqrt(3) / 2) if lat == "hex" else (I * 1.0, J * 1.0)
    a = np.deg2rad(az)
    th = (dth * (np.cos(a) * X + np.sin(a) * Y)) % 180
    polys = []
    for xc, yc, t in zip(X.ravel(), Y.ravel(), np.deg2rad(th.ravel())):
        rot = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
        p = np.array([[-L / 2, -W / 2], [L / 2, -W / 2], [L / 2, W / 2], [-L / 2, W / 2]]) @ rot.T + [xc, yc]
        p[:, 1] *= tilt
        polys.append(p * U_NM / 1000)          # lattice units -> um
    if colored:
        pc = PolyCollection(polys, array=th.ravel(), cmap="twilight", edgecolors="k", linewidths=0.4)
        pc.set_clim(0, 180)
    else:
        pc = PolyCollection(polys, facecolors="0.8", edgecolors="0.5", linewidths=0.4)
    ax.add_collection(pc)
    s = U_NM / 1000
    ax.set_xlim(2 * s, (n - 3) * s)
    ax.set_ylim(2 * s * tilt, (n - 3) * s * tilt * (np.sqrt(3) / 2 if lat == "hex" else 1))
    ax.set_aspect("equal")
    ax.set_xlabel("x (μm)")
    return pc


fig, axs = plt.subplots(2, 3, figsize=(17, 11.5))
for c, (lat, dth, az) in enumerate(cases):
    ax = axs[0, c]
    ax.set_facecolor("0.25")
    fins(ax, lat, dth, az, np.cos(np.deg2rad(35)), False)
    ax.set_yticks([])
    ax.set_title(f"{names[lat]} · 이웃 각도 차 {dth}°/칸 · 반경 방향 {az}°\n35° 기울여 본 모습", fontsize=12)
    pc = fins(axs[1, c], lat, dth, az, 1.0, True)
    axs[1, c].set_ylabel("y (μm)")
    axs[1, c].set_title("위에서 본 모습 (색 = fin 각도)", fontsize=12)
fig.colorbar(pc, ax=axs[1, :].tolist(), shrink=0.8, label="fin 각도 (°)")
fig.suptitle(f"PB metalens 가장자리의 fin 배열: 위상 램프를 격자({U_NM} nm)로 샘플링한 결과", fontsize=16, y=0.98)
fig.savefig(sys.argv[1], dpi=100, bbox_inches="tight")
