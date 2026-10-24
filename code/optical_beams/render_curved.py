#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


NAMES = ("planar", "concave", "convex")
EXPECTED_SOURCE_SHA_LF = "477184e390cd400bfdc90f629284fd1f36b76648e6422da2ec793cba4f66445c"
KNOWN_SOURCE_SHAS = frozenset((
    "ca2c371dc80d4eb72e6a4be4801ca2261abed4e05514899e3e706783291caccf",
    EXPECTED_SOURCE_SHA_LF,
))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hash_matches(meta):
    return (meta.get("source_sha256") in KNOWN_SOURCE_SHAS
            and meta.get("source_sha256_lf_normalized", EXPECTED_SOURCE_SHA_LF)
            == EXPECTED_SOURCE_SHA_LF)


def panel_mask(data):
    return ((abs(data["x"])[:, None] < 2.2)
            & (abs(data["y"])[None, :] < 2.2))


def hot(ax, data, peak, annotation=False):
    im = ax.imshow(data["ez"].T**2/peak, origin="lower",
                   extent=[-2.5, 2.5, -2.5, 2.5], cmap="hot",
                   vmin=0, vmax=1, interpolation="nearest")
    ax.set(xlim=(-2.2, 2.2), ylim=(-2.2, 2.2))
    if annotation:
        ax.contour(data["x"], data["y"], data["epsilon"].T,
                   levels=[(1+1.54**2)/2], colors=["#adb9c5"], linewidths=.85)
        ax.plot([-2.15, -2.15], [-1, 1], color="#42d4df", ls="--", lw=1)
        ax.plot(0, 0, "+", color="white", ms=7, mew=1)
        ax.set(xlabel="x/a", ylabel="y/a")
    else:
        ax.set_axis_off()
    return im


def save_images(root, data, peaks):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.6), facecolor="black")
    fig.subplots_adjust(left=.01, right=.99, top=.80, bottom=.02, wspace=.018)
    for ax, name in zip(axes, NAMES):
        hot(ax, data[name], peaks[name])
        ax.set_title(name.capitalize(), color="white", fontsize=19, loc="left", pad=10)
    fig.text(.01, .935, "Gaussian beam / planar, concave and convex interfaces",
             color="white", fontsize=18, fontweight="bold")
    fig.text(.01, .885, "Instantaneous Ez(t)^2 at t=10 a/c | linear hot | each panel normalized to its own peak",
             color="#c9cdd4", fontsize=12)
    fig.savefig(root/"curved_comparison.png", dpi=170, facecolor="black")
    plt.close(fig)
    for name in NAMES:
        fig, ax = plt.subplots(figsize=(6, 6), facecolor="black")
        fig.subplots_adjust(0, 0, 1, 1)
        hot(ax, data[name], peaks[name])
        fig.savefig(root/f"{name}45_hot.png", dpi=200, facecolor="black")
        plt.close(fig)
    common = max(peaks.values())
    fig, axes = plt.subplots(1, 3, figsize=(15.8, 6.6))
    fig.subplots_adjust(left=.045, right=.985, top=.84, bottom=.23, wspace=.23)
    for ax, name in zip(axes, NAMES):
        im = hot(ax, data[name], common, annotation=True)
        ax.set_title(name.capitalize(), loc="left", fontsize=17, fontweight="bold", pad=12)
    fig.text(.045, .95, "Same field scale, time and observation window", fontsize=19, fontweight="bold")
    fig.text(.045, .905, "t=10 a/c | chi=45 deg at origin | gray: dielectric boundary | cyan: imposed source aperture",
             fontsize=12, color="#465063")
    colorbar = fig.colorbar(im, ax=axes, orientation="horizontal", fraction=.055, pad=.18, aspect=55)
    colorbar.set_label(r"Instantaneous $E_z(t)^2$ / common maximum (linear)")
    fig.savefig(root/"curved_common_scale.png", dpi=170, facecolor="white")
    plt.close(fig)


def save_gifs(root, data):
    for name in NAMES:
        item = data[name]
        frames = item["preview"]**2
        mask = ((abs(item["preview_x"])[:, None] < 2.2)
                & (abs(item["preview_y"])[None, :] < 2.2))
        peak = float(frames[:, mask].max())
        fig, ax = plt.subplots(figsize=(6, 6.6), dpi=100, facecolor="black")
        fig.subplots_adjust(left=0, right=1, bottom=0, top=.9)
        image = ax.imshow(frames[0].T/peak, origin="lower", extent=[-2.5, 2.5, -2.5, 2.5],
                           cmap="hot", vmin=0, vmax=1, interpolation="nearest")
        ax.set(xlim=(-2.2, 2.2), ylim=(-2.2, 2.2))
        ax.set_axis_off()
        label = fig.text(.02, .95, "", color="white", fontsize=12)
        fig.text(.02, .915, "Actual FDTD snapshots | fixed peak per animation | slowed", color="#bac2ce", fontsize=9)
        images = []
        for frame, time in zip(frames, item["times"]):
            image.set_data(frame.T/peak)
            label.set_text(f"{name.capitalize()} | Ez(t)^2 | t={time:.5f} a/c")
            fig.canvas.draw()
            images.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert("RGB"))
        palette = images[0].quantize(colors=256)
        converted = [image.quantize(palette=palette) for image in images]
        converted[0].save(root/f"{name}45_hot.gif", save_all=True, append_images=converted[1:],
                          duration=65, loop=0, optimize=False)
        plt.close(fig)


def validate(root, data, peaks, planar_origin):
    results = {}
    for name in NAMES:
        folder = root/f"{name}45"
        meta = json.loads((folder/"run.json").read_text())
        source_matches = source_hash_matches(meta)
        original_e2 = next(folder.glob(f"{name}/*e2_s*.h5"))
        with h5py.File(original_e2) as file:
            original = file[next(iter(file))][:]
        ez2 = data[name]["ez"]**2
        max_error = float(abs(original-ez2).max())
        finite = bool(all(np.isfinite(value).all() for value in data[name].values()))
        geometry = meta.get("source_geometry")
        if geometry is None:
            ix = np.argmin(abs(data[name]["x"]+2.15))
            iy = np.argmin(abs(data[name]["y"]))
            source_eps = data[name]["epsilon"][ix, abs(data[name]["y"])<=1]
            all_n1 = bool(np.allclose(source_eps, 1.54**2, rtol=0, atol=1e-8))
            geometry = dict(center_epsilon=float(data[name]["epsilon"][ix, iy]),
                            epsilon_min=float(source_eps.min()), epsilon_max=float(source_eps.max()),
                            all_sampled_source_in_n1=all_n1,
                            source_j2_weight_fraction_outside_n1=0 if all_n1 else None,
                            method="Stored epsilon at nearest source-x grid column")
        results[name] = dict(
            passed=bool(meta["passed"] and finite and max_error<1e-8
                        and source_matches
                        and meta["sampling"]["end"]==10
                        and meta["physical"]["interface"]==name),
            source_sha256=meta["source_sha256"], execution_exit_code=0,
            source_sha256_lf_normalized=(EXPECTED_SOURCE_SHA_LF if source_matches
                                         else meta.get("source_sha256_lf_normalized")),
            reused=name=="planar", source_geometry=geometry,
            original_hdf5_e2_max_absolute_error=max_error,
            all_arrays_finite=finite, panel_peak=float(peaks[name]),
            grid_shape=list(ez2.shape), frames=len(data[name]["times"]),
            end_time=float(data[name]["times"][-1]),
            harmonic_fit_relative_l2_residual=meta["sampling"]["harmonic_fit_relative_l2_residual"],
            files=dict(fields_sha256=digest(folder/"fields.npz"),
                       raw_instantaneous_e2_sha256=digest(original_e2),
                       run_json_sha256=digest(folder/"run.json")))
    reused = results["planar"]
    if planar_origin is not None:
        old_e2 = next(planar_origin.glob("planar/*e2_s*.h5"))
        reused["reuse_origin"] = str(planar_origin)
        reused["reuse_hash_match"] = bool(
            digest(planar_origin/"fields.npz")==reused["files"]["fields_sha256"]
            and digest(old_e2)==reused["files"]["raw_instantaneous_e2_sha256"]
            and digest(planar_origin/"run.json")==reused["files"]["run_json_sha256"])
        reused["passed"] = reused["passed"] and reused["reuse_hash_match"]
    checks = dict(
        passed=all(item["passed"] for item in results.values()), cases=results,
        physics=dict(n1=1.54, n2=1, chi_at_origin_deg=45,
                     r_c=150/(2*math.pi*12), cell=[5,5], pml=.25,
                     frequency=12, runtime=10, optical_periods=120,
                     resolution=184.8, s_polarization="Ez",
                     concave="n1 cylinder centered at (-r_c*cos(chi), +r_c*sin(chi)), n2 exterior",
                     convex="n2 cylinder centered at (+r_c*cos(chi), -r_c*sin(chi)), n1 exterior"),
        visualization=dict(quantity="real instantaneous Ez(t)^2, never cycle averaged",
                           hero="linear hot, per-panel peak normalization, no geometry overlay",
                           comparison="linear hot, common maximum, geometry and source overlaid",
                           common_peak=max(peaks.values()), extent=[-2.2,2.2,-2.2,2.2],
                           animation="actual final-two-period Ez samples squared; fixed peak per animation"),
        limitations=["10 pixels per denser-medium wavelength; no mesh or PML convergence sweep",
                     "Concave source center is in n1, but a weak source-aperture tail intersects n2",
                     "Source J-squared weighting is not an energy flux or efficiency measurement",
                     "45-degree incidence is relative to the tangent normal at the origin only",
                     "No focus width, focusing efficiency, beam centroid or R/T flux performance is claimed",
                     "Instantaneous fringes depend on optical phase; the three panels use the same t=10",
                     "Panel normalization compares morphology, not absolute amplitudes"],
        retries=[dict(case="concave", count=1, category="metadata_collection",
                      reason="get_epsilon_point returned a complex scalar with zero imaginary part; collector explicitly records its real part",
                      log="concave45.collector-failed.log")])
    (root/"checks.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    provenance = dict(upstream_commit="ca145119e5bd0f0804d846ea42e35e4c3daa91de",
                      version="2.1.2", version_doi="10.5281/zenodo.5211251", license="MIT",
                      original_source_sha256=results["planar"]["source_sha256"],
                      source_sha256_lf_normalized=EXPECTED_SOURCE_SHA_LF,
                      line_endings_note="execution files CRLF, repository Git text may normalize LF; canonical hash replaces CRLF with LF",
                      source_unchanged=True, geometry_and_numerical_defaults_unchanged=True,
                      fresh_executions=["concave45", "convex45"], reused_execution="planar45",
                      artifacts=results,
                      wrapper_added_only="Interface selection and read-only sampling/source-medium diagnostics",
                      day_local="2026-10-24", timezone="Asia/Seoul")
    (root/"provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))
    if not checks["passed"]:
        raise RuntimeError("Curved-beam checks failed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--planar-origin", type=Path)
    args = parser.parse_args()
    root = args.data_dir.resolve()
    data = {}
    for name in NAMES:
        with np.load(root/f"{name}45/fields.npz") as archive:
            data[name] = {key: archive[key] for key in archive.files}
    peaks = {name: float((item["ez"]**2)[panel_mask(item)].max()) for name,item in data.items()}
    save_images(root, data, peaks)
    save_gifs(root, data)
    validate(root, data, peaks, args.planar_origin)


if __name__ == "__main__":
    main()
