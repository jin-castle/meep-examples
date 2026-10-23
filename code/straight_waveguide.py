"""Meep Example 04 - Straight waveguide and guided modes.

2D silicon strip waveguide in SiO2. Find the guided mode(s) and their effective index with
the eigenmode solver, inject the fundamental TE mode with EigenModeSource, and measure
modal transmission T and reflection R with mode monitors. Expected: T = 1, R = 0.
Then compare total flux with modal power, and check convergence in resolution and PML.

Run:  python straight_waveguide.py            (~3 min on one core: baseline + 2 convergence runs)
Out:  00_source.png, 01_layout.png, 02_field.png, 03_animation.gif, result.json  (-> ../assets/04/)
"""
import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, animate_fields, annotated_layout, field_figure, record_frames, source_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "04")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# Meep is unit-free. We choose 1 length unit = 1 um, so frequency = 1 / wavelength.
wl   = 1.55              # wavelength [um]
fcen = 1 / wl            # center frequency [1/um]
df   = 0.2 * fcen        # source bandwidth (Gaussian pulse)
df_mon = 0.1 * fcen      # monitor bandwidth
nfreq = 11               # number of frequencies the monitors record

w_core = 0.5             # Si strip width [um]
n_si, n_sio2 = 3.48, 1.44

RESOLUTION = 50          # pixels per um  -> core = 25 px, lambda/n_si = 22 px
DPML = 1.0               # PML thickness [um]
sx, sy = 14.0, 6.0       # cell size [um], PML included

# ---------------------------------------------------------------- (2) materials & geometry
geometry = [mp.Block(center=mp.Vector3(0, 0),
                     size=mp.Vector3(mp.inf, w_core),   # infinite in x: runs straight through the PML
                     material=mp.Medium(index=n_si))]
# background (cladding) is set below via default_material = SiO2

# ---------------------------------------------------------------- (3) source
cross = mp.Vector3(0, 3.0)   # a vertical line 3 um tall: wider than the core to include the evanescent tail
src_x, mon_in_x, mon_out_x = -5.0, -4.0, +5.0
PARITY = mp.ODD_Y            # 2D TE polarization (Ey, Hx, Hz)

sources = [mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=df),
                              center=mp.Vector3(src_x, 0), size=cross,
                              eig_band=1,               # 1-indexed: the fundamental mode
                              eig_parity=PARITY)]
decay_pt = (mon_out_x + 0.5, 0)   # where stop_when_fields_decayed watches (step 6)


# ---------------------------------------------------------------- (4) simulation & boundaries
def build(resolution=RESOLUTION, dpml=DPML):
    """Simulation plus its two mode monitors. One function so every run is set up the same way."""
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy),
                        resolution=resolution,
                        boundary_layers=[mp.PML(dpml)],        # absorbing layer on all four sides
                        geometry=geometry,
                        sources=sources,
                        default_material=mp.Medium(index=n_sio2))
    # ------------------------------------------------------------ (5) monitors
    mon_in = sim.add_mode_monitor(fcen, df_mon, nfreq,
                                  mp.ModeRegion(center=mp.Vector3(mon_in_x, 0), size=cross))
    mon_out = sim.add_mode_monitor(fcen, df_mon, nfreq,
                                   mp.ModeRegion(center=mp.Vector3(mon_out_x, 0), size=cross))
    return sim, mon_in, mon_out


def run_and_measure(sim, mon_in, mon_out):
    # ------------------------------------------------------------ (6) run & stop condition
    sim.run(until_after_sources=mp.stop_when_fields_decayed(
                25,                         # check every 25 time units
                mp.Ey,                      # which field component to watch
                mp.Vector3(*decay_pt),      # where to watch: just past the output monitor
                1e-6))                      # stop when |Ey|^2 has decayed to 1e-6 of its peak
    # ------------------------------------------------------------ (7) post-processing
    ci = sim.get_eigenmode_coefficients(mon_in,  [1], eig_parity=PARITY)
    co = sim.get_eigenmode_coefficients(mon_out, [1], eig_parity=PARITY)
    p_in_fwd  = np.abs(ci.alpha[0, :, 0]) ** 2    # forward mode-1 power at the input monitor   (a_in+)
    p_in_back = np.abs(ci.alpha[0, :, 1]) ** 2    # backward mode-1 power at the input monitor  (a_in-)
    p_out_fwd = np.abs(co.alpha[0, :, 0]) ** 2    # forward mode-1 power at the output monitor  (a_out+)
    flux_in  = np.array(mp.get_fluxes(mon_in))    # TOTAL power through the input plane (all modes, net)
    flux_out = np.array(mp.get_fluxes(mon_out))   # TOTAL power through the output plane
    return {
        "T": p_out_fwd / p_in_fwd,                # modal transmission  (section 2, first formula)
        "R": p_in_back / p_in_fwd,                # modal reflection    (section 2, second formula)
        "T_total": flux_out / flux_in,            # total-flux transmission
        "mode1_fraction_in": p_in_fwd / flux_in,  # how much of the injected power is really mode 1
        "freqs": np.array(mp.get_flux_freqs(mon_in)),
    }


t_all = time.time()
ic = nfreq // 2

# ================================================================ baseline run with figures
sim, mon_in, mon_out = build()

# source waveform and spectrum (same GaussianSource the EigenModeSource wraps)
src_info = source_figure(fcen, df, os.path.join(OUT, "00_source.png"), mon_fcen=fcen, mon_df=df_mon,
                         wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=DPML,
    title="2D Si strip waveguide (w = 0.5 um): TE0 EigenModeSource, mode monitors, PML",
    params_text=f"wl={wl} um  res={RESOLUTION}/um\ncell={sx}x{sy}  dpml={DPML}\nn_si={n_si}  n_sio2={n_sio2}",
    params_xy=(-2.2, 1.85), decay_point=decay_pt, decay_text_xy=(2.6, 1.0),
    labels=[
        Label("Si core (geometry)", (1.5, 0.0), (1.0, -1.2), step=2, color="black"),
        Label("EigenModeSource", (src_x, 1.3), (src_x + 1.2, 2.5), step=3, color="red"),
        Label("mode monitor: in / reflection", (mon_in_x, -1.3), (mon_in_x - 1.0, -2.5), step=5, color="blue"),
        Label("mode monitor: out", (mon_out_x, -1.3), (mon_out_x - 0.6, -2.5), step=5, color="blue"),
    ])

# guided modes of the cross-section: effective index n_eff = k / f  (MPB, called through Meep)
sim.init_sim()
where = mp.Volume(center=mp.Vector3(src_x, 0), size=cross)
neff = {}
for band in (1, 2, 3):
    em = sim.get_eigenmode(fcen, mp.X, where, band, mp.Vector3(0.8 * n_si * fcen, 0, 0), parity=PARITY)
    neff[band] = float(em.k.x / fcen) if em is not None else None
print("n_eff by band:", neff, f"(guided if {n_sio2} < n_eff < {n_si})")

nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * DPML, sy - 2 * DPML))
dft = sim.add_dft_fields([mp.Ey], fcen, 0, 1, where=nonpml)

t0 = time.time()
base = run_and_measure(sim, mon_in, mon_out)
wall_base = time.time() - t0
print(f"T = {base['T'][ic]:.6f}, R = {base['R'][ic]:.2e}, T+R = {base['T'][ic] + base['R'][ic]:.6f}  (wall {wall_base:.1f} s)")
print(f"T_total (flux) = {base['T_total'][ic]:.5f}, mode-1 fraction of input flux = {base['mode1_fraction_in'][ic]:.4f}")
wls = 1 / base["freqs"]
print(f"T over band {wls.min():.3f}-{wls.max():.3f} um: {base['T'].min():.5f} .. {base['T'].max():.5f}")

ey = sim.get_dft_array(dft, mp.Ey, 0)
eps = sim.get_array(vol=nonpml, component=mp.Dielectric)   # structure outline for the figure
extent = [-(sx / 2 - DPML), sx / 2 - DPML, -(sy / 2 - DPML), sy / 2 - DPML]
field_figure(ey, extent, os.path.join(OUT, "02_field.png"), core_halfwidth=None, wl=wl, eps=eps)

# ================================================================ animation: the pulse travels from the source to the output monitor
# A fresh simulation (the one above has already run). Timing from the source: the pulse peaks at
# t0 = 5/df and needs (10 um) * n_eff to reach the output monitor, so record t0 - 2*width .. t0 + 10*n_eff + 5.
sim_anim, _, _ = build()
width = 1.0 / df
t_src = 5.0 / df
frames, times = record_frames(sim_anim, nonpml, mp.Ey, t_start=t_src - 2 * width,
                              t_end=t_src + (mon_out_x - src_x) * neff[1] + 5.0, n_frames=60)
animate_fields(frames, times, extent, os.path.join(OUT, "03_animation.gif"), eps=eps, component="Ey",
               lines=[((src_x, -1.5), (src_x, 1.5), "red", "EigenModeSource"),
                      ((mon_in_x, -1.5), (mon_in_x, 1.5), "blue", "mode monitor in"),
                      ((mon_out_x, -1.5), (mon_out_x, 1.5), "blue", "mode monitor out")],
               aspect="auto", figsize=(8.0, 3.6), title="TE0 pulse, source -> output monitor")

# ================================================================ convergence: resolution x PML
convergence = [{"resolution": RESOLUTION, "dpml": DPML, "T": float(base["T"][ic]), "R": float(base["R"][ic]),
                "T_total": float(base["T_total"][ic]), "wall_s": wall_base}]
for res, dpml in ((25, 1.0), (70, 1.0), (50, 0.5)):   # change one thing at a time
    sim, mon_in, mon_out = build(res, dpml)
    t0 = time.time()
    r = run_and_measure(sim, mon_in, mon_out)
    convergence.append({"resolution": res, "dpml": dpml, "T": float(r["T"][ic]), "R": float(r["R"][ic]),
                        "T_total": float(r["T_total"][ic]), "wall_s": time.time() - t0})
    print(f"convergence res={res} dpml={dpml}: T={r['T'][ic]:.6f} R={r['R'][ic]:.2e} T_total={r['T_total'][ic]:.5f}")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"T": float(base["T"][ic]), "R": float(base["R"][ic]), "T_plus_R": float(base["T"][ic] + base["R"][ic]),
                   "T_total": float(base["T_total"][ic]), "mode1_fraction_in": float(base["mode1_fraction_in"][ic]),
                   "neff": neff, "n_core": n_si, "n_clad": n_sio2,
                   "T_band_min": float(base["T"].min()), "T_band_max": float(base["T"].max()),
                   "wavelengths_um": wls.tolist(), "T_spectrum": base["T"].tolist(), "R_spectrum": base["R"].tolist(),
                   "T_total_spectrum": base["T_total"].tolist(),
                   "source": src_info, "convergence": convergence,
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__},
                  f, indent=2)
