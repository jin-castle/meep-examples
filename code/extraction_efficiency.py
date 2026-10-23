"""Meep Example 14 - A point source in a thin film: the share that escapes into air (light-extraction efficiency).

Post 11 measured how much a dipole emits (LDOS); post 13 split a body of revolution into m runs. An LED asks
the ratio of the two: of all the power a dipole in the emitting layer puts out, how much reaches the air?
    extraction efficiency = P_air (flux through an open surface in air) / P_total (source work from dft_ldos)
  A. Official extraction_eff_ldos.py: a dipole in a dielectric layer (n = 2.4, t = 0.7 wl / n) on a ground
     plane, efficiency vs dipole height, in cylindrical coordinates (Er, m = -1) at resolution 40 and 80 and in
     3D (Ex) at resolution 40. The denominator needs the voxel volume of each coordinate system.
  B. Official point_dipole_cyl.py: the same slab, a dipole 3.5 um off the axis = an m series. The official stop
     rule (first m whose radiated flux < 1 % of the running max) is compared with summing far beyond it: the
     slab-guided light reaches the side monitor through high m and the series rebounds.
  C. Official edge_emitter_2D.py: a z-dipole 0.5 um inside the cleaved facet of a multilayer laser stack.
     The 3D problem is a 2D cross-section plus an integral over the out-of-plane wavevector kz.
MPI-safe: collective calls on every rank, figures on the master only.

Run:  mpirun -np 4 python extraction_efficiency.py      (~40 min)
Out:  00_source.png, 01_layout.png, 02_layout_edge.png, 03_height.png, 04_m_series.png, 05_kz.png,
      06_field.png, 07_anim_edge.gif, result.json   (-> ../assets/14/)
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
from blogfig import Label, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "14")
os.makedirs(OUT, exist_ok=True)
MASTER = mp.am_master()
t_all = time.time()


def say(*a):
    if MASTER:
        print(*a, flush=True)


def orient_rz(arr, nr):
    arr = np.asarray(arr)
    if arr.ndim == 2 and abs(arr.shape[1] - nr) < abs(arr.shape[0] - nr):
        return arr.T
    return arr


def source_work(sim, dV):
    """Total power emitted by the point source: -Re(F J*) dV from the dft_ldos data."""
    return float(-np.real(sim.ldos_Fdata[0] * np.conj(sim.ldos_Jdata[0])) * dV)


# ================================================================ A. dipole in a layer on a ground plane: CYL vs 3D
WL, FREQ, N_L = 1.0, 1.0, 2.4
T_L = 0.7 * WL / N_L                      # layer thickness
DPML, DAIR, L = 0.5, 1.0, 6.0             # PML, air above the layer, lateral size of the collection surface
TOL = 1e-8
HEIGHTS = np.round(np.linspace(0.1, 0.9, 9), 3)      # dipole height above the ground plane, fraction of T_L
H3D = (0.1, 0.5, 0.9)


def layer(sz):
    return [mp.Block(material=mp.Medium(index=N_L), center=mp.Vector3(0, 0, -0.5 * sz + 0.5 * T_L), size=mp.Vector3(mp.inf, mp.inf, T_L))]


def eff_cyl(h, res, want=False):
    sr, sz = L + DPML, T_L + DAIR + DPML
    src_pt = mp.Vector3(1.5 / res, 0, -0.5 * sz + h * T_L)          # Er at r = 0 is undefined on the Yee grid (meep #2704)
    sim = mp.Simulation(resolution=res, cell_size=mp.Vector3(sr, 0, sz), dimensions=mp.CYLINDRICAL, m=-1,
                        boundary_layers=[mp.PML(DPML, direction=mp.R), mp.PML(DPML, direction=mp.Z, side=mp.High)],   # bottom: no PML = ground plane
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.1 * FREQ), component=mp.Er, center=src_pt)], geometry=layer(sz))
    flux = sim.add_flux(FREQ, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * L, 0, 0.5 * sz - DPML), size=mp.Vector3(L, 0, 0)),
                        mp.FluxRegion(center=mp.Vector3(L, 0, 0.5 * sz - DPML - 0.5 * DAIR), size=mp.Vector3(0, 0, DAIR)))
    dft = sim.add_dft_fields([mp.Er], FREQ, 0, 1, center=mp.Vector3(0.5 * L, 0, -0.5 * DPML), size=mp.Vector3(L, 0, sz - DPML)) if want else None
    if want:
        annotated_layout(sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(11, 3.6), axis_step=1.0, unit="um",
                         title="part A, cylindrical (r, z) cell: dipole in a layer (n = 2.4) on a ground plane; x = r, y = z",
                         params_text=f"wl={WL} um, res={res}\nt = 0.7 wl/n = {T_L:.3f} um", params_xy=(3.6, 0.33), pml_xy=(6.05, -0.6),
                         decay_point=(src_pt.x, src_pt.z), decay_text_xy=(1.8, -0.45),
                         labels=[Label("layer n = 2.4 (bottom edge: PEC ground plane, no PML)", (2.5, -0.75), (1.8, -0.2), step=2, color="black"),
                                 Label("Er dipole at r = 1.5 px, height h", (src_pt.x, src_pt.z), (1.8, 0.05), step=3, color="red"),
                                 Label("numerator: flux through top + outer r (air only)", (4.0, 0.5 * sz - DPML), (3.6, -0.2), step=5, color="blue")])
    sim.run(mp.dft_ldos(FREQ, 0, 1), until_after_sources=mp.stop_when_fields_decayed(20, mp.Er, src_pt, TOL))
    p_air = float(mp.get_fluxes(flux)[0])
    p_tot = source_work(sim, 2 * np.pi * src_pt.x / res ** 2)         # CYL voxel: 2 pi r dr dz
    er = orient_rz(sim.get_dft_array(dft, mp.Er, 0), int(round(L * res))) if want else None
    sim.reset_meep()
    return p_air / p_tot, er, sz


def eff_3d(h, res):
    sxy, sz = L + 2 * DPML, T_L + DAIR + DPML
    src_pt = mp.Vector3(0, 0, -0.5 * sz + h * T_L)
    sim = mp.Simulation(resolution=res, cell_size=mp.Vector3(sxy, sxy, sz), symmetries=[mp.Mirror(mp.X, phase=-1), mp.Mirror(mp.Y)],
                        boundary_layers=[mp.PML(DPML, direction=mp.X), mp.PML(DPML, direction=mp.Y), mp.PML(DPML, direction=mp.Z, side=mp.High)],
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.1 * FREQ), component=mp.Ex, center=src_pt)], geometry=layer(sz))
    zc = 0.5 * sz - DPML - 0.5 * DAIR
    flux = sim.add_flux(FREQ, 0, 1, mp.FluxRegion(center=mp.Vector3(0, 0, 0.5 * sz - DPML), size=mp.Vector3(L, L, 0)),
                        mp.FluxRegion(center=mp.Vector3(0.5 * L, 0, zc), size=mp.Vector3(0, L, DAIR)),
                        mp.FluxRegion(center=mp.Vector3(-0.5 * L, 0, zc), size=mp.Vector3(0, L, DAIR), weight=-1.0),
                        mp.FluxRegion(center=mp.Vector3(0, 0.5 * L, zc), size=mp.Vector3(L, 0, DAIR)),
                        mp.FluxRegion(center=mp.Vector3(0, -0.5 * L, zc), size=mp.Vector3(L, 0, DAIR), weight=-1.0))
    sim.run(mp.dft_ldos(FREQ, 0, 1), until_after_sources=mp.stop_when_fields_decayed(20, mp.Ex, src_pt, TOL))
    p_air = float(mp.get_fluxes(flux)[0])
    p_tot = source_work(sim, 1 / res ** 3)                                # 3D voxel
    sim.reset_meep()
    return p_air / p_tot


t_a = time.time()
effA = {"cyl40": [], "cyl80": []}
er_map, sz_A = None, None
for h in HEIGHTS:
    effA["cyl40"].append(eff_cyl(h, 40)[0])
    e80, er, sz = eff_cyl(h, 80, want=(h == 0.5))
    effA["cyl80"].append(e80)
    if er is not None:
        er_map, sz_A = er, sz
say("A (cyl): " + "; ".join(f"h {h:.1f}: res40 {a:.4f}, res80 {b:.4f}" for h, a, b in zip(HEIGHTS, effA["cyl40"], effA["cyl80"])) + f"; {time.time() - t_a:.0f} s")
t_a3 = time.time()
eff3 = {h: eff_3d(h, 40) for h in H3D}
say("A (3D, res 40): " + "; ".join(f"h {h}: {v:.4f} (cyl40 {effA['cyl40'][list(HEIGHTS).index(h)]:.4f}, cyl80 {effA['cyl80'][list(HEIGHTS).index(h)]:.4f})" for h, v in eff3.items()) + f"; {time.time() - t_a3:.0f} s")
if MASTER:
    source_figure(FREQ, 0.1 * FREQ, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ B. off-axis dipole in the slab: the m series and when to stop
t_b = time.time()
RES_B, R_CELL, PML_B, PAD_B = 50, 20.0, 1.0, 1.0
M_MAX = 60
R_SRC = 3.5


def dipole_in_slab(rpos, m):
    sr, sz = R_CELL + PML_B, T_L + PAD_B + PML_B
    src_pt = mp.Vector3(rpos, 0, -0.5 * sz + 0.5 * T_L)
    sim = mp.Simulation(resolution=RES_B, cell_size=mp.Vector3(sr, 0, sz), dimensions=mp.CYLINDRICAL, m=m, force_complex_fields=True,
                        boundary_layers=[mp.PML(PML_B, direction=mp.R), mp.PML(PML_B, direction=mp.Z, side=mp.High)],
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.05 * FREQ), component=mp.Er, center=src_pt)], geometry=layer(sz))
    flux = sim.add_flux(FREQ, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * R_CELL, 0, 0.5 * sz - PML_B), size=mp.Vector3(R_CELL, 0, 0)),
                        mp.FluxRegion(center=mp.Vector3(R_CELL, 0, 0.5 * sz - PML_B - 0.5 * PAD_B), size=mp.Vector3(0, 0, PAD_B)))
    sim.run(mp.dft_ldos(FREQ, 0, 1), until_after_sources=mp.stop_when_dft_decayed(tol=1e-4))
    rad = float(mp.get_fluxes(flux)[0])
    src = source_work(sim, 2 * np.pi * rpos / RES_B ** 2)
    sim.reset_meep()
    return rad, src


r_ax = 1.5 / RES_B
rad_ax, src_ax = dipole_in_slab(r_ax, 1)
eff_axis = rad_ax / src_ax
say(f"B: dipole on the axis (m = 1, r = {r_ax:.2f}): extraction {eff_axis:.4f}")
rads, srcs = [], []
for m in range(M_MAX + 1):
    rad, src = dipole_in_slab(R_SRC, m)
    rads.append(rad); srcs.append(src)
    if m % 5 == 0:
        say(f"B: r {R_SRC}, m = {m}: radiated {rad:.4e}, source {src:.4e}; {time.time() - t_b:.0f} s")
rads, srcs = np.array(rads), np.array(srcs)
w = np.where(np.arange(M_MAX + 1) == 0, 1, 2)                                  # +-m give the same power: count m > 0 twice
running_max = np.maximum.accumulate(rads)
rel = rads / running_max
m_stop = int(next(m for m in range(1, M_MAX + 1) if rel[m] < 1e-2))             # official rule: first m > 0 below 1 % of the running max
eff_series = np.cumsum(w * rads) / np.cumsum(w * srcs)
eff_official = float(eff_series[m_stop]); eff_full = float(eff_series[-1])
rebound = float(rel[m_stop:].max())
m_rebound = int(m_stop + np.argmax(rel[m_stop:]))
say(f"B: official stop at m = {m_stop} (radiated/max {rel[m_stop]:.2e}) -> efficiency {eff_official:.4f}; after the stop the series rebounds to "
    f"{rebound:.3f} of the max at m = {m_rebound}; summed to m = {M_MAX}: efficiency {eff_full:.4f} (last term {rel[-1]:.1e}); {time.time() - t_b:.0f} s")

# ================================================================ C. cleaved-facet edge emitter: 2D cross-section + kz integral
t_c = time.time()
RES_C, CLAD, ACT, SUB, PML_C, AIR_C, SIDE = 25, 0.5, 0.3, 1.0, 0.5, 1.0, 3.0
N_SUB, N_CLAD, N_ACT = 3.2, 1.5, 2.3
DKZ, KZ_TOL, POS_C = 0.02, 0.02, 0.5
CX = PML_C + SIDE + AIR_C + PML_C
CY = PML_C + SUB + CLAD + ACT + CLAD + AIR_C + PML_C
SRC_C = mp.Vector3(-0.5 * CX + PML_C + SIDE - POS_C, -0.5 * CY + PML_C + SUB + CLAD + 0.5 * ACT)


def stack():
    x0 = -0.5 * CX + 0.5 * (PML_C + SIDE); wx = PML_C + SIDE; y = -0.5 * CY
    out = []
    for th, n in ((PML_C + SUB, N_SUB), (CLAD, N_CLAD), (ACT, N_ACT), (CLAD, N_CLAD)):
        out.append(mp.Block(material=mp.Medium(index=n), center=mp.Vector3(x0, y + 0.5 * th), size=mp.Vector3(wx, th, mp.inf))); y += th
    return out


def edge_sim(kz, fwidth=0.1 * FREQ, monitors=True):
    sim = mp.Simulation(resolution=RES_C, cell_size=mp.Vector3(CX, CY), k_point=mp.Vector3(0, 0, kz), kz_2d="real/imag",
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=fwidth), component=mp.Ez, center=SRC_C)], geometry=stack(),
                        boundary_layers=[mp.PML(PML_C)])
    flux = None
    if monitors:
        flux = sim.add_flux(FREQ, 0, 1,
                            mp.FluxRegion(center=mp.Vector3(0, 0.5 * CY - PML_C), size=mp.Vector3(CX - 2 * PML_C, 0)),                 # top
                            mp.FluxRegion(center=mp.Vector3(0.5 * CX - PML_C, 0), size=mp.Vector3(0, CY - 2 * PML_C)),                 # right (in front of the facet)
                            mp.FluxRegion(center=mp.Vector3(0.5 * CX - PML_C - 0.5 * AIR_C, -0.5 * CY + PML_C), size=mp.Vector3(AIR_C, 0), weight=-1.0))   # bottom of the air gap
    return sim, flux


kzs, d_kz, a_kz = [], [], []
nkz, dmax = 0, 0.0
while True:
    kz = nkz * DKZ
    sim, flux = edge_sim(kz)
    if nkz == 0:
        annotated_layout(sim, os.path.join(OUT, "02_layout_edge.png"), dpml=PML_C, figsize=(6.4, 6.0), axis_step=1.0, unit="um",
                         title="part C: cleaved facet of a laser stack (2D x-y); the stack is uniform along z",
                         params_text=f"res={RES_C}, kz step {DKZ}\nsub 3.2 / clad 1.5 / act 2.3", params_xy=(-2.4, 2.25), pml_xy=(-2.4, -2.2), decay_point=None,
                         labels=[Label("Ez dipole 0.5 um inside the facet", (SRC_C.x, SRC_C.y), (-2.4, 1.5), step=3, color="red"),
                                 Label("active layer n = 2.3 between claddings", (-1.5, SRC_C.y), (-2.4, 0.8), step=2, color="black"),
                                 Label("air flux: top + front + under the gap", (1.9, 0.6), (-0.3, 1.9), step=5, color="blue")])
    sim.run(mp.dft_ldos(FREQ, 0, 1), until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, SRC_C, 1e-6))
    dflux = source_work(sim, 1 / RES_C ** 2)            # 2D: a line current, pixel area
    aflux = float(mp.get_fluxes(flux)[0])
    sim.reset_meep()
    kzs.append(kz); d_kz.append(dflux); a_kz.append(aflux)
    nkz += 1
    if dflux > dmax:
        dmax = dflux
    elif dflux / dmax < KZ_TOL:
        break
kzs, d_kz, a_kz = map(np.array, (kzs, d_kz, a_kz))
eff_edge = float((a_kz[0] + 2 * a_kz[1:].sum()) / (d_kz[0] + 2 * d_kz[1:].sum()))
eff_kz0 = float(a_kz[0] / d_kz[0])
kz_cut = N_ACT * FREQ
say(f"C: {len(kzs)} kz points up to {kzs[-1]:.2f} (tail {d_kz[-1] / dmax:.4f}); extraction {100 * eff_edge:.3f} % (kz = 0 alone: {100 * eff_kz0:.2f} %); {time.time() - t_c:.0f} s")

# GIF: kz = 0, short pulse, monitor-free
sim_g, _ = edge_sim(0.0, fwidth=0.4 * FREQ, monitors=False)
sim_g.init_sim()
vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(CX - 2 * PML_C, CY - 2 * PML_C))
eps_g = sim_g.get_array(vol=vol, component=mp.Dielectric)
t0 = 5 / (0.4 * FREQ)
frames, times = record_frames(sim_g, vol, mp.Ez, t_start=t0 - 2 / (0.4 * FREQ), t_end=t0 + 9.0, n_frames=60)
sim_g.reset_meep()

# ================================================================ figures
if MASTER:
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3), gridspec_kw={"width_ratios": [1.4, 1]})
    ax[0].plot(HEIGHTS, effA["cyl80"], "o-", color="tab:blue", label="cylindrical, res 80 (official)")
    ax[0].plot(HEIGHTS, effA["cyl40"], "s--", color="tab:cyan", label="cylindrical, res 40")
    ax[0].plot(list(H3D), [eff3[h] for h in H3D], "D", color="tab:red", ms=8, label="3D Cartesian, res 40")
    ax[0].set_xlabel("dipole height above the ground plane / layer thickness"); ax[0].set_ylabel("extraction efficiency into air")
    ax[0].set_title("dipole in a 0.29 um layer (n = 2.4) on a mirror", fontsize=9); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
    ext = [0, L, -0.5 * sz_A, 0.5 * sz_A - DPML]
    ax[1].imshow(np.log10(np.abs(er_map) + 1e-12).T, extent=ext, origin="lower", cmap="inferno", aspect="auto")
    ax[1].add_patch(plt.Rectangle((0, -0.5 * sz_A), L, T_L, fill=False, color="w", lw=1))
    ax[1].set_xlabel("r [um]"); ax[1].set_ylabel("z [um]"); ax[1].set_title("log10 |Er|, h = 0.5 (res 80): much of the light stays in the layer", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_height.png"), dpi=150); plt.close(fig)

    ms = np.arange(M_MAX + 1)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    ax[0].semilogy(ms, rel, "o-", ms=3, color="tab:blue", label="radiated(m) / running max")
    ax[0].axhline(1e-2, color="crimson", ls="--", lw=1, label="official stop: 1 %")
    ax[0].axvline(m_stop, color="crimson", ls=":", lw=1); ax[0].text(m_stop + 0.5, 2e-1, f"stop at m = {m_stop}", color="crimson", fontsize=8)
    ax[0].plot(m_rebound, rebound, "*", color="tab:orange", ms=12, label=f"rebound {rebound:.2f} at m = {m_rebound}")
    ax[0].axvline(2 * np.pi * N_L * R_SRC, color="gray", ls="-.", lw=1); ax[0].text(2 * np.pi * N_L * R_SRC - 14, 2e-4, "m = 2 pi n r (guided in the slab)", fontsize=8, color="gray")
    ax[0].set_xlabel("azimuthal order m"); ax[0].set_ylabel("radiated power of the m term (relative)"); ax[0].set_title(f"dipole at r = {R_SRC} um in the slab", fontsize=9); ax[0].grid(alpha=0.3, which="both"); ax[0].legend(fontsize=7)
    ax[1].plot(ms, eff_series, "-", color="tab:green"); ax[1].axvline(m_stop, color="crimson", ls=":", lw=1)
    ax[1].axhline(eff_axis, color="tab:purple", ls="--", lw=1, label=f"dipole on the axis: {eff_axis:.3f}")
    ax[1].plot(m_stop, eff_official, "o", color="crimson", label=f"official stop: {eff_official:.3f}")
    ax[1].plot(M_MAX, eff_full, "o", color="tab:green", label=f"summed to m = {M_MAX}: {eff_full:.3f}")
    ax[1].set_xlabel("m included up to"); ax[1].set_ylabel("extraction efficiency"); ax[1].set_title("the efficiency depends on where the series is cut", fontsize=9); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_m_series.png"), dpi=150); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    ax[0].plot(kzs, d_kz / d_kz.max(), "o-", ms=3, color="tab:gray", label="total (dft_ldos)")
    ax[0].plot(kzs, a_kz / d_kz.max(), "o-", ms=3, color="tab:blue", label="into air")
    for kc, lab in ((FREQ, "kz = k0 (air light line)"), (N_CLAD * FREQ, "1.5 k0"), (N_ACT * FREQ, "2.3 k0")):
        ax[0].axvline(kc, color="k", ls=":", lw=0.8); ax[0].text(kc + 0.02, 0.9, lab, fontsize=7, rotation=90, va="top")
    ax[0].set_xlabel("kz [2 pi / um]"); ax[0].set_ylabel("power per kz (relative)"); ax[0].set_title(f"{len(kzs)} 2D runs, one per kz", fontsize=9); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
    cum = (np.cumsum(np.where(np.arange(len(kzs)) == 0, 1, 2) * a_kz)) / (np.cumsum(np.where(np.arange(len(kzs)) == 0, 1, 2) * d_kz))
    ax[1].plot(kzs, 100 * cum, "-", color="tab:green"); ax[1].axhline(100 * eff_edge, color="tab:green", ls="--", lw=1)
    ax[1].axhline(100 * eff_kz0, color="tab:orange", ls=":", lw=1.2, label=f"kz = 0 alone (2D line source): {100 * eff_kz0:.1f} %")
    ax[1].set_xlabel("kz included up to"); ax[1].set_ylabel("extraction efficiency [%]"); ax[1].set_title(f"kz integral: {100 * eff_edge:.2f} % into air", fontsize=9); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_kz.png"), dpi=150); plt.close(fig)

    animate_fields(frames, times, [-(0.5 * CX - PML_C), 0.5 * CX - PML_C, -(0.5 * CY - PML_C), 0.5 * CY - PML_C], os.path.join(OUT, "07_anim_edge.gif"),
                   eps=eps_g, figsize=(5.6, 5.0), dpi=70, clip_percentile=99.0, points=[(SRC_C.x, SRC_C.y, "red", "dipole")],
                   title="edge emitter, kz = 0", legend_loc="lower left")
    with open(os.path.join(OUT, "result.json"), "w") as f_:
        json.dump({"A": {"heights": HEIGHTS.tolist(), "cyl40": effA["cyl40"], "cyl80": effA["cyl80"], "3d40": {str(k): v for k, v in eff3.items()}},
                   "B": {"r": R_SRC, "eff_axis": eff_axis, "m_stop": m_stop, "eff_official": eff_official, "eff_full": eff_full, "rebound": rebound,
                         "m_rebound": m_rebound, "rel": rel.tolist(), "eff_series": eff_series.tolist()},
                   "C": {"n_kz": len(kzs), "kz_max": float(kzs[-1]), "tail": float(d_kz[-1] / dmax), "eff": eff_edge, "eff_kz0": eff_kz0},
                   "wall_s_total": time.time() - t_all, "np": mp.count_processors(), "meep": mp.__version__}, f_, indent=2)
say(f"total {time.time() - t_all:.0f} s on {mp.count_processors()} process(es)")
