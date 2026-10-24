---
layout: lesson
permalink: /en/point-line-source/
lesson_title: "Point or line: how does light spread?"
lesson_summary: "Does changing the shape of a source change the direction of its light? Observe the wavefronts, then use snapshot times and power through four sides to explain the difference."
lesson_goals:
  - "Explain the strongest radiation directions from point-source and line-source wavefronts."
  - "Calculate a snapshot wavefront position from the pulse peak time t0."
  - "Read the four flux-box fractions and recognize the limits of this measurement."
lesson_prerequisites: "Start with wavelength and wave speed. Running the code requires a Meep and Python environment."
date: 2026-10-21
title: "Meep Example 01 · Point source and line source — source placement, the pulse time t0, and a flux box for directionality"
title_en: "Meep Example 01 · Point source and line source — source placement, the pulse time t0, and a flux box for directionality"
lang: en
translation_key: point-line-source
series: meep-examples
part: 1
level: beginner
runtime: "21 s (single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#fields-in-a-waveguide"
tags: [meep, fdtd, source, point-source, line-source, flux]
image: /assets/meep/01/02_snapshots.png
excerpt: "a single Ez source in an empty 2D cell, first as a point, then as a 3 µm line. Snapshots after the pulse peak, and a box of four flux planes around the source."
---
<details markdown="1">
<summary>English summary</summary>

- **What**: a single Ez source in an empty 2D cell, first as a point, then as a 3 µm line. Snapshots after the pulse peak, and a box of four flux planes around the source.
- **Result**: the point source radiates exactly 25 % through each side of the box; the 3 µm line sends 92 % through the two sides facing it. The wavefront peak sits on the circle r = c (t − t0).
- **Takeaway**: in FDTD a picture is a time stamp. Know the pulse time t0 = 5/fwidth before you read any field, and derive the recording window from the source and the distances, not by guessing.
- **Code**: full script at the bottom, ~21 s on one core.

</details>

<h2 id="observe">1. Observe · What the source shape changes</h2>

Place one **source** in empty space. On the left it is a point; on the right it is a vertical line 3 µm long. Both images were captured at the same time. First look at the directions in which the strongest colors extend.

<div class="figure-pair">
<figure class="lesson-figure">
  <a href="{{ '/assets/meep/01/03_point_vs_line.png' | relative_url }}" data-lightbox aria-label="Enlarge the original point-source wavefront and shared color bar">
    <svg viewBox="0 90 460 370" role="img" aria-labelledby="point-field-title"><title id="point-field-title">Simulated Re(Ez) wavefronts spreading as concentric circles from a point source</title><image href="{{ '/assets/meep/01/03_point_vs_line.png' | relative_url }}" width="1065" height="463" /></svg>
  </a>
  <figcaption>Point source: the wavefronts spread as concentric circles.</figcaption>
</figure>
<figure class="lesson-figure">
  <a href="{{ '/assets/meep/01/03_point_vs_line.png' | relative_url }}" data-lightbox aria-label="Enlarge the original line-source wavefront and shared color bar">
    <svg viewBox="460 90 460 370" role="img" aria-labelledby="line-field-title"><title id="line-field-title">Simulated Re(Ez) wavefronts spreading more strongly left and right from a vertical 3 micrometer line source</title><image href="{{ '/assets/meep/01/03_point_vs_line.png' | relative_url }}" width="1065" height="463" /></svg>
  </a>
  <figcaption>Vertical line source: light spreads more strongly left and right.</figcaption>
</figure>
</div>
<p class="lesson-figure-scale">Both images show t0 + 3.6 in a cell without PML. They share the Re(Ez) color range from −1 (red) to +1 (blue). Select an image to see the original with its color bar.</p>

<aside class="lesson-note" markdown="1">
**These images show a 2D Ez simulation in vacuum.** Here the point source is the cross-section of a line current extending in the z direction, perpendicular to the screen. Distinguish it from the radiation pattern of a real 3D point source or dipole.
</aside>

### Where this is useful

Point and line sources are inputs to simulations, rather than devices. The source type and location determine the quantities measured later, so the three experiments here provide a starting point for the following problems.

| Application | What this lesson contributes | What comes next |
|---|---|---|
| LED, OLED, and quantum-dot emission-layer models | Point source as one emitting molecule (electric dipole); pulse time t0 and directional distribution | 3D patterns in Chapter 10 and LDOS in Chapter 11 |
| Antennas and RF devices | Point-source radiation patterns and line-source directionality (the simplest array-antenna model) | near2far in Chapter 10 |
| Incident beams for fibers and grating couplers | A line source as a finite-width incident wave; conditions for nearly planar wavefronts | Plane waves in Chapter 17 and Gaussian beams in Chapter 19 |
| Any flux measurement | A flux box surrounding the source and the surface-normal convention | The reference run in Chapter 03 |

<h2 id="predict">2. Predict · Does equal power leave in all four directions?</h2>

Imagine enclosing the source in a square box and measuring power through each side. For a vertical line source, what fraction of the total power will pass through **the left and right sides (±x)**?

<fieldset class="prediction">
  <legend>Choose one answer before reading the result.</legend>
  <label><input type="radio" name="direction-prediction" value="equal"> About 50% · Similar power leaves through all four sides</label>
  <label><input type="radio" name="direction-prediction" value="horizontal"> More than 80% · More power travels left and right, perpendicular to the line</label>
  <label><input type="radio" name="direction-prediction" value="vertical"> Less than 20% · More power travels up and down, along the line</label>
</fieldset>

<details markdown="1">
<summary>Check the reasoning behind your prediction</summary>

All points on the line oscillate in phase. Their waves reinforce one another in the left and right directions, perpendicular to the line, so **more than 80%** is a reasonable prediction. The flux measurement below gives the precise value. For a point source, symmetry gives 25% per side and 50% for the two horizontal sides together.

</details>

<h2 id="understand">3. Understand · Read shape and time together</h2>

{% include chapter-illustration.html %}

<!-- concept-illustration:part-01:start -->

<p class="lesson-note">This concept diagram explains source shape. Diffraction at the ends of the line leaves curved wavefronts. The actual flux measurement uses the PML and box shown in the layout below.</p>

<!-- concept-illustration:part-01:end -->

### Wavefront shape

Light from a 2D Ez point source spreads as a cylindrical wave. Its wavefronts are concentric circles, and its amplitude decreases approximately as 1/√r with distance. A line source of length L is a set of point sources oscillating in phase along the line. When L exceeds the wavelength, the waves reinforce in the perpendicular ±x directions and cancel along ±y. Diffraction remains at the two ends of the finite line.

### When did the wavefront start?

This pulse is not strongest at time 0. First calculate **the peak time t0 = 5/fwidth = 15.5**. In vacuum c = 1, so 3.6 time units after the peak leaves, its wavefront radius is 3.6 µm.

$$r_{\mathrm{peak}} = c\,(t-t_0)$$

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/01/00_source.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/01/00_source.png' | relative_url }}" alt="Time waveform and spectrum of the Gaussian source. The pulse width is 3.1 and the peak time is 15.5." loading="lazy">
  </a>
  <figcaption>The pulse width is 3.1 and the peak is at t0 = 15.5. The weak leading edge emitted before the peak reaches the wall first.</figcaption>
</figure>

<aside class="lesson-note" markdown="1">
**Reflections can appear before the peak reaches the wall.** The weak leading edge, approximately 2 × width = 6.2 ahead of the peak, reaches it first. Experiments A/B, which capture wavefront images, have no PML; experiment C, which measures power, does have PML.
</aside>

<details markdown="1">
<summary>Explore the equations and symbols</summary>

$$
E_z(r,t)\propto \frac{1}{\sqrt r}\,\cos\!\big(k r-\omega t\big),\qquad r_{\mathrm{peak}}(t)=c\,(t-t_0),\qquad
P_{+x}=P_{-x}=P_{+y}=P_{-y}=\tfrac14 P
$$

| Symbol | Meaning | Code variable |
|------|----|-----------|
| width | Pulse-envelope width (time) | `1 / fwidth` |
| $t_0$ | Pulse peak time = 5 × width | `t0 = CUTOFF / fwidth` |
| $r_{\mathrm{peak}}$ | Radius of the peak wavefront at time t | `r_front = offsets[-1]` |
| $d_{\mathrm{wall}}$ | Distance from the source to the nearest wall | `d_wall` |
| $P_{\pm x}, P_{\pm y}$ | Outward power through the four box sides | `mp.get_fluxes(mons["+x"])`, etc. |

</details>

<h2 id="run">4. Run · Change only the line length</h2>

Run the original code first to obtain a baseline. The reproduction environment is **Meep 1.33.0 · Python 3.11**, and the recorded runtime is approximately 21 seconds on one core. Put `point_line_source.py` and `blogfig.py` from the [complete code and shared helpers](https://github.com/jin-castle/meep-examples/blob/main/code) in the same folder. You can also use the [complete code](#reference) below.

```bash
OMP_NUM_THREADS=1 python point_line_source.py
```

After the run, find **x-sides** on the `C. line source` line. The original value is approximately **0.919**. Then change `line_len = 3.0` to `line_len = 1.0` and run again. A line shorter than the 1.55 µm wavelength behaves more like a point source, so the left/right fraction should decrease. Record and compare both values. You must measure the modified run yourself.

### What is measured?

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/01/01_layout.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/01/01_layout.png' | relative_url }}" alt="Layout of experiment C: central source, four-sided flux box, outer PML, and field-decay monitoring point." loading="lazy">
  </a>
  <figcaption>Experiment C surrounds the central source in a 10 × 10 µm cell with a four-sided flux box. Its half-width is 2.5 µm, and the outer PML absorbs returning waves.</figcaption>
</figure>

Add the powers through all four sides, then divide each by that sum. The left (−x) and bottom (−y) sides require **`weight=-1` to count outward power as positive**. The A/B wavefront images use a separate 12 × 8 µm cell, a source at (−2, 0), and no PML.

<details markdown="1">
<summary>Design parameters and differences from the lecture example</summary>

| Parameter | Value | Reason | Effect of changing it |
|----------|-----|-------------|--------|
| `wl` | 1.55 µm | Telecom wavelength; time is measured in µm/c | Changes wavefront spacing |
| `fwidth` | 0.5 × fcen = 0.323 | Wide band = short pulse (about 2 cycles), with distinct concentric rings | A narrower band lengthens the pulse and blurs the rings |
| `t0` | 5/fwidth = 15.5 | Default Meep cutoff of 5 | Set by fwidth, rather than chosen independently |
| `RESOLUTION` | 20 px/µm | 31 px per wavelength | At 10, wavefronts become coarse |
| Snapshot cell, source | 12 × 8 µm, (−2, 0) | 4 µm to the nearest wall | Placing the source near a wall introduces reflections almost immediately |
| Last snapshot | t0 + 3.6 | Before the peak reaches the wall (4 µm) | Later images include reflection of the peak |
| `line_len` | 3.0 µm | About 2 wavelengths, enough for clear directionality | A subwavelength line resembles a point |
| Flux cell, `half` | 10 × 10 µm, 2.5 µm | Box lies between the source ends (±1.5) and PML (±4) | A box touching the source cuts through it |

**Difference from the lecture notebook**: week 2 uses fwidth 0.18 (a long pulse) and only examines snapshots. This lesson uses a shorter pulse for distinct rings and adds a PML-enclosed flux-box experiment (C) to quantify directionality.

</details>

<details markdown="1">
<summary>Code walkthrough · Roles and pitfalls of seven steps</summary>

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → running and stopping → post-processing.
> There are three experiments (A snapshots, B point versus line, C flux box), so steps ④–⑦ appear twice.

### ① Units and parameters — which numbers are fixed?

```python
import numpy as np
import meep as mp

# 1 length unit = 1 um, c = 1: a wave travels 1 um per time unit, so time is in um/c.
wl = 1.55                     # wavelength [um]
fcen = 1 / wl                 # center frequency [1/um]
fwidth = 0.5 * fcen           # wide band -> short pulse (~2 periods): clean concentric rings
CUTOFF = 5.0                  # Meep default: GaussianSource peaks at t0 = CUTOFF / fwidth
t0 = CUTOFF / fwidth          # pulse peak time
RESOLUTION = 20               # pixels per um (31 px per wavelength)

sx_a, sy_a = 12.0, 8.0        # experiment A/B cell, no PML
src_a = mp.Vector3(-2.0, 0.0) # source off-center: nearest wall 4 um away
line_len = 3.0                # finite line source length [um]
d_wall = min(sx_a / 2 - abs(src_a.x), sy_a / 2 - abs(src_a.y))
```

- **What**: choose wavelength and bandwidth, then calculate the pulse peak time t0.
- **Why**: `GaussianSource` is not at its active peak at t = 0. Its envelope reaches its maximum at t0 = 5/fwidth and gradually rises and falls over roughly 2·width on either side. You need this timing to decide when to take snapshots.
- **If wrong**: narrowing fwidth lengthens width, causing rings to overlap and delaying t0. The same `until` can then stop the run before the source becomes appreciable.

> **Pitfall**: if a small `until` stops the simulation before the source becomes appreciable, the field is only numerical noise. Normalizing that field still fills the image with patterns. The timing, rather than the calculation, is wrong.

### ② Materials and geometry — what is placed where?

```python
geometry = []                 # nothing: an empty cell is vacuum (default_material = air)
```

- **What**: there is no structure; the empty cell is vacuum.
- **Why**: the source itself is the subject. A structure would add reflection and scattering, obscuring its behavior.
- **If wrong**: changing `default_material` fills the empty cell with that material. Wavelength decreases by a factor of n, and the wavefront-radius prediction uses c/n instead of c in c(t − t0).

### ③ Source — how is light injected?

```python
def make_source(center, size=mp.Vector3(0, 0, 0)):
    """size (0,0,0) = point source; size (0, L, 0) = line source of length L along y."""
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center, size=size)]
```

- **What**: emit a Gaussian pulse in the Ez component at a point or along a line.
- **Why**: `size` determines the source shape. Zero gives a point; a length along one axis gives a line. All points on the line oscillate in phase.
- **If wrong**: choosing `Ex` or `Ey` selects in-plane polarization (Hz modes) in 2D and introduces angular dependence even for a point source. Use Ez for this isotropy check.

### ④ Simulation and boundaries — the computation box and PML

```python
def make_sim(cell, sources, dpml=0.0, resolution=RESOLUTION):
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=[mp.PML(dpml)] if dpml > 0 else [], sources=sources)
```

- **What**: a `Simulation` whose only changes are cell size, source, and whether PML is present.
- **Why**: snapshot experiments deliberately omit PML to show what the boundaries do. The flux experiment includes PML; returning waves would otherwise contaminate the source power through the four sides.
- **If wrong**: a long run without PML lets waves bounce between the walls dozens of times and fills the cell with standing waves. This is the subject of Chapter 02.

### ⑤ Monitor — what is measured (the flux box)?

```python
half = 2.5
sides = {
    "+x": mp.FluxRegion(center=mp.Vector3(+half, 0), size=mp.Vector3(0, 2 * half)),
    "-x": mp.FluxRegion(center=mp.Vector3(-half, 0), size=mp.Vector3(0, 2 * half), weight=-1),
    "+y": mp.FluxRegion(center=mp.Vector3(0, +half), size=mp.Vector3(2 * half, 0)),
    "-y": mp.FluxRegion(center=mp.Vector3(0, -half), size=mp.Vector3(2 * half, 0), weight=-1),
}
mons = {k: sim.add_flux(fcen, 0, 1, reg) for k, reg in sides.items()}
```

- **What**: four sides of a square surrounding the source, accumulating Poynting flux at the center frequency.
- **Why**: Meep counts flux along the positive normal (+x or +y) as positive. The outward normals of the left and bottom sides are −x and −y, so `weight=-1` makes all four readings outward powers.
- **If wrong**: omitting the weight makes the −x reading negative and drives the total near zero. A box touching the end of the line source cuts through the source and distorts the measurement.

### ⑥ Running and stopping — when should the simulation end?

```python
# A: snapshots. `until` counts from NOW, so pass the difference to the next target time.
prev = 0.0
for off in (0.0, 0.8, 1.6, 2.4, 3.2, 3.6):
    sim.run(until=(t0 + off) - prev)
    prev = t0 + off
    fields.append(sim.get_array(center=mp.Vector3(), size=mp.Vector3(sx_a, sy_a), component=mp.Ez))

# C: flux. run until the pulse has left through the PML.
sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(half + 0.8, 0), 1e-6))
```

- **What**: for snapshots, stop and extract fields at intervals of 0.8 after t0. For flux, continue until the pulse has fully left.
- **Why**: `get_array` returns the field at the instant the simulation stops, so timing determines the image. `until` specifies an interval from now, not an absolute time; pass the difference.
- **If wrong**: passing `until=t0 + off` each time accumulates extra time from the second snapshot onward. Cutting off flux at a fixed time can omit the pulse tail and underestimate the sum.

### ⑦ Post-processing — converting fields into numbers

```python
p = {k: float(mp.get_fluxes(m)[0]) for k, m in mons.items()}
total = sum(p.values())
fractions = {k: v / total for k, v in p.items()}            # point: 0.25 each by symmetry

# is the peak on the predicted circle?  mean |Ez| on the ring vs. over the whole cell
rr = np.hypot(gx, gy)                                        # distance from the source on the grid
ring = np.abs(ez_last)[(rr > r_front - 0.4) & (rr < r_front + 0.4)].mean()
everywhere = np.abs(ez_last).mean()
```

- **What**: divide each side power by their sum; in the last snapshot, compare mean |Ez| on the predicted circle with the cell mean.
- **Why**: fractions remove the arbitrary absolute source strength and allow direct point/line comparison. A clearly higher mean on the circle indicates that the peak is at the predicted position.
- **If wrong**: dividing by one side rather than the total can make a “fraction” exceed 1. Making the ring thickness (±0.4) wider than a wavelength averages several rings together and removes contrast.

</details>

<h2 id="interpret">5. Interpret · Check the pictures with numbers</h2>

**About 92% of line-source power passes through the left and right sides.** The point source distributes 25% to each side. The wavefront difference observed earlier also appears in the flux measurement.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/01/04_flux_box.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/01/04_flux_box.png' | relative_url }}" alt="Power fractions through four sides. Each point-source side is 0.25; each line-source left/right side is 0.4594 and each top/bottom side is 0.0406." loading="lazy">
  </a>
  <figcaption>The line sends a combined 0.919 through the left/right sides and 0.081 through the top/bottom sides. Diffraction at the ends of the finite line leaves nonzero vertical power.</figcaption>
</figure>

<aside class="lesson-note" markdown="1">
**These are power fractions through a nearby box.** The box is 2.5 µm (about 1.6λ) from the source, so this is not a distant radiation-pattern measurement. Far-field analysis requires near2far. Also, the symmetry of a 2D Ez point source does not imply isotropic radiation from a 3D dipole.
</aside>

### Where is the peak as time passes?

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/01/02_snapshots.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/01/02_snapshots.png' | relative_url }}" alt="Six point-source wavefront snapshots from the pulse peak t0 to t0 + 3.6. The last dashed circle has radius 3.6 µm." loading="lazy">
  </a>
  <figcaption>The last dashed circle marks the predicted radius of 3.6 µm. Mean |Ez| on it is 1.26 times the cell mean. All six panels share the same color scale.</figcaption>
</figure>

In a 12 × 8 µm cell without PML, the peak wavefront expands and fades. The small patterns near the edges come from the weak leading edge reflecting from the walls before the peak arrives. [02 · Boundary conditions and PML]({{ site.baseurl }}/en/boundary-pml/) continues with how to absorb these reflections.

### Watch the time evolution

Unlike the snapshots above, these animations place the source **at the center of a 12 × 12 µm cell**. They were recorded without PML, from t0 − 2·width until before the peak approaches the wall. They play automatically; pausing shows the static A/B comparison figures above. The image links also open the original GIFs.

<div class="figure-pair">
  <figure class="lesson-figure lesson-animation">
    <a href="{{ '/assets/meep/01/05_anim_point.gif' | relative_url }}" data-lightbox>
      <img src="{{ '/assets/meep/01/05_anim_point.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/01/05_anim_point.gif' | relative_url }}" data-static-src="{{ '/assets/meep/01/02_snapshots.png' | relative_url }}" alt="Concentric wavefronts from a point source centered in a 12 × 12 µm cell. Pausing shows six snapshots from the 12 × 8 µm cell." loading="lazy">
    </a>
    <button class="animation-toggle" type="button" hidden>Pause animation</button>
    <figcaption>Point source: concentric circles spread in every direction. The static figure and animation use different cell layouts.</figcaption>
  </figure>
  <figure class="lesson-figure lesson-animation">
    <a href="{{ '/assets/meep/01/05_anim_line.gif' | relative_url }}" data-lightbox>
      <img src="{{ '/assets/meep/01/05_anim_line.gif' | relative_url }}" data-animation-src="{{ '/assets/meep/01/05_anim_line.gif' | relative_url }}" data-static-src="{{ '/assets/meep/01/03_point_vs_line.png' | relative_url }}" alt="Horizontal wavefronts and edge diffraction from a central 3 µm line source in a 12 × 12 µm cell. Pausing shows the point/line comparison figure." loading="lazy">
    </a>
    <button class="animation-toggle" type="button" hidden>Pause animation</button>
    <figcaption>Line source: compare the strong left/right wavefronts with edge diffraction. The static figure and animation use different cell layouts.</figcaption>
  </figure>
</div>

<details markdown="1">
<summary>Numerical comparisons and convergence record</summary>

| Quantity | Value | Comparison |
|--------|-----|-----------|
| Mean \|Ez\| on the predicted circle (r = 3.6 µm) / cell mean | 0.162 / 0.128 = 1.26 | A ratio clearly above 1 places the peak on the circle |
| Point-source fractions through four sides | 0.2500, 0.2500, 0.2500, 0.2500 | Isotropic: 0.25 |
| Line-source sum through ±x | 0.919 | — |
| Line-source sum through ±y | 0.081 | — |

### Comparing predictions

| Quantity | Physical prediction | Simulation | Verdict |
|--------|-------------|-----------|------|
| Point-source wavefront shape | Concentric circles | Concentric circles (figures, GIF) | ✅ |
| Peak radius at t0 + 3.6 | 3.6 µm | Circle mean is 1.26 times the cell mean | ✅ |
| Four point-source box fractions | 0.25 each | 0.2500 each | ✅ |
| Line-source ±x fraction | Above 0.8 | 0.919 | ✅ |
| Cell without PML | Wall reflections visible | Leading-edge reflection visible near the edges | ✅ |

The predictions hold, but one feature appears earlier than expected. “Before the peak reaches the wall” applies only to the peak: the leading edge, 2·width ahead, has already reached the wall before t0. A shorter pulse reduces the distance between leading edge and peak, so the wider bandwidth helps. Removing the effective walls requires PML.

### Convergence

| resolution | dpml | Point-source max\|fraction − 0.25\| | Line-source ±x sum | Note |
|---|---|---|---|---|
| 20 | 1.0 | 10⁻¹⁶ | 0.9188 | Baseline |
| 40 | 1.0 | 10⁻¹⁶ | 0.9182 | Double resolution |
| 20 | 2.0 | 10⁻¹⁶ | 0.9188 | Double PML thickness |

The point-source value of 0.25 follows grid symmetry and is exact regardless of resolution. The line-source directionality of 0.919 changes by less than 0.1% with these resolution and PML-thickness checks.

</details>

<details markdown="1">
<summary>When results differ · Find common mistakes</summary>

| Symptom | Cause | Fix |
|------|------|----------|
| Animation is full of patterns from the beginning | `until` below t0 stops before appreciable excitation, followed by normalization | Start recording at t0 − 2·width |
| Concentric circles look elliptical | `imshow(aspect="auto")` | Use `aspect="equal"` |
| Amplitude does not appear to decrease with distance | Separate normalization of each panel | Use the same vmin/vmax for all panels |
| Time jumps after the second snapshot | Absolute time passed to `until` | Pass the difference from the preceding time |
| Four-side sum is near zero | Missing `weight=-1` on −x and −y | Set weights for outward normals |
| Long runs fill the image with standing waves | No PML | Use `mp.PML(1.0)` (Chapter 02) |

</details>

<h2 id="check">6. Check · Explain it in two answers</h2>

1. If fwidth is halved, what happens to the pulse width and peak time t0? Can you directly compare two images taken at the same time?
2. Why does a vertical line send more power left and right? Why does about 8% remain in the up/down directions?

<details markdown="1">
<summary>Compare with your explanation</summary>

**1.** Both double, because width = 1/fwidth and t0 = 5/fwidth. The pulse is at a different stage even at the same absolute time. Compare using t − t0, and check for contamination from the leading edge and wall reflections.

**2.** The in-phase points along the line reinforce one another in the left/right directions. Diffraction at the two ends of the finite line leaves some power in the up/down directions.

</details>

You can now read source shape and capture time together. Next, change **the boundaries of the box** and see how reflections change: [02 · Boundary conditions and PML]({{ site.baseurl }}/en/boundary-pml/).

<h2 id="reference">7. Reference · Complete code and reproduction record</h2>

<details>
<summary>point_line_source.py (expand to read)</summary>
{% highlight python %}
"""Meep Example 01 - Point source and line source.

Three small experiments in an empty 2D cell:
  A. a point Ez source, no PML: snapshots after the pulse peak t0, before the first wall reflection,
     with the predicted wavefront radius c*(t - t0) drawn on top;
  B. point source vs a finite line source at the same instant;
  C. with PML: a flux box around each source measures how the power is split between the four
     sides (point: 25 % each; line: mostly +-x), and the four sides add up to the emitted power.

Run:  python point_line_source.py          (~40 s on one core)
Out:  00_source.png, 01_layout.png, 02_snapshots.png, 03_point_vs_line.png, 04_flux_box.png,
      05_anim_point.gif, 05_anim_line.gif, result.json   (-> ../assets/01/)
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
from blogfig import Label, animate_fields, annotated_layout, bar_figure, panel_grid, record_frames, source_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "01")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# 1 length unit = 1 um, c = 1: a wave travels 1 um per time unit, so time is in um/c.
wl = 1.55                     # wavelength [um]
fcen = 1 / wl                 # center frequency [1/um]
fwidth = 0.5 * fcen           # wide band -> short pulse (~2 periods): clean concentric rings
CUTOFF = 5.0                  # Meep default: GaussianSource peaks at t0 = CUTOFF / fwidth
t0 = CUTOFF / fwidth          # pulse peak time
RESOLUTION = 20               # pixels per um (31 px per wavelength)

# experiment A/B: no PML, source off-center so the nearest wall is 4 um away
sx_a, sy_a = 12.0, 8.0
src_a = mp.Vector3(-2.0, 0.0)
line_len = 3.0                # finite line source length [um] (about 2 wavelengths)
d_wall = min(sx_a / 2 - abs(src_a.x), sy_a / 2 - abs(src_a.y))   # 4 um: reflections return after t0 + 2*d_wall

# experiment C: with PML, source at the center, flux box of half-size `half` around it
sx_c = sy_c = 10.0
DPML = 1.0
half = 2.5


# ---------------------------------------------------------------- (2) materials & geometry
# nothing: an empty cell is vacuum (default_material = air). geometry = [] is the point of this post.

# ---------------------------------------------------------------- (3) source
def make_source(center, size=mp.Vector3(0, 0, 0)):
    """size (0,0,0) = point source; size (0, L, 0) = line source of length L along y."""
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center, size=size)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(cell, sources, dpml=0.0, resolution=RESOLUTION):
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=[mp.PML(dpml)] if dpml > 0 else [], sources=sources)


t_all = time.time()
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ A. snapshots before any reflection
offsets = [0.0, 0.8, 1.6, 2.4, 3.2, 3.6]          # time after the pulse peak; last one < d_wall
sim = make_sim((sx_a, sy_a), make_source(src_a))
fields, titles, prev = [], [], 0.0
for off in offsets:
    target = t0 + off
    sim.run(until=target - prev)                   # `until` counts from NOW, so pass the difference
    prev = target
    fields.append(sim.get_array(center=mp.Vector3(), size=mp.Vector3(sx_a, sy_a), component=mp.Ez))
    titles.append(f"t = {target:.1f}  (t0 + {off:.1f})")
extent_a = [-sx_a / 2, sx_a / 2, -sy_a / 2, sy_a / 2]
r_front = offsets[-1]                              # c = 1: the peak has travelled this far
panel_grid(fields, titles, extent_a, os.path.join(OUT, "02_snapshots.png"), marks=[(src_a.x, src_a.y)],
           circles={len(fields) - 1: (src_a.x, src_a.y, r_front, f"predicted r = {r_front:.1f} um")},
           suptitle="point source, no PML: wavefront after the pulse peak (one color scale)")

# does the field really sit on the predicted circle?  mean |Ez| on the ring vs. over the cell
ez_last = fields[-1]
gx, gy = np.meshgrid(np.linspace(-sx_a / 2, sx_a / 2, ez_last.shape[0]) - src_a.x,
                     np.linspace(-sy_a / 2, sy_a / 2, ez_last.shape[1]) - src_a.y, indexing="ij")
rr = np.hypot(gx, gy)
ring = np.abs(ez_last)[(rr > r_front - 0.4) & (rr < r_front + 0.4)].mean()
everywhere = np.abs(ez_last).mean()
print(f"A. t0 = {t0:.2f}; at t0 + {r_front}: mean |Ez| on the predicted ring = {ring:.4f}, cell mean = {everywhere:.4f} (ratio {ring/everywhere:.2f})")

# ================================================================ B. point vs line at the same instant
t_snap = t0 + 3.6
sim_line = make_sim((sx_a, sy_a), make_source(src_a, mp.Vector3(0, line_len, 0)))
sim_line.run(until=t_snap)
ez_line = sim_line.get_array(center=mp.Vector3(), size=mp.Vector3(sx_a, sy_a), component=mp.Ez)
panel_grid([ez_last, ez_line], ["point source", f"line source, length {line_len:g} um"], extent_a,
           os.path.join(OUT, "03_point_vs_line.png"), ncols=2, marks=[(src_a.x, src_a.y)],
           lines={1: ((src_a.x, src_a.y - line_len / 2), (src_a.x, src_a.y + line_len / 2))},
           suptitle=f"same instant t = t0 + 3.6, no PML")


# ================================================================ B'. animations: point and line source, no PML, until the first reflection
sq = 12.0                                           # square cell, source at the center: symmetric spreading
width = 1.0 / fwidth
for kind, size in (("point", mp.Vector3(0, 0, 0)), ("line", mp.Vector3(0, line_len, 0))):
    sim_anim = make_sim((sq, sq), make_source(mp.Vector3(0, 0), size))
    frames, times = record_frames(sim_anim, mp.Volume(center=mp.Vector3(), size=mp.Vector3(sq, sq)), mp.Ez,
                                  t_start=t0 - 2 * width, t_end=t0 + 0.9 * sq / 2, n_frames=45)
    marker = ([((0, -line_len / 2), (0, line_len / 2), "k", "line source")] if kind == "line" else None)
    animate_fields(frames, times, [-sq / 2, sq / 2, -sq / 2, sq / 2], os.path.join(OUT, f"05_anim_{kind}.gif"),
                   lines=marker, points=([(0, 0, "k", "point source")] if kind == "point" else None),
                   figsize=(5.2, 4.6), title=f"{kind} source, no PML")

# ================================================================ C. flux box: where does the power go?
def flux_split(size, resolution=RESOLUTION, dpml=DPML, layout=False):
    """Power through the four sides of a box around the source, as fractions of the total."""
    sim = make_sim((sx_c, sy_c), make_source(mp.Vector3(0, 0), size), dpml=dpml, resolution=resolution)
    # ------------------------------------------------------------ (5) monitors: four flux planes, outward normals
    sides = {
        "+x": mp.FluxRegion(center=mp.Vector3(+half, 0), size=mp.Vector3(0, 2 * half)),
        "-x": mp.FluxRegion(center=mp.Vector3(-half, 0), size=mp.Vector3(0, 2 * half), weight=-1),
        "+y": mp.FluxRegion(center=mp.Vector3(0, +half), size=mp.Vector3(2 * half, 0)),
        "-y": mp.FluxRegion(center=mp.Vector3(0, -half), size=mp.Vector3(2 * half, 0), weight=-1),
    }
    mons = {k: sim.add_flux(fcen, 0, 1, reg) for k, reg in sides.items()}
    decay_pt = (half + 0.8, 0)
    if layout:
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=dpml, figsize=(6.8, 6.4),
            title="experiment C: point source in vacuum, PML, four flux planes around it",
            params_text=f"wl={wl} um  fwidth={fwidth:.3f}\nres={resolution}/um  cell={sx_c:g}x{sy_c:g}  dpml={dpml:g}",
            params_xy=(-3.8, 3.75), decay_point=decay_pt, decay_text_xy=(2.0, -0.6),
            labels=[
                Label("geometry = []  (vacuum)", (-2.0, 2.0), (-3.5, 2.6), step=2, color="black"),
                Label("point source (Ez)", (0, 0), (-3.5, -1.6), step=3, color="red"),
                Label("flux planes, normals outward", (half, 1.0), (0.3, 1.9), step=5, color="blue"),
            ])
    # ------------------------------------------------------------ (6) run until the pulse has left
    sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
    # ------------------------------------------------------------ (7) post-processing
    p = {k: float(mp.get_fluxes(m)[0]) for k, m in mons.items()}
    total = sum(p.values())
    return {k: v / total for k, v in p.items()}, total


t_c = time.time()
frac_point, P_point = flux_split(mp.Vector3(0, 0, 0), layout=True)
frac_line, P_line = flux_split(mp.Vector3(0, line_len, 0))
print(f"C. point source: " + "  ".join(f"{k}={v:.4f}" for k, v in frac_point.items()) + f"  (total {P_point:.4g})")
print(f"C. line source : " + "  ".join(f"{k}={v:.4f}" for k, v in frac_line.items()) + f"  (total {P_line:.4g}, x-sides {frac_line['+x']+frac_line['-x']:.3f})")
bar_figure(list(frac_point), {"point source": list(frac_point.values()), f"line source ({line_len:g} um)": list(frac_line.values())},
           os.path.join(OUT, "04_flux_box.png"), ylabel="fraction of emitted power", reference=0.25, reference_label="isotropic: 0.25")

# convergence of the point-source split (should be 0.25 each by symmetry)
convergence = [{"resolution": RESOLUTION, "dpml": DPML, "max_dev_from_0.25": max(abs(v - 0.25) for v in frac_point.values()),
                "x_sides_line": frac_line["+x"] + frac_line["-x"]}]
for res, dpml in ((40, 1.0), (20, 2.0)):
    fp, _ = flux_split(mp.Vector3(0, 0, 0), resolution=res, dpml=dpml)
    fl, _ = flux_split(mp.Vector3(0, line_len, 0), resolution=res, dpml=dpml)
    convergence.append({"resolution": res, "dpml": dpml, "max_dev_from_0.25": max(abs(v - 0.25) for v in fp.values()),
                        "x_sides_line": fl["+x"] + fl["-x"]})
    print(f"convergence res={res} dpml={dpml}: point max|frac-0.25|={convergence[-1]['max_dev_from_0.25']:.2e}, line x-sides={convergence[-1]['x_sides_line']:.4f}")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"t0": t0, "fwidth": fwidth, "d_wall": d_wall, "r_front": r_front,
                   "ring_mean_abs_ez": ring, "cell_mean_abs_ez": everywhere,
                   "point_fractions": frac_point, "line_fractions": frac_line, "line_len": line_len,
                   "P_point": P_point, "P_line": P_line, "convergence": convergence,
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
{% endhighlight %}
</details>

Unlike the walkthrough excerpts above, the complete code includes figure saving, GIF recording, and result.json output. The plotting helper `blogfig.py` (`panel_grid`, `bar_figure`, `record_frames`, `animate_fields`, etc.) is shared across the series and lives in the same folder (`code/`). Complete code and helper: [GitHub code folder](https://github.com/jin-castle/meep-examples/blob/main/code).

<details markdown="1">
<summary>Recorded output and reproduction environment</summary>

**Recorded output (run on 2026-10-23)**:
```
A. t0 = 15.50; at t0 + 3.6: mean |Ez| on the predicted ring = 0.1618, cell mean = 0.1282 (ratio 1.26)
C. point source: +x=0.2500  -x=0.2500  +y=0.2500  -y=0.2500  (total 2.44)
C. line source : +x=0.4594  -x=0.4594  +y=0.0406  -y=0.0406  (total 3.594, x-sides 0.919)
convergence res=40 dpml=1.0: point max|frac-0.25|=1.11e-16, line x-sides=0.9182
convergence res=20 dpml=2.0: point max|frac-0.25|=1.94e-16, line x-sides=0.9188
```

**Reproduction environment**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · run `python point_line_source.py` (approximately 21 s, single core)

</details>

### Further reading

- [Official Basics tutorial: Fields in a Waveguide](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#fields-in-a-waveguide) (the first example starts with a point source)
- [Official antenna radiation-pattern example](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-an-antenna) (point-source isotropy and near2far)
- [`Source` / `GaussianSource` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#source) · [`FluxRegion` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#fluxregion)
- Next: [02 · Boundary conditions and PML]({{ site.baseurl }}/en/boundary-pml/)
