import hashlib
import json

import numpy as np

from extract_highres import OUT, save_field, save_grid


def main():
    raw = np.load(OUT / "fields.npz")
    result = json.loads((OUT / "result.json").read_text())
    for prefix, tag in (("forward", "forward"), ("adjoint", "adjoint"), ("updated_forward", "updated-forward")):
        for region_name in ("design", "full"):
            region = {key: raw[f"{prefix}_{region_name}_{key}"] for key in ("Ez", "x", "y")}
            save_field(region, f"{tag}-{region_name}.png", f"{tag} Re(Ez), resolution 60 pixels/um", region_name == "design")
    save_grid(raw["gradient"], "gradient-design.png", True)
    save_grid(raw["density_initial"], "density-initial.png")
    save_grid(raw["density_updated"], "density-updated.png")
    result["rendering_coordinates"] = "imshow pixel edges from stored physical sample centers; axes cropped to requested full/design extent"
    result["script_sha256"] = hashlib.sha256((OUT / "extract_highres.py").read_bytes()).hexdigest()
    (OUT / "result.json").write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
