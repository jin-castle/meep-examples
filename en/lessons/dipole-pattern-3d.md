---
layout: lesson
permalink: /en/dipole-pattern-3d/
lesson_title: "Which directions does a point source radiate into?"
lesson_summary: "Assemble a 3D radiation pattern from directional 1D calculations, then interpret bright and dark directions created by a mirror image."
lesson_goals:
  - "Explain how a collection of Bloch 1D runs produces a 3D pattern."
  - "Distinguish flux conversion from uncomputed large-angle samples."
  - "Assess which comparisons between a 2D mirror model and a 3D pattern are valid."
lesson_prerequisites: "Chapter 01: point sources and flux boxes · Chapter 03: reference runs"
date: 2026-10-23
title: "Meep Example 10 · 3D dipole radiation patterns — Bloch 1D runs and the image dipole of a PEC mirror"
title_en: "Meep Example 10 · 3D radiation pattern of a point dipole — a family of 1D Bloch runs, and the image dipole of a PEC mirror"
lang: en
translation_key: dipole-pattern-3d
series: meep-examples
part: 10
level: intermediate
runtime: "4.3 min (single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/"
tags: [meep, fdtd, dipole, radiation-pattern, bloch, near2far, pec, image-dipole]
image: /assets/meep/10/05_pec_pattern.png
excerpt: "post 01 left the point source radiating equally in all directions, in 2D. This post asks the 3D question twice. First, the 3D pattern of an x-polarized dipole in vacuum without a 3D cell: one 1D simulation per direction, with the direction encoded in a transverse Bloch wavevector. Second, the same dipole above a perfect-electric-conductor mirror, solved in 2D with an opposite-sign image dipole and a closed near2far box, and again with the 1D method."
---

<h2 id="observe">1. Observe: does a point source radiate equally in every direction?</h2>

Move beyond chapter 01’s 2D point source to a **3D dipole with an oscillation axis**. An x-oriented dipole is dark along x and radiates uniformly in the plane perpendicular to that axis. Reconstruct this using directional 1D calculations instead of one large 3D cell.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/03_vacuum_pattern.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/03_vacuum_pattern.png' | relative_url }}" alt="Vacuum x-dipole 3D radiation pattern reconstructed from 240 Bloch 1D runs and compared with the analytical solution"></a>
<figcaption>Across the 240 computed directions, the correctly converted pattern has relative L2 error 0.22%. Gray bands mark uncomputed angles, not directions with zero radiation.</figcaption>
</figure>

<p class="lesson-note"><strong>Distinguish 3D patterns from 2D images.</strong> Parts A and C assemble directional components of a 3D Ex dipole from Bloch 1D runs. The mirror animation in part B uses a separate 2D Ez model. All pattern comparisons are maximum-normalized shapes; absolute emitted power and directivity are not validated.</p>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/06_anim_pec.gif' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/06_anim_pec.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/10/06_anim_pec.gif' | relative_url }}" data-static-src="{{ '/assets/meep/10/04_pec_field.png' | relative_url }}" alt="Pulse propagation of a 2D Ez dipole and its opposite-sign image, canceling at the mirror plane"></a>
<button type="button" class="animation-toggle" hidden>Pause animation</button>
<figcaption>Actual 2D pulse from part B. The upper source and lower image cancel at y = 0. Only the upper half represents physical space above the mirror.</figcaption>
</figure>

<h2 id="predict">2. Predict: how should an uncomputed direction be read?</h2>

<fieldset class="prediction">
<legend>If a radiation map leaves directions above roughly 72° gray, what does that mean?</legend>
<label><input type="radio" name="dipole-prediction" value="null"> No light is emitted in those directions.</label>
<label><input type="radio" name="dipole-prediction" value="missing"> Those samples were not computed, so their intensity is unknown.</label>
</fieldset>

<details markdown="1">
<summary>Compare your prediction with the calculation settings</summary>

The second answer is correct. Part A skips directions with sin θ > 0.95. Nearly grazing waves enter z PML at very oblique angles and are difficult to absorb. Filling these gaps with zero confuses missing data with physical radiation nulls.

</details>

<h2 id="understand">3. Understand: calculate one direction at a time and represent the mirror by an image</h2>

{% include chapter-illustration.html %}

Decompose a point-source field into plane waves: one transverse wavevector <code>k_point</code> corresponds to one outgoing direction. Compute along z for each direction, convert flux using **S_r = S_z cos θ**, and assemble the samples. Angle θ is measured from +z.

<figure class="lesson-figure">
<svg viewBox="0 0 320 210" role="img" aria-labelledby="dipole-bloch-title" xmlns="http://www.w3.org/2000/svg">
<title id="dipole-bloch-title">Conceptual diagram: calculate only along z and use k_point to specify oblique propagation</title>
<rect width="320" height="210" fill="#f5f8fa" />
<path d="M68 180V28M68 28l-6 12M68 28l6 12" stroke="#0d1b2a" fill="none" stroke-width="2" />
<rect x="53" y="46" width="30" height="119" fill="#e7f7fb" stroke="#0087ad" />
<circle cx="68" cy="151" r="6" fill="#0087ad" />
<path d="M74 146L208 64M208 64l-15 1M208 64l-7 14" stroke="#0087ad" fill="none" stroke-width="3" />
<path d="M68 119Q89 117 96 132" fill="none" stroke="#526579" stroke-width="2" />
<g font-family="sans-serif" font-size="16" fill="#0d1b2a">
<text x="30" y="26">+z</text><text x="93" y="119">θ</text>
<text x="109" y="42">k_point → direction</text>
<text x="109" y="171">1D cell: z only</text>
<text x="18" y="200">Sample → convert → 3D pattern</text>
</g>
</svg>
<figcaption>Conceptual diagram. The arrow represents a plane-wave direction, not a computed field. Repeating 1D runs at different directions builds the 3D pattern.</figcaption>
</figure>

The cos θ factor is not merely a projection from z flux onto propagation direction. It also accounts for conversion from transverse-wavevector samples to power per solid angle. In the original calculation, multiplication gives 0.22% error, no conversion gives 53%, and division gives 76%.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/07_anim_1d.gif' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/07_anim_1d.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/10/07_anim_1d.gif' | relative_url }}" data-static-src="{{ '/assets/meep/10/02_layout_1d.png' | relative_url }}" alt="An Ex pulse travels along z in one Bloch 1D calculation representing a 45° direction"></a>
<button type="button" class="animation-toggle" hidden>Pause animation</button>
<figcaption>One actual part-A 1D run at θ = 45°. This observes an oblique plane-wave component along z; it is not an animation of the complete 3D space.</figcaption>
</figure>

Near a mirror, reflected and source fields interfere. An electric dipole parallel to a PEC mirror can be represented by an **opposite-sign image** at equal distance below it. Their direction-dependent path difference 2h cos θ produces alternating bright and dark directions.

<figure class="lesson-figure">
<svg viewBox="0 0 320 210" role="img" aria-labelledby="dipole-image-title" xmlns="http://www.w3.org/2000/svg">
<title id="dipole-image-title">Conceptual diagram: a dipole above PEC and an opposite-sign image symmetrically below</title>
<rect width="320" height="210" fill="#f5f8fa" />
<path d="M22 107H296" stroke="#0d1b2a" stroke-width="5" />
<circle cx="86" cy="58" r="8" fill="#0087ad" /><circle cx="86" cy="156" r="8" fill="#526579" />
<path d="M86 68V97M86 117V146" stroke="#526579" stroke-dasharray="4 4" stroke-width="2" />
<g font-family="sans-serif" font-size="16" fill="#0d1b2a">
<text x="111" y="62">Real dipole (+)</text><text x="111" y="161">Image (−)</text>
<text x="40" y="85">h</text><text x="40" y="139">h</text>
<text x="175" y="98">PEC plane</text><text x="23" y="199">Tangential E cancels at the mirror</text>
</g>
</svg>
<figcaption>The diagram explains the mirror boundary condition; the lower image is not an additional physical emitter. Part B solves the 2D mirror problem using this symmetry.</figcaption>
</figure>

Part B uses 2D Ez, background n = 1.2, wavelength 650 nm, and height h = 1.25 µm. In part C, <code>k_point</code> makes the cell walls periodic, so an **explicit mp.metal block** below the source supplies the mirror. All mirrors here are lossless PEC.

<h2 id="run">4. Run: reduce only the distance to the mirror</h2>

Run the original in the repository’s <code>code/</code> folder with Meep 1.33.0 and keep its outputs separately. The recorded single-core runtime is about 4.3 minutes.

~~~bash
OMP_NUM_THREADS=1 python dipole_pattern_3d.py
~~~

**Change only height H from 1.25 to 0.3 µm**, replacing <code>H = 1.25</code> with <code>H = 0.3</code> in the full script, then rerun the same command. Parts B and C share this height, so both methods receive the same change.

Compare the number and angles of bright lobes in <code>05_pec_pattern.png</code> with the original. Smaller h reduces the range of phase differences, so fewer lobes are expected. Read new peak positions and errors from the new run; do not confuse part A’s vacuum error of 0.22% with mirror-model errors.

<h2 id="interpret">5. Interpret: even an accurate pattern has a limited scope</h2>

| Original comparison | Relative L2 error |
|---|---:|
| Vacuum 3D pattern, 240 computed directions | 0.22% |
| 2D near2far versus analytical array factor | 0.66% |
| 1D Bloch above a mirror versus 2D, below 72° | 6.4% |
| 1D Bloch above a mirror at φ = 90° versus analytical solution, through 85° | 10.5% |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/05_pec_pattern.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/05_pec_pattern.png' | relative_url }}" alt="Five radiation lobes above a mirror, comparing 2D near2far and Bloch 1D results" loading="lazy"></a>
<figcaption>The original height 1.25 µm produces five lobes, with the strongest peak at 12.9°. Gray shading marks angles above 72°. Compare appropriate cross-sections of the different models after shape normalization.</figcaption>
</figure>

Do not transfer the mirror-free 0.22% error to the entire mirror problem. The mirror methods differ by 6.4% even below 72°. The original discussion proposes half-cell uncertainty in mirror position and angular sampling as possible causes; these effects were not independently isolated here.

<p class="lesson-note"><strong>Outside the verified scope.</strong> 1D radiation intensity above 72°, absolute power, directivity, and lossy-metal mirror responses are not established. Large-angle convergence of the 2D near2far result was not independently checked either.</p>

<h2 id="check">6. Check your understanding</h2>

1. Can one 1D run give the full 3D pattern? Explain the repetition and conversion required.
2. When comparing the 2D mirror animation and 3D pattern, how should the gray gaps and 6.4% error be interpreted?

<details markdown="1">
<summary>Read both answers</summary>

1. Each run supplies one directional sample. Repeat with different <code>k_point</code> values and multiply z flux by cos θ to assemble the directional pattern.
2. Compare normalized shapes in the corresponding sections of 2D Ez and 3D Ex models. Gray marks uncomputed regions; 6.4% is the difference remaining between the two methods below 72°. It does not establish agreement of absolute emission.

</details>

<h2 id="reference">7. References and full code</h2>

Directional calculation settings, original failed runs, detailed measurements, and the complete program are retained below.


<details markdown="1">
<summary>English summary</summary>

### TL;DR (English)

<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/05_pec_pattern.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/05_pec_pattern.png' | relative_url }}" alt="Which directions does a point source radiate into? Original overview figure" loading="lazy"></a>
</figure>

- **What**: post 01 left the point source radiating equally in all directions, in 2D. This post asks the 3D question twice. First, the 3D pattern of an x-polarized dipole in vacuum without a 3D cell: one 1D simulation per direction, with the direction encoded in a transverse Bloch wavevector. Second, the same dipole above a perfect-electric-conductor mirror, solved in 2D with an opposite-sign image dipole and a closed near2far box, and again with the 1D method.
- **Result**: 240 one-dimensional runs reproduce the dipole pattern $1-\sin^2\theta\cos^2\phi$ with 0.22% relative error on the computed hemisphere; multiplying the z flux by $\cos\theta$ is the right conversion (dividing gives 76%). Above the mirror the 2D near2far pattern matches the two-element array factor $\sin^2(kh\cos\theta)$ to 0.66% with five lobes; the 1D method agrees with it to 6.4% below 72°, and breaks down at grazing angles where the PML cannot absorb a wave travelling almost parallel to it.
- **Takeaway**: a 3D pattern can be bought with many cheap 1D runs, but only away from grazing angles, and the per-direction flux needs a Jacobian. An infinite mirror is never put inside a near2far box: it is replaced by an image source and a symmetry. A mirror does not just reflect; it rewrites the pattern of the source next to it.
- **Code**: full script at the bottom, ~4.3 min on one core.

</details>

<details markdown="1">
<summary>Background, physical equations, and parameters</summary>

### Original §0 · What this lesson teaches

- Obtain a 3D point-source radiation pattern without a 3D cell: one direction = one 1D run with a different `k_point`.
- Convert z flux to power per solid angle with $\cos\theta$, and recognize an incorrect conversion.
- Understand why the official example omits glancing angles above 72°. Uncomputed zero-filled samples are not radiation nulls.
- When an infinite PEC mirror cannot fit inside a near2far box, use an opposite-sign image dipole and `Mirror(Y, phase=-1)`.
- Recognize that the `weight` of each of four `Near2FarRegion` segments sets the outward normal of the closed surface.
- Compare the array factor from 2D near2far and 1D Bloch methods, including where they diverge.

**Prerequisites**: chapter 01’s point sources and flux boxes; chapter 03’s reference runs. **Official examples**: [Near-to-far field spectra](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/), especially [antenna above a PEC ground plane](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-an-antenna-above-a-perfect-electric-conductor-ground-plane), and [dipole_in_vacuum_1D.py](https://github.com/NanoComp/meep/blob/master/python/examples/dipole_in_vacuum_1D.py). **Previous**: [09 · Waveguide bend inverse design]({{ '/en/bend-inverse/' | relative_url }}) · **Next**: [11 · A point source between two mirrors]({{ '/en/cavity-ldos/' | relative_url }})


### Original §1 · The question

Chapter 01 ended with a 2D point source sending 25% through each side. A real dipole is three-dimensional and has an axis: an x-oriented dipole emits nothing along x and uniformly in the perpendicular plane. This seems to require a 3D cell, but the official example obtains the pattern from hundreds of 1D runs. Why does that work, and where does it fail? The second question starts season 2: how does placing a mirror beside a point emitter change its pattern?

### Applications

A dipole above a mirror models an emitting molecule above the reflective electrode of an OLED or LED. Its radiation pattern is a starting point for outcoupling studies; collections of Bloch 1D runs extend to multilayer OLED extraction calculations.

| Application | What this lesson provides | Next step |
|---|---|---|
| OLED/LED emitting layer above a reflective electrode | Mirror-dipole pattern, 1D Bloch method extendable to multilayers | Chapter 14: extraction efficiency |
| Patch and monopole antennas above a ground plane | Image theory, array factor sin²(kh cosθ) | — |
| Emission directions of quantum dots and single-photon sources | 3D dipole pattern and polarization axis | Chapter 11: LDOS |
| Metasurface and grating far fields | Closed near2far-box rules | Chapter 16: far field |



### Original §2 · Physics on one page

A point-source field is a sum of plane waves. Fixing transverse wavevector $\mathbf k_\perp=(k_x,k_y)$ reduces Maxwell’s equations to a 1D problem along z, with transverse dependence $e^{i\mathbf k_\perp\cdot\mathbf r_\perp}$. This is Meep’s `k_point`. A plane wave leaving in direction $(\theta,\phi)$ has $\mathbf k_\perp=f\sin\theta\,(\cos\phi,\sin\phi)$, so varying `k_point` in a 1D dipole run samples different directions. Each run returns z-directed flux $S_z$. The wavevector-to-solid-angle Jacobian, written in the original derivation as $d^2k_\perp=f^2\cos\theta\,d\Omega$, leads to the conversion $S_r=S_z\cos\theta$ used here.

$$
\frac{dP}{d\Omega}\Big\lvert _{x\text{-dipole}}\propto 1-\sin^2\theta\cos^2\phi,\qquad
S_r(\theta,\phi)=S_z(\theta,\phi)\cos\theta,\qquad
\big\lvert 1-e^{\,i\,2kh\cos\theta}\big\lvert ^2=4\sin^2(kh\cos\theta),\quad k=\frac{2\pi n}{\lambda}
$$

As $\theta$ approaches 90°, a plane wave travels almost parallel to PML, making absorption ineffective and allowing residual waves to traverse the cell. The official example omits $&#124;\mathbf k_\perp&#124;>0.95f$, or $\theta>71.8°$.

Use image theory for a dipole above a mirror. Tangential electric field must vanish at PEC; an opposite-sign dipole at equal distance below the plane cancels it there. Replace the mirror with this second dipole. Path difference $2h\cos\theta$ multiplies the pattern by array factor $4\sin^2(kh\cos\theta)$. A 2D Ez dipole has an isotropic in-plane pattern, so this factor determines the 2D angular shape.

| Symbol | Meaning | Code variable |
|------|----|-----------|
| $\theta,\phi$ | Polar angle from +z or mirror normal; azimuth from x | `POLAR`, `AZIM`, `THETA_B` |
| $\mathbf k_\perp$ | Transverse Bloch wavevector $f\sin\theta(\cos\phi,\sin\phi)$ | `k_point` |
| $S_z$, $S_r$ | 1D z flux and converted radial flux | `flux_z`, `radial` |
| $h$ | Dipole–mirror separation | `H` |
| $kh$ | Phase scale of the path difference | `K_B * H` |
| Image | Second source with sign −1 | `amplitude=-1.0` |

**Assumptions and validity**: part A uses vacuum, one frequency, and Ex polarization. Part B uses 2D Ez (tangential to the mirror), background n = 1.2, wavelength 650 nm, and lossless PEC. Part C represents a 3D Ex dipole with an explicit `mp.metal` block at the bottom of its 1D cell. With `k_point`, cell walls themselves are Bloch-periodic. All comparisons use maximum-normalized shapes, not absolute power.

### Make predictions before seeing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| Collection of 1D runs versus analytical pattern over sampled hemisphere | Within 2% | 1.99% on a 10×12 grid in 10_sources notes |
| z flux → radial flux | Multiply by $\cos\theta$ | Jacobian $d^2k_\perp=f^2\cos\theta\,d\Omega$ |
| $\phi=90°$ section | Constant (isotropic) | Plane perpendicular to the dipole axis |
| 2D PEC near2far versus array factor | Within 1% | 0.47% at res 100 in the notes |
| $\lvert E_z\rvert$ at mirror plane $y=0$ | 0 | Enforced by odd symmetry |
| Lobes over 0–90° | Five (12.8°, 40.7°, 57.2°, 71.0°, 83.8°) | $kh=14.5$; maxima at $kh\cos\theta=(m+\tfrac12)\pi$ |
| 1D Bloch PEC ($\phi=90°$) versus 2D near2far | Within 2% below 72° | Same array factor; dipole factor is 1 in that plane |
| 1D runs above 72° | Distorted | PML poorly absorbs grazing waves |

**Acceptance criteria**: relative L2 above 5% over computed directions suggests a conversion-factor or `k_point` problem. If $\lvert E_z\rvert$ at $y=0$ exceeds a few percent of the maximum, check symmetry phase (sampling half a grid cell away need not give exact zero). If the two methods differ by over 10% below 72°, check mirror and monitor positions.


### Original §3 · Simulation setup

<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/02_layout_1d.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/02_layout_1d.png' | relative_url }}" alt="Parts A and C use a z-only 1D cell with Ex dipole, flux point, and k_point propagation direction; part C has upper PML and lower PEC" loading="lazy"></a>
<figcaption markdown="span">Parts A and C use a 1D cell along z. PML is at both ends in A; C has upper PML and lower PEC. Red line: Ex dipole; blue square: flux point; purple arrow: propagation direction set by `k_point`. Circled numbers match §4.</figcaption>
</figure>


<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/01_layout.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/01_layout.png' | relative_url }}" alt="Part B: 7 by 7 µm 2D cell at n = 1.2 with physical and image dipoles at y = ±1.25, a closed near2far box, and PML" loading="lazy"></a>
<figcaption markdown="span">Part B’s 2D cell (7 × 7 µm, n = 1.2). Red dots: physical dipole at y = +1.25 and image at y = −1.25 with amplitude −1. Blue rectangle: closed near2far box. Green hatching: PML. The effective PEC plane is y = 0; only the upper half is physical.</figcaption>
</figure>


| Parameter | Value | Why this value | Effect of a change |
|----------|-----|-------------|--------|
| A wavelength, resolution, air length | 1 µm, res 50, 10 µm | Scale-independent pattern; official example values | Resolution is independent of the conversion factor |
| A angular grid | 13 polar × 24 azimuthal | Reduced from official 30 × 50; spacings 7.5° and 15° | Runtime grows with sample count |
| A glancing limit | Skip $\sin\theta>0.95$ | Official rule for nearly PML-parallel waves | Including these runs is slow and inaccurate, as part C shows |
| A stopping rule | Ex decay to 1e-6 over a 25-unit window | Official example setting | Correctly configured runs finish within a second |
| A `k_point` | $nf(\sin\theta\cos\phi,\ \sin\theta\sin\phi,\ \cos\theta)$ | The z component keeps $\mathbf k\neq0$ | §4 ③ |
| B wavelength, n, h | 650 nm, 1.2, 1.25 µm | Official values; $kh=14.5$ | Smaller h gives fewer lobes |
| B resolution | 100 | Same as notes; 83 cells per wavelength | At 50, L2 increases |
| B near2far box | Half-width 2 µm | Encloses both dipoles at ±1.25 | Enclosing only one dipole invalidates the image construction |
| B far-field radius | 1000 λ | Far-field approximation | — |
| C cell | Metal 0.5 + h 1.25 + air 10 + PML 1 µm | `k_point` makes walls periodic, so use an explicit `mp.metal` mirror | Assuming the wall is a mirror leaves no mirror (§4 ④) |
| C stopping rule | Fixed 150 time units | A wave at 85° takes about 140 to cross 10 µm at n 1.2 | Decay criteria stall at glancing angles |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/00_source.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/00_source.png' | relative_url }}" alt="Part B source waveform and spectrum: 650 nm and fwidth 0.2 fcen; part A uses wavelength 1 µm at the same relative bandwidth" loading="lazy"></a>
<figcaption markdown="span">Part B source waveform and spectrum (650 nm, fwidth 0.2 fcen). Part A uses wavelength 1 µm with the same relative bandwidth.</figcaption>
</figure>


**Difference from the lecture notebook**: this extends beyond the lecture, taking chapter 01’s point source (week 2) into 3D patterns and mirrors. Two 10_sources PEC notes separately covered 2D near2far (L2 0.47%) and 1D Bloch (correlation 0.947); here both are plotted together to identify their differences.

</details>

<details markdown="1">
<summary>Walk through the original code</summary>

### Original §4 · Code walkthrough

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → run and stop → postprocessing.
> Parts A and C use 1D geometry; step ② in B replaces a mirror by an image and symmetry. Part C additionally requires its explicit PEC block as described in step ④.

### ① Units and parameters — which numbers stay fixed

```python
POLAR = np.radians(np.arange(0.0, 90.1, 7.5))      # 13 polar angles (0 = +z)
AZIM = np.radians(np.arange(0.0, 360.0, 15.0))     # 24 azimuth angles
GLANCING = 0.95                                     # skip k_perp > 0.95 f (official rule)
T_AFTER = 60.0                                      # run time after the source turns off

WL_B, N_B, H, RES_B = 0.65, 1.2, 1.25, 100          # PEC mirror part: wavelength, background index, height, resolution
K_B = 2 * np.pi * N_B / WL_B                        # k h = 14.5 sets the lobes
```

- **What**: set part A’s angular grid and glancing limit, and part B’s mirror parameters.
- **Why**: angular sampling determines run count. Removing three glancing rows from 13 × 24 leaves 240 runs. Since $kh$ sets lobe count and positions, specify wavelength, refractive index, and height together.
- **If wrong**: omitting the background index from `K_B` shifts array-factor lobes to incorrect angles.

### ② Materials and geometry — image and symmetry instead of a mirror

```python
sources_B = [mp.Source(mp.GaussianSource(FCEN_B, fwidth=FWIDTH_B), component=mp.Ez, center=mp.Vector3(0, H)),
             mp.Source(mp.GaussianSource(FCEN_B, fwidth=FWIDTH_B), component=mp.Ez, center=mp.Vector3(0, -H), amplitude=-1.0)]
symB = [mp.Mirror(mp.X), mp.Mirror(mp.Y, phase=-1)]        # odd in y -> Ez = 0 on y = 0 (the PEC plane)
```

- **What**: in part B, no mirror appears in the geometry. An opposite-sign second dipole and odd y mirror symmetry implement its boundary condition.
- **Why**: an infinite PEC plane cannot cross the closed near2far surface used here. Enclosing both image sources preserves the transformation assumptions. The applied symmetries reduce the calculation to one quarter and enforce $E_z=0$ at $y=0$.
- **If wrong**: omitting `phase=-1` adds equal-sign dipoles, making y = 0 an antinode and producing a $\cos^2$ pattern. Hz polarization requires the opposite image sign and parity.

### ③ Source — dipole and k_point in a 1D cell

```python
def bloch_k(theta, phi, fcen, n_index=1.0):          # full wavevector of the outgoing plane wave, |k| = n f
    return mp.Vector3(n_index * fcen * np.sin(theta) * np.cos(phi), n_index * fcen * np.sin(theta) * np.sin(phi), n_index * fcen * np.cos(theta))

sim = mp.Simulation(cell_size=mp.Vector3(0, 0, sz), resolution=RES_A, k_point=bloch_k(theta, phi, fcen, n_index),   # no dimensions=1 (see below)
                    default_material=mp.Medium(index=n_index), boundary_layers=[mp.PML(thickness=DPML_A, direction=mp.Z)],
                    sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ex, center=mp.Vector3(0, 0, z_src), size=mp.Vector3())])
```

- **What**: the cell is one line along z with a point source. `k_point` specifies the outgoing plane wave’s full wavevector: two transverse components and one z component.
- **Why**: changing `k_point` on the same 1D structure selects a different plane-wave direction without a 3D run. The z component is along PML absorption and does not change the transverse decomposition, but keeps $\mathbf k\neq0$ even at $\theta=0$, ensuring complex fields in every run.
- **If wrong**: two failures occurred here. Explicit `dimensions=1` silently ignored transverse k, making flux angle-independent (pattern L2 35%). Without z in `k_point`, the θ = 0 run alone used real fields and returned one-quarter power. Cell size `(0, 0, sz)` already gives a 1D cell; omit `dimensions` in this workflow.

### ④ Simulation and boundaries — PML direction and the mirror

```python
boundary_layers=[mp.PML(thickness=DPML_A, direction=mp.Z)]                     # part A: both ends of z
boundary_layers=[mp.PML(thickness=DPML_A, direction=mp.Z, side=mp.High)]       # part C: PML on top only ...
mirror = [mp.Block(center=mp.Vector3(0, 0, Z_BOT + 0.5 * DMETAL), size=mp.Vector3(mp.inf, mp.inf, DMETAL), material=mp.metal)]   # ... and a PEC block at the bottom
```

- **What**: A uses PML at both ends. C uses upper PML and a lower `mp.metal` perfect-conductor block; its top surface is the mirror.
- **Why**: in chapter 01 an unabsorbed cell wall could represent a mirror, but `k_point` changes walls to Bloch-periodic boundaries. The lower wall is therefore not a PEC mirror; add one as geometry.
- **If wrong**: the second run assumed the lower wall was a mirror and placed PML only above. Its pattern differed from the array factor by 43%, because the lower wall instead connected periodically to upper PML.

### ⑤ Monitors — a 1D flux point and a 2D near2far box

```python
mon = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(0, 0, z_mon)))          # a point in 1D: Poynting z-flux

n2f = sim_B.add_near2far(FCEN_B, 0, 1,
        mp.Near2FarRegion(center=mp.Vector3(0, BOX), size=mp.Vector3(2 * BOX, 0)),
        mp.Near2FarRegion(center=mp.Vector3(0, -BOX), size=mp.Vector3(2 * BOX, 0), weight=-1),
        mp.Near2FarRegion(center=mp.Vector3(BOX, 0), size=mp.Vector3(0, 2 * BOX)),
        mp.Near2FarRegion(center=mp.Vector3(-BOX, 0), size=mp.Vector3(0, 2 * BOX), weight=-1))
```

- **What**: the 1D flux monitor is a point. Four 2D segments form a closed rectangle; bottom and left segments use `weight=-1` for outward normals.
- **Why**: the near2far transform calculates distant fields from equivalent currents on a closed surface. Missing segments or incorrect normal signs invalidate this construction.
- **If wrong**: omitting `weight` makes the lower segment face inward and distorts the pattern, following the same orientation rule as chapter 01’s flux box.

### ⑥ Run — decay conditions and fixed time

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ex, mon_pt, 1e-6))   # part A (official): until Ex at the flux point has decayed
sim.run(until_after_sources=T_C)                                                    # part C: fixed 150 time units (grazing angles included)
sim_B.run(until_after_sources=mp.stop_when_dft_decayed(tol=1e-6))                   # part B: until the DFT monitors stop changing
```

- **What**: part A waits for Ex decay at the flux point as in the official example; C uses fixed time; B waits for DFT convergence.
- **Why**: C deliberately includes glancing angles, where poorly absorbed waves can stall a decay condition. The fixed interval is based on about 140 time units for an 85° wave to cross the 10 µm layer.
- **If wrong**: a short fixed interval ends large-θ runs before the pulse reaches the monitor, suppressing outer-angle radiation artificially. A decay condition at glancing angles can take tens of minutes.

### ⑦ Postprocessing — Jacobian, normalization, and analytical comparison

```python
radial = flux_z * np.cos(POLAR)[:, None]                        # S_r = S_z cos(theta)
analytic_A = 1 - np.sin(TH) ** 2 * np.cos(PH) ** 2              # x-dipole, up to a constant
err = rel_l2(norm(radial), norm(analytic_A))                    # both normalized to their maximum

ff = sim_B.get_farfield(n2f, mp.Vector3(R_FF * np.sin(th), R_FF * np.cos(th)))
S = np.real(np.cross(E, np.conj(H)));  pattern_B[i] = np.hypot(S[0], S[1])
array_factor = np.sin(K_B * H * np.cos(THETA_B)) ** 2
```

- **What**: multiply z flux by $\cos\theta$, normalize by the maximum, and compare with the analytical pattern using L2. For 2D, calculate the far-field Poynting magnitude by angle.
- **Why**: compare normalized shapes only. Absolute flux from 1D runs and absolute 2D near2far power have different units and cannot be directly plotted as the same quantity.
- **If wrong**: dividing by $\cos\theta$ increases L2 to 76% (red × in §5). Treating uncomputed glancing samples as zeros gives errors of tens of percent, measuring missing data rather than physics.

> **Pitfall**: with explicit `dimensions=1`, the first run’s θ = 0 decay condition did not stop after over a million time steps and flux was angle-independent. Removing `dimensions` and adding a z component to `k_point` let the official decay condition finish within one second per run. A stalled run can indicate a setup problem rather than a stopping-rule problem. A list of two `until_after_sources` conditions requires both to pass, so `stop_after_walltime` in that list is not an upper bound.

</details>

<details markdown="1">
<summary>Original results, verification tables, diagnostics, and further experiments</summary>

### Original §5 · Results

<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/03_vacuum_pattern.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/03_vacuum_pattern.png' | relative_url }}" alt="Part A vacuum pattern: angular cuts, L2 errors for three flux conversions, and Meep/analytical/difference maps with uncomputed glancing angles gray" loading="lazy"></a>
<figcaption markdown="span">Part A. Top: the $\phi=0$ section is $\cos^2\theta$ and $\phi=90°$ is constant. Blue points use $S_z\cos\theta$; red × use incorrect $S_z/\cos\theta$. Bars compare L2 for three conversions. Bottom: Meep, analytical, and difference maps for the sampled hemisphere. Gray bands are uncomputed glancing regions.</figcaption>
</figure>


| Conversion | Relative L2 over 240 computed samples |
|---|---|
| $S_z\cos\theta$ | 0.22% |
| Unconverted $S_z$ | 53% |
| $S_z/\cos\theta$ | 76% |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/03b_vacuum_pattern_wrong_setup.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/03b_vacuum_pattern_wrong_setup.png' | relative_url }}" alt="Failed first run with explicit dimensions=1 and no z k_point component: azimuth-independent pattern and dark theta=0 row" loading="lazy"></a>
<figcaption markdown="span">First run of the same script, with explicit `dimensions=1` and no z component in `k_point`. The Meep map is independent of $\phi$ and only its $\theta=0$ row is dark: fingerprints of ignored transverse k and real fields at k = 0, respectively. L2 is 0.35. The incorrect figure is retained because it diagnoses the setup errors.</figcaption>
</figure>


<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/04_pec_field.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/04_pec_field.png' | relative_url }}" alt="Part B steady-state Ez of dipole plus image: mirror plane y=0, residual magnitude 0.012 of maximum, and closed near2far box" loading="lazy"></a>
<figcaption markdown="span">Part B: steady-state Ez of dipole plus image. White dashed $y=0$ marks the mirror; sampled $\lvert E_z\rvert$ there is 0.012 times the maximum. Only the upper half is physical. The dashed rectangle is the near2far box.</figcaption>
</figure>


<figure class="lesson-figure">
<a href="{{ '/assets/meep/10/05_pec_pattern.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/10/05_pec_pattern.png' | relative_url }}" alt="Mirror-dipole pattern comparing 2D near2far, analytical array factor, and 1D Bloch sections, with glancing-angle errors highlighted" loading="lazy"></a>
<figcaption markdown="span">Left: mirror-dipole pattern. Blue: 2D near2far; black dashed: array factor; green: 1D Bloch at $\phi=90°$; red ×: glancing angles. Center: at $\phi=0$, the array factor is multiplied by the dipole’s $\cos^2\theta$. Right: angular errors. Gray shading marks angles above 72°.</figcaption>
</figure>


| Method | Compared against | Relative L2 |
|---|---|---|
| B: 2D near2far (Ez) | $\sin^2(kh\cos\theta)$, 50 angles | 0.66% (peak-bin difference 0) |
| C: 1D Bloch (Ex, $\phi=90°$), below 72° | $\sin^2(kh\cos\theta)$ | 6.8% |
| C: same, including through 85° | Same | 10.5% (correlation 0.981) |
| C: 1D Bloch ($\phi=0$), below 72° | $\cos^2\theta\,\sin^2(kh\cos\theta)$ | 6.0% |
| B versus C, below 72° | Each other | 6.4% |



### Compare against the predictions

| Quantity | Prediction (§2) | Simulation | Verdict |
|--------|-------------|-----------|------|
| 1D runs versus analytical pattern | Within 2% | 0.22% | ✅ |
| Conversion factor | Multiply by $\cos\theta$ | Multiplication 0.22%, division 76% | ✅ |
| $\phi=90°$ section | Constant | Constant | ✅ |
| 2D PEC versus array factor | Within 1% | 0.66% | ✅ |
| $\lvert E_z\rvert$ at $y=0$ | 0 | 0.012 of maximum | ✅ |
| Lobe count | Five | Five; strongest at 12.9° | ✅ |
| 1D Bloch PEC versus 2D | Within 2% | 6.4% | ❌ (6.4%) |
| 1D runs above 72° | Distorted | Including through 85° gives L2 10.5% | ✅ |

Seven of eight predictions agree. The 1D mirror method reproduces lobe positions and count but retains about 6% amplitude disagreement even below 72°. Two possible causes are proposed. Half-cell uncertainty of 10 nm in mirror position changes $kh$ by about 0.12 rad and can alter the θ = 0 lobe amplitude by 5%. Also, 5° sampling can miss peaks and valleys of lobes only about 10° wide, affecting the normalization maximum. The 2D calculation gives 0.66%, but these two effects were not independently isolated. The earlier 10_sources 1D PEC note stopped at correlation 0.947; the present comparison records correlation near 0.98 and L2 0.105 when glancing angles are included. Vacuum has no mirror-position uncertainty and gives 0.22%.

### Convergence

| Variable | Value | Result | Note |
|---|---|---|---|
| A angular grid | 13 × 24 (here) versus 30 × 50 (note 0724) | L2 0.22% versus 0.22% | Samples are independent runs; angular density changes plot sampling, not each run’s spatial resolution. Note 0722’s 1.99% used fixed-time stopping |
| C glancing inclusion | Below 72° / through 85° | 6.8% / 10.5% | Note 0722’s correlation 0.947 included glancing angles |
| B resolution | 100 (same as notes) | 0.66% | Notes: 0.47%; try a resolution ladder yourself |

### What the results do and do not establish

- Supported: the vacuum x-dipole 3D pattern below 72° is reproduced by 1D runs within 0.22%, using $S_z\cos\theta$. The 2D mirror-dipole pattern agrees with the image-theory array factor within 0.66%. The 1D mirror method reproduces the same lobe structure below 72°, with the measured 6.4% cross-method discrepancy.
- Not established: radiation intensity above 72°, where 1D results are unreliable and 2D near2far convergence was not separately checked; absolute power; directivity; lossy-metal mirrors; or generalization to y polarization and other resolutions.


### Original §6 · Common mistakes

| Symptom | Cause | Fix |
|------|------|----------|
| Angle-independent flux, pattern L2 35% | Explicit `dimensions=1` ignores transverse k | Omit `dimensions`; use `cell_size=(0, 0, sz)` |
| Only the $\theta=0$ run gives one-quarter power | $\mathbf k=0$ switches to real fields | Add z component $f\cos\theta$ to `k_point` to keep complex fields |
| 1D run does not finish | Setup error above, or poor glancing-angle PML absorption | Fix setup; use fixed `until_after_sources` for the glancing diagnostic |
| Excessive intensity at large $\theta$ | Incorrect $S_z/\cos\theta$ conversion | Use $S_z\cos\theta$ |
| Hemisphere L2 around 30% | Uncomputed glancing samples included as zeros | Compare computed samples only and plot missing data as missing |
| Antinode at $y=0$ | Wrong image sign or missing `phase=-1` | Ez odd; Hz even |
| All lobe angles shifted | Missing background index in $k$ | Use $k=2\pi n/\lambda$ and include n in part C’s `k_point` |
| Distorted near2far pattern | Wrong segment `weight` signs | Use −1 for bottom and left |
| Mirror disappears in C (L2 43%) | `k_point` makes walls Bloch-periodic | Add an explicit `mp.metal` geometry block |
| 1D lobe amplitude differs by about 5% | Possible half-cell (10 nm) mirror uncertainty and 0.12 rad shift in $kh$ | Refine resolution or align h to the grid and test |


### Original §7 · Try it yourself

| Change | Expected effect | Measurement to inspect |
|---------|----------|------------|
| Use a y dipole in A | Pattern rotates 90° in $\phi$ | Check whether the $\phi=0$ section becomes constant |
| `GLANCING` 0.95 → 0.99 | Adds 72–82° samples with larger error | \|Meep − analytical\| on those rows |
| Part B h → 0.3 µm | $kh=3.5$, one or two lobes | Peak angles |
| Part B resolution 50 / 100 / 150 | L2 convergence ladder | Where the 0.66% error levels off |
| Part B Hz polarization | Image sign +1, `Mirror(Y, phase=+1)` | Check for an antinode at $y=0$ |

</details>

<details>
<summary>Complete code/dipole_pattern_3d.py (expand to view)</summary>
{% highlight python %}
"""Meep Example 10 - 3D radiation pattern of a point dipole: a family of 1D Bloch runs, and a PEC mirror.

Post 01 showed a 2D point source radiating equally in all directions. This post asks the 3D question in two ways.
  A. Vacuum Ex dipole, 3D pattern WITHOUT a 3D cell: one 1D simulation per direction (theta, phi), each with a
     transverse Bloch wavevector k = f (sin t cos p, sin t sin p, 0). The z flux of each run, times cos(theta),
     is one angular sample of the 3D pattern. Compared with the analytic dipole pattern 1 - sin^2(t) cos^2(p).
  B. A dipole 1.25 um above a perfect-electric-conductor (PEC) mirror, 2D (Ez): the mirror is replaced by an
     opposite-sign image dipole plus an odd mirror symmetry, and the far field comes from a closed near2far box.
     Compared with the two-element array factor sin^2(k h cos t).
  C. The same mirror problem with the 1D Bloch method of part A (3D Ex dipole, PEC = metallic cell boundary):
     the two methods agree on the pattern away from grazing angles; near grazing the 1D method breaks down.

Run:  python dipole_pattern_3d.py     (~3 min on one core)
Out:  00_source.png, 01_layout.png, 02_layout_1d.png, 03_vacuum_pattern.png, 04_pec_field.png, 05_pec_pattern.png,
      06_anim_pec.gif, 07_anim_1d.gif, result.json   (-> ../assets/10/)
"""
import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import animation
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, _badge, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "10")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()


def rel_l2(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.linalg.norm(a - b) / np.linalg.norm(b))


# =================================================================== A. vacuum dipole via 1D Bloch runs
# ---------------------------------------------------------------- (1) parameters (official dipole_in_vacuum_1D.py, smaller grid)
WL_A = 1.0                               # wavelength [um]; the pattern is scale-free
FCEN_A = 1 / WL_A
FWIDTH_A = 0.1 * FCEN_A
RES_A = 50
DPML_A, DAIR_A = 1.0, 10.0
SZ_A = DPML_A + DAIR_A + DPML_A
Z_SRC_A = -0.5 * DAIR_A                  # dipole at the bottom of the air gap (official)
Z_MON_A = 0.5 * DAIR_A                   # flux point at the top of the air gap
GLANCING = 0.95                          # skip k_perp > 0.95 f: PML cannot absorb nearly-parallel waves (official rule)
POLAR = np.radians(np.arange(0.0, 90.1, 7.5))      # 13 polar angles (0 = +z)
AZIM = np.radians(np.arange(0.0, 360.0, 15.0))     # 24 azimuth angles


def bloch_k(theta, phi, fcen, n_index=1.0):
    """Full wavevector of the outgoing plane wave, |k| = n f. The z component keeps k != 0 at theta = 0,
    so every run uses complex fields (a k = 0 run would switch to real fields and change the power scale by 4)."""
    return mp.Vector3(n_index * fcen * np.sin(theta) * np.cos(phi), n_index * fcen * np.sin(theta) * np.sin(phi), n_index * fcen * np.cos(theta))


def flux_1d(theta, phi, *, fcen, fwidth, n_index=1.0, sz=SZ_A, z_src=Z_SRC_A, z_mon=Z_MON_A, pml=None, geometry=(), component=mp.Ex, until=None):
    """One 1D run: Bloch k from (theta, phi), source at z_src, Poynting z-flux at z_mon.
    NOTE: do not pass dimensions=1. The cell size (0, 0, sz) already makes the run 1D, and an explicit dimensions=1
    silently drops the transverse k (the flux then no longer depends on the angle)."""
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, sz), resolution=RES_A, k_point=bloch_k(theta, phi, fcen, n_index),
                        default_material=mp.Medium(index=n_index), geometry=list(geometry),
                        boundary_layers=pml if pml is not None else [mp.PML(thickness=DPML_A, direction=mp.Z)],
                        sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=component, center=mp.Vector3(0, 0, z_src), size=mp.Vector3())])
    mon = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(0, 0, z_mon), size=mp.Vector3(), direction=mp.Z))
    sim.run(until_after_sources=until if until is not None else mp.stop_when_fields_decayed(25, component, mp.Vector3(0, 0, z_mon), 1e-6))
    f = float(mp.get_fluxes(mon)[0]); sim.reset_meep()
    return f


t_a = time.time()
flux_z = np.full((len(POLAR), len(AZIM)), np.nan)
for i, th in enumerate(POLAR):
    if np.sin(th) > GLANCING:
        continue
    for j, ph in enumerate(AZIM):
        flux_z[i, j] = flux_1d(th, ph, fcen=FCEN_A, fwidth=FWIDTH_A)
n_runs = int(np.sum(~np.isnan(flux_z)))
computed = ~np.isnan(flux_z)
cos_t = np.cos(POLAR)[:, None]
radial = flux_z * cos_t                                   # official: radial flux = (kz / f) * flux_z
TH, PH = np.meshgrid(POLAR, AZIM, indexing="ij")
analytic_A = 1 - np.sin(TH) ** 2 * np.cos(PH) ** 2        # |E|^2 of an x-polarized dipole, up to a constant


def norm(p, mask):
    return p / np.nanmax(np.where(mask, p, np.nan))


err_mul = rel_l2(norm(radial, computed)[computed], norm(analytic_A, computed)[computed])
err_div = rel_l2(norm(flux_z / cos_t, computed)[computed], norm(analytic_A, computed)[computed])
err_raw = rel_l2(norm(flux_z, computed)[computed], norm(analytic_A, computed)[computed])
j0 = 0; j90 = int(np.argmin(np.abs(AZIM - np.pi / 2)))
err_phi0 = rel_l2(norm(radial, computed)[computed[:, j0], j0], norm(analytic_A, computed)[computed[:, j0], j0])
print(f"A: {n_runs} 1D runs ({len(POLAR)}x{len(AZIM)} grid, {int(np.sum(~computed))} glancing samples skipped) in {time.time() - t_a:.0f} s; "
      f"rel L2 vs analytic (computed samples): flux_z*cos = {err_mul:.4f}, flux_z/cos = {err_div:.4f}, flux_z raw = {err_raw:.4f}; phi=0 cut {err_phi0:.4f}")

# schematic of the 1D cell (plot2D has nothing to draw in 1D)
fig, ax = plt.subplots(figsize=(8.6, 3.2))
ax.axhspan(-0.5, 0.5, xmin=0, xmax=DPML_A / SZ_A, color="green", alpha=0.25); ax.axhspan(-0.5, 0.5, xmin=1 - DPML_A / SZ_A, xmax=1, color="green", alpha=0.25)
ax.plot([Z_SRC_A, Z_SRC_A], [-0.4, 0.4], color="red", lw=3); ax.plot(Z_MON_A, 0, "s", color="blue", ms=9)
th_demo = np.radians(45)
ax.annotate("", xy=(Z_SRC_A + 2.2 * np.cos(th_demo), 0.45 * np.sin(th_demo)), xytext=(Z_SRC_A, 0), arrowprops=dict(arrowstyle="->", color="purple", lw=1.8))
ax.text(Z_SRC_A + 1.4, 0.36, "k = f (sin t cos p, sin t sin p, cos t)\nonly the z axis is simulated", color="purple", fontsize=8)
for xy, step, color, txt, txy in (((-0.5 * SZ_A + 0.3, 0.42), 1, "dimgray", f"wl={WL_A} um, res={RES_A}\n{len(POLAR)} polar x {len(AZIM)} azimuth runs", (-0.5 * SZ_A + 0.6, 0.30)),
                                   ((Z_SRC_A, -0.42), 3, "red", "Ex dipole (GaussianSource)", (Z_SRC_A + 0.25, -0.46)),
                                   ((-0.5 * SZ_A + 0.5 * DPML_A, 0), 4, "green", "PML (both ends)", (-0.5 * SZ_A + 0.1, -0.15)),
                                   ((Z_MON_A, 0.12), 5, "blue", "flux point: Poynting z-flux", (Z_MON_A - 2.6, 0.18)),
                                   ((Z_MON_A, -0.12), 6, "purple", "decay watch point", (Z_MON_A - 1.9, -0.3))):
    _badge(ax, xy, step, color); ax.text(*txy, txt, fontsize=8, color=color)
ax.set_xlim(-0.5 * SZ_A, 0.5 * SZ_A); ax.set_ylim(-0.5, 0.5); ax.set_yticks([]); ax.set_xlabel("z [um]")
ax.set_title("part A: one 1D cell per direction; the transverse Bloch wavevector k_point picks the direction (theta, phi)", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_layout_1d.png"), dpi=150); plt.close(fig)

# pattern figure: two polar cuts + hemisphere maps
fig = plt.figure(figsize=(13, 7.6))
gs = fig.add_gridspec(2, 3)
for col, (j, lab, an) in enumerate(((j0, "phi = 0 (plane of the dipole axis): cos^2(theta)", np.cos(POLAR) ** 2),
                                    (j90, "phi = 90 deg (plane normal to the dipole): isotropic", np.ones_like(POLAR)))):
    ax = fig.add_subplot(gs[0, col], projection="polar")
    m = computed[:, j]
    ax.plot(POLAR[m], norm(radial, computed)[m, j], "o", color="tab:blue", ms=4, label="Meep: flux_z cos(theta)")
    ax.plot(POLAR, an, "-", color="k", lw=1.2, label="analytic")
    ax.plot(POLAR[m], norm(flux_z / cos_t, computed)[m, j], "x", color="tab:red", ms=4, alpha=0.6, label="flux_z / cos(theta) (wrong)")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.set_rlim(0, 1.6)
    ax.set_title(lab, fontsize=9); ax.legend(fontsize=7, loc="lower left")
ax = fig.add_subplot(gs[0, 2])
ax.bar(["flux_z cos", "flux_z raw", "flux_z / cos"], [err_mul, err_raw, err_div], color=["tab:green", "tab:gray", "tab:red"])
for k_, v in enumerate([err_mul, err_raw, err_div]):
    ax.text(k_, v + 0.01, f"{v:.3f}", ha="center", fontsize=8)
ax.set_ylabel("relative L2 vs analytic (computed samples)"); ax.set_title("which conversion of the z flux is the radial flux?", fontsize=9); ax.grid(axis="y", alpha=0.3)
Td, Pd = np.degrees(POLAR), np.degrees(AZIM)
for col, (data, ttl, cmap, vmax) in enumerate(((norm(radial, computed), "Meep: normalized radial flux", "viridis", 1.0),
                                                (norm(analytic_A, computed), "analytic 1 - sin^2(t) cos^2(p)", "viridis", 1.0),
                                                (np.abs(norm(radial, computed) - norm(analytic_A, computed)), "|Meep - analytic|", "magma", None))):
    ax = fig.add_subplot(gs[1, col])
    pc = ax.pcolormesh(Pd, Td, np.where(computed, data, np.nan), cmap=cmap, vmin=0, vmax=vmax, shading="nearest")
    ax.axhspan(np.degrees(np.arcsin(GLANCING)), 90, color="lightgray", alpha=0.6); ax.text(5, 80, "not computed (glancing)", fontsize=7)
    ax.set_xlabel("azimuth phi [deg]"); ax.set_ylabel("polar theta [deg]"); ax.set_title(ttl, fontsize=9); fig.colorbar(pc, ax=ax, shrink=0.85)
fig.suptitle(f"3D pattern of an x-dipole from {n_runs} 1D runs: rel L2 {err_mul:.3f} on the computed hemisphere", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_vacuum_pattern.png"), dpi=150); plt.close(fig)

# GIF of one oblique 1D run (theta = 45 deg): Re(Ex) along z vs time
th_g = np.radians(45)
sim_g = mp.Simulation(cell_size=mp.Vector3(0, 0, SZ_A), resolution=RES_A, k_point=bloch_k(th_g, 0.0, FCEN_A),
                      boundary_layers=[mp.PML(thickness=DPML_A, direction=mp.Z)],
                      sources=[mp.Source(mp.GaussianSource(FCEN_A, fwidth=0.4 * FCEN_A), component=mp.Ex, center=mp.Vector3(0, 0, Z_SRC_A), size=mp.Vector3())])
sim_g.init_sim()
t0g = 5 / (0.4 * FCEN_A)
frames_g, times_g = [], []
sim_g.run(until=t0g - 2 / (0.4 * FCEN_A))
for i in range(50):
    sim_g.run(until=0.3)
    frames_g.append(np.real(sim_g.get_array(center=mp.Vector3(), size=mp.Vector3(0, 0, SZ_A), component=mp.Ex)))
    times_g.append(sim_g.meep_time())
zs = np.linspace(-0.5 * SZ_A, 0.5 * SZ_A, len(frames_g[0]))
lim_g = max(np.max(np.abs(f)) for f in frames_g)
fig_g, ax_g = plt.subplots(figsize=(7.6, 2.9))
ln, = ax_g.plot(zs, frames_g[0], color="tab:blue"); ax_g.set_ylim(-lim_g, lim_g); ax_g.set_xlim(zs[0], zs[-1])
ax_g.axvspan(zs[0], zs[0] + DPML_A, color="green", alpha=0.2); ax_g.axvspan(zs[-1] - DPML_A, zs[-1], color="green", alpha=0.2)
ax_g.axvline(Z_SRC_A, color="red", lw=1.5, label="source"); ax_g.axvline(Z_MON_A, color="blue", lw=1.5, ls="--", label="flux point")
ax_g.set_xlabel("z [um]"); ax_g.set_ylabel("Re(Ex)"); ax_g.legend(fontsize=7, loc="upper right"); ttl_g = ax_g.set_title("", fontsize=9)
fig_g.tight_layout()


def _upd(i):
    ln.set_ydata(frames_g[i]); ttl_g.set_text(f"one 1D run (theta = 45 deg): the pulse moves along z at c cos(theta)   t = {times_g[i]:.1f} um/c")
    return ln, ttl_g


animation.FuncAnimation(fig_g, _upd, frames=len(frames_g), blit=False).save(os.path.join(OUT, "07_anim_1d.gif"), writer=animation.PillowWriter(fps=10), dpi=80)
plt.close(fig_g); sim_g.reset_meep()

# =================================================================== B. dipole above a PEC mirror, 2D near2far with an image dipole
# ---------------------------------------------------------------- (1) parameters (official antenna_pec_ground_plane.py)
WL_B = 0.65
FCEN_B = 1 / WL_B
FWIDTH_B = 0.2 * FCEN_B
N_B = 1.2
H = 1.25                                 # dipole height above the mirror
RES_B = 100
DPML_B, DBULK = 0.5, 6.0
S_B = DBULK + 2 * DPML_B                 # 7 x 7 cell
R_FF = 1000 * WL_B
NANG = 50
THETA_B = np.linspace(0, 0.5 * np.pi, NANG)          # angle from the mirror normal (+y)
K_B = 2 * np.pi * N_B / WL_B
array_factor = np.sin(K_B * H * np.cos(THETA_B)) ** 2
array_factor /= array_factor.max()

sources_B = [mp.Source(mp.GaussianSource(FCEN_B, fwidth=FWIDTH_B), component=mp.Ez, center=mp.Vector3(0, H)),
             mp.Source(mp.GaussianSource(FCEN_B, fwidth=FWIDTH_B), component=mp.Ez, center=mp.Vector3(0, -H), amplitude=-1.0)]   # image dipole
symB = [mp.Mirror(mp.X), mp.Mirror(mp.Y, phase=-1)]                                                                        # odd in y -> Ez = 0 on y = 0 (PEC)
common_B = dict(cell_size=mp.Vector3(S_B, S_B), resolution=RES_B, boundary_layers=[mp.PML(DPML_B)], default_material=mp.Medium(index=N_B))
sim_B = mp.Simulation(sources=sources_B, symmetries=symB, **common_B)
BOX = 2.0                                                                                                                  # half-size of the near2far box (encloses both dipoles)
n2f = sim_B.add_near2far(FCEN_B, 0, 1,
                        mp.Near2FarRegion(center=mp.Vector3(0, BOX), size=mp.Vector3(2 * BOX, 0)),
                        mp.Near2FarRegion(center=mp.Vector3(0, -BOX), size=mp.Vector3(2 * BOX, 0), weight=-1),
                        mp.Near2FarRegion(center=mp.Vector3(BOX, 0), size=mp.Vector3(0, 2 * BOX)),
                        mp.Near2FarRegion(center=mp.Vector3(-BOX, 0), size=mp.Vector3(0, 2 * BOX), weight=-1))
dft_B = sim_B.add_dft_fields([mp.Ez], FCEN_B, 0, 1, center=mp.Vector3(), size=mp.Vector3(DBULK, DBULK))
annotated_layout(
    sim_B, os.path.join(OUT, "01_layout.png"), dpml=DPML_B, figsize=(6.6, 6.2), axis_step=1.0,
    title="part B: dipole above a PEC mirror = dipole + opposite image, odd mirror symmetry in y",
    params_text=f"wl={WL_B} um, n={N_B}\nh={H} um, res={RES_B}\nk h = {K_B * H:.1f}",
    params_xy=(-3.4, 3.1), pml_xy=(-3.0, -3.25), decay_point=None,
    labels=[Label("physical Ez dipole at y = +h", (0.05, H), (0.6, 2.4), step=3, color="red"),
            Label("image dipole at y = -h, amplitude -1", (0.05, -H), (0.6, -2.4), step=3, color="red"),
            Label("y = 0: Ez = 0 here (effective PEC)", (-1.2, 0.0), (-3.4, -0.9), step=2, color="black"),
            Label("closed near2far box (4 segments)", (BOX, 1.0), (0.4, 1.4), step=5, color="blue")])
source_figure(FCEN_B, FWIDTH_B, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")
t_b = time.time()
sim_B.run(until_after_sources=mp.stop_when_dft_decayed(tol=1e-6))
ez_B = sim_B.get_dft_array(dft_B, mp.Ez, 0)
pattern_B = np.zeros(NANG)
for i, th in enumerate(THETA_B):
    ff = sim_B.get_farfield(n2f, mp.Vector3(R_FF * np.sin(th), R_FF * np.cos(th)))
    E = np.array(ff[:3]); Hf = np.array(ff[3:])
    S = np.real(np.cross(E, np.conj(Hf)))
    pattern_B[i] = np.hypot(S[0], S[1])
sim_B.reset_meep()
pattern_B /= pattern_B.max()
err_B = rel_l2(pattern_B, array_factor)
peak_B, peak_an = int(np.argmax(pattern_B)), int(np.argmax(array_factor))
node = float(np.max(np.abs(ez_B[:, ez_B.shape[1] // 2])) / np.max(np.abs(ez_B)))
print(f"B: 2D near2far pattern vs sin^2(k h cos theta): rel L2 {err_B:.4f}, peak bin Meep {peak_B} vs analytic {peak_an} "
      f"({np.degrees(THETA_B[peak_B]):.1f} deg), |Ez| on the y = 0 line / max = {node:.1e}; {time.time() - t_b:.0f} s")

ext_B = [-0.5 * DBULK, 0.5 * DBULK, -0.5 * DBULK, 0.5 * DBULK]
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.6))
lim = float(np.max(np.abs(ez_B)))
ax[0].imshow(np.real(ez_B).T, extent=ext_B, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal"); ax[0].set_title("Re(Ez) at the center frequency", fontsize=9)
ax[1].imshow(np.abs(ez_B).T, extent=ext_B, origin="lower", cmap="inferno", aspect="equal"); ax[1].set_title("|Ez|: the y = 0 line is a node (the mirror)", fontsize=9)
for a in ax:
    a.axhline(0, color="w", ls="--", lw=1.0); a.plot([0, 0], [H, -H], "o", color="lime", ms=4)
    a.add_patch(plt.Rectangle((-BOX, -BOX), 2 * BOX, 2 * BOX, fill=False, color="cyan", lw=1.0, ls=":")); a.set_xlabel("x [um]")
ax[0].set_ylabel("y [um]")
fig.suptitle("part B: steady-state field of dipole + image. Only the upper half (y > 0) is physical.", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_pec_field.png"), dpi=150); plt.close(fig)

# GIF: monitor-free run with a short pulse, both dipoles visible, node line marked
sim_gB = mp.Simulation(sources=[mp.Source(mp.GaussianSource(FCEN_B, fwidth=0.5 * FCEN_B), component=mp.Ez, center=mp.Vector3(0, H)),
                                mp.Source(mp.GaussianSource(FCEN_B, fwidth=0.5 * FCEN_B), component=mp.Ez, center=mp.Vector3(0, -H), amplitude=-1.0)],
                       symmetries=symB, **dict(common_B, resolution=50))
sim_gB.init_sim()
vol_gB = mp.Volume(center=mp.Vector3(), size=mp.Vector3(DBULK, DBULK))
t0B = 5 / (0.5 * FCEN_B)
frames_B, times_B = record_frames(sim_gB, vol_gB, mp.Ez, t_start=t0B - 2 / (0.5 * FCEN_B), t_end=t0B + 1.1 * 0.5 * DBULK * N_B * 1.5, n_frames=60)
animate_fields(frames_B, times_B, ext_B, os.path.join(OUT, "06_anim_pec.gif"), figsize=(5.6, 5.0), dpi=70,
               lines=[((-0.5 * DBULK, 0), (0.5 * DBULK, 0), "k", "mirror plane y = 0 (Ez node)"), ((-BOX, BOX), (BOX, BOX), "blue", "near2far box (top)")],
               points=[(0, H, "red", "dipole"), (0, -H, "orange", "image dipole (-1)")], title="dipole + image", legend_loc="lower right")
sim_gB.reset_meep()

# =================================================================== C. the mirror problem with the 1D Bloch method (3D Ex dipole above PEC)
# A k_point makes EVERY cell boundary Bloch-periodic, so the mirror cannot be the cell wall: it is a block of mp.metal
# (perfect electric conductor) at the bottom of the 1D cell. PML only at the top; background n = 1.2.
DMETAL = 0.5
SZ_C = DMETAL + H + DAIR_A + DPML_A
Z_BOT = -0.5 * SZ_C
Z_PEC = Z_BOT + DMETAL                               # mirror surface
Z_SRC_C = Z_PEC + H
Z_MON_C = Z_PEC + H + DAIR_A
mirror = [mp.Block(center=mp.Vector3(0, 0, Z_BOT + 0.5 * DMETAL), size=mp.Vector3(mp.inf, mp.inf, DMETAL), material=mp.metal)]
POLAR_C = np.radians(np.arange(0.0, 90.0, 5.0))      # includes grazing angles on purpose
T_C = 150.0                                          # fixed duration: at 85 deg the wave needs ~140 time units to cross 10 um of n = 1.2
flux_C = {}
for phi_deg in (90.0, 0.0):
    vals = [flux_1d(th, np.radians(phi_deg), fcen=FCEN_B, fwidth=0.1 * FCEN_B, n_index=N_B, sz=SZ_C, z_src=Z_SRC_C, z_mon=Z_MON_C,
                    pml=[mp.PML(thickness=DPML_A, direction=mp.Z, side=mp.High)], geometry=mirror, until=T_C) for th in POLAR_C]
    flux_C[phi_deg] = np.array(vals) * np.cos(POLAR_C)
af_C = np.sin(K_B * H * np.cos(POLAR_C)) ** 2
an_C = {90.0: af_C, 0.0: af_C * np.cos(POLAR_C) ** 2}             # phi=0: times the dipole's own cos^2
ok_C = np.sin(POLAR_C) <= GLANCING
res_C = {}
for phi_deg in (90.0, 0.0):
    p = flux_C[phi_deg] / flux_C[phi_deg][ok_C].max(); a = an_C[phi_deg] / an_C[phi_deg][ok_C].max()
    res_C[phi_deg] = {"pattern": p, "analytic": a, "err_in": rel_l2(p[ok_C], a[ok_C]), "err_all": rel_l2(p, a),
                      "corr_all": float(np.corrcoef(p, a)[0, 1])}
    print(f"C [phi = {phi_deg:.0f} deg]: 1D Bloch, {len(POLAR_C)} angles: rel L2 {res_C[phi_deg]['err_in']:.4f} below the glancing limit, "
          f"{res_C[phi_deg]['err_all']:.4f} with grazing angles included (correlation {res_C[phi_deg]['corr_all']:.4f})")
pB_on_C = np.interp(POLAR_C, THETA_B, pattern_B)
err_BC = rel_l2(res_C[90.0]["pattern"][ok_C], pB_on_C[ok_C])
print(f"B vs C: 2D near2far (Ez) vs 1D Bloch (Ex, phi = 90 deg) on the same angles: rel L2 {err_BC:.4f}")

fig = plt.figure(figsize=(13, 4.6))
ax = fig.add_subplot(1, 3, 1, projection="polar")
ax.plot(THETA_B, pattern_B, "-", color="tab:blue", lw=1.6, label="B: 2D near2far (Ez dipole)")
ax.plot(THETA_B, array_factor, "--", color="k", lw=1.2, label="analytic sin^2(k h cos t)")
ax.plot(POLAR_C[ok_C], res_C[90.0]["pattern"][ok_C], "o", color="tab:green", ms=4, label="C: 1D Bloch (Ex, phi = 90)")
ax.plot(POLAR_C[~ok_C], res_C[90.0]["pattern"][~ok_C], "x", color="tab:red", ms=6, label="C: grazing angles")
ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.set_rlim(0, 1.3)
ax.set_title(f"dipole {H} um above a PEC, k h = {K_B * H:.1f}", fontsize=9); ax.legend(fontsize=6.5, loc="lower left")
ax = fig.add_subplot(1, 3, 2, projection="polar")
ax.plot(POLAR_C[ok_C], res_C[0.0]["pattern"][ok_C], "o", color="tab:green", ms=4, label="C: 1D Bloch, phi = 0")
ax.plot(POLAR_C[~ok_C], res_C[0.0]["pattern"][~ok_C], "x", color="tab:red", ms=6, label="grazing")
ax.plot(POLAR_C, res_C[0.0]["analytic"], "--", color="k", lw=1.2, label="analytic cos^2(t) sin^2(k h cos t)")
ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.set_rlim(0, 1.3)
ax.set_title("phi = 0: array factor times the dipole's cos^2", fontsize=9); ax.legend(fontsize=6.5, loc="lower left")
ax = fig.add_subplot(1, 3, 3)
for phi_deg, c in ((90.0, "tab:green"), (0.0, "tab:olive")):
    ax.plot(np.degrees(POLAR_C), np.abs(res_C[phi_deg]["pattern"] - res_C[phi_deg]["analytic"]), "o-", color=c, ms=4, label=f"1D Bloch, phi = {phi_deg:.0f}")
ax.plot(np.degrees(THETA_B), np.abs(pattern_B - array_factor), "-", color="tab:blue", lw=1.4, label="2D near2far")
ax.axvspan(np.degrees(np.arcsin(GLANCING)), 90, color="lightgray", alpha=0.6); ax.text(np.degrees(np.arcsin(GLANCING)) + 1, 0.02, "glancing:\nPML fails", fontsize=7)
ax.set_xlabel("theta from the mirror normal [deg]"); ax.set_ylabel("|pattern - analytic| (normalized)"); ax.set_yscale("log"); ax.set_ylim(1e-4, 2)
ax.grid(alpha=0.3); ax.legend(fontsize=7); ax.set_title("where each method fails", fontsize=9)
fig.suptitle(f"B: rel L2 {err_B:.4f} (near2far) | C: {res_C[90.0]['err_in']:.4f} below 72 deg, {res_C[90.0]['err_all']:.3f} with grazing angles", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.92]); fig.savefig(os.path.join(OUT, "05_pec_pattern.png"), dpi=150); plt.close(fig)

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"A": {"wl": WL_A, "res": RES_A, "n_polar": len(POLAR), "n_azimuth": len(AZIM), "n_runs": n_runs, "n_skipped": int(np.sum(~computed)),
                         "glancing_limit_deg": float(np.degrees(np.arcsin(GLANCING))), "err_mul": err_mul, "err_div": err_div, "err_raw": err_raw, "err_phi0": err_phi0},
                   "B": {"wl": WL_B, "n": N_B, "h": H, "res": RES_B, "kh": K_B * H, "box": BOX, "err": err_B, "peak_bin": [peak_B, peak_an],
                         "peak_deg": float(np.degrees(THETA_B[peak_B])), "node_ratio": node,
                         "pattern": pattern_B.tolist(), "analytic": array_factor.tolist(), "theta_deg": np.degrees(THETA_B).tolist()},
                   "C": {str(int(k_)): {"err_in": v["err_in"], "err_all": v["err_all"], "corr_all": v["corr_all"], "pattern": v["pattern"].tolist()} for k_, v in res_C.items()},
                   "B_vs_C": err_BC, "theta_C_deg": np.degrees(POLAR_C).tolist(),
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
print(f"total {time.time() - t_all:.0f} s")
{% endhighlight %}
</details>

<details markdown="1">
<summary>Original execution records and reproduction environment</summary>

Unlike the excerpts in §4, the complete code includes the 1D setup diagram, hemisphere maps, two GIFs, and result.json output. The shared helper `blogfig.py` is in the same `code/` folder. Full code and helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**Execution results (run on 2026-10-23)**:
```
A: 240 1D runs (13x24 grid, 72 glancing samples skipped) in 201 s; rel L2 vs analytic (computed samples): flux_z*cos = 0.0022, flux_z/cos = 0.7585, flux_z raw = 0.5290; phi=0 cut 0.0012
B: 2D near2far pattern vs sin^2(k h cos theta): rel L2 0.0066, peak bin Meep 7 vs analytic 7 (12.9 deg), |Ez| on the y = 0 line / max = 1.2e-02; 3 s
C [phi = 90 deg]: 1D Bloch, 18 angles: rel L2 0.0675 below the glancing limit, 0.1052 with grazing angles included (correlation 0.9809)
C [phi = 0 deg]: 1D Bloch, 18 angles: rel L2 0.0599 below the glancing limit, 0.0601 with grazing angles included (correlation 0.9965)
B vs C: 2D near2far (Ez) vs 1D Bloch (Ex, phi = 90 deg) on the same angles: rel L2 0.0637
total 258 s
```

**Reproduction environment**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · run `python dipole_pattern_3d.py` (about 4.3 min, single core)

</details>

### Official documentation and next lesson

- [Near-to-far field spectra tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/) · [Antenna above a PEC ground plane](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-an-antenna-above-a-perfect-electric-conductor-ground-plane) · [dipole_in_vacuum_1D.py](https://github.com/NanoComp/meep/blob/master/python/examples/dipole_in_vacuum_1D.py)
- [`k_point` and Bloch boundaries](https://meep.readthedocs.io/en/latest/Python_User_Interface/#simulation) · [`Symmetry` and `phase`](https://meep.readthedocs.io/en/latest/Python_User_Interface/#symmetry) · [`Near2FarRegion`](https://meep.readthedocs.io/en/latest/Python_User_Interface/#near2farregion)
- Previous: [09 · Waveguide bend inverse design]({{ '/en/bend-inverse/' | relative_url }}) · Season 2 foundations: [01 · Point and line sources]({{ '/en/point-line-source/' | relative_url }}) · Next: [11 · A point source between two mirrors]({{ '/en/cavity-ldos/' | relative_url }})
