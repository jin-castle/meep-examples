import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image, ImageDraw


FULL_EXTENT = [-3.0, 3.0, -2.5, 2.5]
DESIGN_EXTENT = [-0.5, 0.5, -0.5, 0.5]
PHASE_FRAME_COUNT = 32
PHASE_COLUMNS = 8
PHASE_ROWS = 4


def field_rgba(values, limit):
    return matplotlib.colormaps["RdBu"]((values.T[::-1] / limit + 1) / 2, bytes=True)


def save_phase_sprite(field, limit, path):
    phases = np.arange(PHASE_FRAME_COUNT) * 2 * np.pi / PHASE_FRAME_COUNT
    fields = np.real(field[None, :, :] * np.exp(-1j * phases[:, None, None]))
    quarter_errors = {}
    for frame, expected in ((0, field.real), (8, field.imag), (16, -field.real), (24, -field.imag)):
        error = float(np.max(np.abs(fields[frame] - expected)))
        assert error < 1e-12 * limit
        quarter_errors[str(frame)] = error
    loop_error = float(np.max(np.abs(np.real(field * np.exp(-2j * np.pi)) - fields[0])))
    assert loop_error < 1e-12 * limit
    atlas = Image.new("RGBA", (360 * PHASE_COLUMNS, 300 * PHASE_ROWS))
    for frame, values in enumerate(fields):
        atlas.paste(Image.fromarray(field_rgba(values, limit)), ((frame % PHASE_COLUMNS) * 360, (frame // PHASE_COLUMNS) * 300))
    atlas.save(path)
    saved = Image.open(path)
    for frame, values in enumerate(fields):
        left, top = (frame % PHASE_COLUMNS) * 360, (frame // PHASE_COLUMNS) * 300
        assert np.array_equal(np.asarray(saved.crop((left, top, left + 360, top + 300))), field_rgba(values, limit))
    assert not np.array_equal(field_rgba(fields[0], limit), field_rgba(fields[1], limit))
    assert not np.array_equal(field_rgba(fields[0], limit), field_rgba(fields[-1], limit))
    return {
        "sprite": path.name, "sprite_pixels": list(saved.size),
        "quarter_cycle_max_absolute_errors": quarter_errors,
        "loop_closure_max_absolute_error": loop_error,
        "saved_all_frames_match": True, "animated_content": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fields", type=Path)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[2] / "assets/meep/09/highres")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    result_path = args.out / "result.json"
    result = json.loads(result_path.read_text())
    raw = np.load(args.fields)
    source_hash = hashlib.sha256(args.fields.read_bytes()).hexdigest()
    assert result["scene_rendering"]["source_sha256"] == source_hash
    rendering = {
        "source": "saved complex128 full-cell Ez DFT, fields.npz",
        "source_sha256": source_hash,
        "quantity": "Re(Ez * exp(-i phase)); saved complex DFT phasor",
        "colormap": "RdBu",
        "sign": "negative red; zero white; positive blue",
        "full_extent_um": FULL_EXTENT,
        "design_extent_um": DESIGN_EXTENT,
        "scene_pixels": [360, 300],
        "capture_pixels": [720, 720],
        "native_design_pixels": [60, 60],
        "native_spacing_um": 1 / 60,
        "orientation": "RGBA[row,col] = RdBu(normalize(real(Ez[col,Ny-1-row] * exp(-i phase)))); top is +y",
        "capture_rendering": "exact full-scene design crop, nearest enlargement, black boundary and centered port markers",
        "phase_frame_count": PHASE_FRAME_COUNT,
        "phase_columns": PHASE_COLUMNS,
        "phase_rows": PHASE_ROWS,
        "phase_convention": "phase_k = 2*pi*k/32; Re(F*exp(-i*phase_k)); phase0 is the original real phasor",
        "normalization": "fixed symmetric +/-max(abs(complex full Ez)) per calculation, shared by every phase, scene, capture",
        "notTransient": True,
        "provenance": "DFT phase cycle / steady state; no wavefront arrival, source turn-on, or propagation delay",
        "scenes": {},
    }
    for prefix, stem in (("forward", "forward"), ("adjoint", "adjoint"), ("updated_forward", "updated-forward")):
        field = raw[f"{prefix}_full_Ez"]
        values = np.real(field)
        x, y = raw[f"{prefix}_full_x"], raw[f"{prefix}_full_y"]
        assert values.shape == (360, 300)
        assert np.allclose(np.diff(x), 1 / 60) and np.allclose(np.diff(y), 1 / 60)
        limit = float(np.max(np.abs(field)))
        rgba = field_rgba(values, limit)
        scene_name = f"{stem}-scene.png"
        Image.fromarray(rgba).save(args.out / scene_name)
        entry = {"scene": scene_name, "symmetric_limit": limit, "vmin": -limit, "vmax": limit}
        if prefix != "updated_forward":
            entry.update(save_phase_sprite(field, limit, args.out / f"{stem}-phases.png"))
            assert np.array_equal(np.asarray(Image.open(args.out / entry["sprite"]).crop((0, 0, 360, 300))), rgba)
            ix = np.flatnonzero((x >= -.5) & (x <= .5))
            iy = np.flatnonzero((y >= -.5) & (y <= .5))
            assert len(ix) == len(iy) == 60
            left, top = int(ix[0]), int(len(y) - 1 - iy[-1])
            crop = rgba[top:top + 60, left:left + 60]
            expected = field_rgba(values[np.ix_(ix, iy)], limit)
            assert np.array_equal(crop, expected)
            capture = Image.fromarray(crop).resize((720, 720), Image.Resampling.NEAREST)
            outline = ImageDraw.Draw(capture)
            outline.rectangle((0, 0, 719, 719), outline="black", width=3)
            outline.line((0, 180, 0, 540), fill="black", width=5)
            outline.line((180, 0, 540, 0), fill="black", width=5)
            capture_name = f"{stem}-capture.png"
            capture.save(args.out / capture_name)
            assert np.array_equal(np.asarray(capture)[5:-5, 5:-5], np.asarray(Image.fromarray(crop).resize((720, 720), Image.Resampling.NEAREST))[5:-5, 5:-5])
            entry.update({"capture": capture_name, "capture_limit": limit, "scene_crop_box_pixels": [left, top, left + 60, top + 60], "capture_matches_scene_interior": True, "frame0_capture_match": True, "frame0_scene_match": True})
        assert np.array_equal(np.asarray(Image.open(args.out / scene_name)), rgba)
        rendering["scenes"][stem] = entry
    x, y = raw["forward_full_x"], raw["forward_full_y"]
    y_index = int(np.argmin(np.abs(y)))
    input_mask = (x >= -1.35) & (x <= -.65)
    input_phase = np.unwrap(np.angle(raw["forward_full_Ez"][input_mask, y_index]))
    slope = float(np.polyfit(x[input_mask], input_phase, 1)[0])
    assert slope > 0
    rendering["input_phase_direction_check"] = {
        "sample_x_range_um": [float(x[input_mask][0]), float(x[input_mask][-1])],
        "sample_y_um": float(y[y_index]), "phase_slope_rad_per_um": slope,
        "convention": "positive spatial phase slope with exp(-i phase) advances constant phase toward +x",
        "direction": "source to design (+x)", "passed": True,
        "interpretation": "total steady-state field may also contain reflected waves; this is not transient arrival",
    }
    result["scene_rendering"] = rendering
    result_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(rendering, indent=2))


if __name__ == "__main__":
    main()
