---
layout: lesson
permalink: /en/parallel-waveguide-force/
lesson_title: "How much force does light exert between two waveguides?"
lesson_summary: "Measure the optical force between two parallel silicon waveguides with the Maxwell stress tensor, cross-check it against the mode-frequency derivative from MPB, and see why fixing ω and fixing k give different curves."
lesson_goals:
  - "Measure a force with add_force and two ForceRegion lines in vacuum, normalized by the transmitted power."
  - "Treat a z-infinite waveguide as a 2D cross-section with a Bloch k_point, and find k at fixed frequency with match_frequency."
  - "Cross-check the stress tensor against Eq.1 of Povinelli 2005 and know where the line monitor stops converging."
lesson_prerequisites: "Chapter 04: EigenModeSource and flux normalization · Chapter 12: Harminv and modes"
date: 2026-11-10
title: "Meep Example 28 · Optical force between two parallel waveguides — the Maxwell stress tensor, the MPB Eq.1 route, and fixed-ω versus fixed-k"
title_en: "Meep Example 28 · Optical force between two parallel waveguides — the Maxwell stress tensor, the MPB Eq.1 route, and fixed-ω versus fixed-k"
lang: en
translation_key: parallel-waveguide-force
series: meep-examples
part: 28
level: intermediate
runtime: "62 s per (s, mode) on one core; 40 runs ≈ 40 min"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Optical_Forces/"
tags: [meep, fdtd, optical-force, stress-tensor, mpb, eigenmode, waveguide, povinelli]
image: /assets/meep/28/02_results.png
excerpt: "two parallel silicon strip waveguides (n 3.45, square a×a, gap s). The coupled modes split into a symmetric and an anti-symmetric branch, and a change of the gap shifts their frequency; that shift is a force. Meep measures the force directly with the Maxwell stress tensor (`add_force`) and MPB gives it from the mode frequency derivative, F = −(1/ω)(dω/ds)|_k U (Eq.1 of Povinelli 2005)."
---
<h2 id="observe">1. Observe: a force between two waveguides</h2>

Can the same pair of waveguides attract or repel depending on the optical mode? In the plots below, compare the signs of the symmetric- and antisymmetric-mode forces and how they change with the gap.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/28/02_results.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/28/02_results.png' | relative_url }}" alt="Optical forces of symmetric and antisymmetric modes versus the gap between parallel silicon waveguides, comparing stress-tensor and MPB results" loading="eager"></a>
<figcaption>Actual Meep and MPB results. Negative force is attractive; positive force is repulsive. Distinguish the fixed-frequency and fixed-wavevector curves.</figcaption>
</figure>

<details markdown="1">
<summary>Calculation summary and runtime</summary>

- **What**: two parallel silicon strip waveguides (n 3.45, square a×a, gap s). The coupled modes split into a symmetric and an anti-symmetric branch, and a change of the gap shifts their frequency; that shift is a force. Meep measures the force directly with the Maxwell stress tensor (`add_force`) and MPB gives it from the mode frequency derivative, F = −(1/ω)(dω/ds)|_k U (Eq.1 of Povinelli 2005).
- **Result**: at the paper's condition (fixed a/λ = 0.2) the symmetric mode is attractive at every gap and matches the paper's Fig.1(c) within 0.04 (dimensionless (F/L)(ac/P), gap 0.1–1.0 a); the anti-symmetric mode is repulsive for s/a ≥ 0.1 with a peak +0.66 at s/a 0.2 and matches for s/a ≥ 0.25. Stress tensor and Eq.1 agree to a median of 2–3 %. The official example fixes k_z = 0.5 instead of ω and therefore draws a different curve (s 0.5: −0.198 vs −0.291 for the symmetric mode).
- **Takeaway**: decide first what is held fixed — ω or k. Inside a narrow gap the stress-tensor line monitor converges slowly (s/a 0.1: Meep +0.50 vs Eq.1 +0.11), so for small gaps trust the mode-frequency derivative. With `find_k` at fixed ω, Eq.1 becomes (F/L)(ac/P) = (1/f)·dk/ds.
- **Code**: full script at the bottom; one (s, mode) run takes ~62 s on one core.

</details>

<details markdown="1">
<summary>Learning scope and applications</summary>

- How to measure a Maxwell-stress-tensor force with `add_force` and `ForceRegion`, and why two line monitors replace a closed box.
- How to handle a waveguide that is infinite along z as a 2D cross-section with a `k_point`, and how `get_eigenmode` with `match_frequency` finds k.
- How to obtain the same force by a second method (MPB, the derivative of the mode frequency) as a cross-check.
- Why the paper (fixed frequency) and the official example (fixed k) draw different curves.

**Prerequisites**: `EigenModeSource` and flux normalization from chapter 04, Harminv and the idea of a mode from chapter 12. **Official example**: the [Optical Forces tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Optical_Forces/), scripts [parallel-wvgs-force.py](https://github.com/NanoComp/meep/blob/master/python/examples/parallel-wvgs-force.py) · [parallel-wvgs-mpb.py](https://github.com/NanoComp/meep/blob/master/python/examples/parallel-wvgs-mpb.py).

Put two waveguides side by side and the evanescent tail of one reaches into the other. Of the two coupled modes, the symmetric mode drops in frequency as the gap narrows and the anti-symmetric mode rises. For a mode carrying energy U = Nħω, changing the gap by Δs changes the energy in proportion to Δω, and that derivative is a force. Two questions: can FDTD measure this force directly (stress tensor), and does the value agree with the mode-frequency derivative and with the paper's figure?

### Where is this useful?

This is the starting point of optomechanics, moving structures with light. For 100 mW in a 310 nm silicon waveguide the force is a few nN/µm, and a 30 µm suspended length bends by about 20 nm (paper Fig.2). The same calculation serves optical tweezers, cavity optomechanics (resonator–mechanics coupling) and self-aligning couplers.

| Application | What it takes from this chapter | What it needs next |
|---|---|---|
| suspended-waveguide optical actuators | (F/L)(ac/P) versus gap | beam mechanics (Euler–Bernoulli) |
| cavity optomechanics | dω/ds (optomechanical coupling g = dω/dx) | chapter 12 resonator Q |
| optical tweezers and particle binding | stress-tensor monitor placement | chapter 03 scattered field |

</details>

<h2 id="predict">2. Predict before viewing the results</h2>

<fieldset class="prediction">
<legend>Does it matter whether frequency ω or wavevector k is held fixed when plotting force against gap?</legend>
<label><input type="radio" name="parallel-waveguide-force-prediction" value="different"> Yes. Different fixed conditions can give different curves.</label>
<label><input type="radio" name="parallel-waveguide-force-prediction" value="same"> No. The same geometry must always give the same curve.</label>
</fieldset>

<details markdown="1">
<summary>Compare the predictions and criteria</summary>

| Quantity | My prediction | Reasoning |
|--------|---------|------|
| sign of the symmetric-mode force | negative everywhere (attractive) | frequency drops as the gap closes |
| anti-symmetric mode | repulsive for s/a ≳ 0.3, turning attractive at small gaps | paper Fig.1(c) |
| stress tensor vs Eq.1 | within 5 % | mathematically the same quantity |
| fixed-k vs fixed-ω curves | different | different paths of the derivative |
| notebook (2020) frequencies | within 1e-6 | same code |

**Decision rule**: if the symmetric mode comes out positive, or the two methods differ by more than 10 %, suspect the force-line positions or the normalization.

</details>

<h2 id="understand">3. Understand: the physics on one page</h2>

{% include chapter-illustration.html %}

Change the gap s adiabatically while k is conserved:

$$
F=-\frac{1}{\omega}\left.\frac{d\omega}{ds}\right|_{k}U,\qquad
\frac{F}{L}\frac{ac}{P}=-\frac{1}{\omega}\frac{d\omega}{ds}\frac{ac}{v_g}
$$

P = v_g U/L is the transmitted power. Negative means attractive. If instead the frequency is fixed and k(s) is found, then dω/ds|_k = −v_g·dk/ds|_ω, so the dimensionless force becomes (1/f)·dk/ds (k in units of 2π/a). The stress tensor integrates the same quantity directly from the fields: the surface integral of T_xx over a surface enclosing one waveguide is the x force.

| Symbol | Meaning | Code variable |
|---|---|---|
| a | waveguide side (= 1) | `a` |
| s | gap (d/a) | `s` |
| k_z | propagation constant (2π/a) | `k_point.z` |
| f | frequency (c/a) | `fcen` |
| (F/L)(ac/P) | dimensionless force | `-force/flux` |

**Assumptions and range of validity**: 2D cross-section + Bloch k_z (infinite along z), lossless n 3.45, vacuum cladding, one mode excited. The paper fixes a/λ = 0.2; the official example fixes k_z = 0.5.

### Simulation layout

![layout]({{ '/assets/meep/28/01_layout_modes.png' | relative_url }})
*(a) Cell 7×5 µm (PML 1), two Si waveguides (gap s = 0.5), two force lines (red x = 0.49 s, orange x = 0.5 s + 1.01 a), green dashed line is the full-cell flux plane. (b)(c) |Ey| of the two modes. (d) Time convergence of the accumulated DFT F/P. (e) Mode frequencies at fixed k — □ current build at res 30, × the 2020 notebook. (f) k_z found at fixed f = 0.2.*

| Item | Value | Source | Note |
|---|---|---|---|
| resolution | 40 px/a | official example | ladder 20/40/80 |
| cell | (5+2)×(3+2), PML 1 | official example | |
| waveguides | n 3.45, a 1, gap s 0.05–1.0 | paper and example | |
| symmetry | Mirror X (±1) · Mirror Y (−1) | example | the x sign selects sym/anti-sym |
| mode | ODD_Y band 1 (sym) / 2 (anti-sym) | example | |
| k or f | k_z 0.5 fixed / f 0.2 fixed (match_frequency) | example / paper | |
| source | EigenModeSource Gaussian fwidth 0.1 f | example | |
| monitors | flux plane z (whole cell), two ForceRegion x lines | example | one line inside the gap |
| termination | until_after_sources 1500 | example | 4e-5 from 3000 |

**Difference from the tutorial notebook**: the official notebook uses res 30 and s from 0.1 in steps of 0.1, and the `data:` (force) lines are not stored. This chapter uses res 40, step 0.05 and both conditions (fixed k and fixed f).

<h2 id="run">4. Run and follow the code</h2>

### ① Parameters — what is held fixed

```python
fixed = "f"           # "k": k_z 0.5 (official example)   "f": a/λ 0.2 (paper)
k_point = mp.Vector3(z=0.5)
```
What: choose the fixed quantity. Why: this is why the paper and the example draw different curves. If wrong: at the same s the symmetric force is −0.20 (fixed k) or −0.29 (fixed f).

### ② Geometry — two blocks with gap s

```python
geometry = [mp.Block(center=mp.Vector3(-0.5*(s+a)), size=mp.Vector3(a, a, mp.inf), material=Si),
            mp.Block(center=mp.Vector3(+0.5*(s+a)), size=mp.Vector3(a, a, mp.inf), material=Si)]
symmetries = [mp.Mirror(mp.X, phase=-1 if xodd else 1), mp.Mirror(mp.Y, phase=-1)]
```
What: the phase of the x mirror selects the symmetric (+1) or anti-symmetric (−1) mode. Why: symmetry cuts the cell to a quarter and keeps only the wanted mode. If wrong: a Y phase of +1 removes the ODD_Y modes and `get_eigenmode` returns a different mode.

### ③ Source — find the mode frequency first

```python
sim.init_sim()
em = sim.get_eigenmode(0.2 if fixed == "f" else 0.22, mp.Z, vol, band, k_point,
                       match_frequency=(fixed == "f"), parity=mp.ODD_Y)
fcen = em.freq;  kz = em.k.z if fixed == "f" else 0.5
```
What: at fixed k, MPB returns the mode frequency at that k; at fixed f, it finds the k at which f = 0.2. Why: the source and monitor frequency and the Bloch k must belong to the same mode. If wrong: passing 0.2 with `match_frequency=False` ignores the input frequency and reproduces the k 0.5 curve.

### ④ Boundaries — a k_point makes z infinite

```python
sim = mp.Simulation(resolution=40, cell_size=cell, geometry=geometry, boundary_layers=[mp.PML(1.0)],
                    symmetries=symmetries, k_point=mp.Vector3(z=kz))
```
What: give the 2D cross-section a Bloch phase along z (complex fields). Why: the waveguide is infinite along z and the mode propagates as e^{ik_z z}. If wrong: without a k_point the 2D problem has no propagation and becomes a 2D resonance problem.

### ⑤ Monitors — one flux plane, two force lines

```python
wvg_flux  = sim.add_flux(fcen, 0, 1, mp.FluxRegion(direction=mp.Z, center=mp.Vector3(), size=mp.Vector3(sx, sy)))
wvg_force = sim.add_force(fcen, 0, 1,
    mp.ForceRegion(mp.Vector3(0.49*s), direction=mp.X, weight=+1, size=mp.Vector3(y=sy)),
    mp.ForceRegion(mp.Vector3(0.5*s + 1.01*a), direction=mp.X, weight=-1, size=mp.Vector3(y=sy)))
```
What: the transmitted power is one flux plane across the whole cell (both waveguides; by symmetry half belongs to one), and the force uses two lines bracketing the right waveguide. Why: the y faces of a closed box cancel by top–bottom symmetry, and per-waveguide flux planes overlap when the gap is narrow. The stress tensor must be evaluated in vacuum. If wrong: a line inside the waveguide runs into the Abraham–Minkowski ambiguity and the value is not defined.

### ⑥ Run — to steady state

```python
sim.run(until_after_sources=1500)
flux = mp.get_fluxes(wvg_flux)[0];  force = mp.get_forces(wvg_force)[0]
```
What: run 1500 more after the Gaussian pulse. Why: the fields do not decay to zero (a waveguide mode), so a fixed time replaces a decay criterion. If wrong: too long and the accumulated DFT grows large enough for rounding error; too short and F/P wobbles (1500 vs 3000: 4e-5).

### ⑦ Postprocessing — −F/P and Eq.1

```python
F_over_P = -force / flux                      # (F/L)(ac/P)
# MPB route at fixed f: k(s) from find_k → (1/f) * dk/ds (centered difference)
```
What: apply the sign convention (negative = attractive) and evaluate Eq.1 from the MPB k(s). Why: two independent methods must agree before the monitor placement can be trusted. If wrong: at fixed f, the example's formula −(1/f)(df/ds)/v_g gives df = 0 and hence zero force.

<h2 id="interpret">5. Interpret the results</h2>

![results]({{ '/assets/meep/28/02_results.png' | relative_url }})
*(a) Example condition (k_z 0.5): Meep stress tensor (points) vs MPB Eq.1 (line, res 64; △ res 128 check). (b) Paper condition (f 0.2): Meep (filled points) vs values read by eye from the paper's Fig.1(c) (○ anti-symmetric, + symmetric) vs MPB find_k Eq.1 (line). (c) Meep − paper. Symmetric within ±0.04, anti-symmetric +0.1 to +0.2 for s/a ≤ 0.2.*

![forward dft]({{ '/assets/meep/28/03_forward_dft.png' | relative_url }})
*(a)(b) |Ey| DFT at the paper condition, s = 0.5; red and orange are the force lines. (c) Stress tensor − Eq.1 (MPB): below 0.05 for s/a ≥ 0.25, diverging in narrow gaps.*

| s/a | sym Meep (f 0.2) | sym paper (by eye) | anti-sym Meep | anti-sym paper | anti-sym MPB Eq.1 |
|---|---|---|---|---|---|
| 0.05 | −1.17 | −1.25 | −0.015 | −2.3 | — |
| 0.10 | −0.92 | −0.95 | +0.500 | +0.10 | +0.11 |
| 0.15 | −0.82 | −0.78 | +0.638 | +0.45 | — |
| 0.20 | −0.69 | −0.65 | +0.664 | +0.55 | — |
| 0.25 | −0.61 | — | +0.645 | +0.57 | — |
| 0.50 | −0.29 | −0.31 | +0.399 | +0.40 | +0.38 |
| 1.00 | −0.09 | −0.10 | +0.116 | +0.13 | — |

![animation]({{ '/assets/meep/28/05_anim_sym.gif' | relative_url }})
*Re Ey(x, y, t) of the s = 0.5 symmetric mode (f 0.2, k 0.386). Because this is a cross-section with a Bloch k, no propagation direction is visible; the two waveguides oscillate in phase. Frames are (n + 1/8) optical periods apart. The strip below is Ey at the center of the right waveguide.*

### Compare with the predictions

| Quantity | My prediction (§2) | Simulation | Verdict |
|--------|-------------|-----------|------|
| symmetric sign | negative everywhere | all 20 points negative, at most 0.039 from the paper | ✅ |
| anti-symmetric shape | repulsive, turning attractive at small gaps | 0.05: −0.015, positive from 0.1 up, maximum +0.664 at 0.2 | ✅ (values 0.1–0.2 above the paper for s/a ≤ 0.15) |
| stress tensor vs Eq.1 | within 5 % | median 1.9 % (fixed k) · 2.6 % (fixed f); s/a 0.1 anti-sym 363 % | ✅ (except narrow gaps) |
| fixed k vs fixed ω | different | s 0.5: sym −0.198 vs −0.291, anti-sym +0.179 vs +0.399 | ✅ |
| notebook frequencies | within 1e-6 | uniformly +0.5 % (4.6–7.8e-3) | ❌ |

Four of five predictions held. The 20 frequency lines of the notebook (2020-05) come out 0.5 % high when rerun in the current Meep 1.33 at the same res 30. Unlike the Harminv and LDOS routes of chapters 11 and 13, which matched the 2019–2020 numbers to 1e-9, the `get_eigenmode` numbers (MPB boundary smoothing) move at the 1e-3 level between builds. The force ratio −F/P is less sensitive. In narrow gaps the anti-symmetric stress-tensor force is larger than both the paper and Eq.1. A gap of 0.1 is 4 px at res 40 and the inner force line sits 1–2 px from the wall, so the grid cannot hold the Ex enhancement inside the gap (the cause of the paper's d → 0 limit of −21.54). Even at res 80 it moves only slowly, 0.466 → 0.458 (fixed k, s 0.1).

### Convergence

| Variable | Values | Result | Note |
|---|---|---|---|
| resolution (fixed k) | 20 / 40 / 80 | s 0.5: sym −0.198/−0.198/−0.195, anti-sym +0.155/+0.179/+0.180; s 0.1 anti-sym +0.481/+0.466/+0.458 | 40→80 at most 1.7 % |
| run time | 1500 / 3000 | relative difference ≤ 4.2e-5 | 1500 suffices |
| Meep − MPB (s 0.5) | res 40 → 80 | 0.0011 → 0.0002 (anti-sym), 0.0023 → 0.0006 (sym) | ratios 0.16 · 0.27 — a discretization component |
| MPB resolution | 64 / 128 | force differs ≤ 2.4 % (fixed k) · 1.1 % (fixed f) | |

### What the results do and do not establish

- Established: at fixed a/λ 0.2, the attractive symmetric-mode curve (s/a 0.1–1.0) and the anti-symmetric curve for s/a ≥ 0.25 agree with the paper's Fig.1(c) within the eye-reading error. The stress tensor and the mode-frequency derivative give the same force (except in narrow gaps). The official example's curve (k_z 0.5) is not the paper's curve.
- Not established: the anti-symmetric force for s/a ≤ 0.15 and the d → 0 limit (−1.49/−21.54) — the resolution is insufficient. The paper values are read from the figure by eye (±0.08). Finite-length and substrate (SOI) effects are absent in a 2D cross-section with k.

### Common mistakes

| Symptom | Cause | Fix |
|------|------|----------|
| whole curve disagrees with the paper | fixed k_z (example) vs fixed ω (paper) | find k with `match_frequency=True` and rebuild the k_point |
| all MPB forces are zero | the example's formula with df = 0 at fixed f | (1/f)·dk/ds |
| narrow-gap force differs from Eq.1 | force line 1–2 px from the wall | raise the resolution or use Eq.1 |
| force sign reversed | weight signs, −force/flux convention | negative = attractive throughout |
| F/P wobbles with time | until too short | 1500 or more, compare with 3000 |
| 1e-3 difference from the notebook | eigenmode-solver build differences | compare force ratios |

### Try it yourself

| Change | Expected change | Number to check |
|---------|----------|------------|
| resolution 160, s/a 0.05–0.15 anti-sym | approaches the paper's +0.10 (0.1) · −2.3 (0.05) | force at s 0.1 |
| inner force line 0.49 s → 0.3 s | must be the same anywhere inside the gap | difference by line position |
| Hz-polarized (TE) mode | a different curve | sign-change position |
| a/λ 0.15 · 0.25 | coupling strength changes | force at s 0.5 |

<h2 id="check">6. Check your understanding</h2>

1. Explain why the symmetric-mode force is negative in terms of how the frequency depends on the gap. (§3)
2. At fixed f, why does the example's formula −(1/f)(df/ds)/v_g give zero when used with MPB Eq.1? (§4 ⑦)
3. At s/a 0.1 the stress tensor and Eq.1 differ by a factor of five — which one should you trust, and why? (§5)

<h2 id="reference">7. Full code and references</h2>

`code/parallel_waveguide_force.py` — computes one (s, mode, fixed) combination and saves JSON. The sweep over s 0.05–1.0, mode odd/even and fixed k/f runs outside. The MPB route is `parallel-wvgs-mpb.py` plus `find_k` to obtain the propagation constant at fixed frequency.

<details>
<summary>parallel_waveguide_force.py (click to expand)</summary>
{% highlight python %}
"""Optical force between two parallel Si waveguides (Povinelli 2005 Fig.1(c) / Meep parallel-wvgs-force.py).
--fixed k : official example (k_z 0.5 fixed)    --fixed f : paper condition (a/lambda 0.2 fixed, k found by match_frequency)
"""
import argparse, json, os
import numpy as np
import meep as mp

ap = argparse.ArgumentParser()
ap.add_argument("--s", type=float, required=True)            # gap s/a
ap.add_argument("--mode", choices=["odd", "even"], required=True)  # odd = anti-symmetric, even = symmetric
ap.add_argument("--fixed", choices=["k", "f"], default="k")
ap.add_argument("--f0", type=float, default=0.2)
ap.add_argument("--resolution", type=float, default=40)
ap.add_argument("--after", type=float, default=1500)
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

Si = mp.Medium(index=3.45)
dpml, sx, sy, aa = 1.0, 5, 3, 1.0
cell = mp.Vector3(sx + 2 * dpml, sy + 2 * dpml, 0)
s, xodd = a.s, a.mode == "odd"
geometry = [mp.Block(center=mp.Vector3(-0.5 * (s + aa)), size=mp.Vector3(aa, aa, mp.inf), material=Si),
            mp.Block(center=mp.Vector3(+0.5 * (s + aa)), size=mp.Vector3(aa, aa, mp.inf), material=Si)]
symmetries = [mp.Mirror(mp.X, phase=-1 if xodd else 1), mp.Mirror(mp.Y, phase=-1)]
band = 2 if xodd else 1
k_point = mp.Vector3(z=0.5)

# (1) mode frequency (fixed k) or wavevector (fixed f)
sim = mp.Simulation(resolution=a.resolution, cell_size=cell, geometry=geometry, boundary_layers=[mp.PML(dpml)],
                    symmetries=symmetries, k_point=k_point)
sim.init_sim()
vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx, sy))
if a.fixed == "k":
    em = sim.get_eigenmode(0.22, mp.Z, vol, band, k_point, match_frequency=False, parity=mp.ODD_Y)
    fcen, kz = float(np.real(em.freq)), 0.5
else:
    em = sim.get_eigenmode(a.f0, mp.Z, vol, band, k_point, match_frequency=True, parity=mp.ODD_Y)
    fcen, kz = float(np.real(em.freq)), float(em.k.z)
    k_point = mp.Vector3(z=kz)
sim.reset_meep()

# (2) launch the mode, measure flux (power) and stress-tensor force on the right waveguide
sim = mp.Simulation(resolution=a.resolution, cell_size=cell, geometry=geometry, boundary_layers=[mp.PML(dpml)],
                    symmetries=symmetries, k_point=k_point)
sim.change_sources([mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=0.1 * fcen), size=mp.Vector3(sx, sy),
                                       center=mp.Vector3(), eig_band=band, eig_kpoint=k_point, eig_match_freq=False,
                                       eig_parity=mp.ODD_Y)])
wvg_flux = sim.add_flux(fcen, 0, 1, mp.FluxRegion(direction=mp.Z, center=mp.Vector3(), size=mp.Vector3(sx, sy)))
wvg_force = sim.add_force(fcen, 0, 1,
                          mp.ForceRegion(mp.Vector3(0.49 * s), direction=mp.X, weight=1, size=mp.Vector3(y=sy)),
                          mp.ForceRegion(mp.Vector3(0.5 * s + 1.01 * aa), direction=mp.X, weight=-1, size=mp.Vector3(y=sy)))
sim.run(until_after_sources=a.after)
flux = float(mp.get_fluxes(wvg_flux)[0]); force = float(mp.get_forces(wvg_force)[0])
out = dict(s=s, mode=a.mode, fixed=a.fixed, fcen=fcen, kz=kz, flux=flux, force=force, F_over_P=-force / flux)
if mp.am_master():
    json.dump(out, open(os.path.join(a.out, f"{a.fixed}_{a.mode}_s{s}.json"), "w"), indent=1)
    print(f"data:, {a.mode}, {s}, F/P {-force / flux:+.5f}  (fixed {a.fixed}, f {fcen:.6f}, kz {kz:.6f})")
{% endhighlight %}
</details>

### Further reading

- M. L. Povinelli et al., "Evanescent-wave bonding between optical waveguides," Opt. Lett. 30, 3042 (2005); arXiv physics/0509073.
- P. T. Rakich, M. A. Popović, Z. Wang, Opt. Express 17, 18116 (2009) — equivalence of Eq.1 and the stress tensor.
- Meep documentation: [Optical Forces](https://meep.readthedocs.io/en/latest/Python_Tutorials/Optical_Forces/), [Force spectra](https://meep.readthedocs.io/en/latest/Python_User_Interface/#force-spectra).
- Mode sources: [04 · A straight waveguide]({{ site.baseurl }}/en/straight-waveguide/) · Resonator modes: [12 · A ring that confines light]({{ site.baseurl }}/en/ring-resonator/)
