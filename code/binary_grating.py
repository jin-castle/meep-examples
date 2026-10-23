"""Meep Example 06 - Binary grating and diffraction orders.

  A. One period of a glass binary grating (period 2.6 um > wavelength): the grating equation says only
     m = 0, +-1 propagate in air, at +-36.6 deg. DiffractedPlanewave gives the power in each order;
     checks: sum of orders = total transmitted flux, T + R = 1.  (official binary_grating.py, period reduced)
  B. A subwavelength period (1.2 um): only m = 0 propagates. Sweep the duty cycle and record the
     transmitted amplitude AND phase of the zeroth order, for two ridge heights. This curve is the
     prototype of the meta-atom phase library of post 07; the phase span scales like dn * h / lambda.
  C. A finite grating (8 ridges) with PML on all sides: the three beams become visible; the beam angle
     is read from the spatial FFT of the scattered field on a far cut and compared with the equation.
  D. GIF of C in time.

Run:  python binary_grating.py           (~5 min on one core)
Out:  00_source.png, 01_layout.png, 02_orders.png, 03_duty_sweep.png, 04_finite.png,
      05_anim_finite.gif, result.json   (-> ../assets/06/)
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, animate_fields, annotated_layout, bar_figure, record_frames, source_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "06")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()

# ---------------------------------------------------------------- (1) units & parameters
wl = 1.55
fcen = 1 / wl
fwidth = 0.1 * fcen           # narrow band: single-frequency order decomposition
n_glass = 1.5
glass = mp.Medium(index=n_glass)
DPML, DSUB, DPAD = 1.0, 2.0, 2.0

GP_A, GH_A, GDC_A = 2.6, 0.5, 0.5       # A: diffracting period (lambda / GP = 0.60 -> m = 0, +-1 only)
GP_B = 1.2                               # B: subwavelength period (lambda / GP = 1.29 -> m = 0 only)
RESOLUTION = 25


def orders_propagating(gp):
    """Grating equation at normal incidence: sin(theta_m) = m * wl / gp (into air)."""
    m_max = int(np.floor(gp / wl))
    return {m: float(np.degrees(np.arcsin(m * wl / gp))) for m in range(-m_max, m_max + 1)}


# ---------------------------------------------------------------- (2) geometry: substrate + one ridge per period
def grating_geometry(sx, gp, gh, gdc):
    return [mp.Block(material=glass, size=mp.Vector3(DPML + DSUB, mp.inf, mp.inf),
                     center=mp.Vector3(-0.5 * sx + 0.5 * (DPML + DSUB), 0)),          # substrate through the PML
            mp.Block(material=glass, size=mp.Vector3(gh, gdc * gp, mp.inf),
                     center=mp.Vector3(-0.5 * sx + DPML + DSUB + 0.5 * gh, 0))]      # the ridge, width gdc * gp


# ---------------------------------------------------------------- (3) source: plane wave inside the glass, travelling +x
def plane_wave(sx, sy, fw=fwidth):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw), component=mp.Ez,
                      center=mp.Vector3(-0.5 * sx + DPML + 0.5 * DSUB, 0), size=mp.Vector3(0, sy))]


# ---------------------------------------------------------------- (4) one periodic cell: PML in x only, Bloch-periodic in y (k = 0)
def periodic_cell(gp, gh, gdc, resolution=RESOLUTION, empty=False):
    sx = DPML + DSUB + gh + DPAD + DPML
    sim = mp.Simulation(cell_size=mp.Vector3(sx, gp), resolution=resolution,
                        boundary_layers=[mp.PML(DPML, direction=mp.X)],
                        geometry=[] if empty else grating_geometry(sx, gp, gh, gdc),
                        default_material=glass if empty else mp.air,     # reference: glass everywhere
                        sources=plane_wave(sx, gp), k_point=mp.Vector3())
    # ------------------------------------------------------------ (5) monitors: reflection (in glass), transmission (in air)
    refl = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(-0.5 * sx + DPML + 0.8 * DSUB, 0), size=mp.Vector3(0, gp)))
    tran = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * sx - DPML - 0.5 * DPAD, 0), size=mp.Vector3(0, gp)))
    return sim, refl, tran, sx


def run_periodic(gp, gh, gdc, orders, resolution=RESOLUTION, layout=False):
    """Reference (all glass) then grating. Returns P_in-normalised T_m, T_total, R and the order amplitudes."""
    sim, refl, tran, sx = periodic_cell(gp, gh, gdc, resolution, empty=True)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(0.5 * sx - DPML - 0.5 * DPAD, 0), 1e-6))  # (6)
    P_in = float(mp.get_fluxes(tran)[0])                      # incident power per period (measured in glass)
    refl_data = sim.get_flux_data(refl)

    sim, refl, tran, sx = periodic_cell(gp, gh, gdc, resolution)
    sim.load_minus_flux_data(refl, refl_data)
    if layout:
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(8.6, 4.2),
            title=f"one period: glass substrate + ridge, PML in x only, Bloch-periodic in y (period {gp} um)",
            params_text=f"wl={wl}  res={resolution}\nL={gp} h={gh} dc={gdc}",
            params_xy=(1.5, 1.15), pml_xy=(-2.6, -1.0), decay_point=(0.5 * sx - DPML - 0.5 * DPAD, 0), decay_text_xy=(1.4, -1.0),
            labels=[Label("glass substrate + ridge (geometry)", (-0.5 * sx + DPML + DSUB + 0.25, 0.3), (-2.0, 0.95), step=2, color="black"),
                    Label("plane-wave source in the glass", (-0.5 * sx + DPML + 0.5 * DSUB, -0.6), (-2.3, -1.15), step=3, color="red"),
                    Label("flux: reflection (glass) / transmission (air)", (0.5 * sx - DPML - 0.5 * DPAD, -0.2), (-0.1, -0.55), step=5, color="blue")],
            axis_step=1.0)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(0.5 * sx - DPML - 0.5 * DPAD, 0), 1e-6))
    # ------------------------------------------------------------ (7) orders by DiffractedPlanewave, totals by flux
    # one DiffractedPlanewave per call: order m along the periodic direction y, s-polarised (Ez)
    amp = {m: sim.get_eigenmode_coefficients(tran, mp.DiffractedPlanewave((0, m, 0), mp.Vector3(0, 1, 0), 1, 0)).alpha[0, 0, 0]
           for m in orders}
    T_m = {m: float(abs(a) ** 2 / P_in) for m, a in amp.items()}
    phase_m = {m: float(np.angle(a)) for m, a in amp.items()}
    return {"T_m": T_m, "phase_m": phase_m, "T_total": float(mp.get_fluxes(tran)[0] / P_in),
            "R": float(-mp.get_fluxes(refl)[0] / P_in), "P_in": P_in}


source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ A. diffraction orders of the 2.6 um grating
angles = orders_propagating(GP_A)
A = run_periodic(GP_A, GH_A, GDC_A, sorted(angles), layout=True)
sum_orders = sum(A["T_m"].values())
print(f"A. period {GP_A} um: propagating orders {sorted(angles)} at " + ", ".join(f"m={m}: {a:+.1f} deg" for m, a in sorted(angles.items())))
print(f"A. T_m = " + ", ".join(f"m={m}: {t:.4f}" for m, t in sorted(A['T_m'].items())) +
      f"; sum = {sum_orders:.4f}, T_total (flux) = {A['T_total']:.4f}, R = {A['R']:.4f}, T+R = {A['T_total'] + A['R']:.4f}")
bar_figure([f"m = {m}\n({angles[m]:+.1f} deg)" for m in sorted(angles)] + ["sum of orders", "T (flux)", "R", "T + R"],
           {"fraction of incident power": [A["T_m"][m] for m in sorted(angles)] + [sum_orders, A["T_total"], A["R"], A["T_total"] + A["R"]]},
           os.path.join(OUT, "02_orders.png"), ylabel="fraction of incident power", reference=1.0, reference_label="lossless: 1", figsize=(8, 4))
convergence = [{"resolution": RESOLUTION, **{f"T_{m}": A["T_m"][m] for m in sorted(angles)}, "R": A["R"], "T_plus_R": A["T_total"] + A["R"]}]
for res in (50,):
    Ar = run_periodic(GP_A, GH_A, GDC_A, sorted(angles), resolution=res)
    convergence.append({"resolution": res, **{f"T_{m}": Ar["T_m"][m] for m in sorted(angles)}, "R": Ar["R"], "T_plus_R": Ar["T_total"] + Ar["R"]})
    print(f"convergence res={res}: " + ", ".join(f"T_{m}={Ar['T_m'][m]:.4f}" for m in sorted(angles)) + f", R={Ar['R']:.4f}, T+R={Ar['T_total'] + Ar['R']:.4f}")

# ================================================================ B. subwavelength period: duty-cycle sweep of the zeroth order
duty = np.linspace(0.1, 0.9, 9)
sweep = {}
for gh in (0.35, 0.9):
    rows = [run_periodic(GP_B, gh, float(d), [0]) for d in duty]
    T0 = np.array([r["T_m"][0] for r in rows])
    ph = np.unwrap(np.array([r["phase_m"][0] for r in rows]))
    ph -= ph[0]
    step = float(np.max(np.abs(np.diff(ph))))
    sweep[gh] = {"duty": duty.tolist(), "T0": T0.tolist(), "phase": ph.tolist(), "span_over_2pi": float((ph.max() - ph.min()) / (2 * np.pi)),
                 "estimate_dn_h_over_wl": (n_glass - 1) * gh / wl, "max_step_rad": step,
                 "T_total_minus_T0_max": float(max(abs(r["T_total"] - r["T_m"][0]) for r in rows))}
    print(f"B. h={gh}: T0 in [{T0.min():.3f}, {T0.max():.3f}], phase span = {sweep[gh]['span_over_2pi']:.3f} x 2pi "
          f"(estimate dn*h/wl = {sweep[gh]['estimate_dn_h_over_wl']:.3f}), max step {step:.2f} rad, max|T_total - T0| = {sweep[gh]['T_total_minus_T0_max']:.1e}")
fig, ax = plt.subplots(1, 2, figsize=(11, 3.9))
for gh, st in ((0.35, "o-"), (0.9, "s--")):
    ax[0].plot(duty, sweep[gh]["T0"], st, label=f"h = {gh} um")
    ax[1].plot(duty, np.array(sweep[gh]["phase"]) / (2 * np.pi), st, label=f"h = {gh} um  (span {sweep[gh]['span_over_2pi']:.2f}, estimate {sweep[gh]['estimate_dn_h_over_wl']:.2f})")
ax[0].set_xlabel("duty cycle (ridge width / period)"); ax[0].set_ylabel("zeroth-order transmission T0"); ax[0].set_ylim(0, 1.05); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
ax[0].set_title(f"subwavelength period {GP_B} um: amplitude side", fontsize=9)
ax[1].axhline(1.0, color="crimson", ls="--", lw=1.0); ax[1].text(0.12, 1.02, "2 pi (what a phase library needs)", color="crimson", fontsize=8)
ax[1].set_xlabel("duty cycle"); ax[1].set_ylabel("phase of T0 / 2 pi  (relative to duty 0.1)"); ax[1].set_ylim(-0.05, 1.15); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
ax[1].set_title("phase side: prototype of a phase library", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_duty_sweep.png"), dpi=150); plt.close(fig)

# ================================================================ C. finite grating: the beams, and the angle from a spatial FFT
N_RIDGE = 8
RES_C = 15
pad_y = 3.0
sx_c = DPML + DSUB + GH_A + 10.0 + DPML
sy_c = N_RIDGE * GP_A + 2 * pad_y + 2 * DPML
x_ridge = -0.5 * sx_c + DPML + DSUB + 0.5 * GH_A


def finite_geometry(with_ridges):
    g = [mp.Block(material=glass, size=mp.Vector3(DPML + DSUB, mp.inf, mp.inf), center=mp.Vector3(-0.5 * sx_c + 0.5 * (DPML + DSUB), 0))]
    if with_ridges:
        for i in range(N_RIDGE):
            yc = (i - (N_RIDGE - 1) / 2) * GP_A
            g.append(mp.Block(material=glass, size=mp.Vector3(GH_A, GDC_A * GP_A, mp.inf), center=mp.Vector3(x_ridge, yc)))
    return g


def finite_sim(with_ridges, fw=fwidth, resolution=RES_C):
    return mp.Simulation(cell_size=mp.Vector3(sx_c, sy_c), resolution=resolution, boundary_layers=[mp.PML(DPML)],
                         geometry=finite_geometry(with_ridges),
                         sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=True), component=mp.Ez,
                                            center=mp.Vector3(-0.5 * sx_c + DPML + 0.5 * DSUB, 0), size=mp.Vector3(0, sy_c))])


nonpml_c = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx_c - 2 * DPML, sy_c - 2 * DPML))
extent_c = [-(sx_c / 2 - DPML), sx_c / 2 - DPML, -(sy_c / 2 - DPML), sy_c / 2 - DPML]
fields = {}
for tag, ridges in (("flat", False), ("grating", True)):
    sim = finite_sim(ridges)
    dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml_c)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(0.5 * sx_c - DPML - 1.0, 0), 1e-5))
    fields[tag] = sim.get_dft_array(dft, mp.Ez, 0)
    if ridges:
        eps_c = sim.get_array(vol=nonpml_c, component=mp.Dielectric)
ez_sc = fields["grating"] - fields["flat"]                 # scattered field: what the ridges added
nx, ny = ez_sc.shape
xs = np.linspace(extent_c[0], extent_c[1], nx); ys = np.linspace(extent_c[2], extent_c[3], ny)
x_cut = x_ridge + 8.0                                      # far cut, 8 um past the ridges, in homogeneous air
line = ez_sc[np.argmin(abs(xs - x_cut)), :]
ky = np.fft.fftshift(np.fft.fftfreq(ny, d=ys[1] - ys[0]))  # cycles per um
spec = np.abs(np.fft.fftshift(np.fft.fft(line * np.hanning(ny)))) ** 2
spec /= spec.max()
pos = ky > 0.15
k_peak = float(ky[pos][np.argmax(spec[pos])])
theta_meas = float(np.degrees(np.arcsin(min(k_peak * wl, 1.0))))   # sin(theta) = k_y / k0 = k_peak * wl
print(f"C. finite grating ({N_RIDGE} ridges): spatial-FFT peak at {k_peak:.3f} cycles/um -> theta = {theta_meas:.1f} deg "
      f"(grating equation: 1/period = {1/GP_A:.3f} cycles/um -> {angles[1]:.1f} deg)")

fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1.5, 1]})
im = ax[0].imshow(np.abs(fields["grating"]).T, origin="lower", extent=extent_c, cmap="inferno", aspect="equal")
ax[0].contour(xs, ys, eps_c.T, levels=[0.5 * (eps_c.min() + eps_c.max())], colors="w", linewidths=0.5)
for m, a in angles.items():
    L = 9.0
    ax[0].plot([x_ridge, x_ridge + L * np.cos(np.radians(a))], [0, L * np.sin(np.radians(a))], "--", color="cyan", lw=1.0)
    ax[0].text(x_ridge + L * np.cos(np.radians(a)) + 0.2, L * np.sin(np.radians(a)), f"m={m:+d}", color="cyan", fontsize=8, va="center")
ax[0].axvline(x_cut, color="lime", ls=":", lw=1.0); ax[0].text(x_cut, extent_c[3] - 0.8, "FFT cut", color="lime", fontsize=8, ha="center")
ax[0].set_xlabel("x [um]"); ax[0].set_ylabel("y [um]"); ax[0].set_title(f"|Ez| at 1550 nm, {N_RIDGE} ridges; dashed = grating-equation angles", fontsize=9)
fig.colorbar(im, ax=ax[0], shrink=0.8)
ax[1].semilogy(ky, spec, color="tab:blue")
for m in (-1, 1):
    ax[1].axvline(m / GP_A, color="crimson", ls="--", lw=0.9)
ax[1].text(1 / GP_A, 1.2, f"+1/period = {1/GP_A:.3f}", color="crimson", fontsize=8, ha="center")
ax[1].set_xlim(-1.2, 1.2); ax[1].set_ylim(1e-4, 3); ax[1].set_xlabel("spatial frequency k_y / 2pi [cycles/um]"); ax[1].set_ylabel("|FFT(E_scat on the cut)|^2 (norm.)")
ax[1].set_title(f"peak {k_peak:.3f} -> {theta_meas:.1f} deg (equation {angles[1]:.1f} deg)", fontsize=9); ax[1].grid(alpha=0.3, which="both")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_finite.png"), dpi=150); plt.close(fig)

# ================================================================ D. GIF: the beams forming in time
fw_anim = 0.3 * fcen
sim_anim = finite_sim(True, fw=fw_anim, resolution=12)
sim_anim.init_sim()
eps_anim = sim_anim.get_array(vol=nonpml_c, component=mp.Dielectric)
frames, times = record_frames(sim_anim, nonpml_c, mp.Ez, t_start=5 / fw_anim - 2 / fw_anim, t_end=5 / fw_anim + 1.5 * sx_c + 10, n_frames=60)
animate_fields(frames, times, extent_c, os.path.join(OUT, "05_anim_finite.gif"), eps=eps_anim, figsize=(5.2, 6.4), dpi=70,
               title=f"{N_RIDGE}-ridge grating, plane wave from the left", legend_loc="lower right")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"A": {"period": GP_A, "angles_deg": angles, **{k: A[k] for k in ("T_m", "phase_m", "T_total", "R")}, "sum_orders": sum_orders},
                   "convergence": convergence, "B": {str(k): v for k, v in sweep.items()},
                   "C": {"n_ridges": N_RIDGE, "k_peak_cycles_per_um": k_peak, "theta_meas_deg": theta_meas, "theta_eq_deg": angles[1]},
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
