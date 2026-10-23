"""Meep Example 08 - Metagrating inverse design (adjoint), with a four-step contract.

Start from the post-07 library design (four Si bars). Open the whole supercell period as a 1D design
region (73 pixels of density 0..1) and let the adjoint gradient move it. Every step is looked at:
  1. differentiability: eps_averaging=False, MaterialGrid do_averaging=False
  2. gradient gate: adjoint gradient vs centred finite differences along the gradient direction
  3. a short MMA run (maxeval 5): a smoke test, not a converged design
  4. verification in a FRESH simulation with DiffractedPlanewave, order by order
Plus: forward field of baseline and of a random start, adjoint field, raw gradient, one manual step.

Run:  python metagrating_inverse.py      (~1.5 min on one core)
Out:  00_source.png, 01_layout.png, 02_fields.png, 03_gradient.png, 04_gate.png, 05_step_mma.png,
      06_verify.png, 07_anim_optimized.gif, result.json   (-> ../assets/08/)
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
import meep.adjoint as mpa
import nlopt
from autograd import numpy as npa

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "08")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()
np.random.seed(20260815)

# ---------------------------------------------------------------- (1) units & parameters: identical to post 07
wl = 1.55
fcen = 1 / wl
fwidth = 0.1 * fcen
Si, SiO2 = mp.Medium(index=3.45), mp.Medium(index=1.45)
N_SEC, LA = 4, 0.45
LAMBDA = N_SEC * LA
THETA_D = float(np.degrees(np.arcsin(wl / LAMBDA)))
H = 0.9
RES = 40
DPML, DSUB, DAIR = 1.0, 1.0, 1.0
SY = DPML + DSUB + H + DAIR + DPML
Y_BOT = -0.5 * SY
Y_DEV = Y_BOT + DPML + DSUB
SRC_Y = Y_BOT + DPML + 0.3
MON_Y = -Y_BOT - DPML - 0.3
BLAZED_BOUND = (np.sin(np.pi / N_SEC) / (np.pi / N_SEC)) ** 2
EXTENT = [-0.5 * LAMBDA, 0.5 * LAMBDA, Y_BOT, -Y_BOT]

# baseline widths: post-07 library design (read from its result.json if present)
try:
    with open(os.path.join(HERE, "..", "assets", "07", "result.json")) as f:
        W_LIB = np.array(json.load(f)["design"]["widths"])
except Exception:
    W_LIB = np.array([0.075, 0.100, 0.175, 0.225])

sources = [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=mp.Vector3(0, SRC_Y), size=mp.Vector3(LAMBDA, 0))]
common = dict(resolution=RES, cell_size=mp.Vector3(LAMBDA, SY), sources=sources,
              boundary_layers=[mp.PML(thickness=DPML, direction=mp.Y)], k_point=mp.Vector3())
stop_cond = mp.stop_when_fields_decayed(10, mp.Ez, mp.Vector3(0, MON_Y), 1e-7)

# ---------------------------------------------------------------- (2) geometry: substrate + a 1D MaterialGrid design region
Nx, Ny = int(round(RES * LAMBDA)) + 1, 1
x_grid = np.linspace(-0.5 * LAMBDA, 0.5 * LAMBDA, Nx)
design_variables = mp.MaterialGrid(mp.Vector3(Nx, Ny), mp.air, Si, grid_type="U_MEAN", do_averaging=False)   # contract 1
design_region = mpa.DesignRegion(design_variables, volume=mp.Volume(center=mp.Vector3(0, Y_DEV + 0.5 * H), size=mp.Vector3(LAMBDA, H)))
x_baseline = np.zeros(Nx)
for j, w in enumerate(W_LIB):
    xj = -0.5 * LAMBDA + (j + 0.5) * LA
    x_baseline[np.abs(x_grid - xj) <= 0.5 * w] = 1.0


def geometry_with(weights):
    grid = mp.MaterialGrid(mp.Vector3(Nx, Ny), mp.air, Si, weights=np.asarray(weights).reshape(Nx, Ny), grid_type="U_MEAN", do_averaging=False)
    return [mp.Block(center=mp.Vector3(0, Y_BOT + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2),
            mp.Block(center=design_region.center, size=design_region.size, material=grid)]


geometry = [mp.Block(center=mp.Vector3(0, Y_BOT + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2),
            mp.Block(center=design_region.center, size=design_region.size, material=design_variables)]

# ---------------------------------------------------------------- (4) simulation + (5) objective: +1 order amplitude
sim = mp.Simulation(geometry=geometry, eps_averaging=False, **common)
kdiff = mp.Vector3(1 / LAMBDA, np.sqrt(fcen ** 2 - (1 / LAMBDA) ** 2))      # +1 order direction
emc = mpa.EigenmodeCoefficient(sim, mp.Volume(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0)), mode=1,
                               eig_parity=mp.ODD_Z, kpoint_func=lambda *_: kdiff,
                               eig_vol=mp.Volume(center=mp.Vector3(0, MON_Y), size=mp.Vector3(1 / RES, 0, 0)))
opt = mpa.OptimizationProblem(simulation=sim, objective_functions=lambda e: npa.abs(e[0]) ** 2, objective_arguments=[emc],
                              design_regions=[design_region], fcen=fcen, df=0, nf=1, decay_by=1e-6)
opt.update_design([x_baseline])
annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(5.2, 7.0), axis_step=0.5,
    title="supercell: 1D design region (73 px) replaces the bars",
    params_text=f"wl={wl} res={RES}\nLambda={LAMBDA} H={H}\nNx={Nx} (25 nm px)",
    params_xy=(-0.85, 2.35), pml_xy=(-0.5, Y_BOT + 0.5 * DPML), decay_point=(0, MON_Y), decay_text_xy=(-0.1, 1.75),
    labels=[Label("design region: MaterialGrid, baseline = library bars", (-0.3, Y_DEV + 0.5 * H), (-0.85, 1.25), step=2, color="black"),
            Label("plane wave in SiO2", (0.3, SRC_Y), (-0.85, SRC_Y - 0.35), step=3, color="red"),
            Label("objective: |a_+1|^2 on this line", (0.5, MON_Y), (-0.85, MON_Y + 0.35), step=5, color="blue")])
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")


def run_dft_field(src_list, geometry_list):
    s = mp.Simulation(geometry=geometry_list, eps_averaging=False, **dict(common, sources=src_list))
    dft = s.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(LAMBDA, SY))
    s.run(until_after_sources=stop_cond)
    field = s.get_dft_array(dft, mp.Ez, 0); eps = s.get_epsilon(); s.reset_meep()
    return field, eps


# ---------------------------------------------------------------- source check + input flux (empty substrate)
sim_ref = mp.Simulation(default_material=SiO2, **common)
fl = sim_ref.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0)))
dft_ref = sim_ref.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(LAMBDA, SY))
sim_ref.run(until_after_sources=stop_cond)
input_flux = float(mp.get_fluxes(fl)[0])
field_ref = sim_ref.get_dft_array(dft_ref, mp.Ez, 0)
sim_ref.reset_meep()
row = field_ref[:, field_ref.shape[1] // 2]
phase_spread = float(np.ptp(np.unwrap(np.angle(row))))
print(f"source check: input_flux = {input_flux:.5e}, phase spread across x at mid-height = {phase_spread:.4f} rad ({'normal incidence' if phase_spread < 0.2 else 'TILTED'})")


def fom(x, need_gradient=False):
    """+1 order efficiency = |a_+1|^2 / input_flux (and its gradient w.r.t. the 73 densities)."""
    f, dJ = opt([np.clip(x, 0, 1)], need_gradient=need_gradient)
    f = float(np.real(np.asarray(f).squeeze())) / input_flux
    if not need_gradient:
        return f
    return f, np.squeeze(np.asarray(dJ)) / input_flux


# ---------------------------------------------------------------- forward fields: baseline vs random start; adjoint field
field_fwd, eps_fwd = run_dft_field(sources, geometry_with(x_baseline))
f_baseline, g_baseline = fom(x_baseline, need_gradient=True)
x_random = np.random.rand(Nx)
field_rand, eps_rand = run_dft_field(sources, geometry_with(x_random))
f_random = fom(x_random)
adjoint_sources = opt.adjoint_sources[0]
field_adj, eps_adj = run_dft_field(adjoint_sources, geometry_with(x_baseline))
print(f"forward: baseline +1 efficiency = {f_baseline:.4f} (|grad| = {np.linalg.norm(g_baseline):.3e}); random grayscale start = {f_random:.4f}; "
      f"adjoint sources: {len(adjoint_sources)} x {type(adjoint_sources[0]).__name__}")

xs = np.linspace(EXTENT[0], EXTENT[1], eps_fwd.shape[0]); ys = np.linspace(EXTENT[2], EXTENT[3], eps_fwd.shape[1])
fig, ax = plt.subplots(2, 3, figsize=(10.5, 7.2))
lim = max(np.max(np.abs(field_fwd)), np.max(np.abs(field_rand)))
for col, (fld, eps, ttl) in enumerate(((field_fwd, eps_fwd, f"forward, baseline (library bars)  J = {f_baseline:.3f}"),
                                       (field_rand, eps_rand, f"forward, random grayscale start  J = {f_random:.3f}"),
                                       (field_adj, eps_adj, "adjoint: source placed at the objective monitor"))):
    l = lim if col < 2 else float(np.max(np.abs(fld)))
    ax[0, col].imshow(np.real(fld).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-l, vmax=l, aspect="equal")
    ax[1, col].imshow(np.abs(fld).T, extent=EXTENT, origin="lower", cmap="inferno", aspect="equal")
    for a in ax[:, col]:
        a.contour(xs, ys, eps.T, levels=[1.5, 6.0], colors="w", linewidths=0.6); a.set_xlabel("x [um]")
    ax[0, col].set_title(ttl, fontsize=8.5)
ax[0, 0].set_ylabel("Re(Ez)  y [um]"); ax[1, 0].set_ylabel("|Ez|  y [um]")
fig.suptitle("the field follows the design; the adjoint field flows from the monitor back down", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_fields.png"), dpi=150); plt.close(fig)

# ---------------------------------------------------------------- raw gradient
fig, ax = plt.subplots(2, 1, figsize=(9, 4.8), sharex=True)
ax[0].plot(x_grid, g_baseline, lw=1.2, color="tab:purple"); ax[0].axhline(0, color="k", lw=0.7)
ax[0].fill_between(x_grid, 0, g_baseline, where=g_baseline > 0, color="tab:red", alpha=0.25, label="increase density here")
ax[0].fill_between(x_grid, 0, g_baseline, where=g_baseline < 0, color="tab:blue", alpha=0.25, label="decrease density here")
ax[0].set_ylabel("dJ / d(density)"); ax[0].set_title("raw adjoint gradient at the baseline (no filtering)", fontsize=9); ax[0].legend(fontsize=8, loc="upper right")
ax[1].step(x_grid, x_baseline, where="mid", color="tab:gray", lw=1.3); ax[1].fill_between(x_grid, 0, x_baseline, step="mid", color="tab:gray", alpha=0.35)
ax[1].set_ylabel("density (0 = air, 1 = Si)"); ax[1].set_xlabel("x [um]"); ax[1].set_ylim(-0.05, 1.15); ax[1].set_title("current design", fontsize=9)
for a in ax:
    for j in range(1, N_SEC):
        a.axvline(-0.5 * LAMBDA + j * LA, color="k", ls=":", lw=0.8)
    a.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_gradient.png"), dpi=150); plt.close(fig)
top = sorted(np.argsort(np.abs(g_baseline))[::-1][:5])
print("gradient: largest 5 |dJ/drho| at x = " + ", ".join(f"{x_grid[i]:+.3f} ({g_baseline[i]:+.3f}, rho={x_baseline[i]:.0f})" for i in top))

# ---------------------------------------------------------------- contract 2: gradient gate (interior point, gradient direction)
x_gate = np.clip(x_baseline, 0.02, 0.98)
f_gate, g_gate = fom(x_gate, need_gradient=True)
v = g_gate / np.linalg.norm(g_gate)
adjoint_dd = float(np.dot(g_gate, v))
steps = [2e-3, 5e-3, 1e-2]
gate_rows = []
for step in steps:
    fd = (fom(x_gate + step * v) - fom(x_gate - step * v)) / (2 * step)
    rel = abs(adjoint_dd - fd) / max(abs(fd), 1e-30)
    gate_rows.append({"step": step, "fd": fd, "adjoint": adjoint_dd, "rel_err": rel, "pass": bool(rel <= 0.20 and np.sign(fd) == np.sign(adjoint_dd))})
gradient_gate = all(r["pass"] for r in gate_rows)
print(f"gate: interior-point FOM = {f_gate:.4f}; " + "; ".join(f"step {r['step']:.0e}: FD {r['fd']:.4e} vs adjoint {r['adjoint']:.4e}, rel {r['rel_err']:.4f} {'PASS' if r['pass'] else 'HOLD'}" for r in gate_rows)
      + f" -> gradient gate {'PASS' if gradient_gate else 'HOLD'}")
fig, ax = plt.subplots(1, 2, figsize=(10, 3.4))
idx = np.arange(len(steps))
ax[0].bar(idx - 0.2, [r["fd"] for r in gate_rows], width=0.4, color="tab:orange", label="centred finite difference")
ax[0].bar(idx + 0.2, [adjoint_dd] * 3, width=0.4, color="tab:blue", label="adjoint  g . v")
ax[0].set_xticks(idx); ax[0].set_xticklabels([f"{s:.0e}" for s in steps]); ax[0].set_xlabel("finite-difference step"); ax[0].set_ylabel("directional derivative")
ax[0].set_title("adjoint vs finite difference along the gradient direction", fontsize=9); ax[0].grid(axis="y", alpha=0.3); ax[0].legend(fontsize=8)
bars = ax[1].bar(idx, [r["rel_err"] for r in gate_rows], color=["tab:green" if r["pass"] else "tab:red" for r in gate_rows])
ax[1].axhline(0.20, ls="--", color="crimson", lw=1.2, label="gate: 20 %")
for b, r in zip(bars, gate_rows):
    ax[1].text(b.get_x() + b.get_width() / 2, r["rel_err"] + 0.004, f"{r['rel_err']:.4f}", ha="center", fontsize=8)
ax[1].set_xticks(idx); ax[1].set_xticklabels([f"{s:.0e}" for s in steps]); ax[1].set_ylim(0, 0.25); ax[1].set_ylabel("relative error")
ax[1].set_title(f"gradient gate: {'PASS' if gradient_gate else 'HOLD'}", fontsize=9); ax[1].grid(axis="y", alpha=0.3); ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_gate.png"), dpi=150); plt.close(fig)
if not gradient_gate:
    raise SystemExit("gradient gate HOLD: do not interpret optimizer results")

# ---------------------------------------------------------------- one manual step, then MMA (contract 3)
direction = g_baseline / np.linalg.norm(g_baseline)
one_step = []
for alpha in (0.05, 0.3, 0.8, 2.0):
    x_try = np.clip(x_baseline + alpha * direction, 0, 1)
    one_step.append((alpha, x_try, fom(x_try)))
print("one manual step: " + ", ".join(f"alpha {a} -> {f:.4f} ({f - f_baseline:+.4f})" for a, _, f in one_step))

history, design_history = [], []


def nlopt_objective(x, grad):
    f, dJ = fom(x, need_gradient=True)
    if grad.size > 0:
        grad[:] = dJ
    history.append(f); design_history.append(np.array(x, copy=True))
    return f


solver = nlopt.opt(nlopt.LD_MMA, Nx)
solver.set_lower_bounds(np.zeros(Nx)); solver.set_upper_bounds(np.ones(Nx))
solver.set_max_objective(nlopt_objective); solver.set_maxeval(5)
x_optimized = np.clip(solver.optimize(x_baseline.copy()), 0, 1)
best_k = int(np.argmax(history))
x_optimized = design_history[best_k]                         # keep the best evaluated design (MMA may overshoot)
gray = int(np.sum((x_optimized > 0.02) & (x_optimized < 0.98)))
print("MMA (maxeval 5): " + ", ".join(f"eval {k+1}: {f:.4f}" for k, f in enumerate(history)) + f"; best eval {best_k+1} = {max(history):.4f} ({max(history)/history[0]:.3f}x); grayscale pixels {gray}/{Nx}")

fig = plt.figure(figsize=(14, 6.2))
gs = fig.add_gridspec(2, 6, height_ratios=[1, 1])
axs = [fig.add_subplot(gs[0, k]) for k in range(5)]
axs[0].step(x_grid, x_baseline, where="mid", color="tab:gray", lw=1.1); axs[0].fill_between(x_grid, 0, x_baseline, step="mid", color="tab:gray", alpha=0.4)
axs[0].set_title(f"baseline\nJ = {f_baseline:.4f}", fontsize=8); axs[0].set_ylabel("density")
for a, (alpha, x_try, f_try) in zip(axs[1:], one_step):
    a.step(x_grid, x_try, where="mid", color="tab:green", lw=1.1); a.fill_between(x_grid, 0, x_try, step="mid", color="tab:green", alpha=0.4)
    a.set_title(f"one step, alpha = {alpha}\nJ = {f_try:.4f}", fontsize=8)
for a in axs:
    a.set_ylim(-0.05, 1.08); a.set_xlabel("x [um]"); a.grid(alpha=0.3)
axh = fig.add_subplot(gs[0, 5])
axh.plot(range(1, len(history) + 1), history, "o-", color="tab:blue"); axh.axhline(f_baseline, ls="--", color="gray", lw=1, label="baseline")
axh.set_xticks(range(1, len(history) + 1)); axh.set_xlabel("MMA evaluation"); axh.set_ylabel("+1 efficiency"); axh.set_title("MMA history", fontsize=8); axh.grid(alpha=0.3); axh.legend(fontsize=7)
for k in range(len(design_history)):
    a = fig.add_subplot(gs[1, k])
    a.step(x_grid, design_history[k], where="mid", color="tab:blue", lw=1.0); a.fill_between(x_grid, 0, design_history[k], step="mid", color="tab:blue", alpha=0.4)
    a.set_title(f"MMA eval {k + 1}  J = {history[k]:.4f}" + ("  (kept)" if k == best_k else ""), fontsize=8); a.set_ylim(-0.05, 1.08); a.set_xlabel("x [um]"); a.grid(alpha=0.3)
    if k == 0:
        a.set_ylabel("density")
a = fig.add_subplot(gs[1, 5])
a.step(x_grid, x_baseline, where="mid", color="tab:gray", lw=1.2, label="baseline"); a.step(x_grid, x_optimized, where="mid", color="tab:blue", lw=1.2, label="optimized")
a.fill_between(x_grid, 0, x_optimized, step="mid", color="tab:blue", alpha=0.3); a.set_ylim(-0.05, 1.08); a.set_xlabel("x [um]"); a.set_title(f"final vs baseline ({gray} gray px)", fontsize=8); a.legend(fontsize=7); a.grid(alpha=0.3)
fig.suptitle("top: one manual gradient step (alpha sweep) and the MMA history; bottom: the design at every MMA evaluation", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_step_mma.png"), dpi=150); plt.close(fig)


# ---------------------------------------------------------------- contract 4: verification in a fresh simulation
def forward_orders(weights):
    s = mp.Simulation(geometry=geometry_with(weights), eps_averaging=False, **common)
    mon = s.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0)))
    dft = s.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(LAMBDA, SY))
    s.run(until_after_sources=stop_cond)
    total = float(mp.get_fluxes(mon)[0] / input_flux)
    eff = {m: float(abs(s.get_eigenmode_coefficients(mon, mp.DiffractedPlanewave((m, 0, 0), mp.Vector3(1, 0, 0), 1, 0)).alpha[0, 0, 0]) ** 2 / input_flux) for m in (-1, 0, 1)}
    field = s.get_dft_array(dft, mp.Ez, 0); eps = s.get_epsilon(); s.reset_meep()
    return eff, total, field, eps


report = {}
for tag, weights in (("baseline", x_baseline), ("optimized", x_optimized)):
    eff, total, fld, eps = forward_orders(weights)
    report[tag] = {"orders": eff, "sum": sum(eff.values()), "T_total": total, "field": fld, "eps": eps}
    print(f"verify [{tag}]: m=-1 {eff[-1]:.4f}, m=0 {eff[0]:.4f}, m=+1 {eff[1]:.4f}; sum {sum(eff.values()):.4f} = total {total:.4f}; "
          f"+1 / bound = {eff[1] / BLAZED_BOUND * 100:.1f} %")
fig, ax = plt.subplots(1, 3, figsize=(13, 4.4), gridspec_kw={"width_ratios": [1.4, 1, 1]})
ms = (-1, 0, 1); idx = np.arange(3)
ax[0].bar(idx - 0.2, [report["baseline"]["orders"][m] for m in ms], width=0.4, color="tab:gray", label="baseline (post-07 library)")
ax[0].bar(idx + 0.2, [report["optimized"]["orders"][m] for m in ms], width=0.4, color="tab:blue", label=f"after MMA (eval {best_k + 1})")
ax[0].axhline(BLAZED_BOUND, ls="--", color="crimson", lw=1.2, label=f"4-level blazed bound {BLAZED_BOUND:.3f}")
for k, m in enumerate(ms):
    ax[0].text(k - 0.2, report["baseline"]["orders"][m] + 0.008, f"{report['baseline']['orders'][m]:.3f}", ha="center", fontsize=8)
    ax[0].text(k + 0.2, report["optimized"]["orders"][m] + 0.008, f"{report['optimized']['orders'][m]:.3f}", ha="center", fontsize=8)
ax[0].set_xticks(idx); ax[0].set_xticklabels([f"m = {m:+d}" for m in ms]); ax[0].set_ylim(0, 1.0); ax[0].set_ylabel("efficiency (fresh forward run)")
ax[0].set_title("contract 4: measured again in a new simulation", fontsize=9); ax[0].grid(axis="y", alpha=0.3); ax[0].legend(fontsize=7)
lim = max(np.max(np.abs(report["baseline"]["field"])), np.max(np.abs(report["optimized"]["field"])))
for a, tag in zip(ax[1:], ("baseline", "optimized")):
    fld, eps = report[tag]["field"], report[tag]["eps"]
    a.imshow(np.real(fld).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
    a.contour(xs, ys, eps.T, levels=[1.5, 6.0], colors="w", linewidths=0.6); a.set_title(f"Re(Ez), {tag}", fontsize=9); a.set_xlabel("x [um]")
ax[1].set_ylabel("y [um]")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "06_verify.png"), dpi=150); plt.close(fig)

# ---------------------------------------------------------------- GIF: optimized pattern repeated 5 times, short pulse
periods = 5
fw_anim = 0.4 * fcen
aperture = periods * LAMBDA
sx_a = aperture + 2 * 1.0 + 2 * DPML
sy_a = DPML + DSUB + H + 2.5 + DPML
yb = -0.5 * sy_a
ydev = yb + DPML + DSUB
geom_a = [mp.Block(center=mp.Vector3(0, yb + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2)]
for j in range(periods):
    xj = -0.5 * aperture + (j + 0.5) * LAMBDA
    geom_a.append(mp.Block(center=mp.Vector3(xj, ydev + 0.5 * H), size=mp.Vector3(LAMBDA, H),
                           material=mp.MaterialGrid(mp.Vector3(Nx, Ny), mp.air, Si, weights=x_optimized.reshape(Nx, Ny), grid_type="U_MEAN", do_averaging=False)))
sim_a = mp.Simulation(resolution=RES, cell_size=mp.Vector3(sx_a, sy_a), boundary_layers=[mp.PML(DPML)], geometry=geom_a, eps_averaging=False,
                      sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fw_anim, is_integrated=True), component=mp.Ez,
                                         center=mp.Vector3(0, yb + DPML + 0.3), size=mp.Vector3(aperture, 0))])
sim_a.init_sim()
vol_a = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx_a - 2 * DPML, sy_a - 2 * DPML))
eps_a = sim_a.get_array(vol=vol_a, component=mp.Dielectric)
ext_a = [-(sx_a / 2 - DPML), sx_a / 2 - DPML, -(sy_a / 2 - DPML), sy_a / 2 - DPML]
t_src = 5 / fw_anim
frames, times = record_frames(sim_a, vol_a, mp.Ez, t_start=t_src - 1 / fw_anim, t_end=t_src + 1.2 * sy_a * 1.45, n_frames=60)
animate_fields(frames, times, ext_a, os.path.join(OUT, "07_anim_optimized.gif"), eps=eps_a, figsize=(6.4, 4.6), dpi=70,
               title=f"optimized metagrating x{periods}: wavefront toward +{THETA_D:.0f} deg", legend_loc="lower right")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"params": {"wl": wl, "Lambda": LAMBDA, "H": H, "theta_d": THETA_D, "Nx": Nx, "w_lib": W_LIB.tolist()},
                   "input_flux": input_flux, "phase_spread": phase_spread,
                   "fom": {"baseline": f_baseline, "random": f_random, "gate_point": f_gate},
                   "gate": gate_rows, "gate_pass": gradient_gate,
                   "one_step": [{"alpha": a, "fom": f} for a, _, f in one_step],
                   "mma": {"history": history, "best_eval": best_k + 1, "gray_pixels": gray},
                   "verify": {k: {"orders": v["orders"], "sum": v["sum"], "T_total": v["T_total"]} for k, v in report.items()},
                   "blazed_bound": BLAZED_BOUND, "x_baseline": x_baseline.tolist(), "x_optimized": x_optimized.tolist(),
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__, "nlopt": f"{nlopt.version_major()}.{nlopt.version_minor()}"}, f, indent=2)
