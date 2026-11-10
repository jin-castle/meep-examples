---
layout: lesson
permalink: /en/zone-plate-near2far/
lesson_title: "How do we look at a focus 200 µm outside the cell?"
lesson_summary: "Focus a binary-phase zone plate with cylindrical near2far, compare the spot against scalar theory (1.22·Δr_N, N², 1/√N), and learn where far-field sampling silently breaks the energy balance."
lesson_goals:
  - "Write an x-polarized planewave in cylindrical coordinates as a single m = −1 source (Er and −iEφ)."
  - "Place near2far surfaces in a homogeneous medium and read fields on lines far outside the cell."
  - "Check a diffractive focus against scalar theory and against a far-field power balance, including the angular-sampling trap."
lesson_prerequisites: "Chapter 13: cylindrical coordinates and m · Chapter 10: near2far"
date: 2026-11-10
title: "Meep Example 16 · Collecting the extracted light — near-to-far field in cylindrical coordinates and a binary-phase zone plate"
title_en: "Meep Example 16 · Collecting the extracted light — near-to-far field in cylindrical coordinates and a binary-phase zone plate"
lang: en
translation_key: zone-plate-near2far
series: meep-examples
part: 16
level: intermediate
runtime: "N 25: 23 s FDTD + 1,500 far-field points (≈ 4 min on one core); N 100 ≈ 30 min"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/#focusing-properties-of-a-binary-phase-zone-plate"
tags: [meep, fdtd, near2far, zone-plate, cylindrical, diffractive-lens, focusing]
image: /assets/meep/16/02_results.png
excerpt: "a binary-phase glass zone plate (N = 25/50/100 zones, f = 200 µm, λ = 0.5 µm) on a glass substrate, illuminated from below by an x-polarized planewave written in cylindrical coordinates as m = −1 (Er − iEφ). The focal spot lies 200 µm outside the cell, so the fields there come from a near-to-far transformation (`add_near2far` + `get_farfields`) of the fields on the top and side faces of the cell."
---
<h2 id="observe">Observe: a focus far outside the cell</h2>

![hero]({{ '/assets/meep/16/02_results.png' | relative_url }})

- **What**: a binary-phase glass zone plate (N = 25/50/100 zones, f = 200 µm, λ = 0.5 µm) on a glass substrate, illuminated from below by an x-polarized planewave written in cylindrical coordinates as m = −1 (Er − iEφ). The focal spot lies 200 µm outside the cell, so the fields there come from a near-to-far transformation (`add_near2far` + `get_farfields`) of the fields on the top and side faces of the cell.
- **Result**: the three documented curves come out as drawn — focus at z = 199.8–199.9 µm for all N, peak |E|² 4683 / 17403 / 64881 (ratios 3.7 and 13.9 versus N² = 4 and 16), first zero of the focal spot 1.204 / 0.901 / 0.701 µm versus the scalar 1.22·Δr_N = 1.261 / 0.907 / 0.667 µm (within 5 %), FWHM ratio N 100 / N 25 = 0.54 (1/√N → 0.5). Resolution 25 is converged (peak 2 %, FWHM 0.1 % from 25 to 50). Transmitted/incident net flux 0.99–1.00, but the far power integrated over a hemisphere with 1° steps is only 70–76 % of the near flux.
- **Takeaway**: near2far gives the field anywhere outside the cell from one run, but each far point costs an integral over the near surface — sampling matters twice: the far scan step for the focal profile, and the angular step if you integrate the far power. Here a 1° angular step misses the λ/D ≈ 0.15–0.3° fringes of a 100–200 µm aperture and under-counts the power by 25–30 %.
- **Code**: full script at the bottom; N 25 takes ~4 min on one core (the far-field points, not the FDTD, dominate).

## 0. What you will learn

- How to write an x-polarized planewave as a single m = −1 source in cylindrical coordinates (Er and −iEφ), and why the planewave needs `is_integrated`.
- Where to put the `add_near2far` surfaces (in air, inside the PML) and how `get_farfields` returns the field on any line or plane outside the cell.
- The zone-plate design rule r_n² = nλ(f + nλ/4), the resolution 1.22·Δr_N, and the peak intensity ∝ N².
- An energy balance that integrates the far-field power and compares it with the near flux — and how it goes wrong when the angular sampling is too coarse.

**Prerequisites**: cylindrical coordinates and m from chapter 13, near2far from chapter 10. **Official example**: [Focusing properties of a binary-phase zone plate](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/#focusing-properties-of-a-binary-phase-zone-plate), script [zone_plate.py](https://github.com/NanoComp/meep/blob/master/python/examples/zone_plate.py). **Previous**: 15 · When there are thousands of point sources · **Next**: 17 · Launching an oblique planewave

## 1. What do we want to find out?

Up to chapter 14 the light left the structure and went outward. The simplest device that gathers that light at a distant point is a zone plate. Cut the radius every half-wavelength of path difference and flip the phase of the odd zones by π, and every zone adds constructively at the focus. Two questions follow. The cell is only 6.5 µm tall — can Meep show a focus 200 µm away (near2far)? And if the number of zones N is quadrupled, does the focal width halve?

### Where is this useful?

Zone plates are the objective lenses of X-ray and EUV microscopes (wavelengths with no refractive lenses), and at visible wavelengths they are the starting point for flat diffractive lenses and metalenses. The outermost zone width Δr_N sets the resolution, so "how finely can you pattern" is the performance.

| Application | What it takes from this chapter | What it needs next |
|---|---|---|
| X-ray zone-plate microscopes | spot size 1.22·Δr_N, peak ∝ N² | efficiency (distribution among diffraction orders) |
| Flat diffractive lenses and metalenses | near2far focal profile, PSF outside the cell | chapter 07 meta-atoms, the metalens topic page |
| LED and laser package optics | far-field distribution of the extracted light | chapter 14 extraction |

<h2 id="understand">2. Understand: the physics on one page</h2>

{% include chapter-illustration.html %}

Require that the distance from the edge of the n-th zone to the focus is f + nλ/2:

$$
r_n^2 = n\lambda\left(f + \frac{n\lambda}{4}\right),\qquad
\Delta r \approx 1.22\,\Delta r_N,\qquad I_{\mathrm{peak}} \propto N^2
$$

Δr_N = r_N − r_{N−1} is the outermost zone width and sets the resolution (the radius of the first zero). Glass (n 1.5) of height 0.5 µm adds an optical path of 0.25 µm = λ/2, so the odd zones carry a π phase. near2far integrates the equivalent surface currents (E, H) on the cell surface with the free-space Green's function to obtain the field outside. In cylindrical coordinates there is an extra φ integral, so each point costs more, and far points close to the near surface are the slowest (as the documentation says).

| Symbol | Meaning | Code variable |
|---|---|---|
| N | number of zones | `num_zones` |
| f | focal length 200 µm | `focal_length_um` |
| r_n | zone radii | `zone_radius_um` |
| Δr_N | outermost zone width | `outer_zone_width` |

**Assumptions and range of validity**: cylindrical coordinates with m = −1 (x-polarized planewave), lossless glass, vacuum outside the cell, far points in the φ = 0 (r–z) plane.

<h2 id="predict">Predict before viewing the results</h2>

| Quantity | My prediction | Reasoning |
|--------|---------|------|
| z of the peak | 200 ± 1 µm | design rule |
| peak ratio N 50/25, 100/25 | 4, 16 | ∝ N² |
| first zero r₀ | 1.26 / 0.91 / 0.67 µm | 1.22·Δr_N |
| hemisphere far power / near top flux | 1 ± 0.1 | power conservation |
| transmitted/incident net flux | 1 ± 0.03 | lossless |

**Decision rule**: if the z peak misses 200 µm by several µm or the peak ratio departs from N² by more than a factor of two, suspect the near-surface position or the sign of m.

## 3. Simulation layout

![layout]({{ '/assets/meep/16/01_layout_source.png' | relative_url }})
*(a) The r ≤ 20 µm region: glass substrate and zone plate (dark blue), green dashed near2far and transmitted-flux top face, red planewave source (inside the substrate), orange incident-flux face, ▲ the decay monitor point (mid-r, z 0). The cell radius is R_N + 3 µm. (b) Re Er(t) at mid-r, z 0. (c) Spectrum — fwidth 0.2 f.*

| Item | Value | Source | Note |
|---|---|---|---|
| resolution | 25 px/µm | official example | ladder 12.5/25/50 (N 25) |
| cell | r = R_N + 2 + 1, z = 1 + 2 + 0.5 + 2 + 1 | official example | PML 1 on all sides |
| zone plate | N 25/50/100, glass 1.5, height 0.5 | official example and docs | |
| source | Er + (−i)Eφ Gaussian f 2 fwidth 0.4 is_integrated | official example | inside the substrate |
| near2far | top face (z = size_z/2 − 1) + side face (air) | official example | |
| far scan | r 0…size_r − 1 at z f; z f ± 50 at r 0; step 0.1 µm | official example | |
| added | transmitted and incident flux, hemisphere (R = f, 91 points) integral, DFT Er map | this chapter | field-neutral |
| termination | decay(50, Er, (size_r/2, 0, 0), 1e-6) | official example | |

**Difference from the tutorial notebook**: the official notebook (2024-02) runs N 25 only and stores only the figures. This chapter adds three values of N, a resolution ladder and the balance monitors.

<h2 id="run">4. Run and follow the code</h2>

### ① Parameters — the zone radii

```python
zone_radius_um = np.array([math.sqrt(n*wavelength_um*(focal_length_um + n*wavelength_um/4)) for n in range(1, num_zones+1)])
size_r_um = zone_radius_um[-1] + padding_um + pml_um
```
What: build the N radii from the design rule and size the cell radius to the outermost zone. Why: a cell smaller than the zone plate clips the outer zones and blurs the focus. If wrong: using r_n instead of r_n² gives equally spaced zones and no focus.

### ② Geometry — stack discs from the largest down

```python
for n in range(num_zones-1, -1, -1):
    geometry.append(mp.Block(material=glass if n % 2 == 0 else mp.vacuum,
                             size=mp.Vector3(zone_radius_um[n], 0, height_um),
                             center=mp.Vector3(0.5*zone_radius_um[n], 0, z_lens)))
```
What: alternate glass and vacuum discs from the largest radius to the smallest, so the overlaps form the ring pattern. Why: later objects override earlier ones in Meep, so no explicit rings are needed. If wrong: reversing the order leaves only the largest disc.

### ③ Source — an x-polarized planewave as m = −1

```python
sources = [mp.Source(mp.GaussianSource(f, fwidth=0.2*f, is_integrated=True), component=mp.Er, center=..., size=mp.Vector3(size_r_um)),
           mp.Source(mp.GaussianSource(f, fwidth=0.2*f, is_integrated=True), component=mp.Ep, ..., amplitude=-1j)]
```
What: Er and −iEφ with equal amplitude form a single m = −1 circularly polarized planewave, whose results equal those of a linear x polarization (chapter 13). Why: in cylindrical coordinates a planewave is written in m = ±1 components. If wrong: Er alone mixes m = ±1 and changes the φ dependence. Without `is_integrated`, the source edge touching the PML produces spurious diffraction.

### ④ Simulation and boundaries

```python
sim = mp.Simulation(cell_size=cell_size, boundary_layers=[mp.PML(1.0)], resolution=25, sources=sources,
                    geometry=geometry, dimensions=mp.CYLINDRICAL, m=-1)
```
What: cylindrical coordinates, m = −1, PML on all sides. Why: the axis (r = 0) is not a boundary but is handled analytically, and the z faces open onto substrate and air. If wrong: with m = 0 an Er planewave is not defined.

### ⑤ Monitors — the near2far faces stay in air

```python
n2f = sim.add_near2far(f, 0, 1,
    mp.Near2FarRegion(center=mp.Vector3(0.5*(size_r-pml), 0, z_top), size=mp.Vector3(size_r-pml, 0, 0)),
    mp.Near2FarRegion(center=mp.Vector3(size_r-pml, 0, z_top-0.5*(height+padding)), size=mp.Vector3(0, 0, height+padding)))
```
What: a top face and a side face enclose the region above the zone plate. Why: near2far is exact only for surfaces inside a homogeneous medium (air here) — a surface crossing the substrate is not allowed. If wrong: lowering the face into the glass makes the far field wrong by a factor of several.

### ⑥ Run — until the fields have left

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(50.0, mp.Er, mp.Vector3(0.5*size_r, 0, 0), 1e-6))
```
What: run until Er at the monitor point has fallen to 1e-6 of its maximum. Why: near2far accumulates a DFT, so the whole pulse must pass. If wrong: stopping early leaves spurious fringes in the far field.

### ⑦ Postprocessing — the field 200 µm outside the cell

```python
ff_r = sim.get_farfields(n2f, 10, center=mp.Vector3(0.5*r_max, 0, z_f), size=mp.Vector3(r_max, 0, 0))
ff_z = sim.get_farfields(n2f, 10, center=mp.Vector3(0, 0, z_f), size=mp.Vector3(0, 0, 100))
I = |Ex|² + |Ey|² + |Ez|²
```
What: an r scan across the focal plane and a z scan along the axis, both with 0.1 µm steps. Why: the focal spot is about 1 µm wide, so 0.1 µm resolves the FWHM. If wrong: the number of points is the cost (0.1–0.9 s per point), and far points near the near surface are slower still.

<h2 id="interpret">5. Interpret the results</h2>

![results]({{ '/assets/meep/16/02_results.png' | relative_url }})
*(a) On-axis z scan (r 0), N 25/50/100. (b) Focal-plane r scan. ▽ marks the first zero read by eye from the official documentation figure. (c) Peak |E|² and first zero r₀ versus N — dotted N², red dotted 1.22·Δr_N.*

![forward]({{ '/assets/meep/16/03_forward_dft.png' | relative_url }})
*(a) |Er| DFT at λ 0.5 (log color, r ≤ 20): diffraction behind the zone plate. (b) N 25 z scan and FWHM_z. (c) Energy balance: transmitted/incident net flux, hemisphere far power / near top flux.*

| N | z peak (µm) | peak \|E\|² | peak ratio (to N 25) | first zero r₀ (µm) | 1.22·Δr_N (µm) | FWHM_r (µm) | transmitted/incident | hemisphere (91 pts)/near |
|---|---|---|---|---|---|---|---|---|
| 25 | 199.85 | 4683 | 1 | 1.204 | 1.261 | 1.052 | 0.996 | 0.758 |
| 50 | 199.85 | 17403 | 3.72 | 0.901 | 0.907 | 0.766 | 0.991 | 0.735 |
| 100 | 199.75 | 64881 | 13.9 | 0.701 | 0.667 | 0.564 | 0.990 | 0.697 |

Read by eye, the documentation figure gives peak ratios of 3.4 and 14 and first zeros of 1.3/0.9/0.65 µm. The r scan step is 0.1 µm, so r₀ is pinned to that grid.

![animation]({{ '/assets/meep/16/05_anim.gif' | relative_url }})
*N 25, res 25: Re Er(r, z, t) as the planewave pulse crosses the substrate and the zone plate (r ≤ 20 µm shown). Frames are (n + 1/8) optical periods apart. The strip below is Er at mid-r, z 0.*

### Compare with the predictions

| Quantity | My prediction (§2) | Simulation | Verdict |
|--------|-------------|-----------|------|
| z peak | 200 ± 1 | 199.75–199.85 | ✅ |
| peak ratio 50/25, 100/25 | 4, 16 | 3.72, 13.9 | ✅ (7–13 % below N²) |
| first zero r₀ | 1.26 / 0.91 / 0.67 | 1.204 / 0.901 / 0.701 (−4.5 / −0.7 / +5.1 %) | ✅ |
| hemisphere far / near flux | 1 ± 0.1 | 0.76 / 0.73 / 0.70 | ❌ |
| transmitted/incident net flux | 1 ± 0.03 | 0.996 / 0.991 / 0.990 | ✅ |

Four of five predictions held. The peak ratio sits slightly below N², which I attribute to the outer zones seeing steeper angles (NA 0.24 → 0.46) so their efficiency drops, and to the 0.5 µm glass step giving exactly π only for normal rays — not checked numerically. The miss is the hemisphere integral. Integrating over a hemisphere of radius R = f = 200 µm with θ from 0 to 90° in 91 steps returns only 70–76 % of the near top flux, and less for larger N. With an aperture D ≈ 2R_N of 100–200 µm the far-field fringe spacing is λ/D ≈ 0.14–0.29°, so a 1° sample skips several fringes at a time. The 0.96 at res 12.5 is a case where the samples happened to land on crests. Re-integrating the same run with 1801 θ points (0.05°) gives 1.025 of the near flux, which confirms under-sampling as the cause. The transmitted/incident flux close to 1 shows that the near-field balance itself is right; what was wrong was the sampling of the far integral.

### Convergence

| Variable | Values | Result | Note |
|---|---|---|---|
| resolution (N 25) | 12.5 / 25 / 50 | z peak 199.45 / 199.85 / 199.95; peak 3616 / 4683 / 4789; FWHM_r 1.047 / 1.052 / 1.054 | 25 → 50: peak 2.2 %, FWHM 0.1 % — res 25 converged |
| far scan step | 0.1 µm (upstream) | r₀ = 1.2043 at all three resolutions | pinned to the grid; use ≤ 0.02 µm to compare resolution |
| hemisphere θ samples | 91 (1°) | far/near 0.70–0.76 | 1801 points (0.05°) diagnostic: far/near 1.025 — sampling confirmed |
| run time | N 25 609 s, N 50 1439 s, N 100 3413 s (4 runs concurrently) | 1.5–3.7 s per far point | 0.1–0.5 s per point when run alone |

### What the results do and do not establish

- Established: the cylindrical near2far of the current Meep (1.33) reproduces the official zone-plate figures (N 25/50/100) as drawn, and the focal position, size and intensity agree with scalar theory (f, 1.22·Δr_N, N²) within 5 %. The upstream resolution 25 is converged.
- Not established (by the pre-registered criteria): power conservation of the 91-point hemisphere integral — the 1801-point diagnostic gives 1.025. The dependence of r₀ on resolution (pinned to the far grid). Why the peak ratio sits below N² (hypothesis only).

## 6. Common mistakes

| Symptom | Cause | Fix |
|------|------|----------|
| far field off by a factor of several | near2far face inside the glass | move the face into the air (inside the PML) |
| no focus | typo in the r_n rule, or disc stacking order | r_n² rule, largest disc first |
| hemisphere power smaller than the near flux | θ sampling coarser than the fringes (λ/D) | sample step < λ/(2D) |
| only the r = 0 column is bright / image transposed | cylindrical get_array is ordered (z, r) | do not transpose |
| seconds per far point | far points near the near surface, or concurrent runs | shrink the scan or run alone |
| diffraction from the source edge | no is_integrated | enable it |

## 7. Try it yourself

| Change | Expected change | Number to check |
|---------|----------|------------|
| N 200 | peak 4×, r₀ 0.47 µm | peak ratio, r₀ |
| height 0.5 → 0.4 (phase 0.8π) | lower peak | peak ratio |
| far step 0.1 → 0.02 | FWHM stable to more digits | FWHM_r |
| hemisphere θ 91 → 1801 points | power ratio → 1 | P_far/P_top |

<h2 id="reference">8. Full code and references</h2>

`code/zone_plate_near2far.py` — arguments `--num-zones --resolution --far-res --hemi --anim`. It includes the PROJ-013 reproduction monitors (flux, hemisphere, DFT, recording).

<details>
<summary>zone_plate_near2far.py (click to expand)</summary>
{% highlight python %}
"""E track — reproduction of the official Meep example zone_plate.py / .ipynb (Cylindrical_Coordinates.md "Focusing Properties of a Binary-Phase Zone Plate").
Upstream: NanoComp/meep python/examples/zone_plate.py @ upstream/COMMIT :10–164 unchanged
(cyl m=−1, res 25, PML 1, glass substrate 2(+PML), zone height 0.5, padding 2, λ 0.5 fwidth 0.2 f, planewave Er + (−i)Eφ is_integrated (inside the substrate at z = −size_z/2 + pml),
N zones r_n² = nλ(f + nλ/4), f 200; near2far faces: top z = size_z/2 − pml (width size_r − pml) + side; stop_when_fields_decayed(50, Er, (size_r/2, 0, 0), 1e-6);
far-field r scan (z = f, 0…size_r−pml) and z scan (r 0, f ± 50) with step 1/far_res).
Added (field-neutral): transmitted flux face (same position as the near2far top), incident flux (inside the substrate above the source), hemisphere far-field power (balance), DFT Er map, source-point waveform, (--anim) recording, peak/FWHM/first-zero postprocessing, resolution argument.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import meep as mp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_blog", "tools"))
ap = argparse.ArgumentParser()
ap.add_argument("--num-zones", type=int, default=25)
ap.add_argument("--resolution", type=float, default=25)
ap.add_argument("--far-res", type=float, default=10, help="far-field scan points per µm (upstream 10)")
ap.add_argument("--scan-z", type=float, default=100)
ap.add_argument("--rscan-max", type=float, default=None, help="end of the r scan (default size_r − pml; smaller is faster)")
ap.add_argument("--hemi", type=int, default=0, help="number of hemisphere far-field points (0 = skip), radius = f")
ap.add_argument("--anim", action="store_true")
ap.add_argument("--tag", default="zp")
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
resolution_um = a.resolution
pml_um, substrate_um, padding_um, height_um = 1.0, 2.0, 2.0, 0.5
focal_length_um, scan_length_z_um, farfield_resolution_um = 200, a.scan_z, a.far_res
wavelength_um = 0.5
frequency = 1 / wavelength_um
fwidth = 0.2 * frequency
num_zones = a.num_zones
zone_radius_um = np.array([math.sqrt(n * wavelength_um * (focal_length_um + n * wavelength_um / 4)) for n in range(1, num_zones + 1)])
size_r_um = zone_radius_um[-1] + padding_um + pml_um
size_z_um = pml_um + substrate_um + height_um + padding_um + pml_um
cell_size = mp.Vector3(size_r_um, 0, size_z_um)
src_z = -0.5 * size_z_um + pml_um
sources = [mp.Source(mp.GaussianSource(frequency, fwidth=fwidth, is_integrated=True), component=mp.Er, center=mp.Vector3(0.5 * size_r_um, 0, src_z), size=mp.Vector3(size_r_um)),
           mp.Source(mp.GaussianSource(frequency, fwidth=fwidth, is_integrated=True), component=mp.Ep, center=mp.Vector3(0.5 * size_r_um, 0, src_z), size=mp.Vector3(size_r_um), amplitude=-1j)]
glass = mp.Medium(index=1.5)
geometry = [mp.Block(material=glass, size=mp.Vector3(size_r_um, 0, pml_um + substrate_um), center=mp.Vector3(0.5 * size_r_um, 0, -0.5 * size_z_um + 0.5 * (pml_um + substrate_um)))]
z_lens = -0.5 * size_z_um + pml_um + substrate_um + 0.5 * height_um
for n in range(num_zones - 1, -1, -1):
    geometry.append(mp.Block(material=glass if n % 2 == 0 else mp.vacuum, size=mp.Vector3(zone_radius_um[n], 0, height_um), center=mp.Vector3(0.5 * zone_radius_um[n], 0, z_lens)))
sim = mp.Simulation(cell_size=cell_size, boundary_layers=[mp.PML(thickness=pml_um)], resolution=resolution_um, sources=sources, geometry=geometry, dimensions=mp.CYLINDRICAL, m=-1)
z_top = 0.5 * size_z_um - pml_um
n2f = sim.add_near2far(frequency, 0, 1, mp.Near2FarRegion(center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, z_top), size=mp.Vector3(size_r_um - pml_um, 0, 0)),
                       mp.Near2FarRegion(center=mp.Vector3(size_r_um - pml_um, 0, z_top - 0.5 * (height_um + padding_um)), size=mp.Vector3(0, 0, height_um + padding_um)))
# added monitors: transmitted flux (top), incident flux (inside the substrate, 0.5 above the source), DFT Er map
fl_top = sim.add_flux(frequency, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, z_top), size=mp.Vector3(size_r_um - pml_um, 0, 0)))
fl_inc = sim.add_flux(frequency, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, src_z + 0.5), size=mp.Vector3(size_r_um - pml_um, 0, 0)))
dm = sim.add_dft_fields([mp.Er], [frequency], center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, 0), size=mp.Vector3(size_r_um - pml_um, 0, size_z_um - 2 * pml_um))
probe = mp.Vector3(0.5 * size_r_um, 0, 0)
tv = {"t": [], "v": []}


def rec_probe(s_):
    v = s_.get_field_point(mp.Er, probe)
    if mp.am_master():
        tv["t"].append(s_.meep_time()); tv["v"].append([float(np.real(v)), float(np.imag(v))])


steps = [mp.at_every(0.1, rec_probe)]
rec = None
if a.anim:
    from field_anim import Recorder
    rec = Recorder(sim, mp.Er, mp.Vector3(0.5 * (size_r_um - pml_um), 0, 0), mp.Vector3(min(size_r_um - pml_um, 20.0), 0, size_z_um - 2 * pml_um), dt=0.25, t_max=30.0, probe=probe, period=1 / frequency)
    steps += [rec.step, rec.pstep]
t1 = time.time()
sim.run(*steps, until_after_sources=mp.stop_when_fields_decayed(50.0, mp.Er, probe, 1e-6))
out = {"tag": a.tag, "num_zones": num_zones, "resolution": resolution_um, "far_res": farfield_resolution_um, "size_r": size_r_um, "size_z": size_z_um, "R_N": float(zone_radius_um[-1]), "outer_zone_width": float(zone_radius_um[-1] - zone_radius_um[-2]),
       "steps": int(round(sim.meep_time() / sim.fields.dt)), "t_end": sim.meep_time(), "wall_fdtd": time.time() - t1}
out["flux_top"] = float(mp.get_fluxes(fl_top)[0]); out["flux_inc"] = float(mp.get_fluxes(fl_inc)[0]); out["T_top_over_inc"] = out["flux_top"] / out["flux_inc"]
z_f = -0.5 * size_z_um + pml_um + substrate_um + height_um + focal_length_um
r_max = a.rscan_max if a.rscan_max else (size_r_um - pml_um)
t2 = time.time()
ff_r = sim.get_farfields(n2f, farfield_resolution_um, center=mp.Vector3(0.5 * r_max, 0, z_f), size=mp.Vector3(r_max, 0, 0))
ff_z = sim.get_farfields(n2f, farfield_resolution_um, center=mp.Vector3(0, 0, z_f), size=mp.Vector3(0, 0, scan_length_z_um))
out["wall_farfield"] = time.time() - t2
Ir = np.abs(ff_r["Ex"]) ** 2 + np.abs(ff_r["Ey"]) ** 2 + np.abs(ff_r["Ez"]) ** 2
Iz = np.abs(ff_z["Ex"]) ** 2 + np.abs(ff_z["Ey"]) ** 2 + np.abs(ff_z["Ez"]) ** 2
rr = np.linspace(0, r_max, Ir.size); zz = np.linspace(focal_length_um - 0.5 * scan_length_z_um, focal_length_um + 0.5 * scan_length_z_um, Iz.size)


def fwhm_first_zero(x, y):
    i0 = int(np.argmax(y)); half = y[i0] / 2
    j = i0
    while j + 1 < len(y) and y[j + 1] > half:
        j += 1
    xr = x[j] + (x[j + 1] - x[j]) * (y[j] - half) / (y[j] - y[j + 1]) if j + 1 < len(y) else x[-1]
    k = i0
    while k - 1 >= 0 and y[k - 1] > half:
        k -= 1
    xl = x[k] - (x[k] - x[k - 1]) * (y[k] - half) / (y[k] - y[k - 1]) if k - 1 >= 0 else x[0]
    m = i0
    while m + 1 < len(y) and y[m + 1] < y[m]:
        m += 1
    return float(xr - xl), float(x[m])


out["I_peak_r"] = float(Ir.max()); out["r_peak"] = float(rr[int(np.argmax(Ir))]); out["I_peak_z"] = float(Iz.max()); out["z_peak"] = float(zz[int(np.argmax(Iz))])
w_r, r_first_min = fwhm_first_zero(rr, Ir)
out["fwhm_r_half_profile"] = w_r; out["fwhm_r_full"] = 2 * (w_r if rr[int(np.argmax(Ir))] == 0 else w_r)   # r ≥ 0 half profile → full width 2×(half width) when the peak is at r = 0
out["r_first_min"] = r_first_min
w_z, _ = fwhm_first_zero(zz, Iz); out["fwhm_z"] = w_z
if a.hemi:
    t3 = time.time()
    th = np.linspace(0, 0.5 * math.pi, a.hemi)
    Rh = focal_length_um
    P = 0.0; rows = []
    for t_ in th:
        pt = mp.Vector3(Rh * math.sin(t_), 0, z_f - focal_length_um + Rh * math.cos(t_))
        E = sim.get_farfield(n2f, pt)
        Ex, Ey, Ez, Hx, Hy, Hz = [E[i] for i in range(6)]
        Sx = np.real(Ey * np.conj(Hz) - Ez * np.conj(Hy)); Sz = np.real(Ex * np.conj(Hy) - Ey * np.conj(Hx))
        Sr = Sx * math.sin(t_) + Sz * math.cos(t_)
        rows.append([float(t_), float(Sr)])
    th_a = np.array([r_[0] for r_ in rows]); Sr_a = np.array([r_[1] for r_ in rows])
    P = float(np.trapezoid(Sr_a * 2 * math.pi * Rh**2 * np.sin(th_a), th_a))   # the φ average of the m = ±1 components is axisymmetric → φ integral = 2π (Sr is the φ average)
    out["P_far_hemisphere"] = P; out["hemi_rows"] = rows; out["P_far_over_flux_top"] = P / out["flux_top"] if out["flux_top"] else None; out["wall_hemi"] = time.time() - t3
er = sim.get_dft_array(dm, mp.Er, 0)
eps = sim.get_array(component=mp.Dielectric, center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, 0), size=mp.Vector3(size_r_um - pml_um, 0, size_z_um - 2 * pml_um))
if mp.am_master():
    out["probe"] = tv
    out["wall_total"] = time.time() - T0
    np.savez_compressed(os.path.join(a.out, a.tag + "_fields.npz"), er=er, eps=np.real(eps), extent=np.array([0, size_r_um - pml_um, -(size_z_um / 2 - pml_um), size_z_um / 2 - pml_um]), rr=rr, Ir=Ir, zz=zz, Iz=Iz)
    if rec is not None:
        pass
    json.dump(out, open(os.path.join(a.out, a.tag + ".json"), "w"), indent=1)
    print(f"RESULT N={num_zones} res={resolution_um:g} z_peak={out['z_peak']:.2f} I_peak_z={out['I_peak_z']:.1f} I_peak_r={out['I_peak_r']:.1f} fwhm_r_full={out['fwhm_r_full']:.3f} r_first_min={out['r_first_min']:.3f} fwhm_z={out['fwhm_z']:.2f} T={out['T_top_over_inc']:.4f} Pfar/Ptop={out.get('P_far_over_flux_top')} steps={out['steps']} wall={out['wall_total']:.0f}s", flush=True)
if rec is not None:
    rec.save(os.path.join(a.out, a.tag + "_anim.npz"), eps=True, meta=dict(title=f"zone plate N={num_zones} Er(r,z,t)", extent=[0, min(size_r_um - pml_um, 20.0), -(size_z_um / 2 - pml_um), size_z_um / 2 - pml_um], probe_label="mid-r, z 0"))

{% endhighlight %}
</details>

<h2 id="check">Check your understanding</h2>

1. Why does a 0.5 µm glass step in the odd zones amount to a π phase? (§2)
2. Why must the near2far surface not be placed inside the substrate? (§4 ⑤)
3. The hemisphere far-field power comes out below the near flux — what do you suspect first? (§5 balance, §6)

## 9. Further reading

- Meep documentation: [Cylindrical Coordinates — zone plate](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/#focusing-properties-of-a-binary-phase-zone-plate), [Near-to-far field spectra](https://meep.readthedocs.io/en/latest/Python_User_Interface/#near-to-far-field-spectra).
- LBL CXRO, [Zone plate theory](http://zoneplate.lbl.gov/theory) — Δr = 1.22 Δr_N.
- Original record of this chapter: PROJ-013 reproduction report e-zone-plate (14 pre-registered criteria; awaiting human review).
- Previous: 15 · When there are thousands of point sources · Cylindrical coordinates: [13 · Computing 3D with rotational symmetry]({{ site.baseurl }}/en/cylindrical-dipole/) · Next: 17 · Launching an oblique planewave
