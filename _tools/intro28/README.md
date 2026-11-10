# Chapter 28 intro authoring

This scene uses an existing Meep complex Ey DFT cross-section. It does not run a simulation. `field.json` records its source SHA-256, run metadata SHA-256, packed-data SHA-256, parameters and decoding rules.

Two square Si waveguides (`n=3.45`, side `a=1`, gap `s/a=0.5`) run along simulation z. The field is reconstructed as `Re[(Ey_re(x,y)+i Ey_im(x,y)) exp(i(2π kz z−phase))]`, with `fa/c=0.2`, `kz a=0.3857897870486012`. Signed fields use RdBu. Both rods and the reference grid use the same world axes. The finite displayed length and grid are visual aids; the calculation used infinite Bloch-periodic guides. This is a steady-state DFT phase cycle, not a 3D transient recording.

The signed RdBu coordinate is linear, `clamp(1.25*Re(Ey)/lim,-1,1)`, with one fixed gain across space and time. Red is negative, blue positive and zero white. Ray opacity tends continuously to zero with field magnitude, making zero transparent. A complex-magnitude display threshold of 0.012 suppresses quantization noise far outside the guides. These display choices are recorded in `field.json`; color and opacity are not a power measurement.

`index.html` uses the same Three.js version as the existing intro pipeline (0.170.0 via jsDelivr). Serve this directory over HTTP. Append `?t=4` for a frozen poster or use `window.__hero.setTime(seconds)` for deterministic capture. Eight seconds contains two complete optical phase cycles and one periodic camera orbit.

To regenerate the small packed texture with existing Python/NumPy:

```text
python pack_field.py <path-to-existing-anim_even_s0.5_ey.npz>
```

Capture 240 PNG frames at 1280×720 with the existing `C:/Users/bgs43/.claude/skills/photonics-motion/scripts/render_loop.mjs`; encode with FFmpeg (`libx264`, CRF26, yuv420p, faststart, no audio). Poster is frame120 (4s). No dependency installation is required.

Exact PowerShell recipe, from this authoring directory:

```powershell
# Keep this server running in its terminal while capturing.
python -m http.server 8738 --bind 127.0.0.1 --directory .

# In a second terminal, use a fresh scratch directory for deterministic PNGs.
./render.ps1 -Frames '<absolute-scratch-directory>/intro28-render'
```

`render.ps1` writes the MP4/JPG to this repository's `assets/meep/28/` and prints FFprobe evidence. It uses the already-installed Node, Chrome, FFmpeg and the existing capture script; `-CaptureScript` can point to that renderer on another machine. FFmpeg/FFprobe resolve from PATH, then the existing Windows WinGet installation; override them with `-Ffmpeg <absolute-path> -Ffprobe <absolute-path>`. The page exposes the same `window.__hero.setTime(t)` interface as the other intros, so any deterministic browser capture tool can be substituted. The renderer performs no network requests beyond loading the pinned Three.js module and the local field files.
