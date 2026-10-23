"""Meep Example 13 - Computing 3D with rotational symmetry: cylindrical coordinates and the m series.

Post 12's ring was a 2D cross-section. A real disc or ring is a body of revolution, and Meep's
dimensions=mp.CYLINDRICAL solves it as one 2D (r, z) run per azimuthal order m, with fields ~ exp(i m phi).
  A. On-axis dipoles in vacuum (official dipole_in_vacuum_cyl_on_axis.py): a z-dipole is m = 0 (Ez);
     an x-dipole is NOT m = 0 but the sum of m = +1 and m = -1 (Er + i Ep, Er - i Ep). Far-field
     patterns vs the analytic cos^2(theta) and sin^2(theta).
  B. An off-axis x-dipole at r = 0.5 um (official dipole_in_vacuum_cyl_off_axis.py): a point away from
     the axis is a Fourier series over m = 0, 1, 2, ... The series is summed until the power of the last
     m drops below 1e-4 of the largest; the pattern is checked after every added m.
  C. The ring of post 12 in cylindrical coordinates (official ring-cyl.py): one 1D radial run per m.
     Frequencies and Q compared with post 12's 2D Cartesian values; the m = 3 field rebuilt in the
     x-y plane from Ez(r) exp(i m phi).
  D. A dielectric disc on a ground plane (official disc_radiation_pattern.py): a ring source (m = -1),
     near flux vs far-field flux; the 7 % gap comes from the open near2far surface, checked by
     enlarging the radial cell.
MPI-safe: collective calls on every rank, figures on the master only.

Run:  mpirun -np 4 python cylindrical_dipole.py     (~6 min)
Out:  00_source.png, 01_layout.png, 02_layout_dipole.png, 03_on_axis.png, 04_off_axis.png, 05_ring_cyl.png,
      06_disc.png, 07_anim_m3.gif, result.json   (-> ../assets/13/)
"""
import cmath
import json
import math
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, annotated_layout, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "13")
os.makedirs(OUT, exist_ok=True)
MASTER = mp.am_master()
t_all = time.time()


def say(*a):
    if MASTER:
        print(*a, flush=True)


def rel_l2(a, b):
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)) / np.linalg.norm(np.asarray(b)))


def orient_rz(arr, nr):
    """Cylindrical get_array/get_dft_array return (z, r) in this Meep version; return (r, z) whatever the order."""
    arr = np.asarray(arr)
    if arr.ndim == 2 and abs(arr.shape[1] - nr) < abs(arr.shape[0] - nr):
        return arr.T
    return arr


# ---------------------------------------------------------------- (1) parameters shared by A and B (official values, um)
WL = 1.0
FREQ = 1 / WL
RES_D = 50
PML_D = 1.0
SR_D, SZ_D = 2.0, 4.0                       # near2far box: r 0..2, z -2..2
R_FF = 1e6 * WL
NPTS = 50
THETA = np.linspace(0, 0.5 * np.pi, NPTS)   # 0 = +z (pole), pi/2 = +r (equator), in the phi = 0 plane
GREENCYL_TOL = 1e-6
POWER_DECAY = 1e-4


def n2f_regions(sr, sz):
    return [mp.FluxRegion(center=mp.Vector3(0.5 * sr, 0, 0.5 * sz), size=mp.Vector3(sr, 0, 0)),
            mp.FluxRegion(center=mp.Vector3(sr, 0, 0), size=mp.Vector3(0, 0, sz)),
            mp.FluxRegion(center=mp.Vector3(0.5 * sr, 0, -0.5 * sz), size=mp.Vector3(sr, 0, 0), weight=-1.0)]


def farfields(sim, n2f, tol=GREENCYL_TOL, theta=THETA, r_ff=R_FF):
    e = np.zeros((len(theta), 3), complex); h = np.zeros((len(theta), 3), complex)
    for n, th in enumerate(theta):
        ff = sim.get_farfield(n2f, mp.Vector3(r_ff * math.sin(th), 0, r_ff * math.cos(th)), tol)
        e[n] = ff[:3]; h[n] = ff[3:]
    return e, h


def radial_flux(e, h):
    fx = np.real(e[:, 1] * np.conj(h[:, 2]) - e[:, 2] * np.conj(h[:, 1]))
    fz = np.real(e[:, 0] * np.conj(h[:, 1]) - e[:, 1] * np.conj(h[:, 0]))
    return np.sqrt(fx ** 2 + fz ** 2)


def total_flux(pattern, theta=THETA, r_ff=R_FF):
    return float(2 * np.pi * r_ff ** 2 * np.trapezoid(pattern * np.sin(theta), theta))


def dipole_sim(m, sources):
    return mp.Simulation(resolution=RES_D, cell_size=mp.Vector3(SR_D + PML_D, 0, SZ_D + 2 * PML_D), dimensions=mp.CYLINDRICAL, m=m,
                         boundary_layers=[mp.PML(thickness=PML_D)], sources=sources, force_complex_fields=True)


# ================================================================ A. on-axis dipoles
t_a = time.time()
r_off = 1.5 / RES_D                          # an Er source exactly at r = 0 hits a known bug (meep issue 2704): offset by 1.5 px
gs = lambda f: mp.GaussianSource(f, fwidth=0.1 * abs(f))
on = {}
# z-dipole: m = 0, Ez on the axis
sim = dipole_sim(0, [mp.Source(gs(FREQ), component=mp.Ez, center=mp.Vector3())])
annotated_layout(sim, os.path.join(OUT, "02_layout_dipole.png"), dpml=PML_D, figsize=(5.4, 7.6), axis_step=1.0, unit="um",
                 title="parts A, B: cylindrical (r, z) cell; r = 0 is the left edge (the axis)",
                 params_text=f"wl={WL} um, res={RES_D}\nm = 0, +-1 (A)\nm = 0..8 (B)", params_xy=(0.15, 3.75), pml_xy=(0.15, -3.5), decay_point=None,
                 labels=[Label("dipole on the axis (A) or at r = 0.5 (B)", (0.03, 0.0), (0.4, 0.9), step=3, color="red"),
                         Label("near2far: top, outer r, bottom (weight -1)", (2.0, 1.0), (0.4, 2.6), step=5, color="blue"),
                         Label("vacuum: no geometry", (1.0, -1.0), (0.4, -1.4), step=2, color="black")])
n2f = sim.add_near2far(FREQ, 0, 1, *n2f_regions(SR_D, SZ_D))
sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(), 1e-6))
on["z"] = farfields(sim, n2f); sim.reset_meep()
# x-dipole: m = +1 and m = -1, each Er + (+-i) Ep, combined with weight 1/2 and exp(+-i phi) at phi = 0
ex = np.zeros((NPTS, 3), complex); hx = np.zeros((NPTS, 3), complex)
for m in (+1, -1):
    src = [mp.Source(gs(FREQ), component=mp.Er, center=mp.Vector3(r_off)),
           mp.Source(gs(FREQ), component=mp.Ep, center=mp.Vector3(r_off), amplitude=1j if m == 1 else -1j)]
    sim = dipole_sim(m, src)
    n2f = sim.add_near2far(FREQ, 0, 1, *n2f_regions(SR_D, SZ_D))
    sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Er, mp.Vector3(r_off), 1e-6))
    e, h = farfields(sim, n2f); sim.reset_meep()
    ex += 0.5 * e; hx += 0.5 * h
on["x"] = (ex, hx)
pat_on = {k: radial_flux(*v) for k, v in on.items()}
an_on = {"x": np.cos(THETA) ** 2, "z": np.sin(THETA) ** 2}
err_on = {k: rel_l2(pat_on[k] / pat_on[k].max(), an_on[k]) for k in on}
say(f"A: on-axis z-dipole (m = 0) vs sin^2: rel L2 {err_on['z']:.4f}; x-dipole (m = +1 and -1) vs cos^2: {err_on['x']:.4f}; {time.time() - t_a:.0f} s")
if MASTER:
    source_figure(FREQ, 0.1 * FREQ, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ B. off-axis x-dipole: the m series
t_b = time.time()
R_SRC = 0.5
e_tot = np.zeros((NPTS, 3), complex); h_tot = np.zeros((NPTS, 3), complex)
m_flux, m_err, flux_max = [], [], 0.0
m = 0
while True:
    src = [mp.Source(gs(FREQ), component=mp.Er, center=mp.Vector3(R_SRC)),
           mp.Source(gs(-FREQ), component=mp.Er, center=mp.Vector3(R_SRC))]          # +f gives the +m term, -f the -m term (conjugated)
    sim = dipole_sim(m, src)
    n2p = sim.add_near2far(FREQ, 0, 1, *n2f_regions(SR_D, SZ_D))
    n2m = sim.add_near2far(-FREQ, 0, 1, *n2f_regions(SR_D, SZ_D))
    sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Er, mp.Vector3(R_SRC), 1e-6))
    ep, hp = farfields(sim, n2p); em, hm = farfields(sim, n2m); sim.reset_meep()
    e_tot += ep; h_tot += hp                                   # exp(i m phi) = 1 at phi = 0
    if m > 0:
        e_tot += np.conj(em); h_tot += np.conj(hm)
    fl = total_flux(radial_flux(ep, hp))
    flux_max = max(flux_max, fl)
    p = radial_flux(e_tot, h_tot)
    m_flux.append(fl); m_err.append(rel_l2(p / p.max(), np.cos(THETA) ** 2))
    say(f"B: m = {m}: power of this m / max = {fl / flux_max:.2e}; pattern error after summing 0..{m}: {m_err[-1]:.4f}")
    if m > 0 and fl / flux_max < POWER_DECAY:
        break
    m += 1
pat_off = radial_flux(e_tot, h_tot)
say(f"B: off-axis x-dipole at r = {R_SRC}: stopped at m = {m}; final rel L2 vs cos^2 {m_err[-1]:.4f}; {time.time() - t_b:.0f} s")

# ================================================================ C. post 12's ring in cylindrical coordinates
t_c = time.time()
N_RING, W, R_IN, PAD, DPML_R = 3.4, 1.0, 1.0, 4.0, 32.0
SR_R = R_IN + W + PAD + DPML_R
RES_R = 20
FC, DFC = 0.15, 0.1
POST12 = {3: (0.11818, 79), 4: (0.14736, 342), 5: (0.17564, 2132)}     # 2D Cartesian, res 20 (post 12)
ring = {}


def ring_sim(m, f, df):
    return mp.Simulation(cell_size=mp.Vector3(SR_R, 0, 0), resolution=RES_R, dimensions=mp.CYLINDRICAL, m=m, boundary_layers=[mp.PML(DPML_R)],
                         geometry=[mp.Block(center=mp.Vector3(R_IN + 0.5 * W), size=mp.Vector3(W, mp.inf, mp.inf), material=mp.Medium(index=N_RING))],
                         sources=[mp.Source(mp.GaussianSource(f, fwidth=df), component=mp.Ez, center=mp.Vector3(R_IN + 0.1))])


for mm in (3, 4, 5):
    sim = ring_sim(mm, FC, DFC)
    hv = mp.Harminv(mp.Ez, mp.Vector3(R_IN + 0.1), FC, DFC)
    sim.run(mp.after_sources(hv), until_after_sources=200)
    modes = [md for md in hv.modes if md.Q > 0 and FC - 0.5 * DFC < md.freq < FC + 0.5 * DFC]
    md = max(modes, key=lambda x: abs(x.amp)); sim.reset_meep()
    f, Q = float(md.freq), float(md.Q)
    sim = ring_sim(mm, f, 0.01)
    dft = sim.add_dft_fields([mp.Ez], f, 0, 1, center=mp.Vector3(0.5 * (R_IN + W + PAD)), size=mp.Vector3(R_IN + W + PAD))
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(R_IN + 0.1), 1e-6))
    ezr = np.squeeze(sim.get_dft_array(dft, mp.Ez, 0)); sim.reset_meep()
    ring[mm] = {"f": f, "Q": Q, "ez_r": ezr}
    say(f"C: m = {mm}: cylindrical f {f:.5f} Q {Q:.0f} | post 12 (2D, res 20): f {POST12[mm][0]:.5f} Q {POST12[mm][1]} -> df/f {(f - POST12[mm][0]) / POST12[mm][0]:+.2e}")
say(f"C done in {time.time() - t_c:.0f} s")

# ================================================================ D. disc on a ground plane, near vs far flux
t_d = time.time()
RES_DISC, PML_DISC, AIR = 100, 0.5, 1.0
DISC_R, N_DISC = 1.2, 2.4
DISC_T = 0.7 * WL / N_DISC
NPOL = 100
THETA_D = np.linspace(0, 0.5 * np.pi, NPOL)
disc = {}
for cell_r in (6.0, 8.0):
    sr = cell_r + PML_DISC; sz = DISC_T + AIR + PML_DISC
    src_pt = mp.Vector3(0.5 * DISC_R, 0, -0.5 * sz + 0.5 * DISC_T)
    sim = mp.Simulation(resolution=RES_DISC, cell_size=mp.Vector3(sr, 0, sz), dimensions=mp.CYLINDRICAL, m=-1,
                        boundary_layers=[mp.PML(PML_DISC, direction=mp.R), mp.PML(PML_DISC, direction=mp.Z, side=mp.High)],   # no PML at the bottom: PEC ground plane
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.1 * FREQ), component=mp.Er, center=src_pt)],
                        geometry=[mp.Block(material=mp.Medium(index=N_DISC), center=mp.Vector3(0.5 * DISC_R, 0, -0.5 * sz + 0.5 * DISC_T), size=mp.Vector3(DISC_R, mp.inf, DISC_T))])
    regs = [mp.FluxRegion(center=mp.Vector3(0.5 * cell_r, 0, 0.5 * sz - PML_DISC), size=mp.Vector3(cell_r, 0, 0)),
            mp.FluxRegion(center=mp.Vector3(cell_r, 0, 0.5 * sz - PML_DISC - 0.5 * (AIR + DISC_T)), size=mp.Vector3(0, 0, AIR + DISC_T))]
    flux = sim.add_flux(FREQ, 0, 1, *regs)
    n2f = sim.add_near2far(FREQ, 0, 1, *regs)
    dft = None
    if cell_r == 6.0:
        dft = sim.add_dft_fields([mp.Er], FREQ, 0, 1, center=mp.Vector3(0.5 * cell_r, 0, -0.5 * PML_DISC), size=mp.Vector3(cell_r, 0, sz - PML_DISC))
        annotated_layout(sim, os.path.join(OUT, "01_layout.png"), dpml=PML_DISC, figsize=(11, 3.8), axis_step=1.0, unit="um",
                         title="part D: disc (n = 2.4, R = 1.2 um) on a ground plane, cylindrical (r, z); bottom edge = PEC (no PML)",
                         params_text=f"wl={WL} um, res={RES_DISC}\nm = -1, t = {DISC_T:.3f} um", params_xy=(3.4, 0.33), pml_xy=(6.05, -0.6),
                         decay_point=(src_pt.x, src_pt.z), decay_text_xy=(1.5, -0.45),
                         labels=[Label("disc", (0.9, src_pt.z + 0.05), (1.5, -0.2), step=2, color="black"),
                                 Label("Er ring source at r = 0.6", (src_pt.x, src_pt.z), (1.5, 0.05), step=3, color="red"),
                                 Label("flux + near2far: top and outer r (open at the bottom)", (5.0, 0.5 * sz - PML_DISC), (3.4, -0.2), step=5, color="blue")])
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Er, src_pt, 1e-8))
    f_near = float(mp.get_fluxes(flux)[0])
    e, h = farfields(sim, n2f, tol=1e-8, theta=THETA_D)
    pat = radial_flux(e, h)
    f_far = total_flux(pat, theta=THETA_D)
    er = orient_rz(sim.get_dft_array(dft, mp.Er, 0), int(round(cell_r * RES_DISC))) if dft is not None else None
    sim.reset_meep()
    disc[cell_r] = {"near": f_near, "far": f_far, "gap": abs(f_near - f_far) / f_near, "pattern": pat, "er": er, "sz": sz}
    say(f"D: cell r {cell_r}: near flux {f_near:.4f}, far flux {f_far:.4f}, gap {100 * disc[cell_r]['gap']:.2f} %")
say(f"D done in {time.time() - t_d:.0f} s")

# ================================================================ figures (master only)
if MASTER:
    # A
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.6), subplot_kw={"projection": "polar"})
    for a, k, lab in ((ax[0], "z", "z-dipole: m = 0 (Ez)  vs sin^2"), (ax[1], "x", "x-dipole: m = +1 and m = -1  vs cos^2")):
        a.plot(THETA, pat_on[k] / pat_on[k].max(), "b-", lw=1.6, label="Meep (cylindrical)")
        a.plot(THETA, an_on[k], "r--", lw=1.2, label="analytic")
        a.set_theta_zero_location("N"); a.set_theta_direction(-1); a.set_thetamin(0); a.set_thetamax(90); a.set_rmax(1.05)
        a.set_title(f"{lab}\nrel L2 {err_on[k]:.4f}", fontsize=9); a.legend(fontsize=7, loc="lower left")
    fig.suptitle("part A: on-axis dipoles (angle from +z, phi = 0 plane). A linearly polarized in-plane dipole is two m runs", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_on_axis.png"), dpi=150); plt.close(fig)
    # B
    fig = plt.figure(figsize=(13, 4.4))
    ax = fig.add_subplot(1, 3, 1)
    ms = np.arange(len(m_flux))
    ax.semilogy(ms, np.array(m_flux) / max(m_flux), "o-", color="tab:blue"); ax.axhline(POWER_DECAY, color="crimson", ls="--", lw=1, label="stop: 1e-4 of the max")
    ax.set_xlabel("azimuthal order m"); ax.set_ylabel("far-field power of the m term / max"); ax.set_title(f"dipole at r = {R_SRC} um: how much each m radiates", fontsize=9); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=8)
    ax = fig.add_subplot(1, 3, 2)
    ax.semilogy(ms, m_err, "s-", color="tab:green"); ax.set_xlabel("m included up to"); ax.set_ylabel("rel L2 of the summed pattern vs cos^2"); ax.set_title("the pattern converges as m terms are added", fontsize=9); ax.grid(alpha=0.3, which="both")
    ax = fig.add_subplot(1, 3, 3, projection="polar")
    ax.plot(THETA, pat_off / pat_off.max(), "b-", lw=1.6, label=f"Meep, m = 0..{m}"); ax.plot(THETA, np.cos(THETA) ** 2, "r--", lw=1.2, label="cos^2")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.set_rmax(1.05); ax.legend(fontsize=7, loc="lower left")
    ax.set_title(f"off-axis x-dipole: rel L2 {m_err[-1]:.4f}", fontsize=9)
    fig.suptitle("part B: a point away from the axis is a Fourier series over m; each m is one 2D (r, z) run", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_off_axis.png"), dpi=150); plt.close(fig)
    # C: Ez(r) and the x-y reconstruction for m = 3, 4, 5
    rr = np.linspace(0, R_IN + W + PAD, len(ring[3]["ez_r"]))
    L = R_IN + W + 1.5
    xg = np.linspace(-L, L, 301); X, Y = np.meshgrid(xg, xg, indexing="ij"); RG = np.hypot(X, Y); PH = np.arctan2(Y, X)
    fig, ax = plt.subplots(2, 3, figsize=(12.5, 7.8), gridspec_kw={"height_ratios": [1, 1.5]})
    for k, mm in enumerate((3, 4, 5)):
        d = ring[mm]; ez = d["ez_r"] / np.max(np.abs(d["ez_r"]))
        ax[0, k].plot(rr, np.real(ez), "b-", label="Re"); ax[0, k].plot(rr, np.abs(ez), "k-", lw=0.8, label="|Ez|")
        ax[0, k].axvspan(R_IN, R_IN + W, color="gray", alpha=0.25); ax[0, k].set_xlabel("r [a]"); ax[0, k].set_title(f"m = {mm}: f = {d['f']:.4f}, Q = {d['Q']:.0f} (one 1D radial run)", fontsize=9)
        ax[0, k].grid(alpha=0.3); ax[0, k].legend(fontsize=7)
        field = np.real(np.interp(RG, rr, np.real(ez)) * np.cos(mm * PH) - np.interp(RG, rr, np.imag(ez)) * np.sin(mm * PH))
        field[RG > rr[-1]] = 0
        lim = np.max(np.abs(field))
        ax[1, k].imshow(field.T, extent=[-L, L, -L, L], origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
        for rc in (R_IN, R_IN + W):
            ax[1, k].add_patch(plt.Circle((0, 0), rc, fill=False, color="k", lw=0.8))
        ax[1, k].set_title(f"Re[Ez(r) exp(i {mm} phi)]: {2 * mm} sign lobes; post 12: f {POST12[mm][0]:.4f}", fontsize=9); ax[1, k].set_xlabel("x [a]")
    ax[1, 0].set_ylabel("y [a]")
    fig.suptitle("part C: post 12's ring as one radial run per m; the 2D picture is rebuilt from exp(i m phi)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_ring_cyl.png"), dpi=150); plt.close(fig)
    # D
    fig = plt.figure(figsize=(13.5, 4.4))
    ax = fig.add_subplot(1, 3, 1, projection="polar")
    for cr, c in ((6.0, "tab:blue"), (8.0, "tab:orange")):
        p = disc[cr]["pattern"]; ax.plot(THETA_D, p / disc[6.0]["pattern"].max(), "-", color=c, lw=1.4, label=f"cell r {cr:.0f} um")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.legend(fontsize=7, loc="lower left")
    ax.set_title("disc on a ground plane: far-field pattern", fontsize=9)
    ax = fig.add_subplot(1, 3, 2)
    idx = np.arange(2)
    ax.bar(idx - 0.2, [disc[c]["near"] for c in (6.0, 8.0)], width=0.4, color="tab:gray", label="near flux (monitor)")
    ax.bar(idx + 0.2, [disc[c]["far"] for c in (6.0, 8.0)], width=0.4, color="tab:blue", label="far flux (hemisphere integral)")
    for k, c in enumerate((6.0, 8.0)):
        ax.text(k, max(disc[c]["near"], disc[c]["far"]) * 1.02, f"gap {100 * disc[c]['gap']:.2f} %", ha="center", fontsize=8)
    ax.set_xticks(idx); ax.set_xticklabels(["cell r 6 um", "cell r 8 um"]); ax.set_ylabel("power (a.u.)"); ax.set_title("the open near2far surface misses currents on the ground plane", fontsize=9); ax.legend(fontsize=7, loc="lower right")
    ax = fig.add_subplot(1, 3, 3)
    er = disc[6.0]["er"]; sz = disc[6.0]["sz"]
    ax.imshow(np.log10(np.abs(er) + 1e-12).T, extent=[0, 6.0, -0.5 * sz, 0.5 * sz - PML_DISC], origin="lower", cmap="inferno", aspect="auto")
    ax.add_patch(plt.Rectangle((0, -0.5 * sz), DISC_R, DISC_T, fill=False, color="w", lw=1))
    ax.set_xlabel("r [um]"); ax.set_ylabel("z [um]"); ax.set_title("log10 |Er| at 1 um (r, z plane)", fontsize=9)
    fig.suptitle("part D: near vs far flux; the gap shrinks when the radial cell grows", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "06_disc.png"), dpi=150); plt.close(fig)
    # GIF: m = 3 mode rotating: Re[Ez(r) exp(i (3 phi - w t))]
    d = ring[3]; ez = d["ez_r"] / np.max(np.abs(d["ez_r"]))
    Er_ = np.interp(RG, rr, np.real(ez)); Ei_ = np.interp(RG, rr, np.imag(ez)); amp = np.where(RG > rr[-1], 0, 1)
    fig_g, ax_g = plt.subplots(figsize=(4.8, 4.4))
    im = ax_g.imshow(np.zeros_like(RG).T, extent=[-L, L, -L, L], origin="lower", cmap="RdBu", vmin=-1, vmax=1, aspect="equal")
    for rc in (R_IN, R_IN + W):
        ax_g.add_patch(plt.Circle((0, 0), rc, fill=False, color="k", lw=0.8))
    ax_g.set_xlabel("x [a]"); ax_g.set_ylabel("y [a]"); ttl = ax_g.set_title("", fontsize=9); fig_g.tight_layout()
    NF = 36

    def upd(i):
        wt = 2 * np.pi * i / NF
        fld = amp * (Er_ * np.cos(3 * PH - wt) - Ei_ * np.sin(3 * PH - wt))
        im.set_data((fld / np.max(np.abs(fld))).T); ttl.set_text(f"m = 3 mode, Re[Ez(r) exp(i(3 phi - wt))], wt = {np.degrees(wt):.0f} deg")
        return im, ttl

    animation.FuncAnimation(fig_g, upd, frames=NF, blit=False).save(os.path.join(OUT, "07_anim_m3.gif"), writer=animation.PillowWriter(fps=12), dpi=75)
    plt.close(fig_g)
    with open(os.path.join(OUT, "result.json"), "w") as f_:
        json.dump({"A": {"err_z": err_on["z"], "err_x": err_on["x"]},
                   "B": {"r_src": R_SRC, "m_last": m, "m_flux_rel": (np.array(m_flux) / max(m_flux)).tolist(), "m_err": m_err},
                   "C": {str(k): {"f": v["f"], "Q": v["Q"], "post12_f": POST12[k][0], "post12_Q": POST12[k][1]} for k, v in ring.items()},
                   "D": {str(k): {"near": v["near"], "far": v["far"], "gap": v["gap"]} for k, v in disc.items()},
                   "wall_s_total": time.time() - t_all, "np": mp.count_processors(), "meep": mp.__version__}, f_, indent=2)
say(f"total {time.time() - t_all:.0f} s on {mp.count_processors()} process(es)")
