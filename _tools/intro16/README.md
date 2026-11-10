# Chapter 16 cylindrical zone-plate intro

The saved Meep complex DFT **Er** coefficient is reconstructed as `Re[Er(r,z) exp(-i phi - i phase)]`, using the actual cylindrical azimuthal order `m=-1`. It shows only the recorded near-field slab `r=0…52.3891109269 µm`, `z=-2.25…2.25 µm`. It is a steady-state phase cycle, not a transient or a computed 3D arrival sequence. The distant 200 µm focus is not shown: saved far-field arrays contain only real intensity profiles, so no intermediate or far-field phase has been invented.

All axial positions, including substrate, relief, source reference and field, are uniformly magnified **8×** for legibility. Radial coordinates retain their original scale. The full25-zone binary-phase geometry is rendered, with glass index1.5. Glass occupies the central disk and alternating annuli at physical `z=-.25…+.25 µm`, above a substrate whose displayed non-PML portion is `z=-2.25…-.25 µm`. The pale cyan color denotes glass; the amber lower outline marks the source height. The reference grid is illustrative.

`field.json` records all source hashes, axis order, formula, geometry and display choices. The raw source array has axes `(z,r)`, not `(r,z)`. Packing retains all114 axial rows and all1311 radial columns at native resolution. Signed linear RdBu uses one fixed gain3, clipped at the color-scale endpoints; zero field becomes transparent. Opacity is a display aid and does not measure intensity or efficiency. Append `&camera=fixed` to a frozen preview URL to verify phase motion independently of the camera.

Three.js0.170.0 is pinned, matching the other intros. The MIT notice is in `THREE-LICENSE.txt`. No package installation or new simulation is needed.

```powershell
python pack_field.py '<existing-zp_n25_r25_fields.npz>'
# Keep this server running while rendering.
python -m http.server 8739 --bind 127.0.0.1 --directory .
# In a second terminal use a fresh scratch directory (capture resumes existing PNGs).
./render.ps1 -Frames '<absolute-scratch-directory>/intro16-render'
```

`render.ps1` captures240 PNGs at1280×720,30fps,8s through the existing deterministic Chrome capture script. It writes H.264/yuv420p MP4 and a JPEG poster from frame120. FFmpeg/FFprobe resolve through PATH or the existing WinGet installation; explicit `-Ffmpeg`/`-Ffprobe` overrides are supported. `-CaptureScript` can select the existing renderer elsewhere. `index.html?t=4` and `window.__hero.setTime(t)` provide deterministic previews.
