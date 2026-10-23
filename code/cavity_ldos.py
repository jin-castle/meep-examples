"""Meep Example 11 - A point dipole between two mirrors: LDOS and the Purcell factor.

Post 10 showed that one mirror rewrites the radiation pattern. Here the dipole sits between two mirrors and the
question is the emitted POWER itself, measured as the local density of states (LDOS) at the dipole position.
  A. Planar cavity (official planar_cavity_ldos.py): lossless metallic walls, dielectric n = 2.4, in-plane dipole.
     The Purcell factor F = LDOS(cavity) / LDOS(bulk) versus the normalized thickness t = n L / wl, swept in
     cylindrical coordinates (Er, m = -1 represents an x-dipole) and checked at two thicknesses in full 3D.
     Compared with the analytic Eq. 7 of Abram et al. (1998): F = 3N/(4t) + (4N^3 - N)/(16 t^3), N = fix(t + 1/2).
  B. Metal box with an aperture (official metal-cavity-ldos.py, 2D): Harminv gives f and Q of the fundamental mode;
     the LDOS at f is measured directly with dft_ldos and compared with the single-mode estimate 2Q/(pi w V).
     The required run time 2Q/f grows with Q; the narrowest aperture is deliberately left under-converged.

Run:  python cavity_ldos.py       (~15 min on one core)
Out:  00_source.png, 01_layout.png, 02_layout_cyl.png, 03_purcell.png, 04_cavity_field.png, 05_metal_ldos.png,
      06_anim_planar.gif, 07_anim_metal.gif, result.json   (-> ../assets/11/)
"""
import json
import math
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, _badge, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "11")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()

# =================================================================== A. planar cavity with lossless metallic walls
# ---------------------------------------------------------------- (1) parameters (official values; 21-point sweep instead of 41)
WL = 1.0
FCEN = 1 / WL
FWIDTH = 0.2 * FCEN
N_CAV = 2.4
RES_CYL = 71
RES_3D = 48                              # 3D cross-check only (official: 71)
DPML = 0.5
BULK_CYL, BULK_3D = 6.0, 3.0
DECAY_TOL, DECAY_PERIOD = 1e-6, 20
T_NORM = np.round(np.arange(0.5, 2.51, 0.1), 2)          # t = n L / wl; cutoffs at 0.5, 1.5, 2.5
T_3D = (1.0, 2.0)                                         # thicknesses checked in full 3D


def purcell_theory(t):
    N = np.fix(t + 0.5)
    return 3 * N / (4 * t) + (4 * N ** 3 - N) / (16 * t ** 3)


def ldos_cyl(cavity_um=None, *, want_field=False):
    """LDOS of an in-plane dipole (Er, m = -1) in cylindrical coordinates; bulk medium if cavity_um is None."""
    if cavity_um is None:
        cell_z, pml = BULK_CYL + 2 * DPML, [mp.PML(thickness=DPML)]
    else:
        cell_z, pml = cavity_um, [mp.PML(thickness=DPML, direction=mp.R)]      # no z PML: the cell walls are the mirrors
    cell_r = BULK_CYL + DPML
    src_pt = mp.Vector3(1.5 / RES_CYL, 0, 0)                                    # Er at r = 0 is singular: offset by 1.5 px
    sim = mp.Simulation(resolution=RES_CYL, cell_size=mp.Vector3(cell_r, 0, cell_z), boundary_layers=pml, dimensions=mp.CYLINDRICAL, m=-1,
                        default_material=mp.Medium(index=N_CAV),
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Er, center=src_pt)])
    dft = sim.add_dft_fields([mp.Er], FCEN, 0, 1, center=mp.Vector3(0.5 * BULK_CYL, 0, 0), size=mp.Vector3(BULK_CYL, 0, cell_z)) if want_field else None
    sim.run(mp.dft_ldos(FCEN, 0, 1), until_after_sources=mp.stop_when_fields_decayed(DECAY_PERIOD, mp.Er, src_pt, DECAY_TOL))
    ldos = float(sim.ldos_data[0]); t_end = sim.meep_time()
    field = sim.get_dft_array(dft, mp.Er, 0) if want_field else None
    sim.reset_meep()
    return (ldos, t_end, field) if want_field else (ldos, t_end)


def ldos_3d(cavity_um=None):
    """LDOS of an Ex dipole in full 3D (reduced resolution); bulk if cavity_um is None."""
    if cavity_um is None:
        size_z, pml = BULK_3D + 2 * DPML, [mp.PML(thickness=DPML)]
    else:
        size_z, pml = cavity_um, [mp.PML(thickness=DPML, direction=mp.X), mp.PML(thickness=DPML, direction=mp.Y)]
    size_xy = BULK_3D + 2 * DPML
    sim = mp.Simulation(resolution=RES_3D, cell_size=mp.Vector3(size_xy, size_xy, size_z), boundary_layers=pml,
                        default_material=mp.Medium(index=N_CAV),
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Ex, center=mp.Vector3())],
                        symmetries=[mp.Mirror(mp.X, phase=-1), mp.Mirror(mp.Y), mp.Mirror(mp.Z)])      # Ex is odd under x, even under y, z
    sim.run(mp.dft_ldos(FCEN, 0, 1), until_after_sources=mp.stop_when_fields_decayed(DECAY_PERIOD, mp.Ex, mp.Vector3(), DECAY_TOL))
    ldos = float(sim.ldos_data[0]); t_end = sim.meep_time(); sim.reset_meep()
    return ldos, t_end


source_figure(FCEN, FWIDTH, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# layout of the CYL cavity (r-z plane) at t = 1.0, drawn by hand: the cell is 6.5 x 0.42 um, far too thin for plot2D
L_demo = 1.0 * WL / N_CAV
fig, ax = plt.subplots(figsize=(9.5, 3.6))
ax.axvspan(BULK_CYL, BULK_CYL + DPML, color="green", alpha=0.25)
ax.axhline(0.5 * L_demo, color="k", lw=4); ax.axhline(-0.5 * L_demo, color="k", lw=4)
ax.plot(1.5 / RES_CYL, 0, "o", color="red", ms=7); ax.axvline(0, color="gray", ls="-.", lw=1)
for xy, step, color, txt, txy in (((0.25, 0.5 * L_demo - 0.03), 1, "dimgray", f"wl={WL} um, n={N_CAV}, res={RES_CYL}\ncell r {BULK_CYL + DPML} um x z L={L_demo:.3f} um, m=-1", (0.45, 0.5 * L_demo - 0.03)),
                                   ((3.0, 0.5 * L_demo), 2, "black", "top/bottom cell walls: no PML here, so they are PEC = the two mirrors", (3.2, 0.5 * L_demo - 0.035)),
                                   ((1.5 / RES_CYL, -0.035), 3, "red", "Er dipole (m = -1 = an in-plane dipole) at r = 1.5 px, the axis is singular", (0.45, -0.045)),
                                   ((BULK_CYL + 0.5 * DPML, 0.0), 4, "green", "PML (r only)", (BULK_CYL + 0.08, 0.04)),
                                   ((0.4, 0.07), 5, "blue", "LDOS: dft_ldos at the source point (no spatial monitor); bulk run = same cell with PML on z too", (0.6, 0.06)),
                                   ((1.5 / RES_CYL, 0.11), 6, "purple", "decay watch point = source point", (0.45, 0.10))):
    _badge(ax, xy, step, color); ax.text(*txy, txt, fontsize=8, color=color, va="center")
ax.text(0.05, -0.5 * L_demo + 0.01, "r = 0 (axis)", fontsize=7, color="gray", rotation=90, va="bottom")
ax.set_xlim(-0.1, BULK_CYL + DPML); ax.set_ylim(-0.5 * L_demo - 0.02, 0.5 * L_demo + 0.02)
ax.set_xlabel("r [um]"); ax.set_ylabel("z [um]  (stretched)")
ax.set_title("part A: cylindrical r-z cell at t = 1.0. The z axis is stretched 6x; the real cell is a thin disc between two mirrors", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_layout_cyl.png"), dpi=150); plt.close(fig)

t_a = time.time()
bulk_cyl, t_bulk_cyl = ldos_cyl()
purcell_cyl, t_end_cyl, fields = [], [], {}
for t in T_NORM:
    L = t * WL / N_CAV
    if t in (1.0, 2.0):
        ldos, t_end, fld = ldos_cyl(L, want_field=True); fields[t] = (fld, L)
    else:
        ldos, t_end = ldos_cyl(L)
    purcell_cyl.append(ldos / bulk_cyl); t_end_cyl.append(t_end)
purcell_cyl = np.array(purcell_cyl)
theory = purcell_theory(T_NORM)
cutoff = np.isclose(np.mod(T_NORM, 1.0), 0.5)
err_cyl = np.abs(purcell_cyl - theory) / theory
print(f"A (cyl): bulk LDOS {bulk_cyl:.5f} (t_end {t_bulk_cyl:.0f}); {len(T_NORM)} thicknesses in {time.time() - t_a:.0f} s; "
      f"rel error vs Eq. 7 away from cutoffs: median {np.median(err_cyl[~cutoff]):.4f}, max {err_cyl[~cutoff].max():.4f} at t = {T_NORM[~cutoff][np.argmax(err_cyl[~cutoff])]:.2f}; "
      f"at the cutoffs: " + ", ".join(f"t={t:.1f}: Meep {p:.3f} vs Eq.7 {th:.3f}" for t, p, th in zip(T_NORM[cutoff], purcell_cyl[cutoff], theory[cutoff])))

t_a = time.time()
bulk_3d, t_bulk_3d = ldos_3d()
purcell_3d = {}
for t in T_3D:
    ldos, t_end = ldos_3d(t * WL / N_CAV)
    purcell_3d[t] = ldos / bulk_3d
print(f"A (3D, res {RES_3D}): bulk LDOS {bulk_3d:.5f} (t_end {t_bulk_3d:.0f}); " + ", ".join(f"t={t}: 3D {purcell_3d[t]:.4f} vs cyl {purcell_cyl[np.isclose(T_NORM, t)][0]:.4f} vs Eq.7 {purcell_theory(t):.4f}" for t in T_3D)
      + f"; {time.time() - t_a:.0f} s")

fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
tt = np.linspace(0.5, 2.5, 801)
ax[0].plot(tt, purcell_theory(tt), "-", color="k", lw=1.2, label="Eq. 7 (Abram 1998)")
ax[0].plot(T_NORM, purcell_cyl, "o", color="tab:red", ms=5, label=f"Meep cylindrical (Er, m = -1), res {RES_CYL}")
ax[0].plot(list(T_3D), [purcell_3d[t] for t in T_3D], "s", color="tab:blue", ms=7, label=f"Meep 3D (Ex), res {RES_3D}")
for tc in (0.5, 1.5, 2.5):
    ax[0].axvline(tc, color="gray", ls=":", lw=1)
ax[0].axhline(1, color="gray", ls="--", lw=1); ax[0].text(2.3, 1.03, "bulk", fontsize=8, color="gray")
ax[0].set_xlabel("normalized cavity thickness t = n L / wavelength"); ax[0].set_ylabel("Purcell factor  LDOS(cavity) / LDOS(bulk)")
ax[0].set_title("in-plane dipole between two lossless mirrors (n = 2.4): a new mode opens at every half-integer", fontsize=9)
ax[0].set_ylim(0.4, 3.2); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
ax[1].bar(T_NORM[~cutoff], 100 * err_cyl[~cutoff], width=0.07, color="tab:red", alpha=0.7, label="cylindrical")
ax[1].bar(T_NORM[cutoff], 100 * err_cyl[cutoff], width=0.07, color="lightgray", label="at a cutoff (excluded)")
for t in T_3D:
    ax[1].plot(t, 100 * abs(purcell_3d[t] - purcell_theory(t)) / purcell_theory(t), "s", color="tab:blue", ms=7)
ax[1].set_xlabel("t"); ax[1].set_ylabel("|Meep - Eq. 7| / Eq. 7  [%]"); ax[1].set_title(f"error: median {100 * np.median(err_cyl[~cutoff]):.2f} % away from cutoffs", fontsize=9)
ax[1].grid(axis="y", alpha=0.3); ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_purcell.png"), dpi=150); plt.close(fig)

fig, ax = plt.subplots(2, 1, figsize=(10, 5.2))
for a, t in zip(ax, (1.0, 2.0)):
    fld, L = fields[t]
    # NOTE: in cylindrical coordinates get_dft_array / get_array return (z, r), not (r, z): no transpose here
    fld = fld[2:-2, :]                                      # drop the two grid rows touching each mirror (boundary pixels of the DFT array)
    nz = fld.shape[0]; dz = L / (nz + 4)
    ext = [0, BULK_CYL, -0.5 * L + 2 * dz, 0.5 * L - 2 * dz]
    lim = float(np.percentile(np.abs(fld), 99.5))           # the source pixel dominates the maximum: clip the colour scale
    a.imshow(np.real(fld), extent=ext, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="auto")
    a.axhline(0.5 * L, color="k", lw=2); a.axhline(-0.5 * L, color="k", lw=2); a.plot(1.5 / RES_CYL, 0, "o", color="lime", ms=4)
    a.set_title(f"Re(Er) at t = {t:.1f} (L = {L:.3f} um): F = {purcell_cyl[np.isclose(T_NORM, t)][0]:.3f}   (thick black lines = mirrors)", fontsize=9)
    a.set_ylabel("z [um]")
ax[1].set_xlabel("r [um]")
fig.suptitle("part A: steady-state field between the mirrors, cylindrical r-z plane", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_cavity_field.png"), dpi=150); plt.close(fig)

# GIF: a short pulse between the mirrors at t = 1.0 (r-z plane)
L = 1.0 * WL / N_CAV
fw_anim = 0.5 * FCEN
sim_g = mp.Simulation(resolution=RES_CYL, cell_size=mp.Vector3(BULK_CYL + DPML, 0, L), boundary_layers=[mp.PML(thickness=DPML, direction=mp.R)],
                      dimensions=mp.CYLINDRICAL, m=-1, default_material=mp.Medium(index=N_CAV),
                      sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=fw_anim), component=mp.Er, center=mp.Vector3(1.5 / RES_CYL, 0, 0))])
sim_g.init_sim()
vol_g = mp.Volume(center=mp.Vector3(0.5 * BULK_CYL, 0, 0), size=mp.Vector3(BULK_CYL, 0, L))
t0g = 5 / fw_anim
frames, times = record_frames(sim_g, vol_g, mp.Er, t_start=t0g - 2 / fw_anim, t_end=t0g + 1.1 * BULK_CYL * N_CAV, n_frames=60)
frames = [f.T for f in frames]                      # cylindrical get_array returns (z, r); animate_fields expects (x, y) = (r, z)
animate_fields(frames, times, [0, BULK_CYL, -0.5 * L, 0.5 * L], os.path.join(OUT, "06_anim_planar.gif"), figsize=(7.5, 2.8), dpi=70, aspect="auto",
               component="Er", unit="um", xlabel="r [um]", ylabel="z [um] (stretched)", clip_percentile=99.0,
               lines=[((0, 0.5 * L), (BULK_CYL, 0.5 * L), "k", "mirrors (cell walls)"), ((0, -0.5 * L), (BULK_CYL, -0.5 * L), "k", "_nolegend_")],
               points=[(1.5 / RES_CYL, 0, "red", "dipole")], title="planar cavity, t = 1.0", legend_loc="upper right")
sim_g.reset_meep()

# =================================================================== B. metal box with an aperture (2D), official metal-cavity-ldos.py
RES_M = 50
A_BOX, T_WALL, DPML_M = 1.0, 0.1, 1.0
SXY = 2.0 + 2 * DPML_M
FCEN_M = math.sqrt(0.5) / A_BOX                      # fundamental mode of the closed a x a box
DF_M = 0.2
WS = (0.2, 0.3, 0.4, 0.5)
T_MAX = 6000.0                                        # cap on the dft_ldos run (the official 2Q/f is not capped)
V_MODE = 0.25 * A_BOX ** 2                            # modal volume of the fundamental mode, analytic


def metal_box(w):
    return [mp.Block(mp.Vector3(A_BOX + 2 * T_WALL, A_BOX + 2 * T_WALL, mp.inf), material=mp.metal),
            mp.Block(mp.Vector3(A_BOX, A_BOX, mp.inf), material=mp.air),
            mp.Block(center=mp.Vector3(A_BOX / 2), size=mp.Vector3(2 * T_WALL, w, mp.inf), material=mp.air)]     # the aperture in the right wall


def make_sim(w, sources):
    return mp.Simulation(cell_size=mp.Vector3(SXY, SXY), geometry=metal_box(w), boundary_layers=[mp.PML(DPML_M)], sources=sources,
                         symmetries=[mp.Mirror(mp.Y)], resolution=RES_M)


src_M = [mp.Source(mp.GaussianSource(FCEN_M, fwidth=DF_M), component=mp.Ez, center=mp.Vector3())]
sim_lay = make_sim(0.3, src_M)
sim_lay.add_dft_fields([mp.Ez], FCEN_M, 0, 1, center=mp.Vector3(), size=mp.Vector3(2, 2))
annotated_layout(sim_lay, os.path.join(OUT, "01_layout.png"), dpml=DPML_M, figsize=(6.4, 6.0), axis_step=1.0,
                 title="part B: metal box 1 x 1 um, wall 0.1, aperture w = 0.3 (plot2D draws mp.metal white)",
                 params_text=f"a={A_BOX}, t={T_WALL}, res={RES_M}\nfcen=sqrt(0.5)/a={FCEN_M:.3f}", params_xy=(-1.9, 1.75),
                 pml_xy=(-1.9, -1.5), decay_point=None,
                 labels=[Label("Ez dipole at the center: Harminv probe and dft_ldos point", (0.02, 0.0), (-1.9, 1.2), step=3, color="red"),
                         Label("metal walls (mp.metal)", (-0.55, 0.3), (-1.9, 0.75), step=2, color="black"),
                         Label("aperture w: the only leak", (0.6, 0.0), (0.75, -0.9), step=2, color="black"),
                         Label("DFT Ez map (representative)", (-0.9, -0.9), (-1.9, -1.2), step=5, color="blue")])
sim_lay.reset_meep()

res_M = {}
t_b = time.time()
for w in WS:
    sim = make_sim(w, src_M)
    h = mp.Harminv(mp.Ez, mp.Vector3(), FCEN_M, DF_M)
    sim.run(mp.after_sources(h), until_after_sources=500)
    modes = [m for m in h.modes if m.Q > 0]
    m = max(modes, key=lambda mm: mm.Q)
    f, Q = float(m.freq), float(m.Q)
    sim.reset_meep()
    ldos_qv = Q / V_MODE / (2 * math.pi * f * math.pi * 0.5)          # 2Q / (pi w V), w = 2 pi f
    T_req = 2 * Q / f
    T_run = min(T_req, T_MAX)
    sim = make_sim(w, src_M)
    nfreq = 101
    df_spec = 8 * f / Q                                               # spectrum: +-4 linewidths around the Harminv frequency
    dft = sim.add_dft_fields([mp.Ez], f, 0, 1, center=mp.Vector3(), size=mp.Vector3(2, 2)) if w == 0.3 else None
    sim.run(mp.dft_ldos(f, df_spec, nfreq), until_after_sources=T_run)
    freqs = np.array(sim.ldos_freqs if hasattr(sim, "ldos_freqs") else np.linspace(f - 0.5 * df_spec, f + 0.5 * df_spec, nfreq))
    spec = np.array(sim.ldos_data)
    ez = sim.get_dft_array(dft, mp.Ez, 0) if dft is not None else None
    sim.reset_meep()
    ldos_f = float(spec[nfreq // 2])
    half = spec >= 0.5 * spec.max()
    fwhm = float(freqs[half].max() - freqs[half].min()) if half.sum() > 1 else float("nan")
    res_M[w] = {"f": f, "Q": Q, "ldos_qv": ldos_qv, "ldos_dft": ldos_f, "T_req": T_req, "T_run": T_run, "converged": T_run >= T_req,
                "spec_f": freqs, "spec": spec, "fwhm": fwhm, "Q_spec": f / fwhm if fwhm == fwhm else float("nan"), "ez": ez}
    print(f"B [w = {w}]: Harminv f {f:.5f}, Q {Q:.0f}; 2Q/f = {T_req:.0f} -> ran {T_run:.0f}{'' if T_run >= T_req else ' (CAPPED, under-converged)'}; "
          f"LDOS: Q/V estimate {ldos_qv:.4f}, dft_ldos {ldos_f:.4f}, ratio {ldos_f / ldos_qv:.3f}; spectrum FWHM {fwhm:.2e} -> Q {f / fwhm if fwhm == fwhm else float('nan'):.0f}")
print(f"B done in {time.time() - t_b:.0f} s")

fig = plt.figure(figsize=(13.5, 4.4))
ax = fig.add_subplot(1, 3, 1)
for w, c in zip(WS, ("tab:red", "tab:orange", "tab:green", "tab:blue")):
    r = res_M[w]
    ax.plot((r["spec_f"] - r["f"]) / r["f"] * 1e3, r["spec"] / r["spec"].max(), "-", color=c, lw=1.4, label=f"w = {w}: Q_Harminv {r['Q']:.0f}, Q_spectrum {r['Q_spec']:.0f}" + ("" if r["converged"] else " (capped)"))
ax.set_xlabel("(f - f_res) / f_res  [x 1e-3]"); ax.set_ylabel("LDOS / peak"); ax.set_title("dft_ldos spectrum around the resonance: width = f / Q", fontsize=9); ax.grid(alpha=0.3); ax.legend(fontsize=7)
ax = fig.add_subplot(1, 3, 2)
inv_w = [A_BOX / w for w in WS]
ax.semilogy(inv_w, [res_M[w]["ldos_qv"] for w in WS], "bo-", label="2Q / (pi w V)  (Harminv Q, analytic V)")
ax.semilogy(inv_w, [res_M[w]["ldos_dft"] for w in WS], "rs-", label="dft_ldos at f_res")
for w in WS:
    if not res_M[w]["converged"]:
        ax.annotate("under-converged\n(run capped)", (A_BOX / w, res_M[w]["ldos_dft"]), textcoords="offset points", xytext=(-70, -28), fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.set_xlabel("a / w"); ax.set_ylabel("LDOS at the resonance"); ax.set_title("narrower aperture: higher Q, higher LDOS", fontsize=9); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=7)
ax = fig.add_subplot(1, 3, 3)
ez = res_M[0.3]["ez"]; lim = float(np.percentile(np.abs(ez), 96.0))     # clip: the source pixel dominates, and 3/4 of the map is outside the box
ax.imshow(np.real(ez).T, extent=[-1, 1, -1, 1], origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
ax.add_patch(plt.Rectangle((-0.5, -0.5), 1, 1, fill=False, color="k", lw=1.2)); ax.add_patch(plt.Rectangle((0.5, -0.15), 0.2, 0.3, fill=False, color="k", lw=1.0, ls="--"))
ax.set_title(f"Re(Ez) at f_res, w = 0.3: fundamental mode sin(pi x/a) sin(pi y/a)", fontsize=9); ax.set_xlabel("x [um]"); ax.set_ylabel("y [um]")
fig.suptitle("part B: a point dipole in a metal box with one aperture", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.93]); fig.savefig(os.path.join(OUT, "05_metal_ldos.png"), dpi=150); plt.close(fig)

# GIF: the box rings and leaks through the aperture (w = 0.4, monitor-free)
sim_g = make_sim(0.4, [mp.Source(mp.GaussianSource(FCEN_M, fwidth=0.4 * FCEN_M), component=mp.Ez, center=mp.Vector3())])
sim_g.init_sim()
vol_g = mp.Volume(center=mp.Vector3(), size=mp.Vector3(2, 2))
eps_g = sim_g.get_array(vol=vol_g, component=mp.Dielectric)
eps_g = np.where(np.isfinite(eps_g), eps_g, 100.0)
t0g = 5 / (0.4 * FCEN_M)
frames, times = record_frames(sim_g, vol_g, mp.Ez, t_start=t0g - 2 / (0.4 * FCEN_M), t_end=t0g + 40, n_frames=60)
animate_fields(frames, times, [-1, 1, -1, 1], os.path.join(OUT, "07_anim_metal.gif"), eps=eps_g, figsize=(5.4, 4.8), dpi=70, clip_percentile=99.0,
               points=[(0, 0, "red", "dipole")], lines=[((0.6, -0.2), (0.6, 0.2), "blue", "aperture w = 0.4")], title="metal box", legend_loc="lower left")
sim_g.reset_meep()

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f_:
        json.dump({"A": {"wl": WL, "n": N_CAV, "res_cyl": RES_CYL, "res_3d": RES_3D, "t": T_NORM.tolist(), "purcell_cyl": purcell_cyl.tolist(), "theory": theory.tolist(),
                         "err_cyl": err_cyl.tolist(), "cutoff": cutoff.tolist(), "median_err_away": float(np.median(err_cyl[~cutoff])), "max_err_away": float(err_cyl[~cutoff].max()),
                         "bulk_cyl": bulk_cyl, "bulk_3d": bulk_3d, "purcell_3d": {str(k): v for k, v in purcell_3d.items()}, "t_end_cyl": [float(x) for x in t_end_cyl]},
                   "B": {str(w): {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in r.items() if k != "ez"} for w, r in res_M.items()},
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f_, indent=2)
print(f"total {time.time() - t_all:.0f} s")
