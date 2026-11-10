---
layout: lesson
permalink: /en/angular-reflectance/
lesson_title: "How does reflection change at an angle?"
lesson_summary: "Send a P-polarized pulse toward an air–dielectric interface at fixed Bloch kx, then compare every frequency with Fresnel theory at its actual angle. Check the Brewster minimum, resolution convergence and the remaining energy residual separately."
lesson_goals:
  - "Distinguish the input angle from the actual angle at each frequency."
  - "Use an empty-cell run and field subtraction to calculate R and T."
  - "Check Fresnel convergence and energy balance as separate tests."
lesson_prerequisites: "Chapter 17: oblique planewaves and Bloch phase · Chapter 03: reference subtraction"
date: 2026-11-10
title: "Meep Example 18 · Light at an angle — angular reflectance and the Brewster angle"
title_en: "Meep Example 18 · Light at an angle — angular reflectance and the Brewster angle"
lang: en
translation_key: angular-reflectance
series: meep-examples
part: 18
level: intermediate
runtime: "Saved runs: a resolution ladder at 0°, 45°, 75°; seconds to minutes per angle/resolution"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#angular-reflectance-spectrum-of-a-planar-interface"
tags: [meep, fdtd, fresnel, brewster, oblique, bloch, convergence]
image: /assets/meep/18/02_results.en.png
excerpt: "Measure P-polarized reflection from air into an n=3.5 dielectric, locate the Brewster minimum, and check the angle convention, grid convergence and energy balance."
---
<h2 id="observe">1. Observe: an angle with very little reflection</h2>

Chapter 17 sets a planewave's direction. Here that wave meets a flat boundary. Look at P-polarized reflection from air into a lossless dielectric of index 3.5: over part of the angular range, oblique incidence reflects less than normal incidence.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/18/02_results.en.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/18/02_results.en.png' | relative_url }}" alt="P reflectance versus actual incident angle and Fresnel theory, and spectra for three input angles at resolution 200" loading="eager"></a>
<figcaption>Actual Meep 1.33.0 results saved on 2026-11-08. Left: resolution 50, plotted at each frequency's actual angle. Right: resolution 200 spectra. θ₀ is defined at λ = 0.8 µm; a curve does not represent the same angle at all wavelengths.</figcaption>
</figure>

P polarization places the electric field in the plane of incidence. The Brewster angle of this interface is approximately **74.05°**. At λ = 0.8 µm and an input angle of 75°, the saved resolution-50 result is **R = 0.00226**. This samples near the minimum, rather than exactly at the Brewster angle.

These figures redraw existing saved runs; no new simulation was run for this lesson. Resolution 50 reproduces the official notebook's 850 reflectance samples to a maximum absolute difference of 0.000131, yet its error against Fresnel theory is much larger. Reproducing an earlier output and establishing physical accuracy are separate checks.

<h2 id="predict">2. Predict: does one pulse have one angle?</h2>

<fieldset class="prediction">
<legend>With fixed kx and a 0.4–0.8 µm pulse, what happens to the incident angle?</legend>
<label><input type="radio" name="angular-reflectance-prediction" value="vary"> The incident angle varies with frequency.</label>
<label><input type="radio" name="angular-reflectance-prediction" value="fixed"> All frequencies arrive at the input angle.</label>
</fieldset>

The input θ₀ = 75° is defined at the longest wavelength, 0.8 µm. At 0.4 µm the frequency doubles, so sin θ halves and the actual angle becomes approximately **28.88°**. The next section derives this relationship.

| Prediction to check | Comparison |
|---|---|
| P reflectance becomes small near 74.05° | Calculate the actual angle before comparing with Fresnel theory |
| Increasing resolution reduces the error in R | Use the same θ₀ = 0°, 45°, 75° and the same 50 frequencies |
| A lossless interface has R + T = 1 | Check the energy residual separately from reflectance accuracy |

<h2 id="understand">3. Understand: fixed kx, changing angle</h2>

{% include chapter-illustration.html %}

The plane of incidence is x–z and the interface is z = 0. Because the structure is uniform transversely, a Bloch phase in x lets a cell with a grid only along z represent oblique incidence. For nonzero angles, `dimensions=3` retains the vector field components and transverse wavevector; the cell lengths in x and y remain zero.

Meep's `k_point` excludes the factor 2π. With µm as the length unit and air index 1,

$$
k_x=f_{\min}\sin\theta_0,\qquad
\theta(f)=\sin^{-1}\!\left(\frac{k_x}{f}\right),\qquad
f_{\min}=1/0.8.
$$

Do not confuse this with an angle defined at the source's `fcen`. Following the official example, **θ₀ is defined at fmin**. A broadband response at one fixed actual angle needs a different construction, such as separate frequency calculations with the corresponding kx.

Snell's law gives the transmitted angle θt and the P-polarized reflectance:

$$
\sin\theta_t=\frac{\sin\theta}{3.5},\qquad
R_p=\left|\frac{\cos\theta_t-3.5\cos\theta}
{\cos\theta_t+3.5\cos\theta}\right|^2,\qquad
\theta_B=\tan^{-1}(3.5).
$$

The sign convention for the reflected amplitude can differ without changing its squared magnitude. At normal incidence, R = ((3.5 − 1)/(3.5 + 1))² ≈ 0.30864.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/18/01_layout.en.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/18/01_layout.en.png' | relative_url }}" alt="A 12 µm z cell showing PML, source and reflection/transmission monitors, with the saved empty-cell pulse and incident flux spectrum" loading="lazy"></a>
<figcaption>Left: a 1D diagram at the actual code coordinates. Center and right: saved empty-cell results. Incident flux changes with θ₀, so each run uses its own normalization denominator.</figcaption>
</figure>

| Item | Setting |
|---|---|
| Structure | Air for z &lt; 0; lossless n = 3.5 half-space for z &gt; 0 |
| Cell and boundaries | Length 12 µm along z; 1 µm PML at both ends |
| Source | z = −5 µm, Ex GaussianSource, 0.4–0.8 µm |
| Monitors | Reflection z = −3 µm; transmission z = +2 µm; 50 frequencies |
| Normalization | An empty cell at the same kx supplies incident flux and complex flux data |
| Stopping | After the source ends, check the maximum squared magnitude of Ex over 50-time-unit windows; stop below 10⁻⁹ of its previous peak |
| Saved comparison | res 50: θ₀ = 0°…80° in 5° steps; res 100 and 200: 0°, 45°, 75° |

The assumptions are a flat, lossless, nondispersive interface and P polarization. The results do not establish behavior for a finite-aperture beam, S polarization, surface roughness or dispersive materials.

<h2 id="run">4. Run: subtract the empty cell and measure R and T</h2>

[Download the full Python script]({{ '/code/angular_reflectance.py' | relative_url }}) · [Data and figure provenance with hashes]({{ '/assets/meep/18/provenance.json' | relative_url }})

Run in an environment with Meep and NumPy, using the same Meep environment as the other lessons. Viewing the saved figures does not require running the solver.

```bash
# Three input angles at the official script's resolution 200
python angular_reflectance.py --resolution 200 --theta 0 45 75 --out out18 --tag r200
# Change only resolution for a comparable ladder
python angular_reflectance.py --resolution 50 --theta 0 45 75 --out out18 --tag r50
python angular_reflectance.py --resolution 100 --theta 0 45 75 --out out18 --tag r100
```

Start with only 0° if you want to check the source and normalization first. These commands run real FDTD simulations: an empty cell and an interface cell at every angle.

```python
k = mp.Vector3(z=fmin).rotate(mp.Vector3(y=1), math.radians(angle))
reflection = sim.add_flux(fcen, df, 50,
                         mp.FluxRegion(center=mp.Vector3(z=-3)))
# Save empty_data and incident in the empty cell, then in the new sim:
sim.load_minus_flux_data(reflection, empty_data)
R = -reflected_flux / incident
T = transmitted_flux / incident
```

The reflection monitor's positive normal is +z while reflected power travels in −z, hence the minus sign in R. The transmitted monitor needs no incident-field subtraction. As in chapter 03, subtract **complex fields rather than powers** to remove the incident–reflected interference term.

The script saves `.npz` and `.json` files. It records `freqs`, `kx`, `R`, `T`, `theta_actual_deg` and `R_fresnel` for frequency-by-frequency checks. The older saved `.npz` files lack the last two arrays; the figure script derives them from `kx` and `freqs`.

<h2 id="interpret">5. Interpret: convergence and a remaining residual</h2>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/18/03_convergence.en.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/18/03_convergence.en.png' | relative_url }}" alt="Fresnel error decreasing with resolution at the same three input angles, and the remaining R plus T minus 1 residual at 75 degrees" loading="lazy"></a>
<figcaption>Recomputed from saved data without a new solver run. Left: Fresnel errors at the same three input angles. Right: the θ₀ = 75° energy balance; approximately 1.5% remains near λ = 0.8 µm at resolution 200.</figcaption>
</figure>

| Resolution (px/µm) | Maximum absolute R error (common three angles) | Maximum absolute energy residual |
|---|---|---|
| 50 | 0.06350 | 0.13714 (all 17 input angles) |
| 100 | 0.01395 | 0.01269 (three input angles) |
| 200 | 0.003398 | 0.01454 (three input angles) |

The reflectance error is max |R − RFresnel| and the energy residual is max |R + T − 1|. The resolution-200/50 Fresnel error ratio is **0.0535**. This establishes strong resolution sensitivity; it does not identify every source of error.

Energy balance does not improve monotonically from resolution 100 to 200. PML and stopping settings are candidates for a further investigation of the grazing-incidence residual, but these saved runs do not isolate its cause. **Do not interpret the approximately 1.5% residual as absorption.** The material is lossless.

At shorter wavelengths, the high-index material also has fewer pixels per internal wavelength. For λ = 0.4 µm, n = 3.5 and resolution 50, there are only about 5.7 pixels per internal wavelength. Even settings copied from an official notebook need a convergence check for the intended measurement.

<h2 id="check">6. Check: angle, normalization and accuracy</h2>

<details markdown="1">
<summary>Question 1. For θ₀ = 75°, what is the actual angle at λ = 0.4 µm?</summary>

Approximately **28.88°**. kx is fixed at (1/0.8)sin75°, while f = 1/0.4, so sin θ = 0.5sin75°. Calling the entire spectrum a “75° reflectance spectrum” would therefore be misleading.

</details>

<details markdown="1">
<summary>Question 2. Does R + T = 1.015 mean 1.5% gain?</summary>

No. The model has neither loss nor gain. This is a numerical residual to investigate through normalization, resolution, PML and stopping settings. The saved data do not determine which cause dominates.

</details>

<details markdown="1">
<summary>Question 3. Is reproducing the notebook output enough?</summary>

Reproducibility and accuracy are separate tests. Here 850 notebook samples agree closely, yet the resolution-50 maximum Fresnel error is 0.0635. Check an analytic solution, a resolution ladder and energy balance together.

</details>

For a next experiment, change kx with frequency to construct a spectrum at **one actual angle**. Define its comparison criteria and stopping/PML settings first, and record new calculations separately from the saved dataset.

<h2 id="reference">7. References and next steps</h2>

- [03 · Reference subtraction]({{ '/en/reference-subtraction/' | relative_url }}): review removal of the incident field
- [17 · Oblique planewaves]({{ '/en/oblique-plane-wave/' | relative_url }}): propagation direction and Bloch phase
- [06 · Binary grating]({{ '/en/binary-grating/' | relative_url }}) · [07 · Meta-atoms]({{ '/en/meta-atom/' | relative_url }}): extend a flat interface to angular response of periodic structures
- [14 · Extraction efficiency]({{ '/en/extraction-efficiency/' | relative_url }}): integrate power emitted into many angles
- [Official Meep tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#angular-reflectance-spectrum-of-a-planar-interface) · [Version-pinned upstream script](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/refl-angular.py)
- [Meep stopping-condition API](https://meep.readthedocs.io/en/latest/Python_User_Interface/#run-and-step-functions): the squared-field and time-window definition of `stop_when_fields_decayed`

The interface, materials, source and normalization follow the original example. The adaptation adds a transmission monitor and portable data output. Figures are educational redraws of saved results. The [verified metrics]({{ '/assets/meep/18/verified_metrics.json' | relative_url }}) and [figure-generation script]({{ '/assets/meep/18/plot_saved_results.py' | relative_url }}) are available alongside [provenance.json]({{ '/assets/meep/18/provenance.json' | relative_url }}), which records dates and source SHA-256 hashes.
