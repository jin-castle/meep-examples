"""Redraw chapter 27's saved diagnostic data; never starts the solver."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
import numpy as np

root = Path(__file__).resolve().parent
data = {r: json.loads((root / f"md_r{r}.json").read_text(encoding="utf-8")) for r in (25, 50)}
field = np.load(root / "md_r25.npz")
plt.rcParams.update({"font.family": ["Malgun Gothic", "DejaVu Sans"], "axes.unicode_minus": False, "font.size": 11})
metrics = {str(r): {"Lt_um": [x["Lt"] for x in d["rows"]],
                    "R_coeff": [x["R_coeff"] for x in d["rows"]],
                    "R_flux_signed": [x["R_flux"] for x in d["rows"]],
                    "forward_residual_power": [x["T_coeff_in"] for x in d["rows"]],
                    "negative_reflectance_count": sum(x["R_flux"] < 0 for x in d["rows"])}
           for r, d in data.items()}
for lang in ("ko", "en"):
    ko = lang == "ko"
    fig, ax = plt.subplots(figsize=(12, 4.6), layout="constrained")
    e = field["Ez"].real; eps = field["eps"]
    extent = [-14, 14, -4, 4]
    limit = np.quantile(abs(e), .995)
    pic = ax.imshow(e.T, origin="lower", extent=extent, cmap="RdBu", vmin=-limit, vmax=limit, aspect="equal")
    ax.contour(np.linspace(-14,14,eps.shape[0]), np.linspace(-4,4,eps.shape[1]), eps.T, levels=[6.5], colors="#333", linewidths=.6)
    ax.set(xlabel="x (µm)", ylabel="y (µm)", title="실제 DFT 장 Re Ez: Lt = 8 µm, res 25" if ko else "Actual DFT field Re Ez: Lt = 8 µm, res 25")
    fig.colorbar(pic, ax=ax, label="Re Ez (Meep units)")
    fig.savefig(root / f"01_field.{lang}.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    for r, color in ((25, "#397fa8"), (50, "#cc9255")):
        rows = data[r]["rows"]; lengths = [x["Lt"] for x in rows]
        axes[0].plot(lengths, [x["R_coeff"] * 100 for x in rows], "o-", color=color, label=f"mode, res {r}")
        axes[0].plot(lengths, [x["R_flux"] * 100 for x in rows], "s--", color=color, label=f"signed flux, res {r}")
        axes[1].plot(lengths, [x["T_coeff_in"] * 100 for x in rows], "o-", color=color, label=f"res {r}")
    axes[0].axhline(0, color="#666", lw=.7)
    axes[0].set(xlabel="Lt (µm)", ylabel="R (%)", xticks=[1,2,4,8],
                title="음수 flux 추정값도 그대로 표시" if ko else "Signed negative estimates retained")
    axes[1].set(xlabel="Lt (µm)", ylabel="Residual forward mode / incident (%)", xticks=[1,2,4,8],
                title="반사면: 빼기 후 남은 전방 성분" if ko else "Reflection plane: forward residual after subtraction")
    for ax in axes: ax.legend(fontsize=9)
    fig.savefig(root / f"02_diagnostic.{lang}.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    rows = data[25]["rows"]; lengths = np.array([x["Lt"] for x in rows])
    axes[0].loglog(lengths, [x["R_coeff"] for x in rows], "o-", label="mode, res 25")
    axes[0].loglog(lengths, [x["R_flux"] for x in rows], "s--", label="flux, res 25")
    axes[0].set(xticks=lengths, xticklabels=lengths, yticks=[.00002,.0001,.0004], yticklabels=["0.00002","0.0001","0.0004"],
                xlabel="Lt (µm)", ylabel="R", title="res 25: 관측된 감소" if ko else "res 25: observed decrease")
    axes[0].xaxis.set_minor_locator(NullLocator()); axes[0].yaxis.set_minor_locator(NullLocator())
    for r, color in ((25,"#397fa8"),(50,"#cc9255")):
        rows = data[r]["rows"]
        axes[1].plot([x["Lt"] for x in rows], [x["T_flux"] for x in rows], "o-", color=color, label=f"res {r}")
    axes[1].axhline(1, color="#666", lw=.7)
    axes[1].set(xlabel="Lt (µm)", ylabel="Output total flux / reference flux", xticks=[1,2,4,8],
                title="출력 총 flux: 특정 모드의 T가 아님" if ko else "Output total flux: not a selected modal T")
    for ax in axes: ax.legend(fontsize=9)
    fig.savefig(root / f"03_comparison.{lang}.png", dpi=150); plt.close(fig)
(root / "verified_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
print("Chapter27 signed diagnostic figures and metrics written")
