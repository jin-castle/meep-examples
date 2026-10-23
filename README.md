# meep-examples

Meep (FDTD) 공식 예제 해설 시리즈 — 입문자용. 사이트: https://jin-castle.github.io/meep-examples/

A beginner-friendly walkthrough of the official [Meep](https://meep.readthedocs.io/) examples, ordered like a 10-week applied-electromagnetics course (post number = week − 1; weeks 2–10 → posts 01–09).
Korean body, English TL;DR, English code comments. Every script in `code/` was re-run before publishing.

| # | Post | Script | Key numbers (Meep 1.33.0) |
|---|------|--------|---------------------------|
| 04 | Straight waveguide와 guided mode — EigenModeSource, mode monitor, modal transmission | `code/straight_waveguide.py` | T = 1.0000, R = 8e-6 |
| 05 | Bent waveguide와 radiation loss — sharp bend의 2-run flux 정규화 | `code/bend90.py` | T = 0.20, R = 0.22, radiated = 0.58 |

## Run a script

```bash
conda install -c conda-forge pymeep
cd code
python straight_waveguide.py   # ~35 s, writes ../assets/04/
python bend90.py               # ~12 s, writes ../assets/05/
```

`code/blogfig.py` holds the shared figure helpers (annotated layout with code-step badges, field maps with the structure outlined, spectra in nm).

## Site

Jekyll + minima, built by GitHub Pages. Math via MathJax. Posts are in `_posts/`, figures in `assets/meep/NN/`.
