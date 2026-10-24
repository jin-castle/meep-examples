---
layout: topic
permalink: /en/optical-beams/
title: "Optical-beams-MEEP lab — curved interfaces, 3D vortex and Airy beams"
title_en: "Optical-beams-MEEP lab — curved interfaces, 3D vortex and Airy beams"
lang: en
translation_key: optical-beams
series: meep-examples
topic_label: OPTICAL BEAMS
lesson_title: "Why do beam wavefronts curve and twist?"
lesson_summary: "Compare Gaussian beams at planar, concave, and convex interfaces, then calculate a 3D vortex and an Airy beam. Follow bright fringes on a black background to read wavefronts and interference."
lesson_goals:
  - "Compare the same Gaussian beam at planar, concave, and convex interfaces."
  - "Distinguish vortex phase winding from the curving bright pattern of an Airy beam."
  - "Distinguish instantaneous squared electric fields, time-averaged squared fields, and power transmission."
lesson_prerequisites: "Chapter 01: sources · Chapter 02: PML · Chapter 03: reference calculations"
calc_note: "Actual Meep 1.33.0 runs · one CPU core. 4 Gaussian cases, a 3D Laguerre–Gaussian beam, and a free-space Airy beam. Original grids and end times retained."
toc:
  - { id: observe, label: "Start with the illustrated beams" }
  - { id: curved, label: "Planar, concave, and convex" }
  - { id: vortex, label: "Read the 3D vortex" }
  - { id: airy, label: "Read the Airy beam" }
  - { id: understand, label: "What the bright fringes mean" }
  - { id: predict, label: "Snell’s law and planar interfaces" }
  - { id: setup, label: "Actual simulation conditions" }
  - { id: run, label: "Run it yourself" }
  - { id: verify, label: "Validation and limitations" }
  - { id: reference, label: "Sources and license" }
related:
  - { url: "/en/point-line-source/", label: "01 · Point and line sources" }
  - { url: "/en/reference-subtraction/", label: "03 · Quantitative reflection and transmission measurements" }
  - { url: "/en/metalens/", label: "Metalens · Focus light with phase" }
date: 2026-10-24
tags: [meep, gaussian-beam, optical-beams, vortex, airy, curved-interface, fdtd]
image: /assets/meep/optical-beams/gallery/reference_gallery.png
excerpt: "Real single-core Meep runs of curved Gaussian interfaces, a 3D charge-two vortex and a free-space Airy beam, rendered as instantaneous squared real fields."
---

<h2 id="observe">1. Start with the illustrated beams</h2>

Spiral-looking bright patterns, a cross section with an empty center, and a beam that seems to bend by itself. We ran the [Optical-beams-MEEP](https://danielkotik.github.io/Optical-beams-MEEP/) code in Meep and rendered new figures. The top three images show a **3D Laguerre–Gaussian vortex**; the bottom image shows a **free-space Airy beam**.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/reference_gallery.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/reference_gallery.png" alt="Longitudinal, transverse, and 3D sections of a charge 2 vortex, and a free-space Airy beam, calculated in Meep" loading="eager"></a>
  <figcaption>Black→red→yellow→white represents the instantaneous squared real electric field. For LG, this is the sum of the squares of all three components; for Airy, it is E<sub>z</sub>². The separate 2D LG plots use 20% of the global maximum as the color limit; the two sections in the 3D view use 2%. Airy uses its own maximum. These scales do not compare the beams’ powers.</figcaption>
</figure>

**Look first:** Why does the vortex cross section have four bright lobes? Why does the Airy beam’s bright line curve instead of traveling straight? How does the same Gaussian beam change when it encounters a curved interface?

These results are not PNGs copied from the original website. We calculated the same types of beams and displayed their **instantaneous squared fields**, preserving rapid fringes like those in the reference images. The original PNGs do not document every run condition, so we do not claim pixel-by-pixel reproduction.

<h2 id="curved">2. The same beam at planar, concave, and convex interfaces</h2>

Keep the beam unchanged and vary only the interface shape. All three cases use an incidence angle of 45° relative to the interface normal at the origin, an incident-medium refractive index of 1.54, and an opposite-medium index of 1.00.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/curved/curved_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/curved/curved_comparison.png" alt="Instantaneous squared electric fields of the same Gaussian beam at planar, concave, and convex interfaces with 45-degree central incidence" loading="lazy"></a>
  <figcaption>E<sub>z</sub>(t)² at the common end time t=10 a/c. Each panel is normalized by its own maximum so that weak patterns remain visible. Expand the figure below for annotations and a shared brightness scale.</figcaption>
</figure>

| Interface | What to compare |
|---|---|
| Planar | The normal is constant. Fringes formed by overlapping incident and reflected waves provide the reference. |
| Concave | The normal varies with position. Observe the curvature of the reflected wave and the spacing and direction of the overlapping fringes. |
| Convex | The curvature has the opposite sign. Compare the spreading direction and near-interface field distribution with the concave case. |

At a curved interface, **45° is the value at the origin**. It does not mean that light arrives at the same angle everywhere. The circular interface radius is approximately 1.9894a. Different components of the beam reach different positions and normals, so the planar-interface critical angle alone cannot characterize the entire curved-interface result.

<details>
<summary>Check interface and source positions on a shared brightness scale</summary>
<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/curved/curved_common_scale.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/curved/curved_common_scale.png" alt="Planar, concave, and convex results compared with a common maximum and linear hot color scale, with interface and source positions marked" loading="lazy"></a>
  <figcaption>This linear scale uses one shared maximum. Gray marks the interface obtained from the actual permittivity; teal marks the source interval. Distinguish this scale from the brightness of the individually normalized panels.</figcaption>
</figure>
</details>

Compare actual time samples in the [planar GIF]({{ site.baseurl }}/assets/meep/optical-beams/curved/planar45_hot.gif), [concave GIF]({{ site.baseurl }}/assets/meep/optical-beams/curved/concave45_hot.gif), and [convex GIF]({{ site.baseurl }}/assets/meep/optical-beams/curved/convex45_hot.gif). They contain 62 actual FDTD frames from the last two periods, played slowly.

In the concave case, the original source center lies inside n=1.54, but its weak tails overlap the other medium. A 401-point check found that this interval accounts for **approximately 0.0273% of the source’s squared-amplitude weight**. This diagnoses the source distribution; it is not transmission. The geometry was left unchanged to compare with the original.

<h2 id="vortex">3. A 3D vortex: where do the four lobes come from?</h2>

A Laguerre–Gaussian beam has phase that winds around its axis. This source has topological charge m=2. Its azimuthal phase factor exp(imφ) changes phase by 4π over one full turn. The source amplitude is 0 on the axis.

<div class="figure-pair">
  <figure class="lesson-figure">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_longitudinal.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_longitudinal.png" alt="Instantaneous squared real electric field in a longitudinal section containing the propagation axis of a 3D Meep vortex beam" loading="lazy"></a>
    <figcaption>Longitudinal section: a plane containing the propagation axis. It shows both wavefronts and interference at the interface.</figcaption>
  </figure>
  <figure class="lesson-figure">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_transverse.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_transverse.png" alt="Four bright lobes in a transverse section of a charge 2 vortex beam" loading="lazy"></a>
    <figcaption>Transverse section: a plane perpendicular to the propagation axis. For m=2, the instantaneous squared real field can produce a bright pattern that repeats four times around the azimuth.</figcaption>
  </figure>
</div>

The four lobes are not four independent beams. They arise from taking the real part of the complex field at one instant and squaring it. Time averaging changes this rapid phase pattern. Shapes in the reflected and refracted regions can also differ from the source’s ideal ring.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d.png" alt="Spatial sections and an isosurface of the instantaneous squared real field from actual 3D Meep vortex data" loading="lazy"></a>
  <figcaption>A 2% isosurface of the instantaneous squared real field, extracted at full resolution. Also shown are two sections on the incident side at x=−2.09740a and reflected side at y=2.11039a, the tilted material block, and red lines indicating geometrical-optics directions. The white surface is not the material interface. Following the original method, the lower-half endpoint includes the first positive z sample, +0.00649a.</figcaption>
</figure>

This view uses **all 325×325×125 samples without striding**, excluding 30 edge cells from the stored 385×385×308 field. The 1,308,590 triangles obtained with VTK 9.5.2’s `vtkContourFilter` are rendered in Blender 4.5.14 without mesh decimation or shape-changing smoothing. The actual cell height of 4a is retained; coordinates are not compressed to the obsolete height of 3.5a left in the original visualization script.

The camera direction and sequential rotations follow the original, with its distance adjusted to leave a 5% margin so that the actual cell and annotations are not clipped. The 1200×1200 image uses Cycles with 64 samples and denoising. These are display settings and do not change the stored field or isosurface geometry.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d_comparison.png" alt="Comparison of the original project’s 3D image, the earlier strided visualization, and the full-resolution rerender" loading="lazy"></a>
  <figcaption>Left: an enlarged reference from the original project’s 200-pixel image. Center: the earlier incorrect display using a stride of 6 cells. Right: the full-resolution rerender. Undersampling the wavefronts made the earlier isosurface look rough and differently shaped. Not all original run and camera settings are known, so pixel-by-pixel identity is not claimed.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d_modulus.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d_modulus.png" alt="Alternative 3D isosurface using the sum of squared complex electric-field magnitudes from the same stored field" loading="lazy"></a>
  <figcaption>An alternative view of the same field using Σ|E<sub>j</sub>|². Both the isosurface and section colors use 2% of this scalar’s own global maximum as their reference. Distinguish it from the rapid phase fringes in the instantaneous squared real part.</figcaption>
</figure>

The original Mayavi script currently defaults to the sum of squared real and imaginary parts, and also provides a line that selects only the squared real part. This page’s main view uses Σ[Re E<sub>j</sub>]²; the alternative uses Σ&#124;E<sub>j</sub>&#124;². These are different physical quantities read from the same stored data, not competing versions of one correct answer.

<h2 id="airy">4. An Airy beam: why the bright pattern curves</h2>

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/airy_free_space.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/airy_free_space.png" alt="Curving bright pattern of an M 0 W 4 Airy beam calculated by actual FDTD in free space" loading="lazy"></a>
  <figcaption>M=0, W=4, n₁=n₂=1. E<sub>z</sub>(t)² at the final time t=90 a/c.</figcaption>
</figure>

An Airy beam is a wave in which multiple plane-wave components interfere so that the bright main lobe moves along a curved trajectory. A curving bright trace does not mean that light particles accelerate without an external force, or that all the energy follows only that curve.

Both refractive indices were set to 1 to observe **the beam’s own interference without a refracting interface**. This differs from the original Airy example’s default interface-scattering run with n₂=0.65. Unlike an ideal infinite Airy function, this calculation has a finite source interval and grid.

<h2 id="understand">5. What the bright fringes mean</h2>

The main figures show **the squared real electric field at that instant**. Crests and troughs pass even within one period, so the bright fringes move. Time averaging removes these rapid fringes from the reference-style images.

| Representation | What it shows |
|---|---|
| Instantaneous real field E<sub>z</sub>(t) | Signed wavefronts. A red–blue scale is appropriate. |
| Instantaneous squared real field | E<sub>z</sub>(t)² in 2D; Σ<sub>j=x,y,z</sub>[Re E<sub>j</sub>(t)]² in 3D. Preserves rapid phase fringes and interference. |
| Single-frequency time average ⟨E<sub>z</sub>²⟩ | ∣Ẽ∣²/2 when Ẽ denotes the real-field amplitude. The distribution averages over rapid temporal oscillations. |
| Normalized Poynting flux | Reflected and transmitted powers measured using a separate reference calculation and monitors. |

The 3D example computes complex fields. **Σ<sub>j</sub>[Re E<sub>j</sub>]²** and **Σ<sub>j</sub>∣E<sub>j</sub>∣²** give different images. Here, the first retains the bright phase pattern. It does not include the magnetic field or material-dependent coefficients, so it is not the full energy density or device efficiency.

<h2 id="predict">6. Snell’s law and planar interfaces</h2>

The 30° and 45° planar Gaussian results are also retained as a reference for understanding curved interfaces and special beams. Incidence angles are measured from the interface normal.

$$n_1\sin\chi_i=n_2\sin\chi_t,\qquad\chi_c=\arcsin(1/1.54)\approx40.49^\circ.$$

| Central incidence angle | Plane-wave prediction |
|---|---|
| 30° | Refraction angle approximately 50.35°. Reflection and refraction occur together. |
| 45° | Above the critical angle. A single plane wave undergoes total internal reflection, with an evanescent field in the lower-index medium. |

<details>
<summary>Expand signed wavefronts and time-averaged plots at 30° and 45°</summary>
<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/wavefront_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/wavefront_comparison.png" alt="Signed instantaneous electric fields for planar Gaussian incidence at 30 and 45 degrees" loading="lazy"></a>
  <figcaption>Red and blue show the sign of E<sub>z</sub>. Both actual runs are compared on the same scale.</figcaption>
</figure>
<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/intensity_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/intensity_comparison.png" alt="Mean squared electric fields estimated over the last two periods of the two planar Gaussian runs" loading="lazy"></a>
  <figcaption>(A²+B²)/2 from a cos/sin/DC fit over the last two periods. Unlike the instantaneous squared field, this distribution averages over rapid temporal oscillations.</figcaption>
</figure>
<div class="figure-pair">
  <figure class="lesson-figure lesson-animation">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/planar30.gif" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/planar30_wavefront.png" data-animation-src="{{ site.baseurl }}/assets/meep/optical-beams/planar30.gif" data-static-src="{{ site.baseurl }}/assets/meep/optical-beams/planar30_wavefront.png" alt="Actual FDTD wavefronts over the final two periods of the 30-degree Gaussian run" loading="lazy"></a>
    <figcaption>30° · Actual time samples from the final two periods.</figcaption>
    <button type="button" class="animation-toggle" hidden>Play animation</button>
  </figure>
  <figure class="lesson-figure lesson-animation">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/planar45.gif" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/planar45_wavefront.png" data-animation-src="{{ site.baseurl }}/assets/meep/optical-beams/planar45.gif" data-static-src="{{ site.baseurl }}/assets/meep/optical-beams/planar45_wavefront.png" alt="Actual FDTD wavefronts over the final two periods of the 45-degree Gaussian run" loading="lazy"></a>
    <figcaption>45° · This does not show the initial arrival transient.</figcaption>
    <button type="button" class="animation-toggle" hidden>Play animation</button>
  </figure>
</div>
</details>

An evanescent field can remain near the interface even under total internal reflection. A finite-width Gaussian beam also contains multiple incident directions, so its central angle of 45° alone does not establish that the total transmitted power is exactly 0.

<h2 id="setup">7. Actual simulation conditions</h2>

The source is pinned to commit `ca145119e5bd0f0804d846ea42e35e4c3daa91de`, corresponding to v2.1.2. We used Meep 1.33.0 on one CPU core. Here a is an arbitrary length unit, not specifically μm.

| Parameter | Gaussian | 3D Laguerre–Gaussian | Free-space Airy |
|---|---|---|---|
| Source | 2D E<sub>z</sub> | 3D E<sub>z</sub>, m=2 | 2D E<sub>z</sub>, M=0, W=4 |
| n₁ → n₂ | 1.54 → 1.00 | 1.00 → 1.54 | 1.00 → 1.00 |
| Interface | Planar 30°/45°, concave/convex 45° | Planar 45° | No refractive-index contrast |
| Cell | 5a × 5a | 5a × 5a × 4a | 10a × 10a |
| PML | 0.25a | 0.25a | 0.25a |
| f (c/a) | 12 | 5 | 12 |
| Resolution (pixels/a) | 184.8 | 77 | 180 |
| End time (a/c) | 10 | 10 | 90 |
| Vacuum optical periods | 120 | 50 | 1080 |

Gaussian uses `kw_0=8, kr_w=60`, LG uses `kw_0=8, kr_w=0`, and Airy uses `kw_0=7, kr_w=0`. The original grid-setting formulas and end times are retained. The Courant factor is 0.5 for Gaussian and 1/3 for LG. Airy follows the original medium-dependent formula, giving 0.5 in free space at n₂=1 (and 0.325 at the default n₂=0.65). For planar 45°, data from an earlier run with identical conditions were reused after checking their hash and provenance.

To accelerate 3D source initialization, we used an **equivalent 1D integral that evaluates the azimuthal integral exactly with a Bessel function**. A comparison with the original double integral at 23 points gave a maximum absolute error of 4.52×10⁻¹⁰ and a maximum relative error of 2.50×10⁻⁹ for meaningful amplitudes. Field outputs were saved using Meep array reads rather than per-grid-point Python callbacks. The original source files are also preserved.

<h2 id="run">8. Run it yourself</h2>

Use the [reproduction directory](https://github.com/jin-castle/meep-examples/tree/main/code/optical_beams) in a Meep environment. `source/` contains the original Python and Scheme examples, optbeam, and the MIT license.

```bash
cd code/optical_beams
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python run_original.py --upstream source --output planar45 --chi 45 --interface planar
python run_original.py --upstream source --output concave45 --chi 45 --interface concave
python run_original.py --upstream source --output convex45 --chi 45 --interface convex
python render_curved.py --data-dir .
mkdir -p output/gallery/lg output/gallery/airy
python run_gallery.py --upstream source --output output/gallery/lg --beam lg > output/gallery/lg/run.log 2>&1
python run_gallery.py --upstream source --output output/gallery/airy --beam airy > output/gallery/airy/run.log 2>&1
python -m pip install vtk==9.5.2
python prepare_vortex_scene.py output/gallery
blender --background --factory-startup --threads 1 --python render_vortex_blender.py -- output/gallery
python render_gallery.py output/gallery
```

Each run writes to its own output folder. Preprocessing uses scientific Python in WSL; rendering uses Blender’s own Python and NumPy with one Cycles CPU thread. Replace `blender` with your installed executable path if needed. When calling Windows Blender from WSL, pass Windows absolute paths for the script and output folder. The default 3D grid has approximately 45.65 million cells and requires more memory and time than 2D. If fields have already been saved, skip both `run_gallery.py` commands and start again from preprocessing. Display coordinates, normalization, and detailed execution instructions are in the [reproduction README](https://github.com/jin-castle/meep-examples/blob/main/code/optical_beams/README.md).

You can also run the original examples. The 3D command below uses the original double integral, so initialization can be slow. Use a different working directory for each run to avoid overwriting outputs.

```bash
export PYTHONPATH="$PWD/source"
python source/scripts/Gauss_2d/Gauss2d.py -interface concave -chi_deg 45
python source/scripts/Gauss_2d/Gauss2d.py -interface convex -chi_deg 45
python source/scripts/Laguerre_Gauss_3d/LaguerreGauss3d.py
python source/scripts/Airy_2d/Airy2d.py -n1 1 -n2 1 -M 0 -W 4
```

<h2 id="verify">9. Run evidence and limits of interpretation</h2>

- Curved-interface completion checks, finite-array checks, and agreement between the original HDF5 data and instantaneous squared fields are in [curved checks.json]({{ site.baseurl }}/assets/meep/optical-beams/curved/checks.json). Sources and reuse records are in [curved provenance.json]({{ site.baseurl }}/assets/meep/optical-beams/curved/provenance.json).
- Vortex and Airy execution checks, source-integral comparisons, and field-output checks are in [gallery checks.json]({{ site.baseurl }}/assets/meep/optical-beams/gallery/checks.json); conditions are in [gallery provenance.json]({{ site.baseurl }}/assets/meep/optical-beams/gallery/provenance.json).
- Full-grid isosurface field-value agreement, saved-data hashes, and direction-line coordinate checks are in the [3D rerender checks]({{ site.baseurl }}/assets/meep/optical-beams/gallery/native3d-checks.json). Sources for the original, earlier, and corrected comparison images are in the [comparison record]({{ site.baseurl }}/assets/meep/optical-beams/gallery/comparison-provenance.json).
- In the [planar phase diagnostics]({{ site.baseurl }}/assets/meep/optical-beams/checks.json), the local refracted wavefront direction for 30° incidence was 50.66°, approximately 0.31° from the Snell reference of 50.35°. This is not a direct measurement of the beam center or power.
- The relative L2 residuals of harmonic fits over the final two Gaussian periods are 0.0822% for planar 30°, 0.0207% for planar 45°, 0.0216% for concave, and 0.1021% for convex. These check harmonic fits over a short interval; they do not establish grid convergence.
- Numerical integration of the original Airy source produced SciPy warnings about subdivision limits and slow convergence. These are retained in the run logs. Finite fields and normal completion alone do not guarantee convergence of the source integral.
- Grid and PML convergence, normalized R and T, curved-interface focal distances and beam widths, and vortex orbital angular momentum were not measured. This lab observes and compares actual fields.

<details markdown="1">
<summary>English summary</summary>

Actual single-core Meep 1.33.0 runs compare planar, concave and convex Gaussian interfaces, a charge-two fully 3D Laguerre–Gaussian beam, and an M=0, W=4 free-space Airy beam. Main figures show instantaneous squared real electric fields on black, preserving phase fringes. The original grid and runtime are retained. An analytically equivalent Bessel reduction accelerates the 3D source and is checked against the original double integral. Native array export replaces Python output callbacks. These are field visualizations, not convergence-tested power efficiencies or pixel-identical reproductions of the upstream PNGs.

</details>

<h2 id="reference">10. Sources and license</h2>

- **Original:** Daniel Kotik and Jörg Götte’s [Optical-beams-MEEP documentation](https://danielkotik.github.io/Optical-beams-MEEP/) · [pinned source version](https://github.com/DanielKotik/Optical-beams-MEEP/tree/ca145119e5bd0f0804d846ea42e35e4c3daa91de)
- **Software citation:** v2.1.2, [DOI: 10.5281/zenodo.5211251](https://doi.org/10.5281/zenodo.5211251). This DOI identifies the software version.
- **License:** MIT, Copyright (c) 2018 Daniel Kotik. [Permission notice retained with the distributed source](https://github.com/jin-castle/meep-examples/tree/main/code/optical_beams/source).
- **Additional work:** Run and validation records, the equivalent integral and observation wrappers, new result rendering, and the Korean explanation translated here.
