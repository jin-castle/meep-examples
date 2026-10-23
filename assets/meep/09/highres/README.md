# Resolution-60 DFT capture data

Generated2026-10-23 using Meep1.33.0, one MPI process and one CPU thread. The forward and adjoint Ez DFT monitors were recorded in the same runs used to calculate the initial adjoint gradient.

- FDTD resolution:60pixels/µm; design variables:61×61.
- Wavelength:1.55µm; cell:6×5µm; design square:1×1µm; guide width:0.5µm.
- Full DFT:360×300 complex samples. Design monitor:62×62 including boundary padding; image crop uses stored physical coordinates.
- RdBu, symmetric scales centered at zero, negative red/positive blue; black unfilled layout boundaries.
- Two centered directional finite differences passed; maximum relative error0.001839%.
- One accepted projected gradient-ascent update, maximum density change0.15: objective2.9157725347→38.4147296510. These are unnormalized mode-power units, not transmission efficiency.
-720×720 design PNGs display native samples with nearest interpolation. They are not720×720 simulation grids.

result.json contains density/gradient arrays, solver settings, source/normalization description, field display limits and numerical validation. Flat density indexing is x*Ny+y; y increases upward.

The reproducible extraction and packaging scripts are in code/highres_bend/. Run them in a dedicated output directory with Meep1.33.0. Raw complex128 arrays are retained in the separately delivered reproducibility archive; they are not required by the website. This initial single update is not an optimized or fabricated binary bend.
