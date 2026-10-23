---
layout: topic
permalink: /metalens/
title: "Metalens 위상 지도와 PB 위상 — 이상적 렌즈 위상, 2π 접기, 격자 샘플링"
title_en: "Metalens phase maps and the PB phase — the ideal lens phase, 2π wrapping, lattice sampling"
lang: ko
series: meep-examples
topic_label: METALENS
lesson_title: "메타렌즈의 fin은 왜 위치마다 다르게 돌아가 있을까?"
lesson_summary: "같은 크기의 직사각 fin이 렌즈 위치마다 다른 각도로 놓이는 이유를 이상적 렌즈 위상에서 출발해 따라갑니다. 위상을 2π로 접고, 격자로 샘플링하고, 회전각으로 옮기는 세 단계입니다."
lesson_goals:
  - "등광로 조건에서 이상적 렌즈 위상을 유도하고, 근축 2차 위상이 어디서 틀리는지 설명한다."
  - "2π 접기와 격자 샘플링이 위상 그림의 톱니, 계단, 중앙의 0을 만드는 과정을 설명한다."
  - "PB 위상과 전파 위상의 차이, 그리고 렌즈 가장자리 fin 무늬가 생기는 이유를 설명한다."
lesson_prerequisites: "06편 회절 차수 · 07편 meta-atom과 phase library"
calc_note: "그림은 numpy 위상 모델과 1D 스칼라 각스펙트럼 전파로 계산했습니다. Meep(FDTD) 계산이 아닙니다."
toc:
  - { id: observe, label: "관찰하기" }
  - { id: ideal, label: "이상적 렌즈 위상" }
  - { id: wrap, label: "2π 접기와 샘플링" }
  - { id: pb, label: "PB 위상" }
  - { id: edge, label: "가장자리 무늬" }
  - { id: animation, label: "한 번에 보기" }
  - { id: verify, label: "초점 확인" }
  - { id: check, label: "이해 확인하기" }
  - { id: reference, label: "코드와 참고 자료" }
related:
  - { url: "/binary-grating/", label: "06 · 회절 격자: 위상 차이가 방향을 정한다" }
  - { url: "/meta-atom/", label: "07 · meta-atom: 폭으로 위상을 고르는 전파 위상" }
  - { url: "/metagrating-inverse/", label: "08 · 역설계: 국소 주기 근사가 틀리는 곳을 adjoint로" }
date: 2026-10-23
tags: [metalens, metasurface, geometric-phase, pancharatnam-berry, phase-wrapping]
image: /assets/meep/metalens/04_ideal_pb.png
excerpt: "Why identical rectangular nanofins sit at different angles across a PB metalens: the ideal lens phase from equal optical paths, 2π wrapping, lattice sampling, and theta = phi/2."
---

<details markdown="1">
<summary>TL;DR (English)</summary>

- **What**: how the phase map of a geometric-phase (Pancharatnam–Berry) metalens is built: ideal hyperbolic lens phase → wrap into 0–2π → sample on a sub-wavelength lattice → set each nanofin angle to θ = φ/2.
- **Result**: in a 1D scalar check (λ = 532 nm, f = 10 µm, NA 0.46, 250 nm lattice) the sampled PB phase focuses with FWHM 499 nm vs 493 nm for the continuous ideal phase, at 0.95 of its peak; the opposite circular polarization diverges.
- **Takeaway**: the isolated zero at the centre of the phase plot, the sawtooth and the triangle/ring fin motifs at the lens edge are all products of wrapping and sampling, not separate design choices.
- **Code**: numpy + matplotlib scripts at the bottom (no Meep run on this page).

</details>

<h2 id="observe">1. 관찰하기: 같은 fin, 위치마다 다른 각도</h2>

PB(Pancharatnam–Berry) 위상을 쓰는 메타렌즈의 SEM 사진을 보면 크기가 같은 직사각 기둥(nanofin)이 격자점마다 다른 각도로 서 있습니다. 렌즈 중심에서는 이웃 fin이 거의 나란하고, 가장자리로 갈수록 이웃끼리 각도가 크게 달라지며 삼각형이나 고리처럼 보이는 반복 무늬가 나타납니다. 아래 그림은 사진이 아니라, 렌즈 가장자리의 위상을 격자로 샘플링해 fin을 놓은 계산 결과입니다. 위 줄은 SEM에서 흔히 쓰는 35° 기울인 시점, 아래 줄은 같은 배열을 위에서 본 모습입니다.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/metalens/01_edge_patterns.png" data-lightbox aria-label="렌즈 가장자리 조건에서 계산한 fin 배열의 기울인 모습과 위에서 본 모습 원본 확대"><img src="{{ site.baseurl }}/assets/meep/metalens/01_edge_patterns.png" alt="육방 격자와 정사각 격자에서 이웃 각도 차 60°와 80°일 때의 fin 배열" loading="lazy"></a>
<figcaption>왼쪽 육방 격자(이웃 각도 차 60°/칸)에서는 세로 fin 둘레를 비스듬한 fin들이 감싸는 고리 무늬가 반복됩니다. 아래 줄의 색을 보면 각도가 몇 개만 돌아가며 쓰입니다.</figcaption>
</figure>

이 무늬는 따로 설계한 단위 구조가 아닙니다. 렌즈에 필요한 위상을 회전각으로 옮겨 격자점마다 찍은 결과이고, 다음 절부터 그 과정을 순서대로 따라갑니다.

### 어디에 쓰이는가

메타렌즈는 렌즈 곡면 대신 수백 nm 두께의 평면 구조로 초점을 만듭니다. 위상 지도를 만드는 방법은 소자 종류와 관계없이 같고, 어떤 meta-atom으로 그 위상을 구현하느냐가 달라집니다.

| 응용 | 이 페이지의 어떤 것을 쓰는가 | 그다음에 필요한 것 |
|------|------------------------------|--------------------|
| 스마트폰·내시경용 평면 렌즈 | 이상적 렌즈 위상, 2π 접기, 격자 샘플링 | 편광 무관 meta-atom(07편 전파 위상), 색수차 보정 |
| 원편광 분리·스핀 다중화 소자 | PB 위상의 부호가 원편광에 따라 바뀌는 성질 | 반파장판 조건을 만족하는 fin 높이·폭의 FDTD 확인 |
| 빔 조향·홀로그램 | 위상 램프와 칸당 위상 변화 조건 | 고차 회절을 줄이는 역설계(08편) |

<h2 id="ideal">2. 이상적 렌즈 위상</h2>

평면파를 축 위의 한 점(초점 거리 $f$)으로 모으려면, 렌즈 위 어느 점에서 출발한 빛이든 초점에 같은 위상으로 도착해야 합니다(등광로 조건). 반지름 $r$에서 초점까지의 거리는 $\sqrt{r^2+f^2}$이므로, $k = 2\pi/\lambda$로 두면

$$\varphi(r) + k\sqrt{r^2+f^2} = k f$$

$$\varphi(r) = -k\left(\sqrt{r^2+f^2}-f\right)$$

입니다. 위상 기울기를 확인하면 $\frac{1}{k}\frac{d\varphi}{dr} = -\frac{r}{\sqrt{r^2+f^2}} = -\sin\theta$로, 렌즈의 각 점이 빛을 초점 방향의 각도 $\theta$로 꺾습니다. 물체 거리 $s_o$의 점광원을 상 거리 $s_i$에 맺으려면 같은 조건에서 $\varphi(r) = -k\,(L_o + L_i)$가 됩니다. 여기서 $L_o = \sqrt{r^2+s_o^2}-s_o$, $L_i = \sqrt{r^2+s_i^2}-s_i$입니다.

Fourier optics 교과서의 얇은 렌즈 $t(r) = \exp\left(-ik\,r^2/2f\right)$는 이 쌍곡 위상을 근축 근사로 전개한 첫 항입니다.

$$\varphi(r) = -\frac{k r^2}{2f} + \frac{k r^4}{8 f^3} - \cdots$$

둘째 항부터가 2차 위상으로 고NA 렌즈를 만들 때 생기는 구면수차입니다. 이 항이 1/4 파장(Rayleigh 기준)보다 작으려면 대략 $\mathrm{NA}^4 < 2\lambda/f$여야 합니다.

| 비교 | 조건 | 값 |
|------|------|----|
| 2차 위상이 쓸 만한 NA 상한 | f = 1 mm, λ = 0.5 µm | NA ≈ 0.18 |
| 가장자리 위상, 쌍곡 | NA 0.8, f = 50 µm, λ = 532 nm | 62.7 파장 |
| 가장자리 위상, 2차 | 같은 렌즈 | 83.5 파장 (쌍곡보다 20.9 파장 많음) |

2차 위상에도 쓰임이 있습니다. 비스듬히 들어온 평면파는 위상에 기울기 항을 더할 뿐이라 초점이 수차 없이 옆으로 이동하므로, 초점이 퍼지는 대신 시야각이 넓습니다.

평평한 위상판 하나로는 모든 조건을 함께 맞출 수 없습니다. 쌍곡 위상은 수직 입사에서만 수차가 없고, 비스듬한 입사에서는 코마가 생깁니다. 축 밖까지 좋은 결상을 하려면 sine 조건 $h = f\sin\theta$를 만족해야 하는데, 평면 렌즈는 구조상 $h = f\tan\theta$입니다. 또 모든 파장에서 같은 $f$를 얻으려면 위상 전체가 $1/\lambda$에 비례해야 하지만, 2π로 접은 위상은 그렇지 않아 $f \propto 1/\lambda$의 색수차가 생깁니다. 굴절 렌즈는 같은 위상을 두께로 만듭니다($\varphi = k_0(n-1)t(r)$). 두께가 쌍곡 위상을 따르면 비구면 렌즈이고, 가공이 쉬운 구면은 이 식에서 벗어나 구면수차를 남깁니다.

<h2 id="wrap">3. 2π 접기와 격자 샘플링</h2>

위상은 2π 차이를 구별하지 않으므로 메타표면은 $\varphi \bmod 2\pi$만 구현하면 됩니다. 매끄러운 쌍곡선을 0~2π 범위로 접으면 톱니가 되고, 톱니 폭은 위상 기울기($k\sin\theta$)가 커지는 바깥으로 갈수록 좁아집니다. 중심은 $\varphi = 0$이고 바로 옆은 $-0.04$ rad 정도라 접으면 $2\pi - 0.04$가 됩니다. 그래서 위상 그래프에서는 중앙 한 칸만 0으로 떨어져 보이지만, 0과 2π는 같은 위상이므로 구조나 빛에는 차이가 없습니다. 렌즈 전체에 상수 위상을 더해도 초점은 그대로라, 접히는 위치는 이 상수에 따라 옮겨 갈 뿐입니다.

메타표면은 격자 칸마다 위상 하나만 줄 수 있어 접은 위상을 계단으로 샘플링합니다. 칸 사이 위상 변화가 π보다 작아야 위상이 되살아나므로(Nyquist) 격자 주기 $U$는 $U < \lambda/(2\,\mathrm{NA})$를 만족해야 하고, 넘으면 고차 회절로 빛이 새어 나갑니다. PB 렌즈에서 칸당 fin 각도 변화는

$$\Delta\theta \approx 180^\circ \times \frac{U\sin\theta}{\lambda}$$

이고, 반경이 커질수록 커집니다.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/metalens/02_radius_layout.png" data-lightbox aria-label="반경에 따른 fin 회전 배열 변화 원본 확대"><img src="{{ site.baseurl }}/assets/meep/metalens/02_radius_layout.png" alt="렌즈 위상 지도, 반경별 칸당 회전 변화 곡선, 중심·중간·가장자리의 fin 배열" loading="lazy"></a>
<figcaption>(b)의 곡선이 60°/칸을 넘는 반경부터 (e), (f)처럼 각도 몇 개만 반복되는 배열이 됩니다. (c)의 중심에서는 fin이 거의 나란합니다.</figcaption>
</figure>

| 위치 (NA 0.8, f = 50 µm, λ = 532 nm, U = 300 nm) | 반경 | 칸당 fin 각도 변화 |
|------------------------------|------|----------------------|
| 중심 | 0 µm | 0° |
| 중간 | 7.5 µm | 15° |
| 세 각도만 반복 | 36.6 µm | 60° |
| 가장자리 | 66.7 µm | 81° (위상 162°, Nyquist 한계에 가까움) |

<h2 id="pb">4. PB 위상: 회전각이 곧 위상</h2>

직사각 fin은 긴 축과 짧은 축의 유효 굴절률이 달라서 높이를 맞추면 반파장판으로 동작합니다. 원편광이 들어오면 반대 원편광으로 바뀐 성분이 $\exp(\pm i\,2\theta)$의 위상을 얻습니다. 그래서 위상 $\varphi$가 필요한 자리에는 fin을 $\theta = \varphi/2$만큼 돌려 놓고, 0~180° 회전으로 0~2π를 덮습니다. 부호는 입사 원편광에 따라 바뀌므로 한쪽 원편광에 렌즈인 배열은 반대 원편광에 $-\varphi$를 주어 발산 렌즈가 됩니다. 반파장판 조건에서 벗어난 만큼은 편광이 바뀌지 않은 채 위상 없이 지나가 배경광이 됩니다.

같은 격자를 채우는 방식을 비교하면 차이가 분명해집니다. 같은 unit cell만 반복하면 모든 칸의 위상이 같아 파면이 평평하게 나가므로 초점이 생기지 않습니다. 렌즈가 되려면 칸마다 위상이 달라야 하고, [07편]({{ site.baseurl }}/meta-atom/)의 기둥은 폭(직경)으로, PB 렌즈는 회전각으로 그 위상을 고릅니다.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/metalens/03_three_types.png" data-lightbox aria-label="같은 격자를 동일 셀, 직경 변화, 회전 변화로 채운 비교 원본 확대"><img src="{{ site.baseurl }}/assets/meep/metalens/03_three_types.png" alt="동일 셀 반복, 직경 변화 원기둥, 회전 변화 fin의 배치와 가운데 줄 위상" loading="lazy"></a>
<figcaption>아래 줄의 가운데 행 위상을 보면 (1)은 평평하고 (2)와 (3)은 같은 계단 위상입니다. 직경과 위상의 대응은 시뮬레이션 라이브러리가 아니라 설명용 선형 대응입니다.</figcaption>
</figure>

| 항목 | 원기둥 직경 (전파 위상, 07편은 2D 막대 폭) | 직사각 fin 회전 (PB 위상) |
|------|-------------------------------|---------------------------|
| 위상을 고르는 변수 | 직경 (회전은 의미 없음) | 회전각 (크기 고정) |
| 위상의 원리 | 짧은 도파로: $k_0 n_\mathrm{eff}(d) H$ | 반파장판 회전: $2\theta$ |
| 편광 | 원형 대칭이라 편광 무관 | 원편광 전용, 반대 원편광은 $-\varphi$ |
| 위상 지도를 만드는 법 | 셀 시뮬레이션으로 직경→위상 라이브러리 (파장마다 다름) | 각도가 곧 위상, 반파장판 조건만 맞추면 됨 |
| 2π 경계 | 가장 굵은 기둥 옆에 가장 가는 기둥이 놓임 | 0°와 180°가 같은 모양이라 이어짐 |
| 공정 | 직경이 여러 개라 가장 가는 기둥과 좁은 틈이 한계 | 크기 하나라 식각 관리가 쉬움 |

07편의 phase library는 같은 셀이 무한히 반복된다고 놓고(주기 경계) 계산합니다. 렌즈는 이 표를 보고 칸마다 다른 셀을 이어 붙이는 국소 주기 근사(LPA)로 만듭니다. 이웃 셀이 비슷한 중심에서는 이 근사가 잘 맞고, 칸마다 위상이 크게 바뀌는 가장자리와 직경형 렌즈의 2π 경계에서는 어긋납니다. 이 어긋남을 줄이는 방법이 [08편]({{ site.baseurl }}/metagrating-inverse/)의 adjoint 역설계입니다.

<h2 id="edge">5. 가장자리 무늬가 생기는 이유</h2>

가장자리 근처의 렌즈 위상은 좁은 영역 안에서 기울기가 일정한 위상 램프로 볼 수 있습니다. 칸당 각도 변화가 60°이면 정사각 격자에서는 0°, 60°, 120°만 반복되고, 이 세 방향은 정삼각형의 세 변 방향이라 이웃한 fin 세 개가 삼각형이나 바람개비처럼 보입니다. 육방 격자에서는 행이 반 칸씩 어긋나 각도가 30° 간격으로 여섯 개가 되고, 세로 fin 둘레를 비스듬한 fin이 감싸는 고리 무늬가 됩니다(1절 그림의 왼쪽).

무늬의 모양은 반경 방향이 격자 축과 이루는 각도와 칸당 각도 변화가 정수 비에 얼마나 가까운지에 따라 달라지고, 정수 비에서 벗어나면 천천히 변하는 모아레가 됩니다. 원형 렌즈에서는 방위각에 따라 반경 방향이 계속 바뀌므로, 같은 반지름에서도 위치마다 무늬가 다르게 보입니다.

<h2 id="animation">6. 단면에서 fin 배치까지 한 번에 보기</h2>

<figure class="lesson-figure lesson-animation">
<a href="{{ site.baseurl }}/assets/meep/metalens/05_phase_anim.gif" data-lightbox aria-label="위상 단면을 접고 샘플링하고 회전시켜 fin 배치까지 만드는 애니메이션 원본 확대"><img src="{{ site.baseurl }}/assets/meep/metalens/05_phase_anim.gif" data-animation-src="{{ site.baseurl }}/assets/meep/metalens/05_phase_anim.gif" data-static-src="{{ site.baseurl }}/assets/meep/metalens/05_phase_anim_end.png" alt="이상적 위상 단면을 2π씩 접고, 격자로 샘플링하고, 축 둘레로 돌려 원형 위상 지도와 fin 배치를 만드는 애니메이션" loading="lazy"></a>
<button class="animation-toggle" type="button" hidden>애니메이션 정지</button>
<figcaption>① 단면 → ② 0 아래로 내려간 부분을 2π씩 올림 → ③ 250 nm 격자로 샘플링 → ④ 지름 한 줄을 180° 돌려 동심원 위상 지도 → ⑤ 정사각 격자 픽셀 → ⑥ θ = φ/2로 fin 배치. 정지하면 마지막 장면(중앙과 가장자리 확대)을 보여 줍니다.</figcaption>
</figure>

②에서 오른쪽 위에서 본 색은 바뀌지 않습니다. 2π를 더해도 같은 위상이기 때문입니다. ④의 3D 곡면은 위상을 높이로 그린 것이고, 실제 소자의 fin 높이는 모두 같습니다.

| 마지막 장면 (λ = 532 nm, f = 10 µm, U = 250 nm) | 위치 | 이웃 fin 각도 차 |
|------------------------------|------|------------------|
| 중앙 확대 | x ≈ 0 µm | 약 1° (0°와 178.9°, fin은 180° 대칭) |
| 가장자리 확대 | x ≈ 4 µm | 약 31° |

<h2 id="verify">7. 이 위상이 초점을 만드는지 확인</h2>

계단 위상이 실제로 초점을 만드는지 1D 스칼라 각스펙트럼 전파로 확인했습니다. fin은 구조로 넣지 않고, 칸마다 변환 효율 100%의 위상 $\exp(i\varphi)$를 주는 이상적 반파장판으로 놓았습니다.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/metalens/04_ideal_pb.png" data-lightbox aria-label="이상적 PB metalens 위상의 유도, 매핑, 초점 확인 원본 확대"><img src="{{ site.baseurl }}/assets/meep/metalens/04_ideal_pb.png" alt="등광로 조건, 접기 전후 위상, fin 매핑, 두 원편광의 전파, 초점면 단면" loading="lazy"></a>
<figcaption>(E)에서 변환된 원편광은 z ≈ 10 µm에 모이고, (F)에서 반대 원편광은 퍼집니다. (G)에서 계단 위상(빨간 점선)의 초점 단면은 연속 이상 위상(회색)과 폭이 같습니다.</figcaption>
</figure>

| 항목 (λ = 532 nm, f = 10 µm, 구경 ±5.12 µm, U = 250 nm) | 값 |
|------|----|
| NA | 0.46 |
| 칸당 위상 변화 최대 | 77° (< 180°) |
| 초점 FWHM, 연속 이상 위상 | 493 nm |
| 초점 FWHM, 계단 샘플링 | 499 nm |
| 피크 세기 비 (계단 / 연속) | 0.95 |
| 초점 위치 | 9.7 µm |
| Fresnel 수 $a^2/(\lambda f)$ | 약 5 |

초점이 10 µm보다 조금 당겨진 것은 구경이 작아 생기는 회절 효과로, 계단 없는 연속 위상에서도 같은 위치가 나옵니다.

| 주장할 수 있는 것 | 주장할 수 없는 것 |
|-------------------|-------------------|
| 쌍곡 위상을 2π로 접고 250 nm로 샘플링해 θ = φ/2로 옮긴 배열은 한쪽 원편광을 회절 한계 폭으로 모으고, 반대 원편광은 퍼뜨린다 (이상적 fin, 1D 스칼라). | 실제 fin의 변환 효율, 동편광 누설, 이웃 셀 결합, 파장 의존성. 이것들은 3D FDTD로 fin 구조를 넣어 계산해야 알 수 있다. |

<h2 id="check">8. 이해 확인하기</h2>

<details markdown="1">
<summary>질문 1. 위상 그래프 중앙에 한 칸만 0으로 떨어진 부분이 있다. 이 자리의 fin은 옆 fin과 크게 다른가?</summary>

다르지 않습니다. 중앙은 φ = 0, 옆은 φ ≈ 2π − 0.04 rad이고 0과 2π는 같은 위상입니다. fin 각도로는 0°와 178.9°인데, 직사각 fin은 180° 돌려도 같은 모양이라 두 fin은 약 1° 차이로 거의 나란합니다.

</details>

<details markdown="1">
<summary>질문 2. 같은 unit cell만 규칙적으로 반복한 메타표면은 렌즈가 될 수 있는가?</summary>

될 수 없습니다. 모든 칸이 같은 위상을 주므로 파면이 평평하게 나가고 초점이 생기지 않습니다. 렌즈는 반경에 따라 위상이 달라야 하므로 칸마다 직경(전파 위상)이나 회전각(PB 위상)을 바꿉니다.

</details>

<details markdown="1">
<summary>질문 3. 같은 PB 렌즈에 반대 원편광을 넣으면 어떻게 되는가?</summary>

PB 위상의 부호가 바뀌어 $-\varphi$를 받으므로 발산 렌즈(오목 렌즈)처럼 퍼집니다. 7절 그림 (F)가 이 경우입니다.

</details>

<h2 id="reference">9. 코드와 참고 자료</h2>

이 페이지의 그림은 모두 numpy와 matplotlib로 만들었고 Meep을 쓰지 않았습니다. 스크립트는 출력 경로를 인자로 받습니다.

| 그림 | 스크립트 |
|------|----------|
| 1절 가장자리 무늬 | [metalens_edge_patterns.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_edge_patterns.py) |
| 3절 반경별 배열 | [metalens_radius_layout.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_radius_layout.py) |
| 4절 세 방식 비교 | [metalens_three_types.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_three_types.py) |
| 6절 애니메이션 | [metalens_phase_anim.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_phase_anim.py) |
| 7절 초점 확인 | [metalens_ideal_pb.py](https://github.com/jin-castle/meep-examples/blob/main/code/metalens_ideal_pb.py) |

참고 문헌

- M. Khorasaninejad et al., "Metalenses at visible wavelengths: Diffraction-limited focusing and subwavelength resolution imaging," Science 352, 1190 (2016). [doi:10.1126/science.aaf6644](https://doi.org/10.1126/science.aaf6644) — TiO₂ nanofin을 회전시킨 PB 메타렌즈.
- A. Arbabi et al., "Subwavelength-thick lenses with high numerical apertures and large efficiency based on high-contrast transmitarrays," Nature Communications 6, 7069 (2015). [doi:10.1038/ncomms8069](https://doi.org/10.1038/ncomms8069) — 직경으로 위상을 고르는 전파 위상 렌즈.
- J. W. Goodman, Introduction to Fourier Optics — 얇은 렌즈의 2차 위상 투과 함수.
