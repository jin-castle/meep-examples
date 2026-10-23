#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


parser = argparse.ArgumentParser()
parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent)
ROOT = parser.parse_args().data_dir.resolve()
plt.rcParams.update({"font.size": 12, "axes.titlesize": 16,
                     "axes.labelsize": 12, "font.family": "DejaVu Sans"})


def load_case(angle):
    with np.load(ROOT / f"planar{angle}/fields.npz") as archive:
        return {key: archive[key] for key in archive.files}


CASES = {angle: load_case(angle) for angle in (30, 45)}
LIMIT = max(np.abs(data["ez"])[(np.abs(data["x"])[:, None] < 2.2)
                              & (np.abs(data["y"])[None, :] < 2.2)].max()
            for data in CASES.values())
INTENSITY_LIMIT = max(data["mean_ez2"][(np.abs(data["x"])[:, None] < 2.2)
                                     & (np.abs(data["y"])[None, :] < 2.2)].max()
                     for data in CASES.values())


def panel(ax, data, angle, kind, frame=None):
    extent = [-2.5, 2.5, -2.5, 2.5]
    if kind == "wavefront":
        eps = data["epsilon"]
        ax.imshow(eps.T, origin="lower", extent=extent, cmap="Greys",
                  vmin=0, vmax=5, interpolation="nearest")
        field = data["ez"] if frame is None else frame
        rgba = plt.get_cmap("RdBu_r")((np.clip(field / LIMIT, -1, 1).T + 1) / 2)
        rgba[..., 3] = np.sqrt(np.minimum(abs(field.T) / LIMIT, 1))
        ax.imshow(rgba, origin="lower", extent=extent, interpolation="nearest")
        mappable = plt.cm.ScalarMappable(norm=matplotlib.colors.Normalize(-1, 1),
                                         cmap="RdBu_r")
        label = r"Instantaneous $E_z(t) / E_{\rm common,max}$"
        textcolor = "#1c2434"
        contour_color = "#465063"
    else:
        mappable = ax.imshow(data["mean_ez2"].T / INTENSITY_LIMIT, origin="lower",
                             extent=extent, cmap="hot", vmin=0, vmax=1,
                             interpolation="nearest")
        label = r"Cycle-mean $E_z^2$ / common maximum"
        textcolor = "white"
        contour_color = "#b0b7bf"
    ax.contour(data["x"], data["y"], data["epsilon"].T,
               levels=[(1 + 1.54 ** 2) / 2], colors=[contour_color], linewidths=.9)
    ax.set(xlim=(-2.2, 2.2), ylim=(-2.2, 2.2), xlabel=r"$x/a$", ylabel=r"$y/a$")
    ax.text(.04, .96, r"$n_1=1.54$", transform=ax.transAxes, va="top",
            color=textcolor, fontsize=13)
    ax.text(.96, .04, r"$n_2=1.00$", transform=ax.transAxes, ha="right",
            color=textcolor, fontsize=13)
    ax.set_title(f"{angle} deg incidence", loc="left", fontweight="bold", pad=12)
    return mappable, label


def save_static():
    for kind in ("wavefront", "intensity"):
        fig, axes = plt.subplots(1, 2, figsize=(12, 6.7))
        fig.subplots_adjust(left=.06, right=.98, top=.84, bottom=.20, wspace=.18)
        for ax, angle in zip(axes, CASES):
            mappable, label = panel(ax, CASES[angle], angle, kind)
        fig.suptitle("Gaussian beam at a dielectric interface", x=.06, y=.97,
                     ha="left", fontsize=21, fontweight="bold")
        fig.text(.06, .91, "Original Optical-beams-MEEP Gauss2d.py | Meep 1.33.0 | s-polarized",
                 color="#465063", fontsize=12)
        colorbar = fig.colorbar(mappable, ax=axes, orientation="horizontal",
                                 fraction=.048, pad=.14, aspect=50)
        colorbar.set_label(label)
        fig.savefig(ROOT / f"{kind}_comparison.png", dpi=170, facecolor="white")
        plt.close(fig)
        for angle, data in CASES.items():
            fig, ax = plt.subplots(figsize=(6.3, 6.9))
            fig.subplots_adjust(left=.11, right=.96, top=.89, bottom=.21)
            mappable, label = panel(ax, data, angle, kind)
            bar = fig.colorbar(mappable, ax=ax, orientation="horizontal", fraction=.05,
                               pad=.14, aspect=35)
            bar.set_label(label, fontsize=10)
            fig.savefig(ROOT / f"planar{angle}_{kind}.png", dpi=170, facecolor="white")
            plt.close(fig)


def save_gifs():
    for angle, data in CASES.items():
        fig, ax = plt.subplots(figsize=(6, 6.3), dpi=100)
        fig.subplots_adjust(left=.12, right=.96, top=.86, bottom=.1)
        preview = data["preview"]
        eps = data["epsilon"][::3, ::3]
        ax.imshow(eps.T, origin="lower", extent=[-2.5, 2.5, -2.5, 2.5],
                  cmap="Greys", vmin=0, vmax=5, interpolation="nearest")
        image = ax.imshow(np.zeros((*preview[0].T.shape, 4)), origin="lower",
                           extent=[-2.5, 2.5, -2.5, 2.5], interpolation="nearest")
        ax.contour(data["preview_x"], data["preview_y"], eps.T,
                   levels=[(1+1.54**2)/2], colors=["#465063"], linewidths=.9)
        ax.set(xlim=(-2.2, 2.2), ylim=(-2.2, 2.2), xlabel="x/a", ylabel="y/a")
        title = ax.set_title(f"{angle} deg | actual FDTD snapshots", loc="left", pad=12)
        fig.text(.12, .95, "Optical-beams-MEEP / Gaussian beam", fontweight="bold")
        fig.text(.12, .91, "Two final optical periods, slowed for display", fontsize=10)
        frames = []
        for field, t in zip(preview, data["times"]):
            rgba = plt.get_cmap("RdBu_r")((np.clip(field.T / LIMIT, -1, 1) + 1)/2)
            rgba[..., 3] = np.sqrt(np.minimum(abs(field.T)/LIMIT, 1))
            image.set_data(rgba)
            title.set_text(f"{angle} deg | t = {t:.5f} a/c")
            fig.canvas.draw()
            frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba()).copy()).convert("RGB"))
        palette = frames[0].quantize(colors=256)
        quantized = [frame.quantize(palette=palette) for frame in frames]
        quantized[0].save(ROOT / f"planar{angle}.gif", save_all=True,
                          append_images=quantized[1:], duration=65, loop=0, optimize=False)
        plt.close(fig)


def direction(data, ray, distance):
    x, y = np.meshgrid(data["x"], data["y"], indexing="ij")
    vector = np.array([math.cos(ray), math.sin(ray)])
    along = vector[0]*x + vector[1]*y
    transverse = -vector[1]*x + vector[0]*y
    mask = ((along > distance[0]) & (along < distance[1])
            & (abs(transverse) < .12))
    field = data["phasor"]
    grad_x, grad_y = np.gradient(field, data["x"], data["y"])
    weight = np.abs(field) ** 2
    kx = np.imag(np.conj(field)*grad_x)[mask].sum()/weight[mask].sum()
    ky = np.imag(np.conj(field)*grad_y)[mask].sum()/weight[mask].sum()
    return dict(angle_from_positive_x_deg=float(np.degrees(np.arctan2(ky, kx))),
                spatial_wavevector=[float(kx), float(ky)],
                method="intensity-weighted local phasor phase gradient",
                mask=dict(along_ray=distance, transverse_half_width=.12))


def validate():
    n1, n2 = 1.54, 1.
    critical = math.degrees(math.asin(n2/n1))
    theta_t = math.degrees(math.asin(n1*math.sin(math.radians(30))/n2))
    results = {}
    for angle, data in CASES.items():
        case = ROOT / f"planar{angle}"
        meta = json.loads((case/"run.json").read_text())
        original = next((case/"planar").glob("*e2_s*.h5"))
        with h5py.File(original, "r") as file:
            instantaneous = file[next(iter(file))][:]
        original_e2_max_error = float(np.max(abs(instantaneous-data["ez"]**2)))
        eps = data["epsilon"]
        reflected = direction(data, math.radians(180-2*angle), [.7, 1.7])
        item = dict(run=meta, original_instantaneous_e2_max_error=original_e2_max_error,
                    epsilon_min=float(eps.min()), epsilon_max=float(eps.max()),
                    all_arrays_finite=all(np.isfinite(value).all() for value in data.values()),
                    reflected_direction=reflected,
                    expected_reflected_direction_from_x_deg=180-2*angle)
        if angle == 30:
            transmitted = direction(data, math.radians(theta_t-30), [.6, 1.6])
            item.update(transmitted_direction=transmitted,
                        plane_wave_snell_angle_from_normal_deg=theta_t,
                        measured_angle_from_normal_deg=transmitted["angle_from_positive_x_deg"]+30,
                        plane_wave_snell_angle_error_deg=abs(transmitted["angle_from_positive_x_deg"]+30-theta_t))
        item["passed"] = bool(meta["passed"] and item["all_arrays_finite"]
                               and original_e2_max_error < 1e-8
                               and np.isclose(eps.min(), 1) and np.isclose(eps.max(), 1.54**2)
                               and abs(reflected["angle_from_positive_x_deg"]-(180-2*angle)) < 3)
        results[str(angle)] = item
    checks = dict(passed=all(item["passed"] for item in results.values()),
                  critical_angle_deg=critical, cases=results,
                  rendering=dict(shared_wavefront_max=float(LIMIT),
                                 shared_cycle_mean_ez2_max=float(INTENSITY_LIMIT),
                                 spatial_display_region=[-2.2, 2.2, -2.2, 2.2],
                                 field_opacity="sqrt(abs(Ez)/shared_max), display only",
                                 intensity_scaling="linear, common limit across both cases"),
                  limitations=["Default 10 grid points per denser-medium wavelength; no resolution convergence study",
                               "Finite-width beam contains an angular spectrum; the central 45-degree ray is above critical but zero total transmission is not asserted",
                               "No flux monitors or incident-only subtraction; no measured R/T efficiency claimed",
                               "Phase-gradient direction is a local diagnostic, not a flux or beam-centroid measurement",
                               "The length unit a is arbitrary; no micrometer mapping is assumed"])
    (ROOT/"checks.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps({"passed":checks["passed"], "critical":critical,
                       "angles":{key:{"reflected":item["reflected_direction"]["angle_from_positive_x_deg"],
                                      "transmitted":item.get("measured_angle_from_normal_deg")}
                                 for key,item in results.items()}}, indent=2))
    if not checks["passed"]:
        raise RuntimeError("Physical/numerical checks failed")


if __name__ == "__main__":
    save_static()
    save_gifs()
    validate()
