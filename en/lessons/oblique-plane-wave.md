---
layout: lesson
permalink: /en/oblique-plane-wave/
lesson_title: "How do we launch a plane wave in the desired direction?"
lesson_summary: "Match an EigenModeSource wavevector to the Bloch boundary and launch plane waves at 0°, 40°, 120° and 210°. Check their direction from complex-field phase before measuring angle-dependent reflection in the next chapter."
lesson_goals:
  - "Explain how a plane wave joined through periodic boundaries differs from a finite line source."
  - "Distinguish eig_kpoint from k_point and specify an angle measured from the x axis."
  - "Check direction and wavevector magnitude from complex Ez, and explain the limitations of a windowed FFT diagnostic."
lesson_prerequisites: "Chapter 01: point and line sources · Chapter 02: PML · Chapter 03: reference runs · Chapter 04: EigenModeSource"
date: 2026-11-10
title: "Meep Example 17 · A plane wave in the desired direction — EigenModeSource, Bloch phase, and wavevector checks"
title_en: "Meep Example 17 · A plane wave in the desired direction — EigenModeSource, Bloch phase, and wavevector checks"
lang: en
translation_key: oblique-plane-wave
series: meep-examples
part: 17
level: beginner
runtime: "Archived res-50 runs: about 1–3 s per angle (WSL, 4 MPI processes); single-core runtime was not separately measured"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Eigenmode_Source/#planewaves-in-homogeneous-media"
tags: [meep, fdtd, plane-wave, eigenmode-source, bloch, oblique-incidence]
image: /assets/meep/17/01_planewave.png
excerpt: "Launch plane waves at four angles in a homogeneous n = 1.5 medium and inspect their phase gradients and spatial Fourier spectra. Verify the illumination before adding an interface in chapter 18."
---
<h2 id="observe">1. Observe: rotate the wavefront, keep the source line vertical</h2>

The short line source in chapter 01 produced curved wavefronts at its ends. Here a source spanning the entire y cell and a Bloch boundary produce a plane wave. **The source line stays vertical while the propagation direction changes.** We check the illumination before adding an object.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/17/01_planewave.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/17/01_planewave.png' | relative_url }}" alt="Actual Meep real Ez in a uniform index-1.5 medium, for requested angles 0, 40, 120 and 210 degrees. The last two waves propagate to the left." loading="eager"></a>
<figcaption>Actual Re Ez from Meep runs saved on 2026-11-09. Red and blue show electric-field sign, not optical intensity. The vertical source at x = 0 launches toward +x at 0°/40° and toward −x at 120°/210°. Each panel uses its own color range, so amplitudes cannot be compared between panels. The original Korean annotations give the requested angle, fitted angle and FFT diagnostic; the numerical table below translates these values.</figcaption>
</figure>

<details markdown="1">
<summary>Calculation summary and verification scope</summary>

- **What was calculated?** 2D Ez, homogeneous n = 1.5, vacuum wavelength 1 µm, a 14 × 10 µm cell and 2 µm PML along x. The y boundary is Bloch periodic, as specified by `k_point`.
- **What was measured?** Across 0°, 40°, 120° and 210°, the maximum phase-fit angle error is 0.0614° and the maximum wavevector-magnitude error is 0.164%. The largest opposite-window/peak-window spatial FFT ratio is 0.002884.
- **What does that establish?** Only these four angles in this homogeneous, lossless medium were checked. The FFT ratio is not a reflected-power coefficient. The same source project contains failed checks for rotated waveguides and grazing incidence; those extensions are outside the successful scope here.
- **How long?** The original four-process MPI logs report about 1–3 s per angle. The download also runs on one core, but that runtime was not measured. No electromagnetic fields were recomputed while preparing this lesson.

</details>

<h2 id="predict">2. Predict: which way does a 120° wave travel?</h2>

<fieldset class="prediction">
<legend>Angles run counterclockwise from +x. What changes when 40° becomes 120°?</legend>
<label><input type="radio" name="oblique-plane-wave-prediction" value="left"> The x component of propagation changes from rightward to leftward.</label>
<label><input type="radio" name="oblique-plane-wave-prediction" value="right"> A vertical source always launches to the right.</label>
<label><input type="radio" name="oblique-plane-wave-prediction" value="rotate-source"> The angle cannot change unless the source line rotates too.</label>
</fieldset>

<details markdown="1">
<summary>Reasoning and acceptance criteria</summary>

The propagation vector is perpendicular to a constant-phase wavefront. Since $k_x=nf\cos\theta$, it is positive at 40° and negative at 120°. An `EigenModeSource` uses the mode's equivalent electric and magnetic currents to select a propagation direction.

| Check | Prediction before the run | Acceptance criterion for this dataset |
|---|---|---|
| Direction | +x at 0°/40°; −x at 120°/210° | Phase-angle error < 0.5° |
| Wavevector magnitude | n f = 1.5 cycles/µm | Relative error < 1% |
| Opposite spatial component | Smaller than the main peak | Archived FFT window ratio < 0.01 |

210° and −150° describe the same direction. Wrap the angular difference to a 360° interval before reporting its error. These thresholds belong to this experiment; they are not an accuracy guarantee for every structure.

</details>

<h2 id="understand">3. Understand: match the mode direction and boundary phase</h2>

{% include chapter-illustration.html %}

Meep expresses `k_point` in **cycles per unit length**, rather than radians per unit length. In a homogeneous medium,

$$
E_z(\mathbf r,t)\propto \exp\left[2\pi i(\mathbf k\cdot\mathbf r-ft)\right],\qquad
\mathbf k=nf(\cos\theta,\sin\theta),\qquad |\mathbf k|=nf.
$$

With the length unit set to 1 µm, we use f = 1 and n = 1.5. At 40° the target vector is approximately (1.14907, 0.96418) cycles/µm. The source's `eig_kpoint` selects the **injected eigenmode direction**; the simulation's `k_point` sets the **phase acquired across the cell boundary**. We give them the same vector. Across the y boundary,

$$
E_z(x,y+L_y)=e^{2\pi i k_yL_y}E_z(x,y).
$$

This joins the wavefront continuously between copies of the cell. PML is applied along x only. There is no y PML: this is a plane wave represented through Bloch periodicity in a uniform medium, rather than a finite beam.

| Setting | Purpose | Consequence of a wrong setting |
|---|---|---|
| `size=Vector3(0, 10, 0)` | A vertical source covering the y cell | A short source adds endpoint diffraction |
| `eig_kpoint=k_point` | Select the requested modal wavevector | Source and boundary phases disagree |
| `direction=mp.NO_DIRECTION` | Specify the oblique eigenmode search direction | Confusion with an automatic axial search |
| `eig_parity=mp.ODD_Z` | Select 2D Ez polarization | A different polarization/mode |
| `eig_vol` y width `1/resolution` | A small eigenmode domain in a uniform medium | Confusing the mode domain with the full source extent |
| `EVEN_Y` and `Mirror(Y)` only at 0° | Use mirror symmetry for horizontal propagation | Imposing a symmetry incompatible with an oblique wave |

### Measure phase instead of judging stripe tilt

Multiplying adjacent complex fields removes their common temporal phase and leaves their spatial phase increment:

$$
k_x\approx \frac{\arg\sum_{i,j}E_{i+1,j}E^*_{i,j}}{2\pi\Delta x},\quad
k_y\approx \frac{\arg\sum_{i,j}E_{i,j+1}E^*_{i,j}}{2\pi\Delta y},\quad
\theta_{\rm fit}=\operatorname{atan2}(k_y,k_x).
$$

The archived analysis uses the central 6 × 6 µm region. Neighboring phase steps must remain below π to avoid aliasing. This measures direction when the field is dominated by one plane wave; it does not reduce a mixture of reflected waves or several modes to a physically unique wavevector.

<h2 id="run">4. Run: check the illumination in a uniform medium first</h2>

[Download the complete Python script]({{ '/code/oblique_plane_wave.py' | relative_url }}) · [Execution and source record]({{ '/assets/meep/17/provenance.json' | relative_url }}) · [Original 40° execution log]({{ '/assets/meep/17/pw_a40.log' | relative_url }})

Use an existing Meep environment. Meep and NumPy are required; Matplotlib is used only with `--plot`. The script needs no project helper modules or external dataset paths.

```bash
python code/oblique_plane_wave.py --help
python code/oblique_plane_wave.py --angle 40 --tag pw_a40 --out work/plane-wave-40 --plot
python code/oblique_plane_wave.py --angle 120 --tag pw_a120 --out work/plane-wave-120 --plot
```

### Read the code in seven steps

1. **Units and parameters**: fix f = 1, n = 1.5, resolution 50 px/µm and end time 23.56.
2. **Geometry and material**: `default_material=mp.Medium(index=1.5)` fills the cell. There is no object or interface.
3. **Source**: place a continuous-wave `EigenModeSource` at x = 0, spanning 10 µm in y.
4. **Boundaries**: use 2 µm x PML and a Bloch y boundary in a 14 × 10 µm cell.
5. **Measurement**: save complex Ez over the central 10 × 10 µm region, excluding PML; analyze phase in its central 6 × 6 µm.
6. **Stopping**: run to the fixed time used by the original example. This is not a decay criterion or a time-convergence study.
7. **Postprocessing**: write angle, wavevector and spatial FFT diagnostics to JSON, and fields to NPZ. `--plot` adds a real-Ez PNG.

```python
k_point = mp.Vector3(1.5, 0, 0).rotate(mp.Vector3(0, 0, 1), angle)
source = mp.EigenModeSource(
    src=mp.ContinuousSource(1.0), center=mp.Vector3(),
    size=mp.Vector3(0, 10, 0), direction=mp.NO_DIRECTION,
    eig_kpoint=k_point, eig_band=1, eig_parity=mp.ODD_Z,
    eig_vol=mp.Volume(center=mp.Vector3(), size=mp.Vector3(0, 1 / resolution, 0)))
```

This excerpt shows the oblique-source settings. The executable download also handles 0° symmetry, the simulation, analysis and outputs. Propagation parallel to the source line, such as 90° or 270°, is outside the four-angle verification.

<h2 id="interpret">5. Interpret: angle, magnitude and FFT are separate checks</h2>

These values come from the original JSON files used for the figure. They are not estimates from a new run or a conceptual animation.

| Requested angle | Phase-fit angle | Angular error | Measured wavevector magnitude | FFT window ratio |
|---|---|---|---|---|
| 0° | Approximately 0.00000° | < 0.000001° | 1.501556 | 2.884 × 10⁻³ |
| 40° | 40.06136° | 0.06136° | 1.498089 | 4.603 × 10⁻¹⁰ |
| 120° | 120.02029° | 0.02029° | 1.500307 | 2.035 × 10⁻¹⁰ |
| 210° | −149.94588° | 0.05412° | 1.497551 | 2.133 × 10⁻⁸ |

The largest relative magnitude error is $|1.497551-1.5|/1.5=0.001633$. All four waves follow the expected direction and pass the stored angle/magnitude criteria. Using the FFT peak alone would give 40.60° at 40° and 122.01° at 120°: a finite 6 µm window has coarse spatial-frequency bins. We therefore use the phase gradient for the precise direction comparison.

**Do not read the FFT window ratio as reflectance.** It compares 7 × 7-bin windows near the peak and the opposite side of a Hann-windowed spatial FFT. The archive's mirrored-index convention is retained, so it is not even a power integral centered exactly on −k. The finite window, source-region field, settling time and crop position can affect it, and it has no Poynting-flux normalization. In particular, 0.002884 at 0° does not mean an object reflects 0.2884% of the incident power. No object is present.

### What passed, and what remains untested

| Item | Supported by this lesson | Needs an additional check |
|---|---|---|
| Direction | Maximum 0.0614° error at these four angles | All angles and frequencies |
| Wavevector magnitude | Within 0.164% of n f = 1.5 | Independent resolution/time convergence |
| Directionality | Small opposite-window spatial FFT component | Quantitative reflected flux or modal power |
| Real structures | Illumination in a homogeneous medium | Interfaces, finite beams, rotated guides and grazing incidence |

The full source project's verdict is `refuted`. Its plane-wave checks C7/C7b/C8 passed, but comparisons with documented rotated-guide values and grazing-incidence tests included failures and monitor-placement problems. For example, horizontal diagnostic-plane ratios at grazing incidence were 0.888 at 80° and 0.307 at 84°, outside the registered thresholds. We do not turn the successful four-angle plane-wave subset into a general claim about guides. The [complete verdict JSON]({{ '/assets/meep/17/aggregate_verdict.json' | relative_url }}) retains the failed checks.

<h2 id="check">6. Check: what if the direction is right but the magnitude is wrong?</h2>

<details markdown="1">
<summary>Question 1 · Do 40° stripes complete the source verification?</summary>

No. `atan2` checks direction only. The angle can be right even if n or f is wrong. Check that the magnitude equals n f and that `eig_kpoint` matches `k_point`. Confusing radians with cycles introduces a factor of 2π.

</details>

<details markdown="1">
<summary>Question 2 · Does adding y PML give the same plane wave in a more open cell?</summary>

It changes the boundary conditions. Here the Bloch phase joins the upper and lower cells. A finite beam with PML on all sides needs its own width, source profile and injection settings, plus an endpoint-diffraction check. Compare the finite beams in [Beam Lab]({{ '/en/optical-beams/' | relative_url }}).

</details>

### Change one thing

First change the 40° resolution from 50 to 100 and record the angle and magnitude errors. Then return the resolution to 50 and change only `--until 47.12`. Keeping those changes separate distinguishes spatial-grid effects from settling time. Record these new experiments separately from the archived values above.

Now the incident direction is checked. [18 · Angle-dependent interface reflection]({{ '/en/angular-reflectance/' | relative_url }}) adds an interface and measures R/T with a reference run. This also prepares an angular extension to the normal-incidence setup in [06 · Grating diffraction]({{ '/en/binary-grating/' | relative_url }}).

<h2 id="reference">7. References and reproduction record</h2>

- Official explanation: [Meep · Eigenmode Source — Planewaves in Homogeneous Media](https://meep.readthedocs.io/en/latest/Python_Tutorials/Eigenmode_Source/#planewaves-in-homogeneous-media).
- Pinned source: [NanoComp/meep · oblique-planewave.py, commit f7811d4](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/oblique-planewave.py). The source, medium and cell settings follow this example.
- Added here: explanation of the archived four-angle phase/FFT results, CLI arguments, independent output directories, optional PNG output, and Korean/English learning activities. Upstream Meep licensing continues to apply to adapted code.
- Data: [0° JSON]({{ '/assets/meep/17/pw_a0.json' | relative_url }}), [40° JSON]({{ '/assets/meep/17/pw_a40.json' | relative_url }}), [120° JSON]({{ '/assets/meep/17/pw_a120.json' | relative_url }}), [210° JSON]({{ '/assets/meep/17/pw_a210.json' | relative_url }}), [SHA-256 and source inventory]({{ '/assets/meep/17/provenance.json' | relative_url }}).
- Earlier concepts: [01 · Point and line sources]({{ '/en/point-line-source/' | relative_url }}), [04 · Waveguide eigenmode sources]({{ '/en/straight-waveguide/' | relative_url }}). Next measurement: [18 · Angular reflection]({{ '/en/angular-reflectance/' | relative_url }}).

<details markdown="1">
<summary>Expand the complete executable code</summary>

{% highlight python %}
"""Launch and measure the official homogeneous-medium oblique plane wave.

Adapted from NanoComp/meep python/examples/oblique-planewave.py at
f7811d4157ea22f19d4ca76bc41c71b6e055763e and the project's pw_run.py.
Upstream tutorial: https://meep.readthedocs.io/en/latest/Python_Tutorials/Eigenmode_Source/#planewaves-in-homogeneous-media
Keep the upstream Meep license; see assets/meep/17/provenance.json.
The published figures use the archived 2026-11-09 runs, not a new execution.
"""

import argparse
import json
import math
from pathlib import Path
import time

import numpy as np


def measure_field(field, resolution):
    """Preserve the archived phase-fit and windowed-FFT diagnostics."""
    dx = 1 / resolution
    crop = slice(int(2 * resolution), int(8 * resolution))
    sub = field[crop, crop]
    result = {"complex": bool(np.iscomplexobj(field))}
    if np.iscomplexobj(field):
        kx = np.angle(np.sum(sub[1:, :] * np.conj(sub[:-1, :]))) / (2 * math.pi * dx)
        ky = np.angle(np.sum(sub[:, 1:] * np.conj(sub[:, :-1]))) / (2 * math.pi * dx)
        result.update(kx=float(kx), ky=float(ky), k_mag=float(math.hypot(kx, ky)),
                      angle_fit=float(math.degrees(math.atan2(ky, kx))), k_expected=1.5)
    window = np.hanning(sub.shape[0])[:, None] * np.hanning(sub.shape[1])[None, :]
    power = np.abs(np.fft.fftshift(np.fft.fft2(sub * window))) ** 2
    fx = np.fft.fftshift(np.fft.fftfreq(sub.shape[0], dx))
    fy = np.fft.fftshift(np.fft.fftfreq(sub.shape[1], dx))
    i, j = np.unravel_index(np.argmax(power), power.shape)

    def box(ii, jj, radius=3):
        return power[max(ii - radius, 0):ii + radius + 1,
                     max(jj - radius, 0):jj + radius + 1].sum()

    # Retain the archive's mirrored FFT-index convention for comparability.
    # This finite-window spectral ratio is NOT reflected Poynting power.
    ib, jb = power.shape[0] - 1 - i, power.shape[1] - 1 - j
    result.update(fft_peak_k=[float(fx[i]), float(fy[j])],
                  fft_peak_angle=float(math.degrees(math.atan2(fy[j], fx[i]))),
                  backward_fraction_fft=float(box(ib, jb) / box(i, j)))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--angle", type=float, default=40, help="CCW degrees from +x")
    parser.add_argument("--resolution", type=float, default=50, help="pixels per micrometre")
    parser.add_argument("--until", type=float, default=23.56, help="Meep time units")
    parser.add_argument("--tag", default="pw_a40", help="output filename stem")
    parser.add_argument("--out", type=Path, default=Path("oblique-plane-wave-output"))
    parser.add_argument("--plot", action="store_true", help="also save a real-Ez PNG with matplotlib")
    args = parser.parse_args()
    if args.resolution < 4 or args.until <= 0:
        parser.error("resolution must be >= 4 and until must be positive")
    if not args.tag or Path(args.tag).name != args.tag:
        parser.error("tag must be a filename stem")
    import meep as mp

    start = time.time()
    angle = math.radians(args.angle % 360)
    k_point = mp.Vector3(1.5, 0, 0).rotate(mp.Vector3(0, 0, 1), angle)
    if angle == 0:
        direction, parity, mirrors, eig_vol = mp.AUTOMATIC, mp.EVEN_Y + mp.ODD_Z, [mp.Mirror(mp.Y)], None
    else:
        direction, parity, mirrors = mp.NO_DIRECTION, mp.ODD_Z, []
        eig_vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(0, 1 / args.resolution, 0))
    source = mp.EigenModeSource(
        src=mp.ContinuousSource(1.0), center=mp.Vector3(), size=mp.Vector3(0, 10, 0),
        direction=direction, eig_kpoint=k_point, eig_band=1, eig_parity=parity, eig_vol=eig_vol)
    sim = mp.Simulation(
        cell_size=mp.Vector3(14, 10, 0), resolution=args.resolution,
        boundary_layers=[mp.PML(2, direction=mp.X)], sources=[source],
        k_point=k_point, default_material=mp.Medium(index=1.5), symmetries=mirrors)
    sim.run(until=args.until)
    field = np.asarray(sim.get_array(component=mp.Ez, center=mp.Vector3(), size=mp.Vector3(10, 10)))
    result = dict(res=args.resolution, angle=args.angle, until=args.until,
                  steps=sim.timestep(), wall=time.time() - start, **measure_field(field, args.resolution))
    if mp.am_master():
        args.out.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.out / f"{args.tag}.npz", Ez=field, extent=np.array([-5, 5, -5, 5]))
        (args.out / f"{args.tag}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        if args.plot:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            limit = np.percentile(np.abs(field.real), 99.5)
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.imshow(field.real.T, origin="lower", extent=(-5, 5, -5, 5),
                      cmap="RdBu_r", vmin=-limit, vmax=limit)
            ax.set(xlabel="x (µm)", ylabel="y (µm)", title=f"Re Ez, requested angle {args.angle:g}°")
            fig.savefig(args.out / f"{args.tag}.png", dpi=150, bbox_inches="tight")
            plt.close(fig)
        print("RESULT " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
{% endhighlight %}

</details>
