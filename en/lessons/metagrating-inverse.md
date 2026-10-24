---
layout: lesson
permalink: /en/metagrating-inverse/
lesson_title: "How can a grating send more light in the desired direction?"
lesson_summary: "Adjust 73 densities to increase +1-order efficiency. Verify the actual gradient, then connect a single update to independent measurements."
lesson_goals:
  - "Explain how forward and adjoint calculations produce density gradients."
  - "Check what the derivative means using a finite-difference gate and one step."
  - "Distinguish optimizer scores from order efficiencies in a fresh simulation."
lesson_prerequisites: "Chapter 06: diffraction orders · Chapter 07: meta-atom libraries and supercells"
date: 2026-10-23
title: "Meep Example 08 · Metagrating inverse design — a four-step contract for forward, adjoint, gradient, and verification"
title_en: "Meep Example 08 · Metagrating inverse design — a four-step contract: forward, adjoint, gradient, verification"
lang: en
translation_key: metagrating-inverse
series: meep-examples
part: 8
level: intermediate
runtime: "48 s (single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Adjoint_Solver/"
tags: [meep, fdtd, adjoint, inverse-design, metagrating, nlopt, mma]
image: /assets/meep/08/06_verify.png
excerpt: "the post-07 library design (four Si bars) becomes the starting point of an adjoint optimisation. The whole supercell period is a 1D design region of 73 density pixels; the objective is the +1-order efficiency. Four steps are enforced: differentiable materials, a finite-difference gate on the gradient, a short MMA run, and a fresh-simulation verification."
---

<h2 id="observe">1. Observe: can the same grating send more light?</h2>

The four Si ridges chosen in chapter 07 respond differently when their neighbors differ from those in the library. Here we open the entire period to **73 density variables** and increase light traveling into the upper-right +1 order.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/06_verify.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/06_verify.png' | relative_url }}" alt="Original and updated grating order efficiencies and electric fields compared in a fresh simulation"></a>
<figcaption>Independent verification results: +1 efficiency increases from 0.4959 to 0.6228, while order 0 decreases from 0.0666 to 0.0169. Select the figure to enlarge the original.</figcaption>
</figure>

<p class="lesson-note"><strong>Improvement is not convergence.</strong> This is the best design, evaluation 3 of five MMA evaluations. With 27 of 73 densities still gray, no minimum-feature or binarization constraints, and no resolution-convergence study, it is not a fabrication-ready optimum.</p>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/07_anim_optimized.gif' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/07_anim_optimized.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/08/07_anim_optimized.gif' | relative_url }}" data-static-src="{{ '/assets/meep/08/06_verify.png' | relative_url }}" alt="A short pulse exits obliquely from a finite array repeating five periods of the optimized grating"></a>
<button type="button" class="animation-toggle" hidden>Pause animation</button>
<figcaption>Actual pulse-propagation animation. The wavefront tilts toward roughly +59° in a finite five-period array. The efficiency table above comes from a one-period periodic calculation, so efficiencies should not be read from this animation itself.</figcaption>
</figure>

<h2 id="predict">2. Predict: is a longer step along the gradient always better?</h2>

<fieldset class="prediction">
<legend>What happens if the step size α keeps increasing along the current gradient?</legend>
<label><input type="radio" name="metagrating-prediction" value="always"> +1 efficiency keeps increasing.</label>
<label><input type="radio" name="metagrating-prediction" value="local"> It can increase initially but decrease for a large step.</label>
</fieldset>

<details markdown="1">
<summary>Compare your prediction with the actual result</summary>

The second answer is correct. In the original run, α = 0.8 reached J = 0.6134, but α = 2.0 dropped to 0.4840, below the starting 0.4970. A gradient is the **local slope around the current design**; it does not guarantee the performance of distant designs.

</details>

<h2 id="understand">3. Understand: verify the derivative before changing material</h2>

{% include chapter-illustration.html %}

Density ρ = 0 means air, 1 means Si, and intermediate values interpolate permittivity. The 73 variables control vertical strips along x. Each strip shares one density through its entire 0.9 µm height; the SiO₂ substrate remains fixed.

<p class="lesson-note">Conceptual illustration. Light enters along +y from below through the substrate; the target is the upper-right +1 order. Forward and adjoint fields come from separate calculations, and the gray strips are not an actual optimization result.</p>

1. **Forward:** excite the original source and measure the +1 mode amplitude.
2. **Adjoint:** place a source derived from the objective at the output monitor and run a separate calculation.
3. **Gradient gate:** compare the derivative obtained from the two stored fields and material-density dependence with finite differences.
4. **Update and remeasure:** take one manual step, then update with MMA and remeasure order powers in a fresh simulation.

The objective is **J = &#124;a₊₁&#124;²/P_in**. In this single-frequency, single-objective example, one forward and one adjoint calculation give derivatives for every density. Simply multiplying the brightness of two field images does not produce the final geometry.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/03_gradient.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/03_gradient.png' | relative_url }}" alt="Actual signed gradient for 73 densities, with strong positive sensitivity near the second ridge edges" loading="lazy"></a>
<figcaption>Actual initial gradient. Red means increasing density increases J locally; blue means the opposite. The five largest positive values cluster around the second ridge at x = −0.275~−0.175 µm.</figcaption>
</figure>

The gate uses an interior design away from the 0/1 bounds and the gradient direction. Central differences must remain unclipped to compare the same derivative. Relative errors at three steps are **0.68%, 0.12%, 0.06%**, passing the 20% threshold. This verifies the derivative for this setup, not optimization or resolution convergence.

<p class="lesson-note"><strong>Model scope.</strong> 2D Ez, wavelength 1.55 µm, periodic x boundaries, y PML, and resolution 40. The design region is 73 × 1, without boundary averaging, filters, or projection. Adding a filter or projection also requires differentiating that mapping.</p>

<h2 id="run">4. Run: change only one manual step size</h2>

Use the repository’s <code>code/</code> folder in an environment with Meep 1.33.0, nlopt, and autograd. Full code and the shared helper are in the reference section below. Keep the original run first; its recorded runtime is about 48 seconds on one core.

~~~bash
OMP_NUM_THREADS=1 python metagrating_inverse.py
~~~

**Change only α = 2.0 to 1.2 in this experiment.** In the manual-step loop <code>for alpha in (0.05, 0.3, 0.8, 2.0):</code>, replace only the final value with <code>1.2</code> and run the same command. Keep the gradient, starting design, and MMA evaluation count fixed.

Compare J and ΔJ for α = 0.8 and 1.2 in the <code>one manual step</code> log. Although 1.2 travels farther than 0.8, it need not perform better. Measure the new result; do not reuse the old α = 2.0 result 0.4840.

<h2 id="interpret">5. Interpret: which order improved?</h2>

| Fresh-simulation measurement | Original design | Updated design |
|---|---:|---:|
| Target +1 efficiency | 0.4959 | 0.6228 |
| Order 0 efficiency | 0.0666 | 0.0169 |
| Order −1 efficiency | 0.1026 | 0.0973 |
| Order sum = total transmission | 0.6651 | 0.7369 |

Improvement mainly comes from reducing order-0 leakage. Order −1 is nearly unchanged. Check that the sum of order efficiencies agrees with total flux before trusting the decomposition.

The best internal MMA J is **0.6241**; independently verified +1 efficiency is **0.6228**. The difference is small, but report the fresh-run measurement. Intermediate evaluations can be worse, as with J = 0.0492 at evaluation 4, so verify the saved best design rather than simply the last evaluation.

<h2 id="check">6. Check your understanding</h2>

1. Why can a large α reduce efficiency even after the gradient gate passes?
2. Which should be reported as final efficiency, MMA’s 0.6241 or the fresh run’s 0.6228, and what else must be checked?

<details markdown="1">
<summary>Read both answers</summary>

1. The gate verifies the local derivative at the current interior point. Large moves break the linear approximation and may clip densities at 0/1, so improvement is not guaranteed.
2. Report the fresh run’s **0.6228**. Also check agreement of order sum with total flux, selection of the best design, and the limits imposed by grayscale densities, resolution, and absent fabrication constraints.

</details>

<h2 id="reference">7. References and full code</h2>

Detailed original explanations, measurement tables, and logs are retained below. After completing the single-variable experiment above, expand whichever sections you need.


<details markdown="1">
<summary>English summary</summary>

### TL;DR (English)

<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/06_verify.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/06_verify.png' | relative_url }}" alt="How can a grating send more light in the desired direction? Original overview figure" loading="lazy"></a>
</figure>

- **What**: the post-07 library design (four Si bars) becomes the starting point of an adjoint optimisation. The whole supercell period is a 1D design region of 73 density pixels; the objective is the +1-order efficiency. Four steps are enforced: differentiable materials, a finite-difference gate on the gradient, a short MMA run, and a fresh-simulation verification.
- **Result**: the gradient passes the gate (0.7 %, 0.1 %, 0.06 % error at three step sizes). One hand-made gradient step lifts the efficiency from 0.497 to 0.613; five MMA evaluations reach 0.624. Measured again in a new simulation, order by order: +1 goes from 0.496 to 0.623 (61 % → 77 % of the 4-level bound), 0 drops from 0.067 to 0.017, −1 stays near 0.10.
- **Takeaway**: adjoint gives you every pixel's derivative for the price of two runs, but a wrong gradient fails silently. Gate it, take one step by hand before trusting an optimiser, and never report the optimiser's own number: re-measure in a clean run. maxeval = 5 is a smoke test, not a converged design, and 27 of 73 pixels are still grey.
- **Code**: full script at the bottom, ~48 s on one core.

</details>

<details markdown="1">
<summary>Background, physical equations, and parameters</summary>

### Original §0 · What this lesson teaches

- Three elements of `meep.adjoint`: `MaterialGrid` variables, a `DesignRegion`, and an `OptimizationProblem` connecting an `EigenmodeCoefficient` objective.
- What forward and adjoint fields represent, and why their overlap contributes to the gradient.
- A gradient gate: compare a central difference along the gradient with g·v, and understand failures from random directions and boundary points.
- Take one manual step before using an optimizer. Large step sizes violate the linear approximation.
- The meaning and limits of five MMA evaluations. Gray pixels are not physical binary materials.
- Contract 4: remeasure order powers in a fresh simulation instead of reporting only the optimizer’s internal FOM.

**Prerequisites**: chapter 07’s library and supercell, and chapter 06’s `DiffractedPlanewave`. **Official documentation**: [Adjoint Solver tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Adjoint_Solver/), [adjoint example 01](https://github.com/NanoComp/meep/blob/master/python/examples/adjoint_optimization/01-Introduction.ipynb). **Previous**: [07 · Metalens meta-atoms and phase libraries]({{ '/en/meta-atom/' | relative_url }}) · **Next**: [09 · Waveguide bend inverse design]({{ '/en/bend-inverse/' | relative_url }})


### Original §1 · The question

The four-step design in chapter 07 sent 51% into +1, 63% of the ideal 0.81 limit. One limitation is the library assumption that every neighbor is identical. How much performance can be recovered by freeing all 73 pixel densities? More important than the answer is the procedure for checking whether it is trustworthy: an adjoint optimizer can silently converge in the wrong direction with an incorrect gradient.

### Applications

Metagratings are used for LiDAR beam steering and large-angle diffraction. Adjoint inverse design improves performance beyond a local library design.

| Application | What this lesson provides | Next step |
|---|---|---|
| LiDAR, beam steering, large-angle diffraction | Maximize +1 efficiency with a nonlocal design accounting for neighbors | — |
| Introduction to topology optimization | Four-step adjoint contract | Chapters 09, 32–36 |
| Metasurface verification before fabrication | Fresh-run verification and grayscale limitations | Chapter 32: filters and projection |



### Original §2 · Physics on one page



The objective J = &#124;a₊₁&#124;²/P_in depends on 73 densities ρ. Central finite differences for all ∂J/∂ρ_i require 146 simulations; the adjoint method uses two. The original source produces forward field E_f; an objective-derived source at the monitor produces adjoint field E_a. Their overlap, combined with material dependence and the objective’s normalization, yields each pixel’s gradient. Sensitivity is large where the light’s path overlaps regions important to the objective.

$$
\frac{\partial J}{\partial \rho_i}\;\propto\;\mathrm{Re}\big(E_f\cdot E_a\big)\Big\lvert _{\text{pixel } i},\qquad
\text{gate: }\;\frac{\lvert \,g\cdot v - \mathrm{FD}_v\,\lvert }{\lvert \mathrm{FD}_v\lvert }\le 0.2,\quad v=\frac{g}{\lvert g\lvert },\quad
\mathrm{FD}_v=\frac{J(x+sv)-J(x-sv)}{2s}
$$

Follow two rules for the gate. First, use the gradient direction v. In N dimensions, a typical random-direction projection is smaller by roughly 1/√N, making a small directional derivative sensitive to relative error. Second, use an interior point away from ρ = 0, 1. At a binary design, clipping x ± sv removes one side of the central difference for each variable and can yield exactly half the adjoint value. That is a flawed finite-difference comparison, not an adjoint error.

| Symbol | Meaning | Code variable |
|------|----|-----------|
| ρ (73 values) | Design density: 0 air, 1 Si, intermediate grayscale | `x_baseline`, `x_optimized` |
| J | +1 efficiency = \|a₊₁\|²/P_in | `fom(x)` |
| g | adjoint gradient ∂J/∂ρ | `g_baseline` |
| v, s | Gate direction (g/\|g\|), finite-difference step | `v`, `steps` |
| α | Manual step size | `one_step` |
| k_diff | +1 plane-wave direction (1/Λ, √(f² − 1/Λ²)) | `kdiff` |

**Assumptions and validity**: 2D Ez, a 1D design region (one pixel through the entire ridge height), one frequency, and no boundary averaging with `eps_averaging=False`. There are no fabrication constraints such as minimum feature size or binarization.

### Make predictions before seeing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| Gate relative error | Within 1% | 2 × 10⁻⁶ in the 10_sources adjoint tutorial reproduction |
| Largest gradient | Ridge edges | Moving boundaries has the greatest effect |
| Manual step | Rises, then falls as α grows | Limit of the linear approximation |
| Five MMA evaluations | From 0.497 toward 0.6, possibly dropping in between | MMA can make a large trial move and recover |
| Independent verification versus optimizer FOM | A difference around the second decimal | Same MaterialGrid (73 px) and decomposition monitor, but different stopping conditions |
| Gray pixels | Several dozen | Five evaluations without binarization |

**Acceptance criteria**: HOLD if gate relative error exceeds 20%; do not interpret optimization afterward. An order sum different from total flux indicates decomposition error.


### Original §3 · Simulation setup

<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/01_layout.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/01_layout.png' | relative_url }}" alt="Chapter 07 supercell with ridges replaced by a 1D MaterialGrid design region, width 1.8 µm, height 0.9 µm, and 73 pixels, initialized from the four library ridges" loading="lazy"></a>
<figcaption markdown="span">The cell matches chapter 07’s supercell. Ridges become a 1D `MaterialGrid` design region (width 1.8 µm, height 0.9 µm, 73 pixels), initialized from the four library ridges. Red horizontal line: plane-wave source in substrate; blue line: objective monitor (+1 amplitude); green hatching: y PML. The x boundaries are periodic. Circled numbers match §4.</figcaption>
</figure>


| Parameter | Value | Why this value | Effect of a change |
|----------|-----|-------------|--------|
| Cell, period, height, resolution | Same as chapter 07 (1.8 × 4.9 µm, res 40) | Needed to reuse the library design as the baseline | Any change alters the chapter-07 baseline |
| `Nx` | 73 (25 nm pixels) | Cell width × res + 1 | More variables become finer than the simulation grid |
| `decay_by` | 1e-6 | Adjoint stopping condition; loose tolerance can corrupt only the adjoint (10_sources fdcheck) | At 1e-4, the adjoint gradient is wrong by 81% |
| Gate steps | 2e-3, 5e-3, 1e-2 | Balance truncation and roundoff errors | At 1e-6, roundoff rises |
| `maxeval` | 5 | Teaching smoke test | Convergence needs tens of evaluations plus binarization |
| Manual step α | 0.05, 0.3, 0.8, 2.0 | Includes the turnover near 0.8 | — |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/00_source.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/00_source.png' | relative_url }}" alt="Source waveform and spectrum as in chapter 07. A bare-substrate run gives 0.0000 rad of x-dependent phase variation at the monitor, confirming normal incidence." loading="lazy"></a>
<figcaption markdown="span">Source waveform and spectrum match chapter 07. In a bare-substrate run, phase variation along x at monitor height is 0.0000 rad, confirming normal incidence.</figcaption>
</figure>


**Difference from the lecture notebook**: none. The four-step contract, parameters, and numbers (gate 0.0068/0.0012/0.0006, MMA 0.497 → 0.624, verification 0.496 → 0.623) match week 9. Section §6 adds four gate-failure mechanisms from the two 10_sources fdcheck notes.

</details>

<details markdown="1">
<summary>Walk through the original code</summary>

### Original §4 · Code walkthrough

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → run and stop → postprocessing.
> Here step ⑤ is the objective; steps ⑥ and ⑦ expand into forward, adjoint, gate, MMA, and verification.

### ① Units and parameters — which numbers stay fixed

```python
wl, fcen, fwidth = 1.55, 1 / 1.55, 0.1 / 1.55
N_SEC, LA = 4, 0.45; LAMBDA = N_SEC * LA; H = 0.9; RES = 40
W_LIB = np.array([0.075, 0.100, 0.175, 0.225])          # post-07 design (read from assets/07/result.json)
Nx, Ny = int(round(RES * LAMBDA)) + 1, 1                  # 73 x 1 design pixels
x_grid = np.linspace(-0.5 * LAMBDA, 0.5 * LAMBDA, Nx)
x_baseline = np.zeros(Nx)
for j, w in enumerate(W_LIB):
    xj = -0.5 * LAMBDA + (j + 0.5) * LA
    x_baseline[np.abs(x_grid - xj) <= 0.5 * w] = 1.0    # the four bars, as 0/1 densities
```

- **What**: retain chapter 07’s parameters and map its library design onto 73 binary densities.
- **Why**: starting from an already useful design asks how much adjoint optimization can recover. A random grayscale design starts at +1 efficiency 0.018 (§5).
- **If wrong**: mismatching 25 nm pixel widths with library widths (0.075 = 3 px) changes the baseline geometry.

### ② Materials and geometry — what goes where

```python
design_variables = mp.MaterialGrid(mp.Vector3(Nx, Ny), mp.air, Si, grid_type="U_MEAN", do_averaging=False)   # contract 1
design_region = mpa.DesignRegion(design_variables,
                                 volume=mp.Volume(center=mp.Vector3(0, Y_DEV + 0.5 * H), size=mp.Vector3(LAMBDA, H)))
geometry = [mp.Block(..., material=SiO2),                                   # substrate
            mp.Block(center=design_region.center, size=design_region.size, material=design_variables)]
sim = mp.Simulation(geometry=geometry, eps_averaging=False, **common)
```

- **What**: replace ridges with a density grid. `MaterialGrid` gives air at ρ = 0, Si at 1, and linearly interpolated permittivity in between.
- **Why**: permittivity must vary smoothly with ρ to differentiate it. `do_averaging=False` and `eps_averaging=False` form contract 1.
- **If wrong**: leaving `eps_averaging=True` averages boundary permittivity and can mismatch the assumed gradient and actual geometry in this setup.

### ③ Source — how light enters

```python
sources = [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=mp.Vector3(0, SRC_Y), size=mp.Vector3(LAMBDA, 0))]
adjoint_sources = opt.adjoint_sources[0]      # what opt actually fired for the adjoint run (an EigenModeSource at the monitor)
```

- **What**: the forward source is chapter 07’s plane wave. `OptimizationProblem` automatically constructs the adjoint source at the objective monitor.
- **Why**: objective derivatives determine the adjoint source amplitude and profile. Inspect what `opt` computes rather than choosing them manually.
- **If wrong**: a phase that varies with x at the monitor in the bare-substrate run means the source is tilted, invalidating the intended normal-incidence +1-efficiency setup.

### ④ Simulation and boundaries — the cell and PML

```python
common = dict(resolution=RES, cell_size=mp.Vector3(LAMBDA, SY), sources=sources,
              boundary_layers=[mp.PML(thickness=DPML, direction=mp.Y)], k_point=mp.Vector3())
```

- **What**: the same supercell as chapter 07: periodic x boundaries and y PML.
- **Why**: forward, adjoint, finite-difference, and verification runs must share a cell for meaningful comparison.
- **If wrong**: different verification cells make it unclear whether a FOM discrepancy comes from the design or cell settings.

### ⑤ Monitor — the objective

```python
kdiff = mp.Vector3(1 / LAMBDA, np.sqrt(fcen ** 2 - (1 / LAMBDA) ** 2))          # +1 order direction
emc = mpa.EigenmodeCoefficient(sim, mp.Volume(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0)), mode=1,
                               eig_parity=mp.ODD_Z, kpoint_func=lambda *_: kdiff,
                               eig_vol=mp.Volume(center=mp.Vector3(0, MON_Y), size=mp.Vector3(1 / RES, 0, 0)))
opt = mpa.OptimizationProblem(simulation=sim, objective_functions=lambda e: npa.abs(e[0]) ** 2,
                              objective_arguments=[emc], design_regions=[design_region], fcen=fcen, df=0, nf=1, decay_by=1e-6)
```

- **What**: use the +1 plane-wave amplitude a₊₁ on the monitor line as the objective argument, and &#124;a₊₁&#124;² as the objective before incident-power normalization.
- **Why**: `kpoint_func` specifies +1 direction, and a one-pixel `eig_vol` identifies the plane-wave mode (corresponding to chapter 06’s `DiffractedPlanewave`). Use `npa`, autograd’s NumPy, so the objective itself is differentiable.
- **If wrong**: missing `eig_parity` mixes polarizations. Relaxing `decay_by` to 1e-4 can leave forward and finite-difference results apparently correct while the adjoint gradient is wrong by 81% (10_sources fdcheck E4).

### ⑥ Run — forward, adjoint, gate, one step, and MMA

```python
f, dJ = opt([x], need_gradient=True)            # forward + adjoint: J and dJ/drho for all 73 pixels

x_gate = np.clip(x_baseline, 0.02, 0.98)         # interior point, away from 0/1
v = g_gate / np.linalg.norm(g_gate)              # gradient direction
fd = (fom(x_gate + s * v) - fom(x_gate - s * v)) / (2 * s)
ok = abs(g_gate @ v - fd) / abs(fd) <= 0.20

x_try = np.clip(x_baseline + alpha * g / np.linalg.norm(g), 0, 1)    # one step by hand

solver = nlopt.opt(nlopt.LD_MMA, Nx); solver.set_lower_bounds(0); solver.set_upper_bounds(1)
solver.set_max_objective(nlopt_objective); solver.set_maxeval(5)
```

- **What**: one derivative-enabled `opt(...)` call runs forward and adjoint calculations. The gate uses central differences at three steps, followed by a manual step and five MMA evaluations.
- **Why**: the sequence is the contract. Do not use a gradient that fails the gate. A manual step checks whether following the gradient actually improves J, and over what distance.
- **If wrong**: gating the binary baseline directly can yield half the adjoint value because of clipping, producing HOLD. A random direction can have a projection suppressed by 1/√73, inflating relative error.

### ⑦ Postprocessing — contract 4, independent verification

```python
def forward_orders(weights):
    s = mp.Simulation(geometry=geometry_with(weights), eps_averaging=False, **common)   # a NEW simulation
    mon = s.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0)))
    s.run(until_after_sources=stop_cond)
    eff = {m: abs(s.get_eigenmode_coefficients(mon, mp.DiffractedPlanewave((m, 0, 0), mp.Vector3(1, 0, 0), 1, 0)).alpha[0, 0, 0]) ** 2 / input_flux
           for m in (-1, 0, 1)}
    return eff, mp.get_fluxes(mon)[0] / input_flux
```

- **What**: put the selected design in a fresh `Simulation` and remeasure all three orders as in chapter 06. Check order sum = total flux too.
- **Why**: an optimizer FOM depends on its stopping condition and monitor configuration. Report an independent-run measurement.
- **If wrong**: directly quoting optimizer FOM 0.624 differs slightly from verification 0.623. The gap is small here but can grow under other conditions.

> **Pitfall**: the variables here are densities along x without a filter/projection mapping. Adding a mapping requires its chain rule. Omitting it can reverse the direction, giving a gate cosine of −0.45 (10_sources fdcheck E5).

</details>

<details markdown="1">
<summary>Original results, verification tables, diagnostics, and further experiments</summary>

### Original §5 · Results

<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/02_fields.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/02_fields.png' | relative_url }}" alt="Library-baseline forward field, random-grayscale forward field with J = 0.018, and the adjoint field launched downward from the monitor" loading="lazy"></a>
<figcaption markdown="span">Left: library-baseline forward field, with wavefronts tilting right as they rise (+1). Center: random grayscale start, with distorted wavefronts and J = 0.018. Right: the adjoint wave traveling down from the monitor. Compare spatial locations, not absolute amplitudes.</figcaption>
</figure>


<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/03_gradient.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/03_gradient.png' | relative_url }}" alt="Raw baseline gradient: red positive and blue negative, with the five largest magnitudes near the edges of the second ridge at x = −0.275~−0.175" loading="lazy"></a>
<figcaption markdown="span">Raw gradient at the baseline. Red means raising density increases J locally; blue means the opposite. The five largest magnitudes cluster at the second ridge edges (x = −0.275~−0.175), suggesting that widening it is beneficial locally.</figcaption>
</figure>


<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/04_gate.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/04_gate.png' | relative_url }}" alt="Gradient gate: finite differences and adjoint agree within 1% at all three steps, PASS" loading="lazy"></a>
<figcaption markdown="span">Gradient gate: all three steps give agreement within 1% between finite differences and adjoint. PASS.</figcaption>
</figure>


| Step | FD | Adjoint g·v | Relative error |
|---|---|---|---|
| 2e-3 | 0.5410 | 0.5447 | 0.0068 |
| 5e-3 | 0.5454 | 0.5447 | 0.0012 |
| 1e-2 | 0.5451 | 0.5447 | 0.0006 |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/05_step_mma.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/05_step_mma.png' | relative_url }}" alt="Manual alpha sweep and MMA history: the manual step peaks near 0.8 and falls at 2.0; MMA evaluation 3 is best at 0.624" loading="lazy"></a>
<figcaption markdown="span">Top: one manual step (α sweep) and MMA history. J rises through α = 0.8 and falls at 2.0. Bottom: five MMA designs. Evaluation 3 reaches 0.624, evaluation 4 drops to 0.049, and evaluation 5 recovers to 0.540. Keep the best design from evaluation 3.</figcaption>
</figure>


| α | J | ΔJ |
|---|---|---|
| 0.05 | 0.5075 | +0.011 |
| 0.3 | 0.5549 | +0.058 |
| 0.8 | 0.6134 | +0.116 |
| 2.0 | 0.4840 | −0.013 |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/08/06_verify.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/08/06_verify.png' | relative_url }}" alt="Contract 4: fresh-run order efficiencies at left and Re(Ez) of baseline and optimized designs at center and right; red dashed line is the four-step blazed limit" loading="lazy"></a>
<figcaption markdown="span">Contract 4: order efficiencies measured in a fresh simulation (left), and baseline/optimized Re(Ez) (center/right). Red dashed line: four-step blazed limit.</figcaption>
</figure>


| Design | m = −1 | m = 0 | m = +1 | Order sum | Total transmission | +1 / limit |
|---|---|---|---|---|---|---|
| Baseline (chapter-07 library) | 0.1026 | 0.0666 | 0.4959 | 0.6651 | 0.6651 | 61.2% |
| optimized (MMA eval 3) | 0.0973 | 0.0169 | 0.6228 | 0.7369 | 0.7369 | 76.8% |


### Compare against the predictions

| Quantity | Prediction (§2) | Simulation | Verdict |
|--------|-------------|-----------|------|
| Gate relative error | Within 1% | 0.7%, 0.1%, 0.06% | ✅ |
| Largest gradient | Ridge edges | Both edges of the second ridge | ✅ |
| Manual step | Rises, then falls | Maximum at 0.8; falls at 2.0 | ✅ |
| Five MMA evaluations | Near 0.6, with an intermediate drop | 0.624; evaluation 4: 0.049 | ✅ |
| Verification versus optimizer | Difference around the second decimal | 0.6228 vs 0.6241 | ✅ |
| Grayscale | Several dozen | 27 / 73 | ✅ |

Two numerical observations support the predictions. Pixel freedom improves the fraction of the ideal reference from 61% → 77%, recovering nearly half the remaining gap associated with the library-design limitations. Most improvement reduces order-0 leakage (0.067 → 0.017); order −1 remains nearly unchanged. Five evaluations did not remove the staircase pattern’s opposite-order leakage.

### Convergence

Convergence here concerns the gate’s three step sizes, not spatial resolution. Changing step size fivefold leaves FD stable at 0.541–0.545 and within 1% of the adjoint. The library’s resolution sensitivity from chapter 07 (0.82 rad phase variation) still matters; a res-60 run would change even the baseline efficiency.

### What the results do and do not establish

- Supported: for this cell and resolution, adjoint gradients agree with finite differences within 1%. Five MMA evaluations improve the library baseline’s +1 efficiency from 0.50 to 0.62, confirmed in a fresh run.
- Not established: a converged optimum. maxeval 5 is not convergence. With 27 of 73 gray densities and no minimum-feature constraint, the pattern is not a physical binary device; binarization will change efficiency. Other resolutions, wavelengths, and polarizations are untested.


### Original §6 · Common mistakes

| Symptom | Cause | Fix |
|------|------|----------|
| Gate FD equals exactly half the adjoint | Clipped central differences at binary bounds | Use an interior point (0.02–0.98) |
| Gate relative error is tens of percent | Random direction | Use gradient direction v = g/\|g\| |
| Only the adjoint fails the gate | Loose `decay_by` | Use 1e-6 or stricter |
| Negative gate cosine | Missing chain rule for filter/projection mapping | Multiply by the mapping Jacobian with the appropriate chain rule |
| Optimizer FOM differs from verification | Runs use different conditions | Report the fresh-run measurement |
| MMA drops during optimization | An overly large trial step | Retain the best evaluation; decreases can occur |
| Treating grayscale as a device | No binarization or feature-size constraints | Later chapters: filters, projection, and β schedules |


### Original §7 · Try it yourself

| Change | Expected effect | Measurement to inspect |
|---------|----------|------------|
| Uniform 0.5 initialization | No grating: degenerate +1 efficiency of 0; inspect the gradient | g, gate |
| `maxeval` 5 → 30 | Find where efficiency plateaus | history |
| Objective \|a₊₁\|² − \|a₋₁\|² | Test whether −1 leakage decreases | Verification table |
| Gate `decay_by` 1e-6 → 1e-4 | Reproduce failure in the adjoint alone | Relative error |

</details>

<details>
<summary>metagrating_inverse.py (expand to view)</summary>
{% highlight python %}
"""Meep Example 08 - Metagrating inverse design (adjoint), with a four-step contract.

Start from the post-07 library design (four Si bars). Open the whole supercell period as a 1D design
region (73 pixels of density 0..1) and let the adjoint gradient move it. Every step is looked at:
  1. differentiability: eps_averaging=False, MaterialGrid do_averaging=False
  2. gradient gate: adjoint gradient vs centred finite differences along the gradient direction
  3. a short MMA run (maxeval 5): a smoke test, not a converged design
  4. verification in a FRESH simulation with DiffractedPlanewave, order by order
Plus: forward field of baseline and of a random start, adjoint field, raw gradient, one manual step.

Run:  python metagrating_inverse.py      (~1.5 min on one core)
Out:  00_source.png, 01_layout.png, 02_fields.png, 03_gradient.png, 04_gate.png, 05_step_mma.png,
      06_verify.png, 07_anim_optimized.gif, result.json   (-> ../assets/08/)
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
import meep.adjoint as mpa
import nlopt
from autograd import numpy as npa

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "08")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()
np.random.seed(20260815)

# ---------------------------------------------------------------- (1) units & parameters: identical to post 07
wl = 1.55
fcen = 1 / wl
fwidth = 0.1 * fcen
Si, SiO2 = mp.Medium(index=3.45), mp.Medium(index=1.45)
N_SEC, LA = 4, 0.45
LAMBDA = N_SEC * LA
THETA_D = float(np.degrees(np.arcsin(wl / LAMBDA)))
H = 0.9
RES = 40
DPML, DSUB, DAIR = 1.0, 1.0, 1.0
SY = DPML + DSUB + H + DAIR + DPML
Y_BOT = -0.5 * SY
Y_DEV = Y_BOT + DPML + DSUB
SRC_Y = Y_BOT + DPML + 0.3
MON_Y = -Y_BOT - DPML - 0.3
BLAZED_BOUND = (np.sin(np.pi / N_SEC) / (np.pi / N_SEC)) ** 2
EXTENT = [-0.5 * LAMBDA, 0.5 * LAMBDA, Y_BOT, -Y_BOT]

# baseline widths: post-07 library design (read from its result.json if present)
try:
    with open(os.path.join(HERE, "..", "assets", "07", "result.json")) as f:
        W_LIB = np.array(json.load(f)["design"]["widths"])
except Exception:
    W_LIB = np.array([0.075, 0.100, 0.175, 0.225])

sources = [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=mp.Vector3(0, SRC_Y), size=mp.Vector3(LAMBDA, 0))]
common = dict(resolution=RES, cell_size=mp.Vector3(LAMBDA, SY), sources=sources,
              boundary_layers=[mp.PML(thickness=DPML, direction=mp.Y)], k_point=mp.Vector3())
stop_cond = mp.stop_when_fields_decayed(10, mp.Ez, mp.Vector3(0, MON_Y), 1e-7)

# ---------------------------------------------------------------- (2) geometry: substrate + a 1D MaterialGrid design region
Nx, Ny = int(round(RES * LAMBDA)) + 1, 1
x_grid = np.linspace(-0.5 * LAMBDA, 0.5 * LAMBDA, Nx)
design_variables = mp.MaterialGrid(mp.Vector3(Nx, Ny), mp.air, Si, grid_type="U_MEAN", do_averaging=False)   # contract 1
design_region = mpa.DesignRegion(design_variables, volume=mp.Volume(center=mp.Vector3(0, Y_DEV + 0.5 * H), size=mp.Vector3(LAMBDA, H)))
x_baseline = np.zeros(Nx)
for j, w in enumerate(W_LIB):
    xj = -0.5 * LAMBDA + (j + 0.5) * LA
    x_baseline[np.abs(x_grid - xj) <= 0.5 * w] = 1.0


def geometry_with(weights):
    grid = mp.MaterialGrid(mp.Vector3(Nx, Ny), mp.air, Si, weights=np.asarray(weights).reshape(Nx, Ny), grid_type="U_MEAN", do_averaging=False)
    return [mp.Block(center=mp.Vector3(0, Y_BOT + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2),
            mp.Block(center=design_region.center, size=design_region.size, material=grid)]


geometry = [mp.Block(center=mp.Vector3(0, Y_BOT + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2),
            mp.Block(center=design_region.center, size=design_region.size, material=design_variables)]

# ---------------------------------------------------------------- (4) simulation + (5) objective: +1 order amplitude
sim = mp.Simulation(geometry=geometry, eps_averaging=False, **common)
kdiff = mp.Vector3(1 / LAMBDA, np.sqrt(fcen ** 2 - (1 / LAMBDA) ** 2))      # +1 order direction
emc = mpa.EigenmodeCoefficient(sim, mp.Volume(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0)), mode=1,
                               eig_parity=mp.ODD_Z, kpoint_func=lambda *_: kdiff,
                               eig_vol=mp.Volume(center=mp.Vector3(0, MON_Y), size=mp.Vector3(1 / RES, 0, 0)))
opt = mpa.OptimizationProblem(simulation=sim, objective_functions=lambda e: npa.abs(e[0]) ** 2, objective_arguments=[emc],
                              design_regions=[design_region], fcen=fcen, df=0, nf=1, decay_by=1e-6)
opt.update_design([x_baseline])
annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(5.2, 7.0), axis_step=0.5,
    title="supercell: 1D design region (73 px) replaces the bars",
    params_text=f"wl={wl} res={RES}\nLambda={LAMBDA} H={H}\nNx={Nx} (25 nm px)",
    params_xy=(-0.85, 2.35), pml_xy=(-0.5, Y_BOT + 0.5 * DPML), decay_point=(0, MON_Y), decay_text_xy=(-0.1, 1.75),
    labels=[Label("design region: MaterialGrid, baseline = library bars", (-0.3, Y_DEV + 0.5 * H), (-0.85, 1.25), step=2, color="black"),
            Label("plane wave in SiO2", (0.3, SRC_Y), (-0.85, SRC_Y - 0.35), step=3, color="red"),
            Label("objective: |a_+1|^2 on this line", (0.5, MON_Y), (-0.85, MON_Y + 0.35), step=5, color="blue")])
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")


def run_dft_field(src_list, geometry_list):
    s = mp.Simulation(geometry=geometry_list, eps_averaging=False, **dict(common, sources=src_list))
    dft = s.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(LAMBDA, SY))
    s.run(until_after_sources=stop_cond)
    field = s.get_dft_array(dft, mp.Ez, 0); eps = s.get_epsilon(); s.reset_meep()
    return field, eps


# ---------------------------------------------------------------- source check + input flux (empty substrate)
sim_ref = mp.Simulation(default_material=SiO2, **common)
fl = sim_ref.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0)))
dft_ref = sim_ref.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(LAMBDA, SY))
sim_ref.run(until_after_sources=stop_cond)
input_flux = float(mp.get_fluxes(fl)[0])
field_ref = sim_ref.get_dft_array(dft_ref, mp.Ez, 0)
sim_ref.reset_meep()
row = field_ref[:, field_ref.shape[1] // 2]
phase_spread = float(np.ptp(np.unwrap(np.angle(row))))
print(f"source check: input_flux = {input_flux:.5e}, phase spread across x at mid-height = {phase_spread:.4f} rad ({'normal incidence' if phase_spread < 0.2 else 'TILTED'})")


def fom(x, need_gradient=False):
    """+1 order efficiency = |a_+1|^2 / input_flux (and its gradient w.r.t. the 73 densities)."""
    f, dJ = opt([np.clip(x, 0, 1)], need_gradient=need_gradient)
    f = float(np.real(np.asarray(f).squeeze())) / input_flux
    if not need_gradient:
        return f
    return f, np.squeeze(np.asarray(dJ)) / input_flux


# ---------------------------------------------------------------- forward fields: baseline vs random start; adjoint field
field_fwd, eps_fwd = run_dft_field(sources, geometry_with(x_baseline))
f_baseline, g_baseline = fom(x_baseline, need_gradient=True)
x_random = np.random.rand(Nx)
field_rand, eps_rand = run_dft_field(sources, geometry_with(x_random))
f_random = fom(x_random)
adjoint_sources = opt.adjoint_sources[0]
field_adj, eps_adj = run_dft_field(adjoint_sources, geometry_with(x_baseline))
print(f"forward: baseline +1 efficiency = {f_baseline:.4f} (|grad| = {np.linalg.norm(g_baseline):.3e}); random grayscale start = {f_random:.4f}; "
      f"adjoint sources: {len(adjoint_sources)} x {type(adjoint_sources[0]).__name__}")

xs = np.linspace(EXTENT[0], EXTENT[1], eps_fwd.shape[0]); ys = np.linspace(EXTENT[2], EXTENT[3], eps_fwd.shape[1])
fig, ax = plt.subplots(2, 3, figsize=(10.5, 7.2))
lim = max(np.max(np.abs(field_fwd)), np.max(np.abs(field_rand)))
for col, (fld, eps, ttl) in enumerate(((field_fwd, eps_fwd, f"forward, baseline (library bars)  J = {f_baseline:.3f}"),
                                       (field_rand, eps_rand, f"forward, random grayscale start  J = {f_random:.3f}"),
                                       (field_adj, eps_adj, "adjoint: source placed at the objective monitor"))):
    l = lim if col < 2 else float(np.max(np.abs(fld)))
    ax[0, col].imshow(np.real(fld).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-l, vmax=l, aspect="equal")
    ax[1, col].imshow(np.abs(fld).T, extent=EXTENT, origin="lower", cmap="inferno", aspect="equal")
    for a in ax[:, col]:
        a.contour(xs, ys, eps.T, levels=[1.5, 6.0], colors="w", linewidths=0.6); a.set_xlabel("x [um]")
    ax[0, col].set_title(ttl, fontsize=8.5)
ax[0, 0].set_ylabel("Re(Ez)  y [um]"); ax[1, 0].set_ylabel("|Ez|  y [um]")
fig.suptitle("the field follows the design; the adjoint field flows from the monitor back down", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_fields.png"), dpi=150); plt.close(fig)

# ---------------------------------------------------------------- raw gradient
fig, ax = plt.subplots(2, 1, figsize=(9, 4.8), sharex=True)
ax[0].plot(x_grid, g_baseline, lw=1.2, color="tab:purple"); ax[0].axhline(0, color="k", lw=0.7)
ax[0].fill_between(x_grid, 0, g_baseline, where=g_baseline > 0, color="tab:red", alpha=0.25, label="increase density here")
ax[0].fill_between(x_grid, 0, g_baseline, where=g_baseline < 0, color="tab:blue", alpha=0.25, label="decrease density here")
ax[0].set_ylabel("dJ / d(density)"); ax[0].set_title("raw adjoint gradient at the baseline (no filtering)", fontsize=9); ax[0].legend(fontsize=8, loc="upper right")
ax[1].step(x_grid, x_baseline, where="mid", color="tab:gray", lw=1.3); ax[1].fill_between(x_grid, 0, x_baseline, step="mid", color="tab:gray", alpha=0.35)
ax[1].set_ylabel("density (0 = air, 1 = Si)"); ax[1].set_xlabel("x [um]"); ax[1].set_ylim(-0.05, 1.15); ax[1].set_title("current design", fontsize=9)
for a in ax:
    for j in range(1, N_SEC):
        a.axvline(-0.5 * LAMBDA + j * LA, color="k", ls=":", lw=0.8)
    a.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_gradient.png"), dpi=150); plt.close(fig)
top = sorted(np.argsort(np.abs(g_baseline))[::-1][:5])
print("gradient: largest 5 |dJ/drho| at x = " + ", ".join(f"{x_grid[i]:+.3f} ({g_baseline[i]:+.3f}, rho={x_baseline[i]:.0f})" for i in top))

# ---------------------------------------------------------------- contract 2: gradient gate (interior point, gradient direction)
x_gate = np.clip(x_baseline, 0.02, 0.98)
f_gate, g_gate = fom(x_gate, need_gradient=True)
v = g_gate / np.linalg.norm(g_gate)
adjoint_dd = float(np.dot(g_gate, v))
steps = [2e-3, 5e-3, 1e-2]
gate_rows = []
for step in steps:
    fd = (fom(x_gate + step * v) - fom(x_gate - step * v)) / (2 * step)
    rel = abs(adjoint_dd - fd) / max(abs(fd), 1e-30)
    gate_rows.append({"step": step, "fd": fd, "adjoint": adjoint_dd, "rel_err": rel, "pass": bool(rel <= 0.20 and np.sign(fd) == np.sign(adjoint_dd))})
gradient_gate = all(r["pass"] for r in gate_rows)
print(f"gate: interior-point FOM = {f_gate:.4f}; " + "; ".join(f"step {r['step']:.0e}: FD {r['fd']:.4e} vs adjoint {r['adjoint']:.4e}, rel {r['rel_err']:.4f} {'PASS' if r['pass'] else 'HOLD'}" for r in gate_rows)
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
fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_gate.png"), dpi=150); plt.close(fig)
if not gradient_gate:
    raise SystemExit("gradient gate HOLD: do not interpret optimizer results")

# ---------------------------------------------------------------- one manual step, then MMA (contract 3)
direction = g_baseline / np.linalg.norm(g_baseline)
one_step = []
for alpha in (0.05, 0.3, 0.8, 2.0):
    x_try = np.clip(x_baseline + alpha * direction, 0, 1)
    one_step.append((alpha, x_try, fom(x_try)))
print("one manual step: " + ", ".join(f"alpha {a} -> {f:.4f} ({f - f_baseline:+.4f})" for a, _, f in one_step))

history, design_history = [], []


def nlopt_objective(x, grad):
    f, dJ = fom(x, need_gradient=True)
    if grad.size > 0:
        grad[:] = dJ
    history.append(f); design_history.append(np.array(x, copy=True))
    return f


solver = nlopt.opt(nlopt.LD_MMA, Nx)
solver.set_lower_bounds(np.zeros(Nx)); solver.set_upper_bounds(np.ones(Nx))
solver.set_max_objective(nlopt_objective); solver.set_maxeval(5)
x_optimized = np.clip(solver.optimize(x_baseline.copy()), 0, 1)
best_k = int(np.argmax(history))
x_optimized = design_history[best_k]                         # keep the best evaluated design (MMA may overshoot)
gray = int(np.sum((x_optimized > 0.02) & (x_optimized < 0.98)))
print("MMA (maxeval 5): " + ", ".join(f"eval {k+1}: {f:.4f}" for k, f in enumerate(history)) + f"; best eval {best_k+1} = {max(history):.4f} ({max(history)/history[0]:.3f}x); grayscale pixels {gray}/{Nx}")

fig = plt.figure(figsize=(14, 6.2))
gs = fig.add_gridspec(2, 6, height_ratios=[1, 1])
axs = [fig.add_subplot(gs[0, k]) for k in range(5)]
axs[0].step(x_grid, x_baseline, where="mid", color="tab:gray", lw=1.1); axs[0].fill_between(x_grid, 0, x_baseline, step="mid", color="tab:gray", alpha=0.4)
axs[0].set_title(f"baseline\nJ = {f_baseline:.4f}", fontsize=8); axs[0].set_ylabel("density")
for a, (alpha, x_try, f_try) in zip(axs[1:], one_step):
    a.step(x_grid, x_try, where="mid", color="tab:green", lw=1.1); a.fill_between(x_grid, 0, x_try, step="mid", color="tab:green", alpha=0.4)
    a.set_title(f"one step, alpha = {alpha}\nJ = {f_try:.4f}", fontsize=8)
for a in axs:
    a.set_ylim(-0.05, 1.08); a.set_xlabel("x [um]"); a.grid(alpha=0.3)
axh = fig.add_subplot(gs[0, 5])
axh.plot(range(1, len(history) + 1), history, "o-", color="tab:blue"); axh.axhline(f_baseline, ls="--", color="gray", lw=1, label="baseline")
axh.set_xticks(range(1, len(history) + 1)); axh.set_xlabel("MMA evaluation"); axh.set_ylabel("+1 efficiency"); axh.set_title("MMA history", fontsize=8); axh.grid(alpha=0.3); axh.legend(fontsize=7)
for k in range(len(design_history)):
    a = fig.add_subplot(gs[1, k])
    a.step(x_grid, design_history[k], where="mid", color="tab:blue", lw=1.0); a.fill_between(x_grid, 0, design_history[k], step="mid", color="tab:blue", alpha=0.4)
    a.set_title(f"MMA eval {k + 1}  J = {history[k]:.4f}" + ("  (kept)" if k == best_k else ""), fontsize=8); a.set_ylim(-0.05, 1.08); a.set_xlabel("x [um]"); a.grid(alpha=0.3)
    if k == 0:
        a.set_ylabel("density")
a = fig.add_subplot(gs[1, 5])
a.step(x_grid, x_baseline, where="mid", color="tab:gray", lw=1.2, label="baseline"); a.step(x_grid, x_optimized, where="mid", color="tab:blue", lw=1.2, label="optimized")
a.fill_between(x_grid, 0, x_optimized, step="mid", color="tab:blue", alpha=0.3); a.set_ylim(-0.05, 1.08); a.set_xlabel("x [um]"); a.set_title(f"final vs baseline ({gray} gray px)", fontsize=8); a.legend(fontsize=7); a.grid(alpha=0.3)
fig.suptitle("top: one manual gradient step (alpha sweep) and the MMA history; bottom: the design at every MMA evaluation", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_step_mma.png"), dpi=150); plt.close(fig)


# ---------------------------------------------------------------- contract 4: verification in a fresh simulation
def forward_orders(weights):
    s = mp.Simulation(geometry=geometry_with(weights), eps_averaging=False, **common)
    mon = s.add_mode_monitor(fcen, 0, 1, mp.ModeRegion(center=mp.Vector3(0, MON_Y), size=mp.Vector3(LAMBDA, 0)))
    dft = s.add_dft_fields([mp.Ez], fcen, 0, 1, center=mp.Vector3(), size=mp.Vector3(LAMBDA, SY))
    s.run(until_after_sources=stop_cond)
    total = float(mp.get_fluxes(mon)[0] / input_flux)
    eff = {m: float(abs(s.get_eigenmode_coefficients(mon, mp.DiffractedPlanewave((m, 0, 0), mp.Vector3(1, 0, 0), 1, 0)).alpha[0, 0, 0]) ** 2 / input_flux) for m in (-1, 0, 1)}
    field = s.get_dft_array(dft, mp.Ez, 0); eps = s.get_epsilon(); s.reset_meep()
    return eff, total, field, eps


report = {}
for tag, weights in (("baseline", x_baseline), ("optimized", x_optimized)):
    eff, total, fld, eps = forward_orders(weights)
    report[tag] = {"orders": eff, "sum": sum(eff.values()), "T_total": total, "field": fld, "eps": eps}
    print(f"verify [{tag}]: m=-1 {eff[-1]:.4f}, m=0 {eff[0]:.4f}, m=+1 {eff[1]:.4f}; sum {sum(eff.values()):.4f} = total {total:.4f}; "
          f"+1 / bound = {eff[1] / BLAZED_BOUND * 100:.1f} %")
fig, ax = plt.subplots(1, 3, figsize=(13, 4.4), gridspec_kw={"width_ratios": [1.4, 1, 1]})
ms = (-1, 0, 1); idx = np.arange(3)
ax[0].bar(idx - 0.2, [report["baseline"]["orders"][m] for m in ms], width=0.4, color="tab:gray", label="baseline (post-07 library)")
ax[0].bar(idx + 0.2, [report["optimized"]["orders"][m] for m in ms], width=0.4, color="tab:blue", label=f"after MMA (eval {best_k + 1})")
ax[0].axhline(BLAZED_BOUND, ls="--", color="crimson", lw=1.2, label=f"4-level blazed bound {BLAZED_BOUND:.3f}")
for k, m in enumerate(ms):
    ax[0].text(k - 0.2, report["baseline"]["orders"][m] + 0.008, f"{report['baseline']['orders'][m]:.3f}", ha="center", fontsize=8)
    ax[0].text(k + 0.2, report["optimized"]["orders"][m] + 0.008, f"{report['optimized']['orders'][m]:.3f}", ha="center", fontsize=8)
ax[0].set_xticks(idx); ax[0].set_xticklabels([f"m = {m:+d}" for m in ms]); ax[0].set_ylim(0, 1.0); ax[0].set_ylabel("efficiency (fresh forward run)")
ax[0].set_title("contract 4: measured again in a new simulation", fontsize=9); ax[0].grid(axis="y", alpha=0.3); ax[0].legend(fontsize=7)
lim = max(np.max(np.abs(report["baseline"]["field"])), np.max(np.abs(report["optimized"]["field"])))
for a, tag in zip(ax[1:], ("baseline", "optimized")):
    fld, eps = report[tag]["field"], report[tag]["eps"]
    a.imshow(np.real(fld).T, extent=EXTENT, origin="lower", cmap="RdBu", vmin=-lim, vmax=lim, aspect="equal")
    a.contour(xs, ys, eps.T, levels=[1.5, 6.0], colors="w", linewidths=0.6); a.set_title(f"Re(Ez), {tag}", fontsize=9); a.set_xlabel("x [um]")
ax[1].set_ylabel("y [um]")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "06_verify.png"), dpi=150); plt.close(fig)

# ---------------------------------------------------------------- GIF: optimized pattern repeated 5 times, short pulse
periods = 5
fw_anim = 0.4 * fcen
aperture = periods * LAMBDA
sx_a = aperture + 2 * 1.0 + 2 * DPML
sy_a = DPML + DSUB + H + 2.5 + DPML
yb = -0.5 * sy_a
ydev = yb + DPML + DSUB
geom_a = [mp.Block(center=mp.Vector3(0, yb + 0.5 * (DPML + DSUB)), size=mp.Vector3(mp.inf, DPML + DSUB), material=SiO2)]
for j in range(periods):
    xj = -0.5 * aperture + (j + 0.5) * LAMBDA
    geom_a.append(mp.Block(center=mp.Vector3(xj, ydev + 0.5 * H), size=mp.Vector3(LAMBDA, H),
                           material=mp.MaterialGrid(mp.Vector3(Nx, Ny), mp.air, Si, weights=x_optimized.reshape(Nx, Ny), grid_type="U_MEAN", do_averaging=False)))
sim_a = mp.Simulation(resolution=RES, cell_size=mp.Vector3(sx_a, sy_a), boundary_layers=[mp.PML(DPML)], geometry=geom_a, eps_averaging=False,
                      sources=[mp.Source(mp.GaussianSource(fcen, fwidth=fw_anim, is_integrated=True), component=mp.Ez,
                                         center=mp.Vector3(0, yb + DPML + 0.3), size=mp.Vector3(aperture, 0))])
sim_a.init_sim()
vol_a = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx_a - 2 * DPML, sy_a - 2 * DPML))
eps_a = sim_a.get_array(vol=vol_a, component=mp.Dielectric)
ext_a = [-(sx_a / 2 - DPML), sx_a / 2 - DPML, -(sy_a / 2 - DPML), sy_a / 2 - DPML]
t_src = 5 / fw_anim
frames, times = record_frames(sim_a, vol_a, mp.Ez, t_start=t_src - 1 / fw_anim, t_end=t_src + 1.2 * sy_a * 1.45, n_frames=60)
animate_fields(frames, times, ext_a, os.path.join(OUT, "07_anim_optimized.gif"), eps=eps_a, figsize=(6.4, 4.6), dpi=70,
               title=f"optimized metagrating x{periods}: wavefront toward +{THETA_D:.0f} deg", legend_loc="lower right")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"params": {"wl": wl, "Lambda": LAMBDA, "H": H, "theta_d": THETA_D, "Nx": Nx, "w_lib": W_LIB.tolist()},
                   "input_flux": input_flux, "phase_spread": phase_spread,
                   "fom": {"baseline": f_baseline, "random": f_random, "gate_point": f_gate},
                   "gate": gate_rows, "gate_pass": gradient_gate,
                   "one_step": [{"alpha": a, "fom": f} for a, _, f in one_step],
                   "mma": {"history": history, "best_eval": best_k + 1, "gray_pixels": gray},
                   "verify": {k: {"orders": v["orders"], "sum": v["sum"], "T_total": v["T_total"]} for k, v in report.items()},
                   "blazed_bound": BLAZED_BOUND, "x_baseline": x_baseline.tolist(), "x_optimized": x_optimized.tolist(),
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__, "nlopt": f"{nlopt.version_major()}.{nlopt.version_minor()}"}, f, indent=2)
{% endhighlight %}
</details>

<details markdown="1">
<summary>Original execution records and reproduction environment</summary>

Unlike the excerpts in §4, the complete code includes figure saving, GIF recording, and result.json output. The shared helper `blogfig.py` is in the same `code/` folder. Full code and helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**Execution results (run on 2026-10-23)**:
```
source check: input_flux = 1.86866e+01, phase spread across x at mid-height = 0.0000 rad (normal incidence)
forward: baseline +1 efficiency = 0.4970 (|grad| = 6.037e-01); random grayscale start = 0.0177; adjoint sources: 1 x EigenModeSource
gradient: largest 5 |dJ/drho| at x = -0.275 (+0.157, rho=0), -0.250 (+0.208, rho=1), -0.225 (+0.232, rho=1), -0.200 (+0.215, rho=1), -0.175 (+0.165, rho=0)
gate: interior-point FOM = 0.4871; step 2e-03: FD 5.4104e-01 vs adjoint 5.4472e-01, rel 0.0068 PASS; step 5e-03: FD 5.4538e-01 vs adjoint 5.4472e-01, rel 0.0012 PASS; step 1e-02: FD 5.4505e-01 vs adjoint 5.4472e-01, rel 0.0006 PASS -> gradient gate PASS
one manual step: alpha 0.05 -> 0.5075 (+0.0105), alpha 0.3 -> 0.5549 (+0.0579), alpha 0.8 -> 0.6134 (+0.1163), alpha 2.0 -> 0.4840 (-0.0130)
MMA (maxeval 5): eval 1: 0.4970, eval 2: 0.5248, eval 3: 0.6241, eval 4: 0.0492, eval 5: 0.5398; best eval 3 = 0.6241 (1.256x); grayscale pixels 27/73
verify [baseline]: m=-1 0.1026, m=0 0.0666, m=+1 0.4959; sum 0.6651 = total 0.6651; +1 / bound = 61.2 %
verify [optimized]: m=-1 0.0973, m=0 0.0169, m=+1 0.6228; sum 0.7369 = total 0.7369; +1 / bound = 76.8 %
```

**Reproduction environment**: meep 1.33.0 · nlopt 2.x · autograd · Python 3.11 · `conda install -c conda-forge pymeep nlopt autograd` · run `python metagrating_inverse.py` (about 48 s, single core)

</details>

### Official documentation and next lesson

- [Official Adjoint Solver tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Adjoint_Solver/) · [Adjoint example 01 Introduction](https://github.com/NanoComp/meep/blob/master/python/examples/adjoint_optimization/01-Introduction.ipynb)
- [`MaterialGrid` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#materialgrid) · [NLopt MMA](https://nlopt.readthedocs.io/en/latest/NLopt_Algorithms/#mma-method-of-moving-asymptotes-and-ccsa)
- Previous: [07 · Metalens meta-atoms and phase libraries]({{ '/en/meta-atom/' | relative_url }}) · Next: [09 · Waveguide bend inverse design]({{ '/en/bend-inverse/' | relative_url }})
