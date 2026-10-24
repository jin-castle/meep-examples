import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageSequence


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size):
    for name in ("DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    raise RuntimeError("A readable TrueType font is required")


def annotate(image, frame, manifest):
    width, height = image.size
    canvas = Image.new("RGB", (width, height + 92), "black")
    canvas.paste(image, (0, 38))
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 9), "LG m=2 | monochromatic phase cycle", fill="white", font=font(20))
    fraction = frame["phase_radians"] / np.pi
    delta = frame["physical_time_offset"]
    draw.text((16, height + 42), f"phase = {fraction:.3f} pi   |   delta t = {delta:.5f} a/c",
              fill=(225, 225, 225), font=font(16))
    draw.text((16, height + 66), "Native grid | fixed 2% surface | steady state, no turn-on",
              fill=(160, 160, 160), font=font(15))
    return canvas


def material_comparison(directory):
    root = directory / "animation/materials"
    labels = {"diffuse": "Original-style translucent", "glossy": "Subtle glossy (display only)"}
    panels, settings = [], {}
    for style, label in labels.items():
        settings[style] = json.loads((root / (style + ".json")).read_text())
        path = root / (style + ".png")
        assert digest(path) == settings[style]["output_sha256"]
        image = Image.open(path).convert("RGB")
        panel = Image.new("RGB", (image.width, image.height + 55), "black")
        panel.paste(image, (0, 55))
        ImageDraw.Draw(panel).text((20, 18), label, fill="white", font=font(24))
        panels.append(panel)
    for key in ("base_scene_sha256", "fixed_camera", "samples", "resolution", "engine"):
        assert settings["diffuse"][key] == settings["glossy"][key], key
    comparison = Image.new("RGB", (sum(panel.width for panel in panels), panels[0].height), "black")
    comparison.paste(panels[0], (0, 0))
    comparison.paste(panels[1], (panels[0].width, 0))
    comparison.save(root / "comparison.png")
    (root / "checks.json").write_text(json.dumps({"passed": True, "display_only": True,
        "same_meep_field_and_geometry": True, "original_mayavi_opacity": .5,
        "original_script_has_no_mirror_shader": True, "settings": settings,
        "comparison_sha256": digest(root / "comparison.png")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Package measured vortex phase renders as a labeled loop")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--duration-ms", type=int, default=80)
    parser.add_argument("--materials-only", action="store_true")
    args = parser.parse_args()
    if args.duration_ms < 10 or args.duration_ms % 10:
        parser.error("GIF duration must be a positive multiple of 10 ms")
    if args.materials_only:
        material_comparison(args.directory.resolve())
        return
    root = args.directory.resolve() / "animation/vortex"
    manifest = json.loads((root / "animation.json").read_text())
    render = json.loads((root / "rendered/render.json").read_text())
    assert render["complete"] and len(render["frames"]) == len(manifest["frames"])
    assert render["animation_manifest_sha256"] == digest(root / "animation.json")
    frames, differences, raw = [], [], []
    for frame, rendered in zip(manifest["frames"], render["frames"]):
        path = root / "rendered" / rendered["file"]
        assert digest(path) == rendered["sha256"]
        image = Image.open(path).convert("RGB")
        raw.append(np.asarray(image, dtype=np.int16))
        frames.append(annotate(image, frame, manifest))
    for index in range(len(raw)):
        difference = np.abs(raw[(index + 1) % len(raw)] - raw[index])
        differences.append({"from": index, "to": (index + 1) % len(raw),
                            "mean_absolute_rgb_difference": float(difference.mean()),
                            "changed_pixel_fraction": float(np.mean(np.max(difference, axis=2) > 12))})
    assert all(item["changed_pixel_fraction"] > .005 for item in differences), differences
    tile_width = 360
    tile_height = round(frames[0].height * tile_width / frames[0].width)
    contact = Image.new("RGB", (tile_width * 3, tile_height * 2), "black")
    for tile, index in enumerate(np.linspace(0, len(frames) - 1, 6, dtype=int)):
        contact.paste(frames[index].resize((tile_width, tile_height), Image.Resampling.LANCZOS),
                      ((tile % 3) * tile_width, (tile // 3) * tile_height))
    contact.save(root / "contact_sheet.png")
    frames[0].save(root / "poster.png")
    palette = contact.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    gif, webp = root / "vortex_wavefront.gif", root / "vortex_wavefront.webp"
    indexed[0].save(gif, save_all=True, append_images=indexed[1:], loop=0,
                    duration=args.duration_ms, disposal=2, optimize=False)
    frames[0].save(webp, save_all=True, append_images=frames[1:], loop=0,
                   duration=args.duration_ms, quality=85, method=6)
    checks = {}
    for path in (gif, webp):
        with Image.open(path) as image:
            assert image.is_animated and image.n_frames == len(frames)
            decoded = [np.asarray(frame.convert("RGB")) for frame in ImageSequence.Iterator(image)]
            assert all(np.any(decoded[index] != decoded[index - 1]) for index in range(1, len(decoded)))
            checks[path.name] = {"frames": image.n_frames, "size": list(image.size),
                                 "bytes": path.stat().st_size, "sha256": digest(path)}
    metadata = {"kind": "Meep complex snapshot monochromatic phase reconstruction",
                "not_transient_or_dft_accumulator": True, "passed": True,
                "frames": len(frames), "spatial_stride": 1, "duration_ms": args.duration_ms,
                "loop_seconds": len(frames) * args.duration_ms / 1000,
                "physical_squared_field_period_a_over_c": .1,
                "phase_interval": "[0, pi), endpoint excluded; squared field repeats every T/2",
                "fixed_normalization": manifest["normalization"], "motion_differences": differences,
                "fdtd_validation": manifest["validation"], "render_settings": render,
                "scientific_provenance": {key: manifest[key] for key in (
                    "source_h5_sha256", "baseline_h5_sha256", "snapshot_time", "frequency",
                    "time_convention", "formula", "raw_grid_shape", "half_shape",
                    "crop_cells_each_face", "mesh_decimation", "geometric_smoothing",
                    "maximum_contour_residual_fraction_global_maximum", "baseline_comparison", "cuts")},
                "animation_manifest_sha256": digest(root / "animation.json"),
                "artifacts": {**checks, **{name: {"sha256": digest(root / name),
                                                      "bytes": (root / name).stat().st_size}
                                           for name in ("poster.png", "contact_sheet.png")}}}
    (root / "checks.json").write_text(json.dumps(metadata, indent=2))
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
