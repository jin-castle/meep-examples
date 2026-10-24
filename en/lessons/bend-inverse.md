---
layout: lesson
permalink: /en/bend-inverse/
lesson_title: "How can light find its own path around a bend?"
lesson_summary: "Change 121 densities to guide light into the output waveguide. Verify the computed gradient and distinguish optimization scores from measured transmission."
lesson_goals:
  - "Explain the path from forward and adjoint calculations to density gradients."
  - "Check gradients with finite differences and interpret one design update."
  - "Assess design limitations with independent verification and a resolution check."
lesson_prerequisites: "Chapter 04: EigenModeSource · Chapter 05: bends and normalization · Chapter 08: adjoint and gradient gates"
date: 2026-10-23
title: "Meep Example 09 · Waveguide bend inverse design — a free design region and output-port mode power"
title_en: "Meep Example 09 · Waveguide bend inverse design — a free design region and the output-port mode power"
lang: en
translation_key: bend-inverse
series: meep-examples
part: 9
level: intermediate
runtime: "29 s (single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Adjoint_Solver/"
tags: [meep, fdtd, adjoint, inverse-design, waveguide-bend, nlopt, mma]
image: /assets/meep/09/07_verify.png
excerpt: "post 05 steered a 90° bend with one number, the radius. Here the corner is a 1 × 1 µm square opened as a free design region of 11 × 11 densities (SiO2 to Si), and the adjoint gradient fills it. The contract is the one from post 08; only the objective changes, from a diffraction order to the mode-1 power at the output port."
---
<h2 id="observe">1. Observe: where does light go from a gray block?</h2>

The input is on the left; the desired output is above. If only the central 1 × 1 µm square can change material, what structure would turn light through 90°? Chapter 05 varied one radius; here we vary 11 × 11 = **121 densities**.

<div class="figure-pair">
<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/07_verify.png' | relative_url }}" data-lightbox aria-label="Enlarge the original starting-design electric field">
<svg viewBox="690 45 630 560" role="img" aria-labelledby="start-field-title"><title id="start-field-title">Actual electric field spreading right from uniform density 0.5</title><image href="{{ '/assets/meep/09/07_verify.png' | relative_url }}" width="1950" height="630" /></svg>
</a>
<figcaption>Start: all densities are 0.5. Light spreads right; mode-1 transmission into the upper waveguide is 0.0154.</figcaption>
</figure>
<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/07_verify.png' | relative_url }}" data-lightbox aria-label="Enlarge the original updated-design electric field">
<svg viewBox="1335 45 610 560" role="img" aria-labelledby="updated-field-title"><title id="updated-field-title">Actual electric field entering the upper waveguide in the design from MMA evaluation 5</title><image href="{{ '/assets/meep/09/07_verify.png' | relative_url }}" width="1950" height="630" /></svg>
</a>
<figcaption>After updating: the highest-scoring design among five MMA evaluations. Mode-1 transmission measured in a fresh simulation is 0.7801.</figcaption>
</figure>
</div>

<p class="lesson-note"><strong>Conditions for interpreting this result.</strong> Both images show actual Re(Ez) at resolution 10. Remeasuring the same design at resolution 20 gives transmission 0.6391. With 119 of 121 densities still gray and only five optimizer evaluations, this is neither a converged design nor a fabrication drawing.</p>

### Applications

The high-resolution DFT example on the homepage shows an **RdBu electric-field map**. Red is negative, white is zero and blue is positive Re(Ez), using a shared symmetric color range without transparency compositing. Black outlines identify the fixed waveguides, while continuous design densities appear separately in grayscale. The original complex fields, phases and gradient are preserved. This calculation history differs from the original low-resolution MMA example below.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/09/iterations/005/updated-forward-scene.png?v=rdbu-20261024" data-lightbox><img src="{{ site.baseurl }}/assets/meep/09/iterations/005/updated-forward-scene.png?v=rdbu-20261024" alt="Actual DFT electric field in RdBu after six high-resolution density updates" loading="lazy"></a>
<figcaption>Saved steady-state DFT at resolution 60 with 61×61 continuous densities after six updates. Phase playback does not represent the source switching on or the arrival of a wavefront.</figcaption>
</figure>

An inverse-designed bend introduces a method that can shrink the footprint of PIC components by large factors. The same framework applies to splitters, crossings, and mode converters.

| Application | What this lesson provides | Next step |
|---|---|---|
| Compact PIC components (bend, splitter, crossing, mode converter) | Free design region + output-mode objective | Chapters 31, 33, 34 |
| Foundry constraints (minimum feature size, binarization) | Identify grayscale and feature-size limitations | Chapter 32: filters and projection |
| Comparing 1 and 121 design variables | Chapter 05’s radius sweep versus this lesson | — |



<h2 id="predict">2. Predict: does the gradient draw a finished path?</h2>

All we know is that light entering from the left should exit upward. Predict the pattern of the first gradient at a uniform starting design.

<fieldset class="prediction">
<legend>Which pattern is most prominent in the first gradient?</legend>
<label><input type="radio" name="gradient-prediction" value="diagonal"> An entirely positive diagonal band connecting input and output.</label>
<label><input type="radio" name="gradient-prediction" value="local"> Local changes: reduce the center and increase some waveguide connections.</label>
</fieldset>

<details markdown="1">
<summary>Compare your prediction with the actual result</summary>

This starting design is closer to the second answer. The largest magnitude is **negative, −13.4, at the center**; positive values occur near extensions of the two waveguides into the design region. A diagonal structure appears only after a large step drives some densities to 0 or 1. The first derivative gives a local direction for changing the current design, not a finished geometry.

</details>

<h2 id="understand">3. Understand: from two calculations to one update</h2>

{% include chapter-illustration.html %}

Density ρ determines material inside the design region: **0 is SiO₂ and 1 is Si**, with interpolated values in between. Keep the 0.5 µm-wide Si waveguides to the left and above fixed, and change only the 121 values inside the square. Initially all are 0.5; the exterior background is air.

<!-- concept-illustration:part-09:start -->

<p class="lesson-note">The left (+x) input and upper (+y) output waveguides remain fixed. Only the 11 × 11 densities in the central 1 × 1 µm square change. The grid and gray shades explain the variables; they are not an actual optimized result.</p>

<!-- concept-illustration:part-09:end -->

A forward calculation launches light from the input. A separate adjoint calculation uses an objective-derived source at the output to probe the response toward the design region. The two stored fields produce the gradient, which the optimizer uses to update densities.

1. **Forward field:** excite the left input mode and obtain mode-1 amplitude at the upper output port.
2. **Adjoint field:** run separately with a source derived from the objective; here it points from the output port toward the design region.
3. **Gradient:** combine the overlap of the two stored fields with the material’s density dependence to calculate ∂J/∂ρ for each pixel.
4. **Geometry update:** after verifying the gradient, update densities within 0 ≤ ρ ≤ 1 using the optimizer.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/04_gradient.png' | relative_url }}" data-lightbox aria-label="Enlarge the actual 11 by 11 gradient and color bar">
<svg viewBox="625 0 585 555" role="img" aria-labelledby="gradient-map-title"><title id="gradient-map-title">Actual initial signed gradient: strongly negative center and positive regions near some waveguide connections</title><image href="{{ '/assets/meep/09/04_gradient.png' | relative_url }}" width="1800" height="570" /></svg>
</a>
<figcaption>Actual initial 11 × 11 gradient. Red (positive) favors increasing density; blue (negative) favors decreasing it to increase J locally. There are 49 positive and 72 negative entries.</figcaption>
</figure>

<p class="lesson-note"><strong>Reading the colors.</strong> Color represents sensitivity of J, not material density. Decreasing density means moving toward SiO₂ inside the design region. Distinguish this from black/gray/white density maps.</p>

The objective is squared output mode-1 amplitude, **J = |a_out|²**. During optimization, J follows the optimizer’s normalization convention. Report transmission measured from the selected design in a **fresh simulation**, divided by input mode-1 power from a straight-waveguide reference run.

$$
T_{\mathrm{mode1}}=
\frac{P_{\mathrm{out,mode1}}\;\text{(fresh run)}}{P_{\mathrm{in,mode1}}\;\text{(reference run)}}
$$

**Model scope:** 2D Ez (TE), wavelength 1.55 µm, Si index 3.4, SiO₂ index 1.44, and one frequency. The 11 × 11 design grid differs from the electromagnetic Yee grid. There are no minimum-feature or binarization constraints.

<details markdown="1">
<summary>Equations and notation in detail</summary>

The objective is J = |a_out|², the squared mode-1 amplitude at the output-port monitor. The mathematics is the same as in chapter 08. The input waveguide’s `EigenModeSource` generates E_f; an objective-derived mode source at the output monitor generates E_a toward the design region. The gradient combines field overlap, material-density dependence, and normalization factors. The proportional relation below is conceptual. In chapter 08 the adjoint descended from a plane-wave monitor; here it returns along the output waveguide. Changing the objective changes the adjoint source’s position and shape.

$$
J=\lvert a_{\mathrm{out}}\rvert^{2},\qquad
\frac{\partial J}{\partial \rho_i}\;\propto\;\mathrm{Re}\big(E_f\cdot E_a\big)\Big|_{\text{pixel } i},\qquad
T_{\mathrm{mode1}}=\frac{\lvert a_{\mathrm{out}}\rvert^{2}_{\text{fresh run}}}{P_{\mathrm{in}}}
$$

The denominator P_in of reported T_mode1 is mode-1 power at the input plane (x = −1 µm) in a reference run containing only a straight waveguide. The numerator is remeasured using `get_eigenmode_coefficients` after inserting the selected design into a fresh `Simulation`. Optimizer J does not share this normalization; indeed J/P_in gives 1.056.

| Symbol | Meaning | Code variable |
|------|----|-----------|
| ρ (121 values) | Design density: 0 SiO2, 1 Si, intermediate grayscale | `x_start`, `x_optimized` |
| J | Output-port mode-1 power \|a_out\|² in optimizer units | `fom(x)` |
| g | adjoint gradient ∂J/∂ρ | `g_start` |
| v, s | Gate direction (g/\|g\|), finite-difference step | `v`, `steps` |
| α | Manual step size | `one_step` |
| P_in | Input-plane mode-1 power in the reference run | `input_power` |
| T_mode1, T_total | Fresh-run mode-1 power / P_in, total flux / P_in | `report` |

**Assumptions and validity**: 2D Ez (TE), indices Si 3.4 / SiO2 1.44, width 0.5 µm, resolution 10 (100 nm spacing), and one frequency. The 11 × 11 design grid is separate from the Yee grid. No minimum-feature or binarization constraints are imposed.


</details>

<h2 id="run">4. Run: compare one step size</h2>

Place the [complete script and shared helper](https://github.com/jin-castle/meep-examples/blob/main/code) in the same folder: `bend_inverse.py` and `blogfig.py`. Run the original once in an environment with Meep 1.33.0, NLopt, and autograd. The recorded runtime is about 29 seconds on one core.

```bash
python bend_inverse.py
```

Inspect the **`one manual step:` log line**. The original compares α = 0.2, 1, 3, 8 using the same starting design and normalized gradient direction. Each is one independent step from uniform 0.5, not a continuation of the previous result.

```python
# Excerpt from the complete original code: do not run this fragment alone.
x_try = np.clip(x_start + alpha * v, 0, 1)
```

**One experiment:** replace only the final value in `for alpha in (0.2, 1.0, 3.0, 8.0):` with `4.0` and rerun. First predict how J and density saturation differ between α = 4 and 8, then check the log and `06_step_mma.png`. Keep all other parameters and the MMA evaluation count fixed.

**Before interpreting:** check that the gradient gate passes. All three finite-difference steps in this example have relative errors within 0.01%. If the gate reports HOLD, stop interpreting optimizer results and diagnose it. If the input mode-1 fraction is below 0.95, check the source first.

<details markdown="1">
<summary>Simulation setup, parameters, and source verification</summary>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/01_layout.png' | relative_url }}" data-lightbox aria-label="Enlarge: Source and input/output monitor positions in the 6 by 5 micrometer simulation cell"><img src="{{ '/assets/meep/09/01_layout.png' | relative_url }}" alt="Source and input/output monitor positions in the 6 by 5 micrometer simulation cell" loading="lazy"></a>
<figcaption>A 6 × 5 µm cell with 1 µm PML. The source is at x = −1.5 µm, input monitor at x = −1 µm, and output monitor at y = 1 µm.</figcaption>
</figure>

| Parameter | Value | Why this value | Effect of a change |
|----------|-----|-------------|--------|
| Cell, resolution | 6 × 5 µm, res 10 | Same as lecture week 10; one run takes 2–3 s | Res 20 changes results as shown in the convergence table |
| Design region | 1 × 1 µm, 11 × 11 | Twice the waveguide width; 121 variables | 1.5 × 1.5 gives 256 variables, with runtime growing accordingly |
| Initial design | Uniform 0.5 | An interior point supports immediate gating without directional bias | Binary starts need clipping precautions as in chapter 08 |
| Source | Mode 1, fwidth 0.12 fcen | Narrowband for the single-frequency objective | A wider pulse bandwidth suits GIFs; the forward objective run stays unchanged |
| Monitor | Output y = 1, width 2 µm | 0.5 µm from the design region | Moving it against the region mixes near fields into mode decomposition |
| Gate steps | 2e-3, 5e-3, 1e-2 | Same as chapter 08 | — |
| Manual step α | 0.2, 1, 3, 8 | Wider than chapter 08 (0.05–2), to see saturation | — |
| `maxeval` | 5 | Teaching smoke test | Convergence requires tens of evaluations plus binarization |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/00_source.png' | relative_url }}" data-lightbox aria-label="Enlarge: Gaussian source time waveform and frequency spectrum"><img src="{{ '/assets/meep/09/00_source.png' | relative_url }}" alt="Gaussian source time waveform and frequency spectrum" loading="lazy"></a>
<figcaption>The source has fwidth = 0.12 fcen. Pulse width is 12.9, with peak t0 = 64.6 µm/c; power outside ±50 nm of 1550 nm is below 1%.</figcaption>
</figure>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/02_source_check.png' | relative_url }}" data-lightbox aria-label="Enlarge: Input mode measured in a straight-waveguide reference run"><img src="{{ '/assets/meep/09/02_source_check.png' | relative_url }}" alt="Input mode measured in a straight-waveguide reference run" loading="lazy"></a>
<figcaption>Input mode-1 power / total flux = 1.0043. The numerator is forward mode 1; the denominator is net forward-minus-backward flux, so the ratio can slightly exceed 1.</figcaption>
</figure>

**Difference from the lecture notebook**: parameters and numbers match week 10 (mode-1 fraction 1.0043, gate 0.0000/0.0000/0.0001, manual steps 16.7/118.9/176.2/235.5, MMA 4.31 → 222.4, verification 0.0154 → 0.7801). The lecture uses Meep 1.34 and this run 1.33, yet results agree to four decimal places. This lesson adds a resolution-20 remeasurement, two GIFs, and a numbered setup diagram.


</details>

<details markdown="1">
<summary>Seven code steps: roles and common pitfalls</summary>

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → run and stop → postprocessing.
> The structure follows chapter 08; the main changes are the objective in ⑤ and normalization in ⑦.

### ① Units and parameters — which numbers stay fixed

```python
wl, fcen, fwidth = 1.55, 1 / 1.55, 0.12 / 1.55
Si, SiO2 = mp.Medium(index=3.4), mp.Medium(index=1.44)
RES, SX, SY, DPML, W = 10, 6.0, 5.0, 1.0, 0.5
SRC_X, MON_IN_X, MON_OUT_Y = -1.5, -1.0, 1.0        # source, input monitor, objective monitor
D, NX, NY = 1.0, 11, 11                                # design square and its grid (121 densities)
x_start = 0.5 * np.ones(NX * NY)                        # uniform grey: interior point, no bias
```

- **What**: define the cell, waveguides, design grid, and source/input/output monitor planes.
- **Why**: the input monitor lies between source and design region. Its reference-run mode-1 power normalizes all transmissions. Place the output monitor 0.5 µm from the design region.
- **If wrong**: confusing the 11 × 11 design grid with the Yee grid (10 intervals per µm at res 10) suggests a false one-to-one pixel mapping. `MaterialGrid` interpolates the design grid onto the Yee grid.

### ② Materials and geometry — what goes where

```python
def waveguide_blocks():
    return [mp.Block(center=mp.Vector3(-SX / 4, 0), size=mp.Vector3(SX / 2, W), material=Si),    # input, from -x
            mp.Block(center=mp.Vector3(0, SY / 4), size=mp.Vector3(W, SY / 2), material=Si)]     # output, to +y

design_variables = mp.MaterialGrid(mp.Vector3(NX, NY), SiO2, Si, grid_type="U_MEAN", do_averaging=False)   # contract 1
design_region = mpa.DesignRegion(design_variables, volume=mp.Volume(center=mp.Vector3(), size=mp.Vector3(D, D)))
geometry = waveguide_blocks() + [mp.Block(center=design_region.center, size=design_region.size, material=design_variables)]
```

- **What**: two fixed Si waveguides and a square `MaterialGrid` at the origin. Optimization changes only the square.
- **Why**: the waveguides touch the left and upper square edges. Gradients guide how the design region connects them.
- **If wrong**: where geometry objects overlap, the later object determines permittivity. Put the design region last so its density takes effect.

### ③ Source — how light enters

```python
sources = [mp.EigenModeSource(mp.GaussianSource(fcen, fwidth=fwidth), eig_band=1, direction=mp.NO_DIRECTION,
                              eig_kpoint=mp.Vector3(1, 0, 0), size=mp.Vector3(0, 2), center=mp.Vector3(SRC_X, 0))]
adjoint_sources = opt.adjoint_sources[0]      # one EigenModeSource at the OUTPUT monitor, made by opt
```

- **What**: the same `EigenModeSource` as chapter 04. `OptimizationProblem` creates an adjoint source at the output monitor.
- **Why**: because the objective measures mode-1 amplitude, the adjoint source has a mode-1 profile. In chapter 08 it was a plane wave.
- **If wrong**: `direction=mp.NO_DIRECTION` without `eig_kpoint` leaves the mode direction unspecified. Check this first if the reference mode-1 fraction is far from 1.

### ④ Simulation and boundaries — the cell and PML

```python
common = dict(resolution=RES, cell_size=mp.Vector3(SX, SY), boundary_layers=[mp.PML(DPML)], sources=sources, eps_averaging=False)
sim = mp.Simulation(geometry=geometry, **common)
stop_cond = mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(0, MON_OUT_Y), 1e-5)
```

- **What**: 1 µm PML on all four sides, with the decay-monitoring point at the output monitor center.
- **Why**: forward, adjoint, finite-difference, verification, and resolution-check runs all share `common`; only resolution is replaced for the last check.
- **If wrong**: default permittivity averaging violates contract 1 in this setup. `do_averaging=False` handles the design material and `eps_averaging=False` the simulation-level averaging.

### ⑤ Monitor — the objective

```python
out_mode = mpa.EigenmodeCoefficient(sim, mp.Volume(center=mp.Vector3(0, MON_OUT_Y), size=mp.Vector3(2, 0)), mode=1)
opt = mpa.OptimizationProblem(simulation=sim, objective_functions=lambda a: npa.abs(a) ** 2,
                              objective_arguments=[out_mode], design_regions=[design_region], fcen=fcen, df=0, nf=1)
```

- **What**: use output-monitor mode-1 amplitude a_out as the argument and |a_out|² as the objective.
- **Why**: chapter 08’s `kpoint_func` and `eig_vol` are unnecessary. Solve the waveguide mode over the full monitor width; its propagation direction is the monitor normal. These are the two changed lines.
- **If wrong**: the 2 µm monitor must be wider than the 0.5 µm waveguide to include modal tails. Narrowing it to 0.5 reduces a_out and distorts the gradient.

### ⑥ Run — forward, adjoint, gate, one step, and MMA

```python
f, dJ = opt([x], need_gradient=True)                   # forward + adjoint: J and dJ/drho for all 121 pixels

v = g_start / np.linalg.norm(g_start)                   # gate: gradient direction, x_start is already interior
fd = (fom(x_start + s * v) - fom(x_start - s * v)) / (2 * s)
ok = abs(g_start @ v - fd) / abs(fd) <= 0.20

x_try = np.clip(x_start + alpha * v, 0, 1)              # one step by hand, alpha in (0.2, 1, 3, 8)

solver = nlopt.opt(nlopt.LD_MMA, NX * NY); solver.set_lower_bounds(0); solver.set_upper_bounds(1)
solver.set_max_objective(nlopt_objective); solver.set_maxeval(5)
x_optimized = design_history[int(np.argmax(history))]  # keep the best evaluated design
```

- **What**: follow chapter 08’s sequence: gate, manual step, five MMA evaluations, and saving the best evaluation.
- **Why**: uniform 0.5 is an interior start, so gating needs no clipping adjustment. Unlike chapter 08, no binary baseline must first be moved into 0.02–0.98.
- **If wrong**: the x returned by `solver.optimize` reflects MMA’s internal state, not necessarily the evaluation you intend to report. Select the reported design from history.

### ⑦ Postprocessing — contract 4, independent verification and normalization

```python
def modal_power(weights, res=RES):
    s = mp.Simulation(geometry=geometry_with(weights), **dict(common, resolution=res))      # a NEW simulation
    mon = s.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(0, MON_OUT_Y), size=mp.Vector3(2, 0)))
    s.run(until_after_sources=stop_cond)
    mode1 = abs(s.get_eigenmode_coefficients(mon, [1], direction=mp.Y).alpha[0, 0, 0]) ** 2
    return mode1, mp.get_fluxes(mon)[0]

T_mode1 = mode1 / input_power          # input_power: mode-1 power at x = -1 um in the straight-waveguide run
```

- **What**: insert the selected design into a fresh `Simulation`, remeasure output mode-1 power and total flux, and divide by P_in. Repeat the same function at res = 20.
- **Why**: dividing internal optimizer J by P_in gives 1.056 because the normalization conventions differ. Report transmission from the consistently normalized fresh-run function.
- **If wrong**: the res-20 check also needs a res-20 reference denominator. Changing only the numerator mixes normalization changes into the resolution comparison.

> **Pitfall**: `mpa.EigenmodeCoefficient` |a|² and `get_eigenmode_coefficients` |α|² describe the same physical quantity with different normalization conventions in this workflow. Mixing them can produce transmission above 1. Measure numerator and denominator with the same function: that is the practical content of contract 4.


</details>

<h2 id="interpret">5. Interpret: what does an improved number mean?</h2>

Here J increased even up to α = 8, but large steps are not always beneficial. Chapter 08 fell at a large step, and MMA here fluctuated **4.31 → 180.7 → 4.5 → 106.2 → 222.4**. Keep evaluation 5, which has the highest J among the evaluated designs.

| Quantity | Starting design | Retained design |
|---|---|---|
| Fresh-run mode-1 transmission | 0.0154 | 0.7801 |
| Fresh-run total flux / input mode-1 power | 0.1165 | 0.8040 |

Both columns use the same reference input power. The final difference between T_total and T_mode1, about 0.024, is power crossing the output plane not captured as mode 1.

<p class="lesson-note"><strong>Do not read J = 222.4 as transmission.</strong> Dividing it by input power 210.6 gives 1.056 because the normalization conventions differ. Remeasuring numerator and denominator with the same function gives transmission 0.7801.</p>

### How much confidence does this design deserve?

Passing the gradient gate checks **the derivative under the current numerical settings**. It does not guarantee optimization convergence, resolution convergence, or manufacturability.

| Check | Result | Meaning |
|---|---|---|
| Gradient gate | PASS at all three steps, within 0.01% | Finite differences and adjoint agree |
| Same 121 densities, resolution 10 → 20 | T_mode1 0.7801 → 0.6391 | Resolution convergence is not established |
| Densities and evaluation count | 119/121 gray, five MMA evaluations | Neither a binary material design nor a converged optimum |

For the resolution check, **keep design densities fixed and refine the Yee grid**, then remeasure reference input power at the new resolution too. This is a short demonstration of the adjoint procedure. It does not establish performance at other wavelengths, polarizations, in 3D, or after fabrication.

### Light propagation and design evolution

<figure class="lesson-figure lesson-animation">
<a href="{{ '/assets/meep/09/08_anim_optimized.gif' | relative_url }}" data-lightbox aria-label="Enlarge: A short pulse travels through the updated design into the output waveguide"><img src="{{ '/assets/meep/09/08_anim_optimized.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/09/08_anim_optimized.gif' | relative_url }}" data-static-src="{{ '/assets/meep/09/07_verify.png' | relative_url }}" alt="A short pulse travels through the updated design into the output waveguide" loading="lazy"></a>
<button class="animation-toggle" type="button" hidden>Pause animation</button>
<figcaption>A short pulse with fwidth = 0.3 fcen travels from source to output monitor. Pausing displays the actual field image from independent verification.</figcaption>
</figure>

<figure class="lesson-figure lesson-animation">
<a href="{{ '/assets/meep/09/09_anim_design.gif' | relative_url }}" data-lightbox aria-label="Enlarge: Design evolution from the uniform start through MMA evaluations 1–5 to the retained design"><img src="{{ '/assets/meep/09/09_anim_design.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/09/09_anim_design.gif' | relative_url }}" data-static-src="{{ '/assets/meep/09/06_step_mma.png' | relative_url }}" alt="Design evolution from the uniform start through MMA evaluations 1–5 to the retained design" loading="lazy"></a>
<button class="animation-toggle" type="button" hidden>Pause animation</button>
<figcaption>Uniform start → MMA evaluations 1–5 → retained evaluation 5. Pausing displays the complete figure of the same actual evaluation history.</figcaption>
</figure>

<details markdown="1">
<summary>Original result figures and numerical tables</summary>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/03_fields.png' | relative_url }}" data-lightbox aria-label="Enlarge: Forward fields for uniform and random starts, and the adjoint field for the uniform start"><img src="{{ '/assets/meep/09/03_fields.png' | relative_url }}" alt="Forward fields for uniform and random starts, and the adjoint field for the uniform start" loading="lazy"></a>
<figcaption>Forward fields: uniform start above (J = 4.31), random start below (J = 12.23). The right column shows the uniform-start adjoint field launched from the output.</figcaption>
</figure>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/04_gradient.png' | relative_url }}" data-lightbox aria-label="Enlarge: Signed gradient and gradient magnitude calculated at uniform density 0.5"><img src="{{ '/assets/meep/09/04_gradient.png' | relative_url }}" alt="Signed gradient and gradient magnitude calculated at uniform density 0.5" loading="lazy"></a>
<figcaption>The largest initial gradient magnitude is negative, −13.4, at the center. There are 49 positive and 72 negative entries; positive regions mainly extend the two waveguides into the square.</figcaption>
</figure>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/05_gate.png' | relative_url }}" data-lightbox aria-label="Enlarge: Gradient gate comparing finite-difference and adjoint directional derivatives at three steps"><img src="{{ '/assets/meep/09/05_gate.png' | relative_url }}" alt="Gradient gate comparing finite-difference and adjoint directional derivatives at three steps" loading="lazy"></a>
<figcaption>Finite differences at three steps are 38.240, 38.241, and 38.244; the adjoint gives 38.240. All three pass the gate.</figcaption>
</figure>

| Step | FD | Adjoint g·v | Relative error |
|---|---|---|---|
| 2e-3 | 38.2396 | 38.2395 | 0.0000 |
| 5e-3 | 38.2405 | 38.2395 | 0.0000 |
| 1e-2 | 38.2436 | 38.2395 | 0.0001 |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/06_step_mma.png' | relative_url }}" data-lightbox aria-label="Enlarge: Designs after one gradient step at different sizes and the five-evaluation MMA history"><img src="{{ '/assets/meep/09/06_step_mma.png' | relative_url }}" alt="Designs after one gradient step at different sizes and the five-evaluation MMA history" loading="lazy"></a>
<figcaption>Top: one step from the same start with different α. Bottom: actual MMA evaluation history. Evaluation 5, J = 222.4, is retained; 119/121 pixels remain gray.</figcaption>
</figure>

| α | J | J / J_start |
|---|---|---|
| 0.2 | 16.66 | 3.9 |
| 1.0 | 118.92 | 27.6 |
| 3.0 | 176.24 | 40.9 |
| 8.0 | 235.54 | 54.7 |

In chapter 08 the objective fell at α = 2; here it rises through α = 8. Starting from uniform 0.5, a useful direction can keep improving J even when pixels are pushed to clipping bounds. Chapter 08 already started from a useful design, and traveling too far damaged it. Suitable step sizes depend on the problem, which is why the optimizer must adapt its steps.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/09/07_verify.png' | relative_url }}" data-lightbox aria-label="Enlarge: Fresh-simulation transmission measurements and electric fields before and after the update"><img src="{{ '/assets/meep/09/07_verify.png' | relative_url }}" alt="Fresh-simulation transmission measurements and electric fields before and after the update" loading="lazy"></a>
<figcaption>Normalized transmissions and Re(Ez) from a fresh simulation. In the updated design, light turns upward into the output waveguide.</figcaption>
</figure>

| Design | Mode-1 power | Total flux | T_mode1 | T_total |
|---|---|---|---|---|
| Uniform 0.5 start | 3.247 | 24.546 | 0.0154 | 0.1165 |
| Optimized (MMA eval 5) | 164.29 | 169.33 | 0.7801 | 0.8040 |

The difference T_total − T_mode1 (0.024) is power crossing the output plane outside mode 1, as in chapter 05’s diagnostic distinction. Internal J = 222.4 divided by P_in = 210.6 gives 1.056. That ratio is not transmission.

### Compare against the predictions

| Quantity | Initial prediction | Simulation | Verdict |
|--------|-------------|-----------|------|
| Input-plane mode-1 fraction | 0.98–1.02 | 1.0043 | ✅ |
| Starting T_mode1 | A few percent | 0.0154 | ✅ |
| Gradient pattern | Positive diagonal band | Negative center, positive waveguide extensions; diagonal appears only after a large step | ❌ |
| Gate relative error | Within 1% | 0.00%, 0.00%, 0.01% | ✅ |
| Manual step α | Rises, then falls | Keeps increasing through α = 8 | ❌ |
| T_mode1 after five MMA evaluations | 0.5–0.7 | 0.780 | ❌ (higher than predicted) |
| Same design at resolution 20 | A few percent difference | 0.780 → 0.639 | ❌ |
| Gray pixels | More than half | 119 / 121 | ✅ |

Four predictions failed, and those failures are the lesson. First, a raw gradient does not draw a mirror: it asks for lower central density and higher density near the waveguide connections; a diagonal emerges after multiple pixels saturate. Second, step-size intuition does not transfer between problems. Third, reaching 0.78 in five evaluations reflects the large design freedom, not a mature design. Fourth, the drop to 0.64 at resolution 20 shows strong dependence on the res-10 discretization.

### Convergence

| Variable | Value | T_mode1 | T_total | Note |
|---|---|---|---|---|
| Resolution | 10 | 0.7801 | 0.8040 | Resolution used for optimization |
| Resolution | 20 | 0.6391 | 0.6870 | Same 11 × 11 densities; denominator from a res-20 reference |
| Gate step | 2e-3 / 5e-3 / 1e-2 | FD 38.240 / 38.241 / 38.244 | — | All within 0.01% of adjoint 38.240 |

At resolution 10, the Si wavelength is 456 nm and spacing is 100 nm: only 4.5 cells per wavelength, below the Meep documentation’s recommendation of at least 8. With 119 gray pixels, permittivity varies smoothly, but its interpolation onto the Yee grid changes with resolution. Reoptimizing at res 20 would produce a different design. Except for the explicitly labeled resolution check, optimization results here use res 10.

### What the results do and do not establish

- Supported: at this cell, resolution 10, and single frequency, adjoint gradients agree with finite differences within 0.01%. Five MMA evaluations increase fresh-run output mode-1 transmission from 0.015 to 0.780 from a uniform 0.5 start. Chapter 08’s procedure transfers to a different objective.
- Not established: a fabrication-ready 0.78-transmission bend. There are 119 gray densities out of 121; transmission drops to 0.64 at res 20; maxeval 5 is not convergence; and no minimum-feature constraint is applied. Binarization will change performance. Other wavelengths, polarizations, and 3D are untested.


</details>

<details markdown="1">
<summary>Troubleshooting: symptoms and where to check</summary>

| Symptom | Cause | Fix |
|------|------|----------|
| Transmission above 1 | Dividing internal optimizer J by P_in | Measure numerator and denominator with `get_eigenmode_coefficients` |
| Mode-1 fraction below 0.9 | Source too narrow for modal tails or missing `eig_kpoint` | Inspect reference fields and verify 2 µm source width |
| Gate HOLD | Binary-boundary start or random direction | Use an interior point and gradient direction (chapter 08 §6) |
| Manual step reduces J | Can be normal for the problem | Record the turnover α; let the optimizer adapt |
| MMA drops during optimization | Trial step is too large | Retain the best evaluation; decreases can occur |
| Changing resolution changes the result | Design depends strongly on discretization | Optimize at target resolution or restrict feature size with filtering |
| Interpreting gray densities as a device | No binarization or feature-size constraints | Filters, projection, β schedules (official adjoint example 02 onward) |


</details>

<h2 id="check">6. Check: can you explain these two points?</h2>

<details markdown="1">
<summary>1. Where do forward and adjoint calculations start, and what does the gradient ask you to change?</summary>

The forward calculation starts at the mode-1 source in the left input waveguide. The adjoint is a separate calculation using an objective-derived source at the upper output port. Together they provide the local directions in which the 121 design densities should change to increase J. The first gradient itself is not the final waveguide geometry.

</details>

<details markdown="1">
<summary>2. With J = 222.4 and transmission 0.7801, why is this not a finished device?</summary>

J uses internal optimizer normalization; transmission is a consistently remeasured power ratio from fresh and reference runs. Even transmission changes to 0.6391 at resolution 20. The design contains 119 gray pixels and only five evaluations. Resolution and optimization convergence, minimum feature size, and binarization still need verification.

</details>

<h2 id="reference">7. References and full code</h2>

<details markdown="1">
<summary>English summary</summary>

- **What**: post 05 steered a 90° bend with one number, the radius. Here the corner is a 1 × 1 µm square opened as a free design region of 11 × 11 densities (SiO2 to Si), and the adjoint gradient fills it. The contract is the one from post 08; only the objective changes, from a diffraction order to the mode-1 power at the output port.
- **Result**: the source puts 100.4 % of its flux into mode 1. The gradient passes the gate with 0.00 %, 0.00 %, 0.01 % error. Unlike post 08, one hand-made step keeps rising as α grows (3.9×, 28×, 41×, 55×) because pixels saturate at 0/1. Five MMA evaluations lift the internal objective 52×. Measured again in a fresh simulation and normalized to the input mode-1 power, the bend transmission goes from 0.015 to 0.780 (total flux through the port: 0.117 to 0.804). At twice the resolution the same design gives 0.639.
- **Takeaway**: the four steps transfer unchanged when the objective changes. What does not transfer is intuition about step size: whether a gradient step overshoots depends on the problem. The optimizer's internal number is not a transmission (it even exceeds the input power), 119 of 121 pixels are still grey, and the design is not converged in resolution. This is a smoke test, not a device.
- **Code**: full script at the bottom, ~29 s on one core.


</details>

<details markdown="1">
<summary>Initial predictions and additional experiment ideas</summary>

### Make predictions before seeing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| Input-plane mode-1 fraction | 0.98–1.02 | `EigenModeSource` launched one mode in chapter 04 |
| T_mode1 of uniform 0.5 start | A few percent | A gray block is not a waveguide; light travels straight and leaks |
| Gradient pattern | Positive diagonal connecting input and output | A 45° mirror is the simplest bend |
| Gate relative error | Within 1% | 0.7% in chapter 08 |
| Manual step α | Rises, then falls | The same linear-approximation limit as chapter 08 |
| T_mode1 after five MMA evaluations | 0.5–0.7 | 121 degrees of freedom; expected above chapter 05 sharp-bend 0.20 |
| Same design at resolution 20 | A few percent difference | Fixed design densities preserve the nominal permittivity distribution |
| Gray pixels | More than half | Five evaluations will not saturate all variables |

**Acceptance criteria**: HOLD if gate relative error exceeds 20%. If mode-1 fraction is below 0.95, check the source first. T_mode1 > T_total indicates a decomposition problem.


| Change | Expected effect | Measurement to inspect |
|---------|----------|------------|
| Design region 1 × 1 → 1.5 × 1.5 µm | 256 variables, roughly twice the runtime | T_mode1, gray count |
| Initialize with chapter 05’s quarter-circle bend | Starting T near 0.9, small gradient | J_start, gate, change after five evaluations |
| `maxeval` 5 → 30 | Find where transmission plateaus | history, gray count |
| Optimize from the start at res 20 | Different design; compare with res 10 | T_mode1 at both resolutions |
| Average the objective at two frequencies (`nf=2`) | Bandwidth versus peak trade-off | T_mode1 at each frequency |


</details>

### Complete Python code

<details>
<summary>Complete code/bend_inverse.py (expand to view)</summary>
{% highlight python %}
"""Meep Example 09 - Waveguide bend inverse design (adjoint), with the same four-step contract as post 08.

Post 05 turned a 90-degree bend with ONE design variable (the radius). Here the corner is a 1 x 1 um square
opened as a free design region (11 x 11 densities, SiO2..Si) and the adjoint gradient fills it. Only the
objective changes: not a diffraction order but the guided mode-1 power at the output port.
  1. differentiability: eps_averaging=False, MaterialGrid do_averaging=False
  2. gradient gate: adjoint gradient vs centred finite differences along the gradient direction (interior point)
  3. a short MMA run (maxeval 5): a smoke test, not a converged design
  4. verification in a FRESH simulation with get_eigenmode_coefficients, normalized by the input mode-1 power
Plus: source check on a straight waveguide, forward field of uniform and random starts, adjoint field,
raw gradient, one manual step, a resolution check of the final design, two GIFs.

Run:  python bend_inverse.py      (~1 min on one core)
Out:  00_source.png, 01_layout.png, 02_source_check.png, 03_fields.png, 04_gradient.png, 05_gate.png,
      06_step_mma.png, 07_verify.png, 08_anim_optimized.gif, 09_anim_design.gif, result.json  (-> ../assets/09/)
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
import meep.adjoint as mpa
import nlopt
from autograd import numpy as npa

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "09")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()
np.random.seed(20260820)

# ---------------------------------------------------------------- (1) units & parameters (course week 10)
wl = 1.55
fcen = 1 / wl
fwidth = 0.12 * fcen
Si, SiO2 = mp.Medium(index=3.4), mp.Medium(index=1.44)
RES = 10
SX, SY = 6.0, 5.0
DPML = 1.0
W = 0.5                                   # waveguide width
SRC_X, SRC_SIZE = -1.5, 2.0               # EigenModeSource on the input waveguide
MON_IN_X = -1.0                           # input-power monitor (between source and design region)
MON_OUT_Y = 1.0                           # objective monitor on the output waveguide
D = 1.0                                   # design region side
NX = NY = 11                              # design grid: 11 x 11 = 121 densities
EXTENT = [-0.5 * SX, 0.5 * SX, -0.5 * SY, 0.5 * SY]
DEXT = [-0.5 * D, 0.5 * D, -0.5 * D, 0.5 * D]

sources = [mp.EigenModeSource(mp.GaussianSource(fcen, fwidth=fwidth), eig_band=1, direction=mp.NO_DIRECTION,
                              eig_kpoint=mp.Vector3(1, 0, 0), size=mp.Vector3(0, SRC_SIZE), center=mp.Vector3(SRC_X, 0))]
common = dict(resolution=RES, cell_size=mp.Vector3(SX, SY), boundary_layers=[mp.PML(DPML)], sources=sources, eps_averaging=False)
stop_cond = mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(0, MON_OUT_Y), 1e-5)


# ---------------------------------------------------------------- (2) geometry: input (-x) and output (+y) waveguides + design square
def waveguide_blocks():
    return [mp.Block(center=mp.Vector3(-SX / 4, 0), size=mp.Vector3(SX / 2, W), material=Si),
            mp.Block(center=mp.Vector3(0, SY / 4), size=mp.Vector3(W, SY / 2), material=Si)]


def geometry_with(weights):
    grid = mp.MaterialGrid(mp.Vector3(NX, NY), SiO2, Si, weights=np.asarray(weights).reshape(NX, NY), grid_type="U_MEAN", do_averaging=False)
    return waveguide_blocks() + [mp.Block(center=mp.Vector3(), size=mp.Vector3(D, D), material=grid)]


design_variables = mp.MaterialGrid(mp.Vector3(NX, NY), SiO2, Si, grid_type="U_MEAN", do_averaging=False)     # contract 1
design_region = mpa.DesignRegion(design_variables, volume=mp.Volume(center=mp.Vector3(), size=mp.Vector3(D, D)))
geometry = waveguide_blocks() + [mp.Block(center=design_region.center, size=design_region.size, material=design_variables)]

# ---------------------------------------------------------------- (4) simulation + (5) objective: output-port mode-1 power
sim = mp.Simulation(geometry=geometry, **common)
out_mode = mpa.EigenmodeCoefficient(sim, mp.Volume(center=mp.Vector3(0, MON_OUT_Y), size=mp.Vector3(2, 0)), mode=1)
opt = mpa.OptimizationProblem(simulation=sim, objective_functions=lambda a: npa.abs(a) ** 2, objective_arguments=[out_mode],
                              design_regions=[design_region], fcen=fcen, df=0, nf=1)
x_start = 0.5 * np.ones(NX * NY)          # uniform grey: an interior point, differentiable, no bias
opt.update_design([x_start])
# a throw-away copy only for the layout figure: plot2D draws flux monitors, mpa objectives it does not
sim_plot = mp.Simulation(geometry=geometry_with(x_start), **common)
sim_plot.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(0, MON_OUT_Y), size=mp.Vector3(2, 0)))
sim_plot.add_flux(fcen, 0, 1, mp.FluxRegion(center=mp.Vector3(MON_IN_X, 0), size=mp.Vector3(0, 2)))
annotated_layout(
    sim_plot, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(7.4, 6.0), axis_step=1.0,
    title="bend as a free design region: input -x, output +y, 1 x 1 um square of 11 x 11 densities",
    params_text=f"wl={wl} res={RES}\ncell {SX}x{SY}, w={W}\nNx=Ny={NX} (121 vars)",
    params_xy=(-2.9, 2.3), pml_xy=(-2.5, -0.5 * SY + 0.5 * DPML), decay_point=(0, MON_OUT_Y), decay_text_xy=(0.9, 1.75),
    labels=[Label("design region: MaterialGrid, start = uniform 0.5", (-0.5, -0.5), (-2.9, -1.3), step=2, color="black"),
            Label("EigenModeSource, mode 1 -> +x", (SRC_X, 0.6), (-2.9, 1.3), step=3, color="red"),
            Label("objective: |a_out|^2 on this line", (0.8, MON_OUT_Y), (0.9, 0.5), step=5, color="blue"),
            Label("input monitor (normalization)", (MON_IN_X, -0.8), (-0.2, -2.0), step=5, color="blue")])
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")


def run_dft_field(src_list, geometry_list):
    s = mp.Simulation(geometry=geometry_list, **dict(common, sources=src_list))
    dft = s.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(SX, SY))
    s.run(until_after_sources=stop_cond)
    field = s.get_dft_array(dft, mp.Ez, 0); eps = s.get_epsilon(); s.reset_meep()
    return field, eps


def contour(a, eps):
    xs = np.linspace(EXTENT[0], EXTENT[1], eps.shape[0]); ys = np.linspace(EXTENT[2], EXTENT[3], eps.shape[1])
    a.contour(xs, ys, eps.T, levels=[0.5 * (1.44 ** 2 + 3.4 ** 2)], colors="w", linewidths=0.6, alpha=0.9)


def show_design(a, weights, title):
    im = a.imshow(np.asarray(weights).reshape(NX, NY).T, origin="lower", extent=DEXT, cmap="gray_r", vmin=0, vmax=1, aspect="equal")
    a.set_title(title, fontsize=8); a.set_xlabel("x [um]")
    return im


# ---------------------------------------------------------------- source check: straight waveguide, mode-1 share at the input monitor
straight = [mp.Block(center=mp.Vector3(), size=mp.Vector3(mp.inf, W), material=Si)]
field_src, eps_src = run_dft_field(sources, straight)
s_in = mp.Simulation(geometry=straight, **common)
mon_in = s_in.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(MON_IN_X, 0), size=mp.Vector3(0, 2)))
s_in.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(MON_IN_X, 0), 1e-5))
total_in = float(mp.get_fluxes(mon_in)[0])
input_power = float(abs(s_in.get_eigenmode_coefficients(mon_in, [1], direction=mp.X).alpha[0, 0, 0]) ** 2)
s_in.reset_meep()
print(f"source check: input flux {total_in:.5e}, mode-1 power {input_power:.5e}, mode-1 share {input_power / total_in:.4f}")
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
lim = float(np.max(np.abs(field_src)))
ax[0].imshow(np.real(field_src).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal"); ax[0].set_title("Re(Ez): wavefront", fontsize=9)
ax[1].imshow(np.abs(field_src).T, extent=EXTENT, origin="lower", cmap="inferno", aspect="equal"); ax[1].set_title("|Ez|: envelope", fontsize=9)
for a in ax:
    contour(a, eps_src); a.axvline(SRC_X, color="red", lw=1.2, ls="--"); a.axvline(MON_IN_X, color="blue", lw=1.2, ls=":"); a.set_xlabel("x [um]")
ax[0].set_ylabel("y [um]")
fig.suptitle(f"source check on a straight waveguide: mode-1 share at x = {MON_IN_X} um is {input_power / total_in:.4f}", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_source_check.png"), dpi=150); plt.close(fig)


def fom(x, need_gradient=False):
    """Objective = output-port mode-1 power |a_out|^2 in optimizer units (NOT normalized; see contract 4)."""
    f, dJ = opt([np.clip(x, 0, 1)], need_gradient=need_gradient)
    f = float(np.real(np.asarray(f).squeeze()))
    if not need_gradient:
        return f
    return f, np.squeeze(np.asarray(dJ))


# ---------------------------------------------------------------- forward fields: uniform vs random start; adjoint field
field_fwd, eps_fwd = run_dft_field(sources, geometry_with(x_start))
f_start, g_start = fom(x_start, need_gradient=True)
x_random = np.random.rand(NX * NY)
field_rand, eps_rand = run_dft_field(sources, geometry_with(x_random))
f_random = fom(x_random)
adjoint_sources = opt.adjoint_sources[0]
field_adj, eps_adj = run_dft_field(adjoint_sources, geometry_with(x_start))
print(f"forward: uniform-0.5 FOM = {f_start:.4f} (|grad| = {np.linalg.norm(g_start):.3e}); random start FOM = {f_random:.4f}; "
      f"adjoint sources: {len(adjoint_sources)} x {type(adjoint_sources[0]).__name__}")

fig, ax = plt.subplots(2, 4, figsize=(13, 6.4), gridspec_kw={"width_ratios": [0.55, 1, 1, 1]})
lim = max(np.max(np.abs(field_fwd)), np.max(np.abs(field_rand)))
for r, (weights, fld, eps, tag, val) in enumerate(((x_start, field_fwd, eps_fwd, "uniform 0.5", f_start), (x_random, field_rand, eps_rand, "random seed", f_random))):
    show_design(ax[r, 0], weights, f"design: {tag}\nFOM = {val:.3f}"); ax[r, 0].set_ylabel("y [um]")
    ax[r, 1].imshow(np.real(fld).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal"); ax[r, 1].set_title("forward Re(Ez)", fontsize=9)
    ax[r, 2].imshow(np.abs(fld).T, extent=EXTENT, origin="lower", cmap="inferno", aspect="equal"); ax[r, 2].set_title("forward |Ez|", fontsize=9)
    for a in ax[r, 1:3]:
        contour(a, eps); a.set_xlabel("x [um]")
la = float(np.max(np.abs(field_adj)))
ax[0, 3].imshow(np.real(field_adj).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-la, vmax=la, aspect="equal"); ax[0, 3].set_title("adjoint Re(Ez) (source at the output port)", fontsize=9)
ax[1, 3].imshow(np.abs(field_adj).T, extent=EXTENT, origin="lower", cmap="inferno", aspect="equal"); ax[1, 3].set_title("adjoint |Ez|", fontsize=9)
for a in ax[:, 3]:
    contour(a, eps_adj); a.set_xlabel("x [um]")
fig.suptitle("rows: uniform vs random start (forward); right column: the adjoint field of the uniform start", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_fields.png"), dpi=150); plt.close(fig)

# ---------------------------------------------------------------- raw gradient on the 11 x 11 grid
g2 = g_start.reshape(NX, NY)
lim = float(np.max(np.abs(g2)))
fig, ax = plt.subplots(1, 3, figsize=(12, 3.8))
im0 = show_design(ax[0], x_start, "current design (uniform 0.5)"); plt.colorbar(im0, ax=ax[0], fraction=0.046)
im1 = ax[1].imshow(g2.T, origin="lower", extent=DEXT, cmap="RdBu_r", vmin=-lim, vmax=lim, aspect="equal"); ax[1].set_title("raw adjoint gradient dJ/d(density)\nred: more Si helps, blue: more SiO2 helps", fontsize=8); plt.colorbar(im1, ax=ax[1], fraction=0.046)
im2 = ax[2].imshow(np.abs(g2).T, origin="lower", extent=DEXT, cmap="viridis", aspect="equal"); ax[2].set_title("|gradient|: where the design matters most", fontsize=8); plt.colorbar(im2, ax=ax[2], fraction=0.046)
for a in ax[1:]:
    a.set_xlabel("x [um]")
ax[0].set_ylabel("y [um]")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_gradient.png"), dpi=150); plt.close(fig)
print(f"gradient: max {g2.max():+.4e}, min {g2.min():+.4e}; positive pixels {int((g2 > 0).sum())}, negative {int((g2 < 0).sum())}")

# ---------------------------------------------------------------- contract 2: gradient gate (uniform 0.5 is already an interior point)
assert np.all((x_start > 0.02) & (x_start < 0.98))
v = g_start / np.linalg.norm(g_start)
adjoint_dd = float(np.dot(g_start, v))
steps = [2e-3, 5e-3, 1e-2]
gate_rows = []
for step in steps:
    fd = (fom(x_start + step * v) - fom(x_start - step * v)) / (2 * step)
    rel = abs(adjoint_dd - fd) / max(abs(fd), 1e-30)
    gate_rows.append({"step": step, "fd": fd, "adjoint": adjoint_dd, "rel_err": rel, "pass": bool(rel <= 0.20 and np.sign(fd) == np.sign(adjoint_dd))})
gradient_gate = all(r["pass"] for r in gate_rows)
print("gate: " + "; ".join(f"step {r['step']:.0e}: FD {r['fd']:.5e} vs adjoint {r['adjoint']:.5e}, rel {r['rel_err']:.4f} {'PASS' if r['pass'] else 'HOLD'}" for r in gate_rows)
      + f" -> gradient gate {'PASS' if gradient_gate else 'HOLD'}")
fig, ax = plt.subplots(1, 2, figsize=(10, 3.4))
idx = np.arange(len(steps))
ax[0].bar(idx - 0.2, [r["fd"] for r in gate_rows], width=0.4, color="tab:orange", label="centred finite difference")
ax[0].bar(idx + 0.2, [adjoint_dd] * 3, width=0.4, color="tab:blue", label="adjoint  g . v")
ax[0].set_xticks(idx); ax[0].set_xticklabels([f"{s:.0e}" for s in steps]); ax[0].set_xlabel("finite-difference step"); ax[0].set_ylabel("directional derivative")
ax[0].set_title("adjoint vs finite difference along the gradient direction", fontsize=9); ax[0].grid(axis="y", alpha=0.3); ax[0].legend(fontsize=8)
bars = ax[1].bar(idx, [r["rel_err"] for r in gate_rows], color=["tab:green" if r["pass"] else "tab:red" for r in gate_rows])
ax[1].axhline(0.20, ls="--", color="crimson", lw=1.2, label="gate: 20 %")
for b, r in zip(bars, gate_rows):
    ax[1].text(b.get_x() + b.get_width() / 2, r["rel_err"] + 0.004, f"{r['rel_err']:.4f}", ha="center", fontsize=8)
ax[1].set_xticks(idx); ax[1].set_xticklabels([f"{s:.0e}" for s in steps]); ax[1].set_ylim(0, 0.25); ax[1].set_ylabel("relative error")
ax[1].set_title(f"gradient gate: {'PASS' if gradient_gate else 'HOLD'}", fontsize=9); ax[1].grid(axis="y", alpha=0.3); ax[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_gate.png"), dpi=150); plt.close(fig)
if not gradient_gate:
    raise SystemExit("gradient gate HOLD: do not interpret optimizer results")

# ---------------------------------------------------------------- one manual step, then MMA (contract 3)
one_step = []
for alpha in (0.2, 1.0, 3.0, 8.0):
    x_try = np.clip(x_start + alpha * v, 0, 1)
    one_step.append((alpha, x_try, fom(x_try)))
print("one manual step: " + ", ".join(f"alpha {a} -> {f:.3f} ({f / f_start:.1f}x)" for a, _, f in one_step))

history, design_history = [], []


def nlopt_objective(x, grad):
    f, dJ = fom(x, need_gradient=True)
    if grad.size > 0:
        grad[:] = dJ
    history.append(f); design_history.append(np.array(x, copy=True))
    return f


solver = nlopt.opt(nlopt.LD_MMA, NX * NY)
solver.set_lower_bounds(np.zeros(NX * NY)); solver.set_upper_bounds(np.ones(NX * NY))
solver.set_max_objective(nlopt_objective); solver.set_maxeval(5)
solver.optimize(x_start.copy())
best_k = int(np.argmax(history))
x_optimized = design_history[best_k]                          # keep the best evaluated design (MMA may overshoot)
gray = int(np.sum((x_optimized > 0.02) & (x_optimized < 0.98)))
print("MMA (maxeval 5): " + ", ".join(f"eval {k + 1}: {f:.3f}" for k, f in enumerate(history)) + f"; best eval {best_k + 1} = {max(history):.3f} ({max(history) / history[0]:.1f}x); grayscale pixels {gray}/{NX * NY}")

fig, ax = plt.subplots(2, 6, figsize=(14, 5.6))
show_design(ax[0, 0], x_start, f"start (uniform 0.5)\nFOM {f_start:.2f}"); ax[0, 0].set_ylabel("y [um]")
for a, (alpha, x_try, f_try) in zip(ax[0, 1:5], one_step):
    show_design(a, x_try, f"one step, alpha = {alpha}\nFOM {f_try:.1f}")
ax[0, 5].plot(range(1, len(history) + 1), history, "o-", color="tab:blue"); ax[0, 5].axhline(f_start, ls="--", color="gray", lw=1, label="uniform start")
ax[0, 5].set_xticks(range(1, len(history) + 1)); ax[0, 5].set_xlabel("MMA evaluation"); ax[0, 5].set_ylabel("|a_out|^2 (optimizer units)"); ax[0, 5].set_title("MMA history", fontsize=8); ax[0, 5].grid(alpha=0.3); ax[0, 5].legend(fontsize=7)
for k in range(5):
    show_design(ax[1, k], design_history[k], f"MMA eval {k + 1}  FOM {history[k]:.1f}" + ("  (kept)" if k == best_k else ""))
ax[1, 0].set_ylabel("y [um]")
show_design(ax[1, 5], x_optimized, f"optimized (eval {best_k + 1})\n{gray} grey px of {NX * NY}")
fig.suptitle("top: one manual gradient step (alpha sweep) and the MMA history; bottom: the design at every MMA evaluation", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "06_step_mma.png"), dpi=150); plt.close(fig)


# ---------------------------------------------------------------- contract 4: fresh simulation, modal power / input mode-1 power
def modal_power(weights, res=RES):
    s = mp.Simulation(geometry=geometry_with(weights), **dict(common, resolution=res))
    mon = s.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(0, MON_OUT_Y), size=mp.Vector3(2, 0)))
    dft = s.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(SX, SY))
    s.run(until_after_sources=stop_cond)
    total = float(mp.get_fluxes(mon)[0])
    mode1 = float(abs(s.get_eigenmode_coefficients(mon, [1], direction=mp.Y).alpha[0, 0, 0]) ** 2)
    field = s.get_dft_array(dft, mp.Ez, 0); eps = s.get_epsilon(); s.reset_meep()
    return mode1, total, field, eps


report = {}
for tag, weights in (("start", x_start), ("optimized", x_optimized)):
    mode1, total, fld, eps = modal_power(weights)
    report[tag] = {"mode1": mode1, "total": total, "T_mode1": mode1 / input_power, "T_total": total / input_power, "field": fld, "eps": eps}
    print(f"verify [{tag}]: mode-1 power {mode1:.4e}, total flux {total:.4e} -> T_mode1 {mode1 / input_power:.4f}, T_total {total / input_power:.4f}")
# resolution check of the final design (same 11 x 11 densities, finer Yee grid)
res_check = {}
for res in (RES, 2 * RES):
    m1, tot, _, _ = modal_power(x_optimized, res=res)
    s_in2 = mp.Simulation(geometry=straight, **dict(common, resolution=res))
    mi = s_in2.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(MON_IN_X, 0), size=mp.Vector3(0, 2)))
    s_in2.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, mp.Vector3(MON_IN_X, 0), 1e-5))
    pin = float(abs(s_in2.get_eigenmode_coefficients(mi, [1], direction=mp.X).alpha[0, 0, 0]) ** 2); s_in2.reset_meep()
    res_check[res] = {"T_mode1": m1 / pin, "T_total": tot / pin}
    print(f"resolution check [{res}]: T_mode1 {m1 / pin:.4f}, T_total {tot / pin:.4f}")

fig, ax = plt.subplots(1, 3, figsize=(13, 4.2), gridspec_kw={"width_ratios": [1.1, 1, 1]})
idx = np.arange(2)
tm = [report["start"]["T_mode1"], report["optimized"]["T_mode1"]]; tt = [report["start"]["T_total"], report["optimized"]["T_total"]]
ax[0].bar(idx - 0.2, tm, width=0.4, color="tab:blue", label="T_mode1 (output mode 1)"); ax[0].bar(idx + 0.2, tt, width=0.4, color="tab:gray", label="T_total (all flux)")
for k in range(2):
    ax[0].text(k - 0.2, tm[k] + 0.01, f"{tm[k]:.4f}", ha="center", fontsize=8); ax[0].text(k + 0.2, tt[k] + 0.01, f"{tt[k]:.4f}", ha="center", fontsize=8)
ax[0].set_xticks(idx); ax[0].set_xticklabels(["uniform start", f"after MMA (eval {best_k + 1})"]); ax[0].set_ylim(0, 1.0); ax[0].set_ylabel("normalized to input mode-1 power")
ax[0].set_title("contract 4: measured again in a new simulation", fontsize=9); ax[0].grid(axis="y", alpha=0.3); ax[0].legend(fontsize=7)
lim = max(np.max(np.abs(report["start"]["field"])), np.max(np.abs(report["optimized"]["field"])))
for a, tag in zip(ax[1:], ("start", "optimized")):
    a.imshow(np.real(report[tag]["field"]).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
    contour(a, report[tag]["eps"]); a.set_title(f"Re(Ez), {tag}  (T_mode1 = {report[tag]['T_mode1']:.3f})", fontsize=9); a.set_xlabel("x [um]")
ax[1].set_ylabel("y [um]")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "07_verify.png"), dpi=150); plt.close(fig)

# ---------------------------------------------------------------- GIF 1: a short pulse through the optimized bend (source -> output monitor)
fw_anim = 0.3 * fcen
sim_a = mp.Simulation(geometry=geometry_with(x_optimized), **dict(common, sources=[
    mp.EigenModeSource(mp.GaussianSource(fcen, fwidth=fw_anim), eig_band=1, direction=mp.NO_DIRECTION, eig_kpoint=mp.Vector3(1, 0, 0),
                       size=mp.Vector3(0, SRC_SIZE), center=mp.Vector3(SRC_X, 0))]))
sim_a.init_sim()
vol_a = mp.Volume(center=mp.Vector3(), size=mp.Vector3(SX - 2 * DPML, SY - 2 * DPML))
eps_a = sim_a.get_array(vol=vol_a, component=mp.Dielectric)
ext_a = [-(SX / 2 - DPML), SX / 2 - DPML, -(SY / 2 - DPML), SY / 2 - DPML]
t0 = 5 / fw_anim
path = abs(SRC_X) + SY / 2                                    # input straight + output straight, roughly
frames, times = record_frames(sim_a, vol_a, mp.Ez, t_start=t0 - 2 / fw_anim, t_end=t0 + 1.2 * path * 3.4, n_frames=60)
animate_fields(frames, times, ext_a, os.path.join(OUT, "08_anim_optimized.gif"), eps=eps_a, figsize=(6.2, 5.0), dpi=70,
               lines=[((SRC_X, -1), (SRC_X, 1), "red", "source"), ((-1, MON_OUT_Y), (1, MON_OUT_Y), "blue", "output monitor")],
               title="optimized bend", legend_loc="lower right")

# ---------------------------------------------------------------- GIF 2: how the design changed, start -> every MMA eval -> final
evo = [x_start] + design_history + [x_optimized]
evo_lab = ["start"] + [f"eval {k + 1}" for k in range(len(design_history))] + [f"final (eval {best_k + 1})"]
evo_fom = [f_start] + history + [max(history)]
fig_e, ax_e = plt.subplots(figsize=(4.0, 3.8))
im_e = ax_e.imshow(evo[0].reshape(NX, NY).T, origin="lower", extent=DEXT, cmap="gray_r", vmin=0, vmax=1, aspect="equal")
ax_e.set_xlabel("x [um]"); ax_e.set_ylabel("y [um]"); ttl_e = ax_e.set_title("", fontsize=9)
fig_e.colorbar(im_e, ax=ax_e, fraction=0.046, label="density (0 = SiO2, 1 = Si)")
fig_e.tight_layout()


def _evo(i):
    im_e.set_data(evo[i].reshape(NX, NY).T); ttl_e.set_text(f"{evo_lab[i]}   FOM = {evo_fom[i]:.1f}")
    return im_e, ttl_e


animation.FuncAnimation(fig_e, _evo, frames=len(evo), blit=False).save(os.path.join(OUT, "09_anim_design.gif"), writer=animation.PillowWriter(fps=1.5), dpi=80)
plt.close(fig_e)

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"params": {"wl": wl, "res": RES, "cell": [SX, SY], "w": W, "design": [D, D], "N": [NX, NY], "fwidth_rel": 0.12},
                   "source_check": {"total_in": total_in, "input_power": input_power, "mode1_share": input_power / total_in},
                   "fom": {"start": f_start, "random": f_random, "grad_norm": float(np.linalg.norm(g_start)),
                           "grad_max": float(g2.max()), "grad_min": float(g2.min()), "grad_pos": int((g2 > 0).sum()), "grad_neg": int((g2 < 0).sum())},
                   "gate": gate_rows, "gate_pass": gradient_gate,
                   "one_step": [{"alpha": a, "fom": f} for a, _, f in one_step],
                   "mma": {"history": history, "best_eval": best_k + 1, "gray_pixels": gray},
                   "verify": {k: {kk: vv for kk, vv in v.items() if kk not in ("field", "eps")} for k, v in report.items()},
                   "resolution_check": res_check,
                   "x_optimized": x_optimized.tolist(),
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__, "nlopt": f"{nlopt.version_major()}.{nlopt.version_minor()}"}, f, indent=2)
{% endhighlight %}
</details>

Unlike the excerpts in §4, the complete code includes figure saving, two GIFs, result.json output, and a resolution-20 remeasurement. The shared helper `blogfig.py` is in the same `code/` folder. Full code and helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**Execution results (run on 2026-10-23)**:
```
source check: input flux 2.09705e+02, mode-1 power 2.10614e+02, mode-1 share 1.0043
forward: uniform-0.5 FOM = 4.3095 (|grad| = 3.824e+01); random start FOM = 12.2263; adjoint sources: 1 x EigenModeSource
gradient: max +4.4568e+00, min -1.3404e+01; positive pixels 49, negative 72
gate: step 2e-03: FD 3.82396e+01 vs adjoint 3.82395e+01, rel 0.0000 PASS; step 5e-03: FD 3.82405e+01 vs adjoint 3.82395e+01, rel 0.0000 PASS; step 1e-02: FD 3.82436e+01 vs adjoint 3.82395e+01, rel 0.0001 PASS -> gradient gate PASS
one manual step: alpha 0.2 -> 16.657 (3.9x), alpha 1.0 -> 118.917 (27.6x), alpha 3.0 -> 176.244 (40.9x), alpha 8.0 -> 235.537 (54.7x)
MMA (maxeval 5): eval 1: 4.310, eval 2: 180.684, eval 3: 4.533, eval 4: 106.244, eval 5: 222.402; best eval 5 = 222.402 (51.6x); grayscale pixels 119/121
verify [start]: mode-1 power 3.2469e+00, total flux 2.4546e+01 -> T_mode1 0.0154, T_total 0.1165
verify [optimized]: mode-1 power 1.6429e+02, total flux 1.6933e+02 -> T_mode1 0.7801, T_total 0.8040
resolution check [10]: T_mode1 0.7801, T_total 0.8040
resolution check [20]: T_mode1 0.6391, T_total 0.6870
```

**Reproduction environment**: meep 1.33.0 · nlopt 2.x · autograd · Python 3.11 · `conda install -c conda-forge pymeep nlopt autograd` · run `python bend_inverse.py` (about 29 s, single core)

### Official documentation and further reading

- [Official Adjoint Solver tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Adjoint_Solver/) · [Adjoint example 01 Introduction (waveguide bend)](https://github.com/NanoComp/meep/blob/master/python/examples/adjoint_optimization/01-Introduction.ipynb) · [Adjoint example 02 filtering and projection](https://github.com/NanoComp/meep/blob/master/python/examples/adjoint_optimization/02-Filtered_Waveguide_Bend.ipynb)
- [`MaterialGrid` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#materialgrid) · [`EigenModeSource`](https://meep.readthedocs.io/en/latest/Python_User_Interface/#eigenmodesource) · [NLopt MMA](https://nlopt.readthedocs.io/en/latest/NLopt_Algorithms/#mma-method-of-moving-asymptotes-and-ccsa)
- Previous: [08 · Metagrating inverse design]({{ '/en/metagrating-inverse/' | relative_url }}) · One-variable bend design: [05 · Bent waveguide and radius trade-off]({{ '/en/waveguide-bend-90/' | relative_url }}) · Start of the series: [01 · Point and line sources]({{ '/en/point-line-source/' | relative_url }}) · Next (season 2): [10 · 3D dipole radiation patterns]({{ '/en/dipole-pattern-3d/' | relative_url }})
