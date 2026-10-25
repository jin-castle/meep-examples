---
layout: lesson
permalink: /en/reference-subtraction/
lesson_title: "How can we isolate light scattered by an object?"
lesson_summary: "Compare simulations with and without an object. Distinguish the questions answered by scattered-field power and by a difference in total power."
lesson_goals:
  - "Explain the relationship between incident, total, and scattered fields."
  - "Choose the appropriate monitors for power budgets and scattering cross sections."
  - "Use a Fresnel check and resolution comparison to judge the reliability of the results."
lesson_prerequisites: "Read about the flux box in Chapter 01 and reference subtraction in Chapter 02 first."
date: 2026-10-21
title: "Meep Example 03 · Reference subtraction — incident, total, and scattered fields, R·T·S budgets, and scattering cross sections"
title_en: "Meep Example 03 · Reference-run subtraction — incident, total and scattered fields, the R·T·S budget, and a scattering cross section"
lang: en
translation_key: reference-subtraction
series: meep-examples
part: 3
level: beginner
runtime: "28 s (single core)"
meep_version: "1.33.0"
official_example: "https://github.com/NanoComp/meep/blob/master/python/examples/refl-quartz.py"
tags: [meep, fdtd, scattering, reference-subtraction, fresnel, flux]
image: /assets/meep/03/03_fields.png
excerpt: "run the same cell twice, without and with the object. The difference of the two fields is the scattered field; the difference of the two fluxes is what the object did to the power. Checked first in 1D (air | quartz, Fresnel formula), then on a 2D dielectric cylinder."
---
<details markdown="1">
<summary>English summary</summary>

- **What**: run the same cell twice, without and with the object. The difference of the two fields is the scattered field; the difference of the two fluxes is what the object did to the power. Checked first in 1D (air \| quartz, Fresnel formula), then on a 2D dielectric cylinder.
- **Result**: 1D reflectance matches Fresnel to 1.6 × 10⁻⁴ over 400–800 nm. For the cylinder, R = 0.082, T = 0.674, sideways S = 0.243, R + T + S = 0.999; the scattered-field flux through a closed box gives Q_sca = 2.515 against the 2D Mie value 2.513.
- **Takeaway**: subtract fields, not just fluxes, and know which one you are looking at. Flux is quadratic, so the flux of (E_total − E_inc) is the scattered power, not "total minus incident"; the two agree only where incident and scattered waves travel in opposite directions.
- **Code**: full script at the bottom, ~28 s on one core.

</details>

<h2 id="observe">1. Observe · Compare three images</h2>

The left panel is the incident field without the cylinder, the middle is the total field with it, and the right is their difference. **Which stripes in the middle came from the incoming wave, and which changes were created by the object?** The scattered field on the right isolates those changes.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/03/03_fields.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/03/03_fields.png' | relative_url }}" alt="Re(Ez) at 1550 nm, with a shared color scale. The dashed circle marks the cylinder. The right-hand scattered field is total − incident." loading="lazy">
  </a>
  <figcaption>Re(Ez) at 1550 nm, with a shared color scale. The dashed circle marks the cylinder. The right-hand scattered field is total − incident.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/03/05_anim_scatter.gif' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/03/05_anim_scatter.gif' | relative_url }}" alt="Time evolution of incident, total, and scattered fields from left to right. Fields are subtracted frame by frame; light stored in the cylinder leaks out even after the incident pulse has passed." data-animation-src="{{ '/assets/meep/03/05_anim_scatter.gif' | relative_url }}" data-static-src="{{ '/assets/meep/03/03_fields.png' | relative_url }}">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
  <figcaption>Time evolution of incident, total, and scattered fields from left to right. Fields are subtracted frame by frame; light stored in the cylinder leaks out even after the incident pulse has passed.</figcaption>
</figure>

<h2 id="predict">2. Predict · Before reading the results</h2>

Is the flux calculated after subtracting the incident field from the total field always equal to total flux minus incident flux?

<fieldset class="prediction">
  <legend>Choose an answer and think through your reasoning.</legend>
  <label><input type="radio" name="lesson-03-prediction" value="1"> Yes. Subtraction works the same way for fields and power.</label>
  <label><input type="radio" name="lesson-03-prediction" value="2"> No. Power includes an interference term between the two fields.</label>
</fieldset>

<details markdown="1">
<summary>Check the reasoning behind your prediction</summary>

The second answer is correct. Fields add linearly, but power is calculated from products of fields. Scattered-field flux therefore excludes the incident/scattered interference term present in total-field power. Mixing the two quantities can make the power budget appear incomplete even for a lossless object.

</details>

<h2 id="understand">3. Understand the principles</h2>

{% include chapter-illustration.html %}

<!-- concept-illustration:part-03:start -->
<p class="lesson-note">Experiment B sends a +x-directed Ez plane wave onto a cylinder in vacuum with index 2 and radius 0.75 µm, infinite along z. Comparing the object-free reference and cylinder runs at the same locations gives E_scat = E_total − E_inc. This subtracts fields before calculating power. Experiment A separately checks the same method against Fresnel reflection at a single air–fused-quartz interface.</p>
<!-- concept-illustration:part-03:end -->

### Calculate the same incident wave twice

The object-free simulation is the reference run. In the second run, adding only the object adds a scattered field to the incident field. Keep source, cell, grid, and monitors identical to obtain the scattered field from the following difference.

$$E_{\mathrm{scat}} = E_{\mathrm{total}} - E_{\mathrm{inc}}$$

`get_flux_data` stores the monitor’s DFT fields, and `load_minus_flux_data` subtracts those incident fields in the new simulation. The resulting monitor measures **power of the scattered field alone**.

### Power budgets and scattering cross sections answer different questions

R·T·S asks how much incoming power leaves backward, forward, and sideways. This budget uses total-field flux and reference flux. A scattering cross section instead divides object-generated scattered power by incident intensity, so it uses monitors from which incident fields have been subtracted.

$$\sigma_{\mathrm{sc}} = P_{\mathrm{sc}}/I_{\mathrm{inc}},\qquad Q_{\mathrm{sca}} = \sigma_{\mathrm{sc}}/(2r)$$

The left and bottom surfaces have outward normals in negative coordinate directions. Match these signs when adding all four sides of the closed box.

<aside class="lesson-note" markdown="1">
The cylinder is **a 2D model infinite along z**, with Ez polarization and lossless index-2 material. The incident plane wave has finite width. Do not equate these 2D cylinder results with Mie scattering from a 3D sphere.
</aside>

<details markdown="1">
<summary>Read more about equations, symbols, and the original predictions</summary>

The incident field E_inc exists without the object. Adding the object gives E_total = E_inc + E_scat, where E_scat is the field produced by the object. Identical sources, cells, and grids in the two runs allow direct subtraction of E_inc to recover E_scat.

Power is quadratic in fields, so field subtraction does not translate directly into power subtraction. Total-field flux through a surface includes incident flux, scattered flux, and their interference term. Where the incident and scattered waves cross in opposite directions (the left surface), the interference term nearly cancels and the two subtractions are close. On the top/bottom surfaces, where the incident wave travels parallel to the surface, the interference term remains. Keep the two budgets distinct.

$$
R=\frac{-(P_{\mathrm{left}}^{\mathrm{tot}}-P_{\mathrm{left}}^{\mathrm{inc}})}{P_{\mathrm{inc}}},\quad
T=\frac{P_{\mathrm{right}}^{\mathrm{tot}}}{P_{\mathrm{inc}}},\quad
S=\frac{\sum_{\mathrm{top,bottom}}(P^{\mathrm{tot}}-P^{\mathrm{inc}})}{P_{\mathrm{inc}}},\qquad R+T+S=1
$$

$$
P_{\mathrm{sc}}=\oint \mathbf S(E_{\mathrm{tot}}-E_{\mathrm{inc}})\cdot d\mathbf n,\qquad
\sigma_{\mathrm{sc}}=\frac{P_{\mathrm{sc}}}{I_{\mathrm{inc}}},\qquad Q_{\mathrm{sca}}=\frac{\sigma_{\mathrm{sc}}}{2r},\qquad
R_{\mathrm{Fresnel}}=\Big(\frac{1-n}{1+n}\Big)^2
$$

| Symbol | Meaning | Code variable |
|------|----|-----------|
| $P^{\mathrm{inc}}_{\mathrm{side}}$ | Flux through each side in the reference run | `inc_side[k]` |
| $P^{\mathrm{tot}}_{\mathrm{side}}$ | Total-field flux through each side in the device run | `tot[k]` |
| $P_{\mathrm{inc}}$ | Incident power through the right side (denominator) | `inc` |
| $P_{\mathrm{sc}}$ | Outward sum of scattered-field flux through all four sides | `P_sc` from `scat` monitors |
| $I_{\mathrm{inc}}$ | Incident power / box width | `I_inc = inc / (2 * ym)` |
| $Q_{\mathrm{sca}}$ | Scattering cross section / geometrical cross section (2r) | `Q_sca` |
| $x=2\pi r/\lambda$ | Size parameter | `x_size` = 3.04 |

**Assumptions and validity**: 2D, Ez polarization, a lossless cylinder (n = 2), and a finite-width (8 µm) plane wave. The 1D problem uses normal incidence at a single interface, with n(λ) from the Meep materials-library fused_quartz dispersion model.

#### Make predictions before viewing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| 1D quartz reflectance (533 nm) | 3.5% | Fresnel, n = 1.46 |
| 1D R + T | 1.000 | No absorption |
| Cylinder R + T + S | 1 (within 0.5%) | Lossless, closed box |
| Scattered-field flux sum P_sc/P_inc | Below R + T + S | Excludes interference terms |
| Q_sca | Around 2 | x ≈ 3 and n = 2 is a resonant regime; Mie value not assumed in advance |
| Scattered-field shape | Forward-biased wavefronts and standing waves inside the cylinder | Forward scattering dominates for x > 1 |

**Checks**: a 1D R error above 0.5 percentage points relative to Fresnel suggests normalization trouble. An R + T + S error above 2% suggests a box gap or incorrect weight sign.

</details>

<h2 id="run">4. Run · Change one condition</h2>

Run the original code first and record a baseline. The environment is **Meep 1.33.0 · Python 3.11**, with a recorded single-core runtime of about 28 seconds. Put `reference_subtraction.py` and `blogfig.py` from the [complete code and shared helper](https://github.com/jin-castle/meep-examples/blob/main/code) in the same folder. You can also use the [complete code below](#reference).

```bash
OMP_NUM_THREADS=1 python reference_subtraction.py
```

In `r_cyl, n_cyl = 0.75, 2.0`, change **only the radius** to `0.25`. Keep index, wavelength, cell, and box unchanged. Compare with the original **Q_sca = 2.515** and the forward/backward values printed under `B. scattered field`. Observe how directionality changes as the size parameter falls from about 3.04 to about 1.01. Measure the modified Q_sca and directional values by running the code.

### What to check in the layout

Place both a total-field monitor and a scattered-field monitor on each side. Do not subtract the incident field from the total-field monitor. The box must exclude the source and remain inside the non-PML region.

<details markdown="1">
<summary>Layout, parameters, and source waveform</summary>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/03/01_layout.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/03/01_layout.png' | relative_url }}" alt="Device run of the 2D experiment. Red vertical line: full-cell-height Ez source extending through PML to produce a plane wave. Black circle: cylinder (r 0.75 µm, n 2). Blue rectangle: flux box at x = ±5.1, y = ±3.8. Each surface has two overlapping monitors: one for total fields and one for incident-subtracted scattered fields. Purple cross: decay-monitoring point. Circled numbers match the walkthrough steps." loading="lazy">
  </a>
  <figcaption>Device run of the 2D experiment. Red vertical line: full-cell-height Ez source extending through PML to produce a plane wave. Black circle: cylinder (r 0.75 µm, n 2). Blue rectangle: flux box at x = ±5.1, y = ±3.8. Each surface has two overlapping monitors: one for total fields and one for incident-subtracted scattered fields. Purple cross: decay-monitoring point. Circled numbers match the walkthrough steps.</figcaption>
</figure>

| Parameter | Value | Reason | Effect of changing it |
|----------|-----|-------------|--------|
| 1D cell, resolution | 10 µm, 200 px/µm | Official refl-quartz values; λ_min/n = 0.27 µm → 54 px | Lower resolution increases Fresnel error |
| 1D band | 400–800 nm, 25 points | Compare the full dispersion curve | — |
| 2D `fwidth` | 0.12 (width 8.3, t0 41.7) | Narrow band for a clean field map near fcen | Wider bandwidth mixes more wavelengths in the map |
| 2D cell, resolution | 14 × 10 µm, 20 px/µm | Lecture values; cylinder diameter is 30 px | Q_sca changes by 4.6% at 40 (detailed results below) |
| Cylinder | r 0.75 µm, n 2.0 | Lecture values; x = 3.04 | Higher n sharpens resonances |
| Line source | x = −5.75, full-cell height, `is_integrated=True` | Extending through PML avoids source-edge diffraction | Shortening the source introduces edge diffraction |
| Box | x ±5.1, y ±3.8 | Excludes the source, lies inside PML, over 3 µm from the cylinder | Enclosing the source changes the budget |
| Stopping | Ez at the right-side center decays to 1e-5 | Wait for stored cylinder energy to leave | An early stop leaves the budget incomplete |

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/03/00_source.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/03/00_source.png' | relative_url }}" alt="2D source waveform and spectrum: width 8.3, t0 = 41.7. The narrow-band flux monitor uses only fcen." loading="lazy">
  </a>
  <figcaption>2D source waveform and spectrum: width 8.3, t0 = 41.7. The narrow-band flux monitor uses only fcen.</figcaption>
</figure>

**Difference from the lecture notebook**: week 4 uses only left/right monitors and labels A = 1 − R − T = 0.278 as the remainder. This lesson adds top/bottom surfaces to measure that remainder as sideways power S, calculates a scattering cross section from scattered-field flux, and compares it with a 2D Mie analytical solution. The 1D Fresnel check follows the official refl-quartz reproduction from 10_sources.

</details>

<details markdown="1">
<summary>Code walkthrough · The roles of seven steps</summary>

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → running and stopping → post-processing.
> The 1D Fresnel and 2D cylinder experiments follow the same procedure. The walkthrough below uses 2D; the complete code also includes 1D.

#### ① Units and parameters — which numbers are fixed?

```python
wl = 1.55
fcen = 1 / wl
fwidth = 0.12                 # narrow band: a nearly single-frequency field map at fcen
sx, sy = 14.0, 10.0
DPML = 1.0
RESOLUTION = 20
r_cyl, n_cyl = 0.75, 2.0
src_x = -0.5 * sx + DPML + 0.25
xm = 0.5 * sx - DPML - 0.9    # flux box: x = +-5.1
ym = 0.5 * sy - DPML - 0.2    # flux box: y = +-3.8
```

- **What**: wavelength, narrow bandwidth, cell, cylinder, source position, and box position.
- **Why**: a field map representing behavior near fcen needs a narrow-band source. The box must exclude the source but remain inside PML. If the source lies inside the box, its injected power enters the budget.
- **If wrong**: a box inside PML measures power after absorption, making the budget incomplete.

#### ② Materials and geometry — what is placed where?

```python
cylinder = [mp.Cylinder(radius=r_cyl, height=mp.inf, center=mp.Vector3(), material=mp.Medium(index=n_cyl))]
# run 1 uses geometry = [], run 2 uses geometry = cylinder. Nothing else changes.
```

- **What**: one infinitely long cylinder in 2D, absent in run 1 and present only in run 2.
- **Why**: the object must be the only difference between the two runs for their field difference to be its scattered field.
- **If wrong**: changing cell size or resolution in run 2 can make `load_minus_flux_data` fail with mismatched array sizes, or subtract inappropriate fields even if it does not fail.

#### ③ Source — how is light injected?

```python
def plane_wave(fw):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=True), component=mp.Ez,
                      center=mp.Vector3(src_x, 0), size=mp.Vector3(0, sy))]
```

- **What**: a full-cell-height line source, extending into PML unlike the short line in Chapter 01.
- **Why**: ending the line inside PML avoids edge diffraction and produces a plane wave. `is_integrated=True` correctly handles a source extending into PML.
- **If wrong**: stopping the source at the inner PML boundary produces curved wavefronts at its ends, as in Chapter 01. Omitting `is_integrated` incorrectly handles attenuation of the source portion inside PML.

#### ④ Simulation and boundaries — the computation box and PML

```python
def build(geometry, resolution=RESOLUTION, fw=fwidth):
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy), boundary_layers=[mp.PML(DPML)], geometry=geometry,
                        sources=plane_wave(fw), resolution=resolution)
    total = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}   # total field
    scat = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}    # will get E_inc subtracted
    return sim, total, scat
```

- **What**: identical source and 1 µm PML in two `Simulation` objects differing only in structure. Create two monitors per surface.
- **Why**: one monitor measures total-field flux; the other later subtracts incident fields to measure scattered-field flux. Recording both in the same run enables a direct comparison of the two budgets.
- **If wrong**: a single monitor with `load_minus_flux_data` loses the total flux needed to calculate T.

#### ⑤ Monitor — what is measured?

```python
REGIONS = {
    "left":   lambda: mp.FluxRegion(center=mp.Vector3(-xm, 0), size=mp.Vector3(0, 2 * ym)),
    "right":  lambda: mp.FluxRegion(center=mp.Vector3(+xm, 0), size=mp.Vector3(0, 2 * ym)),
    "top":    lambda: mp.FluxRegion(center=mp.Vector3(0, +ym), size=mp.Vector3(2 * xm, 0)),
    "bottom": lambda: mp.FluxRegion(center=mp.Vector3(0, -ym), size=mp.Vector3(2 * xm, 0), weight=-1),
}
# run 1: save the incident fields on every side; run 2: subtract them on the `scat` monitors
inc_data = {k: sim.get_flux_data(m) for k, m in scat.items()}
...
for k, m in scat.items():
    sim.load_minus_flux_data(m, inc_data[k])
```

- **What**: the four surfaces of a closed box. The bottom uses `weight=-1` for outward −y. The left-side sign is reversed in post-processing because its outward direction is −x.
- **Why**: surfaces must meet without gaps, and every flux must follow the outward convention. `get_flux_data` stores DFT fields and `load_minus_flux_data` subtracts those fields. Its monitor therefore returns flux of (E_tot − E_inc), the power of the scattered field alone.
- **If wrong**: treating an incident-subtracted monitor as “total flux − incident flux” omits the interference term on top/bottom. The initial run made that mistake and gave R + T + S = 0.955.

> **Pitfall**: `flux(E_tot − E_inc) ≠ flux(E_tot) − flux(E_inc)`. Equality requires the interference contribution to cancel, as for waves crossing a surface in exactly opposite directions.

#### ⑥ Running and stopping — when should the simulation end?

```python
def run_decay(sim):
    sim.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, right_center, 1e-5))
```

- **What**: run both simulations until Ez at the right-side center decays to 10⁻⁵ of its peak under the stopping criterion.
- **Why**: the cylinder temporarily traps light through resonance. Stopping before that energy leaks out leaves the budget incomplete.
- **If wrong**: a fixed cutoff can miss the tail of the long pulse (t0 = 41.7) and resonant leakage. The baseline run stopped at t ≈ 150.

#### ⑦ Post-processing — converting fields into numbers

```python
R = -(tot["left"] - inc_side["left"]) / inc                 # total-field flux difference, -x outward
T = tot["right"] / inc
S = ((tot["top"] - inc_side["top"]) + (tot["bottom"] - inc_side["bottom"])) / inc
conservation = sum(outward(tot).values()) / inc             # must be 0 for a lossless object

sc_out = outward(sc)                                        # scattered field only
P_sc = sum(sc_out.values())
sigma = P_sc / (inc / (2 * ym))                             # cross section = scattered power / incident intensity
Q_sca = sigma / (2 * r_cyl)
```

- **What**: derive R, T, and S from the total/reference flux budget (sum 1), and derive scattering cross section from the outward sum of scattered-field flux.
- **Why**: conservation applies to total-field power. A scattering cross section is defined as scattered power / incident intensity and therefore needs scattered-field flux. These are different quantities answering different questions.
- **If wrong**: failing to reverse the left-side sign in `outward` subtracts backward-scattered power and underestimates σ. Failing to divide incident power by box width gives σ incorrect units.

</details>

<h2 id="interpret">5. Interpret · Read the numbers and their limits</h2>

The procedure was first checked at a single air–quartz interface. At 533 nm, **R = 0.03513** versus the Fresnel value **0.03505**. The largest difference over 400–800 nm is **1.6 × 10⁻⁴**.

The cylinder’s total-field budget gives **R = 0.0823, T = 0.6736, S = 0.2430**, summing to **0.9988**. The sum from scattered fields alone is **P_sc/P_inc = 0.4963**, a different quantity from the budget total. Dividing scattered power by incident intensity gives **σ_sc = 3.77 µm** and **Q_sca = 2.515**.

<aside class="lesson-note" markdown="1">
**Agreement with the 2D Mie value 2.513 does not establish convergence.** Increasing resolution 20 → 40 changes Q_sca by about 4.5%, from **2.515 → 2.628**. The budget closes more closely at 0.9997, but Q_sca moves away from the analytical value. This is currently a comparison at roughly the 5% level; finite beam width and box-position effects have not been separated.
</aside>

<details markdown="1">
<summary>Full results, prediction comparison, and convergence tables</summary>

#### 1D: does the procedure reproduce an analytical solution?

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/03/02_fresnel.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/03/02_fresnel.png' | relative_url }}" alt="Left: 1D cell, with air at z &lt; 0 and quartz at z &gt; 0 extending through PML; red marks the source and blue the reflection/transmission monitors. Right: Meep R(λ) points and the Fresnel curve, using n(λ) from the same materials library." loading="lazy">
  </a>
  <figcaption>Left: 1D cell, with air at z &lt; 0 and quartz at z &gt; 0 extending through PML; red marks the source and blue the reflection/transmission monitors. Right: Meep R(λ) points and the Fresnel curve, using n(λ) from the same materials library.</figcaption>
</figure>

| Quantity | Meep | Analytical result |
|---|---|---|
| R @ 533 nm | 0.03513 | 0.03505 |
| max \|R − R_Fresnel\| (400–800 nm) | 1.6 × 10⁻⁴ | — |
| R + T @ 533 nm | 1.00000 | 1 |

#### 2D: three cylinder fields and the budget



<figure class="lesson-figure">
  <a href="{{ '/assets/meep/03/04_budget.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/03/04_budget.png' | relative_url }}" alt="Power through four sides. Blue: the total/reference flux budget (R, T, S). Orange: flux of the field after incident-field subtraction. Blue sums to 1; orange sums to scattered power." loading="lazy">
  </a>
  <figcaption>Power through four sides. Blue: the total/reference flux budget (R, T, S). Orange: flux of the field after incident-field subtraction. Blue sums to 1; orange sums to scattered power.</figcaption>
</figure>

| Quantity | Total-field budget | Scattered-field flux |
|---|---|---|
| Left (R / backward scattering) | 0.0823 | 0.0857 |
| Right (T / forward scattering) | 0.6736 | 0.2153 |
| Top + bottom (S / sideways scattering) | 0.2430 | 0.1954 |
| Sum | 0.9988 | 0.4963 = P_sc / P_inc |

| Scattering cross section | Value |
|---|---|
| σ_sc | 3.77 µm |
| Q_sca = σ / 2r (Meep, res 20) | 2.515 |
| Q_sca (2D Mie, E ∥ axis, x = 3.04, m = 2) | 2.513 |

#### Comparing predictions

| Quantity | Original prediction | Simulation | Verdict |
|--------|-------------|-----------|------|
| 1D R @ 533 nm | 3.5% | 3.513% (Fresnel 3.505%) | ✅ |
| 1D R + T | 1.000 | 1.00000 | ✅ |
| R + T + S | 1 (within 0.5%) | 0.9988 | ✅ |
| P_sc/P_inc < R + T + S | Smaller | 0.496 < 0.999 | ✅ |
| Q_sca | Around 2 | 2.515 (Mie 2.513) | ✅ |
| Scattered-field shape | Forward bias and internal standing waves | Seen in the figure | ✅ |

The predictions held, but an initial interpretation was wrong. Treating the top/bottom `load_minus_flux_data` monitor values as “total − incident” gave S = 0.195 and a total of 0.955. The missing 4.5% was the interference term between incident and scattered waves. The two left-surface values (0.0823 and 0.0857) are close because counter-propagating incident and reflected waves nearly cancel the interference term. That is why this subtraction method is suitable for the R measurements in Chapters 04–05.

#### Convergence

| resolution | R | T | S | R + T + S | Q_sca |
|---|---|---|---|---|---|
| 20 | 0.0823 | 0.6736 | 0.2430 | 0.9988 | 2.515 |
| 40 | 0.0861 | 0.6626 | 0.2510 | 0.9997 | 2.628 |

The budget closes near 1 at both resolutions. Individual R·T·S values move by 1–5%, while Q_sca rises 4.5%, from 2.515 to 2.628, away from Mie. The 0.1% agreement at resolution 20 is largely coincidental.

#### Supported claims and remaining limits

- Supported: the reference-run plus `load_minus_flux_data` procedure reproduces the Fresnel analytical solution at about the 10⁻⁴ level. The lossless cylinder’s total-field budget closes to 1 in a closed box. Its scattering cross section agrees with 2D Mie within 5%.
- Not established: the second decimal place of Q_sca. It changes 4.5% with resolution, and effects of finite plane-wave width and a box 3 µm from the cylinder have not been separated. These results do not establish Mie scattering for a 3D sphere (the official cylinder_cross_section example is a 3D problem in cylindrical coordinates).

</details>

<h2 id="check">6. Check · Explain it in your own words</h2>

### 1. Why does using scattered-field top/bottom flux directly as S break the budget?

<details markdown="1">
<summary>Check the answer and reasoning</summary>

S requires total flux minus incident flux. Scattered-field flux lacks the interference term between incident and scattered waves. Confusing them in the original run gave S = 0.195 and R + T + S = 0.955, appearing to lose about 4.5%.

</details>

### 2. Are validation and convergence complete when R + T + S is near 1 and Q_sca is near the analytical value?

<details markdown="1">
<summary>Check the answer and reasoning</summary>

No. Energy conservation guarantees neither the accuracy of individual scattering quantities nor grid convergence. Since Q_sca changed by 4.5% in the resolution comparison, a smaller uncertainty cannot yet be claimed.

</details>

<h2 id="reference">7. Code and references</h2>

<details markdown="1">
<summary>Where this example is useful</summary>

When light meets an object, some returns (reflection), some continues (transmission), and some spreads sideways (scattering). The simulation contains all of them in the total field. To isolate the object’s effect, subtract the incident field calculated without it, just as Chapter 02 isolated boundary reflection. First validate the method against the known Fresnel solution for an air–quartz interface, then measure the dielectric cylinder’s R, T, and S, check closure to 1, and compare its scattering cross section with an analytical result.

#### Applications

Reflection, transmission, and scattering spectra form the specifications of optical devices. These measurements underpin coatings, filters, nanoparticles, and radar cross sections.

| Application | What this lesson contributes | What comes next |
|---|---|---|
| Thin films, antireflection coatings, DBR mirrors, and filters | Normal-incidence R·T spectra and a Fresnel check | Oblique incidence in Chapter 18, Bragg stacks in Chapter 24 |
| Nanoparticle sensors, pigments, and Raman substrates | Q_sca and a monitor isolating the scattered field | 3D Mie scattering in Chapter 23 |
| Radar cross section (RCS) and stealth | The same scattering-cross-section concept at microwave frequencies | — |
| Comparisons with and without a structure | Reference subtraction | Two-run normalization in Chapter 05 |

</details>

<details markdown="1">
<summary>Common mistakes and fixes</summary>

| Symptom | Cause | Fix |
|------|------|----------|
| R + T + S below 1 for a lossless object | Scattered-field monitor read as total flux minus incident flux | Use total/reference flux for budgets, scattered-field monitors for scattering power |
| Negative R | Left outward normal (−x) sign not reversed | `R = -(…)/inc` |
| Four-side sum near zero | Missing bottom `weight=-1` | Use outward-normal weights |
| `load_minus_flux_data` error | Cell, resolution, or monitor positions differ between runs | Build both runs with the same `build` function |
| Curved wavefronts at plane-wave source ends | Line does not extend into PML | `size=(0, sy)`, `is_integrated=True` |
| Budget changes strongly with resolution | Stopping before resonant energy has left | Check decay-monitoring point and threshold |

</details>

<details markdown="1">
<summary>Further exploration from the original lesson</summary>

| Change | Expected effect | Quantity to check |
|---------|----------|------------|
| `n_cyl` 2.0 → 3.5 (Si) | Sharper resonances make Q_sca wavelength-sensitive | Q_sca and internal standing waves |
| `r_cyl` 0.75 → 0.25 µm (x ≈ 1) | Weaker forward bias and more isotropic scattering | Four sc_parts values |
| Move the box close to the cylinder (halve xm, ym) | Does near-field contribution affect P_sc? | Compare Q_sca |
| `fwidth` 0.12 → 0.3 fcen + nfreq 11 | Q_sca(λ) spectrum and Mie resonance positions | Evaluate `mie_q_sca_2d_tm` at each wavelength |

</details>


<details>
<summary>reference_subtraction.py (expand to read)</summary>
{% highlight python %}
"""Meep Example 03 - Reference run subtraction: incident, total, scattered field and R, T, S.

Two runs of the same cell, with and without the object. What differs is the object's doing.
  A. 1D air | fused quartz: the procedure (normalization run + load_minus_flux_data) against the
     Fresnel formula R = ((1-n)/(1+n))^2 with the dispersive n(lambda) of the materials library.
     (official example refl-quartz.py)
  B. 2D dielectric cylinder (r = 0.75 um, n = 2) in a plane wave: E_scat = E_total - E_inc,
     and a closed flux box: R (left, incident subtracted), T (right), S (top + bottom, sideways
     scattering). For a lossless object R + T + S = 1.
  C. GIF: incident, total and scattered field side by side in time.

Run:  python reference_subtraction.py        (~2.5 min on one core)
Out:  00_source.png, 01_layout.png, 02_fresnel.png, 03_fields.png, 04_budget.png,
      05_anim_scatter.gif, result.json   (-> ../assets/03/)
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
from meep.materials import fused_quartz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import (Label, animate_compare, annotated_layout, bar_figure, panel_grid,   # noqa: E402
                     record_frames, source_figure)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "03")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()

# ================================================================ A. 1D air | quartz vs Fresnel
# ---------------------------------------------------------------- (1) parameters (1D, units of um)
sz = 10.0
dpml1 = 1.0
wl_min, wl_max = 0.4, 0.8
fmin, fmax = 1 / wl_max, 1 / wl_min
fcen1, df1, nfreq1 = 0.5 * (fmin + fmax), fmax - fmin, 25
RES1 = 200                    # 1D is cheap: lambda_min / n = 0.27 um -> 54 px


def sim_1d(geometry):
    # ------------------------------------------------------------ (3) source: a plane wave in 1D is a point
    src = [mp.Source(mp.GaussianSource(fcen1, fwidth=df1), component=mp.Ex, center=mp.Vector3(0, 0, -0.5 * sz + dpml1))]
    # ------------------------------------------------------------ (4) simulation
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, sz), boundary_layers=[mp.PML(dpml1)], sources=src,
                        geometry=geometry, dimensions=1, resolution=RES1)
    # ------------------------------------------------------------ (5) monitors: reflection (air side), transmission (inside quartz)
    refl = sim.add_flux(fcen1, df1, nfreq1, mp.FluxRegion(center=mp.Vector3(0, 0, -0.25 * sz)))
    tran = sim.add_flux(fcen1, df1, nfreq1, mp.FluxRegion(center=mp.Vector3(0, 0, +0.25 * sz)))
    return sim, refl, tran


# run 1: empty (air everywhere) -> incident flux and the incident flux DATA at the reflection plane
sim, refl, tran = sim_1d([])
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ex, mp.Vector3(0, 0, 0.25 * sz), 1e-9))   # (6)
inc_flux = np.array(mp.get_fluxes(refl))
refl_data = sim.get_flux_data(refl)
freqs1 = np.array(mp.get_flux_freqs(refl))
# run 2: quartz half-space from z = 0 through the PML
quartz = [mp.Block(size=mp.Vector3(mp.inf, mp.inf, 0.5 * sz), center=mp.Vector3(0, 0, 0.25 * sz), material=fused_quartz)]
sim, refl, tran = sim_1d(quartz)
sim.load_minus_flux_data(refl, refl_data)                              # incident part removed -> reflection only
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ex, mp.Vector3(0, 0, 0.25 * sz), 1e-9))
# ---------------------------------------------------------------- (7) R, T and the Fresnel formula
R1 = -np.array(mp.get_fluxes(refl)) / inc_flux                        # backward flux is negative
T1 = np.array(mp.get_fluxes(tran)) / inc_flux
n_q = np.array([np.sqrt(np.real(fused_quartz.epsilon(f)[0][0])) for f in freqs1])   # n(lambda) from the material model
R_fresnel = ((1 - n_q) / (1 + n_q)) ** 2
wl1 = 1 / freqs1
ic1 = nfreq1 // 2
print(f"A. Fresnel: max|R_meep - R_fresnel| = {np.max(np.abs(R1 - R_fresnel)):.2e}; "
      f"R @ {wl1[ic1]:.3f} um: meep {R1[ic1]:.5f}, Fresnel {R_fresnel[ic1]:.5f}; R+T = {R1[ic1] + T1[ic1]:.5f}; "
      f"n = {n_q[0]:.4f} ({wl1[0]:.2f} um) .. {n_q[-1]:.4f} ({wl1[-1]:.2f} um)")

fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
z = np.linspace(-sz / 2, sz / 2, 400)
eps_z = np.where(z > 0, n_q[ic1] ** 2, 1.0)
ax[0].plot(z, eps_z, color="k")
ax[0].axvline(-0.5 * sz + dpml1, color="red", lw=2, label="source")
ax[0].axvline(-0.25 * sz, color="blue", lw=2, label="reflection monitor")
ax[0].axvline(+0.25 * sz, color="blue", lw=2, ls="--", label="transmission monitor")
for zz in (-sz / 2 + dpml1, sz / 2 - dpml1):
    ax[0].axvspan(zz if zz > 0 else -sz / 2, sz / 2 if zz > 0 else zz, color="green", alpha=0.12)
ax[0].set_xlabel("z [um]"); ax[0].set_ylabel("epsilon"); ax[0].set_title("1D cell: air | fused quartz (green = PML)", fontsize=9)
ax[0].legend(fontsize=7, loc="center left")
ax[1].plot(wl1 * 1000, R_fresnel * 100, "k-", label="Fresnel  ((1-n)/(1+n))^2 with n(lambda) of fused_quartz")
ax[1].plot(wl1 * 1000, R1 * 100, "o", ms=4, color="tab:blue", label="Meep: reference run + load_minus_flux_data")
ax[1].set_xlabel("wavelength [nm]"); ax[1].set_ylabel("reflectance R [%]"); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=7)
ax[1].set_title(f"max |R_meep - R_Fresnel| = {np.max(np.abs(R1 - R_fresnel)):.1e}", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_fresnel.png"), dpi=150); plt.close(fig)

# ================================================================ B. 2D cylinder: fields and the power budget
# ---------------------------------------------------------------- (1) parameters
wl = 1.55
fcen = 1 / wl
fwidth = 0.12                 # narrow band: a nearly single-frequency field map at fcen
sx, sy = 14.0, 10.0
DPML = 1.0
RESOLUTION = 20
r_cyl, n_cyl = 0.75, 2.0
src_x = -0.5 * sx + DPML + 0.25
xm = 0.5 * sx - DPML - 0.9    # flux box: x = +-5.1
ym = 0.5 * sy - DPML - 0.2    # flux box: y = +-3.8
right_center = mp.Vector3(xm, 0)

# ---------------------------------------------------------------- (2) geometry: the object of run 2
cylinder = [mp.Cylinder(radius=r_cyl, height=mp.inf, center=mp.Vector3(), material=mp.Medium(index=n_cyl))]


# ---------------------------------------------------------------- (3) source: a line across the whole cell -> plane wave along +x
def plane_wave(fw):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=True), component=mp.Ez,
                      center=mp.Vector3(src_x, 0), size=mp.Vector3(0, sy))]


# ---------------------------------------------------------------- (4) simulation + (5) the closed flux box
REGIONS = {
    "left":   lambda: mp.FluxRegion(center=mp.Vector3(-xm, 0), size=mp.Vector3(0, 2 * ym)),
    "right":  lambda: mp.FluxRegion(center=mp.Vector3(+xm, 0), size=mp.Vector3(0, 2 * ym)),
    "top":    lambda: mp.FluxRegion(center=mp.Vector3(0, +ym), size=mp.Vector3(2 * xm, 0)),
    "bottom": lambda: mp.FluxRegion(center=mp.Vector3(0, -ym), size=mp.Vector3(2 * xm, 0), weight=-1),
}


def build(geometry, resolution=RESOLUTION, fw=fwidth):
    """Simulation plus TWO flux monitors per side of the box: one for the total field, and one that
    will have the incident field subtracted (load_minus_flux_data) so it measures the scattered field only."""
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy), boundary_layers=[mp.PML(DPML)], geometry=geometry,
                        sources=plane_wave(fw), resolution=resolution)
    total = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}
    scat = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}
    return sim, total, scat


def run_decay(sim):                                                  # (6)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, right_center, 1e-5))


def outward(fluxes):
    """Outward power through the box: the left side's outward normal is -x."""
    return {"left": -fluxes["left"], "right": fluxes["right"], "top": fluxes["top"], "bottom": fluxes["bottom"]}


nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * DPML, sy - 2 * DPML))
extent = [-(sx / 2 - DPML), sx / 2 - DPML, -(sy / 2 - DPML), sy / 2 - DPML]


def budget(resolution=RESOLUTION, fields=False, layout=False):
    """Run 1 (empty) then run 2 (cylinder). Returns the total-field budget R, T, S (sums to 1),
    the scattered-field power and cross section, and optionally the DFT field maps."""
    sim, total, scat = build([], resolution)
    if fields:
        dft_ref = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)
    run_decay(sim)
    inc_side = {k: float(mp.get_fluxes(m)[0]) for k, m in total.items()}   # incident flux through each side (+x / +y)
    inc = inc_side["right"]                                                # incident power through the box width
    inc_data = {k: sim.get_flux_data(m) for k, m in scat.items()}
    ez_inc = sim.get_dft_array(dft_ref, mp.Ez, 0) if fields else None

    sim, total, scat = build(cylinder, resolution)
    for k, m in scat.items():
        sim.load_minus_flux_data(m, inc_data[k])                           # these now see E_total - E_inc only
    if layout:
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(8.2, 6.0),
            title="run 2 (device): plane-wave line source, dielectric cylinder, closed flux box, PML",
            params_text=f"wl={wl} um  fwidth={fwidth}  res={resolution}/um\ncell={sx:g}x{sy:g}  dpml={DPML:g}  r={r_cyl}  n={n_cyl}",
            params_xy=(-5.8, 4.6), pml_xy=(2.0, -4.5), decay_point=(xm, 0), decay_text_xy=(1.6, -1.2),
            labels=[Label("cylinder r = 0.75 um, n = 2 (geometry)", (r_cyl, 0.3), (-4.0, 2.4), step=2, color="black"),
                    Label("line source across the cell (plane wave)", (src_x, 2.0), (-4.5, 3.4), step=3, color="red"),
                    Label("flux box: 4 sides x (total, incident-subtracted)", (xm, -2.5), (-1.5, -3.2), step=5, color="blue")])
    if fields:
        dft_dev = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)
    run_decay(sim)
    # ------------------------------------------------------------ (7) budgets
    tot = {k: float(mp.get_fluxes(m)[0]) for k, m in total.items()}
    sc = {k: float(mp.get_fluxes(m)[0]) for k, m in scat.items()}
    # total-field budget: flux DIFFERENCES to the empty run (exact by energy conservation)
    R = -(tot["left"] - inc_side["left"]) / inc                            # backward: -x is outward on the left
    T = tot["right"] / inc                                                 # what a detector behind the cylinder sees
    S = ((tot["top"] - inc_side["top"]) + (tot["bottom"] - inc_side["bottom"])) / inc   # sideways, both signs outward
    conservation = sum(outward(tot).values()) / inc                        # total field: must be 0 (lossless)
    # scattered-field budget: fluxes of (E_total - E_inc) through the four sides
    sc_out = outward(sc)
    P_sc = sum(sc_out.values())
    R_sub = sc_out["left"] / inc                                           # = R: counter-propagating waves have no cross term
    I_inc = inc / (2 * ym)                                                 # incident power per unit width
    sigma = P_sc / I_inc                                                   # 2D scattering cross section [um]
    out = {"R": R, "T": T, "S": S, "sum": R + T + S, "conservation": conservation, "R_sub": R_sub,
           "P_sc_over_inc": P_sc / inc, "sc_parts": {k: v / inc for k, v in sc_out.items()},
           "sigma_um": sigma, "Q_sca": sigma / (2 * r_cyl), "inc_flux": inc}
    if fields:
        ez_tot = sim.get_dft_array(dft_dev, mp.Ez, 0)
        out["fields"] = (ez_inc, ez_tot, ez_tot - ez_inc)
    return out


def mie_q_sca_2d_tm(m, x, nmax=30):
    """Scattering efficiency of an infinite dielectric cylinder, E parallel to the axis (Ez), normal
    incidence. From continuity of Ez and dEz/dr at r = a: b_n = [m Jn'(mx) Jn(x) - Jn(mx) Jn'(x)] /
    [Jn(mx) Hn'(x) - m Jn'(mx) Hn(x)],  Q_sca = (2/x) sum_n |b_n|^2 over n = -inf..inf."""
    from scipy.special import jv, jvp, hankel1, h1vp
    q = 0.0
    for n in range(-nmax, nmax + 1):
        b = (m * jvp(n, m * x) * jv(n, x) - jv(n, m * x) * jvp(n, x)) / (jv(n, m * x) * h1vp(n, x) - m * jvp(n, m * x) * hankel1(n, x))
        q += abs(b) ** 2
    return 2 * q / x


source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")
base = budget(fields=True, layout=True)
x_size = 2 * np.pi * r_cyl / wl
try:
    Q_mie = mie_q_sca_2d_tm(n_cyl, x_size)
except Exception as exc:                                                  # scipy missing: report, do not fake
    Q_mie = None
    print("Mie comparison skipped:", exc)
print(f"B. total-field budget: R = {base['R']:.4f}, T = {base['T']:.4f}, S = {base['S']:.4f}, R+T+S = {base['sum']:.4f} "
      f"(conservation residual {base['conservation']:+.4f}); R from subtracted field = {base['R_sub']:.4f}")
print(f"B. scattered field: P_sc/inc = {base['P_sc_over_inc']:.4f} " + " ".join(f"{k}={v:.4f}" for k, v in base['sc_parts'].items())
      + f"; sigma = {base['sigma_um']:.3f} um, Q_sca = {base['Q_sca']:.3f}" + (f" (2D Mie, x = {x_size:.2f}: {Q_mie:.3f})" if Q_mie else ""))
ez_inc, ez_tot, ez_sc = base["fields"]
circ = {i: (0, 0, r_cyl, "") for i in range(3)}
panel_grid([ez_inc, ez_tot, ez_sc], ["incident (run 1, no object)", "total (run 2, with cylinder)", "scattered = total - incident"],
           extent, os.path.join(OUT, "03_fields.png"), ncols=3, circles=circ, figsize=(14, 3.9),
           suptitle=f"Re(Ez) at 1550 nm, one color scale; dashed circle = cylinder")
bar_figure(["R (reflected)", "T (transmitted)", "S (sideways)", "R + T + S"],
           {"total field, minus the empty run": [base["R"], base["T"], base["S"], base["sum"]],
            "scattered field only (E_tot - E_inc)": [base["sc_parts"]["left"], base["sc_parts"]["right"],
                                                     base["sc_parts"]["top"] + base["sc_parts"]["bottom"], base["P_sc_over_inc"]]},
           os.path.join(OUT, "04_budget.png"), ylabel="fraction of incident power", reference=1.0, reference_label="lossless: 1")

keys = ("R", "T", "S", "sum", "Q_sca")
convergence = [{"resolution": RESOLUTION, **{k: base[k] for k in keys}}]
for res in (40,):
    b = budget(resolution=res)
    convergence.append({"resolution": res, **{k: b[k] for k in keys}})
    print(f"convergence res={res}: R={b['R']:.4f} T={b['T']:.4f} S={b['S']:.4f} sum={b['sum']:.4f} Q_sca={b['Q_sca']:.3f}")

# ================================================================ C. GIF: incident / total / scattered in time
fw_anim = 0.3 * fcen
w_anim = 1 / fw_anim
t_src = 5 / fw_anim
sets = []
for geom in ([], cylinder):
    s_anim = mp.Simulation(cell_size=mp.Vector3(sx, sy), boundary_layers=[mp.PML(DPML)], geometry=geom,
                           sources=plane_wave(fw_anim), resolution=14)
    frames, times = record_frames(s_anim, nonpml, mp.Ez, t_start=t_src - 2 * w_anim, t_end=t_src + sx + 6, n_frames=60)
    sets.append(frames)
sets.append([t - i for t, i in zip(sets[1], sets[0])])                  # scattered = total - incident, frame by frame
animate_compare(sets, ["incident (no object)", "total (cylinder)", "scattered = total - incident"], times, extent,
                os.path.join(OUT, "05_anim_scatter.gif"), figsize=(13, 3.9), suptitle="plane wave from the left")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"fresnel": {"wavelengths_um": wl1.tolist(), "R_meep": R1.tolist(), "R_fresnel": R_fresnel.tolist(),
                               "T_meep": T1.tolist(), "n_quartz": n_q.tolist(),
                               "max_abs_err": float(np.max(np.abs(R1 - R_fresnel))), "R_center": float(R1[ic1]),
                               "R_fresnel_center": float(R_fresnel[ic1]), "R_plus_T_center": float(R1[ic1] + T1[ic1])},
                   "cylinder": {k: base[k] for k in ("R", "T", "S", "sum", "conservation", "R_sub", "P_sc_over_inc", "sc_parts", "sigma_um", "Q_sca", "inc_flux")},
                   "mie": {"x": x_size, "Q_sca_tm": Q_mie},
                   "convergence": convergence, "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
{% endhighlight %}
</details>

Unlike the walkthrough excerpts, the complete code includes the 1D Fresnel experiment, figure saving, GIF recording, and result.json output. The shared plotting helper `blogfig.py` lives in the same folder (`code/`). Complete code and helper: [GitHub code folder](https://github.com/jin-castle/meep-examples/blob/main/code).

**Recorded output (run on 2026-10-23)**:
```
A. Fresnel: max|R_meep - R_fresnel| = 1.62e-04; R @ 0.533 um: meep 0.03513, Fresnel 0.03505; R+T = 1.00000; n = 1.4533 (0.80 um) .. 1.4701 (0.40 um)
B. total-field budget: R = 0.0823, T = 0.6736, S = 0.2430, R+T+S = 0.9988 (conservation residual -0.0018); R from subtracted field = 0.0857
B. scattered field: P_sc/inc = 0.4963 left=0.0857 right=0.2153 top=0.0977 bottom=0.0977; sigma = 3.772 um, Q_sca = 2.515 (2D Mie, x = 3.04: 2.513)
convergence res=40: R=0.0861 T=0.6626 S=0.2510 sum=0.9997 Q_sca=2.628
```

**Reproduction environment**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · run `python reference_subtraction.py` (approximately 28 s, single core)


### Further reading

- [Official refl-quartz.py example](https://github.com/NanoComp/meep/blob/master/python/examples/refl-quartz.py) (1D normalization run and Fresnel check)
- [Official cylinder_cross_section.py example](https://github.com/NanoComp/meep/blob/master/python/examples/cylinder_cross_section.py) (scattering cross section in 3D cylindrical coordinates)
- [Official tutorial: transmittance/reflectance normalization](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend) · [`load_minus_flux_data` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#flux-spectra)
- Previous: [02 · Boundary conditions and PML]({{ site.baseurl }}/en/boundary-pml/) · Next: [04 · Straight waveguide and guided modes]({{ site.baseurl }}/en/straight-waveguide/)
