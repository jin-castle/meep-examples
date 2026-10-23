# meep-examples

Meep (FDTD) 공식 예제 해설 시리즈 — 입문자용. 사이트: https://jin-castle.github.io/meep-examples/

A beginner-friendly walkthrough of the official [Meep](https://meep.readthedocs.io/) examples, ordered like a 10-week applied-electromagnetics course (post number = week − 1; weeks 2–10 → posts 01–09).
Korean body, English TL;DR, English code comments. Every script in `code/` was re-run before publishing.

| # | Post | Script | Key numbers (Meep 1.33.0) |
|---|------|--------|---------------------------|
| 01 | Point source와 line source — 파원 배치, 펄스 시각 t0, flux box로 보는 방향 분포 | `code/point_line_source.py` | point: 0.25 per side; 3 µm line: 0.92 through the two facing sides |
| 02 | 경계 조건과 PML — 반사 경계, PML, Absorber를 같은 잣대로 재기 | `code/boundary_pml.py` | reflection: no layer 1.0, Absorber 1 µm 1.9e-2, PML 1 µm 4.5e-4 |
| 04 | Straight waveguide와 guided mode — MPB n_eff, EigenModeSource, modal transmission | `code/straight_waveguide.py` | T = 1.0000, R = 8e-6; three guided TE modes (n_eff 3.15 / 2.59 / 1.45) |
| 05 | Bent waveguide와 radius trade-off — 2-run flux 정규화, sharp bend 기준값, radius sweep | `code/bend90.py` | sharp: T = 0.20, R = 0.22, radiated = 0.58; T = 0.91 at R = 0.35 µm, 0.99 at 0.70 µm |

## Run a script

```bash
conda install -c conda-forge pymeep
cd code
python point_line_source.py    # ~20 s, writes ../assets/01/ (incl. 2 GIFs)
python boundary_pml.py         # ~10 s, writes ../assets/02/
python straight_waveguide.py   # ~3 min (incl. GIF) (baseline + convergence), writes ../assets/04/
python bend90.py               # ~95 s (sharp + radius sweep + convergence), writes ../assets/05/
```

`code/blogfig.py` holds the shared figure helpers (annotated layout with code-step badges, field maps with the structure outlined, source waveform/spectrum, spectra in nm, snapshot grids, and GIF animations via `record_frames` + `animate_fields`).

## Site

Jekyll + minima, built by GitHub Pages. Math via MathJax. Posts are in `_posts/`, figures in `assets/meep/NN/`.
