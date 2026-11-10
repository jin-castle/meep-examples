"""Waveguide taper: compare backward fundamental-mode power and signed flux.
Adapted from NanoComp/meep mode-decomposition.py, GPL-2.0-or-later,
commit f7811d4157ea22f19d4ca76bc41c71b6e055763e. Unit length: um.
Retains the saved diagnostic setup; negative R_flux is a failed measurement,
not a physical reflectance or a validated convergence result.
"""
import argparse
import json
import os
import time

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--resolution", type=float, default=25)
ap.add_argument("--Lt", type=float, nargs="+", default=[1, 2, 4, 8])
ap.add_argument("--tag", default="")
ap.add_argument("--out", default="out27")
a = ap.parse_args()
if a.resolution <= 0 or any(v <= 0 for v in a.Lt):
    ap.error("resolution and taper lengths must be positive")
import meep as mp
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
w1, w2, Lw, dair, dpml_x, dpml_y = 1.0, 2.0, 10.0, 3.0, 6.0, 2.0
sy = dpml_y + dair + w2 + dair + dpml_y
Si = mp.Medium(epsilon=12.0)
bl = [mp.PML(dpml_x, direction=mp.X), mp.PML(dpml_y, direction=mp.Y)]
fcen = 1 / 6.67
sym = [mp.Mirror(mp.Y)]
P = mp.ODD_Z + mp.EVEN_Y
rows = []
extra = {}
for Lt in a.Lt:
    sx = dpml_x + Lw + Lt + Lw + dpml_x
    src_pt = mp.Vector3(-0.5 * sx + dpml_x + 0.2 * Lw)
    src = [mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=0.2 * fcen), center=src_pt, size=mp.Vector3(y=sy - 2 * dpml_y), eig_match_freq=True, eig_parity=P)]
    mon_pt = mp.Vector3(-0.5 * sx + dpml_x + 0.7 * Lw)
    straight = [mp.Vector3(-0.5 * sx - 1, 0.5 * w1), mp.Vector3(0.5 * sx + 1, 0.5 * w1), mp.Vector3(0.5 * sx + 1, -0.5 * w1), mp.Vector3(-0.5 * sx - 1, -0.5 * w1)]
    taper = [mp.Vector3(-0.5 * sx - 1, 0.5 * w1), mp.Vector3(-0.5 * Lt, 0.5 * w1), mp.Vector3(0.5 * Lt, 0.5 * w2), mp.Vector3(0.5 * sx + 1, 0.5 * w2),
             mp.Vector3(0.5 * sx + 1, -0.5 * w2), mp.Vector3(0.5 * Lt, -0.5 * w2), mp.Vector3(-0.5 * Lt, -0.5 * w1), mp.Vector3(-0.5 * sx - 1, -0.5 * w1)]
    rec = {}
    for lab, verts in (("wg", straight), ("taper", taper)):
        sim = mp.Simulation(resolution=a.resolution, cell_size=mp.Vector3(sx, sy), boundary_layers=bl, geometry=[mp.Prism(verts, height=mp.inf, material=Si)],
                            sources=src, symmetries=sym)
        flux = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mon_pt, size=mp.Vector3(y=sy - 2 * dpml_y)))
        tflux = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * sx - dpml_x - 0.5 * Lw), size=mp.Vector3(y=sy - 2 * dpml_y)))
        if lab == "taper":
            sim.load_minus_flux_data(flux, inc_data)
        steps = []
        tv = {"t": [], "v": []}
        dft = None
        if lab == "wg" and Lt == a.Lt[0]:
            steps.append(mp.at_every(0.5, lambda s_: (tv["t"].append(s_.meep_time()), tv["v"].append(float(np.real(s_.get_field_point(mp.Ez, src_pt + mp.Vector3(1))))))))
        if lab == "taper" and Lt == max(a.Lt):
            dft = sim.add_dft_fields([mp.Ez], [fcen], center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml_x, sy - 2 * dpml_y))
        sim.run(*steps, until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mon_pt, 1e-9))
        c = sim.get_eigenmode_coefficients(flux, [1], eig_parity=P)
        rec[lab] = dict(alpha=c.alpha[0, 0, :], flux=mp.get_fluxes(flux)[0], tflux=mp.get_fluxes(tflux)[0], t=sim.meep_time(), n=sim.timestep())
        if lab == "wg":
            inc_data = sim.get_flux_data(flux)
            if tv["t"]:
                extra["trace_t"], extra["trace_v"] = np.array(tv["t"]), np.array(tv["v"])
        if dft is not None:
            extra["Ez"] = sim.get_dft_array(dft, mp.Ez, 0)
            extra["eps"] = sim.get_array(component=mp.Dielectric, center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml_x, sy - 2 * dpml_y))
            extra["Lt_map"] = Lt
        sim.reset_meep()
    inc_a = abs(rec["wg"]["alpha"][0]) ** 2
    row = dict(Lt=Lt, R_coeff=abs(rec["taper"]["alpha"][1]) ** 2 / inc_a, R_flux=-rec["taper"]["flux"] / rec["wg"]["flux"],
               T_flux=rec["taper"]["tflux"] / rec["wg"]["tflux"], T_coeff_in=abs(rec["taper"]["alpha"][0]) ** 2 / inc_a,
               t_wg=rec["wg"]["t"], n_wg=rec["wg"]["n"], t_taper=rec["taper"]["t"], n_taper=rec["taper"]["n"], wg_mode_over_flux=inc_a / rec["wg"]["flux"])
    rows.append(row)
    row["R_flux_is_nonnegative"] = bool(row["R_flux"] >= 0)
    row["residual_forward_coeff_power"] = row["T_coeff_in"]
    if mp.am_master():
        print(f"refl:, {Lt:g}, {row['R_coeff']:.8f}, {row['R_flux']:.8f}  T_flux {row['T_flux']:.6f}", flush=True)
tag = a.tag or f"md_r{a.resolution:g}"
if mp.am_master():
    json.dump(dict(res=a.resolution, meep=mp.__version__, rows=rows, wall=time.time() - T0), open(os.path.join(a.out, f"{tag}.json"), "w"), indent=1, default=float)
    if extra:
        np.savez_compressed(os.path.join(a.out, f"{tag}.npz"), **extra)
