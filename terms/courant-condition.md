---
layout: term
permalink: /terms/courant-condition/
lang: ko
title: "Courant 조건 — Meep 개념 사전"
term_label: "Courant 조건"
term_full: "Courant–Friedrichs–Lewy (CFL) condition · 시간 간격 안정성"
axis: numerics
axis_label: "수치해석"
order: 10
lesson_summary: "FDTD의 시간 간격 Δt를 격자 간격 Δx에 묶는 안정성 한계입니다. 한계를 넘으면 코드가 오류 없이 시작해도 장이 지수적으로 커져 발산합니다. Meep에서는 Courant 인자 S 하나로 정합니다."
glance:
  - { k: "Meep 코드", v: "`mp.Simulation(..., Courant=0.5)`" }
  - { k: "정의", v: "c Δt = S Δx. Meep 단위(c = 1, Δx = 1/resolution)에서 Δt = S / resolution" }
  - { k: "기본값", v: "S = 0.5. 진공·유전체에서는 1~3차원 모두 안정" }
  - { k: "안정 조건", v: "S ≤ n_min / √D (D는 차원 수). 진공에서 1D 1, 2D 0.707, 3D 0.577" }
  - { k: "이 페이지의 측정", v: "진공 2D: S 0.70 안정, 0.71 발산 · 3D: 0.57 안정, 0.58 발산 · 1D: 1.00 안정, 1.01 발산" }
  - { k: "발산하면", v: "분산(Lorentz·Drude) 재료가 있으면 Courant를 낮추거나 resolution을 올린다. 계산 시간은 1/S에 비례해 늘어난다" }
related:
  - { url: "/point-line-source/", label: "01 · 점원과 선원에서 빛은 어떻게 퍼질까요?" }
  - { url: "/boundary-pml/", label: "02 · 계산 경계의 반사는 어떻게 줄일까요?" }
  - { url: "/cylindrical-dipole/", label: "13 · 회전 대칭 구조의 3D 전자기장은 어떻게 계산할까요?" }
calc_note: "이 페이지의 그림, 애니메이션, 표 일부는 이 페이지를 위해 새로 실행한 Meep 1.33.0 계산입니다(code/courant_stability.py 약 10초, code/courant_gif.py 약 1분, 단일 코어)."
tags: [meep, fdtd, courant, cfl, stability, dispersive]
---

<h2 id="what">1. 무엇인가</h2>

FDTD는 Yee 격자 위에서 전기장과 자기장을 반 시간 간격씩 엇갈려 갱신합니다. 한 번의 갱신은 바로 옆 격자점의 값만 쓰는 명시적(explicit) 계산이라, 한 시간 간격 동안 정보가 퍼질 수 있는 거리에 한계가 있습니다. 시간 간격이 격자 간격에 비해 너무 크면 계산이 물리적 파동을 따라가지 못하고, 격자에서 가장 짧은 무늬(픽셀마다 부호가 바뀌는 성분)가 매 단계 증폭됩니다.

Meep은 이 관계를 Courant 인자 $S$로 정합니다.

$$c\,\Delta t = S\,\Delta x$$

Meep 단위에서는 $c = 1$, $\Delta x = 1/\text{resolution}$이므로 $\Delta t = S/\text{resolution}$입니다. 균일한 격자의 진공에서 안정하려면 다음을 만족해야 합니다.

$$S \le \frac{n_{\min}}{\sqrt{D}}$$

$D$는 차원 수, $n_{\min}$은 셀 안의 최소 굴절률입니다(보통 진공의 1). 공식 문서는 기본값 0.5가 1~3차원 모두에 충분하다고 적습니다. 굴절률이 1보다 작은 재료(ε < 1)를 넣으면 한계가 그만큼 낮아집니다.

한계를 넘었을 때 무엇이 커지는지는 1D에서 가장 잘 보입니다. 아래는 같은 펄스를 S = 1.00(한계와 같음)과 S = 1.003(0.3 % 초과)으로 계산한 것입니다. 왼쪽 아래 확대 그림의 점이 격자점입니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-courant/03_anim_1d.gif" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-courant/03_anim_1d.gif" alt="1D 진공, resolution 20. 파란 선(S 1.00)은 펄스가 양쪽으로 퍼져 나간다. 빨간 선(S 1.003)은 t ≈ 5부터 격자점마다 부호가 바뀌는 지그재그가 셀 전체에 생겨 커지고, t = 11.2에 max|Ex|가 10⁶을 넘어 멈춘다. 확대 그림은 z = −3 ~ −2 µm의 격자점 20개를 각 프레임 최대값으로 나눈 것이다." data-animation-src="{{ site.baseurl }}/assets/meep/terms-courant/03_anim_1d.gif" data-static-src="{{ site.baseurl }}/assets/meep/terms-courant/03_anim_1d.png">
  </a>
  <button class="animation-toggle" type="button" hidden>애니메이션 정지</button>
  <figcaption>1D 진공, resolution 20. S = 1.00(파랑)은 펄스가 양쪽으로 퍼져 나가고 끝까지 안정합니다. S = 1.003(빨강)은 처음 몇 단계는 같다가 t ≈ 5부터 격자점마다 부호가 바뀌는 지그재그가 자라고, t = 11.2에 max|Ex| > 10⁶이 되어 멈춥니다. 펄스는 아직 셀을 벗어나지도 않았습니다.</figcaption>
</figure>

자라는 것은 펄스가 아니라 픽셀 간격의 지그재그입니다. 이 무늬는 처음에 부동소수점 반올림 오차 크기로 생기고, 물리적 파동과 상관없이 매 단계 일정 배율로 커집니다. 아래 "더 깊이"의 식이 이 배율을 줍니다.

<details markdown="1">
<summary>더 깊이 · 1/√D가 나오는 과정</summary>

평면파 $e^{i(\mathbf{k}\cdot\mathbf{r}-\omega t)}$를 Yee 차분식에 넣으면 격자의 분산 관계가 나옵니다(von Neumann 해석).

$$\sin\!\left(\frac{\omega\Delta t}{2}\right) = S\sqrt{\sum_{i=1}^{D}\sin^2\!\left(\frac{k_i\Delta x}{2}\right)}$$

모든 $\mathbf{k}$에 대해 실수 $\omega$가 있으려면 오른쪽이 1을 넘지 않아야 합니다. 오른쪽이 가장 큰 경우는 모든 방향에서 $k_i\Delta x = \pi$, 곧 픽셀마다 부호가 바뀌는 체크무늬입니다. 이때 값이 $S\sqrt{D}$이므로 $S \le 1/\sqrt{D}$가 됩니다. 이 한계를 넘으면 체크무늬 성분의 $\omega$가 복소수가 되고 매 단계 일정 배율로 커집니다. 처음에는 부동소수점 반올림 오차 크기라도 수백 단계 안에 다른 모든 장을 덮습니다.

1D에서 $S = 1$이면 오른쪽이 $\sin(k\Delta x/2)$가 되어 격자 분산이 사라집니다("magic time step"). 2D·3D에는 이런 값이 없고, 격자 분산 오차는 주로 resolution이 정합니다. S를 낮춘다고 공간 이산화 오차가 줄지는 않습니다.

</details>

### 분산 재료가 있을 때

Lorentz·Drude 재료는 장 방정식 옆에 분극 $P_n$의 방정식을 하나씩 더 풉니다.

$$\frac{d^2P_n}{dt^2} + \gamma_n\frac{dP_n}{dt} + \omega_n^2 P_n = \sigma_n\,\omega_n^2\,E$$

공식 Materials 문서는 이 식이 대략 $\omega_n\Delta t/2 > 1$에서 불안정해진다고 적습니다. $\omega_n = 2\pi f_n$, $\Delta t = S/\text{resolution}$을 넣으면 공진 주파수의 한계는 $f_n < \text{resolution}/(\pi S)$입니다. 진공 조건을 만족해도 재료의 공진 주파수가 높으면 발산할 수 있고, 이때는 S를 낮추거나 resolution을 올리면 Δt가 작아져 한계가 올라갑니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-courant/04_anim_lorentz.gif" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-courant/04_anim_lorentz.gif" alt="1D Lorentz 매질(f_n 5.7, ε∞ 2.25, σ 0.5, γ 0.05), resolution 10, PML 없는 닫힌 셀. 파란 선(S 0.25)은 펄스가 매질 안에서 오가며 크기를 유지한다. 빨간 선(S 0.5)은 t ≈ 10부터 격자점 지그재그가 자라 t = 20.8에 10⁶을 넘어 멈춘다." data-animation-src="{{ site.baseurl }}/assets/meep/terms-courant/04_anim_lorentz.gif" data-static-src="{{ site.baseurl }}/assets/meep/terms-courant/04_anim_lorentz.png">
  </a>
  <button class="animation-toggle" type="button" hidden>애니메이션 정지</button>
  <figcaption>같은 Lorentz 매질(f_n = 5.7), 같은 resolution 10, 같은 source. 진공 한계로 보면 S = 0.5는 1D 한계 1의 절반이라 안전해야 하지만, 재료의 분극 방정식이 먼저 무너져 t = 20.8에 멈춥니다. S를 0.25로 낮추면 같은 계산이 끝까지 갑니다. 이 조건에서 S = 0.5의 발산은 f_n 5.6과 5.7 사이에서 시작했습니다.</figcaption>
</figure>

<h2 id="why">2. 왜 필요한가</h2>

이 한계를 넘은 계산은 오류 메시지 없이 시작합니다. 처음 몇 단계의 장은 정상처럼 보이다가 지수적으로 커집니다. 아래 두 run은 2D 진공에서 S만 0.01 다릅니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-courant/02_anim_2d.gif" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-courant/02_anim_2d.gif" alt="2D 진공, resolution 10, 중앙 Ez 점원. 왼쪽 S 0.70은 원형 파면이 퍼져 PML로 나간다. 가운데 S 0.71은 t ≈ 10까지 같아 보이다가 셀 전체가 픽셀 체크무늬로 덮이고 t = 15.6에 멈춘다. 오른쪽은 가운데 그림의 점선 상자 1 × 1 µm(10 × 10 픽셀)를 프레임마다 최대값으로 나눈 것으로, 이웃 픽셀끼리 부호가 엇갈린다. 아래 그래프는 두 run의 max|Ez|." data-animation-src="{{ site.baseurl }}/assets/meep/terms-courant/02_anim_2d.gif" data-static-src="{{ site.baseurl }}/assets/meep/terms-courant/02_anim_2d.png">
  </a>
  <button class="animation-toggle" type="button" hidden>애니메이션 정지</button>
  <figcaption>2D 진공, resolution 10, 두 장 지도의 색 범위는 같습니다. S = 0.70(한계 0.7071 아래)은 원형 파면이 PML로 빠져나갑니다. S = 0.71은 t ≈ 10까지 구별되지 않다가 체크무늬가 셀을 덮고 t = 15.6에 max|Ez| > 10⁶이 되어 멈춥니다. 오른쪽 확대 그림에서 이웃 픽셀끼리 부호가 엇갈리는 이 무늬가 1절 "더 깊이"에 나오는 $k_i\Delta x = \pi$ 성분입니다.</figcaption>
</figure>

여러 S 값과 3D까지 같은 방식으로 잰 결과를 한 장에 모으면 다음과 같습니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-courant/01_courant.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-courant/01_courant.png" alt="(a) 2D 진공, resolution 10, PML 1 µm에서 셀 전체 max|Ez|의 시간 변화. S 0.50과 0.70은 펄스가 지나간 뒤 10⁻⁹ 아래로 줄고, 0.71·0.72·0.75는 몇 시간 단위 안에 10⁶을 넘는다. (b) 1D Lorentz 매질에서 공진 주파수 f_n을 바꾼 결과. S 0.5에서는 f_n 6.0부터, S 0.25에서는 11.5부터 발산한다. 점선은 대략적 한계 res/(πS)." loading="lazy">
  </a>
  <figcaption>(a) 2D 진공에서 S만 바꾼 다섯 run. 한계 1/√2 = 0.7071 바로 아래(0.70)는 안정하고 바로 위(0.71)는 발산합니다. (b) 1D Lorentz 매질(ε∞ 2.25, σ 0.5, γ 0.05, 닫힌 셀)에서 발산이 시작되는 공진 주파수. S를 절반으로 줄이면 한계가 6.0에서 11.5로 올라갑니다.</figcaption>
</figure>

| 차원 | 이론 한계 1/√D | 안정했던 최대 S | 발산한 최소 S | 발산 판정 시각 |
|---|---|---|---|---|
| 1D (res 20) | 1.000 | 1.00 | 1.01 | t = 21.7 (430 단계) |
| 2D (res 10) | 0.707 | 0.70 | 0.71 | t = 23.4 (329 단계) |
| 3D (res 8) | 0.577 | 0.57 | 0.58 | t = 25.9 (357 단계) |

| Lorentz 매질 | 대략적 한계 res/(πS) | 안정했던 최대 f_n | 발산한 최소 f_n |
|---|---|---|---|
| S = 0.5 | 6.37 | 5.5 | 6.0 |
| S = 0.25 | 12.73 | 11.0 | 11.5 |

<p class="lesson-note">발산 판정은 source가 꺼진 시각(t = 20)의 max|E|보다 1000배 커진 때입니다. 진공 결과는 이론 한계와 0.01 간격 안에서 맞습니다. Lorentz 결과에서 실제 발산은 대략적 한계보다 6~10 % 낮은 f_n에서 시작했습니다. 이 차이는 이 한 가지 재료 파라미터 조합에서 잰 것이고, 공식 문서도 이 식을 대략적인 기준으로만 제시합니다.</p>

실제 예제에서 이 문제가 드러나는 곳은 분산 금속입니다. Meep 공식 예제 `stochastic_emitter_line.py`(은 박막 위의 발광체)를 계산량을 줄이려고 resolution 16으로 낮춰 실행한 기록에서, `mp.materials.Ag`가 초기화된 직후 S 0.5와 0.25 모두 NaN/Inf로 멈췄고 0.1에서 끝까지 계산됐습니다. resolution을 낮추면 Δt가 커져 은 모델의 높은 공진 주파수가 위 한계를 넘기 때문입니다. 같은 기록에서 S 0.1의 결과는 별도의 resolution 수렴 검사를 통과하지 못했습니다. 발산하지 않는 것과 맞는 것은 다른 문제입니다.

<h2 id="meep-code">3. Meep 코드에서</h2>

```python
# code/courant_stability.py (이 페이지), A. vacuum
sim = mp.Simulation(cell_size=c["cell"], resolution=c["res"], dimensions=D, Courant=S,
                    boundary_layers=[mp.PML(1.0)],
                    sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=c["comp"],
                                       center=mp.Vector3())])
# time step: dt = S / resolution  (Meep units, c = 1)
```

- 무엇: `Courant`는 `Simulation`의 인자 하나입니다. 지정하지 않으면 0.5입니다.
- 왜: Δt를 직접 정하는 인자는 없습니다. resolution과 S가 Δt를 함께 정하므로, resolution을 두 배로 올리면 Δt도 절반이 되어 같은 시간을 계산하는 데 단계 수가 두 배가 됩니다(3D 셀 수 8배와 합쳐 16배).
- 틀리면: 공식 예제의 resolution을 낮추면서 분산 재료를 그대로 두면 Δt가 커져 재료 쪽 한계를 넘을 수 있습니다. 2D 계산을 3D로 옮기면서 S를 0.7로 둔 코드는 3D 한계 0.577을 넘습니다.

```python
# code/courant_stability.py, B. Lorentzian medium
medium = mp.Medium(epsilon=2.25, E_susceptibilities=[mp.LorentzianSusceptibility(frequency=fn, gamma=0.05, sigma=0.5)])
```

- 무엇: `frequency`가 위 식의 $f_n$입니다. Meep 주파수 단위(c/a)이므로 a = 1 µm이면 $f_n$ = 10은 파장 0.1 µm에 해당합니다.
- 왜: 금속을 여러 극(pole)으로 맞춘 모델에는 가시광보다 훨씬 높은 공진 주파수가 들어 있습니다. 측정 대역과 상관없이 이 극이 Δt의 한계를 정합니다.
- 틀리면: 대역 밖 극을 줄이려고 재료 모델을 직접 맞출 때 높은 $f_n$을 넣으면 같은 S에서 발산합니다. 공식 문서가 권하는 대응은 resolution 올리기, Courant 낮추기, 다른 모델 함수 쓰기 세 가지입니다.

### 원통 좌표의 m

원통 좌표(`dimensions=mp.CYLINDRICAL`)는 각 방향 의존성 $e^{im\phi}$의 $m$마다 계산합니다. 기본값(`accurate_fields_near_cylorigin=False`)에서 Meep은 축에서 |m| 픽셀 안쪽의 일부 장을 0으로 두어 기본 S 0.5로 안정하게 만듭니다. 이 옵션을 `True`로 켜면 공식 문서는 경험적으로 S를 대략 min(0.5, 1/(|m| + 0.5)) 이하로 낮춰야 한다고 적습니다. 13·14편은 m을 60까지 계산했지만 기본값을 써서 S 0.5에서 안정했습니다.

<h2 id="in-examples">4. 예제에서의 쓰임</h2>

| 예제 | Courant | 이유 |
|---|---|---|
| [02 경계 조건]({{ site.baseurl }}/boundary-pml/) | 0.5를 명시 | 강의 노트북과 같은 값으로 고정. 0.5 → 0.3이 반사 바닥값을 움직이는지 확인하는 실험을 제안 |
| 01, 03~12편 | 기본 0.5 | 진공과 비분산 유전체(Si, SiO₂, ε = 12 등)뿐이라 1/√D 한계만 지키면 됨 |
| [10 점광원 3D 방사]({{ site.baseurl }}/dipole-pattern-3d/) | 기본 0.5 | 1D Bloch run 240개. 1D 한계는 1이라 여유가 큼 |
| [13 회전 대칭]({{ site.baseurl }}/cylindrical-dipole/)·[14 박막 광추출]({{ site.baseurl }}/extraction-efficiency/) | 기본 0.5 | 원통 좌표 m 급수(14편은 m 60까지). 축 근처 장을 0으로 두는 기본값 사용 |

이 사이트의 01~14편에는 분산 재료가 없어서 Courant를 바꿀 일이 없었습니다. 은·금 같은 금속이나 직접 맞춘 Lorentz 모델을 넣는 순간 Courant는 결과를 좌우하는 설정이 됩니다.

<h2 id="pitfalls">5. 돌아가는데 틀리는 경우</h2>

| 증상 | 원인 | 확인법 | 고침 |
|---|---|---|---|
| `meep: simulation fields are NaN or Inf` 또는 장이 지수적으로 커짐 | S가 1/√D를 넘음 (2D 코드를 3D로 옮기며 S 유지 등) | S와 1/√D 비교 | S를 0.5 이하로 |
| 진공에서는 되는데 금속을 넣으면 발산 | 분산 재료의 공진 주파수가 res/(πS)를 넘음 | Courant만 낮춘 가장 작은 run으로 확인 (다른 설정은 고정) | Courant를 낮추거나 resolution을 올림 |
| 분산 재료가 셀 끝까지 이어진 구조에서만 발산 | 분산 재료와 PML이 겹침 (공식 FAQ의 첫 번째 원인) | 재료를 PML 앞에서 끊어 보거나 [PML]({{ site.baseurl }}/terms/pml/)을 Absorber로 교체 | Absorber 사용 |
| ε < 1인 재료나 ε가 음수인 상수 재료에서 발산 | ε < 1은 n_min을 낮춤. 음수 상수 ε는 수치 불안정이 아니라 비물리적 재료의 실제 해 (공식 FAQ) | 재료 정의 확인 | ε < 1이면 S를 n_min/√D 아래로, 음수 ε는 분산 모델로 |
| 원통 좌표에서 큰 m만 발산 | `accurate_fields_near_cylorigin=True`와 S 0.5 조합 | 옵션 값 확인 | S를 min(0.5, 1/(\|m\| + 0.5)) 이하로, 또는 기본값 사용 |
| S를 낮춰 발산은 멈췄는데 resolution을 바꾸면 결과가 변함 | 안정성과 수렴은 별개 | resolution 2~3점 비교 | resolution 수렴을 따로 확인 |

Courant와 resolution을 한 번에 함께 바꾸면 어느 쪽이 발산을 고쳤는지 알 수 없습니다. 위 은 박막 기록도 Courant만 바꾼 run을 먼저 돌려 원인을 좁혔습니다.

<h2 id="inverse-design">6. inverse design에서</h2>

adjoint 최적화는 forward와 adjoint를 같은 Δt로 수십~수백 번 반복합니다. 두 가지가 달라집니다.

첫째, 계산 시간이 1/S에 비례해 곱해집니다. 한 번의 평가가 두 run이므로 S를 0.5에서 0.25로 낮추면 최적화 전체 시간이 두 배가 됩니다. 분산 재료가 있는 역설계에서는 처음 설계에서 안정한 가장 큰 S를 찾아 두고 시작합니다.

둘째, 최적화는 낮은 resolution으로 빠르게 돌리고 최종 설계만 높은 resolution으로 다시 재는 경우가 많습니다([09편]({{ site.baseurl }}/bend-inverse/)은 res 10으로 최적화하고 res 20에서 다시 쟀습니다). 분산 재료의 한계 $f_n < \text{resolution}/(\pi S)$는 resolution이 낮을수록 엄격하므로, 검증용 resolution에서 안정했던 S가 최적화용 낮은 resolution에서는 발산할 수 있습니다. S는 실제로 최적화를 돌릴 resolution에서 확인합니다.

<h2 id="connections">7. 연결</h2>

- 함께 보면 좋은 개념: [PML]({{ site.baseurl }}/terms/pml/) (분산 재료와 PML이 겹칠 때의 발산), [Flux 정규화]({{ site.baseurl }}/terms/flux-normalization/)
- 코드: [code/courant_stability.py](https://github.com/jin-castle/meep-examples/blob/main/code/courant_stability.py)(한계 측정) · [code/courant_gif.py](https://github.com/jin-castle/meep-examples/blob/main/code/courant_gif.py)(애니메이션) · 결과 [result.json]({{ site.baseurl }}/assets/meep/terms-courant/result.json), [anim.json]({{ site.baseurl }}/assets/meep/terms-courant/anim.json)
- Meep 공식 문서: [Introduction: FDTD methods](https://meep.readthedocs.io/en/master/Introduction/#finite-difference-time-domain-methods) · [Materials: Numerical stability](https://meep.readthedocs.io/en/master/Materials/#numerical-stability) · [FAQ: Why are the fields blowing up?](https://meep.readthedocs.io/en/master/FAQ/#why-are-the-fields-blowing-up-in-my-simulation) · [Python API: Simulation](https://meep.readthedocs.io/en/master/Python_User_Interface/#simulation)
- 참고 문헌: A. Taflove, S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed., Artech House (2005), 4장 수치 분산과 안정성

<details markdown="1">
<summary>source 파형 (이 페이지의 모든 run 공통)</summary>

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-courant/00_source.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-courant/00_source.png" alt="GaussianSource(fcen 1, fwidth 0.5)의 시간 파형과 스펙트럼. width 2, 정점 t0 = 10, source는 t = 20에 꺼진다." loading="lazy">
  </a>
  <figcaption>GaussianSource(fcen = 1, fwidth = 0.5). 정점 t0 = 10이고 t = 20에 꺼집니다. 발산 판정의 기준 시각이 이 꺼지는 시각입니다.</figcaption>
</figure>

</details>
