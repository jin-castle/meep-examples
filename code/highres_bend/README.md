# High-resolution centered waveguide bend

`extract_highres.py` runs the existing 2D Ez bend in Meep 1.33.0 at 60 pixels/um on one CPU process. The input guide meets the center of the design square's left edge; the output meets the center of its top edge. The 1 x 1 um MaterialGrid has 61 x 61 independent densities, replacing the original 11 x 11 parameterization. The 6 x 5 um cell, 1 um PML, 0.5 um guide width, refractive indices 3.4 / 1.44, and 1.55 um vacuum wavelength match the original example.

Run in WSL with the existing environment:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/bgs43/miniforge3/envs/pmp/bin/python extract_highres.py
/home/bgs43/miniforge3/envs/pmp/bin/python package_assets.py
/home/bgs43/miniforge3/envs/pmp/bin/python validate_assets.py
```

The initial design is uniform density 0.5. Native Meep forward and adjoint runs produce the output mode-1 power objective and its gradient. The adjoint sources come from `EigenmodeCoefficient.place_adjoint_source` differentiated for `|a_out|^2`, including Meep's temporal, source-Fourier, spatial-volume, and real-field normalization. Display Ez monitors are recorded during these same runs. The native gradient uses persistent complex displacement-field monitors and the derivative of the discretized MaterialGrid operator. Two displayed real-part pictures alone do not determine this gradient.

Two centered finite differences along the normalized adjoint gradient, with L2 steps 0.01 and 0.03, must agree within 2% and have the same sign before an update is attempted. A projected gradient-ascent update starts at maximum density change 0.15, halving that value if necessary. Only an evaluated update with an increased objective is accepted. This is one density update, without binarization or convergence claims. Objective values use source/optimizer units; they are not normalized transmission efficiencies.

`fields.npz` preserves complex128 forward, adjoint, and updated-forward Ez fields with physical sample coordinates, plus initial/updated densities and the gradient. Array order is x then y. Flat density and gradient arrays use `index = x * Ny + y`; y increases upward. Full-cell DFT shape is 360 x 300. The design monitor has 62 x 62 samples at spacing 1/60 um, including boundary padding; plots crop to the exact [-0.5, 0.5] um design square using the stored coordinates.

The PNGs use `RdBu` with symmetric limits centered at zero: red is negative and blue is positive. Each field image has its own symmetric scale, recorded in the result metadata. The design field and gradient PNGs export at 720 x 720 pixels with nearest-sample rendering. Their native numerical resolution remains 60 samples/um. Black geometry outlines identify the guides and design region while leaving the fields visible. Density PNGs use grayscale.

`site-assets/` contains the compact lossless PNGs and JSON consumed by the website. Raw arrays, source, validation details, and execution log remain outside that folder for reproducibility.

`render_assets.py` rebuilds PNGs from the saved numerical arrays without repeating the simulation. Run it before `package_assets.py` when changing plotting styles.
## Unified scene and capture colors

After the simulation, run `python render_scene.py /path/to/fields.npz --out /path/to/assets/meep/09/highres`. This renders native full-cell RdBu fields and matching design crops from the saved complex results; it does not rerun Meep. The helper asserts crop orientation, shared normalization and exact interior pixel agreement. The original simulation source and its SHA256 remain unchanged.

The same command exports32-phase sprites for forward and adjoint playback. It checks quarter-cycle identities, loop closure, all stored RGBA frames, phase0/capture equality and source-to-design input phase progression. Every phase uses the same complex-amplitude color limit; metadata identifies the result as a normal steady-state DFT phase cycle.

## Six accepted optimization updates

The homepage uses the separate `assets/meep/09/iterations/manifest.json` history. From this directory, reproduce its six fresh resolution-60 cycles with:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/bgs43/miniforge3/envs/pmp/bin/python iterate.py --out /tmp/meep-iterations --steps 6
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/bgs43/miniforge3/envs/pmp/bin/python render_iterations.py /tmp/meep-iterations ../../assets/meep/09/iterations
```

Each accepted density is passed unchanged into the following native forward and adjoint solve. Numbered JSON/NPZ checkpoints preserve the actual gradient, before/after densities and complex fields; an existing checkpoint is validated and reused on restart. A projected maximum-density step of 0.15 was accepted in all six cycles. The unnormalized objective increased from 2.9157725347 to 147.0497944969. These are finite early optimization steps, without a binarization or convergence claim.

A new centered finite difference at the second starting geometry agrees with its adjoint directional derivative to relative error 3.084e-6. Rendering verifies exact density continuity, the projected update, physical sample coordinates, all 32 stored phase frames, exact phase-zero capture crops, and independently recomputed forward-field continuity (maximum relative error 1.244e-11). All physical runs stopped before the simulation time cap.

All six before/after forward scenes and captures share the same symmetric color limit, 20.3186982670; all adjoint scenes and captures share a separate common limit, 0.01794171218. The renderer only uses saved complex DFT arrays. It preserves black fixed-port contours and uses grayscale for the continuous 61x61 density. Displayed gradients use their own symmetric limits. Source and raw-array SHA256 values are recorded in the manifest; `validation.json` records numerical and rendering checks.
