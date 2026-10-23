import json
import shutil
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    result = json.loads((root / "result.json").read_text())
    site = root / "site-assets"
    site.mkdir(exist_ok=True)
    result.update({
        "grid_shape": result["design_grid"],
        "f_initial": result["objective_initial"],
        "f_updated": result["objective_updated"],
        "gradient_gate": {
            "passed": all(row["passed"] for row in result["finite_difference_gate"]),
            "max_relative_error": max(row["relative_error"] for row in result["finite_difference_gate"]),
            "checks": result["finite_difference_gate"],
        },
        "update_method": result["update"]["method"],
        "step": result["update"]["max_density_change"],
        "export_pixels": 720,
        "native_field_sampling": "60 pixels/um; 1um design region; raster export uses nearest samples without smoothing",
        "raw_arrays": "fields.npz (packaged with reproducibility source, outside static-site assets)",
    })
    for filename in (
        "forward-design.png", "adjoint-design.png", "gradient-design.png",
        "forward-full.png", "adjoint-full.png", "updated-forward-design.png",
        "updated-forward-full.png", "density-initial.png", "density-updated.png",
    ):
        shutil.copy2(root / filename, site / filename)
    (site / "result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({"site_assets": str(site), "files": len(list(site.iterdir())), "f_initial": result["f_initial"], "f_updated": result["f_updated"]}, indent=2))


if __name__ == "__main__":
    main()
