"""Meep Example 03 - Reference run subtraction: incident, total, scattered field and R, T, S.

Two runs of the same cell, with and without the object. What differs is the object's doing.
  A. 1D air | fused quartz: the procedure (normalization run + load_minus_flux_data) against the
     Fresnel formula R = ((1-n)/(1+n))^2 with the dispersive n(lambda) of the materials library.
     (official example refl-quartz.py)
  B. 2D dielectric cylinder (r = 0.75 um, n = 2) in a plane wave: E_scat = E_total - E_inc,
     and a closed flux box: R (left, incident subtracted), T (right), S (top + bottom, sideways
     scattering). For a lossless object R + T + S = 1.
  C. GIF: incident, total and scattered field side by side in time.

Run:  python reference_subtraction.py        (~2.5 min on one core)
Out:  00_source.png, 01_layout.png, 02_fresnel.png, 03_fields.png, 04_budget.png,
      05_anim_scatter.gif, result.json   (-> ../assets/03/)
"""
import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp
from meep.materials import fused_quartz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import (Label, animate_compare, annotated_layout, bar_figure, panel_grid,   # noqa: E402
                     record_frames, source_figure)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "03")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()

# ================================================================ A. 1D air | quartz vs Fresnel
# ---------------------------------------------------------------- (1) parameters (1D, units of um)
sz = 10.0
dpml1 = 1.0
wl_min, wl_max = 0.4, 0.8
fmin, fmax = 1 / wl_max, 1 / wl_min
fcen1, df1, nfreq1 = 0.5 * (fmin + fmax), fmax - fmin, 25
RES1 = 200                    # 1D is cheap: lambda_min / n = 0.27 um -> 54 px


def sim_1d(geometry):
    # ------------------------------------------------------------ (3) source: a plane wave in 1D is a point
    src = [mp.Source(mp.GaussianSource(fcen1, fwidth=df1), component=mp.Ex, center=mp.Vector3(0, 0, -0.5 * sz + dpml1))]
    # ------------------------------------------------------------ (4) simulation
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, sz), boundary_layers=[mp.PML(dpml1)], sources=src,
                        geometry=geometry, dimensions=1, resolution=RES1)
    # ------------------------------------------------------------ (5) monitors: reflection (air side), transmission (inside quartz)
    refl = sim.add_flux(fcen1, df1, nfreq1, mp.FluxRegion(center=mp.Vector3(0, 0, -0.25 * sz)))
    tran = sim.add_flux(fcen1, df1, nfreq1, mp.FluxRegion(center=mp.Vector3(0, 0, +0.25 * sz)))
    return sim, refl, tran


# run 1: empty (air everywhere) -> incident flux and the incident flux DATA at the reflection plane
sim, refl, tran = sim_1d([])
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ex, mp.Vector3(0, 0, 0.25 * sz), 1e-9))   # (6)
inc_flux = np.array(mp.get_fluxes(refl))
refl_data = sim.get_flux_data(refl)
freqs1 = np.array(mp.get_flux_freqs(refl))
# run 2: quartz half-space from z = 0 through the PML
quartz = [mp.Block(size=mp.Vector3(mp.inf, mp.inf, 0.5 * sz), center=mp.Vector3(0, 0, 0.25 * sz), material=fused_quartz)]
sim, refl, tran = sim_1d(quartz)
sim.load_minus_flux_data(refl, refl_data)                              # incident part removed -> reflection only
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ex, mp.Vector3(0, 0, 0.25 * sz), 1e-9))
# ---------------------------------------------------------------- (7) R, T and the Fresnel formula
R1 = -np.array(mp.get_fluxes(refl)) / inc_flux                        # backward flux is negative
T1 = np.array(mp.get_fluxes(tran)) / inc_flux
n_q = np.array([np.sqrt(np.real(fused_quartz.epsilon(f)[0][0])) for f in freqs1])   # n(lambda) from the material model
R_fresnel = ((1 - n_q) / (1 + n_q)) ** 2
wl1 = 1 / freqs1
ic1 = nfreq1 // 2
print(f"A. Fresnel: max|R_meep - R_fresnel| = {np.max(np.abs(R1 - R_fresnel)):.2e}; "
      f"R @ {wl1[ic1]:.3f} um: meep {R1[ic1]:.5f}, Fresnel {R_fresnel[ic1]:.5f}; R+T = {R1[ic1] + T1[ic1]:.5f}; "
      f"n = {n_q[0]:.4f} ({wl1[0]:.2f} um) .. {n_q[-1]:.4f} ({wl1[-1]:.2f} um)")

fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
z = np.linspace(-sz / 2, sz / 2, 400)
eps_z = np.where(z > 0, n_q[ic1] ** 2, 1.0)
ax[0].plot(z, eps_z, color="k")
ax[0].axvline(-0.5 * sz + dpml1, color="red", lw=2, label="source")
ax[0].axvline(-0.25 * sz, color="blue", lw=2, label="reflection monitor")
ax[0].axvline(+0.25 * sz, color="blue", lw=2, ls="--", label="transmission monitor")
for zz in (-sz / 2 + dpml1, sz / 2 - dpml1):
    ax[0].axvspan(zz if zz > 0 else -sz / 2, sz / 2 if zz > 0 else zz, color="green", alpha=0.12)
ax[0].set_xlabel("z [um]"); ax[0].set_ylabel("epsilon"); ax[0].set_title("1D cell: air | fused quartz (green = PML)", fontsize=9)
ax[0].legend(fontsize=7, loc="center left")
ax[1].plot(wl1 * 1000, R_fresnel * 100, "k-", label="Fresnel  ((1-n)/(1+n))^2 with n(lambda) of fused_quartz")
ax[1].plot(wl1 * 1000, R1 * 100, "o", ms=4, color="tab:blue", label="Meep: reference run + load_minus_flux_data")
ax[1].set_xlabel("wavelength [nm]"); ax[1].set_ylabel("reflectance R [%]"); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=7)
ax[1].set_title(f"max |R_meep - R_Fresnel| = {np.max(np.abs(R1 - R_fresnel)):.1e}", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_fresnel.png"), dpi=150); plt.close(fig)

# ================================================================ B. 2D cylinder: fields and the power budget
# ---------------------------------------------------------------- (1) parameters
wl = 1.55
fcen = 1 / wl
fwidth = 0.12                 # narrow band: a nearly single-frequency field map at fcen
sx, sy = 14.0, 10.0
DPML = 1.0
RESOLUTION = 20
r_cyl, n_cyl = 0.75, 2.0
src_x = -0.5 * sx + DPML + 0.25
xm = 0.5 * sx - DPML - 0.9    # flux box: x = +-5.1
ym = 0.5 * sy - DPML - 0.2    # flux box: y = +-3.8
right_center = mp.Vector3(xm, 0)

# ---------------------------------------------------------------- (2) geometry: the object of run 2
cylinder = [mp.Cylinder(radius=r_cyl, height=mp.inf, center=mp.Vector3(), material=mp.Medium(index=n_cyl))]


# ---------------------------------------------------------------- (3) source: a line across the whole cell -> plane wave along +x
def plane_wave(fw):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=True), component=mp.Ez,
                      center=mp.Vector3(src_x, 0), size=mp.Vector3(0, sy))]


# ---------------------------------------------------------------- (4) simulation + (5) the closed flux box
REGIONS = {
    "left":   lambda: mp.FluxRegion(center=mp.Vector3(-xm, 0), size=mp.Vector3(0, 2 * ym)),
    "right":  lambda: mp.FluxRegion(center=mp.Vector3(+xm, 0), size=mp.Vector3(0, 2 * ym)),
    "top":    lambda: mp.FluxRegion(center=mp.Vector3(0, +ym), size=mp.Vector3(2 * xm, 0)),
    "bottom": lambda: mp.FluxRegion(center=mp.Vector3(0, -ym), size=mp.Vector3(2 * xm, 0), weight=-1),
}


def build(geometry, resolution=RESOLUTION, fw=fwidth):
    """Simulation plus TWO flux monitors per side of the box: one for the total field, and one that
    will have the incident field subtracted (load_minus_flux_data) so it measures the scattered field only."""
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy), boundary_layers=[mp.PML(DPML)], geometry=geometry,
                        sources=plane_wave(fw), resolution=resolution)
    total = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}
    scat = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}
    return sim, total, scat


def run_decay(sim):                                                  # (6)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, right_center, 1e-5))


def outward(fluxes):
    """Outward power through the box: the left side's outward normal is -x."""
    return {"left": -fluxes["left"], "right": fluxes["right"], "top": fluxes["top"], "bottom": fluxes["bottom"]}


nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * DPML, sy - 2 * DPML))
extent = [-(sx / 2 - DPML), sx / 2 - DPML, -(sy / 2 - DPML), sy / 2 - DPML]


def budget(resolution=RESOLUTION, fields=False, layout=False):
    """Run 1 (empty) then run 2 (cylinder). Returns the total-field budget R, T, S (sums to 1),
    the scattered-field power and cross section, and optionally the DFT field maps."""
    sim, total, scat = build([], resolution)
    if fields:
        dft_ref = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)
    run_decay(sim)
    inc_side = {k: float(mp.get_fluxes(m)[0]) for k, m in total.items()}   # incident flux through each side (+x / +y)
    inc = inc_side["right"]                                                # incident power through the box width
    inc_data = {k: sim.get_flux_data(m) for k, m in scat.items()}
    ez_inc = sim.get_dft_array(dft_ref, mp.Ez, 0) if fields else None

    sim, total, scat = build(cylinder, resolution)
    for k, m in scat.items():
        sim.load_minus_flux_data(m, inc_data[k])                           # these now see E_total - E_inc only
    if layout:
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(8.2, 6.0),
            title="run 2 (device): plane-wave line source, dielectric cylinder, closed flux box, PML",
            params_text=f"wl={wl} um  fwidth={fwidth}  res={resolution}/um\ncell={sx:g}x{sy:g}  dpml={DPML:g}  r={r_cyl}  n={n_cyl}",
            params_xy=(-5.8, 4.6), pml_xy=(2.0, -4.5), decay_point=(xm, 0), decay_text_xy=(1.6, -1.2),
            labels=[Label("cylinder r = 0.75 um, n = 2 (geometry)", (r_cyl, 0.3), (-4.0, 2.4), step=2, color="black"),
                    Label("line source across the cell (plane wave)", (src_x, 2.0), (-4.5, 3.4), step=3, color="red"),
                    Label("flux box: 4 sides x (total, incident-subtracted)", (xm, -2.5), (-1.5, -3.2), step=5, color="blue")])
    if fields:
        dft_dev = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)
    run_decay(sim)
    # ------------------------------------------------------------ (7) budgets
    tot = {k: float(mp.get_fluxes(m)[0]) for k, m in total.items()}
    sc = {k: float(mp.get_fluxes(m)[0]) for k, m in scat.items()}
    # total-field budget: flux DIFFERENCES to the empty run (exact by energy conservation)
    R = -(tot["left"] - inc_side["left"]) / inc                            # backward: -x is outward on the left
    T = tot["right"] / inc                                                 # what a detector behind the cylinder sees
    S = ((tot["top"] - inc_side["top"]) + (tot["bottom"] - inc_side["bottom"])) / inc   # sideways, both signs outward
    conservation = sum(outward(tot).values()) / inc                        # total field: must be 0 (lossless)
    # scattered-field budget: fluxes of (E_total - E_inc) through the four sides
    sc_out = outward(sc)
    P_sc = sum(sc_out.values())
    R_sub = sc_out["left"] / inc                                           # = R: counter-propagating waves have no cross term
    I_inc = inc / (2 * ym)                                                 # incident power per unit width
    sigma = P_sc / I_inc                                                   # 2D scattering cross section [um]
    out = {"R": R, "T": T, "S": S, "sum": R + T + S, "conservation": conservation, "R_sub": R_sub,
           "P_sc_over_inc": P_sc / inc, "sc_parts": {k: v / inc for k, v in sc_out.items()},
           "sigma_um": sigma, "Q_sca": sigma / (2 * r_cyl), "inc_flux": inc}
    if fields:
        ez_tot = sim.get_dft_array(dft_dev, mp.Ez, 0)
        out["fields"] = (ez_inc, ez_tot, ez_tot - ez_inc)
    return out


def mie_q_sca_2d_tm(m, x, nmax=30):
    """Scattering efficiency of an infinite dielectric cylinder, E parallel to the axis (Ez), normal
    incidence. From continuity of Ez and dEz/dr at r = a: b_n = [m Jn'(mx) Jn(x) - Jn(mx) Jn'(x)] /
    [Jn(mx) Hn'(x) - m Jn'(mx) Hn(x)],  Q_sca = (2/x) sum_n |b_n|^2 over n = -inf..inf."""
    from scipy.special import jv, jvp, hankel1, h1vp
    q = 0.0
    for n in range(-nmax, nmax + 1):
        b = (m * jvp(n, m * x) * jv(n, x) - jv(n, m * x) * jvp(n, x)) / (jv(n, m * x) * h1vp(n, x) - m * jvp(n, m * x) * hankel1(n, x))
        q += abs(b) ** 2
    return 2 * q / x


source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")
base = budget(fields=True, layout=True)
x_size = 2 * np.pi * r_cyl / wl
try:
    Q_mie = mie_q_sca_2d_tm(n_cyl, x_size)
except Exception as exc:                                                  # scipy missing: report, do not fake
    Q_mie = None
    print("Mie comparison skipped:", exc)
print(f"B. total-field budget: R = {base['R']:.4f}, T = {base['T']:.4f}, S = {base['S']:.4f}, R+T+S = {base['sum']:.4f} "
      f"(conservation residual {base['conservation']:+.4f}); R from subtracted field = {base['R_sub']:.4f}")
print(f"B. scattered field: P_sc/inc = {base['P_sc_over_inc']:.4f} " + " ".join(f"{k}={v:.4f}" for k, v in base['sc_parts'].items())
      + f"; sigma = {base['sigma_um']:.3f} um, Q_sca = {base['Q_sca']:.3f}" + (f" (2D Mie, x = {x_size:.2f}: {Q_mie:.3f})" if Q_mie else ""))
ez_inc, ez_tot, ez_sc = base["fields"]
circ = {i: (0, 0, r_cyl, "") for i in range(3)}
panel_grid([ez_inc, ez_tot, ez_sc], ["incident (run 1, no object)", "total (run 2, with cylinder)", "scattered = total - incident"],
           extent, os.path.join(OUT, "03_fields.png"), ncols=3, circles=circ, figsize=(14, 3.9),
           suptitle=f"Re(Ez) at 1550 nm, one color scale; dashed circle = cylinder")
bar_figure(["R (reflected)", "T (transmitted)", "S (sideways)", "R + T + S"],
           {"total field, minus the empty run": [base["R"], base["T"], base["S"], base["sum"]],
            "scattered field only (E_tot - E_inc)": [base["sc_parts"]["left"], base["sc_parts"]["right"],
                                                     base["sc_parts"]["top"] + base["sc_parts"]["bottom"], base["P_sc_over_inc"]]},
           os.path.join(OUT, "04_budget.png"), ylabel="fraction of incident power", reference=1.0, reference_label="lossless: 1")

keys = ("R", "T", "S", "sum", "Q_sca")
convergence = [{"resolution": RESOLUTION, **{k: base[k] for k in keys}}]
for res in (40,):
    b = budget(resolution=res)
    convergence.append({"resolution": res, **{k: b[k] for k in keys}})
    print(f"convergence res={res}: R={b['R']:.4f} T={b['T']:.4f} S={b['S']:.4f} sum={b['sum']:.4f} Q_sca={b['Q_sca']:.3f}")

# ================================================================ C. GIF: incident / total / scattered in time
fw_anim = 0.3 * fcen
w_anim = 1 / fw_anim
t_src = 5 / fw_anim
sets = []
for geom in ([], cylinder):
    s_anim = mp.Simulation(cell_size=mp.Vector3(sx, sy), boundary_layers=[mp.PML(DPML)], geometry=geom,
                           sources=plane_wave(fw_anim), resolution=14)
    frames, times = record_frames(s_anim, nonpml, mp.Ez, t_start=t_src - 2 * w_anim, t_end=t_src + sx + 6, n_frames=60)
    sets.append(frames)
sets.append([t - i for t, i in zip(sets[1], sets[0])])                  # scattered = total - incident, frame by frame
animate_compare(sets, ["incident (no object)", "total (cylinder)", "scattered = total - incident"], times, extent,
                os.path.join(OUT, "05_anim_scatter.gif"), figsize=(13, 3.9), suptitle="plane wave from the left")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"fresnel": {"wavelengths_um": wl1.tolist(), "R_meep": R1.tolist(), "R_fresnel": R_fresnel.tolist(),
                               "T_meep": T1.tolist(), "n_quartz": n_q.tolist(),
                               "max_abs_err": float(np.max(np.abs(R1 - R_fresnel))), "R_center": float(R1[ic1]),
                               "R_fresnel_center": float(R_fresnel[ic1]), "R_plus_T_center": float(R1[ic1] + T1[ic1])},
                   "cylinder": {k: base[k] for k in ("R", "T", "S", "sum", "conservation", "R_sub", "P_sc_over_inc", "sc_parts", "sigma_um", "Q_sca", "inc_flux")},
                   "mie": {"x": x_size, "Q_sca_tm": Q_mie},
                   "convergence": convergence, "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
