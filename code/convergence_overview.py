"""convergence_overview.py — how much each published quantity moved between two resolutions (concept pages:
convergence check, energy conservation). No new simulation: every number is copied from the convergence
tables of the published examples (assets/<NN>/result.json and the lesson text).

    python convergence_overview.py
Output: ../assets/terms-convergence/01_overview.png, overview.json
"""
from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "terms-convergence")
os.makedirs(OUT, exist_ok=True)

# (part, quantity, kind, res_a, value_a, res_b, value_b)
ROWS = [
    (1, "line source: share of power along +-x", "ratio", 20, 0.9188, 40, 0.9182),
    (3, "cylinder: R + T + S", "sum", 20, 0.9988, 40, 0.9997),
    (6, "grating: T + R", "sum", 25, 0.9994, 50, 0.9998),
    (4, "straight guide: T", "ratio", 25, 0.999996, 50, 1.000000),
    (6, "grating: 0th-order T", "ratio", 25, 0.7591, 50, 0.7597),
    (5, "sharp bend: R", "ratio", 25, 0.220, 40, 0.224),
    (3, "cylinder: T", "ratio", 20, 0.6736, 40, 0.6626),
    (3, "cylinder: Q_sca", "ratio", 20, 2.515, 40, 2.628),
    (3, "cylinder: R", "ratio", 20, 0.0823, 40, 0.0861),
    (5, "sharp bend: T", "ratio", 25, 0.200, 40, 0.189),
    (2, "PML 1 um: reflection metric", "ratio", 12, 4.5e-4, 24, 5.1e-4),
    (12, "ring: resonance frequency f3", "resonance", 10, 0.17525, 20, 0.17564),
    (12, "ring: quality factor Q3", "resonance", 10, 1675, 20, 2132),
    (9, "bend inverse design: mode-1 T", "design", 10, 0.7801, 20, 0.6391),
    (14, "thin-film extraction, h >= 0.6 (largest)", "ratio", 40, None, 80, None),
]
EXTRACTION_MAX = 54.0      # lesson 14: CYL res 40 vs 80 differ by 18-54 % for dipole heights h >= 0.6
COLORS = {"sum": "#1b7837", "ratio": "#2166ac", "resonance": "#762a83", "design": "#b2182b"}
LABELS = {"sum": "power sum (energy conservation)", "ratio": "individual ratio or efficiency",
          "resonance": "resonance", "design": "optimized design, re-measured"}

rows = []
for part, q, kind, ra, va, rb, vb in ROWS:
    change = EXTRACTION_MAX if va is None else 100 * abs(vb - va) / abs(va)
    rows.append(dict(part=part, quantity=q, kind=kind, res=[ra, rb], values=[va, vb], change_percent=change))
rows.sort(key=lambda r: r["change_percent"])

fig, ax = plt.subplots(figsize=(10.0, 6.6))
for i, r in enumerate(rows):
    ax.barh(i, r["change_percent"], color=COLORS[r["kind"]], height=0.62)
    ax.text(r["change_percent"] * 1.15, i, f"{r['change_percent']:.2g} %  (res {r['res'][0]} -> {r['res'][1]})",
            va="center", fontsize=8)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([f"{r['part']:02d}  {r['quantity']}" for r in rows], fontsize=8)
ax.set_xscale("log")
ax.set_xlim(1e-4, 800)
ax.axvline(1, color="gray", ls=":", lw=0.8)
ax.text(1.05, len(rows) - 0.4, "1 %", fontsize=8, color="gray")
ax.set_xlabel("relative change between the two resolutions [%]  (log scale)", fontsize=9)
ax.set_title("How much each published result moved when the resolution was raised (examples 01-14)", fontsize=10)
ax.legend(handles=[Patch(color=COLORS[k], label=lab) for k, lab in LABELS.items()], fontsize=8, loc="lower right")
ax.grid(alpha=0.3, axis="x", which="both")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "01_overview.png"), dpi=130)
with open(os.path.join(OUT, "overview.json"), "w", encoding="utf-8") as fh:
    json.dump({"source": "convergence tables of the published examples", "rows": rows}, fh, indent=1)
print("\n".join(f"{r['change_percent']:8.3g} %  {r['part']:02d} {r['quantity']}" for r in rows))
