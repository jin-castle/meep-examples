---
layout: lesson
permalink: /en/cylindrical-dipole/
lesson_title: "How can rotational symmetry simplify a 3D light calculation?"
lesson_summary: "Split the calculation by azimuthal order m and combine dipole fields. Compare ring coordinate systems and examine the limits of open near2far surfaces."
lesson_goals:
  - "Choose azimuthal orders m for the source direction and position."
  - "Distinguish field summation from per-m power stopping criteria."
  - "Interpret the ring’s dimensionality and the disk’s near–far discrepancy."
lesson_prerequisites: "Chapter 10: near2far and radiation patterns · Chapter 12: azimuthal order m in a ring"
date: 2026-10-23
title: "Meep Example 13 · Computing 3D with rotational symmetry — cylindrical coordinates, m series, on/off-axis dipoles, and disk radiation"
title_en: "Meep Example 13 · Computing 3D with rotational symmetry — cylindrical coordinates, the m series, on- and off-axis dipoles, a radiating disc"
lang: en
translation_key: cylindrical-dipole
series: meep-examples
part: 13
level: intermediate
runtime: "7.6 min (mpirun -np 4)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/"
tags: [meep, fdtd, cylindrical, azimuthal-order, near2far, dipole, disc, ring-resonator]
image: /assets/meep/13/04_off_axis.png
excerpt: "post 12's ring was a 2D cross-section; real discs, rings, lenses and LED mesas are bodies of revolution. `dimensions=mp.CYLINDRICAL` solves them as one 2D (r, z) run per azimuthal order m, with fields ∝ exp(imφ). Four official examples: on-axis dipoles, an off-axis dipole as an m series, post 12's ring as one radial run per m, and a disc on a ground plane radiating through an open near2far surface."
---

<h2 id="observe">1. Observe: how many runs represent an off-axis point source?</h2>

Even when a structure is rotationally symmetric, its source need not be axisymmetric. Representing a point source 0.5 µm from the axis requires **summing fields from multiple runs with different azimuthal orders m**.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/04_off_axis.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/04_off_axis.png' | relative_url }}" alt="Per-m power, partial-sum pattern error, and final radiation pattern of a dipole 0.5 micrometers from the axis"></a>
<figcaption>The actual calculation includes m = 0…8. The last term’s power is 9.49 × 10⁻⁶ of the maximum. The normalized pattern in the φ = 0 plane agrees with analytic cos²θ to relative L2 error 0.63%.</figcaption>
</figure>

<p class="lesson-note"><strong>A partial sum does not improve at every step.</strong> The pattern error for m = 0…2 was 0.099, but adding m = 3 temporarily increased it to 0.141. Check both per-m power and the pattern rather than stopping at an intermediate result that looks good. With other structures or a more distant source, power can become small and then rebound.</p>

<h2 id="predict">2. Predict: does rotational symmetry mean m = 0 is enough?</h2>

<fieldset class="prediction">
<legend>How should an on-axis, x-directed, linearly polarized dipole be represented?</legend>
<label><input type="radio" name="cylindrical-prediction" value="zero"> One m = 0 run is sufficient because the structure is rotationally symmetric.</label>
<label><input type="radio" name="cylindrical-prediction" value="pair"> Both m = +1 and −1 are needed to represent the source direction.</label>
</fieldset>

<details markdown="1">
<summary>Compare your prediction with the source representation</summary>

The second answer is correct. Even in a rotationally symmetric structure, the cylindrical r and φ components of an x-directed vector vary with azimuth φ. This example uses Er and ±i Ep at m = +1 and −1, then adds half of each field. An on-axis z dipole needs only one m = 0 run.

</details>

<h2 id="understand">3. Understand: separate the azimuthal dependence into m orders</h2>

{% include chapter-illustration.html %}

When the structure is independent of φ, the field can be written as **E(r, φ, z) = Σ E_m(r, z) exp(imφ)**. For a chosen m, an azimuthal derivative becomes multiplication by im, and Meep solves the remaining r–z cross-section. This retains 3D effects by representing the azimuthal dependence separately.

<figure class="lesson-figure">
<svg viewBox="0 0 320 220" role="img" aria-labelledby="cylindrical-concept-title" xmlns="http://www.w3.org/2000/svg">
<title id="cylindrical-concept-title">Conceptual diagram: solve the r-z cross-section for each azimuthal order and combine the fields</title>
<rect width="320" height="220" fill="#f5f8fa" />
<path d="M35 142V36M35 142H149M35 36l-5 11M35 36l5 11M149 142l-11-5M149 142l-11 5" stroke="#0d1b2a" fill="none" stroke-width="2" />
<rect x="36" y="77" width="70" height="45" fill="#e7f7fb" stroke="#0087ad" stroke-width="2" />
<circle cx="70" cy="98" r="6" fill="#0087ad" />
<path d="M172 87H290M290 87l-11-5M290 87l-11 5" stroke="#0087ad" fill="none" stroke-width="2" />
<g font-family="sans-serif" font-size="16" fill="#0d1b2a">
<text x="20" y="28">z</text><text x="143" y="165">r</text>
<text x="174" y="55">One run per m</text>
<text x="171" y="115">Apply exp(imφ)</text>
<text x="31" y="186">r–z slice + azimuthal dependence</text>
<text x="31" y="209">Sum fields → directional pattern</text>
</g>
</svg>
<figcaption>Conceptual diagram. The rectangle is a cross-section of a rotationally symmetric structure; the dot is an example source position. Colors and arrows are not numerical fields. Apply the azimuthal dependence to each m solution to reconstruct the desired field.</figcaption>
</figure>

| Source or problem | Required representation |
|---|---|
| On-axis z dipole | m = 0, Ez |
| On-axis x dipole | m = +1 and −1, Er and ±i Ep |
| Off-axis point source | Fourier series over multiple m |
| Ring mode of a specified azimuthal order | One run at that m |

**For a directional pattern, add fields before calculating power.** Adding only per-m powers in the φ = 0 plane loses interference between terms. In contrast, total power integrated over all azimuths can be summed term by term because different m orders are orthogonal. This example stops when an m term’s power falls below 10⁻⁴ of the maximum.

That stopping rule applies to this vacuum example with r₀ = 0.5 µm. For a more distant source or a structured environment, finding **one small term for the first time** does not guarantee that all later terms are small.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/07_anim_m3.gif' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/07_anim_m3.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/13/07_anim_m3.gif' | relative_url }}" data-static-src="{{ '/assets/meep/13/05_ring_cyl.png' | relative_url }}" alt="Rotating m=3 ring mode reconstructed from the calculated radial field using azimuthal and time phase"></a>
<button type="button" class="animation-toggle" hidden>Pause animation</button>
<figcaption>A phase-reconstruction animation applying exp[i(3φ−ωt)] to the calculated Ez(r). This is not a new time-domain 3D simulation. Including an m = −3 component can form a standing wave.</figcaption>
</figure>

<p class="lesson-note"><strong>Dimensionality of the ring example.</strong> The ring-cyl cell in part C has zero z size. It solves the same z-invariant 2D ring problem as chapter 12 in different coordinates; it does not validate a finite-height 3D ring. A general cylindrical r–z cell, however, can represent a rotationally symmetric 3D structure order by order.</p>

Part D uses a disk with refractive index 2.4 and radius 1.2 µm above a lossless PEC ground plane. It calculates one m = −1 ring source, not the full field of an arbitrary off-axis point dipole. The ground plane means the near2far surface includes only the top and outer-r faces and is open underneath.

<h2 id="run">4. Run it: tighten only the m-series stopping threshold</h2>

Download the repository and run from <code>code/</code>. Both <code>cylindrical_dipole.py</code> and the neighboring <code>blogfig.py</code> are required. The original record uses Meep 1.33.0 MPI with Python, NumPy, and Matplotlib, taking about 7.6 minutes on 4 MPI processes.

~~~bash
OMP_NUM_THREADS=1 mpirun -np 4 python cylindrical_dipole.py
~~~

Save the original results in a separate folder first. **Change only POWER_DECAY = 1e-4 to 1e-5**, then rerun the same command. Keep source distance, resolution, and all other parts unchanged.

Compare the last m, last-term power ratio, and final pattern error in the part B log. The original m = 8 ratio is already **9.49e-6**, so this one-step tightening may not increase the last m. Check the actual termination record rather than assuming that unchanged m is a failure. Record new measurements separately from the original 0.63%.

<h2 id="interpret">5. Interpret: what agrees, and what remains unresolved?</h2>

| Original comparison | Actual result | Scope |
|---|---|---|
| On-axis z dipole vs sin²θ | Relative L2 0.43% | Normalized pattern at φ = 0 |
| On-axis x dipole vs cos²θ | Relative L2 0.46% | Sum of m = ±1 fields |
| Off-axis r₀ = 0.5 µm | m = 0…8, relative L2 0.63% | Series for this vacuum example |
| Ring m = 3, 4, 5 frequencies | Differences from chapter 12 of about 0.02%, 0.07%, 0.10% | Coordinate comparison for the same 2D problem |

For ring m = 5, Q is **1627** in cylindrical coordinates and **2132** at Cartesian resolution 20 in chapter 12. Similar frequencies do not establish converged Q. The Cartesian values 1675 and 1610 at other resolutions are closer to the cylindrical result, but this alone does not prove staircased boundaries are the sole cause.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/06_disc.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/06_disc.png' | relative_url }}" alt="Near and far flux comparison for cell radii 6 and 8 micrometers around a disk above a ground plane" loading="lazy"></a>
<figcaption>Actual results from part D. Increasing cell radius from 6 to 8 µm reduces the near–far discrepancy from 7.43% to 6.41%. A discrepancy remains, so total far-field power cannot yet be called converged.</figcaption>
</figure>

| Cell radius | Near flux | Far flux | Relative difference |
|---|---:|---:|---:|
| 6 µm | 643.65 | 595.80 | 7.43% |
| 8 µm | 643.28 | 602.05 | 6.41% |

Near flux stays almost constant while far flux increases. This is consistent with truncating equivalent currents outside the open surface, but two cell sizes do not determine the true total far-field power. **7.43% is a mismatch between two power measurements, not an extraction efficiency.**

<h2 id="check">6. Check your understanding</h2>

1. Explain why one m = 0 run cannot represent an on-axis x dipole, and describe the order of operations for constructing its directional pattern.
2. If the disk’s near–far discrepancy falls from 7.43% to 6.41%, can total far-field power be called converged?

<details markdown="1">
<summary>Check both answers</summary>

1. The cylindrical components of an x-directed vector depend on φ, requiring m = +1 and −1. Add the necessary complex fields first, then calculate the Poynting pattern to preserve interference.
2. No. The result is consistent with reduced truncation at the open near2far surface, but a discrepancy remains. Without a larger surface and further convergence checks, it cannot be reported as the true total power or extraction efficiency.

</details>

<h2 id="reference">7. References and full code</h2>

The detailed equations, per-m results, coordinate-specific settings, and complete execution record are preserved below.


<details markdown="1">
<summary>English summary</summary>

### TL;DR (English)

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/04_off_axis.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/04_off_axis.png' | relative_url }}" alt="Original overview figure for the cylindrical-coordinate calculation" loading="lazy"></a>
</figure>

- **What**: post 12's ring was a 2D cross-section; real discs, rings, lenses and LED mesas are bodies of revolution. `dimensions=mp.CYLINDRICAL` solves them as one 2D (r, z) run per azimuthal order m, with fields ∝ exp(imφ). Four official examples: on-axis dipoles, an off-axis dipole as an m series, post 12's ring as one radial run per m, and a disc on a ground plane radiating through an open near2far surface.
- **Result**: an on-axis z-dipole (m = 0) and x-dipole (m = +1 and −1) reproduce sin²θ and cos²θ to 0.43% and 0.46%. A dipole 0.5 µm off the axis needs m = 0…8 before the last term drops below 10⁻⁴ of the largest; the summed pattern matches cos²θ to 0.63%. The ring's m = 3, 4, 5 modes land within 0.1% of post 12's 2D frequencies. The disc radiates 7.43% less in the far field than through the near monitor, 6.41% with a larger radial cell.
- **Takeaway**: a linearly polarized in-plane dipole is never m = 0. Every point off the axis is a sum over m, each m a separate run, and power (not field) per m decides when to stop. An open near2far surface on a ground plane loses the currents beyond its edge, and that, not the solver, is the near–far gap.
- **Code**: full script at the bottom, ~7.6 min (mpirun -np 4).

</details>

<details markdown="1">
<summary>Background, equations, and parameters in detail</summary>

### Original §0 · What you will learn

- `dimensions=mp.CYLINDRICAL` and `m`: represent fields with exp(imφ) instead of explicitly discretizing φ. The cell is (r, 0, z).
- An on-axis z dipole uses m = 0; an x dipole combines m = +1 and −1. Two circular polarizations form linear polarization.
- An off-axis point source is a Fourier series over m = 0, 1, 2, …. Each m is an independent run, and its radiated power guides truncation.
- Solve chapter 12’s ring again with one 1D radial run per m and reconstruct its 2D image using exp(imφ).
- With an infinite ground plane below, the near2far surface is open. Interpret the difference between near and far flux.

**Prerequisites**: near2far and radiation patterns from chapter 10, azimuthal order m from chapter 12. **Official examples**: [Cylindrical coordinates tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/) · [Antenna in cylindrical coordinates](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-an-antenna-in-cylindrical-coordinates) · scripts [dipole_in_vacuum_cyl_on_axis.py](https://github.com/NanoComp/meep/blob/master/python/examples/dipole_in_vacuum_cyl_on_axis.py) · [dipole_in_vacuum_cyl_off_axis.py](https://github.com/NanoComp/meep/blob/master/python/examples/dipole_in_vacuum_cyl_off_axis.py) · [ring-cyl.py](https://github.com/NanoComp/meep/blob/master/python/examples/ring-cyl.py) · [disc_radiation_pattern.py](https://github.com/NanoComp/meep/blob/master/python/examples/disc_radiation_pattern.py). **Previous**: [12 · A ring that confines light]({{ site.baseurl }}/en/ring-resonator/) · **Next**: 14 · A point source in a thin film: the fraction escaping into air


### Original §1 · What do we want to find out?

This was the closing question of chapter 12. Its ring was a 2D cross-section, but real microdisks, lenses, and LED mesas are 3D bodies of revolution. A full 3D mesh scales cubically. If geometry is independent of φ, the field’s azimuthal dependence can be expanded in exp(imφ); fixing m leaves only (r, z). One 3D problem becomes a 2D problem per m. We ask: which m represents an on-axis dipole, how many orders represent an off-axis point source, and how do the results compare with 3D and chapter 12’s 2D ring?

### Where is this useful?

Axial symmetry is common in emitting, resonant, and focusing devices. Cylindrical coordinates allow these structures to be calculated at a 2D cost per azimuthal order.

| Application | Quantity used here | What comes next |
|---|---|---|
| Extraction from LED, OLED, and micro-LED mesas | On-axis dipoles (m = ±1), off-axis m series, open near2far surfaces | Chapter 14: extraction efficiency |
| Microdisk and microring lasers, biosensors | Azimuthal m as whispering-gallery order; radial 1D runs for z-invariant rings | Comparison with chapter 12; chapter 26: defect cavities |
| Axisymmetric lenses, zone plates, nanoantennas | m = ±1 circularly polarized incidence and axisymmetric far fields | Chapter 16: zone plates |
| Fiber cross-sections and circular grating couplers | Cylindrical guided modes (m), radial PML | — |


### Original §2 · The physics on one page

When geometry is independent of φ, azimuthal derivatives in Maxwell’s equations become multiplication by $im$. Expanding $\mathbf E(r,\phi,z)=\sum_m \mathbf E_m(r,z)\,e^{im\phi}$ gives one independent (r, z) problem per m. Meep accepts one m and solves that problem.

$$
\mathbf E(r,\phi,z)=\sum_{m}\mathbf E_m(r,z)\,e^{im\phi},\qquad
\hat x=\tfrac12\big[e^{i\phi}(\hat r+i\hat\phi)+e^{-i\phi}(\hat r-i\hat\phi)\big],\qquad
P=\sum_m P_m
$$

An on-axis z dipole is independent of φ, so m = 0. An x dipole is not: its cylindrical components rotate with φ. As shown in the middle equation, it combines two circular polarizations ($E_r\pm iE_\phi$) with $e^{\pm i\phi}$ dependence, so add half of each m = +1 and m = −1 run. A point source displaced by r₀ is a delta function in φ, whose Fourier series contains every m. Terms become weak when m exceeds $k r_0$ in this vacuum example. Increase m from 0 and stop when that term’s radiated power falls below 10⁻⁴ of the maximum. Different m orders are orthogonal over the full azimuth, so total integrated power is the sum of per-m powers.

| Symbol | Meaning | Code variable |
|------|----|-----------|
| $m$ | Azimuthal order, field ∝ $e^{im\phi}$ | `m=` |
| $(r, z)$ | Computed cross-section; cell `(sr, 0, sz)` | `cell_size` |
| $r_0$ | Source distance from the axis | `R_SRC` |
| $E_r\pm iE_\phi$ | m = ±1 circularly polarized dipoles | `Er` + `Ep`(amp ±1j) |
| $P_m$ | Radiated power of one m term | `m_flux` |
| near / far | Nearby monitor flux / distant hemisphere integral | `f_near`, `f_far` |

**Assumptions and validity**: parts A and B use vacuum, wavelength 1 µm, and resolution 50. Part C solves chapter 12’s ring (n 3.4, a = 1 µm) in different coordinates; it does not replace that 2D problem with a finite-height axisymmetric 3D device. Its zero-z-size ring-cyl cell is z-invariant. Part D uses an n 2.4 disk above a PEC ground plane and calculates only m = −1 (a ring source).

### Predict before viewing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| On-axis z dipole vs sin²θ | Within 1% | Notes: 0.43% |
| On-axis x dipole (m = ±1) vs cos²θ | Within 1% | Notes: 0.46% |
| m needed for r₀ = 0.5 µm point source | 7~9 | $k r_0=\pi$; notes: m = 8 |
| Decrease in m-series pattern error | Monotonic | More terms should improve accuracy |
| ring-cyl m = 3/4/5 vs chapter 12 2D | Frequencies within 0.2% | Same problem, different coordinates |
| ring-cyl Q(m = 5) vs chapter 12 2D (res 20) | Similar | Same physics |
| Disk near vs far flux | 7% difference | Notes: 7.42%; official example: 7.43% |
| Cell radius 6 → 8 µm | Smaller discrepancy | If caused by open-surface truncation |

**Decision criteria**: if A differs by more than 5%, check the x-dipole $E_\phi$ phase and m sign. If B’s final error stays above 1%, check for a missing −m term (the conjugate negative-frequency field). If D’s discrepancy persists unchanged as the cell grows, investigate a cause other than truncation.


### Original §3 · Simulation layout

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/01_layout.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/01_layout.png' | relative_url }}" alt="Part D cylindrical r-z cell: disk of index 2.4, Er ring source at r = 0.6 µm, upper and radial monitors, PEC ground plane, and PML" loading="lazy"></a>
<figcaption markdown="span">Part D cylindrical (r, z) cell. The left edge is the axis r = 0. The gray block is the n 2.4 disk (radius 1.2 µm), the red point is the Er ring source at r = 0.6 µm, and blue lines show flux and near2far surfaces (top and outer r). No PML is placed at the bottom, so it is a PEC ground plane. Green hatching marks radial and top PML; blue hatching is a representative DFT region. `plot2D` labels even cylindrical axes x and y: here x means r and y means z. Circled numbers refer to §4.</figcaption>
</figure>


<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/02_layout_dipole.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/02_layout_dipole.png' | relative_url }}" alt="Vacuum r-z cell for on-axis and off-axis dipoles, with PML away from the axis and three near2far faces described in the caption" loading="lazy"></a>
<figcaption markdown="span">Parts A and B: a vacuum (r, z) cell with 1 µm PML on every external side except the axis. The dipole is on the axis (A) or at r = 0.5 µm (B). The near2far surface consists of top, outer-r, and bottom (weight −1) faces. The symmetry axis needs no face. This layout was drawn before attaching monitors, so the near2far faces are not shown.</figcaption>
</figure>


| Parameter | Value | Why this value? | Effect of changing it |
|----------|-----|-------------|--------|
| A/B cell | r 2 + PML 1, z 4 + PML 2 | Official values | Keep near2far surfaces outside PML |
| A/B resolution | 50 | Official value | Er source offset 1.5/res changes with it |
| A x dipole | Er + Ep(±1j), m = ±1, r = 1.5/res | Sum of two circular polarizations; Er at r = 0 has a reported bug (meep #2704) | m = 0 does not represent an x dipole |
| B source | Er at r₀ = 0.5, sources at +f and −f | +f supplies +m; conjugate −f supplies −m | Omitting −f loses the −m term |
| B stopping criterion | m-term power / maximum < 10⁻⁴ | Official value | A loose criterion can encounter the rebound in chapter 14 |
| C ring | n 3.4, R 1, w 1, PML 32, res 20 | Official ring-cyl.py | A radial-only cell keeps thick PML inexpensive |
| D disk | n 2.4, R 1.2, t = 0.7λ/n, res 100 | Official values | Changing t changes pattern lobes |
| D cell radius | 6 µm (official), 8 µm | Tests truncation | A larger cell omits less of the open surface |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/00_source.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/00_source.png' | relative_url }}" alt="Source waveform and spectrum, 1000 nm and fwidth 0.1 fcen; all parts use the same relative bandwidth" loading="lazy"></a>
<figcaption markdown="span">Source waveform and spectrum (1000 nm, fwidth 0.1 fcen). All parts use the same relative bandwidth.</figcaption>
</figure>


**Differences from the course notebooks**: this topic is outside the course scope. The 10_sources notes reproduced the four examples separately. This chapter runs all four in one script, measures pattern error after each added m term in B, and places C alongside chapter 12’s 2D results in the same table.

</details>

<details markdown="1">
<summary>Original code, step by step</summary>

### Original §4 · Follow the code

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → run and stopping conditions → postprocessing.
> The new elements are `dimensions=mp.CYLINDRICAL, m=` in ④ and summation over m in ⑦.

### ① Units and parameters — which values are fixed?

```python
WL, RES_D, PML_D = 1.0, 50, 1.0
SR_D, SZ_D = 2.0, 4.0                       # near2far box: r 0..2, z -2..2
R_FF, NPTS = 1e6 * WL, 50                   # far-field radius and polar samples
THETA = np.linspace(0, 0.5 * np.pi, NPTS)   # 0 = +z (pole), pi/2 = +r (equator), in the phi = 0 plane
POWER_DECAY = 1e-4                          # stop the m series when the last term is this small
```

- **What**: official values. Angles are polar angles from +z, and the pattern is sampled in the φ = 0 plane.
- **Why**: x denotes r in a cylindrical cell, while z remains z. The y size is always 0.
- **If wrong**: writing the cell as (sr, sz, 0) from Cartesian habit produces a different problem with zero z size. Part C deliberately uses zero z size.

### ② Materials and geometry — draw only the r ≥ 0 half

```python
mp.Block(material=mp.Medium(index=N_DISC), center=mp.Vector3(0.5 * DISC_R, 0, -0.5 * sz + 0.5 * DISC_T),
         size=mp.Vector3(DISC_R, mp.inf, DISC_T))                                         # D: a disc = a block from r 0 to R
mp.Block(center=mp.Vector3(R_IN + 0.5 * W), size=mp.Vector3(W, mp.inf, mp.inf), material=mp.Medium(index=N_RING))   # C: a ring = a block from r 1 to 2
```

- **What**: the disk is a block from r = 0 to R; the ring is a block from r = 1 to 2. Its φ size is `mp.inf`.
- **Why**: these axisymmetric objects are rectangles in the (r, z) cross-section. There is no need to overlay two cylinders as in chapter 12.
- **If wrong**: centering a width-2R block at r = 0 places its negative-r half outside the cell. The result is the same, but the intent is less clear.

### ③ Sources — the source depends on m

```python
mp.Source(gs(FREQ), component=mp.Ez, center=mp.Vector3())                              # A: z-dipole on the axis, m = 0
[mp.Source(gs(FREQ), component=mp.Er, center=mp.Vector3(r_off)),                       # A: x-dipole = Er + (+-i) Ep, run with m = +1 and m = -1
 mp.Source(gs(FREQ), component=mp.Ep, center=mp.Vector3(r_off), amplitude=1j if m == 1 else -1j)]
[mp.Source(gs(FREQ), component=mp.Er, center=mp.Vector3(R_SRC)),                       # B: off-axis, +f gives the +m term ...
 mp.Source(gs(-FREQ), component=mp.Er, center=mp.Vector3(R_SRC))]                      # ... -f gives the -m term after conjugation
```

- **What**: an on-axis z dipole uses Ez alone. An x dipole uses paired Er and ±i Ep in each m = ±1 run. An off-axis point source uses +f and −f sources for each m.
- **Why**: the third configuration avoids a separate $e^{-im\phi}$ run. Conjugating the negative-frequency field yields the −m contribution, so one run supplies ±m.
- **If wrong**: one m = 0 Er source produces axisymmetric ring-dipole radiation, not the x-dipole cos²θ pattern. Linear polarization is not m = 0.

### ④ Simulation and boundaries — the axis is not an outer boundary

```python
mp.Simulation(resolution=RES_D, cell_size=mp.Vector3(SR_D + PML_D, 0, SZ_D + 2 * PML_D), dimensions=mp.CYLINDRICAL, m=m,
              boundary_layers=[mp.PML(thickness=PML_D)], sources=sources, force_complex_fields=True)
boundary_layers=[mp.PML(PML_DISC, direction=mp.R), mp.PML(PML_DISC, direction=mp.Z, side=mp.High)]   # D: no PML at the bottom -> ground plane
```

- **What**: specify `dimensions=mp.CYLINDRICAL` and `m`. PML goes at outer r and both z ends, never at r = 0. Part D omits bottom PML to make a ground plane.
- **Why**: nonzero m uses complex fields, with `force_complex_fields=True`. As in chapter 11, an external cell wall without PML supplies the PEC boundary here.
- **If wrong**: chapter 10’s `k_point` changed walls into periodic boundaries and removed a mirror. This cylindrical setup has no `k_point`, so its bottom wall remains a mirror.

### ⑤ Monitors — no near2far face is needed on the axis

```python
mp.FluxRegion(center=mp.Vector3(0.5 * sr, 0, 0.5 * sz), size=mp.Vector3(sr, 0, 0))                  # top
mp.FluxRegion(center=mp.Vector3(sr, 0, 0), size=mp.Vector3(0, 0, sz))                                 # outer r
mp.FluxRegion(center=mp.Vector3(0.5 * sr, 0, -0.5 * sz), size=mp.Vector3(sr, 0, 0), weight=-1.0)     # bottom (A, B only)
ff = sim.get_farfield(n2f, mp.Vector3(R_FF * math.sin(th), 0, R_FF * math.cos(th)), GREENCYL_TOL)
```

- **What**: A/B use top, outer, and bottom faces; D uses only top and outer faces because the bottom is a ground plane. Evaluate far fields at (r, z) points in the φ = 0 plane.
- **Why**: the axis requires no closing face. Rotating the cross-section yields top and bottom disks plus an enclosing cylinder. `GREENCYL_TOL` controls azimuthal integration tolerance.
- **If wrong**: an open bottom, as in D, omits equivalent currents beyond the outer-r boundary above the ground plane, producing the near–far discrepancy in §5.

### ⑥ Run — one calculation per m

```python
m = 0
while True:
    sim = dipole_sim(m, src); ...; sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Er, mp.Vector3(R_SRC), 1e-6))
    if m > 0 and P_m / P_max < POWER_DECAY:
        break
    m += 1
```

- **What**: increment m from 0 and repeat. Runs are independent and may be executed in parallel.
- **Why**: estimate the required order scale from $k r_0$. With r₀ = 0.5 µm and k = 2π/µm, $kr_0\approx3.1$; power falls rapidly from around m = 5.
- **If wrong**: the official stopping rule selects the first small m term. A distant point source or structured cell can have a rebound: the 10_sources Point Dipole CYL example at r = 3.5 µm rises from 0.5% at m = 32 to 38% at m = 41. Chapter 14 examines this.

### ⑦ Postprocessing — sum fields, then measure power

```python
e_tot += ep; h_tot += hp                         # +m term (exp(i m phi) = 1 at phi = 0)
if m > 0:
    e_tot += np.conj(em); h_tot += np.conj(hm)   # -m term from the negative-frequency run
pattern = radial_flux(e_tot, h_tot)              # |Re(E x H*)| on the far-field arc
P_m = total_flux(radial_flux(ep, hp))            # power of this m alone: decides when to stop
```

- **What**: sum fields over m at φ = 0, then calculate the Poynting pattern. Use individual m-term power to judge stopping.
- **Why**: summing fields retains interference in the directional pattern. Total azimuth-integrated power can also be summed as powers because m orders are orthogonal.
- **If wrong**: adding per-m powers for a directional pattern removes interference and yields an azimuthally averaged pattern. The x-dipole cos²θ pattern depends on interference.

> **Pitfall**: in this Meep version, cylindrical `get_array` and `get_dft_array` return (z, r) arrays (chapter 11). Transposing as for a 2D Cartesian plot flips the image. This script uses `orient_rz`, checking expected dimensions to orient the array.

</details>

<details markdown="1">
<summary>Original results, validation tables, troubleshooting, and further experiments</summary>

### Original §5 · Results

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/03_on_axis.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/03_on_axis.png' | relative_url }}" alt="Part A on-axis dipole patterns in the φ = 0 plane: z dipole from m = 0 and x dipole from half the sum of m = ±1 fields" loading="lazy"></a>
<figcaption markdown="span">Part A. On-axis dipole patterns in the φ = 0 plane (0° is +z). Left: z dipole, one m = 0 run. Right: x dipole, half the sum of m = +1 and −1 runs.</figcaption>
</figure>


| Dipole | m | Analytic pattern | Relative L2 |
|---|---|---|---|
| z, on axis | 0 | sin²θ | 0.43% |
| x, on axis | +1, −1 | cos²θ | 0.46% |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/04_off_axis.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/04_off_axis.png' | relative_url }}" alt="Part B off-axis x dipole: normalized per-m radiated power, partial-sum pattern errors, and final m = 0…8 pattern versus cos²θ" loading="lazy"></a>
<figcaption markdown="span">Part B. An x dipole at r₀ = 0.5 µm. Left: radiated power of each m term divided by the maximum. Center: pattern error after each added order. Right: the full m = 0…8 pattern compared with cos²θ.</figcaption>
</figure>


| m | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| $P_m/P_{\max}$ | 1.00 | 0.94 | 1.00 | 0.64 | 0.18 | 2.8e-2 | 2.8e-3 | 1.9e-4 | 9.5e-6 |
| Pattern error of the 0…m sum | 0.589 | 0.409 | 0.099 | 0.141 | 0.030 | 0.0087 | 0.0064 | 0.0064 | 0.0063 |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/05_ring_cyl.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/05_ring_cyl.png' | relative_url }}" alt="Part C: radial ring solutions per m and x-y fields reconstructed using azimuthal dependence" loading="lazy"></a>
<figcaption markdown="span">Part C. Chapter 12’s ring solved with one 1D radial run per m. Top: Ez(r) and the ring position (gray). Bottom: the x–y image reconstructed from Re[Ez(r)e^{imφ}], with 2m alternating-sign lobes.</figcaption>
</figure>


| m | f (cylindrical) | Q (cylindrical) | f (chapter 12 2D, res 20) | Q (chapter 12) | Δf/f |
|---|---|---|---|---|---|
| 3 | 0.11821 | 77 | 0.11818 | 79 | +0.02% |
| 4 | 0.14746 | 343 | 0.14736 | 342 | +0.07% |
| 5 | 0.17582 | 1627 | 0.17564 | 2132 | +0.10% |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/13/06_disc.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/13/06_disc.png' | relative_url }}" alt="Part D: disk far-field patterns for two cell sizes, near versus far integrated flux, and log magnitude Er in r-z" loading="lazy"></a>
<figcaption markdown="span">Part D. Left: far-field patterns of a disk above a ground plane for two cell sizes. Center: near-monitor flux and the far-hemisphere integral. Right: log&#124;Er&#124; in (r, z); the white rectangle is the disk.</figcaption>
</figure>


| Cell radius | Near flux | Far flux | Difference |
|---|---|---|---|
| 6 µm (official) | 643.65 | 595.80 | 7.43% (official documentation: 7.43%) |
| 8 µm | 643.28 | 602.05 | 6.41% |


### Compare with the predictions

| Quantity | Prediction (§2) | Simulation | Assessment |
|--------|-------------|-----------|------|
| z dipole vs sin²θ | Within 1% | 0.43% | Pass |
| x dipole (m = ±1) vs cos²θ | Within 1% | 0.46% | Pass |
| m needed at r₀ = 0.5 µm | 7~9 | 8 | Pass |
| Decrease in m-series error | Monotonic | Rises 0.099 → 0.141 from m = 2 → 3, then falls | Fail |
| ring-cyl vs chapter 12 frequency | Within 0.2% | 0.1% | Pass |
| ring-cyl Q(m = 5) vs chapter 12 | Similar | 1627 vs 2132 | Fail |
| Disk near vs far | 7% | 7.43% | Pass |
| Cell 6 → 8 µm | Smaller discrepancy | 6.41% | Pass |

Six of eight predictions held, and two failed. First, m-series error did not decrease monotonically. The m = 0…2 pattern (error 0.099) is closer to cos²θ than the sum including m = 3 (0.141). Partial sums do not approach the analytic pattern from one direction. The still-strong m = 3 term (power 0.64) temporarily changes the shape; m = 4 and 5 then bring it back. Thus an intermediate small pattern error is not a stopping criterion; inspect per-m power as well. Second, ring Q at m = 5 is 1627 in cylindrical coordinates and 2132 in chapter 12’s 2D res 20 calculation, a roughly 30% difference. That chapter gave 1675 at res 10 and 1610 at res 30. Cylindrical coordinates avoid a staircased circle and agree more closely with res 10 and 30; the outlying value is res 20. This is consistent with the staircase interpretation of nonmonotonic Q, but does not uniquely prove it. Frequencies agree within 0.1% for all three modes. The disk’s near–far discrepancy is 7.43% for a 6 µm cell, matching the documentation, and drops to 6.41% at 8 µm. This supports truncation of equivalent currents beyond the open surface above the ground plane. Near flux barely changes (643.65 → 643.28); the reduced discrepancy comes from increased far flux.

### Convergence

| Variable | Values | Result | Notes |
|---|---|---|---|
| B: included m | 0…4 / 0…5 / 0…8 | Errors 0.030 / 0.0087 / 0.0063 | After m = 6, resolution limits further improvement |
| C: coordinates | 2D Cartesian (chapter 12, res 10/20/30) vs cylindrical (res 20) | Q(m = 5) 1675/2132/1610 vs 1627 | Cylindrical geometry without a staircase is close to res 10 and 30 |
| D: cell radius | 6 / 8 µm | 7.43% / 6.41% | Size-dependent discrepancy supports truncation |

### What the results do and do not establish

- Established: in vacuum, on-axis dipole patterns agree within 0.5% using m = 0 (z) or m = ±1 (x). An x dipole 0.5 µm off-axis agrees to about 0.6% (measured 0.63%) with m = 0…8. Chapter 12’s ring frequencies agree between cylindrical and 2D Cartesian calculations within 0.1%. The disk near–far discrepancy decreases as radial extent increases, consistent with truncation.
- Not established: that the first m below 10⁻⁴ ends the series for a distant source or structured cell (chapter 14 provides a counterexample); the disk’s true total far-field power with an open surface; or staircase boundaries as the sole cause of Cartesian Q variation. This chapter shows consistency with that explanation, not a unique diagnosis.


### Original §6 · Common mistakes

| Symptom | Cause | Fix |
|------|------|----------|
| x-dipole pattern is axisymmetric | Only Er at m = 0 was used | Use m = +1 and −1, each with Er + (±i)Ep |
| Field diverges at the Er source | Source exactly at r = 0 (meep #2704) | Offset by 1.5/res |
| Error stays at 30% after summation | Missing −m term (conjugate −f field) | For m > 0, add conj(minus field) |
| Pattern has no interference | Added per-m powers | Sum fields for the pattern; use per-m power for stopping |
| 2D image is flipped | Cylindrical array order is (z, r) | Check orientation against expected dimensions |
| Disk near and far differ by 7% | Open near2far surface | Increase the cell and check that the discrepancy falls |
| Bottom mirror disappears | PML placed at the bottom | Omit PML on the ground-plane side |


### Original §7 · Try it yourself

| Change | Expected effect | Quantity to check |
|---------|----------|------------|
| B r₀ 0.5 → 1.5 µm | Required m roughly triples (proportional to kr₀) | Last m and any power rebound |
| B: y dipole (Ep) | Constant pattern in the sampled plane | Relative L2 against 1 |
| C: m = 2 | Outside 0.10~0.20, low Q | Harminv result |
| D: cell radius 12 µm | Smaller discrepancy | Near–far difference |
| D: disk thickness 0.7λ/n → 0.5λ/n | Changed lobes | Radiation pattern |

</details>

<details markdown="1">
<summary>Full code/cylindrical_dipole.py (expand)</summary>
{% highlight python %}
"""Meep Example 13 - Computing 3D with rotational symmetry: cylindrical coordinates and the m series.

Post 12's ring was a 2D cross-section. A real disc or ring is a body of revolution, and Meep's
dimensions=mp.CYLINDRICAL solves it as one 2D (r, z) run per azimuthal order m, with fields ~ exp(i m phi).
  A. On-axis dipoles in vacuum (official dipole_in_vacuum_cyl_on_axis.py): a z-dipole is m = 0 (Ez);
     an x-dipole is NOT m = 0 but the sum of m = +1 and m = -1 (Er + i Ep, Er - i Ep). Far-field
     patterns vs the analytic cos^2(theta) and sin^2(theta).
  B. An off-axis x-dipole at r = 0.5 um (official dipole_in_vacuum_cyl_off_axis.py): a point away from
     the axis is a Fourier series over m = 0, 1, 2, ... The series is summed until the power of the last
     m drops below 1e-4 of the largest; the pattern is checked after every added m.
  C. The ring of post 12 in cylindrical coordinates (official ring-cyl.py): one 1D radial run per m.
     Frequencies and Q compared with post 12's 2D Cartesian values; the m = 3 field rebuilt in the
     x-y plane from Ez(r) exp(i m phi).
  D. A dielectric disc on a ground plane (official disc_radiation_pattern.py): a ring source (m = -1),
     near flux vs far-field flux; the 7 % gap comes from the open near2far surface, checked by
     enlarging the radial cell.
MPI-safe: collective calls on every rank, figures on the master only.

Run:  mpirun -np 4 python cylindrical_dipole.py     (~6 min)
Out:  00_source.png, 01_layout.png, 02_layout_dipole.png, 03_on_axis.png, 04_off_axis.png, 05_ring_cyl.png,
      06_disc.png, 07_anim_m3.gif, result.json   (-> ../assets/13/)
"""
import cmath
import json
import math
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
from blogfig import Label, annotated_layout, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "13")
os.makedirs(OUT, exist_ok=True)
MASTER = mp.am_master()
t_all = time.time()


def say(*a):
    if MASTER:
        print(*a, flush=True)


def rel_l2(a, b):
    return float(np.linalg.norm(np.asarray(a) - np.asarray(b)) / np.linalg.norm(np.asarray(b)))


def orient_rz(arr, nr):
    """Cylindrical get_array/get_dft_array return (z, r) in this Meep version; return (r, z) whatever the order."""
    arr = np.asarray(arr)
    if arr.ndim == 2 and abs(arr.shape[1] - nr) < abs(arr.shape[0] - nr):
        return arr.T
    return arr


# ---------------------------------------------------------------- (1) parameters shared by A and B (official values, um)
WL = 1.0
FREQ = 1 / WL
RES_D = 50
PML_D = 1.0
SR_D, SZ_D = 2.0, 4.0                       # near2far box: r 0..2, z -2..2
R_FF = 1e6 * WL
NPTS = 50
THETA = np.linspace(0, 0.5 * np.pi, NPTS)   # 0 = +z (pole), pi/2 = +r (equator), in the phi = 0 plane
GREENCYL_TOL = 1e-6
POWER_DECAY = 1e-4


def n2f_regions(sr, sz):
    return [mp.FluxRegion(center=mp.Vector3(0.5 * sr, 0, 0.5 * sz), size=mp.Vector3(sr, 0, 0)),
            mp.FluxRegion(center=mp.Vector3(sr, 0, 0), size=mp.Vector3(0, 0, sz)),
            mp.FluxRegion(center=mp.Vector3(0.5 * sr, 0, -0.5 * sz), size=mp.Vector3(sr, 0, 0), weight=-1.0)]


def farfields(sim, n2f, tol=GREENCYL_TOL, theta=THETA, r_ff=R_FF):
    e = np.zeros((len(theta), 3), complex); h = np.zeros((len(theta), 3), complex)
    for n, th in enumerate(theta):
        ff = sim.get_farfield(n2f, mp.Vector3(r_ff * math.sin(th), 0, r_ff * math.cos(th)), tol)
        e[n] = ff[:3]; h[n] = ff[3:]
    return e, h


def radial_flux(e, h):
    fx = np.real(e[:, 1] * np.conj(h[:, 2]) - e[:, 2] * np.conj(h[:, 1]))
    fz = np.real(e[:, 0] * np.conj(h[:, 1]) - e[:, 1] * np.conj(h[:, 0]))
    return np.sqrt(fx ** 2 + fz ** 2)


def total_flux(pattern, theta=THETA, r_ff=R_FF):
    return float(2 * np.pi * r_ff ** 2 * np.trapezoid(pattern * np.sin(theta), theta))


def dipole_sim(m, sources):
    return mp.Simulation(resolution=RES_D, cell_size=mp.Vector3(SR_D + PML_D, 0, SZ_D + 2 * PML_D), dimensions=mp.CYLINDRICAL, m=m,
                         boundary_layers=[mp.PML(thickness=PML_D)], sources=sources, force_complex_fields=True)


# ================================================================ A. on-axis dipoles
t_a = time.time()
r_off = 1.5 / RES_D                          # an Er source exactly at r = 0 hits a known bug (meep issue 2704): offset by 1.5 px
gs = lambda f: mp.GaussianSource(f, fwidth=0.1 * abs(f))
on = {}
# z-dipole: m = 0, Ez on the axis
sim = dipole_sim(0, [mp.Source(gs(FREQ), component=mp.Ez, center=mp.Vector3())])
annotated_layout(sim, os.path.join(OUT, "02_layout_dipole.png"), dpml=PML_D, figsize=(5.4, 7.6), axis_step=1.0, unit="um",
                 title="parts A, B: cylindrical (r, z) cell; r = 0 is the left edge (the axis)",
                 params_text=f"wl={WL} um, res={RES_D}\nm = 0, +-1 (A)\nm = 0..8 (B)", params_xy=(0.15, 3.75), pml_xy=(0.15, -3.5), decay_point=None,
                 labels=[Label("dipole on the axis (A) or at r = 0.5 (B)", (0.03, 0.0), (0.4, 0.9), step=3, color="red"),
                         Label("near2far: top, outer r, bottom (weight -1)", (2.0, 1.0), (0.4, 2.6), step=5, color="blue"),
                         Label("vacuum: no geometry", (1.0, -1.0), (0.4, -1.4), step=2, color="black")])
n2f = sim.add_near2far(FREQ, 0, 1, *n2f_regions(SR_D, SZ_D))
sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Ez, mp.Vector3(), 1e-6))
on["z"] = farfields(sim, n2f); sim.reset_meep()
# x-dipole: m = +1 and m = -1, each Er + (+-i) Ep, combined with weight 1/2 and exp(+-i phi) at phi = 0
ex = np.zeros((NPTS, 3), complex); hx = np.zeros((NPTS, 3), complex)
for m in (+1, -1):
    src = [mp.Source(gs(FREQ), component=mp.Er, center=mp.Vector3(r_off)),
           mp.Source(gs(FREQ), component=mp.Ep, center=mp.Vector3(r_off), amplitude=1j if m == 1 else -1j)]
    sim = dipole_sim(m, src)
    n2f = sim.add_near2far(FREQ, 0, 1, *n2f_regions(SR_D, SZ_D))
    sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Er, mp.Vector3(r_off), 1e-6))
    e, h = farfields(sim, n2f); sim.reset_meep()
    ex += 0.5 * e; hx += 0.5 * h
on["x"] = (ex, hx)
pat_on = {k: radial_flux(*v) for k, v in on.items()}
an_on = {"x": np.cos(THETA) ** 2, "z": np.sin(THETA) ** 2}
err_on = {k: rel_l2(pat_on[k] / pat_on[k].max(), an_on[k]) for k in on}
say(f"A: on-axis z-dipole (m = 0) vs sin^2: rel L2 {err_on['z']:.4f}; x-dipole (m = +1 and -1) vs cos^2: {err_on['x']:.4f}; {time.time() - t_a:.0f} s")
if MASTER:
    source_figure(FREQ, 0.1 * FREQ, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ B. off-axis x-dipole: the m series
t_b = time.time()
R_SRC = 0.5
e_tot = np.zeros((NPTS, 3), complex); h_tot = np.zeros((NPTS, 3), complex)
m_flux, m_err, flux_max = [], [], 0.0
m = 0
while True:
    src = [mp.Source(gs(FREQ), component=mp.Er, center=mp.Vector3(R_SRC)),
           mp.Source(gs(-FREQ), component=mp.Er, center=mp.Vector3(R_SRC))]          # +f gives the +m term, -f the -m term (conjugated)
    sim = dipole_sim(m, src)
    n2p = sim.add_near2far(FREQ, 0, 1, *n2f_regions(SR_D, SZ_D))
    n2m = sim.add_near2far(-FREQ, 0, 1, *n2f_regions(SR_D, SZ_D))
    sim.run(until_after_sources=mp.stop_when_fields_decayed(20, mp.Er, mp.Vector3(R_SRC), 1e-6))
    ep, hp = farfields(sim, n2p); em, hm = farfields(sim, n2m); sim.reset_meep()
    e_tot += ep; h_tot += hp                                   # exp(i m phi) = 1 at phi = 0
    if m > 0:
        e_tot += np.conj(em); h_tot += np.conj(hm)
    fl = total_flux(radial_flux(ep, hp))
    flux_max = max(flux_max, fl)
    p = radial_flux(e_tot, h_tot)
    m_flux.append(fl); m_err.append(rel_l2(p / p.max(), np.cos(THETA) ** 2))
    say(f"B: m = {m}: power of this m / max = {fl / flux_max:.2e}; pattern error after summing 0..{m}: {m_err[-1]:.4f}")
    if m > 0 and fl / flux_max < POWER_DECAY:
        break
    m += 1
pat_off = radial_flux(e_tot, h_tot)
say(f"B: off-axis x-dipole at r = {R_SRC}: stopped at m = {m}; final rel L2 vs cos^2 {m_err[-1]:.4f}; {time.time() - t_b:.0f} s")

# ================================================================ C. post 12's ring in cylindrical coordinates
t_c = time.time()
N_RING, W, R_IN, PAD, DPML_R = 3.4, 1.0, 1.0, 4.0, 32.0
SR_R = R_IN + W + PAD + DPML_R
RES_R = 20
FC, DFC = 0.15, 0.1
POST12 = {3: (0.11818, 79), 4: (0.14736, 342), 5: (0.17564, 2132)}     # 2D Cartesian, res 20 (post 12)
ring = {}


def ring_sim(m, f, df):
    return mp.Simulation(cell_size=mp.Vector3(SR_R, 0, 0), resolution=RES_R, dimensions=mp.CYLINDRICAL, m=m, boundary_layers=[mp.PML(DPML_R)],
                         geometry=[mp.Block(center=mp.Vector3(R_IN + 0.5 * W), size=mp.Vector3(W, mp.inf, mp.inf), material=mp.Medium(index=N_RING))],
                         sources=[mp.Source(mp.GaussianSource(f, fwidth=df), component=mp.Ez, center=mp.Vector3(R_IN + 0.1))])


for mm in (3, 4, 5):
    sim = ring_sim(mm, FC, DFC)
    hv = mp.Harminv(mp.Ez, mp.Vector3(R_IN + 0.1), FC, DFC)
    sim.run(mp.after_sources(hv), until_after_sources=200)
    modes = [md for md in hv.modes if md.Q > 0 and FC - 0.5 * DFC < md.freq < FC + 0.5 * DFC]
    md = max(modes, key=lambda x: abs(x.amp)); sim.reset_meep()
    f, Q = float(md.freq), float(md.Q)
    sim = ring_sim(mm, f, 0.01)
    dft = sim.add_dft_fields([mp.Ez], f, 0, 1, center=mp.Vector3(0.5 * (R_IN + W + PAD)), size=mp.Vector3(R_IN + W + PAD))
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(R_IN + 0.1), 1e-6))
    ezr = np.squeeze(sim.get_dft_array(dft, mp.Ez, 0)); sim.reset_meep()
    ring[mm] = {"f": f, "Q": Q, "ez_r": ezr}
    say(f"C: m = {mm}: cylindrical f {f:.5f} Q {Q:.0f} | post 12 (2D, res 20): f {POST12[mm][0]:.5f} Q {POST12[mm][1]} -> df/f {(f - POST12[mm][0]) / POST12[mm][0]:+.2e}")
say(f"C done in {time.time() - t_c:.0f} s")

# ================================================================ D. disc on a ground plane, near vs far flux
t_d = time.time()
RES_DISC, PML_DISC, AIR = 100, 0.5, 1.0
DISC_R, N_DISC = 1.2, 2.4
DISC_T = 0.7 * WL / N_DISC
NPOL = 100
THETA_D = np.linspace(0, 0.5 * np.pi, NPOL)
disc = {}
for cell_r in (6.0, 8.0):
    sr = cell_r + PML_DISC; sz = DISC_T + AIR + PML_DISC
    src_pt = mp.Vector3(0.5 * DISC_R, 0, -0.5 * sz + 0.5 * DISC_T)
    sim = mp.Simulation(resolution=RES_DISC, cell_size=mp.Vector3(sr, 0, sz), dimensions=mp.CYLINDRICAL, m=-1,
                        boundary_layers=[mp.PML(PML_DISC, direction=mp.R), mp.PML(PML_DISC, direction=mp.Z, side=mp.High)],   # no PML at the bottom: PEC ground plane
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.1 * FREQ), component=mp.Er, center=src_pt)],
                        geometry=[mp.Block(material=mp.Medium(index=N_DISC), center=mp.Vector3(0.5 * DISC_R, 0, -0.5 * sz + 0.5 * DISC_T), size=mp.Vector3(DISC_R, mp.inf, DISC_T))])
    regs = [mp.FluxRegion(center=mp.Vector3(0.5 * cell_r, 0, 0.5 * sz - PML_DISC), size=mp.Vector3(cell_r, 0, 0)),
            mp.FluxRegion(center=mp.Vector3(cell_r, 0, 0.5 * sz - PML_DISC - 0.5 * (AIR + DISC_T)), size=mp.Vector3(0, 0, AIR + DISC_T))]
    flux = sim.add_flux(FREQ, 0, 1, *regs)
    n2f = sim.add_near2far(FREQ, 0, 1, *regs)
    dft = None
    if cell_r == 6.0:
        dft = sim.add_dft_fields([mp.Er], FREQ, 0, 1, center=mp.Vector3(0.5 * cell_r, 0, -0.5 * PML_DISC), size=mp.Vector3(cell_r, 0, sz - PML_DISC))
        annotated_layout(sim, os.path.join(OUT, "01_layout.png"), dpml=PML_DISC, figsize=(11, 3.8), axis_step=1.0, unit="um",
                         title="part D: disc (n = 2.4, R = 1.2 um) on a ground plane, cylindrical (r, z); bottom edge = PEC (no PML)",
                         params_text=f"wl={WL} um, res={RES_DISC}\nm = -1, t = {DISC_T:.3f} um", params_xy=(3.4, 0.33), pml_xy=(6.05, -0.6),
                         decay_point=(src_pt.x, src_pt.z), decay_text_xy=(1.5, -0.45),
                         labels=[Label("disc", (0.9, src_pt.z + 0.05), (1.5, -0.2), step=2, color="black"),
                                 Label("Er ring source at r = 0.6", (src_pt.x, src_pt.z), (1.5, 0.05), step=3, color="red"),
                                 Label("flux + near2far: top and outer r (open at the bottom)", (5.0, 0.5 * sz - PML_DISC), (3.4, -0.2), step=5, color="blue")])
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Er, src_pt, 1e-8))
    f_near = float(mp.get_fluxes(flux)[0])
    e, h = farfields(sim, n2f, tol=1e-8, theta=THETA_D)
    pat = radial_flux(e, h)
    f_far = total_flux(pat, theta=THETA_D)
    er = orient_rz(sim.get_dft_array(dft, mp.Er, 0), int(round(cell_r * RES_DISC))) if dft is not None else None
    sim.reset_meep()
    disc[cell_r] = {"near": f_near, "far": f_far, "gap": abs(f_near - f_far) / f_near, "pattern": pat, "er": er, "sz": sz}
    say(f"D: cell r {cell_r}: near flux {f_near:.4f}, far flux {f_far:.4f}, gap {100 * disc[cell_r]['gap']:.2f} %")
say(f"D done in {time.time() - t_d:.0f} s")

# ================================================================ figures (master only)
if MASTER:
    # A
    fig, ax = plt.subplots(1, 2, figsize=(10, 4.6), subplot_kw={"projection": "polar"})
    for a, k, lab in ((ax[0], "z", "z-dipole: m = 0 (Ez)  vs sin^2"), (ax[1], "x", "x-dipole: m = +1 and m = -1  vs cos^2")):
        a.plot(THETA, pat_on[k] / pat_on[k].max(), "b-", lw=1.6, label="Meep (cylindrical)")
        a.plot(THETA, an_on[k], "r--", lw=1.2, label="analytic")
        a.set_theta_zero_location("N"); a.set_theta_direction(-1); a.set_thetamin(0); a.set_thetamax(90); a.set_rmax(1.05)
        a.set_title(f"{lab}\nrel L2 {err_on[k]:.4f}", fontsize=9); a.legend(fontsize=7, loc="lower left")
    fig.suptitle("part A: on-axis dipoles (angle from +z, phi = 0 plane). A linearly polarized in-plane dipole is two m runs", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_on_axis.png"), dpi=150); plt.close(fig)
    # B
    fig = plt.figure(figsize=(13, 4.4))
    ax = fig.add_subplot(1, 3, 1)
    ms = np.arange(len(m_flux))
    ax.semilogy(ms, np.array(m_flux) / max(m_flux), "o-", color="tab:blue"); ax.axhline(POWER_DECAY, color="crimson", ls="--", lw=1, label="stop: 1e-4 of the max")
    ax.set_xlabel("azimuthal order m"); ax.set_ylabel("far-field power of the m term / max"); ax.set_title(f"dipole at r = {R_SRC} um: how much each m radiates", fontsize=9); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=8)
    ax = fig.add_subplot(1, 3, 2)
    ax.semilogy(ms, m_err, "s-", color="tab:green"); ax.set_xlabel("m included up to"); ax.set_ylabel("rel L2 of the summed pattern vs cos^2"); ax.set_title("the pattern converges as m terms are added", fontsize=9); ax.grid(alpha=0.3, which="both")
    ax = fig.add_subplot(1, 3, 3, projection="polar")
    ax.plot(THETA, pat_off / pat_off.max(), "b-", lw=1.6, label=f"Meep, m = 0..{m}"); ax.plot(THETA, np.cos(THETA) ** 2, "r--", lw=1.2, label="cos^2")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.set_rmax(1.05); ax.legend(fontsize=7, loc="lower left")
    ax.set_title(f"off-axis x-dipole: rel L2 {m_err[-1]:.4f}", fontsize=9)
    fig.suptitle("part B: a point away from the axis is a Fourier series over m; each m is one 2D (r, z) run", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_off_axis.png"), dpi=150); plt.close(fig)
    # C: Ez(r) and the x-y reconstruction for m = 3, 4, 5
    rr = np.linspace(0, R_IN + W + PAD, len(ring[3]["ez_r"]))
    L = R_IN + W + 1.5
    xg = np.linspace(-L, L, 301); X, Y = np.meshgrid(xg, xg, indexing="ij"); RG = np.hypot(X, Y); PH = np.arctan2(Y, X)
    fig, ax = plt.subplots(2, 3, figsize=(12.5, 7.8), gridspec_kw={"height_ratios": [1, 1.5]})
    for k, mm in enumerate((3, 4, 5)):
        d = ring[mm]; ez = d["ez_r"] / np.max(np.abs(d["ez_r"]))
        ax[0, k].plot(rr, np.real(ez), "b-", label="Re"); ax[0, k].plot(rr, np.abs(ez), "k-", lw=0.8, label="|Ez|")
        ax[0, k].axvspan(R_IN, R_IN + W, color="gray", alpha=0.25); ax[0, k].set_xlabel("r [a]"); ax[0, k].set_title(f"m = {mm}: f = {d['f']:.4f}, Q = {d['Q']:.0f} (one 1D radial run)", fontsize=9)
        ax[0, k].grid(alpha=0.3); ax[0, k].legend(fontsize=7)
        field = np.real(np.interp(RG, rr, np.real(ez)) * np.cos(mm * PH) - np.interp(RG, rr, np.imag(ez)) * np.sin(mm * PH))
        field[RG > rr[-1]] = 0
        lim = np.max(np.abs(field))
        ax[1, k].imshow(field.T, extent=[-L, L, -L, L], origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
        for rc in (R_IN, R_IN + W):
            ax[1, k].add_patch(plt.Circle((0, 0), rc, fill=False, color="k", lw=0.8))
        ax[1, k].set_title(f"Re[Ez(r) exp(i {mm} phi)]: {2 * mm} sign lobes; post 12: f {POST12[mm][0]:.4f}", fontsize=9); ax[1, k].set_xlabel("x [a]")
    ax[1, 0].set_ylabel("y [a]")
    fig.suptitle("part C: post 12's ring as one radial run per m; the 2D picture is rebuilt from exp(i m phi)", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_ring_cyl.png"), dpi=150); plt.close(fig)
    # D
    fig = plt.figure(figsize=(13.5, 4.4))
    ax = fig.add_subplot(1, 3, 1, projection="polar")
    for cr, c in ((6.0, "tab:blue"), (8.0, "tab:orange")):
        p = disc[cr]["pattern"]; ax.plot(THETA_D, p / disc[6.0]["pattern"].max(), "-", color=c, lw=1.4, label=f"cell r {cr:.0f} um")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(90); ax.legend(fontsize=7, loc="lower left")
    ax.set_title("disc on a ground plane: far-field pattern", fontsize=9)
    ax = fig.add_subplot(1, 3, 2)
    idx = np.arange(2)
    ax.bar(idx - 0.2, [disc[c]["near"] for c in (6.0, 8.0)], width=0.4, color="tab:gray", label="near flux (monitor)")
    ax.bar(idx + 0.2, [disc[c]["far"] for c in (6.0, 8.0)], width=0.4, color="tab:blue", label="far flux (hemisphere integral)")
    for k, c in enumerate((6.0, 8.0)):
        ax.text(k, max(disc[c]["near"], disc[c]["far"]) * 1.02, f"gap {100 * disc[c]['gap']:.2f} %", ha="center", fontsize=8)
    ax.set_xticks(idx); ax.set_xticklabels(["cell r 6 um", "cell r 8 um"]); ax.set_ylabel("power (a.u.)"); ax.set_title("the open near2far surface misses currents on the ground plane", fontsize=9); ax.legend(fontsize=7, loc="lower right")
    ax = fig.add_subplot(1, 3, 3)
    er = disc[6.0]["er"]; sz = disc[6.0]["sz"]
    ax.imshow(np.log10(np.abs(er) + 1e-12).T, extent=[0, 6.0, -0.5 * sz, 0.5 * sz - PML_DISC], origin="lower", cmap="inferno", aspect="auto")
    ax.add_patch(plt.Rectangle((0, -0.5 * sz), DISC_R, DISC_T, fill=False, color="w", lw=1))
    ax.set_xlabel("r [um]"); ax.set_ylabel("z [um]"); ax.set_title("log10 |Er| at 1 um (r, z plane)", fontsize=9)
    fig.suptitle("part D: near vs far flux; the gap shrinks when the radial cell grows", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "06_disc.png"), dpi=150); plt.close(fig)
    # GIF: m = 3 mode rotating: Re[Ez(r) exp(i (3 phi - w t))]
    d = ring[3]; ez = d["ez_r"] / np.max(np.abs(d["ez_r"]))
    Er_ = np.interp(RG, rr, np.real(ez)); Ei_ = np.interp(RG, rr, np.imag(ez)); amp = np.where(RG > rr[-1], 0, 1)
    fig_g, ax_g = plt.subplots(figsize=(4.8, 4.4))
    im = ax_g.imshow(np.zeros_like(RG).T, extent=[-L, L, -L, L], origin="lower", cmap="RdBu", vmin=-1, vmax=1, aspect="equal")
    for rc in (R_IN, R_IN + W):
        ax_g.add_patch(plt.Circle((0, 0), rc, fill=False, color="k", lw=0.8))
    ax_g.set_xlabel("x [a]"); ax_g.set_ylabel("y [a]"); ttl = ax_g.set_title("", fontsize=9); fig_g.tight_layout()
    NF = 36

    def upd(i):
        wt = 2 * np.pi * i / NF
        fld = amp * (Er_ * np.cos(3 * PH - wt) - Ei_ * np.sin(3 * PH - wt))
        im.set_data((fld / np.max(np.abs(fld))).T); ttl.set_text(f"m = 3 mode, Re[Ez(r) exp(i(3 phi - wt))], wt = {np.degrees(wt):.0f} deg")
        return im, ttl

    animation.FuncAnimation(fig_g, upd, frames=NF, blit=False).save(os.path.join(OUT, "07_anim_m3.gif"), writer=animation.PillowWriter(fps=12), dpi=75)
    plt.close(fig_g)
    with open(os.path.join(OUT, "result.json"), "w") as f_:
        json.dump({"A": {"err_z": err_on["z"], "err_x": err_on["x"]},
                   "B": {"r_src": R_SRC, "m_last": m, "m_flux_rel": (np.array(m_flux) / max(m_flux)).tolist(), "m_err": m_err},
                   "C": {str(k): {"f": v["f"], "Q": v["Q"], "post12_f": POST12[k][0], "post12_Q": POST12[k][1]} for k, v in ring.items()},
                   "D": {str(k): {"near": v["near"], "far": v["far"], "gap": v["gap"]} for k, v in disc.items()},
                   "wall_s_total": time.time() - t_all, "np": mp.count_processors(), "meep": mp.__version__}, f_, indent=2)
say(f"total {time.time() - t_all:.0f} s on {mp.count_processors()} process(es)")
{% endhighlight %}
</details>
<details markdown="1">
<summary>Original execution record and environment</summary>

Unlike the excerpts in §4, the full code includes two layouts, m-series convergence plots, x–y reconstruction of ring modes, disk fields, a GIF, and result.json output. For MPI, collective calls (run, get_farfield, get_dft_array) execute on every rank, while figures are saved only on the master. Full code and helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**Execution output (run on 2026-10-23, mpirun -np 4)**:
```
A: on-axis z-dipole (m = 0) vs sin^2: rel L2 0.0043; x-dipole (m = +1 and -1) vs cos^2: 0.0046; 53 s
B: m = 0: power of this m / max = 1.00e+00; pattern error after summing 0..0: 0.5890
B: m = 1: power of this m / max = 9.36e-01; pattern error after summing 0..1: 0.4094
B: m = 2: power of this m / max = 1.00e+00; pattern error after summing 0..2: 0.0987
B: m = 3: power of this m / max = 6.36e-01; pattern error after summing 0..3: 0.1405
B: m = 4: power of this m / max = 1.80e-01; pattern error after summing 0..4: 0.0298
B: m = 5: power of this m / max = 2.79e-02; pattern error after summing 0..5: 0.0087
B: m = 6: power of this m / max = 2.78e-03; pattern error after summing 0..6: 0.0064
B: m = 7: power of this m / max = 1.90e-04; pattern error after summing 0..7: 0.0064
B: m = 8: power of this m / max = 9.49e-06; pattern error after summing 0..8: 0.0063
B: off-axis x-dipole at r = 0.5: stopped at m = 8; final rel L2 vs cos^2 0.0063; 139 s
C: m = 3: cylindrical f 0.11821 Q 77 | post 12 (2D, res 20): f 0.11818 Q 79 -> df/f +2.30e-04
C: m = 4: cylindrical f 0.14746 Q 343 | post 12 (2D, res 20): f 0.14736 Q 342 -> df/f +6.62e-04
C: m = 5: cylindrical f 0.17582 Q 1627 | post 12 (2D, res 20): f 0.17564 Q 2132 -> df/f +1.02e-03
D: cell r 6.0: near flux 643.6506, far flux 595.8024, gap 7.43 %
D: cell r 8.0: near flux 643.2784, far flux 602.0512, gap 6.41 %
total 457 s on 4 process(es)
```

**Reproduction environment**: meep 1.33.0 (MPI) · Python 3.11 · `conda install -c conda-forge pymeep=*=mpi_mpich_*` · command `mpirun -np 4 python cylindrical_dipole.py` (about 7.6 min (mpirun -np 4))

</details>

### Official documentation and the next chapter

- [Cylindrical coordinates tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/) · [Antenna in cylindrical coordinates](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-an-antenna-in-cylindrical-coordinates) · [Disk in cylindrical coordinates](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-a-disc-in-cylindrical-coordinates)
- Scripts: [dipole_in_vacuum_cyl_on_axis.py](https://github.com/NanoComp/meep/blob/master/python/examples/dipole_in_vacuum_cyl_on_axis.py) · [dipole_in_vacuum_cyl_off_axis.py](https://github.com/NanoComp/meep/blob/master/python/examples/dipole_in_vacuum_cyl_off_axis.py) · [ring-cyl.py](https://github.com/NanoComp/meep/blob/master/python/examples/ring-cyl.py) · [disc_radiation_pattern.py](https://github.com/NanoComp/meep/blob/master/python/examples/disc_radiation_pattern.py) · [meep issue 2704 (Er at r = 0)](https://github.com/NanoComp/meep/issues/2704)
- Previous: [12 · A ring that confines light]({{ site.baseurl }}/en/ring-resonator/) · near2far and mirrors: [10 · 3D radiation patterns of a point source]({{ site.baseurl }}/en/dipole-pattern-3d/) · Next: 14 · A point source in a thin film: the fraction escaping into air
