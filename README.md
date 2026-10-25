# meep-examples

Meep (FDTD) 공식 예제 해설 시리즈 — 입문자용. 사이트: https://jin-castle.github.io/meep-examples/

A beginner-friendly walkthrough of the official [Meep](https://meep.readthedocs.io/) examples, ordered like a 10-week applied-electromagnetics course (post number = week − 1; weeks 2–10 → posts 01–09), followed by season 2 (posts 10–16: the journey of a point source, from a mirror to light extraction and the far field).
Full Korean and English editions, with shared scientific results and English code comments. Every script in `code/` was re-run before publishing.

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
| 09 | Waveguide bend inverse design — 자유 설계 영역과 출력 포트 mode power | `code/bend_inverse.py` | gate PASS (0.00 / 0.00 / 0.01 %); MMA x5: output mode-1 transmission 0.015 → 0.780 in a fresh run (0.639 at twice the resolution); 119 / 121 pixels still grey |
| 10 | 점광원의 3D 방사 패턴 — Bloch 1D run 묶음과 PEC 거울의 image dipole | `code/dipole_pattern_3d.py` | x-dipole 3D pattern from 240 1D Bloch runs: 0.22 % vs analytic; dipole above a PEC mirror: image-dipole near2far 0.66 % (5 lobes), 1D Bloch 6.8 % below the glancing limit |
| 11 | 두 거울 사이의 점광원 — LDOS와 Purcell 인자 | `code/cavity_ldos.py` | planar cavity Purcell factor vs Abram Eq. 7: median 0.94 % away from the modal cutoffs (cyl), 3D check 2.3 / 0.9 %; metal box: dft_ldos = 0.81–0.89 of 2Q/(πωV), under-converged 0.72 when the run is capped |
| 12 | 빛을 가두는 고리 — Harminv, Q, FSR, solve_cw 교차검증 | `code/ring_resonator.py` | three Ez modes at 0.118 / 0.147 / 0.176 (Q 81 / 317 / 1675 at res 10, tutorial values); FSR 0.029 → n_g 3.69; m = 3 / 4 / 5; solve_cw vs time-domain DFT 0.40 % |
| 13 | 회전 대칭으로 3D를 계산하기 — cylindrical 좌표, m 급수, on/off-axis 쌍극자, 디스크 방사 | `code/cylindrical_dipole.py` | on-axis dipoles 0.43 / 0.46 % vs sin² / cos²; off-axis dipole as m = 0..8, 0.63 %; post-12 ring per m within 0.1 % in f; disc near/far gap 7.43 % → 6.41 % with a larger cell |
| 14 | 박막 속 점광원, 공기로 나오는 몫 — 광추출 효율, LDOS 정규화, kz 적분, CYL 대 3D | `code/extraction_efficiency.py` | layer on a mirror: 0.323 at mid-height (cyl, res 80), 0.52 → 0.09 with height; off-axis m series: official stop 0.632 vs 0.362 summed to m = 60; cleaved facet: 22.4 % from 76 kz runs |
| topic | Metalens 위상 지도와 PB 위상 — 이상적 렌즈 위상, 2π 접기, 격자 샘플링 (`/metalens/`) | `code/metalens_*.py` (numpy, no Meep) | 1D scalar check: sampled PB phase focuses with FWHM 499 nm vs 493 nm for the continuous ideal phase (peak 0.95); the opposite circular polarization diverges |

## Beam Lab

The [Beam Lab lesson](https://jin-castle.github.io/meep-examples/optical-beams/)
uses newly written source profiles, Meep controls and analysis in
[`code/beam_lab/`](code/beam_lab/). Its parameter studies compare Gaussian beams
at interfaces with curvature 0 and ±0.1, Laguerre–Gaussian charges +2 and −2,
and finite-energy Airy profiles with apodization 0.08 and 0.2. The new experiment
data and figures come from this implementation, which does not import the
vendored `optbeam` package or the earlier reproduction wrappers.
Daniel Kotik and Jörg Götte's
[Optical-beams-MEEP](https://danielkotik.github.io/Optical-beams-MEEP/) is a
reference for visual presentation and beam topics; the
[Meep Python interface](https://meep.readthedocs.io/en/latest/Python_User_Interface/)
documents the simulation API.

The earlier original-code runs, native-grid Blender scene and moving 3D vortex
remain available in the [reproduction archive](https://jin-castle.github.io/meep-examples/optical-beams/archive/)
([English](https://jin-castle.github.io/meep-examples/en/optical-beams/archive/)).
Those results retain their original provenance and are not relabeled as Beam Lab
calculations. Their sources, MIT notice, execution commands and wrappers remain in
[`code/optical_beams/`](code/optical_beams/), with results and provenance under
`assets/meep/optical-beams/`. The archive comparison's left panel is an attributed
upstream image. Archived software citation: Optical-beams-MEEP v2.1.2,
[doi:10.5281/zenodo.5211251](https://doi.org/10.5281/zenodo.5211251).

The inverse-bend DFT scene, phase playback and captures use opaque RdBu fields
with black waveguide outlines. Metalens intensity panels use a black-to-hot map;
its model remains the original 1D scalar angular-spectrum calculation.

## Run a script

```bash
conda install -c conda-forge pymeep
cd code
python point_line_source.py    # ~20 s, writes ../assets/01/ (incl. 2 GIFs)
python boundary_pml.py         # ~10 s, writes ../assets/02/
python reference_subtraction.py # ~30 s, writes ../assets/03/
python straight_waveguide.py   # ~3 min (incl. GIF) (baseline + convergence), writes ../assets/04/
python bend90.py               # ~2 min (incl. GIFs) (sharp + radius sweep + convergence), writes ../assets/05/
python binary_grating.py       # ~30 s, writes ../assets/06/
python meta_atom.py            # ~35 s, writes ../assets/07/
python metagrating_inverse.py  # ~50 s (meep.adjoint + nlopt), writes ../assets/08/
python bend_inverse.py         # ~30 s (meep.adjoint + nlopt), writes ../assets/09/
python dipole_pattern_3d.py    # ~4.5 min (240 1D runs + 2D near2far), writes ../assets/10/
python cavity_ldos.py          # ~7 min (cyl sweep + 3D + Harminv/dft_ldos), writes ../assets/11/
mpirun -np 4 python ring_resonator.py   # ~4 min (Harminv x3 res, mode images, solve_cw), writes ../assets/12/
mpirun -np 4 python cylindrical_dipole.py   # ~8 min (cylindrical m runs, disc), writes ../assets/13/
mpirun -np 4 python extraction_efficiency.py   # ~77 min (m series to 60 dominates), writes ../assets/14/
```

`code/blogfig.py` holds the shared figure helpers (annotated layout with code-step badges, field maps with the structure outlined, source waveform/spectrum, spectra in nm, snapshot grids, and GIF animations via `record_frames` + `animate_fields`).

## Sources, contributions and reuse

Maintained and edited by [jin-castle](https://github.com/jin-castle), with AI-assisted
code, translation and illustration workflows. The bilingual
[권리 및 라이선스](https://jin-castle.github.io/meep-examples/rights-and-licenses/) /
[Rights & Licenses](https://jin-castle.github.io/meep-examples/en/rights-and-licenses/)
pages distinguish upstream examples, project additions, computed figures and AI
illustrations. Each lesson/topic also links its sources and added experiments.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for upstream notices and the
chapter-to-source inventory; `_data/sources.json` drives the bilingual site inventory.
No new repository-wide code license is granted. Upstream/file-specific licenses
take precedence. Reorganizing or modifying upstream code does not remove its
license obligations. Original protectable editorial contributions are reserved
unless separately licensed; this does not restrict third-party permissions or
statutory exceptions, or assert exclusive copyright over entire AI outputs.

## Site configuration

Private visitor and Google Search reports are described in [ANALYTICS.md](ANALYTICS.md).
GA4 loads only after visitor consent; bilingual privacy pages and footer settings
explain the choice. The public site does not publish dashboard data.

Jekyll + minima, built by GitHub Pages. Math via MathJax. Korean posts are in `_posts/`; English lessons and topics are in `en/`. Use [한국어](https://jin-castle.github.io/meep-examples/) or [English](https://jin-castle.github.io/meep-examples/en/) and select System, Light or Dark in the header. Language switches preserve the corresponding page and section; theme choices persist when browser storage is available.

Each of the 14 chapter concept illustrations has four explicit PNG exports in `assets/illustrations/`: `XX.ko.light.png`, `XX.ko.dark.png`, `XX.en.light.png`, and `XX.en.dark.png`. The catalog and “Understand the principle” sections share these assets. `manifest.json` records prompts, dimensions and hashes. Numerical figures remain in `assets/meep/NN/` with their original pixels and color scales; theme changes do not invert or generatively edit them.
