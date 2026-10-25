---
layout: lesson
permalink: /en/waveguide-bend-90/
lesson_title: "How well does light turn a right-angle corner?"
lesson_summary: "Observe light leaking from a sharp corner, then measure transmission and reflection relative to a straight guide. See how rounding the corner changes loss and footprint."
lesson_goals:
  - "Connect field images with transmitted, reflected, and radiated power."
  - "Explain why a straight reference run and incident-field subtraction are needed."
  - "Compare bend radius and loss while recognizing numerical uncertainty."
lesson_prerequisites: "Waveguide modes from Chapter 04 and reference runs from Chapter 03 are helpful. Running the code requires Meep and Python."
date: 2026-10-23
title: "Meep Example 05 · Bent waveguide and radius trade-off — two-run flux normalization, sharp-bend baseline, radius sweep"
title_en: "Meep Example 05 · Bent waveguide and the radius trade-off — two-run flux normalization, sharp-bend baseline, radius sweep"
lang: en
translation_key: waveguide-bend-90
series: meep-examples
part: 5
level: beginner
runtime: "95 s (sharp bend 10 s + radius sweep + convergence)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend"
tags: [meep, fdtd, waveguide, bend, flux, normalization]
image: /assets/meep/05/02_field.png
excerpt: "a dielectric waveguide (ε = 12, width 1) turns a sharp 90° corner. We measure how much power goes around the corner, how much comes back, and how much leaks out."
---
<details markdown="1">
<summary>English summary</summary>

- **What**: a dielectric waveguide (ε = 12, width 1) turns a sharp 90° corner. We measure how much power goes around the corner, how much comes back, and how much leaks out.
- **Result**: T = 0.20, R = 0.22, radiated = 0.58 at the center wavelength. Most of the light is lost at the sharp corner. Rounding it recovers the light: T = 0.91 at a bend radius of 0.35 µm and 0.99 at 0.70 µm.
- **Takeaway**: two-run flux normalization. A straight reference run gives the input power and the incident fields; subtracting them in the bend run leaves only the reflection. A sharp corner is not usable in a photonic circuit.
- **Code**: full script at the bottom, ~95 s on one core (the sharp bend alone takes 10 s).

</details>

<h2 id="observe">1. Observe · Follow the path of light first</h2>

Bend a constant-width waveguide through a right angle. Light enters from the left and exits upward. Watch whether wavefronts reaching the corner **continue only into the vertical arm or also spread into the surrounding air**. Do not read transmission directly from field brightness; connect it to the flux measurements below.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/05/02_field.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/05/02_field.png' | relative_url }}" alt="Simulated Re(Ez) and amplitude in a sharp L-shaped waveguide. Radiation spreads outside the corner and the output arm is weak." loading="lazy">
  </a>
  <figcaption>Simulated fields at 1550 nm. Thin lines mark the guide boundaries. Wavefronts outside the corner and standing waves in the input arm indicate radiation and reflection, respectively.</figcaption>
</figure>

<figure class="lesson-figure lesson-animation">
  <a href="{{ '/assets/meep/05/06_anim_sharp.gif' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/05/06_anim_sharp.gif' | relative_url }}" alt="Time evolution as a pulse splits into reflection, radiation, and transmission at a sharp corner" loading="lazy" data-animation-src="{{ '/assets/meep/05/06_anim_sharp.gif' | relative_url }}" data-static-src="{{ '/assets/meep/05/02_field.png' | relative_url }}">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
  <figcaption>Time evolution at the sharp corner. As the pulse reaches the corner, a large wavefront spreads into the cladding and only part turns into the vertical arm. The returning wave overlaps the incident pulse in the horizontal arm.</figcaption>
</figure>

<figure class="lesson-figure lesson-animation">
  <a href="{{ '/assets/meep/05/06_anim_round.gif' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/05/06_anim_round.gif' | relative_url }}" alt="Time evolution as a pulse follows a rounded corner of radius 3a toward the output" loading="lazy" data-animation-src="{{ '/assets/meep/05/06_anim_round.gif' | relative_url }}" data-static-src="{{ '/assets/meep/05/05_field_round.png' | relative_url }}">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
  <figcaption>Time evolution at radius 3a. Nearly all of the same pulse turns the corner and reaches the transmission plane (blue line) on the vertical arm.</figcaption>
</figure>

<h2 id="predict">2. Predict · Before reading the results</h2>

Can the transmitted fraction T into the upward guide decrease even when the material does not absorb light?

<fieldset class="prediction">
  <legend>Choose one answer first.</legend>
  <label><input type="radio" name="prediction-05" value="0"> Without absorption, T must be almost 1</label>
  <label><input type="radio" name="prediction-05" value="1"> Reflection and radiation make T less than 1</label>
</fieldset>

<details markdown="1">
<summary>Check the reasoning behind your prediction</summary>

The second answer is correct. Lossless material does not mean the output guide receives all power. Count reflection R returning to the input and radiation L leaking into the surrounding air as well. Measure whether radiation is the largest fraction in this structure.

</details>

<h2 id="understand">3. Understand · Explain what you observed</h2>

{% include chapter-illustration.html %}

<!-- concept-illustration:part-05:start -->

<p class="lesson-note">Compare a straight reference, sharp right angle, and rounded bend in an ε = 12 dielectric waveguide in air. Effective incident light travels from the left along +x, and the output travels upward along +y. The corner can split power into transmission, reflection, and outward radiation. R ≈ 0.70 µm in the diagram is the rounded value of the bend centerline radius 0.6975 µm. Dashed lines are position guides; arrow widths do not represent calculated power fractions. With the wavelength scaled to 1550 nm, the guide width is 232.5 nm.</p>

<!-- concept-illustration:part-05:end -->

### Establish a straight-guide reference first

The reference run uses a straight guide with the same material, width, and source. Save its transmitted power as P_in and its incident DFT fields at the reflection plane. In the bend run, apply `load_minus_flux_data` at that same reflection plane to **subtract the incident contribution at field level**. Subtracting power values instead leaves an interference contribution.

### Separate output, return, and outward leakage

$$T=P_{\mathrm{tran}}/P_{\mathrm{in}},\qquad R=-P_{\mathrm{refl}}/P_{\mathrm{in}},\qquad L=1-T-R$$

Reflected power travels in −x and has negative flux; the minus sign in R converts it to a positive fraction. The transmission monitor must be a **horizontal line** crossing light traveling in +y. A sharper corner changes mode direction and shape more abruptly, causing reflection and radiation. Rounding smooths that transition.

<aside class="lesson-note" markdown="1">
**Model scope:** 2D Ez and lossless ε = 12 material. L is a residual, not a separate radiation-monitor measurement. With 1a = 232.5 nm, width 1a and wavelength 6.67a become 232.5 nm and 1550 nm. These radii cannot be used directly as minimum-radius rules for other materials or 3D structures.
</aside>

<details markdown="1">
<summary>Explore symbols, assumptions, and prediction tables</summary>

At the corner, the incoming mode encounters a guide abruptly pointing in a new direction. Its overlap with the vertical-arm mode is small (mode mismatch), so unmatched power radiates outward or returns. There is no simple closed-form solution here; energy conservation constrains the result.

$$
T=\frac{P_{\mathrm{tran}}}{P_{\mathrm{in}}},\qquad
R=\frac{-P_{\mathrm{refl}}}{P_{\mathrm{in}}},\qquad
T+R+L_{\mathrm{rad}}=1
$$

| Symbol | Meaning | Code variable |
|------|----|-----------|
| $P_{\mathrm{in}}$ | Power transmitted through the straight reference guide | `P_in` |
| $P_{\mathrm{tran}}$ | Power through the vertical-arm cross-section in the bend run | `mp.get_fluxes(tran)` |
| $P_{\mathrm{refl}}$ | Bend reflection-plane flux after incident-field subtraction; only backward power remains, so it is **negative** | `mp.get_fluxes(refl)` |
| $L_{\mathrm{rad}}$ | Power leaking outward at the corner, inferred as a residual rather than measured directly | `L = 1 - T - R` |

**Assumptions and validity**: 2D, lossless material (the residual is interpreted as radiation), Ez polarization perpendicular to the plane, and official-example dimensionless units (length a, ε = 12, wavelength 6.67a). Figures use a = 232.5 nm to label the center wavelength as 1550 nm and lengths in µm.

### Make predictions before viewing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| T | Below 0.5, tens of percent | High index contrast (√12 ≈ 3.5) and a sharp corner give small modal overlap |
| R | Tens of percent | The corner returns some power like a reflecting wall |
| L (radiation) | Largest fraction | Severe mode mismatch sends much of the power outward |
| Field shape | Radiation lobes in the cladding around the corner; weak vertical arm | Mode mismatch |
| T + R | At most 1 | Energy conservation |

**Checks**: first confirm low T and the energy budget for this sharp geometry. A small excess in T + R may be numerical error; check signs, normalization, and convergence together.

</details>

<h2 id="run">4. Run it yourself · Change one variable</h2>

### Try one change: waveguide width

1. Put the complete code below and shared `blogfig.py` in the same `code/` folder, then run `python bend90.py` there. Keep a separate copy of the original `w = 1.0` results and `result.json`.
2. Change **only `w = 1.0` to `w = 0.8`** and rerun. Keep material, wavelength, radius list, and resolution unchanged.
3. Compare T·R·L at matching radii in the two `radius_sweep` results. Record the first radius with T above 0.9 and the sharp-bend T.

Changing width changes confinement and mode overlap at the corner. Predict which radius will show the largest difference first. **Width-0.8 results have not been measured in this lesson**; the published curve is the width-1.0 baseline. Runs overwrite output files, so save the reference results before the comparison.

<details markdown="1">
<summary>View the layout, source, and parameters</summary>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/05/01_layout.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/05/01_layout.png' | relative_url }}" alt="L-shaped waveguide with source, reflection/transmission flux planes, PML, and decay-monitoring point" loading="lazy">
  </a>
  <figcaption>Black L: horizontal and vertical guide arms (`geometry`, both extending through PML). Red line: Ez line source at x = −6.5. Vertical blue line: reflection plane at x = −5.5, downstream of the source. Horizontal blue line: transmission plane at y = +6.5 on the vertical arm. Green hatching: PML. Purple cross: bend-run decay point (4, 6.5). Coordinates are in code units a, while axes show µm using a = 232.5 nm (cell 16a = 3.72 µm). Circled numbers identify ① parameters, ② geometry, ③ source, ④ PML, ⑤ monitors, and ⑥ decay point; ⑦ post-processing has no physical position. The straight reference retains the same source and reflection plane with a continuous horizontal arm.</figcaption>
</figure>

| Parameter | Value | Reason | Effect of changing it |
|----------|-----|-------------|--------|
| `eps_wg`, `w` | 12, 1 | Official tutorial values (n ≈ 3.46) | Lower ε weakens confinement and can increase L |
| `fcen`, `df` | 0.15, 0.1 | Wavelength 6.67a = 1550 nm (a = 232.5 nm); band 5–10a = 1160–2325 nm | Low source power makes band-edge ratios unstable |
| `resolution` | 25 | Increased from the official 10; guide width 25 px, guided wavelength 48 px | At 10, coarse corner representation causes numerical variation |
| `dpml` | 1.0 | Approximately one-sixth wavelength; both arms cross PML | Thin PML can contaminate R with boundary reflection |
| `sx = sy` | 16 | Room for corner radiation to spread before PML | Smaller cells can return radiation toward the monitor |
| `src_x`, `refl_x` | −6.5, −5.5 | Source is 0.5 outside PML; reflection plane is 1.0 **downstream** of it | An upstream reflection plane changes incident-field normalization |
| `span` | w + 2 | Includes 1a of evanescent tail on each side of the core | Core-only width can underestimate P_in and overestimate T |

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/05/00_source.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/05/00_source.png' | relative_url }}" alt="Bend-experiment Gaussian source waveform and spectrum, with weak power at the band edges" loading="lazy">
  </a>
  <figcaption>Source waveform (left) and power spectrum (right): width = 1/fwidth = 10, pulse peak t0 = 50. At the monitor-band edges (1162–2325 nm), source power is only 0.005% of its central value. Endpoints in the spectrum below therefore divide one nearly zero value by another; use them only for qualitative trends.</figcaption>
</figure>

**Difference from the lecture notebook**: week 6 sweeps radii 0.6–3.0 µm for a curved bend with indices 3.4/1.44 and width 0.6 µm. This lesson uses the official sharp bend (ε = 12, w = 1a) as a baseline and rounds only the corner of the same structure.

</details>

<details markdown="1">
<summary>Read the step-by-step code explanation</summary>

> The reading order is the same as Chapter 04: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → running and stopping → post-processing.
> There are two runs, so steps ⑤–⑥ appear once for the reference and once for the bend.

### ① Units and parameters — which numbers are fixed?

```python
import numpy as np
import meep as mp

# Dimensionless units as in the official tutorial: 1 length unit = a (think 1 um).
eps_wg = 12.0            # waveguide permittivity (n = sqrt(12) = 3.46)
w = 1.0                  # waveguide width
fcen = 0.15              # center frequency -> wavelength 1/0.15 = 6.67 units
df = 0.1                 # source bandwidth
nfreq = 11               # number of frequencies in the flux monitors

resolution = 25          # pixels per unit -> width = 25 px, wavelength in the guide (1.92) = 48 px
dpml = 1.0               # PML thickness
sx = sy = 16.0           # square cell, PML included

ycen = -4.0              # y of the input (horizontal) arm
xcen = +4.0              # x of the output (vertical) arm  -> corner at (xcen, ycen)

src_x = -6.5             # source: 0.5 outside the left PML (PML edge at x = -7)
refl_x = -5.5            # reflection flux plane: downstream of the source
tran_straight_x = +6.5   # transmission plane for the straight reference run
tran_bend_y = +6.5       # transmission plane for the bend run (on the vertical arm)
span = mp.Vector3(0, w + 2)   # source / monitor line: core + 1 unit on each side (evanescent tail)
```

- **What**: fix the official dimensionless setup (ε = 12, w = 1, f = 0.15), corner location, and source/monitor coordinates.
- **Why**: Chapter 04 used 1 = 1 µm; here the length unit a is left scalable. For this nondispersive model, Maxwell’s equations are scale invariant: a = 1 µm gives wavelength 6.67 µm, while a ≈ 0.23 µm gives approximately 1.55 µm. Figures use a = 232.5 nm, wavelength in nm, and length in µm. Coordinates are chosen relative to the PML boundaries at ±7.
- **If wrong**: moving `refl_x` left (upstream) of the source breaks the intended downstream incident-field reference and can produce an incorrect R.

> **Pitfall**: `df = 0.1` spans the wide wavelength band 5–10a. Source power is almost zero at the edges, making T and R unstable. Trust the central part of the band (see interpretation below).

### ② Materials and geometry — what is placed where?

```python
def make_geometry(bend: bool):
    """Straight reference (bend=False) or the L-shaped bend (bend=True). Same width and material."""
    wg = mp.Medium(epsilon=eps_wg)
    if not bend:
        return [mp.Block(center=mp.Vector3(0, ycen), size=mp.Vector3(mp.inf, w), material=wg)]
    horizontal = mp.Block(center=mp.Vector3(0.5 * (-sx / 2 + xcen + w / 2), ycen),
                          size=mp.Vector3(sx / 2 + xcen + w / 2, w), material=wg)   # left PML -> corner
    vertical = mp.Block(center=mp.Vector3(xcen, 0.5 * (ycen - w / 2 + sy / 2)),
                        size=mp.Vector3(w, sy / 2 - ycen + w / 2), material=wg)     # corner -> top PML
    return [horizontal, vertical]
```

- **What**: one function creates either the straight reference or L-shaped bend with a flag. Two `Block` objects overlap by width w at the corner to make a continuous right angle.
- **Why**: only geometry should differ between reference and bend runs. A shared function prevents mismatched material, width, or coordinates. The horizontal arm must cross the left PML and the vertical arm the top PML to avoid end-face reflection.
- **If wrong**: ending the horizontal arm at `xcen - w/2` can leave a square gap at the corner and raise R. Ending the vertical arm inside the cell mixes end reflection into T.

### ②′ Rounded corner — a quarter annulus

```python
r = radius
cx, cy = xcen - r, ycen + r                      # center of the quarter ring
big = r + w / 2 + 1.0
geom = [mp.Cylinder(radius=r + w / 2, center=mp.Vector3(cx, cy), material=wg),    # outer disk: waveguide
        mp.Cylinder(radius=r - w / 2, center=mp.Vector3(cx, cy), material=air),   # inner disk: air -> ring
        # keep only the lower-right quadrant (x > cx, y < cy): cover the other three with air
        mp.Block(center=mp.Vector3(cx - big / 2, cy), size=mp.Vector3(big, 2 * big), material=air),
        mp.Block(center=mp.Vector3(cx + big / 2, cy + big / 2), size=mp.Vector3(big, big), material=air)]
# the two arms are appended AFTER this list, so they are drawn on top of the air blocks
```

- **What**: subtract a disk of radius r − w/2 from a disk of radius r + w/2, then cover three quadrants with air blocks, retaining only the lower-right quarter. The horizontal arm meets it at x = xcen − r and the vertical arm at y = ycen + r.
- **Why**: later Meep geometry objects overwrite earlier ones. The order “disk → air disk → air blocks → arms” implements the required differences. At r = 0 there is no annulus and the geometry returns to the sharp corner.
- **If wrong**: putting the arms before the air blocks erases their ends. Omitting the air blocks leaves a full ring instead of a bend.

### ③ Source — how is light injected?

```python
# A plain Ez line source (not an eigenmode source), as in the official tutorial.
sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ez,
                     center=mp.Vector3(src_x, ycen), size=span)]
```

- **What**: inject an Ez Gaussian pulse from a vertical line of length 3a across the horizontal arm.
- **Why**: unlike Chapter 04’s `EigenModeSource`, this simple line source is not matched to the mode profile. It also injects nonguided components; the reference run measures power actually transported along the guide for P_in. This is one reason two-run normalization is necessary.
- **If wrong**: changing `component` to `Ey` selects in-plane polarization in 2D and a different mode with different confinement. Restricting `size` to core width still runs, but worsens mode coupling and increases radiation noise.

### ④ Simulation and boundaries — the computation box and PML

```python
def make_sim(bend: bool):
    return mp.Simulation(cell_size=mp.Vector3(sx, sy), resolution=resolution,
                         boundary_layers=[mp.PML(dpml)],
                         geometry=make_geometry(bend), sources=sources)
```

- **What**: a function creates each `Simulation` in a 16 × 16 box with 1a PML on all sides, identical source and resolution, and only geometry changed.
- **Why**: a completed `Simulation` retains fields, making careless reuse problematic. Create a new instance for every run; one shared function keeps their settings consistent.
- **If wrong**: different `resolution` or `cell_size` changes grid positions and can make `load_minus_flux_data` attempt to subtract arrays of different sizes.

### ⑤ Monitor — what is measured (reference run)?

```python
sim = make_sim(bend=False)
refl  = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(refl_x, ycen), size=span))
tran0 = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(tran_straight_x, ycen), size=span))
```

- **What**: put reflection and transmission planes in the straight structure at x = −5.5 and x = +6.5. `add_flux` accumulates Poynting flux through each line by frequency.
- **Why**: the straight guide has negligible reflection, so transmitted flux supplies the reference power P_in launched along the guide. The reflection plane records incident DFT data in this run.
- **If wrong**: a transmission plane inside PML measures attenuated power, underestimating P_in and inflating T.

### ⑥ Running and stopping (reference run)

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(tran_straight_x, ycen), 1e-6))

P_in = np.array(mp.get_fluxes(tran0))     # what actually travels down the guide = input power
refl_data = sim.get_flux_data(refl)       # incident fields at the reflection plane (to subtract later)
freqs = np.array(mp.get_flux_freqs(tran0))
```

- **What**: run until Ez near the transmission plane meets the 10⁻⁶ decay criterion, then save P_in and the reflection-plane DFT field data.
- **Why**: `get_fluxes` returns power values, whereas `get_flux_data` returns the underlying fields. Subtract fields in the next run to remove the incident contribution correctly; power subtraction does not do the same operation.
- **If wrong**: an early stop misses the pulse tail and underestimates P_in. Incomplete incident DFT data also leaves residual incident contributions in R.

### ⑤′ Monitor — what is measured (bend run)?

```python
sim = make_sim(bend=True)
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(refl_x, ycen), size=span))
sim.load_minus_flux_data(refl, refl_data)  # subtract the incident part -> this monitor now sees reflection only
tran = sim.add_flux(fcen, df, nfreq,
                    mp.FluxRegion(center=mp.Vector3(xcen, tran_bend_y), size=mp.Vector3(w + 2, 0)))
```

- **What**: create the reflection plane at the same position in the bend and preload the negative reference incident data. The transmission plane becomes a horizontal line on the vertical arm at y = +6.5.
- **Why**: both the right-traveling incident pulse and left-traveling reflected pulse cross the reflection plane. Subtracting incident fields leaves only reflection when the run ends.
- **If wrong**: omitting this step leaves incident power at the reflection monitor, causing the same R formula to underestimate reflection or give a negative value.

> **Pitfall**: transmission-plane `size` is `(w + 2, 0)`, a horizontal line. In the vertical arm, light travels +y, so the cross-section must span x. Reusing `span` makes a vertical line parallel to propagation.

### ⑥′ Running and stopping (bend run)

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(xcen, tran_bend_y), 1e-6))
```

- **What**: now wait for Ez to decay at the end of the vertical arm, at the transmission-plane location.
- **Why**: the decay point should be where light passes last, which is the end of the vertical arm in a bend.
- **If wrong**: reusing the reference point (+6.5, −4) puts the point outside the guide in the bend geometry. The local field can vanish before the transmitted pulse has fully passed, ending the run prematurely.

### ⑦ Post-processing — converting fields into numbers

```python
T = np.array(mp.get_fluxes(tran)) / P_in      # transmitted fraction
R = -np.array(mp.get_fluxes(refl)) / P_in     # backward flux is negative -> flip the sign
L = 1.0 - T - R                               # what is left: radiated out at the corner
ic = nfreq // 2
print(f"T = {T[ic]:.4f}, R = {R[ic]:.4f}, radiation loss = {L[ic]:.4f}")
```

- **What**: divide both fluxes by P_in to obtain T and R, then interpret the remainder from 1 as radiation loss.
- **Why**: Meep flux is directional. Reflection travels −x and gives negative flux, so reverse the sign. Without a separate radiation monitor, `1 - T - R` is a residual estimate.
- **If wrong**: forgetting the sign reversal makes R negative and can push L above 1.

</details>

<h2 id="interpret">5. Interpret · Read measurements and limits together</h2>

### Quantify why transmission is low

| Geometry at 1550 nm | T | R | L = 1 − T − R |
|---|---|---|---|
| Sharp corner | 0.1997 | 0.2202 | 0.5801 |
| Radius 3a = 0.6975 µm | 0.9859 | 0.0003 | 0.0138 |

Only about 20% of the reference input reaches the upper arm in the sharp bend; the inferred radiation residual is about 58%. With increasing radius, reflection becomes small near 1a, while radiation decreases more slowly. The improvement starts flattening around 1.5–2a in this example.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/05/03_spectrum.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/05/03_spectrum.png' | relative_url }}" alt="Sharp-bend transmission, reflection, and residual radiation versus wavelength" loading="lazy">
  </a>
  <figcaption>Near the center wavelength 1550 nm (dashed line), radiation (green) is largest and T (blue) is near 0.2. At band edges (1160 nm, 2325 nm), weak source power makes ratios unstable, so read only qualitative trends. Longer wavelengths have weaker confinement and broader cladding tails, making the abrupt corner less severe and increasing T.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/05/04_radius_sweep.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/05/04_radius_sweep.png' | relative_url }}" alt="Measured curves showing higher transmission and lower reflection/radiation as corner radius increases" loading="lazy">
  </a>
  <figcaption>T, R, and inferred radiation when only the corner radius changes. Radius 0 is the sharp bend above. The axis is in µm using a = 232.5 nm.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/05/05_field_round.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/05/05_field_round.png' | relative_url }}" alt="Simulated Re(Ez) and amplitude fields in a rounded waveguide with radius 3a" loading="lazy">
  </a>
  <figcaption>Radius 3a = 0.70 µm. Standing-wave nodes in the horizontal arm disappear (reflection 0.03%), and little light leaks outside the corner.</figcaption>
</figure>

<aside class="lesson-note" markdown="1">
**Meaningful digits are part of the result.** Sharp-bend T changes from 0.1997→0.1894 with resolution 25→40, and to 0.1703 when PML thickness 1→1.5 and monitor positions are changed together. Read the trend as T ≈ 0.2. At radius 4a, T = 1.0031 is numerical error, not gain. Ratios at band edges where source power is only 0.005% of its peak have low reliability.
</aside>

<details markdown="1">
<summary>View all measurements, prediction comparisons, and convergence records</summary>

| Quantity | Value @ 1550 nm (6.67a) | Comparison |
|--------|-----------|-----------|
| T | 0.1997 | The official tutorial also demonstrates low T |
| R | 0.2202 | — |
| L (radiation residual) | 0.5801 | — |
| T + R | 0.4199 | Satisfies ≤ 1 |

### Rounding the corner: radius sweep









| Radius | µm | T | R | Radiation |
|---|---|---|---|---|
| 0 (sharp) | 0 | 0.200 | 0.220 | 0.580 |
| 0.5a | 0.12 | 0.487 | 0.052 | 0.462 |
| 1a | 0.23 | 0.746 | 0.001 | 0.253 |
| 1.5a | 0.35 | 0.907 | 0.001 | 0.092 |
| 2a | 0.47 | 0.964 | 0.000 | 0.036 |
| 3a | 0.70 | 0.986 | 0.000 | 0.014 |
| 4a | 0.93 | 1.003 | 0.000 | −0.003 |
| 6a | 1.40 | 1.000 | 0.000 | 0.000 |

Reflection is already very small at radius 1a (about 1/7 wavelength). Radiation falls more slowly, below 10% at 1.5a and to the 1% range at 3a. The knee of the loss curve is around 1.5–2a, near one wavelength inside the guide (1.92a); larger radii increase footprint for progressively smaller gains. T exceeding 1 by 0.3% at 4a is numerical error between reference and bend runs, not gain.

### Convergence (sharp bend)

| resolution | dpml | T | R | Radiation | Note |
|---|---|---|---|---|---|
| 25 | 1.0 | 0.200 | 0.220 | 0.580 | Baseline |
| 10 | 1.0 | 0.198 | 0.229 | 0.573 | Official-example resolution |
| 40 | 1.0 | 0.189 | 0.224 | 0.587 | 1.6 times resolution |
| 25 | 1.5 | 0.170 | 0.217 | 0.612 | Thicker PML; source/monitor planes moved 0.5a inward |

Across resolutions 10–40, T changes by roughly 5%. Thickening PML while moving the source and monitor planes inward by 0.5a lowers T by about 15%. The result depends on how radiation from the corner is captured between the transmission plane and PML. Sharp-bend T = 0.20 is therefore meaningful only to about one significant digit. Rounded bends (R ≥ 2a, where R denotes radius here) radiate much less and are less sensitive to this effect.

### Comparing predictions

| Quantity | Prediction (§2) | Simulation | Verdict |
|--------|-------------|-----------|------|
| T | Below 0.5 | 0.20 | ✅ |
| R | Tens of percent | 0.22 | ✅ |
| L | Largest fraction | 0.58 | ✅ |
| Field shape | Corner radiation lobes and weak vertical arm | Seen in the figure | ✅ |
| T + R | ≤ 1 | 0.42 | ✅ |

The trends were predicted correctly, but T = 0.20 required computation. T + R ≤ 1 is a consistency check rather than a prediction. A significant violation points to sign, normalization, or numerical problems; a small excess must be assessed with convergence.

**Validation checks**: T + R = 0.42 ≤ 1; source (x = −6.5), reflection plane (−5.5), and transmission plane (y = 6.5) all lie outside PML (\|x\|, \|y\| > 7); both runs stop by field decay.

### Supported claims and remaining limits

- Supported in this model: the sharp bend loses more than half its input as inferred radiation. A radius near one guided wavelength (1.5–2a, 0.35–0.47 µm) brings loss below 10%, with little further improvement beyond 3a.
- Not established: the second decimal place of sharp-bend T = 0.20. Resolution and monitor placement move it over 0.17–0.20. The knee for 3D guides or other index contrasts is not established, nor is the exact radiation fraction without a direct radiation-flux monitor.

</details>

<details markdown="1">
<summary>View the troubleshooting checklist</summary>

| Symptom | Cause | Fix |
|------|------|----------|
| Underestimated or negative reflectance | Missing `load_minus_flux_data` | Call it **immediately after** creating the bend reflection monitor |
| Negative R | Backward flux sign not reversed | `R = -get_fluxes(refl) / P_in` |
| `load_minus_flux_data` array-size error | Resolution, cell, or monitor positions differ | Create both runs with the same `make_sim` function |
| T ≈ 0 | Transmission section is a vertical line (`span`) parallel to light | On the vertical arm use horizontal `size=(w+2, 0)` |
| Unstable spectrum edges | Wide band with almost zero edge source power | Reduce `df` or interpret only the central ±30% |
| Unexpectedly large R | Reflection plane upstream of source, or thin PML | Use a **downstream** reflection plane and check `dpml ≥ λ/6` |

</details>

<h2 id="check">6. Check · Answer two questions</h2>

### 1. What happens to reflectance if you remove incident-field subtraction?

<details markdown="1">
<summary>Check the explanation</summary>

Both incident and reflected contributions remain in the reflection monitor. Applying the same minus-sign formula then underestimates reflectance or makes it negative. This subtraction is not a source changing the simulated field, so removing it does not itself change propagation of the transmitted field.

</details>

### 2. If L = 1 − T − R is 0.58, have we measured radiation as exactly 58%?

<details markdown="1">
<summary>Check the explanation</summary>

No. Here the residual of a nonabsorbing model is interpreted as radiation. Monitor position, PML, and grid errors also affect it. That precision needs a direct radiation-flux measurement and convergence checks.

</details>

<h2 id="reference">7. Reference · Complete code and original records</h2>

The complete program below is preserved from the original. Read it together with the environment and recorded results.

<details>
<summary>bend90.py (expand to read)</summary>
{% highlight python %}
"""Meep Example 05 - Bent waveguide and the radius trade-off (two-run flux normalization).

A dielectric waveguide (eps = 12, width 1) turns a 90 degree corner.
Run 1: straight waveguide  -> input power P_in and the "incident" flux data at the reflection plane.
Run 2: bent waveguide      -> transmitted flux (vertical arm) and reflected flux (incident part subtracted).
T = P_tran / P_in,  R = -P_refl / P_in,  radiation loss = 1 - T - R.
The sharp corner (radius 0) follows the official bend-flux tutorial; then the corner is rounded
with a quarter-ring of radius R and T is swept over R to find where the loss disappears.

Run:  python bend90.py            (~3 min on one core: sharp + radius sweep + convergence)
Out:  00_source.png, 01_layout.png, 02_field.png, 03_spectrum.png, 04_radius_sweep.png,
      05_field_round.png, 06_anim_sharp.gif, 06_anim_round.gif, result.json   (-> ../assets/05/)
"""
import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import (Label, animate_fields, annotated_layout, field_figure, line_figure,   # noqa: E402
                     record_frames, source_figure, spectrum_figure)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "05")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# Dimensionless units as in the official tutorial: 1 length unit = a (think 1 um).
eps_wg = 12.0            # waveguide permittivity (n = sqrt(12) = 3.46)
w = 1.0                  # waveguide width
fcen = 0.15              # center frequency -> wavelength 1/0.15 = 6.67 units
df = 0.1                 # source bandwidth
nfreq = 11               # number of frequencies in the flux monitors

# Physical reading used only for the figures: choose a so that the center wavelength is 1550 nm.
a_nm = 1550 * fcen       # = 232.5 nm per unit  -> waveguide width 233 nm, cell 3.72 um
a_um = a_nm / 1000

RESOLUTION = 25          # pixels per unit -> width = 25 px, wavelength in the guide (1.92) = 48 px
DPML = 1.0               # PML thickness
sx = sy = 16.0           # square cell, PML included

ycen = -4.0              # y of the input (horizontal) arm
xcen = +4.0              # x of the output (vertical) arm  -> corner at (xcen, ycen)
span = mp.Vector3(0, w + 2)   # source / monitor line: core + 1 unit on each side (evanescent tail)


def positions(dpml):
    """Source and monitor planes measured from the PML edge, so a thicker PML keeps them outside it."""
    edge = sx / 2 - dpml
    return {"src_x": -edge + 0.5,          # source: 0.5 outside the left PML
            "refl_x": -edge + 1.5,         # reflection flux plane: downstream of the source
            "tran_straight_x": edge - 0.5,  # transmission plane for the straight reference run
            "tran_bend_y": edge - 0.5}      # transmission plane for the bend run (on the vertical arm)


# ---------------------------------------------------------------- (2) materials & geometry
def make_geometry(bend: bool, radius: float = 0.0):
    """Straight reference (bend=False), sharp corner (radius=0) or rounded corner (radius>0).

    The rounded corner is a quarter ring: outer cylinder (waveguide) minus inner cylinder (air),
    cut down to one quadrant with air blocks; the two arms are drawn last so they stay intact.
    """
    wg = mp.Medium(epsilon=eps_wg)
    air = mp.Medium(epsilon=1.0)
    if not bend:
        return [mp.Block(center=mp.Vector3(0, ycen), size=mp.Vector3(mp.inf, w), material=wg)]
    r = radius
    cx, cy = xcen - r, ycen + r                      # center of the quarter ring
    geom = []
    if r > 0:
        big = r + w / 2 + 1.0
        geom += [mp.Cylinder(radius=r + w / 2, center=mp.Vector3(cx, cy), material=wg),
                 mp.Cylinder(radius=r - w / 2, center=mp.Vector3(cx, cy), material=air)]
        # keep only the lower-right quadrant (x > cx, y < cy)
        geom += [mp.Block(center=mp.Vector3(cx - big / 2, cy), size=mp.Vector3(big, 2 * big), material=air),
                 mp.Block(center=mp.Vector3(cx + big / 2, cy + big / 2), size=mp.Vector3(big, big), material=air)]
    # sharp corner: the arms overlap by w x w so the outer corner is filled (official geometry);
    # rounded corner: the arms stop where the ring begins
    x_end = xcen + w / 2 if r == 0 else xcen - r     # horizontal arm: left PML -> corner / ring
    horizontal = mp.Block(center=mp.Vector3(0.5 * (-sx / 2 + x_end), ycen),
                          size=mp.Vector3(sx / 2 + x_end, w), material=wg)
    y_start = ycen - w / 2 if r == 0 else ycen + r   # vertical arm: corner / ring -> top PML
    vertical = mp.Block(center=mp.Vector3(xcen, 0.5 * (y_start + sy / 2)),
                        size=mp.Vector3(w, sy / 2 - y_start), material=wg)
    return geom + [horizontal, vertical]


# ---------------------------------------------------------------- (3) source
def make_sources(dpml):
    """A plain Ez line source (not an eigenmode source), as in the official tutorial."""
    p = positions(dpml)
    return [mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ez,
                      center=mp.Vector3(p["src_x"], ycen), size=span)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(bend: bool, radius=0.0, resolution=RESOLUTION, dpml=DPML):
    return mp.Simulation(cell_size=mp.Vector3(sx, sy), resolution=resolution,
                         boundary_layers=[mp.PML(dpml)],
                         geometry=make_geometry(bend, radius), sources=make_sources(dpml))


_reference = {}


def reference_run(resolution, dpml):
    """RUN 1 (cached per resolution/PML): straight guide -> P_in and the incident flux data."""
    key = (resolution, dpml)
    if key in _reference:
        return _reference[key]
    p = positions(dpml)
    sim = make_sim(bend=False, resolution=resolution, dpml=dpml)
    # ------------------------------------------------------------ (5) monitors, run 1
    refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
    tran0 = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["tran_straight_x"], ycen), size=span))
    # ------------------------------------------------------------ (6) run 1 & stop condition
    sim.run(until_after_sources=mp.stop_when_fields_decayed(
                25, mp.Ez, mp.Vector3(p["tran_straight_x"], ycen), 1e-6))
    _reference[key] = {"P_in": np.array(mp.get_fluxes(tran0)),      # what actually travels down the guide
                       "refl_data": sim.get_flux_data(refl),         # incident fields at the reflection plane
                       "freqs": np.array(mp.get_flux_freqs(tran0))}
    return _reference[key]


def bend_run(radius=0.0, resolution=RESOLUTION, dpml=DPML, figures=False, field_png=None):
    """RUN 2: the bend. Returns T, R, L spectra (fractions of P_in)."""
    ref = reference_run(resolution, dpml)
    p = positions(dpml)
    sim = make_sim(bend=True, radius=radius, resolution=resolution, dpml=dpml)
    # ------------------------------------------------------------ (5) monitors, run 2
    refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
    sim.load_minus_flux_data(refl, ref["refl_data"])  # subtract the incident part -> reflection only
    tran = sim.add_flux(fcen, df, nfreq,
                        mp.FluxRegion(center=mp.Vector3(xcen, p["tran_bend_y"]), size=mp.Vector3(w + 2, 0)))
    decay_pt = (xcen, p["tran_bend_y"])
    if figures:
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=dpml, unit="um", axis_scale=a_um, axis_step=0.5,
            figsize=(7.5, 7.2), pml_xy=(-3.0, -sy / 2 + dpml / 2),
            params_text=(f"a = {a_nm:.1f} nm  (1 Meep unit)\n"
                         f"eps={eps_wg:g}  w={w:g}a={w*a_nm:.1f}nm  dpml={dpml:g}a\n"
                         f"wl={1/fcen:.2f}a={a_nm/fcen:.0f}nm  res={resolution}/a  cell={sx:g}a"),
            params_xy=(-6.6, 6.6), decay_point=decay_pt, decay_text_xy=(4.6, 5.6),
            title="90-deg waveguide bend (eps = 12, w = 1): Ez line source, flux monitors, PML",
            labels=[
                Label("horizontal arm (geometry)", (-1.0, ycen), (-3.5, -1.8), step=2, color="black"),
                Label("vertical arm (geometry)", (xcen - 0.5, 2.0), (-2.5, 3.5), step=2, color="black"),
                Label("Ez line source", (p["src_x"], ycen - 1.6), (-6.3, -6.2), step=3, color="red"),
                Label("flux: reflection (minus incident)", (p["refl_x"], ycen + 1.6), (-6.3, 0.2), step=5, color="blue"),
                Label("flux: transmission", (xcen - 1.5, p["tran_bend_y"]), (0.0, 5.0), step=5, color="blue"),
            ])
    want_field = figures or field_png is not None
    if want_field:
        nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml, sy - 2 * dpml))
        dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)
    # ------------------------------------------------------------ (6) run 2 & stop condition
    sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
    # ------------------------------------------------------------ (7) post-processing
    T = np.array(mp.get_fluxes(tran)) / ref["P_in"]      # transmitted fraction
    R = -np.array(mp.get_fluxes(refl)) / ref["P_in"]     # backward flux is negative -> flip the sign
    L = 1.0 - T - R                                      # what is left: radiated out at the corner
    if want_field:
        ez = sim.get_dft_array(dft, mp.Ez, 0)
        eps = sim.get_array(vol=nonpml, component=mp.Dielectric)
        extent_um = [v * a_um for v in (-(sx / 2 - dpml), sx / 2 - dpml, -(sy / 2 - dpml), sy / 2 - dpml)]
        field_figure(ez, extent_um, os.path.join(OUT, field_png or "02_field.png"), core_halfwidth=None,
                     eps=eps, wl=round(a_nm / fcen), wl_unit="nm", component="Ez",
                     layout="row", aspect="equal", unit="um")
    return {"T": T, "R": R, "L": L, "freqs": ref["freqs"]}


t_all = time.time()
ic = nfreq // 2

# source waveform and spectrum; the monitor band is fcen +- df/2
src_info = source_figure(fcen, df, os.path.join(OUT, "00_source.png"), mon_fcen=fcen, mon_df=df,
                         wl_scale=a_nm, wl_unit="nm", time_unit="a/c")

# ================================================================ sharp corner (official example)
t0 = time.time()
sharp = bend_run(0.0, figures=True)
wall_sharp = time.time() - t0
wl = 1 / sharp["freqs"]
print(f"sharp: T = {sharp['T'][ic]:.4f}, R = {sharp['R'][ic]:.4f}, radiation loss = {sharp['L'][ic]:.4f}  ({wall_sharp:.0f} s incl. reference)")
print(f"T over band {wl.min():.2f}-{wl.max():.2f}: {sharp['T'].min():.3f} .. {sharp['T'].max():.3f}")
spectrum_figure(wl * a_nm, {"T (transmitted)": sharp["T"], "R (reflected)": sharp["R"], "1 - T - R (radiated)": sharp["L"]},
                os.path.join(OUT, "03_spectrum.png"), unit="nm", mark=1550, mark_label="1550 nm (fcen)")

# ================================================================ radius sweep
radii = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]
sweep = []
for r in radii:
    if r == 0.0:
        res = sharp
    else:
        res = bend_run(r, field_png=("05_field_round.png" if r == 3.0 else None))
    sweep.append({"radius_a": r, "radius_um": r * a_um, "radius_over_wl": r * fcen,
                  "T": float(res["T"][ic]), "R": float(res["R"][ic]), "L": float(res["L"][ic])})
    print(f"radius {r:.1f} a ({r*a_um:.2f} um): T={res['T'][ic]:.4f} R={res['R'][ic]:.4f} L={res['L'][ic]:.4f}")
line_figure([s["radius_um"] for s in sweep],
            {"T (transmitted)": [s["T"] for s in sweep], "R (reflected)": [s["R"] for s in sweep],
             "1 - T - R (radiated)": [s["L"] for s in sweep]},
            os.path.join(OUT, "04_radius_sweep.png"), xlabel=f"bend radius [um]  (a = {a_nm:.1f} nm, wl = 1550 nm)")

# ================================================================ animations: sharp corner vs rounded corner (radius 3a)
# Fresh simulations with the same source; record from before the pulse peak (t0 = 5/df) until the
# pulse has gone from the source to the top monitor along the guide (distance ~ 21 a at n_eff ~ 2.5).
p = positions(DPML)
nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * DPML, sy - 2 * DPML))
extent_um = [v * a_um for v in (-(sx / 2 - DPML), sx / 2 - DPML, -(sy / 2 - DPML), sy / 2 - DPML)]
for tag, r_anim in (("sharp", 0.0), ("round", 3.0)):
    sim_anim = make_sim(bend=True, radius=r_anim)
    sim_anim.init_sim()
    eps_anim = sim_anim.get_array(vol=nonpml, component=mp.Dielectric)
    frames, times = record_frames(sim_anim, nonpml, mp.Ez, t_start=5.0 / df - 2.0 / df,
                                  t_end=5.0 / df + 21.0 * 2.5 + 10.0, n_frames=60)
    animate_fields(frames, times, extent_um, os.path.join(OUT, f"06_anim_{tag}.gif"), eps=eps_anim,
                   lines=[((p["src_x"] * a_um, (ycen - 1.5) * a_um), (p["src_x"] * a_um, (ycen + 1.5) * a_um), "red", "Ez source"),
                          (((xcen - 1.5) * a_um, p["tran_bend_y"] * a_um), ((xcen + 1.5) * a_um, p["tran_bend_y"] * a_um), "blue", "flux: transmission")],
                   time_unit="a/c", figsize=(5.4, 4.8), title=f"{tag} corner", legend_loc="lower right")

# ================================================================ convergence (sharp corner)
convergence = [{"resolution": RESOLUTION, "dpml": DPML, "T": sweep[0]["T"], "R": sweep[0]["R"], "L": sweep[0]["L"]}]
for res_px, dpml in ((10, 1.0), (40, 1.0), (25, 1.5)):   # change one thing at a time
    t0 = time.time()
    r = bend_run(0.0, resolution=res_px, dpml=dpml)
    convergence.append({"resolution": res_px, "dpml": dpml, "T": float(r["T"][ic]), "R": float(r["R"][ic]),
                        "L": float(r["L"][ic]), "wall_s": time.time() - t0})
    print(f"convergence res={res_px} dpml={dpml}: T={r['T'][ic]:.4f} R={r['R'][ic]:.4f} L={r['L'][ic]:.4f}")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"T": sweep[0]["T"], "R": sweep[0]["R"], "loss": sweep[0]["L"],
                   "a_nm": a_nm, "wavelengths_a": wl.tolist(), "wavelengths_nm": (wl * a_nm).tolist(),
                   "T_spectrum": sharp["T"].tolist(), "R_spectrum": sharp["R"].tolist(),
                   "radius_sweep": sweep, "convergence": convergence, "source": src_info,
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__},
                  f, indent=2)
{% endhighlight %}
</details>

<details markdown="1">
<summary>View the original run log and reproduction environment</summary>

Unlike the excerpts in §4, the complete code includes figure saving and result.json output. The shared plotting helper `blogfig.py` (`annotated_layout`, `field_figure`, `spectrum_figure`) lives in the same folder (`code/`). Complete code and helper: [GitHub code folder](https://github.com/jin-castle/meep-examples/blob/main/code).

**Recorded output (rerun on 2026-10-23)**:
```
sharp: T = 0.1997, R = 0.2202, radiation loss = 0.5801  (10 s incl. reference)
T over band 5.00-10.00: 0.169 .. 0.512
radius 0.0 a (0.00 um): T=0.1997 R=0.2202 L=0.5801
radius 0.5 a (0.12 um): T=0.4865 R=0.0518 L=0.4617
radius 1.0 a (0.23 um): T=0.7458 R=0.0014 L=0.2528
radius 1.5 a (0.35 um): T=0.9073 R=0.0009 L=0.0918
radius 2.0 a (0.47 um): T=0.9638 R=0.0005 L=0.0358
radius 3.0 a (0.70 um): T=0.9859 R=0.0003 L=0.0138
radius 4.0 a (0.93 um): T=1.0031 R=0.0001 L=-0.0031
radius 6.0 a (1.40 um): T=0.9995 R=0.0000 L=0.0005
convergence res=10 dpml=1.0: T=0.1983 R=0.2287 L=0.5730
convergence res=40 dpml=1.0: T=0.1894 R=0.2241 L=0.5865
convergence res=25 dpml=1.5: T=0.1703 R=0.2173 L=0.6124
```

**Reproduction environment**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · run `python bend90.py` (approximately 12 s, single core)

</details>

<details markdown="1">
<summary>View applications and next learning topics</summary>

### Applications

Bend radius sets chip footprint. Doubling the radius quadruples the area of a ring, and foundry design rules specify minimum bend radii.

| Application | What this lesson contributes | What comes next |
|---|---|---|
| PIC routing and footprint | Radius–loss curve and its knee | Inverse-designed bends in Chapter 09 |
| Ring resonators and spiral delay lines | Curvature loss at small radii affects Q; radius also affects FSR | Rings in Chapter 12 |
| Foundry PDK minimum-bend-radius rules | A loss-curve knee illustrates the rationale; the 1.5–2a value is specific to this model | — |
| Any input-normalized output measurement | Two-run normalization | Chapter 06 onward |

</details>

- [Official tutorial: Transmittance Spectrum of a Waveguide Bend](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend)
- [`add_flux` / `load_minus_flux_data` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#flux-spectra) · [`Cylinder` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#cylinder)
- Previous: [04 · Straight waveguide and guided modes]({{ site.baseurl }}/en/straight-waveguide/) · Next: [06 · Binary grating and diffraction orders]({{ site.baseurl }}/en/binary-grating/)
