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
