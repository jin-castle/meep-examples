"""Meep Example 02 - 90 degree Waveguide Bend (two-run flux normalization).

A dielectric waveguide (eps = 12, width 1) turns a sharp 90 degree corner.
Run 1: straight waveguide  -> input power P_in and the "incident" flux data at the reflection plane.
Run 2: bent waveguide      -> transmitted flux (vertical arm) and reflected flux (incident part subtracted).
T = P_tran / P_in,  R = -P_refl / P_in,  radiation loss = 1 - T - R.
Follows the official bend-flux tutorial (dimensionless units, a = 1).

Run:  python bend90.py            (~2 min on one core)
Out:  01_layout.png, 02_field.png, 03_spectrum.png, result.json
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
from blogfig import Label, annotated_layout, field_figure, spectrum_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "02")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# Dimensionless units as in the official tutorial: 1 length unit = a (think 1 um).
eps_wg = 12.0            # waveguide permittivity (n = sqrt(12) = 3.46)
w = 1.0                  # waveguide width
fcen = 0.15              # center frequency -> wavelength 1/0.15 = 6.67 units
df = 0.1                 # source bandwidth
nfreq = 11               # number of frequencies in the flux monitors

# Physical reading used only for the figures: choose a so that the center wavelength is 1550 nm.
a_nm = 1550 * fcen       # = 232.5 nm per unit  -> waveguide width 233 nm, cell 3.72 um
a_um = a_nm / 1000

resolution = 25          # pixels per unit -> width = 25 px, wavelength in the guide (1.92) = 48 px
dpml = 1.0               # PML thickness
sx = sy = 16.0           # square cell, PML included

ycen = -4.0              # y of the input (horizontal) arm
xcen = +4.0              # x of the output (vertical) arm  -> corner at (xcen, ycen)

src_x = -6.5             # source: 0.5 outside the left PML (PML edge at x = -7)
refl_x = -5.5            # reflection flux plane: downstream of the source
tran_straight_x = +6.5   # transmission plane for the straight reference run
tran_bend_y = +6.5       # transmission plane for the bend run (on the vertical arm)
span = mp.Vector3(0, w + 2)   # source / monitor line: core + 1 unit on each side (evanescent tail)


# ---------------------------------------------------------------- (2) materials & geometry
def make_geometry(bend: bool):
    """Straight reference (bend=False) or the L-shaped bend (bend=True). Same width and material."""
    wg = mp.Medium(epsilon=eps_wg)
    if not bend:
        return [mp.Block(center=mp.Vector3(0, ycen), size=mp.Vector3(mp.inf, w), material=wg)]
    horizontal = mp.Block(center=mp.Vector3(0.5 * (-sx / 2 + xcen + w / 2), ycen),
                          size=mp.Vector3(sx / 2 + xcen + w / 2, w), material=wg)   # left PML -> corner
    vertical = mp.Block(center=mp.Vector3(xcen, 0.5 * (ycen - w / 2 + sy / 2)),
                        size=mp.Vector3(w, sy / 2 - ycen + w / 2), material=wg)     # corner -> top PML
    return [horizontal, vertical]


# ---------------------------------------------------------------- (3) source
# A plain Ez line source (not an eigenmode source), as in the official tutorial.
# It excites mostly the guided mode plus some radiation; the straight reference run
# measures exactly what the source puts into the guide, so that part cancels out.
sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ez,
                     center=mp.Vector3(src_x, ycen), size=span)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(bend: bool):
    return mp.Simulation(cell_size=mp.Vector3(sx, sy), resolution=resolution,
                         boundary_layers=[mp.PML(dpml)],
                         geometry=make_geometry(bend), sources=sources)


t0 = time.time()

# ================================================================ RUN 1: straight reference
sim = make_sim(bend=False)
# ---------------------------------------------------------------- (5) monitors, run 1
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(refl_x, ycen), size=span))
tran0 = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(tran_straight_x, ycen), size=span))

# ---------------------------------------------------------------- (6) run 1 & stop condition
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(tran_straight_x, ycen), 1e-6))

P_in = np.array(mp.get_fluxes(tran0))     # what actually travels down the guide = input power
refl_data = sim.get_flux_data(refl)       # incident fields at the reflection plane (to subtract later)
freqs = np.array(mp.get_flux_freqs(tran0))
t_run1 = time.time() - t0

# ================================================================ RUN 2: bend
sim = make_sim(bend=True)
# ---------------------------------------------------------------- (5) monitors, run 2
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(refl_x, ycen), size=span))
sim.load_minus_flux_data(refl, refl_data)  # subtract the incident part -> this monitor now sees reflection only
tran = sim.add_flux(fcen, df, nfreq,
                    mp.FluxRegion(center=mp.Vector3(xcen, tran_bend_y), size=mp.Vector3(w + 2, 0)))

decay_pt = (xcen, tran_bend_y)   # where stop_when_fields_decayed watches in the bend run (step 6)
annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=dpml, unit="um", axis_scale=a_um, axis_step=0.5,
    figsize=(7.5, 7.2), pml_xy=(-3.0, -sy / 2 + dpml / 2),
    params_text=(f"a = {a_nm:.1f} nm  (1 Meep unit)\n"
                 f"eps={eps_wg:g}  w={w:g}a={w*a_nm:.1f}nm  dpml={dpml:g}a\n"
                 f"wl={1/fcen:.2f}a={a_nm/fcen:.0f}nm  res={resolution}/a  cell={sx:g}a"),
    params_xy=(-6.6, 6.6), decay_point=decay_pt, decay_text_xy=(4.6, 5.6),
    title="90-deg waveguide bend (eps = 12, w = 1): Ez line source, flux monitors, PML",
    labels=[
        Label("horizontal arm (geometry)", (-1.0, ycen), (-3.5, -1.8), step=2, color="black"),
        Label("vertical arm (geometry)", (xcen - 0.5, 2.0), (-2.5, 3.5), step=2, color="black"),
        Label("Ez line source", (src_x, ycen - 1.6), (-6.3, -6.2), step=3, color="red"),
        Label("flux: reflection (minus incident)", (refl_x, ycen + 1.6), (-6.3, 0.2), step=5, color="blue"),
        Label("flux: transmission", (xcen - 1.5, tran_bend_y), (0.0, 5.0), step=5, color="blue"),
    ])

nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml, sy - 2 * dpml))
dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)

# ---------------------------------------------------------------- (6) run 2 & stop condition
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
wall = time.time() - t0

# ---------------------------------------------------------------- (7) post-processing
T = np.array(mp.get_fluxes(tran)) / P_in      # transmitted fraction
R = -np.array(mp.get_fluxes(refl)) / P_in     # backward flux is negative -> flip the sign
L = 1.0 - T - R                               # what is left: radiated out at the corner
ic = nfreq // 2
wl = 1 / freqs
print(f"T = {T[ic]:.4f}, R = {R[ic]:.4f}, radiation loss = {L[ic]:.4f}  (run1 {t_run1:.0f} s, total {wall:.0f} s)")
print(f"T over band {wl.min():.2f}-{wl.max():.2f}: {T.min():.3f} .. {T.max():.3f}")

ez = sim.get_dft_array(dft, mp.Ez, 0)
eps = sim.get_array(vol=nonpml, component=mp.Dielectric)   # structure outline for the figure
extent_um = [v * a_um for v in (-(sx / 2 - dpml), sx / 2 - dpml, -(sy / 2 - dpml), sy / 2 - dpml)]
field_figure(ez, extent_um, os.path.join(OUT, "02_field.png"), core_halfwidth=None, eps=eps,
             wl=round(a_nm / fcen), wl_unit="nm", component="Ez", layout="row", aspect="equal", unit="um")
spectrum_figure(wl * a_nm, {"T (transmitted)": T, "R (reflected)": R, "1 - T - R (radiated)": L},
                os.path.join(OUT, "03_spectrum.png"), unit="nm", mark=1550, mark_label="1550 nm (fcen)")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"T": float(T[ic]), "R": float(R[ic]), "loss": float(L[ic]),
                   "a_nm": a_nm, "wavelengths_a": wl.tolist(), "wavelengths_nm": (wl * a_nm).tolist(),
                   "T_spectrum": T.tolist(),
                   "R_spectrum": R.tolist(), "P_in_spectrum": P_in.tolist(),
                   "wall_s": wall, "run1_s": t_run1, "meep": mp.__version__},
                  f, indent=2)
