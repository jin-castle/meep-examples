"""Measure absorption in a lossy cylinder using volume and surface integrals.

Adapted from NanoComp/meep absorbed_power_density.py at
f7811d4157ea22f19d4ca76bc41c71b6e055763e and the project's abs_repro.py.
Upstream licensing remains applicable; see assets/meep/25/provenance.json.
Publication reuses archived fields; this CLI executes a new run only on request.
"""
import argparse
import json
from pathlib import Path
import time

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolution", type=float, default=100, help="pixels per micrometre")
    parser.add_argument("--after-sources", type=float, default=100, help="Meep time after pulse ends")
    parser.add_argument("--tag", default="abs_r100", help="output filename stem")
    parser.add_argument("--out", type=Path, default=Path("absorbed-power-output"))
    args = parser.parse_args()
    if args.resolution <= 0 or args.after_sources <= 0:
        parser.error("resolution and after-sources must be positive")
    if not args.tag or Path(args.tag).name != args.tag:
        parser.error("tag must be a filename stem")
    import meep as mp
    from meep.materials import SiO2

    start = time.time()
    dpml, radius, air = 1.0, 1.0, 2.0
    length = 2 * (dpml + air + radius)
    frequency, big_half_width = 1.0, radius + 1.0

    def make(geometry):
        source = mp.Source(
            mp.GaussianSource(frequency, fwidth=0.1 * frequency, is_integrated=True),
            center=mp.Vector3(-0.5 * length + dpml), size=mp.Vector3(0, length), component=mp.Ez)
        return mp.Simulation(
            resolution=args.resolution, cell_size=mp.Vector3(length, length),
            boundary_layers=[mp.PML(dpml)], sources=[source], k_point=mp.Vector3(),
            symmetries=[mp.Mirror(mp.Y)], geometry=geometry)

    def inward_box(sim, half_width):
        h = half_width
        return sim.add_flux(
            frequency, 0, 1,
            mp.FluxRegion(center=mp.Vector3(x=-h), size=mp.Vector3(0, 2 * h), weight=+1),
            mp.FluxRegion(center=mp.Vector3(x=+h), size=mp.Vector3(0, 2 * h), weight=-1),
            mp.FluxRegion(center=mp.Vector3(y=+h), size=mp.Vector3(2 * h, 0), weight=-1),
            mp.FluxRegion(center=mp.Vector3(y=-h), size=mp.Vector3(2 * h, 0), weight=+1))

    # Empty-cell run: incident intensity and fields to subtract for scattering.
    sim = make([])
    incident = sim.add_flux(frequency, 0, 1, mp.FluxRegion(
        center=mp.Vector3(x=-big_half_width), size=mp.Vector3(0, 2 * radius)))
    reference_box = inward_box(sim, big_half_width)
    trace = {"t": [], "v": []}

    def record_trace(current_sim):
        trace["t"].append(current_sim.meep_time())
        probe = mp.Vector3(-0.5 * length + dpml + 0.5)
        trace["v"].append(float(np.real(current_sim.get_field_point(mp.Ez, probe))))

    sim.run(mp.at_every(0.05, record_trace), until_after_sources=args.after_sources)
    intensity = mp.get_fluxes(incident)[0] / (2 * radius)
    reference_data = sim.get_flux_data(reference_box)
    sim.reset_meep()

    sim = make([mp.Cylinder(material=SiO2, radius=radius, height=mp.inf)])
    material_fields = sim.add_dft_fields(
        [mp.Dz, mp.Ez], frequency, 0, 1, center=mp.Vector3(),
        size=mp.Vector3(2 * radius, 2 * radius), yee_grid=True)
    small_box = inward_box(sim, radius)
    big_box = inward_box(sim, big_half_width)
    scattered_box = inward_box(sim, big_half_width)
    sim.load_minus_flux_data(scattered_box, reference_data)
    field_map = sim.add_dft_fields([mp.Ez], frequency, 0, 1,
                                  center=mp.Vector3(), size=mp.Vector3(length - 2 * dpml, length - 2 * dpml))
    sim.run(until_after_sources=args.after_sources)
    displacement = sim.get_dft_array(material_fields, mp.Dz, 0)
    electric = sim.get_dft_array(material_fields, mp.Ez, 0)
    # Use the exact Meep tutorial DFT convention; do not add a separate 1/2.
    density = 2 * np.pi * frequency * np.imag(np.conj(electric) * displacement)
    volume_power = float(np.sum(density) / args.resolution ** 2)
    surface_power = mp.get_fluxes(small_box)[0]
    large_surface_power = mp.get_fluxes(big_box)[0]
    scattered_power = -mp.get_fluxes(scattered_box)[0]
    epsilon = SiO2.epsilon(frequency)[0][0]
    summary = dict(
        res=args.resolution, t_end=sim.meep_time(), timesteps=sim.timestep(),
        P_dft=volume_power, P_box=surface_power,
        err=abs(volume_power - surface_power) / surface_power, P_box_big=large_surface_power,
        P_scat=scattered_power, I0=intensity,
        Q_abs=surface_power / (intensity * 2 * radius),
        Q_scat=scattered_power / (intensity * 2 * radius),
        eps_SiO2=[float(epsilon.real), float(epsilon.imag)], wall=time.time() - start)
    # Field gathers are collective: every MPI rank must reach them.
    electric_map = sim.get_dft_array(field_map, mp.Ez, 0)
    epsilon_map = sim.get_array(component=mp.Dielectric, center=mp.Vector3(),
                                size=mp.Vector3(length - 2 * dpml, length - 2 * dpml))
    if mp.am_master():
        args.out.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.out / f"{args.tag}.npz", apd=density, Ezmap=electric_map,
                            eps=epsilon_map, trace_t=np.array(trace["t"]), trace_v=np.array(trace["v"]))
        (args.out / f"{args.tag}.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print("RESULT " + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
