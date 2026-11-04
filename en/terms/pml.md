---
layout: term
permalink: /en/terms/pml/
lang: en
translation_key: terms-pml
title: "PML (Perfectly Matched Layer) — Meep concept dictionary"
term_label: "PML"
term_full: "Perfectly Matched Layer"
axis: numerics
axis_label: "Numerics"
order: 20
lesson_summary: "A region at the edge of a finite computational cell that attenuates outgoing waves without sending them back. It is not an absorbing material but a complex stretch of the coordinate, and it occupies the inside of the cell."
glance:
  - { k: "Meep code", v: "`boundary_layers=[mp.PML(thickness)]`" }
  - { k: "Defaults", v: "No default thickness · `R_asymptotic=1e-15` · conductivity turns on quadratically (u²) inside the layer" }
  - { k: "Where it sits", v: "Thickness d inward from each cell edge. The cell does not grow, so the PML-free region is `cell − 2d`" }
  - { k: "Rule of thumb", v: "Start near half the largest wavelength, then keep doubling until the results stop changing (official docs)" }
  - { k: "Measured on this site", v: "Part 02, 2D vacuum point source, reflection metric: no layer 1.03 · Absorber 1 µm 1.9 × 10⁻² · PML 1 µm 4.5 × 10⁻⁴" }
  - { k: "Use instead", v: "`mp.Absorber` where PML fails: periodic media, backward-wave modes, waveguides hitting the edge at an angle, overlap with dispersive materials" }
related:
  - { url: "/en/boundary-pml/", label: "02 · What if light returns from the walls of the computation box?" }
  - { url: "/en/waveguide-bend-90/", label: "05 · How well does light turn a right-angle corner?" }
  - { url: "/en/binary-grating/", label: "06 · Which directions does a grating send light?" }
  - { url: "/en/cavity-ldos/", label: "11 · How does the amount of light change between two mirrors?" }
tags: [meep, fdtd, pml, absorber, boundary]
---

<h2 id="what">1. What it is</h2>

FDTD computes fields only inside a finite box. If you specify nothing at the edges, Meep treats them as perfect electric conductor walls: the tangential electric field is zero there and every wave that arrives is sent back. To simulate a device in open space, waves reaching the edge have to disappear instead of returning.

PML is the boundary region that does this. Inside the layer, the coordinate $x$ normal to the boundary is replaced by a complex coordinate.

$$\tilde{x} = x + \frac{i}{\omega}\int^{x}\sigma(x')\,dx'$$

$\sigma(x)$ rises gradually from zero inside the layer. Substituting this into a plane wave $e^{i(k_x x - \omega t)}$ keeps the oscillation and only reduces the amplitude.

$$e^{ik_x \tilde{x}} = e^{ik_x x}\,\exp\!\left(-\frac{k_x}{\omega}\int^{x}\sigma\,dx'\right)$$

In the continuous equations the impedance at the layer interface matches the outside exactly, so there is no reflection at any frequency or angle of incidence. That is what "matched" means. The official docs describe PML as a medium that in theory absorbs electromagnetic waves at all frequencies and angles without reflection.

On a grid it is different. A $\sigma$ that switches on abruptly creates numerical reflection at the discontinuity, so Meep turns it on slowly as $\sigma \propto u^2$ over the layer depth $u$ (0 → 1). The overall strength is set so that the reflection left in the limit of infinite resolution or thickness is `R_asymptotic` = 10⁻¹⁵. The reflection that actually remains is therefore mostly this discretization reflection, and it shrinks as the layer gets thicker because $\sigma$ then changes more gently. Making a PML thicker does not make the absorption stronger; it makes the ramp gentler.

<details markdown="1">
<summary>Going deeper · why attenuation depends on angle and on the kind of wave</summary>

The attenuation rate above is proportional to $k_x/\omega$. A wave entering at angle $\theta$ in a medium of index $n$ has $k_x/\omega = n\cos\theta / c$, so a wave grazing the boundary ($\theta \to 90°$) is attenuated less for the same thickness. The continuous equations still give zero reflection, but weaker attenuation means more of the wave comes back from the metal wall behind the layer, and discretization reflection matters more. That is why the cell corners are the hardest part of the point-source experiment in Part 02, where waves leave over a wide range of angles.

An evanescent wave $e^{-\kappa x}$ has $k_x = i\kappa$. The same substitution then only changes the phase and adds no extra decay. A standard PML does not speed up the decay of evanescent fields, which is why the official docs recommend making the cell large enough that the evanescent fields of waveguide or cavity modes do not overlap the PML.

`mp.Absorber` turns on scalar electric and magnetic conductivities with the same $u^2$ profile (it is not a PML except in 1D). Without the matching condition it reflects at its entrance, so for the same thickness it reflects more than PML and is usually made thicker.

</details>

<h2 id="why">2. Why it matters</h2>

A wave returned by the boundary adds a reflector that the real device does not have. Transmission, radiation loss, cavity Q and the emission rate of a point source are all affected by this spurious reflection.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-pml/01_anim_pml.gif" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-pml/01_anim_pml.gif" alt="2D vacuum, Ez point source at the centre (wavelength 1.55 µm), resolution 12, 8 × 8 µm interior. Top row, Ez: with no layer the wave returning from the walls fills the interior; with Absorber and PML the wave fades in the outer 1 µm layer. Bottom row, the field sent back by the boundary (a large reference cell subtracted), ×50: saturated for no layer, a pattern reflected at the layer entrance for Absorber, nearly empty for PML." data-animation-src="{{ site.baseurl }}/assets/meep/terms-pml/01_anim_pml.gif" data-static-src="{{ site.baseurl }}/assets/meep/terms-pml/01_anim_pml.png">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
  <figcaption>The same point source with three boundaries (top row Ez, one colour scale). The bottom row shows only what the boundary sent back: the field of a large reference cell that no boundary reaches is subtracted, then magnified 50 times. The reflection at the Absorber's entrance is plain at ×50 (largest metric after t = 20: 4.5 × 10⁻²), while the PML stays nearly invisible at the same magnification (9.5 × 10⁻⁵). The metric is defined as in Part 02, but the source position and time differ, so the numbers are not directly comparable with the table from Part 02.</figcaption>
</figure>
 Part 02 kept the source and the cell fixed, changed only the boundary treatment and measured the field returned by the boundary.

| Boundary treatment | Reflection metric (Part 02, 2D vacuum, res 12) |
|---|---|
| No layer (Meep's default wall) | 1.03 |
| `mp.Absorber(1.0)` | 1.9 × 10⁻² |
| `mp.PML(0.25)` | 1.5 × 10⁻² |
| `mp.PML(0.5)` | 7.9 × 10⁻⁴ |
| `mp.PML(1.0)` | 4.5 × 10⁻⁴ |
| `mp.PML(2.0)` | 4.2 × 10⁻⁴ |

<p class="lesson-note">This metric is the RMS of the field returned by the boundary divided by the time-maximum RMS of the incident field. It is not a power reflectance. Part 02 did not determine why it stops falling near 4 × 10⁻⁴ beyond 0.5 µm (going from resolution 12 to 24 gave 4.5 → 5.1 × 10⁻⁴).</p>

In the waveguide bend of Part 05 this value sets the floor for measuring radiation loss: light leaking out at the corner must be absorbed by the PML before 1 − T − R can be read as radiation loss.

<h2 id="meep-code">3. In Meep code</h2>

### Basic form: the same thickness on every side

```python
# code/boundary_pml.py (Part 02), (4) simulation & boundaries
def make_sim(cell, layers, center=mp.Vector3(), resolution=RESOLUTION):
    """layers = [] (reflecting), [mp.PML(d)] or [mp.Absorber(d)]."""
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=layers, sources=point_source(center), Courant=0.5)

# the layer is ADDED outside the fixed L x L interior
cell = L + 2 * d
```

- What: putting `mp.PML(d)` in `boundary_layers` creates a layer of thickness d inside every side of the cell. An empty list means reflecting walls.
- Why: PML uses the inside of the cell rather than enlarging it. To keep a region of interest L fixed, you must enlarge the cell yourself to `L + 2*d`.
- If wrong: keeping the cell and increasing only d pushes the compared region into the layer. The first run of Part 02 produced the reversed result "thicker PML reflects more" exactly this way.

### Choosing directions and sides

```python
# code/binary_grating.py (Part 06): PML in x only, Bloch-periodic in y
boundary_layers=[mp.PML(DPML, direction=mp.X)], ..., k_point=mp.Vector3()

# code/cavity_ldos.py (Part 11): no z PML, the cell walls are the mirrors
pml = [mp.PML(thickness=DPML, direction=mp.R)]

# code/extraction_efficiency.py (Part 14): bottom has no PML = ground plane
boundary_layers=[mp.PML(DPML, direction=mp.R), mp.PML(DPML, direction=mp.Z, side=mp.High)]
```

- What: `direction` selects which axis gets the layer, and `side` selects both ends (`mp.ALL`, the default) or one of them (`mp.Low`/`mp.High`).
- Why: a periodic structure uses a Bloch-periodic boundary (`k_point`) instead of PML along its period. Leaving PML off a face turns it back into a perfect conductor wall, which is also how you build a mirror or a ground plane on purpose.
- If wrong: adding PML along the period of a grating computes a finite structure truncated by PML, not an infinite periodic one.

### Objects inside the layer

```python
# code/straight_waveguide.py (Part 04)
geometry = [mp.Block(center=mp.Vector3(0, 0),
                     size=mp.Vector3(mp.inf, w_core),   # infinite in x: runs straight through the PML
```

As the official tutorial puts it, the PML is inside the cell and overlaps whatever objects are there. A waveguide must continue through the PML to the cell edge so the mode is attenuated inside the layer. If the waveguide ends in front of the PML, its end facet becomes a reflector.

<h2 id="in-examples">4. In the examples</h2>

| Example | Role of the PML | Placement |
|---|---|---|
| [01 Point and line sources]({{ site.baseurl }}/en/point-line-source/) | Experiments A and B use no PML and stop before the first wall reflection; experiment C opens the vacuum so the flux can be measured | Every side, C only |
| [02 Boundary conditions]({{ site.baseurl }}/en/boundary-pml/) | The object under test | Every side, 0.25–2 µm |
| [04 Straight waveguide]({{ site.baseurl }}/en/straight-waveguide/) · [05 Bend]({{ site.baseurl }}/en/waveguide-bend-90/) | Makes both waveguide ends look infinitely long; absorbs radiation loss | Every side, waveguide passes through |
| [06 Binary grating]({{ site.baseurl }}/en/binary-grating/) · [07 Meta-atom]({{ site.baseurl }}/en/meta-atom/) | Absorbs reflected and transmitted diffracted waves | Propagation direction only; `k_point` along the period |
| [10 3D point-source radiation]({{ site.baseurl }}/en/dipole-pattern-3d/) | Absorbs in the radiation direction, leaves the mirror face open | z only, or one side of z |
| [11 Between two mirrors]({{ site.baseurl }}/en/cavity-ldos/) | Absorbs light leaking sideways | r (or x, y) only; the z walls are the mirrors |
| [13 Rotational symmetry]({{ site.baseurl }}/en/cylindrical-dipole/) · [14 Thin-film extraction]({{ site.baseurl }}/en/extraction-efficiency/) | Absorbs at the r and z boundaries in cylindrical coordinates | r and the top of z; the bottom is a ground plane |

<h2 id="pitfalls">5. Runs, but wrong</h2>

These are cases where the code finishes without error but the numbers are wrong. Start from the symptom and narrow down the cause.

| Symptom | Cause | How to check | Fix |
|---|---|---|---|
| Reflection or loss seems to grow with PML thickness | The measured region or a monitor has entered the PML | In the layout figure, compute the distance from the inner PML boundary to the monitor edge | Enlarge the cell to `L + 2d` to keep the PML-free region fixed (Part 02) |
| Odd fields or emission rate near the source; Harminv Q too low | Evanescent fields of the source or cavity reach the PML and are absorbed artificially (official FAQ) | Double the gap to the PML and see whether the value changes | Increase the gap to at least half a wavelength |
| Every numerical check passes, but the design falls apart at another resolution | A monitor sits exactly on the PML boundary; absorption is still weak there, so results look normal | Before running, compute the distance from monitors, sources and design region to the inner PML boundary | Enlarge the cell or move the monitor inward |
| In a grating or periodic structure, reflection will not go down or the fields diverge | No true PML exists for periodic media; near a band edge the group velocity is small and absorption is weak | Switch to `mp.Absorber` and compare | Use an Absorber and make it thicker |
| Fields grow at a metal interface (surface plasmons) | PML diverges for backward-wave modes | Check whether replacing PML with an Absorber removes it | Use an Absorber |
| Divergence only when a dispersive material runs to the cell edge | Dispersive material overlapping PML is unstable (official Materials page) | End the material before the PML, or switch to an Absorber | Use an Absorber; also check the [Courant condition]({{ site.baseurl }}/en/terms/courant-condition/) |
| Large reflection when the waveguide stops at the cell edge | The waveguide end facet reflects in front of the PML | Change the length to `mp.inf` and compare R | Extend the waveguide to the cell edge |
| Residual fields with a very narrow Gaussian (nearly CW) | High-frequency components from the abrupt turn-on and turn-off are poorly absorbed by PML (official FAQ) | Look at the source spectrum | Use an `fwidth` similar to the measured band |

<p class="lesson-note">The third row happened in a 2D bend inverse-design project. The output monitor sat on the inner PML boundary, yet transmission, energy conservation and the gradient check were all within range; it was found only by looking at the layout figure. Result numbers alone cannot catch a placement error.</p>

<h2 id="inverse-design">6. In inverse design</h2>

An adjoint calculation runs the same cell twice: the forward run sends light from the input source, and the adjoint run sends light backward from the monitor where the objective is measured. Both runs use the same PML, so any reflection the PML leaves ends up in both fields. The gradient is exact for the problem that was simulated, but that problem differs from real open space. The optimizer can find designs that exploit waves returning from the PML, and such designs change performance when the PML changes.

Two checks therefore come first in inverse design. First, before running, compute that the design region and the monitors that become adjoint sources are far enough from the inner PML boundary; the third row of the table above is the case where this was skipped. Second, re-measure the finished design in a new simulation with a different PML thickness or cell size and confirm the performance holds. That is also why [Part 09]({{ site.baseurl }}/en/bend-inverse/) re-measures its final design in a new `Simulation`.

<h2 id="connections">7. Connections</h2>

- Related concepts: [Courant condition]({{ site.baseurl }}/en/terms/courant-condition/) (divergence when dispersive materials overlap PML), [Flux normalization]({{ site.baseurl }}/en/terms/flux-normalization/) (the gap between monitors and the PML)
- Measurements and explanation: [02 · Boundary conditions and PML]({{ site.baseurl }}/en/boundary-pml/)
- Animation code: [code/pml_flux_gif.py](https://github.com/jin-castle/meep-examples/blob/main/code/pml_flux_gif.py) (Meep 1.33.0, about 1 min on one core) · [anim.json]({{ site.baseurl }}/assets/meep/terms-pml/anim.json)
- Official Meep documentation: [Perfectly Matched Layer](https://meep.readthedocs.io/en/master/Perfectly_Matched_Layer/) · [Python API: PML, Absorber](https://meep.readthedocs.io/en/master/Python_User_Interface/#pml) · [FAQ: Checking convergence](https://meep.readthedocs.io/en/master/FAQ/#checking-convergence)
- Reference: S. G. Johnson, [Notes on Perfectly Matched Layers](https://arxiv.org/abs/2108.05348) (MIT course notes, arXiv 2021)
