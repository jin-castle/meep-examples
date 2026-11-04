---
layout: term
permalink: /en/terms/flux-normalization/
lang: en
translation_key: terms-flux-normalization
title: "Flux normalization — Meep concept dictionary"
term_label: "Flux normalization"
term_full: "Flux monitor normalization · two-run normalization and reflection subtraction"
axis: block
axis_label: "Meep building blocks"
order: 30
lesson_summary: "A flux monitor returns values in arbitrary units set by the source strength and spectrum. They become transmittance and reflectance only after dividing by the incident power from a matching reference run, and on the reflection plane the incident field must be subtracted first."
glance:
  - { k: "Meep code", v: "`add_flux` → `get_fluxes` · `get_flux_data` → (in the next run) `load_minus_flux_data`" }
  - { k: "Definition", v: "T(f) = P_tran(f) / P_inc(f), R(f) = −P_refl(f) / P_inc(f), where P_refl is the flux on the reflection plane after the incident field is subtracted" }
  - { k: "What you need", v: "A reference run without the structure, with the same cell, resolution, source, monitor positions and background material" }
  - { k: "Sign", v: "Flux is positive along the positive coordinate direction. A reflection travelling in −x comes out negative, so multiply by −1" }
  - { k: "Measured on this site", v: "Part 04 straight waveguide T 1.0000, R 8 × 10⁻⁶ · Part 05 sharp bend T 0.20, R 0.22, radiated 0.58 · Part 03 cylinder R + T + S 0.999" }
  - { k: "Suspect first", v: "If T > 1 or R < 0, check reference mismatch, band edges and early termination before blaming the structure" }
related:
  - { url: "/en/reference-subtraction/", label: "03 · How can we isolate light scattered by an object?" }
  - { url: "/en/straight-waveguide/", label: "04 · Does all the light emerge from a straight waveguide?" }
  - { url: "/en/waveguide-bend-90/", label: "05 · How well does light turn a right-angle corner?" }
  - { url: "/en/bend-inverse/", label: "09 · How can light find its own path around a bend?" }
tags: [meep, fdtd, flux, normalization, transmission, reflection]
---

<h2 id="what">1. What it is</h2>

`sim.add_flux(fcen, df, nfreq, mp.FluxRegion(...))` Fourier-transforms the tangential electric and magnetic fields on a plane at each frequency and accumulates them while the simulation runs. When the run ends, `mp.get_fluxes(flux)` returns the Poynting flux through that plane, frequency by frequency.

$$P(f) \propto \operatorname{Re}\int_{\text{plane}} \big(\tilde{\mathbf{E}}^{*}(f)\times\tilde{\mathbf{H}}(f)\big)\cdot\hat{\mathbf{n}}\,dA$$

This value is multiplied by the source strength and spectrum $|s(f)|^2$. A Gaussian source has less power away from its centre frequency, so the flux differs between frequencies even for the same structure. As the official FAQ puts it, the Poynting flux is a dimensionful quantity that can take any value, positive or negative. To keep only what the structure did to the light, divide by the flux of a run without the structure, which removes $|s(f)|^2$. This is two-run normalization.

Reflection needs one more step. The reflection plane lies between the source and the structure, so incident and reflected waves cross the same plane. Flux is quadratic in the fields, so the fluxes of the two waves do not simply add; cross terms appear.

$$P[\mathbf{E}_{\text{inc}}+\mathbf{E}_{\text{r}}] = P[\mathbf{E}_{\text{inc}}] + P[\mathbf{E}_{\text{r}}] + (\text{cross terms})$$

Meep therefore subtracts fields, not fluxes. In the reference run you save the Fourier-transformed fields on the reflection plane with `get_flux_data`; in the run with the structure you create the same monitor and immediately load those fields with their sign flipped using `load_minus_flux_data`. From then on, the accumulated value is $\tilde{\mathbf{E}}-\tilde{\mathbf{E}}_{\text{inc}}$, the flux of the reflected (scattered) field alone. The reflection plane must sit at the same position relative to the source in both runs so the phases match.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-flux/01_anim_flux.gif" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-flux/01_anim_flux.gif" alt="The two runs of the Part 05 sharp bend. Top left run 1 straight guide, centre run 2 bend, right their difference. Green line: reflection plane; purple: transmission planes. Bottom: flux accumulated so far at the centre frequency divided by the final P_in of run 1: purple (run 1 P_in) goes from 0 to 1, blue (T) from 0 to 0.20, red (R) starts at −1.05, crosses 0 near t = 65 and rises to 0.22." data-animation-src="{{ site.baseurl }}/assets/meep/terms-flux/01_anim_flux.gif" data-static-src="{{ site.baseurl }}/assets/meep/terms-flux/01_anim_flux.png">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
  <figcaption>The Part 05 sharp bend recomputed with the same settings. What remains left of the reflection plane in the right panel (run 2 − run 1) is the reflected wave. The bottom graph is the flux accumulated while the run proceeds. Run 2 starts with the whole incident field already subtracted, so R(t) begins at −1.05 and reaches 0.22 only after the reflected wave has fully passed the plane (t ≈ 140). Stopping when the source switches off at t = 100 would have given T = 0.011 and R = 0.0002. The start is slightly below −1 because the incident power crossing the reflection plane includes what the line source radiated outside the guide, 5 % more than P_in measured down the guide.</figcaption>
</figure>

<details markdown="1">
<summary>Going deeper · when subtracting fluxes and subtracting fields agree</summary>

If the incident and reflected waves are the forward and backward versions of the same lossless waveguide mode, the real part of the cross terms vanishes and $P_{\text{total}} = P_{\text{inc}} - P_{\text{r}}$. In that case subtracting fluxes also gives the reflectance. When several modes mix, when scattered waves also travel in the incident direction (the cylinder of Part 03), or when the monitor is in the near field, the cross terms remain. Part 03 summed the scattered-field flux over a closed box to obtain the scattering efficiency Q_sca = 2.515, compared with the 2D Mie value 2.513. Measuring the total flux through the same box instead gives the net power leaving the box, which is minus the absorbed power. For a lossless cylinder that is zero and tells you nothing about scattering.

Total flux and the power in a particular mode are also different quantities. A flux monitor counts all power through the plane, every mode and radiation included. To isolate one mode, measure its coefficient $|a|^2$ with `get_eigenmode_coefficients`. In the straight waveguide of Part 04 the two agree at 1.0000; in the bend of Part 05 their difference is what went into radiation and higher-order modes.

</details>

<h2 id="why">2. Why it matters</h2>

Printing `get_fluxes` without normalization, doubling the source amplitude quadruples the value. Such numbers cannot compare one structure with another. Only after dividing by the reference do physical checks such as energy conservation become possible.

| Calculation | Normalized result | Check |
|---|---|---|
| [04 Straight waveguide]({{ site.baseurl }}/en/straight-waveguide/) | T = 1.0000, R = 8.0 × 10⁻⁶ (1.55 µm) | No reflector, so T + R must be 1 |
| [05 Sharp bend]({{ site.baseurl }}/en/waveguide-bend-90/) | T = 0.20, R = 0.22, radiated = 1 − T − R = 0.58 | Recovers to T 0.99 at radius 0.70 µm |
| [03 Dielectric cylinder]({{ site.baseurl }}/en/reference-subtraction/) | R = 0.082, T = 0.674, sideways S = 0.243, sum 0.999 | Lossless, so the sum is 1 |

This is why Part 04 first checks the measurement setup against a known answer (T = 1). If T is not 1 for a straight guide, the source, monitor or normalization is wrong, not the structure.

<h2 id="meep-code">3. In Meep code</h2>

These are the two runs of the bend in Part 05. Run 1 is the straight guide (the reference, standing in for "no structure"); run 2 is the bend.

```python
# code/bend90.py (Part 05), RUN 1: straight guide -> P_in and the incident flux data
sim = make_sim(bend=False, resolution=resolution, dpml=dpml)
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
tran0 = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["tran_straight_x"], ycen), size=span))
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(p["tran_straight_x"], ycen), 1e-6))
P_in = np.array(mp.get_fluxes(tran0))        # what actually travels down the guide
refl_data = sim.get_flux_data(refl)          # incident fields at the reflection plane
```

- What: two monitors, the reflection plane `refl` and the transmission plane `tran0`; run until the fields have decayed, then store the incident power `P_in` and the incident fields on the reflection plane `refl_data`.
- Why: the denominator `P_in` must be the power that actually travels down the guide, not what leaves the source. A line source radiates part of its power outside the guide, and measuring right in front of the source would count that too.
- If wrong: stopping too early leaves the Fourier transforms under-accumulated, so `P_in` itself is wrong, and that error multiplies straight into the T of run 2.

```python
# RUN 2: the bend (same cell, resolution, source, monitor positions)
sim = make_sim(bend=True, radius=radius, resolution=resolution, dpml=dpml)
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
sim.load_minus_flux_data(refl, ref["refl_data"])  # subtract the incident part -> reflection only
tran = sim.add_flux(fcen, df, nfreq,
                    mp.FluxRegion(center=mp.Vector3(xcen, p["tran_bend_y"]), size=mp.Vector3(w + 2, 0)))
sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
T = np.array(mp.get_fluxes(tran)) / ref["P_in"]      # transmitted fraction
R = -np.array(mp.get_fluxes(refl)) / ref["P_in"]     # backward flux is negative -> flip the sign
L = 1.0 - T - R                                      # what is left: radiated out at the corner
```

- What: create the reflection monitor at the same place as in run 1 and subtract the incident field right away. The transmission plane is new, at the bend exit. Both are divided by `P_in` from run 1.
- Why: `load_minus_flux_data` only fits a monitor of the same shape, and the phases match only if its position relative to the source is the same. The reflection travels in −x, so its flux is negative and gets multiplied by −1.
- If wrong: applying `load_minus_flux_data` to the transmission plane as well gives the scattered-field flux, not the total. Changing the cell or resolution in run 2 either fails on mismatched array sizes or, worse, subtracts the wrong fields without failing (Part 03).

<h2 id="in-examples">4. In the examples</h2>

| Example | Denominator (reference) | Notes |
|---|---|---|
| [01 Point and line sources]({{ site.baseurl }}/en/point-line-source/) | Sum over four planes around the source, same run | No reference run, only ratios; a point source gives 0.25 per plane |
| [03 Reference subtraction]({{ site.baseurl }}/en/reference-subtraction/) | Incident flux and fields from a run without the object | 1D Fresnel comparison (error 1.6 × 10⁻⁴); Q_sca from the scattered-field flux through a closed box |
| [04 Straight waveguide]({{ site.baseurl }}/en/straight-waveguide/) | Input plane in the same run | Records both total flux and mode-1 power |
| [05 Bend]({{ site.baseurl }}/en/waveguide-bend-90/) | Straight-guide run | The code above; the reference is recomputed and cached per resolution and PML |
| [06 Binary grating]({{ site.baseurl }}/en/binary-grating/) | Cell with the grating removed and filled with glass | The source is in glass, so the reference background is glass too |
| [07 Meta-atom]({{ site.baseurl }}/en/meta-atom/) | Empty unit cell with ridge width w = 0 | The transmitted phase arg t(w) is also relative to this reference |
| [09 Bend inverse design]({{ site.baseurl }}/en/bend-inverse/) | Mode-1 power of a straight-guide run | The final design is re-measured in a new `Simulation` with the same function |

<h2 id="pitfalls">5. Runs, but wrong</h2>

The official FAQ lists five reasons for reflectance or transmittance below zero or above one. The table adds cases met in this site's examples and is organised by symptom.

| Symptom | Cause | How to check | Fix |
|---|---|---|---|
| T > 1 or R + T > 1 | The reference and structure runs are not comparable (cell, resolution, source, monitor position or background material differs) | Print both runs' settings side by side | Recompute the reference with the same settings; never reuse a reference from another resolution |
| Values jump or exceed 1 at the band edges | Source power at the edge frequencies is so small that round-off dominates | Check the relative source power at the edges | Use an `fwidth` similar to the measured band; do not report edge values |
| T changes when the decay tolerance is tightened | The run stopped before the fields left, so the Fourier transforms are incomplete (bottom graph of the animation in section 1) | Rerun with a 10× tighter tolerance | `stop_when_fields_decayed` at a point near the transmission plane, or `stop_when_dft_decayed` |
| Negative reflectance | The −1 was forgotten, or the monitor is behind the source | Check that the reflection plane lies between the source and the structure | Fix the position and use −flux |
| Transmission too small and 1 − T − R suspiciously large | `load_minus_flux_data` was applied to the transmission plane too, so it measures only the scattered field | Check which monitor received the data | Use it on the reflection plane only |
| A straight reference whose T is not 1 | The reference monitor is too close to the source and counts radiation outside the guide | Move the monitor away from the source and compare `P_in` | Move it farther, or use an `EigenModeSource` |
| Values near the structure change with monitor position | The monitor sits in the near or evanescent field | Shift the monitor slightly and compare | Move it farther from the structure |
| Values change with PML thickness although the monitor did not move | The monitor is inside or on the edge of the PML | Compute the distance from the inner [PML]({{ site.baseurl }}/en/terms/pml/) boundary to the monitor edge | Move it out of the PML |
| Modal transmittance above 1 | Mixing values from two functions with different normalization conventions (\|a\|² from `mpa.EigenmodeCoefficient` and \|α\|² from `get_eigenmode_coefficients`) | Check which function measured numerator and denominator | Re-measure both with the same function (Part 09) |

<h2 id="inverse-design">6. In inverse design</h2>

The objective in adjoint optimization is usually not a flux but the squared mode coefficient $|a|^2$ or the field at a location (`mpa.EigenmodeCoefficient`, `mpa.FourierFields`). That value follows the optimizer's own normalization and is not a transmittance. At the end of the optimization in Part 09 the objective was J = 222.4; dividing it by an input power of 210.6 measured with another function gives 1.056. That is not a transmittance above one but a ratio of two numbers with different conventions. Part 09 put the final design in a new `Simulation`, re-measured it with the same `get_eigenmode_coefficients` as the reference, and reported a mode-1 transmittance of 0.7801.

Dividing the objective by a constant (the reference input power) does not change the direction of the gradient, only its magnitude. During optimization, normalization affects only the step size; when reporting, it decides what the number means. Keep the two uses apart.

Termination becomes stricter. The adjoint run also builds the gradient from the monitors' Fourier-transformed fields, so a decay tolerance that was enough for the forward run can be too loose for the adjoint run. In a 2D bend inverse-design project, an adjoint run with a decay tolerance of 10⁻³ stopped early and its gradient disagreed with finite differences by 47 %, while the forward result looked normal. Set the tolerance by the adjoint run and confirm the gradient against finite differences.

<h2 id="connections">7. Connections</h2>

- Related concepts: [PML]({{ site.baseurl }}/en/terms/pml/) (the gap between monitors and the PML), [Courant condition]({{ site.baseurl }}/en/terms/courant-condition/)
- Measurements and explanation: [03 · Reference subtraction]({{ site.baseurl }}/en/reference-subtraction/) · [05 · Two-run normalization]({{ site.baseurl }}/en/waveguide-bend-90/)
- Animation code: [code/pml_flux_gif.py](https://github.com/jin-castle/meep-examples/blob/main/code/pml_flux_gif.py) (Meep 1.33.0, about 1 min on one core) · [anim.json]({{ site.baseurl }}/assets/meep/terms-flux/anim.json)
- Official Meep documentation: [Basics: Transmittance spectrum of a waveguide bend](https://meep.readthedocs.io/en/master/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend) · [Introduction: Transmittance/reflectance spectra](https://meep.readthedocs.io/en/master/Introduction/#transmittancereflectance-spectra) · [Python API: Flux spectra](https://meep.readthedocs.io/en/master/Python_User_Interface/#flux-spectra) · [FAQ: reflectance/transmittance below zero or above one](https://meep.readthedocs.io/en/master/FAQ/#why-are-my-reflectancetransmittance-values-less-than-zero-andor-greater-than-one)
