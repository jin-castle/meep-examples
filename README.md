# meep-examples

Meep (FDTD) 공식 예제 해설 시리즈 — 입문자용. 사이트: https://jin-castle.github.io/meep-examples/

A beginner-friendly walkthrough of the official [Meep](https://meep.readthedocs.io/) examples, ordered like a 10-week applied-electromagnetics course (post number = week − 1; weeks 2–10 → posts 01–09).
Korean body, English TL;DR, English code comments. Every script in `code/` was re-run before publishing.

| # | Post | Script | Key numbers (Meep 1.33.0) |
|---|------|--------|---------------------------|
| 01 | Point source와 line source — 파원 배치, 펄스 시각 t0, flux box로 보는 방향 분포 | `code/point_line_source.py` | point: 0.25 per side; 3 µm line: 0.92 through the two facing sides |
| 02 | 경계 조건과 PML — 반사 경계, PML, Absorber를 같은 잣대로 재기 | `code/boundary_pml.py` | reflection: no layer 1.0, Absorber 1 µm 1.9e-2, PML 1 µm 4.5e-4 |
| 03 | Reference run 빼기 — incident·total·scattered field, R·T·S 수지, 산란 단면적 | `code/reference_subtraction.py` | Fresnel to 1.6e-4; cylinder R+T+S = 0.999, Q_sca 2.515 vs 2D Mie 2.513 |
| 04 | Straight waveguide와 guided mode — MPB n_eff, EigenModeSource, modal transmission | `code/straight_waveguide.py` | T = 1.0000, R = 8e-6; three guided TE modes (n_eff 3.15 / 2.59 / 1.45) |
| 05 | Bent waveguide와 radius trade-off — 2-run flux 정규화, sharp bend 기준값, radius sweep | `code/bend90.py` | sharp: T = 0.20, R = 0.22, radiated = 0.58; T = 0.91 at R = 0.35 µm, 0.99 at 0.70 µm |
| 06 | Binary grating과 diffraction order — grating equation, 차수별 효율, duty cycle이 만드는 위상 | `code/binary_grating.py` | m=0 0.759, m=±1 0.088, T+R 0.999; duty-cycle phase span 0.09/0.23 × 2π; finite grating beam 35.2° (eq. 36.6°) |
| 07 | Metalens의 meta-atom과 phase library — 폭 하나로 위상을 돌리고, 4단계로 빛을 꺾고, 어디서 설계가 틀어지는가 | `code/meta_atom.py` | library span 1.10 × 2π; 4-level supercell +1 order 0.514 = 63 % of the blazed bound; 40-atom array peaks at 58.5° |
| 08 | Metagrating inverse design — forward, adjoint, gradient, 검증의 4단계 계약 | `code/metagrating_inverse.py` | gradient gate PASS (0.7 / 0.1 / 0.06 %); MMA x5: +1 order 0.496 → 0.623 in a fresh run (61 → 77 % of the bound) |

## Run a script

```bash
conda install -c conda-forge pymeep
cd code
python point_line_source.py    # ~20 s, writes ../assets/01/ (incl. 2 GIFs)
python boundary_pml.py         # ~10 s, writes ../assets/02/
python reference_subtraction.py # ~30 s, writes ../assets/03/
python straight_waveguide.py   # ~3 min (incl. GIF) (baseline + convergence), writes ../assets/04/
python bend90.py               # ~2 min (incl. GIFs)
python binary_grating.py       # ~30 s, writes ../assets/06/
python meta_atom.py            # ~35 s, writes ../assets/07/
python metagrating_inverse.py  # ~50 s (meep.adjoint + nlopt), writes ../assets/08/ (sharp + radius sweep + convergence), writes ../assets/05/
```

`code/blogfig.py` holds the shared figure helpers (annotated layout with code-step badges, field maps with the structure outlined, source waveform/spectrum, spectra in nm, snapshot grids, and GIF animations via `record_frames` + `animate_fields`).

## Site

Jekyll + minima, built by GitHub Pages. Math via MathJax. Posts are in `_posts/`, figures in `assets/meep/NN/`.
