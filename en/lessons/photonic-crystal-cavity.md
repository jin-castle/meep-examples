---
layout: lesson
permalink: /en/photonic-crystal-cavity/
lesson_title: "How can holes in a waveguide trap light?"
lesson_summary: "Introduce a defect into a periodic waveguide's partial band gap. Compare a narrow transmission peak with Harminv's Q, then inspect the effects of hole count, resolution and stopping criteria."
lesson_goals:
  - "Connect the partial guided-mode band gap to a localized defect resonance."
  - "Normalize R, T and radiation by a reference waveguide and inspect the resonant peak."
  - "Separate frequency sampling, stopping-time and grid checks, and explain the limits of a Q plateau."
lesson_prerequisites: "Chapter 03: reference runs · Chapter 04: guided modes · Chapter 12: Harminv and Q · Chapter 17: Bloch phase"
date: 2026-11-11
title: "Meep Example 26 · Trapping light in a defect — waveguide bands, resonant transmission, and Q checks"
title_en: "Meep Example 26 · Trapping light in a defect — waveguide bands, resonant transmission, and Q checks"
lang: en
translation_key: photonic-crystal-cavity
series: meep-examples
part: 26
level: intermediate
runtime: "Archived 2-process MPI: N-3 Harminv about 1–2 s; transmission about 19 s at decay 1e−5; other modes depend on settings"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Resonant_Modes_and_Transmission_in_a_Waveguide_Cavity/"
tags: [meep, fdtd, photonic-crystal, cavity, harminv, band-gap, transmission]
image: /assets/meep/26/results.png
excerpt: "Compute a defect mode and narrow transmission peak in a perforated waveguide. Harminv Q 372.4 and linewidth Q 370.4 agree for N 3, while the larger Q plateau in the documentation remains unreproduced."
---
<h2 id="observe">1. Observe: a narrow path inside a blocked frequency range</h2>

If we add regularly spaced holes to chapter 04's straight waveguide, will every frequency still pass? Widen one central spacing and a **localized defect mode** appears inside a range where the periodic guide blocks propagation. Light near its resonance can couple through to the other side.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/26/results.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/26/results.png' | relative_url }}" alt="Actual calculated periodic waveguide bands, N-3 defect transmission peak, Q versus hole count and resonance versus grid resolution" loading="eager"></a>
<figcaption>Archived Meep results: selected-symmetry periodic bands at upper left, N-3 transmission at upper right, and Q/grid checks below. N counts holes on one side, so N = 3 means six holes in total. The shaded range is this model's partial guided-mode gap, not a complete 3D gap for every polarization and direction. Original plot labels are Korean; numerical values are translated below.</figcaption>
</figure>

<details markdown="1">
<summary>Key numbers and verification scope</summary>

For N = 3, res 20, Harminv gives f = 0.234454153 c/a and Q = 372.408. A Lorentz fit to a dense transmission scan gives f₀ = 0.234450094 and Q = 370.395, a 0.541% Q difference. Tightening the stopping threshold from decay 1e−3 to 1e−5 improves R + T + S from 0.8806–1.1479 to 0.99585–1.00799. However, N-14 Q ≈ 6082 at res 20 and ≈ 6402 at res 80 do not reproduce the documentation's roughly 8750. That discrepancy remains unresolved. This lesson reuses archived fields, JSON and logs; it performs no new electromagnetic solves for publication.

</details>

<h2 id="predict">2. Predict: will more holes increase Q without limit?</h2>

<fieldset class="prediction">
<legend>What do you expect as the number N of holes on each side increases?</legend>
<label><input type="radio" name="photonic-crystal-cavity-prediction" value="radiation"> Q growth may level off if radiation into air remains after port leakage decreases.</label>
<label><input type="radio" name="photonic-crystal-cavity-prediction" value="infinite"> A periodic structure must make Q increase without limit.</label>
<label><input type="radio" name="photonic-crystal-cavity-prediction" value="same"> Hole count cannot affect the resonance lifetime.</label>
</fieldset>

<details markdown="1">
<summary>Reasoning</summary>

Confinement along the guide does not eliminate radiation into the surrounding air. Independent loss rates can be written $1/Q=1/Q_{\rm port}+1/Q_{\rm rad}$. A slowing increase with N is consistent with this picture, but finite-grid, PML and Harminv checks remain necessary. A numerical plateau alone does not establish the physical radiation-limited Q.

</details>

<h2 id="understand">3. Understand: band gap → defect mode → resonant transmission</h2>

{% include chapter-illustration.html %}

Use the period a as the unit of length. The guide has ε = 13, width 1.2a, and air-hole radius 0.36a. The nearest hole centers are x = ±0.7a, followed by ±1.7a and ±2.7a. Thus one central spacing is widened to d = 1.4a. **N = 3 counts three holes per side**, six in total.

1. **Periodic cell**: a cell of length a and an x Bloch phase yield the guided bands. At k = 0.5/a the selected Hz symmetry gives two boundary frequencies, 0.199902 and 0.304970 c/a.
2. **Defect resonance**: widen the central spacing between finite hole arrays. The in-gap mode concentrates there and leaks through ports and into air.
3. **Transmission**: launch an Ey line-source pulse from the left and normalize by a guide without holes. A narrow transmission peak encodes the resonance lifetime.

$$
Q=\frac{f_0}{\Delta f_{\rm FWHM}},\qquad
T(f)\approx \frac{A}{1+4Q^2[(f-f_0)/f_0]^2}+C.
$$

This Lorentz profile models the archived isolated peak. An asymmetric background or multiple resonances may require a different model. Harminv estimates the same mode's frequency and Q from Hz decay after the source ends.

| Calculation mode | Cell and boundaries | Source and measurement |
|---|---|---|
| `bands` | 1a × 12a; 1a y PML; x Bloch | Hz point source; 21 k points; 300 Harminv time units per point |
| `harminv` | Length 2(N+3)a + 0.4a; height 6a; 1a PML | Central Hz point source; x/y mirrors; 400 after source |
| `trans` | 12.4a × 6a for N = 3; 1a PML | Left Ey line source; reference/defect flux and Hz DFT |

The transmission source is **not an `EigenModeSource`**. The measured fundamental-mode-power/flux ratio in the reference run ranges from 0.96971 to 0.99982 over the band. Do not assume perfect single-mode illumination at every frequency.

<h2 id="run">4. Run: separate bands, decay and transmission</h2>

[Download Python code]({{ '/code/photonic_crystal_cavity.py' | relative_url }}) · [Sources and SHA-256]({{ '/assets/meep/26/provenance.json' | relative_url }}) · [Actual transmission log]({{ '/assets/meep/26/trans_r20_dec1e5.log' | relative_url }})

Use Meep and NumPy; no external helper is needed. The previously fitted Lorentz parameters come from the saved summary, so no new fitting dependency is added to the CLI.

```bash
python code/photonic_crystal_cavity.py --help
python code/photonic_crystal_cavity.py --mode bands --out work/cavity-bands
python code/photonic_crystal_cavity.py --mode harminv -N 3 --tag N3 --out work/cavity-harminv
python code/photonic_crystal_cavity.py --mode trans -N 3 --decay 1e-5 --tag N3-strict --out work/cavity-trans
```

1. **Parameters**: fix a = 1, ε, guide width, hole radius and defect spacing.
2. **Geometry**: `bands` uses one period; other modes use a defect with 2N holes.
3. **Source**: bands/resonances use Hz point sources; transmission uses an Ey line source.
4. **Boundaries**: distinguish the periodic cell from an open cavity. Preserve the Harminv mirror phases.
5. **Monitors**: transmission records full-width T/R, upper/lower radiation S, 500 broadband points and 261 points around the narrow peak.
6. **Execution**: Harminv uses a fixed post-source time; transmission uses `stop_when_fields_decayed`. Specify 1e−5 for the verified stricter comparison instead of the default 1e−3.
7. **Postprocessing**: normalize by the empty guide and save JSON/NPZ. Separate `--out` directories keep modes and runs easy to compare.

```python
R = -cavity_reflected_flux / reference_incident_flux
T = cavity_transmitted_flux / reference_incident_flux
S = (upper_outward_flux + lower_outward_flux) / reference_incident_flux
balance = R + T + S
```

<h2 id="interpret">5. Interpret: resolve the narrow peak</h2>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/26/forward_dft.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/26/forward_dft.png' | relative_url }}" alt="Actual Hz intensity at three frequencies, transmission/reflection/radiation balance, and a Lorentz fit to the narrow resonance" loading="lazy"></a>
<figcaption>Left: |Hz|² at f = 0.18, 0.2345 and 0.27 c/a. Upper right: energy balance. Lower right: the densely sampled resonant peak. Field panels have separate color ranges; their brightness is not a cross-panel power comparison.</figcaption>
</figure>

| N = 3, res 20 check | Archived result | Interpretation |
|---|---|---|
| Harminv | f = 0.234454153; Q = 372.408 | Estimate from 400 after source |
| Dense-peak Lorentz fit | f₀ = 0.234450094; Q = 370.395 | Q differs by 0.541% |
| Maximum T in 261-point narrow scan | 0.928430 at f = 0.23445 | Does not establish 100% transmission |
| Near-resonance T in 500-point broad scan | 0.829747 at f = 0.234569 | Sampling misses the peak maximum |
| R + T + S, decay 1e−3 | 0.880632–1.147894 | Inadequate stopping criterion for this comparison |
| R + T + S, decay 1e−5 | 0.995845–1.007986 | Balance within about 1% for this setup |

A narrow peak needs **both a sufficiently long time record and sufficiently fine frequency sampling**. A field-decay stop watches a particular probe, so it is not a universal error guarantee. These balance ranges compare actual runs at the same N = 3 and res 20.

### Separate Q growth from the unresolved documentation discrepancy

At res 20, the fundamental-mode Q values for N = 2/4/6/8/10/12/14 are 62.46 / 1604.36 / 5748.04 / 6014.98 / 6082.39 / 6099.60 / 6081.56. Growth slows at large N, but numerical checks remain:

| Setting | Resonance f (c/a) | Q |
|---|---|---|
| N 3, res 20 | 0.234454153 | 372.408 |
| N 3, res 40 | 0.234893768 | 380.244 |
| N 3, res 60 | 0.234940116 | 380.267 |
| N 14, res 40 | 0.234980965 | 6379.389 |
| N 14, res 60 | 0.235027254 | 6436.946 |
| N 14, res 80 | 0.235014047 | 6401.640 |

At N = 14, res 20, extending Harminv's post-source window from 400 to 3000 gives Q = 6066.89; increasing cell height from 6 to 12 gives Q = 6081.70. These checks **do not recover the documentation's Q ≈ 8750**. The res-20 result agrees with the original notebook's approximately 6080, but that does not make it a converged high-resolution value. The cause remains unresolved. Higher-frequency second modes and entries detected with negative Q are not mixed into the successful fundamental-mode comparison.

<h2 id="check">6. Check: does higher resolution also fix peak sampling?</h2>

<details markdown="1">
<summary>Question 1 · Can 500 frequency samples still miss a peak?</summary>

Yes, if the total interval is broad. Compare frequency spacing with the linewidth, rather than sample count alone. This setup records a broad 500-point monitor and a separate narrow 261-point monitor in the same run. Interpolation cannot recover peak information absent from the samples.

</details>

<details markdown="1">
<summary>Question 2 · Does a small Harminv fit error establish grid convergence?</summary>

Fit error describes a model fit to the supplied time record. It is distinct from errors in curved-boundary sampling, PML, source choice and mode selection. Check frequency, Q, energy balance, grid resolution and run time separately.

</details>

### Change one thing

Keep N = 3 and res 20 while comparing `--decay 1e-3` and `1e-5`. Then change only the grid with `--mode harminv -N 3 --resolution 40`. Do not directly compare one coarse transmission sample between runs with shifted resonances. Compare with [12 · Ring resonator]({{ '/en/ring-resonator/' | relative_url }}): different confinement mechanisms still need independent checks on Q.

<h2 id="reference">7. References and reproduction record</h2>

- Official explanation: [Meep · Band Diagram, Resonant Modes, and Transmission of a Waveguide Cavity](https://meep.readthedocs.io/en/latest/Python_Tutorials/Resonant_Modes_and_Transmission_in_a_Waveguide_Cavity/).
- Pinned sources: [holey-wvg-cavity.py](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/holey-wvg-cavity.py), [holey-wvg-bands.py](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/holey-wvg-bands.py), commit f7811d4.
- Added work: full-width energy accounting, source-mode checks, a dense peak monitor, stopping/grid/Harminv-window/cell-height comparisons and bilingual learning activities. The CLI ports the saved physical setup and removes optional animation helpers. Previously fitted Lorentz parameters are retained in the [summary]({{ '/assets/meep/26/summary.json' | relative_url }}).
- Data: [default-stop JSON]({{ '/assets/meep/26/trans_r20.json' | relative_url }}), [strict-stop JSON]({{ '/assets/meep/26/trans_r20_dec1e5.json' | relative_url }}), [strict-stop fields/spectra NPZ]({{ '/assets/meep/26/trans_r20_dec1e5.npz' | relative_url }}), [Harminv versus N]({{ '/assets/meep/26/harminv_QvsN_r20.json' | relative_url }}), [periodic bands]({{ '/assets/meep/26/bands_r20.json' | relative_url }}), [sources, limits and hashes]({{ '/assets/meep/26/provenance.json' | relative_url }}).
- Path: [04 · Guided modes]({{ '/en/straight-waveguide/' | relative_url }}) → [12 · Resonance and Q]({{ '/en/ring-resonator/' | relative_url }}) → this lesson. Compare absorption and leakage with [25 · Absorbed power]({{ '/en/absorbed-power/' | relative_url }}). Upstream Meep licensing continues to apply to adapted code.

<details markdown="1">
<summary>Expand the complete executable code</summary>

{% highlight python %}
"""Band gap, resonant modes and transmission of a perforated waveguide cavity.

Adapted from NanoComp/meep holey-wvg-cavity.py and holey-wvg-bands.py at
f7811d4157ea22f19d4ca76bc41c71b6e055763e, via holey_repro.py.
Upstream licensing remains applicable; see assets/meep/26/provenance.json.
Publication uses archived calculations. No optional animation helpers are needed.
Modes: bands (periodic cell), harminv (defect modes), trans (two-run spectrum).
"""
import argparse
import json
import os
import time

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["bands", "trans", "harminv"], required=True)
    ap.add_argument("--resolution", type=float, default=20)
    ap.add_argument("-N", type=int, nargs="+", default=[3])
    ap.add_argument("--sy", type=float, default=6)
    ap.add_argument("--fcen", type=float, default=0.25)
    ap.add_argument("--df", type=float, default=0.2)
    ap.add_argument("--window", type=float, default=400, help="harminv: time after source ends (default 400)")
    ap.add_argument("--decay", type=float, default=1e-3, help="trans: field-decay threshold (default 1e-3)")
    ap.add_argument("--noavg", action="store_true", help="disable subpixel averaging")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default="photonic-crystal-cavity-output")
    a = ap.parse_args()
    import meep as mp
    if a.resolution <= 0 or a.sy <= 2 or a.window <= 0 or not 0 < a.decay < 1 or any(n < 0 for n in a.N):
        ap.error("require resolution/window > 0, sy > 2, 0 < decay < 1, N >= 0")
    os.makedirs(a.out, exist_ok=True)
    T0 = time.time()
    eps, w, r, d, pad, dpml = 13, 1.2, 0.36, 1.4, 2, 1
    WG = mp.Medium(epsilon=eps)


    def geom(N):
        g = [mp.Block(size=mp.Vector3(mp.inf, w, mp.inf), material=WG)]
        for i in range(N):
            g.append(mp.Cylinder(r, center=mp.Vector3(d / 2 + i)))
            g.append(mp.Cylinder(r, center=mp.Vector3(-(d / 2 + i))))
        return g


    def dump(name, obj):
        if mp.am_master():
            json.dump(obj, open(os.path.join(a.out, name), "w"), indent=1, default=float)


    if a.mode == "bands":
        sim = mp.Simulation(cell_size=mp.Vector3(1, 12), geometry=[mp.Block(size=mp.Vector3(mp.inf, w, mp.inf), material=WG), mp.Cylinder(radius=r)],
                            sources=[mp.Source(mp.GaussianSource(0.25, fwidth=1.5), component=mp.Hz, center=mp.Vector3(0.1234))],
                            symmetries=[mp.Mirror(direction=mp.Y, phase=-1)], boundary_layers=[mp.PML(1, direction=mp.Y)], resolution=a.resolution)
        kpts = mp.interpolate(19, [mp.Vector3(0), mp.Vector3(0.5)])
        fs = sim.run_k_points(300, kpts)
        dump(f"bands_r{a.resolution:g}.json", dict(kx=[k.x for k in kpts], freqs=[[float(np.real(f)) for f in fl] for fl in fs], wall=time.time() - T0))
        if mp.am_master():
            print("BANDS done", time.time() - T0, flush=True)
        return

    if a.mode == "harminv":
        rows = []
        for N in a.N:
            sx = 2 * (pad + dpml + N) + d - 1
            sim = mp.Simulation(cell_size=mp.Vector3(sx, a.sy), geometry=geom(N), boundary_layers=[mp.PML(dpml)], resolution=a.resolution,
                                sources=[mp.Source(mp.GaussianSource(a.fcen, fwidth=a.df), component=mp.Hz, center=mp.Vector3())],
                                symmetries=[mp.Mirror(mp.Y, phase=-1), mp.Mirror(mp.X, phase=-1)], eps_averaging=not a.noavg)
            h = mp.Harminv(mp.Hz, mp.Vector3(), a.fcen, a.df)
            t1 = time.time()
            sim.run(mp.after_sources(h), until_after_sources=a.window)
            modes = [dict(f=m.freq, Q=m.Q, amp=abs(m.amp), err=abs(m.err)) for m in h.modes]
            rows.append(dict(N=N, sy=a.sy, res=a.resolution, window=a.window, noavg=a.noavg, modes=modes, wall=time.time() - t1))
            if mp.am_master():
                print("HARM " + json.dumps(rows[-1], default=float), flush=True)
            sim.reset_meep()
        dump(f"harminv_{a.tag or 'run'}.json", dict(args=vars(a), rows=rows))
        return

    # ---------------- trans
    N = a.N[0]
    sx = 2 * (pad + dpml + N) + d - 1
    X = 0.5 * sx - dpml
    Y = a.sy - 2 * dpml
    x_t = X - 0.5
    x_src = -X
    x_r = x_src + 0.5
    FR = (a.fcen, a.df, 500)
    FRD = (0.2345, 0.013, 261)
    F3 = [0.18, 0.2345, 0.27]


    def make(Nh):
        sim = mp.Simulation(cell_size=mp.Vector3(sx, a.sy), geometry=geom(Nh), boundary_layers=[mp.PML(dpml)], resolution=a.resolution,
                            sources=[mp.Source(mp.GaussianSource(a.fcen, fwidth=a.df), component=mp.Ey, center=mp.Vector3(x_src), size=mp.Vector3(0, w))],
                            symmetries=[mp.Mirror(mp.Y, phase=-1)])
        fl = dict(
            up=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(x_t), size=mp.Vector3(0, 2 * w))),
            tran=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(x_t), size=mp.Vector3(0, Y))),
            refl=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(x_r), size=mp.Vector3(0, Y))),
            side_p=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(0.5 * (x_r + x_t), 0.5 * Y), size=mp.Vector3(x_t - x_r))),
            side_m=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(0.5 * (x_r + x_t), -0.5 * Y), size=mp.Vector3(x_t - x_r), weight=-1)),
            dense=sim.add_flux(*FRD, mp.FluxRegion(center=mp.Vector3(x_t), size=mp.Vector3(0, Y))),
        )
        mode = sim.add_mode_monitor(*FR, mp.ModeRegion(center=mp.Vector3(x_r), size=mp.Vector3(0, Y)))
        return sim, fl, mode


    pt_t = mp.Vector3(x_t)
    res = {}
    for label, Nh in (("wg", 0), ("cav", N)):
        sim, fl, mode = make(Nh)
        if label == "cav":
            sim.load_minus_flux_data(fl["refl"], refl_data)
        dft = sim.add_dft_fields([mp.Hz], F3, center=mp.Vector3(), size=mp.Vector3(2 * X, Y))
        tr = {"t": [], "v": []}
        steps = [mp.at_every(0.25, lambda s: (tr["t"].append(s.meep_time()), tr["v"].append(float(np.real(s.get_field_point(mp.Ey, mp.Vector3(x_r)))))))]
        t1 = time.time()
        sim.run(*steps, until_after_sources=mp.stop_when_fields_decayed(50, mp.Ey, pt_t, a.decay))
        out = {k: np.array(mp.get_fluxes(v)) for k, v in fl.items()}
        out["freqs"] = np.array(mp.get_flux_freqs(fl["up"]))
        out["dfreqs"] = np.array(mp.get_flux_freqs(fl["dense"]))
        cf = sim.get_eigenmode_coefficients(mode, [1], eig_parity=mp.EVEN_Z)
        out["a_fwd"], out["a_bwd"] = cf.alpha[0, :, 0], cf.alpha[0, :, 1]
        out["Hz"] = np.array([sim.get_dft_array(dft, mp.Hz, i) for i in range(3)])
        out["eps"] = sim.get_array(component=mp.Dielectric, center=mp.Vector3(), size=mp.Vector3(2 * X, Y))
        out["trace_t"], out["trace_v"] = np.array(tr["t"]), np.array(tr["v"])
        out["t_end"], out["wall"] = sim.meep_time(), time.time() - t1
        if label == "wg":
            refl_data = sim.get_flux_data(fl["refl"])
        res[label] = out
        if mp.am_master():
            print(f"TRANS {label} t_end={out['t_end']:.1f} wall={out['wall']:.0f}s", flush=True)
        sim.reset_meep()
    if mp.am_master():
        flat = {f"{lab}_{k}": v for lab, o in res.items() for k, v in o.items()}
        np.savez_compressed(os.path.join(a.out, f"trans_{a.tag or 'r%g' % a.resolution}.npz"), N=N, sx=sx, sy=a.sy, X=X, Y=Y, x_t=x_t, x_r=x_r, x_src=x_src, F3=F3, **flat)
        inc = res["wg"]["tran"]
        R = -res["cav"]["refl"] / inc
        T = res["cav"]["tran"] / inc
        S = (res["cav"]["side_p"] + res["cav"]["side_m"]) / inc
        tot = R + T + S
        i0 = int(np.argmin(np.abs(res["wg"]["freqs"] - 0.2345)))
        mf = np.abs(res["wg"]["a_fwd"]) ** 2 / res["wg"]["refl"]
        summ = dict(tag=a.tag, res=a.resolution, N=N, decay=a.decay, t_end_cav=res["cav"]["t_end"], sum_minmax=[float(tot.min()), float(tot.max())],
                    sum_at=float(tot[i0]), T_at=float(T[i0]), R_at=float(R[i0]), S_at=float(S[i0]),
                    mode_frac_minmax=[float(mf.min()), float(mf.max())], wall=time.time() - T0)
        dump(f"trans_{a.tag or 'r%g' % a.resolution}.json", summ)
        print("RESULT " + json.dumps(summ, default=float), flush=True)


if __name__ == "__main__":
    main()
{% endhighlight %}

</details>
