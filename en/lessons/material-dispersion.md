---
layout: lesson
lesson_title: "What changes when a material's index depends on wavelength?"
lesson_summary: "Replace a constant index with fused_quartz and a Lorentz dispersion model. Check quartz reflectance against Fresnel theory, then examine the limits of estimating permittivity from extracted mode frequencies."
lesson_goals:
  - "Distinguish a constant index from frequency-dependent complex permittivity."
  - "Normalize a dispersive-material reflection experiment with an empty-cell run and check grid convergence."
  - "Distinguish complex mode frequencies at real k from material response at real frequency."
lesson_prerequisites: "02 PML · 03 reference subtraction and Fresnel reflection · 12 mode frequencies"
date: 2026-11-10
title: "Meep Example 20 · Giving materials a spectrum — quartz reflection and Lorentz dispersion"
title_en: "Meep Example 20 · Giving materials a spectrum — quartz reflection and Lorentz dispersion"
lang: en
permalink: /en/material-dispersion/
series: meep-examples
part: 20
level: intermediate
runtime: "Quartz at resolution 200: 40,001 time steps; Lorentz: 101 k points (wall time depends on hardware)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Material_Dispersion/"
tags: [meep, fdtd, material, dispersion, quartz, lorentz, fresnel, convergence]
image: /assets/meep/20/quartz-reflectance.png
excerpt: "Check dispersive quartz reflectance against Sellmeier–Fresnel theory and examine a failed simple permittivity-retrieval check in a Lorentz medium."
---
<h2 id="observe">1. Observe: the same glass reflects different colours differently</h2>

Chapter 03 used an interface with a fixed refractive index. Here light enters a **dispersive fused-quartz half-space from air**. One pulse measures reflection at 50 frequencies spanning vacuum wavelengths of 0.4–0.8 µm. The surface remains flat, yet shorter wavelengths reflect slightly more strongly.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/20/quartz-reflectance.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/20/quartz-reflectance.png" alt="Normal-incidence air/quartz reflectance and absolute Fresnel errors at resolutions 100 and 200" loading="eager"></a>
<figcaption>Replotted saved Meep 1.33.0 results. The left panel shows reflectance; the right shows its absolute difference from Sellmeier–Fresnel theory. Dots are computed values. Doubling resolution from 100 to 200 reduces the maximum error by approximately four.</figcaption>
</figure>

We also inspect **modes of a uniform Lorentz medium**, without a physical interface. The validation outcomes differ: quartz reflection meets its error target, whereas the simple permittivity estimate below fails its 1% target. Reading the remaining errors is part of the experiment.

<details markdown="1">
<summary>Models and connections to earlier chapters</summary>

| Experiment | Model and conditions | Quantity to check |
|---|---|---|
| Quartz reflection | 1D air/quartz half-space; 1 µm PML at both ends; 0.4–0.8 µm; 50 frequencies | R(λ) normalized by an empty-cell run; Fresnel error |
| Lorentz medium | 0D Bloch cell; ε∞ = 2.25; two resonance terms; resolution 20 | 202 complex mode frequencies over k = 0.3–2.2 |

Keep chapter 03's normalization and change the material. Broadband phase libraries and metalenses built from chapter 07 also need material dispersion. Validate chapter 18's angular response and this chapter's spectral response separately before combining them.

</details>

<h2 id="predict">2. Make a prediction: is one fixed index enough?</h2>

<fieldset class="prediction">
<legend>How does normal-incidence reflectance of an ideal lossless half-space with constant n = 1.5 depend on wavelength?</legend>
<label><input type="radio" name="material-dispersion-prediction" value="constant"> It stays at 4% in the continuum model.</label>
<label><input type="radio" name="material-dispersion-prediction" value="dispersion"> It automatically acquires the same wavelength dependence as quartz.</label>
</fieldset>

<details markdown="1">
<summary>Prediction and validation criteria</summary>

The first answer is correct: R = [(n−1)/(n+1)]² = 0.04. `mp.Medium(index=1.5)` does not automatically include the Sellmeier dispersion of quartz. Compare against theory and refine the grid to separate material dispersion from numerical dispersion.

The registered quartz criterion is **max |RMeep−RFresnel| < 5×10⁻⁴**. Resolution 200 passes; resolution 100 does not. The separate 1% target for the simple Lorentz permittivity estimate is not met by these saved results.

</details>

<h2 id="understand">3. Understand the principles: materials have a response time</h2>

{% include chapter-illustration.html %}

When polarization cannot follow an electric field instantaneously, the response depends on frequency. Meep evolves auxiliary polarization equations in time. In Meep's ordinary-frequency units, a scalar Lorentz model has the form

$$
\varepsilon(f)=\varepsilon_\infty+\sum_j\frac{\sigma_j f_j^2}{f_j^2-f^2-i\gamma_j f}.
$$

The parameters are `frequency` = fⱼ, `gamma` = γⱼ, and `sigma` = σⱼ. Keep their frequency units consistent. With the exp(−iωt) convention, positive Im ε in a passive medium is associated with absorption. The quartz experiment here does not independently measure absorbed power. Power removed by PML must not be counted as material absorption.

{% highlight python %}
material = mp.Medium(
    epsilon=2.25,
    E_susceptibilities=[
        mp.LorentzianSusceptibility(frequency=1.1, gamma=1e-5, sigma=0.5),
        mp.LorentzianSusceptibility(frequency=0.5, gamma=0.1, sigma=2e-5),
    ],
)
{% endhighlight %}

This illustrative two-resonance material and fused quartz are **different materials**. The quartz script imports `fused_quartz` from `meep.materials`. With a length unit of 1 µm, λ = 0.4–0.8 is in µm and f = 1/λ. Stay within the material library model's stated wavelength range.

For normal incidence from air into a nonmagnetic transparent medium, n(λ) = √ε(λ) gives

$$
R(\lambda)=\left|\frac{1-n(\lambda)}{1+n(\lambda)}\right|^2.
$$

Evaluate the script's Sellmeier formula and Meep quartz response at the same wavelengths.

<h2 id="run">4. Run it yourself: change the material, retain the normalization</h2>

Use a Meep 1.33.0 Python environment. The quartz script also uses NumPy and Matplotlib. Both files run independently. The saved outputs linked below let you inspect this lesson without running another simulation.

{% highlight bash %}
# Quartz: compute empty-cell and material runs in sequence.
OMP_NUM_THREADS=1 python code/dispersive_quartz.py --out results/quartz200 --resolution 200
OMP_NUM_THREADS=1 python code/dispersive_quartz.py --out results/quartz100 --resolution 100

# Extension: extract complex frequencies at each real Bloch k.
OMP_NUM_THREADS=1 python code/material_dispersion.py --out results/lorentz20 --resolution 20
{% endhighlight %}

Quartz produces `reflquartz.json` and `refl_quartz.png`; the Lorentz experiment produces `matdisp.json`. `--out` is relative to your working directory; `--help` lists the arguments. The one-core environment assignment above uses WSL/Linux shell syntax. Wall time varies with hardware and stopping conditions.

Retain this sequence in the quartz experiment:

1. Save incident flux and complex DFT data from the empty cell.
2. After `reset_meep()`, add the quartz half-space with the same source, frequencies and monitor.
3. Subtract incident fields with `load_minus_flux_data()` before computing R = −Φrefl/Φinc.
4. Compare all 50 frequencies with theory and then compare resolutions 100 and 200.

{% highlight python %}
empty_flux = mp.get_fluxes(refl)
empty_data = sim.get_flux_data(refl)
# In a new material simulation, create refl at the same position.
sim.load_minus_flux_data(refl, empty_data)
# After the source ends and fields have decayed:
R_meep = -np.asarray(mp.get_fluxes(refl)) / np.asarray(empty_flux)
{% endhighlight %}

<h2 id="interpret">5. Interpret the results: separate passing checks from unresolved errors</h2>

| Quartz comparison | Resolution 100 | Resolution 200 |
|---|---:|---:|
| Maximum absolute reflectance error | 6.594×10⁻⁴ | 1.678×10⁻⁴ |
| Target of 5×10⁻⁴ | Not met | Met |

At resolution 200, R is 0.034182 at 0.8 µm (theory 0.034143) and 0.036390 at 0.4 µm (theory 0.036222). **An absolute error of 1.68×10⁻⁴ is 0.0168 percentage points**, not a relative error of 0.0168% in R. This run ended after 40,001 time steps, at Meep time 100.0025.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/20/lorentz-validation.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/20/lorentz-validation.png" alt="Two Lorentz-medium mode branches and errors of a simple real-frequency permittivity estimate" loading="lazy"></a>
<figcaption>The saved Lorentz extension. The right panel compares (k/Re f)² with Re ε(Re f). Even samples more than 0.05 from the resonances do not all meet the 1% target. This is not a validation of the full complex permittivity.</figcaption>
</figure>

`run_k_points` returns **complex f at real k**. A usual material spectrum ε(f) is evaluated at real f. Mixing these evaluations gives an unfair comparison, particularly for the imaginary part. A rigorous mode check must evaluate the model at the same complex frequency and examine grid dispersion and the reliability of the extracted modes.

The saved check compared **(k/Re f)² with Re ε(Re f)** over 193 samples with f > 0.02 and distances greater than 0.05 from both resonances, 0.5 and 1.1. The median relative difference was 1.862%; the maximum was 37.176%. The 1% target therefore failed. A post-hoc Yee-dispersion correction lowered the median to 0.333%, but left a maximum of 37.030%. That correction is a diagnostic added after the original check. The identity of the large-error modes remains unresolved. These results alone neither validate nor refute the material model or Meep as a whole.

<h2 id="check">6. Check your understanding: which error are you reducing?</h2>

<details markdown="1">
<summary>Why should a constant index=1.5 not be checked against quartz Sellmeier theory?</summary>

They describe different materials. First match ε(λ), then assess discretization error. A constant index can approximate one wavelength but cannot reproduce a broadband dispersive response.

</details>

<details markdown="1">
<summary>Does passing the quartz reflectance check also validate the Lorentz mode estimate?</summary>

No. These 1D reflection and 0D Bloch-mode experiments differ in material, observable and error sources. Each needs its own validation. Only the former meets its stated criterion in this dataset.

</details>

<details markdown="1">
<summary>What is lost when the imaginary part of a mode frequency is discarded?</summary>

The difference between a decaying mode's complex frequency and real-frequency steady-state response is lost. Use the simple estimate as a diagnostic; compare precisely at the same frequency argument, time convention and units. Also examine weakly excited modes and finite-time extraction error.

</details>

Try refining the quartz grid while retaining the source and monitors. Then return to [chapter 07's phase library]({{ site.baseurl }}/en/meta-atom/) and identify where a constant-index approximation would affect a broadband design. To vary angle as well, check the fixed-k∥ normalization conditions in [chapter 18]({{ site.baseurl }}/en/angular-reflectance/).

<h2 id="reference">7. Code and references</h2>

- Runnable code: [dispersive_quartz.py]({{ site.baseurl }}/code/dispersive_quartz.py), [material_dispersion.py]({{ site.baseurl }}/code/material_dispersion.py)
- Saved results: [quartz at resolution 200]({{ site.baseurl }}/assets/meep/20/quartz-r200.json), [resolution 100]({{ site.baseurl }}/assets/meep/20/quartz-r100.json), [complex Lorentz modes]({{ site.baseurl }}/assets/meep/20/lorentz-modes.json)
- Checks: [summary]({{ site.baseurl }}/assets/meep/20/summary.json), [post-hoc diagnostic]({{ site.baseurl }}/assets/meep/20/posthoc-numdisp.json), [provenance and SHA-256]({{ site.baseurl }}/assets/meep/20/provenance.json), [plot regeneration]({{ site.baseurl }}/assets/meep/20/render_results.py)
- Official Meep: [Material Dispersion](https://meep.readthedocs.io/en/latest/Python_Tutorials/Material_Dispersion/), [Materials](https://meep.readthedocs.io/en/latest/Materials/#material-dispersion), [Material Library](https://meep.readthedocs.io/en/latest/Materials/#materials-library)
- Upstream calculation sources: [material-dispersion.py](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/material-dispersion.py), [refl-quartz.py](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/refl-quartz.py). This lesson reorganizes saved calculations for learning; no new simulation was run.
