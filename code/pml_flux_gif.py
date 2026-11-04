"""pml_flux_gif.py — animations for the concept pages PML and flux normalization.

    OMP_NUM_THREADS=1 python pml_flux_gif.py

A. PML (same source as Part 02: Ez point source, fcen = 1/1.55, fwidth = 0.4, resolution 12).
   Interior 8 x 8 um, three boundary treatments: no layer (Meep's default wall), mp.Absorber(1), mp.PML(1),
   the 1 um layer added outside the interior. Top row: Ez. Bottom row: what the boundary sent back,
   Ez(test) - Ez(reference) inside the interior, x50. The reference cell has 16 um of padding and no layer,
   so the front of its own wall reflection reaches the interior only after t ~ 41; the animation ends at t = 32.
B. Flux normalization (Part 05 sharp bend, parameters copied from code/bend90.py: eps 12, w 1, fcen 0.15,
   df 0.1, resolution 25, cell 16, PML 1). Run 1 straight guide, run 2 bend, and run 2 - run 1.
   Bottom: the flux spectra at fcen accumulated so far, divided by the final P_in of run 1.
   Run 2 starts with the negated incident DFT fields loaded, so the running R starts at -1.
Outputs: ../assets/terms-pml/{01_anim_pml.gif, 01_anim_pml.png}, ../assets/terms-flux/{01_anim_flux.gif,
         01_anim_flux.png}, anim.json in each folder.
Published GIFs are recompressed with one shared palette (see courant_gif.py).
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

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PML = os.path.join(HERE, "..", "assets", "terms-pml")
OUT_FLUX = os.path.join(HERE, "..", "assets", "terms-flux")
for d in (OUT_PML, OUT_FLUX):
    os.makedirs(d, exist_ok=True)
mp.verbosity(0)


def save(fig, update, n, out_dir, name, png_step):
    anim = animation.FuncAnimation(fig, update, frames=n, blit=False)
    anim.save(os.path.join(out_dir, name + ".gif"), writer=animation.PillowWriter(fps=12), dpi=80)
    update(png_step)
    fig.savefig(os.path.join(out_dir, name + ".png"), dpi=110)
    plt.close(fig)


# ================================================================ A. PML
WL = 1.55
FCEN_A, FW_A = 1 / WL, 0.4
RES_A, L, D, PAD = 12, 8.0, 1.0, 16.0
DT_A, T_A = 0.4, 32.0
AMP = 50


def run_pml(layers, cell):
    sim = mp.Simulation(cell_size=mp.Vector3(cell, cell), resolution=RES_A, boundary_layers=layers, Courant=0.5,
                        sources=[mp.Source(mp.GaussianSource(FCEN_A, fwidth=FW_A), component=mp.Ez, center=mp.Vector3())])
    full, inner = [], []
    vin = mp.Volume(center=mp.Vector3(), size=mp.Vector3(L, L))

    def grab(s):
        full.append(np.real(s.get_array(component=mp.Ez)).astype(np.float32))
        inner.append(np.real(s.get_array(component=mp.Ez, vol=vin)).astype(np.float32))

    sim.run(mp.at_every(DT_A, grab), until=T_A)
    return full, inner


def gif_pml():
    _, ref = run_pml([], L + 2 * PAD)
    cases = [("no layer (Meep default wall)", [], L), ("mp.Absorber(1.0)", [mp.Absorber(D)], L + 2 * D),
             ("mp.PML(1.0)", [mp.PML(D)], L + 2 * D)]
    runs = []
    for title, layers, cell in cases:
        full, inner = run_pml(layers, cell)
        n = min(len(inner), len(ref))
        diff = []
        for k in range(n):
            a, b = inner[k], ref[k]
            m0, m1 = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
            diff.append(a[:m0, :m1] - b[:m0, :m1])
        runs.append(dict(title=title, cell=cell, full=full, diff=diff))
    n = min(len(r["diff"]) for r in runs)
    lim = float(np.percentile(np.abs(np.stack(ref[:n])), 99.0))
    # reflection metric over time: rms(test - ref) / peak rms(ref), as in Part 02
    peak_ref = max(float(np.sqrt(np.mean(f ** 2))) for f in ref[:n])
    metric = {r["title"]: [float(np.sqrt(np.mean(d ** 2))) / peak_ref for d in r["diff"][:n]] for r in runs}
    times = np.arange(n) * DT_A

    fig, axs = plt.subplots(2, 3, figsize=(10.5, 7.0))
    ims_top, ims_bot = [], []
    for k, r in enumerate(runs):
        half = r["cell"] / 2
        ax = axs[0, k]
        ims_top.append(ax.imshow(r["full"][0].T, origin="lower", extent=[-half, half, -half, half],
                                 cmap="RdBu", vmin=-lim, vmax=lim))
        ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
        ax.add_patch(plt.Rectangle((-L / 2, -L / 2), L, L, fill=False, ec="k", lw=0.9, ls="--"))
        if r["cell"] > L:
            ax.text(-4.9, 4.55, "layer", fontsize=7, color="k")
        else:
            ax.text(-4.9, 4.55, "outside the cell", fontsize=7, color="gray")
        ax.set_title("Ez: " + r["title"], fontsize=9); ax.tick_params(labelsize=7)
        ax.set_xlabel("x [um]", fontsize=8); ax.set_ylabel("y [um]", fontsize=8)
        ax = axs[1, k]
        ax.set_title(f"sent back by the boundary, x{AMP}", fontsize=9)
        ims_bot.append(ax.imshow(r["diff"][0].T, origin="lower", extent=[-L / 2, L / 2, -L / 2, L / 2],
                                 cmap="RdBu", vmin=-lim / AMP, vmax=lim / AMP))
        ax.set_xlim(-5, 5); ax.set_ylim(-5, 5); ax.tick_params(labelsize=7)
        ax.set_xlabel("x [um]", fontsize=8); ax.set_ylabel("y [um]", fontsize=8)
    txt = [axs[1, k].text(0, -4.7, "", ha="center", fontsize=8, bbox=dict(fc="white", ec="0.6", alpha=0.85)) for k in range(3)]
    sup = fig.suptitle("", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    def update(i):
        for k, r in enumerate(runs):
            ims_top[k].set_data(r["full"][i].T)
            ims_bot[k].set_data(r["diff"][i].T)
            txt[k].set_text(f"rms / peak incident = {metric[r['title']][i]:.1e}")
        sup.set_text(f"2D vacuum, Ez point source (wavelength 1.55 um), res 12. Bottom: Ez(test) - Ez(reference, no boundary within reach); t = {times[i]:.1f} um/c")

    save(fig, update, n, OUT_PML, "01_anim_pml", int(round(18.0 / DT_A)))
    i27 = int(round(27.0 / DT_A))
    info = {"colour_limit": lim, "amplification": AMP, "metric_at_t27": {k: v[i27] for k, v in metric.items()},
            "metric_max_after_t20": {k: max(v[int(20 / DT_A):]) for k, v in metric.items()}}
    with open(os.path.join(OUT_PML, "anim.json"), "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=1)
    return info


# ================================================================ B. flux normalization (Part 05 sharp bend)
EPS_WG, W, FCEN, DF, NFREQ = 12.0, 1.0, 0.15, 0.1, 11
RES_B, DPML, SX = 25, 1.0, 16.0
YCEN, XCEN = -4.0, 4.0
SPAN = mp.Vector3(0, W + 2)
A_UM = 1.55 * FCEN                    # 1 Meep unit = 232.5 nm when the centre wavelength is 1550 nm
EDGE = SX / 2 - DPML
SRC_X, REFL_X, TRAN0_X, TRAN_Y = -EDGE + 0.5, -EDGE + 1.5, EDGE - 0.5, EDGE - 0.5
DT_B = 2.0
IC = NFREQ // 2


def geometry(bend):
    wg = mp.Medium(epsilon=EPS_WG)
    if not bend:
        return [mp.Block(center=mp.Vector3(0, YCEN), size=mp.Vector3(mp.inf, W), material=wg)]
    x_end, y_start = XCEN + W / 2, YCEN - W / 2
    return [mp.Block(center=mp.Vector3(0.5 * (-SX / 2 + x_end), YCEN), size=mp.Vector3(SX / 2 + x_end, W), material=wg),
            mp.Block(center=mp.Vector3(XCEN, 0.5 * (y_start + SX / 2)), size=mp.Vector3(W, SX / 2 - y_start), material=wg)]


def sim_b(bend):
    return mp.Simulation(cell_size=mp.Vector3(SX, SX), resolution=RES_B, boundary_layers=[mp.PML(DPML)],
                         geometry=geometry(bend),
                         sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=DF), component=mp.Ez,
                                            center=mp.Vector3(SRC_X, YCEN), size=SPAN)])


VOL_B = mp.Volume(center=mp.Vector3(), size=mp.Vector3(SX - 2 * DPML, SX - 2 * DPML))


def gif_flux():
    # run 1: straight reference
    s1 = sim_b(False)
    refl1 = s1.add_flux(FCEN, DF, NFREQ, mp.FluxRegion(center=mp.Vector3(REFL_X, YCEN), size=SPAN))
    tran0 = s1.add_flux(FCEN, DF, NFREQ, mp.FluxRegion(center=mp.Vector3(TRAN0_X, YCEN), size=SPAN))
    f1, pin_t, t1 = [], [], []

    def g1(s):
        f1.append(np.real(s.get_array(component=mp.Ez, vol=VOL_B))[::2, ::2].astype(np.float32))
        pin_t.append(mp.get_fluxes(tran0)[IC]); t1.append(s.meep_time())

    s1.run(mp.at_every(DT_B, g1), until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(TRAN0_X, YCEN), 1e-6))
    P_in = np.array(mp.get_fluxes(tran0)); refl_data = s1.get_flux_data(refl1)

    # run 2: bend, incident DFT fields loaded negated on the reflection plane
    s2 = sim_b(True)
    refl = s2.add_flux(FCEN, DF, NFREQ, mp.FluxRegion(center=mp.Vector3(REFL_X, YCEN), size=SPAN))
    s2.load_minus_flux_data(refl, refl_data)
    tran = s2.add_flux(FCEN, DF, NFREQ, mp.FluxRegion(center=mp.Vector3(XCEN, TRAN_Y), size=mp.Vector3(W + 2, 0)))
    f2, T_t, R_t, t2 = [], [], [], []

    def g2(s):
        f2.append(np.real(s.get_array(component=mp.Ez, vol=VOL_B))[::2, ::2].astype(np.float32))
        T_t.append(mp.get_fluxes(tran)[IC] / P_in[IC]); R_t.append(-mp.get_fluxes(refl)[IC] / P_in[IC]); t2.append(s.meep_time())

    s2.run(mp.at_every(DT_B, g2), until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(XCEN, TRAN_Y), 1e-6))
    T_fin = float(mp.get_fluxes(tran)[IC] / P_in[IC]); R_fin = float(-mp.get_fluxes(refl)[IC] / P_in[IC])

    n = max(len(f1), len(f2))
    h1 = lambda i: min(i, len(f1) - 1)
    h2 = lambda i: min(i, len(f2) - 1)
    t_all = np.arange(n) * DT_B
    lim = float(np.percentile(np.abs(np.stack(f1)), 99.5))
    ext = [v * A_UM for v in (-EDGE, EDGE, -EDGE, EDGE)]

    fig = plt.figure(figsize=(11.0, 7.4))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1])
    axs = [fig.add_subplot(gs[0, k]) for k in range(3)]
    axt = fig.add_subplot(gs[1, :])
    titles = ["run 1: straight guide (reference)", "run 2: sharp bend", "run 2 - run 1"]
    ims = []
    for ax, ttl in zip(axs, titles):
        ims.append(ax.imshow(f1[0].T, origin="lower", extent=ext, cmap="RdBu", vmin=-lim, vmax=lim))
        ax.set_title(ttl, fontsize=9); ax.tick_params(labelsize=7)
        ax.set_xlabel("x [um]", fontsize=8); ax.set_ylabel("y [um]", fontsize=8)
    seg = lambda x0, y0, x1, y1: ([x0 * A_UM, x1 * A_UM], [y0 * A_UM, y1 * A_UM])
    refl_seg = seg(REFL_X, YCEN - 1.5, REFL_X, YCEN + 1.5)
    for ax in axs:
        ax.plot(*refl_seg, color="#1b7837", lw=2.2)
    axs[0].plot(*seg(TRAN0_X, YCEN - 1.5, TRAN0_X, YCEN + 1.5), color="#762a83", lw=2.2)
    axs[1].plot(*seg(XCEN - 1.5, TRAN_Y, XCEN + 1.5, TRAN_Y), color="#762a83", lw=2.2)
    axs[0].text(REFL_X * A_UM, (YCEN + 1.9) * A_UM, "refl plane", color="#1b7837", fontsize=7)
    axs[0].text(TRAN0_X * A_UM - 0.55, (YCEN + 1.9) * A_UM, "P_in plane", color="#762a83", fontsize=7)
    axs[1].text((XCEN - 2.6) * A_UM, (TRAN_Y - 0.9) * A_UM, "tran plane", color="#762a83", fontsize=7)

    axt.plot(t1, np.array(pin_t) / P_in[IC], color="#762a83", lw=0.8, alpha=0.25)
    axt.plot(t2, T_t, color="#2166ac", lw=0.8, alpha=0.25)
    axt.plot(t2, R_t, color="#b2182b", lw=0.8, alpha=0.25)
    l_pin, = axt.plot([], [], color="#762a83", lw=1.8, label="run 1: P_in(t) / P_in(final)")
    l_T, = axt.plot([], [], color="#2166ac", lw=1.8, label="run 2: T(t) = P_tran(t) / P_in")
    l_R, = axt.plot([], [], color="#b2182b", lw=1.8, label="run 2: R(t) = -P_refl(t) / P_in")
    for v, c in ((1.0, "#762a83"), (T_fin, "#2166ac"), (R_fin, "#b2182b")):
        axt.axhline(v, color=c, ls="--", lw=0.8)
    axt.text(0.55 * t_all[-1], R_fin + 0.05, f"final R = {R_fin:.2f}", fontsize=8, color="#b2182b")
    axt.text(0.55 * t_all[-1], T_fin - 0.12, f"final T = {T_fin:.2f}", fontsize=8, color="#2166ac")
    t_off = 2 * 5.0 / DF
    axt.axvline(t_off, color="gray", ls=":", lw=0.8); axt.text(t_off + 1, -1.05, "source off", fontsize=7, color="gray")
    cur = axt.axvline(0, color="k", lw=0.8)
    axt.set_xlim(0, t_all[-1]); axt.set_ylim(-1.15, 1.2)
    axt.set_xlabel("time [Meep units a/c, a = 232.5 nm]", fontsize=8)
    axt.set_ylabel(f"accumulated flux at fcen / P_in", fontsize=8)
    axt.tick_params(labelsize=7); axt.grid(alpha=0.3); axt.legend(fontsize=7, loc="upper left")
    sup = fig.suptitle("", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))

    def update(i):
        a, b = f1[h1(i)], f2[h2(i)]
        ims[0].set_data(a.T); ims[1].set_data(b.T); ims[2].set_data((b - a).T)
        j1, j2 = h1(i), h2(i)
        l_pin.set_data(t1[:j1 + 1], np.array(pin_t[:j1 + 1]) / P_in[IC])
        l_T.set_data(t2[:j2 + 1], T_t[:j2 + 1]); l_R.set_data(t2[:j2 + 1], R_t[:j2 + 1])
        cur.set_xdata([t_all[i], t_all[i]])
        sup.set_text(f"Part 05 sharp bend, two-run normalization (fields on one colour scale); t = {t_all[i]:.0f}")

    save(fig, update, n, OUT_FLUX, "01_anim_flux", min(int(100 / DT_B), n - 1))
    info = {"T_final": T_fin, "R_final": R_fin, "t_end_run1": float(t1[-1]), "t_end_run2": float(t2[-1]),
            "R_running_first": float(R_t[0]), "T_at_source_off": float(np.interp(t_off, t2, T_t)),
            "R_at_source_off": float(np.interp(t_off, t2, R_t)), "colour_limit": lim}
    with open(os.path.join(OUT_FLUX, "anim.json"), "w", encoding="utf-8") as fh:
        json.dump(info, fh, indent=1)
    return info


if __name__ == "__main__":
    print("PML", gif_pml())
    print("flux", gif_flux())
