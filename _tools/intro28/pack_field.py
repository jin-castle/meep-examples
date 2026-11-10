"""Pack a saved complex Meep Ey cross-section; does not run a simulation."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
args = parser.parse_args()
folder = Path(__file__).resolve().parent
source = args.source.resolve()
d = np.load(source, allow_pickle=False)
re, im = d["ey_re"], d["ey_im"]
lim = float(np.max(np.hypot(re, im)))
rgba = np.zeros((re.shape[1], re.shape[0], 4), dtype=np.uint8)
rgba[:, :, 0] = np.rint(np.clip(re.T / lim, -1, 1) * 127.5 + 127.5)
rgba[:, :, 1] = np.rint(np.clip(im.T / lim, -1, 1) * 127.5 + 127.5)
rgba[:, :, 3] = 255
packed = rgba.tobytes()
(folder / "field.bin").write_bytes(packed)
runfile = source.with_name(source.name.replace("_ey.npz", ".json"))
run = json.loads(runfile.read_text())
info = {
    "source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "run_metadata_sha256": hashlib.sha256(runfile.read_bytes()).hexdigest(),
    "field_sha256": hashlib.sha256(packed).hexdigest(),
    "nx": int(re.shape[0]), "ny": int(re.shape[1]), "extent": d["extent"].tolist(),
    "encoding": "RGBA8, rows y ascending, columns x ascending; R=Re(Ey)/lim and G=Im(Ey)/lim mapped from [-1,1] to [0,255]; B=0,A=255",
    "lim": lim, "max_component_quantization_error_normalized": 1 / 255,
    "fcen": run["fcen"], "kz": run["kz"], "gap": run["s"], "mode": run["mode"],
    "resolution": run["resolution"], "index": 3.45,
    "formula": "Re[(Ey_re(x,y)+i*Ey_im(x,y))*exp(i*(2*pi*kz*z-phase))]",
    "units": "dimensionless normalized lattice units: a=1; frequency fa/c; kz*a",
    "interpretation": "Saved Meep complex transverse DFT field extended with the known Bloch propagation factor; steady-state phase cycle, not a 3D transient simulation. Finite z length and ground grid are display geometry.",
    "display": {"rod_length_a": 9, "loop_seconds": 8, "phase_cycles": 2, "fps": 30, "size": [1280, 720],
                "colormap": "RdBu, negative red, positive blue, zero white; signed color clamp(1.25*Re(Ey)/lim,-1,1)",
                "fixed_color_gain": 1.25,
                "opacity": "1-exp(-3.8*abs(Re(Ey)/lim)^1.3*ray_step); zero field transparent; complex magnitude below .012 omitted as display threshold"},
}
(folder / "field.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
print(json.dumps(info, indent=2))
