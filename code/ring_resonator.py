"""Meep Example 12 - A ring that traps light: Harminv resonances, Q, FSR, and a solve_cw cross-check.

Post 11 measured how much a dipole emits between two mirrors. On a chip the trap is a dielectric ring, and
the first questions about any resonator are: at which frequencies does it trap light, for how long (Q),
how far apart are the resonances (FSR), and what does each trapped mode look like.
  A. Official ring.py: a broadband Ez pulse inside the ring, Harminv on the ringing field after the source
     stops -> frequencies and Q of the modes in the band. Repeated at resolution 10 (official), 20, 30:
     frequencies converge fast, Q of the sharpest mode does not.
  B. Each resonance imaged alone: a narrow-band pulse at that frequency and a DFT field at the same frequency.
     The number of azimuthal lobes m is counted from the field along the ring.
  C. Official solve-cw.py: the same mode at f = 0.118 solved in the frequency domain (continuous source,
     BiCGSTAB-L), tolerance sweep, and compared with a time-domain DFT of the same mode after complex alignment.
Written to run under MPI: collective calls (run, get_array, solve_cw) on every rank, plotting on the master only.

Run:  python ring_resonator.py        (~10 min on one core, ~4 min with mpirun -np 4)
Out:  00_source.png, 01_layout.png, 02_harminv.png, 03_modes.png, 04_solve_cw.png, 05_anim_ring.gif, result.json
      (-> ../assets/12/)
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

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "12")
os.makedirs(OUT, exist_ok=True)
MASTER = mp.am_master()
t_all = time.time()


def say(*a):
    if MASTER:
        print(*a, flush=True)


# ---------------------------------------------------------------- (1) parameters (official ring.py; a = 1 um)
N_RING, W, R = 3.4, 1.0, 1.0                # index, ring width, inner radius  [a = 1 um]
PAD, DPML = 4.0, 2.0
SXY = 2 * (R + W + PAD + DPML)              # 16 x 16
FCEN, DF = 0.15, 0.1                        # broadband pulse covering 0.10..0.20
T_HARMINV = 300.0                           # ringing window after the source (official)
SRC_PT = mp.Vector3(R + 0.1)                # inside the ring, off the symmetry axes of the modes
RES_LIST = (10, 20, 30)                     # official 10, plus two finer
RES_IMG = 20                                # resolution for mode images, solve_cw, GIF
R_MID = R + 0.5 * W
L_RING = 2 * np.pi * R_MID                  # mean circumference
NONPML = mp.Volume(center=mp.Vector3(), size=mp.Vector3(SXY - 2 * DPML, SXY - 2 * DPML))
EXT = [-(0.5 * SXY - DPML), 0.5 * SXY - DPML, -(0.5 * SXY - DPML), 0.5 * SXY - DPML]

geometry = [mp.Cylinder(radius=R + W, material=mp.Medium(index=N_RING)),     # later objects win: outer dielectric first ...
            mp.Cylinder(radius=R)]                                             # ... then the air hole


def make_sim(res, sources, symmetries=(mp.Mirror(mp.Y),), **kw):
    return mp.Simulation(cell_size=mp.Vector3(SXY, SXY), geometry=geometry, sources=sources, resolution=res,
                         symmetries=list(symmetries), boundary_layers=[mp.PML(DPML)], **kw)


# ================================================================ A. Harminv at three resolutions
harm = {}
t_a = time.time()
for res in RES_LIST:
    src = [mp.Source(mp.GaussianSource(FCEN, fwidth=DF), mp.Ez, SRC_PT)]
    sim = make_sim(res, src)
    if res == RES_LIST[0]:
        annotated_layout(sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(6.6, 6.2), axis_step=2.0,
                         title="ring resonator (res 10 shown): n = 3.4, inner radius 1, width 1, a = 1 um",
                         params_text=f"n={N_RING}, r={R}, w={W}\nfcen={FCEN}, df={DF}\nres {RES_LIST}", params_xy=(-7.6, 7.0),
                         pml_xy=(-7.6, -6.6), decay_point=None,
                         labels=[Label("Ez point source at (r + 0.1, 0): every Ez mode in the band", (R + 0.1, 0.0), (-7.6, 4.6), step=3, color="red"),
                                 Label("ring = dielectric cylinder minus air cylinder", (-R_MID * 0.7, R_MID * 0.7), (-7.6, 3.2), step=2, color="black"),
                                 Label("Harminv probe = the source point, after the source", (R + 0.1, -0.3), (-5.2, -4.2), step=5, color="blue")])
    h = mp.Harminv(mp.Ez, SRC_PT, FCEN, DF)
    sim.run(mp.after_sources(h), until_after_sources=T_HARMINV)
    modes = sorted([(m.freq, m.Q, abs(m.amp), abs(m.err)) for m in h.modes if m.Q > 0 and FCEN - 0.5 * DF <= m.freq <= FCEN + 0.5 * DF])
    harm[res] = modes
    sim.reset_meep()
    say(f"A [res {res}]: " + "; ".join(f"f {f:.5f} Q {q:.0f} |amp| {a:.2e} err {e:.1e}" for f, q, a, e in modes))
modes_ref = harm[RES_IMG]
fsr = np.diff([m[0] for m in modes_ref])
ng = 1 / (np.mean(fsr) * L_RING)
say(f"A: FSR {', '.join(f'{x:.4f}' for x in fsr)} -> effective group index n_g = 1 / (FSR L) = {ng:.2f} (ring index {N_RING}); {time.time() - t_a:.0f} s")
if MASTER:
    source_figure(FCEN, DF, os.path.join(OUT, "00_source.png"), wl_scale=1.0, wl_unit="um", time_unit="um/c")

# ================================================================ B. one narrow-band run per resonance: field image + azimuthal order
imgs = []
t_b = time.time()
for f0, q0, _, _ in modes_ref:
    df0 = 0.01
    src = [mp.Source(mp.GaussianSource(f0, fwidth=df0), mp.Ez, SRC_PT)]
    sim = make_sim(RES_IMG, src)
    dft = sim.add_dft_fields([mp.Ez], f0, 0, 1, where=NONPML)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, SRC_PT, 1e-6))
    ez = sim.get_dft_array(dft, mp.Ez, 0)
    t_end = sim.meep_time()
    sim.reset_meep()
    # azimuthal order: sample the DFT field on the ring's mid-circle and count the dominant Fourier index
    nx, ny = ez.shape
    xs = np.linspace(EXT[0], EXT[1], nx); ys = np.linspace(EXT[2], EXT[3], ny)
    phis = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    ix = np.clip(np.searchsorted(xs, R_MID * np.cos(phis)), 0, nx - 1); iy = np.clip(np.searchsorted(ys, R_MID * np.sin(phis)), 0, ny - 1)
    ring_vals = ez[ix, iy]
    spec = np.abs(np.fft.rfft(np.real(ring_vals)))
    m_az = int(np.argmax(spec[1:]) + 1)
    imgs.append({"f": f0, "Q": q0, "ez": ez, "m": m_az, "t_end": t_end, "ring_vals": ring_vals})
    say(f"B [f {f0:.4f}]: azimuthal order m = {m_az} (m / (n L f) = {m_az / (N_RING * L_RING * f0):.3f}); run ended at t = {t_end:.0f}")
say(f"B done in {time.time() - t_b:.0f} s")

# ================================================================ C. solve_cw at f = 0.118 vs a time-domain DFT of the same mode
F_CW = modes_ref[0][0]
sym_cw = (mp.Mirror(mp.X, phase=-1), mp.Mirror(mp.Y, phase=+1))
src_cw = [mp.Source(mp.ContinuousSource(F_CW), component=mp.Ez, center=mp.Vector3(R + 0.1)),
          mp.Source(mp.ContinuousSource(F_CW), component=mp.Ez, center=mp.Vector3(-(R + 0.1)), amplitude=-1)]
TOLS = (1e-8, 1e-10, 1e-12)
MAXITERS, L_BICG = 10000, 10
sim = make_sim(RES_IMG, src_cw, sym_cw, force_complex_fields=True)
cw = []
t_c = time.time()
for tol in TOLS:
    sim.init_sim()
    t1 = time.time()
    sim.solve_cw(tol, MAXITERS, L_BICG)
    cw.append((tol, sim.get_array(vol=NONPML, component=mp.Ez), time.time() - t1))
eps_cw = sim.get_array(vol=NONPML, component=mp.Dielectric)
sim.reset_meep()
ref = cw[-1][1]
cw_err = [float(np.linalg.norm(a - ref) / np.linalg.norm(ref)) for _, a, _ in cw[:-1]]
say("C: solve_cw " + "; ".join(f"tol {t:.0e}: {s:.0f} s" for t, _, s in cw) + " | rel error vs tightest: " + ", ".join(f"{t:.0e}: {e:.2e}" for (t, _, _), e in zip(cw[:-1], cw_err)))

src_td = [mp.Source(mp.GaussianSource(F_CW, fwidth=0.08), component=mp.Ez, center=mp.Vector3(R + 0.1)),
          mp.Source(mp.GaussianSource(F_CW, fwidth=0.08), component=mp.Ez, center=mp.Vector3(-(R + 0.1)), amplitude=-1)]
sim = make_sim(RES_IMG, src_td, sym_cw)
dft = sim.add_dft_fields([mp.Ez], F_CW, 0, 1, where=NONPML)
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(R + 0.1523), 1e-8))
ez_td = sim.get_dft_array(dft, mp.Ez, 0); t_td = sim.meep_time()
sim.reset_meep()
alpha = np.vdot(ez_td, ref) / np.vdot(ez_td, ez_td)          # best-fit complex scale: CW and DFT differ by amplitude and global phase
err_td = float(np.linalg.norm(alpha * ez_td - ref) / np.linalg.norm(ref))
corr = float(np.corrcoef(np.abs(ez_td).ravel(), np.abs(ref).ravel())[0, 1])
say(f"C: time-domain DFT (decay 1e-8, ended t = {t_td:.0f}) vs solve_cw after complex alignment: rel L2 {err_td:.4f}, |Ez| correlation {corr:.6f}; {time.time() - t_c:.0f} s")

# ================================================================ GIF: broadband pulse rings the resonator (monitor-free)
sim_g = make_sim(RES_IMG, [mp.Source(mp.GaussianSource(FCEN, fwidth=DF), mp.Ez, SRC_PT)])
sim_g.init_sim()
eps_g = sim_g.get_array(vol=NONPML, component=mp.Dielectric)
t0g = 5 / DF
frames, times = record_frames(sim_g, NONPML, mp.Ez, t_start=t0g - 1 / DF, t_end=t0g + 260, n_frames=80)
sim_g.reset_meep()

# ================================================================ figures (master only)
if MASTER:
    # A: Harminv results vs resolution
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.0))
    cols = {10: "tab:gray", 20: "tab:blue", 30: "tab:red"}
    for j, (res, modes) in enumerate(harm.items()):
        ax[0].plot([m[0] for m in modes], [m[1] for m in modes], "o-", color=cols[res], label=f"res {res}: Q = " + " / ".join(f"{m[1]:.0f}" for m in modes))
    ax[0].set_yscale("log"); ax[0].set_xlabel("resonance frequency f [c/a]"); ax[0].set_ylabel("Q (Harminv)")
    ax[0].set_title("three Ez modes in the band 0.10-0.20: Q climbs with f (less bending radiation)", fontsize=9); ax[0].grid(alpha=0.3, which="both"); ax[0].legend(fontsize=8, loc="upper left")
    for k, (f, q, _, _) in enumerate(modes_ref):
        ax[1].axvline(f, color="tab:blue", lw=1.2); ax[1].text(f, 0.88, f"m = {imgs[k]['m']}\nf = {f:.4f}", ha="center", fontsize=8, color="tab:blue")
    ax[1].axvspan(FCEN - 0.5 * DF, FCEN + 0.5 * DF, color="orange", alpha=0.12, label="source band")
    for k in range(len(fsr)):
        ax[1].annotate("", xy=(modes_ref[k + 1][0], 0.5), xytext=(modes_ref[k][0], 0.5), arrowprops=dict(arrowstyle="<->", color="k"))
        ax[1].text(0.5 * (modes_ref[k][0] + modes_ref[k + 1][0]), 0.55, f"FSR {fsr[k]:.4f}", ha="center", fontsize=8)
    ax[1].text(0.102, 0.15, f"1 / (n_g L) with n_g = {ng:.2f}, L = 2 pi {R_MID} = {L_RING:.2f}", fontsize=8)
    ax[1].set_xlim(0.095, 0.205); ax[1].set_ylim(0, 1); ax[1].set_yticks([]); ax[1].set_xlabel("f [c/a]"); ax[1].set_title("free spectral range and azimuthal order (res 20)", fontsize=9); ax[1].legend(fontsize=8, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_harminv.png"), dpi=150); plt.close(fig)

    # B: mode images
    fig, ax = plt.subplots(2, 3, figsize=(13, 8.2), gridspec_kw={"height_ratios": [1.6, 1]})
    for k, d in enumerate(imgs):
        ez = d["ez"]; lim = float(np.percentile(np.abs(ez), 99.5))
        ax[0, k].imshow(np.real(ez).T, extent=EXT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
        ax[0, k].contour(np.linspace(EXT[0], EXT[1], eps_cw.shape[0]), np.linspace(EXT[2], EXT[3], eps_cw.shape[1]), eps_cw.T, levels=[0.5 * (1 + N_RING ** 2)], colors="k", linewidths=0.6)
        ax[0, k].plot(R + 0.1, 0, "o", color="lime", ms=4)
        ax[0, k].set_title(f"f = {d['f']:.4f} (lambda = {1 / d['f']:.2f} a), Q = {d['Q']:.0f}, m = {d['m']}", fontsize=9); ax[0, k].set_xlabel("x [a]")
        ax[1, k].plot(np.degrees(np.linspace(0, 2 * np.pi, 720, endpoint=False)), np.real(d["ring_vals"]) / np.max(np.abs(d["ring_vals"])), color="tab:blue", lw=1)
        ax[1, k].set_xlabel("angle around the ring [deg]"); ax[1, k].set_title(f"Re(Ez) on the mid-circle r = {R_MID}: {d['m']} periods", fontsize=9); ax[1, k].grid(alpha=0.3); ax[1, k].set_xlim(0, 360)
    ax[0, 0].set_ylabel("y [a]"); ax[1, 0].set_ylabel("normalized")
    fig.suptitle("each resonance imaged alone (narrow-band source, DFT at the resonance): the azimuthal order m counts the wavelengths around the ring", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_modes.png"), dpi=150); plt.close(fig)

    # C: solve_cw
    fig = plt.figure(figsize=(13, 4.4))
    ax = fig.add_subplot(1, 3, 1)
    ax.loglog([t for t, _, _ in cw[:-1]], cw_err, "bo-"); ax.invert_xaxis()
    for (t, _, s), e in zip(cw[:-1], cw_err):
        ax.annotate(f"{s:.0f} s", (t, e), textcoords="offset points", xytext=(6, -12), fontsize=8)
    ax.set_xlabel("solve_cw tolerance"); ax.set_ylabel(f"relative error vs tol {TOLS[-1]:.0e} field"); ax.set_title("frequency-domain solver: tighter tolerance, smaller change", fontsize=9); ax.grid(alpha=0.3, which="both")
    lim = float(np.percentile(np.abs(ref), 99.5))
    for a, data, ttl in ((fig.add_subplot(1, 3, 2), np.real(ref), f"solve_cw at f = {F_CW:.4f} (tol {TOLS[-1]:.0e})"),
                         (fig.add_subplot(1, 3, 3), np.real(alpha * ez_td), f"time-domain DFT, aligned: rel L2 {err_td:.3f}")):
        a.imshow(data.T, extent=EXT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
        a.contour(np.linspace(EXT[0], EXT[1], eps_cw.shape[0]), np.linspace(EXT[2], EXT[3], eps_cw.shape[1]), eps_cw.T, levels=[0.5 * (1 + N_RING ** 2)], colors="k", linewidths=0.6)
        a.set_title(ttl, fontsize=9); a.set_xlabel("x [a]")
    fig.suptitle("the same mode from two solvers: continuous source + BiCGSTAB-L (left, centre) and a pulse + DFT (right)", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.93]); fig.savefig(os.path.join(OUT, "04_solve_cw.png"), dpi=150); plt.close(fig)

    animate_fields(frames, times, EXT, os.path.join(OUT, "05_anim_ring.gif"), eps=eps_g, figsize=(5.6, 5.0), dpi=70, clip_percentile=99.0, unit="a",
                   points=[(R + 0.1, 0, "red", "source / probe")], title="broadband pulse, then ringing", legend_loc="lower left")

    with open(os.path.join(OUT, "result.json"), "w") as f_:
        json.dump({"params": {"n": N_RING, "r": R, "w": W, "pad": PAD, "dpml": DPML, "fcen": FCEN, "df": DF, "T_harminv": T_HARMINV, "L_ring": L_RING},
                   "harminv": {str(k): [{"f": f, "Q": q, "amp": a, "err": e} for f, q, a, e in v] for k, v in harm.items()},
                   "fsr": fsr.tolist(), "n_g": float(ng),
                   "modes": [{"f": d["f"], "Q": d["Q"], "m": d["m"], "t_end": float(d["t_end"])} for d in imgs],
                   "solve_cw": {"f": F_CW, "tols": list(TOLS), "seconds": [s for _, _, s in cw], "rel_err_vs_tightest": cw_err,
                                "td_vs_cw_rel_l2": err_td, "td_vs_cw_corr": corr, "td_t_end": float(t_td)},
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__, "np": mp.count_processors()}, f_, indent=2)
say(f"total {time.time() - t_all:.0f} s on {mp.count_processors()} process(es)")
