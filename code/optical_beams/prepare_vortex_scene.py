"""Extract native-resolution Meep contours and measured cut textures for Blender.

Requires the gallery runner's lg/fields.h5 and VTK 9.5.2. No spatial stride,
mesh decimation, geometric smoothing, or invented field geometry is applied.
"""

import argparse
import hashlib
import json
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
from matplotlib import colormaps
import numpy as np
from PIL import Image
import vtk
from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def texture(array, maximum, path):
    colors = colormaps["hot"](np.clip(array.T[::-1] / maximum, 0, 1), bytes=True)
    Image.fromarray(colors[:, :, :3]).save(path)


def extract(volume, coordinates, level, output):
    image = vtk.vtkImageData()
    image.SetDimensions(*volume.shape)
    image.SetOrigin(*(float(axis[0]) for axis in coordinates))
    image.SetSpacing(*(float(np.diff(axis).mean()) for axis in coordinates))
    scalars = numpy_to_vtk(volume.ravel(order="F"), deep=True)
    scalars.SetName("measured_field_squared")
    image.GetPointData().SetScalars(scalars)
    contour = vtk.vtkContourFilter()
    contour.SetInputData(image)
    contour.SetValue(0, level)
    contour.ComputeNormalsOn()
    contour.Update()
    mesh = contour.GetOutput()
    points = vtk_to_numpy(mesh.GetPoints().GetData()).copy()
    cells = vtk_to_numpy(mesh.GetPolys().GetData()).reshape(-1, 4)
    assert np.all(cells[:, 0] == 3)
    faces = cells[:, 1:].copy()
    normals = vtk_to_numpy(mesh.GetPointData().GetNormals()).copy()
    assert np.isfinite(points).all() and np.isfinite(normals).all()
    assert len(faces) > 0
    np.savez_compressed(output, vertices=points, faces=faces, normals=normals)
    return {"vertices": len(points), "triangles": len(faces),
            "bounds": [float(v) for v in mesh.GetBounds()],
            "file": output.name, "sha256": digest(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    root = args.directory.resolve()
    out = root / "native3d"
    out.mkdir(exist_ok=True)
    vtk.vtkSMPTools.Initialize(1)
    vtk.vtkMultiThreader.SetGlobalMaximumNumberOfThreads(1)
    source = root / "lg/fields.h5"
    run = json.loads((root / "lg/result.json").read_text())
    physical = run["physical"]
    assert physical["n1"] == 1 and physical["n2"] == 1.54
    assert physical["chi_deg"] == 45
    with h5py.File(source, "r") as field:
        axes = [field[key][30:-30] for key in ("x", "y", "z")]
        half_last = int(np.ceil(len(axes[2]) / 2))
        half_axes = [axes[0], axes[1], axes[2][:half_last + 1]]
        max_real = max(float(slab.max()) for slab in field["real2"])
        max_modulus = max(float((field["real2"][i] + field["imag2"][i]).max())
                          for i in range(field["real2"].shape[0]))
        description = {
            "source_h5_sha256": digest(source), "source_shape": list(field["real2"].shape),
            "vtk_version": vtk.vtkVersion.GetVTKVersion(), "contour_engine": "vtkContourFilter",
            "spatial_stride": 1, "mesh_decimation": False, "geometric_smoothing": False,
            "crop_cells_each_face": 30, "cropped_shape": [len(a) for a in axes],
            "half_shape": [len(a) for a in half_axes],
            "coordinates": {key: [float(a[0]), float(a[-1])] for key, a in zip("xyz", axes)},
            "half_z_max": float(half_axes[2][-1]),
            "half_note": "Original inclusive ceil(Nz/2) index; one half-cell above z=0 on the even z grid.",
            "coordinate_note": "Actual saved 5x5x4 Meep coordinates; historical renderer's hardcoded z=3.5 is not reused.",
            "iso_fraction_of_full_volume_maximum": .02,
            "cut_color_fraction_of_full_volume_maximum": .02,
            "normalization_maxima": {"real2": max_real, "modulus2": max_modulus},
            "cuts": [{"name": "incident", "axis": "x", "source_index": 30,
                      "position": float(axes[0][0]), "texture_axes": ["y", "z"]},
                     {"name": "reflected", "axis": "y", "source_index": len(field["y"]) - 31,
                      "position": float(axes[1][-1]), "texture_axes": ["x", "z"]}],
            "cut_index_note": "Historical slice_index=Ny is out of range; use last valid cropped y index Ny-1.",
            "surfaces": {}, "physical": physical,
            "reference_scalar_note": "Historical script defaults to real2+imag2 and offers real2. Main image uses real2 to retain the reference's carrier fringes; both are rendered explicitly.",
        }
        for scalar, maximum in (("real2", max_real), ("modulus2", max_modulus)):
            volume = field["real2"][30:-30, 30:-30, 30:30 + half_last + 1]
            incident = field["real2"][30, 30:-30, 30:-30]
            reflected = field["real2"][30:-30, -31, 30:-30]
            if scalar == "modulus2":
                volume += field["imag2"][30:-30, 30:-30, 30:30 + half_last + 1]
                incident += field["imag2"][30, 30:-30, 30:-30]
                reflected += field["imag2"][30:-30, -31, 30:-30]
            assert np.isfinite(volume).all()
            level = .02 * maximum
            description["surfaces"][scalar] = extract(volume, half_axes, level, out / (scalar + ".npz"))
            texture(incident, level, out / (scalar + "_incident.png"))
            texture(reflected, level, out / (scalar + "_reflected.png"))
            print(scalar, description["surfaces"][scalar], flush=True)
    # Reproduce mlab.view(-45, 0, distance=12), then VTK camera rotations.
    camera = vtk.vtkCamera()
    phi = np.deg2rad(-45)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetPosition(0, 0, 12)
    camera.SetViewUp(float(np.sin(phi)), float(np.cos(phi)), 0)
    camera.Azimuth(20)
    camera.Elevation(30)
    camera.OrthogonalizeViewUp()
    description["camera"] = {"relative_position": list(camera.GetPosition()),
                             "up": list(camera.GetViewUp()), "vertical_fov_degrees": 30,
                             "convention": "Mayavi polar elevation, followed by VTK Azimuth(20), Elevation(30)"}
    description["artifact_hashes"] = {p.name: digest(p) for p in out.glob("*.png")}
    (out / "scene.json").write_text(json.dumps(description, indent=2))
    print("NATIVE_SCENE_PREPARED", flush=True)


if __name__ == "__main__":
    main()
