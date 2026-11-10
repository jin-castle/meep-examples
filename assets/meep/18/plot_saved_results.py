"""Redraw chapter 18 figures from saved Meep data; no solver is run."""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
import numpy as np

root = Path(__file__).resolve().parent
z = {r: np.load(root / f"ang_r{r}.npz") for r in (50, 100, 200)}
plt.rcParams.update({"font.family": ["Malgun Gothic", "DejaVu Sans"],
                     "axes.unicode_minus": False, "font.size": 11,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})


def fresnel(theta):
    transmitted = np.arcsin(np.sin(theta) / 3.5)
    return ((np.cos(transmitted) - 3.5 * np.cos(theta)) /
            (np.cos(transmitted) + 3.5 * np.cos(theta))) ** 2


metrics = {}
for resolution, data in z.items():
    angles = np.arcsin(data["kx"][:, None] / data["freqs"][None, :])
    error = np.abs(data["R"] - fresnel(angles))
    select = [list(data["theta"]).index(t) for t in (0, 45, 75)]
    metrics[str(resolution)] = {
        "fresnel_max_abs_error_common_angles": float(error[select].max()),
        "energy_max_abs_residual": float(np.abs(data["R"] + data["T"] - 1).max()),
        "angles_at_0p8um_deg": data["theta"].tolist(),
    }

for lang in ("ko", "en"):
    ko = lang == "ko"
    data = z[50]
    freqs = data["freqs"]
    wavelengths = 1 / freqs
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.1), layout="constrained")
    ax = axes[0]
    ax.axvspan(-6, -5, color="#d3dae0"); ax.axvspan(5, 6, color="#d3dae0")
    ax.axvspan(0, 5, color="#b6d8ef")
    for value, label, color in ((-5, "source", "#c95858"), (-3, "R", "#449a77"), (2, "T", "#cf9c38")):
        ax.axvline(value, color=color, lw=2)
        ax.text(value, 0.08, label, rotation=90, ha="right", va="bottom", color=color)
    ax.text(-1.5, .75, "n = 1", ha="center"); ax.text(3, .75, "n = 3.5", ha="center")
    ax.text(-5.5, .75, "PML", rotation=90, ha="center"); ax.text(5.5, .75, "PML", rotation=90, ha="center")
    ax.set(xlim=(-6, 6), ylim=(0, 1), yticks=[], xlabel="z (µm)",
           title="(a) 1D 셀과 측정면" if ko else "(a) 1D cell and monitors")
    axes[1].plot(data["trace_t"], data["trace_v"] / np.max(np.abs(data["trace_v"])), color="#377caa", lw=.8)
    axes[1].set(xlim=(0, 40), xlabel="t (µm/c)", ylabel="Ex / max|Ex|",
                title="(b) 빈 셀의 입사 펄스 (θ = 0°)" if ko else "(b) Empty-cell pulse (θ = 0°)")
    for angle, color in ((0, "#377caa"), (75, "#c95c48")):
        j = list(data["theta"]).index(angle)
        axes[2].plot(wavelengths, data["inc"][j] / data["inc"][0].max(), color=color, label=f"θ = {angle}°")
    axes[2].set(xlabel="파장 (µm)" if ko else "Wavelength (µm)", ylabel="Flux / max(flux at 0°)",
                title="(c) 반사율의 분모: 입사 flux" if ko else "(c) Incident normalization flux")
    axes[2].legend()
    fig.savefig(root / f"01_layout.{lang}.png", dpi=140); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    theta = np.linspace(0, 89, 500)
    axes[0].plot(theta, fresnel(np.radians(theta)), "k-", label="Fresnel P")
    for wavelength, color in ((.4, "#377caa"), (.8, "#c95c48")):
        i = np.argmin(abs(wavelengths - wavelength))
        actual = np.degrees(np.arcsin(data["kx"] / freqs[i]))
        axes[0].plot(actual, data["R"][:, i], "o", ms=4, color=color,
                     label=f"Meep res 50, λ = {wavelengths[i]:.2f} µm")
    brewster = np.degrees(np.arctan(3.5))
    axes[0].axvline(brewster, color="#81909d", ls=":")
    axes[0].set(xlabel="실제 입사각 (도)" if ko else "Actual incident angle (degrees)", ylabel="R",
                title=f"(a) P 편광 반사와 Brewster 각 {brewster:.2f}°" if ko else f"(a) P reflectance; Brewster angle {brewster:.2f}°")
    axes[0].legend(fontsize=9)
    for angle, color in ((0, "#377caa"), (45, "#449a77"), (75, "#c95c48")):
        d = z[200]; j = list(d["theta"]).index(angle)
        actual = np.arcsin(d["kx"][j] / d["freqs"])
        axes[1].plot(1 / d["freqs"], d["R"][j], color=color, label=f"Meep θ₀ = {angle}°")
        axes[1].plot(1 / d["freqs"], fresnel(actual), "--", color=color, alpha=.6)
    axes[1].set(xlabel="파장 (µm)" if ko else "Wavelength (µm)", ylabel="R",
                title="(b) res 200: 실선 Meep / 점선 Fresnel" if ko else "(b) res 200: solid Meep / dashed Fresnel")
    axes[1].legend(fontsize=9)
    fig.savefig(root / f"02_results.{lang}.png", dpi=140); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    rs = [50, 100, 200]
    errors = [metrics[str(r)]["fresnel_max_abs_error_common_angles"] for r in rs]
    axes[0].loglog(rs, errors, "o-", color="#377caa")
    for r, error in zip(rs, errors):
        axes[0].annotate(f"{error:.5f}", (r, error), xytext=(5, 5), textcoords="offset points")
    axes[0].set(xlim=(43, 240), ylim=(.0025, .1), xticks=rs, xticklabels=rs,
                yticks=[.003, .01, .03, .1], yticklabels=["0.003", "0.01", "0.03", "0.1"],
                xlabel="해상도 (px/µm)" if ko else "Resolution (px/µm)",
                ylabel="max |R − R(Fresnel)|",
                title="(a) 같은 θ₀ = 0°, 45°, 75°에서 비교" if ko else "(a) Common θ₀ = 0°, 45°, 75°")
    axes[0].xaxis.set_minor_locator(NullLocator())
    axes[0].yaxis.set_minor_locator(NullLocator())
    for r, color in ((50, "#c95c48"), (100, "#cf9c38"), (200, "#377caa")):
        d = z[r]; j = list(d["theta"]).index(75)
        axes[1].plot(1 / d["freqs"], d["R"][j] + d["T"][j] - 1, color=color, label=f"res {r}")
    axes[1].axhline(0, color="#81909d", lw=.8)
    axes[1].set(xlabel="파장 (µm)" if ko else "Wavelength (µm)", ylabel="R + T − 1",
                title="(b) θ₀ = 75° 에너지 수지 잔차" if ko else "(b) Energy residual at θ₀ = 75°")
    axes[1].legend()
    fig.savefig(root / f"03_convergence.{lang}.png", dpi=140); plt.close(fig)

(root / "verified_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
print(json.dumps(metrics, indent=2))
