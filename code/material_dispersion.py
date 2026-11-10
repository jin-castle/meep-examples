"""Bulk Lorentz-medium modes at real Bloch wavevectors.

Adapted from NanoComp/meep python/examples/material-dispersion.py @ f7811d4157ea22f19d4ca76bc41c71b6e055763e.
The saved lesson data used Meep 1.33.0. Upstream physics is retained;
only command-line output/resolution controls and JSON export are added.
Meep source license: GPL-2.0-or-later (see repository LICENSES).
"""
import argparse
import os as _o

_parser = argparse.ArgumentParser(description=__doc__)
_parser.add_argument('--out', default='results', help='Output directory')
_parser.add_argument('--resolution', type=int, default=20, help='Grid pixels per unit length')
_args = _parser.parse_args()
if _args.resolution <= 0:
    _parser.error('--resolution must be positive')
_o.makedirs(_args.out, exist_ok=True)
_o.chdir(_args.out)

import meep as mp

cell = mp.Vector3()
resolution = _args.resolution

# We'll use a dispersive material with two polarization terms, just for
# illustration.  The first one is a strong resonance at omega=1.1,
# which leads to a polaritonic gap in the dispersion relation.  The second
# one is a weak resonance at omega=0.5, whose main effect is to add a
# small absorption loss around that frequency.

susceptibilities = [
    mp.LorentzianSusceptibility(frequency=1.1, gamma=1e-5, sigma=0.5),
    mp.LorentzianSusceptibility(frequency=0.5, gamma=0.1, sigma=2e-5),
]

default_material = mp.Medium(epsilon=2.25, E_susceptibilities=susceptibilities)

fcen = 1.0
df = 2.0

sources = [
    mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ez, center=mp.Vector3())
]

kmin = 0.3
kmax = 2.2
k_interp = 99

kpts = mp.interpolate(k_interp, [mp.Vector3(kmin), mp.Vector3(kmax)])

sim = mp.Simulation(
    cell_size=cell,
    geometry=[],
    sources=sources,
    default_material=default_material,
    resolution=resolution,
)

all_freqs = sim.run_k_points(200, kpts)  # a list of lists of frequencies

for fs, kx in zip(all_freqs, [v.x for v in kpts]):
    for f in fs:
        print(f"eps:, {f.real:.6g}, {f.imag:.6g}, {(kx / f) ** 2:.6g}")

# Save the computed result for inspection and plotting.
if mp.am_master():
    import json as _j
    _rows = [[v.x, f.real, f.imag] for fs, v in zip(all_freqs, kpts) for f in fs]
    _j.dump(dict(rows=_rows), open("matdisp.json", "w"))
