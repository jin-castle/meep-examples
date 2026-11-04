"""resolution_dispersion_gif.py — what too few pixels per wavelength does to a travelling wave (concept page: resolution).

    OMP_NUM_THREADS=1 python resolution_dispersion_gif.py

A 1D pulse (centre wavelength 1.55 um) travels 28 um through silicon (n = 3.48, wavelength in Si 0.445 um).
The same run at resolution 10, 20, 40 (4.5, 8.9, 17.8 pixels per wavelength in Si) is compared with resolution 80.
A DFT at the centre frequency, taken at two probe points 20 um apart, gives the phase accumulated over that
distance; the difference to resolution 80 is compared with the 1D Yee dispersion relation
    sin(omega dt / 2) / (c dt / n) = sin(k dx / 2) / (dx / 2)       (dt = S dx, S = Courant = 0.5).
Outputs: ../assets/terms-resolution/{00_source.png, 01_anim_dispersion.gif, 01_anim_dispersion.png, result.json}
"""
from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp
import numpy as np
from matplotlib import animation

from blogfig import source_figure

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "terms-resolution")
os.makedirs(OUT, exist_ok=True)
mp.verbosity(0)

N_SI = 3.48
WL = 1.55
FCEN, FWIDTH = 1 / WL, 0.25
L, DPML = 40.0, 2.0
Z_SRC, Z_P1, Z_P2 = -16.0, -8.0, 12.0          # probes 20 um apart
T_END = 130.0
DT_REC = 1.0
RESOLUTIONS = [10, 20, 40, 80]
COLORS = {10: "#b2182b", 20: "#ef8a62", 40: "#67a9cf", 80: "#000000"}


def run(res):
    si = mp.Medium(index=N_SI)
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, L), resolution=res, dimensions=1, default_material=si,
                        boundary_layers=[mp.PML(DPML)],
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Ex,
                                           center=mp.Vector3(0, 0, Z_SRC))])
    vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(0, 0, L - 2 * DPML))
    dft = sim.add_dft_fields([mp.Ex], FCEN, 0, 1, where=mp.Volume(center=mp.Vector3(0, 0, 0.5 * (Z_P1 + Z_P2)),
                                                                  size=mp.Vector3(0, 0, Z_P2 - Z_P1)))
    frames, times = [], []

    def grab(s):
        frames.append(np.real(s.get_array(component=mp.Ex, vol=vol)).astype(np.float32))
        times.append(s.meep_time())

    sim.run(mp.at_every(DT_REC, grab), until=T_END)
    ex = sim.get_dft_array(dft, mp.Ex, 0)
    meta = sim.get_array_metadata(dft_cell=dft)
    z_dft = np.asarray(meta[2])                     # exact grid coordinates of the DFT samples
    # numerical wavenumber = slope of the unwrapped phase along z (a fit, so endpoints do not matter)
    phase = np.unwrap(np.angle(ex))
    k_num = abs(np.polyfit(z_dft, phase, 1)[0])
    zm = np.asarray(sim.get_array_metadata(vol=vol)[2])
    return dict(res=res, z=zm, frames=frames, times=np.array(times), k_num=float(k_num),
                span=float(z_dft[-1] - z_dft[0]))


def yee_k(res, courant=0.5):
    """Numerical wavenumber of the 1D Yee scheme in a medium of index N_SI at FCEN (c = 1):
    (n / dt)^2 sin^2(w dt / 2) = (1 / dx)^2 sin^2(k dx / 2)  ->  k = (2 / dx) asin(n dx / dt * sin(w dt / 2))."""
    dx = 1 / res
    dt = courant * dx
    w = 2 * np.pi * FCEN
    return 2 / dx * np.arcsin(N_SI * dx / dt * np.sin(w * dt / 2))


def yee_group_velocity(res, courant=0.5):
    """d(omega)/dk of the same relation: v_g = cos(k dx / 2) / (n cos(omega dt / 2))  (c = 1)."""
    dx = 1 / res
    dt = courant * dx
    w = 2 * np.pi * FCEN
    return np.cos(yee_k(res, courant) * dx / 2) / (N_SI * np.cos(w * dt / 2))


def pulse_centre(z, field, width_um=1.0):
    """Centre of the pulse envelope: argmax of the field energy smoothed over about one wavelength in Si."""
    dz = z[1] - z[0]
    k = max(int(width_um / dz), 1)
    smooth = np.convolve(field.astype(float) ** 2, np.ones(k) / k, mode="same")
    return float(z[int(np.argmax(smooth))])


if __name__ == "__main__":
    src_info = source_figure(FCEN, FWIDTH, os.path.join(OUT, "00_source.png"), wl_unit="um", wl_scale=1.0)
    runs = {r: run(r) for r in RESOLUTIONS}
    k_exact = 2 * np.pi * FCEN * N_SI
    dist = Z_P2 - Z_P1
    table = []
    # group velocity: pulse centre at two times, t1 = 60 and t2 = 115 (the pulse is inside the cell for all resolutions)
    i1, i2 = int(60 / DT_REC), int(115 / DT_REC)
    for r in RESOLUTIONS:
        rr = runs[r]
        z1, z2 = pulse_centre(rr["z"], rr["frames"][i1]), pulse_centre(rr["z"], rr["frames"][i2])
        rr["vg_measured"] = (z2 - z1) / (rr["times"][i2] - rr["times"][i1])
        rr["vg_theory"] = float(yee_group_velocity(r))
    for r in RESOLUTIONS:
        k_th = yee_k(r)
        k_me = runs[r]["k_num"]
        table.append(dict(resolution=r, pixels_per_wavelength_in_si=round(r * WL / N_SI, 2),
                          k_measured=k_me, k_yee_theory=float(k_th), k_exact=float(k_exact),
                          phase_error_percent_measured=100 * (k_me - k_exact) / k_exact,
                          phase_error_percent_yee=100 * (k_th - k_exact) / k_exact,
                          lag_over_20um_rad_measured=(k_me - k_exact) * dist,
                          lag_over_20um_wavelengths_measured=(k_me - k_exact) * dist / (2 * np.pi),
                          group_velocity_measured=runs[r]["vg_measured"], group_velocity_yee=runs[r]["vg_theory"],
                          group_velocity_error_percent_measured=100 * (runs[r]["vg_measured"] * N_SI - 1),
                          group_velocity_error_percent_yee=100 * (runs[r]["vg_theory"] * N_SI - 1),
                          dft_span_um=runs[r]["span"]))
    for row in table:
        print(row)

    # ------------------------------------------------------------ animation
    n = min(len(runs[r]["frames"]) for r in RESOLUTIONS)
    ref = runs[80]
    lim = 1.3 * max(float(np.abs(f).max()) for f in ref["frames"][int(40 / DT_REC):n])
    fig = plt.figure(figsize=(10.5, 6.0))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1])
    ax, axz = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    lines, zlines = {}, {}
    for r in RESOLUTIONS:
        lab = f"res {r}  ({r * WL / N_SI:.1f} px per wavelength in Si)" + ("  reference" if r == 80 else "")
        lw = 1.0 if r == 80 else 1.5
        lines[r], = ax.plot([], [], color=COLORS[r], lw=lw, label=lab)
        zlines[r], = axz.plot([], [], color=COLORS[r], lw=lw, marker="." if r == 10 else None, ms=4)
    ax.set_xlim(ref["z"][0], ref["z"][-1]); ax.set_ylim(-lim, lim)
    for zp in (Z_P1, Z_P2):
        ax.axvline(zp, color="gray", ls=":", lw=0.8)
    ax.text(Z_P1 + 0.2, 0.85 * lim, "DFT probe", fontsize=7, color="gray")
    ax.text(Z_P2 + 0.2, 0.85 * lim, "DFT probe", fontsize=7, color="gray")
    ax.set_xlabel("z [um]", fontsize=8); ax.set_ylabel("Ex", fontsize=8); ax.tick_params(labelsize=7)
    ax.legend(fontsize=7, loc="lower left"); ax.grid(alpha=0.3)
    win = ax.axvspan(0, 0, color="#ffd92f", alpha=0.25)
    axz.set_ylim(-lim, lim); axz.set_xlabel("z [um]  (window following the res-80 pulse peak; dots = res 10 grid points)", fontsize=8)
    axz.set_ylabel("Ex", fontsize=8); axz.tick_params(labelsize=7); axz.grid(alpha=0.3)
    sup = fig.suptitle("", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    v_g = 1 / N_SI

    def update(i):
        t = ref["times"][i]
        z_peak = Z_SRC + max(t - 5.0 / FWIDTH, 0) * v_g
        for r in RESOLUTIONS:
            lines[r].set_data(runs[r]["z"], runs[r]["frames"][i])
            zlines[r].set_data(runs[r]["z"], runs[r]["frames"][i])
        axz.set_xlim(z_peak - 1.5, z_peak + 1.5)
        win.set_x(z_peak - 1.5)
        win.set_width(3.0)
        sup.set_text(f"1D pulse in silicon (n = {N_SI}), centre wavelength {WL} um, Courant 0.5; t = {t:.0f}")

    anim = animation.FuncAnimation(fig, update, frames=n, blit=False)
    anim.save(os.path.join(OUT, "01_anim_dispersion.gif"), writer=animation.PillowWriter(fps=12), dpi=80)
    update(int(110 / DT_REC))
    fig.savefig(os.path.join(OUT, "01_anim_dispersion.png"), dpi=110)
    plt.close(fig)

    with open(os.path.join(OUT, "result.json"), "w", encoding="utf-8") as fh:
        json.dump({"meep_version": mp.__version__, "n_si": N_SI, "wavelength_um": WL, "fcen": FCEN, "fwidth": FWIDTH,
                   "probe_distance_um": dist, "exact_phase_rad": float(k_exact * dist), "courant": 0.5,
                   "source": src_info, "table": table}, fh, indent=1)
