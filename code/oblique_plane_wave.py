"""Launch and measure the official homogeneous-medium oblique plane wave.

Adapted from NanoComp/meep python/examples/oblique-planewave.py at
f7811d4157ea22f19d4ca76bc41c71b6e055763e and the project's pw_run.py.
Upstream tutorial: https://meep.readthedocs.io/en/latest/Python_Tutorials/Eigenmode_Source/#planewaves-in-homogeneous-media
Keep the upstream Meep license; see assets/meep/17/provenance.json.
The published figures use the archived 2026-11-09 runs, not a new execution.
"""

import argparse
import json
import math
from pathlib import Path
import time

import numpy as np


def measure_field(field, resolution):
    """Preserve the archived phase-fit and windowed-FFT diagnostics."""
    dx = 1 / resolution
    crop = slice(int(2 * resolution), int(8 * resolution))
    sub = field[crop, crop]
    result = {"complex": bool(np.iscomplexobj(field))}
    if np.iscomplexobj(field):
        kx = np.angle(np.sum(sub[1:, :] * np.conj(sub[:-1, :]))) / (2 * math.pi * dx)
        ky = np.angle(np.sum(sub[:, 1:] * np.conj(sub[:, :-1]))) / (2 * math.pi * dx)
        result.update(kx=float(kx), ky=float(ky), k_mag=float(math.hypot(kx, ky)),
                      angle_fit=float(math.degrees(math.atan2(ky, kx))), k_expected=1.5)
    window = np.hanning(sub.shape[0])[:, None] * np.hanning(sub.shape[1])[None, :]
    power = np.abs(np.fft.fftshift(np.fft.fft2(sub * window))) ** 2
    fx = np.fft.fftshift(np.fft.fftfreq(sub.shape[0], dx))
    fy = np.fft.fftshift(np.fft.fftfreq(sub.shape[1], dx))
    i, j = np.unravel_index(np.argmax(power), power.shape)

    def box(ii, jj, radius=3):
        return power[max(ii - radius, 0):ii + radius + 1,
                     max(jj - radius, 0):jj + radius + 1].sum()

    # Retain the archive's mirrored FFT-index convention for comparability.
    # This finite-window spectral ratio is NOT reflected Poynting power.
    ib, jb = power.shape[0] - 1 - i, power.shape[1] - 1 - j
    result.update(fft_peak_k=[float(fx[i]), float(fy[j])],
                  fft_peak_angle=float(math.degrees(math.atan2(fy[j], fx[i]))),
                  backward_fraction_fft=float(box(ib, jb) / box(i, j)))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--angle", type=float, default=40, help="CCW degrees from +x")
    parser.add_argument("--resolution", type=float, default=50, help="pixels per micrometre")
    parser.add_argument("--until", type=float, default=23.56, help="Meep time units")
    parser.add_argument("--tag", default="pw_a40", help="output filename stem")
    parser.add_argument("--out", type=Path, default=Path("oblique-plane-wave-output"))
    parser.add_argument("--plot", action="store_true", help="also save a real-Ez PNG with matplotlib")
    args = parser.parse_args()
    if args.resolution < 4 or args.until <= 0:
        parser.error("resolution must be >= 4 and until must be positive")
    if not args.tag or Path(args.tag).name != args.tag:
        parser.error("tag must be a filename stem")
    import meep as mp

    start = time.time()
    angle = math.radians(args.angle % 360)
    k_point = mp.Vector3(1.5, 0, 0).rotate(mp.Vector3(0, 0, 1), angle)
    if angle == 0:
        direction, parity, mirrors, eig_vol = mp.AUTOMATIC, mp.EVEN_Y + mp.ODD_Z, [mp.Mirror(mp.Y)], None
    else:
        direction, parity, mirrors = mp.NO_DIRECTION, mp.ODD_Z, []
        eig_vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(0, 1 / args.resolution, 0))
    source = mp.EigenModeSource(
        src=mp.ContinuousSource(1.0), center=mp.Vector3(), size=mp.Vector3(0, 10, 0),
        direction=direction, eig_kpoint=k_point, eig_band=1, eig_parity=parity, eig_vol=eig_vol)
    sim = mp.Simulation(
        cell_size=mp.Vector3(14, 10, 0), resolution=args.resolution,
        boundary_layers=[mp.PML(2, direction=mp.X)], sources=[source],
        k_point=k_point, default_material=mp.Medium(index=1.5), symmetries=mirrors)
    sim.run(until=args.until)
    field = np.asarray(sim.get_array(component=mp.Ez, center=mp.Vector3(), size=mp.Vector3(10, 10)))
    result = dict(res=args.resolution, angle=args.angle, until=args.until,
                  steps=sim.timestep(), wall=time.time() - start, **measure_field(field, args.resolution))
    if mp.am_master():
        args.out.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.out / f"{args.tag}.npz", Ez=field, extent=np.array([-5, 5, -5, 5]))
        (args.out / f"{args.tag}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        if args.plot:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            limit = np.percentile(np.abs(field.real), 99.5)
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.imshow(field.real.T, origin="lower", extent=(-5, 5, -5, 5),
                      cmap="RdBu_r", vmin=-limit, vmax=limit)
            ax.set(xlabel="x (µm)", ylabel="y (µm)", title=f"Re Ez, requested angle {args.angle:g}°")
            fig.savefig(args.out / f"{args.tag}.png", dpi=150, bbox_inches="tight")
            plt.close(fig)
        print("RESULT " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
