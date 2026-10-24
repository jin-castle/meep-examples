---
layout: lesson
permalink: /en/straight-waveguide/
lesson_title: "Does all the light emerge from a straight waveguide?"
lesson_summary: "Validate the source and monitors with a straight waveguide whose answer is known. Distinguish the modes a structure supports from the mode actually injected and measured."
lesson_goals:
  - "Explain guided modes and the effective index n_eff."
  - "Use EigenModeSource and mode monitors to measure transmission of the same mode."
  - "Assess numerical residuals with a T ≈ 1 check and resolution comparisons."
lesson_prerequisites: "Start with refractive index and total internal reflection, source and pulse timing from Chapter 01, and PML from Chapter 02."
date: 2026-10-22
title: "Meep Example 04 · Straight waveguide and guided modes — MPB n_eff, EigenModeSource, modal transmission"
title_en: "Meep Example 04 · Straight waveguide and guided modes — MPB n_eff, EigenModeSource, modal transmission"
lang: en
translation_key: straight-waveguide
series: meep-examples
part: 4
level: beginner
runtime: "2.5 min (baseline 34 s + 3 convergence runs)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/"
tags: [meep, fdtd, waveguide, eigenmode, mode-decomposition]
image: /assets/meep/04/02_field.png
excerpt: "a 2D silicon strip waveguide (0.5 µm wide, SiO₂ cladding) with the fundamental TE mode injected at one end and measured at the other."
---
<details markdown="1">
<summary>English summary</summary>

- **What**: a 2D silicon strip waveguide (0.5 µm wide, SiO₂ cladding) with the fundamental TE mode injected at one end and measured at the other.
- **Result**: T = 1.0000, R = 8×10⁻⁶ at 1.55 µm. Everything that goes in comes out. The 0.5 µm strip guides three TE modes (n_eff = 3.15, 2.59, 1.45); only mode 1 is injected and measured.
- **Takeaway**: start with a problem whose answer you already know. If T ≠ 1 here, the measurement setup is wrong, not the device.
- **Code**: full script at the bottom, ~2.5 min on one core (the baseline run is 34 s; the rest is the convergence check).

</details>

<h2 id="observe">1. Observe · Follow the path of light</h2>

Inject a fundamental-mode pulse into a silicon strip. The stripes in the upper panel follow the strip, while the envelope below weakens outside the core. A uniform straight guide has no discontinuity that bends or reflects light. Check whether **the power in the injected mode emerges unchanged at the other end**.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/04/02_field.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/04/02_field.png' | relative_url }}" alt="Top: Re(Ey). Bottom: magnitude of Ey. Solid lines mark the Si core; the mode tail extends weakly beyond them." loading="lazy">
  </a>
  <figcaption>Top: Re(Ey). Bottom: magnitude of Ey. Solid lines mark the Si core; the mode tail extends weakly beyond them.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/04/03_animation.gif' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/04/03_animation.gif' | relative_url }}" alt="The pulse travels right, passes the input and output monitors, and disappears in PML. Red marks the source; blue marks the two mode monitors." data-animation-src="{{ '/assets/meep/04/03_animation.gif' | relative_url }}" data-static-src="{{ '/assets/meep/04/02_field.png' | relative_url }}">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
  <figcaption>The pulse travels right, passes the input and output monitors, and disappears in PML. Red marks the source; blue marks the two mode monitors.</figcaption>
</figure>

<h2 id="predict">2. Predict · Before reading the results</h2>

If fundamental-mode transmission is T ≈ 1, does that mean the guide supports only one guided mode?

<fieldset class="prediction">
  <legend>Choose an answer and think through your reasoning.</legend>
  <label><input type="radio" name="lesson-04-prediction" value="1"> Yes. T = 1 means the waveguide is single-mode.</label>
  <label><input type="radio" name="lesson-04-prediction" value="2"> No. You can inject and measure one mode even when several modes are supported.</label>
</fieldset>

<details markdown="1">
<summary>Check the reasoning behind your prediction</summary>

The second answer is correct. Injecting only band 1 and projecting onto band 1 measures mode 1 → mode 1 transmission. The number of supported modes requires a separate eigenmode calculation. This 2D cross-section supports three modes.

</details>

<h2 id="understand">3. Understand the principles</h2>

{% include chapter-illustration.html %}

<!-- concept-illustration:part-04:start -->
<p class="lesson-note">The left illustrates a real 3D guide with finite thickness; the right is the 2D model used here, with material and fields invariant along z. The model has a 0.5 µm Si (n = 3.48) core in SiO₂ (n = 1.44) cladding, and a weak mode tail outside the core. This 2D calculation does not directly represent a finite-thickness device cross-section. Several guided modes are supported, but this example injects and measures only the fundamental.</p>
<!-- concept-illustration:part-04:end -->

### A mode is a field shape allowed by the cross-section

The boundary between high-index Si core (n = 3.48) and low-index SiO₂ cladding (n = 1.44) confines light. A mode preserves its transverse shape as it propagates. The outside tail is part of the mode, so sources and monitors must span more than the core width.

The effective index n_eff = k/f describes the phase-accumulation rate along propagation. Here **1.44 < n_eff < 3.48** identifies a guided mode. The MPB values for bands 1 onward are **3.153, 2.592, 1.447**; the third is only slightly above the cladding index.

### Measure the same mode at the input and output

`EigenModeSource(eig_band=1)` injects the fundamental-mode shape. `get_eigenmode_coefficients(..., [1])` selects that same mode from the input/output fields. Divide forward output power by forward input power for T, and backward power at the input plane by forward input power for R.

$$T = \frac{\lvert a^+_{\mathrm{out}}\rvert^2}{\lvert a^+_{\mathrm{in}}\rvert^2},\qquad R = \frac{\lvert a^-_{\mathrm{in}}\rvert^2}{\lvert a^+_{\mathrm{in}}\rvert^2}$$

<aside class="lesson-note" markdown="1">
This is **a 2D model with material and fields invariant along z**. A width of 0.5 µm alone does not establish single-mode operation. Its mode count and n_eff do not replace those of a finite-thickness 3D SOI guide. T here means **mode 1 → mode 1**.
</aside>

<details markdown="1">
<summary>Read more about equations, symbols, and the original predictions</summary>

With the core (silicon, n = 3.48) at a higher index than the cladding (SiO₂, n = 1.44), total internal reflection confines propagating light. The confined field shape is a mode, with the simplest shape called the fundamental TE0 mode. A uniform straight guide has no reflecting discontinuity and transmits without loss in the ideal model.

$$
T=\frac{\|a^{+}_{\mathrm{out}}\|^2}{\|a^{+}_{\mathrm{in}}\|^2},\qquad
R=\frac{\|a^{-}_{\mathrm{in}}\|^2}{\|a^{+}_{\mathrm{in}}\|^2},\qquad
T+R=1 \ (\text{lossless})
$$

| Symbol | Meaning | Code variable |
|------|----|-----------|
| $n_{\mathrm{core}}, n_{\mathrm{clad}}$ | Core / cladding refractive index | `n_si`, `n_sio2` |
| $a^{+}_{\mathrm{in}}$ | Forward TE0 amplitude at the input monitor | `ci.alpha[0, :, 0]` |
| $a^{-}_{\mathrm{in}}$ | Backward (reflected) TE0 amplitude at the input monitor | `ci.alpha[0, :, 1]` |
| $a^{+}_{\mathrm{out}}$ | Forward TE0 amplitude at the output monitor | `co.alpha[0, :, 0]` |

**Assumptions and validity**: 2D (infinite along z), lossless materials. The 0.5 µm slab supports three TE modes (table below), but only the fundamental is injected and used for projection.

#### How many modes? Start with n_eff

Before injecting light, solve the cross-section modes with MPB. Calling `sim.get_eigenmode` within Meep performs the same calculation. A mode is guided when its effective index n_eff = k/f lies between n_clad and n_core.

```python
sim.init_sim()
where = mp.Volume(center=mp.Vector3(src_x, 0), size=cross)   # the source cross-section
for band in (1, 2, 3):
    em = sim.get_eigenmode(fcen, mp.X, where, band, mp.Vector3(0.8 * n_si * fcen, 0, 0), parity=mp.ODD_Y)
    print(band, em.k.x / fcen)          # n_eff = k / f
```

| band | n_eff | guided? |
|---|---|---|
| 1 | 3.153 | Yes |
| 2 | 2.592 | Yes |
| 3 | 1.447 | Barely (n_clad = 1.44) |

`EigenModeSource(eig_band=1)` injects only band 1, and `get_eigenmode_coefficients(..., [1])` projects only onto band 1. Thus T in this lesson is mode 1 → mode 1 transmission.

#### Make predictions before viewing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| T | 1.000 (error within 10⁻³) | Nothing causes reflection or scattering |
| R | ≪ 10⁻³ | No discontinuity; only numerical discretization residuals remain |
| Field shape | Fixed width in the core, rapid decay outside | Definition of a guided mode |
| Number of guided modes | 1 | Initial guess: width 0.5 µm is 1/3 wavelength, so perhaps single-mode |

**Checks**: if \|T − 1\| > 0.01 or R > 10⁻³, first suspect source/monitor placement or normalization rather than the uniform structure.

</details>

<h2 id="run">4. Run · Change one condition</h2>

Run the original code first and record a baseline. The environment is **Meep 1.33.0 · Python 3.11**. Recorded single-core runtime is about 34 seconds for the baseline and about 2.5 minutes including convergence runs. Put `straight_waveguide.py` and `blogfig.py` from the [complete code and shared helper](https://github.com/jin-castle/meep-examples/blob/main/code) in the same folder. You can also use the [complete code below](#reference).

```bash
OMP_NUM_THREADS=1 python straight_waveguide.py
```

Change `w_core = 0.5` to `w_core = 0.2` in the complete code and rerun with other parameters unchanged. In **`n_eff by band`**, compare every band with cladding index **1.44** and count the guided modes again. Also verify that `T` still refers to fundamental-mode transmission. Narrowing the core is expected to weaken confinement, but judge the new n_eff and mode count from your actual run.

### What to check in the layout

The source is at x = −5, the input monitor at −4, and the output monitor at +5. The core extends through PML using `mp.inf`; source and monitor widths are 3 µm to include the mode tails.

<details markdown="1">
<summary>Layout, parameters, and source waveform</summary>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/04/01_layout.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/04/01_layout.png' | relative_url }}" alt="Black strip: Si core (`geometry`, extending through PML at both ends). Red line: `EigenModeSource` at x = −5. Blue lines: mode monitors at x = −4 (input/reflection) and +5 (transmission). Green hatching: PML. Purple cross: decay-monitoring point at x = 5.5. Circled numbers identify ① parameters, ② geometry, ③ source, ④ PML, ⑤ monitors, and ⑥ stopping point; ⑦ post-processing has no physical location. Source and monitors span 3 µm, wider than the core." loading="lazy">
  </a>
  <figcaption>Black strip: Si core (`geometry`, extending through PML at both ends). Red line: `EigenModeSource` at x = −5. Blue lines: mode monitors at x = −4 (input/reflection) and +5 (transmission). Green hatching: PML. Purple cross: decay-monitoring point at x = 5.5. Circled numbers identify ① parameters, ② geometry, ③ source, ④ PML, ⑤ monitors, and ⑥ stopping point; ⑦ post-processing has no physical location. Source and monitors span 3 µm, wider than the core.</figcaption>
</figure>

| Parameter | Value | Reason | Effect of changing it |
|----------|-----|-------------|--------|
| `wl` | 1.55 µm | Standard telecom wavelength | Changes mode count and n_eff |
| `w_core` | 0.5 µm | Baseline 2D cross-section; only fundamental injected | Wider guides support higher-order modes |
| `resolution` | 50 px/µm | Core is 25 px wide; in-material wavelength is 22 px | Below 20, T departs more from 1 |
| `dpml` | 1.0 µm | ≈ λ/1.5, sufficient reflection suppression here | A thin layer can increase PML reflection and R |
| `sx, sy` | 14 × 6 µm | Separation among source, monitors, and PML | Smaller cells can place monitors against PML |
| Section width `cross` | 3.0 µm | Includes core and evanescent tails | Restricting to core width can produce T < 1 |

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/04/00_source.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/04/00_source.png' | relative_url }}" alt="Source waveform (left) and power spectrum (right). GaussianSource has width = 1/fwidth = 7.75 and peak t0 = 5 × width = 38.8. Red lines mark the monitor-band edges (1476–1632 nm), where source power is 8.5% of its central value, sufficient for this band. In Chapter 05 the corresponding edge power falls to 0.005%." loading="lazy">
  </a>
  <figcaption>Source waveform (left) and power spectrum (right). GaussianSource has width = 1/fwidth = 7.75 and peak t0 = 5 × width = 38.8. Red lines mark the monitor-band edges (1476–1632 nm), where source power is 8.5% of its central value, sufficient for this band. In Chapter 05 the corresponding edge power falls to 0.005%.</figcaption>
</figure>

**Difference from the lecture notebook**: week 5 uses n_core 3.4, a vertical (+y) guide, and directly calls MPB `ModeSolver`. This lesson uses the official value 3.48, a horizontal guide, and calls the same MPB solver inside Meep through `sim.get_eigenmode`.

</details>

<details markdown="1">
<summary>Code walkthrough · The roles of seven steps</summary>

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → running and stopping → post-processing.
> Meep scripts usually follow this order.

#### ① Units and parameters — which numbers are fixed?

```python
import numpy as np
import meep as mp
import matplotlib.pyplot as plt

# Meep is unit-free. We choose 1 length unit = 1 um, so frequency = 1 / wavelength.
wl   = 1.55              # wavelength [um]
fcen = 1 / wl            # center frequency [1/um]
df   = 0.2 * fcen        # source bandwidth (Gaussian pulse)
nfreq = 11               # number of frequencies the monitors record

w_core = 0.5             # Si strip width [um]
n_si, n_sio2 = 3.48, 1.44

resolution = 50          # pixels per um  -> core = 25 px, lambda/n_si = 22 px
dpml = 1.0               # PML thickness [um]
sx, sy = 14.0, 6.0       # cell size [um], PML included
```

- **What**: choose the length unit (µm), then express wavelength, frequency, geometry, and grid density in that unit.
- **Why**: Meep uses dimensionless units. If 1 = 1 µm, frequency is in 1/µm and wavelength 1.55 µm corresponds to f = 0.645.
- **If wrong**: low `resolution` represents the core with too few pixels, distorting the mode and moving T away from 1. An overly narrow `df` lengthens the pulse and runtime.

> **Pitfall**: writing `fcen = 1.55`. Frequency in Meep is the reciprocal of wavelength.

#### ② Materials and geometry — what is placed where?

```python
geometry = [mp.Block(center=mp.Vector3(0, 0),
                     size=mp.Vector3(mp.inf, w_core),   # infinite in x: runs straight through the PML
                     material=mp.Medium(index=n_si))]
# background (cladding) is set later via default_material=SiO2
```

- **What**: one infinitely long silicon strip 0.5 µm wide.
- **Why**: `mp.inf` extends the guide into PML. Continuing a uniform structure through the boundary minimizes unwanted end reflections.
- **If wrong**: ending the guide inside the cell creates a reflecting end face and raises R.

#### ③ Source — how is light injected?

```python
cross = mp.Vector3(0, 3.0)   # a vertical line 3 um tall: wider than the core to include the evanescent tail

sources = [mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=df),
                              center=mp.Vector3(-5.0, 0), size=cross,
                              eig_band=1,               # 1-indexed: the fundamental mode
                              eig_parity=mp.ODD_Y)]     # 2D TE polarization (Ey, Hx, Hz)
```

- **What**: inject a Gaussian pulse with the fundamental-mode profile from a vertical line at x = −5.
- **Why**: a point source or plane wave also injects components that do not match the guided mode, producing reflection and radiation noise. `EigenModeSource` solves the mode with MPB first, then injects that shape to select TE0.
- **If wrong**: changing `eig_parity` to `EVEN_Y` selects a different symmetry/mode in this setup. Restricting `size` to the core width truncates the tails and can produce T < 1.

> **Pitfall**: there is no `eig_band=0`; band numbering starts at 1.

#### ④ Simulation and boundaries — the computation box and PML

```python
sim = mp.Simulation(cell_size=mp.Vector3(sx, sy),
                    resolution=resolution,
                    boundary_layers=[mp.PML(dpml)],        # absorbing layer on all four sides
                    geometry=geometry,
                    sources=sources,
                    default_material=mp.Medium(index=n_sio2))

sim.plot2D()                       # ALWAYS look at the layout before running
plt.savefig("01_layout.png", dpi=150)
```

- **What**: put the materials, geometry, and source in a 14 × 6 µm box with 1 µm PML on all four sides.
- **Why**: PML (perfectly matched layer) absorbs light at the box boundary to approximate unbounded space with minimal reflection. `plot2D` produces the layout figure; inspect it before running.
- **If wrong**: omitting `boundary_layers` makes the boundary reflecting, returning light and raising R.

#### ⑤ Monitor — what is measured?

```python
mon_in  = sim.add_mode_monitor(fcen, 0.1 * fcen, nfreq,
                               mp.ModeRegion(center=mp.Vector3(-4.0, 0), size=cross))
mon_out = sim.add_mode_monitor(fcen, 0.1 * fcen, nfreq,
                               mp.ModeRegion(center=mp.Vector3(+5.0, 0), size=cross))

# optional: steady-state field map of the whole non-PML region (for the figure in section 5)
dft = sim.add_dft_fields([mp.Ey], fcen, 0, 1,
                         where=mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2*dpml, sy - 2*dpml)))
```

- **What**: two mode-decomposition monitors, just downstream of the source at x = −4 and near the opposite end at x = +5, plus frequency-domain field recording over the full region.
- **Why**: a single input monitor separates forward and backward (reflected) components, so the reflection monitor can sit downstream rather than upstream of the source.
- **If wrong**: a monitor at the source x mixes with the injecting field and contaminates the coefficients. A monitor inside PML measures an already attenuated field.

#### ⑥ Running and stopping — when should the simulation end?

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25,                     # check every 25 time units
            mp.Ey,                  # which field component to watch
            mp.Vector3(5.5, 0),     # where to watch: just past the output monitor
            1e-6))                  # stop when |Ey|^2 has decayed to 1e-6 of its peak
```

- **What**: after the source turns off, run until the field near the output monitor reaches the 10⁻⁶ decay threshold relative to its maximum.
- **Why**: the whole pulse must cross the monitor for an accurate DFT. A fixed cutoff (`until=200`) can fail when geometry changes.
- **If wrong**: an early stop misses part of the pulse tail, giving T below 1 and ripples in the spectrum.

#### ⑦ Post-processing — converting fields into numbers

```python
ci = sim.get_eigenmode_coefficients(mon_in,  [1], eig_parity=mp.ODD_Y)
co = sim.get_eigenmode_coefficients(mon_out, [1], eig_parity=mp.ODD_Y)

p_in_fwd  = np.abs(ci.alpha[0, :, 0])**2    # forward power at the input monitor   (a_in+)
p_in_back = np.abs(ci.alpha[0, :, 1])**2    # backward power at the input monitor  (a_in-)
p_out_fwd = np.abs(co.alpha[0, :, 0])**2    # forward power at the output monitor  (a_out+)

T = p_out_fwd / p_in_fwd                    # section 2, first formula
R = p_in_back / p_in_fwd                    # section 2, second formula
ic = nfreq // 2                             # index of the center frequency
print(f"T = {T[ic]:.4f}, R = {R[ic]:.2e}, T+R = {T[ic]+R[ic]:.4f}")
```

- **What**: project both monitor fields onto TE0 to obtain amplitudes $a^{\pm}$, then compute T and R using the equations above.
- **Why**: the last axis of `alpha[band, freq, direction]` is 0 for forward and 1 for backward. The backward component at the input monitor is reflection.
- **If wrong**: a source/monitor `eig_parity` mismatch projects onto a different mode and produces misleading T.

</details>

<h2 id="interpret">5. Interpret · Read the numbers and their limits</h2>

At 1.55 µm, **T = 1.0000, R = 8.0 × 10⁻⁶**. Across 1.48–1.63 µm, T is **0.99999–1.00001**. This checks consistency of fundamental-mode injection, measurement, and normalization in the straight reference guide.

Total-flux transmission is also 1.0000, and mode 1 accounts for **0.9999** of input flux. The two nearly coincide in this straight guide, but total flux and a particular modal power can differ in other geometries. Use the same denominator before comparing or subtracting them.

<aside class="lesson-note" markdown="1">
**The small R value is not converged to all displayed digits.** Raising resolution 25 → 50 → 70 reduces R from **2.1 × 10⁻⁴ → 8.0 × 10⁻⁶ → 1.4 × 10⁻⁶**. Changing PML from 1 → 0.5 µm instead leaves R nearly unchanged at ≈ 8.1 × 10⁻⁶. This residual is sensitive to grid discretization and is not a 3D device reflectance.
</aside>

<details markdown="1">
<summary>Full results, prediction comparison, and convergence tables</summary>

| Quantity | Value | Comparison |
|--------|-----|-----------|
| T @ 1.55 µm | 1.0000 | Theory: 1 |
| R @ 1.55 µm | 8.0 × 10⁻⁶ | Theory: 0 |
| T + R | 1.0000 | Energy conservation |
| T (1.48–1.63 µm) | 0.99999–1.00001 | Flat across the band |

#### Total flux and modal power

`add_mode_monitor` also acts as a flux monitor. Both quantities can be extracted at the same cross-section.

| Quantity | Denominator | Value @ 1.55 µm |
|---|---|---|
| T (modal) = \|a_out+\|² / \|a_in+\|² | Incident mode-1 power | 1.0000 |
| T_total = flux_out / flux_in | Total input-plane flux | 1.0000 |
| Mode-1 fraction of input flux = \|a_in+\|² / flux_in | Total input-plane flux | 0.9999 |

These quantities nearly coincide in the straight guide: 99.99% of injected power is in mode 1, with negligible conversion or radiation. In the Chapter 05 bend, total flux and mode-1 power separate, so the power accounting must distinguish guided transmission from radiation. Subtracting quantities with different denominators can yield negative apparent loss; use a common denominator.

#### Convergence

| resolution | dpml | T | R | Note |
|---|---|---|---|---|
| 50 | 1.0 | 1.000000 | 8.0 × 10⁻⁶ | Baseline |
| 25 | 1.0 | 0.999996 | 2.1 × 10⁻⁴ | Half resolution |
| 70 | 1.0 | 1.000000 | 1.4 × 10⁻⁶ | 1.4 times resolution |
| 50 | 0.5 | 1.000000 | 8.1 × 10⁻⁶ | Half PML thickness |

Even at resolution 25, T is within 10⁻⁵ of 1. R falls from 10⁻⁴ to 10⁻⁶ with increasing resolution and is insensitive to the tested PML thicknesses. In this structure, the evidence points to grid-discretization residuals rather than PML reflection.

#### Comparing predictions

| Quantity | Original prediction | Simulation | Verdict |
|--------|-------------|-----------|------|
| T | 1.000 ± 0.001 | 1.0000 | ✅ |
| R | ≪ 10⁻³ | 8 × 10⁻⁶ | ✅ |
| Field shape | Confined in the core | Seen in the figure | ✅ |
| Guided-mode count | 1 | 3 (n_eff 3.15, 2.59, 1.45) | ❌ |

T, R, and the fields match the predictions. A uniform straight guide has no reflecting discontinuity, so this expected result validates the source, monitors, PML, and normalization setup.

The mode-count prediction was wrong. The slab V number $V = (\pi w/\lambda)\sqrt{n_{\mathrm{core}}^2 - n_{\mathrm{clad}}^2} = 3.2$ exceeds π, allowing three TE modes. The third sits just above cladding index 1.44 at n_eff = 1.447. T still equals 1 because `EigenModeSource` injects band 1 and the mode monitor projects onto band 1. When discussing transmission in a multimode guide, always name the input and output modes.

**Validation checks**: T + R = 1.0000; source (x = −5) and monitors (x = −4, +5) all lie outside PML (\|x\| > 6); stopping uses field decay.

#### Supported claims and remaining limits

- Supported: mode 1 → mode 1 transmission is 1 in this setup; the source, monitors, PML, and normalization are internally consistent.
- Not established: values for a 3D SOI guide. A 2D slab has different effective indices and mode counts. The small R value and its displayed precision depend on resolution.

</details>

<h2 id="check">6. Check · Explain it in your own words</h2>

### 1. Why can T = 1 even though three guided modes exist?

<details markdown="1">
<summary>Check the answer and reasoning</summary>

Supported modes and excited modes are different. The source injects band 1 and the monitor projects onto band 1, measuring whether that same mode travels unchanged through the uniform straight guide.

</details>

### 2. What do you miss if source and monitor widths are reduced to the core width?

<details markdown="1">
<summary>Check the answer and reasoning</summary>

The evanescent tail outside the core is part of the mode. Narrowing the source truncates the injected profile; narrowing the monitor omits some field. A change in T alone does not identify which of these caused it.

</details>

<h2 id="reference">7. Code and references</h2>

<details markdown="1">
<summary>Where this example is useful</summary>

Light injected into a straight silicon waveguide should emerge at the opposite end. This lesson verifies that in Meep. Choosing a problem with known answer T = 1 separates source/monitor validation from device behavior. If this reference does not give 1, later device calculations cannot yet be trusted.

#### Applications

Straight waveguides are the wiring of silicon photonics, and their components use the same sources and monitors as this lesson.

| Application | What this lesson contributes | What comes next |
|---|---|---|
| Silicon-photonic interconnects and transceivers | Guided modes, n_eff, and single-mode conditions | Bends in Chapter 05 and tapers in Chapter 29 |
| Waveguide cross-section design (width/thickness choice) | MPB n_eff table and the existence of three modes | Band structure in Chapter 24 |
| Transmission reference for waveguide components | EigenModeSource plus mode monitors; T = 1 calibration | Chapters 05 and 09 |
| Fiber–chip couplers, modulators, and optical switches | Defining the input mode | GDS components in Chapter 30 |

</details>

<details markdown="1">
<summary>Common mistakes and fixes</summary>

| Symptom | Cause | Fix |
|------|------|----------|
| T ≈ 0.9 or lower | Source/monitor only spans the core | Make `cross` wider than the core (3 µm here) |
| Jagged transmission spectrum | Stopping too early | Lower the `stop_when_fields_decayed` threshold |
| Unexpected mode shape | `EVEN_Y` rather than the intended symmetry in this setup | Use the specified `ODD_Y` parity for this mode |
| `eig_band=0` error | Mistaking bands for zero-based indices | Start at 1 |
| R above 10⁻³ | Thin PML or a guide ending before PML | Check `dpml ≥ λ/2` and length `mp.inf` |

</details>

<details markdown="1">
<summary>Further exploration from the original lesson</summary>

| Change | Expected effect | Quantity to check |
|---------|----------|------------|
| `resolution` 50 → 20 | Slightly larger deviation of T from 1 | \|T − 1\| |
| `w_core` 0.5 → 0.2 µm | Bands 2–3 may fall below n_clad, leaving a single guided mode | n_eff table |
| `dpml` 1.0 → 0.2 µm | Increased PML reflection and R | R |

</details>


<details>
<summary>straight_waveguide.py (expand to read)</summary>
{% highlight python %}
"""Meep Example 04 - Straight waveguide and guided modes.

2D silicon strip waveguide in SiO2. Find the guided mode(s) and their effective index with
the eigenmode solver, inject the fundamental TE mode with EigenModeSource, and measure
modal transmission T and reflection R with mode monitors. Expected: T = 1, R = 0.
Then compare total flux with modal power, and check convergence in resolution and PML.

Run:  python straight_waveguide.py            (~3 min on one core: baseline + 2 convergence runs)
Out:  00_source.png, 01_layout.png, 02_field.png, 03_animation.gif, result.json  (-> ../assets/04/)
"""
import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, animate_fields, annotated_layout, field_figure, record_frames, source_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "04")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# Meep is unit-free. We choose 1 length unit = 1 um, so frequency = 1 / wavelength.
wl   = 1.55              # wavelength [um]
fcen = 1 / wl            # center frequency [1/um]
df   = 0.2 * fcen        # source bandwidth (Gaussian pulse)
df_mon = 0.1 * fcen      # monitor bandwidth
nfreq = 11               # number of frequencies the monitors record

w_core = 0.5             # Si strip width [um]
n_si, n_sio2 = 3.48, 1.44

RESOLUTION = 50          # pixels per um  -> core = 25 px, lambda/n_si = 22 px
DPML = 1.0               # PML thickness [um]
sx, sy = 14.0, 6.0       # cell size [um], PML included

# ---------------------------------------------------------------- (2) materials & geometry
geometry = [mp.Block(center=mp.Vector3(0, 0),
                     size=mp.Vector3(mp.inf, w_core),   # infinite in x: runs straight through the PML
                     material=mp.Medium(index=n_si))]
# background (cladding) is set below via default_material = SiO2

# ---------------------------------------------------------------- (3) source
cross = mp.Vector3(0, 3.0)   # a vertical line 3 um tall: wider than the core to include the evanescent tail
src_x, mon_in_x, mon_out_x = -5.0, -4.0, +5.0
PARITY = mp.ODD_Y            # 2D TE polarization (Ey, Hx, Hz)

sources = [mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=df),
                              center=mp.Vector3(src_x, 0), size=cross,
                              eig_band=1,               # 1-indexed: the fundamental mode
                              eig_parity=PARITY)]
decay_pt = (mon_out_x + 0.5, 0)   # where stop_when_fields_decayed watches (step 6)


# ---------------------------------------------------------------- (4) simulation & boundaries
def build(resolution=RESOLUTION, dpml=DPML):
    """Simulation plus its two mode monitors. One function so every run is set up the same way."""
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy),
                        resolution=resolution,
                        boundary_layers=[mp.PML(dpml)],        # absorbing layer on all four sides
                        geometry=geometry,
                        sources=sources,
                        default_material=mp.Medium(index=n_sio2))
    # ------------------------------------------------------------ (5) monitors
    mon_in = sim.add_mode_monitor(fcen, df_mon, nfreq,
                                  mp.ModeRegion(center=mp.Vector3(mon_in_x, 0), size=cross))
    mon_out = sim.add_mode_monitor(fcen, df_mon, nfreq,
                                   mp.ModeRegion(center=mp.Vector3(mon_out_x, 0), size=cross))
    return sim, mon_in, mon_out


def run_and_measure(sim, mon_in, mon_out):
    # ------------------------------------------------------------ (6) run & stop condition
    sim.run(until_after_sources=mp.stop_when_fields_decayed(
                25,                         # check every 25 time units
                mp.Ey,                      # which field component to watch
                mp.Vector3(*decay_pt),      # where to watch: just past the output monitor
                1e-6))                      # stop when |Ey|^2 has decayed to 1e-6 of its peak
    # ------------------------------------------------------------ (7) post-processing
    ci = sim.get_eigenmode_coefficients(mon_in,  [1], eig_parity=PARITY)
    co = sim.get_eigenmode_coefficients(mon_out, [1], eig_parity=PARITY)
    p_in_fwd  = np.abs(ci.alpha[0, :, 0]) ** 2    # forward mode-1 power at the input monitor   (a_in+)
    p_in_back = np.abs(ci.alpha[0, :, 1]) ** 2    # backward mode-1 power at the input monitor  (a_in-)
    p_out_fwd = np.abs(co.alpha[0, :, 0]) ** 2    # forward mode-1 power at the output monitor  (a_out+)
    flux_in  = np.array(mp.get_fluxes(mon_in))    # TOTAL power through the input plane (all modes, net)
    flux_out = np.array(mp.get_fluxes(mon_out))   # TOTAL power through the output plane
    return {
        "T": p_out_fwd / p_in_fwd,                # modal transmission  (section 2, first formula)
        "R": p_in_back / p_in_fwd,                # modal reflection    (section 2, second formula)
        "T_total": flux_out / flux_in,            # total-flux transmission
        "mode1_fraction_in": p_in_fwd / flux_in,  # how much of the injected power is really mode 1
        "freqs": np.array(mp.get_flux_freqs(mon_in)),
    }


t_all = time.time()
ic = nfreq // 2

# ================================================================ baseline run with figures
sim, mon_in, mon_out = build()

# source waveform and spectrum (same GaussianSource the EigenModeSource wraps)
src_info = source_figure(fcen, df, os.path.join(OUT, "00_source.png"), mon_fcen=fcen, mon_df=df_mon,
                         wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=DPML,
    title="2D Si strip waveguide (w = 0.5 um): TE0 EigenModeSource, mode monitors, PML",
    params_text=f"wl={wl} um  res={RESOLUTION}/um\ncell={sx}x{sy}  dpml={DPML}\nn_si={n_si}  n_sio2={n_sio2}",
    params_xy=(-2.2, 1.85), decay_point=decay_pt, decay_text_xy=(2.6, 1.0),
    labels=[
        Label("Si core (geometry)", (1.5, 0.0), (1.0, -1.2), step=2, color="black"),
        Label("EigenModeSource", (src_x, 1.3), (src_x + 1.2, 2.5), step=3, color="red"),
        Label("mode monitor: in / reflection", (mon_in_x, -1.3), (mon_in_x - 1.0, -2.5), step=5, color="blue"),
        Label("mode monitor: out", (mon_out_x, -1.3), (mon_out_x - 0.6, -2.5), step=5, color="blue"),
    ])

# guided modes of the cross-section: effective index n_eff = k / f  (MPB, called through Meep)
sim.init_sim()
where = mp.Volume(center=mp.Vector3(src_x, 0), size=cross)
neff = {}
for band in (1, 2, 3):
    em = sim.get_eigenmode(fcen, mp.X, where, band, mp.Vector3(0.8 * n_si * fcen, 0, 0), parity=PARITY)
    neff[band] = float(em.k.x / fcen) if em is not None else None
print("n_eff by band:", neff, f"(guided if {n_sio2} < n_eff < {n_si})")

nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * DPML, sy - 2 * DPML))
dft = sim.add_dft_fields([mp.Ey], fcen, 0, 1, where=nonpml)

t0 = time.time()
base = run_and_measure(sim, mon_in, mon_out)
wall_base = time.time() - t0
print(f"T = {base['T'][ic]:.6f}, R = {base['R'][ic]:.2e}, T+R = {base['T'][ic] + base['R'][ic]:.6f}  (wall {wall_base:.1f} s)")
print(f"T_total (flux) = {base['T_total'][ic]:.5f}, mode-1 fraction of input flux = {base['mode1_fraction_in'][ic]:.4f}")
wls = 1 / base["freqs"]
print(f"T over band {wls.min():.3f}-{wls.max():.3f} um: {base['T'].min():.5f} .. {base['T'].max():.5f}")

ey = sim.get_dft_array(dft, mp.Ey, 0)
eps = sim.get_array(vol=nonpml, component=mp.Dielectric)   # structure outline for the figure
extent = [-(sx / 2 - DPML), sx / 2 - DPML, -(sy / 2 - DPML), sy / 2 - DPML]
field_figure(ey, extent, os.path.join(OUT, "02_field.png"), core_halfwidth=None, wl=wl, eps=eps)

# ================================================================ animation: the pulse travels from the source to the output monitor
# A fresh simulation (the one above has already run). Timing from the source: the pulse peaks at
# t0 = 5/df and needs (10 um) * n_eff to reach the output monitor, so record t0 - 2*width .. t0 + 10*n_eff + 5.
sim_anim, _, _ = build()
width = 1.0 / df
t_src = 5.0 / df
frames, times = record_frames(sim_anim, nonpml, mp.Ey, t_start=t_src - 2 * width,
                              t_end=t_src + (mon_out_x - src_x) * neff[1] + 5.0, n_frames=60)
animate_fields(frames, times, extent, os.path.join(OUT, "03_animation.gif"), eps=eps, component="Ey",
               lines=[((src_x, -1.5), (src_x, 1.5), "red", "EigenModeSource"),
                      ((mon_in_x, -1.5), (mon_in_x, 1.5), "blue", "mode monitor in"),
                      ((mon_out_x, -1.5), (mon_out_x, 1.5), "blue", "mode monitor out")],
               aspect="auto", figsize=(8.0, 3.6), title="TE0 pulse, source -> output monitor")

# ================================================================ convergence: resolution x PML
convergence = [{"resolution": RESOLUTION, "dpml": DPML, "T": float(base["T"][ic]), "R": float(base["R"][ic]),
                "T_total": float(base["T_total"][ic]), "wall_s": wall_base}]
for res, dpml in ((25, 1.0), (70, 1.0), (50, 0.5)):   # change one thing at a time
    sim, mon_in, mon_out = build(res, dpml)
    t0 = time.time()
    r = run_and_measure(sim, mon_in, mon_out)
    convergence.append({"resolution": res, "dpml": dpml, "T": float(r["T"][ic]), "R": float(r["R"][ic]),
                        "T_total": float(r["T_total"][ic]), "wall_s": time.time() - t0})
    print(f"convergence res={res} dpml={dpml}: T={r['T'][ic]:.6f} R={r['R'][ic]:.2e} T_total={r['T_total'][ic]:.5f}")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"T": float(base["T"][ic]), "R": float(base["R"][ic]), "T_plus_R": float(base["T"][ic] + base["R"][ic]),
                   "T_total": float(base["T_total"][ic]), "mode1_fraction_in": float(base["mode1_fraction_in"][ic]),
                   "neff": neff, "n_core": n_si, "n_clad": n_sio2,
                   "T_band_min": float(base["T"].min()), "T_band_max": float(base["T"].max()),
                   "wavelengths_um": wls.tolist(), "T_spectrum": base["T"].tolist(), "R_spectrum": base["R"].tolist(),
                   "T_total_spectrum": base["T_total"].tolist(),
                   "source": src_info, "convergence": convergence,
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__},
                  f, indent=2)
{% endhighlight %}
</details>

Unlike the walkthrough excerpts, the complete code includes figure saving and result.json output. The shared plotting helper `blogfig.py` (`annotated_layout`, `field_figure`) lives in the same folder (`code/`). Complete code and helper: [GitHub code folder](https://github.com/jin-castle/meep-examples/blob/main/code).

**Recorded output (rerun on 2026-10-23)**:
```
n_eff by band: {1: 3.153, 2: 2.592, 3: 1.447} (guided if 1.44 < n_eff < 3.48)
T = 1.000000, R = 8.04e-06, T+R = 1.000008  (wall 33.8 s)
T_total (flux) = 1.00000, mode-1 fraction of input flux = 0.9999
T over band 1.476-1.632 um: 0.99999 .. 1.00001
convergence res=25 dpml=1.0: T=0.999996 R=2.13e-04 T_total=1.00000
convergence res=70 dpml=1.0: T=1.000000 R=1.44e-06 T_total=1.00000
convergence res=50 dpml=0.5: T=1.000000 R=8.08e-06 T_total=1.00000
```

**Reproduction environment**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · run `python straight_waveguide.py` (approximately 35 s, single core)


### Further reading

- [Official Mode Decomposition tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/)
- [`EigenModeSource` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#eigenmodesource) · [`get_eigenmode` / mode-decomposition reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#mode-decomposition)
- Next: [05 · Bent waveguide and radius trade-off]({{ site.baseurl }}/en/waveguide-bend-90/)
