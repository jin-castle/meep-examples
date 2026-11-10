"""Plot saved chapter-20 evidence. No Meep simulation is performed."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
quartz = {r: json.loads((ROOT / f"quartz-r{r}.json").read_text()) for r in (100, 200)}
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), constrained_layout=True)
q = quartz[200]
ax[0].plot(q["wvls"], q["R_analytic"], color="#172b44", label="Sellmeier + Fresnel")
for r, color in ((100, "#cc8b30"), (200, "#3985b0")):
    q = quartz[r]
    wl = np.array(q["wvls"])
    delta = np.abs(np.array(q["R_meep"]) - np.array(q["R_analytic"]))
    ax[0].plot(wl, q["R_meep"], ".", color=color, label=f"Meep, resolution {r}")
    ax[1].semilogy(wl, delta, color=color, label=f"resolution {r}")
ax[0].set(ylabel="Power reflectance R", title="Air / fused quartz, normal incidence")
ax[1].set(ylabel="Absolute reflectance error", title="Grid refinement reduces error")
for a in ax:
    a.set(xlabel="Vacuum wavelength (µm)", xlim=(.4, .8))
    a.grid(alpha=.15)
    a.legend(fontsize=9)
fig.savefig(ROOT / "quartz-reflectance.png", dpi=160)
plt.close(fig)

rows = np.array(json.loads((ROOT / "lorentz-modes.json").read_text())["rows"])
k, f = rows[:, 0], rows[:, 1]
e = np.full(f.shape, 2.25 + 0j)
for f0, g, sigma in ((1.1, 1e-5, .5), (.5, .1, 2e-5)):
    e += sigma * f0**2 / (f0**2 - f**2 - 1j*f*g)
off = (f > .02) & (abs(f-1.1) > .05) & (abs(f-.5) > .05)
relative = abs((k/f)**2 - e.real) / abs(e.real)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), constrained_layout=True)
ax[0].plot(k[::2], f[::2], ".", color="#3985b0", label="Lower extracted branch")
ax[0].plot(k[1::2], f[1::2], ".", color="#cc8b30", label="Upper extracted branch")
ax[0].axhline(1.1, ls="--", color="#657487", lw=1, label="Strong material resonance")
ax[0].set(xlabel="Bloch wavevector k (cycles / length)", ylabel="Re(f) (c / length)", title="202 extracted complex-frequency modes")
ax[0].legend(fontsize=9)
ax[1].semilogy(f[off], relative[off], ".", color="#3985b0")
ax[1].axhline(.01, ls="--", color="#b54e45", label="1% validation target")
ax[1].set(xlabel="Re(f) (c / length)", ylabel="Relative error of real-frequency estimate", title="Simple ε estimate: target not met")
ax[1].legend(fontsize=9)
for a in ax:
    a.grid(alpha=.15)
fig.savefig(ROOT / "lorentz-validation.png", dpi=160)
plt.close(fig)
assert len(rows) == 202
assert np.isclose(relative[off].max(), .37176305873808624)
for r, expected in ((100, .0006594415397795789), (200, .00016779191653321784)):
    q = quartz[r]
    assert len(q["wvls"]) == 50
    assert np.isclose(max(abs(np.array(q["R_meep"]) - q["R_analytic"])), expected)
print("PASS: saved-data plots and reported metrics; no simulations run")
