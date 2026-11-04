---
layout: term
permalink: /en/terms/resolution/
lang: en
translation_key: terms-resolution
concept_id: resolution
title: "Resolution and grid spacing — Meep concept dictionary"
term_label: "Resolution"
term_full: "Grid spacing · pixels per wavelength"
axis: numerics
axis_label: "Numerics"
order: 15
lesson_summary: "The grid spacing, set as pixels per unit length. It sets accuracy and cost together, and the time step follows it. There is no way to know in advance which value is enough, so you choose it by doubling it and checking that the result stops changing."
glance:
  - { k: "Meep code", v: "`mp.Simulation(..., resolution=20)` · grid spacing Δx = 1/resolution (in Meep length units a)" }
  - { k: "How to read it", v: "With a = 1 µm, resolution 20 is a 50 nm grid. Pixels per wavelength in a material = resolution × λ₀ / n" }
  - { k: "Official rule of thumb", v: "At least 8 pixels per wavelength in the highest-index lossless material; for metals, enough to resolve the skin depth (tens of nm)" }
  - { k: "Cost", v: "In 3D, doubling the resolution gives 8× the cells × 2× the time steps ≈ 16×" }
  - { k: "Measured on this page", v: "At 4.5 · 8.9 · 17.8 · 35.6 pixels per wavelength in Si, the phase error is 9.2 · 2.15 · 0.51 · 0.13 %, about 1/4 per doubling" }
  - { k: "How to choose", v: "Keep doubling until the reported quantity stays within tolerance ([convergence check](/meep-examples/en/terms/convergence-check/))" }
related:
  - { url: "/en/straight-waveguide/", label: "04 · Does all the light emerge from a straight waveguide?" }
  - { url: "/en/bend-inverse/", label: "09 · How can light find its own path around a bend?" }
  - { url: "/en/ring-resonator/", label: "12 · How long does light remain trapped in a ring?" }
  - { url: "/en/extraction-efficiency/", label: "14 · How much light escapes from a thin film into air?" }
calc_note: "The animation and the first table come from a Meep 1.33.0 run made for this page (code/resolution_dispersion_gif.py, about 20 s on one core)."
tags: [meep, fdtd, resolution, numerical-dispersion, convergence]
---

<h2 id="what">1. What it is</h2>

Meep's `resolution` sets how many grid points go into one length unit a. The grid spacing is $\Delta x = a/\text{resolution}$, and through the [Courant condition]({{ site.baseurl }}/en/terms/courant-condition/) the time step changes with it, $\Delta t = S\,\Delta x / c$. One number sets both the spatial and the temporal discretization.

What sets the accuracy is not the resolution itself but how many pixels fit into the shortest length that matters. The wavelength in a material of index $n$ is $\lambda_0/n$, so the number of pixels per wavelength is

$$N_\lambda = \text{resolution}\times\frac{\lambda_0}{n\,a}$$

With a = 1 µm, λ₀ = 1.55 µm and Si (n = 3.48), resolution 20 gives $N_\lambda$ = 8.9. The official FAQ's rule of thumb is at least 8 pixels per wavelength in the lossless material with the highest index. The wavelength is not the only length, though: thin layers, narrow gaps, the skin depth of metals and the decay length of evanescent fields all need a few pixels too.

Errors from a coarse grid fall into three kinds.

| Error | What goes wrong | Convergence with resolution |
|---|---|---|
| Numerical dispersion | Phase and group velocity on the grid differ from the true ones | Second order ($\propto\Delta x^2$); analytic for a homogeneous medium |
| Geometry discretization | Material boundaries sit on a staircase, misplacing edges and areas | Usually smooth with subpixel averaging, irregular without it |
| Short feature lengths | Thin layers, gaps, evanescent and metal fields represented by a few pixels | Hard to predict while the pixel count is too low |

The official FAQ notes that in practice errors from material inhomogeneities are usually much larger than numerical dispersion. The animation below isolates numerical dispersion alone, in homogeneous Si with no boundaries.

<details markdown="1">
<summary>Going deeper · the 1D Yee dispersion relation</summary>

Substituting a plane wave into the 1D Yee difference equations in a homogeneous medium of index $n$ gives the wavenumber on the grid, $\tilde k$ ($c = 1$):

$$\sin\!\left(\frac{\tilde k\,\Delta x}{2}\right) = \frac{n\,\Delta x}{\Delta t}\,\sin\!\left(\frac{\omega\,\Delta t}{2}\right)$$

As $\Delta x \to 0$, $\tilde k \to n\omega$, the true wavenumber. Expanding for small $\Delta x$, the relative error is $\tilde k/k - 1 \approx (k\Delta x)^2(1 - S^2/n^2)/24$, proportional to the square of the grid spacing. Differentiating with respect to $\omega$ gives the numerical group velocity $v_g = \cos(\tilde k\Delta x/2)/[n\cos(\omega\Delta t/2)]$. With few pixels per wavelength $\cos(\tilde k\Delta x/2)$ drops well below 1, so the pulse as a whole (group velocity) falls behind much more than its phase.

</details>

<h2 id="why">2. Why it matters</h2>

The same pulse travels 28 µm through the same Si with only the resolution changed. The black line is the resolution-80 reference.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-resolution/01_anim_dispersion.gif" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-resolution/01_anim_dispersion.gif" alt="Animation of a pulse (centre wavelength 1.55 µm) travelling through 1D Si (n = 3.48), computed at resolution 10, 20, 40 and 80 and overlaid. Top: Ex over the whole cell. Bottom: a 3 µm window following the resolution-80 pulse peak. The resolution-10 pulse (4.5 pixels per wavelength) is about 7.5 µm behind at t = 111; resolution 20 is visibly out of phase in the window; resolution 40 nearly coincides with the reference." data-animation-src="{{ site.baseurl }}/assets/meep/terms-resolution/01_anim_dispersion.gif" data-static-src="{{ site.baseurl }}/assets/meep/terms-resolution/01_anim_dispersion.png">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
  <figcaption>1D Si (n = 3.48), centre wavelength 1.55 µm, Courant 0.5. Top: the whole cell. Bottom: a 3 µm window following the reference pulse (dots are resolution-10 grid points). At 4.5 pixels per wavelength (red) the pulse ends about 7.5 µm behind the reference, at 8.9 (orange) the phase is visibly off inside the window, and at 17.8 (blue) it nearly coincides.</figcaption>
</figure>

The wavenumber on the grid, measured from the DFT phase between two probes, compared with the Yee dispersion relation:

| Resolution | Pixels per wavelength in Si | Phase error (measured) | Yee theory | Phase lag after 20 µm (≈45 wavelengths) | Group-velocity error (measured / theory) |
|---|---|---|---|---|---|
| 10 | 4.5 | 9.17 % | 10.76 % | 4.1 wavelengths | −27.9 % / −28.6 % |
| 20 | 8.9 | 2.154 % | 2.153 % | 0.97 wavelengths | −6.0 % / −6.3 % |
| 40 | 17.8 | 0.5148 % | 0.5148 % | 0.23 wavelengths | — |
| 80 | 35.6 | 0.1273 % | 0.1273 % | 0.057 wavelengths | — |

<p class="lesson-note">At resolution 20, 40 and 80 measurement and theory agree to four digits, and the error falls by about 1/4 per doubling: second-order convergence. At resolution 10 they differ by 1.6 percentage points; the cause was not investigated. The group-velocity errors at 40 and 80 are below the precision of the pulse-centre method used (about 1 %) and are not listed.</p>

Even near the rule of thumb of 8 pixels per wavelength (resolution 20), the phase falls almost one wavelength behind after 45 wavelengths. For long waveguides, resonators and interferometers, where the phase decides the result, 8 pixels may not be enough. In the real examples, material boundaries and thin layers made the differences larger: the 0.29 µm film of Part 14 was 11.7 pixels thick at resolution 40, and its extraction efficiency differed from resolution 80 by up to 54 %. The inverse design of Part 09 gave a mode-1 transmittance of 0.780 at resolution 10, and 0.639 when the same design was re-measured at resolution 20.

<h2 id="meep-code">3. In Meep code</h2>

```python
# code/resolution_dispersion_gif.py (this page)
def run(res):
    si = mp.Medium(index=N_SI)
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, L), resolution=res, dimensions=1, default_material=si,
                        boundary_layers=[mp.PML(DPML)],
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Ex,
                                           center=mp.Vector3(0, 0, Z_SRC))])
```

- What: `resolution` is one argument of `Simulation`: the number of pixels per length unit a. It has no default.
- Why: compute the pixels per wavelength yourself as resolution × λ₀ / n. Here resolution 20 is 31 pixels per vacuum wavelength but only 8.9 in Si.
- If wrong: choosing the resolution for air leaves a high-index material short by a factor of n. If the reference run and the structure run use different resolutions, [flux normalization]({{ site.baseurl }}/en/terms/flux-normalization/) no longer holds.

```python
# code/straight_waveguide.py (Part 04): change one thing at a time
for res, dpml in ((25, 1.0), (70, 1.0), (50, 0.5)):
    sim, mon_in, mon_out = build(res, dpml)
    r = run_and_measure(sim, mon_in, mon_out)
```

- What: from the baseline (resolution 50, PML 1), two more runs change only the resolution and one changes only the PML.
- Why: whether a resolution is enough cannot be known in advance; you raise it and see whether the result stops changing. The procedure is in [convergence check]({{ site.baseurl }}/en/terms/convergence-check/).
- If wrong: changing the resolution together with another setting hides which one changed the result.

<h2 id="in-examples">4. In the examples</h2>

| Example | Resolution | What set it | When raised |
|---|---|---|---|
| [02 Boundary conditions]({{ site.baseurl }}/en/boundary-pml/) | 12 | Lecture value; 7 cases in 10 s | At 24 the PML reflection metric went 4.5 → 5.1 × 10⁻⁴; the ranking held |
| [03 Reference subtraction]({{ site.baseurl }}/en/reference-subtraction/) | 20 | Cylinder radius 0.75 µm | At 40, R+T+S 0.9988 → 0.9997 and Q_sca 2.515 → 2.628 |
| [04 Straight waveguide]({{ site.baseurl }}/en/straight-waveguide/) | 50 | 0.5 µm Si core | T 0.999996 even at 25 |
| [05 Bend]({{ site.baseurl }}/en/waveguide-bend-90/) | 25 | ε = 12 guide, width 1a | At 40, T 0.200 → 0.189 |
| [09 Bend inverse design]({{ site.baseurl }}/en/bend-inverse/) | 10 (optimization) | Run time | Re-measured at 20: 0.780 → 0.639 |
| [12 Ring resonator]({{ site.baseurl }}/en/ring-resonator/) | 10 (official) | Official example value | At 20 and 30 the frequency stays within 0.3 %; Q goes 1675 → 2132 → 1610 |
| [14 Thin-film extraction]({{ site.baseurl }}/en/extraction-efficiency/) | 80 (cylindrical) | 0.29 µm film | Compared with 40, up to 54 % apart for dipoles high in the layer |

<h2 id="pitfalls">5. Runs, but wrong</h2>

| Symptom | Cause | How to check | Fix |
|---|---|---|---|
| The result keeps changing every time the resolution goes up | A short length (thin layer, gap, evanescent field) spans only a few pixels | Count the pixels across the shortest feature | Raise it to 10 or more pixels there, or save cost with cylindrical or 2D reduction (Part 14) |
| A cavity Q goes up and down with resolution | The staircase boundary lands differently on each grid | Tabulate Q at three or more resolutions | Treat Q as converging more slowly than frequency and report a range (Parts 12, 13) |
| Only structures with metal fail to converge | Subpixel averaging does not apply to dispersive materials (official FAQ) | Compare pixels near the metal boundary with the skin depth | Raise the resolution to resolve the skin depth |
| Phase in a long waveguide or interferometer disagrees with theory | Numerical dispersion accumulates a phase error | Phase error from the table above × propagation length | More pixels per wavelength, or a shorter path |
| A point source's field amplitude grows with resolution | Its current sits in one pixel, so smaller pixels mean higher current density (official FAQ) | Compare flux or LDOS instead of amplitude | Normalize by the incident flux at the same resolution, not by the source amplitude |
| Lowering the resolution makes a dispersive material diverge | A larger Δt crosses the material limit of the [Courant condition]({{ site.baseurl }}/en/terms/courant-condition/) | Compare with a run that lowers only the Courant factor | Lower the Courant factor as well |
| Only the run at a new resolution has odd transmittance | The reference run was reused from the old resolution | Compare the two runs' resolutions | Recompute the reference at the same resolution |

<h2 id="inverse-design">6. In inverse design</h2>

Inverse design has two resolutions: the simulation grid and the grid of design (density) variables. The optimizer sees only the performance measured on the simulation grid, so it can produce a design that exploits that grid's staircase errors or numerical dispersion. This is what happened when the Part 09 design lost its transmittance from 0.780 at resolution 10 to 0.639 at resolution 20.

There are three responses. Optimize at the target resolution, or rerun the last few iterations there. Make the filter radius several simulation pixels wide so the design only carries patterns larger than the grid. Re-measure the final design in a new simulation at a higher resolution before reporting it. The accuracy of the adjoint gradient also depends on the resolution, so run the finite-difference check at the resolution you optimize at.

<h2 id="connections">7. Connections</h2>

- Related concepts: [Convergence check]({{ site.baseurl }}/en/terms/convergence-check/), [Courant condition]({{ site.baseurl }}/en/terms/courant-condition/), [Energy conservation check]({{ site.baseurl }}/en/terms/energy-conservation/)
- Code: [code/resolution_dispersion_gif.py](https://github.com/jin-castle/meep-examples/blob/main/code/resolution_dispersion_gif.py) · results [result.json]({{ site.baseurl }}/assets/meep/terms-resolution/result.json)
- Official Meep documentation: [FAQ: What is a good rule of thumb for the grid resolution?](https://meep.readthedocs.io/en/master/FAQ/#what-is-a-good-rule-of-thumb-for-the-grid-resolution) · [FAQ: How does Meep deal with numerical dispersion?](https://meep.readthedocs.io/en/master/FAQ/#how-does-meep-deal-with-numerical-dispersion) · [Subpixel Smoothing](https://meep.readthedocs.io/en/master/Subpixel_Smoothing/) · [Python API: Simulation](https://meep.readthedocs.io/en/master/Python_User_Interface/#simulation)
- Reference: A. Taflove, S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed., Artech House (2005), ch. 4

<details markdown="1">
<summary>Source waveform (shared by the runs on this page)</summary>

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-resolution/00_source.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-resolution/00_source.png" alt="Time waveform and spectrum of GaussianSource(fcen 1/1.55, fwidth 0.25); peak t0 = 20." loading="lazy">
  </a>
  <figcaption>GaussianSource(fcen = 1/1.55, fwidth = 0.25), peak t0 = 20. The phase comparison uses a single-frequency DFT at the centre frequency.</figcaption>
</figure>

</details>
