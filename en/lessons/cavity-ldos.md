---
layout: lesson
permalink: /en/cavity-ldos/
lesson_title: "How does the amount of light change between two mirrors?"
lesson_summary: "Compare the LDOS of the same dipole with and without mirrors. Interpret the Purcell factor, modal cutoffs, and the runtime limits of high-Q calculations."
lesson_goals:
  - "Calculate the Purcell factor from cavity and bulk runs with the same source."
  - "Interpret planar-cavity cutoffs and results in two coordinate systems."
  - "Distinguish Q and LDOS in a 2D box from unconverged results."
lesson_prerequisites: "Chapter 01: point sources · Chapter 10: PEC and image dipoles"
date: 2026-10-23
title: "Meep Example 11 · A point source between two mirrors — LDOS and the Purcell factor"
title_en: "Meep Example 11 · A point source between two mirrors — the local density of states and the Purcell factor"
lang: en
translation_key: cavity-ldos
series: meep-examples
part: 11
level: intermediate
runtime: "6.6 min (single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/"
tags: [meep, fdtd, ldos, purcell, cavity, harminv, dft_ldos, cylindrical]
image: /assets/meep/11/03_purcell.png
excerpt: "post 10 put one mirror next to a dipole and the pattern changed. Here the dipole sits between two mirrors and the question is the emitted power itself. Meep measures it as the local density of states (LDOS) at the source point with `dft_ldos`. Part A: an in-plane dipole in a dielectric slab (n = 2.4) between two lossless metallic mirrors, the Purcell factor F = LDOS(cavity)/LDOS(bulk) versus the normalized thickness t = nL/λ, swept in cylindrical coordinates and checked in 3D. Part B: a dipole in a 2D metal box with one aperture, where the LDOS at resonance is compared with the single-mode estimate 2Q/(πωV)."
---

<h2 id="observe">1. Observe: can mirrors change the amount of light?</h2>

In chapter 10, one mirror changed the direction of emitted light. Here we ask **how much the emitted power changes when the same dipole is placed between two mirrors**. The Purcell factor is the LDOS measured at the source divided by the LDOS in bulk material without the mirrors.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/03_purcell.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/03_purcell.png' | relative_url }}" alt="Measured Purcell factor versus mirror spacing, compared with the analytic expression, cylindrical simulations, and 3D simulations"></a>
<figcaption>Actual results from part A. The horizontal axis is normalized thickness t = nL/λ. Across 18 points excluding the three cutoffs, the error relative to the analytic expression has a median of 0.94% and a maximum of 3.6%.</figcaption>
</figure>

<p class="lesson-note"><strong>Distinguish the quantities in the two experiments.</strong> Part A calculates the bulk-normalized Purcell factor between lossless planar mirrors. Part B compares raw LDOS in a 2D PEC box with an aperture against a Q/V approximation. The numbers in part B are not validated 3D Purcell factors.</p>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/06_anim_planar.gif' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/06_anim_planar.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/11/06_anim_planar.gif' | relative_url }}" data-static-src="{{ '/assets/meep/11/04_cavity_field.png' | relative_url }}" alt="Actual cylindrical Er pulse spreading radially between two planar mirrors"></a>
<button type="button" class="animation-toggle" hidden>Pause animation</button>
<figcaption>A pulse at t = 1.0 in part A. The two black lines are mirrors; the horizontal axis is r and the vertical axis is z. The z axis is stretched for readability, so this is not a 3D scene drawn to scale.</figcaption>
</figure>

<h2 id="predict">2. Predict: do mirrors always make emission brighter?</h2>

<fieldset class="prediction">
<legend>Is the Purcell factor always greater than 1 when the same source is placed between two mirrors?</legend>
<label><input type="radio" name="cavity-prediction" value="always"> It is always greater than 1 because the light is confined.</label>
<label><input type="radio" name="cavity-prediction" value="modes"> It can be less than 1, depending on the spacing and available modes.</label>
</fieldset>

<details markdown="1">
<summary>Compare your prediction with the result</summary>

The second answer is correct. At t = 1.0, the cylindrical result is **0.912**, the 3D result is **0.933**, and the analytic result is **0.9375**. All are below 1. Mirrors change the modes available to the source and can either enhance or suppress emission.

</details>

<h2 id="understand">3. Understand: why measure twice with the same source?</h2>

{% include chapter-illustration.html %}

A dipole interacts with the field it creates. When a reflected field changes the response at the source, the power emitted by a current of the same amplitude also changes. <code>dft_ldos</code> obtains this response from the frequency components of the field and current at the source.

<figure class="lesson-figure">
<svg viewBox="0 0 320 210" role="img" aria-labelledby="cavity-concept-title" xmlns="http://www.w3.org/2000/svg">
<title id="cavity-concept-title">Conceptual diagram: calculate the same source in bulk and between mirrors, then take the LDOS ratio</title>
<rect width="320" height="210" fill="#f5f8fa" />
<g font-family="sans-serif" font-size="16" fill="#0d1b2a">
<text x="26" y="29">① bulk</text><text x="176" y="29">② cavity</text>
<text x="27" y="155">Same source</text><text x="183" y="155">Spacing L</text>
<text x="25" y="193">Purcell factor = LDOS② / LDOS①</text>
</g>
<rect x="21" y="42" width="117" height="90" fill="#e7f7fb" stroke="#dce5eb" />
<rect x="176" y="42" width="119" height="90" fill="#e7f7fb" />
<path d="M176 43H295M176 131H295" stroke="#0d1b2a" stroke-width="6" />
<circle cx="79" cy="87" r="7" fill="#0087ad" /><circle cx="235" cy="87" r="7" fill="#0087ad" />
<path d="M56 87H102M212 87H258M56 87l8-5M56 87l8 5M102 87l-8-5M102 87l-8 5M212 87l8-5M212 87l8 5M258 87l-8-5M258 87l-8 5" fill="none" stroke="#0087ad" stroke-width="2" />
</svg>
<figcaption>Conceptual diagram. Black lines are lossless PEC mirrors; teal dots and horizontal arrows represent a dipole parallel to the mirrors. Both runs use the same medium and source representation. The diagram does not show measured field values.</figcaption>
</figure>

Taking **F_P = LDOS(cavity) / LDOS(bulk)** cancels the common source, coordinate-system, and grid normalization factors. Cylindrical and 3D results must each be divided by their own bulk run.

Read the mirror spacing as **t = nL/λ**, measured in wavelengths inside the medium. For this planar cavity and in-plane dipole, a new mode opens when t passes 0.5, 1.5, and 2.5, producing discontinuous jumps in the analytic expression. These are cutoffs. Do not combine finite-grid, finite-time cutoff values with smooth-region error statistics.

<p class="lesson-note"><strong>Planar-cavity assumptions.</strong> Wavelength 1 µm, refractive index 2.4, and lossless material and PEC mirrors. The in-plane dipole is represented by Er with m = −1 in cylindrical coordinates and Ex in 3D. There is no PML in the mirror-normal z direction; only waves leaving laterally are absorbed. This procedure cannot be transferred directly to point-source LDOS in a lossy medium.</p>

In part B, an aperture of width w is cut in a 1 × 1 µm 2D PEC box. A narrower aperture reduces leakage, increases Q, and requires a longer run to measure LDOS near resonance. This example uses **2Q/f** as the runtime criterion, with a cap of 6000.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/07_anim_metal.gif' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/07_anim_metal.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/11/07_anim_metal.gif' | relative_url }}" data-static-src="{{ '/assets/meep/11/05_metal_ldos.png' | relative_url }}" alt="Ez pulse resonating inside a 2D PEC box and leaking through an aperture 0.4 micrometers wide"></a>
<button type="button" class="animation-toggle" hidden>Pause animation</button>
<figcaption>Actual pulse in part B at w = 0.4 µm. The field oscillates inside the box and exits through the aperture on the right. This is a separate 2D experiment from the planar-cavity Purcell sweep.</figcaption>
</figure>

<h2 id="run">4. Run it: observe a high-Q cavity for longer</h2>

Use Meep 1.33.0 with the original script and shared helper in the repository’s <code>code/</code> folder. Save the original results first. The existing single-core run takes about 6.6 minutes.

~~~bash
OMP_NUM_THREADS=1 python cavity_ldos.py
~~~

**Change only T_MAX from 6000.0 to 12000.0** and run the same command. This experiment changes only the runtime cap in part B. Keep all other parameters and the source unchanged.

For w = 0.2, compare <code>T_run</code>, <code>dft_ldos</code>, and Q from the spectral linewidth against the original log. Observe how the resonance spectrum changes in the longer run. The original required time was 23915, so **12000 is still below that criterion.** Do not label the new value converged; record it separately from the original 3499.1119.

<h2 id="interpret">5. Interpret: high Q does not guarantee reliable LDOS</h2>

| Planar-cavity comparison | Recorded result |
|---|---|
| Error against the analytic expression, excluding cutoffs | Median 0.94%, maximum 3.6% |
| t = 1.0: CYL / 3D / analytic | 0.912 / 0.933 / 0.9375 |
| t = 2.0: CYL / 3D / analytic | 0.988 / 0.979 / 0.9844 |
| CYL value at the t = 1.5 cutoff | 0.507, near the lower analytic limit of about 0.519 |

The 3D check covers **only two points**, t = 1, 2. This agreement does not validate all thicknesses and resolutions, including the vicinity of cutoffs. At t = 2.5, the CYL value 1.172 lies between the lower limit 0.728 and upper limit 1.320; it cannot be called an exact match to either step.

| Aperture w in the 2D box | Harminv Q | Time criterion 2Q/f | Runtime | LDOS / (Q/V estimate) |
|---|---:|---:|---:|---:|
| 0.2 µm | 8060 | 23915 | 6000, cap reached | 0.72 |
| 0.3 µm | 1271 | 3802 | 3802 | 0.89 |
| 0.4 µm | 189 | 574 | 574 | 0.85 |
| 0.5 µm | 74 | 230 | 230 | 0.81 |

The table uses 2Q/(πωV), with V = a²/4 from the analytic **closed-box** mode. This is an approximation for a box with an aperture, so the ratio need not reach exactly 1 even with sufficient runtime. At w = 0.2 the run is also too short: spectral Q is 5597, below Harminv’s 8060. Therefore raw LDOS 3499 is not reported as a converged value.

<h2 id="check">6. Check your understanding</h2>

1. Why can you not state the factor by which emission changed from the cavity LDOS alone?
2. Why can the LDOS at w = 0.2 not be reported as converged even though Q was measured as 8060?

<details markdown="1">
<summary>Check both answers</summary>

1. A bulk reference with the same medium, source, and coordinate system is required. The ratio of the two LDOS values is the Purcell factor; one raw LDOS value still contains normalization factors.
2. The LDOS run was capped at 6000, whereas the time criterion 2Q/f was 23915. The long resonance response was not fully captured, and the spectral Q differs as well. A large Q alone does not guarantee LDOS convergence.

</details>

<h2 id="reference">7. References and full code</h2>

The original analytic expressions, coordinate-specific settings, detailed measurements, and execution records are provided below.


<details markdown="1">
<summary>English summary</summary>

### TL;DR (English)

<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/03_purcell.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/03_purcell.png' | relative_url }}" alt="How does the amount of light change between two mirrors? Original overview figure" loading="lazy"></a>
</figure>

- **What**: post 10 put one mirror next to a dipole and the pattern changed. Here the dipole sits between two mirrors and the question is the emitted power itself. Meep measures it as the local density of states (LDOS) at the source point with `dft_ldos`. Part A: an in-plane dipole in a dielectric slab (n = 2.4) between two lossless metallic mirrors, the Purcell factor F = LDOS(cavity)/LDOS(bulk) versus the normalized thickness t = nL/λ, swept in cylindrical coordinates and checked in 3D. Part B: a dipole in a 2D metal box with one aperture, where the LDOS at resonance is compared with the single-mode estimate 2Q/(πωV).
- **Result**: away from the three modal cutoffs the cylindrical sweep matches the analytic curve of Abram et al. with a median error of 0.94% (max 3.6%); at the cutoffs t = 0.5, 1.5, 2.5 the LDOS is discontinuous and FDTD lands on one side of the step. Two full-3D points agree with the cylindrical run to 2.3% / 0.9% (t = 1.0 / 2.0). In the metal box the Harminv Q rises from 74 (w = 0.5) to 8060 (w = 0.2); the directly measured LDOS is 0.81–0.89 of 2Q/(πωV) where the run was long enough, and only 0.72 of it for w = 0.2, whose required run time 2Q/f = 23915 was capped at 6000.
- **Takeaway**: a mirror changes not only where light goes but how much is emitted. The Purcell factor is always a ratio of two LDOS runs with the same source. A new cavity mode opens at every half wavelength and the LDOS jumps there. A high-Q LDOS costs a run time of order 2Q/f, and an under-converged LDOS is not a small error but a different number.
- **Code**: full script at the bottom, ~6.6 min on one core.

</details>

<details markdown="1">
<summary>Background, equations, and parameters in detail</summary>

### Original §0 · What you will learn

- What LDOS measures: the power emitted locally by a unit dipole. `dft_ldos` measures it at the source point without a spatial monitor.
- Why the Purcell factor is the ratio of two runs, cavity and bulk, using the same source, rather than one LDOS value.
- Why a new mode opens every half wavelength between two mirrors and the LDOS jumps. At cutoffs, the ordinary pointwise comparison breaks down.
- How to represent an in-plane dipole with cylindrical `Er`, `m = -1` (a preview of chapter 13), and cross-check it against 3D.
- Why omitting PML in z implements the physical mirror condition rather than a mistake.
- Resonant LDOS ≈ 2Q/(πωV): use Harminv Q to choose the required runtime 2Q/f and see what goes wrong when the run is too short.

**Prerequisites**: image dipoles and PEC from chapter 10, and point sources from chapter 01. **Official examples**: [Local density of states tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/), [planar cavity with lossless metallic walls](https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/#planar-cavity-with-lossless-metallic-walls), and [metal cavity with an aperture](https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/#square-box-with-a-small-opening); scripts [planar_cavity_ldos.py](https://github.com/NanoComp/meep/blob/master/python/examples/planar_cavity_ldos.py) · [metal-cavity-ldos.py](https://github.com/NanoComp/meep/blob/master/python/examples/metal-cavity-ldos.py). **Previous**: [10 · 3D radiation patterns of a point source]({{ site.baseurl }}/en/dipole-pattern-3d/) · **Next**: [12 · A ring that confines light]({{ site.baseurl }}/en/ring-resonator/)


### Original §1 · What do we want to find out?

This was the closing question of chapter 10. One mirror turned the radiation pattern into five lobes. If a point source is placed between two mirrors, does the amount of light change as well as its pattern? Classical electromagnetism explains why the same dipole at the same amplitude emits different power in different surroundings. Dipole power is the work its own field does on its current; when mirrors return that field, the work changes. LDOS measures this quantity, and its ratio to bulk is the Purcell factor. The second question concerns confined light: when a metal box has a small aperture, light stays longer (Q). Does the resulting Q/V enhancement of LDOS agree with measurement?

### Where is this useful?

There are three reasons to confine light. First, the emission rate changes: a radiating molecule that emits faster relative to nonradiative pathways can become more efficient (Purcell enhancement). Second, the interaction time increases. Repeated optical circulation can enhance sensing, modulation, and nonlinear interactions, with Q setting the enhancement scale. Third, the structure selects frequencies. Passing only resonant light underlies filters and lasers. LDOS and Q are basic quantities for all three applications.

| Application | Quantity used in this chapter | What comes next |
|---|---|---|
| Internal efficiency of OLEDs and LEDs | Purcell factor: electrodes (mirrors) and emitting-layer thickness set the emission rate | Chapter 14: extraction efficiency |
| Single-photon sources (quantum dot–cavity), laser threshold | LDOS, Q/V, and resonant-mode β factor | Chapter 12: rings; chapter 13: cylindrical coordinates |
| Sensors, modulators, nonlinear devices | Q increases the interaction time | Chapter 12: rings; chapter 22: nonlinearity |
| Filters and wavelength-division multiplexing (WDM) | Resonance selection and linewidth f/Q | Chapter 12: ring resonators |
| Thermal emission and radiative cooling | LDOS itself (thermal LDOS) | — |



### Original §2 · The physics on one page

At frequency ω, the power emitted by a dipole $\hat p$ at $\mathbf x_0$ is proportional to the work of the local electric field on the current, $-\tfrac12\mathrm{Re}[\hat E\cdot\hat J^*]$. Meep’s `dft_ldos` returns this normalized to a unit dipole.

$$
\mathrm{LDOS}(\mathbf x_0,\omega)=-\frac{2}{\pi}\,\varepsilon(\mathbf x_0)\,
\frac{\mathrm{Re}\big[\hat E_\ell(\mathbf x_0,\omega)\,\hat p(\omega)^*\big]}{\lvert \hat p(\omega)\lvert ^2},\qquad
F_P=\frac{\mathrm{LDOS}_{\mathrm{cavity}}}{\mathrm{LDOS}_{\mathrm{bulk}}}
$$

The denominator is needed because the numerator contains source-amplitude, coordinate-system, and grid normalization factors. Running bulk with the same source representation and taking the ratio cancels them. For an in-plane dipole between two mirrors, Abram et al. (1998) give a closed expression in terms of thickness $t=nL/\lambda$.

$$
F_P(t)=\frac{3N}{4t}+\frac{4N^3-N}{16t^3},\qquad N=\mathrm{fix}\!\left(t+\tfrac12\right)
$$

$N$ is the number of modes that fit between the mirrors. Whenever $t$ passes a half integer, a mode opens and $F_P$ jumps. It is 3 at $t=0.5$, 0.94 at $t=1.0$, and 0.98 at $t=2.0$. At these jumps (cutoffs), LDOS is discontinuous, so finite-time, finite-grid FDTD values depend on which side of the step is represented.

When one resonant mode of the metal box dominates LDOS, a single-mode approximation applies.

$$
\mathrm{LDOS}(\omega_n)\approx\frac{2}{\pi\,\omega_n}\,\frac{Q_n}{V_n},\qquad
V^{(1)}=\frac{a^2}{4},\quad \omega^{(1)}=\frac{\sqrt2\,\pi c}{a}
$$

The longer light remains ($Q$), and the smaller the region it occupies ($V$), the more the dipole emits. A direct `dft_ldos` measurement must run long enough for the DFT to converge, allowing the field to decay; this time is of order $2Q/f$.

| Symbol | Meaning | Code variable |
|------|----|-----------|
| $t=nL/\lambda$ | Mirror spacing in wavelengths inside the medium | `T_NORM` |
| $L$ | Physical mirror spacing $t\lambda/n$ | `cavity_um` |
| $N$ | Number of open modes $\mathrm{fix}(t+\tfrac12)$ | `np.fix(t + 0.5)` |
| $F_P$ | Purcell factor | `purcell_cyl`, `purcell_3d` |
| $Q$, $f$ | Resonance Q and frequency (Harminv) | `Q`, `f` |
| $V$ | Mode volume $a^2/4$ (analytic) | `V_MODE` |
| $2Q/f$ | Runtime required for `dft_ldos` | `T_req` |

**Assumptions and validity**: part A uses a lossless dielectric (n = 2.4), perfectly conducting mirrors, a single frequency, and an in-plane dipole. Part B is 2D Ez in a perfectly conducting box. Mode volume $a^2/4$ is the analytic closed-box value and is approximate for an open box. Point-source LDOS in a lossy medium diverges with resolution, so this method must not be transferred directly.

### Predict before viewing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| $F_P(t=1.0)$ | 0.94 | Eq. 7, $N=1$ |
| Median CYL error excluding cutoffs | Within 2% | Notes: 0.95% |
| Three cutoff points | Different from Eq. 7; side of the step unknown | Discontinuities |
| 3D (res 48) vs CYL, $t=1,2$ | Within 3% | CYL–3D median in the notes: 1.3% |
| Dependence of $Q$ on w | Tens-fold increase from w 0.5 → 0.2 | A narrower aperture leaks less |
| $Q$(w = 0.2) | Near 8000 | Notes: 8060 |
| Converged-run LDOS vs $2Q/(\pi\omega V)$ | Within 20% | Notes: median 15%; $V$ is approximate |
| w = 0.2 (cap 6000 < 2Q/f) | Below half of $2Q/(\pi\omega V)$ | Notes: 62% short in a 2000-unit run |
| Spectral-FWHM $Q$ vs Harminv $Q$ | Within 10% | Same resonance |

**Decision criteria**: if the median error away from cutoffs exceeds 5%, check bulk normalization or boundaries (z PML). If converged LDOS/(Q/V estimate) differs by more than a factor of 2, check whether Harminv selected a different mode.


### Original §3 · Simulation layout

<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/02_layout_cyl.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/02_layout_cyl.png' | relative_url }}" alt="Part A cylindrical r–z cell at t=1.0, L = 0.417 µm; no PML on the upper and lower PEC walls; outer radial PML and an Er dipole offset by 1.5 pixels" loading="lazy"></a>
<figcaption markdown="span">Part A cylindrical r–z cell ($t=1.0$, L = 0.417 µm). Horizontal is radius r; vertical is the mirror normal z. The top and bottom cell walls have no PML and serve as perfectly conducting mirrors. PML appears only at the outer radial boundary (green hatching). The red dot is the Er dipole, 1.5 pixels off the axis.</figcaption>
</figure>


<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/01_layout.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/01_layout.png' | relative_url }}" alt="Part B 2D PEC box, 1 × 1 µm with 0.1 µm walls and an aperture of width w; central Ez dipole, surrounding PML, and DFT region" loading="lazy"></a>
<figcaption markdown="span">Part B 2D cell. A perfectly conducting box (1 × 1 µm, walls 0.1 µm) has an aperture of width w in its right wall. The central Ez dipole is both the Harminv probe and the `dft_ldos` sampling point. PML is 1 µm on every side. `plot2D` renders `mp.metal` (ε = −∞) white and air black, so the white border is metal. The blue rectangle is a representative Ez DFT region.</figcaption>
</figure>


| Parameter | Value | Why this value? | Effect of changing it |
|----------|-----|-------------|--------|
| A wavelength, n, resolution | 1 µm, 2.4, res 71 | Official values; 30 cells per 0.417 µm wavelength in the medium | At lower resolution, rounding the thickness to the grid produces steps |
| A thickness sweep | $t$ = 0.5~2.5, 21 points spaced by 0.1 | Half the official 41 points; includes three cutoffs | Finer spacing reveals the cutoff steps more clearly |
| A 3D check | $t$ = 1.0, 2.0, res 48 | A full 3D sweep takes tens of minutes | Cross-checks coordinate systems at only two points |
| A bulk cell | CYL 6 µm, 3D 3 µm (+PML 0.5) | A uniform medium is relatively insensitive to size | If too small, PML reflection contaminates LDOS |
| A stopping condition | Source-point field decay to 1e-6 | Official value | Without loss in z, cavity runs take longer than bulk runs |
| B box and aperture | a = 1, walls 0.1, w = 0.2/0.3/0.4/0.5 | Adds 0.5 to the official 0.2~0.4 | Smaller w raises Q and required runtime |
| B Harminv | fcen = √0.5/a = 0.707, df 0.2, 500 time units | Fundamental frequency of the closed box | A wider band includes higher modes |
| B `dft_ldos` time | min(2Q/f, 6000) | Official example has no cap; w = 0.2 is deliberately unconverged | Removing the cap makes w = 0.2 take tens of minutes |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/00_source.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/00_source.png' | relative_url }}" alt="Part A source waveform and spectrum: 1000 nm, fwidth 0.2 fcen; LDOS is measured at the center frequency" loading="lazy"></a>
<figcaption markdown="span">Part A source waveform and spectrum (1000 nm, fwidth 0.2 fcen). LDOS is measured at the single center frequency of this band.</figcaption>
</figure>


**Differences from the course notebooks**: this topic is outside the course scope. The two notes in 10_sources ran a 41-point sweep (full CYL and 3D, res 71) and three apertures (cap 2000), respectively. This chapter reduces the sweep to 21 points and checks only two in 3D, while adding w = 0.5 and measuring Q again from the `dft_ldos` spectral linewidth to compare with Harminv.

</details>

<details markdown="1">
<summary>Original code, step by step</summary>

### Original §4 · Follow the code

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → run and stopping conditions → postprocessing.
> Here, step ⑤ uses source-point `dft_ldos` and `Harminv`, rather than spatial monitors.

### ① Units and parameters — which values are fixed?

```python
WL, N_CAV, RES_CYL, RES_3D = 1.0, 2.4, 71, 48
T_NORM = np.round(np.arange(0.5, 2.51, 0.1), 2)       # t = n L / wl; cutoffs at 0.5, 1.5, 2.5
L = t * WL / N_CAV                                     # the physical mirror spacing that goes into the cell

A_BOX, T_WALL, WS = 1.0, 0.1, (0.2, 0.3, 0.4, 0.5)     # metal box, wall, aperture widths
FCEN_M = math.sqrt(0.5) / A_BOX                        # fundamental mode of the closed box
T_MAX = 6000.0                                         # cap on the dft_ldos run
```

- **What**: the thickness sweep and resolution in part A; the box and aperture widths in part B.
- **Why**: the plot’s horizontal axis is $t=nL/\lambda$, not physical thickness. The cell must use $L=t\lambda/n$. The box fundamental mode has $\omega=\sqrt2\pi c/a$, or $f=\sqrt{0.5}/a$, setting the Harminv center.
- **If wrong**: entering $t$ directly as µm makes the mirror spacing 2.4 times too large and invalidates comparison with Eq. 7.

### ② Materials and geometry — walls without PML serve as mirrors

```python
# part A, cavity: PML only in r (cyl) or x, y (3D). The z walls of the cell are Meep's default PEC = the mirrors.
pml = [mp.PML(thickness=DPML, direction=mp.R)]
# part A, bulk: PML on every side, same source, same medium
pml = [mp.PML(thickness=DPML)]
# part B: a metal shell, an air box, and an air block that cuts the aperture into the right wall
geometry = [mp.Block(mp.Vector3(A_BOX + 2 * T_WALL, A_BOX + 2 * T_WALL, mp.inf), material=mp.metal),
            mp.Block(mp.Vector3(A_BOX, A_BOX, mp.inf), material=mp.air),
            mp.Block(center=mp.Vector3(A_BOX / 2), size=mp.Vector3(2 * T_WALL, w, mp.inf), material=mp.air)]
```

- **What**: part A’s mirrors are not geometry objects. Without z PML, the cell walls are perfectly conducting mirrors. Bulk runs open every direction with PML to remove the mirrors. Part B overlays a metal block, an air block, and an aperture block in that order.
- **Why**: the Purcell factor is the ratio “with mirrors / without mirrors.” The physical distinction between the two runs should be the boundary condition.
- **If wrong**: adding z PML to the cavity makes it finish sooner but removes the mirrors. This is the opposite of chapter 10: there, `k_point` meant the wall was not a mirror; here, the absence of `k_point` makes it a mirror.

### ③ Source — two representations of an in-plane dipole

```python
# cyl: an x-dipole is the m = -1 family of Er; the axis r = 0 is singular, so offset by 1.5 pixels
src_pt = mp.Vector3(1.5 / RES_CYL, 0, 0)
sources = [mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Er, center=src_pt)]
# 3D: the same dipole as Ex at the origin
sources = [mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Ex, center=mp.Vector3())]
```

- **What**: represent the same physical dipole with `Er`, `m = -1` in cylindrical coordinates and `Ex` in 3D.
- **Why**: an x-directed dipole has azimuthal dependence $e^{\pm i\phi}$, corresponding to $m=\pm1$. The radial unit vector is undefined on the axis, so the source is offset by 1.5 pixels. This avoids a coordinate singularity rather than changing the structure.
- **If wrong**: a fixed offset in µm changes the source representation in pixels as resolution changes. Chapter 13 develops cylindrical coordinates in detail.

### ④ Simulation and boundaries — CYL m and 3D symmetry phases

```python
sim = mp.Simulation(resolution=RES_CYL, cell_size=mp.Vector3(cell_r, 0, cell_z), boundary_layers=pml,
                    dimensions=mp.CYLINDRICAL, m=-1, default_material=mp.Medium(index=N_CAV), sources=sources)

sim = mp.Simulation(..., symmetries=[mp.Mirror(mp.X, phase=-1), mp.Mirror(mp.Y), mp.Mirror(mp.Z)])   # 3D: Ex is odd under x
```

- **What**: cylindrical calculations use `dimensions=mp.CYLINDRICAL` and `m`. Three mirror symmetries reduce the 3D computational domain to 1/8.
- **Why**: `Ex` changes sign under x reflection, but not under y or z reflection. The phases describe the source vector’s parity, not just the geometry.
- **If wrong**: setting every phase to +1 computes a source of different parity, rather than accelerating the same problem. This is the same rule that made Ez odd for the image dipole in chapter 10.

### ⑤ Monitors — at the source, without a spatial monitor

```python
sim.run(mp.dft_ldos(FCEN, 0, 1), until_after_sources=...)          # LDOS at one frequency, at the source point
ldos = sim.ldos_data[0]

h = mp.Harminv(mp.Ez, mp.Vector3(), FCEN_M, DF_M)                   # part B: f and Q of the ringing field
sim.run(mp.after_sources(h), until_after_sources=500)
f, Q = h.modes[0].freq, h.modes[0].Q
sim.run(mp.dft_ldos(f, 8 * f / Q, 101), until_after_sources=min(2 * Q / f, T_MAX))   # spectrum +-4 linewidths around f
```

- **What**: `dft_ldos` is a step function that accumulates field and current DFTs at the source to calculate LDOS. Harminv extracts resonant frequency and Q from the decay after the source turns off.
- **Why**: LDOS describes work at the source rather than flux. No flux box is needed. In part B, pass Harminv’s f to `dft_ldos`, then independently check Q using the spectral linewidth.
- **If wrong**: using the initial fcen instead of Harminv’s f samples slightly off resonance and underestimates LDOS. For Q in the thousands, the linewidth is around 1e-4, so a small frequency offset matters.

### ⑥ Run — decay conditions and 2Q/f

```python
until_after_sources=mp.stop_when_fields_decayed(20, mp.Er, src_pt, 1e-6)    # part A
until_after_sources=min(2 * Q / f, T_MAX)                                     # part B
```

- **What**: in part A, run until the source-point field decays to 1e-6. In part B, use the time determined by Q.
- **Why**: resolving linewidth $f/Q$ requires a long observation window; this example uses $2Q/f$. At w = 0.2, Q is near 8000 and $2Q/f\approx 23000$. The run is capped at 6000 to demonstrate the effect of truncation.
- **If wrong**: ending the cavity run as quickly as a bulk run leaves part of the lingering field out of the LDOS accumulation. It is normal for part A’s cavity runs to take longer than bulk.

### ⑦ Postprocessing — ratios, Eq. 7, and Q/V

```python
purcell = ldos_cavity / ldos_bulk                                      # same source, same medium, same coordinates
N = np.fix(t + 0.5); theory = 3 * N / (4 * t) + (4 * N**3 - N) / (16 * t**3)
cutoff = np.isclose(np.mod(t, 1.0), 0.5)                               # exclude from the error statistics, keep the raw values

ldos_qv = Q / V_MODE / (2 * math.pi * f * math.pi * 0.5)               # 2Q / (pi w V), V = a^2 / 4
```

- **What**: Purcell enhancement is a ratio. Report both median and maximum error against Eq. 7, excluding cutoffs. Place the Q/V estimate alongside the direct measurement in part B.
- **Why**: reporting only the median hides local failures such as $t=1.45$. Keep cutoff values in a separate table rather than discarding them.
- **If wrong**: do not simply classify cutoff FDTD values as wrong or move them to the more favorable step. The analytic expression has two one-sided limits there.

> **Pitfall**: Meep rounds the cell size to an integer number of pixels. If $L\times$res is not an integer, adjacent thicknesses may use the same z-grid count, creating small steps in the sweep. Near a cutoff, this rounding can change which open mode is represented. The log message "cell size will be rounded" is meaningful.

</details>

<details markdown="1">
<summary>Original results, validation tables, troubleshooting, and further experiments</summary>

### Original §5 · Results

<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/03_purcell.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/03_purcell.png' | relative_url }}" alt="Part A: Purcell factor versus t, with Eq. 7, cylindrical sweep, two 3D checks, and error excluding cutoffs" loading="lazy"></a>
<figcaption markdown="span">Part A. Left: Purcell factor versus $t$. Black is Eq. 7, red dots are the cylindrical sweep, and blue squares are the two 3D points. Dashed lines mark cutoffs. Right: relative error excluding the cutoffs; gray bars mark the three cutoff points.</figcaption>
</figure>


| $t$ | Eq. 7 | CYL | 3D (res 48) | Notes |
|---|---|---|---|---|
| 0.5 | 3.000 | 3.018 | — | cutoff |
| 1.0 | 0.9375 | 0.912 | 0.933 | |
| 1.5 | 1.556 (upper step) / 0.519 (lower) | 0.507 | — | Cutoff; FDTD is near the lower step |
| 2.0 | 0.9844 | 0.988 | 0.979 | |
| 2.5 | 1.320 (upper) / 0.728 (lower) | 1.172 | — | Cutoff |
| 18 points excluding cutoffs | — | median 0.94%, max 3.6% (t = 0.70) | — | |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/04_cavity_field.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/04_cavity_field.png' | relative_url }}" alt="Steady-state Re(Er) between the mirrors in the r–z plane, with z stretched; modal patterns at t=1.0 and t=2.0" loading="lazy"></a>
<figcaption markdown="span">Steady-state Re(Er) between the mirrors in the r–z plane (z stretched). At $t=1.0$, one mode without a z node propagates radially. At $t=2.0$, a mode with two z nodes is superposed, so the upper and lower lobes have the opposite sign to the center. The green dot marks the dipole; the color range excludes the source pixel.</figcaption>
</figure>


<figure class="lesson-figure">
<a href="{{ '/assets/meep/11/05_metal_ldos.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/11/05_metal_ldos.png' | relative_url }}" alt="Part B: resonant dft_ldos spectra, Q/V estimate versus direct LDOS, and resonant Ez at aperture width 0.3" loading="lazy"></a>
<figcaption markdown="span">Part B. Left: `dft_ldos` spectra near resonance, with linewidth $f/Q$. Center: Q/V estimate (blue) and direct measurement (red) against a/w on a semilog plot. The w = 0.2 run is truncated and unconverged. Right: resonant Ez at w = 0.3, resembling the closed-box fundamental $\sin(\pi x/a)\sin(\pi y/a)$ with leakage toward the aperture.</figcaption>
</figure>


| w | f (Harminv) | Q (Harminv) | Q (spectral linewidth) | 2Q/f | Runtime | $2Q/(\pi\omega V)$ | `dft_ldos` | Ratio |
|---|---|---|---|---|---|---|---|---|
| 0.2 | 0.6740 | 8060 | 5597 (truncated run) | 23915 | 6000 (cap) | 4846 | 3499 | 0.72 |
| 0.3 | 0.6688 | 1271 | 1324 | 3802 | 3802 | 770 | 686 | 0.89 |
| 0.4 | 0.6569 | 189 | 196 | 574 | 574 | 116 | 98 | 0.85 |
| 0.5 | 0.6465 | 74 | 78 | 230 | 230 | 46.7 | 37.6 | 0.81 |



### Compare with the predictions

| Quantity | Prediction (§2) | Simulation | Assessment |
|--------|-------------|-----------|------|
| $F_P(t=1.0)$ | 0.94 | 0.912 | Pass (2.7% difference) |
| Median error excluding cutoffs | Within 2% | 0.94% | Pass |
| Three cutoff points | Different from Eq. 7 | 0.5: 3.018, 1.5: 0.507, 2.5: 1.172 | At cutoffs: 1.5 is near the lower limit; 2.5 lies between both limits |
| 3D vs CYL | Within 3% | 2.3% / 0.9% (t = 1.0 / 2.0) | Pass |
| Dependence of $Q$ on w | Tens-fold increase | 74 → 8060 | Pass (109-fold) |
| $Q$(w = 0.2) | Near 8000 | 8060 | Pass |
| Converged LDOS vs Q/V | Within 20% | 0.81~0.89 | Pass |
| Unconverged w = 0.2 | Below half | 0.72 (28% short) | Fail (above half) |
| Spectral Q vs Harminv Q | Within 10% | 1324/1271, 196/189, 78/74 (4~5%) | Pass |

Eight of nine predictions were correct. The wrong prediction concerned the degree of underconvergence at w = 0.2. The notes ran for only 8% (2000) of the required time and fell short by 62%; this chapter ran for 25% (6000) and fell short by 28%. Truncation omits the long resonance tail from the DFT, reducing LDOS and broadening the spectrum. Spectral Q of 5597, below Harminv’s 8060, is the signature. For the other three apertures, spectral and Harminv Q agree within 5%, while direct LDOS is 81~89% of the Q/V estimate. The remaining 10~20% reflects the closed-box mode-volume approximation $a^2/4$: the open mode spreads farther as the aperture widens, and the ratio falls from 0.89 to 0.81. In part A at $t=1.0$, CYL gives 0.912, 2.7% below Eq. 7’s 0.9375, while 3D gives 0.933 between them; this is attributed to differences in coordinate representation. At the cutoffs, finite-grid behavior follows the predicted discontinuity: $t=0.5$ is near the upper step (3.018 vs 3.0), $t=1.5$ is near the lower limit (0.507 vs 0.519), and $t=2.5$ gives 1.172 between the lower 0.728 and upper 1.320 limits.

### Convergence

| Variable | Values | Result | Notes |
|---|---|---|---|
| A sweep spacing | 0.1 (21 points here) vs 0.05 (41 in the notes) | Median 0.94% vs 0.95% | Spacing does not determine each point’s error; each is an independent run |
| A 3D resolution | 48 here vs 71 in the notes | CYL differences at $t=1,2$: 2.3% / 0.9% (t = 1.0 / 2.0), vs notes median 1.3% | The notes’ 3D maximum of 11.4% at $t=1.45$ was not measured here |
| B runtime | 2Q/f (w ≥ 0.3) vs cap 6000 (w = 0.2) | Ratio 0.81~0.89 vs 0.72 | Underconvergence produces a different number, not merely a small error |

### What the results do and do not establish

- Established: with n = 2.4, PEC mirrors, and res 71, the cylindrical `dft_ldos` Purcell factor has median relative error 0.94% and maximum 3.6% against Eq. 7 away from cutoffs. It agrees with two 3D points within 2.3% / 0.9% (t = 1.0 / 2.0). In the metal box, runs lasting the time set by Harminv Q give direct LDOS of 0.81~0.89 times $2Q/(\pi\omega V)$.
- Not established: a unique value at the three discontinuous cutoffs; the local 11% 3D error at $t=1.45$ seen in the notes but not sampled here; or behavior with lossy mirrors or media. The closed-box $a^2/4$ mode volume becomes a poorer approximation as the aperture widens. The converged LDOS at w = 0.2 is unknown at this runtime.


### Original §6 · Common mistakes

| Symptom | Cause | Fix |
|------|------|----------|
| All Purcell factors near 1 | z PML in the cavity run removes the mirrors | Use only transverse PML for the cavity and all-direction PML for bulk |
| Purcell factor is tens-fold too large | Raw LDOS used without bulk normalization | Run bulk with the same source and divide |
| CYL run diverges at the axis | `Er` placed at r = 0 | Offset by 1.5 pixels |
| 3D differs from CYL by a factor of 2 | All symmetry phases set to +1 | `Ex` requires `Mirror(X, phase=-1)` |
| Small steps in the sweep curve | Cell thickness rounded to pixels | Choose integer $L\times$res or increase resolution |
| 50% error at a cutoff | A discontinuity included as an ordinary statistical sample | Retain raw values, but exclude them from the median |
| Direct LDOS is half the Q/V estimate | `dft_ldos` runtime shorter than 2Q/f | Measure Q first and choose runtime accordingly |
| r–z field is flipped or one column dominates | Cylindrical `get_array` and `get_dft_array` use (z, r) order | Do not transpose as in 2D; the bright column is the r = 0 source column |
| Field image looks almost empty | Source pixel dominates the color maximum | Clip the display range at the 99th percentile |
| LDOS below its resonant value | `dft_ldos` uses fcen instead of Harminv f | Pass the Harminv frequency |


### Original §7 · Try it yourself

| Change | Expected effect | Quantity to check |
|---------|----------|------------|
| Orient part A’s dipole along z (`Ez`, m = 0) | A perpendicular dipole has a different curve between mirrors | Whether emission is nonzero for $t<0.5$ |
| Sweep spacing 0.1 → 0.02, $t$ = 1.4~1.6 | Resolves the step near cutoff 1.5 | The $t$ at which it jumps |
| Part A resolutions 50 / 71 / 100 | A sequence of median errors away from cutoffs | Where the 0.94% error stops improving |
| Remove part B’s cap at w = 0.2 | Ratio moves toward 1 | Ratio and elapsed time |
| Add w = 0.1 to part B | Q in the tens of thousands; 2Q/f in the hundreds of thousands | Estimate Q/V from Harminv alone |

</details>

<details>
<summary>Full code/cavity_ldos.py (expand)</summary>
{% highlight python %}
"""Meep Example 11 - A point dipole between two mirrors: LDOS and the Purcell factor.

Post 10 showed that one mirror rewrites the radiation pattern. Here the dipole sits between two mirrors and the
question is the emitted POWER itself, measured as the local density of states (LDOS) at the dipole position.
  A. Planar cavity (official planar_cavity_ldos.py): lossless metallic walls, dielectric n = 2.4, in-plane dipole.
     The Purcell factor F = LDOS(cavity) / LDOS(bulk) versus the normalized thickness t = n L / wl, swept in
     cylindrical coordinates (Er, m = -1 represents an x-dipole) and checked at two thicknesses in full 3D.
     Compared with the analytic Eq. 7 of Abram et al. (1998): F = 3N/(4t) + (4N^3 - N)/(16 t^3), N = fix(t + 1/2).
  B. Metal box with an aperture (official metal-cavity-ldos.py, 2D): Harminv gives f and Q of the fundamental mode;
     the LDOS at f is measured directly with dft_ldos and compared with the single-mode estimate 2Q/(pi w V).
     The required run time 2Q/f grows with Q; the narrowest aperture is deliberately left under-converged.

Run:  python cavity_ldos.py       (~15 min on one core)
Out:  00_source.png, 01_layout.png, 02_layout_cyl.png, 03_purcell.png, 04_cavity_field.png, 05_metal_ldos.png,
      06_anim_planar.gif, 07_anim_metal.gif, result.json   (-> ../assets/11/)
"""
import json
import math
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, _badge, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "11")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()

# =================================================================== A. planar cavity with lossless metallic walls
# ---------------------------------------------------------------- (1) parameters (official values; 21-point sweep instead of 41)
WL = 1.0
FCEN = 1 / WL
FWIDTH = 0.2 * FCEN
N_CAV = 2.4
RES_CYL = 71
RES_3D = 48                              # 3D cross-check only (official: 71)
DPML = 0.5
BULK_CYL, BULK_3D = 6.0, 3.0
DECAY_TOL, DECAY_PERIOD = 1e-6, 20
T_NORM = np.round(np.arange(0.5, 2.51, 0.1), 2)          # t = n L / wl; cutoffs at 0.5, 1.5, 2.5
T_3D = (1.0, 2.0)                                         # thicknesses checked in full 3D


def purcell_theory(t):
    N = np.fix(t + 0.5)
    return 3 * N / (4 * t) + (4 * N ** 3 - N) / (16 * t ** 3)


def ldos_cyl(cavity_um=None, *, want_field=False):
    """LDOS of an in-plane dipole (Er, m = -1) in cylindrical coordinates; bulk medium if cavity_um is None."""
    if cavity_um is None:
        cell_z, pml = BULK_CYL + 2 * DPML, [mp.PML(thickness=DPML)]
    else:
        cell_z, pml = cavity_um, [mp.PML(thickness=DPML, direction=mp.R)]      # no z PML: the cell walls are the mirrors
    cell_r = BULK_CYL + DPML
    src_pt = mp.Vector3(1.5 / RES_CYL, 0, 0)                                    # Er at r = 0 is singular: offset by 1.5 px
    sim = mp.Simulation(resolution=RES_CYL, cell_size=mp.Vector3(cell_r, 0, cell_z), boundary_layers=pml, dimensions=mp.CYLINDRICAL, m=-1,
                        default_material=mp.Medium(index=N_CAV),
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Er, center=src_pt)])
    dft = sim.add_dft_fields([mp.Er], FCEN, 0, 1, center=mp.Vector3(0.5 * BULK_CYL, 0, 0), size=mp.Vector3(BULK_CYL, 0, cell_z)) if want_field else None
    sim.run(mp.dft_ldos(FCEN, 0, 1), until_after_sources=mp.stop_when_fields_decayed(DECAY_PERIOD, mp.Er, src_pt, DECAY_TOL))
    ldos = float(sim.ldos_data[0]); t_end = sim.meep_time()
    field = sim.get_dft_array(dft, mp.Er, 0) if want_field else None
    sim.reset_meep()
    return (ldos, t_end, field) if want_field else (ldos, t_end)


def ldos_3d(cavity_um=None):
    """LDOS of an Ex dipole in full 3D (reduced resolution); bulk if cavity_um is None."""
    if cavity_um is None:
        size_z, pml = BULK_3D + 2 * DPML, [mp.PML(thickness=DPML)]
    else:
        size_z, pml = cavity_um, [mp.PML(thickness=DPML, direction=mp.X), mp.PML(thickness=DPML, direction=mp.Y)]
    size_xy = BULK_3D + 2 * DPML
    sim = mp.Simulation(resolution=RES_3D, cell_size=mp.Vector3(size_xy, size_xy, size_z), boundary_layers=pml,
                        default_material=mp.Medium(index=N_CAV),
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Ex, center=mp.Vector3())],
                        symmetries=[mp.Mirror(mp.X, phase=-1), mp.Mirror(mp.Y), mp.Mirror(mp.Z)])      # Ex is odd under x, even under y, z
    sim.run(mp.dft_ldos(FCEN, 0, 1), until_after_sources=mp.stop_when_fields_decayed(DECAY_PERIOD, mp.Ex, mp.Vector3(), DECAY_TOL))
    ldos = float(sim.ldos_data[0]); t_end = sim.meep_time(); sim.reset_meep()
    return ldos, t_end


source_figure(FCEN, FWIDTH, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# layout of the CYL cavity (r-z plane) at t = 1.0, drawn by hand: the cell is 6.5 x 0.42 um, far too thin for plot2D
L_demo = 1.0 * WL / N_CAV
fig, ax = plt.subplots(figsize=(9.5, 3.6))
ax.axvspan(BULK_CYL, BULK_CYL + DPML, color="green", alpha=0.25)
ax.axhline(0.5 * L_demo, color="k", lw=4); ax.axhline(-0.5 * L_demo, color="k", lw=4)
ax.plot(1.5 / RES_CYL, 0, "o", color="red", ms=7); ax.axvline(0, color="gray", ls="-.", lw=1)
for xy, step, color, txt, txy in (((0.25, 0.5 * L_demo - 0.03), 1, "dimgray", f"wl={WL} um, n={N_CAV}, res={RES_CYL}\ncell r {BULK_CYL + DPML} um x z L={L_demo:.3f} um, m=-1", (0.45, 0.5 * L_demo - 0.03)),
                                   ((3.0, 0.5 * L_demo), 2, "black", "top/bottom cell walls: no PML here, so they are PEC = the two mirrors", (3.2, 0.5 * L_demo - 0.035)),
                                   ((1.5 / RES_CYL, -0.035), 3, "red", "Er dipole (m = -1 = an in-plane dipole) at r = 1.5 px, the axis is singular", (0.45, -0.045)),
                                   ((BULK_CYL + 0.5 * DPML, 0.0), 4, "green", "PML (r only)", (BULK_CYL + 0.08, 0.04)),
                                   ((0.4, 0.07), 5, "blue", "LDOS: dft_ldos at the source point (no spatial monitor); bulk run = same cell with PML on z too", (0.6, 0.06)),
                                   ((1.5 / RES_CYL, 0.11), 6, "purple", "decay watch point = source point", (0.45, 0.10))):
    _badge(ax, xy, step, color); ax.text(*txy, txt, fontsize=8, color=color, va="center")
ax.text(0.05, -0.5 * L_demo + 0.01, "r = 0 (axis)", fontsize=7, color="gray", rotation=90, va="bottom")
ax.set_xlim(-0.1, BULK_CYL + DPML); ax.set_ylim(-0.5 * L_demo - 0.02, 0.5 * L_demo + 0.02)
ax.set_xlabel("r [um]"); ax.set_ylabel("z [um]  (stretched)")
ax.set_title("part A: cylindrical r-z cell at t = 1.0. The z axis is stretched 6x; the real cell is a thin disc between two mirrors", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_layout_cyl.png"), dpi=150); plt.close(fig)

t_a = time.time()
bulk_cyl, t_bulk_cyl = ldos_cyl()
purcell_cyl, t_end_cyl, fields = [], [], {}
for t in T_NORM:
    L = t * WL / N_CAV
    if t in (1.0, 2.0):
        ldos, t_end, fld = ldos_cyl(L, want_field=True); fields[t] = (fld, L)
    else:
        ldos, t_end = ldos_cyl(L)
    purcell_cyl.append(ldos / bulk_cyl); t_end_cyl.append(t_end)
purcell_cyl = np.array(purcell_cyl)
theory = purcell_theory(T_NORM)
cutoff = np.isclose(np.mod(T_NORM, 1.0), 0.5)
err_cyl = np.abs(purcell_cyl - theory) / theory
print(f"A (cyl): bulk LDOS {bulk_cyl:.5f} (t_end {t_bulk_cyl:.0f}); {len(T_NORM)} thicknesses in {time.time() - t_a:.0f} s; "
      f"rel error vs Eq. 7 away from cutoffs: median {np.median(err_cyl[~cutoff]):.4f}, max {err_cyl[~cutoff].max():.4f} at t = {T_NORM[~cutoff][np.argmax(err_cyl[~cutoff])]:.2f}; "
      f"at the cutoffs: " + ", ".join(f"t={t:.1f}: Meep {p:.3f} vs Eq.7 {th:.3f}" for t, p, th in zip(T_NORM[cutoff], purcell_cyl[cutoff], theory[cutoff])))

t_a = time.time()
bulk_3d, t_bulk_3d = ldos_3d()
purcell_3d = {}
for t in T_3D:
    ldos, t_end = ldos_3d(t * WL / N_CAV)
    purcell_3d[t] = ldos / bulk_3d
print(f"A (3D, res {RES_3D}): bulk LDOS {bulk_3d:.5f} (t_end {t_bulk_3d:.0f}); " + ", ".join(f"t={t}: 3D {purcell_3d[t]:.4f} vs cyl {purcell_cyl[np.isclose(T_NORM, t)][0]:.4f} vs Eq.7 {purcell_theory(t):.4f}" for t in T_3D)
      + f"; {time.time() - t_a:.0f} s")

fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
tt = np.linspace(0.5, 2.5, 801)
ax[0].plot(tt, purcell_theory(tt), "-", color="k", lw=1.2, label="Eq. 7 (Abram 1998)")
ax[0].plot(T_NORM, purcell_cyl, "o", color="tab:red", ms=5, label=f"Meep cylindrical (Er, m = -1), res {RES_CYL}")
ax[0].plot(list(T_3D), [purcell_3d[t] for t in T_3D], "s", color="tab:blue", ms=7, label=f"Meep 3D (Ex), res {RES_3D}")
for tc in (0.5, 1.5, 2.5):
    ax[0].axvline(tc, color="gray", ls=":", lw=1)
ax[0].axhline(1, color="gray", ls="--", lw=1); ax[0].text(2.3, 1.03, "bulk", fontsize=8, color="gray")
ax[0].set_xlabel("normalized cavity thickness t = n L / wavelength"); ax[0].set_ylabel("Purcell factor  LDOS(cavity) / LDOS(bulk)")
ax[0].set_title("in-plane dipole between two lossless mirrors (n = 2.4): a new mode opens at every half-integer", fontsize=9)
ax[0].set_ylim(0.4, 3.2); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
ax[1].bar(T_NORM[~cutoff], 100 * err_cyl[~cutoff], width=0.07, color="tab:red", alpha=0.7, label="cylindrical")
ax[1].bar(T_NORM[cutoff], 100 * err_cyl[cutoff], width=0.07, color="lightgray", label="at a cutoff (excluded)")
for t in T_3D:
    ax[1].plot(t, 100 * abs(purcell_3d[t] - purcell_theory(t)) / purcell_theory(t), "s", color="tab:blue", ms=7)
ax[1].set_xlabel("t"); ax[1].set_ylabel("|Meep - Eq. 7| / Eq. 7  [%]"); ax[1].set_title(f"error: median {100 * np.median(err_cyl[~cutoff]):.2f} % away from cutoffs", fontsize=9)
ax[1].grid(axis="y", alpha=0.3); ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_purcell.png"), dpi=150); plt.close(fig)

fig, ax = plt.subplots(2, 1, figsize=(10, 5.2))
for a, t in zip(ax, (1.0, 2.0)):
    fld, L = fields[t]
    # NOTE: in cylindrical coordinates get_dft_array / get_array return (z, r), not (r, z): no transpose here
    fld = fld[2:-2, :]                                      # drop the two grid rows touching each mirror (boundary pixels of the DFT array)
    nz = fld.shape[0]; dz = L / (nz + 4)
    ext = [0, BULK_CYL, -0.5 * L + 2 * dz, 0.5 * L - 2 * dz]
    lim = float(np.percentile(np.abs(fld), 99.5))           # the source pixel dominates the maximum: clip the colour scale
    a.imshow(np.real(fld), extent=ext, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="auto")
    a.axhline(0.5 * L, color="k", lw=2); a.axhline(-0.5 * L, color="k", lw=2); a.plot(1.5 / RES_CYL, 0, "o", color="lime", ms=4)
    a.set_title(f"Re(Er) at t = {t:.1f} (L = {L:.3f} um): F = {purcell_cyl[np.isclose(T_NORM, t)][0]:.3f}   (thick black lines = mirrors)", fontsize=9)
    a.set_ylabel("z [um]")
ax[1].set_xlabel("r [um]")
fig.suptitle("part A: steady-state field between the mirrors, cylindrical r-z plane", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_cavity_field.png"), dpi=150); plt.close(fig)

# GIF: a short pulse between the mirrors at t = 1.0 (r-z plane)
L = 1.0 * WL / N_CAV
fw_anim = 0.5 * FCEN
sim_g = mp.Simulation(resolution=RES_CYL, cell_size=mp.Vector3(BULK_CYL + DPML, 0, L), boundary_layers=[mp.PML(thickness=DPML, direction=mp.R)],
                      dimensions=mp.CYLINDRICAL, m=-1, default_material=mp.Medium(index=N_CAV),
                      sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=fw_anim), component=mp.Er, center=mp.Vector3(1.5 / RES_CYL, 0, 0))])
sim_g.init_sim()
vol_g = mp.Volume(center=mp.Vector3(0.5 * BULK_CYL, 0, 0), size=mp.Vector3(BULK_CYL, 0, L))
t0g = 5 / fw_anim
frames, times = record_frames(sim_g, vol_g, mp.Er, t_start=t0g - 2 / fw_anim, t_end=t0g + 1.1 * BULK_CYL * N_CAV, n_frames=60)
frames = [f.T for f in frames]                      # cylindrical get_array returns (z, r); animate_fields expects (x, y) = (r, z)
animate_fields(frames, times, [0, BULK_CYL, -0.5 * L, 0.5 * L], os.path.join(OUT, "06_anim_planar.gif"), figsize=(7.5, 2.8), dpi=70, aspect="auto",
               component="Er", unit="um", xlabel="r [um]", ylabel="z [um] (stretched)", clip_percentile=99.0,
               lines=[((0, 0.5 * L), (BULK_CYL, 0.5 * L), "k", "mirrors (cell walls)"), ((0, -0.5 * L), (BULK_CYL, -0.5 * L), "k", "_nolegend_")],
               points=[(1.5 / RES_CYL, 0, "red", "dipole")], title="planar cavity, t = 1.0", legend_loc="upper right")
sim_g.reset_meep()

# =================================================================== B. metal box with an aperture (2D), official metal-cavity-ldos.py
RES_M = 50
A_BOX, T_WALL, DPML_M = 1.0, 0.1, 1.0
SXY = 2.0 + 2 * DPML_M
FCEN_M = math.sqrt(0.5) / A_BOX                      # fundamental mode of the closed a x a box
DF_M = 0.2
WS = (0.2, 0.3, 0.4, 0.5)
T_MAX = 6000.0                                        # cap on the dft_ldos run (the official 2Q/f is not capped)
V_MODE = 0.25 * A_BOX ** 2                            # modal volume of the fundamental mode, analytic


def metal_box(w):
    return [mp.Block(mp.Vector3(A_BOX + 2 * T_WALL, A_BOX + 2 * T_WALL, mp.inf), material=mp.metal),
            mp.Block(mp.Vector3(A_BOX, A_BOX, mp.inf), material=mp.air),
            mp.Block(center=mp.Vector3(A_BOX / 2), size=mp.Vector3(2 * T_WALL, w, mp.inf), material=mp.air)]     # the aperture in the right wall


def make_sim(w, sources):
    return mp.Simulation(cell_size=mp.Vector3(SXY, SXY), geometry=metal_box(w), boundary_layers=[mp.PML(DPML_M)], sources=sources,
                         symmetries=[mp.Mirror(mp.Y)], resolution=RES_M)


src_M = [mp.Source(mp.GaussianSource(FCEN_M, fwidth=DF_M), component=mp.Ez, center=mp.Vector3())]
sim_lay = make_sim(0.3, src_M)
sim_lay.add_dft_fields([mp.Ez], FCEN_M, 0, 1, center=mp.Vector3(), size=mp.Vector3(2, 2))
annotated_layout(sim_lay, os.path.join(OUT, "01_layout.png"), dpml=DPML_M, figsize=(6.4, 6.0), axis_step=1.0,
                 title="part B: metal box 1 x 1 um, wall 0.1, aperture w = 0.3 (plot2D draws mp.metal white)",
                 params_text=f"a={A_BOX}, t={T_WALL}, res={RES_M}\nfcen=sqrt(0.5)/a={FCEN_M:.3f}", params_xy=(-1.9, 1.75),
                 pml_xy=(-1.9, -1.5), decay_point=None,
                 labels=[Label("Ez dipole at the center: Harminv probe and dft_ldos point", (0.02, 0.0), (-1.9, 1.2), step=3, color="red"),
                         Label("metal walls (mp.metal)", (-0.55, 0.3), (-1.9, 0.75), step=2, color="black"),
                         Label("aperture w: the only leak", (0.6, 0.0), (0.75, -0.9), step=2, color="black"),
                         Label("DFT Ez map (representative)", (-0.9, -0.9), (-1.9, -1.2), step=5, color="blue")])
sim_lay.reset_meep()

res_M = {}
t_b = time.time()
for w in WS:
    sim = make_sim(w, src_M)
    h = mp.Harminv(mp.Ez, mp.Vector3(), FCEN_M, DF_M)
    sim.run(mp.after_sources(h), until_after_sources=500)
    modes = [m for m in h.modes if m.Q > 0]
    m = max(modes, key=lambda mm: mm.Q)
    f, Q = float(m.freq), float(m.Q)
    sim.reset_meep()
    ldos_qv = Q / V_MODE / (2 * math.pi * f * math.pi * 0.5)          # 2Q / (pi w V), w = 2 pi f
    T_req = 2 * Q / f
    T_run = min(T_req, T_MAX)
    sim = make_sim(w, src_M)
    nfreq = 101
    df_spec = 8 * f / Q                                               # spectrum: +-4 linewidths around the Harminv frequency
    dft = sim.add_dft_fields([mp.Ez], f, 0, 1, center=mp.Vector3(), size=mp.Vector3(2, 2)) if w == 0.3 else None
    sim.run(mp.dft_ldos(f, df_spec, nfreq), until_after_sources=T_run)
    freqs = np.array(sim.ldos_freqs if hasattr(sim, "ldos_freqs") else np.linspace(f - 0.5 * df_spec, f + 0.5 * df_spec, nfreq))
    spec = np.array(sim.ldos_data)
    ez = sim.get_dft_array(dft, mp.Ez, 0) if dft is not None else None
    sim.reset_meep()
    ldos_f = float(spec[nfreq // 2])
    half = spec >= 0.5 * spec.max()
    fwhm = float(freqs[half].max() - freqs[half].min()) if half.sum() > 1 else float("nan")
    res_M[w] = {"f": f, "Q": Q, "ldos_qv": ldos_qv, "ldos_dft": ldos_f, "T_req": T_req, "T_run": T_run, "converged": T_run >= T_req,
                "spec_f": freqs, "spec": spec, "fwhm": fwhm, "Q_spec": f / fwhm if fwhm == fwhm else float("nan"), "ez": ez}
    print(f"B [w = {w}]: Harminv f {f:.5f}, Q {Q:.0f}; 2Q/f = {T_req:.0f} -> ran {T_run:.0f}{'' if T_run >= T_req else ' (CAPPED, under-converged)'}; "
          f"LDOS: Q/V estimate {ldos_qv:.4f}, dft_ldos {ldos_f:.4f}, ratio {ldos_f / ldos_qv:.3f}; spectrum FWHM {fwhm:.2e} -> Q {f / fwhm if fwhm == fwhm else float('nan'):.0f}")
print(f"B done in {time.time() - t_b:.0f} s")

fig = plt.figure(figsize=(13.5, 4.4))
ax = fig.add_subplot(1, 3, 1)
for w, c in zip(WS, ("tab:red", "tab:orange", "tab:green", "tab:blue")):
    r = res_M[w]
    ax.plot((r["spec_f"] - r["f"]) / r["f"] * 1e3, r["spec"] / r["spec"].max(), "-", color=c, lw=1.4, label=f"w = {w}: Q_Harminv {r['Q']:.0f}, Q_spectrum {r['Q_spec']:.0f}" + ("" if r["converged"] else " (capped)"))
ax.set_xlabel("(f - f_res) / f_res  [x 1e-3]"); ax.set_ylabel("LDOS / peak"); ax.set_title("dft_ldos spectrum around the resonance: width = f / Q", fontsize=9); ax.grid(alpha=0.3); ax.legend(fontsize=7)
ax = fig.add_subplot(1, 3, 2)
inv_w = [A_BOX / w for w in WS]
ax.semilogy(inv_w, [res_M[w]["ldos_qv"] for w in WS], "bo-", label="2Q / (pi w V)  (Harminv Q, analytic V)")
ax.semilogy(inv_w, [res_M[w]["ldos_dft"] for w in WS], "rs-", label="dft_ldos at f_res")
for w in WS:
    if not res_M[w]["converged"]:
        ax.annotate("under-converged\n(run capped)", (A_BOX / w, res_M[w]["ldos_dft"]), textcoords="offset points", xytext=(-70, -28), fontsize=7, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.set_xlabel("a / w"); ax.set_ylabel("LDOS at the resonance"); ax.set_title("narrower aperture: higher Q, higher LDOS", fontsize=9); ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=7)
ax = fig.add_subplot(1, 3, 3)
ez = res_M[0.3]["ez"]; lim = float(np.percentile(np.abs(ez), 96.0))     # clip: the source pixel dominates, and 3/4 of the map is outside the box
ax.imshow(np.real(ez).T, extent=[-1, 1, -1, 1], origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
ax.add_patch(plt.Rectangle((-0.5, -0.5), 1, 1, fill=False, color="k", lw=1.2)); ax.add_patch(plt.Rectangle((0.5, -0.15), 0.2, 0.3, fill=False, color="k", lw=1.0, ls="--"))
ax.set_title(f"Re(Ez) at f_res, w = 0.3: fundamental mode sin(pi x/a) sin(pi y/a)", fontsize=9); ax.set_xlabel("x [um]"); ax.set_ylabel("y [um]")
fig.suptitle("part B: a point dipole in a metal box with one aperture", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.93]); fig.savefig(os.path.join(OUT, "05_metal_ldos.png"), dpi=150); plt.close(fig)

# GIF: the box rings and leaks through the aperture (w = 0.4, monitor-free)
sim_g = make_sim(0.4, [mp.Source(mp.GaussianSource(FCEN_M, fwidth=0.4 * FCEN_M), component=mp.Ez, center=mp.Vector3())])
sim_g.init_sim()
vol_g = mp.Volume(center=mp.Vector3(), size=mp.Vector3(2, 2))
eps_g = sim_g.get_array(vol=vol_g, component=mp.Dielectric)
eps_g = np.where(np.isfinite(eps_g), eps_g, 100.0)
t0g = 5 / (0.4 * FCEN_M)
frames, times = record_frames(sim_g, vol_g, mp.Ez, t_start=t0g - 2 / (0.4 * FCEN_M), t_end=t0g + 40, n_frames=60)
animate_fields(frames, times, [-1, 1, -1, 1], os.path.join(OUT, "07_anim_metal.gif"), eps=eps_g, figsize=(5.4, 4.8), dpi=70, clip_percentile=99.0,
               points=[(0, 0, "red", "dipole")], lines=[((0.6, -0.2), (0.6, 0.2), "blue", "aperture w = 0.4")], title="metal box", legend_loc="lower left")
sim_g.reset_meep()

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f_:
        json.dump({"A": {"wl": WL, "n": N_CAV, "res_cyl": RES_CYL, "res_3d": RES_3D, "t": T_NORM.tolist(), "purcell_cyl": purcell_cyl.tolist(), "theory": theory.tolist(),
                         "err_cyl": err_cyl.tolist(), "cutoff": cutoff.tolist(), "median_err_away": float(np.median(err_cyl[~cutoff])), "max_err_away": float(err_cyl[~cutoff].max()),
                         "bulk_cyl": bulk_cyl, "bulk_3d": bulk_3d, "purcell_3d": {str(k): v for k, v in purcell_3d.items()}, "t_end_cyl": [float(x) for x in t_end_cyl]},
                   "B": {str(w): {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in r.items() if k != "ez"} for w, r in res_M.items()},
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f_, indent=2)
print(f"total {time.time() - t_all:.0f} s")
{% endhighlight %}
</details>

<details markdown="1">
<summary>Original execution record and environment</summary>

Unlike the excerpts in §4, the full script includes the cylindrical layout, r–z field images, spectrum plots, two GIFs, and result.json output. The shared plotting helper `blogfig.py` is in the same `code/` folder. Full code and helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**Execution output (run on 2026-10-23)**:
```
A (cyl): bulk LDOS 0.41625 (t_end 80); 21 thicknesses in 138 s; rel error vs Eq. 7 away from cutoffs: median 0.0094, max 0.0360 at t = 0.70; at the cutoffs: t=0.5: Meep 3.018 vs Eq.7 3.000, t=1.5: Meep 0.507 vs Eq.7 1.556, t=2.5: Meep 1.172 vs Eq.7 1.320
A (3D, res 48): bulk LDOS 3.22287 (t_end 80); t=1.0: 3D 0.9330 vs cyl 0.9120 vs Eq.7 0.9375, t=2.0: 3D 0.9788 vs cyl 0.9879 vs Eq.7 0.9844; 127 s
B [w = 0.2]: Harminv f 0.67403, Q 8060; 2Q/f = 23915 -> ran 6000 (CAPPED, under-converged); LDOS: Q/V estimate 4846.1525, dft_ldos 3499.1119, ratio 0.722; spectrum FWHM 1.20e-04 -> Q 5597
B [w = 0.3]: Harminv f 0.66875, Q 1271; 2Q/f = 3802 -> ran 3802; LDOS: Q/V estimate 770.3846, dft_ldos 685.5049, ratio 0.890; spectrum FWHM 5.05e-04 -> Q 1324
B [w = 0.4]: Harminv f 0.65692, Q 189; 2Q/f = 574 -> ran 574; LDOS: Q/V estimate 116.3766, dft_ldos 98.4505, ratio 0.846; spectrum FWHM 3.34e-03 -> Q 196
B [w = 0.5]: Harminv f 0.64648, Q 74; 2Q/f = 230 -> ran 230; LDOS: Q/V estimate 46.6641, dft_ldos 37.5608, ratio 0.805; spectrum FWHM 8.34e-03 -> Q 78
B done in 118 s
total 396 s
```

**Reproduction environment**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · command `python cavity_ldos.py` (about 6.6 min, single core)

</details>

### Official documentation and the next chapter

- [Local density of states tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/) · [planar_cavity_ldos.py](https://github.com/NanoComp/meep/blob/master/python/examples/planar_cavity_ldos.py) · [metal-cavity-ldos.py](https://github.com/NanoComp/meep/blob/master/python/examples/metal-cavity-ldos.py)
- [`dft_ldos` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#ldos-spectra) · [`Harminv`](https://meep.readthedocs.io/en/latest/Python_User_Interface/#harminv) · [cylindrical coordinates](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/)
- I. Abram et al., "Spontaneous emission control in semiconductor microcavities with metallic or Bragg mirrors," IEEE J. Quantum Electron. 34, 71 (1998)
- Previous: [10 · 3D radiation patterns of a point source]({{ site.baseurl }}/en/dipole-pattern-3d/) · Next: [12 · A ring that confines light]({{ site.baseurl }}/en/ring-resonator/)
