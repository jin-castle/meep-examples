"""Blender background renderer for measured native-resolution Meep contours.

blender --background --factory-startup --threads 1 --python this.py -- DIRECTORY
"""

import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector
import numpy as np


def material(name, color, emission=False, opacity=1):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeEmission" if emission else "ShaderNodeBsdfDiffuse")
    shader.inputs["Color"].default_value = (*color, 1)
    if opacity < 1:
        transparent = nodes.new("ShaderNodeBsdfTransparent")
        mix = nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = opacity
        mat.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
        mat.node_tree.links.new(shader.outputs[0], mix.inputs[2])
        shader = mix
    mat.node_tree.links.new(shader.outputs[0], output.inputs["Surface"])
    return mat


def mesh_object(name, vertices, faces, mat):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def segment(name, start, end, radius, mat, tip=False):
    start, end = Vector(start), Vector(end)
    direction = end - start
    if tip:
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius, radius2=0,
                                       depth=direction.length, location=(start + end) / 2)
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius,
                                           depth=direction.length, location=(start + end) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    obj["expected_start"] = list(start)
    obj["expected_end"] = list(end)
    obj.data.materials.append(mat)
    return obj


def cut_plane(name, vertices, image_path, border_material):
    mat = bpy.data.materials.new(name + "_measured_texture")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeEmission")
    image = nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.load(str(image_path), check_existing=True)
    image.interpolation = "Closest"
    mat.node_tree.links.new(image.outputs["Color"], shader.inputs["Color"])
    mat.node_tree.links.new(shader.outputs[0], output.inputs["Surface"])
    obj = mesh_object(name, vertices, [(0, 1, 2, 3)], mat)
    uv = obj.data.uv_layers.new(name="measured_coordinates")
    for loop, coordinate in zip(uv.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        loop.uv = coordinate
    for index in range(4):
        segment(name + "_border", vertices[index], vertices[(index + 1) % 4], .006, border_material)
    return obj


def scene_for(root, scalar, samples, resolution):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 3
    scene.cycles.transparent_max_bounces = 12
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 1
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    world = bpy.data.worlds.new("black_background")
    world.use_nodes = True
    next(n for n in world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (0, 0, 0, 1)
    scene.world = world
    prepared = root / "native3d"
    metadata = json.loads((prepared / "scene.json").read_text())
    white = material("measured_2percent_isosurface", (.85, .85, .85))
    red = material("geometric_optics_red", (.8, .012, .006), emission=True)
    border = material("cut_plane_outline", (.23, .23, .23), emission=True)
    medium = material("n_1_54_annotation", (.03, .024, .024), emission=True, opacity=.5)
    data = np.load(prepared / (scalar + ".npz"))
    beam = mesh_object("measured_" + scalar + "_native_grid", data["vertices"].tolist(), data["faces"].tolist(), white)
    for polygon in beam.data.polygons:
        polygon.use_smooth = True
    beam.data.normals_split_custom_set_from_vertices(data["normals"].tolist())
    (xl, xr), (yl, yr), (zl, zr) = (metadata["coordinates"][key] for key in "xyz")
    cut_plane("incident_x_boundary", [(xl, yl, zl), (xl, yr, zl), (xl, yr, zr), (xl, yl, zr)],
              prepared / (scalar + "_incident.png"), border)
    cut_plane("reflected_y_boundary", [(xl, yr, zl), (xr, yr, zl), (xr, yr, zr), (xl, yr, zr)],
              prepared / (scalar + "_reflected.png"), border)
    sx, sy = xr - xl, yr - yl
    angle = math.radians(45)
    corners = [(x, y, z) for z in (zl, zr) for y in (-sy / 1.5, 0) for x in (-sx / 2, sx / 2)]
    rotated = [(math.cos(angle) * x - math.sin(angle) * y,
                math.sin(angle) * x + math.cos(angle) * y, z) for x, y, z in corners]
    mesh_object("denser_medium_n_1_54", rotated,
                [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
                 (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)], medium)
    eta = math.asin(math.sin(angle) / 1.54)
    length = 3.5
    incident = (-length, 0, 0)
    reflected = (0, length, 0)
    transmitted = (length * math.sin(eta + angle), -length * math.cos(eta + angle), 0)
    segment("incident_ray", incident, (0, 0, 0), .008, red)
    for name, endpoint in (("reflected", reflected), ("transmitted", transmitted)):
        direction = Vector(endpoint)
        shoulder = direction * .87
        segment(name + "_ray", (0, 0, 0), shoulder, .008, red)
        segment(name + "_arrow", shoulder, endpoint, .025, red, tip=True)
    # mlab focalpoint='auto' is the center of all visible prop bounds.
    bpy.context.view_layer.update()
    endpoint_errors = []
    for obj in scene.objects:
        if "expected_start" not in obj:
            continue
        half_length = (Vector(obj["expected_end"]) - Vector(obj["expected_start"])).length / 2
        actual_start = obj.matrix_world @ Vector((0, 0, -half_length))
        actual_end = obj.matrix_world @ Vector((0, 0, half_length))
        endpoint_errors.extend([(actual_start - Vector(obj["expected_start"])).length,
                                (actual_end - Vector(obj["expected_end"])).length])
    assert max(endpoint_errors) < 2e-6, endpoint_errors
    all_corners = [obj.matrix_world @ Vector(corner) for obj in scene.objects
                   if obj.type == "MESH" for corner in obj.bound_box]
    bounds = np.array(all_corners)
    center = Vector((bounds.max(axis=0) + bounds.min(axis=0)) / 2)
    camera_data = bpy.data.cameras.new("original_mayavi_camera")
    camera = bpy.data.objects.new("original_mayavi_camera", camera_data)
    scene.collection.objects.link(camera)
    offset = Vector(metadata["camera"]["relative_position"])
    up = Vector(metadata["camera"]["up"])
    back = offset.normalized()
    right = up.cross(back).normalized()
    up = back.cross(right).normalized()
    camera.matrix_world = Matrix((right, up, back)).transposed().to_4x4()
    camera.location = center + offset
    camera_data.type = "PERSP"
    camera_data.sensor_fit = "VERTICAL"
    camera_data.sensor_height = 32
    camera_data.lens = 32 / (2 * math.tan(math.radians(15)))
    scene.camera = camera
    framing_points = [obj.matrix_world @ vertex.co for obj in scene.objects
                      if obj.type == "MESH" and len(obj.data.vertices) < 1000
                      for vertex in obj.data.vertices]
    distance_scale = 1.0
    for _ in range(40):
        bpy.context.view_layer.update()
        projected = [world_to_camera_view(scene, camera, point) for point in framing_points]
        if all(.05 <= point.x <= .95 and .05 <= point.y <= .95 for point in projected):
            break
        distance_scale *= 1.025
        camera.location = center + offset * distance_scale
    else:
        raise RuntimeError("Could not frame measured scene with five-percent margin")
    for name, position, power, size in (("key", center + offset + Vector((0, 0, 3)), 1500, 7),
                                        ("fill", center + Vector((2, -4, 6)), 800, 6)):
        light_data = bpy.data.lights.new(name, type="AREA")
        light_data.energy = power
        light_data.shape = "DISK"
        light_data.size = size
        light = bpy.data.objects.new(name, light_data)
        scene.collection.objects.link(light)
        light.location = position
        light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(root / ("vortex_3d.png" if scalar == "real2" else "vortex_3d_modulus.png"))
    bpy.ops.file.pack_all()
    blend_path = root / ("vortex_3d.blend" if scalar == "real2" else "vortex_3d_modulus.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.render.render(write_still=True)
    result = {"scalar": scalar, "blender": bpy.app.version_string, "engine": scene.render.engine,
              "threads": scene.render.threads, "samples": samples, "resolution": resolution,
              "camera_position": list(camera.location), "camera_target": list(center),
              "camera_distance_scale": distance_scale, "camera_margin": .05,
              "camera_framing_note": "Original view orientation retained; distance fitted to actual cell extents with five-percent margin.",
              "denoising": scene.cycles.use_denoising,
              "camera_up": list(up), "measured_triangles": len(data["faces"]),
              "cut_planes": 2, "material_block": True, "red_rays": 3,
              "maximum_annotation_endpoint_error": max(endpoint_errors),
              "rays": {"incident_start": list(incident), "reflected_end": list(reflected),
                       "transmitted_end": list(transmitted)},
              "output": Path(scene.render.filepath).name, "blend": blend_path.name, "passed": True}
    (prepared / ("render_" + scalar + ".json")).write_text(json.dumps(result, indent=2))
    print("BLENDER_RENDER_COMPLETE", json.dumps(result), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--scalar", choices=("real2", "modulus2", "both"), default="both")
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--resolution", type=int, default=1200)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    for scalar in (("real2", "modulus2") if args.scalar == "both" else (args.scalar,)):
        scene_for(args.directory.resolve(), scalar, args.samples, args.resolution)


if __name__ == "__main__":
    main()
