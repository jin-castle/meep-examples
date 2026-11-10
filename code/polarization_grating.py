"""Liquid-crystal polarization grating: Ez +/- i Ey selects a diffraction order.
Adapted from NanoComp/meep polarization_grating.py, GPL-2.0-or-later,
commit f7811d4157ea22f19d4ca76bc41c71b6e055763e. Unit length: um.
Adds portable complex-field data and explicit signed DiffractedPlanewave powers.
This CLI reproduces the circular-input demonstration, not the linear sweep.
"""
import argparse
import json
import math
import os
import time

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--resolution", type=float, default=50)
ap.add_argument("--phase", type=float, default=0.5, help="delta_n * total_thickness / wavelength")
ap.add_argument("--chir", type=int, default=1, help="+1: Ez + iEy, -1: Ez - iEy")
ap.add_argument("--tag", default="circ")
ap.add_argument("--out", default="out21")
a = ap.parse_args()
if a.resolution <= 0 or a.phase <= 0 or a.chir not in (-1, 1):
    ap.error("resolution and phase must be positive; chir must be -1 or 1")
import meep as mp
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
dpml, dsub, dpad = 1.0, 1.0, 1.0
n_0, delta_n, wvl, gp = 1.55, 0.159, 0.54, 6.5
fcen = 1 / wvl
dd = a.phase * wvl / delta_n          # 총 두께
d = 0.5 * dd                          # uniaxial: pol_grating(0.5*dd, 0, ...)
ph = 0.0
sx = dpml + dsub + d + d + dpad + dpml
sy = gp
cell = mp.Vector3(sx, sy, 0)
pml = [mp.PML(thickness=dpml, direction=mp.X)]
epsilon_diag = mp.Matrix(mp.Vector3(n_0 ** 2, 0, 0), mp.Vector3(0, n_0 ** 2, 0), mp.Vector3(0, 0, (n_0 + delta_n) ** 2))


def phi(p):
    xx = p.x - (-0.5 * sx + dpml + dsub)
    if (xx >= 0) and (xx <= d):
        return math.pi * p.y / gp + ph * xx / d
    return math.pi * p.y / gp - ph * xx / d + 2 * ph


def lc_mat(p):
    Rx = mp.Matrix(mp.Vector3(1, 0, 0), mp.Vector3(0, math.cos(phi(p)), math.sin(phi(p))), mp.Vector3(0, -math.sin(phi(p)), math.cos(phi(p))))
    e = Rx * epsilon_diag * Rx.transpose()
    return mp.Medium(epsilon_diag=mp.Vector3(e[0].x, e[1].y, e[2].z), epsilon_offdiag=mp.Vector3(e[1].x, e[2].x, e[2].y))


geometry = [mp.Block(center=mp.Vector3(-0.5 * sx + 0.5 * (dpml + dsub)), size=mp.Vector3(dpml + dsub, mp.inf, mp.inf), material=mp.Medium(index=n_0)),
            mp.Block(center=mp.Vector3(-0.5 * sx + dpml + dsub + d), size=mp.Vector3(2 * d, mp.inf, mp.inf), material=lc_mat)]
src_pt = mp.Vector3(-0.5 * sx + dpml + 0.3 * dsub, 0, 0)
sources = [mp.Source(mp.GaussianSource(fcen, fwidth=0.05 * fcen), component=mp.Ez, center=src_pt, size=mp.Vector3(0, sy, 0)),
           mp.Source(mp.GaussianSource(fcen, fwidth=0.05 * fcen), component=mp.Ey, center=src_pt, size=mp.Vector3(0, sy, 0), amplitude=1j * a.chir)]
tran_pt = mp.Vector3(0.5 * sx - dpml - 0.5 * dpad, 0, 0)
sim = mp.Simulation(resolution=a.resolution, cell_size=cell, boundary_layers=pml, k_point=mp.Vector3(), sources=sources, default_material=mp.Medium(index=n_0))
tf = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=tran_pt, size=mp.Vector3(0, sy, 0)))
sim.run(until_after_sources=100)
inp = mp.get_fluxes(tf)[0]
sim.reset_meep()
sim = mp.Simulation(resolution=a.resolution, cell_size=cell, boundary_layers=pml, k_point=mp.Vector3(), sources=sources, geometry=geometry)
mon = sim.add_mode_monitor(fcen, 0, 1, mp.FluxRegion(center=tran_pt, size=mp.Vector3(0, sy, 0)))
dmap = sim.add_dft_fields([mp.Ez, mp.Ey], [fcen], center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml, sy))
steps = []
sim.run(*steps, until_after_sources=300)
orders = {}
for m in (-1, 0, 1):
    pw = {}
    for pol, (S, P) in (("S", (1, 0)), ("P", (0, 1))):
        r = sim.get_eigenmode_coefficients(mon, mp.DiffractedPlanewave((0, m, 0), mp.Vector3(0, 1, 0), S, P))
        pw[pol] = float(abs(r.alpha[0, 0, 0]) ** 2 / inp) if r is not None else 0.0
    orders[m] = dict(S=pw["S"], P=pw["P"], total=pw["S"] + pw["P"])
Tf = mp.get_fluxes(mon)[0] / inp
Ez = sim.get_dft_array(dmap, mp.Ez, 0)
Ey = sim.get_dft_array(dmap, mp.Ey, 0)
eps = sim.get_array(component=mp.Dielectric, center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml, sy))
summ = dict(res=a.resolution, meep=mp.__version__, phase=a.phase, chir=a.chir, dd=dd, sx=sx, orders=orders, Tflux=float(Tf), angle_analytic=math.degrees(math.asin(wvl / gp)),
            steps=sim.timestep(), wall=time.time() - T0)
if mp.am_master():
    np.savez_compressed(os.path.join(a.out, f"{a.tag}.npz"), Ez=Ez, Ey=Ey, eps=eps, extent=np.array([-(sx - 2 * dpml) / 2, (sx - 2 * dpml) / 2, -sy / 2, sy / 2]))
    json.dump(summ, open(os.path.join(a.out, f"{a.tag}.json"), "w"), indent=1, default=float)
    print("RESULT " + json.dumps(summ, default=float), flush=True)
