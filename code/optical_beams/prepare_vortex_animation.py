import argparse
import json
from pathlib import Path

import h5py
import numpy as np
from scipy.ndimage import map_coordinates
import vtk

from prepare_vortex_scene import digest, extract, texture


def reconstruct(a, b, cross, phase, tolerance):
    cosine, sine = np.cos(phase), np.sin(phase)
    value = a * cosine**2 + b * sine**2 + 2 * cross * sine * cosine
    minimum = float(value.min())
    if not np.isfinite(value).all() or minimum < -tolerance:
        raise ValueError(f"Invalid reconstructed squared field: minimum={minimum}")
    clipped = int(np.count_nonzero(value < 0))
    np.maximum(value, 0, out=value)
    return value, minimum, clipped


def validate_run(source):
    run_path = source.parent / "result.json"
    motion_path = source.parent / "motion-validation.json"
    run = json.loads(run_path.read_text())
    motion = json.loads(motion_path.read_text())
    if (run.get("passed") is not True or run.get("finite") is not True
            or not np.isclose(run["final_time"], 10, rtol=0, atol=1e-10)
            or run["numerical"]["frequency"] != 5):
        raise ValueError("Source must be a successful finite t=10, frequency=5 run")
    samples = motion.get("samples", [])
    if motion.get("passed") is not True or len(samples) < 4:
        raise ValueError("At least four passed direct Meep motion samples are required")
    errors = []
    for sample in samples:
        delta = sample["time"] - run["final_time"]
        if (not np.isfinite(delta) or delta <= 0
                or not np.isclose(sample["delta"], delta, rtol=0, atol=1e-10)
                or not np.isclose(sample["phase_radians"], 2 * np.pi * 5 * delta,
                                  rtol=0, atol=1e-10)):
            raise ValueError("Motion sample times and phases are inconsistent")
        for name in ("native_half_volume", "incident_cut", "reflected_cut"):
            error = sample["relative_l2"][name]
            if not np.isfinite(error) or not 0 <= error < .01:
                raise ValueError(f"Failed direct motion validation: {name}={error}")
            errors.append(error)
    return run, {"passed": True, "direct_meep": motion,
                 "recomputed_maximum_relative_l2": max(errors),
                 "result_sha256": digest(run_path),
                 "motion_validation_sha256": digest(motion_path)}


def inspect_fields(field, baseline, scene):
    shape = field["real2"].shape
    if len(shape) != 3 or min(shape) < 64:
        raise ValueError("Source must have three native axes and room for the 30-cell crop")
    if list(shape) != scene["source_shape"]:
        raise ValueError("Source grid differs from the static scene")
    for name in ("real2", "imag2", "cross"):
        if field[name].shape != shape:
            raise ValueError(f"Inconsistent shape for {name}")
    for name in ("real2", "imag2"):
        if baseline[name].shape != shape:
            raise ValueError(f"Baseline shape differs for {name}")
    axes = [field[key][:] for key in "xyz"]
    for key, axis, count in zip("xyz", axes, shape):
        if (len(axis) != count or not np.isfinite(axis).all()
                or not np.all(np.diff(axis) > 0)
                or not np.allclose(np.diff(axis), np.diff(axis).mean(), rtol=1e-10, atol=1e-12)
                or not np.array_equal(axis, baseline[key][:])
                or not np.allclose([axis[30], axis[-31]], scene["coordinates"][key],
                                   rtol=0, atol=1e-12)):
            raise ValueError(f"Source coordinates do not match the baseline/static scene: {key}")
    cropped = [axis[30:-30] for axis in axes]
    half_count = int(np.ceil(len(cropped[2]) / 2)) + 1
    half_axes = [cropped[0], cropped[1], cropped[2][:half_count]]
    if (scene["cropped_shape"] != [len(a) for a in cropped]
            or scene["half_shape"] != [len(a) for a in half_axes]
            or not np.isclose(scene["half_z_max"], half_axes[2][-1], rtol=0, atol=1e-12)):
        raise ValueError("Static scene crop/half coordinates differ")
    expected_cuts = [("incident", "x", 30, axes[0][30]),
                     ("reflected", "y", shape[1] - 31, axes[1][-31])]
    for cut, (name, axis, index, position) in zip(scene["cuts"], expected_cuts):
        if (cut["name"] != name or cut["axis"] != axis or cut["source_index"] != index
                or not np.isclose(cut["position"], position, rtol=0, atol=1e-12)):
            raise ValueError("Static cut plane differs from source")
    if len(scene["cuts"]) != 2:
        raise ValueError("Exactly two static cut planes are required")
    maximum = max_ab = max_excess = 0.
    comparisons = {name: dict(squared_error=0., squared_norm=0., max_absolute_error=0.)
                   for name in ("real2", "imag2")}
    for i in range(shape[0]):
        a, b, cross = (field[name][i] for name in ("real2", "imag2", "cross"))
        if (not all(np.isfinite(value).all() for value in (a, b, cross))
                or a.min() < 0 or b.min() < 0):
            raise ValueError(f"Nonfinite or negative source squared field in slab {i}")
        product = a * b
        excess = cross**2 - product
        phase_maximum = .5 * (a + b + np.hypot(a - b, 2 * cross))
        if not all(np.isfinite(value).all() for value in (product, excess, phase_maximum)):
            raise ValueError("Source arithmetic overflow")
        max_ab = max(max_ab, float(product.max()))
        max_excess = max(max_excess, float(excess.max()))
        maximum = max(maximum, float(phase_maximum.max()))
        for name, actual in (("real2", a), ("imag2", b)):
            expected = baseline[name][i]
            if not np.isfinite(expected).all():
                raise ValueError("Baseline contains nonfinite values")
            difference = actual - expected
            metric = comparisons[name]
            metric["squared_error"] += float(np.sum(difference**2))
            metric["squared_norm"] += float(np.sum(expected**2))
            metric["max_absolute_error"] = max(metric["max_absolute_error"], float(abs(difference).max()))
    if max_excess > 1e-10 * max_ab or maximum <= 0:
        raise ValueError(f"Cauchy-Schwarz violation: {max_excess}; tolerance={1e-10 * max_ab}")
    for metric in comparisons.values():
        norm, error = metric.pop("squared_norm"), metric.pop("squared_error")
        if norm == 0 and error != 0:
            raise ValueError("Cannot compare nonzero source against zero baseline")
        metric["relative_l2"] = float(np.sqrt(error / norm)) if norm else 0.
        if metric["relative_l2"] > 1e-8:
            raise ValueError(f"Source differs from the saved static baseline: {metric}")
    return half_axes, maximum, {"maximum_ab": max_ab, "maximum_positive_excess": max_excess,
                               "absolute_tolerance": 1e-10 * max_ab, "passed": True}, comparisons


def main():
    parser = argparse.ArgumentParser(description="Prepare native-grid contours from a validated monochromatic Meep snapshot.")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--frames", type=int, default=24)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    if args.frames < 2:
        parser.error("--frames must be at least 2")
    root = args.directory.resolve()
    source = (args.source or root / "animation/data/lg/fields.h5").resolve()
    run, validation = validate_run(source)
    scene_path = root / "native3d/scene.json"
    scene = json.loads(scene_path.read_text())
    if run["physical"] != scene["physical"]:
        raise ValueError("Animation physics differs from the static scene")
    baseline_path = root / "lg/fields.h5"
    source_hash, baseline_hash = digest(source), digest(baseline_path)
    if baseline_hash != scene["source_h5_sha256"]:
        raise ValueError("Static scene no longer matches the baseline file")
    vtk.vtkSMPTools.Initialize(1)
    vtk.vtkMultiThreader.SetGlobalMaximumNumberOfThreads(1)
    out = root / "animation/vortex"
    with h5py.File(source, "r") as field, h5py.File(baseline_path, "r") as baseline:
        half_axes, maximum, cauchy, comparison = inspect_fields(field, baseline, scene)
        level = .02 * maximum
        tolerance = (1e-10 + 64 * np.finfo(float).eps) * maximum
        description = {key: scene[key] for key in ("coordinates", "camera", "cuts", "physical",
                       "half_note", "half_z_max", "cropped_shape", "half_shape", "coordinate_note")}
        description.update(
            kind="Meep complex snapshot monochromatic phase reconstruction; not DFT accumulator or transient frames",
            source=str(source), source_basename=source.name, source_h5_sha256=source_hash,
            baseline_h5_sha256=baseline_hash, static_scene_sha256=digest(scene_path),
            validation=validation, cauchy_schwarz=cauchy, baseline_comparison=comparison,
            maximum_baseline_relative_l2=max(value["relative_l2"] for value in comparison.values()),
            source_shape=list(field["real2"].shape), raw_grid_shape=list(field["real2"].shape),
            crop_cells_each_face=30, spatial_stride=1, mesh_decimation=False, geometric_smoothing=False,
            vtk_version=vtk.vtkVersion.GetVTKVersion(), contour_engine="vtkContourFilter",
            frequency=5, snapshot_time=run["final_time"], optical_period=.2, squared_field_period=.1,
            phase_interval="[0, pi); endpoint excluded", time_convention="exp(-i*phase)",
            formula="A*cos(phase)^2+B*sin(phase)^2+2*C*sin(phase)*cos(phase)",
            normalization={"maximum_over_full_xyz_and_phase": maximum,
                           "analytic_maximum": "0.5*(A+B+sqrt((A-B)^2+4*C^2))",
                           "isolevel": level, "hot_color_limit": level, "fraction": .02,
                           "fixed_across_frames": True, "negative_clip_tolerance": tolerance},
            contour_residual_tolerance_fraction_global_maximum=1e-5, frames=[])
        half_selector = (slice(30, -30), slice(30, -30), slice(30, 30 + len(half_axes[2])))
        half_fields = tuple(field[name][half_selector] for name in ("real2", "imag2", "cross"))
        cut_fields = {
            name: tuple(field[key][selector] for key in ("real2", "imag2", "cross"))
            for name, selector in (("incident", (30, slice(30, -30), slice(30, -30))),
                                   ("reflected", (slice(30, -30), -31, slice(30, -30))))
        }
        for index, phase in enumerate(np.linspace(0, np.pi, args.frames, endpoint=False)):
            frame_dir = out / "native" / f"frame_{index:03d}"
            frame_dir.mkdir(parents=True, exist_ok=True)
            volume, minimum, clipped = reconstruct(*half_fields, phase, tolerance)
            mesh_path = frame_dir / "real2.npz"
            mesh = extract(volume, half_axes, level, mesh_path)
            with np.load(mesh_path) as saved:
                vertices = saved["vertices"]
            residual = 0.
            for start in range(0, len(vertices), 100000):
                points = vertices[start:start + 100000]
                indices = np.array([(points[:, dim].astype(float) - axis[0]) / np.diff(axis).mean()
                                    for dim, axis in enumerate(half_axes)])
                measured = map_coordinates(volume, indices, order=1, mode="nearest", prefilter=False)
                residual = max(residual, float(np.max(abs(measured - level))) / maximum)
            if residual >= 1e-5:
                raise ValueError(f"Contour residual failed: frame={index}, residual={residual}")
            for name, components in cut_fields.items():
                cut, low, count = reconstruct(*components, phase, tolerance)
                minimum, clipped = min(minimum, low), clipped + count
                texture(cut, level, frame_dir / f"real2_{name}.png")
            offset = float(phase / (2 * np.pi * 5))
            frame = dict(index=index, directory=frame_dir.relative_to(out).as_posix(),
                         phase_radians=float(phase), physical_time_offset=offset,
                         time=float(run["final_time"] + offset),
                         label=f"phase={phase / np.pi:.6f} pi; dt={offset:.6f}; t={run['final_time'] + offset:.6f}",
                         surfaces={"real2": mesh}, minimum_before_clip=minimum,
                         negative_values_clipped=clipped,
                         max_contour_residual_fraction_global_maximum=residual,
                         contour_vertices_verified=len(vertices),
                         artifact_hashes={path.name: digest(path) for path in
                                          (mesh_path, frame_dir / "real2_incident.png", frame_dir / "real2_reflected.png")})
            description["frames"].append(frame)
            print("PREPARED_FRAME", index, json.dumps(mesh), flush=True)
        description["maximum_contour_residual_fraction_global_maximum"] = max(
            frame["max_contour_residual_fraction_global_maximum"] for frame in description["frames"])
    if digest(source) != source_hash or digest(baseline_path) != baseline_hash:
        raise ValueError("Input or baseline changed during preparation")
    description["validation"]["inputs_unchanged"] = True
    description["passed"] = True
    (out / "animation.json").write_text(json.dumps(description, indent=2, allow_nan=False))
    print("NATIVE_ANIMATION_PREPARED", flush=True)


if __name__ == "__main__":
    main()
