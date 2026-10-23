"""Meep Example 02 - Boundary conditions and PML.

Same point source, same cell, different boundary treatment.
  A. field maps at one instant: no absorbing layer (Meep's default = perfect reflector) vs PML 1 um,
     summarised by the RMS of Ez in a 1 um band along the edges.
  B. a clean reflection metric: a padded reference run whose boundaries are so far away that nothing
     comes back in time; whatever differs inside the compared region is reflection from the boundary.
       R = rms(E_test - E_ref) / max_t rms(E_ref)
     Cases: no layer, PML 0.25..2 um, Absorber 1 um; convergence in resolution.
  C. GIF: reflecting boundary vs PML, side by side.

Run:  python boundary_pml.py           (~2 min on one core)
Out:  00_source.png, 01_layout.png, 02_fieldmaps.png, 03_reflection.png, 04_pml_sweep.png,
      05_anim_compare.gif, result.json   (-> ../assets/02/)
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
from blogfig import (Label, animate_compare, annotated_layout, bar_figure, line_figure,   # noqa: E402
                     panel_grid, record_frames, source_figure)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "02")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
wl = 1.55                     # wavelength [um]; 1 unit = 1 um, c = 1
fcen = 1 / wl
fwidth = 0.4                  # short pulse (width 2.5): a single wavefront is easy to follow
t0 = 5.0 / fwidth             # pulse peak (Meep cutoff = 5)
width = 1.0 / fwidth
RESOLUTION = 12               # pixels per um (18 px per wavelength); cheap, course value

# experiment A / C: rectangular cell, source off-center
sx, sy = 12.0, 8.0
src = mp.Vector3(-2.5, 0.0)
corner = max(np.hypot(sx / 2 * ax - src.x, sy / 2 * ay - src.y) for ax in (-1, 1) for ay in (-1, 1))
t_compare = t0 + 1.5 * corner # the wavefront has reached every corner and (if reflected) come back

# experiment B: the PML-free interior is always L x L; a layer of thickness d is ADDED outside it
# (cell = L + 2d), so the compared region |x|,|y| <= HALF never overlaps the layer.
# The reference domain is padded by PAD on each side: nothing reflected reaches the compared region by t_B.
L = 8.0
PAD = 6.0
HALF = L / 2 - 1.0            # compared region: |x|,|y| <= 3 um, 1 um inside the layer
t_B = t0 + 1.5 * (L / 2 * np.sqrt(2))

# ---------------------------------------------------------------- (2) materials & geometry
# none: vacuum. The only thing that changes between runs is the boundary layer.


# ---------------------------------------------------------------- (3) source
def point_source(center):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(cell, layers, center=mp.Vector3(), resolution=RESOLUTION):
    """layers = [] (reflecting), [mp.PML(d)] or [mp.Absorber(d)]."""
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=layers, sources=point_source(center), Courant=0.5)


t_all = time.time()
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ A. field maps at t_compare, edge-band RMS
def edge_rms(field):
    x = np.linspace(-sx / 2, sx / 2, field.shape[0], endpoint=False)
    y = np.linspace(-sy / 2, sy / 2, field.shape[1], endpoint=False)
    band = (np.abs(x)[:, None] > sx / 2 - 1.0) | (np.abs(y)[None, :] > sy / 2 - 1.0)
    return float(np.sqrt(np.mean(np.abs(field[band]) ** 2)))


maps, edges = {}, {}
for name, layers in (("no layer", []), ("PML 1 um", [mp.PML(1.0)])):
    sim = make_sim((sx, sy), layers, center=src)
    if name == "PML 1 um":
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=1.0, figsize=(7.4, 5.4),
            title="experiment A: point source, PML 1 um (the 'no layer' case is the same cell without PML)",
            params_text=f"wl={wl} um  fwidth={fwidth}\nres={RESOLUTION}/um  cell={sx:g}x{sy:g}  dpml=1.0",
            params_xy=(-4.6, 3.6), pml_xy=(1.5, -3.5),
            labels=[Label("geometry = []  (vacuum)", (1.0, 1.5), (0.0, 2.6), step=2, color="black"),
                    Label("point source (Ez)", (src.x, src.y), (-4.6, -1.6), step=3, color="red"),
                    Label("no monitor: the field itself is the result", (3.0, -0.3), (0.2, -1.8), step=5, color="blue")])
    sim.run(until=t_compare)                      # (6) the SAME absolute time for both cases
    maps[name] = sim.get_array(center=mp.Vector3(), size=mp.Vector3(sx, sy), component=mp.Ez)   # (7)
    edges[name] = edge_rms(maps[name])
extent_a = [-sx / 2, sx / 2, -sy / 2, sy / 2]
panel_grid([maps["no layer"], maps["PML 1 um"]],
           [f"no absorbing layer: edge RMS {edges['no layer']:.3f}", f"PML 1 um: edge RMS {edges['PML 1 um']:.4f}"],
           extent_a, os.path.join(OUT, "02_fieldmaps.png"), ncols=2, marks=[(src.x, src.y)],
           rects=[(-sx / 2, -sy / 2, sx, sy), (-sx / 2 + 1, -sy / 2 + 1, sx - 2, sy - 2)],
           suptitle=f"same source, same time t = {t_compare:.1f}: only the boundary differs")
print(f"A. t0 = {t0:.1f}, t_compare = {t_compare:.1f}; edge RMS no layer = {edges['no layer']:.4f}, PML 1 um = {edges['PML 1 um']:.4f} (ratio {edges['no layer']/edges['PML 1 um']:.1f})")


# ================================================================ B. padded reference: reflection = test - reference
def crop(field, size):
    """Central square |x|,|y| <= HALF of a field over a `size` x `size` cell."""
    n = field.shape[0]
    axis = (np.arange(n) + 0.5) / n * size - size / 2
    m = np.abs(axis) <= HALF
    return field[np.ix_(m, m)]


def rms(a):
    return float(np.sqrt(np.mean(np.abs(a) ** 2)))


_ref_cache = {}


def reference(resolution):
    """Big domain (L + 2 PAD): no reflection reaches the compared region before t_B. Also tracks the
    peak RMS inside that region over time, the denominator of the reflection metric."""
    if resolution in _ref_cache:
        return _ref_cache[resolution]
    big = L + 2 * PAD
    sim = make_sim((big, big), [], resolution=resolution)
    peak = [0.0]

    def track(s):
        a = s.get_array(center=mp.Vector3(), size=mp.Vector3(2 * HALF, 2 * HALF), component=mp.Ez)
        peak[0] = max(peak[0], rms(a))

    sim.run(mp.at_every(0.25, track), until=t_B)
    field = crop(sim.get_array(center=mp.Vector3(), size=mp.Vector3(big, big), component=mp.Ez), big)
    _ref_cache[resolution] = (field, peak[0])
    return _ref_cache[resolution]


def reflection(layers, d=0.0, resolution=RESOLUTION):
    """Reflection metric for a boundary layer of thickness d (0 = no layer, Meep's reflecting default)."""
    ref, peak = reference(resolution)
    cell = L + 2 * d
    sim = make_sim((cell, cell), layers, resolution=resolution)
    sim.run(until=t_B)
    test = crop(sim.get_array(center=mp.Vector3(), size=mp.Vector3(cell, cell), component=mp.Ez), cell)
    if test.shape != ref.shape:                   # grids of the two domains may differ by a pixel
        k = min(test.shape[0], ref.shape[0]); test, ref = test[:k, :k], ref[:k, :k]
    return rms(test - ref) / peak


cases = {"no layer": ([], 0.0), "Absorber 1 um": ([mp.Absorber(1.0)], 1.0)}
cases.update({f"PML {d:g} um": ([mp.PML(d)], d) for d in (0.25, 0.5, 1.0, 1.5, 2.0)})
R = {k: reflection(layers, d) for k, (layers, d) in cases.items()}
for k, v in R.items():
    print(f"B. {k:14s} reflection / peak incident = {v:.3e}")
bar_figure(["no layer", "Absorber 1 um", "PML 1 um"], {"reflected RMS / peak incident RMS": [R["no layer"], R["Absorber 1 um"], R["PML 1 um"]]},
           os.path.join(OUT, "03_reflection.png"), ylabel="reflected RMS / peak incident RMS", logy=True, fmt="{:.1e}")
thick = [0.25, 0.5, 1.0, 1.5, 2.0]
line_figure(thick, {"PML": [R[f"PML {t:g} um"] for t in thick]}, os.path.join(OUT, "04_pml_sweep.png"),
            xlabel="PML thickness [um]", ylabel="reflected RMS / peak incident RMS", logy=True,
            hline=R["Absorber 1 um"], hline_label="Absorber 1 um")

convergence = [{"resolution": RESOLUTION, "no layer": R["no layer"], "PML 1 um": R["PML 1 um"], "Absorber 1 um": R["Absorber 1 um"]}]
for res in (24,):
    row = {"resolution": res, "no layer": reflection([], 0.0, res), "PML 1 um": reflection([mp.PML(1.0)], 1.0, res),
           "Absorber 1 um": reflection([mp.Absorber(1.0)], 1.0, res)}
    convergence.append(row)
    print(f"convergence res={res}: " + "  ".join(f"{k}={v:.2e}" for k, v in row.items() if k != "resolution"))

# ================================================================ C. GIF: reflecting vs PML, side by side
vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx, sy))
sets, titles = [], []
for name, layers in (("no absorbing layer (reflecting)", []), ("PML 1 um", [mp.PML(1.0)])):
    s_anim = make_sim((sx, sy), layers, center=src)
    frames, times = record_frames(s_anim, vol, mp.Ez, t_start=t0 - 2 * width, t_end=t0 + 1.6 * corner, n_frames=60)
    sets.append(frames); titles.append(name)
animate_compare(sets, titles, times, extent_a, os.path.join(OUT, "05_anim_compare.gif"),
                points=[(src.x, src.y, "k", "source")], suptitle="same source and time")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"t0": t0, "t_compare": t_compare, "t_B": t_B, "edge_rms": edges, "reflection": R,
                   "convergence": convergence, "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
