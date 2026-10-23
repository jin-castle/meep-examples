"""Meep Example 01 - Straight Waveguide.

2D silicon strip waveguide in SiO2. Inject the fundamental TE mode at one end,
measure transmission T and reflection R with mode monitors. Expected: T = 1, R = 0.

Run:  python straight_waveguide.py            (~25 s on one core)
Out:  01_layout.png, 02_field.png, result.json
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
from blogfig import Label, annotated_layout, field_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "01")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# Meep is unit-free. We choose 1 length unit = 1 um, so frequency = 1 / wavelength.
wl   = 1.55              # wavelength [um]
fcen = 1 / wl            # center frequency [1/um]
df   = 0.2 * fcen        # source bandwidth (Gaussian pulse)
nfreq = 11               # number of frequencies the monitors record

w_core = 0.5             # Si strip width [um]
n_si, n_sio2 = 3.48, 1.44

resolution = 50          # pixels per um  -> core = 25 px, lambda/n_si = 22 px
dpml = 1.0               # PML thickness [um]
sx, sy = 14.0, 6.0       # cell size [um], PML included

# ---------------------------------------------------------------- (2) materials & geometry
geometry = [mp.Block(center=mp.Vector3(0, 0),
                     size=mp.Vector3(mp.inf, w_core),   # infinite in x: runs straight through the PML
                     material=mp.Medium(index=n_si))]
# background (cladding) is set below via default_material = SiO2

# ---------------------------------------------------------------- (3) source
cross = mp.Vector3(0, 3.0)   # a vertical line 3 um tall: wider than the core to include the evanescent tail
src_x, mon_in_x, mon_out_x = -5.0, -4.0, +5.0

sources = [mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=df),
                              center=mp.Vector3(src_x, 0), size=cross,
                              eig_band=1,               # 1-indexed: the fundamental mode
                              eig_parity=mp.ODD_Y)]     # 2D TE polarization (Ey, Hx, Hz)

# ---------------------------------------------------------------- (4) simulation & boundaries
sim = mp.Simulation(cell_size=mp.Vector3(sx, sy),
                    resolution=resolution,
                    boundary_layers=[mp.PML(dpml)],        # absorbing layer on all four sides
                    geometry=geometry,
                    sources=sources,
                    default_material=mp.Medium(index=n_sio2))

# ---------------------------------------------------------------- (5) monitors
mon_in  = sim.add_mode_monitor(fcen, 0.1 * fcen, nfreq,
                               mp.ModeRegion(center=mp.Vector3(mon_in_x, 0), size=cross))
mon_out = sim.add_mode_monitor(fcen, 0.1 * fcen, nfreq,
                               mp.ModeRegion(center=mp.Vector3(mon_out_x, 0), size=cross))

# ALWAYS look at the layout before running (drawn here so the mode monitors show up)
decay_pt = (mon_out_x + 0.5, 0)   # where stop_when_fields_decayed watches (step 6)
annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=dpml,
    title="2D Si strip waveguide (w = 0.5 um): TE0 EigenModeSource, mode monitors, PML",
    params_text=f"wl={wl} um  res={resolution}/um\ncell={sx}x{sy}  dpml={dpml}\nn_si={n_si}  n_sio2={n_sio2}",
    params_xy=(-2.2, 1.85), decay_point=decay_pt, decay_text_xy=(2.6, 1.0),
    labels=[
        Label("Si core (geometry)", (1.5, 0.0), (1.0, -1.2), step=2, color="black"),
        Label("EigenModeSource", (src_x, 1.3), (src_x + 1.2, 2.5), step=3, color="red"),
        Label("mode monitor: in / reflection", (mon_in_x, -1.3), (mon_in_x - 1.0, -2.5), step=5, color="blue"),
        Label("mode monitor: out", (mon_out_x, -1.3), (mon_out_x - 0.6, -2.5), step=5, color="blue"),
    ])

# steady-state field map of the whole non-PML region (for the figure in section 5)
nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml, sy - 2 * dpml))
dft = sim.add_dft_fields([mp.Ey], fcen, 0, 1, where=nonpml)

# ---------------------------------------------------------------- (6) run & stop condition
t0 = time.time()
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25,                         # check every 25 time units
            mp.Ey,                      # which field component to watch
            mp.Vector3(*decay_pt),      # where to watch: just past the output monitor
            1e-6))                      # stop when |Ey|^2 has decayed to 1e-6 of its peak
wall = time.time() - t0

# ---------------------------------------------------------------- (7) post-processing
ci = sim.get_eigenmode_coefficients(mon_in,  [1], eig_parity=mp.ODD_Y)
co = sim.get_eigenmode_coefficients(mon_out, [1], eig_parity=mp.ODD_Y)

p_in_fwd  = np.abs(ci.alpha[0, :, 0]) ** 2    # forward power at the input monitor   (a_in+)
p_in_back = np.abs(ci.alpha[0, :, 1]) ** 2    # backward power at the input monitor  (a_in-)
p_out_fwd = np.abs(co.alpha[0, :, 0]) ** 2    # forward power at the output monitor  (a_out+)

T = p_out_fwd / p_in_fwd                      # section 2, first formula
R = p_in_back / p_in_fwd                      # section 2, second formula
freqs = np.array(mp.get_flux_freqs(mon_in))
ic = nfreq // 2                               # index of the center frequency
print(f"T = {T[ic]:.6f}, R = {R[ic]:.2e}, T+R = {T[ic] + R[ic]:.6f}  (wall {wall:.1f} s)")
print(f"T over band {1/freqs.max():.3f}-{1/freqs.min():.3f} um: {T.min():.5f} .. {T.max():.5f}")

ey = sim.get_dft_array(dft, mp.Ey, 0)
eps = sim.get_array(vol=nonpml, component=mp.Dielectric)   # structure outline for the figure
extent = [-(sx / 2 - dpml), sx / 2 - dpml, -(sy / 2 - dpml), sy / 2 - dpml]
field_figure(ey, extent, os.path.join(OUT, "02_field.png"), core_halfwidth=None, wl=wl, eps=eps)

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"T": float(T[ic]), "R": float(R[ic]), "T_plus_R": float(T[ic] + R[ic]),
                   "T_band_min": float(T.min()), "T_band_max": float(T.max()),
                   "wavelengths_um": (1 / freqs).tolist(), "T_spectrum": T.tolist(),
                   "R_spectrum": R.tolist(), "wall_s": wall, "meep": mp.__version__},
                  f, indent=2)
