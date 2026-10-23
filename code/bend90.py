"""Meep Example 05 - Bent waveguide and the radius trade-off (two-run flux normalization).

A dielectric waveguide (eps = 12, width 1) turns a 90 degree corner.
Run 1: straight waveguide  -> input power P_in and the "incident" flux data at the reflection plane.
Run 2: bent waveguide      -> transmitted flux (vertical arm) and reflected flux (incident part subtracted).
T = P_tran / P_in,  R = -P_refl / P_in,  radiation loss = 1 - T - R.
The sharp corner (radius 0) follows the official bend-flux tutorial; then the corner is rounded
with a quarter-ring of radius R and T is swept over R to find where the loss disappears.

Run:  python bend90.py            (~3 min on one core: sharp + radius sweep + convergence)
Out:  00_source.png, 01_layout.png, 02_field.png, 03_spectrum.png, 04_radius_sweep.png,
      05_field_round.png, result.json   (-> ../assets/05/)
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
from blogfig import Label, annotated_layout, field_figure, line_figure, source_figure, spectrum_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "05")
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

RESOLUTION = 25          # pixels per unit -> width = 25 px, wavelength in the guide (1.92) = 48 px
DPML = 1.0               # PML thickness
sx = sy = 16.0           # square cell, PML included

ycen = -4.0              # y of the input (horizontal) arm
xcen = +4.0              # x of the output (vertical) arm  -> corner at (xcen, ycen)
span = mp.Vector3(0, w + 2)   # source / monitor line: core + 1 unit on each side (evanescent tail)


def positions(dpml):
    """Source and monitor planes measured from the PML edge, so a thicker PML keeps them outside it."""
    edge = sx / 2 - dpml
    return {"src_x": -edge + 0.5,          # source: 0.5 outside the left PML
            "refl_x": -edge + 1.5,         # reflection flux plane: downstream of the source
            "tran_straight_x": edge - 0.5,  # transmission plane for the straight reference run
            "tran_bend_y": edge - 0.5}      # transmission plane for the bend run (on the vertical arm)


# ---------------------------------------------------------------- (2) materials & geometry
def make_geometry(bend: bool, radius: float = 0.0):
    """Straight reference (bend=False), sharp corner (radius=0) or rounded corner (radius>0).

    The rounded corner is a quarter ring: outer cylinder (waveguide) minus inner cylinder (air),
    cut down to one quadrant with air blocks; the two arms are drawn last so they stay intact.
    """
    wg = mp.Medium(epsilon=eps_wg)
    air = mp.Medium(epsilon=1.0)
    if not bend:
        return [mp.Block(center=mp.Vector3(0, ycen), size=mp.Vector3(mp.inf, w), material=wg)]
    r = radius
    cx, cy = xcen - r, ycen + r                      # center of the quarter ring
    geom = []
    if r > 0:
        big = r + w / 2 + 1.0
        geom += [mp.Cylinder(radius=r + w / 2, center=mp.Vector3(cx, cy), material=wg),
                 mp.Cylinder(radius=r - w / 2, center=mp.Vector3(cx, cy), material=air)]
        # keep only the lower-right quadrant (x > cx, y < cy)
        geom += [mp.Block(center=mp.Vector3(cx - big / 2, cy), size=mp.Vector3(big, 2 * big), material=air),
                 mp.Block(center=mp.Vector3(cx + big / 2, cy + big / 2), size=mp.Vector3(big, big), material=air)]
    # sharp corner: the arms overlap by w x w so the outer corner is filled (official geometry);
    # rounded corner: the arms stop where the ring begins
    x_end = xcen + w / 2 if r == 0 else xcen - r     # horizontal arm: left PML -> corner / ring
    horizontal = mp.Block(center=mp.Vector3(0.5 * (-sx / 2 + x_end), ycen),
                          size=mp.Vector3(sx / 2 + x_end, w), material=wg)
    y_start = ycen - w / 2 if r == 0 else ycen + r   # vertical arm: corner / ring -> top PML
    vertical = mp.Block(center=mp.Vector3(xcen, 0.5 * (y_start + sy / 2)),
                        size=mp.Vector3(w, sy / 2 - y_start), material=wg)
    return geom + [horizontal, vertical]


# ---------------------------------------------------------------- (3) source
def make_sources(dpml):
    """A plain Ez line source (not an eigenmode source), as in the official tutorial."""
    p = positions(dpml)
    return [mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ez,
                      center=mp.Vector3(p["src_x"], ycen), size=span)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(bend: bool, radius=0.0, resolution=RESOLUTION, dpml=DPML):
    return mp.Simulation(cell_size=mp.Vector3(sx, sy), resolution=resolution,
                         boundary_layers=[mp.PML(dpml)],
                         geometry=make_geometry(bend, radius), sources=make_sources(dpml))


_reference = {}


def reference_run(resolution, dpml):
    """RUN 1 (cached per resolution/PML): straight guide -> P_in and the incident flux data."""
    key = (resolution, dpml)
    if key in _reference:
        return _reference[key]
    p = positions(dpml)
    sim = make_sim(bend=False, resolution=resolution, dpml=dpml)
    # ------------------------------------------------------------ (5) monitors, run 1
    refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
    tran0 = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["tran_straight_x"], ycen), size=span))
    # ------------------------------------------------------------ (6) run 1 & stop condition
    sim.run(until_after_sources=mp.stop_when_fields_decayed(
                25, mp.Ez, mp.Vector3(p["tran_straight_x"], ycen), 1e-6))
    _reference[key] = {"P_in": np.array(mp.get_fluxes(tran0)),      # what actually travels down the guide
                       "refl_data": sim.get_flux_data(refl),         # incident fields at the reflection plane
                       "freqs": np.array(mp.get_flux_freqs(tran0))}
    return _reference[key]


def bend_run(radius=0.0, resolution=RESOLUTION, dpml=DPML, figures=False, field_png=None):
    """RUN 2: the bend. Returns T, R, L spectra (fractions of P_in)."""
    ref = reference_run(resolution, dpml)
    p = positions(dpml)
    sim = make_sim(bend=True, radius=radius, resolution=resolution, dpml=dpml)
    # ------------------------------------------------------------ (5) monitors, run 2
    refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
    sim.load_minus_flux_data(refl, ref["refl_data"])  # subtract the incident part -> reflection only
    tran = sim.add_flux(fcen, df, nfreq,
                        mp.FluxRegion(center=mp.Vector3(xcen, p["tran_bend_y"]), size=mp.Vector3(w + 2, 0)))
    decay_pt = (xcen, p["tran_bend_y"])
    if figures:
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
                Label("Ez line source", (p["src_x"], ycen - 1.6), (-6.3, -6.2), step=3, color="red"),
                Label("flux: reflection (minus incident)", (p["refl_x"], ycen + 1.6), (-6.3, 0.2), step=5, color="blue"),
                Label("flux: transmission", (xcen - 1.5, p["tran_bend_y"]), (0.0, 5.0), step=5, color="blue"),
            ])
    want_field = figures or field_png is not None
    if want_field:
        nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml, sy - 2 * dpml))
        dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)
    # ------------------------------------------------------------ (6) run 2 & stop condition
    sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
    # ------------------------------------------------------------ (7) post-processing
    T = np.array(mp.get_fluxes(tran)) / ref["P_in"]      # transmitted fraction
    R = -np.array(mp.get_fluxes(refl)) / ref["P_in"]     # backward flux is negative -> flip the sign
    L = 1.0 - T - R                                      # what is left: radiated out at the corner
    if want_field:
        ez = sim.get_dft_array(dft, mp.Ez, 0)
        eps = sim.get_array(vol=nonpml, component=mp.Dielectric)
        extent_um = [v * a_um for v in (-(sx / 2 - dpml), sx / 2 - dpml, -(sy / 2 - dpml), sy / 2 - dpml)]
        field_figure(ez, extent_um, os.path.join(OUT, field_png or "02_field.png"), core_halfwidth=None,
                     eps=eps, wl=round(a_nm / fcen), wl_unit="nm", component="Ez",
                     layout="row", aspect="equal", unit="um")
    return {"T": T, "R": R, "L": L, "freqs": ref["freqs"]}


t_all = time.time()
ic = nfreq // 2

# source waveform and spectrum; the monitor band is fcen +- df/2
src_info = source_figure(fcen, df, os.path.join(OUT, "00_source.png"), mon_fcen=fcen, mon_df=df,
                         wl_scale=a_nm, wl_unit="nm", time_unit="a/c")

# ================================================================ sharp corner (official example)
t0 = time.time()
sharp = bend_run(0.0, figures=True)
wall_sharp = time.time() - t0
wl = 1 / sharp["freqs"]
print(f"sharp: T = {sharp['T'][ic]:.4f}, R = {sharp['R'][ic]:.4f}, radiation loss = {sharp['L'][ic]:.4f}  ({wall_sharp:.0f} s incl. reference)")
print(f"T over band {wl.min():.2f}-{wl.max():.2f}: {sharp['T'].min():.3f} .. {sharp['T'].max():.3f}")
spectrum_figure(wl * a_nm, {"T (transmitted)": sharp["T"], "R (reflected)": sharp["R"], "1 - T - R (radiated)": sharp["L"]},
                os.path.join(OUT, "03_spectrum.png"), unit="nm", mark=1550, mark_label="1550 nm (fcen)")

# ================================================================ radius sweep
radii = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]
sweep = []
for r in radii:
    if r == 0.0:
        res = sharp
    else:
        res = bend_run(r, field_png=("05_field_round.png" if r == 3.0 else None))
    sweep.append({"radius_a": r, "radius_um": r * a_um, "radius_over_wl": r * fcen,
                  "T": float(res["T"][ic]), "R": float(res["R"][ic]), "L": float(res["L"][ic])})
    print(f"radius {r:.1f} a ({r*a_um:.2f} um): T={res['T'][ic]:.4f} R={res['R'][ic]:.4f} L={res['L'][ic]:.4f}")
line_figure([s["radius_um"] for s in sweep],
            {"T (transmitted)": [s["T"] for s in sweep], "R (reflected)": [s["R"] for s in sweep],
             "1 - T - R (radiated)": [s["L"] for s in sweep]},
            os.path.join(OUT, "04_radius_sweep.png"), xlabel=f"bend radius [um]  (a = {a_nm:.1f} nm, wl = 1550 nm)")

# ================================================================ convergence (sharp corner)
convergence = [{"resolution": RESOLUTION, "dpml": DPML, "T": sweep[0]["T"], "R": sweep[0]["R"], "L": sweep[0]["L"]}]
for res_px, dpml in ((10, 1.0), (40, 1.0), (25, 1.5)):   # change one thing at a time
    t0 = time.time()
    r = bend_run(0.0, resolution=res_px, dpml=dpml)
    convergence.append({"resolution": res_px, "dpml": dpml, "T": float(r["T"][ic]), "R": float(r["R"][ic]),
                        "L": float(r["L"][ic]), "wall_s": time.time() - t0})
    print(f"convergence res={res_px} dpml={dpml}: T={r['T'][ic]:.4f} R={r['R'][ic]:.4f} L={r['L'][ic]:.4f}")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"T": sweep[0]["T"], "R": sweep[0]["R"], "loss": sweep[0]["L"],
                   "a_nm": a_nm, "wavelengths_a": wl.tolist(), "wavelengths_nm": (wl * a_nm).tolist(),
                   "T_spectrum": sharp["T"].tolist(), "R_spectrum": sharp["R"].tolist(),
                   "radius_sweep": sweep, "convergence": convergence, "source": src_info,
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__},
                  f, indent=2)
