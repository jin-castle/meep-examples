"""Run the archived Gaussian-beam experiment through its existing wrapper.

This entry point uses code/optical_beams/run_original.py and its vendored
Optical-beams-MEEP source, not Beam Lab's analytic-current implementation.
It preserves the archived 30/45-degree model and sampling method.
Requires an existing Meep 1.33.0 environment with NumPy, SciPy and h5py.

Upstream: Daniel Kotik and Joerg Goette, Optical-beams-MEEP 2.1.2,
commit ca145119e5bd0f0804d846ea42e35e4c3daa91de; DOI 10.5281/zenodo.5211251.
MIT License, Copyright (c) 2018 Daniel Kotik.
The complete upstream notice remains in optical_beams/source/LICENSE.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--angle", type=int, choices=(30, 45), default=30,
                        help="incidence angle from the interface normal")
    parser.add_argument("--out", type=Path, default=Path("results/gaussian-beam"),
                        help="parent output folder; case folder planar30/45 is added")
    args = parser.parse_args()
    archive = Path(__file__).resolve().parent / "optical_beams"
    wrapper = archive / "run_original.py"
    upstream = archive / "source"
    for needed in (wrapper, upstream / "scripts/Gauss_2d/Gauss2d.py", upstream / "LICENSE"):
        if not needed.is_file():
            parser.error(f"Missing {needed}; use this script inside the complete repository checkout")
    output = args.out.resolve() / f"planar{args.angle}"
    env = os.environ.copy()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        env[key] = "1"
    subprocess.run([sys.executable, str(wrapper), "--upstream", str(upstream),
                    "--output", str(output), "--chi", str(args.angle),
                    "--interface", "planar"], env=env, check=True)


if __name__ == "__main__":
    main()
