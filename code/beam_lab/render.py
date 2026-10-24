import argparse
import hashlib
import json
import os
from pathlib import Path

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VTK_SMP_MAX_THREADS", "LP_NUM_THREADS"):
    os.environ[key] = "1"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.interpolate import RegularGridInterpolator
import vtk
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

from profiles import phase_winding


CASES = ("gaussian_flat", "gaussian_concave", "gaussian_convex", "lg_plus2",
         "lg_minus2", "airy_alpha008", "airy_alpha020")
BG = "#101820"
FG = "#e8eff3"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(data):
    result = {}
    for name in CASES:
        folder = data / name
        meta = json.loads((folder / "case.json").read_text())
        if not meta["passed"] or digest(folder / "fields.npz") != meta["fields_sha256"]:
            raise ValueError(f"Unverified case {name}")
        for filename, sha in meta["source_hashes"].items():
            if digest(Path(__file__).with_name(filename)) != sha:
                raise ValueError(f"Runner provenance changed: {filename}")
        with np.load(folder / "fields.npz", allow_pickle=False) as archive:
            arrays = {key: archive[key] for key in archive.files}
        shape = tuple(len(arrays[key]) for key in ("x", "y", "z"))
        for key in ("ex", "ey", "ez", "epsilon"):
            if arrays[key].shape != shape or not np.isfinite(arrays[key]).all():
                raise ValueError(f"Bad array {name}:{key}")
        for key in ("x", "y", "z"):
            if len(arrays[key]) > 1 and not np.all(np.diff(arrays[key]) > 0):
                raise ValueError(f"Bad coordinate {name}:{key}")
        result[name] = (arrays, meta)
    return result


def field_power(arrays):
    return sum(np.abs(arrays[key]) ** 2 for key in ("ex", "ey", "ez"))


def save_figure(fig, path):
    fig.savefig(path, dpi=160, facecolor=BG, bbox_inches="tight", pad_inches=.16)
    plt.close(fig)


def maps(cases, names, titles, output, heading):
    plt.rcParams.update({"text.color": FG, "axes.labelcolor": FG, "xtick.color": FG,
                        "ytick.color": FG, "axes.edgecolor": "#647989", "font.size": 10})
    fig, axes = plt.subplots(1, len(names), figsize=(5 * len(names), 4), facecolor=BG,
                             constrained_layout=True, squeeze=False)
    maximum = max(float(field_power(cases[n][0]).max()) for n in names)
    for ax, name, title in zip(axes[0], names, titles):
        a, meta = cases[name]
        power = field_power(a)[:, :, 0] / maximum
        x, y = a["x"], a["y"]
        image = ax.pcolormesh(x, y, power.T, shading="nearest", cmap="inferno", vmin=0, vmax=1,
                              rasterized=True)
        if np.ptp(a["epsilon"]) > .1:
            ax.contour(x, y, a["epsilon"][:, :, 0].T, levels=[1.625], colors=["#a2e6de"], linewidths=.8)
        ax.set(title=title, xlabel="x / a", ylabel="y / a", aspect="equal", facecolor=BG)
    fig.colorbar(image, ax=list(axes[0]), label="sum |DFT E|² / common group maximum", shrink=.8)
    fig.suptitle(heading + "\nEqual peak current; color does not measure power efficiency", fontsize=14)
    save_figure(fig, output)


def phase_maps(cases, output):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.7), facecolor=BG, constrained_layout=True)
    checks = {}
    for ax, name in zip(axes, ("lg_plus2", "lg_minus2")):
        a, meta = cases[name]
        winding = meta["winding"]
        ix = int(np.argmin(np.abs(a["x"] - winding["plane_x"])))
        field = a["ez"][ix]
        theta = np.linspace(0, 2 * np.pi, winding["samples"], endpoint=False)
        circle = winding["radius"] * np.column_stack((np.cos(theta), np.sin(theta)))
        measured = phase_winding(RegularGridInterpolator((a["y"], a["z"]), field)(circle))
        if abs(measured - winding["source_charge"]) > .05:
            raise ValueError("DFT winding does not match signed source charge")
        phase = np.ma.masked_where(np.abs(field) < .05 * np.abs(field).max(), np.angle(field))
        image = ax.pcolormesh(a["y"], a["z"], phase.T, shading="nearest", cmap="twilight_shifted",
                              vmin=-np.pi, vmax=np.pi, rasterized=True)
        ax.plot(circle[:, 0], circle[:, 1], color=FG, linewidth=.8, linestyle="--")
        ax.set(title=f"source m = {winding['source_charge']:+d}; measured winding = {measured:+.3f}\nx = {a['x'][ix]:.3f} a",
               xlabel="y / a", ylabel="z / a", aspect="equal", facecolor=BG)
        checks[name] = {"source_charge": winding["source_charge"], "recomputed_winding": measured,
                        "weak_phase_mask_fraction": .05, "circle_radius": winding["radius"]}
    fig.colorbar(image, ax=list(axes), label="arg(DFT Ez) / rad", ticks=[-np.pi, 0, np.pi], shrink=.8)
    fig.suptitle("Reverse the charge, reverse the phase winding\nMeasured fields; weak-amplitude pixels masked", fontsize=14)
    save_figure(fig, output)
    return checks


def text_image(canvas, xy, message, size=24, color=FG):
    font = None
    for filename in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"):
        if Path(filename).exists():
            font = ImageFont.truetype(filename, size)
            break
    ImageDraw.Draw(canvas).text(xy, message, fill=color, font=font or ImageFont.load_default())


def vortex_animation(cases, out):
    vtk.vtkMultiThreader.SetGlobalMaximumNumberOfThreads(1)
    names = ("lg_plus2", "lg_minus2")
    peak = max(float(np.abs(cases[n][0]["ez"]).max()) for n in names)
    level = .25 * peak
    renderers, pipelines = [], []
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetMultiSamples(0)
    window.SetSize(1200, 570)
    for column, name in enumerate(names):
        a, _ = cases[name]
        renderer = vtk.vtkRenderer()
        renderer.SetViewport(column / 2, 0, (column + 1) / 2, 1)
        renderer.SetBackground(.063, .094, .125)
        window.AddRenderer(renderer)
        grid = vtk.vtkImageData()
        grid.SetDimensions(*a["ez"].shape)
        grid.SetOrigin(*(float(a[key][0]) for key in ("x", "y", "z")))
        grid.SetSpacing(*(float(a[key][1] - a[key][0]) for key in ("x", "y", "z")))
        contours = []
        for sign, color in ((1, (.27, .88, .78)), (-1, (1., .43, .32))):
            contour = vtk.vtkContourFilter()
            contour.SetInputData(grid)
            contour.SetValue(0, sign * level)
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(contour.GetOutputPort())
            mapper.ScalarVisibilityOff()
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(*color)
            actor.GetProperty().SetOpacity(1)
            actor.GetProperty().SetSpecular(.12)
            actor.GetProperty().SetSpecularPower(18)
            renderer.AddActor(actor)
            contours.append(contour)
        outline = vtk.vtkOutlineFilter()
        outline.SetInputData(grid)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(outline.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(.35, .43, .48)
        renderer.AddActor(actor)
        camera = renderer.GetActiveCamera()
        center = (float((a["x"][0] + a["x"][-1]) / 2), 0, 0)
        camera.SetFocalPoint(*center)
        camera.SetPosition(center[0] - 6, -12, 8)
        camera.SetViewUp(0, 0, 1)
        camera.ParallelProjectionOn()
        camera.SetParallelScale(4.9)
        renderer.ResetCameraClippingRange()
        pipelines.append((grid, contours))
        renderers.append(renderer)
    frames, raw_frames, cells = [], [], []
    phases = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    for index, phase in enumerate(phases):
        counts = []
        for name, (grid, contours) in zip(names, pipelines):
            scalar = np.real(cases[name][0]["ez"] * np.exp(-1j * phase))
            grid.GetPointData().SetScalars(numpy_to_vtk(scalar.ravel(order="F"), deep=True))
            grid.Modified()
            for contour in contours:
                contour.Update()
                mesh = contour.GetOutput()
                counts.append(mesh.GetNumberOfCells())
                if not mesh.GetNumberOfCells():
                    raise ValueError("Empty native-grid contour")
        window.Render()
        grab = vtk.vtkWindowToImageFilter()
        grab.SetInput(window)
        grab.ReadFrontBufferOff()
        grab.Update()
        pixels = vtk_to_numpy(grab.GetOutput().GetPointData().GetScalars()).reshape(570, 1200, -1)
        raw = Image.fromarray(np.flipud(pixels[:, :, :3])).convert("RGB")
        raw_frames.append(np.array(raw.resize((300, 143)), copy=True))
        frame = Image.new("RGB", (1200, 700), BG)
        frame.paste(raw, (0, 65))
        text_image(frame, (25, 12), "BEAM LAB   /   Signed vortex field", 28)
        text_image(frame, (770, 16), f"DFT phase {index:02d}/24 = {phase / np.pi:.2f} pi", 20)
        text_image(frame, (50, 77), "m = +2", 25)
        text_image(frame, (650, 77), "m = -2", 25)
        text_image(frame, (25, 637), "Teal: +0.25 max |Ez|     Coral: -0.25 max |Ez|     Same fixed scale; native grid", 19)
        text_image(frame, (25, 666), "DFT phase cycle; not transient arrival. Vacuum / 12 cells per wavelength / x,y,z in a", 17)
        frames.append(frame)
        cells.append(counts)
    changes = [float(np.mean(np.any(a != b, axis=2))) for a, b in zip(raw_frames, raw_frames[1:] + raw_frames[:1])]
    if min(changes) < .005:
        raise ValueError("Static 3D scene or incomplete phase cycle")
    frames[0].save(out / "vortex_poster.png")
    for extension in ("gif", "webp"):
        frames[0].save(out / f"vortex_phase.{extension}", save_all=True, append_images=frames[1:],
                       duration=80, loop=0, **({"disposal": 2} if extension == "gif" else {"quality": 86}))
        with Image.open(out / f"vortex_phase.{extension}") as decoded:
            if decoded.n_frames != len(frames) or decoded.size != (1200, 700):
                raise ValueError("Invalid encoded animation")
    contact = Image.new("RGB", (1200, 1050), BG)
    for tile, index in enumerate((0, 4, 8, 12, 16, 20)):
        contact.paste(frames[index].resize((600, 350)), ((tile % 2) * 600, (tile // 2) * 350))
    contact.save(out / "contact_sheet.png")
    window.Finalize()
    return {"frames": 24, "frame_duration_ms": 80, "loop_ms": 1920,
            "phase_convention": "Re(Ez_tilde exp(-i*phase))", "phase_radians": phases.tolist(),
            "fixed_isovalue": level, "isovalue_fraction_ez_group_peak": .25,
            "spatial_stride": 1, "mesh_decimation": False, "triangle_counts": cells,
            "minimum_raw_scene_changed_fraction": min(changes), "vtk_version": vtk.vtkVersion.GetVTKVersion()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    cases = load(args.data)
    maps(cases, CASES[:3], ("Flat: kappa = 0", "Opens +x: kappa = +0.10 / a", "Opens -x: kappa = -0.10 / a"),
         args.output / "gaussian_curvature.png", "Same Gaussian aperture, three dielectric boundaries")
    maps(cases, CASES[5:], ("alpha = 0.08", "alpha = 0.20"), args.output / "airy_apodization.png",
         "Finite Airy aperture: change the tail attenuation")
    winding = phase_maps(cases, args.output / "vortex_charge.png")
    animation = vortex_animation(cases, args.output)
    overview = Image.new("RGB", (1600, 1000), BG)
    for filename, box in (("gaussian_curvature.png", (0, 0, 1600, 440)),
                          ("vortex_charge.png", (0, 450, 800, 550)),
                          ("airy_apodization.png", (800, 450, 800, 550))):
        with Image.open(args.output / filename) as im:
            im.thumbnail(box[2:])
            overview.paste(im, (box[0] + (box[2] - im.width) // 2, box[1] + (box[3] - im.height) // 2))
    overview.save(args.output / "overview.png")
    report = {"passed": True, "implementation": "Beam Lab direct analytic-current Meep controls; no optbeam dependency",
              "cases": {name: meta for name, (_, meta) in cases.items()}, "phase_winding": winding,
              "animation": animation, "renderer_sha256": digest(Path(__file__)),
              "assets": {p.name: {"sha256": digest(p), "bytes": p.stat().st_size}
                         for p in sorted(args.output.iterdir()) if p.suffix in (".png", ".gif", ".webp")}}
    (args.output / "checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"passed": True, "assets": list(report["assets"]), "winding": winding,
                      "frames": animation["frames"]}), flush=True)


if __name__ == "__main__":
    main()
