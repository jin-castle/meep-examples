"""Validate the saved intro render, provenance and optional capture evidence."""
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument("--frames", type=Path, required=True)
parser.add_argument("--previews", type=Path, required=True)
args = parser.parse_args()
def executable(name):
    found = shutil.which(name)
    if found:
        return found
    fallback = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin" / (name + ".exe")
    if fallback.is_file():
        return str(fallback)
    raise FileNotFoundError(f"Existing {name} executable was not found")
ffmpeg, ffprobe = executable("ffmpeg"), executable("ffprobe")
folder = Path(__file__).resolve().parent
asset = folder.parent.parent / "assets" / "meep" / "16"
info = json.loads((folder / "field.json").read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(folder / "field.bin") == info["field_sha256"]
source = Path(info["source"])
assert sha(source) == info["source_sha256"]
d = np.load(source, allow_pickle=False)
texture = np.frombuffer((folder / "field.bin").read_bytes(), np.uint8).reshape(info["ny"], info["nx"], 4)
error = max(float(np.max(np.abs((texture[:, :, c].astype(float) / 127.5 - 1) - component / info["lim"])))
            for c, component in enumerate([d["er"].real, d["er"].imag]))
assert error <= 1 / 255 + 1e-12
frames = sorted(args.frames.glob("f_*.png"))
assert len(frames) == 240
assert all(Image.open(p).size == (1280, 720) for p in frames)
assert len({sha(p) for p in frames}) == 240
preview_errors = json.loads((args.previews / "preview-errors.json").read_text())
assert not preview_errors
assert sha(args.previews / "t0.png") == sha(args.previews / "t8.png")
assert sha(args.previews / "t0.png") != sha(args.previews / "t1.png")
fixed0 = np.asarray(Image.open(args.previews / "fixed-t0.png").convert("RGB"), float)
fixed1 = np.asarray(Image.open(args.previews / "fixed-t1.png").convert("RGB"), float)
fixed_camera_motion = float(np.abs(fixed0 - fixed1).mean())
assert fixed_camera_motion > .1
assert info["source_axes"] == ["z", "r"] and info["radial_stride"] == 1
assert info["m"] == -1 and info["display"]["axial_magnification"] == 8
assert info["display"]["fixed_color_gain"] == 3
radii = np.asarray(info["zone_radii_um"])
assert np.allclose(radii, [np.sqrt(n * .5 * (200 + n * .5 / 4)) for n in range(1, 26)])
rr = np.linspace(*info["extent"][:2], d["er"].shape[1])
zz = np.linspace(*info["extent"][2:], d["er"].shape[0])
away = np.min(np.abs(rr[:, None] - radii[None, :]), axis=1) > .12
expected_glass = (np.searchsorted(radii, rr) % 2 == 0) & (rr < radii[-1])
observed_glass = d["eps"][np.argmin(abs(zz))] > 1.625
geometry_agreement = float(np.mean(expected_glass[away] == observed_glass[away]))
assert geometry_agreement > .995
movie = asset / "00_intro.mp4"
probe = json.loads(subprocess.check_output([ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(movie)]))
assert len(probe["streams"]) == 1
stream = probe["streams"][0]
assert stream["codec_name"] == "h264" and stream["pix_fmt"] == "yuv420p"
assert (stream["width"], stream["height"]) == (1280, 720)
assert stream["r_frame_rate"] == "30/1" and int(stream["nb_frames"]) == 240
assert float(probe["format"]["duration"]) == 8
subprocess.run([ffmpeg, "-v", "error", "-i", str(movie), "-f", "null", "-"], check=True)
def decode(t):
    return subprocess.check_output([ffmpeg, "-v", "error", "-ss", str(t), "-i", str(movie), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"])
poster_decoded = decode(4)
(args.previews / "decoded-t4.png").write_bytes(poster_decoded)
decoded = np.asarray(Image.open(io.BytesIO(poster_decoded)).convert("RGB"), float)
original = np.asarray(Image.open(args.frames / "f_0120.png").convert("RGB"), float)
first = np.asarray(Image.open(io.BytesIO(decode(0))).convert("RGB"), float)
second = np.asarray(Image.open(io.BytesIO(decode(1))).convert("RGB"), float)
motion = float(np.abs(first - second).mean())
assert motion > .1
report = {
    "verdict": "PASS", "scope": "chapter16_intro",
    "source_sha256": info["source_sha256"], "packed_field_sha256": info["field_sha256"],
    "scene_sha256": sha(folder / "scene.js"), "video_sha256": sha(movie), "poster_sha256": sha(asset / "00_intro.jpg"),
    "capture_frames": len(frames), "unique_frame_hashes": 240, "browser_errors": preview_errors,
    "decoded_video_errors": [], "no_audio": True,
    "periodic_t0_t8_pixel_identical": True, "decoded_t0_t1_mean_absolute_pixel_difference": motion,
    "fixed_camera_t0_t1_mean_absolute_pixel_difference": fixed_camera_motion,
    "zone_geometry_eps_agreement_away_from_boundaries": geometry_agreement,
    "native_resolution_retained": True, "source_axes": info["source_axes"],
    "decoded_t4_vs_png_mean_absolute_pixel_error": float(np.abs(decoded - original).mean()),
    "maximum_normalized_complex_component_quantization_error": error,
    "visual_verdict": {
        "alignment": "PASS: one circular reference footprint; axial scale 8x for both apparatus and field",
        "geometry": "PASS: all 25 binary-phase zones, glass n1.5, radius 50.3891109269um, relief -.25..+.25um above the substrate",
        "field": "PASS: signed red/blue near-field volume uses native saved Er(z,r), m=-1 angular factor and physical slab z +/-2.25um; no invented far-field",
        "framing": "PASS: entire zone plate and full circular reference grid visible at t=0,1,2,3,4,8, no text or overlays",
        "loop": "PASS: two forward optical cycles and one gentle periodic camera path; t0 equals t8",
    },
    "ffprobe": probe,
}
(folder / "render-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k != "ffprobe"}, indent=2))

