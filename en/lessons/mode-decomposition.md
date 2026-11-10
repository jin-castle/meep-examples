---
layout: lesson
permalink: /en/mode-decomposition/
lesson_title: "When do modal power and total flux agree?"
lesson_summary: "Compare backward fundamental-mode power with signed, reference-subtracted flux in a linear taper. Diagnose a saved resolution-50 case with negative reflection estimates through measurement definitions, forward residuals and failed convergence."
lesson_goals:
  - "Read the propagation direction and power normalization of complex mode coefficients."
  - "Distinguish selected-mode power from all power crossing a monitor."
  - "Preserve negative estimates and separate a failed measurement from physical reflectance."
lesson_prerequisites: "Chapter 03: reference subtraction · Chapter 04: guided modes · Chapter 05: bend loss"
date: 2026-11-11
title: "Meep Example 27 · Counting selected modes — taper decomposition and flux diagnostics"
title_en: "Meep Example 27 · Counting selected modes — taper decomposition and flux diagnostics"
lang: en
translation_key: mode-decomposition
series: meep-examples
part: 27
level: intermediate
runtime: "Saved Lt 1,2,4,8 sweep: approximately 477 s at res 25; 1,051 s at res 50"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#reflectance-of-a-waveguide-taper"
tags: [meep, fdtd, waveguide, taper, mode-decomposition, flux, diagnostics]
image: /assets/meep/27/02_diagnostic.en.png
excerpt: "Compare reflected fundamental-mode power with total signed flux in a 1-to-2 µm taper. Preserve negative estimates and forward residuals while learning how to validate a measurement."
---
<h2 id="observe">1. Observe: a finer grid gives negative reflection?</h2>

Chapters 04–05 measure waveguide power. Now resolve power in a selected mode. A linear taper joins widths 1 and 2 µm over lengths Lt = 1, 2, 4 and 8 µm. Will backward fundamental-mode power agree with signed flux through the reflection plane?

<figure class="lesson-figure">
<a href="{{ '/assets/meep/27/02_diagnostic.en.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/27/02_diagnostic.en.png' | relative_url }}" alt="Fundamental-mode reflection and signed flux estimates at resolutions 25 and 50, with the forward fundamental-mode residual after reference subtraction" loading="eager"></a>
<figcaption>Actual Meep 1.33.0 diagnostic data saved on 2026-11-08. Negative values are neither replaced by their magnitude nor clipped to zero. The right panel is a forward residual at the reflection plane after subtraction, not output transmission.</figcaption>
</figure>

At resolution 25 both estimates are positive and decrease with length. At resolution 50 the signed flux reflection estimates are **−0.00477…−0.00521**. A passive, lossless structure does not have negative physical reflectance: **this reflection measurement has failed validation**.

This lesson diagnoses a saved failure. It does not validate agreement between both methods or a 1/Lt² scaling law. Figures reuse existing data; no new simulation was run.

<h2 id="predict">2. Predict: what comes before a smooth curve?</h2>

<fieldset class="prediction">
<legend>What should you do with a negative resolution-50 reflection estimate?</legend>
<label><input type="radio" name="mode-decomposition-prediction" value="diagnose"> Preserve its sign and check the reference, forward residual and convergence.</label>
<label><input type="radio" name="mode-decomposition-prediction" value="absolute"> Take its magnitude and report a small reflectance.</label>
</fieldset>

Deleting negative points because a logarithmic axis cannot show them would conceal the failure. The diagnostic plot uses a linear axis with signs preserved; only the positive resolution-25 data appear separately on log axes.

<h2 id="understand">3. Understand: mode coefficients have directions</h2>

{% include chapter-illustration.html %}

Mode decomposition projects complex DFT fields at a monitor onto eigenmodes. For this +x-oriented setup, `alpha[0,0,0]` denotes the forward fundamental coefficient and `alpha[0,0,1]` the backward coefficient. Their squared magnitudes, divided by reference incident power, give the corresponding modal-power ratios.

$$
R_{\mathrm{mode}}=
\frac{|\alpha_{\mathrm{back,taper}}|^2}
{|\alpha_{\mathrm{forward,reference}}|^2},\qquad
R_{\mathrm{flux}}=-\frac{P_{\mathrm{subtracted}}}{P_{\mathrm{reference}}}.
$$

`load_minus_flux_data` subtracts the complex reference fields. A purely backward remaining wave carries negative x flux, so the minus sign produces positive R. With forward residuals, other modes or radiation present, selected backward-mode power and total net flux measure different quantities. A complete basis and consistent normalization should let all components close the power balance.

At finite resolution, the different discretizations in Meep and the MPB mode calculation also matter. The official example subtracts reference fields even for small modal reflections. This general caution does not establish the cause of the negative estimates in this saved run.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/27/01_field.en.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/27/01_field.en.png' | relative_url }}" alt="Saved complex DFT field Re Ez and actual dielectric boundary for a taper of length 8 µm" loading="lazy"></a>
<figcaption>Actual DFT Re Ez at resolution 25 and Lt = 8 µm, with dielectric boundaries in black. A smooth-looking propagating field does not establish the accuracy of a tiny reflection measurement.</figcaption>
</figure>

| Item | Setting |
|---|---|
| Structure | ε = 12, width 1→2 µm, linear taper with 10 µm straight sections on both sides |
| Frequency | λ = 6.67 µm; GaussianSource width 0.2f |
| Boundaries | x PML 6 µm; y PML 2 µm; y mirror symmetry |
| Source | Fundamental EigenModeSource with ODD_Z + EVEN_Y |
| Reflection plane | At 0.7Lw in the input straight section, spanning the evanescent mode tails |
| Reference | A width-1 µm straight guide with the same cell, source and monitor |
| Output measurement | Total flux in the width-2 µm guide; no output-mode decomposition |
| Stopping | After the source ends, test squared Ez maxima at the reflection plane over 50-time-unit windows against 10⁻⁹ of the maximum recorded peak |

This is a lossless 2D model. The width-2 µm output can support multiple modes, so total output flux is not automatically a selected mode's S21.

<h2 id="run">4. Run: record matching definitions for both methods</h2>

[Standalone script]({{ '/code/mode_decomposition.py' | relative_url }}) · [Source and asset SHA-256 hashes]({{ '/assets/meep/27/provenance.json' | relative_url }})

These commands run new calculations in a Meep/NumPy environment. The supplied script retains the failed diagnostic setup; successful execution does not guarantee an accurate physical reflectance.

```bash
python mode_decomposition.py --resolution 25 --Lt 1 2 4 8 --out out27 --tag r25
python mode_decomposition.py --resolution 50 --Lt 1 2 4 8 --out out27 --tag r50
```

Each length runs a straight reference followed by the taper. Start with `--Lt 1` to inspect the output definitions and signs.

```python
# Subtract complex reference fields at the taper simulation's monitor.
sim.load_minus_flux_data(flux, incident_flux_data)
coeff = sim.get_eigenmode_coefficients(flux, [1],
                                      eig_parity=mp.ODD_Z + mp.EVEN_Y)
R_mode = abs(coeff.alpha[0, 0, 1])**2 / incident_mode_power
R_flux = -subtracted_flux / incident_flux
```

Inspect JSON fields `R_coeff`, `R_flux`, `T_flux` and `residual_forward_coeff_power`. In the historical data the last quantity is named `T_coeff_in`; its T does **not** mean output transmission. The new script's `R_flux_is_nonnegative` is only a minimal sign check, not an accuracy certificate.

<h2 id="interpret">5. Interpret: preserve the failed convergence check</h2>

| Lt (µm) | res 25 modal R | res 25 flux R estimate | res 50 modal R | res 50 signed flux R estimate |
|---|---|---|---|---|
| 1 | 0.00033425 | 0.00041190 | 0.00043445 | −0.00477163 |
| 2 | 0.00008612 | 0.00009790 | 0.00017031 | −0.00510573 |
| 4 | 0.00004647 | 0.00004959 | 0.00011592 | −0.00516962 |
| 8 | 0.00002143 | 0.00002189 | 0.00007969 | −0.00520829 |

The resolution-50 forward residual is approximately **0.00527** of incident fundamental-mode power, larger than the backward component. This is evidence that the remaining field is not a pure reflection. The saved runs do not isolate why the residual occurs. Do not replace the negative estimate by zero or invent a corrected reflectance from an assumed cause.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/27/03_comparison.en.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/27/03_comparison.en.png' | relative_url }}" alt="Decrease of positive resolution-25 reflection estimates and total output-flux ratios at both resolutions" loading="lazy"></a>
<figcaption>Left: only the observed decrease at resolution 25. Right: total output flux, rather than transmission into a selected output mode. Slightly above-one values are retained as numerical residuals.</figcaption>
</figure>

The maximum relative gap between the reflection estimates grows from 0.2323 at resolution 25 to 66.35 at 50. Small or negative R can make relative differences very large, so inspect absolute magnitudes and signs too. Lt = 16 was not computed in this dataset. The fitted modal log slope −1.28 over Lt = 1…8 does not validate 1/Lt² scaling. The original reproduction hypothesis was **refuted**.

Further diagnostics should check the consistency of source, grid, monitor and normalization between reference and structure runs, then vary the forward-residual, stopping and monitor-position tests one at a time. These unperformed changes are candidates to investigate, rather than proven fixes.

<h2 id="check">6. Check: what the data establish</h2>

<details markdown="1"><summary>If flux R is negative but modal R is positive, is modal R correct?</summary>

Positivity is necessary but insufficient. The resolution change and reference-field residual remain substantial, so these data do not establish a converged reflectance.

</details>

<details markdown="1"><summary>Does total T near one imply nearly perfect fundamental-mode transmission?</summary>

Total output flux counts all components crossing its plane. Resolve the desired output mode at that plane to measure its modal transmission.

</details>

<details markdown="1"><summary>May negative values be replaced by their magnitudes for a log plot?</summary>

Their signs are central to this diagnosis. Use a linear axis and label failed estimates; do not report their magnitudes as physical reflectance.

</details>

<h2 id="reference">7. References and next steps</h2>

- [03 · Reference subtraction]({{ '/en/reference-subtraction/' | relative_url }}) · [04 · Straight guide]({{ '/en/straight-waveguide/' | relative_url }}) · [05 · Bend loss]({{ '/en/waveguide-bend-90/' | relative_url }})
- [09 · Waveguide inverse design]({{ '/en/bend-inverse/' | relative_url }}): choose a target-mode overlap appropriate to the design goal
- [21 · Polarization gratings]({{ '/en/polarization-grating/' | relative_url }}): compare summed order powers with total flux
- [Official taper tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#reflectance-of-a-waveguide-taper) · [Version-pinned code](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/mode-decomposition.py)
- [Verified metrics]({{ '/assets/meep/27/verified_metrics.json' | relative_url }}) · [Figure script]({{ '/assets/meep/27/plot_saved_results.py' | relative_url }}) · [Original verdict]({{ '/assets/meep/27/source_result.json' | relative_url }})

The reproduction follows the official setup and adds forward residual, total output flux and DFT-map output. Distinguish the documentation's general result from conclusions this saved execution did not verify.
