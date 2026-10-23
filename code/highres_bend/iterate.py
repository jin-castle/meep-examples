import argparse
import hashlib
import json
import shutil
import time
from pathlib import Path

import extract_highres as h
import numpy as np


def build_problem():
    mp, mpa = h.mp, h.mpa
    density = mp.MaterialGrid(mp.Vector3(h.NX, h.NY), h.SILICA, h.SILICON, grid_type="U_MEAN", do_averaging=False)
    region = mpa.DesignRegion(density, volume=mp.Volume(center=mp.Vector3(), size=mp.Vector3(1, 1)))
    source = mp.EigenModeSource(mp.GaussianSource(h.FREQUENCY, fwidth=h.FREQUENCY_WIDTH), eig_band=1, direction=mp.NO_DIRECTION, eig_kpoint=mp.Vector3(1, 0, 0), size=mp.Vector3(0, 2), center=mp.Vector3(-1.5, 0))
    sim = mp.Simulation(resolution=h.RESOLUTION, cell_size=mp.Vector3(h.SX, h.SY), boundary_layers=[mp.PML(1)], geometry=h.fixed_guides() + [mp.Block(center=mp.Vector3(), size=mp.Vector3(1, 1), material=density)], sources=[source], eps_averaging=False)
    output = mpa.EigenmodeCoefficient(sim, mp.Volume(center=mp.Vector3(0, 1), size=mp.Vector3(2, 0)), mode=1)
    return h.CapturedProblem(simulation=sim, objective_functions=lambda a: h.npa.abs(a)**2, objective_arguments=[output], design_regions=[region], frequencies=[h.FREQUENCY], decay_by=h.DECAY, maximum_run_time=h.MAX_RUN_TIME, decimation_factor=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=6)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    provenance = args.out / "executed-source"
    provenance.mkdir(exist_ok=True)
    hashes = {}
    for name in ("iterate.py", "extract_highres.py"):
        path = Path(__file__).with_name(name)
        shutil.copy2(path, provenance / name)
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    h.mp.verbosity(0)
    problem = build_problem()
    x = np.full(h.NX*h.NY, .5)
    records = []
    started = time.monotonic()
    for i in range(args.steps):
        checkpoint = args.out / f"{i:03d}.json"
        if checkpoint.exists():
            record = json.loads(checkpoint.read_text())
            raw = np.load(args.out / f"{i:03d}.npz")
            assert np.array_equal(x, raw["density_initial"])
            x = raw["density_updated"].copy()
            records.append(record)
            continue
        print(f"ITERATION {i} forward+adjoint", flush=True)
        before, derivative = problem([x], need_gradient=True)
        before = h.scalar(before)
        gradient = np.asarray(derivative).reshape(-1).copy()
        assert np.isfinite(gradient).all() and np.max(np.abs(gradient)) > 0
        if records:
            assert np.isclose(before, records[-1]["objective_after"], rtol=1e-8)
        raw = {"density_initial": x.copy(), "gradient": gradient}
        h.save_raw_capture(problem.captured_forward, "forward", raw)
        h.save_raw_capture(problem.captured_adjoint, "adjoint", raw)
        np.savez_compressed(args.out / f"{i:03d}-before.npz", **raw)
        times = {"forward": problem.captured_forward["simulation_time"], "adjoint": problem.captured_adjoint["simulation_time"]}
        gate = None
        if i == 1:
            direction = gradient / np.linalg.norm(gradient)
            epsilon = .01
            plus = h.scalar(problem([x + epsilon*direction], need_gradient=False)[0])
            minus = h.scalar(problem([x - epsilon*direction], need_gradient=False)[0])
            observed = (plus-minus)/(2*epsilon)
            expected = float(gradient @ direction)
            error = abs(observed-expected)/max(abs(observed), 1e-30)
            gate = {"epsilon": epsilon, "observed": observed, "adjoint": expected, "relative_error": error, "passed": bool(error < .02)}
            (args.out / "iteration1-gradient-gate.json").write_text(json.dumps(gate, indent=2))
            assert gate["passed"], gate
        trials = []
        for step in (.15, .075, .0375, .01875, .009375, .0046875, .00234375):
            candidate = np.clip(x + step*gradient/np.max(np.abs(gradient)), 0, 1)
            after = h.scalar(problem([candidate], need_gradient=False)[0])
            trials.append({"max_density_change": step, "objective": after})
            print(f"ITERATION {i} TRIAL " + json.dumps(trials[-1]), flush=True)
            if after > before:
                break
        else:
            raise RuntimeError(f"No improving update at iteration {i}")
        times["updated_forward"] = problem.captured_forward["simulation_time"]
        assert all(t < h.MAX_RUN_TIME for t in times.values())
        raw["density_updated"] = candidate.copy()
        h.save_raw_capture(problem.captured_forward, "updated_forward", raw)
        np.savez_compressed(args.out / f"{i:03d}.npz", **raw)
        record = {"iteration": i, "objective_before": before, "objective_after": after, "trials": trials, "raw": f"{i:03d}.npz", "simulation_times": times, "finite_difference_gate": gate, "elapsed_seconds": time.monotonic()-started}
        checkpoint.write_text(json.dumps(record, indent=2))
        records.append(record)
        x = candidate.copy()
        print("ACCEPTED " + json.dumps(record), flush=True)
    result = {"records": records, "meep_version": h.mp.__version__, "resolution": h.RESOLUTION, "cpu_threads": 1, "mpi_processes": h.mp.count_processors(), "source_sha256": hashes, "elapsed_seconds": time.monotonic()-started, "objective": "Unnormalized mode-1 output power |a_out|^2, not transmission efficiency", "caveat": "Finite saved projected-gradient steps; not a convergence claim"}
    (args.out / "result.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
