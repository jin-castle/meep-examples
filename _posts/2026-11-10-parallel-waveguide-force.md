---
layout: lesson
lesson_title: "두 도파로 사이에서 빛이 미는 힘은 얼마일까요?"
lesson_summary: "평행한 두 실리콘 도파로 사이의 광력을 Maxwell 응력 텐서로 재고, MPB의 모드 주파수 미분과 교차검증합니다. ω를 고정할 때와 k를 고정할 때 곡선이 왜 달라지는지 봅니다."
lesson_goals:
  - "add_force와 진공 속 ForceRegion 선 두 개로 힘을 재고 전송 전력으로 정규화한다."
  - "z로 무한한 도파로를 2D 단면 + Bloch k_point로 다루고, match_frequency로 고정 주파수의 k를 찾는다."
  - "응력 텐서를 Povinelli 2005 Eq.1과 교차검증하고, 선 monitor가 수렴하지 않는 좁은 틈을 가려낸다."
lesson_prerequisites: "04편 EigenModeSource와 flux 정규화 · 12편 Harminv와 모드"
date: 2026-11-10
title: "Meep Example 28 · 평행한 두 도파로 사이의 광력 — Maxwell 응력 텐서, MPB Eq.1, 고정 ω와 고정 k"
title_en: "Meep Example 28 · Optical force between two parallel waveguides — the Maxwell stress tensor, the MPB Eq.1 route, and fixed-ω versus fixed-k"
lang: ko
series: meep-examples
part: 28
level: intermediate
runtime: "한 코어에서 (s, mode)당 62초; 40회 약 40분"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Optical_Forces/"
tags: [meep, fdtd, optical-force, stress-tensor, mpb, eigenmode, waveguide, povinelli]
image: /assets/meep/28/02_results.png
excerpt: "평행한 두 실리콘 도파로 사이의 광력을 Maxwell 응력 텐서와 MPB의 모드 주파수 미분으로 구합니다. 대칭·반대칭 모드의 힘과 고정 주파수·고정 파수 조건을 비교합니다."
---
<h2 id="observe">1. 관찰하기: 두 도파로 사이의 힘</h2>

같은 두 도파로에 빛을 넣어도 모드에 따라 서로 당기거나 밀어낼 수 있을까요? 아래 그래프에서 대칭·반대칭 모드의 힘 부호와, 간격에 따른 변화를 찾아보세요.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/28/02_results.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/28/02_results.png" alt="평행한 두 실리콘 도파로의 간격에 따른 대칭·반대칭 모드의 광력과 응력 텐서 및 MPB 계산 비교" loading="eager"></a>
<figcaption>실제 Meep·MPB 계산 결과입니다. 음수는 인력, 양수는 척력입니다. 고정 주파수 조건과 고정 파수 조건의 곡선을 구별해 읽습니다.</figcaption>
</figure>

<details markdown="1">
<summary>계산 요약과 실행 시간</summary>

- **무엇을 계산하나요?** 굴절률 3.45, 정사각형 단면 a×a, 간격 s인 두 실리콘 도파로의 광력입니다. 결합한 대칭·반대칭 모드는 간격에 따라 주파수가 달라집니다. Meep은 `add_force`로 Maxwell 응력 텐서를 적분하고, MPB는 모드 주파수 미분으로 같은 힘을 구합니다(Povinelli 2005 식 (1), F = −(1/ω)(dω/ds)|_k U).
- **어떤 결과가 나왔나요?** 논문의 고정 a/λ = 0.2 조건에서 대칭 모드는 모든 간격에서 인력이며, s/a = 0.1–1.0의 무차원 힘 (F/L)(ac/P)이 논문 그림 1(c)와 0.04 안에서 맞습니다. 반대칭 모드는 s/a ≥ 0.1에서 척력이며 s/a = 0.2에서 +0.66의 피크를 보이고, s/a ≥ 0.25에서 논문과 맞습니다. 응력 텐서와 식 (1)의 차이는 중앙값 2–3%입니다. 공식 예제는 ω 대신 k_z = 0.5를 고정하므로 다른 곡선을 만듭니다(s = 0.5의 대칭 모드: −0.198 대 −0.291).
- **무엇을 주의하나요?** ω와 k 중 무엇을 고정하는지 먼저 정합니다. 좁은 틈에서는 응력 텐서 선 모니터의 수렴이 느립니다(s/a = 0.1: Meep +0.50, 식 (1) +0.11). 이 구간은 모드 주파수 미분과 비교해 판정합니다. 고정 ω에서 `find_k`를 쓰면 식 (1)은 (F/L)(ac/P) = (1/f)·dk/ds가 됩니다.
- **코드는 어디에 있나요?** 마지막 절에 전체 스크립트를 실었습니다. 한 (s, mode) 계산은 한 코어에서 약 62초입니다.

</details>

<details markdown="1">
<summary>학습 범위와 활용 분야</summary>

- `add_force`와 `ForceRegion`으로 Maxwell 응력 텐서(Maxwell stress tensor) 힘을 재는 법. 닫힌 상자 대신 두 선 monitor로 충분한 이유
- 2D 단면에 `k_point`를 주어 z 방향으로 무한한 도파로의 모드를 다루는 법, `get_eigenmode`의 `match_frequency`로 k를 찾는 법
- 같은 구조의 힘을 두 번째 방법(MPB, 모드 주파수의 미분)으로 구해 교차 검증하는 법
- 논문(고정 주파수)과 공식 예제(고정 k)가 왜 다른 곡선을 주는가

**전제 지식**: 04편의 `EigenModeSource`와 flux 정규화, 12편의 Harminv와 모드 개념. **공식 예제**: [Optical Forces 튜토리얼](https://meep.readthedocs.io/en/latest/Python_Tutorials/Optical_Forces/), 스크립트 [parallel-wvgs-force.py](https://github.com/NanoComp/meep/blob/master/python/examples/parallel-wvgs-force.py) · [parallel-wvgs-mpb.py](https://github.com/NanoComp/meep/blob/master/python/examples/parallel-wvgs-mpb.py).

두 도파로를 나란히 놓으면 한쪽의 evanescent 꼬리가 다른 쪽에 걸린다. 결합한 두 모드 중 symmetric 모드는 간격이 좁아질수록 주파수가 내려가고 anti-symmetric 모드는 올라간다. 에너지 U = Nħω가 든 모드에서 간격을 Δs만큼 바꾸면 에너지가 Δω에 비례해 바뀌고, 그 미분이 힘이다. 질문은 둘이다. 이 힘을 FDTD로 직접(응력 텐서) 잴 수 있는가, 그리고 그 값이 모드 주파수의 미분으로 구한 값·논문 그림과 맞는가.

### 어디에 쓰이는가

빛으로 구조를 움직이는 optomechanics의 출발점이다. 100 mW, 310 nm Si 도파로에서 이 힘은 수 nN/µm이고 30 µm 현수 길이에서 20 nm쯤 휜다(논문 Fig.2). 같은 계산이 광 트위저, 공진기–역학 결합(cavity optomechanics), 자체 정렬 커플러에 쓰인다.

| 응용 | 이 글의 어떤 것을 쓰는가 | 그 다음에 필요한 것 |
|---|---|---|
| 현수 도파로 광 구동기 | 간격별 (F/L)(ac/P) 곡선 | 빔 역학(Euler–Bernoulli) |
| cavity optomechanics | dω/ds (optomechanical coupling g = dω/dx) | 12편 공진기 Q |
| 광 트위저·입자 결합 | 응력 텐서 monitor 배치 | 03편 산란장 |

</details>

<h2 id="predict">2. 예측하기: 힘의 부호와 두 방법의 일치</h2>

<fieldset class="prediction">
<legend>도파로 간격에 따른 힘을 그릴 때 주파수 ω와 파수 k 중 무엇을 고정하는지가 중요할까요?</legend>
<label><input type="radio" name="parallel-waveguide-force-prediction" value="different"> 중요하다. 고정 조건이 다르면 곡선도 달라진다.</label>
<label><input type="radio" name="parallel-waveguide-force-prediction" value="same"> 같은 구조이므로 두 곡선은 항상 같다.</label>
</fieldset>

<details markdown="1">
<summary>예측의 근거와 판정 기준 보기</summary>

| 물리량 | 내 예측 | 근거 |
|--------|---------|------|
| symmetric 모드 힘 부호 | 전 구간 음수(인력) | 간격이 줄면 주파수가 내려감 |
| anti-symmetric 모드 | s/a ≳ 0.3 척력, 작은 틈에서 인력 전환 | 논문 Fig.1(c) |
| 응력 텐서 vs Eq.1 | 5% 안 | 수학적으로 같은 양 |
| 고정 k vs 고정 ω 곡선 | 다르다 | 미분의 경로가 다름 |
| 노트북(2020) 주파수 | 1e-6 안 | 같은 코드 |

**판정 기준**: symmetric이 양수로 나오거나 두 방법이 10% 넘게 다르면 force 선 위치·정규화를 의심한다.

</details>

<h2 id="understand">3. 원리 이해하기: 모드 주파수의 미분이 힘이다</h2>

{% include chapter-illustration.html %}

k가 보존된 채 간격 s를 단열적으로 바꾸면

$$
F=-\frac{1}{\omega}\left.\frac{d\omega}{ds}\right|_{k}U,\qquad
\frac{F}{L}\frac{ac}{P}=-\frac{1}{\omega}\frac{d\omega}{ds}\frac{ac}{v_g}
$$

P = v_g U/L이 전송 전력이다. 음수가 인력. 주파수를 고정하고 k(s)를 구했다면 dω/ds|_k = −v_g·dk/ds|_ω 이므로 무차원 힘은 (1/f)·dk/ds (k는 2π/a 단위)가 된다. 응력 텐서는 같은 양을 장에서 직접 적분한다: 한 도파로를 감싼 면에서 T_xx의 면적분이 x 방향 힘이다.

| 기호 | 뜻 | 코드 변수 |
|---|---|---|
| a | 도파로 변 길이(= 1) | `a` |
| s | 간격(d/a) | `s` |
| k_z | 전파 상수(2π/a) | `k_point.z` |
| f | 주파수(c/a) | `fcen` |
| (F/L)(ac/P) | 무차원 힘 | `-force/flux` |

**가정과 유효 범위**: 2D 단면 + Bloch k_z(z로 무한), 무손실 n 3.45, 진공 clad, 한 모드만 여기. 논문은 고정 a/λ = 0.2, 공식 예제는 고정 k_z = 0.5.

### 시뮬레이션 설계도

![layout]({{ site.baseurl }}/assets/meep/28/01_layout_modes.png)
*(a) 셀 7×5 µm(PML 1), Si 도파로 둘(간격 s = 0.5), force 선 두 개(빨강 x = 0.49 s, 주황 x = 0.5 s + 1.01 a), 초록 점선이 셀 전체 flux 면. (b)(c) 두 모드의 |Ey|. (d) F/P 누적 DFT의 시간 수렴. (e) 고정 k의 모드 주파수 — □ 현재 판 res 30, × 2020 노트북. (f) 고정 f = 0.2에서 찾은 k_z.*

| 항목 | 값 | 출처 | 비고 |
|---|---|---|---|
| 해상도 | 40 px/a | 공식 예제 | 사다리 20/40/80 |
| 셀 | (5+2)×(3+2), PML 1 | 공식 예제 | |
| 도파로 | n 3.45, a 1, 간격 s 0.05–1.0 | 논문·예제 | |
| 대칭 | Mirror X(±1)·Mirror Y(−1) | 예제 | x 부호가 sym/anti-sym |
| 모드 | ODD_Y band 1(sym)/2(anti-sym) | 예제 | |
| k 또는 f | k_z 0.5 고정 / f 0.2 고정(match_frequency) | 예제 / 논문 | |
| source | EigenModeSource Gaussian fwidth 0.1 f | 예제 | |
| monitor | flux 면 z(셀 전체), ForceRegion x 두 선 | 예제 | 선 하나는 틈 안 |
| 종료 | until_after_sources 1500 | 예제 | 3000과 4e-5 차 |

**강의 노트북과의 차이**: 공식 노트북은 res 30, s 0.1 step 0.1이고 `data:`(힘) 줄은 저장되어 있지 않다. 이 글은 res 40, step 0.05, 두 조건(k·f 고정).

<h2 id="run">4. 실행하기: 코드 따라가기</h2>

### ① 파라미터 — 무엇을 고정하는가

```python
fixed = "f"           # "k": k_z 0.5 (official example)   "f": a/λ 0.2 (paper)
k_point = mp.Vector3(z=0.5)
```
무엇: 고정할 양을 고른다. 왜: 논문과 예제가 다른 곡선을 그린 이유가 여기 있다. 틀리면: 같은 s에서 symmetric 힘이 −0.20(k 고정)인지 −0.29(f 고정)인지 달라진다.

### ② 구조 — 간격 s의 두 블록

```python
geometry = [mp.Block(center=mp.Vector3(-0.5*(s+a)), size=mp.Vector3(a, a, mp.inf), material=Si),
            mp.Block(center=mp.Vector3(+0.5*(s+a)), size=mp.Vector3(a, a, mp.inf), material=Si)]
symmetries = [mp.Mirror(mp.X, phase=-1 if xodd else 1), mp.Mirror(mp.Y, phase=-1)]
```
무엇: x 거울의 위상으로 symmetric(+1)·anti-symmetric(−1) 모드를 고른다. 왜: 대칭으로 셀을 1/4로 줄이고 원하는 모드만 남긴다. 틀리면: Y 위상을 +1로 두면 ODD_Y 모드가 사라져 `get_eigenmode`가 다른 모드를 준다.

### ③ Source — 모드 주파수를 먼저 찾는다

```python
sim.init_sim()
em = sim.get_eigenmode(0.2 if fixed == "f" else 0.22, mp.Z, vol, band, k_point,
                       match_frequency=(fixed == "f"), parity=mp.ODD_Y)
fcen = em.freq;  kz = em.k.z if fixed == "f" else 0.5
```
무엇: k 고정이면 그 k의 모드 주파수를, f 고정이면 f = 0.2가 되는 k를 MPB로 찾는다. 왜: source·monitor 주파수와 Bloch k를 같은 모드에 맞춰야 한다. 틀리면: `match_frequency=False`인 채 0.2를 넘기면 입력 주파수가 무시되어 k 0.5의 곡선이 나온다.

### ④ 경계 — k_point가 있으면 z로 무한

```python
sim = mp.Simulation(resolution=40, cell_size=cell, geometry=geometry, boundary_layers=[mp.PML(1.0)],
                    symmetries=symmetries, k_point=mp.Vector3(z=kz))
```
무엇: 2D 단면에 z 방향 Bloch 위상을 준다(복소장). 왜: 도파로는 z로 무한하고 모드는 e^{ik_z z}로 진행한다. 틀리면: k_point 없이 2D로 두면 전파가 없는 2D 공진 문제가 된다.

### ⑤ Monitor — flux 면 하나, force 선 둘

```python
wvg_flux  = sim.add_flux(fcen, 0, 1, mp.FluxRegion(direction=mp.Z, center=mp.Vector3(), size=mp.Vector3(sx, sy)))
wvg_force = sim.add_force(fcen, 0, 1,
    mp.ForceRegion(mp.Vector3(0.49*s), direction=mp.X, weight=+1, size=mp.Vector3(y=sy)),
    mp.ForceRegion(mp.Vector3(0.5*s + 1.01*a), direction=mp.X, weight=-1, size=mp.Vector3(y=sy)))
```
무엇: 전송 전력은 셀 전체 flux 면 하나(두 도파로 합, 대칭이라 반이 한 도파로), 힘은 오른쪽 도파로를 사이에 둔 두 선. 왜: 닫힌 상자의 y 면은 위아래 대칭으로 상쇄되고, 틈이 좁으면 도파로별 flux 면이 겹친다. 응력 텐서는 진공에서 재야 한다. 틀리면: 선을 도파로 안에 두면 Abraham–Minkowski 문제로 값이 정의되지 않는다.

### ⑥ 실행 — 정상상태까지

```python
sim.run(until_after_sources=1500)
flux = mp.get_fluxes(wvg_flux)[0];  force = mp.get_forces(wvg_force)[0]
```
무엇: 가우시안 펄스 뒤 1500 더 돌린다. 왜: 장이 0으로 감쇠하지 않는(도파로 모드) 문제라 종료 조건 대신 충분한 시간을 준다. 틀리면: 너무 길면 DFT 누적값이 커져 반올림 오차, 너무 짧으면 F/P가 흔들린다(1500 vs 3000: 4e-5).

### ⑦ 후처리 — −F/P와 Eq.1

```python
F_over_P = -force / flux                      # (F/L)(ac/P)
# MPB route at fixed f: k(s) from find_k → (1/f) * dk/ds (centered difference)
```
무엇: 부호 약속(음수 = 인력)을 맞추고, MPB의 k(s)로 Eq.1을 쓴다. 왜: 두 독립 방법이 맞아야 monitor 배치를 믿을 수 있다. 틀리면: 고정 f에서 예제의 식 −(1/f)(df/ds)/v_g를 그대로 쓰면 df = 0이라 힘이 0이 된다.

<h2 id="interpret">5. 결과 해석하기</h2>

![results]({{ site.baseurl }}/assets/meep/28/02_results.png)
*(a) 예제 조건(k_z 0.5): Meep 응력 텐서(점) vs MPB Eq.1(선, res 64; △ res 128 검산). (b) 논문 조건(f 0.2): Meep(채운 점) vs 논문 Fig.1(c)를 눈으로 읽은 값(○ anti-symmetric, + symmetric) vs MPB find_k Eq.1(선). (c) Meep − 논문. symmetric은 ±0.04, anti-symmetric은 s/a ≤ 0.2에서 +0.1~+0.2.*

![forward dft]({{ site.baseurl }}/assets/meep/28/03_forward_dft.png)
*(a)(b) 논문 조건 s = 0.5의 |Ey| DFT, 빨강·주황이 force 선. (c) 응력 텐서 − Eq.1(MPB) 차: s/a ≥ 0.25에서 0.05 아래, 좁은 틈에서 벌어진다.*

| s/a | sym Meep (f 0.2) | sym 논문(눈읽기) | anti-sym Meep | anti-sym 논문 | anti-sym MPB Eq.1 |
|---|---|---|---|---|---|
| 0.05 | −1.17 | −1.25 | −0.015 | −2.3 | — |
| 0.10 | −0.92 | −0.95 | +0.500 | +0.10 | +0.11 |
| 0.15 | −0.82 | −0.78 | +0.638 | +0.45 | — |
| 0.20 | −0.69 | −0.65 | +0.664 | +0.55 | — |
| 0.25 | −0.61 | — | +0.645 | +0.57 | — |
| 0.50 | −0.29 | −0.31 | +0.399 | +0.40 | +0.38 |
| 1.00 | −0.09 | −0.10 | +0.116 | +0.13 | — |

![animation]({{ site.baseurl }}/assets/meep/28/05_anim_sym.gif)
*s = 0.5 symmetric 모드(f 0.2, k 0.386)의 Re Ey(x, y, t). 단면 + Bloch k 계산이라 전파 방향은 보이지 않고 두 도파로가 같은 위상으로 진동한다. 프레임 간격은 광 주기의 (n + 1/8)배. 아래 띠는 오른쪽 도파로 중심의 Ey.*

### 예측과 비교

| 물리량 | 내 예측 (§2) | 시뮬레이션 | 판정 |
|--------|-------------|-----------|------|
| symmetric 부호 | 전 구간 음수 | 20점 전부 음수, 논문과 최대 0.039 차 | ✅ |
| anti-symmetric 모양 | 척력, 작은 틈에서 인력 전환 | 0.05 −0.015, 0.1 이상 양수, 최대 +0.664 @ 0.2 | ✅ (값은 0.15 이하에서 논문보다 0.1~0.2 높음) |
| 응력 텐서 vs Eq.1 | 5% 안 | 중앙 1.9%(k 고정)·2.6%(f 고정); s/a 0.1 anti-sym은 363% | ✅ (좁은 틈 제외) |
| 고정 k vs 고정 ω | 다르다 | s 0.5: sym −0.198 vs −0.291, anti-sym +0.179 vs +0.399 | ✅ |
| 노트북 주파수 | 1e-6 안 | 균일 +0.5%(4.6~7.8e-3) | ❌ |

다섯 예측 중 넷이 맞았다. 노트북(2020-05) 주파수 20줄은 현재 Meep 1.33에서 같은 res 30으로 돌려도 0.5% 높게 나온다. 11·13편의 Harminv·LDOS 경로가 2019~2020 수치와 1e-9로 같았던 것과 달리 `get_eigenmode`(MPB 경계 평활) 수치는 판에 따라 1e-3 수준으로 움직인다. 힘의 비 −F/P는 그보다 둔감하다. 좁은 틈의 anti-symmetric 힘은 응력 텐서가 논문·Eq.1보다 크게 나온다. 틈 0.1은 res 40에서 4 px이고 안쪽 force 선이 벽에서 1~2 px이라 틈 안의 Ex 증강(논문이 말한 d → 0 극한 −21.54의 원인)을 격자가 담지 못한다. res 80에서도 0.466 → 0.458(k 고정, s 0.1)로 천천히만 움직인다.

### 수렴성

| 변수 | 값 | 결과 | 비고 |
|---|---|---|---|
| 해상도 (k 고정) | 20 / 40 / 80 | s 0.5: sym −0.198/−0.198/−0.195, anti-sym +0.155/+0.179/+0.180; s 0.1 anti-sym +0.481/+0.466/+0.458 | 40→80 최대 1.7% |
| 실행 시간 | 1500 / 3000 | 상대 차 ≤ 4.2e-5 | 1500이면 충분 |
| Meep − MPB (s 0.5) | res 40 → 80 | 0.0011 → 0.0002(anti-sym), 0.0023 → 0.0006(sym) | 비 0.16·0.27 — 이산화 성분 |
| MPB 해상도 | 64 / 128 | 힘 차 ≤ 2.4%(k 고정)·1.1%(f 고정) | |

### 주장할 수 있는 것 / 없는 것

- 할 수 있는 것: 고정 a/λ 0.2에서 symmetric 모드의 인력 곡선(s/a 0.1~1.0)과 anti-symmetric의 s/a ≥ 0.25 구간은 논문 Fig.1(c)와 눈읽기 오차 안에서 같다. 응력 텐서와 모드 주파수 미분은 같은 힘을 준다(좁은 틈 제외). 공식 예제 곡선(k_z 0.5)은 논문 곡선이 아니다.
- 할 수 없는 것: s/a ≤ 0.15의 anti-symmetric 힘과 d → 0 극한(−1.49/−21.54) — 해상도가 모자란다. 논문 값은 그림을 눈으로 읽은 것(±0.08)이다. 유한 길이·기판(SOI) 효과는 2D 단면 + k로는 없다.

### 흔한 실수

| 증상 | 원인 | 고치는 법 |
|------|------|----------|
| 논문 곡선과 전체가 어긋남 | k_z 고정(예제) vs ω 고정(논문) | `match_frequency=True`로 k를 찾아 k_point를 다시 세운다 |
| MPB 힘이 전부 0 | 고정 f에서 df = 0인 예제 식 사용 | (1/f)·dk/ds |
| 좁은 틈에서 힘이 Eq.1과 다름 | force 선이 벽에서 1~2 px | 해상도를 올리거나 Eq.1을 쓴다 |
| 힘 부호가 반대 | weight 부호·−force/flux 약속 | 음수 = 인력으로 통일 |
| F/P가 시간에 따라 흔들림 | until이 짧음 | 1500 이상, 3000과 비교 |
| 노트북 수치와 1e-3 차 | eigenmode solver 판 차 | 힘의 비로 비교한다 |

### 직접 해보기

| 바꿀 것 | 예상 변화 | 확인할 수치 |
|---------|----------|------------|
| 해상도 160, s/a 0.05~0.15 anti-sym | 논문 +0.10(0.1)·−2.3(0.05)에 다가감 | s 0.1의 힘 |
| 안쪽 force 선을 0.49 s → 0.3 s | 틈 안 어디서 재도 같아야 함 | 선 위치별 차 |
| Hz 편광(TE) 모드 | 다른 곡선 | 부호 전환 위치 |
| a/λ 0.15·0.25 | 결합 세기 변화 | s 0.5의 힘 |

<h2 id="check">6. 이해 확인하기</h2>

1. symmetric 모드의 힘이 음수인 이유를 주파수의 간격 의존으로 설명하면? (§3)
2. 고정 f에서 MPB Eq.1을 쓸 때 예제의 식 −(1/f)(df/ds)/v_g가 왜 0을 주는가? (§4 ⑦)
3. s/a 0.1에서 응력 텐서와 Eq.1이 5배 다른데 어느 쪽을 믿어야 하고 왜인가? (§5)

<h2 id="reference">7. 전체 코드와 참고 자료</h2>

`code/parallel_waveguide_force.py` — 한 (s, mode, fixed) 조합을 계산해 JSON으로 저장한다. sweep은 s 0.05~1.0, mode odd/even, fixed k/f를 바깥에서 돈다. MPB 경로는 `parallel-wvgs-mpb.py`에 `find_k`를 더해 고정 주파수 조건의 파수를 구하는 방법입니다.

<details>
<summary>parallel_waveguide_force.py (클릭해서 펼치기)</summary>
{% highlight python %}
"""Optical force between two parallel Si waveguides (Povinelli 2005 Fig.1(c) / Meep parallel-wvgs-force.py).
--fixed k : official example (k_z 0.5 fixed)    --fixed f : paper condition (a/lambda 0.2 fixed, k found by match_frequency)
"""
import argparse, json, os
import numpy as np
import meep as mp

ap = argparse.ArgumentParser()
ap.add_argument("--s", type=float, required=True)            # gap s/a
ap.add_argument("--mode", choices=["odd", "even"], required=True)  # odd = anti-symmetric, even = symmetric
ap.add_argument("--fixed", choices=["k", "f"], default="k")
ap.add_argument("--f0", type=float, default=0.2)
ap.add_argument("--resolution", type=float, default=40)
ap.add_argument("--after", type=float, default=1500)
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

Si = mp.Medium(index=3.45)
dpml, sx, sy, aa = 1.0, 5, 3, 1.0
cell = mp.Vector3(sx + 2 * dpml, sy + 2 * dpml, 0)
s, xodd = a.s, a.mode == "odd"
geometry = [mp.Block(center=mp.Vector3(-0.5 * (s + aa)), size=mp.Vector3(aa, aa, mp.inf), material=Si),
            mp.Block(center=mp.Vector3(+0.5 * (s + aa)), size=mp.Vector3(aa, aa, mp.inf), material=Si)]
symmetries = [mp.Mirror(mp.X, phase=-1 if xodd else 1), mp.Mirror(mp.Y, phase=-1)]
band = 2 if xodd else 1
k_point = mp.Vector3(z=0.5)

# (1) mode frequency (fixed k) or wavevector (fixed f)
sim = mp.Simulation(resolution=a.resolution, cell_size=cell, geometry=geometry, boundary_layers=[mp.PML(dpml)],
                    symmetries=symmetries, k_point=k_point)
sim.init_sim()
vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx, sy))
if a.fixed == "k":
    em = sim.get_eigenmode(0.22, mp.Z, vol, band, k_point, match_frequency=False, parity=mp.ODD_Y)
    fcen, kz = float(np.real(em.freq)), 0.5
else:
    em = sim.get_eigenmode(a.f0, mp.Z, vol, band, k_point, match_frequency=True, parity=mp.ODD_Y)
    fcen, kz = float(np.real(em.freq)), float(em.k.z)
    k_point = mp.Vector3(z=kz)
sim.reset_meep()

# (2) launch the mode, measure flux (power) and stress-tensor force on the right waveguide
sim = mp.Simulation(resolution=a.resolution, cell_size=cell, geometry=geometry, boundary_layers=[mp.PML(dpml)],
                    symmetries=symmetries, k_point=k_point)
sim.change_sources([mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=0.1 * fcen), size=mp.Vector3(sx, sy),
                                       center=mp.Vector3(), eig_band=band, eig_kpoint=k_point, eig_match_freq=False,
                                       eig_parity=mp.ODD_Y)])
wvg_flux = sim.add_flux(fcen, 0, 1, mp.FluxRegion(direction=mp.Z, center=mp.Vector3(), size=mp.Vector3(sx, sy)))
wvg_force = sim.add_force(fcen, 0, 1,
                          mp.ForceRegion(mp.Vector3(0.49 * s), direction=mp.X, weight=1, size=mp.Vector3(y=sy)),
                          mp.ForceRegion(mp.Vector3(0.5 * s + 1.01 * aa), direction=mp.X, weight=-1, size=mp.Vector3(y=sy)))
sim.run(until_after_sources=a.after)
flux = float(mp.get_fluxes(wvg_flux)[0]); force = float(mp.get_forces(wvg_force)[0])
out = dict(s=s, mode=a.mode, fixed=a.fixed, fcen=fcen, kz=kz, flux=flux, force=force, F_over_P=-force / flux)
if mp.am_master():
    json.dump(out, open(os.path.join(a.out, f"{a.fixed}_{a.mode}_s{s}.json"), "w"), indent=1)
    print(f"data:, {a.mode}, {s}, F/P {-force / flux:+.5f}  (fixed {a.fixed}, f {fcen:.6f}, kz {kz:.6f})")
{% endhighlight %}
</details>

### 더 읽기

- M. L. Povinelli et al., "Evanescent-wave bonding between optical waveguides," Opt. Lett. 30, 3042 (2005); arXiv physics/0509073.
- P. T. Rakich, M. A. Popović, Z. Wang, Opt. Express 17, 18116 (2009) — Eq.1과 응력 텐서의 동치.
- Meep 문서 [Optical Forces](https://meep.readthedocs.io/en/latest/Python_Tutorials/Optical_Forces/), [Force spectra](https://meep.readthedocs.io/en/latest/Python_User_Interface/#force-spectra).
