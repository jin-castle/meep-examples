---
layout: lesson
permalink: /en/gaussian-beam/
lesson_title: "Can one angle describe a beam with a finite width?"
lesson_summary: "Replace the plane waves of chapters 17–18 with a finite Gaussian beam. Inspect saved refraction and critical-angle results, then learn why a beam's angular spectrum changes the interpretation of total internal reflection."
lesson_goals:
  - "Explain why a finite beam contains plane waves travelling in several directions."
  - "Compare the Snell angle with a direction measured from local complex-field phase."
  - "Distinguish squared electric-field brightness from normalized reflected and transmitted power."
lesson_prerequisites: "01 point and line sources · 17 plane waves and wavevectors · 18 angular reflection"
date: 2026-11-11
title: "Meep Example 19 · Light with a finite width — Gaussian refraction and the critical angle"
title_en: "Meep Example 19 · Light with a finite width — Gaussian refraction and the critical angle"
lang: en
translation_key: gaussian-beam
series: meep-examples
part: 19
level: intermediate
runtime: "Archived single-core runs: about 21–23 s per case (hardware dependent)"
meep_version: "1.33.0"
official_example: "https://danielkotik.github.io/Optical-beams-MEEP/"
tags: [meep, gaussian, beam, angular-spectrum, refraction, critical-angle, finite-aperture]
image: /assets/meep/19/gaussian-cycle-mean.png
excerpt: "Compare Gaussian incidence at 30° and 45°, check a local phase direction against Snell's law, and examine the angular-spectrum limits of a total-internal-reflection interpretation."
---
<h2 id="observe">1. Observe: a beam at 30° and 45°</h2>

Chapter 17's plane wave extended through the cell boundary with one propagation direction. What changes for a finite-width beam, like a laser beam? Below, an s-polarized Gaussian beam travels from **index 1.54 into index 1.00**. Refraction is visible on the left; the reflected beam is prominent on the right.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/19/gaussian-cycle-mean.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/19/gaussian-cycle-mean.png' | relative_url }}" alt="Cycle-mean Ez squared for Gaussian incidence at 30 and 45 degrees from index 1.54 into index 1, using one linear colour scale" loading="eager"></a>
<figcaption>Replotted actual Meep runs from 2026-10-23. Brightness is |Ez phasor|²/2 from a cos/sin/DC fit over the final two optical periods. Both panels use the same linear scale. The thin line marks the actual permittivity interface. Brightness is neither Poynting flux nor transmission efficiency.</figcaption>
</figure>

The plane-wave critical angle is **40.4927°**. The central angle of 30° lies below it, and 45° lies above. A finite beam nevertheless contains more than one angle, so the right panel does not establish exactly zero transmitted power.

This chapter reorganizes two flat-interface cases from the explicitly attributed **original-code Optical-beams-MEEP reproduction**, by Daniel Kotik and Jörg Götte. Its model and data differ from the separate curvature, LG and Airy experiments in [Beam Lab]({{ '/en/optical-beams/' | relative_url }}). We retain the sources of the earlier [reproduction archive]({{ '/en/optical-beams/archive/' | relative_url }}) and do not relabel these data as a new simulation.

<h2 id="predict">2. Predict: does the entire beam totally reflect?</h2>

<fieldset class="prediction">
<legend>What can safely be concluded when a Gaussian beam's central angle exceeds the critical angle?</legend>
<label><input type="radio" name="gaussian-beam-prediction" value="spectrum"> The central plane wave meets the TIR condition, but the whole angular spectrum also matters.</label>
<label><input type="radio" name="gaussian-beam-prediction" value="zero"> Transmitted power must be exactly zero, regardless of beam width.</label>
</fieldset>

<details markdown="1">
<summary>Reasoning behind the prediction</summary>

The first answer is correct. Narrower beams contain a broader transverse-wavevector spectrum. Some components can lie below the critical angle even when the central component lies above it. A near-interface field may also be evanescent, so brightness alone does not establish far-field transmitted power. The saved experiment has no incident-field separation or normalized flux measurement.

</details>

| Question | What this dataset establishes |
|---|---|
| Where does the 30° beam refract? | A local phasor-phase direction compared with the central plane-wave Snell prediction |
| Is 45° above critical? | The condition for the specified central angle and indices |
| What is transmission efficiency? | Not established; requires incident-field separation and flux normalization |

<h2 id="understand">3. Understand: width and angular spectrum go together</h2>

{% include chapter-illustration.html %}

A Gaussian waist-plane amplitude E(y) ∝ exp[−(y/w₀)²] has a Gaussian transverse-wavevector spectrum:

$$
\widetilde E(\kappa_y)\propto
\exp[-(\kappa_y w_0/2)^2],\qquad
\kappa_x=\sqrt{(n_1\kappa_0)^2-\kappa_y^2},\qquad
\kappa_0=2\pi/\lambda_0.
$$

Here κ uses **radians per length**, differing by 2π from chapter 17's Meep `k_point` in cycles per length. Decreasing w₀ broadens the spectrum and mixes more propagation directions. A single plane-wave angle and a beam's central angle are different quantities.

The executed upstream source integrates the propagating spectrum −n₁κ₀ ≤ κy ≤ n₁κ₀ to construct a **complex current profile on a finite source line** away from the waist. It is not simply a real Gaussian imposed at the source plane. The beam's central direction remains +x; rotating the interface produces the 30° and 45° incidence conditions.

The central plane-wave Snell prediction and critical angle are

$$
n_1\sin\theta_i=n_2\sin\theta_t,\qquad
\theta_c=\sin^{-1}(n_2/n_1),\qquad n_1=1.54,\ n_2=1.00.
$$

At 30°, θt = 50.3539°. At 45°, there is no corresponding real transmitted angle. These statements concern the **central component**, without imposing its angle on every beam component. Unlike chapter 18's P-polarized air-to-high-index interface, this experiment uses **s polarization from higher to lower index**.

<h2 id="run">4. Run: use a finite source and open boundaries</h2>

The [entry script]({{ '/code/gaussian_beam.py' | relative_url }}) calls the repository's `code/optical_beams/run_original.py` and vendored MIT `source/`. Use the **complete repository checkout**, rather than downloading the entry file alone. An existing Meep 1.33.0 environment with NumPy, SciPy and h5py is required. The retained pure-Python `optbeam` source needs no additional package installation.

```bash
# Run from the repository root. The wrapper limits CPU libraries to one thread.
python code/gaussian_beam.py --help
python code/gaussian_beam.py --angle 30 --out results/gaussian19
python code/gaussian_beam.py --angle 45 --out results/gaussian19
```

Each command runs a real Meep simulation and writes `fields.npz`, `run.json` and the original HDF5 outputs below `planar30/` or `planar45/`. We reused archived results rather than rerunning these commands while writing the chapter.

| Step | Configuration |
|---|---|
| Units | Length a; f = 12 c/a; λ₀ = a/12; no physical µm mapping assigned to a |
| Source | Ez current line at x = −2.15a, y = −1…1a; continuous wave; upstream angular-spectrum profile |
| Waist parameters | w₀ = 8/(2π·12) = 0.1061a; waist position x = −60/(2π·12) = −0.7958a |
| Grid and boundaries | 5a × 5a; resolution 184.8/a; 0.25a PML on all four sides; Courant = 0.5 |
| Observation | End at t = 10a/c; cos/sin/DC fit to 62 samples over the final two optical periods |
| Retained data | Original 924 × 924 fields and coordinates; this chapter losslessly extracts phasor, ε, x and y |

w₀ is a waist-amplitude model parameter, not a width measured directly at the source line. This chapter does not validate a beam-width propagation curve or grid/PML convergence.

To recreate only the plots and local phase checks, run the following from the repository root in a NumPy/Matplotlib environment. It performs no electromagnetic solve.

```bash
python assets/meep/19/plot_saved_results.py
```

<h2 id="interpret">5. Interpret: phase direction and power are different</h2>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/19/gaussian-signed-phase.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/19/gaussian-signed-phase.png' | relative_url }}" alt="Real parts of the extracted complex Ez phasors, sharing one signed colour scale and showing the permittivity interface" loading="lazy"></a>
<figcaption>One phase of the saved phasor, Re(Ez), on a shared signed scale: blue positive, red negative. This is not a new time evolution or the actual final-time instantaneous field. Near-interface stripes also include incident–reflected interference.</figcaption>
</figure>

| Check | 30° case | 45° case |
|---|---:|---:|
| Central angle versus critical angle | 30° < 40.4927° | 45° > 40.4927° |
| Central plane-wave Snell angle | 50.3539° | No real transmitted angle |
| Transmitted local phase angle | 50.6618° | Not measured with this diagnostic |
| Relative L2 fit residual, final two periods | 0.0822% | 0.0207% |

The transmitted local phase angle at 30° is 50.6618° from the normal, a difference of 0.3080° from the central plane-wave prediction. The phase-gradient diagnostic uses |phasor|² weighting within a small window 0.6–1.6a along the transmitted ray, with a transverse half-width of 0.12a. It measures a **local wavefront direction**, not a beam centroid, total energy-flow direction or power efficiency.

A small harmonic-fit residual means the fit represents the final two periods well. It does not imply equally small grid error or prove steady-state convergence. The higher-index medium has ten pixels per wavelength, with no separate grid, PML or end-time ladder.

Do not read R or T from the interference pattern or mean-Ez² brightness. Equal |E|² does not mean equal power flux in different materials. For efficiencies, add reference runs, field separation and suitable flux surfaces as in chapters 03 and 18.

<h2 id="check">6. Check: what changed from a plane wave to a beam?</h2>

<details markdown="1">
<summary>Why not join the y boundaries with a Bloch phase as in chapter 17?</summary>

We want one finite beam in open space. Here a finite source and PML on all four sides provide a different model. Transverse periodicity would instead create a repeating beam array.

</details>

<details markdown="1">
<summary>Does a field beyond the interface at 45° disprove total internal reflection?</summary>

No. The central angle is above critical, but the beam has an angular spectrum. Evanescent fields can also exist beyond a totally reflecting interface. Field presence and far-field power transfer require separate measurements.

</details>

<details markdown="1">
<summary>Can shared brightness give a numerical comparison of transmission efficiencies?</summary>

A common colour scale helps compare fields but does not replace incident-power normalization or Poynting flux. Those efficiency values are absent from this dataset.

</details>

Next, explore curvature with a different source model in [Beam Lab]({{ '/en/optical-beams/' | relative_url }}). To change wavelength as well, check the material validity range in [chapter 20]({{ '/en/material-dispersion/' | relative_url }}). For quantitative focusing measurements, combine this with the surface-placement and sampling checks in [chapter 16's near2far experiment]({{ '/en/zone-plate-near2far/' | relative_url }}).

<h2 id="reference">7. Code, saved data and sources</h2>

- Run: [gaussian_beam.py]({{ '/code/gaussian_beam.py' | relative_url }}), existing [run_original.py]({{ '/code/optical_beams/run_original.py' | relative_url }}), [reproduction README]({{ '/code/optical_beams/README.md' | relative_url }})
- Native extracted data: [30° phasor, ε and coordinates]({{ '/assets/meep/19/planar30-fields.npz' | relative_url }}), [45° phasor, ε and coordinates]({{ '/assets/meep/19/planar45-fields.npz' | relative_url }})
- [Archived summary]({{ '/assets/meep/19/archived-results.json' | relative_url }}), [public subset of original checks]({{ '/assets/meep/19/validation.json' | relative_url }}), [recomputed diagnostics]({{ '/assets/meep/19/verified_metrics.json' | relative_url }}), [provenance and SHA-256]({{ '/assets/meep/19/provenance.json' | relative_url }}), [plot code]({{ '/assets/meep/19/plot_saved_results.py' | relative_url }})
- Daniel Kotik and Jörg Götte, [Optical-beams-MEEP documentation](https://danielkotik.github.io/Optical-beams-MEEP/), [pinned source ca145119](https://github.com/DanielKotik/Optical-beams-MEEP/tree/ca145119e5bd0f0804d846ea42e35e4c3daa91de), [v2.1.2 DOI](https://doi.org/10.5281/zenodo.5211251)
- The upstream code is **MIT License, Copyright (c) 2018 Daniel Kotik**. The [full notice]({{ '/assets/meep/19/Optical-beams-MIT-LICENSE.txt' | relative_url }}) is retained. Attribution for this original Gaussian implementation remains separate from Beam Lab's implementation.
