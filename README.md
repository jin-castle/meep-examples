# meep-examples

Meep (FDTD) 공식 예제 해설 시리즈 — 입문자용. 사이트: https://jin-castle.github.io/meep-examples/

A beginner-friendly walkthrough of the official [Meep](https://meep.readthedocs.io/) examples.
Korean body, English TL;DR, English code comments. Every script in `code/` was re-run before publishing.

| # | Post | Script | Key numbers (Meep 1.33.0) |
|---|------|--------|---------------------------|
| 01 | Straight Waveguide — 넣은 빛이 전부 나오는가 | `code/straight_waveguide.py` | T = 1.0000, R = 8e-6 |
| 02 | 90° Waveguide Bend — 직각으로 꺾으면 얼마나 새는가 | `code/bend90.py` | T = 0.20, R = 0.22, radiated = 0.58 |

## Run a script

```bash
conda install -c conda-forge pymeep
cd code
python straight_waveguide.py   # ~35 s, writes ../assets/meep/01/
python bend90.py               # ~12 s, writes ../assets/meep/02/
```

`code/blogfig.py` holds the shared figure helpers (annotated layout with code-step badges, field maps with the structure outlined, spectra in nm).

## Site

Jekyll + minima, built by GitHub Pages. Math via MathJax. Posts are in `_posts/`, figures in `assets/meep/NN/`.
