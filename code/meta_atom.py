"""Meep Example 07 - Meta-atoms and a phase library.

Local view of a periodic structure: each Si bar (width w, height H) in a subwavelength unit cell
transmits a plane wave with its own complex coefficient t(w). Collect t(w) -> phase library, pick
4 widths that step the phase by 90 deg, tile them into a supercell that should deflect light to +1,
and check how far the real device falls short of the 4-level blazed bound. Then a finite array and
its far field, and a GIF of the tilted wavefront.

  A. phase library: |t(w)|, arg t(w) at resolution 40 and 60 (reference = empty unit cell)
  B. 4-level design: phase targets phi0 + k*pi/2 -> widths; phi0 chosen to maximise min |t|
  C. supercell (period 4*La): orders by DiffractedPlanewave, sum = total flux, vs sinc^2(1/4) = 0.8106
  D. finite arrays (10 and 40 atoms): near2far pattern, main lobe vs the design angle
  E. GIF: 12-atom array, the wavefront leaves tilted

Run:  python meta_atom.py             (~4 min on one core)
Out:  00_source.png, 01_layout.png, 02_library.png, 03_design.png, 04_supercell.png,
      05_farfield.png, 06_anim_array.gif, result.json   (-> ../assets/07/)
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
from blogfig import Label, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "07")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()

# ---------------------------------------------------------------- (1) units & parameters
wl = 1.55
fcen = 1 / wl
fwidth = 0.1 * fcen
Si = mp.Medium(index=3.45)
SiO2 = mp.Medium(index=1.45)
N_SEC = 4                       # phase levels per supercell period
LA = 0.45                       # atom period [um]: 18 px at resolution 40 (integer pixels matter: see post)
LAMBDA = N_SEC * LA             # supercell period 1.80 um
THETA_D = float(np.degrees(np.arcsin(wl / LAMBDA)))   # +1 order angle: 59.44 deg
H = 0.9                         # bar height [um]
RES = 40
DPML, DSUB, DAIR = 1.0, 1.0, 1.0
SY = DPML + DSUB + H + DAIR + DPML
Y_BOT = -0.5 * SY
Y_DEV = Y_BOT + DPML + DSUB     # substrate top = bar bottom
SRC_Y = Y_BOT + DPML + 0.3      # source inside the substrate
MON_Y = -Y_BOT - DPML - 0.3     # monitor in the air above the bars
BLAZED_BOUND = (np.sin(np.pi / N_SEC) / (np.pi / N_SEC)) ** 2   # 4-level phase quantisation limit


# ---------------------------------------------------------------- (2) geometry: substrate + Si bars
def geometry_bars(widths, period):
    """SiO2 substrate through the bottom PML plus one Si bar per section (bar j centred in section j)."""
    g = [mp.Block(center=mp.Vector3(0, Y_BOT + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2)]
    n = len(widths)
    for j, w in enumerate(widths):
        if w > 0:
            xj = -0.5 * period + (j + 0.5) * period / n
            g.append(mp.Block(center=mp.Vector3(xj, Y_DEV + 0.5 * H), size=mp.Vector3(w, H), material=Si))
    return g


# ---------------------------------------------------------------- (3) source: plane wave in the substrate, travelling +y
def plane_wave(period, fw=fwidth, integrated=False):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=integrated), component=mp.Ez,
                      center=mp.Vector3(0, SRC_Y), size=mp.Vector3(period, 0))]


# ---------------------------------------------------------------- (4) periodic cell: PML in y only, Bloch-periodic in x (k = 0)
def periodic_sim(widths, period, resolution=RES):
    return mp.Simulation(resolution=resolution, cell_size=mp.Vector3(period, SY), geometry=geometry_bars(widths, period),
                         boundary_layers=[mp.PML(thickness=DPML, direction=mp.Y)], k_point=mp.Vector3(),
                         sources=plane_wave(period))


# ================================================================ A. phase library
def t_atom(w, resolution=RES):
    """Zeroth-order complex transmission of one unit cell: the DFT of Ez on the monitor line averaged
    over one period (the average over a period IS the zeroth Fourier coefficient). w = 0 -> reference."""
    sim = periodic_sim([w], LA, resolution)
    dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(0, MON_Y), size=mp.Vector3(LA, 0))   # (5)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(10, mp.Ez, mp.Vector3(0, MON_Y), 1e-7))      # (6)
    t = complex(np.mean(sim.get_dft_array(dft, mp.Ez, 0)))                                                 # (7)
    sim.reset_meep()
    return t


def build_library(widths, resolution=RES):
    t_ref = t_atom(0.0, resolution)
    t = np.array([t_atom(w, resolution) / t_ref for w in widths])
    phase = np.unwrap(np.angle(t))
    return np.abs(t), phase - phase[0]


source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")
widths = np.linspace(0.04, 0.42, 17)
amp40, ph40 = build_library(widths, RES)
amp60, ph60 = build_library(widths, 60)
span40 = float(ph40.max() - ph40.min())
dphi = ph60 - ph40
print(f"A. library H={H}: phase span = {span40:.3f} rad = {span40 / (2*np.pi):.3f} x 2pi; |t| in [{amp40.min():.3f}, {amp40.max():.3f}]; "
      f"monotonic: {bool(np.all(np.diff(ph40) > 0))}; res 60 vs 40: max|dphi| = {np.max(np.abs(dphi)):.3f} rad, max d|t| = {np.max(np.abs(amp60 - amp40)):.3f}")

fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
ax[0].plot(widths, amp40, "o-", label="resolution 40"); ax[0].plot(widths, amp60, "s--", label="resolution 60")
ax[0].set_ylim(0, 1.15); ax[0].set_xlabel("bar width w [um]"); ax[0].set_ylabel("|t|"); ax[0].set_title("transmission amplitude", fontsize=9); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
ax[1].plot(widths, ph40 / (2 * np.pi), "o-", label="resolution 40"); ax[1].plot(widths, ph60 / (2 * np.pi), "s--", label="resolution 60")
ax[1].axhline(1.0, ls="--", color="crimson", lw=1); ax[1].text(0.05, 1.02, "2 pi", color="crimson", fontsize=8)
ax[1].set_xlabel("bar width w [um]"); ax[1].set_ylabel("phase / 2 pi  (relative to w = 0.04)"); ax[1].set_title(f"transmission phase: span {span40/(2*np.pi):.2f} x 2pi", fontsize=9); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
ax[2].plot(widths, dphi, "o-", color="tab:red"); ax[2].axhline(0, color="k", lw=0.8)
ax[2].axhspan(-0.1 * 2 * np.pi / N_SEC, 0.1 * 2 * np.pi / N_SEC, color="tab:green", alpha=0.15)
ax[2].set_xlabel("bar width w [um]"); ax[2].set_ylabel("phase(60) - phase(40) [rad]"); ax[2].set_title("resolution error; green = 10 % of the pi/2 design step", fontsize=9); ax[2].grid(alpha=0.3)
fig.suptitle(f"meta-atom phase library: Si bar, H = {H} um, period {LA} um, lambda = 1550 nm", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_library.png"), dpi=150); plt.close(fig)

# ================================================================ B. 4-level design from the library
w_dense = np.linspace(widths[0], widths[-1], 2001)
ph_dense = np.interp(w_dense, widths, ph40)
amp_dense = np.interp(w_dense, widths, amp40)
best = None
for phi0 in np.linspace(0.0, span40 - 1.5 * np.pi, 400):
    targets = phi0 + np.arange(N_SEC) * (2 * np.pi / N_SEC)
    if targets.max() > span40:
        continue
    ws = np.interp(targets, ph_dense, w_dense)           # phase -> width (library is monotonic)
    amps = np.interp(ws, w_dense, amp_dense)
    if best is None or amps.min() > best[0]:
        best = (float(amps.min()), float(phi0), ws, amps, targets)
min_amp, phi0, w_sel, a_sel, targets = best
w_lib = np.round(w_sel * RES) / RES                       # snap to the pixel grid
print(f"B. design: phi0 = {phi0:.3f} rad, widths = {np.round(w_lib, 3).tolist()} um, |t| = {np.round(a_sel, 3).tolist()}, min |t| = {min_amp:.3f}")

fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
ax[0].plot(w_dense, ph_dense, color="tab:blue")
for j in range(N_SEC):
    ax[0].axhline(targets[j], color="gray", ls=":", lw=0.8); ax[0].plot([w_sel[j]], [targets[j]], "o", color="crimson")
    ax[0].annotate(f"section {j}: {np.degrees(targets[j] - targets[0]):.0f} deg", (w_sel[j], targets[j]), textcoords="offset points", xytext=(6, -11), fontsize=8)
ax[0].set_xlabel("bar width w [um]"); ax[0].set_ylabel("phase [rad]"); ax[0].set_title("solve phase -> width for 4 targets", fontsize=9); ax[0].grid(alpha=0.3)
ax[1].plot(w_dense, amp_dense, color="tab:blue"); ax[1].plot(w_sel, a_sel, "o", color="crimson")
ax[1].axhline(min_amp, ls="--", color="crimson", lw=1, label=f"min |t| = {min_amp:.3f}"); ax[1].set_ylim(0, 1.15)
ax[1].set_xlabel("bar width w [um]"); ax[1].set_ylabel("|t|"); ax[1].set_title("the price: |t| is not uniform", fontsize=9); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
for j in range(N_SEC):
    xj = -0.5 * LAMBDA + (j + 0.5) * LA
    ax[2].add_patch(plt.Rectangle((xj - 0.5 * LA, 0), LA, H, facecolor="none", edgecolor="gray", ls=":"))
    ax[2].add_patch(plt.Rectangle((xj - 0.5 * w_lib[j], 0), w_lib[j], H, facecolor="tab:blue", alpha=0.75))
    ax[2].text(xj, H * 1.08, f"{np.degrees(targets[j] - targets[0]):.0f} deg\nw = {w_lib[j]:.3f}", ha="center", fontsize=7.5)
ax[2].axhline(0, color="k", lw=1.2); ax[2].set_xlim(-0.55 * LAMBDA, 0.55 * LAMBDA); ax[2].set_ylim(-0.1 * H, 1.5 * H); ax[2].set_aspect("equal")
ax[2].set_xlabel("x [um]"); ax[2].set_ylabel("y [um]"); ax[2].set_title("one supercell period (1.8 um)", fontsize=9)
fig.suptitle("4-level phase design: four widths that step the phase by 90 deg", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_design.png"), dpi=150); plt.close(fig)

# ================================================================ C. supercell: where does the light go?
stop_sc = mp.stop_when_fields_decayed(10, mp.Ez, mp.Vector3(0, MON_Y), 1e-7)
mon_region = mp.ModeRegion(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0))
sim = mp.Simulation(resolution=RES, cell_size=mp.Vector3(LAMBDA, SY), default_material=SiO2,     # reference: all substrate
                    boundary_layers=[mp.PML(thickness=DPML, direction=mp.Y)], k_point=mp.Vector3(), sources=plane_wave(LAMBDA))
fl = sim.add_mode_monitor(fcen, 0, 1, mon_region)
sim.run(until_after_sources=stop_sc)
P_in = float(mp.get_fluxes(fl)[0])
sim.reset_meep()

sim = periodic_sim(w_lib, LAMBDA)
mon = sim.add_mode_monitor(fcen, 0, 1, mon_region)
annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(5.2, 7.0), axis_step=0.5,
    title=f"supercell: 4 Si bars on SiO2, period {LAMBDA} um, periodic in x, PML in y",
    params_text=f"wl={wl} res={RES}\nLa={LA} H={H}\nw={np.round(w_lib,3).tolist()}",
    params_xy=(-0.85, 2.35), pml_xy=(-0.5, Y_BOT + 0.5 * DPML), decay_point=(0, MON_Y), decay_text_xy=(-0.1, 1.75),
    labels=[Label("4 Si bars (geometry)", (-0.5 * LAMBDA + 0.5 * LA, Y_DEV + 0.5 * H), (-0.85, 1.25), step=2, color="black"),
            Label("plane wave in SiO2", (0.3, SRC_Y), (-0.85, SRC_Y - 0.35), step=3, color="red"),
            Label("mode monitor: orders", (0.5, MON_Y), (-0.85, MON_Y + 0.35), step=5, color="blue")])
dft_sc = sim.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(LAMBDA, SY))
sim.run(until_after_sources=stop_sc)
T_total = float(mp.get_fluxes(mon)[0] / P_in)
field_sc = sim.get_dft_array(dft_sc, mp.Ez, 0)
eps_sc = sim.get_epsilon()
orders = {}
for m in range(-3, 4):
    kx = m / LAMBDA
    if abs(kx) >= fcen:
        continue                                                                    # evanescent
    a = sim.get_eigenmode_coefficients(mon, mp.DiffractedPlanewave((m, 0, 0), mp.Vector3(1, 0, 0), 1, 0)).alpha[0, 0, 0]
    orders[m] = {"angle_deg": float(np.degrees(np.arcsin(kx / fcen))), "eff": float(abs(a) ** 2 / P_in)}
sim.reset_meep()
sum_orders = sum(v["eff"] for v in orders.values())
print("C. supercell orders: " + ", ".join(f"m={m}: {v['eff']:.4f} ({v['angle_deg']:+.1f} deg)" for m, v in sorted(orders.items())) +
      f"; sum = {sum_orders:.4f}, T_total = {T_total:.4f}; +1 efficiency {orders[1]['eff']:.4f} = {orders[1]['eff'] / BLAZED_BOUND * 100:.1f} % of the 4-level bound {BLAZED_BOUND:.4f}")

ext_sc = [-0.5 * LAMBDA, 0.5 * LAMBDA, Y_BOT, -Y_BOT]
fig, ax = plt.subplots(1, 3, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1.4, 1, 1]})
ms = sorted(orders)
bars = ax[0].bar([f"m = {m}\n{orders[m]['angle_deg']:+.0f} deg" for m in ms], [orders[m]["eff"] for m in ms], color=["tab:blue" if m == 1 else "tab:gray" for m in ms])
ax[0].axhline(BLAZED_BOUND, ls="--", color="crimson", lw=1.2, label=f"4-level blazed bound {BLAZED_BOUND:.3f}")
for b, m in zip(bars, ms):
    ax[0].text(b.get_x() + b.get_width() / 2, orders[m]["eff"] + 0.01, f"{orders[m]['eff']:.3f}", ha="center", fontsize=8)
ax[0].set_ylim(0, 1.0); ax[0].set_ylabel("efficiency (fraction of incident power)"); ax[0].set_title(f"orders: sum {sum_orders:.3f} = total flux {T_total:.3f}", fontsize=9); ax[0].grid(axis="y", alpha=0.3); ax[0].legend(fontsize=8)
xs = np.linspace(ext_sc[0], ext_sc[1], eps_sc.shape[0]); ys = np.linspace(ext_sc[2], ext_sc[3], eps_sc.shape[1])
lim = float(np.max(np.abs(np.real(field_sc))))
ax[1].imshow(np.real(field_sc).T, extent=ext_sc, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal"); ax[1].set_title("Re(Ez): the wavefront tilts", fontsize=9)
ax[2].imshow(np.abs(field_sc).T, extent=ext_sc, origin="lower", cmap="inferno", aspect="equal"); ax[2].set_title("|Ez|", fontsize=9)
for a in ax[1:]:
    a.contour(xs, ys, eps_sc.T, levels=[1.5, 6.0], colors="w", linewidths=0.6)
    a.axhline(MON_Y, color="lime", lw=0.8, ls="--"); a.set_xlabel("x [um]")
ax[1].set_ylabel("y [um]")
fig.suptitle(f"library supercell, design angle {THETA_D:.1f} deg", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_supercell.png"), dpi=150); plt.close(fig)


# ================================================================ D. finite arrays: far field
def finite_array(n_atom, resolution=30, pad=1.0, R_ff=200.0, angles=np.linspace(-85, 85, 341)):
    aperture = n_atom * LA
    sx = aperture + 2 * pad + 2 * DPML
    n2f_y = Y_DEV + H + 0.5 * DAIR
    geom = [mp.Block(center=mp.Vector3(0, Y_BOT + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2)]
    for j in range(n_atom):
        xj = -0.5 * aperture + (j + 0.5) * LA
        geom.append(mp.Block(center=mp.Vector3(xj, Y_DEV + 0.5 * H), size=mp.Vector3(w_lib[j % N_SEC], H), material=Si))
    sim = mp.Simulation(resolution=resolution, cell_size=mp.Vector3(sx, SY), boundary_layers=[mp.PML(DPML)], geometry=geom,
                        sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fwidth, is_integrated=True), component=mp.Ez,
                                           center=mp.Vector3(0, SRC_Y), size=mp.Vector3(aperture, 0))])   # source only under the array
    n2f = sim.add_near2far(fcen, 0, 1, mp.Near2FarRegion(center=mp.Vector3(0, n2f_y), size=mp.Vector3(sx - 2 * DPML, 0)))
    sim.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(0, n2f_y), 1e-6))
    I = np.array([abs(sim.get_farfield(n2f, mp.Vector3(R_ff * np.sin(np.radians(a)), R_ff * np.cos(np.radians(a))))[2]) ** 2 for a in angles])
    sim.reset_meep()
    return aperture, angles, I / I.max()


ff = {}
fig, ax = plt.subplots(figsize=(8, 4.2))
for n_atom, color in ((10, "tab:orange"), (40, "tab:blue")):
    aperture, angles, pattern = finite_array(n_atom)
    peak = float(angles[np.argmax(pattern)])
    bw = float(np.degrees(wl / (aperture * np.cos(np.radians(THETA_D)))))
    ff[n_atom] = {"aperture_um": aperture, "peak_deg": peak, "beamwidth_est_deg": bw}
    ax.plot(angles, pattern, color=color, label=f"{n_atom} atoms (D = {aperture:.1f} um): peak {peak:+.1f} deg, est. width {bw:.1f} deg")
    print(f"D. {n_atom} atoms: aperture {aperture:.2f} um, main lobe {peak:+.1f} deg (design {THETA_D:+.2f}), est. beam width {bw:.1f} deg")
ax.axvline(THETA_D, ls="--", color="gray", lw=1); ax.text(THETA_D, 1.03, f" design {THETA_D:.1f} deg", color="gray", fontsize=8)
ax.set_xlabel("angle from the normal [deg]"); ax.set_ylabel("normalized |Ez|^2 (far field)"); ax.set_ylim(0, 1.12); ax.grid(alpha=0.3); ax.legend(fontsize=8)
ax.set_title("far field of finite arrays built from the library", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_farfield.png"), dpi=150); plt.close(fig)

# ================================================================ E. GIF: 12-atom array, short pulse
n_anim = 12
fw_anim = 0.4 * fcen
aperture = n_anim * LA
sx_a = aperture + 2 * 1.0 + 2 * DPML
sy_a = DPML + DSUB + H + 2.5 + DPML
yb = -0.5 * sy_a
ydev = yb + DPML + DSUB
geom = [mp.Block(center=mp.Vector3(0, yb + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2)]
for j in range(n_anim):
    xj = -0.5 * aperture + (j + 0.5) * LA
    geom.append(mp.Block(center=mp.Vector3(xj, ydev + 0.5 * H), size=mp.Vector3(w_lib[j % N_SEC], H), material=Si))
sim_a = mp.Simulation(resolution=RES, cell_size=mp.Vector3(sx_a, sy_a), boundary_layers=[mp.PML(DPML)], geometry=geom,
                      sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fw_anim, is_integrated=True), component=mp.Ez,
                                         center=mp.Vector3(0, yb + DPML + 0.3), size=mp.Vector3(aperture, 0))])
sim_a.init_sim()
vol_a = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx_a - 2 * DPML, sy_a - 2 * DPML))
eps_a = sim_a.get_array(vol=vol_a, component=mp.Dielectric)
ext_a = [-(sx_a / 2 - DPML), sx_a / 2 - DPML, -(sy_a / 2 - DPML), sy_a / 2 - DPML]
t_src = 5 / fw_anim
frames, times = record_frames(sim_a, vol_a, mp.Ez, t_start=t_src - 1 / fw_anim, t_end=t_src + 1.2 * sy_a * 1.45, n_frames=60)
animate_fields(frames, times, ext_a, os.path.join(OUT, "06_anim_array.gif"), eps=eps_a, figsize=(6.0, 5.2), dpi=70,
               title=f"{n_anim}-atom array: wavefront leaves tilted toward +{THETA_D:.0f} deg", legend_loc="lower right")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"params": {"wl": wl, "La": LA, "Lambda": LAMBDA, "H": H, "theta_d_deg": THETA_D, "n_si": 3.45, "n_sio2": 1.45},
                   "library": {"widths": widths.tolist(), "amp40": amp40.tolist(), "phase40": ph40.tolist(), "amp60": amp60.tolist(),
                               "phase60": ph60.tolist(), "span40_over_2pi": span40 / (2 * np.pi), "max_dphi_60_40": float(np.max(np.abs(dphi)))},
                   "design": {"phi0": phi0, "targets": targets.tolist(), "widths": w_lib.tolist(), "amps": a_sel.tolist(), "min_amp": min_amp},
                   "supercell": {"orders": orders, "sum_orders": sum_orders, "T_total": T_total, "blazed_bound": BLAZED_BOUND,
                                 "plus1_over_bound": orders[1]["eff"] / BLAZED_BOUND},
                   "farfield": ff, "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
