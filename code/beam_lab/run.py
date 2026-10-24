"""Run Beam Lab's independently specified aperture/geometry comparisons.

Each case starts a new Meep simulation. A continuous electric-current sheet
excites both propagation directions; stored fields cover the forward region.
DFT accumulation begins only after the initial settling interval.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import time

for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"

import numpy as np
from scipy.interpolate import RegularGridInterpolator
from profiles import airy_aperture, boundary_x, gaussian, laguerre_p0, phase_winding


CASES = {
    "gaussian_flat": {"kind": "gaussian", "curvature": 0.0},
    "gaussian_concave": {"kind": "gaussian", "curvature": 0.10},
    "gaussian_convex": {"kind": "gaussian", "curvature": -0.10},
    "lg_plus2": {"kind": "lg", "charge": 2},
    "lg_minus2": {"kind": "lg", "charge": -2},
    "airy_alpha008": {"kind": "airy", "alpha": 0.08},
    "airy_alpha020": {"kind": "airy", "alpha": 0.20},
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_case(name, root):
    import meep as mp

    started = time.perf_counter()
    config = dict(CASES[name])
    kind = config["kind"]
    is3d = kind == "lg"
    cell = (9.0, 7.0, 7.0) if is3d else (12.0, 10.0 if kind == "airy" else 8.0, 0.0)
    resolution = 12 if is3d else 20
    pml, frequency = 0.8, 1.0
    source_x = -3.3 if is3d else -4.5
    aperture = cell[1] / 2 - pml - 0.1
    config.update(cell=list(cell), resolution=resolution, pml=pml, frequency=frequency,
                  source_x=source_x, aperture_half_width=aperture,
                  settle_time=24.0, integration_time=8.0,
                  source_type="Ez electric-current sheet; bidirectional emission",
                  n1=1.0, n2=1.5 if kind == "gaussian" else 1.0)
    if kind == "gaussian":
        config.update(waist=0.9, angle_deg=20.0, boundary="x = curvature*y^2; n2 for x >= boundary")
        amplitude = lambda p: complex(gaussian(p.y, config["waist"], frequency, config["angle_deg"]))
    elif is3d:
        config.update(waist=1.0, radial_order=0)
        amplitude = lambda p: complex(laguerre_p0(p.y, p.z, config["waist"], config["charge"]))
    else:
        config.update(scale=0.6)
        # Precompute the normalization once, not once per source grid point.
        grid = np.linspace(-aperture, aperture, 16385)
        profile = airy_aperture(grid, config["scale"], config["alpha"], aperture)
        amplitude = lambda p: complex(np.interp(p.y, grid, profile, left=0, right=0))
    source = mp.Source(mp.ContinuousSource(frequency=frequency, width=2.0),
                       component=mp.Ez, center=mp.Vector3(source_x, 0, 0),
                       size=mp.Vector3(0, 2 * aperture, 2 * aperture if is3d else 0),
                       amp_func=amplitude)
    kwargs = {}
    if kind == "gaussian":
        low, high = mp.Medium(index=1), mp.Medium(index=1.5)
        kwargs["material_function"] = lambda p: high if p.x >= boundary_x(p.y, config["curvature"]) else low
    sim = mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution,
                        dimensions=3 if is3d else 2, boundary_layers=[mp.PML(pml)],
                        sources=[source], force_complex_fields=True, **kwargs)
    sim.run(until=config["settle_time"])
    lower = source_x + 0.3
    upper = cell[0] / 2 - pml - 0.1
    center = mp.Vector3((lower + upper) / 2, 0, 0)
    size = mp.Vector3(upper - lower, 2 * aperture, 2 * aperture if is3d else 0)
    components = [("ex", mp.Ex), ("ey", mp.Ey), ("ez", mp.Ez)] if is3d else [("ez", mp.Ez)]
    monitor = sim.add_dft_fields([component for _, component in components], [frequency], center=center,
                                 size=size, yee_grid=False, decimation_factor=1)
    actual_start = sim.meep_time()
    sim.run(until=config["integration_time"])
    actual_end = sim.meep_time()
    x, y, z, _ = sim.get_array_metadata(dft_cell=monitor)
    shape = (len(x), len(y), len(z))
    arrays = {key: np.asarray(sim.get_dft_array(monitor, component, 0)).reshape(shape)
              for key, component in components}
    if not is3d:
        arrays.update(ex=np.zeros(shape, dtype=complex), ey=np.zeros(shape, dtype=complex))
    arrays["epsilon"] = np.asarray(sim.get_array(center=center, size=size, component=mp.Dielectric)).reshape(shape)
    arrays.update(x=np.asarray(x), y=np.asarray(y), z=np.asarray(z))
    finite = all(np.all(np.isfinite(value)) for value in arrays.values())
    peak = float(np.max(np.abs(arrays["ez"])))
    if not finite or peak == 0:
        raise RuntimeError(f"{name}: invalid or empty field")
    winding = None
    if is3d:
        theta = np.linspace(0, 2 * np.pi, 512, endpoint=False)
        radius = config["waist"]
        ix = int(np.argmin(np.abs(x - (source_x + 0.65))))
        points = np.column_stack((radius * np.cos(theta), radius * np.sin(theta)))
        values = RegularGridInterpolator((y, z), arrays["ez"][ix])(points)
        measured = phase_winding(values)
        winding = {"component": "Ez DFT field", "plane_x": float(x[ix]), "radius": radius,
                   "samples": len(theta), "orientation": "theta=atan2(z,y), increasing theta",
                   "source_charge": config["charge"], "measured": measured,
                   "minimum_to_maximum_amplitude": float(np.min(np.abs(values)) / np.max(np.abs(values))),
                   "matches_source_charge": abs(measured - config["charge"]) < 0.05}
        if not winding["matches_source_charge"]:
            raise RuntimeError(f"{name}: measured field winding disagrees with source: {winding}")
    out = root / name
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "fields.npz", **arrays)
    report = {"schema_version": 1, "case": name, "params": config, "field_shape": list(shape),
              "axis_order": "x,y,z", "field_kind": "complex single-frequency DFT; centered grid; unnormalized amplitude",
              "polarization": "vector 3D" if is3d else "2D Ez polarization; Ex=Ey=0 by symmetry",
              "monitor": {"start_time": actual_start, "end_time": actual_end,
                          "x_min": float(x[0]), "x_max": float(x[-1]), "yee_grid": False},
              "finite": bool(finite), "ez_peak": peak, "winding": winding,
              "meep_version": mp.__version__, "cpu_threads": 1,
              "elapsed_seconds": time.perf_counter() - started,
              "source_hashes": {p.name: digest(p) for p in (Path(__file__), Path(__file__).with_name("profiles.py"))},
              "fields_sha256": digest(out / "fields.npz"),
              "provenance": "Beam Lab analytic electric-current apertures and independently specified Meep experiment",
              "limitations": ["visualization grid; no resolution/PML convergence study", "no normalized power or efficiency claim", "electric-current sheet emits in both directions", "finite settling time; no steady-state convergence claim"],
              "passed": True}
    (out / "case.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    sim.reset_meep()
    print("BEAM_LAB_CASE " + json.dumps(report), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--suite", action="store_true")
    choice.add_argument("--case", choices=CASES)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    names = list(CASES) if args.suite else [args.case]
    results = []
    for name in names:
        results.append(run_case(name, args.output))
        summary = {"cases": [r["case"] for r in results], "complete": len(results) == len(names),
                   "passed": all(r["passed"] for r in results), "requested": names}
        (args.output / "suite.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
