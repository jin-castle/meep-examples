---
layout: topic
permalink: /en/metalens/
title: "Metalens phase maps and the PB phase — the ideal lens phase, 2π wrapping, lattice sampling"
title_en: "Metalens phase maps and the PB phase — the ideal lens phase, 2π wrapping, lattice sampling"
lang: en
translation_key: metalens
series: meep-examples
topic_label: METALENS
lesson_title: "Why do metalens fins rotate differently at each position?"
lesson_summary: "Follow the ideal lens phase to understand why identical rectangular fins have different orientations across a lens. The three steps are wrapping the phase into 2π, sampling it on a lattice, and converting it to a rotation angle."
lesson_goals:
  - "Derive the ideal lens phase from equal optical paths and explain where the paraxial quadratic phase fails."
  - "Explain how 2π wrapping and lattice sampling create sawteeth, steps, and the central zero in a phase plot."
  - "Distinguish PB phase from propagation phase and explain the fin patterns near a lens edge."
lesson_prerequisites: "Chapter 06: diffraction orders · Chapter 07: meta-atoms and phase libraries"
calc_note: "The figures use a numpy phase model and 1D scalar angular-spectrum propagation. They are not Meep (FDTD) calculations."
toc:
  - { id: observe, label: "Observe" }
  - { id: ideal, label: "Ideal lens phase" }
  - { id: wrap, label: "2π wrapping and sampling" }
  - { id: pb, label: "PB phase" }
  - { id: edge, label: "Edge patterns" }
  - { id: animation, label: "See the whole process" }
  - { id: verify, label: "Verify the focus" }
  - { id: check, label: "Check your understanding" }
  - { id: reference, label: "Code and references" }
related:
  - { url: "/en/binary-grating/", label: "06 · Diffraction gratings: phase differences set the direction" }
  - { url: "/en/meta-atom/", label: "07 · Meta-atoms: choose propagation phase by width" }
  - { url: "/en/metagrating-inverse/", label: "08 · Inverse design: adjoint optimization where the local periodic approximation fails" }
date: 2026-10-23
tags: [metalens, metasurface, geometric-phase, pancharatnam-berry, phase-wrapping]
image: /assets/meep/metalens/04_ideal_pb.png
excerpt: "Why identical rectangular nanofins sit at different angles across a PB metalens: the ideal lens phase from equal optical paths, 2π wrapping, lattice sampling, and theta = phi/2."
---

<details markdown="1">
<summary>TL;DR (English)</summary>

- **What**: how the phase map of a geometric-phase (Pancharatnam–Berry) metalens is built: ideal hyperbolic lens phase → wrap into 0–2π → sample on a sub-wavelength lattice → set each nanofin angle to θ = φ/2.
- **Result**: in a 1D scalar check (λ = 532 nm, f = 10 µm, NA 0.46, 250 nm lattice) the sampled PB phase focuses with FWHM 499 nm vs 493 nm for the continuous ideal phase, at 0.95 of its peak; the opposite circular polarization diverges.
- **Takeaway**: the isolated zero at the centre of the phase plot, the sawtooth and the triangle/ring fin motifs at the lens edge are all products of wrapping and sampling, not separate design choices.
- **Code**: numpy + matplotlib scripts at the bottom (no Meep run on this page).

</details>

<h2 id="observe">1. Observe: identical fins, different orientations</h2>

SEM images of a metalens using Pancharatnam–Berry (PB) phase show equally sized rectangular pillars, or nanofins, oriented differently at each lattice point. Near the centre, neighbouring fins are almost parallel. Towards the edge, their orientations differ more strongly, creating repeating patterns that resemble triangles or rings. The figure below is a calculated arrangement obtained by sampling the lens-edge phase on a lattice, rather than a photograph. The top row uses the 35° tilted viewpoint common in SEM images; the bottom row shows the same arrangements from above.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/metalens/01_edge_patterns.png' | relative_url }}" data-lightbox aria-label="Enlarge calculated tilted and top views of fin arrays near the lens edge"><img src="{{ '/assets/meep/metalens/01_edge_patterns.png' | relative_url }}" alt="Fin arrays on hexagonal and square lattices with 60° and 80° differences between neighbours" loading="lazy"></a>
<figcaption>In the hexagonal lattice on the left (60° rotation change per cell), tilted fins surround vertical fins in repeating ring patterns. The colours in the bottom row reveal that only a few orientations repeat.</figcaption>
</figure>

These patterns are not separately designed unit structures. They result from converting the required lens phase into rotation angles and placing a fin at each lattice point. The following sections trace that process.

### Where is this useful?

A metalens focuses light using a planar structure a few hundred nm thick instead of a curved lens surface. The phase-map construction is the same across device types; the choice of meta-atom used to implement that phase changes.

| Application | Ideas from this page | What is needed next |
|------|------------------------------|--------------------|
| Flat lenses for smartphones and endoscopes | Ideal lens phase, 2π wrapping, lattice sampling | Polarization-independent meta-atoms (propagation phase in Chapter 07), chromatic-aberration correction |
| Circular-polarization splitting and spin multiplexing | The PB-phase sign changes with circular polarization | FDTD verification of fin heights and widths satisfying the half-wave-plate condition |
| Beam steering and holograms | Phase ramps and the phase change per cell | Inverse design to reduce higher diffraction orders (Chapter 08) |

<h2 id="ideal">2. The ideal lens phase</h2>

To focus a plane wave onto an on-axis point at focal distance $f$, light leaving every point on the lens must arrive with the same phase: the equal-optical-path condition. The distance from radius $r$ to the focus is $\sqrt{r^2+f^2}$. With $k = 2\pi/\lambda$, this gives

$$\varphi(r) + k\sqrt{r^2+f^2} = k f$$

$$\varphi(r) = -k\left(\sqrt{r^2+f^2}-f\right)$$

The phase gradient is $\frac{1}{k}\frac{d\varphi}{dr} = -\frac{r}{\sqrt{r^2+f^2}} = -\sin\theta$, so each point bends light through the angle $\theta$ towards the focus. To image a point source at object distance $s_o$ onto image distance $s_i$, the same condition gives $\varphi(r) = -k\,(L_o + L_i)$, where $L_o = \sqrt{r^2+s_o^2}-s_o$ and $L_i = \sqrt{r^2+s_i^2}-s_i$.

The thin-lens transmission $t(r) = \exp\left(-ik\,r^2/2f\right)$ in Fourier-optics textbooks is the first term of the paraxial expansion of this hyperbolic phase:

$$\varphi(r) = -\frac{k r^2}{2f} + \frac{k r^4}{8 f^3} - \cdots$$

The second and higher terms describe the spherical-aberration error incurred when using a quadratic phase for a high-NA lens. Keeping this term below 1/4 wavelength (the Rayleigh criterion) requires approximately $\mathrm{NA}^4 < 2\lambda/f$.

| Comparison | Conditions | Value |
|------|------|----|
| Approximate upper NA for a useful quadratic phase | f = 1 mm, λ = 0.5 µm | NA ≈ 0.18 |
| Edge phase, hyperbolic | NA 0.8, f = 50 µm, λ = 532 nm | 62.7 wavelengths |
| Edge phase, quadratic | Same lens | 83.5 wavelengths (20.9 more than the hyperbolic phase) |

Quadratic phase also has uses. In the paraxial model, an obliquely incident plane wave adds a linear phase term and shifts the focus sideways without additional aberration. This supports a wider field of view, at the cost of the broader focus when the quadratic approximation is pushed beyond the paraxial regime.

A single flat phase plate cannot satisfy every requirement at once. The hyperbolic phase is aberration-free for normal incidence, but oblique incidence introduces coma. Good off-axis imaging requires the sine condition $h = f\sin\theta$, whereas the simple planar-lens geometry gives $h = f\tan\theta$. Maintaining the same $f$ at every wavelength would also require the entire phase to scale as $1/\lambda$. A phase wrapped into 2π does not generally do this, giving the diffractive chromatic dependence $f \propto 1/\lambda$. A refractive lens produces phase through thickness ($\varphi = k_0(n-1)t(r)$). A thickness profile following the hyperbolic phase is aspheric; an easier-to-manufacture spherical profile departs from this expression and leaves spherical aberration.

<h2 id="wrap">3. 2π wrapping and lattice sampling</h2>

Phase does not distinguish values separated by 2π, so the metasurface only needs to implement $\varphi \bmod 2\pi$. Wrapping a smooth hyperbola into 0–2π makes a sawtooth whose teeth become narrower towards the edge, where the phase gradient ($k\sin\theta$) grows. The centre has $\varphi = 0$, while its neighbour is about $-0.04$ rad, which wraps to $2\pi - 0.04$. The central cell therefore appears to drop to zero in the plot. But 0 and 2π represent the same phase, so this plotting discontinuity does not create a discontinuity in the structure or light. Adding a constant phase across the lens also leaves the focus unchanged; it only shifts the wrapping boundaries.

The metasurface assigns one phase per lattice cell, so it samples the wrapped phase as steps. Recovering the phase requires a change smaller than π between cells (Nyquist), giving the condition on lattice period $U$: $U < \lambda/(2\,\mathrm{NA})$. Exceeding it lets light escape into higher diffraction orders. For a PB lens, the fin-angle change per cell is

$$\Delta\theta \approx 180^\circ \times \frac{U\sin\theta}{\lambda}$$

and increases with radius.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/metalens/02_radius_layout.png' | relative_url }}" data-lightbox aria-label="Enlarge fin orientations at different lens radii"><img src="{{ '/assets/meep/metalens/02_radius_layout.png' | relative_url }}" alt="Lens phase map, rotation change per cell versus radius, and fin arrays at the centre, middle, and edge" loading="lazy"></a>
<figcaption>Beyond the radius where the curve in (b) reaches 60° per cell, only a few orientations repeat, as in (e) and (f). Near the centre in (c), the fins are almost parallel.</figcaption>
</figure>

| Position (NA 0.8, f = 50 µm, λ = 532 nm, U = 300 nm) | Radius | Fin-angle change per cell |
|------------------------------|------|----------------------|
| Centre | 0 µm | 0° |
| Intermediate | 7.5 µm | 15° |
| Three repeating orientations | 36.6 µm | 60° |
| Edge | 66.7 µm | 81° (162° phase, close to the Nyquist limit) |

<h2 id="pb">4. PB phase: rotation sets the phase</h2>

A rectangular fin has different effective refractive indices along its long and short axes. With a suitable height, it acts as a half-wave plate. For circularly polarized input, the component converted to the opposite handedness acquires phase $\exp(\pm i\,2\theta)$. A location requiring phase $\varphi$ therefore uses a fin rotated by $\theta = \varphi/2$; a 0–180° rotation covers 0–2π. The sign depends on the incident circular polarization, so an array that focuses one handedness gives the opposite handedness $-\varphi$ and acts as a diverging lens. Deviations from the half-wave-plate condition leave an unconverted component without the intended geometric phase, producing background light.

Comparing ways to fill the same lattice makes the difference clear. Repeating identical unit cells gives the same phase everywhere, so a plane wave leaves with a flat wavefront and does not focus. A lens needs phase to vary from cell to cell. The pillars in [Chapter 07]({{ site.baseurl }}/en/meta-atom/) select it by width (or diameter for cylindrical pillars); a PB lens selects it by rotation.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/metalens/03_three_types.png' | relative_url }}" data-lightbox aria-label="Enlarge the comparison of identical cells, varying diameters, and varying rotations on the same lattice"><img src="{{ '/assets/meep/metalens/03_three_types.png' | relative_url }}" alt="Repeated identical cells, variable-diameter pillars, and rotated fins, with their centre-row phase profiles" loading="lazy"></a>
<figcaption>The centre-row phase profiles shown below are flat in (1), while (2) and (3) share the same stepped phase. The diameter-to-phase relation is an illustrative linear mapping, not a simulated phase library.</figcaption>
</figure>

| Property | Cylindrical-pillar diameter (propagation phase; Chapter 07 uses 2D bar width) | Rectangular-fin rotation (PB phase) |
|------|-------------------------------|---------------------------|
| Variable selecting phase | Diameter (rotation has no effect) | Rotation angle (fixed dimensions) |
| Phase mechanism | Short waveguide: $k_0 n_\mathrm{eff}(d) H$ | Rotated half-wave plate: $2\theta$ |
| Polarization | Circular symmetry gives polarization independence | Circularly polarized input; the opposite handedness receives $-\varphi$ |
| Building the phase map | Simulate a diameter-to-phase library for each wavelength | Angle directly sets phase once the half-wave-plate condition is met |
| 2π boundary | The widest pillar sits beside the narrowest | Continuous orientation because 0° and 180° have the same shape |
| Fabrication | Multiple diameters; the narrowest pillars and gaps set limits | One size simplifies etch control |

The phase library in Chapter 07 assumes infinitely repeated identical cells, using periodic boundaries. A lens joins different cells from this table through the local periodic approximation (LPA). This works well near the centre, where neighbours are similar, but becomes less accurate near the edge, where phase changes rapidly, and at 2π boundaries in diameter-based lenses. The adjoint inverse design in [Chapter 08]({{ site.baseurl }}/en/metagrating-inverse/) is one way to reduce this mismatch.

<h2 id="edge">5. Why patterns appear near the edge</h2>

Over a small region near the edge, the lens phase is approximately a ramp with constant slope. With a 60° rotation change per cell, a square lattice repeats only 0°, 60°, and 120°. These are the directions of the three sides of an equilateral triangle, so three neighbouring fins resemble a triangle or pinwheel. In a hexagonal lattice, the half-cell row offset creates six angles spaced by 30°. Tilted fins surround vertical fins, producing ring patterns (left side of the figure in Section 1).

The pattern depends on the angle between the radial direction and the lattice axes, and on how closely the rotation step matches a simple integer ratio. Departures from that ratio produce slowly varying moiré patterns. The radial direction changes with azimuth around a circular lens, so the pattern can vary even at the same radius.

<h2 id="animation">6. From a cross-section to the fin arrangement</h2>

<figure class="lesson-figure lesson-animation">
<a href="{{ '/assets/meep/metalens/05_phase_anim.gif' | relative_url }}" data-lightbox aria-label="Enlarge the animation from phase wrapping and sampling to rotation and fin placement"><img src="{{ '/assets/meep/metalens/05_phase_anim.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/metalens/05_phase_anim.gif' | relative_url }}" data-static-src="{{ '/assets/meep/metalens/05_phase_anim_end.png' | relative_url }}" alt="Animation wrapping an ideal phase cross-section by 2π, sampling it, and rotating it around the axis to create a circular phase map and fin arrangement" loading="lazy"></a>
<button class="animation-toggle" type="button" hidden>Pause animation</button>
<figcaption>① Cross-section → ② raise portions below zero by multiples of 2π → ③ sample on a 250 nm lattice → ④ rotate one diameter through 180° to form concentric phase contours → ⑤ square-lattice pixels → ⑥ place fins with θ = φ/2. Pausing shows the final frame, with enlarged centre and edge views.</figcaption>
</figure>

In step ②, the top-view colours at the upper right do not change, because adding 2π preserves phase. The 3D surface in step ④ plots phase as height; all fins in the actual device have the same physical height.

| Final frame (λ = 532 nm, f = 10 µm, U = 250 nm) | Position | Angle difference between neighbouring fins |
|------------------------------|------|------------------|
| Centre close-up | x ≈ 0 µm | About 1° (0° and 178.9°; fins have 180° rotational symmetry) |
| Edge close-up | x ≈ 4 µm | About 31° |

<h2 id="verify">7. Verify that this phase focuses light</h2>

We checked the stepped phase using 1D scalar angular-spectrum propagation. No physical fin geometry is included: each cell is an ideal half-wave plate with 100% conversion efficiency and phase $\exp(i\varphi)$.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/metalens/04_ideal_pb.png' | relative_url }}" data-lightbox aria-label="Enlarge the derivation, mapping, and focus check of an ideal PB metalens phase"><img src="{{ '/assets/meep/metalens/04_ideal_pb.png' | relative_url }}" alt="Equal optical paths, phase before and after wrapping, fin mapping, propagation for two circular polarizations, and focal-plane profiles" loading="lazy"></a>
<figcaption>In (E), the converted circular polarization focuses at z ≈ 10 µm; in (F), the opposite incident handedness diverges. In (G), the stepped-phase focus (red dashed line) has nearly the same width as the continuous ideal-phase focus (grey).</figcaption>
</figure>

| Quantity (λ = 532 nm, f = 10 µm, aperture ±5.12 µm, U = 250 nm) | Value |
|------|----|
| NA | 0.46 |
| Maximum phase change per cell | 77° (< 180°) |
| Focal FWHM, continuous ideal phase | 493 nm |
| Focal FWHM, stepped sampling | 499 nm |
| Peak intensity ratio (stepped / continuous) | 0.95 |
| Focus position | 9.7 µm |
| Fresnel number $a^2/(\lambda f)$ | About 5 |

The focus shifts slightly forward from 10 µm because of diffraction from the small aperture. The continuous phase without steps produces the same focus position.

| What this supports | What this does not establish |
|-------------------|-------------------|
| Wrapping the hyperbolic phase into 2π, sampling it at 250 nm, and mapping it through θ = φ/2 focuses one circular polarization to a diffraction-limited width and diverges the other (ideal fins, 1D scalar model). | Real-fin conversion efficiency, co-polarized leakage, coupling between neighbouring cells, and wavelength dependence. These require 3D FDTD with the actual fin geometry. |

<h2 id="check">8. Check your understanding</h2>

<details markdown="1">
<summary>Question 1. One cell at the centre of the phase plot drops to zero. Is its fin very different from its neighbour?</summary>

No. The centre has φ = 0 and its neighbour has φ ≈ 2π − 0.04 rad; 0 and 2π represent the same phase. The fin angles are 0° and 178.9°, but a rectangular fin has the same shape after a 180° rotation. The two fins therefore differ by only about 1° and are almost parallel.

</details>

<details markdown="1">
<summary>Question 2. Can a metasurface made by regularly repeating identical unit cells act as a lens?</summary>

Not for the plane-wave input considered here. Every cell gives the same phase, so the outgoing wavefront stays flat and no focus forms. A lens requires phase to vary with radius, implemented by varying diameter (propagation phase) or rotation angle (PB phase) between cells.

</details>

<details markdown="1">
<summary>Question 3. What happens when the opposite circular polarization enters the same PB lens?</summary>

The PB phase changes sign to $-\varphi$, so the light spreads as through a diverging (concave) lens. Panel (F) in Section 7 shows this case.

</details>

<h2 id="reference">9. Code and references</h2>

All figures on this page were created with numpy and matplotlib, without Meep. The scripts take the output path as an argument.

| Figure | Script |
|------|----------|
| Section 1: edge patterns | [metalens_edge_patterns.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_edge_patterns.py) |
| Section 3: arrangements at different radii | [metalens_radius_layout.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_radius_layout.py) |
| Section 4: comparison of three approaches | [metalens_three_types.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_three_types.py) |
| Section 6: animation | [metalens_phase_anim.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_phase_anim.py) |
| Section 7: focus verification | [metalens_ideal_pb.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_ideal_pb.py) |

References

- M. Khorasaninejad et al., "Metalenses at visible wavelengths: Diffraction-limited focusing and subwavelength resolution imaging," Science 352, 1190 (2016). [doi:10.1126/science.aaf6644](https://doi.org/10.1126/science.aaf6644) — PB metalenses made by rotating TiO₂ nanofins.
- A. Arbabi et al., "Subwavelength-thick lenses with high numerical apertures and large efficiency based on high-contrast transmitarrays," Nature Communications 6, 7069 (2015). [doi:10.1038/ncomms8069](https://doi.org/10.1038/ncomms8069) — Propagation-phase lenses that select phase through pillar diameter.
- J. W. Goodman, Introduction to Fourier Optics — The quadratic phase transmission function of a thin lens.
