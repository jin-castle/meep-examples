---
layout: term
permalink: /en/terms/courant-condition/
lang: en
translation_key: terms-courant-condition
title: "Courant condition — Meep concept dictionary"
term_label: "Courant condition"
term_full: "Courant–Friedrichs–Lewy (CFL) condition · time-step stability"
axis: numerics
axis_label: "Numerics"
order: 10
lesson_summary: "The stability limit that ties the FDTD time step Δt to the grid spacing Δx. Past the limit, a run starts without any error and then the fields grow exponentially until they diverge. In Meep a single Courant factor S sets it."
glance:
  - { k: "Meep code", v: "`mp.Simulation(..., Courant=0.5)`" }
  - { k: "Definition", v: "c Δt = S Δx. In Meep units (c = 1, Δx = 1/resolution), Δt = S / resolution" }
  - { k: "Default", v: "S = 0.5, stable in 1 to 3 dimensions for vacuum and ordinary dielectrics" }
  - { k: "Stability condition", v: "S ≤ n_min / √D (D = number of dimensions). In vacuum: 1D 1, 2D 0.707, 3D 0.577" }
  - { k: "Measured on this page", v: "2D vacuum: S 0.70 stable, 0.71 diverges · 3D: 0.57 stable, 0.58 diverges · 1D: 1.00 stable, 1.01 diverges" }
  - { k: "If it diverges", v: "With dispersive (Lorentz, Drude) materials, lower the Courant factor or raise the resolution. Run time grows as 1/S" }
related:
  - { url: "/en/point-line-source/", label: "01 · Point or line: how does light spread?" }
  - { url: "/en/boundary-pml/", label: "02 · What if light returns from the walls of the computation box?" }
  - { url: "/en/cylindrical-dipole/", label: "13 · How can rotational symmetry simplify a 3D light calculation?" }
calc_note: "The figure and part of the tables on this page come from a Meep 1.33.0 run made for this page (code/courant_stability.py, about 10 s on one core)."
tags: [meep, fdtd, courant, cfl, stability, dispersive]
---

<h2 id="what">1. What it is</h2>

FDTD updates the electric and magnetic fields on a Yee grid, staggered by half a time step. Each update is explicit and uses only the neighbouring grid points, so there is a limit to how far information can spread in one time step. If the time step is too large compared with the grid spacing, the calculation cannot follow the physical wave, and the shortest pattern on the grid (a component whose sign flips every pixel) is amplified at every step.

Meep sets this relation with the Courant factor $S$.

$$c\,\Delta t = S\,\Delta x$$

In Meep units $c = 1$ and $\Delta x = 1/\text{resolution}$, so $\Delta t = S/\text{resolution}$. For vacuum on a uniform grid, stability requires

$$S \le \frac{n_{\min}}{\sqrt{D}}$$

where $D$ is the number of dimensions and $n_{\min}$ is the smallest refractive index in the cell (usually 1, vacuum). The official docs note that the default of 0.5 is sufficient for one to three dimensions. A material with index below 1 (ε < 1) lowers the limit accordingly.

<details markdown="1">
<summary>Going deeper · where 1/√D comes from</summary>

Substituting a plane wave $e^{i(\mathbf{k}\cdot\mathbf{r}-\omega t)}$ into the Yee difference equations gives the dispersion relation of the grid (von Neumann analysis).

$$\sin\!\left(\frac{\omega\Delta t}{2}\right) = S\sqrt{\sum_{i=1}^{D}\sin^2\!\left(\frac{k_i\Delta x}{2}\right)}$$

For a real $\omega$ to exist for every $\mathbf{k}$, the right-hand side must not exceed 1. It is largest when $k_i\Delta x = \pi$ in every direction, the checkerboard whose sign flips every pixel. There it equals $S\sqrt{D}$, which gives $S \le 1/\sqrt{D}$. Above the limit, $\omega$ for the checkerboard becomes complex and the component grows by a fixed factor each step. Even if it starts at floating-point round-off, it overwhelms every other field within a few hundred steps.

In 1D with $S = 1$ the right-hand side becomes $\sin(k\Delta x/2)$ and grid dispersion vanishes (the "magic time step"). 2D and 3D have no such value, and grid dispersion error is set mainly by the resolution. Lowering S does not reduce the spatial discretization error.

</details>

### With dispersive materials

Lorentz and Drude materials solve one extra equation for each polarization term $P_n$ alongside the field equations.

$$\frac{d^2P_n}{dt^2} + \gamma_n\frac{dP_n}{dt} + \omega_n^2 P_n = \sigma_n\,\omega_n^2\,E$$

The official Materials page says this equation becomes unstable roughly when $\omega_n\Delta t/2 > 1$. With $\omega_n = 2\pi f_n$ and $\Delta t = S/\text{resolution}$, the limit on the resonance frequency is $f_n < \text{resolution}/(\pi S)$. A run can satisfy the vacuum condition and still diverge if a material resonance is high; lowering S or raising the resolution shrinks Δt and raises the limit.

<h2 id="why">2. Why it matters</h2>

A run past this limit starts without any error message. The fields look normal for the first few steps and then grow exponentially. For this page we ran a vacuum cell changing only S.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-courant/01_courant.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-courant/01_courant.png" alt="(a) Time evolution of max|Ez| over the cell for 2D vacuum, resolution 10, PML 1 µm. S 0.50 and 0.70 fall below 10⁻⁹ after the pulse passes; 0.71, 0.72 and 0.75 exceed 10⁶ within a few time units. (b) Sweeping the resonance frequency f_n in a 1D Lorentz medium. At S 0.5 the run diverges from f_n 6.0, at S 0.25 from 11.5. Dashed lines mark the rough limit res/(πS)." loading="lazy">
  </a>
  <figcaption>(a) Five 2D vacuum runs differing only in S. Just below the limit 1/√2 = 0.7071 (0.70) the run is stable; just above it (0.71) it diverges. (b) The resonance frequency at which a 1D Lorentz medium (ε∞ 2.25, σ 0.5, γ 0.05, closed cell) starts to diverge. Halving S raises the onset from 6.0 to 11.5.</figcaption>
</figure>

| Dimension | Theoretical limit 1/√D | Largest stable S | Smallest diverging S | Flagged at |
|---|---|---|---|---|
| 1D (res 20) | 1.000 | 1.00 | 1.01 | t = 21.7 (430 steps) |
| 2D (res 10) | 0.707 | 0.70 | 0.71 | t = 23.4 (329 steps) |
| 3D (res 8) | 0.577 | 0.57 | 0.58 | t = 25.9 (357 steps) |

| Lorentz medium | Rough limit res/(πS) | Largest stable f_n | Smallest diverging f_n |
|---|---|---|---|
| S = 0.5 | 6.37 | 5.5 | 6.0 |
| S = 0.25 | 12.73 | 11.0 | 11.5 |

<p class="lesson-note">A run is flagged as divergent once max|E| exceeds 1000 times its value when the source switches off (t = 20). The vacuum results agree with the theoretical limits to within the 0.01 step. In the Lorentz runs, divergence began 6–10 % below the rough limit. This gap was measured for this one set of material parameters, and the official docs present the formula only as a rough guide.</p>

In real examples the problem shows up with dispersive metals. In a record of the official example `stochastic_emitter_line.py` (emitters above a silver film), run at resolution 16 to save time, the run stopped with NaN/Inf right after `mp.materials.Ag` was initialized at both S 0.5 and S 0.25, and completed at S 0.1. Lowering the resolution enlarges Δt, so the high resonance frequencies of the silver model cross the limit above. In the same record, the S 0.1 result failed a separate resolution-convergence check. Not diverging and being right are different questions.

<h2 id="meep-code">3. In Meep code</h2>

```python
# code/courant_stability.py (this page), A. vacuum
sim = mp.Simulation(cell_size=c["cell"], resolution=c["res"], dimensions=D, Courant=S,
                    boundary_layers=[mp.PML(1.0)],
                    sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=c["comp"],
                                       center=mp.Vector3())])
# time step: dt = S / resolution  (Meep units, c = 1)
```

- What: `Courant` is a single argument of `Simulation`. It defaults to 0.5.
- Why: there is no argument that sets Δt directly. Resolution and S set it together, so doubling the resolution halves Δt and doubles the number of steps for the same simulated time (16 times the work in 3D, with 8 times the cells).
- If wrong: lowering the resolution of an official example while keeping its dispersive material enlarges Δt and can cross the material's limit. Moving a 2D script to 3D with S left at 0.7 exceeds the 3D limit of 0.577.

```python
# code/courant_stability.py, B. Lorentzian medium
medium = mp.Medium(epsilon=2.25, E_susceptibilities=[mp.LorentzianSusceptibility(frequency=fn, gamma=0.05, sigma=0.5)])
```

- What: `frequency` is $f_n$ in the formula above, in Meep frequency units (c/a). With a = 1 µm, $f_n$ = 10 corresponds to a wavelength of 0.1 µm.
- Why: multi-pole fits of metals contain resonances far above visible frequencies. Those poles set the limit on Δt regardless of the band you measure.
- If wrong: fitting your own material model with a high $f_n$ makes it diverge at the same S. The official docs list three remedies: increase the resolution, decrease the Courant factor, or use a different model function.

### The m index in cylindrical coordinates

Cylindrical coordinates (`dimensions=mp.CYLINDRICAL`) compute one angular dependence $e^{im\phi}$ at a time. By default (`accurate_fields_near_cylorigin=False`) Meep forces some field components within |m| pixels of the axis to zero, which keeps the default S of 0.5 stable. If you turn that option on, the official docs say that empirically S must be roughly min(0.5, 1/(|m| + 0.5)) or smaller. Parts 13 and 14 computed m up to 60 but used the default and were stable at S 0.5.

<h2 id="in-examples">4. In the examples</h2>

| Example | Courant | Reason |
|---|---|---|
| [02 Boundary conditions]({{ site.baseurl }}/en/boundary-pml/) | 0.5, set explicitly | Fixed to the lecture notebook's value; suggests an experiment checking whether 0.5 → 0.3 moves the reflection floor |
| Parts 01, 03–12 | Default 0.5 | Only vacuum and non-dispersive dielectrics (Si, SiO₂, ε = 12, …), so only the 1/√D limit applies |
| [10 3D point-source radiation]({{ site.baseurl }}/en/dipole-pattern-3d/) | Default 0.5 | 240 1D Bloch runs; the 1D limit is 1, leaving a wide margin |
| [13 Rotational symmetry]({{ site.baseurl }}/en/cylindrical-dipole/) · [14 Thin-film extraction]({{ site.baseurl }}/en/extraction-efficiency/) | Default 0.5 | Cylindrical m series (up to m 60 in Part 14) with the default near-axis zeroing |

Parts 01–14 contain no dispersive materials, so there was never a reason to change the Courant factor. The moment silver, gold or a hand-fitted Lorentz model enters, Courant becomes a setting that decides the result.

<h2 id="pitfalls">5. Runs, but wrong</h2>

| Symptom | Cause | How to check | Fix |
|---|---|---|---|
| `meep: simulation fields are NaN or Inf`, or fields growing exponentially | S exceeds 1/√D (for example, a 2D script moved to 3D with S unchanged) | Compare S with 1/√D | Set S to 0.5 or below |
| Fine in vacuum, diverges once a metal is added | A dispersive resonance exceeds res/(πS) | Run the smallest case with only the Courant factor changed (everything else fixed) | Lower the Courant factor or raise the resolution |
| Diverges only when a dispersive material runs to the cell edge | Dispersive material overlaps the PML (the first cause in the official FAQ) | End the material before the PML, or switch the [PML]({{ site.baseurl }}/en/terms/pml/) to an Absorber | Use an Absorber |
| Diverges with an ε < 1 material or a constant negative ε | ε < 1 lowers n_min; a constant negative ε is not a numerical instability but a real solution for an unphysical material (official FAQ) | Check the material definition | For ε < 1, keep S below n_min/√D; replace negative ε with a dispersive model |
| Only large m diverges in cylindrical coordinates | `accurate_fields_near_cylorigin=True` combined with S 0.5 | Check the option | Lower S to min(0.5, 1/(\|m\| + 0.5)), or use the default |
| Lowering S stopped the divergence, but results change with resolution | Stability and convergence are separate | Compare two or three resolutions | Check resolution convergence separately |

If you change Courant and resolution together, you cannot tell which one fixed the divergence. The silver-film record above narrowed the cause by first running a case with only the Courant factor changed.

<h2 id="inverse-design">6. In inverse design</h2>

Adjoint optimization repeats forward and adjoint runs tens to hundreds of times with the same Δt. Two things change.

First, run time multiplies by 1/S. Each evaluation is two runs, so lowering S from 0.5 to 0.25 doubles the whole optimization. In inverse design with dispersive materials, find the largest stable S on the starting design before you begin.

Second, optimization often runs at a low resolution and only the final design is re-measured at a higher one ([Part 09]({{ site.baseurl }}/en/bend-inverse/) optimized at res 10 and re-measured at res 20). The dispersive limit $f_n < \text{resolution}/(\pi S)$ is stricter at lower resolution, so an S that was stable at the verification resolution can diverge at the lower optimization resolution. Check S at the resolution you will actually optimize at.

<h2 id="connections">7. Connections</h2>

- Related concepts: [PML]({{ site.baseurl }}/en/terms/pml/) (divergence when dispersive materials overlap PML), [Flux normalization]({{ site.baseurl }}/en/terms/flux-normalization/)
- Code: [code/courant_stability.py](https://github.com/jin-castle/meep-examples/blob/main/code/courant_stability.py) · results [result.json]({{ site.baseurl }}/assets/meep/terms-courant/result.json)
- Official Meep documentation: [Introduction: FDTD methods](https://meep.readthedocs.io/en/master/Introduction/#finite-difference-time-domain-methods) · [Materials: Numerical stability](https://meep.readthedocs.io/en/master/Materials/#numerical-stability) · [FAQ: Why are the fields blowing up?](https://meep.readthedocs.io/en/master/FAQ/#why-are-the-fields-blowing-up-in-my-simulation) · [Python API: Simulation](https://meep.readthedocs.io/en/master/Python_User_Interface/#simulation)
- Reference: A. Taflove, S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed., Artech House (2005), ch. 4 on numerical dispersion and stability

<details markdown="1">
<summary>Source waveform (shared by every run on this page)</summary>

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-courant/00_source.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-courant/00_source.png" alt="Time waveform and spectrum of GaussianSource(fcen 1, fwidth 0.5): width 2, peak t0 = 10, source off at t = 20." loading="lazy">
  </a>
  <figcaption>GaussianSource(fcen = 1, fwidth = 0.5). The peak is at t0 = 10 and the source switches off at t = 20, the reference time for the divergence criterion.</figcaption>
</figure>

</details>
