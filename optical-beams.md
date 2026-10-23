---
layout: topic
permalink: /optical-beams/
title: "Optical-beams-MEEP 실습 — Gaussian beam의 반사·굴절과 전반사"
title_en: "Optical-beams-MEEP lab — Gaussian beam reflection, refraction and total internal reflection"
lang: ko
topic_label: OPTICAL BEAMS
lesson_title: "유한한 빔이 경계면에 닿으면 어디로 갈까?"
lesson_summary: "Optical-beams-MEEP의 원본 Gaussian beam 코드를 실행해 입사각 30°와 45°를 비교합니다. 파면으로 진행 방향을 읽고, 제곱장 지도로 빛이 집중되는 위치를 확인합니다."
lesson_goals:
  - "평면파와 폭이 유한한 Gaussian beam의 차이를 설명합니다."
  - "Snell 법칙과 임계각으로 결과를 예측하고 실제 FDTD 그림과 비교합니다."
  - "순간 전기장, 시간평균 제곱장, 전력 투과율을 구분합니다."
lesson_prerequisites: "01편 광원 · 02편 PML · 03편 참조 계산"
calc_note: "실제 Meep 1.33.0 실행. 원본 Gauss2d.py의 광원·구조·해상도·실행 시간을 유지하고 관측만 추가했습니다."
toc:
  - { id: observe, label: "먼저 관찰하기" }
  - { id: predict, label: "방향 예측하기" }
  - { id: understand, label: "파면과 제곱장 읽기" }
  - { id: setup, label: "실제 계산 조건" }
  - { id: run, label: "직접 실행하기" }
  - { id: verify, label: "확인한 것과 한계" }
  - { id: reference, label: "출처와 다음 실습" }
related:
  - { url: "/point-line-source/", label: "01 · 점 광원과 선 광원" }
  - { url: "/reference-subtraction/", label: "03 · 반사율과 투과율을 정량적으로 재기" }
  - { url: "/metalens/", label: "Metalens · 위상으로 빛을 모으기" }
date: 2026-10-23
tags: [meep, gaussian-beam, optical-beams, snell, total-internal-reflection, fdtd]
image: /assets/meep/optical-beams/wavefront_comparison.png
excerpt: "Two real runs of the upstream Optical-beams-MEEP Gaussian-beam example: incidence at 30 and 45 degrees, signed wavefronts and cycle-averaged squared fields, with pinned source and reproducible commands."
---

<h2 id="observe">1. 먼저 관찰하기</h2>

얇은 선 하나로 광원을 그리는 것과 **폭이 있는 빔을 넣는 것**은 다릅니다. 빔의 가운데는 밝고 가장자리는 약하며, 멀리 갈수록 폭과 파면의 곡률이 바뀝니다. 이런 빔이 굴절률이 다른 경계면을 만나면 반사된 빔과 굴절된 빔이 생깁니다.

이 글은 Daniel Kotik과 Jörg Götte의 [Optical-beams-MEEP](https://danielkotik.github.io/Optical-beams-MEEP/)을 직접 실행한 실습입니다. 원본이 제공하는 여러 빔 중 **2D Gaussian beam과 평면 경계**를 골라, 입사각만 30°와 45°로 바꿨습니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/wavefront_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/wavefront_comparison.png" alt="입사각 30도와 45도에서 실제 계산한 Gaussian beam의 전기장 파면과 유전체 경계 비교" loading="eager"></a>
  <figcaption>빨강·파랑은 전기장 E<sub>z</sub>의 부호입니다. 밝고 어두운 세기 지도가 아니라, 파동의 마루와 골을 보는 그림입니다. 두 조건은 각각 실제 Meep으로 계산했습니다.</figcaption>
</figure>

**관찰할 것:** 경계에서 갈라지는 빔의 방향, 경계 너머 파면의 간격, 그리고 임계각 이상에서도 경계 가까이에 남는 장을 찾아보세요.

<details>
<summary>파면 움직임 보기 — 마지막 두 주기의 실제 시간 샘플</summary>
<div class="figure-pair">
  <figure class="lesson-figure lesson-animation">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/planar30.gif" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/planar30_wavefront.png" data-animation-src="{{ site.baseurl }}/assets/meep/optical-beams/planar30.gif" data-static-src="{{ site.baseurl }}/assets/meep/optical-beams/planar30_wavefront.png" alt="입사각 30도 Gaussian beam의 마지막 두 주기 실제 FDTD 파면 움직임" loading="lazy"></a>
    <figcaption>30°: 마지막 두 주기를 느리게 재생합니다. 빔이 처음 도착하는 과도 과정은 아닙니다.</figcaption>
    <button type="button" class="animation-toggle" hidden>애니메이션 재생</button>
  </figure>
  <figure class="lesson-figure lesson-animation">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/planar45.gif" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/planar45_wavefront.png" data-animation-src="{{ site.baseurl }}/assets/meep/optical-beams/planar45.gif" data-static-src="{{ site.baseurl }}/assets/meep/optical-beams/planar45_wavefront.png" alt="입사각 45도 Gaussian beam의 마지막 두 주기 실제 FDTD 파면 움직임" loading="lazy"></a>
    <figcaption>45°: 표시용 장만 공간 격자 세 칸마다 추렸습니다. 원본 계산 해상도는 유지했습니다.</figcaption>
    <button type="button" class="animation-toggle" hidden>애니메이션 재생</button>
  </figure>
</div>
</details>

<details markdown="1">
<summary>English summary</summary>

Two single-core Meep 1.33.0 runs execute the upstream `Gauss2d.py` model with a planar interface, s polarization, n₁ = 1.54 and n₂ = 1.00. Incidence angles of 30° and 45° lie below and above the plane-wave critical angle of 40.49°. The original source, geometry, resolution and duration are retained. A wrapper adds observations, including a harmonic fit over the final two periods. Its cycle-averaged squared field is distinguished from the upstream instantaneous real-field square. These figures are field visualizations, not measured reflectance or transmittance.

</details>

<h2 id="predict">2. 먼저 방향을 예측하기</h2>

입사각은 **경계면의 법선과 빔 진행 방향 사이의 각도**입니다. 화면의 가로·세로 축에 대한 각도와 혼동하지 마세요. 원본은 광원의 방향을 유지하면서 경계면을 기울여 입사각을 정합니다.

평면파라면 Snell 법칙은 다음과 같습니다.

$$n_1\sin\chi_i = n_2\sin\chi_t.$$

굴절률이 높은 쪽에서 낮은 쪽으로 나갈 때, 굴절각이 90°가 되는 입사각이 임계각입니다.

$$\chi_c = \arcsin(n_2/n_1) = \arcsin(1/1.54) \approx 40.49^\circ.$$

| 조건 | 평면파 이론으로 먼저 예상하는 것 |
|---|---|
| 입사각 30° | 굴절각 약 50.35°. 반사와 굴절이 함께 나타납니다. |
| 입사각 45° | 임계각 이상입니다. 이상적인 단일 평면파는 전반사하고, 낮은 굴절률 쪽에는 소멸장이 생깁니다. |

<fieldset class="prediction">
<legend>전반사라면 경계 반대쪽의 전기장도 반드시 0일까요?</legend>
<label><input type="radio" name="beam-prediction" value="zero"> 전반사이므로 경계 반대쪽에는 장이 전혀 없다.</label>
<label><input type="radio" name="beam-prediction" value="evanescent"> 경계 근처에 소멸장이 있을 수 있다.</label>
</fieldset>

<details markdown="1">
<summary>예측 확인하기</summary>

**두 번째입니다.** 전반사는 낮은 굴절률 쪽으로 멀리 전파하는 평면파의 법선 방향 평균 전력 흐름이 없다는 뜻입니다. 경계 가까이에는 지수적으로 줄어드는 소멸장이 존재할 수 있습니다.

또한 실제 Gaussian beam은 여러 진행 방향의 성분을 포함합니다. 중심 입사각 45°라는 이유만으로 이 유한 빔의 투과 전력을 정확히 0이라고 결론 내릴 수는 없습니다.

</details>

<h2 id="understand">3. 파면과 제곱장 지도를 함께 읽기</h2>

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/intensity_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/intensity_comparison.png" alt="동일한 두 Gaussian beam 실행에서 마지막 두 주기를 관측해 계산한 평균 전기장 제곱 비교" loading="lazy"></a>
  <figcaption>검은 배경의 hot 지도는 마지막 두 주기 관측으로 얻은 평균 제곱장입니다. 각 패널의 정규화는 색상 막대를 따릅니다. 색만 보고 두 실행의 반사율·투과율을 비교하지 않습니다.</figcaption>
</figure>

| 보고 싶은 것 | 적합한 표현 | 주의할 점 |
|---|---|---|
| 파면의 간격, 굽음, 진행 방향 | 빨강·파랑의 순간 E<sub>z</sub> | 0을 지나는 마디도 어둡거나 희게 보입니다. |
| 빔이 모이는 위치와 넓이 | 시간평균 E<sub>z</sub>² | 전기장 제곱이며 전력 투과율 자체가 아닙니다. |
| 정확한 반사율과 투과율 | 참조 실행으로 정규화한 Poynting flux | 이 실습에서는 측정하지 않았습니다. 03편의 절차가 추가로 필요합니다. |

원본은 `force_complex_fields=False`이므로 마지막에 저장하는 `e2_s`가 **그 시각의 실수 전기장 제곱**입니다. 여기서는 원본 계산에 관측을 추가해 마지막 두 주기의 실제 장을 표본화하고, 아래 형태로 맞췄습니다.

$$E_z(t) = A\cos(\omega t) + B\sin(\omega t) + C,$$

여기서 단일 주파수 성분의 평균 제곱장은 $(A^2+B^2)/2$입니다. 이는 순간장의 제곱에서 보이는 빠른 줄무늬를 평균한 값입니다. 짧은 관측 구간의 조화 성분 추정이므로, 완전히 수렴한 정상상태나 광대역 해석을 대신하지는 않습니다.

<h2 id="setup">4. 실제 계산 조건</h2>

| 항목 | 이번 실행 |
|---|---|
| 원본 | `scripts/Gauss_2d/Gauss2d.py`, optbeam 2.1.2 |
| 소스 고정 | commit `ca145119e5bd0f0804d846ea42e35e4c3daa91de` |
| 계산기 | Meep 1.33.0, CPU 한 코어 |
| 차원·편광 | 2D, s 편광 E<sub>z</sub> |
| 굴절률 | 입사 매질 1.54, 반대 매질 1.00 |
| 입사각 | 30° / 45° |
| 계산 셀·PML | 5a × 5a, 가장자리 PML 두께 0.25a |
| 진공 주파수 | f = 12 c/a, 진공 파장 λ₀ = a/12 |
| 해상도 | 184.8 pixels/a, 높은 굴절률 매질에서 파장당 10 pixels |
| 시간 | 10 a/c = 진공 광학 주기 120개 |

여기서 a는 사용자가 정하는 길이 단위입니다. 별도로 a를 μm에 대응시키지 않았으므로 축의 수치를 그대로 μm라고 읽지 않습니다. 원본의 `kw_0=8`, `kr_w=60`, `ref_medium=0`도 유지했습니다. 빔의 waist는 소스 평면과 독립적으로 정할 수 있습니다.

<h2 id="run">5. 직접 실행하기</h2>

먼저 Meep이 설치된 환경에서 원본을 고정된 버전으로 받습니다. optbeam은 저장소의 Python 구현을 사용하며, 이 실습에서는 Cython 확장을 새로 설치하지 않았습니다.

```bash
git clone https://github.com/DanielKotik/Optical-beams-MEEP.git
cd Optical-beams-MEEP
git checkout ca145119e5bd0f0804d846ea42e35e4c3daa91de
export PYTHONPATH="$PWD"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

python scripts/Gauss_2d/Gauss2d.py -interface planar -chi_deg 30
python scripts/Gauss_2d/Gauss2d.py -interface planar -chi_deg 45
```

위 명령은 원본 HDF5 결과를 만듭니다. 두 실행은 출력 폴더가 같으므로 **첫 실행의 결과를 별도로 보관한 뒤** 두 번째를 실행하세요. 이 사이트의 파면·평균 제곱장 그림까지 다시 만들려면 [관측 wrapper와 실행 안내](https://github.com/jin-castle/meep-examples/tree/main/code/optical_beams)를 사용합니다. Wrapper는 원본 파일을 고치지 않고 실행별 폴더와 추가 관측을 관리합니다.

<h2 id="verify">6. 확인한 것과 아직 측정하지 않은 것</h2>

- 두 조건을 실제 Meep으로 실행하고 종료 상태와 유한한 장 배열을 확인했습니다.
- 그림은 해당 실행에서 저장한 장과 유전율에서 만들었습니다. 원본 웹사이트의 예시 이미지를 결과로 사용하지 않았습니다.
- 마지막 두 주기의 조화 성분 적합과 관련된 검사는 [checks.json]({{ site.baseurl }}/assets/meep/optical-beams/checks.json), 소스 버전과 실행 출처는 [provenance.json]({{ site.baseurl }}/assets/meep/optical-beams/provenance.json)에 기록했습니다.
- Snell 법칙의 굴절각과 임계각은 **평면파 이론의 기준값**입니다. 아래의 국소 위상 기울기 진단과 구분합니다.
- 해상도 수렴, PML 두께 수렴, 정규화한 R·T, Goos–Hänchen 이동량은 이번 실습의 검증 범위에 포함하지 않았습니다.

| 실제 관측 검사 | 30° 실행 | 45° 실행 |
|---|---|---|
| 마지막 두 주기의 표본 수 | 62 | 62 |
| 조화 성분 적합의 상대 L2 잔차 | 0.0822% | 0.0207% |
| 파면으로 추정한 반사 진행 방향, +x 기준 | 119.98° (이론 120°) | 90.85° (이론 90°) |

30° 실행의 굴절장에서는 국소 복소장 위상 기울기로 법선 기준 약 **50.66°**를 얻었습니다. Snell 법칙의 50.35°와 차이는 약 0.31°입니다. 이는 경계와 PML에서 떨어진 좁은 구간에서 제곱장으로 가중한 **국소 파면 방향**이며, 빔 중심의 이동 방향이나 전력 측정은 아닙니다. 유한한 빔 폭과 유한 격자에서의 관찰을 평면파 기준값과 비교하는 검사로 사용합니다.

이 그림은 빔이 경계에서 어떻게 갈라지는지 익히는 출발점입니다. 소자 성능을 계산하려면 파장당 격자를 늘려 수렴을 확인하고, 입사·반사·투과를 분리하는 참조 실행과 flux 측정이 이어져야 합니다.

<h2 id="reference">7. 출처와 다음 실습</h2>

- **원본 프로젝트:** [Optical-beams-MEEP 문서](https://danielkotik.github.io/Optical-beams-MEEP/) · [고정한 소스 버전](https://github.com/DanielKotik/Optical-beams-MEEP/tree/ca145119e5bd0f0804d846ea42e35e4c3daa91de)
- **소프트웨어 인용:** Daniel Kotik, Jörg Götte, Optical-beams-MEEP v2.1.2, [DOI: 10.5281/zenodo.5211251](https://doi.org/10.5281/zenodo.5211251). 이는 소프트웨어 버전의 DOI입니다.
- **라이선스:** 원본 MIT 저작권·허가문을 [복사한 소스와 함께 보존](https://github.com/jin-castle/meep-examples/tree/main/code/optical_beams/source)했습니다.
- **이 사이트의 추가 작업:** 실행별 기록, 마지막 두 주기 관측, 그림 렌더링, 한국어 설명입니다.

원본은 Gaussian beam의 오목·볼록 경계, Airy beam, 3D Laguerre–Gaussian vortex beam도 제공합니다. 이번에 실행한 것은 위의 **평면 경계 Gaussian beam 두 조건**입니다. 다음 실습에서는 `-interface concave`와 `-interface convex`로 곡면이 빔의 진행과 폭을 어떻게 바꾸는지 비교할 수 있습니다.
