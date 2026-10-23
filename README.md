# meep-examples

Meep (FDTD) 공식 예제 해설 시리즈 — 입문자용. 사이트: https://jin-castle.github.io/meep-examples/

A beginner-friendly walkthrough of the official [Meep](https://meep.readthedocs.io/) examples, ordered like a 10-week applied-electromagnetics course (post number = week − 1; weeks 2–10 → posts 01–09).
Korean body, English TL;DR, English code comments. Every script in `code/` was re-run before publishing.

| # | Post | Script | Key numbers (Meep 1.33.0) |
|---|------|--------|---------------------------|
| 04 | Straight waveguide와 guided mode — MPB n_eff, EigenModeSource, modal transmission | `code/straight_waveguide.py` | T = 1.0000, R = 8e-6; three guided TE modes (n_eff 3.15 / 2.59 / 1.45) |
| 05 | Bent waveguide와 radius trade-off — 2-run flux 정규화, sharp bend 기준값, radius sweep | `code/bend90.py` | sharp: T = 0.20, R = 0.22, radiated = 0.58; T = 0.91 at R = 0.35 µm, 0.99 at 0.70 µm |

## Run a script

```bash
conda install -c conda-forge pymeep
cd code
python straight_waveguide.py   # ~2.5 min (baseline + convergence), writes ../assets/04/
python bend90.py               # ~95 s (sharp + radius sweep + convergence), writes ../assets/05/
```

`code/blogfig.py` holds the shared figure helpers (annotated layout with code-step badges, field maps with the structure outlined, spectra in nm).

## Site

Jekyll + minima, built by GitHub Pages. Math via MathJax. Posts are in `_posts/`, figures in `assets/meep/NN/`.
