#!/usr/bin/env python3
"""Execute unchanged upstream Gauss2d.py and add read-only sampling callbacks.

The added samples reconstruct the monochromatic field over the final two
periods; they do not change geometry, source, grid, Courant factor or runtime.
Original output callbacks still write epsilon, Ez and instantaneous E squared.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import h5py
import meep as mp
import numpy as np
import scipy


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chi", type=float, required=True)
    args = parser.parse_args()
    upstream = args.upstream.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    source = upstream / "scripts/Gauss_2d/Gauss2d.py"
    sys.path.insert(0, str(upstream))
    import optbeam

    spec = importlib.util.spec_from_file_location("upstream_gauss", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_run = mp.Simulation.run
    start = time.perf_counter()
    sampled_times, preview = [], []
    gram = np.zeros((3, 3))
    rhs = None
    sum_squares = None
    final_sim = None

    def record(sim):
        nonlocal rhs, sum_squares, final_sim
        t = sim.meep_time()
        if t < 10 - 2 / 12 - 1e-7:
            return
        ez = sim.get_array(component=mp.Ez)
        basis = np.array([np.cos(2 * np.pi * 12 * t),
                          np.sin(2 * np.pi * 12 * t), 1.0])
        if rhs is None:
            rhs = np.zeros((3, *ez.shape))
            sum_squares = np.zeros_like(ez)
        gram[:] += np.outer(basis, basis)
        rhs[:] += basis[:, None, None] * ez
        sum_squares[:] += ez ** 2
        sampled_times.append(float(t))
        preview.append(ez[::3, ::3].astype(np.float32))
        final_sim = sim

    def sampled_run(sim, *steps, **kwargs):
        return original_run(sim, *steps, mp.at_every(1 / (12 * 24), record), **kwargs)

    mp.Simulation.run = sampled_run
    os.chdir(output)
    original_args = SimpleNamespace(interface="planar", s_pol=True, ref_medium=0,
                                    n1=1.54, n2=1.0, kw_0=8, kr_w=60,
                                    kr_c=150, chi_deg=args.chi)
    try:
        module.main(original_args)
    finally:
        mp.Simulation.run = original_run
    if final_sim is None or len(sampled_times) < 20:
        raise RuntimeError("Insufficient samples from the original simulation")
    coefficients = np.linalg.solve(gram, rhs.reshape(3, -1)).reshape(rhs.shape)
    phasor = coefficients[0] + 1j * coefficients[1]
    residual = sum_squares - np.einsum("ixy,ixy->xy", coefficients, rhs)
    relative_residual = float(np.sqrt(np.maximum(residual.sum(), 0)
                                     / sum_squares.sum()))
    x, y, z, weights = final_sim.get_array_metadata()
    epsilon = final_sim.get_array(component=mp.Dielectric)
    ez_final = final_sim.get_array(component=mp.Ez)
    np.savez_compressed(output / "fields.npz", x=x, y=y, epsilon=epsilon,
                        ez=ez_final, phasor=phasor, dc=coefficients[2],
                        mean_ez2=abs(phasor) ** 2 / 2,
                        preview=np.stack(preview), times=sampled_times,
                        preview_x=x[::3], preview_y=y[::3])
    metadata = dict(
        passed=bool(np.isfinite(phasor).all() and np.isfinite(epsilon).all()
                    and relative_residual < 0.05),
        source_sha256=sha256(source),
        upstream_commit="ca145119e5bd0f0804d846ea42e35e4c3daa91de",
        unchanged_original_script=True,
        changes="Wrapper adds read-only final-two-period field samples only",
        scheme_unavailable="No meep, meep-mpi or guile executable in the existing environment",
        physical=vars(original_args),
        numerical=dict(cell=[5, 5], pml=0.25, vacuum_frequency=12,
                       resolution=10 * 1.54 * 12, pixels_per_dense_wavelength=10,
                       courant=0.5, runtime=10, optical_periods=120,
                       unchanged_default_numerics=True, grid_shape=list(phasor.shape)),
        sampling=dict(count=len(sampled_times), start=sampled_times[0],
                      end=sampled_times[-1],
                      harmonic_fit_relative_l2_residual=relative_residual,
                      formula="Ez(t)=Re(phasor*exp(-i*2*pi*12*t))+dc",
                      intensity="mean(Ez^2)=abs(phasor)^2/2, fitted over final two periods; not Poynting flux",
                      animation="actual FDTD snapshots; every third grid point for display only"),
        environment=dict(python=sys.version, meep=mp.__version__, optbeam=optbeam.__version__,
                         numpy=np.__version__, scipy=scipy.__version__, h5py=h5py.__version__,
                         platform=platform.platform(), mpi_processes=mp.count_processors(),
                         threads={k: os.environ.get(k) for k in
                                  ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"]}),
        elapsed_seconds=time.perf_counter()-start,
        command=sys.argv,
    )
    (output / "run.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("RESULT", json.dumps(metadata, indent=2), flush=True)
    if not metadata["passed"]:
        raise RuntimeError("Nonfinite arrays or excessive harmonic fit residual")


if __name__ == "__main__":
    main()
