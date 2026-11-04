---
layout: term
permalink: /en/terms/energy-conservation/
lang: en
translation_key: terms-energy-conservation
concept_id: energy-conservation
title: "Energy conservation check — Meep concept dictionary"
term_label: "Energy conservation check"
term_full: "Power budget"
axis: validation
axis_label: "Validation"
order: 50
lesson_summary: "A check that the power entering a structure is fully accounted for as reflection, transmission, radiation and absorption, and that the parts add up to the incident power. It quickly catches large mistakes in normalization, monitor placement and stop conditions, but a correct sum does not mean the individual values are correct."
glance:
  - { k: "Definition", v: "Lossless: R + T + (side or radiated flux) = 1; with loss, add the absorbed fraction A" }
  - { k: "In Meep", v: "Divide the flux through every exit plane (or a closed flux box around the structure) by the same incident power and add" }
  - { k: "Catches", v: "Normalization mismatch (sum > 1); missing exits, early termination, monitors in the PML (sum < 1)" }
  - { k: "Misses", v: "Resolution error in individual values. In Part 03 the sum was 0.999 while the scattering efficiency moved by 4.5 %" }
  - { k: "Measured on this site", v: "Part 03 R+T+S 0.9988 / 0.9997 · Part 06 T+R 0.9994 / 0.9998 · Part 04 T+R 1.0000" }
  - { k: "Caution", v: "Defining radiation loss as 1 − T − R (Part 05) makes the sum 1 by construction, so it is not a check" }
related:
  - { url: "/en/reference-subtraction/", label: "03 · How can we isolate light scattered by an object?" }
  - { url: "/en/straight-waveguide/", label: "04 · Does all the light emerge from a straight waveguide?" }
  - { url: "/en/waveguide-bend-90/", label: "05 · How well does light turn a right-angle corner?" }
  - { url: "/en/binary-grating/", label: "06 · Which directions does a grating send light?" }
tags: [meep, fdtd, energy-conservation, flux, validation]
---

<h2 id="what">1. What it is</h2>

For time-harmonic fields, Poynting's theorem says that the average power leaving a closed surface equals the power produced by sources inside minus the power absorbed inside. When light is sent onto a structure, the incident power must therefore split completely into reflection, transmission, sideways scattering or radiation, and absorption.

$$R + T + S + A = 1,\qquad R = \frac{P_{\text{refl}}}{P_{\text{inc}}},\; T = \frac{P_{\text{tran}}}{P_{\text{inc}}},\; S = \frac{P_{\text{side}}}{P_{\text{inc}}}$$

$A$ is the absorbed fraction, zero for a lossless structure. The energy conservation check measures each term separately and looks at whether they add up to 1. Every term must be divided by the same incident power $P_{\text{inc}}$, so [flux normalization]({{ site.baseurl }}/en/terms/flux-normalization/) comes first.

The check quickly catches cases where the code ran without error but the measurement setup is wrong. A sum above 1 usually means a wrong denominator, a forgotten sign on the reflection, or a missing incident-field subtraction. A sum below 1 means a missing exit, a monitor that cuts off the evanescent tail, a run that ended early, or a monitor inside the PML.

<details markdown="1">
<summary>Going deeper · sums that are checks and sums that are not</summary>

For the sum to be a check, each term has to be measured independently. The bend of Part 05 measures only T and R and defines the radiation loss as $L = 1 - T - R$. Then $T + R + L$ is 1 by construction and checks nothing; to check L, the radiated power has to be measured directly with a closed flux box around the structure.

Part 03 surrounded the cylinder with a closed box and measured the flux through all four sides. The net power of the total field leaving the box is minus the absorbed power, so it must be zero for a lossless cylinder. Measured this way, R, T and S summed to 0.9988. By contrast, the scattered-field flux summed over the box (0.496) must be smaller than R+T+S, because the interference terms between scattered and incident fields are missing from it.

</details>

<h2 id="why">2. Why it matters</h2>

The examples on this site ran this check before reporting results.

| Example | Sum | Value | Meaning |
|---|---|---|---|
| [03 Cylinder scattering]({{ site.baseurl }}/en/reference-subtraction/) | R + T + S | 0.9988 (res 20), 0.9997 (res 40) | All four sides of a closed box measured |
| [04 Straight waveguide]({{ site.baseurl }}/en/straight-waveguide/) | T + R | 1.0000 | Measurement setup checked on a structure with no reflector |
| [06 Binary grating]({{ site.baseurl }}/en/binary-grating/) | T + R | 0.9994 (res 25), 0.9998 (res 50) | All diffraction orders through one period plane |
| [05 Bend]({{ site.baseurl }}/en/waveguide-bend-90/) | T + R + L | 1 (by definition) | Not a check: L = 1 − T − R |

But a correct sum and a correct result are different things. In Part 03, R+T+S closed near 1 at both resolution 20 and 40, yet R inside it moved by 4.6 % and the scattering efficiency Q_sca by 4.5 %. When errors move between terms, the sum stays the same. In the figure of the [convergence check]({{ site.baseurl }}/en/terms/convergence-check/), the power sums are also among the fastest of the 15 quantities to close.

<p class="lesson-note">The energy conservation check is a necessary condition. Passing it means there is no gross mistake in normalization or monitor placement; the accuracy of individual values is checked separately by resolution convergence and comparison with analytic results.</p>

<h2 id="meep-code">3. In Meep code</h2>

```python
# code/reference_subtraction.py (Part 03): the closed flux box around the cylinder
REGIONS = {
    "left":   lambda: mp.FluxRegion(center=mp.Vector3(-xm, 0), size=mp.Vector3(0, 2 * ym)),
    "right":  lambda: mp.FluxRegion(center=mp.Vector3(+xm, 0), size=mp.Vector3(0, 2 * ym)),
    "top":    lambda: mp.FluxRegion(center=mp.Vector3(0, +ym), size=mp.Vector3(2 * xm, 0)),
    "bottom": lambda: mp.FluxRegion(center=mp.Vector3(0, -ym), size=mp.Vector3(2 * xm, 0), weight=-1),
}
```

- What: flux monitors on the four sides of a box around the cylinder. `weight=-1` on the bottom side makes outward positive on all four.
- Why: Meep's flux is positive along the positive coordinate direction, so on a closed box each side needs its outward sign before the sum means "power leaving the box".
- If wrong: without the sign, the top and bottom sides cancel, the sideways scattering S comes out near zero, and the sum falls below 1.

```python
# total-field budget: flux DIFFERENCES to the empty run (exact by energy conservation)
R = -(tot["left"] - inc_side["left"]) / inc                            # backward: -x is outward on the left
T = tot["right"] / inc                                                 # what a detector behind the cylinder sees
S = ((tot["top"] - inc_side["top"]) + (tot["bottom"] - inc_side["bottom"])) / inc   # sideways, both signs outward
conservation = sum(outward(tot).values()) / inc                        # total field: must be 0 (lossless)
```

- What: subtract each side's flux from the run without the object (`inc_side`) to get R and S, and divide everything by the same incident power `inc`. `conservation` is the net power the total field sends out of the box.
- Why: for a lossless cylinder `conservation` is 0 and R + T + S is 1. The two are independent checks.
- If wrong: dividing by a different incident power on each side pushes the sum away from 1.

<h2 id="in-examples">4. In the examples</h2>

| Example | How it was measured | Value as a check |
|---|---|---|
| [01 Point and line sources]({{ site.baseurl }}/en/point-line-source/) | Four planes around a point source in vacuum | 0.25 each: sum and symmetry together |
| [03 Reference subtraction]({{ site.baseurl }}/en/reference-subtraction/) | Closed box, total and scattered fields | R + T + S 0.999; scattered-field flux sum 0.496 < 0.999 |
| [04 Straight waveguide]({{ site.baseurl }}/en/straight-waveguide/) | Input and output planes | T + R = 1.0000 is the reference for the setup |
| [05 Bend]({{ site.baseurl }}/en/waveguide-bend-90/) | Input and output planes, L = 1 − T − R | A definition of L, not a check |
| [06 Binary grating]({{ site.baseurl }}/en/binary-grating/) | Reflection and transmission through a full period plane | Sum over all diffraction orders 0.9994 |

<h2 id="pitfalls">5. Runs, but wrong</h2>

| Symptom | Cause | How to check | Fix |
|---|---|---|---|
| Sum above 1 | A different reference in a denominator, a missing reflection sign, the incident field not subtracted on the reflection plane | Print each term's denominator and sign | Divide by the same reference; subtract the incident field on the reflection plane only ([flux normalization]({{ site.baseurl }}/en/terms/flux-normalization/)) |
| Sum below 1 for a lossless structure | A sideways exit was not measured | Surround the structure with a closed box and measure again | Put a monitor on every exit |
| Sum stalls near 0.9 | The monitor plane cuts off the mode's evanescent tail | Widen the monitor and compare | Extend the plane into the cladding |
| Sum differs between runs | The run ended before the fields left | Tighten the decay tolerance and recompute | Check decay at a point near the transmission plane before stopping |
| Sum changes with PML thickness | A monitor sits inside or on the edge of the PML | Compute the distance from the inner [PML]({{ site.baseurl }}/en/terms/pml/) boundary to the monitor edge | Move the monitor out of the PML |
| Lossy material, yet the sum is 1 | Absorption was taken as whatever was left over | Measure absorption directly as the total flux through a closed box | Measure A independently and add it |
| Sum is 1 but values change with resolution | Errors move between terms | Convergence table for each reported value | [Convergence check]({{ site.baseurl }}/en/terms/convergence-check/) |

<h2 id="inverse-design">6. In inverse design</h2>

The objective in inverse design is usually the power in a single output port. The optimizer raises only that value, so a design can finish without anyone knowing how much power went into reflection, other ports or radiation. Re-measure the final design in a new simulation that measures every exit separately, check that the sum is 1, and only then report it. Part 09 measured its mode-1 transmittance of 0.7801 together with the total flux transmittance and recorded the difference of about 0.024 as power that crossed the output plane without being captured by mode 1.

Mixing normalization conventions of different functions can also push a transmittance above 1: in Part 09, dividing J by an input power measured with another function gave 1.056. If an energy check shows values above 1, check that numerator and denominator were measured with the same function before suspecting the structure.

<h2 id="connections">7. Connections</h2>

- Related concepts: [Flux normalization]({{ site.baseurl }}/en/terms/flux-normalization/), [Convergence check]({{ site.baseurl }}/en/terms/convergence-check/), [PML]({{ site.baseurl }}/en/terms/pml/)
- Measurements and explanation: [03 · Reference subtraction]({{ site.baseurl }}/en/reference-subtraction/) · [06 · Binary grating]({{ site.baseurl }}/en/binary-grating/)
- Official Meep documentation: [Introduction: Transmittance/reflectance spectra](https://meep.readthedocs.io/en/master/Introduction/#transmittancereflectance-spectra) · [Basics: Mie scattering of a lossless dielectric sphere](https://meep.readthedocs.io/en/master/Python_Tutorials/Basics/#mie-scattering-of-a-lossless-dielectric-sphere) · [Basics: Absorbed power density map of a lossy cylinder](https://meep.readthedocs.io/en/master/Python_Tutorials/Basics/#absorbed-power-density-map-of-a-lossy-cylinder)
