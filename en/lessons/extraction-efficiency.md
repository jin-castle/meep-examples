---
layout: lesson
permalink: /en/extraction-efficiency/
lesson_title: "How much light escapes from a thin film into air?"
lesson_summary: "Measure air-side flux relative to source work, compare cylindrical and 3D calculations, and test m-series and kz-integration limits."
lesson_goals:
  - "Normalize extraction using source work and the correct coordinate-dependent volume."
  - "Identify premature m-series stopping and the need for kz integration."
  - "Report resolution and open-surface limitations alongside extraction efficiency."
lesson_prerequisites: "Chapter 11: dft_ldos · Chapter 13: cylindrical coordinates and m series"
date: 2026-10-23
title: "Meep Example 14 · A point source in a thin film: the fraction escaping into air — extraction efficiency, LDOS normalization, kz integration, and CYL vs 3D"
title_en: "Meep Example 14 · A point source in a thin film and the share that reaches the air — extraction efficiency, LDOS normalization, the kz integral, cylindrical vs 3D"
lang: en
translation_key: extraction-efficiency
series: meep-examples
part: 14
level: intermediate
runtime: "77 min (mpirun -np 4; B alone 58 min)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/#extraction-efficiency-of-a-light-emitting-diode-led"
tags: [meep, fdtd, extraction-efficiency, led, oled, ldos, cylindrical, kz, edge-emitter]
image: /assets/meep/14/04_m_series.png
excerpt: "post 11 measured how much a dipole emits (LDOS); post 13 split a body of revolution into m runs. An LED asks for the ratio: of everything a dipole in the emitting layer puts out, how much reaches the air. Extraction efficiency = flux through an open surface in air ÷ the source's own work from `dft_ldos`. Three official examples: a dipole in a layer on a mirror (cylindrical vs 3D), the same slab with the dipole off the axis (an m series), and a dipole inside the cleaved facet of a laser stack (a 2D cross-section plus a kz integral)."
---
<h2 id="observe">Observe: the fraction that reaches air</h2>

![hero]({{ '/assets/meep/14/04_m_series.png' | relative_url }})

- **What**: post 11 measured how much a dipole emits (LDOS); post 13 split a body of revolution into m runs. An LED asks for the ratio: of everything a dipole in the emitting layer puts out, how much reaches the air. Extraction efficiency = flux through an open surface in air ÷ the source's own work from `dft_ldos`. Three official examples: a dipole in a layer on a mirror (cylindrical vs 3D), the same slab with the dipole off the axis (an m series), and a dipole inside the cleaved facet of a laser stack (a 2D cross-section plus a kz integral).
- **Result**: A dipole halfway up the layer sends 0.323 of its power into air (cylindrical, resolution 80); the efficiency swings from 0.52 near the mirror to 0.09 near the top, and at resolution 40 cylindrical and 3D disagree by up to 16 %: a 0.29 µm layer needs resolution 80. 3.5 µm off the axis, the official stop rule (first m below 1 %) halts at m = 32 and reports 0.632; the series rebounds at m ≈ 41, where the slab-guided emission lives, and the sum to m = 60 gives 0.362, matching the on-axis 0.364. The cleaved laser facet needs 76 kz runs and extracts 22.4 %; a single 2D run (kz = 0) would claim 32.9 %.
- **Takeaway**: the denominator is not a vacuum constant but the dipole's own work, and its voxel volume differs between coordinate systems (2πr/res² vs 1/res³ vs 1/res²). Most of the light stays guided in a high-index film. Where you cut a series (m or kz) changes the answer, and the official "first term below 1 %" rule can stop before the guided light arrives.
- **Code**: full script at the bottom, ~77 min (mpirun -np 4; B alone 58 min).

## 0. What you will learn

- Extraction efficiency: the numerator is flux through an open surface in air; the denominator is source work from `dft_ldos`, $-\mathrm{Re}(FJ^*)\,\Delta V$.
- Coordinate-dependent $\Delta V$: cylindrical $2\pi r/\mathrm{res}^2$, 3D $1/\mathrm{res}^3$, and 2D $1/\mathrm{res}^2$.
- Cross-checking the same problem in cylindrical and 3D coordinates, including where agreement breaks down.
- Cases in which the stopping point of an off-axis dipole’s m series changes the result.
- A 3D point-source problem in a structure uniform along one direction (a cleaved laser facet) as a 2D cross-section plus kz integration.

**Prerequisites**: `dft_ldos` from chapter 11, cylindrical coordinates and m series from chapter 13. **Official examples**: [LED extraction efficiency in the LDOS tutorial](https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/#extraction-efficiency-of-a-light-emitting-diode-led) · [Nonaxisymmetric dipole sources](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/#nonaxisymmetric-dipole-sources) · scripts [extraction_eff_ldos.py](https://github.com/NanoComp/meep/blob/master/python/examples/extraction_eff_ldos.py) · [point_dipole_cyl.py](https://github.com/NanoComp/meep/blob/master/python/examples/point_dipole_cyl.py) · [edge_emitter_2D.py](https://github.com/NanoComp/meep/blob/master/python/examples/edge_emitter_2D.py). **Previous**: [13 · Computing 3D with rotational symmetry]({{ site.baseurl }}/en/cylindrical-dipole/) · **Next**: 15 · When there are thousands of point sources

## 1. What do we want to find out?

This was the closing question of chapter 13. Treat the dipole inside a disk as an emitter in an LED: what percentage of its light reaches air? In an index-2.4 layer, rays reach air only within the roughly 25° critical angle; the rest undergo total internal reflection and travel along the layer. Measuring this fraction requires two numbers: power reaching air and total power emitted by the dipole. A flux monitor measures the first. The second cannot be a vacuum constant because mirrors and layers change emission itself, as in chapter 11; measure the work done by the source in that structure. We also compare three economical approaches to 3D problems: cylindrical coordinates, 3D with symmetry, and 2D plus kz integration.

### Where is this useful?

Extraction efficiency is the second factor in external quantum efficiency (EQE) = internal quantum efficiency × extraction efficiency. Much of emitter design aims to increase it.

| Application | Quantity used here | What comes next |
|---|---|---|
| Emitting-layer design for OLEDs, LEDs, and micro-LEDs | Extraction versus height (distance from the electrode), with an LDOS-derived denominator | Chapter 15: thousands of emitters |
| Cleaved facets of semiconductor lasers and SOAs | 2D cross-section plus kz integration, polarization-dependent extraction | Chapter 18: angular response of interfaces |
| Collection from quantum dots and single-photon sources | On/off-axis dipole differences and m series | Chapter 16: far-field collection |
| Optimizing extraction structures: textures, lenses, photonic crystals | Numerator/denominator definitions and cross-check procedure | Chapter 35: near2far inverse design |

<h2 id="understand">2. Understand: the physics on one page</h2>

{% include chapter-illustration.html %}

Extraction efficiency is a ratio of powers. The numerator is measured with an open flux surface in air. The denominator is work done at the source, calculated from the field $F$ and current $J$ stored by `dft_ldos`. The volume $\Delta V$ associated with one source sample depends on coordinates.

$$
\eta=\frac{P_{\mathrm{air}}}{P_{\mathrm{total}}},\qquad
P_{\mathrm{total}}=-\mathrm{Re}\{F\,J^*\}\,\Delta V,\qquad
\Delta V=\begin{cases}2\pi r/\mathrm{res}^2 & \text{cylindrical}\\ 1/\mathrm{res}^3 & \text{3D}\\ 1/\mathrm{res}^2 & \text{2D (line current)}\end{cases}
$$

Both an off-axis dipole in cylindrical coordinates and a point source in a structure uniform along one direction can be reconstructed as series: the first over m, the second over kz. Different m or kz contributions are orthogonal for integrated power, so add their powers. The ±m and ±kz terms give equal power here, so nonzero terms count twice.

$$
\eta_{\mathrm{off\text{-}axis}}=\frac{\sum_m w_m P^{(m)}_{\mathrm{air}}}{\sum_m w_m P^{(m)}_{\mathrm{total}}},\qquad
\eta_{\mathrm{edge}}=\frac{P_{\mathrm{air}}(0)+2\sum_{k_z>0}P_{\mathrm{air}}(k_z)}{P_{\mathrm{tot}}(0)+2\sum_{k_z>0}P_{\mathrm{tot}}(k_z)},\qquad w_0=1,\ w_{m>0}=2
$$

Light confined to the high-index layer (guided modes) travels radially along it. For a dipole at radius r, guided emission appears around azimuthal order $m\approx 2\pi n_{\mathrm{eff}} r/\lambda$. Contributions sampled by the finite side monitor enter the numerator; truncating the series before reaching those orders changes the answer. The source-work denominator also contains their substantial guided-emission power.

| Symbol | Meaning | Code variable |
|------|----|-----------|
| $\eta$ | Extraction efficiency | `p_air / p_tot` |
| $h$ | Dipole height above the mirror / layer thickness | `HEIGHTS` |
| $F, J$ | Source-point field and current stored by `dft_ldos` | `sim.ldos_Fdata`, `sim.ldos_Jdata` |
| $\Delta V$ | Volume associated with one source sample | `2*pi*r/res**2`, `1/res**3`, `1/res**2` |
| $m$, $k_z$ | Series terms | `m=`, `k_point=(0,0,kz)` |

**Assumptions and validity**: wavelength 1 µm; lossless layers and PEC mirrors in A/B, lossless multilayers in C. The numerator is an open-surface measurement of the fraction entering air, not a closed energy budget. The lateral extent L is finite (A: 6 µm, B: 20 µm), with side monitors counting light crossing those surfaces.

<h2 id="predict">Predict before viewing the results</h2>

| Quantity | Prediction | Reason |
|--------|---------|------|
| Extraction (A, h = 0.5) | Near 0.3 | Notes: 0.323 (CYL), 0.337 (3D) |
| Height dependence | Changes with distance from the mirror | Dipole–image interference (chapter 10) |
| CYL res 40 vs 80 | Within 1% | At least 40 cells per vacuum wavelength |
| 3D vs CYL | Within 2% | Notes: maximum absolute difference 0.017 |
| On-axis dipole (B) | Near 0.3 | Same layer, different cell size |
| B: official stopping rule | Differs from summing to 60 | Notes: 0.63–0.74 vs 0.36 |
| C: number of kz samples | 70~80 | Notes: 76 |
| C: extraction | Near 22% | Notes: 22.4% |

**Decision criteria**: if efficiency is below 0 or above 1, check denominator $\Delta V$ and flux-surface signs. A factor-of-2 mismatch between CYL and 3D suggests voxel volume or source normalization; a 5~10% discrepancy suggests resolution or source position.

## 3. Simulation layout

![layout]({{ '/assets/meep/14/01_layout.png' | relative_url }})
*Part A cylindrical (r, z) cell (x labels r, y labels z). The gray layer has n 2.4 and thickness 0.292 µm. Its bottom cell wall has no PML and acts as a PEC mirror. The red point is the Er dipole 1.5 pixels off-axis. Blue lines are the open top and side flux surfaces measuring the numerator; blue hatching marks a representative DFT region. Circled numbers refer to §4.*

![layout edge]({{ '/assets/meep/14/02_layout_edge.png' | relative_url }})
*Part C 2D cross-section. The multilayer consists of substrate (n 3.2), cladding (1.5), active layer (2.3), and cladding. It ends at x = 1.5 µm (the cleaved facet), with air on the right. The dipole is in the active layer, 0.5 µm inside the facet. Because geometry is uniform along z, each kz requires one 2D run.*

| Parameter | Value | Why this value? | Effect of changing it |
|----------|-----|-------------|--------|
| A layer | n 2.4, thickness 0.7λ/n = 0.292 µm, above a mirror | Official values | Thickness changes the number of guided modes |
| A heights | 0.1~0.9, 9 points | Reduced from the official 21 points | — |
| A resolution | CYL 40/80, 3D 40 | Official value 80; 3D reduced to 40 for cost | A 3D res-80 cell has about 45 million grid cells |
| A collection surface | Lateral extent 6 µm, air height 1 µm | Official values | A narrow surface may miss oblique emission |
| B cell | r 20 µm, same layer, res 50 | Official point_dipole_cyl.py | — |
| B dipole | r = 3.5 µm, m = 0…60 | One official radius, extending beyond $2\pi n r\approx53$ | Official code stops at the first term below 1% |
| C multilayer | 3.2 / 1.5 / 2.3 / 1.5, res 25 | Official edge_emitter_2D.py | — |
| C kz | Step 0.02, until total power is below 2% of its maximum | Official values | Coarse spacing can miss guided peaks |

![source]({{ '/assets/meep/14/00_source.png' | relative_url }})
*Source waveform and spectrum (1000 nm, fwidth 0.1 fcen; B uses 0.05). Efficiency is measured at the single center frequency.*

**Differences from the course notebooks**: this topic is outside the course scope. Three 10_sources notes used the full official conditions: 21 heights × 2 coordinate systems at res 80, four radii with hundreds of m runs, and 76 kz samples. This chapter reduces A’s 3D checks to three heights at res 40, and compares the official stopping rule with summation through m = 60 at one radius in B.

<h2 id="run">4. Run and follow the code</h2>

> Reading order: units and parameters → materials and geometry → source → Simulation and boundaries → monitors → run and stopping conditions → postprocessing.
> The key step here is the denominator in ⑦.

### ① Units and parameters — which values are fixed?

```python
WL, FREQ, N_L = 1.0, 1.0, 2.4
T_L = 0.7 * WL / N_L                      # layer thickness
DPML, DAIR, L = 0.5, 1.0, 6.0             # PML, air above the layer, lateral size of the collection surface
HEIGHTS = np.round(np.linspace(0.1, 0.9, 9), 3)      # dipole height above the ground plane, fraction of T_L
DKZ, KZ_TOL = 0.02, 0.02                  # part C: kz step and stop when the total power falls below 2 % of its max
```

- **What**: layer and collection surface, height sweep, and kz step.
- **Why**: thickness 0.7λ/n supports roughly one guided mode. Changing height alters dipole–image interference, changing both the amount and direction of emission.
- **If wrong**: a narrow collection extent L lets oblique light reach PML without being counted, reducing the numerator.

### ② Materials and geometry — one layer and a mirror

```python
mp.Block(material=mp.Medium(index=N_L), center=mp.Vector3(0, 0, -0.5 * sz + 0.5 * T_L), size=mp.Vector3(mp.inf, mp.inf, T_L))
boundary_layers=[mp.PML(DPML, direction=mp.R), mp.PML(DPML, direction=mp.Z, side=mp.High)]     # bottom: no PML = ground plane
```

- **What**: an infinite layer touching the cell bottom, which has no PML.
- **Why**: as in chapters 11 and 13, the bottom wall without PML is a PEC mirror. Only the top and sides are open.
- **If wrong**: the official docstring says "metallic ground plane," but there is no metal block. The mirror is a boundary condition. Bottom PML removes it and changes efficiency.

### ③ Sources — three representations of the same dipole

```python
mp.Source(src, component=mp.Er, center=mp.Vector3(1.5 / res, 0, z_src))      # cylindrical, m = -1 (chapter 13: in-plane dipole)
mp.Source(src, component=mp.Ex, center=mp.Vector3(0, 0, z_src))              # 3D with Mirror(X, -1), Mirror(Y)
mp.Source(src, component=mp.Ez, center=SRC_C)                                 # 2D + kz: a line current along z with phase exp(i kz z)
```

- **What**: A’s horizontal dipole is Er (m = −1) in cylindrical coordinates and Ex in 3D. C uses a z-directed dipole in the cleaved laser stack.
- **Why**: a point source in a 2D cell represents a z-invariant line current. Applying phase $e^{ik_zz}$ and integrating over kz reconstructs a point source. This extends chapter 10’s 1D Bloch-run idea by one dimension.
- **If wrong**: Er at r = 0 has no corresponding component on the axial Yee grid, causing incorrect results (meep #2704). Offset by 1.5 pixels.

### ④ Simulation and boundaries — coordinates and kz

```python
mp.Simulation(..., dimensions=mp.CYLINDRICAL, m=-1)                                                   # A, cylindrical
mp.Simulation(..., symmetries=[mp.Mirror(mp.X, phase=-1), mp.Mirror(mp.Y)])                          # A, 3D: 1/4 of the cell
mp.Simulation(..., k_point=mp.Vector3(0, 0, kz), kz_2d="real/imag")                                   # C: 2D cell, out-of-plane wavevector
```

- **What**: the same physics in three representations. C uses the z component of `k_point` and `kz_2d` in a 2D cell.
- **Why**: `kz_2d="real/imag"` solves the nonzero-kz 2D problem using two real field sets. Equivalence of real/imag, complex, and 3d representations was checked in the 10_sources kz_2d note (planned for chapter 18).
- **If wrong**: setting both 3D mirror phases to +1 represents a source with different parity (chapter 11).

### ⑤ Monitors — the numerator uses an open surface in air

```python
mp.FluxRegion(center=mp.Vector3(0.5 * L, 0, 0.5 * sz - DPML), size=mp.Vector3(L, 0, 0))                   # top
mp.FluxRegion(center=mp.Vector3(L, 0, 0.5 * sz - DPML - 0.5 * DAIR), size=mp.Vector3(0, 0, DAIR))         # side, air only
sim.run(mp.dft_ldos(FREQ, 0, 1), until_after_sources=...)                                                  # denominator data
```

- **What**: flux through the top and sides, with sides spanning only air height. In 3D there are four side faces; negative-facing ones use `weight=-1`. A concurrent `dft_ldos` step function collects denominator data.
- **Why**: extending side monitors into the layer counts laterally guided light as extracted. Limit their span to the air region.
- **If wrong**: in B’s cylindrical cell (r 20 µm), guided light has an evanescent tail reaching the air-side monitor near PML. Although the official code limits the side monitor to the air height, that tail can contribute. This is related to the rebound in §5.

### ⑥ Run — series and stopping criteria

```python
for m in range(M_MAX + 1):                                    # B: every m up to 60, then decide where to cut afterwards
    rad, src = dipole_in_slab(R_SRC, m)
m_stop = next(m for m in range(1, M_MAX + 1) if rel[m] < 1e-2)    # the official rule, applied to the same data

while True:                                                    # C: kz = 0, 0.02, 0.04, ...
    ...
    if dflux > dmax: dmax = dflux
    elif dflux / dmax < KZ_TOL: break
```

- **What**: B runs every m through 60 instead of stopping early, then applies the official stopping rule to the same data for comparison. C retains the official rule.
- **Why**: testing a stopping rule requires actually observing terms beyond its proposed stopping point.
- **If wrong**: using only the official rule in B hides all terms after m_stop, including the rebound.

### ⑦ Postprocessing — denominator and series

```python
p_tot = -np.real(sim.ldos_Fdata[0] * np.conj(sim.ldos_Jdata[0])) * dV     # dV: 2*pi*r/res**2 (cyl), 1/res**3 (3D), 1/res**2 (2D)
eff = p_air / p_tot
eff_series = np.cumsum(w * rads) / np.cumsum(w * srcs)                    # w = 1 for m = 0, 2 for m > 0
eff_edge = (a_kz[0] + 2 * a_kz[1:].sum()) / (d_kz[0] + 2 * d_kz[1:].sum())
```

- **What**: the denominator is work done by one source. Sum numerator and denominator separately across the series, then divide.
- **Why**: do not average per-term efficiencies. Terms carrying more power must carry more weight.
- **If wrong**: omitting $\Delta V$ can make cylindrical and 3D results differ by hundreds-fold. The cylindrical $2\pi r$ factor reflects the source ring around the axis.

> **Pitfall**: chapter 11’s Purcell factor divides two runs in the same coordinate system, so $\Delta V$ cancels. Extraction divides physical flux by source work, so $\Delta V$ does not cancel. Change this factor when changing coordinates.

<h2 id="interpret">5. Interpret the results</h2>

![height]({{ '/assets/meep/14/03_height.png' | relative_url }})
*Part A. Left: extraction versus dipole height, for cylindrical res 80 (blue), res 40 (cyan), and 3D res 40 (red diamonds). Right: log|Er| at h = 0.5. The white rectangle is the layer; light traveling far along it is the confined portion.*

| h | CYL res 80 | CYL res 40 | 3D res 40 | Notes: 3D res 80 |
|---|---|---|---|---|
| 0.1 | 0.5230 | 0.5494 | 0.5475 | — |
| 0.2 | 0.5038 | 0.5214 | — | — |
| 0.3 | 0.4645 | 0.4735 | — | — |
| 0.4 | 0.4050 | 0.4014 | — | — |
| 0.5 | 0.3232 | 0.3018 | 0.3505 | 0.3369 |
| 0.6 | 0.2213 | 0.1805 | — | — |
| 0.7 | 0.1259 | 0.0891 | — | — |
| 0.8 | 0.0915 | 0.1095 | — | — |
| 0.9 | 0.1745 | 0.2681 | 0.2607 | — |

![m series]({{ '/assets/meep/14/04_m_series.png' | relative_url }})
*Part B. Left: radiated power per m for the r = 3.5 µm dipole, divided by the running maximum. The red dashed line is the official 1% threshold; gray marks $m=2\pi nr$. Right: efficiency versus series truncation order. The purple dashed line is the on-axis dipole’s efficiency in the same layer.*

| Calculation | m range | Extraction efficiency |
|---|---|---|
| On-axis dipole (r = 0.03 µm, m = 1) | 1 run | 0.3636 |
| r = 3.5 µm, official rule (first term below 1%) | 0…32 | 0.6323 |
| r = 3.5 µm, summed through m = 60 | 0…60 | 0.3616 |
| Rebound after the official stop | 0.38 of maximum at m = 41 | — |
| Notes (10_sources): official CYL / 3D reference | — | 0.320–0.324 / 0.334 |

![kz]({{ '/assets/meep/14/05_kz.png' | relative_url }})
*Part C. Left: total emission (gray) and power entering air (blue) per kz. Dashed lines mark the light lines of air, cladding, and active layer. Right: efficiency versus the largest included kz.*

| Quantity | Value |
|---|---|
| kz samples | 76 (0~1.50, step 0.02) |
| Last-kz total power / maximum | 0.0189 |
| Extraction efficiency (kz integral) | 22.375% |
| kz = 0 alone (2D line current) | 32.91% |
| Notes (10_sources) | 22.375%, 76 points |

![animation]({{ '/assets/meep/14/07_anim_edge.gif' | relative_url }})
*Part C, short pulse at kz = 0. Most light from the active-layer dipole (red) travels along the multilayer toward the substrate; some crosses the facet into air.*

### Compare with the predictions

| Quantity | Prediction (§2) | Simulation | Assessment |
|--------|-------------|-----------|------|
| Extraction (A, h = 0.5) | Near 0.3 | 0.323 (CYL res 80) | Pass |
| Height dependence | Changes with mirror distance | 0.52 → 0.09(h 0.8) → 0.17 | Pass |
| CYL res 40 vs 80 | Within 1% | 2~5% at h ≤ 0.4; 18~54% at h ≥ 0.6 | Fail |
| 3D vs CYL | Within 2% | res 40: h 0.1 0.4%, h 0.5 16%, h 0.9 2.7% | Fail |
| On-axis dipole (B) | Near 0.3 | 0.364 | Pass |
| B: official stopping rule | Different from sum-to-60 | 0.632 vs 0.362 | Pass |
| C: required kz samples | 70~80 | 76 | Pass |
| C: extraction | Near 22% | 22.375% | Pass |

Six of eight predictions held; both failures concerned resolution. A 0.292 µm layer spans only 11.7 cells at res 40. Specifying dipole height as a thickness fraction leads to grid rounding. Near the upper air interface (h ≥ 0.6), the field varies rapidly, so one or two cells can change efficiency substantially. The 16% CYL–3D mismatch at h = 0.5 and res 40 is likewise attributed to resolution/source placement. The notes’ res-80 values, CYL 0.323 and 3D 0.337, differ by 0.014, or 1.4 percentage points (not 1.4% relative). This layer needs finer resolution than 40; even res 80 requires a convergence check for a precise claim. B matches the notes to four decimal places. The official rule stops at m = 32 and returns 0.632, but terms rebound around m = 41. Those terms have large source work (denominator) and a smaller air contribution (numerator). Guided emission is carried near the order fitting the effective-index wavelengths around circumference $2\pi r$, namely $m\approx2\pi n_{\mathrm{eff}}r$. Omitting it removes much of the denominator and roughly doubles efficiency. Summing through m = 60 gives 0.362, within 0.5% of the on-axis 0.364. In an infinite layer, lateral translation of a dipole should not change extraction, making this a useful check on truncation. In C, kz = 0 alone (a 2D line current) gives 32.9%, while integration gives 22.4%. Beyond the air light line k₀, propagating emission into air vanishes (blue), but guided emission in the stack remains (gray peaks). A single 2D calculation misses that portion of a 3D point source.

### Convergence

| Variable | Values | Result | Notes |
|---|---|---|---|
| A resolution | CYL 40 / 80 (notes: 80) | h 0.5: 0.302 / 0.323 | res 40 gives only about 12 cells through the layer |
| A coordinates | CYL 40 vs 3D 40; notes: CYL 80 vs 3D 80 | 16% relative / 1.4 percentage points absolute (h 0.5) | Higher resolution improves agreement; these use different error conventions |
| B m range | 0…32 / 0…60 | 0.632 / 0.362 | Last term 2e-8 |
| C kz range | 0 / 0…1.50 | 32.9% / 22.4% | Tail 0.019 |

### What the results do and do not establish

- Established: for this layer (n 2.4, 0.7λ/n, above a mirror), horizontal-dipole extraction varies from 0.52 to 0.09 with height. At h = 0.5, the cylindrical res-80 value is 0.323. A dipole 3.5 µm off-axis gives the same roughly 0.36 as the on-axis dipole when the series extends beyond guided-emission orders to 60. The cleaved laser facet (z dipole, 0.5 µm inside) gives 22.4% after kz integration.
- Not established: convergence of the res-40 height curve, especially h ≥ 0.6; convergence of 3D results (only res 40 was run here); a unique cause for B’s 0.36 versus A’s 0.32, since cell size (20 vs 6 µm), resolution (50 vs 80), and bandwidth differ; or a closed energy budget showing where all confined light goes in this lossless model.

## 6. Common mistakes

| Symptom | Cause | Fix |
|------|------|----------|
| Efficiency exceeds 1 or differs hundreds-fold | Missing or coordinate-inappropriate $\Delta V$ | Cylindrical $2\pi r/\mathrm{res}^2$, 3D $1/\mathrm{res}^3$, 2D $1/\mathrm{res}^2$ |
| Denominator uses vacuum source power | Mirrors and layers alter emission | Measure `dft_ldos` in the same run |
| Efficiency too large | Side monitor extends down through the layer | Limit the side surface to air height |
| CYL fails near the axis | Er placed at r = 0 | Offset by 1.5 pixels |
| m-series efficiency differs greatly | Stopped at the first 1% crossing | Examine orders beyond guided light at $m\approx2\pi nr$ |
| kz integral too small | Positive-kz terms not doubled | Use ±kz symmetry, $w=2$ |
| 3D differs from CYL by a factor of 2 | Wrong 3D symmetry phase | Ex requires Mirror(X, −1) |

## 7. Try it yourself

| Change | Expected effect | Quantity to check |
|---------|----------|------------|
| A layer thickness 0.7λ/n → 0.4λ/n | Fewer guided modes may increase extraction | η(h = 0.5) |
| A: vertical dipole (Ez, m = 0) | Less upward radiation, substantially lower extraction | η |
| B r = 6.7, 9.5 µm | Rebound shifts to larger m | m_stop and rebound order |
| C: x and y polarization | Different extraction for each polarization | η |
| Disk with 11 dipoles (disc_extraction_efficiency.py) | Notes: 0.932, 93 m runs | η and last-term contribution |

<h2 id="reference">8. Full code and references</h2>

<details>
<summary>Full code/extraction_efficiency.py (expand)</summary>
{% highlight python %}
"""Meep Example 14 - A point source in a thin film: the share that escapes into air (light-extraction efficiency).

Post 11 measured how much a dipole emits (LDOS); post 13 split a body of revolution into m runs. An LED asks
the ratio of the two: of all the power a dipole in the emitting layer puts out, how much reaches the air?
    extraction efficiency = P_air (flux through an open surface in air) / P_total (source work from dft_ldos)
  A. Official extraction_eff_ldos.py: a dipole in a dielectric layer (n = 2.4, t = 0.7 wl / n) on a ground
     plane, efficiency vs dipole height, in cylindrical coordinates (Er, m = -1) at resolution 40 and 80 and in
     3D (Ex) at resolution 40. The denominator needs the voxel volume of each coordinate system.
  B. Official point_dipole_cyl.py: the same slab, a dipole 3.5 um off the axis = an m series. The official stop
     rule (first m whose radiated flux < 1 % of the running max) is compared with summing far beyond it: the
     slab-guided light reaches the side monitor through high m and the series rebounds.
  C. Official edge_emitter_2D.py: a z-dipole 0.5 um inside the cleaved facet of a multilayer laser stack.
     The 3D problem is a 2D cross-section plus an integral over the out-of-plane wavevector kz.
MPI-safe: collective calls on every rank, figures on the master only.

Run:  mpirun -np 4 python extraction_efficiency.py      (~40 min)
Out:  00_source.png, 01_layout.png, 02_layout_edge.png, 03_height.png, 04_m_series.png, 05_kz.png,
      06_field.png, 07_anim_edge.gif, result.json   (-> ../assets/14/)
"""
import json
import math
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, animate_fields, annotated_layout, record_frames, source_figure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets", "14")
os.makedirs(OUT, exist_ok=True)
MASTER = mp.am_master()
t_all = time.time()


def say(*a):
    if MASTER:
        print(*a, flush=True)


def orient_rz(arr, nr):
    arr = np.asarray(arr)
    if arr.ndim == 2 and abs(arr.shape[1] - nr) < abs(arr.shape[0] - nr):
        return arr.T
    return arr


def source_work(sim, dV):
    """Total power emitted by the point source: -Re(F J*) dV from the dft_ldos data."""
    return float(-np.real(sim.ldos_Fdata[0] * np.conj(sim.ldos_Jdata[0])) * dV)


# ================================================================ A. dipole in a layer on a ground plane: CYL vs 3D
WL, FREQ, N_L = 1.0, 1.0, 2.4
T_L = 0.7 * WL / N_L                      # layer thickness
DPML, DAIR, L = 0.5, 1.0, 6.0             # PML, air above the layer, lateral size of the collection surface
TOL = 1e-8
HEIGHTS = np.round(np.linspace(0.1, 0.9, 9), 3)      # dipole height above the ground plane, fraction of T_L
H3D = (0.1, 0.5, 0.9)


def layer(sz):
    return [mp.Block(material=mp.Medium(index=N_L), center=mp.Vector3(0, 0, -0.5 * sz + 0.5 * T_L), size=mp.Vector3(mp.inf, mp.inf, T_L))]


def eff_cyl(h, res, want=False):
    sr, sz = L + DPML, T_L + DAIR + DPML
    src_pt = mp.Vector3(1.5 / res, 0, -0.5 * sz + h * T_L)          # Er at r = 0 is undefined on the Yee grid (meep #2704)
    sim = mp.Simulation(resolution=res, cell_size=mp.Vector3(sr, 0, sz), dimensions=mp.CYLINDRICAL, m=-1,
                        boundary_layers=[mp.PML(DPML, direction=mp.R), mp.PML(DPML, direction=mp.Z, side=mp.High)],   # bottom: no PML = ground plane
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.1 * FREQ), component=mp.Er, center=src_pt)], geometry=layer(sz))
    flux = sim.add_flux(FREQ, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * L, 0, 0.5 * sz - DPML), size=mp.Vector3(L, 0, 0)),
                        mp.FluxRegion(center=mp.Vector3(L, 0, 0.5 * sz - DPML - 0.5 * DAIR), size=mp.Vector3(0, 0, DAIR)))
    dft = sim.add_dft_fields([mp.Er], FREQ, 0, 1, center=mp.Vector3(0.5 * L, 0, -0.5 * DPML), size=mp.Vector3(L, 0, sz - DPML)) if want else None
    if want:
        annotated_layout(sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(11, 3.6), axis_step=1.0, unit="um",
                         title="part A, cylindrical (r, z) cell: dipole in a layer (n = 2.4) on a ground plane; x = r, y = z",
                         params_text=f"wl={WL} um, res={res}\nt = 0.7 wl/n = {T_L:.3f} um", params_xy=(3.6, 0.33), pml_xy=(6.05, -0.6),
                         decay_point=(src_pt.x, src_pt.z), decay_text_xy=(1.8, -0.45),
                         labels=[Label("layer n = 2.4 (bottom edge: PEC ground plane, no PML)", (2.5, -0.75), (1.8, -0.2), step=2, color="black"),
                                 Label("Er dipole at r = 1.5 px, height h", (src_pt.x, src_pt.z), (1.8, 0.05), step=3, color="red"),
                                 Label("numerator: flux through top + outer r (air only)", (4.0, 0.5 * sz - DPML), (3.6, -0.2), step=5, color="blue")])
    sim.run(mp.dft_ldos(FREQ, 0, 1), until_after_sources=mp.stop_when_fields_decayed(20, mp.Er, src_pt, TOL))
    p_air = float(mp.get_fluxes(flux)[0])
    p_tot = source_work(sim, 2 * np.pi * src_pt.x / res ** 2)         # CYL voxel: 2 pi r dr dz
    er = orient_rz(sim.get_dft_array(dft, mp.Er, 0), int(round(L * res))) if want else None
    sim.reset_meep()
    return p_air / p_tot, er, sz


def eff_3d(h, res):
    sxy, sz = L + 2 * DPML, T_L + DAIR + DPML
    src_pt = mp.Vector3(0, 0, -0.5 * sz + h * T_L)
    sim = mp.Simulation(resolution=res, cell_size=mp.Vector3(sxy, sxy, sz), symmetries=[mp.Mirror(mp.X, phase=-1), mp.Mirror(mp.Y)],
                        boundary_layers=[mp.PML(DPML, direction=mp.X), mp.PML(DPML, direction=mp.Y), mp.PML(DPML, direction=mp.Z, side=mp.High)],
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.1 * FREQ), component=mp.Ex, center=src_pt)], geometry=layer(sz))
    zc = 0.5 * sz - DPML - 0.5 * DAIR
    flux = sim.add_flux(FREQ, 0, 1, mp.FluxRegion(center=mp.Vector3(0, 0, 0.5 * sz - DPML), size=mp.Vector3(L, L, 0)),
                        mp.FluxRegion(center=mp.Vector3(0.5 * L, 0, zc), size=mp.Vector3(0, L, DAIR)),
                        mp.FluxRegion(center=mp.Vector3(-0.5 * L, 0, zc), size=mp.Vector3(0, L, DAIR), weight=-1.0),
                        mp.FluxRegion(center=mp.Vector3(0, 0.5 * L, zc), size=mp.Vector3(L, 0, DAIR)),
                        mp.FluxRegion(center=mp.Vector3(0, -0.5 * L, zc), size=mp.Vector3(L, 0, DAIR), weight=-1.0))
    sim.run(mp.dft_ldos(FREQ, 0, 1), until_after_sources=mp.stop_when_fields_decayed(20, mp.Ex, src_pt, TOL))
    p_air = float(mp.get_fluxes(flux)[0])
    p_tot = source_work(sim, 1 / res ** 3)                                # 3D voxel
    sim.reset_meep()
    return p_air / p_tot


t_a = time.time()
effA = {"cyl40": [], "cyl80": []}
er_map, sz_A = None, None
for h in HEIGHTS:
    effA["cyl40"].append(eff_cyl(h, 40)[0])
    e80, er, sz = eff_cyl(h, 80, want=(h == 0.5))
    effA["cyl80"].append(e80)
    if er is not None:
        er_map, sz_A = er, sz
say("A (cyl): " + "; ".join(f"h {h:.1f}: res40 {a:.4f}, res80 {b:.4f}" for h, a, b in zip(HEIGHTS, effA["cyl40"], effA["cyl80"])) + f"; {time.time() - t_a:.0f} s")
t_a3 = time.time()
eff3 = {h: eff_3d(h, 40) for h in H3D}
say("A (3D, res 40): " + "; ".join(f"h {h}: {v:.4f} (cyl40 {effA['cyl40'][list(HEIGHTS).index(h)]:.4f}, cyl80 {effA['cyl80'][list(HEIGHTS).index(h)]:.4f})" for h, v in eff3.items()) + f"; {time.time() - t_a3:.0f} s")
if MASTER:
    source_figure(FREQ, 0.1 * FREQ, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ B. off-axis dipole in the slab: the m series and when to stop
t_b = time.time()
RES_B, R_CELL, PML_B, PAD_B = 50, 20.0, 1.0, 1.0
M_MAX = 60
R_SRC = 3.5


def dipole_in_slab(rpos, m):
    sr, sz = R_CELL + PML_B, T_L + PAD_B + PML_B
    src_pt = mp.Vector3(rpos, 0, -0.5 * sz + 0.5 * T_L)
    sim = mp.Simulation(resolution=RES_B, cell_size=mp.Vector3(sr, 0, sz), dimensions=mp.CYLINDRICAL, m=m, force_complex_fields=True,
                        boundary_layers=[mp.PML(PML_B, direction=mp.R), mp.PML(PML_B, direction=mp.Z, side=mp.High)],
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=0.05 * FREQ), component=mp.Er, center=src_pt)], geometry=layer(sz))
    flux = sim.add_flux(FREQ, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * R_CELL, 0, 0.5 * sz - PML_B), size=mp.Vector3(R_CELL, 0, 0)),
                        mp.FluxRegion(center=mp.Vector3(R_CELL, 0, 0.5 * sz - PML_B - 0.5 * PAD_B), size=mp.Vector3(0, 0, PAD_B)))
    sim.run(mp.dft_ldos(FREQ, 0, 1), until_after_sources=mp.stop_when_dft_decayed(tol=1e-4))
    rad = float(mp.get_fluxes(flux)[0])
    src = source_work(sim, 2 * np.pi * rpos / RES_B ** 2)
    sim.reset_meep()
    return rad, src


r_ax = 1.5 / RES_B
rad_ax, src_ax = dipole_in_slab(r_ax, 1)
eff_axis = rad_ax / src_ax
say(f"B: dipole on the axis (m = 1, r = {r_ax:.2f}): extraction {eff_axis:.4f}")
rads, srcs = [], []
for m in range(M_MAX + 1):
    rad, src = dipole_in_slab(R_SRC, m)
    rads.append(rad); srcs.append(src)
    if m % 5 == 0:
        say(f"B: r {R_SRC}, m = {m}: radiated {rad:.4e}, source {src:.4e}; {time.time() - t_b:.0f} s")
rads, srcs = np.array(rads), np.array(srcs)
w = np.where(np.arange(M_MAX + 1) == 0, 1, 2)                                  # +-m give the same power: count m > 0 twice
running_max = np.maximum.accumulate(rads)
rel = rads / running_max
m_stop = int(next(m for m in range(1, M_MAX + 1) if rel[m] < 1e-2))             # official rule: first m > 0 below 1 % of the running max
eff_series = np.cumsum(w * rads) / np.cumsum(w * srcs)
eff_official = float(eff_series[m_stop]); eff_full = float(eff_series[-1])
rebound = float(rel[m_stop:].max())
m_rebound = int(m_stop + np.argmax(rel[m_stop:]))
say(f"B: official stop at m = {m_stop} (radiated/max {rel[m_stop]:.2e}) -> efficiency {eff_official:.4f}; after the stop the series rebounds to "
    f"{rebound:.3f} of the max at m = {m_rebound}; summed to m = {M_MAX}: efficiency {eff_full:.4f} (last term {rel[-1]:.1e}); {time.time() - t_b:.0f} s")

# ================================================================ C. cleaved-facet edge emitter: 2D cross-section + kz integral
t_c = time.time()
RES_C, CLAD, ACT, SUB, PML_C, AIR_C, SIDE = 25, 0.5, 0.3, 1.0, 0.5, 1.0, 3.0
N_SUB, N_CLAD, N_ACT = 3.2, 1.5, 2.3
DKZ, KZ_TOL, POS_C = 0.02, 0.02, 0.5
CX = PML_C + SIDE + AIR_C + PML_C
CY = PML_C + SUB + CLAD + ACT + CLAD + AIR_C + PML_C
SRC_C = mp.Vector3(-0.5 * CX + PML_C + SIDE - POS_C, -0.5 * CY + PML_C + SUB + CLAD + 0.5 * ACT)


def stack():
    x0 = -0.5 * CX + 0.5 * (PML_C + SIDE); wx = PML_C + SIDE; y = -0.5 * CY
    out = []
    for th, n in ((PML_C + SUB, N_SUB), (CLAD, N_CLAD), (ACT, N_ACT), (CLAD, N_CLAD)):
        out.append(mp.Block(material=mp.Medium(index=n), center=mp.Vector3(x0, y + 0.5 * th), size=mp.Vector3(wx, th, mp.inf))); y += th
    return out


def edge_sim(kz, fwidth=0.1 * FREQ, monitors=True):
    sim = mp.Simulation(resolution=RES_C, cell_size=mp.Vector3(CX, CY), k_point=mp.Vector3(0, 0, kz), kz_2d="real/imag",
                        sources=[mp.Source(mp.GaussianSource(FREQ, fwidth=fwidth), component=mp.Ez, center=SRC_C)], geometry=stack(),
                        boundary_layers=[mp.PML(PML_C)])
    flux = None
    if monitors:
        flux = sim.add_flux(FREQ, 0, 1,
                            mp.FluxRegion(center=mp.Vector3(0, 0.5 * CY - PML_C), size=mp.Vector3(CX - 2 * PML_C, 0)),                 # top
                            mp.FluxRegion(center=mp.Vector3(0.5 * CX - PML_C, 0), size=mp.Vector3(0, CY - 2 * PML_C)),                 # right (in front of the facet)
                            mp.FluxRegion(center=mp.Vector3(0.5 * CX - PML_C - 0.5 * AIR_C, -0.5 * CY + PML_C), size=mp.Vector3(AIR_C, 0), weight=-1.0))   # bottom of the air gap
    return sim, flux


kzs, d_kz, a_kz = [], [], []
nkz, dmax = 0, 0.0
while True:
    kz = nkz * DKZ
    sim, flux = edge_sim(kz)
    if nkz == 0:
        annotated_layout(sim, os.path.join(OUT, "02_layout_edge.png"), dpml=PML_C, figsize=(6.4, 6.0), axis_step=1.0, unit="um",
                         title="part C: cleaved facet of a laser stack (2D x-y); the stack is uniform along z",
                         params_text=f"res={RES_C}, kz step {DKZ}\nsub 3.2 / clad 1.5 / act 2.3", params_xy=(-2.4, 2.25), pml_xy=(-2.4, -2.2), decay_point=None,
                         labels=[Label("Ez dipole 0.5 um inside the facet", (SRC_C.x, SRC_C.y), (-2.4, 1.5), step=3, color="red"),
                                 Label("active layer n = 2.3 between claddings", (-1.5, SRC_C.y), (-2.4, 0.8), step=2, color="black"),
                                 Label("air flux: top + front + under the gap", (1.9, 0.6), (-0.3, 1.9), step=5, color="blue")])
    sim.run(mp.dft_ldos(FREQ, 0, 1), until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, SRC_C, 1e-6))
    dflux = source_work(sim, 1 / RES_C ** 2)            # 2D: a line current, pixel area
    aflux = float(mp.get_fluxes(flux)[0])
    sim.reset_meep()
    kzs.append(kz); d_kz.append(dflux); a_kz.append(aflux)
    nkz += 1
    if dflux > dmax:
        dmax = dflux
    elif dflux / dmax < KZ_TOL:
        break
kzs, d_kz, a_kz = map(np.array, (kzs, d_kz, a_kz))
eff_edge = float((a_kz[0] + 2 * a_kz[1:].sum()) / (d_kz[0] + 2 * d_kz[1:].sum()))
eff_kz0 = float(a_kz[0] / d_kz[0])
kz_cut = N_ACT * FREQ
say(f"C: {len(kzs)} kz points up to {kzs[-1]:.2f} (tail {d_kz[-1] / dmax:.4f}); extraction {100 * eff_edge:.3f} % (kz = 0 alone: {100 * eff_kz0:.2f} %); {time.time() - t_c:.0f} s")

# GIF: kz = 0, short pulse, monitor-free
sim_g, _ = edge_sim(0.0, fwidth=0.4 * FREQ, monitors=False)
sim_g.init_sim()
vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(CX - 2 * PML_C, CY - 2 * PML_C))
eps_g = sim_g.get_array(vol=vol, component=mp.Dielectric)
t0 = 5 / (0.4 * FREQ)
frames, times = record_frames(sim_g, vol, mp.Ez, t_start=t0 - 2 / (0.4 * FREQ), t_end=t0 + 9.0, n_frames=60)
sim_g.reset_meep()

# ================================================================ figures
if MASTER:
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3), gridspec_kw={"width_ratios": [1.4, 1]})
    ax[0].plot(HEIGHTS, effA["cyl80"], "o-", color="tab:blue", label="cylindrical, res 80 (official)")
    ax[0].plot(HEIGHTS, effA["cyl40"], "s--", color="tab:cyan", label="cylindrical, res 40")
    ax[0].plot(list(H3D), [eff3[h] for h in H3D], "D", color="tab:red", ms=8, label="3D Cartesian, res 40")
    ax[0].set_xlabel("dipole height above the ground plane / layer thickness"); ax[0].set_ylabel("extraction efficiency into air")
    ax[0].set_title("dipole in a 0.29 um layer (n = 2.4) on a mirror", fontsize=9); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
    ext = [0, L, -0.5 * sz_A, 0.5 * sz_A - DPML]
    ax[1].imshow(np.log10(np.abs(er_map) + 1e-12).T, extent=ext, origin="lower", cmap="inferno", aspect="auto")
    ax[1].add_patch(plt.Rectangle((0, -0.5 * sz_A), L, T_L, fill=False, color="w", lw=1))
    ax[1].set_xlabel("r [um]"); ax[1].set_ylabel("z [um]"); ax[1].set_title("log10 |Er|, h = 0.5 (res 80): much of the light stays in the layer", fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "03_height.png"), dpi=150); plt.close(fig)

    ms = np.arange(M_MAX + 1)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    ax[0].semilogy(ms, rel, "o-", ms=3, color="tab:blue", label="radiated(m) / running max")
    ax[0].axhline(1e-2, color="crimson", ls="--", lw=1, label="official stop: 1 %")
    ax[0].axvline(m_stop, color="crimson", ls=":", lw=1); ax[0].text(m_stop + 0.5, 2e-1, f"stop at m = {m_stop}", color="crimson", fontsize=8)
    ax[0].plot(m_rebound, rebound, "*", color="tab:orange", ms=12, label=f"rebound {rebound:.2f} at m = {m_rebound}")
    ax[0].axvline(2 * np.pi * N_L * R_SRC, color="gray", ls="-.", lw=1); ax[0].text(2 * np.pi * N_L * R_SRC - 14, 2e-4, "m = 2 pi n r (guided in the slab)", fontsize=8, color="gray")
    ax[0].set_xlabel("azimuthal order m"); ax[0].set_ylabel("radiated power of the m term (relative)"); ax[0].set_title(f"dipole at r = {R_SRC} um in the slab", fontsize=9); ax[0].grid(alpha=0.3, which="both"); ax[0].legend(fontsize=7)
    ax[1].plot(ms, eff_series, "-", color="tab:green"); ax[1].axvline(m_stop, color="crimson", ls=":", lw=1)
    ax[1].axhline(eff_axis, color="tab:purple", ls="--", lw=1, label=f"dipole on the axis: {eff_axis:.3f}")
    ax[1].plot(m_stop, eff_official, "o", color="crimson", label=f"official stop: {eff_official:.3f}")
    ax[1].plot(M_MAX, eff_full, "o", color="tab:green", label=f"summed to m = {M_MAX}: {eff_full:.3f}")
    ax[1].set_xlabel("m included up to"); ax[1].set_ylabel("extraction efficiency"); ax[1].set_title("the efficiency depends on where the series is cut", fontsize=9); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "04_m_series.png"), dpi=150); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    ax[0].plot(kzs, d_kz / d_kz.max(), "o-", ms=3, color="tab:gray", label="total (dft_ldos)")
    ax[0].plot(kzs, a_kz / d_kz.max(), "o-", ms=3, color="tab:blue", label="into air")
    for kc, lab in ((FREQ, "kz = k0 (air light line)"), (N_CLAD * FREQ, "1.5 k0"), (N_ACT * FREQ, "2.3 k0")):
        ax[0].axvline(kc, color="k", ls=":", lw=0.8); ax[0].text(kc + 0.02, 0.9, lab, fontsize=7, rotation=90, va="top")
    ax[0].set_xlabel("kz [2 pi / um]"); ax[0].set_ylabel("power per kz (relative)"); ax[0].set_title(f"{len(kzs)} 2D runs, one per kz", fontsize=9); ax[0].grid(alpha=0.3); ax[0].legend(fontsize=8)
    cum = (np.cumsum(np.where(np.arange(len(kzs)) == 0, 1, 2) * a_kz)) / (np.cumsum(np.where(np.arange(len(kzs)) == 0, 1, 2) * d_kz))
    ax[1].plot(kzs, 100 * cum, "-", color="tab:green"); ax[1].axhline(100 * eff_edge, color="tab:green", ls="--", lw=1)
    ax[1].axhline(100 * eff_kz0, color="tab:orange", ls=":", lw=1.2, label=f"kz = 0 alone (2D line source): {100 * eff_kz0:.1f} %")
    ax[1].set_xlabel("kz included up to"); ax[1].set_ylabel("extraction efficiency [%]"); ax[1].set_title(f"kz integral: {100 * eff_edge:.2f} % into air", fontsize=9); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "05_kz.png"), dpi=150); plt.close(fig)

    animate_fields(frames, times, [-(0.5 * CX - PML_C), 0.5 * CX - PML_C, -(0.5 * CY - PML_C), 0.5 * CY - PML_C], os.path.join(OUT, "07_anim_edge.gif"),
                   eps=eps_g, figsize=(5.6, 5.0), dpi=70, clip_percentile=99.0, points=[(SRC_C.x, SRC_C.y, "red", "dipole")],
                   title="edge emitter, kz = 0", legend_loc="lower left")
    with open(os.path.join(OUT, "result.json"), "w") as f_:
        json.dump({"A": {"heights": HEIGHTS.tolist(), "cyl40": effA["cyl40"], "cyl80": effA["cyl80"], "3d40": {str(k): v for k, v in eff3.items()}},
                   "B": {"r": R_SRC, "eff_axis": eff_axis, "m_stop": m_stop, "eff_official": eff_official, "eff_full": eff_full, "rebound": rebound,
                         "m_rebound": m_rebound, "rel": rel.tolist(), "eff_series": eff_series.tolist()},
                   "C": {"n_kz": len(kzs), "kz_max": float(kzs[-1]), "tail": float(d_kz[-1] / dmax), "eff": eff_edge, "eff_kz0": eff_kz0},
                   "wall_s_total": time.time() - t_all, "np": mp.count_processors(), "meep": mp.__version__}, f_, indent=2)
say(f"total {time.time() - t_all:.0f} s on {mp.count_processors()} process(es)")
{% endhighlight %}
</details>

Unlike the excerpts in §4, the full code includes the height sweep, comparison of m-series stopping rules, kz integration, a GIF, and result.json output. Collective calls execute on every MPI rank; figures are saved only on the master. Both layouts were drawn with `code/extraction_layouts.py`, which constructs the same cells without time stepping. Full code and helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**Execution output (run on 2026-10-23, mpirun -np 4)**:
```
A (cyl): h 0.1: res40 0.5494, res80 0.5230; h 0.2: res40 0.5214, res80 0.5038; h 0.3: res40 0.4735, res80 0.4645; h 0.4: res40 0.4014, res80 0.4050; h 0.5: res40 0.3018, res80 0.3232; h 0.6: res40 0.1805, res80 0.2213; h 0.7: res40 0.0891, res80 0.1259; h 0.8: res40 0.1095, res80 0.0915; h 0.9: res40 0.2681, res80 0.1745; 253 s
A (3D, res 40): h 0.1: 0.5475 (cyl40 0.5494, cyl80 0.5230); h 0.5: 0.3505 (cyl40 0.3018, cyl80 0.3232); h 0.9: 0.2607 (cyl40 0.2681, cyl80 0.1745); 476 s
B: dipole on the axis (m = 1, r = 0.03): extraction 0.3636
B: r 3.5, m = 0: radiated 8.3457e+03, source 9.8732e+03
B: r 3.5, m = 20: radiated 1.8285e+03, source 5.9457e+03
B: r 3.5, m = 40: radiated 4.1701e+03, source 3.9968e+04
B: r 3.5, m = 60: radiated 2.4012e-04, source 3.0755e-02
B: official stop at m = 32 (radiated/max 5.48e-03) -> efficiency 0.6323; after the stop the series rebounds to 0.382 of the max at m = 41; summed to m = 60: efficiency 0.3616 (last term 2.0e-08); 3502 s
C: 76 kz points up to 1.50 (tail 0.0189); extraction 22.375 % (kz = 0 alone: 32.91 %); 359 s
total 4604 s on 4 process(es)
```

**Reproduction environment**: meep 1.33.0 (MPI) · Python 3.11 · `conda install -c conda-forge pymeep=*=mpi_mpich_*` · command `mpirun -np 4 python extraction_efficiency.py` (about 77 min (mpirun -np 4; B alone 58 min))

<h2 id="check">Check your understanding</h2>

1. Why does extraction efficiency need $\Delta V$ when chapter 11’s Purcell factor did not?
2. Explain why the m series of a dipole 3.5 µm off-axis becomes small near m = 30 and then grows again, using guided light and $m\approx2\pi n r$.
3. A real OLED emitting layer contains thousands of molecules with different positions, orientations, and uncorrelated phases. How many runs would summing the power of individual dipoles require? Can this be reduced to only a few runs? (Chapter 15)

## 9. Further reading

- [LDOS tutorial: LED extraction efficiency](https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/#extraction-efficiency-of-a-light-emitting-diode-led) · [Nonaxisymmetric dipole sources](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/#nonaxisymmetric-dipole-sources) · [`dft_ldos`](https://meep.readthedocs.io/en/latest/Python_User_Interface/#ldos-spectra) · [kz_2d](https://meep.readthedocs.io/en/latest/Python_User_Interface/#the-simulation-class)
- Scripts: [extraction_eff_ldos.py](https://github.com/NanoComp/meep/blob/master/python/examples/extraction_eff_ldos.py) · [point_dipole_cyl.py](https://github.com/NanoComp/meep/blob/master/python/examples/point_dipole_cyl.py) · [edge_emitter_2D.py](https://github.com/NanoComp/meep/blob/master/python/examples/edge_emitter_2D.py) · [disc_extraction_efficiency.py](https://github.com/NanoComp/meep/blob/master/python/examples/disc_extraction_efficiency.py)
- Previous: [13 · Computing 3D with rotational symmetry]({{ site.baseurl }}/en/cylindrical-dipole/) · LDOS: [11 · A point source between two mirrors]({{ site.baseurl }}/en/cavity-ldos/) · Next: 15 · When there are thousands of point sources
