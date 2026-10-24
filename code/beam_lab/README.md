# Beam Lab

Beam Lab is a separately written Meep experiment, built around analytic
electric-current apertures and a parameter comparison chosen for this site.
It does not load `optbeam`, execute a downloaded example, or depend on the
historical `../optical_beams/source/` directory.

The earlier reproduction remains available at
[the archive](https://jin-castle.github.io/meep-examples/optical-beams/archive/).
Its code, measurements, figures and MIT notices retain their original provenance.
The new experiment is a different model, not a relabeling of those datasets.

## Model

All sources are finite Ez electric-current sheets. They emit in both directions;
the saved monitor covers the forward side. The aperture expressions describe
source currents, not exact nonparaxial vector Maxwell beam solutions.

| Study | Current aperture | Changed parameter |
|---|---|---|
| Gaussian | `exp(-(y/w)^2) exp(i 2*pi*f*n*sin(angle)*y)` | Boundary `x=kappa*y^2`, kappa = 0, +0.10, -0.10 |
| Vortex | `(sqrt(2)*r/w)^abs(m) exp(-r^2/w^2) exp(i*m*atan2(z,y))` | m = +2, -2 in vacuum |
| Airy | `Ai(y/s) exp(alpha*y/s)` on a finite aperture | alpha = 0.08, 0.20 in vacuum |

Each current profile is peak normalized. Equal peak current does not establish
equal injected power. Lengths are in arbitrary units `a`, with vacuum wavelength
`a` at `f=1 c/a`; no physical micrometre scale is assigned.

## Run and reproduce

Use a Meep-enabled Python environment with NumPy, SciPy, Matplotlib, Pillow and
VTK. The published environment is Meep 1.33.0; existing scientific tools are used
without an additional beam-profile package.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VTK_SMP_MAX_THREADS=1
python -m unittest discover -s code/beam_lab -p 'test_*.py'
python code/beam_lab/run.py --suite --output output/beam-lab
python code/beam_lab/render.py --data output/beam-lab --output assets/meep/beam-lab
```

To run just one case:

```bash
python code/beam_lab/run.py --case lg_minus2 --output output/beam-lab
```

`profiles.py` contains the analytic source functions and phase-winding check.
`run.py` constructs the simulation directly, settles the source for 24 a/c,
then accumulates complex DFT fields for 8 a/c. Resolution is 20/a for 2D and
12/a for 3D; the Gaussian high-index medium therefore has about 13.3 points per
wavelength. PML thickness is 0.8a. Each case writes native centered `ex/ey/ez`,
permittivity and coordinates to `fields.npz`; `case.json` binds the arrays to
the exact runner/profile hashes and records the actual monitor times.

`render.py` creates common-scale parameter comparisons, measured DFT phase
maps and a native-grid signed-field 3D phase cycle. The phase cycle is
`Re(E_tilde exp(-i*phi))`; it does not show turn-on or wavefront arrival.
The finite settling time is not a demonstrated steady-state convergence test.
The two charge cases use one fixed color/isovalue scale across every phase.

Raw NPZ fields remain in the execution folder, outside the site assets.
Published `checks.json` includes case metadata, source/data hashes, measured
winding and rendering checks. These visualization runs do not establish
resolution/PML convergence, normalized transmission or efficiency.

## References and authorship boundary

- [Meep Python API](https://meep.readthedocs.io/en/latest/Python_User_Interface/)
  supplies the simulator interface.
- [SciPy Airy function](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.airy.html)
  supplies `Ai`; the analytic aperture expressions are stated above.
- [Optical-beams-MEEP](https://danielkotik.github.io/Optical-beams-MEEP/)
  inspired the beam topics and visual exploration. This new implementation
  uses different source models, geometry, parameters, measurements and figures.
  It does not reproduce that project's exact angular-spectrum sources.

Maintained by jin-castle with AI-assisted implementation and editorial work.
This identifies the implementation boundary, not a legal clean-room audit or
a claim of ownership of mathematical formulas, Meep or third-party libraries.
Repository and file-specific reuse conditions remain in
`THIRD_PARTY_NOTICES.md` and the site's rights pages.
