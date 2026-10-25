---
layout: lesson
permalink: /en/meta-atom/
lesson_title: "Can ridge width alone steer light?"
lesson_summary: "Build a table mapping Si ridge width to phase, then select four ridges to tilt the wavefront. Investigate the gap between unit-cell predictions and actual array efficiency."
lesson_goals:
  - "Read a phase library using complex-transmission amplitude and phase."
  - "Connect a four-step phase pattern to the target diffraction angle."
  - "Distinguish measured efficiency from an ideal upper bound and resolution error."
lesson_prerequisites: "Familiarity with periodic cells, diffraction orders, and duty-cycle phase in chapter 06 is helpful. Running the examples requires Meep and Python."
date: 2026-10-23
title: "Meep Example 07 · Metalens meta-atoms and phase libraries — phase from width, steering with four steps, and where the design approximation fails"
title_en: "Meep Example 07 · Meta-atoms and a phase library — turning phase with a width, a 4-level deflector, and where the design falls short"
lang: en
translation_key: meta-atom
series: meep-examples
part: 7
level: intermediate
runtime: "35 s (single core)"
meep_version: "1.33.0"
official_example: "https://github.com/NanoComp/meep/blob/master/python/examples/metasurface_lens.py"
tags: [meep, fdtd, metasurface, meta-atom, phase-library, blazed-grating, near2far]
image: /assets/meep/07/04_supercell.png
excerpt: "a silicon bar in a 0.45 µm unit cell is a meta-atom. Sweep its width, record the complex transmission t(w), and you have a phase library. Pick four widths that step the phase by 90°, tile them into a 1.8 µm supercell, and the structure should deflect 1550 nm light to +59.4°."
---
<details markdown="1">
<summary>English summary</summary>

- **What**: a silicon bar in a 0.45 µm unit cell is a meta-atom. Sweep its width, record the complex transmission t(w), and you have a phase library. Pick four widths that step the phase by 90°, tile them into a 1.8 µm supercell, and the structure should deflect 1550 nm light to +59.4°.
- **Result**: the library covers 1.10 × 2π with \|t\| between 0.69 and 1.01. The 4-level supercell sends 51 % of the power into the +1 order, 16 % into −1 and 3 % straight through; that is 63 % of the 4-level blazed bound 0.81. A 40-atom array peaks at 58.5°.
- **Takeaway**: the library assumes every neighbour is identical. In the real supercell they are not, so the local-phase approximation leaks power into the wrong orders. That gap is what inverse design (post 08) closes.
- **Code**: full script at the bottom, ~35 s on one core.

</details>

<h2 id="observe">1. Observe · Follow the light</h2>

Four Si ridges of different widths form a repeating array. Light enters upward from below, and the transmitted wavefront tilts right. Check the order-efficiency bars on the left to see **whether all light enters the right-going +1 order**.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/07/04_supercell.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/07/04_supercell.png' | relative_url }}" alt="Order efficiencies and actual Re(Ez) and amplitude fields of a four-ridge Si supercell. Order +1 is strongest, but other orders remain." loading="lazy">
  </a>
<figcaption>The target +1 efficiency is about 0.514; orders −1 and 0 retain power. The dashed 0.811 line is the ideal four-step phase-model reference assuming uniform amplitude.</figcaption>
</figure>

<figure class="lesson-figure lesson-animation">
  <a href="{{ '/assets/meep/07/06_anim_array.gif' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/07/06_anim_array.gif' | relative_url }}" alt="A pulse transmitted through 12 Si ridges propagates with its wavefront tilted right" loading="lazy" data-animation-src="{{ '/assets/meep/07/06_anim_array.gif' | relative_url }}" data-static-src="{{ '/assets/meep/07/04_supercell.png' | relative_url }}">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
<figcaption>A short pulse (fwidth 0.4 fcen) enters a 12-atom array from below. Beyond the ridges, the wavefront travels tilted right. The phase gradient sets its direction; the aperture sets its width.</figcaption>
</figure>

<h2 id="predict">2. Predict · Before reading the results</h2>

If a unit-cell phase library covers the full 2π range, must an array of four selected ridges send 100% into the target order?

<fieldset class="prediction">
  <legend>Choose an answer first.</legend>
  <label><input type="radio" name="prediction-07" value="0"> Yes: every required phase is available, so efficiency is 100%</label>
  <label><input type="radio" name="prediction-07" value="1"> No: amplitude differences and changed neighbors can reduce efficiency</label>
</fieldset>

<details markdown="1">
<summary>Check the reasoning</summary>

The second answer is correct. Four-step phase quantization alone limits the ideal model to about 0.811. Actual ridges have unequal amplitudes, and their neighbors differ from the identical neighbors assumed in the unit-cell library. Full 2π coverage enables phase selection; it does not guarantee 100% efficiency.

</details>

<h2 id="understand">3. Understand · Explain what you observed</h2>

{% include chapter-illustration.html %}

<!-- concept-illustration:part-07:start -->

<p class="lesson-note">Si (n = 3.45) ridges sit on a SiO₂ (n = 1.45) substrate, with light entering along +y from within the substrate. Ridge height is 0.9 µm; widths 75, 100, 175, and 225 nm approximate four relative phase steps. The four-section period of 1.8 µm repeats along x, targeting +1 at about 59.4° to the right of the +y normal. The 0°, 90°, 180°, and 270° labels are target relative phases, not exact measured values. Depth shading explains the geometry; the actual 2D ridges extend infinitely along z.</p>

<!-- concept-illustration:part-07:end -->

### A phase library maps width to phase

At 1550 nm, only order 0 propagates in a unit cell of period 0.45 µm. Average the complex DFT field over one period above the ridge and divide by the ridge-free reference to obtain complex transmission t(w). Its magnitude is amplitude; its argument is phase. Recording both as width changes produces the library.

$$t(w)=\frac{\langle E_z\rangle(w)}{\langle E_z\rangle(0)}$$

Use `np.unwrap` to connect phase samples, but it cannot reliably recover changes that are too large between samples. Also inspect widths with strongly reduced amplitude. Here t is a **field ratio relative to the ridge-free reference**, so its magnitude alone is not an efficiency relative to incident power.

### Four widths create a tilted wavefront

The four sections target relative phases of 0°, 90°, 180°, and 270°. Shifting their common starting phase φ₀ leaves the phase gradient and target angle unchanged. Use this freedom to avoid widths with very small amplitudes.

$$\Lambda=4\times0.45=1.8\;\mu\mathrm{m},\qquad \sin\theta_{+1}=1.55/1.8$$

The target angle is 59.4° right of the +y normal. Selected widths are 75, 100, 175, and 225 nm. The library for each ridge assumes **infinitely repeated identical-width neighbors**. Once different widths become neighbors, that approximation needs validation.

<aside class="lesson-note" markdown="1">
**The four phases in the concept figure are targets.** Do not confuse them with measured phases. This calculation uses 2D Ez, normal incidence, and lossless Si (3.45) and SiO₂ (1.45). Results for infinitely long z-directed ridges do not directly establish the performance of a real 3D metalens.
</aside>

<details markdown="1">
<summary>Show notation, assumptions, and predictions</summary>

A Si ridge in a unit cell of period Λ_a = 0.45 µm (0.29 times the wavelength) has no higher propagating diffraction orders. Only order 0 propagates, so one complex transmission coefficient t(w) summarizes the cell. Wider ridges increase effective index and accumulated phase. With H = 0.9 µm and Δn ≈ 2.45, the estimate Δn·H/λ = 1.4 turns suggests more than one full turn is available.

Steering into +1 requires transmission phase proportional to x: φ(x) = 2πx/Λ. Set Λ = 4Λ_a = 1.8 µm and assign 0°, 90°, 180°, and 270° to four sections for a staircase approximation. An N-step discretized blazed grating has ideal +1 efficiency sinc²(1/N), or 0.81 at N = 4. Two further effects reduce it: nonuniform \|t\| and the mismatch between identical-neighbor periodic library assumptions and actual different-width neighbors.

$$
t(w)=\frac{\langle E_z\rangle_{\text{period}}(w)}{\langle E_z\rangle_{\text{period}}(0)},\qquad
\phi_{\text{target}}(x)=\frac{2\pi x}{\Lambda},\qquad
\sin\theta_{+1}=\frac{\lambda}{\Lambda}=\frac{1.55}{1.8}\Rightarrow 59.4^\circ,\qquad
\eta_{+1}\le\mathrm{sinc}^2\!\Big(\frac1N\Big)=0.811
$$

| Symbol | Meaning | Code variable |
|------|----|-----------|
| Λ_a, Λ | Atom period 0.45, supercell period 1.8 µm | `LA`, `LAMBDA` |
| w, H | Ridge width (design variable), height 0.9 µm | `widths`, `H` |
| t(w) | Zeroth-order complex transmission normalized to an empty cell | `t_atom(w) / t_atom(0)` |
| φ₀ | Starting point of four target phases (global phase) | `phi0` |
| w_lib | Four selected widths, pixel-aligned | `w_lib` |
| η_m | Order-m efficiency relative to incident flux | `orders[m]["eff"]` |
| θ_d | Design deflection angle 59.44° | `THETA_D` |

**Assumptions and validity**: 2D, Ez polarization, normal incidence, lossless Si (3.45) and SiO₂ (1.45). Build the library at res 40 and compare against res 60. The far field is the angular distribution for a 2D line focus.

### Make predictions before seeing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| Phase span (H 0.9, Si) | More than one turn | 70–80% of Δn·H/λ = 1.4, based on chapter 06 |
| Phase monotonicity | Increases monotonically with w | Wider ridges increase effective index |
| \|t\| | Falls at larger w | Ridge resonance and reflection |
| +1 efficiency | Below 0.81, around 0.5–0.7 | Four-step limit × amplitude nonuniformity × neighbor coupling |
| Orders −1 and 0 | Nonzero; sum 0.1–0.2 | Leakage from the staircase approximation |
| 40-atom beam direction | Near 59°; 10 atoms deviate more | A short aperture broadens the beam and shifts its peak |

**Acceptance criteria**: a difference above 1 percentage point between the order sum and total transmitted flux indicates decomposition error. Adjacent unwrapped phase changes above π indicate insufficient sampling.

</details>

<h2 id="run">4. Run · Change one variable</h2>

### Change one thing: design resolution

1. Run `python meta_atom.py` in the `code/` folder containing `meta_atom.py` and `blogfig.py`. Keep the four selected widths and +1 efficiency from baseline `result.json`.
2. Change **only `RES = 40` to `RES = 60`**, then rerun. Retain all 17 width samples and the other geometry and parameters.
3. Compare widths selected from the new library and the supercell +1 efficiency with the original. Check that each order sum still matches total transmitted flux.

The original includes a resolution-60 library comparison, but **does not record the efficiency of an array redesigned from that library**. Obtain it in this new experiment. Recomputing only a subset of widths can change the unwrap branch, so use the full sample set.

<details markdown="1">
<summary>Show the setup, source, and parameters</summary>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/07/01_layout.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/07/01_layout.png' | relative_url }}" alt="Four Si ridges on a SiO2 substrate, with source, mode monitor, and y PML" loading="lazy">
  </a>
<figcaption>Supercell (experiment C). Bottom black band: SiO₂ substrate extending through bottom PML; four black ridges: designed Si meta-atoms; red horizontal line: plane-wave source in the substrate; blue line: order-resolving mode monitor; green hatching: y PML. The x boundaries are periodic. Purple ×: decay-monitoring point. Circled numbers correspond to §4. The unit cell (experiment A) is one quarter as wide and contains one ridge.</figcaption>
</figure>

| Parameter | Value | Why this value | Effect of a change |
|----------|-----|-------------|--------|
| Λ_a | 0.45 µm | Exactly 18 px at res 40; otherwise Meep rounds the cell, mismatching actual period and k_x = m/Λ | θ_d changes accordingly |
| Λ = 4Λ_a, θ_d | 1.8 µm, 59.44° | Fix an integer-pixel period first, then derive θ_d | — |
| H | 0.9 µm | Near the minimum height for more than 2π | Lowering it gives span < 2π |
| `widths` | 0.04–0.42, 17 samples | Dense enough for adjacent phase differences < π | Sparse samples can mis-unwrap by 2π |
| `RES` | 40 (convergence: 60) | A 0.075 µm ridge spans 3 px | At 60, phase changes by up to 0.82 rad (§5) |
| Stopping rule | Ez at monitor decays to 1e-7 | Captures the narrowband (fwidth 0.1 fcen) pulse tail | Fixed times give width-dependent errors |
| Far field | R = 200 µm, 341 angles, source spans only the array | Avoids a 0° artifact from light passing beside the array | A full-cell source exaggerates 0° |

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/07/00_source.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/07/00_source.png' | relative_url }}" alt="Gaussian source waveform and narrowband spectrum for the meta-atom experiment" loading="lazy">
  </a>
<figcaption>Source waveform and spectrum: fwidth 0.1 fcen, width 15.5, t0 = 77.5.</figcaption>
</figure>

**Difference from the lecture notebook**: none in parameters, procedure, or numbers; these match week 8 (phase span 1.101 × 2π, four design widths, +1 efficiency 0.514). Sections §4 and §6 add two lessons from reproducing the official metasurface_lens example in 10_sources: do not read wrapped phase jumps as physical discontinuities, and place target phases on the same 2π branch as the library.

</details>

<details markdown="1">
<summary>Walk through the code</summary>

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → run and stop → postprocessing.
> Propagation is along +y, swapping x and y relative to chapter 06. Experiment A (library) uses a unit cell; C (supercell) uses a four-times-wider cell; D (far field) uses a finite cell with PML on all sides.

### ① Units and parameters — which numbers stay fixed

```python
wl = 1.55; fcen = 1 / wl; fwidth = 0.1 * fcen
Si, SiO2 = mp.Medium(index=3.45), mp.Medium(index=1.45)
N_SEC = 4                       # phase levels per supercell period
LA = 0.45                       # atom period [um]: 18 px at resolution 40
LAMBDA = N_SEC * LA             # supercell period 1.80 um
THETA_D = np.degrees(np.arcsin(wl / LAMBDA))   # 59.44 deg
H = 0.9                         # bar height [um]
RES = 40
DPML, DSUB, DAIR = 1.0, 1.0, 1.0
SY = DPML + DSUB + H + DAIR + DPML
Y_BOT = -0.5 * SY; Y_DEV = Y_BOT + DPML + DSUB; SRC_Y = Y_BOT + DPML + 0.3; MON_Y = -Y_BOT - DPML - 0.3
BLAZED_BOUND = (np.sin(np.pi / N_SEC) / (np.pi / N_SEC)) ** 2   # 0.8106
```

- **What**: first fix the atom period to an integer number of pixels, then derive supercell period and deflection angle. Calculate the blazed-grating limit here too.
- **Why**: choosing θ_d = 60° gives Λ = 1.7898 µm, not an integer number of pixels. Meep’s cell rounding then mismatches the actual period with k_x = m/Λ. Fixing the period before deriving the angle avoids this.
- **If wrong**: a cell-rounding warning appears and ±1 angles and efficiencies are slightly wrong. The period 1.2 µm rounded at res 22 in chapter 06 was the same issue.

### ② Materials and geometry — what goes where

```python
def geometry_bars(widths, period):
    g = [mp.Block(center=mp.Vector3(0, Y_BOT + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2)]
    n = len(widths)
    for j, w in enumerate(widths):
        if w > 0:
            xj = -0.5 * period + (j + 0.5) * period / n
            g.append(mp.Block(center=mp.Vector3(xj, Y_DEV + 0.5 * H), size=mp.Vector3(w, H), material=Si))
    return g
```

- **What**: one Si ridge per section above the substrate. `widths=[w]` creates a unit cell; `widths=w_lib` creates a four-section supercell.
- **Why**: both must use the same geometry function to make comparisons meaningful. Width w = 0 is the ridge-free reference.
- **If wrong**: off-center ridges introduce offsets into the phase pattern and increase order 0.

### ③ Source — how light enters

```python
def plane_wave(period, fw=fwidth, integrated=False):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=integrated), component=mp.Ez,
                      center=mp.Vector3(0, SRC_Y), size=mp.Vector3(period, 0))]
```

- **What**: a horizontal line source spanning the cell inside the substrate, producing a +y plane wave.
- **Why**: in a periodic cell, source width equals period and represents a plane wave. Only the finite-array experiment D uses `is_integrated=True` and a source spanning the array alone.
- **If wrong**: a full-cell-width source in the finite-array experiment illuminates bare substrate beside the array, producing a large artificial 0° peak.

### ④ Simulation and boundaries — the cell and PML

```python
def periodic_sim(widths, period, resolution=RES):
    return mp.Simulation(resolution=resolution, cell_size=mp.Vector3(period, SY), geometry=geometry_bars(widths, period),
                         boundary_layers=[mp.PML(thickness=DPML, direction=mp.Y)], k_point=mp.Vector3(),
                         sources=plane_wave(period))
```

- **What**: PML along y only, periodic x boundaries with `k_point=0`; the axes are swapped relative to chapter 06.
- **Why**: unit-cell t(w) describes a ridge inside an infinite periodic array. Later we test where this assumption breaks.
- **If wrong**: adding x PML to the unit cell computes isolated-ridge scattering and changes the meaning of t(w).

### ⑤ Monitors — what is measured

```python
# A. unit cell: DFT of Ez on a line across one period; its mean is the zeroth Fourier coefficient
dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(0, MON_Y), size=mp.Vector3(LA, 0))
t = np.mean(sim.get_dft_array(dft, mp.Ez, 0))
# C. supercell: a mode monitor across the period, decomposed order by order
mon = sim.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0)))
a_m = sim.get_eigenmode_coefficients(mon, mp.DiffractedPlanewave((m, 0, 0), mp.Vector3(1, 0, 0), 1, 0)).alpha[0, 0, 0]
```

- **What**: average the complex DFT across one unit-cell period to obtain t; in the supercell, obtain order amplitudes as in chapter 06.
- **Why**: the average of a periodic function over one period is its zeroth Fourier coefficient. Only order 0 propagates in the subwavelength cell, so this average represents propagating transmission. Use `get_dft_array`, not `get_array`, because a steady-state complex amplitude is required rather than a final-time snapshot.
- **If wrong**: `get_array` averages residual fields after the pulse. A monitor immediately above a ridge includes evanescent fields; here it is 0.7 µm above.

### ⑥ Run and stopping condition — when to stop

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(10, mp.Ez, mp.Vector3(0, MON_Y), 1e-7))
```

- **What**: wait for Ez at the monitor to decay to 10⁻⁷, using the same condition for all 34 library runs.
- **Why**: complex phase is more sensitive to pulse tails than amplitude, so the threshold is stricter than the usual 10⁻⁶.
- **If wrong**: width-dependent stopping times are acceptable; a fixed time can leave tails at some widths and corrupt phase.

### ⑦ Postprocessing — extracting the numbers

```python
t_ref = t_atom(0.0)
t = np.array([t_atom(w) / t_ref for w in widths])
phase = np.unwrap(np.angle(t)); phase -= phase[0]          # library: |t|, relative phase

# design: for each trial phi0, four targets phi0 + k*pi/2 -> widths by inverse interpolation; keep the phi0 with the largest min|t|
targets = phi0 + np.arange(N_SEC) * (2 * np.pi / N_SEC)
ws = np.interp(targets, ph_dense, w_dense)
w_lib = np.round(ws * RES) / RES                            # snap to the pixel grid

eff_m = abs(a_m) ** 2 / P_in                               # supercell: efficiency per order, P_in from an all-SiO2 run
```

- **What**: unwrap the phase of reference-normalized t, invert the library to select widths for target phases, and choose global phase φ₀ to increase min\|t\|. Align widths to pixels.
- **Why**: `np.angle` returns wrapped values in (−π, π]. As noted in the 10_sources phase-map discussion, apparent jumps may be branch cuts rather than physical discontinuities. Unwrapping is reliable only for neighboring changes below π, hence dense width sampling. Library phases are relative, so a common offset is available to improve amplitude uniformity.
- **If wrong**: clipping targets on a different 2π branch pushes all four widths toward the library minimum, as in a 10_sources failure. Omitting pixel alignment rounds supercell widths differently from the library.

> **Pitfall**: recomputing only a sparse width subset for convergence can mis-unwrap phase by 2π. Rebuild the library on the entire original width grid before comparing (§5).

</details>

<h2 id="interpret">5. Interpret · Read the measurements and their limits</h2>

### One full phase turn does not mean 100% efficiency

The original library covers **1.101 × 2π**, with amplitudes 0.689–1.011. Selected-width amplitudes are nonuniform: 1.001, 0.959, 0.885, and 0.885.

| Actual supercell order | Angle | Efficiency relative to incident flux |
|---|---|---|
| −1 | −59.4° | 0.1576 |
| 0 | 0° | 0.0325 |
| +1 | +59.4° | 0.5144 |

Their sum 0.7045 matches total transmitted flux. Target-order efficiency 0.5144 is 63.5% of the ideal four-step value 0.8106. **This experiment alone cannot quantitatively separate** the contributions of amplitude nonuniformity and neighbor coupling.

Aperture matters for a finite array. The peak is 49.5° for 10 ridges (4.5 µm) and 58.5° for 40 ridges (18 µm). The wider array produces a narrower beam closer to the 59.4° target.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/07/02_library.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/07/02_library.png' | relative_url }}" alt="Transmission amplitude and relative phase versus ridge width, and phase difference between resolutions 40 and 60" loading="lazy">
  </a>
<figcaption>Left: &#124;t&#124;. Center: phase relative to w = 0.04, in units of 2π. Right: phase difference from resolution 40 → 60. Phase increases monotonically through 1.10 turns. Amplitude falls to about 0.7 near w ≈ 0.13 and 0.3. Resolution differences are 0.49 rad at w = 0.087 and 0.39 rad at 0.42, exceeding 10% of the π/2 design step (green band) at several samples.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/07/03_design.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/07/03_design.png' | relative_url }}" alt="Widths selected for four target phases, their transmission amplitudes, and the supercell geometry" loading="lazy">
  </a>
<figcaption>Left: widths read at four target phases (φ₀ + 0°, 90°, 180°, 270°). Center: &#124;t&#124; at those widths. Right: one resulting supercell period.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/07/05_farfield.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/07/05_farfield.png' | relative_url }}" alt="Far-field angular distributions for arrays of 10 and 40 ridges, compared with the 59.4° design angle" loading="lazy">
  </a>
<figcaption>Far fields of 10-atom (4.5 µm) and 40-atom (18 µm) arrays repeating the library widths. The gray dashed line marks the 59.4° design angle.</figcaption>
</figure>

<aside class="lesson-note" markdown="1">
**The resolution-40 design is not converged.** From 40→60, phase span changes from 1.101→1.163 × 2π, the largest phase difference is about 0.82 rad, and amplitude difference is 0.071. The narrowest selected ridge is only 3 px wide. Efficiency 0.5144 was designed and tested at resolution 40; it does not establish second-decimal accuracy or behavior in 3D, other polarizations, or other wavelengths.
</aside>

<details markdown="1">
<summary>Show all measurements, predictions, and convergence checks</summary>

### A. Phase library



| Quantity | res 40 | res 60 |
|---|---|---|
| Phase span / 2π | 1.101 | 1.163 |
| \|t\| range | 0.689–1.011 | 0.690–1.015 |
| max \|Δφ\| (60 − 40) | — | 0.82 rad (13% of 2π) |

### B. Four-step design



| Section | Target phase | w (µm, pixel-aligned) | \|t\| |
|---|---|---|---|
| 0 | 0.797 rad | 0.075 | 1.001 |
| 1 | 2.368 | 0.100 | 0.959 |
| 2 | 3.938 | 0.175 | 0.885 |
| 3 | 5.509 | 0.225 | 0.885 |

φ₀ = 0.797 rad gives min\|t\| = 0.885. Three of the four widths are below or near 0.1 µm, corresponding to 3–4 px at res 40.

### C. Supercell: where does the light go?



| Order | Angle | Efficiency |
|---|---|---|
| −1 | −59.4° | 0.158 |
| 0 | 0° | 0.033 |
| +1 | +59.4° | 0.514 |
| Sum | | 0.705 = total transmitted flux 0.705 |

The +1 efficiency 0.514 is 63.5% of the 0.811 limit. Remaining power goes into −1 (0.158), 0 (0.033), and reflection (1 − 0.705 = 0.295).

### D. Far field of a finite array



| Array | Aperture | Main lobe | Estimated beamwidth λ/(D cos θ) |
|---|---|---|---|
| 10 atom | 4.5 µm | +49.5° | 38.8° |
| 40 atom | 18 µm | +58.5° | 9.7° |



### Compare against the predictions

| Quantity | Prediction (§2) | Simulation | Verdict |
|--------|-------------|-----------|------|
| Phase span | More than one turn | 1.10 × 2π | ✅ |
| Monotonicity | Monotonic increase | All 17 samples increase | ✅ |
| \|t\| | Falls at larger w | 0.69–0.71 near 0.13 and 0.30 | ✅ |
| +1 efficiency | 0.5–0.7 | 0.514 | ✅ |
| Orders −1 + 0 | 0.1–0.2 | 0.191 | ✅ |
| Beam direction | 40 atoms ≈ 59°; 10 atoms deviate | 58.5°, 49.5° | ✅ |

The predictions agree, but attaining 63.5% of the ideal limit still needs interpretation. The rough amplitude factor 0.885² ≈ 0.78 suggests part of the reduction; changed neighbors provide another mechanism. Each library width was measured with identical neighbors, whereas the supercell places 0.075 beside 0.100 and 0.175 beside 0.225. The sharpest change is the section 3 → 0 boundary (0.225 → 0.075), where a larger phase mismatch is expected. These observations are qualitative, not a measured separation of losses. Chapter 08 uses pixel-level inverse-design freedom to address this gap.

### Convergence

| Quantity | res 40 | res 60 | Note |
|---|---|---|---|
| Phase span / 2π | 1.101 | 1.163 | 6% |
| max \|Δφ\| | — | 0.82 rad | Largest near w = 0.087, 0.42 |
| max Δ\|t\| | — | 0.071 | |

Phase changes by up to 13% of 2π with resolution, about half of a π/2 design step. The narrowest ridge spans only 3 px, so inspect errors specifically over the widths used in the design. The supercell value 0.514 is internally consistent because both design and validation use res 40, but redesigning at res 60 will change the widths and efficiency.

### What the results do and do not establish

- Supported: the Si-ridge library (H 0.9, period 0.45) covers 2π at 1550 nm. The four-step supercell sends 51% into +1, and a finite array directs a beam near the design angle. Agreement of order sum and total flux validates the decomposition.
- Not established: second-decimal accuracy of 0.514; rebuilding the library at res 60 changes selected widths. Nor are 3D, polarization, or wavelength dependence established. Quantitative attribution of loss to the local-phase approximation is unavailable because the two mechanisms were not separately switched off.

</details>

<details markdown="1">
<summary>Show the troubleshooting checklist</summary>

| Symptom | Cause | Fix |
|------|------|----------|
| 2π jumps in the phase curve | Sparse sampling or subset-only recomputation causes unwrap failure | Decrease width spacing and recompute the full grid |
| All four widths collapse to one value | Targets clipped on a different 2π branch | `target_on_map = (target − φ_min) mod 2π + φ_min` |
| Cell-rounding warning, slight angle error | Period is not an integer number of pixels | Fix an integer-pixel period, then derive the angle |
| Large 0° far-field peak | Finite-array source spans the whole cell | Restrict it to array width; use `is_integrated=True` |
| Order sum ≠ total flux | Evanescent orders included or monitor too close to ridges | Keep only \|k_x\| < k₀; move monitor farther away |
| t(w) changes between runs | Using a `get_array` snapshot | Use `add_dft_fields` + `get_dft_array` |

</details>

<h2 id="check">6. Check · Answer two questions</h2>

### 1. Why can a global phase φ₀ change all four widths without changing the target angle?

<details markdown="1">
<summary>Read the explanation</summary>

Adding the same constant to every target phase leaves the spatial phase gradient unchanged, and that gradient determines direction. Selected widths, amplitudes, and actual neighbor coupling can still change, so actual efficiency may differ.

</details>

### 2. Does 2π coverage plus order sum = flux mean the device design is finished?

<details markdown="1">
<summary>Read the explanation</summary>

No. The first checks whether target phases are selectable; the second checks whether order decomposition matches total transmission. Target-order efficiency, resolution convergence, finite aperture, and intended 3D conditions need separate validation.

</details>

<h2 id="reference">7. Reference · Full code and original records</h2>

The complete program below is preserved from the original. Check the execution environment and recorded results together.

<details>
<summary>meta_atom.py (expand to view)</summary>
{% highlight python %}
"""Meep Example 07 - Meta-atoms and a phase library.

Local view of a periodic structure: each Si bar (width w, height H) in a subwavelength unit cell
transmits a plane wave with its own complex coefficient t(w). Collect t(w) -> phase library, pick
4 widths that step the phase by 90 deg, tile them into a supercell that should deflect light to +1,
and check how far the real device falls short of the 4-level blazed bound. Then a finite array and
its far field, and a GIF of the tilted wavefront.

  A. phase library: |t(w)|, arg t(w) at resolution 40 and 60 (reference = empty unit cell)
  B. 4-level design: phase targets phi0 + k*pi/2 -> widths; phi0 chosen to maximise min |t|
  C. supercell (period 4*La): orders by DiffractedPlanewave, sum = total flux, vs sinc^2(1/4) = 0.8106
  D. finite arrays (10 and 40 atoms): near2far pattern, main lobe vs the design angle
  E. GIF: 12-atom array, the wavefront leaves tilted

Run:  python meta_atom.py             (~4 min on one core)
Out:  00_source.png, 01_layout.png, 02_library.png, 03_design.png, 04_supercell.png,
      05_farfield.png, 06_anim_array.gif, result.json   (-> ../assets/07/)
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

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "07")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()

# ---------------------------------------------------------------- (1) units & parameters
wl = 1.55
fcen = 1 / wl
fwidth = 0.1 * fcen
Si = mp.Medium(index=3.45)
SiO2 = mp.Medium(index=1.45)
N_SEC = 4                       # phase levels per supercell period
LA = 0.45                       # atom period [um]: 18 px at resolution 40 (integer pixels matter: see post)
LAMBDA = N_SEC * LA             # supercell period 1.80 um
THETA_D = float(np.degrees(np.arcsin(wl / LAMBDA)))   # +1 order angle: 59.44 deg
H = 0.9                         # bar height [um]
RES = 40
DPML, DSUB, DAIR = 1.0, 1.0, 1.0
SY = DPML + DSUB + H + DAIR + DPML
Y_BOT = -0.5 * SY
Y_DEV = Y_BOT + DPML + DSUB     # substrate top = bar bottom
SRC_Y = Y_BOT + DPML + 0.3      # source inside the substrate
MON_Y = -Y_BOT - DPML - 0.3     # monitor in the air above the bars
BLAZED_BOUND = (np.sin(np.pi / N_SEC) / (np.pi / N_SEC)) ** 2   # 4-level phase quantisation limit


# ---------------------------------------------------------------- (2) geometry: substrate + Si bars
def geometry_bars(widths, period):
    """SiO2 substrate through the bottom PML plus one Si bar per section (bar j centred in section j)."""
    g = [mp.Block(center=mp.Vector3(0, Y_BOT + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2)]
    n = len(widths)
    for j, w in enumerate(widths):
        if w > 0:
            xj = -0.5 * period + (j + 0.5) * period / n
            g.append(mp.Block(center=mp.Vector3(xj, Y_DEV + 0.5 * H), size=mp.Vector3(w, H), material=Si))
    return g


# ---------------------------------------------------------------- (3) source: plane wave in the substrate, travelling +y
def plane_wave(period, fw=fwidth, integrated=False):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=integrated), component=mp.Ez,
                      center=mp.Vector3(0, SRC_Y), size=mp.Vector3(period, 0))]


# ---------------------------------------------------------------- (4) periodic cell: PML in y only, Bloch-periodic in x (k = 0)
def periodic_sim(widths, period, resolution=RES):
    return mp.Simulation(resolution=resolution, cell_size=mp.Vector3(period, SY), geometry=geometry_bars(widths, period),
                         boundary_layers=[mp.PML(thickness=DPML, direction=mp.Y)], k_point=mp.Vector3(),
                         sources=plane_wave(period))


# ================================================================ A. phase library
def t_atom(w, resolution=RES):
    """Zeroth-order complex transmission of one unit cell: the DFT of Ez on the monitor line averaged
    over one period (the average over a period IS the zeroth Fourier coefficient). w = 0 -> reference."""
    sim = periodic_sim([w], LA, resolution)
    dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(0, MON_Y), size=mp.Vector3(LA, 0))   # (5)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(10, mp.Ez, mp.Vector3(0, MON_Y), 1e-7))      # (6)
    t = complex(np.mean(sim.get_dft_array(dft, mp.Ez, 0)))                                                 # (7)
    sim.reset_meep()
    return t


def build_library(widths, resolution=RES):
    t_ref = t_atom(0.0, resolution)
    t = np.array([t_atom(w, resolution) / t_ref for w in widths])
    phase = np.unwrap(np.angle(t))
    return np.abs(t), phase - phase[0]


source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")
widths = np.linspace(0.04, 0.42, 17)
amp40, ph40 = build_library(widths, RES)
amp60, ph60 = build_library(widths, 60)
span40 = float(ph40.max() - ph40.min())
dphi = ph60 - ph40
print(f"A. library H={H}: phase span = {span40:.3f} rad = {span40 / (2*np.pi):.3f} x 2pi; |t| in [{amp40.min():.3f}, {amp40.max():.3f}]; "
      f"monotonic: {bool(np.all(np.diff(ph40) > 0))}; res 60 vs 40: max|dphi| = {np.max(np.abs(dphi)):.3f} rad, max d|t| = {np.max(np.abs(amp60 - amp40)):.3f}")

fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
ax[0].plot(widths, amp40, "o-", label="resolution 40"); ax[0].plot(widths, amp60, "s--", label="resolution 60")
ax[0].set_ylim(0, 1.15); ax[0].set_xlabel("bar width w [um]"); ax[0].set_ylabel("|t|"); ax[0].set_title("transmission amplitude", fontsize=9); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
ax[1].plot(widths, ph40 / (2 * np.pi), "o-", label="resolution 40"); ax[1].plot(widths, ph60 / (2 * np.pi), "s--", label="resolution 60")
ax[1].axhline(1.0, ls="--", color="crimson", lw=1); ax[1].text(0.05, 1.02, "2 pi", color="crimson", fontsize=8)
ax[1].set_xlabel("bar width w [um]"); ax[1].set_ylabel("phase / 2 pi  (relative to w = 0.04)"); ax[1].set_title(f"transmission phase: span {span40/(2*np.pi):.2f} x 2pi", fontsize=9); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
ax[2].plot(widths, dphi, "o-", color="tab:red"); ax[2].axhline(0, color="k", lw=0.8)
ax[2].axhspan(-0.1 * 2 * np.pi / N_SEC, 0.1 * 2 * np.pi / N_SEC, color="tab:green", alpha=0.15)
ax[2].set_xlabel("bar width w [um]"); ax[2].set_ylabel("phase(60) - phase(40) [rad]"); ax[2].set_title("resolution error; green = 10 % of the pi/2 design step", fontsize=9); ax[2].grid(alpha=0.3)
fig.suptitle(f"meta-atom phase library: Si bar, H = {H} um, period {LA} um, lambda = 1550 nm", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_library.png"), dpi=150); plt.close(fig)

# ================================================================ B. 4-level design from the library
w_dense = np.linspace(widths[0], widths[-1], 2001)
ph_dense = np.interp(w_dense, widths, ph40)
amp_dense = np.interp(w_dense, widths, amp40)
best = None
for phi0 in np.linspace(0.0, span40 - 1.5 * np.pi, 400):
    targets = phi0 + np.arange(N_SEC) * (2 * np.pi / N_SEC)
    if targets.max() > span40:
        continue
    ws = np.interp(targets, ph_dense, w_dense)           # phase -> width (library is monotonic)
    amps = np.interp(ws, w_dense, amp_dense)
    if best is None or amps.min() > best[0]:
        best = (float(amps.min()), float(phi0), ws, amps, targets)
min_amp, phi0, w_sel, a_sel, targets = best
w_lib = np.round(w_sel * RES) / RES                       # snap to the pixel grid
print(f"B. design: phi0 = {phi0:.3f} rad, widths = {np.round(w_lib, 3).tolist()} um, |t| = {np.round(a_sel, 3).tolist()}, min |t| = {min_amp:.3f}")

fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
ax[0].plot(w_dense, ph_dense, color="tab:blue")
for j in range(N_SEC):
    ax[0].axhline(targets[j], color="gray", ls=":", lw=0.8); ax[0].plot([w_sel[j]], [targets[j]], "o", color="crimson")
    ax[0].annotate(f"section {j}: {np.degrees(targets[j] - targets[0]):.0f} deg", (w_sel[j], targets[j]), textcoords="offset points", xytext=(6, -11), fontsize=8)
ax[0].set_xlabel("bar width w [um]"); ax[0].set_ylabel("phase [rad]"); ax[0].set_title("solve phase -> width for 4 targets", fontsize=9); ax[0].grid(alpha=0.3)
ax[1].plot(w_dense, amp_dense, color="tab:blue"); ax[1].plot(w_sel, a_sel, "o", color="crimson")
ax[1].axhline(min_amp, ls="--", color="crimson", lw=1, label=f"min |t| = {min_amp:.3f}"); ax[1].set_ylim(0, 1.15)
ax[1].set_xlabel("bar width w [um]"); ax[1].set_ylabel("|t|"); ax[1].set_title("the price: |t| is not uniform", fontsize=9); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
for j in range(N_SEC):
    xj = -0.5 * LAMBDA + (j + 0.5) * LA
    ax[2].add_patch(plt.Rectangle((xj - 0.5 * LA, 0), LA, H, facecolor="none", edgecolor="gray", ls=":"))
    ax[2].add_patch(plt.Rectangle((xj - 0.5 * w_lib[j], 0), w_lib[j], H, facecolor="tab:blue", alpha=0.75))
    ax[2].text(xj, H * 1.08, f"{np.degrees(targets[j] - targets[0]):.0f} deg\nw = {w_lib[j]:.3f}", ha="center", fontsize=7.5)
ax[2].axhline(0, color="k", lw=1.2); ax[2].set_xlim(-0.55 * LAMBDA, 0.55 * LAMBDA); ax[2].set_ylim(-0.1 * H, 1.5 * H); ax[2].set_aspect("equal")
ax[2].set_xlabel("x [um]"); ax[2].set_ylabel("y [um]"); ax[2].set_title("one supercell period (1.8 um)", fontsize=9)
fig.suptitle("4-level phase design: four widths that step the phase by 90 deg", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_design.png"), dpi=150); plt.close(fig)

# ================================================================ C. supercell: where does the light go?
stop_sc = mp.stop_when_fields_decayed(10, mp.Ez, mp.Vector3(0, MON_Y), 1e-7)
mon_region = mp.ModeRegion(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0))
sim = mp.Simulation(resolution=RES, cell_size=mp.Vector3(LAMBDA, SY), default_material=SiO2,     # reference: all substrate
                    boundary_layers=[mp.PML(thickness=DPML, direction=mp.Y)], k_point=mp.Vector3(), sources=plane_wave(LAMBDA))
fl = sim.add_mode_monitor(fcen, 0, 1, mon_region)
sim.run(until_after_sources=stop_sc)
P_in = float(mp.get_fluxes(fl)[0])
sim.reset_meep()

sim = periodic_sim(w_lib, LAMBDA)
mon = sim.add_mode_monitor(fcen, 0, 1, mon_region)
annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(5.2, 7.0), axis_step=0.5,
    title=f"supercell: 4 Si bars on SiO2, period {LAMBDA} um, periodic in x, PML in y",
    params_text=f"wl={wl} res={RES}\nLa={LA} H={H}\nw={np.round(w_lib,3).tolist()}",
    params_xy=(-0.85, 2.35), pml_xy=(-0.5, Y_BOT + 0.5 * DPML), decay_point=(0, MON_Y), decay_text_xy=(-0.1, 1.75),
    labels=[Label("4 Si bars (geometry)", (-0.5 * LAMBDA + 0.5 * LA, Y_DEV + 0.5 * H), (-0.85, 1.25), step=2, color="black"),
            Label("plane wave in SiO2", (0.3, SRC_Y), (-0.85, SRC_Y - 0.35), step=3, color="red"),
            Label("mode monitor: orders", (0.5, MON_Y), (-0.85, MON_Y + 0.35), step=5, color="blue")])
dft_sc = sim.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(LAMBDA, SY))
sim.run(until_after_sources=stop_sc)
T_total = float(mp.get_fluxes(mon)[0] / P_in)
field_sc = sim.get_dft_array(dft_sc, mp.Ez, 0)
eps_sc = sim.get_epsilon()
orders = {}
for m in range(-3, 4):
    kx = m / LAMBDA
    if abs(kx) >= fcen:
        continue                                                                    # evanescent
    a = sim.get_eigenmode_coefficients(mon, mp.DiffractedPlanewave((m, 0, 0), mp.Vector3(1, 0, 0), 1, 0)).alpha[0, 0, 0]
    orders[m] = {"angle_deg": float(np.degrees(np.arcsin(kx / fcen))), "eff": float(abs(a) ** 2 / P_in)}
sim.reset_meep()
sum_orders = sum(v["eff"] for v in orders.values())
print("C. supercell orders: " + ", ".join(f"m={m}: {v['eff']:.4f} ({v['angle_deg']:+.1f} deg)" for m, v in sorted(orders.items())) +
      f"; sum = {sum_orders:.4f}, T_total = {T_total:.4f}; +1 efficiency {orders[1]['eff']:.4f} = {orders[1]['eff'] / BLAZED_BOUND * 100:.1f} % of the 4-level bound {BLAZED_BOUND:.4f}")

ext_sc = [-0.5 * LAMBDA, 0.5 * LAMBDA, Y_BOT, -Y_BOT]
fig, ax = plt.subplots(1, 3, figsize=(13, 4.6), gridspec_kw={"width_ratios": [1.4, 1, 1]})
ms = sorted(orders)
bars = ax[0].bar([f"m = {m}\n{orders[m]['angle_deg']:+.0f} deg" for m in ms], [orders[m]["eff"] for m in ms], color=["tab:blue" if m == 1 else "tab:gray" for m in ms])
ax[0].axhline(BLAZED_BOUND, ls="--", color="crimson", lw=1.2, label=f"4-level blazed bound {BLAZED_BOUND:.3f}")
for b, m in zip(bars, ms):
    ax[0].text(b.get_x() + b.get_width() / 2, orders[m]["eff"] + 0.01, f"{orders[m]['eff']:.3f}", ha="center", fontsize=8)
ax[0].set_ylim(0, 1.0); ax[0].set_ylabel("efficiency (fraction of incident power)"); ax[0].set_title(f"orders: sum {sum_orders:.3f} = total flux {T_total:.3f}", fontsize=9); ax[0].grid(axis="y", alpha=0.3); ax[0].legend(fontsize=8)
xs = np.linspace(ext_sc[0], ext_sc[1], eps_sc.shape[0]); ys = np.linspace(ext_sc[2], ext_sc[3], eps_sc.shape[1])
lim = float(np.max(np.abs(np.real(field_sc))))
ax[1].imshow(np.real(field_sc).T, extent=ext_sc, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal"); ax[1].set_title("Re(Ez): the wavefront tilts", fontsize=9)
ax[2].imshow(np.abs(field_sc).T, extent=ext_sc, origin="lower", cmap="inferno", aspect="equal"); ax[2].set_title("|Ez|", fontsize=9)
for a in ax[1:]:
    a.contour(xs, ys, eps_sc.T, levels=[1.5, 6.0], colors="w", linewidths=0.6)
    a.axhline(MON_Y, color="lime", lw=0.8, ls="--"); a.set_xlabel("x [um]")
ax[1].set_ylabel("y [um]")
fig.suptitle(f"library supercell, design angle {THETA_D:.1f} deg", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_supercell.png"), dpi=150); plt.close(fig)


# ================================================================ D. finite arrays: far field
def finite_array(n_atom, resolution=30, pad=1.0, R_ff=200.0, angles=np.linspace(-85, 85, 341)):
    aperture = n_atom * LA
    sx = aperture + 2 * pad + 2 * DPML
    n2f_y = Y_DEV + H + 0.5 * DAIR
    geom = [mp.Block(center=mp.Vector3(0, Y_BOT + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2)]
    for j in range(n_atom):
        xj = -0.5 * aperture + (j + 0.5) * LA
        geom.append(mp.Block(center=mp.Vector3(xj, Y_DEV + 0.5 * H), size=mp.Vector3(w_lib[j % N_SEC], H), material=Si))
    sim = mp.Simulation(resolution=resolution, cell_size=mp.Vector3(sx, SY), boundary_layers=[mp.PML(DPML)], geometry=geom,
                        sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fwidth, is_integrated=True), component=mp.Ez,
                                           center=mp.Vector3(0, SRC_Y), size=mp.Vector3(aperture, 0))])   # source only under the array
    n2f = sim.add_near2far(fcen, 0, 1, mp.Near2FarRegion(center=mp.Vector3(0, n2f_y), size=mp.Vector3(sx - 2 * DPML, 0)))
    sim.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(0, n2f_y), 1e-6))
    I = np.array([abs(sim.get_farfield(n2f, mp.Vector3(R_ff * np.sin(np.radians(a)), R_ff * np.cos(np.radians(a))))[2]) ** 2 for a in angles])
    sim.reset_meep()
    return aperture, angles, I / I.max()


ff = {}
fig, ax = plt.subplots(figsize=(8, 4.2))
for n_atom, color in ((10, "tab:orange"), (40, "tab:blue")):
    aperture, angles, pattern = finite_array(n_atom)
    peak = float(angles[np.argmax(pattern)])
    bw = float(np.degrees(wl / (aperture * np.cos(np.radians(THETA_D)))))
    ff[n_atom] = {"aperture_um": aperture, "peak_deg": peak, "beamwidth_est_deg": bw}
    ax.plot(angles, pattern, color=color, label=f"{n_atom} atoms (D = {aperture:.1f} um): peak {peak:+.1f} deg, est. width {bw:.1f} deg")
    print(f"D. {n_atom} atoms: aperture {aperture:.2f} um, main lobe {peak:+.1f} deg (design {THETA_D:+.2f}), est. beam width {bw:.1f} deg")
ax.axvline(THETA_D, ls="--", color="gray", lw=1); ax.text(THETA_D, 1.03, f" design {THETA_D:.1f} deg", color="gray", fontsize=8)
ax.set_xlabel("angle from the normal [deg]"); ax.set_ylabel("normalized |Ez|^2 (far field)"); ax.set_ylim(0, 1.12); ax.grid(alpha=0.3); ax.legend(fontsize=8)
ax.set_title("far field of finite arrays built from the library", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_farfield.png"), dpi=150); plt.close(fig)

# ================================================================ E. GIF: 12-atom array, short pulse
n_anim = 12
fw_anim = 0.4 * fcen
aperture = n_anim * LA
sx_a = aperture + 2 * 1.0 + 2 * DPML
sy_a = DPML + DSUB + H + 2.5 + DPML
yb = -0.5 * sy_a
ydev = yb + DPML + DSUB
geom = [mp.Block(center=mp.Vector3(0, yb + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2)]
for j in range(n_anim):
    xj = -0.5 * aperture + (j + 0.5) * LA
    geom.append(mp.Block(center=mp.Vector3(xj, ydev + 0.5 * H), size=mp.Vector3(w_lib[j % N_SEC], H), material=Si))
sim_a = mp.Simulation(resolution=RES, cell_size=mp.Vector3(sx_a, sy_a), boundary_layers=[mp.PML(DPML)], geometry=geom,
                      sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fw_anim, is_integrated=True), component=mp.Ez,
                                         center=mp.Vector3(0, yb + DPML + 0.3), size=mp.Vector3(aperture, 0))])
sim_a.init_sim()
vol_a = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx_a - 2 * DPML, sy_a - 2 * DPML))
eps_a = sim_a.get_array(vol=vol_a, component=mp.Dielectric)
ext_a = [-(sx_a / 2 - DPML), sx_a / 2 - DPML, -(sy_a / 2 - DPML), sy_a / 2 - DPML]
t_src = 5 / fw_anim
frames, times = record_frames(sim_a, vol_a, mp.Ez, t_start=t_src - 1 / fw_anim, t_end=t_src + 1.2 * sy_a * 1.45, n_frames=60)
animate_fields(frames, times, ext_a, os.path.join(OUT, "06_anim_array.gif"), eps=eps_a, figsize=(6.0, 5.2), dpi=70,
               title=f"{n_anim}-atom array: wavefront leaves tilted toward +{THETA_D:.0f} deg", legend_loc="lower right")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"params": {"wl": wl, "La": LA, "Lambda": LAMBDA, "H": H, "theta_d_deg": THETA_D, "n_si": 3.45, "n_sio2": 1.45},
                   "library": {"widths": widths.tolist(), "amp40": amp40.tolist(), "phase40": ph40.tolist(), "amp60": amp60.tolist(),
                               "phase60": ph60.tolist(), "span40_over_2pi": span40 / (2 * np.pi), "max_dphi_60_40": float(np.max(np.abs(dphi)))},
                   "design": {"phi0": phi0, "targets": targets.tolist(), "widths": w_lib.tolist(), "amps": a_sel.tolist(), "min_amp": min_amp},
                   "supercell": {"orders": orders, "sum_orders": sum_orders, "T_total": T_total, "blazed_bound": BLAZED_BOUND,
                                 "plus1_over_bound": orders[1]["eff"] / BLAZED_BOUND},
                   "farfield": ff, "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
{% endhighlight %}
</details>

<details markdown="1">
<summary>Show original logs and the reproduction environment</summary>

Unlike the excerpts in §4, the complete code includes far fields, figure saving, GIF recording, and result.json output. The shared helper `blogfig.py` is in the same `code/` folder. Full code and helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**Execution results (run on 2026-10-23)**:
```
A. library H=0.9: phase span = 6.920 rad = 1.101 x 2pi; |t| in [0.689, 1.011]; monotonic: True; res 60 vs 40: max|dphi| = 0.817 rad, max d|t| = 0.071
B. design: phi0 = 0.797 rad, widths = [0.075, 0.1, 0.175, 0.225] um, |t| = [1.001, 0.959, 0.885, 0.885], min |t| = 0.885
C. supercell orders: m=-1: 0.1576 (-59.4 deg), m=0: 0.0325 (+0.0 deg), m=1: 0.5144 (+59.4 deg); sum = 0.7045, T_total = 0.7045; +1 efficiency 0.5144 = 63.5 % of the 4-level bound 0.8106
D. 10 atoms: aperture 4.50 um, main lobe +49.5 deg (design +59.44), est. beam width 38.8 deg
D. 40 atoms: aperture 18.00 um, main lobe +58.5 deg (design +59.44), est. beam width 9.7 deg
```

**Reproduction environment**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · run `python meta_atom.py` (about 35 s, single core)

</details>

<details markdown="1">
<summary>Explore applications and next topics</summary>

### Applications

Meta-atoms and phase libraries form a design workflow for metalenses, beam steerers, and polarization splitters: characterize one unit cell, then arrange cells into a device.

| Application | What this lesson provides | Next step |
|---|---|---|
| Metalens (thin smartphone cameras, AR displays, endoscopes) | Phase library → position-dependent phase → focus | Chapter 35: near2far inverse design |
| Beam deflector (LiDAR, optical switches) | Four-step blazed design, supercell efficiency | Chapter 08: metagrating inverse design |
| Polarization- and color-splitting metasurfaces | Add polarization axes and wavelengths to the library method | Chapter 21: anisotropic materials |
| Unit cell → arrangement → validation workflow | This entire lesson | — |

</details>

- [Official metasurface_lens.py example](https://github.com/NanoComp/meep/blob/master/python/examples/metasurface_lens.py) (lens design through duty-cycle → phase lookup) · [Official binary_grating_phasemap.py](https://github.com/NanoComp/meep/blob/master/python/examples/binary_grating_phasemap.py)
- [Near-to-Far Field tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/) · [`add_near2far` / `get_farfield` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#near-to-far-field-spectra)
- Previous: [06 · Binary grating and diffraction orders]({{ '/en/binary-grating/' | relative_url }}) · Next: [08 · Metagrating inverse design]({{ '/en/metagrating-inverse/' | relative_url }})
