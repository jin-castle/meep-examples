"""Redraw chapter 21 from saved Meep results; never starts the solver."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parent
load = lambda name: json.loads((root / name).read_text(encoding="utf-8"))
cases = [load(f"circ_p{phase}_{chir}.json") for phase in ("05", "10") for chir in ("c1", "cm1")]
summary = load("summary.json")
field = np.load(root / "circ_p05_c1.npz")
plt.rcParams.update({"font.family": ["Malgun Gothic", "DejaVu Sans"], "axes.unicode_minus": False, "font.size": 11})
metrics = {"cases": [{"phase": c["phase"], "chir": c["chir"],
                      "order_powers": {m: c["orders"][m]["total"] for m in ("-1", "0", "1")},
                      "T": c["Tflux"], "order_sum_over_T": sum(c["orders"][m]["total"] for m in ("-1", "0", "1")) / c["Tflux"]}
                     for c in cases],
           "linear_sweep_max_analytic_errors": {str(r): summary[f"analytic_abs_max_res{r}"] for r in (30, 50)},
           "angle_deg": cases[0]["angle_analytic"]}
for lang in ("ko", "en"):
    ko = lang == "ko"
    fig, ax = plt.subplots(figsize=(5.3, 7.0), layout="constrained")
    e = field["Ez"].real
    limit = np.quantile(abs(e), .995)
    pic = ax.imshow(e.T, origin="lower", extent=field["extent"], cmap="RdBu", vmin=-limit, vmax=limit, aspect="equal")
    half = cases[0]["dd"] / 2
    for x in (-half, half): ax.axvline(x, color="#222", lw=.9, ls="--")
    ax.set(xlabel="x (µm)", ylabel="y (µm)", title="DFT 장: Re Ez · p = 0.5" if ko else "DFT field: Re Ez · p = 0.5")
    fig.colorbar(pic, ax=ax, label="Re Ez (Meep units)")
    fig.savefig(root / f"01_field.{lang}.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout="constrained")
    for index, phase in enumerate((.5, 1)):
        ax = axes[index]
        x = np.arange(3)
        for shift, c, color in ((-.17, cases[2 * index], "#397fa8"), (.17, cases[2 * index + 1], "#cc9255")):
            ax.bar(x + shift, [c["orders"][str(m)]["total"] for m in (-1, 0, 1)], width=.32, color=color,
                   label="Ez + iEy" if c["chir"] == 1 else "Ez - iEy")
        ax.set(xticks=x, xticklabels=["-1", "0", "+1"], ylim=(0, 1.04),
               xlabel="회절 차수" if ko else "Diffraction order",
               ylabel="입사 전력에 대한 비" if ko else "Fraction of incident power",
               title=f"Δnd / λ = {phase:g}, T = {cases[2 * index]['Tflux']:.4f}")
        ax.legend()
    fig.savefig(root / f"02_orders.{lang}.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), layout="constrained")
    errors = [summary[f"analytic_abs_max_res{r}"] for r in (30, 50)]
    axes[0].plot([30, 50], errors, "o-", color="#397fa8")
    axes[0].axhline(.03, ls="--", color="#cc9255", label="0.03 criterion")
    axes[0].set(xticks=[30, 50], xlabel="해상도 (px/µm)" if ko else "Resolution (px/µm)",
                ylabel="max absolute efficiency difference",
                title="선형 입사 sweep의 해석식 검사" if ko else "Analytic check: linear-input sweep")
    axes[0].legend()
    d = load("pg_r50.json")
    phase = np.array(d["dd"]) * .159 / .54
    r = np.array([v["Rflux"] for v in d["uniaxial"]]); t = np.array([v["Tflux"] for v in d["uniaxial"]])
    axes[1].plot(phase, r, label="R"); axes[1].plot(phase, t, label="T"); axes[1].plot(phase, r+t, ":", label="R+T")
    axes[1].set(xlabel="Δnd / λ", ylabel="Fraction of incident power",
                title="선형 입사 수지: res 50" if ko else "Linear-input power balance: res 50")
    axes[1].legend()
    fig.savefig(root / f"03_validation.{lang}.png", dpi=150); plt.close(fig)
(root / "verified_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
print("Chapter21 saved-data figures and metrics written")
