---
layout: lesson
date: 2026-10-23
title: "Meep Example 12 · A ring that confines light — Harminv, Q, FSR, and solve_cw cross-checks"
title_en: "Meep Example 12 · A ring that traps light — Harminv, Q, the free spectral range, and a solve_cw cross-check"
lang: en
translation_key: ring-resonator
series: meep-examples
part: 12
permalink: /en/ring-resonator/
lesson_title: "How long does light remain trapped in a ring?"
lesson_summary: "Read resonance frequency, Q, and mode spacing from the ringing after a pulse ends, and check which numbers are reliable."
lesson_goals:
  - "Distinguish resonance frequency, Q, and FSR."
  - "Change the Harminv observation time to check the reliability of Q."
  - "Explain why frequency and Q converge differently."
lesson_prerequisites: "Familiarity with resonance and linewidth in chapter 11 and bend loss in chapter 05 is helpful."
level: intermediate
runtime: "4 min (mpirun -np 4)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#modes-of-a-ring-resonator"
tags: [meep, fdtd, ring-resonator, harminv, q-factor, fsr, solve_cw, frequency-domain]
image: /assets/meep/12/03_modes.png
excerpt: "post 11 measured how much a dipole emits between two mirrors. On a chip the trap is a dielectric ring. This post asks the first questions about any resonator: at which frequencies does it trap light, for how long (Q), how far apart are the resonances (FSR), and what does each trapped mode look like. Official `ring.py` (Harminv on the ringing field), one narrow-band run per mode, and official `solve-cw.py` (the same mode solved in the frequency domain)."
---
<h2 id="observe">1. Observe first</h2>

Does light disappear immediately after a short pulse in a ring is switched off? Look for **ringing around the ring and light leaking outward** in the animation. Instead of the two mirrors in chapter 11, a dielectric waveguide is bent into a circle to confine light.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/12/05_anim_ring.gif' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/12/05_anim_ring.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/12/05_anim_ring.gif' | relative_url }}" data-static-src="{{ '/assets/meep/12/03_modes.png' | relative_url }}" alt="Electric field ringing in the ring and leaking outward after a broadband pulse" loading="eager"></a>
  <figcaption>Three modes continue ringing after the pulse ends, producing beats. Lower modes leak toward the PML more strongly.</figcaption>
  <button type="button" class="animation-toggle" hidden>Pause animation</button>
</figure>

**Our question:** which frequencies remain, for how long, and how can we verify the answer? These measurements are for a **2D Ez, lossless, isolated ring**. They exclude waveguide coupling loss and do not give the Q of a 3D device.

<details markdown="1">
<summary>English summary</summary>

- **What**: post 11 measured how much a dipole emits between two mirrors. On a chip the trap is a dielectric ring. This post asks the first questions about any resonator: at which frequencies does it trap light, for how long (Q), how far apart are the resonances (FSR), and what does each trapped mode look like. Official `ring.py` (Harminv on the ringing field), one narrow-band run per mode, and official `solve-cw.py` (the same mode solved in the frequency domain).
- **Result**: a broadband pulse in the band 0.10–0.20 excites three Ez modes; at the official resolution 10 Harminv gives f = 0.1181 / 0.1472 / 0.1753 with Q = 81 / 317 / 1675 (tutorial: 0.1181 / 0.1472 / 0.1752, Q 81 / 316 / 1677). The frequencies move by less than 0.3% between resolution 10 and 30; the Q of the sharpest mode goes 1675 → 2132 → 1610, not monotonically. The spacing 0.0292 / 0.0283 matches 1/(n_g L) with n_g = 3.69, and the three modes carry m = 3, 4, 5 wavelengths around the ring. `solve_cw` reproduces the time-domain DFT of the f = 0.118 mode to 0.40% relative L2 (|Ez| correlation 0.99998) after a complex scale factor.
- **Takeaway**: Harminv turns 300 time units of ringing into frequencies and Q without waiting for the field to decay, but Q converges much more slowly with resolution than the frequency does. One mode at a time needs a source as narrow as the mode. The frequency-domain solver and the time-domain pulse are two routes to the same steady state, and agreeing to a percent is what "the same mode" means.
- **Code**: full script at the bottom, ~4 min (mpirun -np 4).
</details>

<details markdown="1">
<summary>Where are resonators used?</summary>

The metal box in chapter 11 controlled Q through one aperture. On a chip, a dielectric waveguide can instead form a ring, confining circulating light through total internal reflection. Bend radiation, introduced in chapter 05, is the only loss in this model. After a pulse, which frequencies remain, how long do they last, and how far apart are they? We measure them using Harminv, which decomposes time-domain ringing, and solve_cw, which directly computes the frequency-domain steady state, then compare the results.

### Where is this useful?

Ring resonators are widely used in silicon photonics. Resonant frequency, Q, and FSR translate directly into device specifications.

| Application | Quantity used here | What comes next |
|---|---|---|
| Wavelength filters, add-drop multiplexers (WDM), ring modulators | Resonant frequency and FSR (channel spacing), Q (linewidth and passband) | Chapter 30: GDS rings |
| Biological and gas sensors | Resonance shift Δf relative to linewidth f/Q sets a detection scale | Chapter 13: disk resonators |
| Microring and microdisk lasers, frequency combs | Q and mode volume (threshold), FSR (comb spacing) | Chapter 22: nonlinearity |
| Measurement procedures for resonant structures | Harminv for f and Q, narrowband excitation for one mode, solve_cw for steady state | Chapter 26: photonic-crystal cavities |
</details>

<h2 id="predict">2. Predict the results</h2>

As resolution increases from 10 → 20 → 30, **will frequency and Q both converge smoothly?** Choose first.

<fieldset class="prediction">
<legend>Predict how the two quantities converge as resolution increases.</legend>
<label><input type="radio" name="ring-prediction" value="together"> Once frequency stabilizes, Q stabilizes by a similar relative amount.</label>
<label><input type="radio" name="ring-prediction" value="different"> Q can still vary substantially even when frequency is stable.</label>
</fieldset>

<details markdown="1">
<summary>Check your prediction</summary>

**The second answer is correct.** The third-mode frequency is 0.17525 → 0.17564 → 0.17572, but Q is 1675 → 2132 → 1610. Because Q measures small radiation losses, it is more sensitive to how the grid represents the boundary. The measured table below shows this difference.

</details>

<h2 id="understand">3. Understand the principle</h2>

{% include chapter-illustration.html %}

<figure class="lesson-figure">
<svg viewBox="0 0 300 245" role="img" aria-labelledby="ring-principle-title ring-principle-desc" xmlns="http://www.w3.org/2000/svg">
  <title id="ring-principle-title">The principle of ring resonance</title>
  <desc id="ring-principle-desc">A wave reinforces itself when it returns in phase after a circuit around the ring. Outward leakage limits its lifetime.</desc>
  <rect width="300" height="245" rx="12" fill="#f1f7f8"/>
  <circle cx="144" cy="115" r="70" fill="none" stroke="#d5e5e9" stroke-width="34"/>
  <circle cx="144" cy="115" r="70" fill="none" stroke="#157c8c" stroke-width="3" stroke-dasharray="9 5"/>
  <path d="M144 45 A70 70 0 0 1 214 115" fill="none" stroke="#157c8c" stroke-width="5"/>
  <path d="M205 105 L214 121 L222 104" fill="none" stroke="#157c8c" stroke-width="4"/>
  <circle cx="214" cy="115" r="6" fill="#bb4f39"/>
  <path d="M213 65 L249 38 M242 39 L250 37 L248 46" fill="none" stroke="#bb4f39" stroke-width="2.5"/>
  <text x="144" y="108" text-anchor="middle" font-size="17" fill="#183744">One full circuit</text>
  <text x="144" y="131" text-anchor="middle" font-size="15" fill="#183744">In phase: reinforcement</text>
  <text x="210" y="25" font-size="16" fill="#8c3d2e">Radiation loss</text>
  <text x="144" y="222" text-anchor="middle" font-size="14" fill="#183744">Resonance: m wavelengths fit around L</text>
</svg>
<figcaption>Conceptual diagram. The dashed line indicates the round-trip path; arrows show propagation and leakage. This is not a measured electric-field distribution or a quantitative loss map.</figcaption>
</figure>

A wave reinforces itself when it returns in phase after one circuit. Only **resonant frequencies** compatible with the circumference remain. **Q** describes how slowly that ringing decays, and **FSR** describes the separation between neighboring resonances.

`Harminv` finds frequencies and decay rates from **the signal remaining at one point after the source turns off**. Even for high Q, it need not wait for the full decay, but its estimation error must be checked. Basic requirements are **positive Q, a mode inside the observation band**, and `error < f/(2Q)`. The three modes here have errors below 2% of that threshold.

<details markdown="1">
<summary>Resonance equations, symbols, and quantitative predictions</summary>

Light reinforces itself only when its phase matches after one circuit. Resonance requires an integer number $m$ of wavelengths around circumference $L=2\pi R_{\mathrm{mid}}$; the frequency spacing between adjacent $m$ is the FSR. The group index $n_g$ includes dispersion and differs from the material index. With only bend radiation as loss, higher-frequency light is confined more tightly and Q rises.

$$
m\,\lambda_m = n_{\mathrm{eff}}L,\qquad \mathrm{FSR}=f_{m+1}-f_m\approx\frac{1}{n_g L},\qquad
Q=\frac{f}{\Delta f}=\frac{\mathrm{Re}\,\omega}{-2\,\mathrm{Im}\,\omega}
$$

Harminv decomposes the field recorded at one point after the source ends into decaying sinusoids, $\sum_k a_k e^{-i\omega_k t}$. The real part of complex $\omega_k$ gives the resonant frequency, the imaginary part gives the decay rate, and their ratio determines Q. A 300-time-unit record can identify modes with lifetimes of thousands of time units, but the returned `error` must be smaller than the imaginary part for that Q to be reliable.

The frequency-domain solver tackles the same problem differently. With a continuous-wave source, it iteratively solves $\nabla\times\nabla\times\mathbf E-\omega^2\varepsilon\mathbf E=i\omega\mathbf J$ using BiCGSTAB-L to obtain the steady state directly. It should yield the same mode as a time-domain pulse plus DFT, but source normalization and global phase differ, so compare after fitting one complex constant.

| Symbol | Meaning | Code variable |
|------|----|-----------|
| $R$, $w$, $n$ | Inner radius 1, width 1, index 3.4 (unit a = 1 µm) | `R`, `W`, `N_RING` |
| $L$ | Mean circumference $2\pi(R+w/2)$ = 9.42 | `L_RING` |
| $f_{\mathrm{cen}}$, $df$ | Broadband pulse 0.15 ± 0.05 | `FCEN`, `DF` |
| $m$ | Azimuthal order (wavelengths around the circumference) | `m_az` |
| $Q$, error | Harminv output | `h.modes[k].Q`, `.err` |
| tol | solve_cw iteration stopping criterion | `TOLS` |
| $\alpha$ | Complex constant aligning CW and DFT | `alpha` |

**Assumptions and validity**: 2D Ez, lossless dielectric, unit a = 1 µm (resonant wavelengths 5.7~8.5 µm). Multiplying all lengths by 0.27 moves the geometry toward telecommunications wavelengths. This isolated ring is not coupled to a waveguide, so Q reflects only bend radiation.

### Predict before viewing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| Modes in the 0.10~0.20 band | 3 | FSR ≈ 1/(3.5 × 9.42) ≈ 0.03 across a 0.1 band |
| Resonant frequencies (res 10) | 0.118 / 0.147 / 0.175 | Official tutorial |
| Q trend | Increases with frequency | Weak confinement produces stronger bend radiation |
| Frequency change, res 10 → 30 | Within 1% | More than 20 cells per wavelength |
| Highest-Q change, res 10 → 30 | Tens of percent | Notes: 2515 at res 25; official res 10: 1677 |
| Azimuthal order m | Three consecutive integers between 3~6 | $m\approx n_{\mathrm{eff}}Lf$, $n_{\mathrm{eff}}<3.4$ |
| solve_cw error | Decreases monotonically as tolerance tightens | Tutorial |
| CW vs time-domain DFT | L2 within 2%, correlation above 0.999 | Notes: 1.2%, 0.99992 |

**Decision criteria**: if FSR differs from the hand estimate by more than 30%, check circumference and index. Do not report a Q if Harminv error exceeds the imaginary part. A CW–DFT mismatch above 10% suggests mismatched source symmetry or frequency.

</details>

<h2 id="run">4. Experiment by changing one variable</h2>

Change **only the time over which Harminv observes the ringing**. Place `ring_resonator.py` and the shared helper `blogfig.py` together in the repository’s `code/` folder and run them in a Meep environment. The full code is also in the references below. A single-CPU run takes about 10 minutes; the original 4-minute record used 4 MPI processes.

```bash
OMP_NUM_THREADS=1 python ring_resonator.py
```

1. Run the original `T_HARMINV = 300.0` and record f, Q, and error for every mode.
2. Change only that value to `600.0` and run again. Keep geometry, resolution, and source fixed.
3. Match modes by frequency and compare error against `f/(2Q)`. Increasing observation time and increasing spatial resolution test different error sources.

**Decision criterion:** record how much frequency and Q move after increasing observation time. Longer observation alone does not establish accurate Q. The numbers below are the original **300-time-unit** results, not new measurements at 600.

<details markdown="1">
<summary>Inspect the simulation layout and parameters</summary>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/12/01_layout.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/12/01_layout.png' | relative_url }}" alt="Ring, source, Harminv probe, and PML layout" loading="lazy"></a>
<figcaption>A 16 × 16 cell (a = 1 µm), with PML 2. The ring has n = 3.4, inner radius 1, and width 1. The red point is both the Ez point source and Harminv probe at (r + 0.1, 0); there is no flux monitor. Circled numbers refer to the code steps below.</figcaption>
</figure>

| Parameter | Value | Why this value? | Effect of changing it |
|----------|-----|-------------|--------|
| Ring | n 3.4, R 1, w 1 | Official ring.py | Changing circumference changes FSR |
| Pulse | fcen 0.15, df 0.1 | Three modes in 0.10~0.20 | A narrower band can miss modes |
| Source position | (R + 0.1, 0) | Away from the center to excite the relevant Ez modes | A symmetry-incompatible source position can exclude odd modes |
| Harminv window | 300 after the source ends | Official value; resolves Q in the thousands | Too short a window increases error |
| Resolution | 10 (official), 20, 30 | Convergence check | Q is resolution-sensitive (§5) |
| Mode images | df 0.01, DFT at f_k | Excludes neighboring modes 0.03 away | df 0.1 superposes three modes |
| solve_cw | f 0.118, tol 1e-8/1e-10/1e-12, maxiters 10000, L 10 | Official solve-cw.py | Default L = 2 converges more slowly |
| CW source symmetry | Amplitudes +1/−1 at (±(R+0.1), 0), X odd | Parity of the 0.118 mode | Wrong parity solves a different mode |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/12/00_source.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/12/00_source.png' | relative_url }}" alt="Time waveform and spectrum of the broadband Gaussian pulse" loading="lazy"></a>
<figcaption>Broadband pulse waveform and spectrum (a units). Width 10, peak t0 = 50. The 300-time-unit Harminv window starts after the source has turned off.</figcaption>
</figure>

**Differences from the course notebooks**: this topic is outside the course scope. The 0710 note in 10_sources used one resolution, res 25; the 0722 note used five solve_cw tolerances. This chapter uses three resolutions (10/20/30) to show the different convergence rates of frequency and Q, then reruns each mode with narrowband excitation to count its azimuthal order m.

</details>

<details markdown="1">
<summary>Follow the code in seven steps</summary>

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → run and stopping conditions → postprocessing.
> Here step ⑤ uses `Harminv` (a time signal at one point) and `solve_cw`, rather than a flux monitor.

### ① Units and parameters — which values are fixed?

```python
N_RING, W, R = 3.4, 1.0, 1.0                # index, ring width, inner radius  [a = 1 um]
PAD, DPML = 4.0, 2.0
SXY = 2 * (R + W + PAD + DPML)              # 16 x 16
FCEN, DF = 0.15, 0.1                        # broadband pulse covering 0.10..0.20
T_HARMINV = 300.0                           # ringing window after the source (official)
L_RING = 2 * np.pi * (R + 0.5 * W)          # mean circumference, for the FSR estimate
```

- **What**: the official values are retained. Circumference $L$ is used to estimate FSR by hand.
- **Why**: estimating the mode count from $1/(n_g L)$ before the run helps reveal modes missed by Harminv.
- **If wrong**: placing PML too close to the ring (small pad) allows reflected radiation to perturb Q.

### ② Materials and geometry — a ring from two cylinders

```python
geometry = [mp.Cylinder(radius=R + W, material=mp.Medium(index=N_RING)),     # later objects win: outer dielectric first ...
            mp.Cylinder(radius=R)]                                             # ... then the air hole
```

- **What**: overlay a dielectric cylinder with an air cylinder to make a ring.
- **Why**: later Meep objects overwrite earlier ones. Reversing their order produces a dielectric disk.
- **If wrong**: remember the same ordering rule in chapter 11’s box: metal → air → aperture.

### ③ Sources — one broadband pulse, three narrowband pulses, and two CW sources

```python
mp.Source(mp.GaussianSource(FCEN, fwidth=DF), mp.Ez, SRC_PT)                    # A: broadband, every mode in the band
mp.Source(mp.GaussianSource(f0, fwidth=0.01), mp.Ez, SRC_PT)                    # B: one mode at a time
[mp.Source(mp.ContinuousSource(F_CW), mp.Ez, mp.Vector3(R + 0.1)),             # C: continuous wave, antisymmetric pair
 mp.Source(mp.ContinuousSource(F_CW), mp.Ez, mp.Vector3(-(R + 0.1)), amplitude=-1)]
```

- **What**: three source configurations serve different purposes. A excites all modes at once, B isolates them individually, and C solves the steady state.
- **Why**: a single-mode image needs a band (0.01) that excludes neighbors 0.03 away. Changing only the Harminv center does not change the source spectrum. The official ring-mode-overlap.py example illustrates this pitfall and Meep emits a warning.
- **If wrong**: CW sources of the same sign select an X-even mode, which does not match the time-domain 0.118 mode.

### ④ Simulation and boundaries — symmetry and complex fields

```python
sim = mp.Simulation(cell_size=mp.Vector3(SXY, SXY), geometry=geometry, sources=sources, resolution=res,
                    symmetries=[mp.Mirror(mp.Y)], boundary_layers=[mp.PML(DPML)])                                   # A, B
sim = make_sim(RES_IMG, src_cw, (mp.Mirror(mp.X, phase=-1), mp.Mirror(mp.Y, phase=+1)), force_complex_fields=True)  # C
```

- **What**: PML 2 on all sides. A and B use Y mirror symmetry (the source is on the x axis); C uses X odd, Y even, and complex fields.
- **Why**: `solve_cw` returns amplitude and phase, requiring complex fields. Symmetry reduces the computational domain by 1/2 or 1/4 and selects mode parity.
- **If wrong**: as in chapter 11, setting every phase to +1 solves modes of a different parity.

### ⑤ Monitors — Harminv, DFT, and solve_cw

```python
h = mp.Harminv(mp.Ez, SRC_PT, FCEN, DF)                   # A: time signal at one point -> (f, Q, amp, err) per mode
sim.run(mp.after_sources(h), until_after_sources=T_HARMINV)
modes = [(m.freq, m.Q, abs(m.amp), m.err) for m in h.modes if m.Q > 0]

dft = sim.add_dft_fields([mp.Ez], f0, 0, 1, where=NONPML)  # B: steady-state field at the resonance

sim.init_sim(); sim.solve_cw(tol, MAXITERS, L_BICG)        # C: frequency-domain solve, then read the field
ez_cw = sim.get_array(vol=NONPML, component=mp.Ez)
```

- **What**: Harminv is a step function receiving the time signal at one point. `after_sources` records only after excitation ends. B’s DFT gives the steady-state field at one resonance. C reads the solved field with `get_array`.
- **Why**: resonance frequencies and decay information are present in a point time signal. A spatial monitor is needed only to view mode shapes.
- **If wrong**: a Harminv probe at a mode node cannot see that mode. A probe at the source can observe the modes excited there.

### ⑥ Run — observation windows, decay, and iteration stopping

```python
sim.run(mp.after_sources(h), until_after_sources=300)                                              # A: fixed window (official)
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, SRC_PT, 1e-6))                  # B
sim.solve_cw(tol, 10000, 10)                                                                        # C
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(R + 0.1523), 1e-8))   # C, time-domain comparator
```

- **What**: A uses the official fixed window. B and C’s time-domain runs use decay criteria. C’s solver uses tolerance and a maximum iteration count.
- **Why**: Harminv does not wait for complete decay; this is its advantage. A DFT must capture the field tail for accuracy, so higher-Q modes require longer runs (chapter 11’s 2Q/f).
- **If wrong**: a loose decay threshold in B leaves a truncated DFT and can retain neighboring-mode contamination in the image.

### ⑦ Postprocessing — FSR, m, and complex alignment

```python
fsr = np.diff(freqs); ng = 1 / (fsr.mean() * L_RING)                      # group index from the spacing
ring_vals = ez[ix, iy]                                                     # DFT field sampled on the mid-circle
m_az = int(np.argmax(np.abs(np.fft.rfft(np.real(ring_vals)))[1:]) + 1)   # dominant azimuthal order

alpha = np.vdot(ez_td, ref) / np.vdot(ez_td, ez_td)                        # best-fit complex scale
err_td = np.linalg.norm(alpha * ez_td - ref) / np.linalg.norm(ref)
```

- **What**: infer $n_g$ from resonance spacing, Fourier-transform the field along the ring’s midline to count $m$, then align CW and DFT by a complex constant before calculating L2 error.
- **Why**: source normalization (CW versus pulse DFT) and global phase are arbitrary for this comparison. Remove them to expose the difference between solvers.
- **If wrong**: without $\alpha$, L2 can exceed 100%, incorrectly treating the same mode with a different global phase as a different mode.

> **Pitfall**: Harminv can return spurious modes with negative Q or large error. Keep positive-Q modes inside the band, and compare error to the imaginary part $f/(2Q)$. All three modes here have error below 2% of that quantity.

</details>

<h2 id="interpret">5. Interpret the results</h2>

First read the third mode’s **frequency and Q side by side**. From resolution 10 → 30, frequency changes by at most 0.3%, while Q varies nonmonotonically. Thus **frequency is stable, but the absolute Q cannot yet be called converged.**

<figure class="lesson-figure">
<a href="{{ '/assets/meep/12/02_harminv.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/12/02_harminv.png' | relative_url }}" alt="Resonant frequency, Q, and FSR compared across resolutions" loading="lazy"></a>
<figcaption>Frequency barely moves on the left, while Q changes substantially. The right shows measured FSR, the hand estimate, and each mode’s azimuthal order m. Select the figure to enlarge it.</figcaption>
</figure>

| res | $f_1$ / $Q_1$ | $f_2$ / $Q_2$ | $f_3$ / $Q_3$ |
|---|---|---|---|
| 10 (official) | 0.11810 / 81 | 0.14716 / 317 | 0.17525 / 1675 |
| 20 | 0.11818 / 79 | 0.14736 / 342 | 0.17564 / 2132 |
| 30 | 0.11822 / 79 | 0.14740 / 336 | 0.17572 / 1610 |

| Measured FSR | $n_g = 1/(\mathrm{FSR}\,L)$ | Ring material index |
|---|---|---|
| 0.0292 / 0.0283 | 3.69 | 3.4 |

**What FSR tells us:** spacings 0.0292 / 0.0283 give group index 3.69, which is not the same quantity as material index 3.4. The modes below fit m = 3, 4, 5 wavelengths around the ring.

<details markdown="1">
<summary>View mode shapes and the frequency-domain cross-check</summary>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/12/03_modes.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/12/03_modes.png' | relative_url }}" alt="Electric fields of the three resonant modes and their azimuthal oscillation counts" loading="lazy"></a>
<figcaption>Top: narrowband DFT at each frequency. Bottom: Re(Ez) on the circle r = 1.5, with m wavelengths around the circumference.</figcaption>
</figure>

| Mode | f | λ [a] | Q (res 20) | m | $m/(n L f)$ |
|---|---|---|---|---|---|
| 1 | 0.1182 | 8.46 | 79 | 3 | 0.79 |
| 2 | 0.1474 | 6.79 | 342 | 4 | 0.85 |
| 3 | 0.1756 | 5.69 | 2132 | 5 | 0.89 |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/12/04_solve_cw.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/12/04_solve_cw.png' | relative_url }}" alt="solve_cw tolerance comparison and electric-field comparison with time-domain DFT" loading="lazy"></a>
<figcaption>Left: errors at different tolerances. The frequency-domain solution in the center and time-domain DFT on the right are compared after matching normalization and global phase with a complex constant.</figcaption>
</figure>

| Quantity | Value |
|---|---|
| solve_cw runtime at tol 1e-8 / 1e-10 / 1e-12 | 5 / 6 / 7 s (4 processes) |
| Relative error at tol 1e-8, 1e-10 (vs 1e-12) | 4.2e-7, 1.1e-10 |
| Time-domain DFT vs CW, L2 after complex alignment | 0.40% |
| \|Ez\| correlation | 0.99998 |
| Time-domain runtime (decay 1e-8) | 2001 time units |

</details>

**Agreement between solvers:** for the f = 0.118 mode, `solve_cw` and time-domain DFT agree to relative L2 0.40% after complex alignment, with amplitude correlation 0.99998. This does not establish Q convergence for every mode.

<details markdown="1">
<summary>The original eight predictions, convergence, and interpretation</summary>

### Compare with the predictions

| Quantity | Prediction (§2) | Simulation | Assessment |
|--------|-------------|-----------|------|
| Mode count | 3 | 3 | Pass |
| Resonant frequencies (res 10) | 0.118 / 0.147 / 0.175 | 0.1181 / 0.1472 / 0.1753 | Pass |
| Q trend | Higher at higher frequency | 81 → 317 → 1675 | Pass |
| Frequency change, res 10→30 | Within 1% | At most 0.3% | Pass |
| Highest-Q change, res 10→30 | Tens of percent | 1675 → 2132 → 1610 (nonmonotonic, ±30%) | Pass (not monotonic) |
| Azimuthal order m | Consecutive integers, 3~6 | 3, 4, 5 | Pass |
| solve_cw error | Monotonically decreasing | 4.2e-7, 1.1e-10 | Pass |
| CW vs DFT | L2 within 2%, correlation above 0.999 | 0.40%, 0.99998 | Pass |

All eight predictions had the correct trend; the numbers reveal two details. First, resolution dependence of Q is not monotonic. The sharpest mode has Q 1675 at res 10, 2132 at 20, and 1610 at 30. Bend radiation is a small leakage at the outer ring boundary, sensitive to how the grid cuts that boundary (staircasing), so increasing resolution need not move Q in one direction. Frequency stays within 0.3% across all three resolutions. Second, $m/(n L f)$ is 0.79, 0.85, 0.89: below 1 and approaching it at higher frequency. The mode extends outside the ring, lowering its effective index below 3.4; tighter confinement at higher frequency brings it toward the material value. Group index $n_g$ = 3.69 inferred from FSR exceeds the material index because of dispersion, $n_g = n_{\mathrm{eff}} + f\,dn_{\mathrm{eff}}/df$. Single-mode runs grow longer with Q. The Q 2132 mode needed 19110 time units to reach decay 1e-6. DFT took about 60 times the 300-unit Harminv window. All three solve_cw tolerances completed in seconds, agreeing with time-domain DFT to 0.4%.

### Convergence

| Variable | Values | Result | Notes |
|---|---|---|---|
| Resolution (Harminv) | 10 / 20 / 30 | $f_3$: 0.17525 / 0.17564 / 0.17572, $Q_3$: 1675 / 2132 / 1610 | Frequency is stable at 20 cells/wavelength; Q is not yet converged |
| Harminv window | 300 (official) | error ≤ 1e-5, below 2% of imaginary part f/(2Q) | Longer windows reduce estimation error |
| solve_cw tolerance | 1e-8 / 1e-10 / 1e-12 | 4.2e-7, 1.1e-10 | Notes: nonmonotonic behavior near 1e-11 |

### What the results do and do not establish

- Established: this ring (2D, n 3.4, R 1, w 1) has three Ez modes in 0.10~0.20, with frequencies already within 1% at resolution 10. Their spacing agrees with $1/(n_gL)$ for $n_g$ 3.69. The f = 0.118 mode agrees between time and frequency domains within 0.40%.
- Not established: absolute Q, which remains unconverged at resolution 30 and was estimated with a 300-unit Harminv window; Q of a waveguide-coupled ring, which includes coupling loss; values for a 3D disk; or material dispersion after scaling to telecommunications wavelengths.

</details>

<details markdown="1">
<summary>What to check when results differ from expectations</summary>

| Symptom | Cause | Fix |
|------|------|----------|
| Harminv returns only one mode | Source band too narrow or probe at a node | Widen df and place the probe at the source |
| Q in the tens of thousands, with large error | Spurious mode | Keep only Q > 0, error < f/(2Q), and in-band modes |
| Neighboring modes contaminate the image | Imaging-source bandwidth exceeds FSR | Use df < FSR/3 |
| Changing only the Harminv center has no effect | Source spectrum is unchanged | Recreate the source (see the warning in official ring-mode-overlap.py) |
| solve_cw does not converge | L = 2 or missing complex fields | L = 10, `force_complex_fields=True` |
| CW and DFT differ by 100% | Normalization/phase unaligned, or parity differs | Align with complex α and check source signs |
| Q changes greatly at higher resolution | Q converges slowly | Report Q together with a resolution ladder |

</details>

<details markdown="1">
<summary>Further experiments</summary>

| Change | Expected effect | Quantity to check |
|---------|----------|------------|
| Ring width w 1 → 0.5 | Weaker confinement lowers Q; smaller circumference raises FSR | f, Q, FSR |
| Move source to the y axis at (0, R + 0.1) | Check compatibility with the existing Y symmetry first | Mode count and source symmetry |
| Harminv window 300 → 1000 | Smaller error and more stable Q | error, Q |
| res 40 | Check convergence of Q_3 | Q_3 |
| ω–2ω overlap (ring-mode-overlap.py) | Spatial overlap of the 0.118 and 0.236 modes around 0.05 | Normalized overlap |

</details>

<h2 id="check">6. Check your understanding</h2>

1. If frequency is stable within 0.3% but Q is 1675 → 2132 → 1610, what should you report?
2. Are increasing the Harminv observation time and increasing resolution the same validation?

<details markdown="1">
<summary>Check the answers and reasoning</summary>

1. Report stable frequency but an absolute Q that is not yet converged. Include resolution, observation time, and error.
2. No. Observation time tests mode-estimation error in the time signal; resolution tests representation of geometry and fields on a spatial grid. Small Harminv error alone does not guarantee spatial convergence.

</details>

<h2 id="reference">7. Code and references</h2>

**Official examples**: [Ring resonator in the Basics tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#modes-of-a-ring-resonator) · [Frequency-domain solver tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Frequency_Domain_Solver/) · scripts [ring.py](https://github.com/NanoComp/meep/blob/master/python/examples/ring.py) · [solve-cw.py](https://github.com/NanoComp/meep/blob/master/python/examples/solve-cw.py).

### Full code

<details markdown="1">
<summary>Full code/ring_resonator.py (expand)</summary>
{% highlight python %}
"""Meep Example 12 - A ring that traps light: Harminv resonances, Q, FSR, and a solve_cw cross-check.

Post 11 measured how much a dipole emits between two mirrors. On a chip the trap is a dielectric ring, and
the first questions about any resonator are: at which frequencies does it trap light, for how long (Q),
how far apart are the resonances (FSR), and what does each trapped mode look like.
  A. Official ring.py: a broadband Ez pulse inside the ring, Harminv on the ringing field after the source
     stops -> frequencies and Q of the modes in the band. Repeated at resolution 10 (official), 20, 30:
     frequencies converge fast, Q of the sharpest mode does not.
  B. Each resonance imaged alone: a narrow-band pulse at that frequency and a DFT field at the same frequency.
     The number of azimuthal lobes m is counted from the field along the ring.
  C. Official solve-cw.py: the same mode at f = 0.118 solved in the frequency domain (continuous source,
     BiCGSTAB-L), tolerance sweep, and compared with a time-domain DFT of the same mode after complex alignment.
Written to run under MPI: collective calls (run, get_array, solve_cw) on every rank, plotting on the master only.

Run:  python ring_resonator.py        (~10 min on one core, ~4 min with mpirun -np 4)
Out:  00_source.png, 01_layout.png, 02_harminv.png, 03_modes.png, 04_solve_cw.png, 05_anim_ring.gif, result.json
      (-> ../assets/12/)
"""
import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "12")
os.makedirs(OUT, exist_ok=True)
MASTER = mp.am_master()
t_all = time.time()


def say(*a):
    if MASTER:
        print(*a, flush=True)


# ---------------------------------------------------------------- (1) parameters (official ring.py; a = 1 um)
N_RING, W, R = 3.4, 1.0, 1.0                # index, ring width, inner radius  [a = 1 um]
PAD, DPML = 4.0, 2.0
SXY = 2 * (R + W + PAD + DPML)              # 16 x 16
FCEN, DF = 0.15, 0.1                        # broadband pulse covering 0.10..0.20
T_HARMINV = 300.0                           # ringing window after the source (official)
SRC_PT = mp.Vector3(R + 0.1)                # inside the ring, off the symmetry axes of the modes
RES_LIST = (10, 20, 30)                     # official 10, plus two finer
RES_IMG = 20                                # resolution for mode images, solve_cw, GIF
R_MID = R + 0.5 * W
L_RING = 2 * np.pi * R_MID                  # mean circumference
NONPML = mp.Volume(center=mp.Vector3(), size=mp.Vector3(SXY - 2 * DPML, SXY - 2 * DPML))
EXT = [-(0.5 * SXY - DPML), 0.5 * SXY - DPML, -(0.5 * SXY - DPML), 0.5 * SXY - DPML]

geometry = [mp.Cylinder(radius=R + W, material=mp.Medium(index=N_RING)),     # later objects win: outer dielectric first ...
            mp.Cylinder(radius=R)]                                             # ... then the air hole


def make_sim(res, sources, symmetries=(mp.Mirror(mp.Y),), **kw):
    return mp.Simulation(cell_size=mp.Vector3(SXY, SXY), geometry=geometry, sources=sources, resolution=res,
                         symmetries=list(symmetries), boundary_layers=[mp.PML(DPML)], **kw)


# ================================================================ A. Harminv at three resolutions
harm = {}
t_a = time.time()
for res in RES_LIST:
    src = [mp.Source(mp.GaussianSource(FCEN, fwidth=DF), mp.Ez, SRC_PT)]
    sim = make_sim(res, src)
    if res == RES_LIST[0]:
        annotated_layout(sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(6.6, 6.2), axis_step=2.0,
                         title="ring resonator (res 10 shown): n = 3.4, inner radius 1, width 1, a = 1 um",
                         params_text=f"n={N_RING}, r={R}, w={W}\nfcen={FCEN}, df={DF}\nres {RES_LIST}", params_xy=(-7.6, 7.0),
                         pml_xy=(-7.6, -6.6), decay_point=None,
                         labels=[Label("Ez point source at (r + 0.1, 0): every Ez mode in the band", (R + 0.1, 0.0), (-7.6, 4.6), step=3, color="red"),
                                 Label("ring = dielectric cylinder minus air cylinder", (-R_MID * 0.7, R_MID * 0.7), (-7.6, 3.2), step=2, color="black"),
                                 Label("Harminv probe = the source point, after the source", (R + 0.1, -0.3), (-5.2, -4.2), step=5, color="blue")])
    h = mp.Harminv(mp.Ez, SRC_PT, FCEN, DF)
    sim.run(mp.after_sources(h), until_after_sources=T_HARMINV)
    modes = sorted([(m.freq, m.Q, abs(m.amp), abs(m.err)) for m in h.modes if m.Q > 0 and FCEN - 0.5 * DF <= m.freq <= FCEN + 0.5 * DF])
    harm[res] = modes
    sim.reset_meep()
    say(f"A [res {res}]: " + "; ".join(f"f {f:.5f} Q {q:.0f} |amp| {a:.2e} err {e:.1e}" for f, q, a, e in modes))
modes_ref = harm[RES_IMG]
fsr = np.diff([m[0] for m in modes_ref])
ng = 1 / (np.mean(fsr) * L_RING)
say(f"A: FSR {', '.join(f'{x:.4f}' for x in fsr)} -> effective group index n_g = 1 / (FSR L) = {ng:.2f} (ring index {N_RING}); {time.time() - t_a:.0f} s")
if MASTER:
    source_figure(FCEN, DF, os.path.join(OUT, "00_source.png"), wl_scale=1.0, wl_unit="um", time_unit="um/c")

# ================================================================ B. one narrow-band run per resonance: field image + azimuthal order
imgs = []
t_b = time.time()
for f0, q0, _, _ in modes_ref:
    df0 = 0.01
    src = [mp.Source(mp.GaussianSource(f0, fwidth=df0), mp.Ez, SRC_PT)]
    sim = make_sim(RES_IMG, src)
    dft = sim.add_dft_fields([mp.Ez], f0, 0, 1, where=NONPML)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, SRC_PT, 1e-6))
    ez = sim.get_dft_array(dft, mp.Ez, 0)
    t_end = sim.meep_time()
    sim.reset_meep()
    # azimuthal order: sample the DFT field on the ring's mid-circle and count the dominant Fourier index
    nx, ny = ez.shape
    xs = np.linspace(EXT[0], EXT[1], nx); ys = np.linspace(EXT[2], EXT[3], ny)
    phis = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    ix = np.clip(np.searchsorted(xs, R_MID * np.cos(phis)), 0, nx - 1); iy = np.clip(np.searchsorted(ys, R_MID * np.sin(phis)), 0, ny - 1)
    ring_vals = ez[ix, iy]
    spec = np.abs(np.fft.rfft(np.real(ring_vals)))
    m_az = int(np.argmax(spec[1:]) + 1)
    imgs.append({"f": f0, "Q": q0, "ez": ez, "m": m_az, "t_end": t_end, "ring_vals": ring_vals})
    say(f"B [f {f0:.4f}]: azimuthal order m = {m_az} (m / (n L f) = {m_az / (N_RING * L_RING * f0):.3f}); run ended at t = {t_end:.0f}")
say(f"B done in {time.time() - t_b:.0f} s")

# ================================================================ C. solve_cw at f = 0.118 vs a time-domain DFT of the same mode
F_CW = modes_ref[0][0]
sym_cw = (mp.Mirror(mp.X, phase=-1), mp.Mirror(mp.Y, phase=+1))
src_cw = [mp.Source(mp.ContinuousSource(F_CW), component=mp.Ez, center=mp.Vector3(R + 0.1)),
          mp.Source(mp.ContinuousSource(F_CW), component=mp.Ez, center=mp.Vector3(-(R + 0.1)), amplitude=-1)]
TOLS = (1e-8, 1e-10, 1e-12)
MAXITERS, L_BICG = 10000, 10
sim = make_sim(RES_IMG, src_cw, sym_cw, force_complex_fields=True)
cw = []
t_c = time.time()
for tol in TOLS:
    sim.init_sim()
    t1 = time.time()
    sim.solve_cw(tol, MAXITERS, L_BICG)
    cw.append((tol, sim.get_array(vol=NONPML, component=mp.Ez), time.time() - t1))
eps_cw = sim.get_array(vol=NONPML, component=mp.Dielectric)
sim.reset_meep()
ref = cw[-1][1]
cw_err = [float(np.linalg.norm(a - ref) / np.linalg.norm(ref)) for _, a, _ in cw[:-1]]
say("C: solve_cw " + "; ".join(f"tol {t:.0e}: {s:.0f} s" for t, _, s in cw) + " | rel error vs tightest: " + ", ".join(f"{t:.0e}: {e:.2e}" for (t, _, _), e in zip(cw[:-1], cw_err)))

src_td = [mp.Source(mp.GaussianSource(F_CW, fwidth=0.08), component=mp.Ez, center=mp.Vector3(R + 0.1)),
          mp.Source(mp.GaussianSource(F_CW, fwidth=0.08), component=mp.Ez, center=mp.Vector3(-(R + 0.1)), amplitude=-1)]
sim = make_sim(RES_IMG, src_td, sym_cw)
dft = sim.add_dft_fields([mp.Ez], F_CW, 0, 1, where=NONPML)
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(R + 0.1523), 1e-8))
ez_td = sim.get_dft_array(dft, mp.Ez, 0); t_td = sim.meep_time()
sim.reset_meep()
alpha = np.vdot(ez_td, ref) / np.vdot(ez_td, ez_td)          # best-fit complex scale: CW and DFT differ by amplitude and global phase
err_td = float(np.linalg.norm(alpha * ez_td - ref) / np.linalg.norm(ref))
corr = float(np.corrcoef(np.abs(ez_td).ravel(), np.abs(ref).ravel())[0, 1])
say(f"C: time-domain DFT (decay 1e-8, ended t = {t_td:.0f}) vs solve_cw after complex alignment: rel L2 {err_td:.4f}, |Ez| correlation {corr:.6f}; {time.time() - t_c:.0f} s")

# ================================================================ GIF: broadband pulse rings the resonator (monitor-free)
sim_g = make_sim(RES_IMG, [mp.Source(mp.GaussianSource(FCEN, fwidth=DF), mp.Ez, SRC_PT)])
sim_g.init_sim()
eps_g = sim_g.get_array(vol=NONPML, component=mp.Dielectric)
t0g = 5 / DF
frames, times = record_frames(sim_g, NONPML, mp.Ez, t_start=t0g - 1 / DF, t_end=t0g + 260, n_frames=80)
sim_g.reset_meep()

# ================================================================ figures (master only)
if MASTER:
    # A: Harminv results vs resolution
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.0))
    cols = {10: "tab:gray", 20: "tab:blue", 30: "tab:red"}
    for j, (res, modes) in enumerate(harm.items()):
        ax[0].plot([m[0] for m in modes], [m[1] for m in modes], "o-", color=cols[res], label=f"res {res}: Q = " + " / ".join(f"{m[1]:.0f}" for m in modes))
    ax[0].set_yscale("log"); ax[0].set_xlabel("resonance frequency f [c/a]"); ax[0].set_ylabel("Q (Harminv)")
    ax[0].set_title("three Ez modes in the band 0.10-0.20: Q climbs with f (less bending radiation)", fontsize=9); ax[0].grid(alpha=0.3, which="both"); ax[0].legend(fontsize=8, loc="upper left")
    for k, (f, q, _, _) in enumerate(modes_ref):
        ax[1].axvline(f, color="tab:blue", lw=1.2); ax[1].text(f, 0.88, f"m = {imgs[k]['m']}\nf = {f:.4f}", ha="center", fontsize=8, color="tab:blue")
    ax[1].axvspan(FCEN - 0.5 * DF, FCEN + 0.5 * DF, color="orange", alpha=0.12, label="source band")
    for k in range(len(fsr)):
        ax[1].annotate("", xy=(modes_ref[k + 1][0], 0.5), xytext=(modes_ref[k][0], 0.5), arrowprops=dict(arrowstyle="<->", color="k"))
        ax[1].text(0.5 * (modes_ref[k][0] + modes_ref[k + 1][0]), 0.55, f"FSR {fsr[k]:.4f}", ha="center", fontsize=8)
    ax[1].text(0.102, 0.15, f"1 / (n_g L) with n_g = {ng:.2f}, L = 2 pi {R_MID} = {L_RING:.2f}", fontsize=8)
    ax[1].set_xlim(0.095, 0.205); ax[1].set_ylim(0, 1); ax[1].set_yticks([]); ax[1].set_xlabel("f [c/a]"); ax[1].set_title("free spectral range and azimuthal order (res 20)", fontsize=9); ax[1].legend(fontsize=8, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_harminv.png"), dpi=150); plt.close(fig)

    # B: mode images
    fig, ax = plt.subplots(2, 3, figsize=(13, 8.2), gridspec_kw={"height_ratios": [1.6, 1]})
    for k, d in enumerate(imgs):
        ez = d["ez"]; lim = float(np.percentile(np.abs(ez), 99.5))
        ax[0, k].imshow(np.real(ez).T, extent=EXT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
        ax[0, k].contour(np.linspace(EXT[0], EXT[1], eps_cw.shape[0]), np.linspace(EXT[2], EXT[3], eps_cw.shape[1]), eps_cw.T, levels=[0.5 * (1 + N_RING ** 2)], colors="k", linewidths=0.6)
        ax[0, k].plot(R + 0.1, 0, "o", color="lime", ms=4)
        ax[0, k].set_title(f"f = {d['f']:.4f} (lambda = {1 / d['f']:.2f} a), Q = {d['Q']:.0f}, m = {d['m']}", fontsize=9); ax[0, k].set_xlabel("x [a]")
        ax[1, k].plot(np.degrees(np.linspace(0, 2 * np.pi, 720, endpoint=False)), np.real(d["ring_vals"]) / np.max(np.abs(d["ring_vals"])), color="tab:blue", lw=1)
        ax[1, k].set_xlabel("angle around the ring [deg]"); ax[1, k].set_title(f"Re(Ez) on the mid-circle r = {R_MID}: {d['m']} periods", fontsize=9); ax[1, k].grid(alpha=0.3); ax[1, k].set_xlim(0, 360)
    ax[0, 0].set_ylabel("y [a]"); ax[1, 0].set_ylabel("normalized")
    fig.suptitle("each resonance imaged alone (narrow-band source, DFT at the resonance): the azimuthal order m counts the wavelengths around the ring", fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_modes.png"), dpi=150); plt.close(fig)

    # C: solve_cw
    fig = plt.figure(figsize=(13, 4.4))
    ax = fig.add_subplot(1, 3, 1)
    ax.loglog([t for t, _, _ in cw[:-1]], cw_err, "bo-"); ax.invert_xaxis()
    for (t, _, s), e in zip(cw[:-1], cw_err):
        ax.annotate(f"{s:.0f} s", (t, e), textcoords="offset points", xytext=(6, -12), fontsize=8)
    ax.set_xlabel("solve_cw tolerance"); ax.set_ylabel(f"relative error vs tol {TOLS[-1]:.0e} field"); ax.set_title("frequency-domain solver: tighter tolerance, smaller change", fontsize=9); ax.grid(alpha=0.3, which="both")
    lim = float(np.percentile(np.abs(ref), 99.5))
    for a, data, ttl in ((fig.add_subplot(1, 3, 2), np.real(ref), f"solve_cw at f = {F_CW:.4f} (tol {TOLS[-1]:.0e})"),
                         (fig.add_subplot(1, 3, 3), np.real(alpha * ez_td), f"time-domain DFT, aligned: rel L2 {err_td:.3f}")):
        a.imshow(data.T, extent=EXT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
        a.contour(np.linspace(EXT[0], EXT[1], eps_cw.shape[0]), np.linspace(EXT[2], EXT[3], eps_cw.shape[1]), eps_cw.T, levels=[0.5 * (1 + N_RING ** 2)], colors="k", linewidths=0.6)
        a.set_title(ttl, fontsize=9); a.set_xlabel("x [a]")
    fig.suptitle("the same mode from two solvers: continuous source + BiCGSTAB-L (left, centre) and a pulse + DFT (right)", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.93]); fig.savefig(os.path.join(OUT, "04_solve_cw.png"), dpi=150); plt.close(fig)

    animate_fields(frames, times, EXT, os.path.join(OUT, "05_anim_ring.gif"), eps=eps_g, figsize=(5.6, 5.0), dpi=70, clip_percentile=99.0, unit="a",
                   points=[(R + 0.1, 0, "red", "source / probe")], title="broadband pulse, then ringing", legend_loc="lower left")

    with open(os.path.join(OUT, "result.json"), "w") as f_:
        json.dump({"params": {"n": N_RING, "r": R, "w": W, "pad": PAD, "dpml": DPML, "fcen": FCEN, "df": DF, "T_harminv": T_HARMINV, "L_ring": L_RING},
                   "harminv": {str(k): [{"f": f, "Q": q, "amp": a, "err": e} for f, q, a, e in v] for k, v in harm.items()},
                   "fsr": fsr.tolist(), "n_g": float(ng),
                   "modes": [{"f": d["f"], "Q": d["Q"], "m": d["m"], "t_end": float(d["t_end"])} for d in imgs],
                   "solve_cw": {"f": F_CW, "tols": list(TOLS), "seconds": [s for _, _, s in cw], "rel_err_vs_tightest": cw_err,
                                "td_vs_cw_rel_l2": err_td, "td_vs_cw_corr": corr, "td_t_end": float(t_td)},
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__, "np": mp.count_processors()}, f_, indent=2)
say(f"total {time.time() - t_all:.0f} s on {mp.count_processors()} process(es)")
{% endhighlight %}
</details>

Unlike the excerpts in §4, the full script includes the resolution ladder, mode images and azimuthal-order calculation, solve_cw sweep, GIF, and result.json output. For MPI execution, collective calls (run, get_array, solve_cw) execute on every rank, while figures are saved only on the master rank. The shared `blogfig.py` helper is in the same `code/` folder. Full code and helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**Execution output (run on 2026-10-23, mpirun -np 4)**:
```
A [res 10]: f 0.11810 Q 81 |amp| 3.41e-03 err 1.0e-05; f 0.14716 Q 317 |amp| 2.86e-02 err 7.3e-07; f 0.17525 Q 1675 |amp| 7.21e-03 err 2.0e-07
A [res 20]: f 0.11818 Q 79 |amp| 3.51e-03 err 6.8e-06; f 0.14736 Q 342 |amp| 2.81e-02 err 1.7e-07; f 0.17564 Q 2132 |amp| 6.76e-03 err 1.4e-06
A [res 30]: f 0.11822 Q 79 |amp| 3.52e-03 err 2.6e-06; f 0.14740 Q 336 |amp| 2.82e-02 err 1.5e-07; f 0.17572 Q 1610 |amp| 6.79e-03 err 9.7e-08
A: FSR 0.0292, 0.0283 -> effective group index n_g = 1 / (FSR L) = 3.69 (ring index 3.4)
B [f 0.1182]: azimuthal order m = 3 (m / (n L f) = 0.792); run ended at t = 2101
B [f 0.1474]: azimuthal order m = 4 (m / (n L f) = 0.847); run ended at t = 5453
B [f 0.1756]: azimuthal order m = 5 (m / (n L f) = 0.888); run ended at t = 19110
C: solve_cw tol 1e-08: 5 s; tol 1e-10: 6 s; tol 1e-12: 7 s | rel error vs tightest: 1e-08: 4.24e-07, 1e-10: 1.08e-10
C: time-domain DFT (decay 1e-8, ended t = 2001) vs solve_cw after complex alignment: rel L2 0.0040, |Ez| correlation 0.999984
total ~4 min on 4 processes
```

**Reproduction environment**: meep 1.33.0 (MPI) · Python 3.11 · `conda install -c conda-forge pymeep=*=mpi_mpich_*` · command `mpirun -np 4 python ring_resonator.py` (about 4 min (mpirun -np 4))

<details markdown="1">
<summary>Advanced questions: connect to the next chapter</summary>

1. Harminv estimates Q for modes with lifetimes of thousands of time units from a 300-unit signal. Explain why this is possible and the error condition needed to trust Q.
2. Frequency is within 1% at resolution 10, but Q is not converged even at 30. Explain their different convergence rates in terms of bend radiation and the grid.
3. This ring is a 2D cross-section. A real microdisk is an axisymmetric 3D structure whose modes have azimuthal order m. Which coordinate system reduces it to one 2D calculation per m, and where does m enter? (Chapter 13)

</details>

### Further reading

- [Basics tutorial: modes of a ring resonator](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#modes-of-a-ring-resonator) · [Frequency-domain solver](https://meep.readthedocs.io/en/latest/Python_Tutorials/Frequency_Domain_Solver/) · [Harminv reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#harminv) · [solve_cw](https://meep.readthedocs.io/en/latest/Python_User_Interface/#frequency-domain-solver)
- Scripts: [ring.py](https://github.com/NanoComp/meep/blob/master/python/examples/ring.py) · [solve-cw.py](https://github.com/NanoComp/meep/blob/master/python/examples/solve-cw.py) · [ring-mode-overlap.py](https://github.com/NanoComp/meep/blob/master/python/examples/ring-mode-overlap.py)
- Previous: [11 · A point source between two mirrors]({{ site.baseurl }}/en/cavity-ldos/) · Bend loss from chapter 05: [05 · Bent waveguide and radius trade-off]({{ site.baseurl }}/en/waveguide-bend-90/) · Next: [13 · Computing 3D with rotational symmetry]({{ site.baseurl }}/en/cylindrical-dipole/)
