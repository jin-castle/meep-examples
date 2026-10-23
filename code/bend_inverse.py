"""Meep Example 09 - Waveguide bend inverse design (adjoint), with the same four-step contract as post 08.

Post 05 turned a 90-degree bend with ONE design variable (the radius). Here the corner is a 1 x 1 um square
opened as a free design region (11 x 11 densities, SiO2..Si) and the adjoint gradient fills it. Only the
objective changes: not a diffraction order but the guided mode-1 power at the output port.
  1. differentiability: eps_averaging=False, MaterialGrid do_averaging=False
  2. gradient gate: adjoint gradient vs centred finite differences along the gradient direction (interior point)
  3. a short MMA run (maxeval 5): a smoke test, not a converged design
  4. verification in a FRESH simulation with get_eigenmode_coefficients, normalized by the input mode-1 power
Plus: source check on a straight waveguide, forward field of uniform and random starts, adjoint field,
raw gradient, one manual step, a resolution check of the final design, two GIFs.

Run:  python bend_inverse.py      (~1 min on one core)
Out:  00_source.png, 01_layout.png, 02_source_check.png, 03_fields.png, 04_gradient.png, 05_gate.png,
      06_step_mma.png, 07_verify.png, 08_anim_optimized.gif, 09_anim_design.gif, result.json  (-> ../assets/09/)
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
import meep.adjoint as mpa
import nlopt
from autograd import numpy as npa

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "09")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()
np.random.seed(20260820)

# ---------------------------------------------------------------- (1) units & parameters (course week 10)
wl = 1.55
fcen = 1 / wl
fwidth = 0.12 * fcen
Si, SiO2 = mp.Medium(index=3.4), mp.Medium(index=1.44)
RES = 10
SX, SY = 6.0, 5.0
DPML = 1.0
W = 0.5                                   # waveguide width
SRC_X, SRC_SIZE = -1.5, 2.0               # EigenModeSource on the input waveguide
MON_IN_X = -1.0                           # input-power monitor (between source and design region)
MON_OUT_Y = 1.0                           # objective monitor on the output waveguide
D = 1.0                                   # design region side
NX = NY = 11                              # design grid: 11 x 11 = 121 densities
EXTENT = [-0.5 * SX, 0.5 * SX, -0.5 * SY, 0.5 * SY]
DEXT = [-0.5 * D, 0.5 * D, -0.5 * D, 0.5 * D]

sources = [mp.EigenModeSource(mp.GaussianSource(fcen, fwidth=fwidth), eig_band=1, direction=mp.NO_DIRECTION,
                              eig_kpoint=mp.Vector3(1, 0, 0), size=mp.Vector3(0, SRC_SIZE), center=mp.Vector3(SRC_X, 0))]
common = dict(resolution=RES, cell_size=mp.Vector3(SX, SY), boundary_layers=[mp.PML(DPML)], sources=sources, eps_averaging=False)
stop_cond = mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(0, MON_OUT_Y), 1e-5)


# ---------------------------------------------------------------- (2) geometry: input (-x) and output (+y) waveguides + design square
def waveguide_blocks():
    return [mp.Block(center=mp.Vector3(-SX / 4, 0), size=mp.Vector3(SX / 2, W), material=Si),
            mp.Block(center=mp.Vector3(0, SY / 4), size=mp.Vector3(W, SY / 2), material=Si)]


def geometry_with(weights):
    grid = mp.MaterialGrid(mp.Vector3(NX, NY), SiO2, Si, weights=np.asarray(weights).reshape(NX, NY), grid_type="U_MEAN", do_averaging=False)
    return waveguide_blocks() + [mp.Block(center=mp.Vector3(), size=mp.Vector3(D, D), material=grid)]


design_variables = mp.MaterialGrid(mp.Vector3(NX, NY), SiO2, Si, grid_type="U_MEAN", do_averaging=False)     # contract 1
design_region = mpa.DesignRegion(design_variables, volume=mp.Volume(center=mp.Vector3(), size=mp.Vector3(D, D)))
geometry = waveguide_blocks() + [mp.Block(center=design_region.center, size=design_region.size, material=design_variables)]

# ---------------------------------------------------------------- (4) simulation + (5) objective: output-port mode-1 power
sim = mp.Simulation(geometry=geometry, **common)
out_mode = mpa.EigenmodeCoefficient(sim, mp.Volume(center=mp.Vector3(0, MON_OUT_Y), size=mp.Vector3(2, 0)), mode=1)
opt = mpa.OptimizationProblem(simulation=sim, objective_functions=lambda a: npa.abs(a) ** 2, objective_arguments=[out_mode],
                              design_regions=[design_region], fcen=fcen, df=0, nf=1)
x_start = 0.5 * np.ones(NX * NY)          # uniform grey: an interior point, differentiable, no bias
opt.update_design([x_start])
# a throw-away copy only for the layout figure: plot2D draws flux monitors, mpa objectives it does not
sim_plot = mp.Simulation(geometry=geometry_with(x_start), **common)
sim_plot.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(0, MON_OUT_Y), size=mp.Vector3(2, 0)))
sim_plot.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(MON_IN_X, 0), size=mp.Vector3(0, 2)))
annotated_layout(
    sim_plot, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(7.4, 6.0), axis_step=1.0,
    title="bend as a free design region: input -x, output +y, 1 x 1 um square of 11 x 11 densities",
    params_text=f"wl={wl} res={RES}\ncell {SX}x{SY}, w={W}\nNx=Ny={NX} (121 vars)",
    params_xy=(-2.9, 2.3), pml_xy=(-2.5, -0.5 * SY + 0.5 * DPML), decay_point=(0, MON_OUT_Y), decay_text_xy=(0.9, 1.75),
    labels=[Label("design region: MaterialGrid, start = uniform 0.5", (-0.5, -0.5), (-2.9, -1.3), step=2, color="black"),
            Label("EigenModeSource, mode 1 -> +x", (SRC_X, 0.6), (-2.9, 1.3), step=3, color="red"),
            Label("objective: |a_out|^2 on this line", (0.8, MON_OUT_Y), (0.9, 0.5), step=5, color="blue"),
            Label("input monitor (normalization)", (MON_IN_X, -0.8), (-0.2, -2.0), step=5, color="blue")])
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")


def run_dft_field(src_list, geometry_list):
    s = mp.Simulation(geometry=geometry_list, **dict(common, sources=src_list))
    dft = s.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(SX, SY))
    s.run(until_after_sources=stop_cond)
    field = s.get_dft_array(dft, mp.Ez, 0); eps = s.get_epsilon(); s.reset_meep()
    return field, eps


def contour(a, eps):
    xs = np.linspace(EXTENT[0], EXTENT[1], eps.shape[0]); ys = np.linspace(EXTENT[2], EXTENT[3], eps.shape[1])
    a.contour(xs, ys, eps.T, levels=[0.5 * (1.44 ** 2 + 3.4 ** 2)], colors="w", linewidths=0.6, alpha=0.9)


def show_design(a, weights, title):
    im = a.imshow(np.asarray(weights).reshape(NX, NY).T, origin="lower", extent=DEXT, cmap="gray_r", vmin=0, vmax=1, aspect="equal")
    a.set_title(title, fontsize=8); a.set_xlabel("x [um]")
    return im


# ---------------------------------------------------------------- source check: straight waveguide, mode-1 share at the input monitor
straight = [mp.Block(center=mp.Vector3(), size=mp.Vector3(mp.inf, W), material=Si)]
field_src, eps_src = run_dft_field(sources, straight)
s_in = mp.Simulation(geometry=straight, **common)
mon_in = s_in.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(MON_IN_X, 0), size=mp.Vector3(0, 2)))
s_in.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(MON_IN_X, 0), 1e-5))
total_in = float(mp.get_fluxes(mon_in)[0])
input_power = float(abs(s_in.get_eigenmode_coefficients(mon_in, [1], direction=mp.X).alpha[0, 0, 0]) ** 2)
s_in.reset_meep()
print(f"source check: input flux {total_in:.5e}, mode-1 power {input_power:.5e}, mode-1 share {input_power / total_in:.4f}")
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
lim = float(np.max(np.abs(field_src)))
ax[0].imshow(np.real(field_src).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal"); ax[0].set_title("Re(Ez): wavefront", fontsize=9)
ax[1].imshow(np.abs(field_src).T, extent=EXTENT, origin="lower", cmap="inferno", aspect="equal"); ax[1].set_title("|Ez|: envelope", fontsize=9)
for a in ax:
    contour(a, eps_src); a.axvline(SRC_X, color="red", lw=1.2, ls="--"); a.axvline(MON_IN_X, color="blue", lw=1.2, ls=":"); a.set_xlabel("x [um]")
ax[0].set_ylabel("y [um]")
fig.suptitle(f"source check on a straight waveguide: mode-1 share at x = {MON_IN_X} um is {input_power / total_in:.4f}", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_source_check.png"), dpi=150); plt.close(fig)


def fom(x, need_gradient=False):
    """Objective = output-port mode-1 power |a_out|^2 in optimizer units (NOT normalized; see contract 4)."""
    f, dJ = opt([np.clip(x, 0, 1)], need_gradient=need_gradient)
    f = float(np.real(np.asarray(f).squeeze()))
    if not need_gradient:
        return f
    return f, np.squeeze(np.asarray(dJ))


# ---------------------------------------------------------------- forward fields: uniform vs random start; adjoint field
field_fwd, eps_fwd = run_dft_field(sources, geometry_with(x_start))
f_start, g_start = fom(x_start, need_gradient=True)
x_random = np.random.rand(NX * NY)
field_rand, eps_rand = run_dft_field(sources, geometry_with(x_random))
f_random = fom(x_random)
adjoint_sources = opt.adjoint_sources[0]
field_adj, eps_adj = run_dft_field(adjoint_sources, geometry_with(x_start))
print(f"forward: uniform-0.5 FOM = {f_start:.4f} (|grad| = {np.linalg.norm(g_start):.3e}); random start FOM = {f_random:.4f}; "
      f"adjoint sources: {len(adjoint_sources)} x {type(adjoint_sources[0]).__name__}")

fig, ax = plt.subplots(2, 4, figsize=(13, 6.4), gridspec_kw={"width_ratios": [0.55, 1, 1, 1]})
lim = max(np.max(np.abs(field_fwd)), np.max(np.abs(field_rand)))
for r, (weights, fld, eps, tag, val) in enumerate(((x_start, field_fwd, eps_fwd, "uniform 0.5", f_start), (x_random, field_rand, eps_rand, "random seed", f_random))):
    show_design(ax[r, 0], weights, f"design: {tag}\nFOM = {val:.3f}"); ax[r, 0].set_ylabel("y [um]")
    ax[r, 1].imshow(np.real(fld).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal"); ax[r, 1].set_title("forward Re(Ez)", fontsize=9)
    ax[r, 2].imshow(np.abs(fld).T, extent=EXTENT, origin="lower", cmap="inferno", aspect="equal"); ax[r, 2].set_title("forward |Ez|", fontsize=9)
    for a in ax[r, 1:3]:
        contour(a, eps); a.set_xlabel("x [um]")
la = float(np.max(np.abs(field_adj)))
ax[0, 3].imshow(np.real(field_adj).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-la, vmax=la, aspect="equal"); ax[0, 3].set_title("adjoint Re(Ez) (source at the output port)", fontsize=9)
ax[1, 3].imshow(np.abs(field_adj).T, extent=EXTENT, origin="lower", cmap="inferno", aspect="equal"); ax[1, 3].set_title("adjoint |Ez|", fontsize=9)
for a in ax[:, 3]:
    contour(a, eps_adj); a.set_xlabel("x [um]")
fig.suptitle("rows: uniform vs random start (forward); right column: the adjoint field of the uniform start", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_fields.png"), dpi=150); plt.close(fig)

# ---------------------------------------------------------------- raw gradient on the 11 x 11 grid
g2 = g_start.reshape(NX, NY)
lim = float(np.max(np.abs(g2)))
fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
im0 = show_design(ax[0], x_start, "current design (uniform 0.5)"); plt.colorbar(im0, ax=ax[0], fraction=0.046)
im1 = ax[1].imshow(g2.T, origin="lower", extent=DEXT, cmap="RdBu_r", vmin=-lim, vmax=lim, aspect="equal"); ax[1].set_title("raw adjoint gradient dJ/d(density)\nred: more Si helps, blue: more SiO2 helps", fontsize=8); plt.colorbar(im1, ax=ax[1], fraction=0.046)
im2 = ax[2].imshow(np.abs(g2).T, origin="lower", extent=DEXT, cmap="viridis", aspect="equal"); ax[2].set_title("|gradient|: where the design matters most", fontsize=8); plt.colorbar(im2, ax=ax[2], fraction=0.046)
for a in ax[1:]:
    a.set_xlabel("x [um]")
ax[0].set_ylabel("y [um]")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_gradient.png"), dpi=150); plt.close(fig)
print(f"gradient: max {g2.max():+.4e}, min {g2.min():+.4e}; positive pixels {int((g2 > 0).sum())}, negative {int((g2 < 0).sum())}")

# ---------------------------------------------------------------- contract 2: gradient gate (uniform 0.5 is already an interior point)
assert np.all((x_start > 0.02) & (x_start < 0.98))
v = g_start / np.linalg.norm(g_start)
adjoint_dd = float(np.dot(g_start, v))
steps = [2e-3, 5e-3, 1e-2]
gate_rows = []
for step in steps:
    fd = (fom(x_start + step * v) - fom(x_start - step * v)) / (2 * step)
    rel = abs(adjoint_dd - fd) / max(abs(fd), 1e-30)
    gate_rows.append({"step": step, "fd": fd, "adjoint": adjoint_dd, "rel_err": rel, "pass": bool(rel <= 0.20 and np.sign(fd) == np.sign(adjoint_dd))})
gradient_gate = all(r["pass"] for r in gate_rows)
print("gate: " + "; ".join(f"step {r['step']:.0e}: FD {r['fd']:.5e} vs adjoint {r['adjoint']:.5e}, rel {r['rel_err']:.4f} {'PASS' if r['pass'] else 'HOLD'}" for r in gate_rows)
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
fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_gate.png"), dpi=150); plt.close(fig)
if not gradient_gate:
    raise SystemExit("gradient gate HOLD: do not interpret optimizer results")

# ---------------------------------------------------------------- one manual step, then MMA (contract 3)
one_step = []
for alpha in (0.2, 1.0, 3.0, 8.0):
    x_try = np.clip(x_start + alpha * v, 0, 1)
    one_step.append((alpha, x_try, fom(x_try)))
print("one manual step: " + ", ".join(f"alpha {a} -> {f:.3f} ({f / f_start:.1f}x)" for a, _, f in one_step))

history, design_history = [], []


def nlopt_objective(x, grad):
    f, dJ = fom(x, need_gradient=True)
    if grad.size > 0:
        grad[:] = dJ
    history.append(f); design_history.append(np.array(x, copy=True))
    return f


solver = nlopt.opt(nlopt.LD_MMA, NX * NY)
solver.set_lower_bounds(np.zeros(NX * NY)); solver.set_upper_bounds(np.ones(NX * NY))
solver.set_max_objective(nlopt_objective); solver.set_maxeval(5)
solver.optimize(x_start.copy())
best_k = int(np.argmax(history))
x_optimized = design_history[best_k]                          # keep the best evaluated design (MMA may overshoot)
gray = int(np.sum((x_optimized > 0.02) & (x_optimized < 0.98)))
print("MMA (maxeval 5): " + ", ".join(f"eval {k + 1}: {f:.3f}" for k, f in enumerate(history)) + f"; best eval {best_k + 1} = {max(history):.3f} ({max(history) / history[0]:.1f}x); grayscale pixels {gray}/{NX * NY}")

fig, ax = plt.subplots(2, 6, figsize=(14, 5.6))
show_design(ax[0, 0], x_start, f"start (uniform 0.5)\nFOM {f_start:.2f}"); ax[0, 0].set_ylabel("y [um]")
for a, (alpha, x_try, f_try) in zip(ax[0, 1:5], one_step):
    show_design(a, x_try, f"one step, alpha = {alpha}\nFOM {f_try:.1f}")
ax[0, 5].plot(range(1, len(history) + 1), history, "o-", color="tab:blue"); ax[0, 5].axhline(f_start, ls="--", color="gray", lw=1, label="uniform start")
ax[0, 5].set_xticks(range(1, len(history) + 1)); ax[0, 5].set_xlabel("MMA evaluation"); ax[0, 5].set_ylabel("|a_out|^2 (optimizer units)"); ax[0, 5].set_title("MMA history", fontsize=8); ax[0, 5].grid(alpha=0.3); ax[0, 5].legend(fontsize=7)
for k in range(5):
    show_design(ax[1, k], design_history[k], f"MMA eval {k + 1}  FOM {history[k]:.1f}" + ("  (kept)" if k == best_k else ""))
ax[1, 0].set_ylabel("y [um]")
show_design(ax[1, 5], x_optimized, f"optimized (eval {best_k + 1})\n{gray} grey px of {NX * NY}")
fig.suptitle("top: one manual gradient step (alpha sweep) and the MMA history; bottom: the design at every MMA evaluation", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "06_step_mma.png"), dpi=150); plt.close(fig)


# ---------------------------------------------------------------- contract 4: fresh simulation, modal power / input mode-1 power
def modal_power(weights, res=RES):
    s = mp.Simulation(geometry=geometry_with(weights), **dict(common, resolution=res))
    mon = s.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(0, MON_OUT_Y), size=mp.Vector3(2, 0)))
    dft = s.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(SX, SY))
    s.run(until_after_sources=stop_cond)
    total = float(mp.get_fluxes(mon)[0])
    mode1 = float(abs(s.get_eigenmode_coefficients(mon, [1], direction=mp.Y).alpha[0, 0, 0]) ** 2)
    field = s.get_dft_array(dft, mp.Ez, 0); eps = s.get_epsilon(); s.reset_meep()
    return mode1, total, field, eps


report = {}
for tag, weights in (("start", x_start), ("optimized", x_optimized)):
    mode1, total, fld, eps = modal_power(weights)
    report[tag] = {"mode1": mode1, "total": total, "T_mode1": mode1 / input_power, "T_total": total / input_power, "field": fld, "eps": eps}
    print(f"verify [{tag}]: mode-1 power {mode1:.4e}, total flux {total:.4e} -> T_mode1 {mode1 / input_power:.4f}, T_total {total / input_power:.4f}")
# resolution check of the final design (same 11 x 11 densities, finer Yee grid)
res_check = {}
for res in (RES, 2 * RES):
    m1, tot, _, _ = modal_power(x_optimized, res=res)
    s_in2 = mp.Simulation(geometry=straight, **dict(common, resolution=res))
    mi = s_in2.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(MON_IN_X, 0), size=mp.Vector3(0, 2)))
    s_in2.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(MON_IN_X, 0), 1e-5))
    pin = float(abs(s_in2.get_eigenmode_coefficients(mi, [1], direction=mp.X).alpha[0, 0, 0]) ** 2); s_in2.reset_meep()
    res_check[res] = {"T_mode1": m1 / pin, "T_total": tot / pin}
    print(f"resolution check [{res}]: T_mode1 {m1 / pin:.4f}, T_total {tot / pin:.4f}")

fig, ax = plt.subplots(1, 3, figsize=(13, 4.2), gridspec_kw={"width_ratios": [1.1, 1, 1]})
idx = np.arange(2)
tm = [report["start"]["T_mode1"], report["optimized"]["T_mode1"]]; tt = [report["start"]["T_total"], report["optimized"]["T_total"]]
ax[0].bar(idx - 0.2, tm, width=0.4, color="tab:blue", label="T_mode1 (output mode 1)"); ax[0].bar(idx + 0.2, tt, width=0.4, color="tab:gray", label="T_total (all flux)")
for k in range(2):
    ax[0].text(k - 0.2, tm[k] + 0.01, f"{tm[k]:.4f}", ha="center", fontsize=8); ax[0].text(k + 0.2, tt[k] + 0.01, f"{tt[k]:.4f}", ha="center", fontsize=8)
ax[0].set_xticks(idx); ax[0].set_xticklabels(["uniform start", f"after MMA (eval {best_k + 1})"]); ax[0].set_ylim(0, 1.0); ax[0].set_ylabel("normalized to input mode-1 power")
ax[0].set_title("contract 4: measured again in a new simulation", fontsize=9); ax[0].grid(axis="y", alpha=0.3); ax[0].legend(fontsize=7)
lim = max(np.max(np.abs(report["start"]["field"])), np.max(np.abs(report["optimized"]["field"])))
for a, tag in zip(ax[1:], ("start", "optimized")):
    a.imshow(np.real(report[tag]["field"]).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
    contour(a, report[tag]["eps"]); a.set_title(f"Re(Ez), {tag}  (T_mode1 = {report[tag]['T_mode1']:.3f})", fontsize=9); a.set_xlabel("x [um]")
ax[1].set_ylabel("y [um]")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "07_verify.png"), dpi=150); plt.close(fig)

# ---------------------------------------------------------------- GIF 1: a short pulse through the optimized bend (source -> output monitor)
fw_anim = 0.3 * fcen
sim_a = mp.Simulation(geometry=geometry_with(x_optimized), **dict(common, sources=[
    mp.EigenModeSource(mp.GaussianSource(fcen, fwidth=fw_anim), eig_band=1, direction=mp.NO_DIRECTION, eig_kpoint=mp.Vector3(1, 0, 0),
                       size=mp.Vector3(0, SRC_SIZE), center=mp.Vector3(SRC_X, 0))]))
sim_a.init_sim()
vol_a = mp.Volume(center=mp.Vector3(), size=mp.Vector3(SX - 2 * DPML, SY - 2 * DPML))
eps_a = sim_a.get_array(vol=vol_a, component=mp.Dielectric)
ext_a = [-(SX / 2 - DPML), SX / 2 - DPML, -(SY / 2 - DPML), SY / 2 - DPML]
t0 = 5 / fw_anim
path = abs(SRC_X) + SY / 2                                    # input straight + output straight, roughly
frames, times = record_frames(sim_a, vol_a, mp.Ez, t_start=t0 - 2 / fw_anim, t_end=t0 + 1.2 * path * 3.4, n_frames=60)
animate_fields(frames, times, ext_a, os.path.join(OUT, "08_anim_optimized.gif"), eps=eps_a, figsize=(6.2, 5.0), dpi=70,
               lines=[((SRC_X, -1), (SRC_X, 1), "red", "source"), ((-1, MON_OUT_Y), (1, MON_OUT_Y), "blue", "output monitor")],
               title="optimized bend", legend_loc="lower right")

# ---------------------------------------------------------------- GIF 2: how the design changed, start -> every MMA eval -> final
evo = [x_start] + design_history + [x_optimized]
evo_lab = ["start"] + [f"eval {k + 1}" for k in range(len(design_history))] + [f"final (eval {best_k + 1})"]
evo_fom = [f_start] + history + [max(history)]
fig_e, ax_e = plt.subplots(figsize=(4.0, 3.8))
im_e = ax_e.imshow(evo[0].reshape(NX, NY).T, origin="lower", extent=DEXT, cmap="gray_r", vmin=0, vmax=1, aspect="equal")
ax_e.set_xlabel("x [um]"); ax_e.set_ylabel("y [um]"); ttl_e = ax_e.set_title("", fontsize=9)
fig_e.colorbar(im_e, ax=ax_e, fraction=0.046, label="density (0 = SiO2, 1 = Si)")
fig_e.tight_layout()


def _evo(i):
    im_e.set_data(evo[i].reshape(NX, NY).T); ttl_e.set_text(f"{evo_lab[i]}   FOM = {evo_fom[i]:.1f}")
    return im_e, ttl_e


animation.FuncAnimation(fig_e, _evo, frames=len(evo), blit=False).save(os.path.join(OUT, "09_anim_design.gif"), writer=animation.PillowWriter(fps=1.5), dpi=80)
plt.close(fig_e)

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"params": {"wl": wl, "res": RES, "cell": [SX, SY], "w": W, "design": [D, D], "N": [NX, NY], "fwidth_rel": 0.12},
                   "source_check": {"total_in": total_in, "input_power": input_power, "mode1_share": input_power / total_in},
                   "fom": {"start": f_start, "random": f_random, "grad_norm": float(np.linalg.norm(g_start)),
                           "grad_max": float(g2.max()), "grad_min": float(g2.min()), "grad_pos": int((g2 > 0).sum()), "grad_neg": int((g2 < 0).sum())},
                   "gate": gate_rows, "gate_pass": gradient_gate,
                   "one_step": [{"alpha": a, "fom": f} for a, _, f in one_step],
                   "mma": {"history": history, "best_eval": best_k + 1, "gray_pixels": gray},
                   "verify": {k: {kk: vv for kk, vv in v.items() if kk not in ("field", "eps")} for k, v in report.items()},
                   "resolution_check": res_check,
                   "x_optimized": x_optimized.tolist(),
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__, "nlopt": f"{nlopt.version_major()}.{nlopt.version_minor()}"}, f, indent=2)
