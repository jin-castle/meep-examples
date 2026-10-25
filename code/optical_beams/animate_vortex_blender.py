import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import bpy
import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block_material(style):
    obj = bpy.data.objects["denser_medium_n_1_54"]
    if style == "flat":
        return {"style": style, "opacity": .5, "reflective_shader": False}
    mat = bpy.data.materials.new("medium_display_" + style)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    # Mayavi's display RGB interpreted as sRGB, converted to linear values.
    rgb = [((v + .055) / 1.055)**2.4 for v in (.227, .188, .188)]
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["IOR"].default_value = 1.54
    shader.inputs["Metallic"].default_value = 1 if style == "mirror" else 0
    shader.inputs["Roughness"].default_value = .08 if style == "mirror" else .16 if style == "glossy" else .8
    if style == "diffuse":
        shader.inputs["Specular IOR Level"].default_value = 0
    elif style == "glossy":
        shader.inputs["Specular IOR Level"].default_value = .1
    if style == "mirror":
        shader.inputs["Base Color"].default_value = (.55, .55, .55, 1)
    mix = nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = .5
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(shader.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs["Surface"])
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return {"style": style, "opacity": .5, "display_only": True,
            "IOR": 1.54, "metallic": float(shader.inputs["Metallic"].default_value),
            "specular_ior_level": float(shader.inputs["Specular IOR Level"].default_value),
            "roughness": float(shader.inputs["Roughness"].default_value),
            "note": "Display shader only; no change to the Meep dielectric interface or field data."}


def replace_beam(path):
    obj = bpy.data.objects["measured_real2_native_grid"]
    previous = obj.data
    material = previous.materials[0]
    with np.load(path) as data:
        vertices = data["vertices"]
        faces = data["faces"]
        normals = data["normals"]
    mesh = bpy.data.meshes.new("native_phase_isosurface")
    mesh.vertices.add(len(vertices))
    mesh.vertices.foreach_set("co", vertices.ravel())
    mesh.loops.add(faces.size)
    mesh.loops.foreach_set("vertex_index", faces.ravel())
    mesh.polygons.add(len(faces))
    mesh.polygons.foreach_set("loop_start", np.arange(0, faces.size, 3, dtype=np.int32))
    mesh.polygons.foreach_set("loop_total", np.full(len(faces), 3, dtype=np.int32))
    mesh.polygons.foreach_set("use_smooth", np.ones(len(faces), dtype=bool))
    mesh.update()
    mesh.normals_split_custom_set_from_vertices(normals.tolist())
    mesh.materials.append(material)
    obj.data = mesh
    bpy.data.meshes.remove(previous)
    measured = np.empty(vertices.size, dtype=np.float32)
    mesh.vertices.foreach_get("co", measured)
    error = float(np.max(np.abs(measured.reshape(-1, 3) - vertices)))
    assert error < 1e-6
    return {"vertices": len(vertices), "triangles": len(faces), "import_maximum_coordinate_error": error}


def replace_texture(name, path):
    obj = bpy.data.objects[name]
    node = next(node for node in obj.data.materials[0].node_tree.nodes if node.type == "TEX_IMAGE")
    previous = node.image
    node.image = bpy.data.images.load(str(path), check_existing=False)
    node.interpolation = "Closest"
    if previous.users == 0:
        bpy.data.images.remove(previous)


def main():
    parser = argparse.ArgumentParser(description="Render native-grid vortex frames in the verified Blender scene")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--material", choices=("flat", "diffuse", "glossy", "mirror"), default="diffuse")
    parser.add_argument("--preview", action="store_true", help="Render only a material test of the existing static measured scene")
    parser.add_argument("--samples", type=int, default=16)
    parser.add_argument("--resolution", type=int, default=720)
    parser.add_argument("--limit", type=int, help="Limit frames for a render smoke check")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    root = args.directory.resolve()
    started = time.monotonic()
    base = root / "vortex_3d.blend"
    bpy.ops.wm.open_mainfile(filepath=str(base))
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 5
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 1
    scene.render.resolution_x = scene.render.resolution_y = args.resolution
    material = block_material(args.material)
    settings = {"blender": bpy.app.version_string, "engine": scene.render.engine,
                "threads": 1, "device": "CPU", "samples": args.samples,
                "resolution": args.resolution, "denoising": True, "material": material,
                "base_scene_sha256": digest(base), "fixed_camera": list(scene.camera.matrix_world),
                "cut_planes": 2, "red_direction_annotations": 3, "spatial_stride": 1}
    settings["fixed_camera"] = [list(row) for row in scene.camera.matrix_world]
    if args.preview:
        out = root / "animation/materials"
        out.mkdir(parents=True, exist_ok=True)
        native = root / "native3d"
        static = json.loads((native / "scene.json").read_text())
        assert digest(native / "real2.npz") == static["surfaces"]["real2"]["sha256"]
        settings["native_mesh_import"] = replace_beam(native / "real2.npz")
        scene.render.filepath = str(out / (args.material + ".png"))
        bpy.ops.render.render(write_still=True)
        settings["output_sha256"] = digest(Path(scene.render.filepath))
        (out / (args.material + ".json")).write_text(json.dumps(settings, indent=2))
        print("MATERIAL_PREVIEW_COMPLETE", json.dumps(settings), flush=True)
        return
    prepared = root / "animation/vortex"
    manifest = json.loads((prepared / "animation.json").read_text())
    assert manifest["passed"] and manifest["validation"]["passed"]
    assert manifest["spatial_stride"] == 1
    output = prepared / "rendered"
    output.mkdir(exist_ok=True)
    frames = []
    for index, frame in enumerate(manifest["frames"][:args.limit]):
        folder = prepared / frame["directory"]
        assert folder.resolve().is_relative_to(prepared.resolve())
        for name in ("real2.npz", "real2_incident.png", "real2_reflected.png"):
            assert digest(folder / name) == frame["artifact_hashes"][name], name
        mesh = replace_beam(folder / "real2.npz")
        replace_texture("incident_x_boundary", folder / "real2_incident.png")
        replace_texture("reflected_y_boundary", folder / "real2_reflected.png")
        target = output / f"frame_{index:03d}.png"
        scene.cycles.seed = 0
        scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)
        frames.append({"index": index, "file": target.name, "sha256": digest(target), **mesh})
        settings.update(frames=frames, elapsed_seconds=time.monotonic() - started, complete=False)
        (output / "render.json").write_text(json.dumps(settings, indent=2))
        print("VORTEX_FRAME_COMPLETE", json.dumps(frames[-1]), flush=True)
    settings.update(complete=len(frames) == len(manifest["frames"]),
                    animation_manifest_sha256=digest(prepared / "animation.json"))
    (output / "render.json").write_text(json.dumps(settings, indent=2))
    print("VORTEX_RENDER_COMPLETE", json.dumps(settings), flush=True)


if __name__ == "__main__":
    main()
