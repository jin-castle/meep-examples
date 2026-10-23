"""Layout figures for post 14 only (no time stepping). Same cells as extraction_efficiency.py.

Run:  python extraction_layouts.py      (~10 s)   -> ../assets/14/01_layout.png, 02_layout_edge.png
"""
import os
import sys

import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, annotated_layout   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "14")
FREQ, N_L, T_L, DPML, DAIR, L, RES = 1.0, 2.4, 0.7 / 2.4, 0.5, 1.0, 6.0, 80

# part A: cylindrical layer on a mirror
sr, sz = L + DPML, T_L + DAIR + DPML
src_pt = mp.Vector3(1.5 / RES, 0, -0.5 * sz + 0.5 * T_L)
sim = mp.Simulation(resolution=RES, cell_size=mp.Vector3(sr, 0, sz), dimensions=mp.CYLINDRICAL, m=-1,
                    boundary_layers=[mp.PML(DPML, direction=mp.R), mp.PML(DPML, direction=mp.Z, side=mp.High)],
                    sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.1 * FREQ), component=mp.Er, center=src_pt)],
                    geometry=[mp.Block(material=mp.Medium(index=N_L), center=mp.Vector3(0, 0, -0.5 * sz + 0.5 * T_L), size=mp.Vector3(mp.inf, mp.inf, T_L))])
sim.add_flux(FREQ, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * L, 0, 0.5 * sz - DPML), size=mp.Vector3(L, 0, 0)),
             mp.FluxRegion(center=mp.Vector3(L, 0, 0.5 * sz - DPML - 0.5 * DAIR), size=mp.Vector3(0, 0, DAIR)))
annotated_layout(sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(11, 3.6), axis_step=1.0, unit="um",
                 title="part A, cylindrical (r, z) cell: dipole in a layer (n = 2.4) on a ground plane; x = r, y = z",
                 params_text=f"wl=1.0 um, res 40 / {RES}\nt = 0.7 wl/n = {T_L:.3f} um", params_xy=(3.7, 0.33), pml_xy=(6.05, -0.6),
                 decay_point=(src_pt.x, src_pt.z), decay_text_xy=(1.4, -0.45),
                 labels=[Label("Er dipole at r = 1.5 px, height h", (src_pt.x, src_pt.z), (1.4, 0.05), step=3, color="red"),
                         Label("layer n = 2.4; bottom edge = PEC mirror (no PML)", (1.0, -0.7), (1.4, -0.2), step=2, color="black"),
                         Label("numerator: flux through top + outer r (air only)", (5.0, 0.5 * sz - DPML), (3.7, 0.05), step=5, color="blue")])
sim.reset_meep()

# part C: cleaved facet of a laser stack, 2D
RES_C, CLAD, ACT, SUB, PML_C, AIR_C, SIDE = 25, 0.5, 0.3, 1.0, 0.5, 1.0, 3.0
CX = PML_C + SIDE + AIR_C + PML_C
CY = PML_C + SUB + CLAD + ACT + CLAD + AIR_C + PML_C
SRC_C = mp.Vector3(-0.5 * CX + PML_C + SIDE - 0.5, -0.5 * CY + PML_C + SUB + CLAD + 0.5 * ACT)
x0, wx, y = -0.5 * CX + 0.5 * (PML_C + SIDE), PML_C + SIDE, -0.5 * CY
geom = []
for th, n in ((PML_C + SUB, 3.2), (CLAD, 1.5), (ACT, 2.3), (CLAD, 1.5)):
    geom.append(mp.Block(material=mp.Medium(index=n), center=mp.Vector3(x0, y + 0.5 * th), size=mp.Vector3(wx, th, mp.inf))); y += th
sim = mp.Simulation(resolution=RES_C, cell_size=mp.Vector3(CX, CY), k_point=mp.Vector3(0, 0, 0.0), kz_2d="real/imag", geometry=geom,
                    sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.1 * FREQ), component=mp.Ez, center=SRC_C)], boundary_layers=[mp.PML(PML_C)])
sim.add_flux(FREQ, 0, 1, mp.FluxRegion(center=mp.Vector3(0, 0.5 * CY - PML_C), size=mp.Vector3(CX - 2 * PML_C, 0)),
             mp.FluxRegion(center=mp.Vector3(0.5 * CX - PML_C, 0), size=mp.Vector3(0, CY - 2 * PML_C)),
             mp.FluxRegion(center=mp.Vector3(0.5 * CX - PML_C - 0.5 * AIR_C, -0.5 * CY + PML_C), size=mp.Vector3(AIR_C, 0), weight=-1.0))
annotated_layout(sim, os.path.join(OUT, "02_layout_edge.png"), dpml=PML_C, figsize=(6.6, 6.2), axis_step=1.0, unit="um",
                 title="part C: cleaved facet of a laser stack (2D), uniform along z",
                 params_text="res 25, kz step 0.02\nn: sub 3.2 / clad 1.5 / act 2.3", params_xy=(-1.9, -1.0), pml_xy=(-1.9, -1.9), decay_point=None,
                 labels=[Label("Ez dipole 0.5 um inside the facet", (SRC_C.x, SRC_C.y), (-1.9, 1.35), step=3, color="red"),
                         Label("active layer between two claddings", (-1.2, SRC_C.y), (-1.9, 0.95), step=2, color="black"),
                         Label("air flux: top, front, under the gap", (2.0, 0.9), (-0.4, 1.8), step=5, color="blue")])
print("layouts written")
