"""courant_stability.py — where Meep's time step stops being stable (concept page: Courant condition).

    OMP_NUM_THREADS=1 python courant_stability.py

A. Vacuum, 1D / 2D / 3D: the Yee update is stable for S = c*dt/dx <= 1/sqrt(D).
   Each case runs a short Gaussian pulse in a small PML cell at a few S values around the limit
   and records max|E| over the whole cell. A run counts as divergent when max|E| grows past
   1e3 x its value at the end of the source (the pulse has left; only growth can push it up).
B. 1D Lorentzian medium in a closed cell (no PML, so PML-dispersive coupling is not involved):
   sweep the resonance frequency f_n at S = 0.5 and S = 0.25 and find where the run diverges.
   Meep's Materials page gives the rough bound omega_n * dt / 2 > 1, i.e. f_n > resolution / (pi * S).
Outputs: ../assets/terms-courant/{00_source.png, 01_courant.png, result.json}
"""
from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp
import numpy as np

from blogfig import source_figure

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "terms-courant")
os.makedirs(OUT, exist_ok=True)
mp.verbosity(0)

FCEN, FWIDTH = 1.0, 0.5          # 1 unit = 1 um, so the centre wavelength is 1 um
T_SRC = 2 * 5.0 / FWIDTH          # GaussianSource is off after 2 * cutoff * width = 20


class Diverged(Exception):
    pass


# ---------------------------------------------------------------- A. vacuum, D = 1, 2, 3
CASES = {
    1: dict(cell=mp.Vector3(0, 0, 16), res=20, comp=mp.Ex, S=[0.5, 0.99, 1.0, 1.01, 1.05]),
    2: dict(cell=mp.Vector3(8, 8), res=10, comp=mp.Ez, S=[0.5, 0.70, 0.71, 0.72, 0.75]),
    3: dict(cell=mp.Vector3(4, 4, 4), res=8, comp=mp.Ez, S=[0.5, 0.57, 0.58, 0.59, 0.62]),
}
T_END = 80.0


def vacuum_run(D: int, S: float) -> dict:
    c = CASES[D]
    sim = mp.Simulation(cell_size=c["cell"], resolution=c["res"], dimensions=D, Courant=S,
                        boundary_layers=[mp.PML(1.0)],
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=c["comp"],
                                           center=mp.Vector3())])
    times, peaks = [], []
    ref = {}

    def track(s):
        a = np.abs(s.get_array(component=c["comp"]))
        m = float(np.nan_to_num(a.max(), nan=np.inf))
        times.append(s.meep_time())
        peaks.append(m)
        if s.meep_time() >= T_SRC and "end_of_source" not in ref:
            ref["end_of_source"] = max(m, 1e-300)
        if "end_of_source" in ref and m > 1e3 * ref["end_of_source"]:
            raise Diverged

    status = "stable"
    try:
        sim.run(mp.at_every(0.5, track), until=T_END)
    except Diverged:
        status = "diverged"
    except RuntimeError as err:          # Meep's own NaN/Inf abort
        status = "diverged" if "NaN" in str(err) or "Inf" in str(err) else f"error: {err}"
    steps = int(round(times[-1] * c["res"] / S)) if times else 0
    return dict(D=D, S=S, limit=1 / np.sqrt(D), status=status, t_last=times[-1] if times else 0.0,
                steps_last=steps, times=times, peaks=peaks)


# ---------------------------------------------------------------- B. 1D Lorentzian, closed cell
RES_B, L_B, T_B = 10, 10.0, 300.0
FN_SWEEP = np.round(np.arange(3.0, 16.01, 0.5), 2)


def lorentz_run(fn: float, S: float) -> str:
    medium = mp.Medium(epsilon=2.25, E_susceptibilities=[mp.LorentzianSusceptibility(frequency=fn, gamma=0.05, sigma=0.5)])
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, L_B), resolution=RES_B, dimensions=1, Courant=S,
                        default_material=medium,
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Ex,
                                           center=mp.Vector3(0, 0, 0.3))])
    ref = {}

    def track(s):
        m = float(np.nan_to_num(np.abs(s.get_array(component=mp.Ex)).max(), nan=np.inf))
        if s.meep_time() >= T_SRC and "end" not in ref:
            ref["end"] = max(m, 1e-300)
        if "end" in ref and m > 1e3 * ref["end"]:
            raise Diverged

    try:
        sim.run(mp.at_every(1.0, track), until=T_B)
    except Diverged:
        return "diverged"
    except RuntimeError as err:
        return "diverged" if "NaN" in str(err) or "Inf" in str(err) else f"error: {err}"
    return "stable"


if __name__ == "__main__":
    src_info = source_figure(FCEN, FWIDTH, os.path.join(OUT, "00_source.png"), wl_unit="um", wl_scale=1.0)

    vac = [vacuum_run(D, S) for D in CASES for S in CASES[D]["S"]]
    for r in vac:
        print(f"A. D={r['D']}  S={r['S']:.2f}  limit={r['limit']:.4f}  {r['status']:9s}  last t={r['t_last']:.1f} ({r['steps_last']} steps)")

    lor = {}
    for S in (0.5, 0.25):
        lor[S] = {float(fn): lorentz_run(float(fn), S) for fn in FN_SWEEP}
        first_bad = next((fn for fn, st in lor[S].items() if st != "stable"), None)
        print(f"B. S={S}: predicted f_n* = res/(pi S) = {RES_B / (np.pi * S):.2f};  first divergent f_n in sweep = {first_bad}")

    # ------------------------------------------------------------ figure
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    ax = axes[0]
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(CASES[2]["S"])))
    for r, col in zip([r for r in vac if r["D"] == 2], colors):
        ax.semilogy(r["times"], np.maximum(r["peaks"], 1e-12), color=col, lw=1.4,
                    label=f"S = {r['S']:.2f}  ({r['status']})")
    ax.axvline(T_SRC, color="gray", ls=":", lw=1)
    ax.text(T_SRC + 1, 1e-10, "source off", color="gray", fontsize=8)
    ax.set_xlabel("time [a/c]  (a = 1 um)")
    ax.set_ylabel("max |Ez| over the cell")
    ax.set_title("(a) 2D vacuum, res 10, PML 1 um: limit 1/sqrt(2) = 0.7071", fontsize=10)
    ax.set_ylim(1e-12, 1e8)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3, which="both")

    ax = axes[1]
    for S, mk, off in ((0.5, "o", 0.0), (0.25, "s", 0.12)):
        fns = np.array(list(lor[S].keys()))
        ok = np.array([lor[S][f] == "stable" for f in fns])
        ax.plot(fns[ok], np.full(ok.sum(), S), mk, color="tab:blue", ms=6, label="stable" if S == 0.5 else None)
        ax.plot(fns[~ok], np.full((~ok).sum(), S), mk, color="tab:red", ms=6, mfc="none", label="diverged" if S == 0.5 else None)
        ax.axvline(RES_B / (np.pi * S), color="gray", ls="--", lw=1)
        ax.text(RES_B / (np.pi * S) + 0.1, S + 0.04, f"res/(pi S) = {RES_B / (np.pi * S):.2f}", fontsize=8, color="gray")
    ax.set_xlabel("Lorentzian resonance f_n [c/a]")
    ax.set_ylabel("Courant S")
    ax.set_ylim(0.1, 0.65)
    ax.set_title("(b) 1D Lorentzian medium, res 10, closed cell", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "01_courant.png"), dpi=150)
    plt.close(fig)

    with open(os.path.join(OUT, "result.json"), "w", encoding="utf-8") as fh:
        json.dump({"meep_version": mp.__version__, "source": {"fcen": FCEN, "fwidth": FWIDTH, **src_info},
                   "vacuum": [{k: v for k, v in r.items() if k not in ("times", "peaks")} for r in vac],
                   "lorentz": {str(S): v for S, v in lor.items()}, "lorentz_res": RES_B}, fh, indent=1)
