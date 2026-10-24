---
layout: lesson
permalink: /en/boundary-pml/
lesson_title: "What if light returns from the walls of the computation box?"
lesson_summary: "Send the same pulse toward a reflecting boundary and PML, then isolate the returning field to measure the absorbing layer’s effect."
lesson_goals:
  - "Explain how reflecting boundaries, PML, and Absorber affect waves."
  - "Subtract a large reference cell to isolate the field returned by the boundary."
  - "Read the limits of the numerical result by checking PML thickness and measurement region together."
lesson_prerequisites: "Start with the point source, pulse peak time t0, and RMS from Chapter 01."
date: 2026-10-21
title: "Meep Example 02 · Boundary conditions and PML — measuring reflecting boundaries, PML, and Absorber on the same basis"
title_en: "Meep Example 02 · Boundary conditions and PML — reflecting walls, PML and Absorber on one ruler"
lang: en
translation_key: boundary-pml
series: meep-examples
part: 2
level: beginner
runtime: "10 s (single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Perfectly_Matched_Layer/"
tags: [meep, fdtd, pml, absorber, boundary]
image: /assets/meep/02/02_fieldmaps.png
excerpt: "the same point source in the same empty cell, three boundary treatments: Meep's default (a perfect reflector), `mp.PML`, and `mp.Absorber`. A padded reference run isolates what the boundary sends back."
---
<details markdown="1">
<summary>English summary</summary>

- **What**: the same point source in the same empty cell, three boundary treatments: Meep's default (a perfect reflector), `mp.PML`, and `mp.Absorber`. A padded reference run isolates what the boundary sends back.
- **Result**: no layer reflects 100 % of the pulse; a 1 µm Absorber 1.9 %; a 1 µm PML 0.045 %. PML reflection drops steeply up to 0.5 µm and then floors near 4 × 10⁻⁴.
- **Takeaway**: the cell edge is a mirror unless you say otherwise. PML is not a material you add; it is a coordinate stretch that makes the edge look infinitely far away. Measure it by subtracting a run whose walls are too far to matter.
- **Code**: full script at the bottom, ~10 s on one core.

</details>

<h2 id="observe">1. Observe · Find the returning wave</h2>

These snapshots show pulses from the same point source at the same time. There is no absorbing layer on the left; the right has 1 µm of PML. Look for **patterns returning toward the center**.

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/02/02_fieldmaps.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/02/02_fieldmaps.png' | relative_url }}" alt="Experiment A at t = 26.6. Reflected waves remain on the left; on the right they leave through PML. Both panels use the same color range." loading="lazy">
  </a>
  <figcaption>Experiment A at t = 26.6. Reflected waves remain on the left; on the right they leave through PML. Both panels use the same color range.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/02/05_anim_compare.gif' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/02/05_anim_compare.gif' | relative_url }}" alt="Time evolution with the same source and times. On the left the pulse returns from the wall; on the right it decays as it passes through PML." data-animation-src="{{ '/assets/meep/02/05_anim_compare.gif' | relative_url }}" data-static-src="{{ '/assets/meep/02/02_fieldmaps.png' | relative_url }}">
  </a>
  <button class="animation-toggle" type="button" hidden>Pause animation</button>
  <figcaption>Time evolution with the same source and times. On the left the pulse returns from the wall; on the right it decays as it passes through PML.</figcaption>
</figure>

<h2 id="predict">2. Predict · Before reading the results</h2>

If the PML thickness increases from 1 µm to 2 µm, what happens to the reflection metric measured in this experiment?

<fieldset class="prediction">
  <legend>Choose an answer and think through your reasoning.</legend>
  <label><input type="radio" name="lesson-02-prediction" value="1"> Doubling the thickness must reduce the metric by at least half.</label>
  <label><input type="radio" name="lesson-02-prediction" value="2"> It may decrease, but can remain almost unchanged if other errors dominate.</label>
</fieldset>

<details markdown="1">
<summary>Check the reasoning behind your prediction</summary>

The second answer is correct. Even if reflection from the outer end of the absorbing layer decreases, reference-subtraction residuals or near-field effects may remain. The actual thickness sweep hardly changed beyond 1 µm. Thickness alone cannot guarantee accuracy.

</details>

<h2 id="understand">3. Understand the principles</h2>

{% include chapter-illustration.html %}

<!-- concept-illustration:part-02:start -->
<p class="lesson-note">Without an absorbing layer, the boundary in this code returns the wave. In the same 12 × 8 µm vacuum cell, 1 µm PML inside all four edges attenuates the wave as it passes through. Both panels compare the same Ez point-source position and observation time. PML is a computational absorbing region, not a physical wall or sensor. Distinguish the field-RMS reflection metric in the separate experiment B from power reflectance.</p>
<!-- concept-illustration:part-02:end -->

### Provide a region where waves decay

The boundary without an absorbing layer in this example is a reflecting boundary with zero electric field. PML is **a computational region that imitates open space**, rather than a wall attached to a real device. It attenuates waves by stretching coordinates into the complex plane. Absorber instead gradually increases conductivity.

### A remaining field is not necessarily a returning field

RMS near the boundary includes the pulse that is still traveling outward. Experiment B therefore runs a second, larger cell with more distant boundaries. Subtracting its field from the smaller-cell field over the same region at the same time leaves the difference caused by the boundary.

$$R = \frac{\operatorname{rms}(E_{\mathrm{test}}-E_{\mathrm{ref}})}{\max_t\operatorname{rms}(E_{\mathrm{ref}})}$$

The denominator is the **maximum RMS over time** as the pulse crosses the region. Dividing by the small value after the pulse leaves would inflate the reflection ratio.

<aside class="lesson-note" markdown="1">
R in this lesson is **a ratio of field RMS values**, not power reflectance. It compares one time in a 2D vacuum Ez point-source simulation. No reflection may return into the reference region before that observation time.
</aside>

<details markdown="1">
<summary>Read more about equations, symbols, and the original predictions</summary>

The default boundary in this Meep setup is a wall with zero electric field (a perfect conductor). The wave returns completely with reversed sign. PML (perfectly matched layer) is a coordinate transformation rather than an ordinary absorbing material. Complex coordinate stretching makes the wave decay exponentially inside the layer without reflection at entry in the ideal theory. The ideal reflection is zero independent of incidence angle; practical reflection arises from grid discretization and finite thickness. `mp.Absorber` instead uses an ordinary absorbing material with gradually increased conductivity. It lacks the zero-reflection matching condition and returns more light than PML at the same thickness.

A reference is needed to isolate reflection from the boundary. Run a larger cell with boundaries moved outward by PAD to the same time: no reflected wave has yet returned into the inner comparison region. The difference between small and large cells then measures boundary reflection.

$$
R=\frac{\mathrm{rms}\big(E_{\mathrm{test}}-E_{\mathrm{ref}}\big)\big\|_{t_B}}{\max_t \mathrm{rms}\big(E_{\mathrm{ref}}\big)},\qquad
t_B = t_0 + 1.5\,\frac{L}{2}\sqrt2
$$

| Symbol | Meaning | Code variable |
|------|----|-----------|
| $E_{\mathrm{test}}$ | Field in the comparison region of the L × L interior with a boundary layer | `test = crop(...)` |
| $E_{\mathrm{ref}}$ | Field in the same region with boundaries moved outward by PAD = 6 µm | `ref` from `reference()` |
| $\max_t \mathrm{rms}(E_{\mathrm{ref}})$ | Maximum RMS while the pulse crosses the comparison region (denominator) | `peak` |
| $t_B$ | Time after the peak has traveled to the cell corner and back | `t_B` |
| edge RMS | RMS of \|Ez\| in a strip 1 µm inside the boundary (simple metric) | `edge_rms(field)` |

**Assumptions and validity**: 2D vacuum, an Ez point source, and snapshots compared at one time. The denominator is the reference maximum over time, not its field at the comparison time: by then the pulse has left the region and that value is small.

#### Make predictions before viewing the results

| Quantity | Prediction | Reason |
|--------|---------|------|
| R without a boundary layer | Close to 1 | Complete reflection |
| R with 1 µm PML | Below 10⁻³ | The usual expectation that 2/3 of a wavelength (1.55 µm) is sufficient |
| 1 µm Absorber versus 1 µm PML | Absorber more than 10 times worse | No impedance matching |
| Increasing PML thickness | Decreases until it reaches a floor | Thickness-related reflection falls exponentially; discretization reflection remains |
| Doubling resolution | PML R decreases | Reduced discretization reflection |

**Checks**: if R without a boundary layer differs greatly from 1, insufficient PAD may have contaminated the reference run with reflection. If PML R rises and falls with thickness, check whether the comparison region overlaps PML.

</details>

<h2 id="run">4. Run · Change one condition</h2>

Run the original code first and record the baseline. The environment is **Meep 1.33.0 · Python 3.11**, with a recorded single-core runtime of about 10 seconds. Place `boundary_pml.py` and `blogfig.py` from the [complete code and shared helper](https://github.com/jin-castle/meep-examples/blob/main/code) in the same folder. The [complete code below](#reference) is also ready to use.

```bash
OMP_NUM_THREADS=1 python boundary_pml.py
```

In the complete code, change only `L = 8.0` to `L = 12.0` and rerun. Keep `PAD = 6.0` and all other settings unchanged. The code recalculates the comparison region `HALF`, observation time `t_B`, and cell size from L. Compare **`B. PML 1 um`** with the baseline **4.508e-04**. This tests whether the residual decreases as source-to-PML distance increases. Record the measured result instead of assuming that it must decrease.

### What to check in the layout

Experiment B makes the full cell `L + 2*d` to keep the interior fixed at L × L. Since `mp.PML(d)` occupies space inside the cell, increasing thickness without enlarging the cell can put the comparison region inside the absorber.

<details markdown="1">
<summary>Layout, parameters, and source waveform</summary>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/02/01_layout.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/02/01_layout.png' | relative_url }}" alt="Experiment A layout with 1 µm PML. Red dot: Ez point source at (−2.5, 0); green hatching: PML. The no-layer case uses the same cell without PML. There is no monitor: the fields themselves are compared, and step ⑥ stops at a fixed time, so no decay-monitoring point is needed. Circled numbers match the code-walkthrough steps." loading="lazy">
  </a>
  <figcaption>Experiment A layout with 1 µm PML. Red dot: Ez point source at (−2.5, 0); green hatching: PML. The no-layer case uses the same cell without PML. There is no monitor: the fields themselves are compared, and step ⑥ stops at a fixed time, so no decay-monitoring point is needed. Circled numbers match the code-walkthrough steps.</figcaption>
</figure>

| Parameter | Value | Reason | Effect of changing it |
|----------|-----|-------------|--------|
| `fwidth` | 0.4 (width 2.5, t0 = 12.5) | A short pulse makes one wavefront easy to track and permits an early comparison | Narrower bandwidth delays t0 and comparison time |
| `RESOLUTION` | 12 px/µm | 18 px per wavelength; lecture value; 7 cases in 10 s | At 24, test the change in PML R (see detailed results) |
| Experiment A cell, source | 12 × 8 µm, (−2.5, 0) | Farthest corner is 9.4 µm away | A source close to PML can have its near field absorbed, distorting the result |
| `t_compare` | t0 + 1.5 × 9.4 = 26.6 | After the peak reaches every corner and starts returning | Earlier comparisons may precede the reflection |
| Experiment B interior L, PAD | 8 µm, 6 µm | Reference cell is 20 µm; reflection cannot reach the comparison region by t_B = 21 | Smaller PAD contaminates the reference and underestimates R |
| Comparison region `HALF` | 3 µm (1 µm inside the layer) | The layer is added outside the interior, preventing overlap | Overlap can make thicker PML appear to increase R |
| `Courant` | 0.5 | Meep default, fixed to the lecture value | — |

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/02/00_source.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/02/00_source.png' | relative_url }}" alt="Source waveform and spectrum: width 2.5, peak t0 = 12.5. The short pulse also keeps the leading-edge-to-peak separation short, at 5 µm." loading="lazy">
  </a>
  <figcaption>Source waveform and spectrum: width 2.5, peak t0 = 12.5. The short pulse also keeps the leading-edge-to-peak separation short, at 5 µm.</figcaption>
</figure>

**Difference from the lecture notebook**: week 3 compares thickness using edge RMS, extends the first-week numpy FDTD to 2D, and implements a first-order Mur absorbing boundary for comparison with PML (Mur 1.8 × 10⁻², PML 6.6 × 10⁻⁵). This lesson stays within Meep, replacing Mur with `mp.Absorber` and using reference subtraction for the thickness sweep. The initial run incorrectly made thicker PML look worse because the comparison region overlapped PML. Adding the layer outside a fixed interior corrected that mistake.

</details>

<details markdown="1">
<summary>Code walkthrough · The roles of seven steps</summary>

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → running and stopping → post-processing.
> Experiments A (field maps) and B (reference subtraction) differ in steps ④ and ⑦. Step ⑤ has no monitor.

#### ① Units and parameters — which numbers are fixed?

```python
wl = 1.55                     # wavelength [um]; 1 unit = 1 um, c = 1
fcen = 1 / wl
fwidth = 0.4                  # short pulse (width 2.5): a single wavefront is easy to follow
t0 = 5.0 / fwidth             # pulse peak (Meep cutoff = 5)
RESOLUTION = 12               # pixels per um (18 px per wavelength)

sx, sy = 12.0, 8.0            # experiment A cell
src = mp.Vector3(-2.5, 0.0)
corner = max(np.hypot(sx / 2 * ax - src.x, sy / 2 * ay - src.y) for ax in (-1, 1) for ay in (-1, 1))
t_compare = t0 + 1.5 * corner # the wavefront has reached every corner and (if reflected) come back

L, PAD, HALF = 8.0, 6.0, 3.0  # experiment B: interior, reference padding, compared half-size
t_B = t0 + 1.5 * (L / 2 * np.sqrt(2))
```

- **What**: derive wavelength, pulse, cell dimensions, and the two comparison times from the source and distances.
- **Why**: both cases must be compared at the same time for the metric to mean anything. The time must be late enough for the peak to reach the farthest corner and return. With c = 1, distance directly sets travel time.
- **If wrong**: an early comparison makes even the no-layer case look clean because reflection has not yet returned. PAD smaller than L/2 can contaminate the reference.

#### ② Materials and geometry — what is placed where?

```python
geometry = []                 # vacuum. Only the boundary layer changes between runs
```

- **What**: no structure.
- **Why**: to compare boundaries, nothing else should change.
- **If wrong**: adding a structure mixes structural reflections with boundary reflections.

#### ③ Source — how is light injected?

```python
def point_source(center):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center)]
```

- **What**: the same Ez point source as in Chapter 01.
- **Why**: a point source spreads in every direction and tests all incidence angles together. This is why simple first-order absorbing boundaries such as Mur become inadequate in 2D.
- **If wrong**: a plane-wave source tests only normal incidence and misses reflections at oblique angles.

#### ④ Simulation and boundaries — the computation box and PML

```python
def make_sim(cell, layers, center=mp.Vector3(), resolution=RESOLUTION):
    """layers = [] (reflecting), [mp.PML(d)] or [mp.Absorber(d)]."""
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=layers, sources=point_source(center), Courant=0.5)

# experiment B: the layer is ADDED outside the fixed 8 x 8 interior
cell = L + 2 * d
```

- **What**: a `Simulation` changing only `boundary_layers`. An empty list gives a reflecting boundary; `mp.PML(d)` or `mp.Absorber(d)` adds a layer of thickness d inside the cell edge.
- **Why**: PML uses the outer d of the cell without enlarging it. Experiment B therefore expands the cell to L + 2d, keeping the non-PML interior at 8 µm. The comparison region must not overlap the layer.
- **If wrong**: increasing d at fixed cell size moves the comparison region into PML. Because the field deliberately decays there, the difference can misleadingly suggest that thicker PML causes more reflection. That happened in the initial run.

> **Pitfall**: `mp.PML(d)` occupies the inner d of the cell, rather than attaching outside it. Keep structures of interest, sources, and monitors away from the inner PML boundary.

#### ⑤ Monitor — what is measured?

There is no monitor here because the comparison uses the whole field at a particular time. Instead, the reference run records the maximum RMS over time in the comparison region with `mp.at_every(0.25, track)` for the denominator.

```python
def track(s):
    a = s.get_array(center=mp.Vector3(), size=mp.Vector3(2 * HALF, 2 * HALF), component=mp.Ez)
    peak[0] = max(peak[0], rms(a))
sim.run(mp.at_every(0.25, track), until=t_B)
```

- **What**: measure comparison-region RMS every 0.25 time units and retain its maximum.
- **Why**: expressing reflection relative to the incident peak requires the field magnitude as the pulse passes through. At the later comparison time the pulse has already left, so dividing by that small value inflates the ratio.
- **If wrong**: an `at_every` interval longer than the pulse width (2.5) can miss the peak.

#### ⑥ Running and stopping — when should the simulation end?

```python
sim.run(until=t_compare)      # experiment A: both cases stop at the SAME absolute time
sim.run(until=t_B)            # experiment B: likewise
```

- **What**: stop at a fixed time, unlike `stop_when_fields_decayed` used from Chapter 04 onward.
- **Why**: compare one scene just after the boundary reflection returns, rather than waiting for the field to vanish. Without an absorbing layer the field never fully leaves, so a decay criterion is unsuitable.
- **If wrong**: different capture times place the pulses at different positions and invalidate the comparison.

#### ⑦ Post-processing — converting fields into numbers

```python
def edge_rms(field):                                   # experiment A: 1 um band along the edges
    band = (np.abs(x)[:, None] > sx / 2 - 1.0) | (np.abs(y)[None, :] > sy / 2 - 1.0)
    return float(np.sqrt(np.mean(np.abs(field[band]) ** 2)))

def reflection(layers, d=0.0, resolution=RESOLUTION): # experiment B: test - reference
    ref, peak = reference(resolution)
    sim = make_sim((L + 2 * d, L + 2 * d), layers, resolution=resolution)
    sim.run(until=t_B)
    test = crop(sim.get_array(..., component=mp.Ez), L + 2 * d)
    return rms(test - ref) / peak
```

- **What**: summarize experiment A with RMS in the edge strip and experiment B with RMS(test − ref) divided by the peak incident RMS.
- **Why**: edge RMS is simple but cannot distinguish returning waves from waves still going outward. Reference subtraction cancels the common outgoing pulse and leaves reflection.
- **If wrong**: misaligned test and reference grids leave part of the pulse after subtraction, increasing R. Both cell half-lengths should be integer multiples of grid spacing.

</details>

<h2 id="interpret">5. Interpret · Read the numbers and their limits</h2>

Experiment A reduces edge RMS from **0.122 → 0.0015**. After removing the outgoing pulse by reference subtraction in experiment B, the values are **1.03** without a layer, **1.9 × 10⁻²** for 1 µm Absorber, and **4.5 × 10⁻⁴** for 1 µm PML. At the same thickness, PML is about **41 times** lower by this metric.

Increasing PML from 0.25 → 0.5 µm sharply reduces the metric from **1.5 × 10⁻² → 7.9 × 10⁻⁴**. Increasing it from 1 → 2 µm barely changes it: **4.5 × 10⁻⁴ → 4.2 × 10⁻⁴**.

<aside class="lesson-note" markdown="1">
**The cause of the 4 × 10⁻⁴ floor is not established.** Raising resolution from 12 → 24 changes R for 1 µm PML from 4.5 → 5.1 × 10⁻⁴. Near-field effects and reference-grid alignment residuals have not been separated. Neither this floor nor a suitable thickness can be generalized to other materials, wavelengths, or 3D. Waveguides extending through PML also require separate validation.
</aside>

<details markdown="1">
<summary>Full results, prediction comparison, and convergence tables</summary>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/02/03_reflection.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/02/03_reflection.png' | relative_url }}" alt="Experiment B: returning-field RMS divided by peak incident RMS (log axis). No layer: 1.0; 1 µm Absorber: 1.9 × 10⁻²; 1 µm PML: 4.5 × 10⁻⁴." loading="lazy">
  </a>
  <figcaption>Experiment B: returning-field RMS divided by peak incident RMS (log axis). No layer: 1.0; 1 µm Absorber: 1.9 × 10⁻²; 1 µm PML: 4.5 × 10⁻⁴.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ '/assets/meep/02/04_pml_sweep.png' | relative_url }}" data-lightbox>
    <img src="{{ '/assets/meep/02/04_pml_sweep.png' | relative_url }}" alt="PML thickness sweep. From 0.25 → 0.5 µm the metric drops by a factor of 20; from 1 µm it plateaus near 4 × 10⁻⁴. The red dashed line is 1 µm Absorber." loading="lazy">
  </a>
  <figcaption>PML thickness sweep. From 0.25 → 0.5 µm the metric drops by a factor of 20; from 1 µm it plateaus near 4 × 10⁻⁴. The red dashed line is 1 µm Absorber.</figcaption>
</figure>

| Metric | No boundary layer | Absorber 1 µm | PML 1 µm |
|---|---|---|---|
| edge RMS (experiment A) | 0.122 | — | 0.0015 |
| R = reflected / peak incident field RMS (experiment B) | 1.03 | 1.9 × 10⁻² | 4.5 × 10⁻⁴ |

| PML thickness | 0.25 µm | 0.5 µm | 1 µm | 1.5 µm | 2 µm |
|---|---|---|---|---|---|
| R | 1.5 × 10⁻² | 7.9 × 10⁻⁴ | 4.5 × 10⁻⁴ | 4.3 × 10⁻⁴ | 4.2 × 10⁻⁴ |

#### Comparing predictions

| Quantity | Original prediction | Simulation | Verdict |
|--------|-------------|-----------|------|
| R without a boundary layer | ≈ 1 | 1.03 | ✅ |
| R for 1 µm PML | Below 10⁻³ | 4.5 × 10⁻⁴ | ✅ |
| Absorber versus PML (1 µm) | Absorber more than 10 times worse | 41 times | ✅ |
| Increasing thickness | Decrease, then a floor | Approaches a 4 × 10⁻⁴ floor beyond 0.5 µm | ✅ |
| Double resolution | Lower PML R | 4.5 → 5.1 × 10⁻⁴, almost unchanged | ❌ |

Higher resolution did not lower the PML floor. If discretization reflection alone caused it, it should decrease with resolution. Two other candidates remain: incomplete treatment of evanescent near-field components (the source is 3 µm, about 2 wavelengths, from the relevant region) and subtraction residuals from test/reference grids that are not exactly aligned. Moving the source farther from PML and measuring again would help distinguish them. See the limits below.

#### Convergence

| resolution | No boundary layer | PML 1 µm | Absorber 1 µm |
|---|---|---|---|
| 12 | 1.03 | 4.5 × 10⁻⁴ | 1.86 × 10⁻² |
| 24 | 1.04 | 5.1 × 10⁻⁴ | 1.85 × 10⁻² |

All three values are insensitive to these resolution changes. The ordering of the boundaries (1 : 0.02 : 0.0005) is already clear at resolution 12.

#### Supported claims and remaining limits

- Supported: the default boundary in this setup fully reflects. At equal thickness, PML returns about 40 times less field by this metric than Absorber. Here 0.5 µm PML (1/3 wavelength) brings R below 10⁻³, and thicknesses beyond 1 µm provide little further benefit.
- Not established: the origin of the 4 × 10⁻⁴ PML R floor. Its lack of resolution dependence rules out a simple discretization-only explanation; near fields or grid-alignment residuals may matter. Thickness criteria for other wavelengths, materials, or 3D are not established. Reflection when a structure crosses PML (the waveguide in Chapter 04) is outside this experiment.

</details>

<h2 id="check">6. Check · Explain it in your own words</h2>

### 1. Why does reference subtraction isolate boundary reflection better than edge RMS?

<details markdown="1">
<summary>Check the answer and reasoning</summary>

Edge RMS includes both outgoing and returning waves. Subtraction of a large reference cell cancels the outgoing pulse common to both calculations and exposes the difference created by the boundary.

</details>

### 2. If R increases with thicker PML, what should you check first?

<details markdown="1">
<summary>Check the answer and reasoning</summary>

Check for overlap between the comparison region and PML. The field deliberately decays inside the layer, and that difference can be mistaken for reflection. Increase the cell to L + 2d to preserve the interior region.

</details>

<h2 id="reference">7. Code and references</h2>

<details markdown="1">
<summary>Where this example is useful</summary>

The edges of the Chapter 01 snapshots contained small patterns returning from the walls. This lesson removes those effective walls. The calculation box is finite, while the physics assumes unbounded space. An absorbing layer at the edge imitates the condition that outgoing light never returns. With the same source and observation time, compare numerically what happens without a layer, how PML differs from Absorber, and how much thickness is sufficient.

#### Applications

PML is a way to imitate unbounded space. Whenever light escapes into open space, PML reflection can set a measurement-error floor.

| Application | What this lesson contributes | What comes next |
|---|---|---|
| Radiation loss of waveguide bends and tapers | Escaped light must not return if loss is to be measured as loss; PML reflection 4.5e-4 indicates the floor of this setup’s field metric | Bend in Chapter 05, taper in Chapter 29 |
| Far fields of antennas, scatterers, and metasurfaces | Open boundaries; returning light distorts the far field | near2far in Chapter 10 |
| Structures with metals or dispersive materials reaching the boundary (plasmonics, absorbers) | Absorber when PML is unstable | Dispersive materials in Chapter 20 |
| Periodic structures (gratings, metasurfaces) | PML in one direction and Bloch-periodic boundaries in the others | Gratings in Chapter 06 |

</details>

<details markdown="1">
<summary>Common mistakes and fixes</summary>

| Symptom | Cause | Fix |
|------|------|----------|
| Long runs fill the cell with standing waves | `boundary_layers=[]` | Use `mp.PML(...)` |
| Thicker PML increases apparent reflection | Comparison region or monitor enters PML | Enlarge the cell to keep the non-PML interior fixed |
| Field near the source looks wrong after adding PML | Source too close to PML | Keep at least half a wavelength from the inner PML boundary in this setup |
| Reference-subtraction R far below 1 despite no boundary layer | Comparison precedes the reflection, or PAD is insufficient | Use t_B after the corner round trip and PAD ≥ L/2 |
| Reflection ratio far above 1 | Dividing by the reference field at comparison time | Divide by maximum reference RMS over time |
| Waveguide reflects at PML | Structure ends before PML | Extend it through PML with `mp.inf` (Chapter 04) |

</details>

<details markdown="1">
<summary>Further exploration from the original lesson</summary>

| Change | Expected effect | Quantity to check |
|---------|----------|------------|
| Move the source farther from PML (L 8 → 12, keep PAD) | A near-field-driven floor should decrease | R for 1 µm PML |
| `Courant` 0.5 → 0.3 | Change time discretization; does the floor move? | PML R |
| `mp.Absorber` thickness 1 → 3 µm | More thickness may compensate; does it approach 1 µm PML? | R |
| `fwidth` 0.4 → 0.15 (long pulse, narrow band) | Reflection closer to a single wavelength; does the value change? | R |

</details>


<details>
<summary>boundary_pml.py (expand to read)</summary>
{% highlight python %}
"""Meep Example 02 - Boundary conditions and PML.

Same point source, same cell, different boundary treatment.
  A. field maps at one instant: no absorbing layer (Meep's default = perfect reflector) vs PML 1 um,
     summarised by the RMS of Ez in a 1 um band along the edges.
  B. a clean reflection metric: a padded reference run whose boundaries are so far away that nothing
     comes back in time; whatever differs inside the compared region is reflection from the boundary.
       R = rms(E_test - E_ref) / max_t rms(E_ref)
     Cases: no layer, PML 0.25..2 um, Absorber 1 um; convergence in resolution.
  C. GIF: reflecting boundary vs PML, side by side.

Run:  python boundary_pml.py           (~2 min on one core)
Out:  00_source.png, 01_layout.png, 02_fieldmaps.png, 03_reflection.png, 04_pml_sweep.png,
      05_anim_compare.gif, result.json   (-> ../assets/02/)
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
from blogfig import (Label, animate_compare, annotated_layout, bar_figure, line_figure,   # noqa: E402
                     panel_grid, record_frames, source_figure)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "02")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
wl = 1.55                     # wavelength [um]; 1 unit = 1 um, c = 1
fcen = 1 / wl
fwidth = 0.4                  # short pulse (width 2.5): a single wavefront is easy to follow
t0 = 5.0 / fwidth             # pulse peak (Meep cutoff = 5)
width = 1.0 / fwidth
RESOLUTION = 12               # pixels per um (18 px per wavelength); cheap, course value

# experiment A / C: rectangular cell, source off-center
sx, sy = 12.0, 8.0
src = mp.Vector3(-2.5, 0.0)
corner = max(np.hypot(sx / 2 * ax - src.x, sy / 2 * ay - src.y) for ax in (-1, 1) for ay in (-1, 1))
t_compare = t0 + 1.5 * corner # the wavefront has reached every corner and (if reflected) come back

# experiment B: the PML-free interior is always L x L; a layer of thickness d is ADDED outside it
# (cell = L + 2d), so the compared region |x|,|y| <= HALF never overlaps the layer.
# The reference domain is padded by PAD on each side: nothing reflected reaches the compared region by t_B.
L = 8.0
PAD = 6.0
HALF = L / 2 - 1.0            # compared region: |x|,|y| <= 3 um, 1 um inside the layer
t_B = t0 + 1.5 * (L / 2 * np.sqrt(2))

# ---------------------------------------------------------------- (2) materials & geometry
# none: vacuum. The only thing that changes between runs is the boundary layer.


# ---------------------------------------------------------------- (3) source
def point_source(center):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(cell, layers, center=mp.Vector3(), resolution=RESOLUTION):
    """layers = [] (reflecting), [mp.PML(d)] or [mp.Absorber(d)]."""
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=layers, sources=point_source(center), Courant=0.5)


t_all = time.time()
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ A. field maps at t_compare, edge-band RMS
def edge_rms(field):
    x = np.linspace(-sx / 2, sx / 2, field.shape[0], endpoint=False)
    y = np.linspace(-sy / 2, sy / 2, field.shape[1], endpoint=False)
    band = (np.abs(x)[:, None] > sx / 2 - 1.0) | (np.abs(y)[None, :] > sy / 2 - 1.0)
    return float(np.sqrt(np.mean(np.abs(field[band]) ** 2)))


maps, edges = {}, {}
for name, layers in (("no layer", []), ("PML 1 um", [mp.PML(1.0)])):
    sim = make_sim((sx, sy), layers, center=src)
    if name == "PML 1 um":
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=1.0, figsize=(7.4, 5.4),
            title="experiment A: point source, PML 1 um (the 'no layer' case is the same cell without PML)",
            params_text=f"wl={wl} um  fwidth={fwidth}\nres={RESOLUTION}/um  cell={sx:g}x{sy:g}  dpml=1.0",
            params_xy=(-4.6, 3.6), pml_xy=(1.5, -3.5),
            labels=[Label("geometry = []  (vacuum)", (1.0, 1.5), (0.0, 2.6), step=2, color="black"),
                    Label("point source (Ez)", (src.x, src.y), (-4.6, -1.6), step=3, color="red"),
                    Label("no monitor: the field itself is the result", (3.0, -0.3), (0.2, -1.8), step=5, color="blue")])
    sim.run(until=t_compare)                      # (6) the SAME absolute time for both cases
    maps[name] = sim.get_array(center=mp.Vector3(), size=mp.Vector3(sx, sy), component=mp.Ez)   # (7)
    edges[name] = edge_rms(maps[name])
extent_a = [-sx / 2, sx / 2, -sy / 2, sy / 2]
panel_grid([maps["no layer"], maps["PML 1 um"]],
           [f"no absorbing layer: edge RMS {edges['no layer']:.3f}", f"PML 1 um: edge RMS {edges['PML 1 um']:.4f}"],
           extent_a, os.path.join(OUT, "02_fieldmaps.png"), ncols=2, marks=[(src.x, src.y)],
           rects=[(-sx / 2, -sy / 2, sx, sy), (-sx / 2 + 1, -sy / 2 + 1, sx - 2, sy - 2)],
           suptitle=f"same source, same time t = {t_compare:.1f}: only the boundary differs")
print(f"A. t0 = {t0:.1f}, t_compare = {t_compare:.1f}; edge RMS no layer = {edges['no layer']:.4f}, PML 1 um = {edges['PML 1 um']:.4f} (ratio {edges['no layer']/edges['PML 1 um']:.1f})")


# ================================================================ B. padded reference: reflection = test - reference
def crop(field, size):
    """Central square |x|,|y| <= HALF of a field over a `size` x `size` cell."""
    n = field.shape[0]
    axis = (np.arange(n) + 0.5) / n * size - size / 2
    m = np.abs(axis) <= HALF
    return field[np.ix_(m, m)]


def rms(a):
    return float(np.sqrt(np.mean(np.abs(a) ** 2)))


_ref_cache = {}


def reference(resolution):
    """Big domain (L + 2 PAD): no reflection reaches the compared region before t_B. Also tracks the
    peak RMS inside that region over time, the denominator of the reflection metric."""
    if resolution in _ref_cache:
        return _ref_cache[resolution]
    big = L + 2 * PAD
    sim = make_sim((big, big), [], resolution=resolution)
    peak = [0.0]

    def track(s):
        a = s.get_array(center=mp.Vector3(), size=mp.Vector3(2 * HALF, 2 * HALF), component=mp.Ez)
        peak[0] = max(peak[0], rms(a))

    sim.run(mp.at_every(0.25, track), until=t_B)
    field = crop(sim.get_array(center=mp.Vector3(), size=mp.Vector3(big, big), component=mp.Ez), big)
    _ref_cache[resolution] = (field, peak[0])
    return _ref_cache[resolution]


def reflection(layers, d=0.0, resolution=RESOLUTION):
    """Reflection metric for a boundary layer of thickness d (0 = no layer, Meep's reflecting default)."""
    ref, peak = reference(resolution)
    cell = L + 2 * d
    sim = make_sim((cell, cell), layers, resolution=resolution)
    sim.run(until=t_B)
    test = crop(sim.get_array(center=mp.Vector3(), size=mp.Vector3(cell, cell), component=mp.Ez), cell)
    if test.shape != ref.shape:                   # grids of the two domains may differ by a pixel
        k = min(test.shape[0], ref.shape[0]); test, ref = test[:k, :k], ref[:k, :k]
    return rms(test - ref) / peak


cases = {"no layer": ([], 0.0), "Absorber 1 um": ([mp.Absorber(1.0)], 1.0)}
cases.update({f"PML {d:g} um": ([mp.PML(d)], d) for d in (0.25, 0.5, 1.0, 1.5, 2.0)})
R = {k: reflection(layers, d) for k, (layers, d) in cases.items()}
for k, v in R.items():
    print(f"B. {k:14s} reflection / peak incident = {v:.3e}")
bar_figure(["no layer", "Absorber 1 um", "PML 1 um"], {"reflected RMS / peak incident RMS": [R["no layer"], R["Absorber 1 um"], R["PML 1 um"]]},
           os.path.join(OUT, "03_reflection.png"), ylabel="reflected RMS / peak incident RMS", logy=True, fmt="{:.1e}")
thick = [0.25, 0.5, 1.0, 1.5, 2.0]
line_figure(thick, {"PML": [R[f"PML {t:g} um"] for t in thick]}, os.path.join(OUT, "04_pml_sweep.png"),
            xlabel="PML thickness [um]", ylabel="reflected RMS / peak incident RMS", logy=True,
            hline=R["Absorber 1 um"], hline_label="Absorber 1 um")

convergence = [{"resolution": RESOLUTION, "no layer": R["no layer"], "PML 1 um": R["PML 1 um"], "Absorber 1 um": R["Absorber 1 um"]}]
for res in (24,):
    row = {"resolution": res, "no layer": reflection([], 0.0, res), "PML 1 um": reflection([mp.PML(1.0)], 1.0, res),
           "Absorber 1 um": reflection([mp.Absorber(1.0)], 1.0, res)}
    convergence.append(row)
    print(f"convergence res={res}: " + "  ".join(f"{k}={v:.2e}" for k, v in row.items() if k != "resolution"))

# ================================================================ C. GIF: reflecting vs PML, side by side
vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx, sy))
sets, titles = [], []
for name, layers in (("no absorbing layer (reflecting)", []), ("PML 1 um", [mp.PML(1.0)])):
    s_anim = make_sim((sx, sy), layers, center=src)
    frames, times = record_frames(s_anim, vol, mp.Ez, t_start=t0 - 2 * width, t_end=t0 + 1.6 * corner, n_frames=60)
    sets.append(frames); titles.append(name)
animate_compare(sets, titles, times, extent_a, os.path.join(OUT, "05_anim_compare.gif"),
                points=[(src.x, src.y, "k", "source")], suptitle="same source and time")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"t0": t0, "t_compare": t_compare, "t_B": t_B, "edge_rms": edges, "reflection": R,
                   "convergence": convergence, "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
{% endhighlight %}
</details>

Unlike the walkthrough excerpts, the complete code includes figure saving, GIF recording, and result.json output. The plotting helper `blogfig.py` (`panel_grid`, `bar_figure`, `line_figure`, `animate_compare`, etc.) is shared across the series and lives in the same folder (`code/`). Complete code and helper: [GitHub code folder](https://github.com/jin-castle/meep-examples/blob/main/code).

**Recorded output (run on 2026-10-23)**:
```
A. t0 = 12.5, t_compare = 26.6; edge RMS no layer = 0.1216, PML 1 um = 0.0015 (ratio 79.0)
B. no layer       reflection / peak incident = 1.031e+00
B. Absorber 1 um  reflection / peak incident = 1.861e-02
B. PML 0.25 um    reflection / peak incident = 1.496e-02
B. PML 0.5 um     reflection / peak incident = 7.926e-04
B. PML 1 um       reflection / peak incident = 4.508e-04
B. PML 1.5 um     reflection / peak incident = 4.271e-04
B. PML 2 um       reflection / peak incident = 4.220e-04
convergence res=24: no layer=1.04e+00  PML 1 um=5.09e-04  Absorber 1 um=1.85e-02
```

**Reproduction environment**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · run `python boundary_pml.py` (approximately 10 s, single core)


### Further reading

- [Official documentation: Perfectly Matched Layer](https://meep.readthedocs.io/en/latest/Perfectly_Matched_Layer/) (PML principles, limitations, and when to use Absorber)
- [Official absorber-1d.py example](https://github.com/NanoComp/meep/blob/master/python/examples/absorber-1d.py) (switch PML and Absorber in the same cell)
- [`PML` / `Absorber` reference](https://meep.readthedocs.io/en/latest/Python_User_Interface/#pml)
- Previous: [01 · Point source and line source]({{ site.baseurl }}/en/point-line-source/) · Next: [03 · Reference subtraction]({{ site.baseurl }}/en/reference-subtraction/)
