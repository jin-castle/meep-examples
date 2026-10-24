---
layout: topic
permalink: /optical-beams/
title: "Optical-beams-MEEP 실습 — 곡면 Gaussian, 3D vortex와 Airy beam"
title_en: "Optical-beams-MEEP lab — curved interfaces, 3D vortex and Airy beams"
lang: ko
topic_label: OPTICAL BEAMS
lesson_title: "빔의 파면은 왜 휘고, 나선으로 돌까?"
lesson_summary: "평면·오목·볼록 경계의 Gaussian beam을 비교하고, 3D vortex와 Airy beam을 직접 계산합니다. 검은 배경의 밝은 줄무늬를 따라 파면과 간섭을 읽어 봅니다."
lesson_goals:
  - "같은 Gaussian beam의 평면·오목·볼록 경계 결과를 비교합니다."
  - "Vortex의 위상 감김과 Airy beam의 휘는 밝은 무늬를 구분합니다."
  - "순간 전기장 제곱, 시간평균 제곱장, 전력 투과율을 구분합니다."
lesson_prerequisites: "01편 광원 · 02편 PML · 03편 참조 계산"
calc_note: "실제 Meep 1.33.0 · CPU 한 코어. Gaussian 4조건, 3D Laguerre–Gaussian, 자유공간 Airy. 원본 격자·종료 시간 유지."
toc:
  - { id: observe, label: "첨부 그림의 빔부터 보기" }
  - { id: curved, label: "평면·오목·볼록 비교" }
  - { id: vortex, label: "3D vortex 읽기" }
  - { id: airy, label: "Airy beam 읽기" }
  - { id: understand, label: "밝은 줄무늬의 뜻" }
  - { id: predict, label: "Snell 법칙과 평면 경계" }
  - { id: setup, label: "실제 계산 조건" }
  - { id: run, label: "직접 실행하기" }
  - { id: verify, label: "검증과 한계" }
  - { id: reference, label: "출처와 라이선스" }
related:
  - { url: "/point-line-source/", label: "01 · 점 광원과 선 광원" }
  - { url: "/reference-subtraction/", label: "03 · 반사율과 투과율을 정량적으로 재기" }
  - { url: "/metalens/", label: "Metalens · 위상으로 빛을 모으기" }
date: 2026-10-24
tags: [meep, gaussian-beam, optical-beams, vortex, airy, curved-interface, fdtd]
image: /assets/meep/optical-beams/gallery/reference_gallery.png
excerpt: "Real single-core Meep runs of curved Gaussian interfaces, a 3D charge-two vortex and a free-space Airy beam, rendered as instantaneous squared real fields."
---

<h2 id="observe">1. 첨부 그림의 빔부터 보기</h2>

나선처럼 보이는 밝은 무늬, 가운데가 빈 횡단면, 그리고 스스로 휘는 듯한 빔. [Optical-beams-MEEP](https://danielkotik.github.io/Optical-beams-MEEP/)의 코드를 실제 Meep으로 실행해 새로 그렸습니다. 위쪽 세 장은 **3D Laguerre–Gaussian vortex**, 아래쪽은 **자유공간 Airy beam**입니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/reference_gallery.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/reference_gallery.png" alt="실제 Meep으로 계산한 charge 2 vortex의 종단면·횡단면·3D 단면과 자유공간 Airy beam" loading="eager"></a>
  <figcaption>검정→빨강→노랑→흰색은 순간 실수 전기장의 제곱입니다. LG는 세 성분의 제곱 합, Airy는 E<sub>z</sub>²입니다. LG의 별도 2D 그림은 전체 최대값의 20%, 3D 안의 두 단면은 2%를 색상 상한으로 사용합니다. Airy는 자체 최대값을 사용하며 서로의 전력을 비교하는 척도가 아닙니다.</figcaption>
</figure>

**먼저 볼 것:** vortex의 횡단면에는 왜 네 개의 밝은 날개가 있을까요? Airy의 밝은 줄은 왜 직선으로 가지 않을까요? 곡면 경계를 만나면 같은 Gaussian beam은 어떻게 달라질까요?

원본 웹사이트의 PNG를 결과로 가져온 것이 아닙니다. 같은 종류의 빔을 계산하고, 첨부 그림처럼 빠른 줄무늬가 남는 **순간장 제곱**으로 표시했습니다. 원본 PNG의 모든 실행 조건이 기록되어 있지는 않아 픽셀 단위 재현을 주장하지 않습니다.

<h2 id="curved">2. 같은 빔, 평면·오목·볼록 경계</h2>

빔은 그대로 두고 경계의 모양만 바꿉니다. 세 조건 모두 원점의 경계 법선을 기준으로 입사각 45°, 입사 매질 굴절률 1.54, 반대 매질 1.00입니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/curved/curved_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/curved/curved_comparison.png" alt="동일한 Gaussian beam의 45도 평면·오목·볼록 경계에서의 순간 전기장 제곱 비교" loading="lazy"></a>
  <figcaption>공통 종료 시각 t=10 a/c의 E<sub>z</sub>(t)². 약한 무늬까지 읽도록 각 패널의 최대값으로 정규화했습니다. 주석을 포함한 공통 밝기 척도는 아래에서 펼쳐 볼 수 있습니다.</figcaption>
</figure>

| 경계 | 비교할 것 |
|---|---|
| 평면 | 법선이 일정합니다. 입사파와 반사파가 겹쳐 만드는 줄무늬가 기준입니다. |
| 오목 concave | 위치마다 법선이 달라집니다. 반사파의 굽음과 겹치는 무늬의 간격·방향을 관찰하세요. |
| 볼록 convex | 곡률의 부호가 반대입니다. 퍼지는 방향과 경계 가까운 장의 분포를 오목 조건과 비교하세요. |

곡면에서 **45°는 원점에서의 값**입니다. 경계의 모든 위치에 같은 각도로 입사한다는 뜻은 아닙니다. 원형 경계 반지름은 약 1.9894a입니다. 빔의 여러 성분이 서로 다른 위치와 법선에 닿으므로, 평면 경계의 임계각만으로 곡면 결과 전체를 판정하기 어렵습니다.

<details>
<summary>경계·소스 위치와 공통 밝기 척도 확인하기</summary>
<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/curved/curved_common_scale.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/curved/curved_common_scale.png" alt="평면·오목·볼록 결과를 공통 최대값과 선형 hot 색상 척도로 비교하고 경계와 소스 위치를 표시" loading="lazy"></a>
  <figcaption>하나의 공통 최대값을 사용하는 선형 척도입니다. 회색은 실제 유전율에서 얻은 경계, 청록은 소스 구간입니다. 개별 정규화 그림의 밝기와 구분해 읽으세요.</figcaption>
</figure>
</details>

실제 시간 샘플의 움직임도 [평면 GIF]({{ site.baseurl }}/assets/meep/optical-beams/curved/planar45_hot.gif) · [오목 GIF]({{ site.baseurl }}/assets/meep/optical-beams/curved/concave45_hot.gif) · [볼록 GIF]({{ site.baseurl }}/assets/meep/optical-beams/curved/convex45_hot.gif)로 비교할 수 있습니다. 마지막 두 주기의 실제 FDTD 62프레임이며 느리게 재생합니다.

오목 조건에서는 원본 소스 중심이 n=1.54 안에 있지만 약한 끝부분은 다른 매질과 겹칩니다. 401점 검사에서 그 구간의 **소스 진폭 제곱 가중 비율은 약 0.0273%**였습니다. 이는 소스 분포 진단이며 투과율이 아닙니다. 원본을 비교하기 위해 구조는 수정하지 않았습니다.

<h2 id="vortex">3. 3D vortex: 네 날개는 어디서 생길까?</h2>

Laguerre–Gaussian beam은 축 주위로 위상이 감기는 빔입니다. 이번 소스의 위상 전하는 m=2입니다. 소스의 방위각 위상 인자 exp(imφ)는 한 바퀴에서 위상이 4π만큼 변합니다. 축에서는 소스 진폭이 0이 됩니다.

<div class="figure-pair">
  <figure class="lesson-figure">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_longitudinal.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_longitudinal.png" alt="3D Meep vortex beam의 진행 축을 포함하는 종단면 순간 실수 전기장 제곱" loading="lazy"></a>
    <figcaption>종단면: 진행 축을 포함하는 단면입니다. 파면과 경계에서의 간섭을 함께 봅니다.</figcaption>
  </figure>
  <figure class="lesson-figure">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_transverse.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_transverse.png" alt="charge 2 vortex beam의 횡단면에 나타나는 네 개의 밝은 날개" loading="lazy"></a>
    <figcaption>횡단면: 진행 축에 수직인 단면입니다. m=2의 순간 실수장 제곱은 방위각에 네 번 반복되는 밝은 무늬를 만들 수 있습니다.</figcaption>
  </figure>
</div>

네 날개를 서로 독립적인 네 빔으로 해석하지 않습니다. 복소장의 실수부를 한 시각에 잘라 제곱했기 때문에 나타나는 무늬입니다. 시간평균하면 이 빠른 위상 무늬가 달라집니다. 반사·굴절 영역의 모양은 소스의 이상적인 고리와도 다를 수 있습니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d.png" alt="실제 3D Meep vortex 장 데이터의 공간 단면과 순간 실수장 제곱 등위면 입체도" loading="lazy"></a>
  <figcaption>전체 해상도 장에서 추출한 순간 실수장 제곱의 2% 등위면입니다. 입사 쪽 x=−2.09740a와 반사 쪽 y=2.11039a의 두 단면, 기울어진 매질 블록, 기하광학 방향을 나타내는 빨간 선을 함께 표시합니다. 흰 표면은 매질 경계가 아닙니다. 원본 방식의 하반부 끝점은 첫 양의 z 표본인 +0.00649a까지 포함합니다.</figcaption>
</figure>

이 입체도는 저장된 385×385×308 장에서 가장자리 30칸을 제외하고 **325×325×125 표본을 건너뛰지 않고** 사용합니다. VTK 9.5.2의 `vtkContourFilter`로 얻은 1,308,590개 삼각형을 Blender 4.5.14에서 렌더링하며, 메시 축소나 형상을 바꾸는 평활화는 하지 않습니다. 실제 셀 높이 4a를 유지하므로 원본 시각화 스크립트에 남은 과거의 높이 3.5a로 좌표를 눌러 맞추지 않습니다.

카메라의 방향과 순차 회전은 원본을 따르되, 실제 셀과 주석이 잘리지 않도록 거리를 조정해 화면에 5% 여백을 둡니다. 1200×1200 이미지에 Cycles 64 samples와 노이즈 제거를 적용합니다. 이 설정은 표시용이며 저장된 장이나 등위면 형상을 바꾸지 않습니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d_comparison.png" alt="원본 프로젝트 3D 그림, 격자를 건너뛴 이전 그림, 전체 해상도 재렌더 비교" loading="lazy"></a>
  <figcaption>왼쪽은 원본 프로젝트의 200픽셀 그림을 확대한 참조, 가운데는 이전의 잘못된 6칸 간격 표시, 오른쪽은 전체 해상도 재렌더입니다. 이전 그림은 파면을 충분히 표본화하지 못해 등위면이 거칠고 다른 모양으로 보였습니다. 원본 이미지의 모든 실행·카메라 설정은 알려져 있지 않으므로 픽셀 단위 동일성을 주장하지 않습니다.</figcaption>
</figure>

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d_modulus.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/vortex_3d_modulus.png" alt="동일한 저장 장의 복소 전기장 크기 제곱 합으로 그린 대안 3D 등위면" loading="lazy"></a>
  <figcaption>같은 장의 Σ|E<sub>j</sub>|²로 그린 대안입니다. 등위면과 단면 색상은 이 스칼라 자체의 전체 최대값 2%를 기준으로 합니다. 순간 실수부 제곱의 빠른 위상 줄무늬와 구분해 보세요.</figcaption>
</figure>

원본 Mayavi 스크립트의 현재 기본값은 실수부·허수부 제곱의 합이고, 실수부 제곱만 선택하는 줄도 제공합니다. 이 글의 주 그림은 Σ[Re E<sub>j</sub>]², 대안은 Σ|E<sub>j</sub>|²입니다. 두 표현은 같은 저장 데이터를 다른 물리량으로 읽은 것이며, 하나를 다른 하나의 정답으로 취급하지 않습니다.

<h2 id="airy">4. Airy beam: 밝은 무늬가 휘어 가는 이유</h2>

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/gallery/airy_free_space.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/gallery/airy_free_space.png" alt="자유공간에서 실제 FDTD로 계산한 M 0 W 4 Airy beam의 휘는 밝은 무늬" loading="lazy"></a>
  <figcaption>M=0, W=4, n₁=n₂=1. 최종 시각 t=90 a/c의 E<sub>z</sub>(t)²입니다.</figcaption>
</figure>

Airy beam은 여러 평면파 성분이 간섭하며 밝은 주엽의 위치가 곡선을 따라 이동하는 파동입니다. 밝은 자취가 휜다고 해서 빛 입자가 외력 없이 가속되거나 전체 에너지가 그 곡선만 따라간다는 뜻은 아닙니다.

**굴절 경계 없이 빔 자체의 간섭**을 보기 위해 양쪽 굴절률을 모두 1로 바꿨습니다. 원본 Airy 예제의 기본 n₂=0.65인 경계 산란 실행과 구분해야 합니다. 이상적인 무한 Airy 함수와 달리 여기에는 유한한 소스 구간과 격자가 있습니다.

<h2 id="understand">5. 밝은 줄무늬의 뜻</h2>

이 글의 주 그림은 **그 시각의 실수 전기장 제곱**입니다. 한 주기 안에서도 마루와 골이 지나가므로 밝은 줄무늬가 움직입니다. 이를 시간평균하면 첨부 그림의 빠른 줄무늬가 사라집니다.

| 표현 | 보여 주는 것 |
|---|---|
| 순간 실수장 E<sub>z</sub>(t) | 부호 있는 파면. 빨강·파랑 척도가 적합합니다. |
| 순간 실수장 제곱 | 2D는 E<sub>z</sub>(t)², 3D는 Σ<sub>j=x,y,z</sub>[Re E<sub>j</sub>(t)]². 빠른 위상 줄무늬와 간섭을 보존합니다. |
| 단일 주파수 시간평균 ⟨E<sub>z</sub>²⟩ | 실수장 진폭을 Ẽ라 정의하면 ∣Ẽ∣²/2. 빠른 시간 진동을 평균한 분포입니다. |
| 정규화한 Poynting flux | 별도의 참조 계산과 모니터로 측정하는 반사·투과 전력입니다. |

3D 예제는 복소장을 계산합니다. **Σ<sub>j</sub>[Re E<sub>j</sub>]²**와 **Σ<sub>j</sub>∣E<sub>j</sub>∣²**는 서로 다른 그림입니다. 이번에는 첫 번째로 밝은 위상 무늬를 살렸습니다. 자기장이나 매질에 따른 계수를 포함하지 않으므로 에너지 밀도 전체나 소자 효율로 부르지 않습니다.

<h2 id="predict">6. Snell 법칙과 평면 경계</h2>

곡면과 특수 빔을 이해하는 기준으로 평면 Gaussian의 30°·45° 결과도 남겼습니다. 입사각은 경계면 법선 기준입니다.

$$n_1\sin\chi_i=n_2\sin\chi_t,\qquad\chi_c=\arcsin(1/1.54)\approx40.49^\circ.$$

| 중심 입사각 | 평면파 이론의 예상 |
|---|---|
| 30° | 굴절각 약 50.35°. 반사와 굴절이 함께 나타납니다. |
| 45° | 임계각 이상. 단일 평면파는 전반사하고 낮은 굴절률 쪽에는 소멸장이 생깁니다. |

<details>
<summary>30°·45°의 부호 있는 파면과 시간평균 그림 펼치기</summary>
<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/wavefront_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/wavefront_comparison.png" alt="평면 Gaussian 30도·45도의 부호 있는 순간 전기장" loading="lazy"></a>
  <figcaption>빨강·파랑은 E<sub>z</sub>의 부호입니다. 두 실제 실행을 같은 척도로 비교합니다.</figcaption>
</figure>
<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/optical-beams/intensity_comparison.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/intensity_comparison.png" alt="두 평면 Gaussian 실행의 마지막 두 주기에서 추정한 평균 전기장 제곱" loading="lazy"></a>
  <figcaption>마지막 두 주기의 cos/sin/DC 적합에서 얻은 (A²+B²)/2. 순간장 제곱과 달리 빠른 시간 진동을 평균한 분포입니다.</figcaption>
</figure>
<div class="figure-pair">
  <figure class="lesson-figure lesson-animation">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/planar30.gif" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/planar30_wavefront.png" data-animation-src="{{ site.baseurl }}/assets/meep/optical-beams/planar30.gif" data-static-src="{{ site.baseurl }}/assets/meep/optical-beams/planar30_wavefront.png" alt="30도 Gaussian 마지막 두 주기의 실제 FDTD 파면" loading="lazy"></a>
    <figcaption>30° · 최종 두 주기의 실제 시간 샘플입니다.</figcaption>
    <button type="button" class="animation-toggle" hidden>애니메이션 재생</button>
  </figure>
  <figure class="lesson-figure lesson-animation">
    <a href="{{ site.baseurl }}/assets/meep/optical-beams/planar45.gif" data-lightbox><img src="{{ site.baseurl }}/assets/meep/optical-beams/planar45_wavefront.png" data-animation-src="{{ site.baseurl }}/assets/meep/optical-beams/planar45.gif" data-static-src="{{ site.baseurl }}/assets/meep/optical-beams/planar45_wavefront.png" alt="45도 Gaussian 마지막 두 주기의 실제 FDTD 파면" loading="lazy"></a>
    <figcaption>45° · 처음 도착하는 과도 과정이 아닙니다.</figcaption>
    <button type="button" class="animation-toggle" hidden>애니메이션 재생</button>
  </figure>
</div>
</details>

전반사여도 경계 가까이에는 소멸장이 남을 수 있습니다. 또한 유한 폭 Gaussian beam은 여러 입사 방향을 포함하므로 중심각 45°만 보고 전체 투과 전력이 정확히 0이라고 결론 내릴 수는 없습니다.

<h2 id="setup">7. 실제 계산 조건</h2>

소스는 v2.1.2와 같은 commit `ca145119e5bd0f0804d846ea42e35e4c3daa91de`로 고정했습니다. Meep 1.33.0, CPU 한 코어를 사용했습니다. a는 임의 길이 단위이며 μm로 지정하지 않았습니다.

| 항목 | Gaussian | 3D Laguerre–Gaussian | Airy 자유공간 |
|---|---|---|---|
| 소스 | 2D E<sub>z</sub> | 3D E<sub>z</sub>, m=2 | 2D E<sub>z</sub>, M=0, W=4 |
| n₁ → n₂ | 1.54 → 1.00 | 1.00 → 1.54 | 1.00 → 1.00 |
| 경계 | 평면 30°/45°, 오목·볼록 45° | 평면 45° | 굴절률 차이 없음 |
| 셀 | 5a × 5a | 5a × 5a × 4a | 10a × 10a |
| PML | 0.25a | 0.25a | 0.25a |
| f (c/a) | 12 | 5 | 12 |
| 해상도 (pixels/a) | 184.8 | 77 | 180 |
| 종료 시간 (a/c) | 10 | 10 | 90 |
| 진공 광학 주기 수 | 120 | 50 | 1080 |

Gaussian은 `kw_0=8, kr_w=60`, LG는 `kw_0=8, kr_w=0`, Airy는 `kw_0=7, kr_w=0`입니다. 원본의 격자 설정식과 종료 시간을 유지했습니다. Courant는 Gaussian 0.5, LG 1/3이며, Airy는 원본의 매질 의존 설정식을 따라 자유공간 n₂=1에서 0.5가 됩니다(기본 n₂=0.65에서는 0.325). 평면 45°는 이전 실행의 동일 조건 데이터를 해시와 출처를 확인해 재사용했습니다.

3D 소스는 초기화를 빠르게 하기 위해 **방위각 적분을 Bessel 함수로 정확히 계산하는 동등한 1차원 적분**을 사용했습니다. 원본 이중적분과 23점 비교에서 최대 절대오차 4.52×10⁻¹⁰, 의미 있는 진폭의 최대 상대오차 2.50×10⁻⁹였습니다. 장 출력은 Python 격자점별 콜백 대신 Meep의 배열 읽기로 저장했습니다. 원본 소스 파일 자체도 보존했습니다.

<h2 id="run">8. 직접 실행하기</h2>

Meep 환경에서 [재현 폴더](https://github.com/jin-castle/meep-examples/tree/main/code/optical_beams)를 사용합니다. `source/`에는 원본 Python·Scheme 예제, optbeam과 MIT 라이선스가 있습니다.

```bash
cd code/optical_beams
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python run_original.py --upstream source --output planar45 --chi 45 --interface planar
python run_original.py --upstream source --output concave45 --chi 45 --interface concave
python run_original.py --upstream source --output convex45 --chi 45 --interface convex
python render_curved.py --data-dir .
mkdir -p output/gallery/lg output/gallery/airy
python run_gallery.py --upstream source --output output/gallery/lg --beam lg > output/gallery/lg/run.log 2>&1
python run_gallery.py --upstream source --output output/gallery/airy --beam airy > output/gallery/airy/run.log 2>&1
python -m pip install vtk==9.5.2
python prepare_vortex_scene.py output/gallery
blender --background --factory-startup --threads 1 --python render_vortex_blender.py -- output/gallery
python render_gallery.py output/gallery
```

실행별 폴더에 결과가 나뉩니다. 전처리는 WSL 과학계산 Python, 렌더링은 Blender 자체 Python·NumPy와 Cycles CPU 한 스레드를 사용합니다. `blender`는 설치한 실행 파일 경로로 바꿀 수 있습니다. Windows Blender를 WSL에서 부르면 스크립트와 결과 폴더를 Windows 절대 경로로 전달하세요. 3D 기본 격자는 약 4,565만 셀로 2D보다 메모리와 시간이 많이 듭니다. 이미 저장한 장이 있으면 두 `run_gallery.py` 명령을 생략하고 전처리부터 다시 실행합니다. 표시용 좌표·정규화와 자세한 실행 안내는 [재현 README](https://github.com/jin-castle/meep-examples/blob/main/code/optical_beams/README.md)에 있습니다.

원본 실행도 가능합니다. 아래 3D 명령은 원본 이중적분을 사용하므로 초기화가 느릴 수 있습니다. 실행 전마다 다른 작업 폴더를 사용해 출력 덮어쓰기를 피하세요.

```bash
export PYTHONPATH="$PWD/source"
python source/scripts/Gauss_2d/Gauss2d.py -interface concave -chi_deg 45
python source/scripts/Gauss_2d/Gauss2d.py -interface convex -chi_deg 45
python source/scripts/Laguerre_Gauss_3d/LaguerreGauss3d.py
python source/scripts/Airy_2d/Airy2d.py -n1 1 -n2 1 -M 0 -W 4
```

<h2 id="verify">9. 실행 증거와 해석의 범위</h2>

- 곡면의 종료·배열 유한성·원본 HDF5와 순간장 제곱 일치는 [곡면 checks.json]({{ site.baseurl }}/assets/meep/optical-beams/curved/checks.json), 출처와 재사용 기록은 [곡면 provenance.json]({{ site.baseurl }}/assets/meep/optical-beams/curved/provenance.json)에 있습니다.
- Vortex·Airy의 실행, 소스 적분 비교와 장 출력 검사는 [갤러리 checks.json]({{ site.baseurl }}/assets/meep/optical-beams/gallery/checks.json), 조건은 [갤러리 provenance.json]({{ site.baseurl }}/assets/meep/optical-beams/gallery/provenance.json)에 있습니다.
- 전체 격자 등위면의 장 값 일치, 저장 데이터 해시와 방향선 좌표 검사는 [3D 재렌더 검사]({{ site.baseurl }}/assets/meep/optical-beams/gallery/native3d-checks.json), 원본·이전·수정 비교 이미지의 출처는 [비교 기록]({{ site.baseurl }}/assets/meep/optical-beams/gallery/comparison-provenance.json)에 있습니다.
- [평면 위상 진단]({{ site.baseurl }}/assets/meep/optical-beams/checks.json)에서 30°의 국소 굴절 파면 방향은 50.66°로 Snell 기준 50.35°와 약 0.31° 차이였습니다. 빔 중심이나 전력을 직접 잰 값은 아닙니다.
- Gaussian 최종 두 주기의 조화 성분 적합 상대 L2 잔차는 평면 30° 0.0822%, 평면 45° 0.0207%, 오목 0.0216%, 볼록 0.1021%입니다. 짧은 구간의 조화파 적합 검사이며 격자 수렴을 증명하지 않습니다.
- 원본 Airy 소스의 수치 적분에서 SciPy의 분할 한계·느린 수렴 경고가 발생했습니다. 실행 기록에 보존했으며, 유한한 장과 정상 종료만으로 소스 적분의 수렴을 보장하지 않습니다.
- 격자·PML 수렴, 정규화한 R·T, 곡면의 초점 거리·빔 폭, vortex의 궤도각운동량은 측정하지 않았습니다. 이 글은 실제 장을 관찰하고 비교하는 실습입니다.

<details markdown="1">
<summary>English summary</summary>

Actual single-core Meep 1.33.0 runs compare planar, concave and convex Gaussian interfaces, a charge-two fully 3D Laguerre–Gaussian beam, and an M=0, W=4 free-space Airy beam. Main figures show instantaneous squared real electric fields on black, preserving phase fringes. The original grid and runtime are retained. An analytically equivalent Bessel reduction accelerates the 3D source and is checked against the original double integral. Native array export replaces Python output callbacks. These are field visualizations, not convergence-tested power efficiencies or pixel-identical reproductions of the upstream PNGs.

</details>

<h2 id="reference">10. 출처와 라이선스</h2>

- **원본:** Daniel Kotik·Jörg Götte의 [Optical-beams-MEEP 문서](https://danielkotik.github.io/Optical-beams-MEEP/) · [고정 소스 버전](https://github.com/DanielKotik/Optical-beams-MEEP/tree/ca145119e5bd0f0804d846ea42e35e4c3daa91de)
- **소프트웨어 인용:** v2.1.2, [DOI: 10.5281/zenodo.5211251](https://doi.org/10.5281/zenodo.5211251). 소프트웨어 버전의 DOI입니다.
- **라이선스:** MIT, Copyright (c) 2018 Daniel Kotik. [배포 소스와 함께 허가문 보존](https://github.com/jin-castle/meep-examples/tree/main/code/optical_beams/source).
- **추가 작업:** 실행·검사 기록, 동등 적분과 관측 wrapper, 새 결과 렌더링, 한국어 해설입니다.
