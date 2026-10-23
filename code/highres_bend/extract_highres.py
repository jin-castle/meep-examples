"""Recompute the centered bend's DFT fields and one verified update in Meep.

Run with the existing WSL pmp environment on one CPU:
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    /home/bgs43/miniforge3/envs/pmp/bin/python extract_highres.py
Outputs stay beside this script. Field arrays retain complex128 values; PNGs
show only their real parts, each with its own symmetric color scale.
"""

import os

for thread_variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[thread_variable] = "1"

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp
import meep.adjoint as mpa
import numpy as np
from autograd import numpy as npa
from meep.adjoint import utils


OUT = Path(__file__).resolve().parent
RESOLUTION = 60
NX = NY = 61
WAVELENGTH = 1.55
FREQUENCY = 1 / WAVELENGTH
FREQUENCY_WIDTH = 0.12 * FREQUENCY
SX, SY = 6.0, 5.0
DESIGN_SIDE = 1.0
GUIDE_WIDTH = 0.5
DECAY = 1e-10
MAX_RUN_TIME = 1000
EXTENT = [-SX / 2, SX / 2, -SY / 2, SY / 2]
DESIGN_EXTENT = [-0.5, 0.5, -0.5, 0.5]
SILICON, SILICA = mp.Medium(index=3.4), mp.Medium(index=1.44)
STARTED = time.monotonic()


def scalar(value):
    return float(np.real(np.asarray(value).squeeze()))


def fixed_guides():
    return [
        mp.Block(center=mp.Vector3(-SX / 4, 0), size=mp.Vector3(SX / 2, GUIDE_WIDTH), material=SILICON),
        mp.Block(center=mp.Vector3(0, SY / 4), size=mp.Vector3(GUIDE_WIDTH, SY / 2), material=SILICON),
    ]


class CapturedProblem(mpa.OptimizationProblem):
    """Keep display DFT monitors alongside the native gradient's D monitors."""

    capture_enabled = True

    def install_capture(self):
        self.capture_monitors = {
            "full": self.sim.add_dft_fields([mp.Ez], [FREQUENCY], center=mp.Vector3(), size=mp.Vector3(SX, SY), decimation_factor=1),
            "design": self.sim.add_dft_fields([mp.Ez], [FREQUENCY], center=mp.Vector3(), size=mp.Vector3(1, 1), decimation_factor=1),
        }

    def collect_capture(self):
        captured = {}
        for region_name, monitor in self.capture_monitors.items():
            x, y, z, weights = self.sim.get_array_metadata(dft_cell=monitor)
            captured[region_name] = {
                "Ez": np.array(self.sim.get_dft_array(monitor, mp.Ez, 0), copy=True),
                "x": np.asarray(x),
                "y": np.asarray(y),
            }
        captured["simulation_time"] = self.sim.meep_time()
        return captured

    def prepare_forward_run(self):
        super().prepare_forward_run()
        if self.capture_enabled:
            self.install_capture()

    def forward_run(self):
        super().forward_run()
        if self.capture_enabled:
            self.captured_forward = self.collect_capture()

    def adjoint_run(self):
        assert len(self.objective_functions) == 1 and not self.sim.k_point
        self.prepare_adjoint_run()
        self.sim.restart_fields()
        self.sim.clear_dft_monitors()
        self.sim.change_sources(self.adjoint_sources[0])
        self.adjoint_design_region_monitors = [utils.install_design_region_monitors(self.sim, self.design_regions, self.frequencies, self.decimation_factor)]
        if self.capture_enabled:
            self.install_capture()
        self.sim._evaluate_dft_objects()
        self.sim.run(*self.step_funcs, until_after_sources=mp.stop_when_dft_decayed(self.decay_by, self.minimum_run_time, self.maximum_run_time))
        if self.capture_enabled:
            self.captured_adjoint = self.collect_capture()
        self.current_state = "ADJ"


def outline_layout(axis, cropped=False):
    if cropped:
        axis.plot([-.5, -.5, .5, .5, -.5], [-.5, .5, .5, -.5, -.5], color="black", linewidth=1.8)
        axis.plot([-.5, -.5], [-.25, .25], color="black", linewidth=3)
        axis.plot([-.25, .25], [.5, .5], color="black", linewidth=3)
    else:
        axis.plot([-3, -.5, -.5, .5, .5, .25, .25], [-.25, -.25, -.5, -.5, .5, .5, 2.5], color="black", linewidth=1.1)
        axis.plot([-.25, -.25, -.5, -.5, -3], [2.5, .5, .5, .25, .25], color="black", linewidth=1.1)
        axis.add_patch(plt.Rectangle((-.5, -.5), 1, 1, fill=False, edgecolor="black", linewidth=.8, linestyle=(0, (3, 3))))


def save_field(region, filename, title, cropped):
    values = np.real(region["Ez"])
    limit = float(np.max(np.abs(values)))
    extent = DESIGN_EXTENT if cropped else EXTENT
    x, y = region["x"], region["y"]
    dx, dy = float(np.median(np.diff(x))), float(np.median(np.diff(y)))
    pixel_extent = [x[0] - dx / 2, x[-1] + dx / 2, y[0] - dy / 2, y[-1] + dy / 2]
    if cropped:
        fig, axis = plt.subplots(figsize=(4, 4), dpi=180)
        fig.subplots_adjust(0, 0, 1, 1)
        axis.imshow(values.T, origin="lower", extent=pixel_extent, cmap="RdBu", vmin=-limit, vmax=limit, interpolation="nearest")
        outline_layout(axis, True)
        axis.axis("off")
    else:
        fig, axis = plt.subplots(figsize=(9, 7.5), dpi=180)
        im = axis.imshow(values.T, origin="lower", extent=pixel_extent, cmap="RdBu", vmin=-limit, vmax=limit, interpolation="nearest")
        outline_layout(axis)
        axis.set(xlabel="x [um]", ylabel="y [um]", title=title)
        fig.colorbar(im, ax=axis, label="Re(Ez), Meep DFT units", shrink=.8)
        fig.tight_layout()
    axis.set_xlim(extent[:2])
    axis.set_ylim(extent[2:])
    fig.savefig(OUT / filename, dpi=180)
    plt.close(fig)
    return limit


def save_grid(values, filename, signed=False):
    fig, axis = plt.subplots(figsize=(4, 4), dpi=180)
    fig.subplots_adjust(0, 0, 1, 1)
    if signed:
        limit = float(np.max(np.abs(values)))
        axis.imshow(values.reshape(NX, NY).T, origin="lower", extent=DESIGN_EXTENT, cmap="RdBu", vmin=-limit, vmax=limit, interpolation="nearest")
    else:
        axis.imshow(values.reshape(NX, NY).T, origin="lower", extent=DESIGN_EXTENT, cmap="gray_r", vmin=0, vmax=1, interpolation="nearest")
    outline_layout(axis, True)
    axis.axis("off")
    axis.set_xlim(-.5, .5)
    axis.set_ylim(-.5, .5)
    fig.savefig(OUT / filename, dpi=180)
    plt.close(fig)


def save_raw_capture(capture, prefix, destination):
    for region_name in ("full", "design"):
        for key, value in capture[region_name].items():
            destination[f"{prefix}_{region_name}_{key}"] = value


def main():
    mp.verbosity(0)
    density = mp.MaterialGrid(mp.Vector3(NX, NY), SILICA, SILICON, grid_type="U_MEAN", do_averaging=False)
    region = mpa.DesignRegion(density, volume=mp.Volume(center=mp.Vector3(), size=mp.Vector3(1, 1)))
    sources = [mp.EigenModeSource(mp.GaussianSource(FREQUENCY, fwidth=FREQUENCY_WIDTH), eig_band=1, direction=mp.NO_DIRECTION, eig_kpoint=mp.Vector3(1, 0, 0), size=mp.Vector3(0, 2), center=mp.Vector3(-1.5, 0))]
    simulation = mp.Simulation(resolution=RESOLUTION, cell_size=mp.Vector3(SX, SY), boundary_layers=[mp.PML(1)], geometry=fixed_guides() + [mp.Block(center=mp.Vector3(), size=mp.Vector3(1, 1), material=density)], sources=sources, eps_averaging=False)
    output = mpa.EigenmodeCoefficient(simulation, mp.Volume(center=mp.Vector3(0, 1), size=mp.Vector3(2, 0)), mode=1)
    problem = CapturedProblem(simulation=simulation, objective_functions=lambda a: npa.abs(a) ** 2, objective_arguments=[output], design_regions=[region], frequencies=[FREQUENCY], decay_by=DECAY, maximum_run_time=MAX_RUN_TIME, decimation_factor=1)
    initial = np.full(NX * NY, .5)
    print("HIGHRES initial forward+adjoint", flush=True)
    objective, derivative = problem([initial], need_gradient=True)
    objective = scalar(objective)
    gradient = np.asarray(derivative).reshape(-1).copy()
    forward = problem.captured_forward
    adjoint = problem.captured_adjoint
    raw = {"density_initial": initial, "gradient": gradient}
    save_raw_capture(forward, "forward", raw)
    save_raw_capture(adjoint, "adjoint", raw)
    np.savez_compressed(OUT / "initial-checkpoint.npz", **raw)
    assert np.all(np.isfinite(gradient)) and np.linalg.norm(gradient) > 0
    direction = gradient / np.linalg.norm(gradient)
    expected = float(gradient @ direction)
    problem.capture_enabled = False
    gates = []
    for step in (.01, .03):
        print(f"HIGHRES finite difference step={step}", flush=True)
        plus = scalar(problem([initial + step * direction], need_gradient=False)[0])
        minus = scalar(problem([initial - step * direction], need_gradient=False)[0])
        observed = (plus - minus) / (2 * step)
        error = abs(observed - expected) / max(abs(observed), 1e-30)
        gate = {"step_l2": step, "finite_difference": observed, "adjoint": expected, "relative_error": error, "passed": bool(error < .02 and observed * expected > 0)}
        gates.append(gate)
        print("HIGHRES GATE " + json.dumps(gate), flush=True)
    if not all(gate["passed"] for gate in gates):
        (OUT / "failed-gate.json").write_text(json.dumps(gates, indent=2))
        raise RuntimeError("Adjoint directional derivative did not pass the 2% gate")
    trials = []
    accepted = None
    for maximum_density_change in (.15, .075, .0375, .01875):
        candidate = np.clip(initial + maximum_density_change * gradient / np.max(np.abs(gradient)), 0, 1)
        problem.capture_enabled = True
        candidate_value = scalar(problem([candidate], need_gradient=False)[0])
        trials.append({"max_density_change": maximum_density_change, "objective": candidate_value})
        print("HIGHRES UPDATE " + json.dumps(trials[-1]), flush=True)
        if candidate_value > objective:
            accepted = candidate
            updated_forward = problem.captured_forward
            break
    if accepted is None:
        raise RuntimeError("Backtracking did not produce an improving density update")
    raw["density_updated"] = accepted
    save_raw_capture(updated_forward, "updated_forward", raw)
    np.savez_compressed(OUT / "fields.npz", **raw)
    limits = {}
    for tag, capture in (("forward", forward), ("adjoint", adjoint), ("updated-forward", updated_forward)):
        limits[tag] = {
            "design_re_Ez_symmetric_limit": save_field(capture["design"], f"{tag}-design.png", tag, True),
            "full_re_Ez_symmetric_limit": save_field(capture["full"], f"{tag}-full.png", f"{tag} Re(Ez), resolution 60 pixels/um", False),
        }
    save_grid(gradient, "gradient-design.png", True)
    save_grid(initial, "density-initial.png")
    save_grid(accepted, "density-updated.png")
    result = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "meep_version": mp.__version__, "resolution": RESOLUTION, "pixels_per_um": RESOLUTION,
        "design_grid": [NX, NY], "design_variables": NX * NY, "density_indexing": "x*Ny+y; x,y increase; plot transposes with origin lower",
        "wavelength_um": WAVELENGTH, "frequency_inverse_um": FREQUENCY, "frequency_width": FREQUENCY_WIDTH,
        "cell_um": [SX, SY], "pml_um": 1, "design_extent_um": DESIGN_EXTENT, "full_extent_um": EXTENT,
        "indices": {"silicon": 3.4, "silica": 1.44}, "guide_width_um": GUIDE_WIDTH,
        "source_center_um": [-1.5, 0], "source_mode": 1, "output_monitor_center_um": [0, 1],
        "polarization": "2D Ez", "eps_averaging": False, "materialgrid_averaging": False,
        "dft_decay_by": DECAY, "maximum_run_time": MAX_RUN_TIME, "dft_decimation_factor": 1,
        "objective": "Unnormalized output mode-1 power |a_out|^2, optimizer/source units; not transmission efficiency",
        "objective_initial": objective, "objective_updated": candidate_value, "objective_ratio": candidate_value / objective,
        "update": {"method": "one projected gradient-ascent step with backtracking", "max_density_change": trials[-1]["max_density_change"], "trials": trials},
        "finite_difference_gate": gates,
        "adjoint_source": "Native mpa.EigenmodeCoefficient.place_adjoint_source(dJ/da) for |a_out|^2 at output; includes Meep discrete-time/source-Fourier and cell-volume normalization. Captured during same adjoint run used by mpa gradient.",
        "gradient_method": "mpa.DesignRegion.get_gradient uses retained complex forward/adjoint D fields and derivative of discretized MaterialGrid operator; displayed Re(Ez) maps alone do not determine gradient.",
        "color_map": "RdBu", "color_sign": "negative red; zero white; positive blue", "layout_color": "black contours; no opaque mask over DFT fields", "display_limits": limits,
        "gradient_symmetric_limit": float(np.max(np.abs(gradient))),
        "field_shape_full": list(forward["full"]["Ez"].shape), "field_shape_design": list(forward["design"]["Ez"].shape),
        "forward_time": forward["simulation_time"], "adjoint_time": adjoint["simulation_time"], "updated_forward_time": updated_forward["simulation_time"],
        "x_initial": initial.tolist(), "x_updated": accepted.tolist(), "gradient": gradient.tolist(),
        "cpu_threads": 1, "mpi_processes": mp.count_processors(), "elapsed_seconds": time.monotonic() - STARTED,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2))
    print("HIGHRES DONE " + json.dumps({key: result[key] for key in ("objective_initial", "objective_updated", "objective_ratio", "field_shape_full", "field_shape_design", "elapsed_seconds")}), flush=True)


if __name__ == "__main__":
    main()
