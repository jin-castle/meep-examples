"""Replot and check chapter 19's saved native Gaussian fields; no solver run.

The NPZ arrays retain all 924 x 924 native samples of x,y,epsilon,phasor.
Phasor convention: Ez(t)=Re(phasor*exp(-i*2*pi*12*t))+dc, fitted over
the final two periods of the original Optical-beams-MEEP executions.
"""
from pathlib import Path
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


def direction(data, ray, distance):
    x, y = np.meshgrid(data["x"], data["y"], indexing="ij")
    along = math.cos(ray)*x + math.sin(ray)*y
    across = -math.sin(ray)*x + math.cos(ray)*y
    mask = (along > distance[0]) & (along < distance[1]) & (abs(across) < .12)
    field = data["phasor"]
    gx, gy = np.gradient(field, data["x"], data["y"])
    weights = np.abs(field)**2
    kx = np.imag(field.conj()*gx)[mask].sum()/weights[mask].sum()
    ky = np.imag(field.conj()*gy)[mask].sum()/weights[mask].sum()
    return float(np.degrees(np.arctan2(ky, kx)))


def main():
    cases = {}
    for angle in [30, 45]:
        with np.load(ROOT/f"planar{angle}-fields.npz") as archive:
            cases[angle] = {key: archive[key] for key in archive.files}
        assert cases[angle]["phasor"].shape == (924, 924)
        assert all(np.isfinite(a).all() for a in cases[angle].values())
    limit = max((abs(d["phasor"])**2/2)[(abs(d["x"])[:, None] < 2.2) &
                                       (abs(d["y"])[None, :] < 2.2)].max() for d in cases.values())
    real_limit = max(abs(d["phasor"].real).max() for d in cases.values())
    for quantity in ["cycle-mean", "signed-phase"]:
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.7), constrained_layout=True)
        for ax, (angle, d) in zip(axes, cases.items()):
            x, y = d["x"], d["y"]
            extent = (x[0], x[-1], y[0], y[-1])
            if quantity == "cycle-mean":
                value = abs(d["phasor"])**2/2/limit
                image = ax.imshow(value.T, origin="lower", extent=extent, cmap="hot", vmin=0, vmax=1)
                contour_color = "#a9c5cc"
            else:
                value = d["phasor"].real/real_limit
                image = ax.imshow(value.T, origin="lower", extent=extent, cmap="RdBu", vmin=-1, vmax=1)
                contour_color = "#657488"
            ax.contour(x, y, d["epsilon"].T, levels=[(1+1.54**2)/2], colors=[contour_color], linewidths=.8)
            ax.set(xlim=(-2.2, 2.2), ylim=(-2.2, 2.2), xlabel="x / a", ylabel="y / a",
                   title=f"{angle}° incidence from the interface normal")
        fig.colorbar(image, ax=axes, shrink=.8, label=("Cycle-mean Ez² / common maximum (not power flux)"
                                                     if quantity == "cycle-mean" else "Re(phasor) / common maximum (one phase)"))
        fig.suptitle("Saved Gaussian beam: n₁ = 1.54 → n₂ = 1.00, s polarization", fontsize=16)
        fig.savefig(ROOT/f"gaussian-{quantity}.png", dpi=160)
        plt.close(fig)
    analytic = math.degrees(math.asin(1.54*math.sin(math.radians(30))))
    measured = direction(cases[30], math.radians(analytic-30), [.6, 1.6])+30
    critical = math.degrees(math.asin(1/1.54))
    reflected = {str(a): direction(d, math.radians(180-2*a), [.7, 1.7]) for a, d in cases.items()}
    assert abs(measured-50.66184010623955) < 1e-9
    assert abs(reflected["30"]-119.97571438340682) < 1e-9
    assert abs(reflected["45"]-90.85074682046765) < 1e-9
    metrics = {"critical_angle_deg": critical, "snell_30_deg": analytic,
               "local_phase_angle_30_deg": measured, "difference_deg": abs(measured-analytic),
               "reflected_phase_direction_from_positive_x_deg": reflected,
               "native_shape": [924, 924], "new_simulations": False,
               "method": "Intensity-weighted local phasor phase gradient; not a beam centroid or Poynting-flux direction"}
    (ROOT/"verified_metrics.json").write_text(json.dumps(metrics, indent=2)+"\n", encoding="utf-8")
    print("PASS native arrays and reproduced archived local phase diagnostics", json.dumps(metrics))


if __name__ == "__main__":
    main()
