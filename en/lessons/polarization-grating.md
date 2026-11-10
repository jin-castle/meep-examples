---
layout: lesson
permalink: /en/polarization-grating/
lesson_title: "Can polarization reverse the direction of diffraction?"
lesson_summary: "Rotate a liquid crystal's optical axis in space and resolve the ±1-order powers for Ez ± iEy inputs. Separate polarization selectivity from incident-power efficiency and examine the remaining disagreement with a retardance formula."
lesson_goals:
  - "Represent a rotated permittivity tensor using epsilon_diag and epsilon_offdiag."
  - "Change the relative phase of two electric-field components by ±π/2."
  - "Distinguish order power, total transmission and their normalization denominators."
lesson_prerequisites: "Chapter 06: diffraction orders · Chapter 07: phase control · Chapter 20: material models"
date: 2026-11-11
title: "Meep Example 21 · Steering with polarization — anisotropic liquid-crystal gratings"
title_en: "Meep Example 21 · Steering with polarization — anisotropic liquid-crystal gratings"
lang: en
translation_key: polarization-grating
series: meep-examples
part: 21
level: intermediate
runtime: "Saved circular-input cases: approximately 13–18 s per case at resolution 50"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#diffraction-spectrum-of-liquid-crystal-polarization-gratings"
tags: [meep, fdtd, anisotropy, polarization, liquid-crystal, diffraction]
image: /assets/meep/21/02_orders.en.png
excerpt: "A rotating liquid-crystal permittivity tensor selects opposite diffraction orders when the input phase sign changes. Learn why single-order selection does not imply 100% transmission."
---
<h2 id="observe">1. Observe: reverse the phase sign, reverse the order</h2>

Chapter 06 divides light into orders by shaping a refractive-index profile. Here the thickness stays constant while the **optical-axis direction** rotates periodically. The inputs below are Ez + iEy and Ez − iEy: equal component magnitudes, opposite relative phase signs.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/21/02_orders.en.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/21/02_orders.en.png' | relative_url }}" alt="Actual -1,0,+1 order powers for Ez plus or minus iEy at retardances 0.5 and 1" loading="eager"></a>
<figcaption>Redrawn from Meep 1.33.0 data saved on 2026-11-09. Bars are normalized to incident power from a uniform-glass reference. At Δnd/λ = 0.5 the phase sign selects −1 or +1; at 1 most transmitted power returns to order 0.</figcaption>
</figure>

For half-wave retardance (Δnd/λ = 0.5), Ez + iEy puts **0.94294** into order −1 while total transmission is **0.94355**. The opposite input gives the same power in +1. Nearly 100% selectivity between ±1 orders does not mean all incident power is transmitted.

This lesson reuses saved data; no new FDTD run was performed. Keep the introductory concept animation separate from the numerical results below.

<h2 id="predict">2. Predict: what happens when thickness doubles?</h2>

<fieldset class="prediction">
<legend>What changes when retardance increases from half-wave 0.5 to full-wave 1?</legend>
<label><input type="radio" name="polarization-grating-prediction" value="zero"> Conversion decreases and light returns mainly to order 0.</label>
<label><input type="radio" name="polarization-grating-prediction" value="stronger"> The same ±1-order efficiency doubles.</label>
</fieldset>

A simple retarder model gives a converted fraction sin²(πΔnd/λ), with a maximum at 0.5 and zero at 1. The actual grating also has reflection and discretization error, so this prediction is different from a numerical requirement of exactly zero.

<h2 id="understand">3. Understand: a tensor rather than one index</h2>

{% include chapter-illustration.html %}

Propagation is along x and periodicity along y. The principal indices are nₒ = 1.55 and nₑ = 1.709, giving Δn = 0.159. At λ = 0.54 µm and period Λ = 6.5 µm, the optical axis rotates as φ(y) = πy/Λ. An optical-axis rotation of π returns the same material tensor.

$$
\boldsymbol\varepsilon(y)=R_x(\phi)
\operatorname{diag}(n_o^2,n_o^2,n_e^2)R_x^T(\phi),\qquad
p=\frac{\Delta n\,d}{\lambda}.
$$

Here d is the **total liquid-crystal thickness**: 1.69811 µm for half-wave and 3.39623 µm for full-wave retardance. Off-diagonal tensor terms couple Ey and Ez, so separate scalar 2D polarization calculations do not represent this problem.

```python
e = Rx * epsilon_diag * Rx.transpose()
material = mp.Medium(
    epsilon_diag=mp.Vector3(e[0].x, e[1].y, e[2].z),
    epsilon_offdiag=mp.Vector3(e[1].x, e[2].x, e[2].y))
```

The optical-axis pattern gives the converted polarization a spatial phase, selecting opposite first orders for opposite input signs. In output air, sin θₘ = mλ/Λ gives **±4.76545°** for ±1. Right/left circular labels depend on the viewing convention; this lesson states inputs explicitly as Ez ± iEy.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/21/01_field.en.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/21/01_field.en.png' | relative_url }}" alt="Actual real part of the complex DFT Ez for Ez plus iEy input, with liquid-crystal boundaries" loading="lazy"></a>
<figcaption>Actual Re Ez from the half-wave complex DFT field. Dashed lines mark the liquid-crystal boundaries; glass n = 1.55 lies to the left and air to the right. Color represents neither power nor optical-axis direction.</figcaption>
</figure>

| Item | Setting |
|---|---|
| Structure | 1 µm n = 1.55 substrate, liquid crystal, 1 µm air padding |
| Boundaries | 1 µm PML at both x ends; periodic y with Λ = 6.5 µm |
| Source | Two lines in the substrate: Ez and Ey with amplitude ±i |
| Frequency | f = 1/0.54; Gaussian width 0.05f |
| Normalization | Transmitted flux of a uniform n = 1.55 reference cell |
| Measurement | Total air-side flux; explicit m = −1, 0, +1 powers summed over S and P |
| Stopping | 100 time units after the source ends in the reference; 300 in the structure |

This is normal incidence on a linear, lossless anisotropic material. Voltage-driven director changes, chromatic material dispersion and fabrication errors are outside the model.

<h2 id="run">4. Run: change only input phase and retardance</h2>

[Standalone Python script]({{ '/code/polarization_grating.py' | relative_url }}) · [Data provenance and SHA-256 hashes]({{ '/assets/meep/21/provenance.json' | relative_url }})

These commands run new calculations in a Meep/NumPy environment. Viewing the saved example does not require running them.

```bash
python polarization_grating.py --phase 0.5 --chir 1 --out out21 --tag half_plus
python polarization_grating.py --phase 0.5 --chir -1 --out out21 --tag half_minus
python polarization_grating.py --phase 1 --chir 1 --out out21 --tag full_plus
python polarization_grating.py --phase 1 --chir -1 --out out21 --tag full_minus
```

`--phase` is p = Δnd/λ and `--chir 1` means Ez + iEy. The script reproduces these circular-input cases, rather than the separate linear-input thickness sweep used for the diagnostic below.

```python
for m in (-1, 0, 1):
    # Resolve S and P separately, then add their powers.
    plane_wave = mp.DiffractedPlanewave((0, m, 0), mp.Vector3(0, 1, 0), S, P)
    coeff = sim.get_eigenmode_coefficients(monitor, plane_wave)
    power = abs(coeff.alpha[0, 0, 0])**2 / incident_flux
```

The `.json` output records each order's `S`, `P`, `total` and overall `Tflux`; `.npz` stores complex `Ez`, `Ey` and the spatial extent. `total/Tflux` is a fraction of transmitted light, whereas `total` is the incident-power efficiency.

<h2 id="interpret">5. Interpret: selectivity and efficiency differ</h2>

| p | Input | −1 / incident | 0 / incident | +1 / incident | Total T |
|---|---|---|---|---|---|
| 0.5 | Ez + iEy | 0.94294 | 0.000627 | about 4.2×10⁻¹¹ | 0.94355 |
| 0.5 | Ez − iEy | about 4.2×10⁻¹¹ | 0.000627 | 0.94294 | 0.94355 |
| 1 | Ez + iEy | 0.001696 | 0.92469 | about 1.6×10⁻⁹ | 0.92638 |
| 1 | Ez − iEy | about 1.6×10⁻⁹ | 0.92469 | 0.001696 | 0.92638 |

At p = 0.5, dominant order/(+1 + −1) is approximately 0.99999999996, but efficiency relative to incident power is **94.29%**. At p = 1, **order 0/T = 99.8176%**. The three measured orders sum to 1.000007–1.000010 times total flux.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/21/03_validation.en.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/21/03_validation.en.png' | relative_url }}" alt="Analytic efficiency error of a separate linear-input thickness sweep, and resolution-50 reflected and transmitted flux" loading="lazy"></a>
<figcaption>Additional saved linear-input runs. The analytic efficiency comparison follows the source notebook's order normalization and angular correction. The right panel separately shows flux normalized to incident power.</figcaption>
</figure>

The linear-input cos²/sin² comparison has maximum absolute differences **0.15015** at resolution 30 and **0.06119** at 50. The error decreases but still exceeds the predefined 0.03 criterion. The aggregate reproduction verdict is **inconclusive**, rather than complete agreement with the formula. Resolution-50 mean R is 0.06252 and mean T is 0.93746.

The source dataset also contains a twisted bilayer, but its total thickness is twice the uniaxial case at the same sweep parameter. This lesson does not present that as an equal-thickness performance comparison.

<h2 id="check">6. Check: state the denominator first</h2>

<details markdown="1"><summary>Does 100% selectivity between ±1 mean 100% transmission efficiency?</summary>

No. Selectivity uses dominant order/(+1 + −1); efficiency uses dominant order/incident power. The half-wave efficiency here is approximately 94.29%.

</details>

<details markdown="1"><summary>Can one scalar epsilon give the same result?</summary>

It removes the rotating optical axis and off-diagonal coupling. A position-dependent tensor and coupling between both polarization components are essential here.

</details>

<details markdown="1"><summary>Does improvement at resolution 50 validate the formula?</summary>

It supports a convergence trend without meeting the accuracy criterion. Record the failed 0.03 threshold alongside the measured 0.06119 difference.

</details>

<h2 id="reference">7. References and next steps</h2>

- [06 · Binary gratings]({{ '/en/binary-grating/' | relative_url }}) · [07 · Meta-atoms]({{ '/en/meta-atom/' | relative_url }}): diffraction orders and spatial phase
- [20 · Material dispersion]({{ '/en/material-dispersion/' | relative_url }}): material-model assumptions and checks
- [27 · Mode decomposition]({{ '/en/mode-decomposition/' | relative_url }}): compare selected-mode power with total flux
- [Official tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#diffraction-spectrum-of-liquid-crystal-polarization-gratings) · [Version-pinned source](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/polarization_grating.py)
- [Verified metrics]({{ '/assets/meep/21/verified_metrics.json' | relative_url }}) · [Figure script]({{ '/assets/meep/21/plot_saved_results.py' | relative_url }}) · [Original reproduction verdict]({{ '/assets/meep/21/source_result.json' | relative_url }})

The saved reproduction retains the original optical-axis, source and boundary model while adding signed-order monitors and output data. Next, vary wavelength or the optical-axis pattern one at a time, checking summed modal power against total flux.
