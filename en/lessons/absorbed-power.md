---
layout: lesson
permalink: /en/absorbed-power/
lesson_title: "How do we check the power absorbed by a material?"
lesson_summary: "Map absorption in a lossy SiO₂ cylinder and measure its power independently with a DFT volume integral and a closed flux box. Check how the methods approach each other with resolution, and where changing the box still exposes a discrepancy."
lesson_goals:
  - "Distinguish electric-field intensity from absorbed-power density."
  - "Compare an integral of complex E and D with the inward flux through a closed surface."
  - "Distinguish grid error, monitor dependence, absorption cross section and efficiency."
lesson_prerequisites: "Chapter 03: reference subtraction and scattering · Chapter 20: complex permittivity and material dispersion"
date: 2026-11-11
title: "Meep Example 25 · Where power is absorbed — a DFT density integral and a closed flux box"
title_en: "Meep Example 25 · Where power is absorbed — a DFT density integral and a closed flux box"
lang: en
translation_key: absorbed-power
series: meep-examples
part: 25
level: intermediate
runtime: "Archived 4-process MPI runs: about 7 s / 54 s / 9 min at res 50/100/200; single-core runtime not measured"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#absorbed-power-density-map-of-a-lossy-cylinder"
tags: [meep, fdtd, absorption, dft, flux, convergence, dispersive-material]
image: /assets/meep/25/forward_dft.png
excerpt: "Measure absorption in a weakly lossy SiO₂ cylinder by two methods. Their difference decreases from 3.66% to 0.249% at res 50→200, while a separate box-size test reveals a remaining limitation."
---
<h2 id="observe">1. Observe: does a bright field mean strong absorption?</h2>

Chapter 20 introduced complex material permittivity. Now we ask **where, and how much, power is absorbed**. A plane-wave pulse illuminates a 2D SiO₂ cylinder from the left; DFT fields are recorded at vacuum wavelength 1 µm.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/25/forward_dft.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/25/forward_dft.png' | relative_url }}" alt="Actual Meep DFT electric-field intensity around the cylinder, absorbed-power density inside it, and volume/surface power integrals versus resolution" loading="eager"></a>
<figcaption>Archived numerical results: |Ez|² on the left, 2πf Im(Ez* Dz) in the middle, integrated powers on the right. Illumination comes from the left; absorption density peaks downstream near x = 0.98 µm. Dark colors mean larger values in the middle panel: read its color bar. Field intensity and absorption density are different quantities. Original plot annotations are Korean; the tables below give the values in English.</figcaption>
</figure>

<details markdown="1">
<summary>What was verified?</summary>

The model is an infinite cylinder of radius 1 µm, 2D Ez, Meep materials `SiO2`, at one wavelength λ = 1 µm. Its small loss is ε = 2.132084 + 0.000985244i. At res 100, the volume integral is 0.131204225 and the small flux box gives 0.132491690, a 0.9717% difference. At res 50→100→200 the difference decreases from 3.6556%→0.9717%→0.2494%. However, the large and small boxes differ by 3.3803% at res 100, failing the registered 2% criterion. This lesson reuses saved results; no new fields were solved for publication.

</details>

<h2 id="predict">2. Predict: internal loss versus net inward power</h2>

<fieldset class="prediction">
<legend>A closed box encloses a lossy cylinder but no source. What should an accurate calculation give?</legend>
<label><input type="radio" name="absorbed-power-prediction" value="balance"> The integral of internal absorption density equals the net power entering the box.</label>
<label><input type="radio" name="absorbed-power-prediction" value="scattered"> The outward scattered power always equals the absorbed power.</label>
<label><input type="radio" name="absorbed-power-prediction" value="field"> Summing |Ez|² gives absorption regardless of material loss.</label>
</fieldset>

<details markdown="1">
<summary>Prediction and acceptance criteria</summary>

Poynting's theorem relates loss inside a box to net flux through its boundary. This dataset registered three tests: < 1.5% volume/surface difference at res 100, < 2% large/small box difference, and a res-200/res-50 method-error ratio < 0.5. The first and third passed; the box-size test failed. Higher resolution should not be assumed to resolve every check automatically.

</details>

<h2 id="understand">3. Understand: count the same absorption along two paths</h2>

{% include chapter-illustration.html %}

In the official Meep example's DFT normalization, absorbed-power density and its integral are

$$
p_{\rm abs}=2\pi f\,\operatorname{Im}(\mathbf E^*\!\cdot\mathbf D),\qquad
P_{\rm vol}\approx\sum_{i,j}p_{\mathrm{abs},ij}\,\Delta x\Delta y.
$$

Do not import an extra factor of 1/2 from a different amplitude convention. Only Ez and Dz are needed for this 2D Ez model. `yee_grid=True` retains the official example's DFT sampling, with area weight 1/resolution². Even a large |E|² gives no absorption in lossless vacuum. This calculation measures electromagnetic energy loss; it does not solve temperature rise or heat diffusion.

The independent route uses the total field's **net inward flux**:

$$
P_{\rm box}=-\oint_{\partial V}\mathbf S\cdot\hat{\mathbf n}\,d\ell.
$$

The face weights are +1 on the left, −1 on the right, −1 on top and +1 below. Absorption uses total fields. A separate scattering box subtracts empty-cell DFT fields, as in chapter 03, and measures outward scattered power. Mixing total and scattered fields changes the measured quantity.

| Item | Fixed setting | Reason |
|---|---|---|
| Geometry | SiO₂, r = 1 µm, infinite along z | Official 2D cylinder |
| Cell/boundary | 8 × 8 µm, 1 µm PML, 2 µm air padding | Separate the object from the boundary |
| Source | x = −3 µm, y extent 8 µm, Ez Gaussian pulse | `is_integrated=True` handles the source spanning PML |
| Frequency | f = 1 µm⁻¹, fwidth = 0.1 f | Compare absorption at one frequency |
| Measurement | DFT/small box [−1,1]²; large box [−2,2]² | Volume/surface and monitor-location checks |
| Stopping | 100 after the source; final t = 200 | Same finite record as the archive |

<h2 id="run">4. Run: empty cell first, lossy cylinder second</h2>

[Download Python code]({{ '/code/absorbed_power.py' | relative_url }}) · [Sources and SHA-256]({{ '/assets/meep/25/provenance.json' | relative_url }}) · [Actual res-100 log]({{ '/assets/meep/25/abs_r100.log' | relative_url }})

Use an environment with Meep and NumPy. No external helper module is required, and `--help` does not import Meep.

```bash
python code/absorbed_power.py --help
python code/absorbed_power.py --resolution 100 --tag abs_r100 --out work/abs-r100
python code/absorbed_power.py --resolution 200 --tag abs_r200 --out work/abs-r200
```

1. **Parameters**: keep r, λ and PML fixed; vary only resolution.
2. **Geometry**: create an empty cell, then add a `SiO2` cylinder in the second run.
3. **Source**: use identical source position, extent and pulse in both runs.
4. **Boundary**: use PML on all sides and y mirror symmetry.
5. **Monitors**: save incident intensity and reference fields. In the cylinder run, collect E/D and three flux boxes: small total, large total and large scattered.
6. **Execution**: run each simulation until 100 after the pulse. All MPI ranks must reach collective field gathers.
7. **Postprocessing**: write density integral, net flux and normalized scattering cross section to JSON; save maps and source trace in NPZ.

```python
density = 2 * np.pi * frequency * np.imag(np.conj(electric) * displacement)
volume_power = float(np.sum(density) / resolution ** 2)
surface_power = mp.get_fluxes(small_box)[0]
error = abs(volume_power - surface_power) / surface_power
```

<h2 id="interpret">5. Interpret: methods approach, but box dependence remains</h2>

| Resolution (px/µm) | DFT volume integral | Small-box net power | Large-box net power | Volume/small-box difference |
|---|---|---|---|---|
| 50 | 0.131200795 | 0.136178929 | 0.154296396 | 3.6556% |
| 100 | 0.131204225 | 0.132491690 | 0.136970288 | 0.9717% |
| 200 | 0.131072200 | 0.131399930 | 0.132511796 | 0.2494% |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/25/resolution_ladder.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/25/resolution_ladder.png' | relative_url }}" alt="Actual volume-versus-small-box relative error decreases at resolutions 50, 100 and 200" loading="lazy"></a>
<figcaption>Doubling resolution reduces the difference by approximately a factor of four. This is an observed three-point trend, rather than proof of a convergence order for every material and wavelength.</figcaption>
</figure>

At res 100, the volume and flux powers match the 2020 official notebook to relative differences 5.12 × 10⁻⁸ and 2.76 × 10⁻⁵. The source record labels its overall verdict `supported`, but **one large-box test failed**. The box discrepancy is 3.3803% at res 100 and still about 0.846% at res 200. No experiment isolated residual energy, finite DFT record length or monitor sampling as the cause; that cause remains unresolved.

The diameter-normalized absorption cross section $Q_{\rm abs}=P_{\rm box}/(I_0\,2r)$ is 0.010595 at res 100; the analogous scattering quantity $Q_{\rm sca}$ is 2.001215. **These are neither cavity quality factors nor fractions of all incident power.** They normalize a 2D cross section by the diameter, so Q_sca may exceed 1. The reported power values use this source/DFT normalization and should not be read directly as watts.

<h2 id="check">6. Check: what if a source or PML lies inside the box?</h2>

<details markdown="1">
<summary>Question 1 · Should absorption-box fields also subtract the empty cell?</summary>

Absorption uses the closed net flux of the total field. Subtracting to obtain only scattered fields integrates a different quantity. The code keeps total absorption boxes separate from the reference-subtracted scattering box. Enclosing a source or PML would mix source work or computational-boundary loss with material absorption.

</details>

<details markdown="1">
<summary>Question 2 · Does 0.25% agreement at res 200 finish verification?</summary>

Check monitor size, time after the source and the material's valid frequency range independently. This archive covers one wavelength and one material; the large-box discrepancy is unresolved. An early res-20 attempt recorded NaN with the dispersive material and is excluded from the verified table.

</details>

### Change one thing

Keep res 100 and set `--after-sources 200`; record the large/small box discrepancy. Do not change time and resolution together if you want to distinguish their effects. Label the new result separately from the archived table. In [26 · A defect waveguide cavity]({{ '/en/photonic-crystal-cavity/' | relative_url }}), loss in a nonabsorbing structure is separated into radiation and leakage through the ports.

<h2 id="reference">7. References and reproduction record</h2>

- Official explanation: [Meep Basics · Absorbed Power Density Map of a Lossy Cylinder](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#absorbed-power-density-map-of-a-lossy-cylinder).
- Pinned source: [absorbed_power_density.py, commit f7811d4](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/absorbed_power_density.py). Physical settings and the DFT convention follow this example.
- Added work: a resolution ladder, larger-box check, empty-cell incident normalization/scattering measurement, bilingual lessons and standalone CLI. Optional animation-helper dependencies were removed from the CLI. Read the conceptual header animation separately from the DFT results.
- Data: [res 50]({{ '/assets/meep/25/abs_r50.json' | relative_url }}), [res 100]({{ '/assets/meep/25/abs_r100.json' | relative_url }}), [res 200]({{ '/assets/meep/25/abs_r200.json' | relative_url }}), [res-100 DFT data]({{ '/assets/meep/25/abs_r100.npz' | relative_url }}), [verdict retaining the failed check]({{ '/assets/meep/25/aggregate_verdict.json' | relative_url }}), [sources and hashes]({{ '/assets/meep/25/provenance.json' | relative_url }}).
- Path: [03 · Reference subtraction]({{ '/en/reference-subtraction/' | relative_url }}) → [20 · Material dispersion]({{ '/en/material-dispersion/' | relative_url }}) → this lesson. Upstream Meep licensing continues to apply to adapted code.

<details markdown="1">
<summary>Expand the complete executable code</summary>

{% highlight python %}
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
{% endhighlight %}

</details>
