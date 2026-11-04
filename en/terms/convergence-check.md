---
layout: term
permalink: /en/terms/convergence-check/
lang: en
translation_key: terms-convergence-check
concept_id: convergence-check
title: "Convergence check — Meep concept dictionary"
term_label: "Convergence check"
term_full: "Does the result stop changing when an approximation is refined?"
axis: validation
axis_label: "Validation"
order: 40
lesson_summary: "The procedure of refining each approximation a run makes (resolution, run time, PML thickness, cell padding), one at a time by a factor of two, and checking that the reported result stays within the tolerance you want. No formula tells you the required resolution in advance, so this is the most reliable method."
glance:
  - { k: "Method (official FAQ)", v: "Double the resolution, the run time and the PML thickness one at a time and compare the reported value" }
  - { k: "Verdict", v: "Converged when the reported quantity stays within a tolerance fixed before running" }
  - { k: "What closes first", v: "Energy sums (R+T+S) and frequencies. Individual ratios, Q, efficiencies and optimized-design performance close later" }
  - { k: "Measured on this site", v: "15 quantities from Parts 01–14: sums and frequency within 0.3 %, Q 27 %, thin-film extraction up to 54 %, inverse design 18 %" }
  - { k: "How to report", v: "A table with 2–3 settings and each value. Say so when a quantity has not converged" }
related:
  - { url: "/en/reference-subtraction/", label: "03 · How can we isolate light scattered by an object?" }
  - { url: "/en/straight-waveguide/", label: "04 · Does all the light emerge from a straight waveguide?" }
  - { url: "/en/ring-resonator/", label: "12 · How long does light remain trapped in a ring?" }
  - { url: "/en/extraction-efficiency/", label: "14 · How much light escapes from a thin film into air?" }
calc_note: "The figure is not a new calculation: it collects the numbers published in the convergence tables of Parts 01–14 (code/convergence_overview.py)."
tags: [meep, fdtd, convergence, resolution, validation]
---

<h2 id="what">1. What it is</h2>

A simulation solves a continuous problem on a finite grid, in a finite cell, for a finite time. Each of those replacements introduces an error, and whether that error is small compared with the result you report cannot be known before computing. A convergence check refines one approximation, computes again, and looks at whether the result stays the same.

The official FAQ states that there is no simple formula that tells you in advance how much resolution is needed, and that the most reliable procedure is to double the resolution and verify that the answers you care about do not change to your desired tolerance. It lists the resolution, the run time for Fourier spectra and the PML thickness as things to check by doubling.

| Approximation | Setting to change | Related concept |
|---|---|---|
| Spatial and temporal discretization | `resolution` | [Resolution]({{ site.baseurl }}/en/terms/resolution/) |
| Run time | the `stop_when_fields_decayed` tolerance, `until` | Stop conditions |
| Open boundaries | PML thickness | [PML]({{ site.baseurl }}/en/terms/pml/) |
| Cell size | gaps between structure, boundaries and monitors | Placement clearance |
| Frequency sampling | `nfreq`, DFT band | Flux spectra |
| Cylindrical m series | how many m terms are summed | Cylindrical coordinates |

<details markdown="1">
<summary>Going deeper · estimating the converged value from two points</summary>

If the error scales as the $p$-th power of the grid spacing ($Q(\Delta x) \approx Q_\infty + C\,\Delta x^p$), the results at spacing $\Delta x$ and $\Delta x/2$ give an estimate of the converged value (Richardson extrapolation):

$$Q_\infty \approx Q_{\Delta x/2} + \frac{Q_{\Delta x/2} - Q_{\Delta x}}{2^p - 1}$$

Numerical dispersion in a homogeneous medium has $p = 2$ (in the [resolution]({{ site.baseurl }}/en/terms/resolution/) measurement the error falls to 1/4 per doubling). Errors from material boundaries placed on a staircase have no fixed $p$ and can go up and down, so the extrapolation does not apply. The official FAQ notes that subpixel smoothing often makes convergence faster and smoother. Check first that three or more points decrease monotonically; if they do not, report a range rather than extrapolating.

</details>

<h2 id="why">2. Why it matters</h2>

The values from the convergence tables of Parts 01–14 collected on one figure. Each bar is how much a value moved when the resolution was raised.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-convergence/01_overview.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-convergence/01_overview.png" alt="Relative change of 15 results from Parts 01–14 between two resolutions (log axis). The green power sums (Part 06 T+R 0.04 %, Part 03 R+T+S 0.09 %) and the Part 12 resonance frequency (0.22 %) are below 1 %; the blue individual ratios spread from 0.0004 % to 13 %; the largest are Part 12 Q at 27 %, Part 09 inverse-design transmittance at 18 % and Part 14 thin-film extraction at 54 %." loading="lazy">
  </a>
  <figcaption>Published numbers from the convergence tables of Parts 01–14. Green: energy sums; blue: individual ratios and efficiencies; purple: resonances; red: an optimized design re-measured. The dotted line is 1 %.</figcaption>
</figure>

Three things stand out.

- Sums close first. In the cylinder of Part 03, R+T+S moved by 0.09 % (0.9988 → 0.9997) while R, T and Q_sca inside it moved by 1.6–4.6 %. The 0.1 % agreement of Q_sca with the Mie value at resolution 20 was close to luck.
- Quantities from the same run converge at different rates. In the ring of Part 12 the resonance frequency moved by 0.22 % from resolution 10 to 20 while Q moved by 27%, and at 30 it went back down (1675 → 2132 → 1610).
- Optimized designs and thin structures move most. The Part 09 inverse design changed by 18 %, and the extraction efficiency of dipoles in the 0.29 µm film of Part 14 by up to 54 %.

<p class="lesson-note">So convergence is checked per reported quantity, not once for the whole run. An energy sum closing at 1 does not mean the individual values have converged (<a href="{{ site.baseurl }}/en/terms/energy-conservation/">energy conservation check</a>).</p>

<h2 id="meep-code">3. In Meep code</h2>

```python
# code/straight_waveguide.py (Part 04): convergence, resolution x PML
for res, dpml in ((25, 1.0), (70, 1.0), (50, 0.5)):   # change one thing at a time
    sim, mon_in, mon_out = build(res, dpml)
    r = run_and_measure(sim, mon_in, mon_out)
    convergence.append({"resolution": res, "dpml": dpml, "T": float(r["T"][ic]), "R": float(r["R"][ic]),
                        "T_total": float(r["T_total"][ic]), "wall_s": time.time() - t0})
```

- What: from the baseline (resolution 50, PML 1 µm), one run each with the resolution halved, at 1.4×, and with the PML halved; the same quantities (T, R, T_total) and the run time go into a table.
- Why: only one setting may change at a time, or the cause of a change is unknown. Recording the run time gives the basis for choosing a resolution next time.
- If wrong: changing only the structure run's resolution while keeping the reference run shows a normalization difference, not a resolution difference (Part 09). That is why `build()` and `run_and_measure()` recompute the reference too.

The convergence table is kept in this shape (Part 04):

| Resolution | PML | T | R | Note |
|---|---|---|---|---|
| 50 | 1.0 | 1.000000 | 8.0 × 10⁻⁶ | baseline |
| 25 | 1.0 | 0.999996 | 2.1 × 10⁻⁴ | half resolution |
| 70 | 1.0 | 1.000000 | 1.4 × 10⁻⁶ | 1.4× resolution |
| 50 | 0.5 | 1.000000 | 8.1 × 10⁻⁶ | half PML |

<h2 id="in-examples">4. In the examples</h2>

| Example | Changed | Converged | Not converged |
|---|---|---|---|
| [02 Boundary conditions]({{ site.baseurl }}/en/boundary-pml/) | resolution 12 → 24, PML thickness | Ranking of the boundary treatments | PML reflection floor (4.5 → 5.1 × 10⁻⁴, cause undetermined) |
| [03 Reference subtraction]({{ site.baseurl }}/en/reference-subtraction/) | resolution 20 → 40 | R+T+S | Q_sca 4.5 %, R 4.6 % |
| [04 Straight waveguide]({{ site.baseurl }}/en/straight-waveguide/) | resolution 25, 50, 70; PML | T, R | — |
| [05 Bend]({{ site.baseurl }}/en/waveguide-bend-90/) | resolution 10, 25, 40; PML 1.5 | R 1.8 % | T 5.5 %; a thicker PML moves the monitors and gives T 0.170 |
| [06 Binary grating]({{ site.baseurl }}/en/binary-grating/) | resolution 25 → 50 | Diffraction efficiency 0.08 %, T+R | — |
| [12 Ring resonator]({{ site.baseurl }}/en/ring-resonator/) | resolution 10, 20, 30 | Resonance frequency within 0.3 % | Q (non-monotonic) |
| [14 Thin-film extraction]({{ site.baseurl }}/en/extraction-efficiency/) | resolution 40, 80; cylindrical and 3D | Dipole heights h ≤ 0.4: 2–5 % | h ≥ 0.6: 18–54 % |

<h2 id="pitfalls">5. Runs, but wrong</h2>

| Symptom | Cause | How to check | Fix |
|---|---|---|---|
| Two points agreed, so it looked converged, but a third point differs | The staircase boundary makes the result oscillate and the first two were close by chance | Tabulate three or more points and check they are monotonic | If not monotonic, report a range (Part 12 Q, Part 03 Q_sca) |
| The energy sum is 1 but individual values change with resolution | Errors cancel inside the sum, so it closes first | Put each reported value in the table | Judge by the reported value, not the sum |
| The result changes with resolution and the cause is unclear | Resolution was changed together with PML, cell or monitor position | List what changed | Change one thing at a time; check whether changing the PML thickness also moves the monitors (Part 05) |
| The convergence table jumps around | Too short a run leaves the DFT incomplete | Recompute the baseline with a 10× tighter decay tolerance | Converge the run time before the resolution |
| Only the higher-resolution run has odd normalization | The reference run was reused from another resolution | Compare the two runs' resolutions | Recompute the reference at each resolution |
| Only the band edges fail to converge | Little source power there, so round-off dominates | Check the source spectrum at the edges | Judge by the central band, or widen fwidth |

<h2 id="inverse-design">6. In inverse design</h2>

Inverse design needs convergence checked in two places. The first is the gradient: comparing the adjoint gradient with finite differences also depends on resolution and stop conditions. In a 2D bend project, an adjoint run with a decay tolerance of 10⁻³ stopped early and its gradient disagreed with finite differences by 47 %, while the forward result looked normal. Converge the stop condition on the adjoint run.

The second is the final performance. Optimization usually runs at a low resolution, so the final design must be re-measured in a new simulation at a higher resolution before it can be reported. Part 09 reported its 0.780 at resolution 10 as 0.639 at resolution 20 and wrote that resolution convergence had not been confirmed. A result that has not converged is still useful when it is reported together with that fact.

<h2 id="connections">7. Connections</h2>

- Related concepts: [Resolution]({{ site.baseurl }}/en/terms/resolution/), [Energy conservation check]({{ site.baseurl }}/en/terms/energy-conservation/), [Flux normalization]({{ site.baseurl }}/en/terms/flux-normalization/), [PML]({{ site.baseurl }}/en/terms/pml/)
- Code: [code/convergence_overview.py](https://github.com/jin-castle/meep-examples/blob/main/code/convergence_overview.py) · collected numbers [overview.json]({{ site.baseurl }}/assets/meep/terms-convergence/overview.json)
- Official Meep documentation: [FAQ: Checking convergence](https://meep.readthedocs.io/en/master/FAQ/#checking-convergence) · [Subpixel Smoothing](https://meep.readthedocs.io/en/master/Subpixel_Smoothing/)
