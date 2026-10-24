---
layout: topic
permalink: /en/optical-beams/
title: "Beam Lab — curvature, signed vortex and finite-energy Airy"
title_en: "Beam Lab — curvature, signed vortex and finite-energy Airy"
lang: en
translation_key: optical-beams
series: meep-examples
topic_label: BEAM LAB
lesson_title: "What changes when you control the boundary and source phase?"
lesson_summary: "Change interface curvature, vortex charge sign and Airy apodization one at a time in a newly written Meep experiment. Distinguish the imposed source from the computed field."
lesson_goals:
  - "Compare field distributions while changing only the interface curvature."
  - "Distinguish source charges ±2 from measured complex-field winding."
  - "Observe how Airy apodization changes the beam and explain the calculation limits."
lesson_prerequisites: "Chapter 01: sources · Chapter 02: PML · Chapter 03: reference calculations"
calc_note: "New Meep control code · one CPU core · 3 Gaussian, 2 three-dimensional vortex and 2 Airy cases. Complex DFT fields are saved directly."
toc:
  - { id: observe, label: "Start with three questions" }
  - { id: curved, label: "Change boundary curvature" }
  - { id: vortex, label: "Reverse the charge sign" }
  - { id: vortex-animation, label: "Moving 3D wavefronts" }
  - { id: vortex-material, label: "The earlier medium block" }
  - { id: airy, label: "Change Airy apodization" }
  - { id: run, label: "Model and reproduction" }
  - { id: verify, label: "Checks and interpretation" }
  - { id: reference, label: "References and archive" }
related:
  - { url: "/en/point-line-source/", label: "01 · Point and line sources" }
  - { url: "/en/reference-subtraction/", label: "03 · Reflection and transmission measurements" }
  - { url: "/en/metalens/", label: "Metalens · Focus light with phase" }
date: 2026-10-24
tags: [meep, beam-lab, gaussian-beam, vortex, airy, fdtd]
image: /assets/meep/beam-lab/overview.png
excerpt: "Seven experiments comparing curvature, vortex charge sign and Airy apodization with newly written current profiles and Meep controls."
---

<h2 id="observe">1. Start with three questions</h2>

Beam Lab is a **newly written experiment covering source profiles, Meep execution and field analysis**. Its questions guide the comparisons: What happens when only the interface curvature changes? What happens when the vortex charge changes sign? What happens when the Airy source tail is more strongly suppressed?

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/overview.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/overview.png" alt="New Beam Lab calculations comparing interface curvature, vortex charge sign and Airy apodization" loading="eager"></a>
  <figcaption>Seven cases calculated with the new implementation. Gaussian and Airy panels show the sum of squared complex DFT electric-field magnitudes; vortex sections show the phase of complex E<sub>z</sub>. Colors representing different quantities should not be compared directly.</figcaption>
</figure>

[Optical-beams-MEEP](https://danielkotik.github.io/Optical-beams-MEEP/) inspired the beam topics and visual presentation. This implementation constructs finite current apertures from standard analytical expressions and uses different geometry, parameters and measurements. Earlier upstream-code executions and the Blender 3D vortex remain in the [reproduction archive]({{ '/en/optical-beams/archive/' | relative_url }}).

<h2 id="curved">2. Same source, different curvature</h2>

The Gaussian source has a central incidence angle of 20°, with refractive index changing from 1 to 1.5. The interface is **x = κy²**. κ=0 is flat, +0.10/a opens toward +x, and −0.10/a opens toward −x. The source and color scale stay the same across the three cases.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/gaussian_curvature.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/gaussian_curvature.png" alt="Measured DFT fields for a 20-degree Gaussian source at flat, positive-curvature and negative-curvature parabolic interfaces" loading="lazy"></a>
  <figcaption>Brightness is Σ|DFT E<sub>j</sub>|² divided by the common maximum of the three cases. Follow the interface outline and the bright region beyond it. Equal peak current does not make this a transmission measurement normalized by incident power.</figcaption>
</figure>

Compare the width and direction of the bright region beyond the boundary. With curvature, the surface normal changes with position. The source's central 20° angle is relative to the normal at the origin, not every point on the interface. Plane-wave Snell refraction provides a reference for the central direction at a flat interface, but does not determine the complete interference pattern of a finite beam.

<h2 id="vortex">3. Charges +2 and −2</h2>

The source uses the p=0 LG aperture shape. Its radial amplitude is the same in both cases; only the **sign of m** in exp(imθ) changes. One circuit around the source produces a phase change of +4π or −4π.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/vortex_charge.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/vortex_charge.png" alt="Actual Meep DFT Ez phase sections and winding-measurement loops for source charges +2 and -2" loading="lazy"></a>
  <figcaption>Colors show the computed complex E<sub>z</sub> phase, not a drawing of the imposed source. Winding is measured around the circle. Pixels below 5% of the section's maximum field magnitude are masked. Compare the measured value in each title with the source charge.</figcaption>
</figure>

Phase is poorly defined where the field vanishes near the center. Inspect its change around a closed path with sufficient amplitude rather than interpreting a central pixel. This source is a **finite E<sub>z</sub> current sheet with an LG-shaped aperture**, not an injection of an exact nonparaxial vector LG solution.

<h2 id="vortex-animation">4. A 3D cycle of the signed field</h2>

Reconstruct Re(Ẽ<sub>z</sub> exp(−iφ)) from the complex DFT field. Positive isosurfaces are teal and negative ones coral. Compare how the two charge cases evolve side by side.

<figure class="lesson-figure lesson-animation">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/vortex_phase.gif" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/vortex_poster.png" data-animation-src="{{ site.baseurl }}/assets/meep/beam-lab/vortex_phase.gif" data-static-src="{{ site.baseurl }}/assets/meep/beam-lab/vortex_poster.png" alt="Positive and negative 3D isosurfaces reconstructed from actual DFT fields for charges +2 and -2" loading="lazy"></a>
  <figcaption>Signed E<sub>z</sub> isosurfaces extracted on the native grid. Their levels remain fixed at ±25% of the maximum |Ẽ<sub>z</sub>| across both cases. The 24 frames span a full 2π phase cycle, playing at 80ms per frame in a 1.92-second loop.</figcaption>
  <button type="button" class="animation-toggle" hidden>Play animation</button>
</figure>

At f=1 c/a, one phase cycle corresponds to 1 a/c. This is a single-frequency complex-field phase reconstruction, not a series of transient time samples showing the source turning on or the beam arriving.

[Six phases side by side]({{ '/assets/meep/beam-lab/contact_sheet.png' | relative_url }}) · [Calculation and rendering checks]({{ '/assets/meep/beam-lab/checks.json' | relative_url }})

<h2 id="vortex-material">5. Where did the medium block go?</h2>

This charge comparison changes only the source phase **in vacuum**, so there is no medium block. The earlier white vortex at a dielectric boundary, two measured sections and translucent block belong to a different experiment. They remain in the [earlier 3D animation]({{ '/en/optical-beams/archive/#vortex-animation' | relative_url }}) and [translucent/glossy material comparison]({{ '/en/optical-beams/archive/#vortex-material' | relative_url }}). Adding surface gloss to a rendering and adding a physical mirror boundary to FDTD are different changes.

<h2 id="airy">6. What if the Airy source tail is suppressed?</h2>

The aperture is Ai(y/s) exp(αy/s), truncated at a finite width. Compare α=0.08 and 0.20. Increasing α suppresses the oscillating tail toward negative y more strongly. Both cases are in vacuum, so no refracting interface contributes to the changing bright pattern.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/airy_apodization.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/airy_apodization.png" alt="Actual DFT fields in vacuum for Airy current apertures with apodization 0.08 and 0.20" loading="lazy"></a>
  <figcaption>Σ|DFT E<sub>j</sub>|² on a common scale. Inspect the main lobe's trajectory, neighboring fringes and spreading. The finite aperture and exponential apodization distinguish this source from an infinite ideal Airy beam.</figcaption>
</figure>

<h2 id="run">7. Model and reproduction</h2>

Lengths use the arbitrary unit a, with vacuum wavelength a. No physical micrometre dimensions are assigned. The finite E<sub>z</sub> current sheet radiates in both directions; the saved monitoring region covers its forward side.

| Study | Changed parameter | Fixed conditions |
|---|---|---|
| Gaussian | κ = 0, +0.10/a, −0.10/a | Central angle 20°, n=1→1.5, waist 0.9a |
| Vortex | m = +2, −2 | Vacuum, p=0 aperture shape, waist 1a |
| Airy | α = 0.08, 0.20 | Vacuum, same finite aperture and length scale |

Resolution is 20/a in 2D and 12/a in 3D; PML thickness is 0.8a. The simulation runs for 24 a/c before accumulating complex DFT fields for another 8 a/c. Actual monitor start and end times are saved in each execution record. A finite settling interval does not establish steady-state convergence.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VTK_SMP_MAX_THREADS=1
python -m unittest discover -s code/beam_lab -p 'test_*.py'
python code/beam_lab/run.py --suite --output output/beam-lab
python code/beam_lab/render.py --data output/beam-lab --output assets/meep/beam-lab
```

See the [run instructions](https://github.com/jin-castle/meep-examples/tree/main/code/beam_lab) for the environment and single-case commands. `profiles.py` defines the source expressions, `run.py` controls Meep and saves fields, and `render.py` analyzes the measurements and produces the figures.

<h2 id="verify">8. Checks and interpretation</h2>

[checks.json]({{ '/assets/meep/beam-lab/checks.json' | relative_url }}) records case settings, actual monitoring times, code/data hashes, measured winding and animation checks. Winding is recomputed from saved DFT fields rather than copied from the source setting. The 3D isosurfaces use spatial stride 1 without mesh decimation.

These calculations visualize fields on finite grids. They do not establish resolution, PML or steady-state convergence, normalize incident power, or measure transmission efficiency. Equal peak current does not establish equal injected power. Do not interpret brightness comparisons as efficiency measurements.

<h2 id="reference">9. References and earlier reproductions</h2>

- [Meep Python API](https://meep.readthedocs.io/en/latest/Python_User_Interface/): simulator and complex DFT monitoring.
- [SciPy Airy function](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.airy.html): evaluation of Ai.
- [Optical-beams-MEEP · Daniel Kotik and Jörg Götte](https://danielkotik.github.io/Optical-beams-MEEP/): reference for beam topics and visual exploration.
- [Earlier upstream-code reproduction archive]({{ '/en/optical-beams/archive/' | relative_url }}): historical measurements, Blender renderings, original-image comparison and their MIT notices.

The new Beam Lab does not import `optbeam` or execute the preserved upstream code. Historical data retain their actual provenance in the archive, separate from the new experiments here. AI tools assisted implementation, translation and editing; file-specific reuse conditions are described in [Rights & Licenses]({{ '/en/rights-and-licenses/#source-optical-beams' | relative_url }}).
