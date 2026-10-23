"""Meep Example 01 - Point source and line source.

Three small experiments in an empty 2D cell:
  A. a point Ez source, no PML: snapshots after the pulse peak t0, before the first wall reflection,
     with the predicted wavefront radius c*(t - t0) drawn on top;
  B. point source vs a finite line source at the same instant;
  C. with PML: a flux box around each source measures how the power is split between the four
     sides (point: 25 % each; line: mostly +-x), and the four sides add up to the emitted power.

Run:  python point_line_source.py          (~40 s on one core)
Out:  00_source.png, 01_layout.png, 02_snapshots.png, 03_point_vs_line.png, 04_flux_box.png,
      05_anim_point.gif, 05_anim_line.gif, result.json   (-> ../assets/01/)
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
from blogfig import Label, animate_fields, annotated_layout, bar_figure, panel_grid, record_frames, source_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "01")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# 1 length unit = 1 um, c = 1: a wave travels 1 um per time unit, so time is in um/c.
wl = 1.55                     # wavelength [um]
fcen = 1 / wl                 # center frequency [1/um]
fwidth = 0.5 * fcen           # wide band -> short pulse (~2 periods): clean concentric rings
CUTOFF = 5.0                  # Meep default: GaussianSource peaks at t0 = CUTOFF / fwidth
t0 = CUTOFF / fwidth          # pulse peak time
RESOLUTION = 20               # pixels per um (31 px per wavelength)

# experiment A/B: no PML, source off-center so the nearest wall is 4 um away
sx_a, sy_a = 12.0, 8.0
src_a = mp.Vector3(-2.0, 0.0)
line_len = 3.0                # finite line source length [um] (about 2 wavelengths)
d_wall = min(sx_a / 2 - abs(src_a.x), sy_a / 2 - abs(src_a.y))   # 4 um: reflections return after t0 + 2*d_wall

# experiment C: with PML, source at the center, flux box of half-size `half` around it
sx_c = sy_c = 10.0
DPML = 1.0
half = 2.5


# ---------------------------------------------------------------- (2) materials & geometry
# nothing: an empty cell is vacuum (default_material = air). geometry = [] is the point of this post.

# ---------------------------------------------------------------- (3) source
def make_source(center, size=mp.Vector3(0, 0, 0)):
    """size (0,0,0) = point source; size (0, L, 0) = line source of length L along y."""
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center, size=size)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(cell, sources, dpml=0.0, resolution=RESOLUTION):
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=[mp.PML(dpml)] if dpml > 0 else [], sources=sources)


t_all = time.time()
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ A. snapshots before any reflection
offsets = [0.0, 0.8, 1.6, 2.4, 3.2, 3.6]          # time after the pulse peak; last one < d_wall
sim = make_sim((sx_a, sy_a), make_source(src_a))
fields, titles, prev = [], [], 0.0
for off in offsets:
    target = t0 + off
    sim.run(until=target - prev)                   # `until` counts from NOW, so pass the difference
    prev = target
    fields.append(sim.get_array(center=mp.Vector3(), size=mp.Vector3(sx_a, sy_a), component=mp.Ez))
    titles.append(f"t = {target:.1f}  (t0 + {off:.1f})")
extent_a = [-sx_a / 2, sx_a / 2, -sy_a / 2, sy_a / 2]
r_front = offsets[-1]                              # c = 1: the peak has travelled this far
panel_grid(fields, titles, extent_a, os.path.join(OUT, "02_snapshots.png"), marks=[(src_a.x, src_a.y)],
           circles={len(fields) - 1: (src_a.x, src_a.y, r_front, f"predicted r = {r_front:.1f} um")},
           suptitle="point source, no PML: wavefront after the pulse peak (one color scale)")

# does the field really sit on the predicted circle?  mean |Ez| on the ring vs. over the cell
ez_last = fields[-1]
gx, gy = np.meshgrid(np.linspace(-sx_a / 2, sx_a / 2, ez_last.shape[0]) - src_a.x,
                     np.linspace(-sy_a / 2, sy_a / 2, ez_last.shape[1]) - src_a.y, indexing="ij")
rr = np.hypot(gx, gy)
ring = np.abs(ez_last)[(rr > r_front - 0.4) & (rr < r_front + 0.4)].mean()
everywhere = np.abs(ez_last).mean()
print(f"A. t0 = {t0:.2f}; at t0 + {r_front}: mean |Ez| on the predicted ring = {ring:.4f}, cell mean = {everywhere:.4f} (ratio {ring/everywhere:.2f})")

# ================================================================ B. point vs line at the same instant
t_snap = t0 + 3.6
sim_line = make_sim((sx_a, sy_a), make_source(src_a, mp.Vector3(0, line_len, 0)))
sim_line.run(until=t_snap)
ez_line = sim_line.get_array(center=mp.Vector3(), size=mp.Vector3(sx_a, sy_a), component=mp.Ez)
panel_grid([ez_last, ez_line], ["point source", f"line source, length {line_len:g} um"], extent_a,
           os.path.join(OUT, "03_point_vs_line.png"), ncols=2, marks=[(src_a.x, src_a.y)],
           lines={1: ((src_a.x, src_a.y - line_len / 2), (src_a.x, src_a.y + line_len / 2))},
           suptitle=f"same instant t = t0 + 3.6, no PML")


# ================================================================ B'. animations: point and line source, no PML, until the first reflection
sq = 12.0                                           # square cell, source at the center: symmetric spreading
width = 1.0 / fwidth
for kind, size in (("point", mp.Vector3(0, 0, 0)), ("line", mp.Vector3(0, line_len, 0))):
    sim_anim = make_sim((sq, sq), make_source(mp.Vector3(0, 0), size))
    frames, times = record_frames(sim_anim, mp.Volume(center=mp.Vector3(), size=mp.Vector3(sq, sq)), mp.Ez,
                                  t_start=t0 - 2 * width, t_end=t0 + 0.9 * sq / 2, n_frames=45)
    marker = ([((0, -line_len / 2), (0, line_len / 2), "k", "line source")] if kind == "line" else None)
    animate_fields(frames, times, [-sq / 2, sq / 2, -sq / 2, sq / 2], os.path.join(OUT, f"05_anim_{kind}.gif"),
                   lines=marker, points=([(0, 0, "k", "point source")] if kind == "point" else None),
                   figsize=(5.2, 4.6), title=f"{kind} source, no PML")

# ================================================================ C. flux box: where does the power go?
def flux_split(size, resolution=RESOLUTION, dpml=DPML, layout=False):
    """Power through the four sides of a box around the source, as fractions of the total."""
    sim = make_sim((sx_c, sy_c), make_source(mp.Vector3(0, 0), size), dpml=dpml, resolution=resolution)
    # ------------------------------------------------------------ (5) monitors: four flux planes, outward normals
    sides = {
        "+x": mp.FluxRegion(center=mp.Vector3(+half, 0), size=mp.Vector3(0, 2 * half)),
        "-x": mp.FluxRegion(center=mp.Vector3(-half, 0), size=mp.Vector3(0, 2 * half), weight=-1),
        "+y": mp.FluxRegion(center=mp.Vector3(0, +half), size=mp.Vector3(2 * half, 0)),
        "-y": mp.FluxRegion(center=mp.Vector3(0, -half), size=mp.Vector3(2 * half, 0), weight=-1),
    }
    mons = {k: sim.add_flux(fcen, 0, 1, reg) for k, reg in sides.items()}
    decay_pt = (half + 0.8, 0)
    if layout:
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=dpml, figsize=(6.8, 6.4),
            title="experiment C: point source in vacuum, PML, four flux planes around it",
            params_text=f"wl={wl} um  fwidth={fwidth:.3f}\nres={resolution}/um  cell={sx_c:g}x{sy_c:g}  dpml={dpml:g}",
            params_xy=(-3.8, 3.75), decay_point=decay_pt, decay_text_xy=(2.0, -0.6),
            labels=[
                Label("geometry = []  (vacuum)", (-2.0, 2.0), (-3.5, 2.6), step=2, color="black"),
                Label("point source (Ez)", (0, 0), (-3.5, -1.6), step=3, color="red"),
                Label("flux planes, normals outward", (half, 1.0), (0.3, 1.9), step=5, color="blue"),
            ])
    # ------------------------------------------------------------ (6) run until the pulse has left
    sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
    # ------------------------------------------------------------ (7) post-processing
    p = {k: float(mp.get_fluxes(m)[0]) for k, m in mons.items()}
    total = sum(p.values())
    return {k: v / total for k, v in p.items()}, total


t_c = time.time()
frac_point, P_point = flux_split(mp.Vector3(0, 0, 0), layout=True)
frac_line, P_line = flux_split(mp.Vector3(0, line_len, 0))
print(f"C. point source: " + "  ".join(f"{k}={v:.4f}" for k, v in frac_point.items()) + f"  (total {P_point:.4g})")
print(f"C. line source : " + "  ".join(f"{k}={v:.4f}" for k, v in frac_line.items()) + f"  (total {P_line:.4g}, x-sides {frac_line['+x']+frac_line['-x']:.3f})")
bar_figure(list(frac_point), {"point source": list(frac_point.values()), f"line source ({line_len:g} um)": list(frac_line.values())},
           os.path.join(OUT, "04_flux_box.png"), ylabel="fraction of emitted power", reference=0.25, reference_label="isotropic: 0.25")

# convergence of the point-source split (should be 0.25 each by symmetry)
convergence = [{"resolution": RESOLUTION, "dpml": DPML, "max_dev_from_0.25": max(abs(v - 0.25) for v in frac_point.values()),
                "x_sides_line": frac_line["+x"] + frac_line["-x"]}]
for res, dpml in ((40, 1.0), (20, 2.0)):
    fp, _ = flux_split(mp.Vector3(0, 0, 0), resolution=res, dpml=dpml)
    fl, _ = flux_split(mp.Vector3(0, line_len, 0), resolution=res, dpml=dpml)
    convergence.append({"resolution": res, "dpml": dpml, "max_dev_from_0.25": max(abs(v - 0.25) for v in fp.values()),
                        "x_sides_line": fl["+x"] + fl["-x"]})
    print(f"convergence res={res} dpml={dpml}: point max|frac-0.25|={convergence[-1]['max_dev_from_0.25']:.2e}, line x-sides={convergence[-1]['x_sides_line']:.4f}")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"t0": t0, "fwidth": fwidth, "d_wall": d_wall, "r_front": r_front,
                   "ring_mean_abs_ez": ring, "cell_mean_abs_ez": everywhere,
                   "point_fractions": frac_point, "line_fractions": frac_line, "line_len": line_len,
                   "P_point": P_point, "P_line": P_line, "convergence": convergence,
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
