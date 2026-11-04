---
layout: term
permalink: /terms/resolution/
lang: ko
concept_id: resolution
title: "Resolution과 격자 간격 — Meep 개념 사전"
term_label: "Resolution"
term_full: "격자 간격 · 파장당 격자 수"
axis: numerics
axis_label: "수치해석"
order: 15
lesson_summary: "단위 길이당 격자 수로 정하는 격자 간격입니다. 정확도와 계산량을 함께 정하고, 시간 간격도 따라 바뀝니다. 어느 값이면 충분한지는 미리 알 수 없어서, 두 배로 올려 보고 결과가 멈추는지로 정합니다."
glance:
  - { k: "Meep 코드", v: "`mp.Simulation(..., resolution=20)` · 격자 간격 Δx = 1/resolution (Meep 길이 단위 a 기준)" }
  - { k: "읽는 법", v: "a = 1 µm이면 resolution 20은 격자 50 nm. 재료 안 파장당 격자 수 = resolution × λ₀ / n" }
  - { k: "공식 경험칙", v: "가장 굴절률 높은 무손실 재료에서 파장당 최소 8칸. 금속은 skin depth(수십 nm)를 풀 만큼" }
  - { k: "계산량", v: "3D에서 resolution 2배 → 셀 8배 × 시간 단계 2배 = 약 16배" }
  - { k: "이 페이지의 측정", v: "Si 안 파장당 4.5 · 8.9 · 17.8 · 35.6칸에서 위상 오차 9.2 · 2.15 · 0.51 · 0.13 %. 두 배마다 약 1/4" }
  - { k: "정하는 법", v: "보고할 양이 허용 오차 안에서 멈출 때까지 두 배씩 올린다 ([수렴 확인](/meep-examples/terms/convergence-check/))" }
related:
  - { url: "/straight-waveguide/", label: "04 · 직선 도파로의 투과율은 어떻게 구할까요?" }
  - { url: "/bend-inverse/", label: "09 · 도파로의 굽힘 구조는 어떻게 역설계할까요?" }
  - { url: "/ring-resonator/", label: "12 · 고리 공진기의 빛은 얼마나 오래 남을까요?" }
  - { url: "/extraction-efficiency/", label: "14 · 박막 속 빛은 얼마나 공기로 빠져나올까요?" }
calc_note: "애니메이션과 첫 표는 이 페이지를 위해 새로 실행한 Meep 1.33.0 계산입니다(code/resolution_dispersion_gif.py, 단일 코어 약 20초)."
tags: [meep, fdtd, resolution, numerical-dispersion, convergence]
---

<h2 id="what">1. 무엇인가</h2>

Meep의 `resolution`은 길이 단위 a 하나에 격자점을 몇 개 둘지 정합니다. 격자 간격은 $\Delta x = a/\text{resolution}$이고, [Courant 조건]({{ site.baseurl }}/terms/courant-condition/)에 따라 시간 간격도 $\Delta t = S\,\Delta x / c$로 함께 바뀝니다. resolution 하나가 공간과 시간의 이산화를 같이 정하는 셈입니다.

정확도를 정하는 것은 resolution 숫자 자체가 아니라 가장 짧은 길이에 격자가 몇 칸 들어가느냐입니다. 굴절률 $n$인 재료 안의 파장은 $\lambda_0/n$이므로 파장당 격자 수는 다음과 같습니다.

$$N_\lambda = \text{resolution}\times\frac{\lambda_0}{n\,a}$$

a = 1 µm, λ₀ = 1.55 µm, Si(n = 3.48)에서 resolution 20이면 $N_\lambda$ = 8.9칸입니다. 공식 FAQ의 경험칙은 가장 굴절률이 높은 무손실 재료에서 파장당 최소 8칸입니다. 다만 파장만 보면 안 됩니다. 얇은 층, 좁은 틈, 금속의 skin depth, 소멸장의 감쇠 길이처럼 파장보다 짧은 길이가 있으면 그 길이에도 격자가 몇 칸 들어가야 합니다.

격자가 거칠어서 생기는 오차는 크게 세 가지입니다.

| 오차 | 무엇이 틀리는가 | resolution에 대한 수렴 |
|---|---|---|
| 수치 분산 | 격자 위 파의 위상 속도와 군속도가 실제와 다름 | 2차($\propto\Delta x^2$). 균일 매질에서는 해석식으로 계산된다 |
| 구조 이산화 | 재료 경계가 계단 모양으로 놓여 경계 위치와 면적이 어긋남 | subpixel averaging이 있으면 대체로 매끄럽게, 없으면 불규칙하게 |
| 짧은 특징 길이 | 얇은 층, 틈, 소멸장, 금속 내부 장을 몇 칸으로만 표현 | 칸 수가 모자란 동안은 예측하기 어렵다 |

공식 FAQ는 실제 계산에서는 재료 경계 쪽 오차가 수치 분산보다 대개 훨씬 크다고 적습니다. 아래 애니메이션은 경계가 없는 균일한 Si에서 수치 분산만 따로 보여 줍니다.

<details markdown="1">
<summary>더 깊이 · 1D Yee 격자의 분산 관계</summary>

굴절률 $n$인 균일 매질에서 1D Yee 차분식에 평면파를 넣으면 격자 위의 파수 $\tilde k$가 나옵니다($c = 1$).

$$\sin\!\left(\frac{\tilde k\,\Delta x}{2}\right) = \frac{n\,\Delta x}{\Delta t}\,\sin\!\left(\frac{\omega\,\Delta t}{2}\right)$$

$\Delta x \to 0$이면 $\tilde k \to n\omega$로 실제 파수가 됩니다. 작은 $\Delta x$에서 전개하면 상대 오차는 $\tilde k/k - 1 \approx (k\Delta x)^2(1 - S^2/n^2)/24$로, 격자 간격의 제곱에 비례합니다. 이 식을 $\omega$에 대해 미분하면 수치 군속도는 $v_g = \cos(\tilde k\Delta x/2)/[n\cos(\omega\Delta t/2)]$입니다. 파장당 칸 수가 적으면 $\cos(\tilde k\Delta x/2)$가 1보다 꽤 작아져, 펄스 덩어리(군속도)가 위상보다 훨씬 많이 늦어집니다.

</details>

<h2 id="why">2. 왜 필요한가</h2>

같은 펄스를 같은 Si에서 resolution만 바꿔 28 µm 진행시켰습니다. 검은 선이 resolution 80 기준입니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-resolution/01_anim_dispersion.gif" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-resolution/01_anim_dispersion.gif" alt="1D Si(n = 3.48) 안을 진행하는 펄스(중심 파장 1.55 µm)를 resolution 10, 20, 40, 80으로 계산해 겹친 애니메이션. 위는 셀 전체의 Ex, 아래는 resolution 80 펄스 정점을 따라가는 3 µm 창. resolution 10(파장당 4.5칸)의 펄스는 t = 111에 기준보다 약 7.5 µm 뒤에 있고, resolution 20은 창 안에서 위상이 앞서며, resolution 40은 기준과 거의 겹친다." data-animation-src="{{ site.baseurl }}/assets/meep/terms-resolution/01_anim_dispersion.gif" data-static-src="{{ site.baseurl }}/assets/meep/terms-resolution/01_anim_dispersion.png">
  </a>
  <button class="animation-toggle" type="button" hidden>애니메이션 정지</button>
  <figcaption>1D Si(n = 3.48), 중심 파장 1.55 µm, Courant 0.5. 위는 셀 전체, 아래는 기준 펄스를 따라가는 3 µm 창(점은 resolution 10의 격자점)입니다. 파장당 4.5칸(빨강)인 펄스는 끝에 기준보다 약 7.5 µm 뒤처지고, 8.9칸(주황)은 창 안에서 위상이 눈에 띄게 어긋나며, 17.8칸(파랑)은 기준과 거의 겹칩니다.</figcaption>
</figure>

두 점의 DFT 위상으로 잰 격자 위 파수를 Yee 분산식과 비교했습니다.

| resolution | Si 안 파장당 칸 수 | 위상 오차 (측정) | Yee 이론 | 20 µm(약 45파장) 뒤 위상 지연 | 군속도 오차 (측정 / 이론) |
|---|---|---|---|---|---|
| 10 | 4.5 | 9.17 % | 10.76 % | 4.1 파장 | −27.9 % / −28.6 % |
| 20 | 8.9 | 2.154 % | 2.153 % | 0.97 파장 | −6.0 % / −6.3 % |
| 40 | 17.8 | 0.5148 % | 0.5148 % | 0.23 파장 | — |
| 80 | 35.6 | 0.1273 % | 0.1273 % | 0.057 파장 | — |

<p class="lesson-note">resolution 20·40·80은 측정과 이론이 넷째 자리까지 맞고, 두 배마다 오차가 약 1/4로 줄어 2차 수렴을 보입니다. resolution 10은 이론과 1.6 %p 다르며 원인은 확인하지 않았습니다. resolution 40·80의 군속도 오차는 펄스 중심 위치로 잰 방법의 정밀도(약 1 %)보다 작아 표에 적지 않았습니다.</p>

경험칙인 파장당 8칸 근처(resolution 20)에서도 45파장을 지나면 위상이 한 파장 가까이 늦습니다. 긴 도파로, 공진기, 간섭계처럼 위상이 결과를 정하는 구조에서는 8칸이 충분하지 않을 수 있습니다. 실제 예제에서는 재료 경계와 얇은 층 때문에 차이가 더 커졌습니다. 14편의 0.29 µm 박막은 resolution 40에서 11.7칸이었고, resolution 80과 추출 효율이 최대 54 % 달랐습니다. 09편의 역설계는 resolution 10에서 mode 1 투과율 0.780이었지만 같은 설계를 resolution 20으로 다시 재면 0.639였습니다.

<h2 id="meep-code">3. Meep 코드에서</h2>

```python
# code/resolution_dispersion_gif.py (이 페이지)
def run(res):
    si = mp.Medium(index=N_SI)
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, L), resolution=res, dimensions=1, default_material=si,
                        boundary_layers=[mp.PML(DPML)],
                        sources=[mp.Source(mp.GaussianSource(FCEN, fwidth=FWIDTH), component=mp.Ex,
                                           center=mp.Vector3(0, 0, Z_SRC))])
```

- 무엇: `resolution`은 `Simulation`의 인자 하나입니다. 길이 단위가 a일 때 a당 격자 수이고, 기본값은 없습니다.
- 왜: 파장당 칸 수는 resolution × λ₀ / n로 직접 계산해 두는 것이 좋습니다. 위 계산에서 resolution 20은 진공 파장에 대해 31칸이지만 Si 안에서는 8.9칸입니다.
- 틀리면: 공기 기준으로 resolution을 고르면 고굴절률 재료 안에서 칸 수가 n배 모자랍니다. reference run과 구조 run의 resolution이 다르면 [flux 정규화]({{ site.baseurl }}/terms/flux-normalization/)가 성립하지 않습니다.

```python
# code/straight_waveguide.py (04편): change one thing at a time
for res, dpml in ((25, 1.0), (70, 1.0), (50, 0.5)):
    sim, mon_in, mon_out = build(res, dpml)
    r = run_and_measure(sim, mon_in, mon_out)
```

- 무엇: 기준(resolution 50, PML 1)에서 resolution만 바꾼 run 두 개와 PML만 바꾼 run 하나를 더 돌립니다.
- 왜: resolution이 충분한지는 미리 알 수 없어서, 올려 보고 결과가 멈추는지로 판단합니다. 자세한 절차는 [수렴 확인]({{ site.baseurl }}/terms/convergence-check/)에 있습니다.
- 틀리면: resolution과 다른 설정을 함께 바꾸면 어느 쪽이 결과를 바꿨는지 알 수 없습니다.

<h2 id="in-examples">4. 예제에서의 쓰임</h2>

| 예제 | resolution | 무엇이 resolution을 정했나 | 올렸을 때 |
|---|---|---|---|
| [02 경계 조건]({{ site.baseurl }}/boundary-pml/) | 12 | 강의 값, 7 case를 10초 안에 | 24에서 PML 반사 지표 4.5 → 5.1 × 10⁻⁴, 순위는 그대로 |
| [03 reference 빼기]({{ site.baseurl }}/reference-subtraction/) | 20 | 원기둥 반지름 0.75 µm | 40에서 R+T+S 0.9988 → 0.9997, Q_sca 2.515 → 2.628 |
| [04 직선 도파로]({{ site.baseurl }}/straight-waveguide/) | 50 | 0.5 µm Si 코어 | 25에서도 T 0.999996 |
| [05 굽은 도파로]({{ site.baseurl }}/waveguide-bend-90/) | 25 | ε = 12 도파로 폭 1a | 40에서 T 0.200 → 0.189 |
| [09 bend 역설계]({{ site.baseurl }}/bend-inverse/) | 10 (최적화) | 계산 시간 | 같은 설계를 20에서 재면 0.780 → 0.639 |
| [12 고리 공진기]({{ site.baseurl }}/ring-resonator/) | 10 (공식) | 공식 예제 값 | 20·30에서 주파수는 0.3 % 안, Q는 1675 → 2132 → 1610 |
| [14 박막 광추출]({{ site.baseurl }}/extraction-efficiency/) | 80 (원통 좌표) | 0.29 µm 박막 | 40과 비교하면 층 위쪽 쌍극자에서 최대 54 % 차이 |

<h2 id="pitfalls">5. 돌아가는데 틀리는 경우</h2>

| 증상 | 원인 | 확인법 | 고침 |
|---|---|---|---|
| resolution을 올릴 때마다 결과가 계속 변함 | 얇은 층, 틈, 소멸장 같은 짧은 길이가 몇 칸뿐 | 가장 짧은 특징 길이에 들어가는 칸 수를 계산 | 그 길이에 10칸 이상이 되도록 올리거나, 원통 좌표·2D 축소로 비용을 줄여 확보 (14편) |
| 공진기 Q가 resolution에 따라 오르내림 | 계단 모양 경계가 격자마다 다르게 놓임 | resolution 3점 이상으로 Q를 표로 | Q는 주파수보다 늦게 수렴한다고 보고 범위로 보고 (12·13편) |
| 금속이 있는 구조만 수렴하지 않음 | 분산 재료에는 subpixel averaging이 적용되지 않음 (공식 FAQ) | 금속 경계 근처 칸 수와 skin depth 비교 | skin depth를 풀 만큼 resolution을 올림 |
| 긴 도파로·간섭계의 위상이 해석값과 다름 | 수치 분산으로 위상이 누적해 어긋남 | 위 표의 위상 오차 × 진행 거리 | 파장당 칸 수를 올리거나 진행 거리를 줄임 |
| 점원의 장 진폭이 resolution에 따라 커짐 | 점원 전류가 한 격자 칸에 들어가 칸이 작을수록 전류 밀도가 큼 (공식 FAQ) | 진폭 대신 flux·LDOS로 비교 | 결과를 source 진폭이 아니라 같은 resolution의 입사 flux로 정규화 |
| resolution을 낮췄더니 분산 재료에서 발산 | Δt가 커져 [Courant 조건]({{ site.baseurl }}/terms/courant-condition/)의 재료 한계를 넘음 | Courant만 낮춘 run과 비교 | Courant를 함께 낮춤 |
| resolution을 바꾼 run의 투과율만 이상함 | reference run을 이전 resolution으로 재사용 | 두 run의 resolution 비교 | 같은 resolution으로 reference를 다시 계산 |

<h2 id="inverse-design">6. inverse design에서</h2>

역설계에는 resolution이 두 개 있습니다. 시뮬레이션 격자와 설계 변수(밀도) 격자입니다. 최적화기는 시뮬레이션 격자에서 잰 성능만 보므로, 그 격자의 계단 오차나 수치 분산까지 이용하는 설계를 만들 수 있습니다. 09편의 설계가 resolution 10에서 0.780이던 투과율을 resolution 20에서 0.639로 잃은 것이 이 경우입니다.

대응은 세 가지입니다. 목표 resolution에서 최적화하거나 마지막 몇 단계를 목표 resolution으로 다시 돌립니다. filter 반경을 시뮬레이션 격자 몇 칸 이상으로 잡아 설계가 격자보다 큰 무늬만 갖게 합니다. 최종 설계는 더 높은 resolution의 새 시뮬레이션에서 다시 재서 보고합니다. adjoint gradient의 정확도도 resolution에 따라 달라지므로 유한 차분 검사는 최적화에 쓸 resolution에서 합니다.

<h2 id="connections">7. 연결</h2>

- 함께 보면 좋은 개념: [수렴 확인]({{ site.baseurl }}/terms/convergence-check/), [Courant 조건]({{ site.baseurl }}/terms/courant-condition/), [에너지 보존 검사]({{ site.baseurl }}/terms/energy-conservation/)
- 코드: [code/resolution_dispersion_gif.py](https://github.com/jin-castle/meep-examples/blob/main/code/resolution_dispersion_gif.py) · 결과 [result.json]({{ site.baseurl }}/assets/meep/terms-resolution/result.json)
- Meep 공식 문서: [FAQ: What is a good rule of thumb for the grid resolution?](https://meep.readthedocs.io/en/master/FAQ/#what-is-a-good-rule-of-thumb-for-the-grid-resolution) · [FAQ: How does Meep deal with numerical dispersion?](https://meep.readthedocs.io/en/master/FAQ/#how-does-meep-deal-with-numerical-dispersion) · [Subpixel Smoothing](https://meep.readthedocs.io/en/master/Subpixel_Smoothing/) · [Python API: Simulation](https://meep.readthedocs.io/en/master/Python_User_Interface/#simulation)
- 참고 문헌: A. Taflove, S. C. Hagness, *Computational Electrodynamics: The Finite-Difference Time-Domain Method*, 3rd ed., Artech House (2005), 4장

<details markdown="1">
<summary>source 파형 (이 페이지의 run 공통)</summary>

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-resolution/00_source.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-resolution/00_source.png" alt="GaussianSource(fcen 1/1.55, fwidth 0.25)의 시간 파형과 스펙트럼. 정점 t0 = 20." loading="lazy">
  </a>
  <figcaption>GaussianSource(fcen = 1/1.55, fwidth = 0.25). 정점 t0 = 20입니다. 위상 비교는 중심 주파수 하나의 DFT로 했습니다.</figcaption>
</figure>

</details>
