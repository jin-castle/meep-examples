import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image, ImageDraw


FULL_EXTENT = [-3.0, 3.0, -2.5, 2.5]
DESIGN_EXTENT = [-0.5, 0.5, -0.5, 0.5]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fields", type=Path)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "assets/meep/09/highres")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    result_path = args.out / "result.json"
    result = json.loads(result_path.read_text())
    raw = np.load(args.fields)
    rendering = {
        "source": "saved complex128 full-cell Ez DFT, fields.npz",
        "source_sha256": hashlib.sha256(args.fields.read_bytes()).hexdigest(),
        "quantity": "Re(Ez); original complex phase, no phase rotation",
        "colormap": "RdBu",
        "sign": "negative red; zero white; positive blue",
        "full_extent_um": FULL_EXTENT,
        "design_extent_um": DESIGN_EXTENT,
        "scene_pixels": [360, 300],
        "capture_pixels": [720, 720],
        "native_design_pixels": [60, 60],
        "native_spacing_um": 1 / 60,
        "orientation": "RGBA[row,col] = RdBu(normalize(real(Ez[col,Ny-1-row]))); top is +y",
        "capture_rendering": "exact full-scene design crop, nearest enlargement, black boundary and centered port markers",
        "scenes": {},
    }
    for prefix, stem in (("forward", "forward"), ("adjoint", "adjoint"), ("updated_forward", "updated-forward")):
        values = np.real(raw[f"{prefix}_full_Ez"])
        x, y = raw[f"{prefix}_full_x"], raw[f"{prefix}_full_y"]
        assert values.shape == (360, 300)
        assert np.allclose(np.diff(x), 1 / 60) and np.allclose(np.diff(y), 1 / 60)
        limit = float(np.max(np.abs(values)))
        rgba = matplotlib.colormaps["RdBu"]((values.T[::-1] / limit + 1) / 2, bytes=True)
        scene_name = f"{stem}-scene.png"
        Image.fromarray(rgba).save(args.out / scene_name)
        entry = {"scene": scene_name, "symmetric_limit": limit, "vmin": -limit, "vmax": limit}
        if prefix != "updated_forward":
            ix = np.flatnonzero((x >= -.5) & (x <= .5))
            iy = np.flatnonzero((y >= -.5) & (y <= .5))
            assert len(ix) == len(iy) == 60
            left, top = int(ix[0]), int(len(y) - 1 - iy[-1])
            crop = rgba[top:top + 60, left:left + 60]
            expected = matplotlib.colormaps["RdBu"]((values[np.ix_(ix, iy)].T[::-1] / limit + 1) / 2, bytes=True)
            assert np.array_equal(crop, expected)
            capture = Image.fromarray(crop).resize((720, 720), Image.Resampling.NEAREST)
            outline = ImageDraw.Draw(capture)
            outline.rectangle((0, 0, 719, 719), outline="black", width=3)
            outline.line((0, 180, 0, 540), fill="black", width=5)
            outline.line((180, 0, 540, 0), fill="black", width=5)
            capture_name = f"{stem}-capture.png"
            capture.save(args.out / capture_name)
            assert np.array_equal(np.asarray(capture)[5:-5, 5:-5], np.asarray(Image.fromarray(crop).resize((720, 720), Image.Resampling.NEAREST))[5:-5, 5:-5])
            entry.update({"capture": capture_name, "capture_limit": limit, "scene_crop_box_pixels": [left, top, left + 60, top + 60], "capture_matches_scene_interior": True})
        assert np.array_equal(np.asarray(Image.open(args.out / scene_name)), rgba)
        rendering["scenes"][stem] = entry
    result["scene_rendering"] = rendering
    result_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(rendering, indent=2))


if __name__ == "__main__":
    main()
