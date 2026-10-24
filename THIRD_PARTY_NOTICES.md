# Third-party notices and contribution inventory

Updated: 2026-10-24. Maintainer/editor: [jin-castle](https://github.com/jin-castle).

한국어 안내: 원본 자료의 권리는 각 권리자에게 있습니다. 아래의 출처와 프로젝트 추가 작업은 모든 파일의 독립 창작이나 단독 소유를 입증하는 목록이 아닙니다. 코드 재구성은 기존 라이선스 의무를 없애지 않으며, AI 산출물 전체에 독점 저작권을 주장하지 않습니다.

Readable site policies: [한국어](https://jin-castle.github.io/meep-examples/rights-and-licenses/) / [English](https://jin-castle.github.io/meep-examples/en/rights-and-licenses/).

This mixed educational repository does not grant a new repository-wide software license. Existing upstream and file-specific licenses prevail. Original protectable editorial additions are reserved unless separately licensed; this does not restrict third-party permissions or statutory exceptions, claim ownership of scientific facts, or assert exclusive human copyright over entire AI outputs. AI tools have assisted code, translation and illustration workflows.

## 1. Scope and limits of this inventory

This inventory records references and project additions found in the current sources, not a line-by-line comparison with every historical upstream revision. The top-level scientific Python programs have descriptive headers and cite official examples, but their original files do not consistently carry per-file copyright/license notices. Several explicitly adapt official example cases. Their independent-versus-derived status has not been established for every statement; they must not all be described as independently authored Python controls.

Meep links using `master` and documentation links using `latest` are moving references. The published calculations identify Meep 1.33.0, but that does not pin each example's historical source. Optical-beams provenance is separately commit-pinned below. Citations to papers and documentation identify references; they do not relicense their text or figures.

Project additions include bilingual educational explanations, a guided learning sequence, additional parameter sweeps and checks, `code/blogfig.py` figure/animation helpers, execution and rendering records, website layouts, themes and interactions. A description of added work is not a claim of sole human authorship of all resulting material.

## 2. Meep software and official examples

- Project: [Meep](https://github.com/NanoComp/meep).
- Official clarification: [License and Copyright](https://meep.readthedocs.io/en/latest/License_and_Copyright/).
- Upstream software notice: [COPYRIGHT](https://github.com/NanoComp/meep/blob/495abd14cb26854df61110987c66e0cc08f8e9e9/COPYRIGHT).
- Software license: GNU General Public License, version 2 or (at your option) any later version.
- Verbatim GPL version 2 text retained here: [LICENSES/Meep-GPL-2.0.txt](LICENSES/Meep-GPL-2.0.txt). The version-2-or-later grant is in the upstream copyright notice; including this license text does not assign one license to every file in this repository.

Upstream copyright and distribution notice:

```text
/* Copyright (C) 2005-2026 Massachusetts Institute of Technology
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
```

The official clarification distinguishes user-written Python/Scheme control files loaded at runtime **which do not contain code distributed with Meep** from derived works. Running Meep alone does not automatically make such independent controls GPL works. Conversely, reorganizing, translating, renaming or modifying copied Meep code does not remove its applicable copyright/license conditions. Preserve applicable notices, modification information and required source when distributing derivatives. No part of this page claims that a structural refactor alone makes a file independent.

The chapter inventory below identifies the examples and tutorials referenced by this project. Its qualification above remains applicable to local implementations and embedded code listings.

## 3. Optical-beams-MEEP

- Project authors: Daniel Kotik and Jörg Götte.
- [Project documentation](https://danielkotik.github.io/Optical-beams-MEEP/).
- [Pinned source commit ca145119e5bd0f0804d846ea42e35e4c3daa91de](https://github.com/DanielKotik/Optical-beams-MEEP/tree/ca145119e5bd0f0804d846ea42e35e4c3daa91de).
- Software citation: Optical-beams-MEEP v2.1.2 (2021), [doi:10.5281/zenodo.5211251](https://doi.org/10.5281/zenodo.5211251).
- License: MIT License, **Copyright (c) 2018 Daniel Kotik**.
- Retained full notice: [code/optical_beams/source/LICENSE](code/optical_beams/source/LICENSE).
- Retained authorship/citation metadata: [code/optical_beams/source/CITATION.cff](code/optical_beams/source/CITATION.cff).
- Vendored scope: `code/optical_beams/source/`, including Python/Scheme Gauss2d, Airy2d and LaguerreGauss3d scripts, `optbeam` implementations/declarations and notices.

The upstream source files are preserved without modification. Seven documented project execution/rendering additions are `run_original.py`, `run_gallery.py`, `render_results.py`, `render_curved.py`, `prepare_vortex_scene.py`, `render_vortex_blender.py` and `render_gallery.py`. They add observations, native-grid export, analytical source-integral reduction checks and rendering; this does not transfer rights in the upstream implementation.

[Reproduction notes](code/optical_beams/README.md) document actual conditions and limitations. Source/release comparisons recorded there cover the identified files, not a blanket assertion that every vendored file equals the software release. Provenance, checks and results are under `assets/meep/optical-beams/`.

### Reused upstream image in a comparison

`assets/meep/optical-beams/gallery/vortex_3d_comparison.png` includes an original upstream image in its left panel:

- Original: [scripts/Laguerre_Gauss_3d/img/vortex_beam_m_2_3d_half_resized.png](https://github.com/DanielKotik/Optical-beams-MEEP/blob/ca145119e5bd0f0804d846ea42e35e4c3daa91de/scripts/Laguerre_Gauss_3d/img/vortex_beam_m_2_3d_half_resized.png).
- Attribution: Daniel Kotik's Optical-beams-MEEP project, with upstream project MIT notice retained above. This panel is not claimed as a newly generated project result.
- [Comparison provenance](assets/meep/optical-beams/gallery/comparison-provenance.json) records original dimensions, hash and URL.
- The accompanying middle/right panels compare the earlier project rendering and the native-grid rerender. Historical upstream image parameters are incomplete; pixel-identical reproduction is not claimed.

## 4. Browser and site dependencies

### GSAP 3.15.0

- Local file: `assets/vendor/gsap-3.15.0.min.js`, unmodified core browser distribution.
- Source: [official npm archive](https://registry.npmjs.org/gsap/-/gsap-3.15.0.tgz) / [upstream tag](https://github.com/greensock/GSAP/tree/3.15.0).
- License: [GSAP Standard License](https://gsap.com/standard-license/), **not MIT**.
- Original header retains `Copyright 2026, GreenSock. All rights reserved.`, the license URL and author Jack Doyle.
- Used for homepage timeline sequencing; see [vendor notes](assets/vendor/README.md).

### MathJax 2.7.9

- Loaded remotely by `_includes/custom-head.html` from `https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.9/MathJax.js?config=TeX-AMS_CHTML`.
- License: [Apache License 2.0 at tag 2.7.9](https://github.com/mathjax/MathJax/blob/2.7.9/LICENSE).
- It is a remotely served runtime dependency, not an original project implementation or a vendored source tree.

### GitHub Pages / Jekyll build environment

`_config.yml` selects Minima, jekyll-feed, jekyll-seo-tag, kramdown and Rouge. GitHub Pages supplies Jekyll and the theme/build dependencies; exact installed versions are not pinned in this repository. The links below identify their upstream notices, rather than asserting a particular deployment version.

- [Jekyll notice](https://github.com/jekyll/jekyll/blob/master/LICENSE).
- [Minima notice](https://github.com/jekyll/minima/blob/master/LICENSE.txt): Copyright (c) 2016-present Parker Moore and the minima contributors; MIT License.
- [jekyll-feed notice](https://github.com/jekyll/jekyll-feed/blob/master/LICENSE.txt).
- [jekyll-seo-tag notice](https://github.com/jekyll/jekyll-seo-tag/blob/master/LICENSE.txt).
- [kramdown notice](https://github.com/gettalong/kramdown/blob/master/COPYING).
- [Rouge repository and notices](https://github.com/rouge-ruby/rouge).

The CSS font stack names locally installed fallback families, including Pretendard, Noto Sans KR, Apple SD Gothic Neo and Malgun Gothic. No font binaries or remote font stylesheets are bundled/loaded by this project's current custom styles. Naming a fallback family does not claim rights to that font.

### Scientific and rendering tools

Local scientific/rendering scripts also import or invoke tools such as NumPy, SciPy, Matplotlib, h5py, Meep/MPB, meep.adjoint, NLopt, VTK and Blender. They are execution-environment dependencies, rather than vendored implementations claimed by this project. See the relevant script imports, run records and Optical-beams reproduction notes for the versions used. This document does not relicense those tools or claim to be an exhaustive transitive dependency bill of materials.

## 5. Concept illustrations and numerical figures

`assets/illustrations/` contains 56 imagegen-produced PNGs: 14 chapters x Korean/English x light/dark. [manifest.json](assets/illustrations/manifest.json) records prompts, dimensions and hashes. They are explanatory concept illustrations, **not FDTD output or optimized geometry**.

AI assistance also applies to code and translation workflows. No exclusive human copyright in entire AI outputs is asserted. Any protectable human-authored/edited/arranged contributions must be assessed on their actual contribution. An asset hash or prompt record establishes neither copyright registration nor exclusive title.

Numerical field, spectrum, density and animation assets under `assets/meep/` are associated with the published execution/rendering code and records, except for explicitly attributed reused material such as the comparison panel above. Producing a new rendering does not relicense its upstream code/model or transfer another contributor's rights. Scientific facts and bare values are not claimed as exclusive property.

## 6. Chapter and topic inventory

The site inventory is maintained in [`_data/sources.json`](_data/sources.json). Update it, this file and both rights pages together when provenance or reuse conditions change. Lesson pages retain further API references, analytical comparisons and research citations.

### 01 · Point and line sources

- Local page: [한국어](https://jin-castle.github.io/meep-examples/point-line-source/) / [English](https://jin-castle.github.io/meep-examples/en/point-line-source/).
- Local implementation: `code/point_line_source.py`.
- Upstream references: [Meep Basics · Fields in a Waveguide](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#fields-in-a-waveguide); [Meep · Radiation Pattern of an Antenna](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-an-antenna).
- Project additions: An educational comparison of point and line sources in an empty cell, wavefront and pulse-timing explanations, four-sided flux accounting, figures and GIFs.
- 프로젝트 추가 작업: 빈 공간의 점원·선원 비교, 파면과 펄스 시각 설명, 네 면의 flux 비교, 그림과 GIF를 교육용 실험으로 구성했습니다.

### 02 · Boundaries and PML

- Local page: [한국어](https://jin-castle.github.io/meep-examples/boundary-pml/) / [English](https://jin-castle.github.io/meep-examples/en/boundary-pml/).
- Local implementation: `code/boundary_pml.py`.
- Upstream references: [Meep · Perfectly Matched Layer](https://meep.readthedocs.io/en/latest/Perfectly_Matched_Layer/); [Meep · absorber-1d.py](https://github.com/NanoComp/meep/blob/master/python/examples/absorber-1d.py).
- Project additions: Comparable reflecting-boundary, Absorber and PML experiments, reflection measurements using a padded reference, thickness/resolution comparisons and a GIF.
- 프로젝트 추가 작업: 반사 경계·Absorber·PML을 같은 기준으로 비교하고, 기준 계산을 뺀 반사 측정, 두께·해상도 비교와 GIF를 추가했습니다.

### 03 · Reference subtraction

- Local page: [한국어](https://jin-castle.github.io/meep-examples/reference-subtraction/) / [English](https://jin-castle.github.io/meep-examples/en/reference-subtraction/).
- Local implementation: `code/reference_subtraction.py`.
- Upstream references: [Meep · refl-quartz.py](https://github.com/NanoComp/meep/blob/master/python/examples/refl-quartz.py); [Meep · cylinder_cross_section.py](https://github.com/NanoComp/meep/blob/master/python/examples/cylinder_cross_section.py); [Meep Basics · Waveguide-bend normalization](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend).
- Project additions: Fresnel checks, incident/total/scattered-field comparisons for a 2D cylinder, reflected/transmitted/side-flux accounting and a scattering-cross-section check.
- 프로젝트 추가 작업: Fresnel 식과의 대조, 2D 원통의 입사장·전체장·산란장 비교, 반사·투과·측면 flux 수지와 산란 단면적 검사를 구성했습니다.

### 04 · Straight waveguides and guided modes

- Local page: [한국어](https://jin-castle.github.io/meep-examples/straight-waveguide/) / [English](https://jin-castle.github.io/meep-examples/en/straight-waveguide/).
- Local implementation: `code/straight_waveguide.py`.
- Upstream references: [Meep · Mode Decomposition](https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/); [Meep · EigenModeSource](https://meep.readthedocs.io/en/latest/Python_User_Interface/#eigenmodesource).
- Project additions: MPB modes and effective-index explanations, modal-power versus total-flux comparisons, and resolution/PML checks.
- 프로젝트 추가 작업: MPB 모드와 유효 굴절률을 살펴보고, 모드별 전력과 전체 flux를 비교하며 해상도·PML 검사를 추가했습니다.

### 05 · Waveguide bends and bend radius

- Local page: [한국어](https://jin-castle.github.io/meep-examples/waveguide-bend-90/) / [English](https://jin-castle.github.io/meep-examples/en/waveguide-bend-90/).
- Local implementation: `code/bend90.py`.
- Upstream references: [Meep Basics · Transmittance Spectrum of a Waveguide Bend](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend).
- Project additions: Rounded bends, a radius sweep, loss comparisons and verification figures alongside the official sharp-bend baseline.
- 프로젝트 추가 작업: 공식 예제의 직각 굽힘을 기준으로 둥근 굽힘, 반지름 sweep, 손실 비교와 검증 그림을 추가했습니다.

### 06 · Binary gratings and diffraction orders

- Local page: [한국어](https://jin-castle.github.io/meep-examples/binary-grating/) / [English](https://jin-castle.github.io/meep-examples/en/binary-grating/).
- Local implementation: `code/binary_grating.py`.
- Upstream references: [Meep · binary_grating.py](https://github.com/NanoComp/meep/blob/master/python/examples/binary_grating.py); [Meep · Diffraction Spectrum of a Binary Grating](https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#diffraction-spectrum-of-a-binary-grating).
- Project additions: An educational case with an adjusted period, duty-cycle phase comparisons, a finite grating, FFT-based beam-angle checks, figures and GIFs.
- 프로젝트 추가 작업: 주기를 조정한 교육용 사례, duty cycle에 따른 위상 비교, 유한 격자와 FFT 방사각 검사, 그림·GIF를 구성했습니다.

### 07 · Meta-atoms and phase libraries

- Local page: [한국어](https://jin-castle.github.io/meep-examples/meta-atom/) / [English](https://jin-castle.github.io/meep-examples/en/meta-atom/).
- Local implementation: `code/meta_atom.py`.
- Upstream references: [Meep · metasurface_lens.py](https://github.com/NanoComp/meep/blob/master/python/examples/metasurface_lens.py); [Meep · binary_grating_phasemap.py](https://github.com/NanoComp/meep/blob/master/python/examples/binary_grating_phasemap.py).
- Project additions: A width-to-phase library, four-level phase selection, supercell order-power accounting and far-field comparisons for 10- and 40-atom arrays.
- 프로젝트 추가 작업: 폭에 따른 위상 라이브러리, 4단계 위상 선택, supercell의 차수별 전력과 10·40개 원자의 원거리장 비교를 구성했습니다.

### 08 · Metagrating inverse design

- Local page: [한국어](https://jin-castle.github.io/meep-examples/metagrating-inverse/) / [English](https://jin-castle.github.io/meep-examples/en/metagrating-inverse/).
- Local implementation: `code/metagrating_inverse.py`.
- Upstream references: [Meep · Adjoint Solver](https://meep.readthedocs.io/en/latest/Python_Tutorials/Adjoint_Solver/); [Meep · 01-Introduction.ipynb](https://github.com/NanoComp/meep/blob/master/python/examples/adjoint_optimization/01-Introduction.ipynb); [NLopt · MMA](https://nlopt.readthedocs.io/en/latest/NLopt_Algorithms/#mma-method-of-moving-asymptotes-and-ccsa).
- Project additions: An inverse-design problem building on lesson 07, finite-difference gradient checks, a short MMA demonstration and verification in a fresh forward simulation.
- 프로젝트 추가 작업: 07편의 격자를 역설계 문제로 구성하고, 유한차분 gradient 검사, 짧은 MMA 최적화와 새로운 forward 계산을 통한 검증을 추가했습니다.

### 09 · Waveguide-bend inverse design

- Local page: [한국어](https://jin-castle.github.io/meep-examples/bend-inverse/) / [English](https://jin-castle.github.io/meep-examples/en/bend-inverse/).
- Local implementation: `code/bend_inverse.py`, `code/highres_bend/README.md`.
- Upstream references: [Meep · Adjoint Solver](https://meep.readthedocs.io/en/latest/Python_Tutorials/Adjoint_Solver/); [Meep · 01-Introduction.ipynb](https://github.com/NanoComp/meep/blob/master/python/examples/adjoint_optimization/01-Introduction.ipynb); [Meep · 02-Filtered_Waveguide_Bend.ipynb](https://github.com/NanoComp/meep/blob/master/python/examples/adjoint_optimization/02-Filtered_Waveguide_Bend.ipynb).
- Project additions: A free design region, gradient checks, short optimization and resolution rechecks, with computed forward/adjoint/sensitivity views and a scroll sequence explaining geometry updates.
- 프로젝트 추가 작업: 자유 설계 영역, gradient 검사, 짧은 최적화와 해상도 재검사를 구성했습니다. forward·adjoint·민감도·구조 갱신을 계산 결과와 스크롤 장면으로 설명합니다.

### 10 · 3D dipole radiation patterns

- Local page: [한국어](https://jin-castle.github.io/meep-examples/dipole-pattern-3d/) / [English](https://jin-castle.github.io/meep-examples/en/dipole-pattern-3d/).
- Local implementation: `code/dipole_pattern_3d.py`.
- Upstream references: [Meep · Near-to-Far Field Spectra](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/); [Meep · dipole_in_vacuum_1D.py](https://github.com/NanoComp/meep/blob/master/python/examples/dipole_in_vacuum_1D.py); [Meep · antenna_pec_ground_plane.py](https://github.com/NanoComp/meep/blob/master/python/examples/antenna_pec_ground_plane.py).
- Project additions: A reduced angular grid for 1D Bloch calculations, analytical checks and comparisons with image-dipole near-to-far calculations above a PEC mirror, plus figures and GIFs.
- 프로젝트 추가 작업: 각도 격자를 줄인 1D Bloch 계산, 해석식 비교, PEC 거울의 image-dipole near2far와 비교하는 그림·GIF를 추가했습니다.

### 11 · Cavity LDOS and Purcell factors

- Local page: [한국어](https://jin-castle.github.io/meep-examples/cavity-ldos/) / [English](https://jin-castle.github.io/meep-examples/en/cavity-ldos/).
- Local implementation: `code/cavity_ldos.py`.
- Upstream references: [Meep · Local Density of States](https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/); [Meep · planar_cavity_ldos.py](https://github.com/NanoComp/meep/blob/master/python/examples/planar_cavity_ldos.py); [Meep · metal-cavity-ldos.py](https://github.com/NanoComp/meep/blob/master/python/examples/metal-cavity-ldos.py).
- Project additions: A reduced sweep, cylindrical/3D cross-checks, comparisons with the analytical expression by Abram et al., and figures explaining convergence limits under a runtime cap.
- 프로젝트 추가 작업: 축소한 sweep, cylindrical·3D 교차검증, Abram 등의 해석식과 대조, 제한한 실행 시간에서의 수렴 한계를 설명하는 그림을 추가했습니다.

### 12 · Ring resonators

- Local page: [한국어](https://jin-castle.github.io/meep-examples/ring-resonator/) / [English](https://jin-castle.github.io/meep-examples/en/ring-resonator/).
- Local implementation: `code/ring_resonator.py`.
- Upstream references: [Meep Basics · Modes of a Ring Resonator](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#modes-of-a-ring-resonator); [Meep · ring.py](https://github.com/NanoComp/meep/blob/master/python/examples/ring.py); [Meep · solve-cw.py](https://github.com/NanoComp/meep/blob/master/python/examples/solve-cw.py); [Meep · ring-mode-overlap.py](https://github.com/NanoComp/meep/blob/master/python/examples/ring-mode-overlap.py).
- Project additions: Resolution comparisons, individual mode images, azimuthal mode-number counting, and time-domain DFT versus solve_cw cross-checks.
- 프로젝트 추가 작업: 해상도 비교, 개별 모드 영상과 방위 차수 계산, 시간 영역 DFT와 solve_cw의 교차검증을 구성했습니다.

### 13 · Cylindrical coordinates and rotational symmetry

- Local page: [한국어](https://jin-castle.github.io/meep-examples/cylindrical-dipole/) / [English](https://jin-castle.github.io/meep-examples/en/cylindrical-dipole/).
- Local implementation: `code/cylindrical_dipole.py`.
- Upstream references: [Meep · Cylindrical Coordinates](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/); [Meep · dipole_in_vacuum_cyl_on_axis.py](https://github.com/NanoComp/meep/blob/master/python/examples/dipole_in_vacuum_cyl_on_axis.py); [Meep · dipole_in_vacuum_cyl_off_axis.py](https://github.com/NanoComp/meep/blob/master/python/examples/dipole_in_vacuum_cyl_off_axis.py); [Meep · ring-cyl.py](https://github.com/NanoComp/meep/blob/master/python/examples/ring-cyl.py); [Meep · disc_radiation_pattern.py](https://github.com/NanoComp/meep/blob/master/python/examples/disc_radiation_pattern.py).
- Project additions: Azimuthal-series convergence comparisons, Cartesian field reconstruction, ring/disc radiation comparisons, geometry figures and GIFs.
- 프로젝트 추가 작업: m 급수의 수렴 비교, 직교 좌표 장 복원, 고리와 디스크 방사 비교, 구조 그림과 GIF를 구성했습니다.

### 14 · Light extraction from a thin film

- Local page: [한국어](https://jin-castle.github.io/meep-examples/extraction-efficiency/) / [English](https://jin-castle.github.io/meep-examples/en/extraction-efficiency/).
- Local implementation: `code/extraction_efficiency.py`, `code/extraction_layouts.py`.
- Upstream references: [Meep · Extraction Efficiency of an LED](https://meep.readthedocs.io/en/latest/Python_Tutorials/Local_Density_of_States/#extraction-efficiency-of-a-light-emitting-diode-led); [Meep · extraction_eff_ldos.py](https://github.com/NanoComp/meep/blob/master/python/examples/extraction_eff_ldos.py); [Meep · point_dipole_cyl.py](https://github.com/NanoComp/meep/blob/master/python/examples/point_dipole_cyl.py); [Meep · edge_emitter_2D.py](https://github.com/NanoComp/meep/blob/master/python/examples/edge_emitter_2D.py); [Meep · disc_extraction_efficiency.py](https://github.com/NanoComp/meep/blob/master/python/examples/disc_extraction_efficiency.py).
- Project additions: Height sweeps, coordinate/resolution checks, an extended azimuthal series compared with the official stopping rule, kz integration and an edge-emitter study.
- 프로젝트 추가 작업: 높이 sweep과 좌표·해상도 대조, 공식 종료 규칙보다 확장한 m 급수 비교, kz 적분과 edge-emitter 실험을 구성했습니다.

### Topic · Metalens phase maps and PB phase

- Local page: [한국어](https://jin-castle.github.io/meep-examples/metalens/) / [English](https://jin-castle.github.io/meep-examples/en/metalens/).
- Local implementation: `code/metalens_edge_patterns.py`, `code/metalens_radius_layout.py`, `code/metalens_three_types.py`, `code/metalens_phase_anim.py`, `code/metalens_ideal_pb.py`.
- Upstream references: [Khorasaninejad et al. · Science (2016)](https://doi.org/10.1126/science.aaf6644); [Arbabi et al. · Nature Communications (2015)](https://doi.org/10.1038/ncomms8069).
- Project additions: Phase derivation, wrapping, sampling and fin-rotation illustrations, plus a 1D scalar angular-spectrum check. Illustrative dimensions and the diameter-to-phase model do not reproduce the paper's device and are not FDTD results.
- 프로젝트 추가 작업: 위상 유도·접기·샘플링·fin 회전 도해와 1D 스칼라 각 스펙트럼 검사를 구성했습니다. 예시 치수와 직경–위상 모형은 논문 소자의 재현이나 FDTD 결과가 아닙니다.

### Topic · Optical-beam reproduction and visualization

- Local page: [한국어](https://jin-castle.github.io/meep-examples/optical-beams/) / [English](https://jin-castle.github.io/meep-examples/en/optical-beams/).
- Local implementation: `code/optical_beams/README.md`, `code/optical_beams/run_original.py`, `code/optical_beams/run_gallery.py`, `code/optical_beams/render_results.py`, `code/optical_beams/render_curved.py`, `code/optical_beams/prepare_vortex_scene.py`, `code/optical_beams/render_vortex_blender.py`, `code/optical_beams/render_gallery.py`.
- Upstream references: [Daniel Kotik & Jörg Götte · Optical-beams-MEEP](https://danielkotik.github.io/Optical-beams-MEEP/); [Optical-beams-MEEP · pinned source ca145119](https://github.com/DanielKotik/Optical-beams-MEEP/tree/ca145119e5bd0f0804d846ea42e35e4c3daa91de); [Optical-beams-MEEP v2.1.2 · software citation](https://doi.org/10.5281/zenodo.5211251).
- Project additions: Preserved upstream sources and MIT notice; added execution/observation wrappers, source-integral equivalence checks, native-grid field export and Blender rendering. The comparison figure's left panel reuses an upstream image.
- 프로젝트 추가 작업: 원본 소스·MIT 고지를 보존하고 실행·관측 wrapper, 소스 적분 동등성 검사, native-grid 장 내보내기와 Blender 렌더링을 추가했습니다. 비교 그림의 왼쪽 패널은 원본 프로젝트 이미지입니다.

## 7. Attribution corrections and permission requests

For source/credit corrections or permission concerning independently authored project additions, contact [jin-castle through the repository](https://github.com/jin-castle/meep-examples), identifying the relevant page/file, proposed use and source evidence. No inquiry is needed to exercise permissions already granted by an applicable third-party license.
