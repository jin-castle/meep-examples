"""Angular reflectance of an air/n=3.5 interface, with a fixed Bloch kx.

Adapted from NanoComp/meep python/examples/refl-angular.py and .ipynb,
commit f7811d4157ea22f19d4ca76bc41c71b6e055763e (GPL-2.0-or-later).
Adds a transmitted-flux monitor and portable NumPy/JSON output. Unit length: um.
Saved lesson results used Meep 1.33.0; this script does not require blog helpers.
"""

import argparse
import json
import math
from pathlib import Path
import time

import numpy as np


def fresnel_p(theta):
    """Power reflectance, air to lossless n=3.5, angle from the normal."""
    theta_t = np.arcsin(np.sin(theta) / 3.5)
    return ((np.cos(theta_t) - 3.5 * np.cos(theta)) /
            (np.cos(theta_t) + 3.5 * np.cos(theta))) ** 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolution", type=float, default=200,
                        help="pixels per um (saved ladder: 50, 100, 200)")
    parser.add_argument("--theta", type=float, nargs="+", default=[0, 45, 75],
                        help="angle in degrees at wavelength 0.8 um")
    parser.add_argument("--out", type=Path, default=Path("results-angular"))
    parser.add_argument("--tag", default="angular")
    args = parser.parse_args()
    if args.resolution <= 0 or any(t < 0 or t >= 90 for t in args.theta):
        parser.error("resolution must be positive; angles must satisfy 0 <= theta < 90")

    import meep as mp

    args.out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    size_z, dpml = 12.0, 1.0
    fmin, fmax = 1 / 0.8, 1 / 0.4
    fcen, df, nfreq = (fmin + fmax) / 2, fmax - fmin, 50
    rows = {name: [] for name in ("theta", "kx", "R", "T", "inc",
                                  "t_end_empty", "steps_empty",
                                  "t_end_slab", "steps_slab")}
    trace_t, trace_v, dft_e = np.zeros(0), np.zeros(0), np.zeros(0)

    for angle in args.theta:
        radians = math.radians(angle)
        k = mp.Vector3(z=fmin).rotate(mp.Vector3(y=1), radians)
        sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df),
                             component=mp.Ex, center=mp.Vector3(z=-5))]
        material = [mp.Block(mp.Vector3(mp.inf, mp.inf, size_z / 2),
                             center=mp.Vector3(z=size_z / 4),
                             material=mp.Medium(index=3.5))]
        measured = {}
        for label, geometry in (("empty", []), ("slab", material)):
            sim = mp.Simulation(cell_size=mp.Vector3(z=size_z),
                                geometry=geometry, sources=sources,
                                boundary_layers=[mp.PML(dpml)], k_point=k,
                                dimensions=1 if angle == 0 else 3,
                                resolution=args.resolution)
            reflection = sim.add_flux(fcen, df, nfreq,
                                     mp.FluxRegion(center=mp.Vector3(z=-3)))
            transmission = sim.add_flux(fcen, df, nfreq,
                                       mp.FluxRegion(center=mp.Vector3(z=2)))
            if label == "slab":
                sim.load_minus_flux_data(reflection, empty_data)

            steps, samples_t, samples_v = [], [], []
            if angle == args.theta[0] and label == "empty":
                def sample(s):
                    samples_t.append(s.meep_time())
                    samples_v.append(float(np.real(s.get_field_point(mp.Ex, mp.Vector3(z=-4.5)))))
                steps.append(mp.at_every(0.05, sample))
            dft = (sim.add_dft_fields([mp.Ex], [fmin, fcen, fmax],
                                     center=mp.Vector3(), size=mp.Vector3(z=10))
                   if angle == args.theta[0] and label == "slab" else None)
            sim.run(*steps, until_after_sources=mp.stop_when_fields_decayed(
                50, mp.Ex, mp.Vector3(z=-5), 1e-9))
            measured[label] = {"refl": np.array(mp.get_fluxes(reflection)),
                               "tran": np.array(mp.get_fluxes(transmission)),
                               "time": sim.meep_time(), "steps": sim.timestep()}
            if label == "empty":
                empty_data = sim.get_flux_data(reflection)
                freqs = np.array(mp.get_flux_freqs(reflection))
                if samples_t:
                    trace_t, trace_v = np.array(samples_t), np.array(samples_v)
            if dft is not None:
                dft_e = np.array([sim.get_dft_array(dft, mp.Ex, i) for i in range(3)])
            sim.reset_meep()

        incident = measured["empty"]["refl"]
        rows["theta"].append(angle)
        rows["kx"].append(k.x)
        rows["inc"].append(incident)
        rows["R"].append(-measured["slab"]["refl"] / incident)
        rows["T"].append(measured["slab"]["tran"] / incident)
        for label in ("empty", "slab"):
            rows[f"t_end_{label}"].append(measured[label]["time"])
            rows[f"steps_{label}"].append(measured[label]["steps"])

    actual_angles = np.arcsin(np.array(rows["kx"])[:, None] / freqs[None, :])
    analytic = fresnel_p(actual_angles)
    r, t = np.array(rows["R"]), np.array(rows["T"])
    metrics = {"fresnel_max_abs_error": float(np.abs(r - analytic).max()),
               "energy_max_abs_residual": float(np.abs(r + t - 1).max())}
    if mp.am_master():
        np.savez_compressed(args.out / f"{args.tag}.npz", freqs=freqs,
                            **{key: np.array(rows[key]) for key in ("theta", "kx", "R", "T", "inc")},
                            trace_t=trace_t, trace_v=trace_v, dftE=dft_e,
                            sz=size_z, theta_actual_deg=np.degrees(actual_angles), R_fresnel=analytic)
        report = {key: np.asarray(value).tolist() for key, value in rows.items()}
        report.update(res=args.resolution, meep=mp.__version__, metrics=metrics,
                      angle_convention="input theta is defined at fmin=1/0.8; kx is fixed",
                      wall=time.perf_counter() - start)
        (args.out / f"{args.tag}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(metrics))


if __name__ == "__main__":
    main()
