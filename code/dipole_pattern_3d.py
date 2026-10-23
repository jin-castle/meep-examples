"""Meep Example 10 - 3D radiation pattern of a point dipole: a family of 1D Bloch runs, and a PEC mirror.

Post 01 showed a 2D point source radiating equally in all directions. This post asks the 3D question in two ways.
  A. Vacuum Ex dipole, 3D pattern WITHOUT a 3D cell: one 1D simulation per direction (theta, phi), each with a
     transverse Bloch wavevector k = f (sin t cos p, sin t sin p, 0). The z flux of each run, times cos(theta),
     is one angular sample of the 3D pattern. Compared with the analytic dipole pattern 1 - sin^2(t) cos^2(p).
  B. A dipole 1.25 um above a perfect-electric-conductor (PEC) mirror, 2D (Ez): the mirror is replaced by an
     opposite-sign image dipole plus an odd mirror symmetry, and the far field comes from a closed near2far box.
     Compared with the two-element array factor sin^2(k h cos t).
  C. The same mirror problem with the 1D Bloch method of part A (3D Ex dipole, PEC = metallic cell boundary):
     the two methods agree on the pattern away from grazing angles; near grazing the 1D method breaks down.

Run:  python dipole_pattern_3d.py     (~3 min on one core)
Out:  00_source.png, 01_layout.png, 02_layout_1d.png, 03_vacuum_pattern.png, 04_pec_field.png, 05_pec_pattern.png,
      06_anim_pec.gif, 07_anim_1d.gif, result.json   (-> ../assets/10/)
"""
import json
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
from blogfig import Label, _badge, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "10")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()


def rel_l2(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.linalg.norm(a - b) / np.linalg.norm(b))


# =================================================================== A. vacuum dipole via 1D Bloch runs
# ---------------------------------------------------------------- (1) parameters (official dipole_in_vacuum_1D.py, smaller grid)
WL_A = 1.0                               # wavelength [um]; the pattern is scale-free
FCEN_A = 1 / WL_A
FWIDTH_A = 0.1 * FCEN_A
RES_A = 50
DPML_A, DAIR_A = 1.0, 10.0
SZ_A = DPML_A + DAIR_A + DPML_A
Z_SRC_A = -0.5 * DAIR_A                  # dipole at the bottom of the air gap (official)
Z_MON_A = 0.5 * DAIR_A                   # flux point at the top of the air gap
GLANCING = 0.95                          # skip k_perp > 0.95 f: PML cannot absorb nearly-parallel waves (official rule)
POLAR = np.radians(np.arange(0.0, 90.1, 7.5))      # 13 polar angles (0 = +z)
AZIM = np.radians(np.arange(0.0, 360.0, 15.0))     # 24 azimuth angles


def bloch_k(theta, phi, fcen, n_index=1.0):
    """Full wavevector of the outgoing plane wave, |k| = n f. The z component keeps k != 0 at theta = 0,
    so every run uses complex fields (a k = 0 run would switch to real fields and change the power scale by 4)."""
    return mp.Vector3(n_index * fcen * np.sin(theta) * np.cos(phi), n_index * fcen * np.sin(theta) * np.sin(phi), n_index * fcen * np.cos(theta))


def flux_1d(theta, phi, *, fcen, fwidth, n_index=1.0, sz=SZ_A, z_src=Z_SRC_A, z_mon=Z_MON_A, pml=None, geometry=(), component=mp.Ex, until=None):
    """One 1D run: Bloch k from (theta, phi), source at z_src, Poynting z-flux at z_mon.
    NOTE: do not pass dimensions=1. The cell size (0, 0, sz) already makes the run 1D, and an explicit dimensions=1
    silently drops the transverse k (the flux then no longer depends on the angle)."""
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, sz), resolution=RES_A, k_point=bloch_k(theta, phi, fcen, n_index),
                        default_material=mp.Medium(index=n_index), geometry=list(geometry),
                        boundary_layers=pml if pml is not None else [mp.PML(thickness=DPML_A, direction=mp.Z)],
                        sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=component, center=mp.Vector3(0, 0, z_src), size=mp.Vector3())])
    mon = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(0, 0, z_mon), size=mp.Vector3(), direction=mp.Z))
    sim.run(until_after_sources=until if until is not None else mp.stop_when_fields_decayed(25, component, mp.Vector3(0, 0, z_mon), 1e-6))
    f = float(mp.get_fluxes(mon)[0]); sim.reset_meep()
    return f


t_a = time.time()
flux_z = np.full((len(POLAR), len(AZIM)), np.nan)
for i, th in enumerate(POLAR):
    if np.sin(th) > GLANCING:
        continue
    for j, ph in enumerate(AZIM):
        flux_z[i, j] = flux_1d(th, ph, fcen=FCEN_A, fwidth=FWIDTH_A)
n_runs = int(np.sum(~np.isnan(flux_z)))
computed = ~np.isnan(flux_z)
cos_t = np.cos(POLAR)[:, None]
radial = flux_z * cos_t                                   # official: radial flux = (kz / f) * flux_z
TH, PH = np.meshgrid(POLAR, AZIM, indexing="ij")
analytic_A = 1 - np.sin(TH) ** 2 * np.cos(PH) ** 2        # |E|^2 of an x-polarized dipole, up to a constant


def norm(p, mask):
    return p / np.nanmax(np.where(mask, p, np.nan))


err_mul = rel_l2(norm(radial, computed)[computed], norm(analytic_A, computed)[computed])
err_div = rel_l2(norm(flux_z / cos_t, computed)[computed], norm(analytic_A, computed)[computed])
err_raw = rel_l2(norm(flux_z, computed)[computed], norm(analytic_A, computed)[computed])
j0 = 0; j90 = int(np.argmin(np.abs(AZIM - np.pi / 2)))
err_phi0 = rel_l2(norm(radial, computed)[computed[:, j0], j0], norm(analytic_A, computed)[computed[:, j0], j0])
print(f"A: {n_runs} 1D runs ({len(POLAR)}x{len(AZIM)} grid, {int(np.sum(~computed))} glancing samples skipped) in {time.time() - t_a:.0f} s; "
      f"rel L2 vs analytic (computed samples): flux_z*cos = {err_mul:.4f}, flux_z/cos = {err_div:.4f}, flux_z raw = {err_raw:.4f}; phi=0 cut {err_phi0:.4f}")

# schematic of the 1D cell (plot2D has nothing to draw in 1D)
fig, ax = plt.subplots(figsize=(8.6, 3.2))
ax.axhspan(-0.5, 0.5, xmin=0, xmax=DPML_A / SZ_A, color="green", alpha=0.25); ax.axhspan(-0.5, 0.5, xmin=1 - DPML_A / SZ_A, xmax=1, color="green", alpha=0.25)
ax.plot([Z_SRC_A, Z_SRC_A], [-0.4, 0.4], color="red", lw=3); ax.plot(Z_MON_A, 0, "s", color="blue", ms=9)
th_demo = np.radians(45)
ax.annotate("", xy=(Z_SRC_A + 2.2 * np.cos(th_demo), 0.45 * np.sin(th_demo)), xytext=(Z_SRC_A, 0), arrowprops=dict(arrowstyle="->", color="purple", lw=1.8))
ax.text(Z_SRC_A + 1.4, 0.36, "k = f (sin t cos p, sin t sin p, cos t)\nonly the z axis is simulated", color="purple", fontsize=8)
for xy, step, color, txt, txy in (((-0.5 * SZ_A + 0.3, 0.42), 1, "dimgray", f"wl={WL_A} um, res={RES_A}\n{len(POLAR)} polar x {len(AZIM)} azimuth runs", (-0.5 * SZ_A + 0.6, 0.30)),
                                   ((Z_SRC_A, -0.42), 3, "red", "Ex dipole (GaussianSource)", (Z_SRC_A + 0.25, -0.46)),
                                   ((-0.5 * SZ_A + 0.5 * DPML_A, 0), 4, "green", "PML (both ends)", (-0.5 * SZ_A + 0.1, -0.15)),
                                   ((Z_MON_A, 0.12), 5, "blue", "flux point: Poynting z-flux", (Z_MON_A - 2.6, 0.18)),
                                   ((Z_MON_A, -0.12), 6, "purple", "decay watch point", (Z_MON_A - 1.9, -0.3))):
    _badge(ax, xy, step, color); ax.text(*txy, txt, fontsize=8, color=color)
ax.set_xlim(-0.5 * SZ_A, 0.5 * SZ_A); ax.set_ylim(-0.5, 0.5); ax.set_yticks([]); ax.set_xlabel("z [um]")
ax.set_title("part A: one 1D cell per direction; the transverse Bloch wavevector k_point picks the direction (theta, phi)", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_layout_1d.png"), dpi=150); plt.close(fig)

# pattern figure: two polar cuts + hemisphere maps
fig = plt.figure(figsize=(13, 7.6))
gs = fig.add_gridspec(2, 3)
for col, (j, lab, an) in enumerate(((j0, "phi = 0 (plane of the dipole axis): cos^2(theta)", np.cos(POLAR) ** 2),
                                    (j90, "phi = 90 deg (plane normal to the dipole): isotropic", np.ones_like(POLAR)))):
    ax = fig.add_subplot(gs[0, col], projection="polar")
    m = computed[:, j]
    ax.plot(POLAR[m], norm(radial, computed)[m, j], "o", color="tab:blue", ms=4, label="Meep: flux_z cos(theta)")
    ax.plot(POLAR, an, "-", color="k", lw=1.2, label="analytic")
    ax.plot(POLAR[m], norm(flux_z / cos_t, computed)[m, j], "x", color="tab:red", ms=4, alpha=0.6, label="flux_z / cos(theta) (wrong)")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.set_rlim(0, 1.6)
    ax.set_title(lab, fontsize=9); ax.legend(fontsize=7, loc="lower left")
ax = fig.add_subplot(gs[0, 2])
ax.bar(["flux_z cos", "flux_z raw", "flux_z / cos"], [err_mul, err_raw, err_div], color=["tab:green", "tab:gray", "tab:red"])
for k_, v in enumerate([err_mul, err_raw, err_div]):
    ax.text(k_, v + 0.01, f"{v:.3f}", ha="center", fontsize=8)
ax.set_ylabel("relative L2 vs analytic (computed samples)"); ax.set_title("which conversion of the z flux is the radial flux?", fontsize=9); ax.grid(axis="y", alpha=0.3)
Td, Pd = np.degrees(POLAR), np.degrees(AZIM)
for col, (data, ttl, cmap, vmax) in enumerate(((norm(radial, computed), "Meep: normalized radial flux", "viridis", 1.0),
                                                (norm(analytic_A, computed), "analytic 1 - sin^2(t) cos^2(p)", "viridis", 1.0),
                                                (np.abs(norm(radial, computed) - norm(analytic_A, computed)), "|Meep - analytic|", "magma", None))):
    ax = fig.add_subplot(gs[1, col])
    pc = ax.pcolormesh(Pd, Td, np.where(computed, data, np.nan), cmap=cmap, vmin=0, vmax=vmax, shading="nearest")
    ax.axhspan(np.degrees(np.arcsin(GLANCING)), 90, color="lightgray", alpha=0.6); ax.text(5, 80, "not computed (glancing)", fontsize=7)
    ax.set_xlabel("azimuth phi [deg]"); ax.set_ylabel("polar theta [deg]"); ax.set_title(ttl, fontsize=9); fig.colorbar(pc, ax=ax, shrink=0.85)
fig.suptitle(f"3D pattern of an x-dipole from {n_runs} 1D runs: rel L2 {err_mul:.3f} on the computed hemisphere", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_vacuum_pattern.png"), dpi=150); plt.close(fig)

# GIF of one oblique 1D run (theta = 45 deg): Re(Ex) along z vs time
th_g = np.radians(45)
sim_g = mp.Simulation(cell_size=mp.Vector3(0, 0, SZ_A), resolution=RES_A, k_point=bloch_k(th_g, 0.0, FCEN_A),
                      boundary_layers=[mp.PML(thickness=DPML_A, direction=mp.Z)],
                      sources=[mp.Source(mp.GaussianSource(FCEN_A, fwidth=0.4 * FCEN_A), component=mp.Ex, center=mp.Vector3(0, 0, Z_SRC_A), size=mp.Vector3())])
sim_g.init_sim()
t0g = 5 / (0.4 * FCEN_A)
frames_g, times_g = [], []
sim_g.run(until=t0g - 2 / (0.4 * FCEN_A))
for i in range(50):
    sim_g.run(until=0.3)
    frames_g.append(np.real(sim_g.get_array(center=mp.Vector3(), size=mp.Vector3(0, 0, SZ_A), component=mp.Ex)))
    times_g.append(sim_g.meep_time())
zs = np.linspace(-0.5 * SZ_A, 0.5 * SZ_A, len(frames_g[0]))
lim_g = max(np.max(np.abs(f)) for f in frames_g)
fig_g, ax_g = plt.subplots(figsize=(7.6, 2.9))
ln, = ax_g.plot(zs, frames_g[0], color="tab:blue"); ax_g.set_ylim(-lim_g, lim_g); ax_g.set_xlim(zs[0], zs[-1])
ax_g.axvspan(zs[0], zs[0] + DPML_A, color="green", alpha=0.2); ax_g.axvspan(zs[-1] - DPML_A, zs[-1], color="green", alpha=0.2)
ax_g.axvline(Z_SRC_A, color="red", lw=1.5, label="source"); ax_g.axvline(Z_MON_A, color="blue", lw=1.5, ls="--", label="flux point")
ax_g.set_xlabel("z [um]"); ax_g.set_ylabel("Re(Ex)"); ax_g.legend(fontsize=7, loc="upper right"); ttl_g = ax_g.set_title("", fontsize=9)
fig_g.tight_layout()


def _upd(i):
    ln.set_ydata(frames_g[i]); ttl_g.set_text(f"one 1D run (theta = 45 deg): the pulse moves along z at c cos(theta)   t = {times_g[i]:.1f} um/c")
    return ln, ttl_g


animation.FuncAnimation(fig_g, _upd, frames=len(frames_g), blit=False).save(os.path.join(OUT, "07_anim_1d.gif"), writer=animation.PillowWriter(fps=10), dpi=80)
plt.close(fig_g); sim_g.reset_meep()

# =================================================================== B. dipole above a PEC mirror, 2D near2far with an image dipole
# ---------------------------------------------------------------- (1) parameters (official antenna_pec_ground_plane.py)
WL_B = 0.65
FCEN_B = 1 / WL_B
FWIDTH_B = 0.2 * FCEN_B
N_B = 1.2
H = 1.25                                 # dipole height above the mirror
RES_B = 100
DPML_B, DBULK = 0.5, 6.0
S_B = DBULK + 2 * DPML_B                 # 7 x 7 cell
R_FF = 1000 * WL_B
NANG = 50
THETA_B = np.linspace(0, 0.5 * np.pi, NANG)          # angle from the mirror normal (+y)
K_B = 2 * np.pi * N_B / WL_B
array_factor = np.sin(K_B * H * np.cos(THETA_B)) ** 2
array_factor /= array_factor.max()

sources_B = [mp.Source(mp.GaussianSource(FCEN_B, fwidth=FWIDTH_B), component=mp.Ez, center=mp.Vector3(0, H)),
             mp.Source(mp.GaussianSource(FCEN_B, fwidth=FWIDTH_B), component=mp.Ez, center=mp.Vector3(0, -H), amplitude=-1.0)]   # image dipole
symB = [mp.Mirror(mp.X), mp.Mirror(mp.Y, phase=-1)]                                                                        # odd in y -> Ez = 0 on y = 0 (PEC)
common_B = dict(cell_size=mp.Vector3(S_B, S_B), resolution=RES_B, boundary_layers=[mp.PML(DPML_B)], default_material=mp.Medium(index=N_B))
sim_B = mp.Simulation(sources=sources_B, symmetries=symB, **common_B)
BOX = 2.0                                                                                                                  # half-size of the near2far box (encloses both dipoles)
n2f = sim_B.add_near2far(FCEN_B, 0, 1,
                        mp.Near2FarRegion(center=mp.Vector3(0, BOX), size=mp.Vector3(2 * BOX, 0)),
                        mp.Near2FarRegion(center=mp.Vector3(0, -BOX), size=mp.Vector3(2 * BOX, 0), weight=-1),
                        mp.Near2FarRegion(center=mp.Vector3(BOX, 0), size=mp.Vector3(0, 2 * BOX)),
                        mp.Near2FarRegion(center=mp.Vector3(-BOX, 0), size=mp.Vector3(0, 2 * BOX), weight=-1))
dft_B = sim_B.add_dft_fields([mp.Ez], FCEN_B, 0, 1, center=mp.Vector3(), size=mp.Vector3(DBULK, DBULK))
annotated_layout(
    sim_B, os.path.join(OUT, "01_layout.png"), dpml=DPML_B, figsize=(6.6, 6.2), axis_step=1.0,
    title="part B: dipole above a PEC mirror = dipole + opposite image, odd mirror symmetry in y",
    params_text=f"wl={WL_B} um, n={N_B}\nh={H} um, res={RES_B}\nk h = {K_B * H:.1f}",
    params_xy=(-3.4, 3.1), pml_xy=(-3.0, -3.25), decay_point=None,
    labels=[Label("physical Ez dipole at y = +h", (0.05, H), (0.6, 2.4), step=3, color="red"),
            Label("image dipole at y = -h, amplitude -1", (0.05, -H), (0.6, -2.4), step=3, color="red"),
            Label("y = 0: Ez = 0 here (effective PEC)", (-1.2, 0.0), (-3.4, -0.9), step=2, color="black"),
            Label("closed near2far box (4 segments)", (BOX, 1.0), (0.4, 1.4), step=5, color="blue")])
source_figure(FCEN_B, FWIDTH_B, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")
t_b = time.time()
sim_B.run(until_after_sources=mp.stop_when_dft_decayed(tol=1e-6))
ez_B = sim_B.get_dft_array(dft_B, mp.Ez, 0)
pattern_B = np.zeros(NANG)
for i, th in enumerate(THETA_B):
    ff = sim_B.get_farfield(n2f, mp.Vector3(R_FF * np.sin(th), R_FF * np.cos(th)))
    E = np.array(ff[:3]); Hf = np.array(ff[3:])
    S = np.real(np.cross(E, np.conj(Hf)))
    pattern_B[i] = np.hypot(S[0], S[1])
sim_B.reset_meep()
pattern_B /= pattern_B.max()
err_B = rel_l2(pattern_B, array_factor)
peak_B, peak_an = int(np.argmax(pattern_B)), int(np.argmax(array_factor))
node = float(np.max(np.abs(ez_B[:, ez_B.shape[1] // 2])) / np.max(np.abs(ez_B)))
print(f"B: 2D near2far pattern vs sin^2(k h cos theta): rel L2 {err_B:.4f}, peak bin Meep {peak_B} vs analytic {peak_an} "
      f"({np.degrees(THETA_B[peak_B]):.1f} deg), |Ez| on the y = 0 line / max = {node:.1e}; {time.time() - t_b:.0f} s")

ext_B = [-0.5 * DBULK, 0.5 * DBULK, -0.5 * DBULK, 0.5 * DBULK]
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.6))
lim = float(np.max(np.abs(ez_B)))
ax[0].imshow(np.real(ez_B).T, extent=ext_B, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal"); ax[0].set_title("Re(Ez) at the center frequency", fontsize=9)
ax[1].imshow(np.abs(ez_B).T, extent=ext_B, origin="lower", cmap="inferno", aspect="equal"); ax[1].set_title("|Ez|: the y = 0 line is a node (the mirror)", fontsize=9)
for a in ax:
    a.axhline(0, color="w", ls="--", lw=1.0); a.plot([0, 0], [H, -H], "o", color="lime", ms=4)
    a.add_patch(plt.Rectangle((-BOX, -BOX), 2 * BOX, 2 * BOX, fill=False, color="cyan", lw=1.0, ls=":")); a.set_xlabel("x [um]")
ax[0].set_ylabel("y [um]")
fig.suptitle("part B: steady-state field of dipole + image. Only the upper half (y > 0) is physical.", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_pec_field.png"), dpi=150); plt.close(fig)

# GIF: monitor-free run with a short pulse, both dipoles visible, node line marked
sim_gB = mp.Simulation(sources=[mp.Source(mp.GaussianSource(FCEN_B, fwidth=0.5 * FCEN_B), component=mp.Ez, center=mp.Vector3(0, H)),
                                mp.Source(mp.GaussianSource(FCEN_B, fwidth=0.5 * FCEN_B), component=mp.Ez, center=mp.Vector3(0, -H), amplitude=-1.0)],
                       symmetries=symB, **dict(common_B, resolution=50))
sim_gB.init_sim()
vol_gB = mp.Volume(center=mp.Vector3(), size=mp.Vector3(DBULK, DBULK))
t0B = 5 / (0.5 * FCEN_B)
frames_B, times_B = record_frames(sim_gB, vol_gB, mp.Ez, t_start=t0B - 2 / (0.5 * FCEN_B), t_end=t0B + 1.1 * 0.5 * DBULK * N_B * 1.5, n_frames=60)
animate_fields(frames_B, times_B, ext_B, os.path.join(OUT, "06_anim_pec.gif"), figsize=(5.6, 5.0), dpi=70,
               lines=[((-0.5 * DBULK, 0), (0.5 * DBULK, 0), "k", "mirror plane y = 0 (Ez node)"), ((-BOX, BOX), (BOX, BOX), "blue", "near2far box (top)")],
               points=[(0, H, "red", "dipole"), (0, -H, "orange", "image dipole (-1)")], title="dipole + image", legend_loc="lower right")
sim_gB.reset_meep()

# =================================================================== C. the mirror problem with the 1D Bloch method (3D Ex dipole above PEC)
# A k_point makes EVERY cell boundary Bloch-periodic, so the mirror cannot be the cell wall: it is a block of mp.metal
# (perfect electric conductor) at the bottom of the 1D cell. PML only at the top; background n = 1.2.
DMETAL = 0.5
SZ_C = DMETAL + H + DAIR_A + DPML_A
Z_BOT = -0.5 * SZ_C
Z_PEC = Z_BOT + DMETAL                               # mirror surface
Z_SRC_C = Z_PEC + H
Z_MON_C = Z_PEC + H + DAIR_A
mirror = [mp.Block(center=mp.Vector3(0, 0, Z_BOT + 0.5 * DMETAL), size=mp.Vector3(mp.inf, mp.inf, DMETAL), material=mp.metal)]
POLAR_C = np.radians(np.arange(0.0, 90.0, 5.0))      # includes grazing angles on purpose
T_C = 150.0                                          # fixed duration: at 85 deg the wave needs ~140 time units to cross 10 um of n = 1.2
flux_C = {}
for phi_deg in (90.0, 0.0):
    vals = [flux_1d(th, np.radians(phi_deg), fcen=FCEN_B, fwidth=0.1 * FCEN_B, n_index=N_B, sz=SZ_C, z_src=Z_SRC_C, z_mon=Z_MON_C,
                    pml=[mp.PML(thickness=DPML_A, direction=mp.Z, side=mp.High)], geometry=mirror, until=T_C) for th in POLAR_C]
    flux_C[phi_deg] = np.array(vals) * np.cos(POLAR_C)
af_C = np.sin(K_B * H * np.cos(POLAR_C)) ** 2
an_C = {90.0: af_C, 0.0: af_C * np.cos(POLAR_C) ** 2}             # phi=0: times the dipole's own cos^2
ok_C = np.sin(POLAR_C) <= GLANCING
res_C = {}
for phi_deg in (90.0, 0.0):
    p = flux_C[phi_deg] / flux_C[phi_deg][ok_C].max(); a = an_C[phi_deg] / an_C[phi_deg][ok_C].max()
    res_C[phi_deg] = {"pattern": p, "analytic": a, "err_in": rel_l2(p[ok_C], a[ok_C]), "err_all": rel_l2(p, a),
                      "corr_all": float(np.corrcoef(p, a)[0, 1])}
    print(f"C [phi = {phi_deg:.0f} deg]: 1D Bloch, {len(POLAR_C)} angles: rel L2 {res_C[phi_deg]['err_in']:.4f} below the glancing limit, "
          f"{res_C[phi_deg]['err_all']:.4f} with grazing angles included (correlation {res_C[phi_deg]['corr_all']:.4f})")
pB_on_C = np.interp(POLAR_C, THETA_B, pattern_B)
err_BC = rel_l2(res_C[90.0]["pattern"][ok_C], pB_on_C[ok_C])
print(f"B vs C: 2D near2far (Ez) vs 1D Bloch (Ex, phi = 90 deg) on the same angles: rel L2 {err_BC:.4f}")

fig = plt.figure(figsize=(13, 4.6))
ax = fig.add_subplot(1, 3, 1, projection="polar")
ax.plot(THETA_B, pattern_B, "-", color="tab:blue", lw=1.6, label="B: 2D near2far (Ez dipole)")
ax.plot(THETA_B, array_factor, "--", color="k", lw=1.2, label="analytic sin^2(k h cos t)")
ax.plot(POLAR_C[ok_C], res_C[90.0]["pattern"][ok_C], "o", color="tab:green", ms=4, label="C: 1D Bloch (Ex, phi = 90)")
ax.plot(POLAR_C[~ok_C], res_C[90.0]["pattern"][~ok_C], "x", color="tab:red", ms=6, label="C: grazing angles")
ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.set_rlim(0, 1.3)
ax.set_title(f"dipole {H} um above a PEC, k h = {K_B * H:.1f}", fontsize=9); ax.legend(fontsize=6.5, loc="lower left")
ax = fig.add_subplot(1, 3, 2, projection="polar")
ax.plot(POLAR_C[ok_C], res_C[0.0]["pattern"][ok_C], "o", color="tab:green", ms=4, label="C: 1D Bloch, phi = 0")
ax.plot(POLAR_C[~ok_C], res_C[0.0]["pattern"][~ok_C], "x", color="tab:red", ms=6, label="grazing")
ax.plot(POLAR_C, res_C[0.0]["analytic"], "--", color="k", lw=1.2, label="analytic cos^2(t) sin^2(k h cos t)")
ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.set_rlim(0, 1.3)
ax.set_title("phi = 0: array factor times the dipole's cos^2", fontsize=9); ax.legend(fontsize=6.5, loc="lower left")
ax = fig.add_subplot(1, 3, 3)
for phi_deg, c in ((90.0, "tab:green"), (0.0, "tab:olive")):
    ax.plot(np.degrees(POLAR_C), np.abs(res_C[phi_deg]["pattern"] - res_C[phi_deg]["analytic"]), "o-", color=c, ms=4, label=f"1D Bloch, phi = {phi_deg:.0f}")
ax.plot(np.degrees(THETA_B), np.abs(pattern_B - array_factor), "-", color="tab:blue", lw=1.4, label="2D near2far")
ax.axvspan(np.degrees(np.arcsin(GLANCING)), 90, color="lightgray", alpha=0.6); ax.text(np.degrees(np.arcsin(GLANCING)) + 1, 0.02, "glancing:\nPML fails", fontsize=7)
ax.set_xlabel("theta from the mirror normal [deg]"); ax.set_ylabel("|pattern - analytic| (normalized)"); ax.set_yscale("log"); ax.set_ylim(1e-4, 2)
ax.grid(alpha=0.3); ax.legend(fontsize=7); ax.set_title("where each method fails", fontsize=9)
fig.suptitle(f"B: rel L2 {err_B:.4f} (near2far) | C: {res_C[90.0]['err_in']:.4f} below 72 deg, {res_C[90.0]['err_all']:.3f} with grazing angles", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.92]); fig.savefig(os.path.join(OUT, "05_pec_pattern.png"), dpi=150); plt.close(fig)

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"A": {"wl": WL_A, "res": RES_A, "n_polar": len(POLAR), "n_azimuth": len(AZIM), "n_runs": n_runs, "n_skipped": int(np.sum(~computed)),
                         "glancing_limit_deg": float(np.degrees(np.arcsin(GLANCING))), "err_mul": err_mul, "err_div": err_div, "err_raw": err_raw, "err_phi0": err_phi0},
                   "B": {"wl": WL_B, "n": N_B, "h": H, "res": RES_B, "kh": K_B * H, "box": BOX, "err": err_B, "peak_bin": [peak_B, peak_an],
                         "peak_deg": float(np.degrees(THETA_B[peak_B])), "node_ratio": node,
                         "pattern": pattern_B.tolist(), "analytic": array_factor.tolist(), "theta_deg": np.degrees(THETA_B).tolist()},
                   "C": {str(int(k_)): {"err_in": v["err_in"], "err_all": v["err_all"], "corr_all": v["corr_all"], "pattern": v["pattern"].tolist()} for k_, v in res_C.items()},
                   "B_vs_C": err_BC, "theta_C_deg": np.degrees(POLAR_C).tolist(),
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
print(f"total {time.time() - t_all:.0f} s")
