---
layout: lesson
permalink: /en/binary-grating/
lesson_title: "Which directions does a grating send light?"
lesson_summary: "Begin with one plane wave splitting into three directions. Use the grating equation to predict possible directions, then check the order efficiencies against total power."
lesson_goals:
  - "Find propagating diffraction orders and angles from the period and wavelength."
  - "Compare the sum of order efficiencies with flux and reflectance."
  - "Explain why only amplitude and phase remain when the period is subwavelength."
lesson_prerequisites: "Read incident-field subtraction in chapter 03 and mode coefficients in chapter 04 first. Running the examples requires Meep and Python."
date: 2026-10-23
title: "Meep Example 06 · Binary grating and diffraction orders — the grating equation, power per order, and the phase a duty cycle buys"
title_en: "Meep Example 06 · Binary grating and diffraction orders — the grating equation, power per order, and the phase a duty cycle buys"
lang: en
translation_key: binary-grating
series: meep-examples
part: 6
level: beginner
runtime: "27 s (single core)"
meep_version: "1.33.0"
official_example: "https://github.com/NanoComp/meep/blob/master/python/examples/binary_grating.py"
tags: [meep, fdtd, grating, diffraction, periodic, phase-library]
image: /assets/meep/06/04_finite.png
excerpt: "a glass binary grating under a normally incident plane wave. One period with Bloch-periodic boundaries gives the power in each diffraction order; a subwavelength period gives the amplitude and phase of the only surviving order as the duty cycle changes; a finite 8-ridge grating shows the beams."
---
<details markdown="1">
<summary>English summary</summary>

- **What**: a glass binary grating under a normally incident plane wave. One period with Bloch-periodic boundaries gives the power in each diffraction order; a subwavelength period gives the amplitude and phase of the only surviving order as the duty cycle changes; a finite 8-ridge grating shows the beams.
- **Result**: for a 2.6 µm period only m = 0, ±1 propagate (±36.6°). Power: m = 0 0.759, m = ±1 0.088 each; the orders add up to the transmitted flux and T + R = 0.999. The finite grating's beams sit at 35.2° by spatial FFT. A duty-cycle sweep of a 1.2 µm period turns the phase by 0.09 × 2π (h = 0.35 µm) or 0.23 × 2π (h = 0.9 µm), close to Δn·h/λ.
- **Takeaway**: the grating equation fixes where the light can go; only a simulation says how much goes where. A single period with `k_point` is enough for the numbers, and `DiffractedPlanewave` decomposes the transmitted field order by order.
- **Code**: full script at the bottom, ~27 s on one core.

</details>

<h2 id="observe">1. Observe · Follow the light</h2>

A plane wave illuminates eight glass ridges from the left. Behind them, light splits into **straight and oblique directions**. The cyan dashed lines mark the predicted directions; the curve on the right is the spatial FFT of the actual field.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/06/04_finite.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/06/04_finite.png' | relative_url }}" alt="Three diffraction beams behind eight finite glass ridges and peaks in the scattered-field spatial FFT." loading="lazy">
  </a>
<figcaption>The actual field of the finite grating. Predicted angles are 0°, ±36.6°; the positive FFT peak gives 35.2°. Compare these values with the resolution imposed by the finite cut length.</figcaption>
</figure>

<figure class="lesson-figure lesson-animation">
  <a href="{{ '/assets/meep/06/05_anim_finite.gif' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/06/05_anim_finite.gif' | relative_url }}" alt="Time evolution of a pulse forming three diffraction beams behind eight glass ridges" loading="lazy" data-animation-src="{{ '/assets/meep/06/05_anim_finite.gif' | relative_url }}" data-static-src="{{ '/assets/meep/06/04_finite.png' | relative_url }}">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
<figcaption>The same finite grating driven by a short pulse. Each ridge scatters the incident plane wave; beams grow in the three directions of constructive interference. Order 0 travels straight, and orders ±1 travel obliquely.</figcaption>
</figure>

<h2 id="predict">2. Predict · Before reading the results</h2>

At a wavelength of 1.55 µm, what happens to the ±1 beams propagating into air when the period decreases from 2.6 µm to 1.2 µm?

<fieldset class="prediction">
  <legend>Choose an answer first.</legend>
  <label><input type="radio" name="prediction-06" value="0"> They continue propagating at larger angles as the period shrinks</label>
  <label><input type="radio" name="prediction-06" value="1"> They leave the propagating range, leaving only order 0</label>
</fieldset>

<details markdown="1">
<summary>Check the reasoning</summary>

The second answer is correct. Orders ±1 must satisfy sin θ = ±λ/Λ. Because 1.55/1.2 exceeds 1, no real angle exists and these orders cannot propagate far into air. This does not mean that evanescent fields near the structure disappear.

</details>

<h2 id="understand">3. Understand · Explain what you observed</h2>

{% include chapter-illustration.html %}

<!-- concept-illustration:part-06:start -->

<p class="lesson-note">In experiment A, glass (n = 1.5) occupies the left side and its ridge protrudes into air on the right. Light enters through glass along +x. The y period is 2.6 µm, ridge height 0.5 µm, and width 1.3 µm; the one-period cell uses periodic y boundaries and x PML. At wavelength 1.55 µm, orders 0, ±1 propagate into air, with ±36.6° measured from the +x normal. The repeated array on the right explains directions; it is distinct from the separate finite eight-ridge simulation.</p>

<!-- concept-illustration:part-06:end -->

### Period and wavelength determine the directions

For normally incident light emerging into air, the period Λ gives each order m a different transverse wavevector.

$$\sin\theta_m=m\lambda/\Lambda$$

Propagation requires $\lvert m\rvert\lambda/\Lambda<1$. With period 2.6 µm and wavelength 1.55 µm, only m = 0, ±1 propagate; orders ±1 leave at ±36.6° from the normal. This equation specifies **allowed directions**, not the power in each direction.

### Calculate efficiencies with one period and check their sum

An infinitely repeated grating is modeled by one ridge and periodic boundaries along y. PML is placed only along x, the propagation direction. Use `DiffractedPlanewave` to decompose the complex amplitude of each order, then normalize by incident flux.

$$T_m=\lvert a_m\rvert^2/P_{\mathrm{in}},\qquad \sum_mT_m=T_{\mathrm{total}},\qquad T_{\mathrm{total}}+R\approx1$$

At period 1.2 µm, only order 0 propagates. Changing duty cycle (ridge width/period) changes transmitted amplitude and phase rather than the number of beams. The low refractive-index contrast of glass gives less than one full phase turn even at height 0.9 µm.

<aside class="lesson-note" markdown="1">
**Distinguish the one-period experiment from the finite grating.** These are single-frequency results for 2D Ez polarization, normal incidence, and lossless glass with n = 1.5. Exact diffraction angles in a periodic cell and broad beam peaks from eight finite ridges are different observables.
</aside>

<details markdown="1">
<summary>Show notation, assumptions, and predictions</summary>

A structure with period Λ adds or subtracts transverse momentum 2πm/Λ from a plane wave. Propagation in air requires transverse wavenumber smaller than k₀ = 2π/λ, so only orders with \|m\|λ/Λ < 1 survive. For Λ = 2.6 µm and λ = 1.55 µm, λ/Λ = 0.60 permits m = 0, ±1, with ±1 at ±36.6°. For Λ = 1.2 µm, λ/Λ = 1.29 > 1 leaves only order 0. The grating then changes transmitted amplitude and phase like an effective medium, without additional propagating diffraction orders.

$$
\sin\theta_m=\frac{m\lambda}{\Lambda},\qquad
T_m=\frac{\|a_m\|^2}{P_{\mathrm{in}}},\qquad \sum_m T_m = T_{\mathrm{total}},\qquad T_{\mathrm{total}}+R=1
$$

$$
\frac{\Delta\phi_{\max}}{2\pi}\;\lesssim\;\frac{(n-1)\,h}{\lambda}
$$

The second expression is a rough upper bound on the phase span available through duty cycle. The largest phase difference accumulated through height h is the difference between a fully glass-filled ridge region and an empty one: (n − 1)h/λ turns.

| Symbol | Meaning | Code variable |
|------|----|-----------|
| Λ, h, duty | Period, ridge height, ridge width/period | `gp`, `gh`, `gdc` |
| $a_m$ | Complex amplitude of plane-wave order m (`DiffractedPlanewave`) | `amp[m]` |
| $P_{\mathrm{in}}$ | Transmitted flux in the reference run (cell filled with glass) | `P_in` |
| $T_m$, R | Order-m efficiency, reflectance (incident field subtracted) | `T_m[m]`, `R` |
| $k_y/2\pi$ | Spatial FFT frequency on the far cut (cycles/µm) | `ky` |

**Assumptions and validity**: 2D, Ez polarization, normal incidence, lossless glass (n 1.5). Glass ridges sit on a glass substrate. Finite-grating angles are limited by FFT resolution 1/(cut length) ≈ 0.037 cycles/µm (±1.8°).

### Make predictions before seeing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| Propagating orders at period 2.6 µm | Three: m = 0, ±1 | λ/Λ = 0.60 |
| Angles of orders ±1 | ±36.6° | asin(0.60) |
| T₊₁ = T₋₁ | Equal | Normal incidence + symmetric ridge |
| ΣT_m versus T_total, T + R | Equal, 1 | Complete order decomposition, no loss |
| T_total − T₀ at period 1.2 µm | 0 | Only order 0 propagates |
| Duty-cycle phase span (h 0.35 / 0.9 µm) | At most 0.11 / 0.29 × 2π | (n − 1)h/λ |
| Finite-grating FFT peak | 0.385 cycles/µm (= 1/Λ) | Grating equation |

**Acceptance criteria**: a difference above 1 percentage point between ΣT_m and T_total suggests a missing order or an incorrect DiffractedPlanewave setup. A deviation of T + R from 1 above 1% indicates a reference-run problem.

</details>

<h2 id="run">4. Run · Change one variable</h2>

### Change one thing: the diffraction period

1. Run `python binary_grating.py` in the `code/` folder containing the complete script and `blogfig.py`. Keep the baseline `result.json`.
2. In `GP_A, GH_A, GDC_A = 2.6, 0.5, 0.5`, change **only the first value to 3.5**. Keep height, duty cycle, and wavelength fixed.
3. Run again and compare the order list from `orders_propagating`, each `T_m`, their sum, and `T_total`.

The equation predicts that orders ±2 now propagate too. The simulation must determine how much power enters them. Measured efficiencies below belong to the original 2.6 µm period; **fill in the 3.5 µm efficiencies using your new run**. Leave experiment B at `GP_B = 1.2`.

<details markdown="1">
<summary>Show the setup, source, and parameters</summary>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/06/01_layout.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/06/01_layout.png' | relative_url }}" alt="Glass substrate, ridge, source, flux monitors, and x PML for a grating of period 2.6 µm" loading="lazy">
  </a>
<figcaption>One-period cell for experiment A (2.6 µm tall). Left black block: glass substrate extending through PML; small central block: ridge (height 0.5, width 1.3 µm); red line: plane-wave source inside glass; blue lines: reflection monitor in glass and transmission monitor in air; green hatching: x PML. There is no y PML; `k_point` sets periodic boundaries. Purple ×: decay-monitoring point. Circled numbers identify the steps in §4.</figcaption>
</figure>

| Parameter | Value | Why this value | Effect of a change |
|----------|-----|-------------|--------|
| Period Λ (A / B) | 2.6 / 1.2 µm | A: reduced from the official 10 µm to allow only m = 0, ±1. B: only order 0 | At Λ ≥ 3.1 µm, ±2 orders also appear |
| Ridge h, duty (A) | 0.5 µm, 0.5 | Official example values | Changes efficiency distribution (§7) |
| `fwidth` | 0.1 fcen | Narrow band; orders decomposed at one frequency | A broader band can give order-resolved spectra |
| `RESOLUTION` | 25 (convergence: 50) | Wavelength in glass 1.03 µm → 26 px; ridge 12 px | At 50 the third decimal changes |
| source | Inside glass, full cell width | Width equal to one period gives a plane wave in a periodic cell | — |
| reference run | Entire cell filled with glass | Official approach; P_in is incident flux in glass | Filling with air includes interface reflection in the denominator |
| Finite grating | 8 ridges, 10 µm air, PML on all sides | Enough distance to separate beams; FFT cut 8 µm behind ridges | Fewer ridges broaden the beams |

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/06/00_source.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/06/00_source.png' | relative_url }}" alt="Narrowband Gaussian source waveform and spectrum for the grating experiment" loading="lazy">
  </a>
<figcaption>Source waveform and spectrum: width 15.5, t0 = 77.5. The narrow band uses a single fcen point for flux and order decomposition.</figcaption>
</figure>

**Difference from the lecture notebook**: week 7 sweeps duty cycle at a single 1.2 µm period and uses the band 1 mode coefficient as a proxy for order 0. Here, `DiffractedPlanewave` directly separates three orders at the official example’s diffracting period (2.6 µm), with power-budget checks and a finite-grating experiment added. The duty-cycle sweep agrees with the lecture (phase span 0.089 × 2π).

</details>

<details markdown="1">
<summary>Walk through the code</summary>

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → run and stop → postprocessing.
> Experiments A and B use the same `run_periodic` function; experiment C uses a separate finite cell.

### ① Units and parameters — which numbers stay fixed

```python
wl = 1.55
fcen = 1 / wl
fwidth = 0.1 * fcen           # narrow band: single-frequency order decomposition
n_glass = 1.5
glass = mp.Medium(index=n_glass)
DPML, DSUB, DPAD = 1.0, 2.0, 2.0

GP_A, GH_A, GDC_A = 2.6, 0.5, 0.5       # A: diffracting period (lambda / GP = 0.60 -> m = 0, +-1 only)
GP_B = 1.2                               # B: subwavelength period (lambda / GP = 1.29 -> m = 0 only)

def orders_propagating(gp):
    """Grating equation at normal incidence: sin(theta_m) = m * wl / gp (into air)."""
    m_max = int(np.floor(gp / wl))
    return {m: float(np.degrees(np.arcsin(m * wl / gp))) for m in range(-m_max, m_max + 1)}
```

- **What**: define wavelength, glass, substrate and air thicknesses, two periods, and the list of propagating orders from the grating equation.
- **Why**: the equation, rather than the simulation, determines which orders to decompose. Passing nonpropagating orders to `DiffractedPlanewave` produces evanescent contributions without a meaningful propagating efficiency.
- **If wrong**: counting `m_max` incorrectly and including ±2 adds evanescent amplitudes, so the T_m sum may exceed T_total or fluctuate.

### ② Materials and geometry — what goes where

```python
def grating_geometry(sx, gp, gh, gdc):
    return [mp.Block(material=glass, size=mp.Vector3(DPML + DSUB, mp.inf, mp.inf),
                     center=mp.Vector3(-0.5 * sx + 0.5 * (DPML + DSUB), 0)),          # substrate through the PML
            mp.Block(material=glass, size=mp.Vector3(gh, gdc * gp, mp.inf),
                     center=mp.Vector3(-0.5 * sx + DPML + DSUB + 0.5 * gh, 0))]      # the ridge, width gdc * gp
```

- **What**: a glass substrate extending through left PML, with one ridge on top. Ridge width is duty × period.
- **Why**: one ridge in a periodic cell represents an infinite grating. The substrate must extend through PML to avoid backside reflections.
- **If wrong**: terminating the substrate before PML creates an extra glass–air interface, adding 4% to R.

### ③ Source — how light enters

```python
def plane_wave(sx, sy, fw=fwidth):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw), component=mp.Ez,
                      center=mp.Vector3(-0.5 * sx + DPML + 0.5 * DSUB, 0), size=mp.Vector3(0, sy))]
```

- **What**: a line source inside glass spanning the full cell width (= one period), launching a plane wave along +x.
- **Why**: a full-width line source in a periodic cell is an infinite plane wave. Unlike chapter 03, `is_integrated` is unnecessary because there is no y PML.
- **If wrong**: placing the source in air invalidates normalization by incident flux inside glass.

### ④ Simulation and boundaries — the cell and PML

```python
sim = mp.Simulation(cell_size=mp.Vector3(sx, gp), resolution=resolution,
                    boundary_layers=[mp.PML(DPML, direction=mp.X)],   # PML only along the propagation axis
                    geometry=[] if empty else grating_geometry(sx, gp, gh, gdc),
                    default_material=glass if empty else mp.air,     # reference: glass everywhere
                    sources=plane_wave(sx, gp), k_point=mp.Vector3())  # Bloch-periodic in y with k = 0
```

- **What**: a cell only one period tall, with x PML and Bloch-periodic y boundaries at `k_point=(0,0,0)`.
- **Why**: normal incidence has zero Bloch phase, so `k_point` is zero. The reference run fills the entire cell with glass to measure incident flux without an interface, following the official example.
- **If wrong**: omitting `k_point` makes y boundaries reflecting walls, modeling a waveguide rather than the grating. Adding y PML breaks periodicity.

### ⑤ Monitors — what is measured

```python
refl = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(-0.5 * sx + DPML + 0.8 * DSUB, 0), size=mp.Vector3(0, gp)))
tran = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * sx - DPML - 0.5 * DPAD, 0), size=mp.Vector3(0, gp)))
...
sim.load_minus_flux_data(refl, refl_data)     # reflection only (chapter 03)
```

- **What**: a reflection monitor in glass downstream of the source and a transmission monitor in air; both span the full cell width.
- **Why**: transmitted flux sums all orders. `DiffractedPlanewave` decomposes orders at the same monitor. Subtract the incident field at the reflection monitor as in chapter 03.
- **If wrong**: placing the transmission monitor too close to a ridge mixes in evanescent orders and spoils agreement between the order sum and flux. Leave at least one wavelength of separation.

### ⑥ Run and stopping condition — when to stop

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(0.5 * sx - DPML - 0.5 * DPAD, 0), 1e-6))
```

- **What**: wait until Ez at the transmission monitor decays to 10⁻⁶.
- **Why**: the narrowband pulse is long (width 15.5). Its tail must pass the monitor for an accurate DFT.
- **If wrong**: a fixed `until_after_sources=100`, as in the official example, may be too short at other periods or heights.

### ⑦ Postprocessing — extracting the numbers

```python
amp = {m: sim.get_eigenmode_coefficients(tran, mp.DiffractedPlanewave((0, m, 0), mp.Vector3(0, 1, 0), 1, 0)).alpha[0, 0, 0]
       for m in orders}                       # one order per call: (0, m, 0) along the periodic axis y, s-pol (Ez)
T_m = {m: abs(a) ** 2 / P_in for m, a in amp.items()}
phase_m = {m: np.angle(a) for m, a in amp.items()}
T_total = mp.get_fluxes(tran)[0] / P_in
R = -mp.get_fluxes(refl)[0] / P_in
```

- **What**: obtain each plane-wave amplitude a_m; use \|a_m\|²/P_in as efficiency and its argument as phase.
- **Why**: `DiffractedPlanewave((0, m, 0), axis, s, p)` defines one plane-wave mode: order m along periodic y, s-polarized (Ez). `get_eigenmode_coefficients` accepts one such object per call. This specifies an order directly instead of the band number used in chapter 04.
- **If wrong**: passing a list of `DiffractedPlanewave` objects causes `TypeError` (as on the first run). Setting `axis` to x changes the plane definition and swaps s and p.

> **Pitfall**: connect the phase sweep with `np.unwrap`. This is reliable only when neighboring phase differences are below π, so sample duty cycle densely (9 points). The largest adjacent difference here is 0.33 rad.

</details>

<h2 id="interpret">5. Interpret · Read the measurements and their limits</h2>

### Read direction predictions separately from power measurements

| Order | Angle in air | Efficiency relative to incident power |
|---|---|---|
| −1 | −36.6° | 0.0884 |
| 0 | 0° | 0.7591 |
| +1 | +36.6° | 0.0884 |

The order sum, 0.9358, matches total transmitted flux 0.9358; adding R = 0.0635 gives 0.9994. Symmetry and normal incidence give equal ±1 efficiencies. At resolution 50, T₀ = 0.7597 and T±1 = 0.0881.

At period 1.2 µm, the duty sweep spans **0.089/0.229 × 2π** at heights 0.35/0.9 µm. Even the taller ridge does not cover a full 2π here, limiting the phase library developed in the next chapter.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/06/02_orders.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/06/02_orders.png' | relative_url }}" alt="Measured efficiencies of orders 0 and ±1, comparing their sum with total flux" loading="lazy">
  </a>
<figcaption>Three propagating-order efficiencies and the budget check: m = 0 gives 0.759, and ±1 each give 0.088. Their sum 0.936 matches transmitted flux; adding reflection 0.064 gives 0.999.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/06/03_duty_sweep.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/06/03_duty_sweep.png' | relative_url }}" alt="Zeroth-order transmission and phase versus duty cycle at two ridge heights" loading="lazy">
  </a>
<figcaption>Left: zeroth-order transmission T₀, varying nonmonotonically between 0.83 and 0.97 for both heights. Right: phase of order 0 relative to duty 0.1, in units of 2π. Height 0.35 µm gives 0.09 turns; 0.9 µm gives 0.23. The red line marks the full turn needed for a phase library.</figcaption>
</figure>

<aside class="lesson-note" markdown="1">
**Finite-grating angles have limited resolution.** Compare the FFT peak 0.372 cycles/µm (35.2°) against the equation’s 0.385 cycles/µm (36.6°) within the cut-length resolution of about ±0.037 cycles/µm, ±1.8°. These results do not establish sub-degree accuracy, oblique-incidence behavior, other polarizations, or wavelength spectra.
</aside>

<details markdown="1">
<summary>Show all measurements, predictions, and convergence checks</summary>

### A. Period 2.6 µm: efficiency per order



| Quantity | Value (res 25) | Value (res 50) | Original 10_sources (res 50) |
|---|---|---|---|
| T₀ | 0.7591 | 0.7597 | 0.7597 |
| T₊₁ = T₋₁ | 0.0884 | 0.0881 | 0.0881 |
| ΣT_m | 0.9358 | — | 0.9359 |
| T_total (flux) | 0.9358 | — | 0.9359 |
| R | 0.0635 | 0.0639 | 0.0639 |
| T + R | 0.9994 | 0.9998 | 0.9998 |

### B. Period 1.2 µm: amplitude and phase from duty cycle



| Height h | Phase span / 2π | Estimate (n − 1)h/λ | T₀ range | max \|T_total − T₀\| |
|---|---|---|---|---|
| 0.35 µm | 0.089 | 0.113 | 0.83–0.97 | 3 × 10⁻⁶ |
| 0.90 µm | 0.229 | 0.290 | 0.85–0.95 | 3 × 10⁻⁶ |

### C. Finite grating: beams and angles





### Compare against the predictions

| Quantity | Prediction (§2) | Simulation | Verdict |
|--------|-------------|-----------|------|
| Propagating orders | m = 0, ±1 | Sum of three orders = flux | ✅ |
| T₊₁ = T₋₁ | Equal | 0.0884 = 0.0884 | ✅ |
| ΣT_m = T_total, T + R | Equal, 1 | 0.9358 = 0.9358, 0.9994 | ✅ |
| T_total − T₀ at 1.2 µm | 0 | 3 × 10⁻⁶ | ✅ |
| Phase span (0.35 / 0.9 µm) | ≤ 0.11 / 0.29 | 0.089 / 0.229 | ✅ |
| FFT peak | 0.385 cycles/µm | 0.372 (±0.037 resolution) | ✅ |

All predictions agree. The phase span is 79% of the estimate: ridges do not fill the whole period, so the effective index difference is less than (n − 1), confirming that the estimate is an upper bound. Increasing height 2.6 times still gives only 0.23 turns. This is why the phase library in chapter 07 uses Si instead of glass.

### Convergence

| resolution | T₀ | T₊₁ | R | T + R |
|---|---|---|---|---|
| 25 | 0.7591 | 0.0884 | 0.0635 | 0.9994 |
| 50 | 0.7597 | 0.0881 | 0.0639 | 0.9998 |

Doubling resolution changes efficiency only in the third decimal. The 0.5 µm ridge height is resolved by 12 px at res 25, sufficient for this comparison.

### What the results do and do not establish

- Supported: at normal incidence and Ez polarization, this grating’s three efficiencies are 0.76 / 0.088 / 0.088 and the power budget closes. A subwavelength glass grating changes phase through duty cycle by no more than (n − 1)h/λ turns.
- Not established: finite-grating angles within 1°, since cut length limits resolution to ±1.8°; oblique incidence (nonzero Bloch phase); p polarization; or wavelength-dependent efficiencies (only one frequency was computed).

</details>

<details markdown="1">
<summary>Show the troubleshooting checklist</summary>

| Symptom | Cause | Fix |
|------|------|----------|
| `TypeError ... DiffractedPlanewave` | Multiple orders passed as a list | Call `get_eigenmode_coefficients` separately per order |
| Order sum exceeds flux | Nonpropagating (evanescent) orders included | Keep only orders satisfying \|m\|λ/Λ < 1 |
| Grating behaves like a waveguide | Missing `k_point` makes y boundaries reflecting | Set `k_point=mp.Vector3()` |
| R is 4 percentage points too large | Substrate ends before PML | Extend substrate through PML |
| Sawtooth phase curve | Unwrap fails because samples are too sparse | Sample duty cycle more densely |
| Broad finite-grating FFT peak | Short cut or too few ridges | Increase cut length or ridge count |

</details>

<h2 id="check">6. Check · Answer two questions</h2>

### 1. If only order 0 propagates, do the ridges have no effect on light?

<details markdown="1">
<summary>Read the explanation</summary>

No. Even with one far-field direction, the amplitude and phase of order 0 and the reflectance change. Using this complex transmission coefficient is the starting point for a phase library.

</details>

### 2. The ±1 angles agree, but the order sum differs from total transmitted flux. What should you check?

<details markdown="1">
<summary>Read the explanation</summary>

Check for missing propagating orders or included evanescent orders, and verify the periodic direction, polarization, and monitor placement for DiffractedPlanewave. Correct angles do not replace an independent efficiency-budget check.

</details>

<h2 id="reference">7. Reference · Full code and original records</h2>

The complete program below is preserved from the original. Check the execution environment and recorded results together.

<details>
<summary>binary_grating.py (expand to view)</summary>
{% highlight python %}
"""Meep Example 06 - Binary grating and diffraction orders.

  A. One period of a glass binary grating (period 2.6 um > wavelength): the grating equation says only
     m = 0, +-1 propagate in air, at +-36.6 deg. DiffractedPlanewave gives the power in each order;
     checks: sum of orders = total transmitted flux, T + R = 1.  (official binary_grating.py, period reduced)
  B. A subwavelength period (1.2 um): only m = 0 propagates. Sweep the duty cycle and record the
     transmitted amplitude AND phase of the zeroth order, for two ridge heights. This curve is the
     prototype of the meta-atom phase library of post 07; the phase span scales like dn * h / lambda.
  C. A finite grating (8 ridges) with PML on all sides: the three beams become visible; the beam angle
     is read from the spatial FFT of the scattered field on a far cut and compared with the equation.
  D. GIF of C in time.

Run:  python binary_grating.py           (~5 min on one core)
Out:  00_source.png, 01_layout.png, 02_orders.png, 03_duty_sweep.png, 04_finite.png,
      05_anim_finite.gif, result.json   (-> ../assets/06/)
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
from blogfig import Label, animate_fields, annotated_layout, bar_figure, record_frames, source_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "06")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()

# ---------------------------------------------------------------- (1) units & parameters
wl = 1.55
fcen = 1 / wl
fwidth = 0.1 * fcen           # narrow band: single-frequency order decomposition
n_glass = 1.5
glass = mp.Medium(index=n_glass)
DPML, DSUB, DPAD = 1.0, 2.0, 2.0

GP_A, GH_A, GDC_A = 2.6, 0.5, 0.5       # A: diffracting period (lambda / GP = 0.60 -> m = 0, +-1 only)
GP_B = 1.2                               # B: subwavelength period (lambda / GP = 1.29 -> m = 0 only)
RESOLUTION = 25


def orders_propagating(gp):
    """Grating equation at normal incidence: sin(theta_m) = m * wl / gp (into air)."""
    m_max = int(np.floor(gp / wl))
    return {m: float(np.degrees(np.arcsin(m * wl / gp))) for m in range(-m_max, m_max + 1)}


# ---------------------------------------------------------------- (2) geometry: substrate + one ridge per period
def grating_geometry(sx, gp, gh, gdc):
    return [mp.Block(material=glass, size=mp.Vector3(DPML + DSUB, mp.inf, mp.inf),
                     center=mp.Vector3(-0.5 * sx + 0.5 * (DPML + DSUB), 0)),          # substrate through the PML
            mp.Block(material=glass, size=mp.Vector3(gh, gdc * gp, mp.inf),
                     center=mp.Vector3(-0.5 * sx + DPML + DSUB + 0.5 * gh, 0))]      # the ridge, width gdc * gp


# ---------------------------------------------------------------- (3) source: plane wave inside the glass, travelling +x
def plane_wave(sx, sy, fw=fwidth):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw), component=mp.Ez,
                      center=mp.Vector3(-0.5 * sx + DPML + 0.5 * DSUB, 0), size=mp.Vector3(0, sy))]


# ---------------------------------------------------------------- (4) one periodic cell: PML in x only, Bloch-periodic in y (k = 0)
def periodic_cell(gp, gh, gdc, resolution=RESOLUTION, empty=False):
    sx = DPML + DSUB + gh + DPAD + DPML
    sim = mp.Simulation(cell_size=mp.Vector3(sx, gp), resolution=resolution,
                        boundary_layers=[mp.PML(DPML, direction=mp.X)],
                        geometry=[] if empty else grating_geometry(sx, gp, gh, gdc),
                        default_material=glass if empty else mp.air,     # reference: glass everywhere
                        sources=plane_wave(sx, gp), k_point=mp.Vector3())
    # ------------------------------------------------------------ (5) monitors: reflection (in glass), transmission (in air)
    refl = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(-0.5 * sx + DPML + 0.8 * DSUB, 0), size=mp.Vector3(0, gp)))
    tran = sim.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * sx - DPML - 0.5 * DPAD, 0), size=mp.Vector3(0, gp)))
    return sim, refl, tran, sx


def run_periodic(gp, gh, gdc, orders, resolution=RESOLUTION, layout=False):
    """Reference (all glass) then grating. Returns P_in-normalised T_m, T_total, R and the order amplitudes."""
    sim, refl, tran, sx = periodic_cell(gp, gh, gdc, resolution, empty=True)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(0.5 * sx - DPML - 0.5 * DPAD, 0), 1e-6))  # (6)
    P_in = float(mp.get_fluxes(tran)[0])                      # incident power per period (measured in glass)
    refl_data = sim.get_flux_data(refl)

    sim, refl, tran, sx = periodic_cell(gp, gh, gdc, resolution)
    sim.load_minus_flux_data(refl, refl_data)
    if layout:
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(8.6, 4.2),
            title=f"one period: glass substrate + ridge, PML in x only, Bloch-periodic in y (period {gp} um)",
            params_text=f"wl={wl}  res={resolution}\nL={gp} h={gh} dc={gdc}",
            params_xy=(1.5, 1.15), pml_xy=(-2.6, -1.0), decay_point=(0.5 * sx - DPML - 0.5 * DPAD, 0), decay_text_xy=(1.4, -1.0),
            labels=[Label("glass substrate + ridge (geometry)", (-0.5 * sx + DPML + DSUB + 0.25, 0.3), (-2.0, 0.95), step=2, color="black"),
                    Label("plane-wave source in the glass", (-0.5 * sx + DPML + 0.5 * DSUB, -0.6), (-2.3, -1.15), step=3, color="red"),
                    Label("flux: reflection (glass) / transmission (air)", (0.5 * sx - DPML - 0.5 * DPAD, -0.2), (-0.1, -0.55), step=5, color="blue")],
            axis_step=1.0)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(0.5 * sx - DPML - 0.5 * DPAD, 0), 1e-6))
    # ------------------------------------------------------------ (7) orders by DiffractedPlanewave, totals by flux
    # one DiffractedPlanewave per call: order m along the periodic direction y, s-polarised (Ez)
    amp = {m: sim.get_eigenmode_coefficients(tran, mp.DiffractedPlanewave((0, m, 0), mp.Vector3(0, 1, 0), 1, 0)).alpha[0, 0, 0]
           for m in orders}
    T_m = {m: float(abs(a) ** 2 / P_in) for m, a in amp.items()}
    phase_m = {m: float(np.angle(a)) for m, a in amp.items()}
    return {"T_m": T_m, "phase_m": phase_m, "T_total": float(mp.get_fluxes(tran)[0] / P_in),
            "R": float(-mp.get_fluxes(refl)[0] / P_in), "P_in": P_in}


source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ A. diffraction orders of the 2.6 um grating
angles = orders_propagating(GP_A)
A = run_periodic(GP_A, GH_A, GDC_A, sorted(angles), layout=True)
sum_orders = sum(A["T_m"].values())
print(f"A. period {GP_A} um: propagating orders {sorted(angles)} at " + ", ".join(f"m={m}: {a:+.1f} deg" for m, a in sorted(angles.items())))
print(f"A. T_m = " + ", ".join(f"m={m}: {t:.4f}" for m, t in sorted(A['T_m'].items())) +
      f"; sum = {sum_orders:.4f}, T_total (flux) = {A['T_total']:.4f}, R = {A['R']:.4f}, T+R = {A['T_total'] + A['R']:.4f}")
bar_figure([f"m = {m}\n({angles[m]:+.1f} deg)" for m in sorted(angles)] + ["sum of orders", "T (flux)", "R", "T + R"],
           {"fraction of incident power": [A["T_m"][m] for m in sorted(angles)] + [sum_orders, A["T_total"], A["R"], A["T_total"] + A["R"]]},
           os.path.join(OUT, "02_orders.png"), ylabel="fraction of incident power", reference=1.0, reference_label="lossless: 1", figsize=(8, 4))
convergence = [{"resolution": RESOLUTION, **{f"T_{m}": A["T_m"][m] for m in sorted(angles)}, "R": A["R"], "T_plus_R": A["T_total"] + A["R"]}]
for res in (50,):
    Ar = run_periodic(GP_A, GH_A, GDC_A, sorted(angles), resolution=res)
    convergence.append({"resolution": res, **{f"T_{m}": Ar["T_m"][m] for m in sorted(angles)}, "R": Ar["R"], "T_plus_R": Ar["T_total"] + Ar["R"]})
    print(f"convergence res={res}: " + ", ".join(f"T_{m}={Ar['T_m'][m]:.4f}" for m in sorted(angles)) + f", R={Ar['R']:.4f}, T+R={Ar['T_total'] + Ar['R']:.4f}")

# ================================================================ B. subwavelength period: duty-cycle sweep of the zeroth order
duty = np.linspace(0.1, 0.9, 9)
sweep = {}
for gh in (0.35, 0.9):
    rows = [run_periodic(GP_B, gh, float(d), [0]) for d in duty]
    T0 = np.array([r["T_m"][0] for r in rows])
    ph = np.unwrap(np.array([r["phase_m"][0] for r in rows]))
    ph -= ph[0]
    step = float(np.max(np.abs(np.diff(ph))))
    sweep[gh] = {"duty": duty.tolist(), "T0": T0.tolist(), "phase": ph.tolist(), "span_over_2pi": float((ph.max() - ph.min()) / (2 * np.pi)),
                 "estimate_dn_h_over_wl": (n_glass - 1) * gh / wl, "max_step_rad": step,
                 "T_total_minus_T0_max": float(max(abs(r["T_total"] - r["T_m"][0]) for r in rows))}
    print(f"B. h={gh}: T0 in [{T0.min():.3f}, {T0.max():.3f}], phase span = {sweep[gh]['span_over_2pi']:.3f} x 2pi "
          f"(estimate dn*h/wl = {sweep[gh]['estimate_dn_h_over_wl']:.3f}), max step {step:.2f} rad, max|T_total - T0| = {sweep[gh]['T_total_minus_T0_max']:.1e}")
fig, ax = plt.subplots(1, 2, figsize=(11, 3.9))
for gh, st in ((0.35, "o-"), (0.9, "s--")):
    ax[0].plot(duty, sweep[gh]["T0"], st, label=f"h = {gh} um")
    ax[1].plot(duty, np.array(sweep[gh]["phase"]) / (2 * np.pi), st, label=f"h = {gh} um  (span {sweep[gh]['span_over_2pi']:.2f}, estimate {sweep[gh]['estimate_dn_h_over_wl']:.2f})")
ax[0].set_xlabel("duty cycle (ridge width / period)"); ax[0].set_ylabel("zeroth-order transmission T0"); ax[0].set_ylim(0, 1.05); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
ax[0].set_title(f"subwavelength period {GP_B} um: amplitude side", fontsize=9)
ax[1].axhline(1.0, color="crimson", ls="--", lw=1.0); ax[1].text(0.12, 1.02, "2 pi (what a phase library needs)", color="crimson", fontsize=8)
ax[1].set_xlabel("duty cycle"); ax[1].set_ylabel("phase of T0 / 2 pi  (relative to duty 0.1)"); ax[1].set_ylim(-0.05, 1.15); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
ax[1].set_title("phase side: prototype of a phase library", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_duty_sweep.png"), dpi=150); plt.close(fig)

# ================================================================ C. finite grating: the beams, and the angle from a spatial FFT
N_RIDGE = 8
RES_C = 15
pad_y = 3.0
sx_c = DPML + DSUB + GH_A + 10.0 + DPML
sy_c = N_RIDGE * GP_A + 2 * pad_y + 2 * DPML
x_ridge = -0.5 * sx_c + DPML + DSUB + 0.5 * GH_A


def finite_geometry(with_ridges):
    g = [mp.Block(material=glass, size=mp.Vector3(DPML + DSUB, mp.inf, mp.inf), center=mp.Vector3(-0.5 * sx_c + 0.5 * (DPML + DSUB), 0))]
    if with_ridges:
        for i in range(N_RIDGE):
            yc = (i - (N_RIDGE - 1) / 2) * GP_A
            g.append(mp.Block(material=glass, size=mp.Vector3(GH_A, GDC_A * GP_A, mp.inf), center=mp.Vector3(x_ridge, yc)))
    return g


def finite_sim(with_ridges, fw=fwidth, resolution=RES_C):
    return mp.Simulation(cell_size=mp.Vector3(sx_c, sy_c), resolution=resolution, boundary_layers=[mp.PML(DPML)],
                         geometry=finite_geometry(with_ridges),
                         sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=True), component=mp.Ez,
                                            center=mp.Vector3(-0.5 * sx_c + DPML + 0.5 * DSUB, 0), size=mp.Vector3(0, sy_c))])


nonpml_c = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx_c - 2 * DPML, sy_c - 2 * DPML))
extent_c = [-(sx_c / 2 - DPML), sx_c / 2 - DPML, -(sy_c / 2 - DPML), sy_c / 2 - DPML]
fields = {}
for tag, ridges in (("flat", False), ("grating", True)):
    sim = finite_sim(ridges)
    dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml_c)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mp.Vector3(0.5 * sx_c - DPML - 1.0, 0), 1e-5))
    fields[tag] = sim.get_dft_array(dft, mp.Ez, 0)
    if ridges:
        eps_c = sim.get_array(vol=nonpml_c, component=mp.Dielectric)
ez_sc = fields["grating"] - fields["flat"]                 # scattered field: what the ridges added
nx, ny = ez_sc.shape
xs = np.linspace(extent_c[0], extent_c[1], nx); ys = np.linspace(extent_c[2], extent_c[3], ny)
x_cut = x_ridge + 8.0                                      # far cut, 8 um past the ridges, in homogeneous air
line = ez_sc[np.argmin(abs(xs - x_cut)), :]
ky = np.fft.fftshift(np.fft.fftfreq(ny, d=ys[1] - ys[0]))  # cycles per um
spec = np.abs(np.fft.fftshift(np.fft.fft(line * np.hanning(ny)))) ** 2
spec /= spec.max()
pos = ky > 0.15
k_peak = float(ky[pos][np.argmax(spec[pos])])
theta_meas = float(np.degrees(np.arcsin(min(k_peak * wl, 1.0))))   # sin(theta) = k_y / k0 = k_peak * wl
print(f"C. finite grating ({N_RIDGE} ridges): spatial-FFT peak at {k_peak:.3f} cycles/um -> theta = {theta_meas:.1f} deg "
      f"(grating equation: 1/period = {1/GP_A:.3f} cycles/um -> {angles[1]:.1f} deg)")

fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1.5, 1]})
im = ax[0].imshow(np.abs(fields["grating"]).T, origin="lower", extent=extent_c, cmap="inferno", aspect="equal")
ax[0].contour(xs, ys, eps_c.T, levels=[0.5 * (eps_c.min() + eps_c.max())], colors="w", linewidths=0.5)
for m, a in angles.items():
    L = 9.0
    ax[0].plot([x_ridge, x_ridge + L * np.cos(np.radians(a))], [0, L * np.sin(np.radians(a))], "--", color="cyan", lw=1.0)
    ax[0].text(x_ridge + L * np.cos(np.radians(a)) + 0.2, L * np.sin(np.radians(a)), f"m={m:+d}", color="cyan", fontsize=8, va="center")
ax[0].axvline(x_cut, color="lime", ls=":", lw=1.0); ax[0].text(x_cut, extent_c[3] - 0.8, "FFT cut", color="lime", fontsize=8, ha="center")
ax[0].set_xlabel("x [um]"); ax[0].set_ylabel("y [um]"); ax[0].set_title(f"|Ez| at 1550 nm, {N_RIDGE} ridges; dashed = grating-equation angles", fontsize=9)
fig.colorbar(im, ax=ax[0], shrink=0.8)
ax[1].semilogy(ky, spec, color="tab:blue")
for m in (-1, 1):
    ax[1].axvline(m / GP_A, color="crimson", ls="--", lw=0.9)
ax[1].text(1 / GP_A, 1.2, f"+1/period = {1/GP_A:.3f}", color="crimson", fontsize=8, ha="center")
ax[1].set_xlim(-1.2, 1.2); ax[1].set_ylim(1e-4, 3); ax[1].set_xlabel("spatial frequency k_y / 2pi [cycles/um]"); ax[1].set_ylabel("|FFT(E_scat on the cut)|^2 (norm.)")
ax[1].set_title(f"peak {k_peak:.3f} -> {theta_meas:.1f} deg (equation {angles[1]:.1f} deg)", fontsize=9); ax[1].grid(alpha=0.3, which="both")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_finite.png"), dpi=150); plt.close(fig)

# ================================================================ D. GIF: the beams forming in time
fw_anim = 0.3 * fcen
sim_anim = finite_sim(True, fw=fw_anim, resolution=12)
sim_anim.init_sim()
eps_anim = sim_anim.get_array(vol=nonpml_c, component=mp.Dielectric)
frames, times = record_frames(sim_anim, nonpml_c, mp.Ez, t_start=5 / fw_anim - 2 / fw_anim, t_end=5 / fw_anim + 1.5 * sx_c + 10, n_frames=60)
animate_fields(frames, times, extent_c, os.path.join(OUT, "05_anim_finite.gif"), eps=eps_anim, figsize=(5.2, 6.4), dpi=70,
               title=f"{N_RIDGE}-ridge grating, plane wave from the left", legend_loc="lower right")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"A": {"period": GP_A, "angles_deg": angles, **{k: A[k] for k in ("T_m", "phase_m", "T_total", "R")}, "sum_orders": sum_orders},
                   "convergence": convergence, "B": {str(k): v for k, v in sweep.items()},
                   "C": {"n_ridges": N_RIDGE, "k_peak_cycles_per_um": k_peak, "theta_meas_deg": theta_meas, "theta_eq_deg": angles[1]},
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
{% endhighlight %}
</details>

<details markdown="1">
<summary>Show original logs and the reproduction environment</summary>

Unlike the excerpts in §4, the full code includes the finite-grating experiment (C), figure saving, GIF recording, and result.json output. The shared figure helper `blogfig.py` is in the same `code/` folder. Full code and helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**Execution results (run on 2026-10-23)**:
```
A. period 2.6 um: propagating orders [-1, 0, 1] at m=-1: -36.6 deg, m=0: +0.0 deg, m=1: +36.6 deg
A. T_m = m=-1: 0.0884, m=0: 0.7591, m=1: 0.0884; sum = 0.9358, T_total (flux) = 0.9358, R = 0.0635, T+R = 0.9994
convergence res=50: T_-1=0.0881, T_0=0.7597, T_1=0.0881, R=0.0639, T+R=0.9998
B. h=0.35: T0 in [0.829, 0.969], phase span = 0.089 x 2pi (estimate dn*h/wl = 0.113), max step 0.13 rad, max|T_total - T0| = 2.6e-06
B. h=0.9: T0 in [0.846, 0.950], phase span = 0.229 x 2pi (estimate dn*h/wl = 0.290), max step 0.33 rad, max|T_total - T0| = 2.6e-06
C. finite grating (8 ridges): spatial-FFT peak at 0.372 cycles/um -> theta = 35.2 deg (grating equation: 1/period = 0.385 cycles/um -> 36.6 deg)
```

**Reproduction environment**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · run `python binary_grating.py` (about 27 s, single core)

</details>

<details markdown="1">
<summary>Explore applications and next topics</summary>

### Applications

Diffraction gratings are shared components of spectrometers, fiber couplers, AR glasses, and holograms. Their order efficiencies determine component performance.

| Application | What this lesson provides | Next step |
|---|---|---|
| Spectrometers and monochromators | Order efficiencies, grating equation | Chapter 16: far field |
| Grating coupler (fiber ↔ chip) | Concentrating power in one order, angle | Chapter 07: meta-atoms |
| AR waveguide gratings, holograms, diffractive optical elements (DOE) | Phase produced by duty cycle | Chapter 07: phase library |
| Beam angle of a finite grating | Diffraction angle measured by FFT | Chapter 16 |

</details>

- [Official binary_grating.py example](https://github.com/NanoComp/meep/blob/master/python/examples/binary_grating.py) · [Tutorial: Diffraction Spectrum of a Binary Grating](https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#diffraction-spectrum-of-a-binary-grating)
- [`DiffractedPlanewave` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#diffractedplanewave) · [Bloch-periodic boundaries and `k_point`](https://meep.readthedocs.io/en/latest/FAQ/#how-do-i-model-a-periodic-structure)
- Previous: [05 · Bent waveguide and radius trade-off]({{ '/en/waveguide-bend-90/' | relative_url }}) · Next: [07 · Metalens meta-atoms and phase library]({{ '/en/meta-atom/' | relative_url }})
