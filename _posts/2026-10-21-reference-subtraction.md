---
layout: post
date: 2026-10-21
title: "Meep Example 03 · Reference run 빼기 — incident·total·scattered field, R·T·S 수지, 산란 단면적"
title_en: "Meep Example 03 · Reference-run subtraction — incident, total and scattered fields, the R·T·S budget, and a scattering cross section"
lang: ko
series: meep-examples
part: 3
level: beginner
runtime: "28 s (single core)"
meep_version: "1.33.0"
official_example: "https://github.com/NanoComp/meep/blob/master/python/examples/refl-quartz.py"
tags: [meep, fdtd, scattering, reference-subtraction, fresnel, flux]
image: /assets/meep/03/03_fields.png
excerpt: "run the same cell twice, without and with the object. The difference of the two fields is the scattered field; the difference of the two fluxes is what the object did to the power. Checked first in 1D (air | quartz, Fresnel formula), then on a 2D dielectric cylinder."
---
## TL;DR (English)

![hero]({{ site.baseurl }}/assets/meep/03/03_fields.png)

- **What**: run the same cell twice, without and with the object. The difference of the two fields is the scattered field; the difference of the two fluxes is what the object did to the power. Checked first in 1D (air | quartz, Fresnel formula), then on a 2D dielectric cylinder.
- **Result**: 1D reflectance matches Fresnel to 1.6 × 10⁻⁴ over 400–800 nm. For the cylinder, R = 0.082, T = 0.674, sideways S = 0.243, R + T + S = 0.999; the scattered-field flux through a closed box gives Q_sca = 2.515 against the 2D Mie value 2.513.
- **Takeaway**: subtract fields, not just fluxes, and know which one you are looking at. Flux is quadratic, so the flux of (E_total − E_inc) is the scattered power, not "total minus incident"; the two agree only where incident and scattered waves travel in opposite directions.
- **Code**: full script at the bottom, ~28 s on one core.

## 0. 이 글에서 배우는 것

- reference run(물체 없음)과 device run(물체 있음)을 같은 셀에서 돌리고, E_scat = E_total − E_inc로 산란장을 분리하기
- `get_flux_data` / `load_minus_flux_data`가 하는 일과, 그것이 "flux의 차"가 아니라 "field의 차의 flux"라는 것
- R·T·S 수지가 1로 닫히는 조건: 닫힌 flux box, 모든 면의 바깥 법선, total field의 flux 차
- 산란장의 flux로 산란 단면적 σ와 효율 Q_sca를 구하고 해석해(2D Mie)와 맞춰 보기
- 해석해가 있는 1D Fresnel 문제로 절차를 먼저 검증하는 습관

**전제 지식**: 02편의 참조 빼기, 01편의 flux box. **공식 예제**: [refl-quartz.py](https://github.com/NanoComp/meep/blob/master/python/examples/refl-quartz.py), [cylinder_cross_section.py](https://github.com/NanoComp/meep/blob/master/python/examples/cylinder_cross_section.py). **이전 글**: [02 · 경계 조건과 PML]({{ site.baseurl }}/boundary-pml/) · **다음 글**: [04 · Straight waveguide와 guided mode]({{ site.baseurl }}/straight-waveguide/)

## 1. 무엇을 알고 싶은가

빛이 물체를 만나면 일부는 되돌아오고(반사), 일부는 지나가고(투과), 나머지는 옆으로 흩어진다(산란). 시뮬레이션의 field는 이 모두가 섞인 total field다. 물체가 무엇을 했는지 보려면 물체가 없을 때의 field, 즉 incident field를 빼야 한다. 02편에서 경계가 만든 반사를 분리할 때 쓴 바로 그 방법이다. 이 글은 그 절차를 정답이 있는 문제(공기·석영 계면의 Fresnel 반사)로 먼저 검증하고, 정답이 없는 문제(유전체 원기둥)에서 R, T, S를 재어 수지가 1로 닫히는지, 산란 단면적이 해석해와 맞는지 본다.

## 2. 물리 한 페이지

입사파 E_inc는 물체 없이도 존재하는 field다. 물체를 넣으면 E_total = E_inc + E_scat이 되고, E_scat은 물체가 새로 만든 field다. 두 run의 source·셀·격자가 같으면 E_inc를 그대로 빼서 E_scat을 얻는다.

power는 field의 제곱이라 빼기가 그대로 옮겨가지 않는다. 어떤 면을 지나는 total field의 flux는 입사 flux + 산란 flux + 둘의 간섭항이다. 입사파와 산란파가 서로 반대 방향으로 지나는 면(왼쪽 면)에서는 간섭항이 거의 사라져 "flux의 차"와 "field 차의 flux"가 같지만, 입사파가 면과 나란히 지나는 면(위·아래)에서는 간섭항이 남는다. 그래서 두 수지를 구분한다.

$$
R=\frac{-(P_{\mathrm{left}}^{\mathrm{tot}}-P_{\mathrm{left}}^{\mathrm{inc}})}{P_{\mathrm{inc}}},\quad
T=\frac{P_{\mathrm{right}}^{\mathrm{tot}}}{P_{\mathrm{inc}}},\quad
S=\frac{\sum_{\mathrm{top,bottom}}(P^{\mathrm{tot}}-P^{\mathrm{inc}})}{P_{\mathrm{inc}}},\qquad R+T+S=1
$$

$$
P_{\mathrm{sc}}=\oint \mathbf S(E_{\mathrm{tot}}-E_{\mathrm{inc}})\cdot d\mathbf n,\qquad
\sigma_{\mathrm{sc}}=\frac{P_{\mathrm{sc}}}{I_{\mathrm{inc}}},\qquad Q_{\mathrm{sca}}=\frac{\sigma_{\mathrm{sc}}}{2r},\qquad
R_{\mathrm{Fresnel}}=\Big(\frac{1-n}{1+n}\Big)^2
$$

| 기호 | 뜻 | 코드 변수 |
|------|----|-----------|
| $P^{\mathrm{inc}}_{\mathrm{side}}$ | reference run에서 각 면을 지나는 flux | `inc_side[k]` |
| $P^{\mathrm{tot}}_{\mathrm{side}}$ | device run에서 각 면을 지나는 total field flux | `tot[k]` |
| $P_{\mathrm{inc}}$ | 오른쪽 면의 입사 power (분모) | `inc` |
| $P_{\mathrm{sc}}$ | 산란장만의 flux를 네 면에서 바깥 방향으로 합한 것 | `P_sc` from `scat` monitors |
| $I_{\mathrm{inc}}$ | 입사 power / box 폭 | `I_inc = inc / (2 * ym)` |
| $Q_{\mathrm{sca}}$ | 산란 단면적 / 기하 단면(2r) | `Q_sca` |
| $x=2\pi r/\lambda$ | 크기 매개변수 | `x_size` = 3.04 |

**가정과 유효 범위**: 2D, Ez 편광, 손실 없는 원기둥(n = 2), 유한 폭(8 µm)의 평면파. 1D 문제는 수직 입사·단일 계면이며 n(λ)은 Meep materials library의 fused_quartz 분산 모델이다.

### 결과 보기 전에 맞춰보기

| 물리량 | 내 예측 | 근거 |
|--------|---------|------|
| 1D 석영 반사율 (533 nm) | 3.5% | Fresnel, n = 1.46 |
| 1D R + T | 1.000 | 무흡수 |
| 원기둥 R + T + S | 1 (0.5% 안) | 손실 없음, 닫힌 box |
| 산란장 flux의 합 P_sc/P_inc | R + T + S보다 작음 | 간섭항이 빠지므로 |
| Q_sca | 2 근처 | x ≈ 3, n = 2면 공명 영역. Mie 값은 모름 |
| 산란장 모양 | 앞쪽으로 치우친 파면 + 원기둥 안의 정상파 | x > 1에서 전방 산란 우세 |

**판정 기준**: 1D R이 Fresnel에서 0.5%p 이상 벗어나면 정규화 오류. R + T + S가 1에서 2% 이상 벗어나면 box가 안 닫혔거나 weight 부호 실수.

## 3. 시뮬레이션 설계도

![layout]({{ site.baseurl }}/assets/meep/03/01_layout.png)
*2D 실험의 device run. 빨간 세로선 = 셀 전체 높이를 가로지르는 Ez 선원(PML까지 뻗어 평면파를 만든다), 검은 원 = 원기둥(r 0.75 µm, n 2), 파란 사각형 = flux box 네 면(x = ±5.1, y = ±3.8). 각 면에 monitor가 두 개씩 겹쳐 있다. 하나는 total field, 하나는 입사장을 뺀 산란장용. 보라 × = 종료 감시점. 동그라미 숫자는 §4의 단계 번호다.*

| 파라미터 | 값 | 왜 이 값인가 | 바꾸면 |
|----------|-----|-------------|--------|
| 1D 셀, 해상도 | 10 µm, 200 px/µm | 공식 refl-quartz 값. λ_min/n = 0.27 µm → 54 px | 해상도를 낮추면 Fresnel 오차 증가 |
| 1D 대역 | 400–800 nm, 25점 | 분산 곡선 전체와 비교 | — |
| 2D `fwidth` | 0.12 (width 8.3, t0 41.7) | 좁은 대역 → fcen 한 주파수의 깨끗한 field map | 넓히면 map이 여러 파장의 합이 된다 |
| 2D 셀, 해상도 | 14 × 10 µm, 20 px/µm | 강의 값. 원기둥 지름 30 px | 40에서 Q_sca가 4.6% 바뀐다(§5) |
| 원기둥 | r 0.75 µm, n 2.0 | 강의 값. x = 3.04 | n을 높이면 공명이 날카로워진다 |
| 선원 | x = −5.75, 높이 = 셀 전체, `is_integrated=True` | PML 안까지 뻗어야 가장자리 회절 없는 평면파 | 높이를 줄이면 가장자리에서 회절 |
| box | x ±5.1, y ±3.8 | source 바깥, PML 안쪽, 원기둥에서 3 µm 이상 | box가 source를 품으면 수지가 깨진다 |
| 종료 | 오른쪽 면 중앙 Ez가 1e-5로 감쇠 | 원기둥의 저장 에너지가 다 빠져나갈 때까지 | 이르게 끊으면 수지가 안 닫힌다 |

![source]({{ site.baseurl }}/assets/meep/03/00_source.png)
*2D source의 파형과 스펙트럼. width 8.3, t0 = 41.7. 대역이 좁아 flux monitor는 fcen 한 점만 쓴다.*

**강의 노트북과의 차이**: 강의 week 4는 왼쪽·오른쪽 monitor만 두고 A = 1 − R − T = 0.278을 "남은 몫"으로 둔다. 이 글은 위·아래 면을 더해 그 몫을 옆 방향 산란 S로 실측하고, 산란장 flux로 산란 단면적을 구해 2D Mie 해석해와 비교한다. 1D Fresnel 검증은 10_sources의 공식 refl-quartz 재현을 그대로 가져왔다.

## 4. 코드 따라가기

> 읽는 순서: 단위·파라미터 → 재료·구조 → source → Simulation·경계 → monitor → 실행·종료 → 후처리.
> 1D(Fresnel)와 2D(원기둥)가 같은 절차를 두 번 밟는다. 아래는 2D 기준이고, 1D는 §8 전체 코드에 있다.

### ① 단위와 파라미터 — 어떤 숫자를 고정하는가

```python
wl = 1.55
fcen = 1 / wl
fwidth = 0.12                 # narrow band: a nearly single-frequency field map at fcen
sx, sy = 14.0, 10.0
DPML = 1.0
RESOLUTION = 20
r_cyl, n_cyl = 0.75, 2.0
src_x = -0.5 * sx + DPML + 0.25
xm = 0.5 * sx - DPML - 0.9    # flux box: x = +-5.1
ym = 0.5 * sy - DPML - 0.2    # flux box: y = +-3.8
```

- **무엇**: 파장, 좁은 대역, 셀, 원기둥, source 위치, box 위치.
- **왜**: field map을 "fcen에서의 정상상태"로 보려면 대역이 좁아야 한다. box는 source 바깥쪽이면서 PML 안쪽에 있어야 한다. source가 box 안에 있으면 source가 넣는 power가 수지에 들어온다.
- **틀리면**: box를 PML 안으로 넣으면 흡수된 power를 재서 수지가 모자란다.

### ② 재료와 구조 — 무엇이 어디에 있는가

```python
cylinder = [mp.Cylinder(radius=r_cyl, height=mp.inf, center=mp.Vector3(), material=mp.Medium(index=n_cyl))]
# run 1 uses geometry = [], run 2 uses geometry = cylinder. Nothing else changes.
```

- **무엇**: 2D에서 무한히 긴 원기둥 하나. run 1에는 없고 run 2에만 있다.
- **왜**: 두 run의 차이는 물체 하나뿐이어야 한다. 그래야 field의 차가 물체의 산란장이다.
- **틀리면**: run 2에서 셀 크기나 해상도를 바꾸면 `load_minus_flux_data`가 배열 크기 불일치로 실패하거나, 실패하지 않더라도 엉뚱한 field를 뺀다.

### ③ Source — 빛을 어떻게 넣는가

```python
def plane_wave(fw):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=True), component=mp.Ez,
                      center=mp.Vector3(src_x, 0), size=mp.Vector3(0, sy))]
```

- **무엇**: 셀 전체 높이의 선원. 01편의 짧은 선원과 달리 PML 안까지 뻗는다.
- **왜**: 선이 PML 안에서 끝나야 가장자리 회절 없는 평면파가 된다. `is_integrated=True`는 PML 안에 놓인 source를 올바르게 다루는 옵션이다.
- **틀리면**: 높이를 PML 안쪽까지만 잡으면 01편처럼 양 끝에서 둥근 파면이 생겨 "평면파"가 아니게 된다. `is_integrated`를 빼면 PML 안의 source 부분이 잘못 감쇠된다.

### ④ Simulation과 경계 — 계산 상자와 PML

```python
def build(geometry, resolution=RESOLUTION, fw=fwidth):
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy), boundary_layers=[mp.PML(DPML)], geometry=geometry,
                        sources=plane_wave(fw), resolution=resolution)
    total = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}   # total field
    scat = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}    # will get E_inc subtracted
    return sim, total, scat
```

- **무엇**: PML 1 µm, 같은 source, 구조만 다른 `Simulation`. 면마다 monitor를 두 개 만든다.
- **왜**: 한 monitor는 total field의 flux, 다른 하나는 뒤에서 입사장을 빼 산란장의 flux를 잰다. 둘을 같은 run에서 같이 재야 두 수지를 직접 비교할 수 있다.
- **틀리면**: monitor를 하나만 두고 `load_minus_flux_data`를 걸면 total flux(T 계산에 필요)를 잃는다.

### ⑤ Monitor — 무엇을 재는가

```python
REGIONS = {
    "left":   lambda: mp.FluxRegion(center=mp.Vector3(-xm, 0), size=mp.Vector3(0, 2 * ym)),
    "right":  lambda: mp.FluxRegion(center=mp.Vector3(+xm, 0), size=mp.Vector3(0, 2 * ym)),
    "top":    lambda: mp.FluxRegion(center=mp.Vector3(0, +ym), size=mp.Vector3(2 * xm, 0)),
    "bottom": lambda: mp.FluxRegion(center=mp.Vector3(0, -ym), size=mp.Vector3(2 * xm, 0), weight=-1),
}
# run 1: save the incident fields on every side; run 2: subtract them on the `scat` monitors
inc_data = {k: sim.get_flux_data(m) for k, m in scat.items()}
...
for k, m in scat.items():
    sim.load_minus_flux_data(m, inc_data[k])
```

- **무엇**: 닫힌 box의 네 면. 아래 면은 `weight=-1`로 바깥(−y) 방향을 양수로 만든다. 왼쪽 면은 코드에서 부호를 뒤집는다(바깥이 −x).
- **왜**: 수지를 닫으려면 네 면이 빈틈없이 만나야 하고, 모든 flux가 "밖으로 나가는 양"이어야 한다. `get_flux_data`는 DFT field 자체를 저장하고 `load_minus_flux_data`는 그 field를 빼므로, 그 monitor의 flux는 (E_tot − E_inc)의 flux, 즉 산란장만의 power다.
- **틀리면**: `load_minus_flux_data`를 건 monitor의 값을 "total − incident"로 읽으면 위·아래 면에서 간섭항만큼 틀린다. 처음 실행에서 그렇게 읽어 R + T + S = 0.955가 나왔다.

> **함정**: `flux(E_tot − E_inc) ≠ flux(E_tot) − flux(E_inc)`. 같아지는 것은 두 파가 정반대 방향으로 지나가 간섭항이 상쇄되는 면뿐이다.

### ⑥ 실행과 종료 조건 — 언제 멈추는가

```python
def run_decay(sim):
    sim.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, right_center, 1e-5))
```

- **무엇**: 두 run 모두 오른쪽 면 중앙의 Ez가 최대의 10⁻⁵로 줄 때까지.
- **왜**: 원기둥은 빛을 잠시 가둔다(공명). 가둔 에너지가 다 빠져나가기 전에 멈추면 수지가 모자란다.
- **틀리면**: 고정 시각으로 끊으면 긴 펄스(t0 = 41.7)의 꼬리와 공명 누설을 놓친다. 이 글의 기준 run은 t ≈ 150에서 멈췄다.

### ⑦ 후처리 — 숫자로 바꾸기

```python
R = -(tot["left"] - inc_side["left"]) / inc                 # total-field flux difference, -x outward
T = tot["right"] / inc
S = ((tot["top"] - inc_side["top"]) + (tot["bottom"] - inc_side["bottom"])) / inc
conservation = sum(outward(tot).values()) / inc             # must be 0 for a lossless object

sc_out = outward(sc)                                        # scattered field only
P_sc = sum(sc_out.values())
sigma = P_sc / (inc / (2 * ym))                             # cross section = scattered power / incident intensity
Q_sca = sigma / (2 * r_cyl)
```

- **무엇**: total field의 flux 차로 R, T, S를 만들고(합 1), 산란장 flux의 합으로 산란 단면적을 만든다.
- **왜**: 수지는 total field의 보존에서 나온다. 산란 단면적은 정의가 "산란된 power / 입사 세기"라 산란장만의 flux가 필요하다. 둘은 다른 질문에 답하는 다른 수다.
- **틀리면**: `outward`에서 왼쪽 면 부호를 안 뒤집으면 P_sc에 왼쪽 산란이 음수로 들어가 σ가 작아진다. 입사 세기를 box 폭으로 안 나누면 σ의 단위가 틀린다.

## 5. 결과

### 1D: 절차가 해석해를 재현하는가

![fresnel]({{ site.baseurl }}/assets/meep/03/02_fresnel.png)
*왼쪽: 1D 셀. z < 0 공기, z > 0 석영이 PML까지, 빨강 = source, 파랑 = 반사·투과 monitor. 오른쪽: Meep의 R(λ)(점)과 Fresnel 공식(선). n(λ)은 같은 materials library에서 가져왔다.*

| 물리량 | Meep | 해석해 |
|---|---|---|
| R @ 533 nm | 0.03513 | 0.03505 |
| max \|R − R_Fresnel\| (400–800 nm) | 1.6 × 10⁻⁴ | — |
| R + T @ 533 nm | 1.00000 | 1 |

### 2D: 원기둥의 세 field와 수지

![fields]({{ site.baseurl }}/assets/meep/03/03_fields.png)
*1550 nm에서의 Re(Ez), 색 범위 공통, 점선 = 원기둥. 왼쪽 incident는 평면파, 가운데 total은 원기둥 앞쪽에 반사 간섭 무늬와 뒤쪽에 그림자·집속이 섞여 있고, 오른쪽 scattered는 둘의 차다. 산란장은 앞쪽(+x)으로 강하게 치우쳐 있고 원기둥 안에는 정상파가 선다.*

![animation]({{ site.baseurl }}/assets/meep/03/05_anim_scatter.gif)
*같은 세 가지를 시간으로. 짧은 펄스(fwidth 0.3 fcen)가 왼쪽에서 들어와 원기둥을 지난다. 세 번째 패널은 프레임마다 total에서 incident를 뺀 것이다. 입사 펄스가 원기둥에 닿는 순간부터 산란장이 생기고, 펄스가 지나간 뒤에도 원기둥 안에 갇힌 빛이 천천히 새어 나온다.*

![budget]({{ site.baseurl }}/assets/meep/03/04_budget.png)
*네 면의 power. 파랑 = total field의 flux에서 reference run의 flux를 뺀 것(R, T, S), 주황 = 입사장을 뺀 산란장의 flux. 파랑의 합은 1로 닫히고, 주황의 합은 산란된 power다.*

| 양 | total field 차 | 산란장 flux |
|---|---|---|
| 왼쪽 (R / 후방 산란) | 0.0823 | 0.0857 |
| 오른쪽 (T / 전방 산란) | 0.6736 | 0.2153 |
| 위 + 아래 (S / 옆 산란) | 0.2430 | 0.1954 |
| 합 | 0.9988 | 0.4963 = P_sc / P_inc |

| 산란 단면적 | 값 |
|---|---|
| σ_sc | 3.77 µm |
| Q_sca = σ / 2r (Meep, res 20) | 2.515 |
| Q_sca (2D Mie, E ∥ 축, x = 3.04, m = 2) | 2.513 |

### 예측과 비교

| 물리량 | 내 예측 (§2) | 시뮬레이션 | 판정 |
|--------|-------------|-----------|------|
| 1D R @ 533 nm | 3.5% | 3.513% (Fresnel 3.505%) | ✅ |
| 1D R + T | 1.000 | 1.00000 | ✅ |
| R + T + S | 1 (0.5% 안) | 0.9988 | ✅ |
| P_sc/P_inc < R + T + S | 작음 | 0.496 < 0.999 | ✅ |
| Q_sca | 2 근처 | 2.515 (Mie 2.513) | ✅ |
| 산란장 모양 | 전방 우세 + 내부 정상파 | 그림 확인 | ✅ |

예측은 맞았지만 과정에서 하나 틀렸다. 처음에는 `load_minus_flux_data`를 건 monitor의 값을 위·아래 면에서 "total − incident"로 읽어 S = 0.195, 합 0.955가 나왔다. 빠진 4.5%는 입사파와 산란파의 간섭항이다. 왼쪽 면에서는 두 값(0.0823과 0.0857)이 가깝다. 입사파와 반사파가 정반대 방향이라 간섭항이 거의 상쇄되기 때문이고, 그래서 04·05편의 R 측정은 이 방법으로 충분하다.

### 수렴성

| resolution | R | T | S | R + T + S | Q_sca |
|---|---|---|---|---|---|
| 20 | 0.0823 | 0.6736 | 0.2430 | 0.9988 | 2.515 |
| 40 | 0.0861 | 0.6626 | 0.2510 | 0.9997 | 2.628 |

수지는 두 해상도 모두 1로 닫힌다. R·T·S 각각은 1~5% 움직이고, Q_sca는 2.515에서 2.628로 4.5% 올라가 Mie 값에서 멀어진다. 해상도 20의 0.1% 일치는 우연에 가깝다.

### 주장할 수 있는 것 / 없는 것

- 할 수 있는 것: reference run + `load_minus_flux_data` 절차는 해석해(Fresnel)를 10⁻⁴ 수준으로 재현한다. 손실 없는 원기둥의 total field 수지는 닫힌 box에서 1로 닫힌다. 산란 단면적은 2D Mie와 5% 안에서 맞는다.
- 할 수 없는 것: Q_sca의 소수점 둘째 자리. 해상도에 따라 4.5% 움직이고, 유한 폭 평면파와 원기둥에서 3 µm 떨어진 box의 영향도 분리하지 못했다. 3D 구의 Mie 산란(공식 cylinder_cross_section 예제는 원통 좌표계의 3D 문제다).

## 6. 흔한 실수

| 증상 | 원인 | 고치는 법 |
|------|------|----------|
| R + T + S가 1보다 작음 (lossless인데) | 산란장 monitor 값을 "total − incident"로 읽음 | 수지는 total flux의 차로, 산란 power는 산란장 monitor로 |
| R이 음수 | 왼쪽 면의 바깥 법선(−x)을 안 뒤집음 | `R = -(…)/inc` |
| 네 면 합이 0 근처 | 아래 면 `weight=-1` 누락 | 바깥 방향 weight |
| `load_minus_flux_data` 오류 | 두 run의 셀·해상도·monitor 위치 불일치 | 같은 `build` 함수로 두 run 생성 |
| 평면파 양 끝에서 둥근 파면 | 선원이 PML 안으로 안 뻗음 | `size=(0, sy)`, `is_integrated=True` |
| 수지가 해상도마다 크게 다름 | 공명 에너지가 빠지기 전에 종료 | decay 감시점·임계값 확인 |

## 7. 직접 해보기

| 바꿀 것 | 예상 변화 | 확인할 수치 |
|---------|----------|------------|
| `n_cyl` 2.0 → 3.5 (Si) | 공명이 날카로워져 Q_sca가 파장에 민감 | Q_sca, 내부 정상파 |
| `r_cyl` 0.75 → 0.25 µm (x ≈ 1) | 전방 우세가 약해지고 산란장이 등방에 가까워짐 | sc_parts 네 값 |
| box를 원기둥에 바싹 (xm, ym 절반) | 근접장이 섞여 P_sc 변화? | Q_sca 비교 |
| `fwidth` 0.12 → 0.3 fcen + nfreq 11 | Q_sca(λ) 스펙트럼. Mie 공명 위치 | `mie_q_sca_2d_tm`를 파장별로 |

## 8. 전체 코드

<details>
<summary>reference_subtraction.py (클릭해서 펼치기)</summary>
{% highlight python %}
"""Meep Example 03 - Reference run subtraction: incident, total, scattered field and R, T, S.

Two runs of the same cell, with and without the object. What differs is the object's doing.
  A. 1D air | fused quartz: the procedure (normalization run + load_minus_flux_data) against the
     Fresnel formula R = ((1-n)/(1+n))^2 with the dispersive n(lambda) of the materials library.
     (official example refl-quartz.py)
  B. 2D dielectric cylinder (r = 0.75 um, n = 2) in a plane wave: E_scat = E_total - E_inc,
     and a closed flux box: R (left, incident subtracted), T (right), S (top + bottom, sideways
     scattering). For a lossless object R + T + S = 1.
  C. GIF: incident, total and scattered field side by side in time.

Run:  python reference_subtraction.py        (~2.5 min on one core)
Out:  00_source.png, 01_layout.png, 02_fresnel.png, 03_fields.png, 04_budget.png,
      05_anim_scatter.gif, result.json   (-> ../assets/03/)
"""
import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import meep as mp
from meep.materials import fused_quartz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import (Label, animate_compare, annotated_layout, bar_figure, panel_grid,   # noqa: E402
                     record_frames, source_figure)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "03")
os.makedirs(OUT, exist_ok=True)
t_all = time.time()

# ================================================================ A. 1D air | quartz vs Fresnel
# ---------------------------------------------------------------- (1) parameters (1D, units of um)
sz = 10.0
dpml1 = 1.0
wl_min, wl_max = 0.4, 0.8
fmin, fmax = 1 / wl_max, 1 / wl_min
fcen1, df1, nfreq1 = 0.5 * (fmin + fmax), fmax - fmin, 25
RES1 = 200                    # 1D is cheap: lambda_min / n = 0.27 um -> 54 px


def sim_1d(geometry):
    # ------------------------------------------------------------ (3) source: a plane wave in 1D is a point
    src = [mp.Source(mp.GaussianSource(fcen1, fwidth=df1), component=mp.Ex, center=mp.Vector3(0, 0, -0.5 * sz + dpml1))]
    # ------------------------------------------------------------ (4) simulation
    sim = mp.Simulation(cell_size=mp.Vector3(0, 0, sz), boundary_layers=[mp.PML(dpml1)], sources=src,
                        geometry=geometry, dimensions=1, resolution=RES1)
    # ------------------------------------------------------------ (5) monitors: reflection (air side), transmission (inside quartz)
    refl = sim.add_flux(fcen1, df1, nfreq1, mp.FluxRegion(center=mp.Vector3(0, 0, -0.25 * sz)))
    tran = sim.add_flux(fcen1, df1, nfreq1, mp.FluxRegion(center=mp.Vector3(0, 0, +0.25 * sz)))
    return sim, refl, tran


# run 1: empty (air everywhere) -> incident flux and the incident flux DATA at the reflection plane
sim, refl, tran = sim_1d([])
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ex, mp.Vector3(0, 0, 0.25 * sz), 1e-9))   # (6)
inc_flux = np.array(mp.get_fluxes(refl))
refl_data = sim.get_flux_data(refl)
freqs1 = np.array(mp.get_flux_freqs(refl))
# run 2: quartz half-space from z = 0 through the PML
quartz = [mp.Block(size=mp.Vector3(mp.inf, mp.inf, 0.5 * sz), center=mp.Vector3(0, 0, 0.25 * sz), material=fused_quartz)]
sim, refl, tran = sim_1d(quartz)
sim.load_minus_flux_data(refl, refl_data)                              # incident part removed -> reflection only
sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ex, mp.Vector3(0, 0, 0.25 * sz), 1e-9))
# ---------------------------------------------------------------- (7) R, T and the Fresnel formula
R1 = -np.array(mp.get_fluxes(refl)) / inc_flux                        # backward flux is negative
T1 = np.array(mp.get_fluxes(tran)) / inc_flux
n_q = np.array([np.sqrt(np.real(fused_quartz.epsilon(f)[0][0])) for f in freqs1])   # n(lambda) from the material model
R_fresnel = ((1 - n_q) / (1 + n_q)) ** 2
wl1 = 1 / freqs1
ic1 = nfreq1 // 2
print(f"A. Fresnel: max|R_meep - R_fresnel| = {np.max(np.abs(R1 - R_fresnel)):.2e}; "
      f"R @ {wl1[ic1]:.3f} um: meep {R1[ic1]:.5f}, Fresnel {R_fresnel[ic1]:.5f}; R+T = {R1[ic1] + T1[ic1]:.5f}; "
      f"n = {n_q[0]:.4f} ({wl1[0]:.2f} um) .. {n_q[-1]:.4f} ({wl1[-1]:.2f} um)")

fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
z = np.linspace(-sz / 2, sz / 2, 400)
eps_z = np.where(z > 0, n_q[ic1] ** 2, 1.0)
ax[0].plot(z, eps_z, color="k")
ax[0].axvline(-0.5 * sz + dpml1, color="red", lw=2, label="source")
ax[0].axvline(-0.25 * sz, color="blue", lw=2, label="reflection monitor")
ax[0].axvline(+0.25 * sz, color="blue", lw=2, ls="--", label="transmission monitor")
for zz in (-sz / 2 + dpml1, sz / 2 - dpml1):
    ax[0].axvspan(zz if zz > 0 else -sz / 2, sz / 2 if zz > 0 else zz, color="green", alpha=0.12)
ax[0].set_xlabel("z [um]"); ax[0].set_ylabel("epsilon"); ax[0].set_title("1D cell: air | fused quartz (green = PML)", fontsize=9)
ax[0].legend(fontsize=7, loc="center left")
ax[1].plot(wl1 * 1000, R_fresnel * 100, "k-", label="Fresnel  ((1-n)/(1+n))^2 with n(lambda) of fused_quartz")
ax[1].plot(wl1 * 1000, R1 * 100, "o", ms=4, color="tab:blue", label="Meep: reference run + load_minus_flux_data")
ax[1].set_xlabel("wavelength [nm]"); ax[1].set_ylabel("reflectance R [%]"); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=7)
ax[1].set_title(f"max |R_meep - R_Fresnel| = {np.max(np.abs(R1 - R_fresnel)):.1e}", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "02_fresnel.png"), dpi=150); plt.close(fig)

# ================================================================ B. 2D cylinder: fields and the power budget
# ---------------------------------------------------------------- (1) parameters
wl = 1.55
fcen = 1 / wl
fwidth = 0.12                 # narrow band: a nearly single-frequency field map at fcen
sx, sy = 14.0, 10.0
DPML = 1.0
RESOLUTION = 20
r_cyl, n_cyl = 0.75, 2.0
src_x = -0.5 * sx + DPML + 0.25
xm = 0.5 * sx - DPML - 0.9    # flux box: x = +-5.1
ym = 0.5 * sy - DPML - 0.2    # flux box: y = +-3.8
right_center = mp.Vector3(xm, 0)

# ---------------------------------------------------------------- (2) geometry: the object of run 2
cylinder = [mp.Cylinder(radius=r_cyl, height=mp.inf, center=mp.Vector3(), material=mp.Medium(index=n_cyl))]


# ---------------------------------------------------------------- (3) source: a line across the whole cell -> plane wave along +x
def plane_wave(fw):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fw, is_integrated=True), component=mp.Ez,
                      center=mp.Vector3(src_x, 0), size=mp.Vector3(0, sy))]


# ---------------------------------------------------------------- (4) simulation + (5) the closed flux box
REGIONS = {
    "left":   lambda: mp.FluxRegion(center=mp.Vector3(-xm, 0), size=mp.Vector3(0, 2 * ym)),
    "right":  lambda: mp.FluxRegion(center=mp.Vector3(+xm, 0), size=mp.Vector3(0, 2 * ym)),
    "top":    lambda: mp.FluxRegion(center=mp.Vector3(0, +ym), size=mp.Vector3(2 * xm, 0)),
    "bottom": lambda: mp.FluxRegion(center=mp.Vector3(0, -ym), size=mp.Vector3(2 * xm, 0), weight=-1),
}


def build(geometry, resolution=RESOLUTION, fw=fwidth):
    """Simulation plus TWO flux monitors per side of the box: one for the total field, and one that
    will have the incident field subtracted (load_minus_flux_data) so it measures the scattered field only."""
    sim = mp.Simulation(cell_size=mp.Vector3(sx, sy), boundary_layers=[mp.PML(DPML)], geometry=geometry,
                        sources=plane_wave(fw), resolution=resolution)
    total = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}
    scat = {k: sim.add_flux(fcen, 0, 1, reg()) for k, reg in REGIONS.items()}
    return sim, total, scat


def run_decay(sim):                                                  # (6)
    sim.run(until_after_sources=mp.stop_when_fields_decayed(30, mp.Ez, right_center, 1e-5))


def outward(fluxes):
    """Outward power through the box: the left side's outward normal is -x."""
    return {"left": -fluxes["left"], "right": fluxes["right"], "top": fluxes["top"], "bottom": fluxes["bottom"]}


nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * DPML, sy - 2 * DPML))
extent = [-(sx / 2 - DPML), sx / 2 - DPML, -(sy / 2 - DPML), sy / 2 - DPML]


def budget(resolution=RESOLUTION, fields=False, layout=False):
    """Run 1 (empty) then run 2 (cylinder). Returns the total-field budget R, T, S (sums to 1),
    the scattered-field power and cross section, and optionally the DFT field maps."""
    sim, total, scat = build([], resolution)
    if fields:
        dft_ref = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)
    run_decay(sim)
    inc_side = {k: float(mp.get_fluxes(m)[0]) for k, m in total.items()}   # incident flux through each side (+x / +y)
    inc = inc_side["right"]                                                # incident power through the box width
    inc_data = {k: sim.get_flux_data(m) for k, m in scat.items()}
    ez_inc = sim.get_dft_array(dft_ref, mp.Ez, 0) if fields else None

    sim, total, scat = build(cylinder, resolution)
    for k, m in scat.items():
        sim.load_minus_flux_data(m, inc_data[k])                           # these now see E_total - E_inc only
    if layout:
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=DPML, figsize=(8.2, 6.0),
            title="run 2 (device): plane-wave line source, dielectric cylinder, closed flux box, PML",
            params_text=f"wl={wl} um  fwidth={fwidth}  res={resolution}/um\ncell={sx:g}x{sy:g}  dpml={DPML:g}  r={r_cyl}  n={n_cyl}",
            params_xy=(-5.8, 4.6), pml_xy=(2.0, -4.5), decay_point=(xm, 0), decay_text_xy=(1.6, -1.2),
            labels=[Label("cylinder r = 0.75 um, n = 2 (geometry)", (r_cyl, 0.3), (-4.0, 2.4), step=2, color="black"),
                    Label("line source across the cell (plane wave)", (src_x, 2.0), (-4.5, 3.4), step=3, color="red"),
                    Label("flux box: 4 sides x (total, incident-subtracted)", (xm, -2.5), (-1.5, -3.2), step=5, color="blue")])
    if fields:
        dft_dev = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)
    run_decay(sim)
    # ------------------------------------------------------------ (7) budgets
    tot = {k: float(mp.get_fluxes(m)[0]) for k, m in total.items()}
    sc = {k: float(mp.get_fluxes(m)[0]) for k, m in scat.items()}
    # total-field budget: flux DIFFERENCES to the empty run (exact by energy conservation)
    R = -(tot["left"] - inc_side["left"]) / inc                            # backward: -x is outward on the left
    T = tot["right"] / inc                                                 # what a detector behind the cylinder sees
    S = ((tot["top"] - inc_side["top"]) + (tot["bottom"] - inc_side["bottom"])) / inc   # sideways, both signs outward
    conservation = sum(outward(tot).values()) / inc                        # total field: must be 0 (lossless)
    # scattered-field budget: fluxes of (E_total - E_inc) through the four sides
    sc_out = outward(sc)
    P_sc = sum(sc_out.values())
    R_sub = sc_out["left"] / inc                                           # = R: counter-propagating waves have no cross term
    I_inc = inc / (2 * ym)                                                 # incident power per unit width
    sigma = P_sc / I_inc                                                   # 2D scattering cross section [um]
    out = {"R": R, "T": T, "S": S, "sum": R + T + S, "conservation": conservation, "R_sub": R_sub,
           "P_sc_over_inc": P_sc / inc, "sc_parts": {k: v / inc for k, v in sc_out.items()},
           "sigma_um": sigma, "Q_sca": sigma / (2 * r_cyl), "inc_flux": inc}
    if fields:
        ez_tot = sim.get_dft_array(dft_dev, mp.Ez, 0)
        out["fields"] = (ez_inc, ez_tot, ez_tot - ez_inc)
    return out


def mie_q_sca_2d_tm(m, x, nmax=30):
    """Scattering efficiency of an infinite dielectric cylinder, E parallel to the axis (Ez), normal
    incidence. From continuity of Ez and dEz/dr at r = a: b_n = [m Jn'(mx) Jn(x) - Jn(mx) Jn'(x)] /
    [Jn(mx) Hn'(x) - m Jn'(mx) Hn(x)],  Q_sca = (2/x) sum_n |b_n|^2 over n = -inf..inf."""
    from scipy.special import jv, jvp, hankel1, h1vp
    q = 0.0
    for n in range(-nmax, nmax + 1):
        b = (m * jvp(n, m * x) * jv(n, x) - jv(n, m * x) * jvp(n, x)) / (jv(n, m * x) * h1vp(n, x) - m * jvp(n, m * x) * hankel1(n, x))
        q += abs(b) ** 2
    return 2 * q / x


source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")
base = budget(fields=True, layout=True)
x_size = 2 * np.pi * r_cyl / wl
try:
    Q_mie = mie_q_sca_2d_tm(n_cyl, x_size)
except Exception as exc:                                                  # scipy missing: report, do not fake
    Q_mie = None
    print("Mie comparison skipped:", exc)
print(f"B. total-field budget: R = {base['R']:.4f}, T = {base['T']:.4f}, S = {base['S']:.4f}, R+T+S = {base['sum']:.4f} "
      f"(conservation residual {base['conservation']:+.4f}); R from subtracted field = {base['R_sub']:.4f}")
print(f"B. scattered field: P_sc/inc = {base['P_sc_over_inc']:.4f} " + " ".join(f"{k}={v:.4f}" for k, v in base['sc_parts'].items())
      + f"; sigma = {base['sigma_um']:.3f} um, Q_sca = {base['Q_sca']:.3f}" + (f" (2D Mie, x = {x_size:.2f}: {Q_mie:.3f})" if Q_mie else ""))
ez_inc, ez_tot, ez_sc = base["fields"]
circ = {i: (0, 0, r_cyl, "") for i in range(3)}
panel_grid([ez_inc, ez_tot, ez_sc], ["incident (run 1, no object)", "total (run 2, with cylinder)", "scattered = total - incident"],
           extent, os.path.join(OUT, "03_fields.png"), ncols=3, circles=circ, figsize=(14, 3.9),
           suptitle=f"Re(Ez) at 1550 nm, one color scale; dashed circle = cylinder")
bar_figure(["R (reflected)", "T (transmitted)", "S (sideways)", "R + T + S"],
           {"total field, minus the empty run": [base["R"], base["T"], base["S"], base["sum"]],
            "scattered field only (E_tot - E_inc)": [base["sc_parts"]["left"], base["sc_parts"]["right"],
                                                     base["sc_parts"]["top"] + base["sc_parts"]["bottom"], base["P_sc_over_inc"]]},
           os.path.join(OUT, "04_budget.png"), ylabel="fraction of incident power", reference=1.0, reference_label="lossless: 1")

keys = ("R", "T", "S", "sum", "Q_sca")
convergence = [{"resolution": RESOLUTION, **{k: base[k] for k in keys}}]
for res in (40,):
    b = budget(resolution=res)
    convergence.append({"resolution": res, **{k: b[k] for k in keys}})
    print(f"convergence res={res}: R={b['R']:.4f} T={b['T']:.4f} S={b['S']:.4f} sum={b['sum']:.4f} Q_sca={b['Q_sca']:.3f}")

# ================================================================ C. GIF: incident / total / scattered in time
fw_anim = 0.3 * fcen
w_anim = 1 / fw_anim
t_src = 5 / fw_anim
sets = []
for geom in ([], cylinder):
    s_anim = mp.Simulation(cell_size=mp.Vector3(sx, sy), boundary_layers=[mp.PML(DPML)], geometry=geom,
                           sources=plane_wave(fw_anim), resolution=14)
    frames, times = record_frames(s_anim, nonpml, mp.Ez, t_start=t_src - 2 * w_anim, t_end=t_src + sx + 6, n_frames=60)
    sets.append(frames)
sets.append([t - i for t, i in zip(sets[1], sets[0])])                  # scattered = total - incident, frame by frame
animate_compare(sets, ["incident (no object)", "total (cylinder)", "scattered = total - incident"], times, extent,
                os.path.join(OUT, "05_anim_scatter.gif"), figsize=(13, 3.9), suptitle="plane wave from the left")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"fresnel": {"wavelengths_um": wl1.tolist(), "R_meep": R1.tolist(), "R_fresnel": R_fresnel.tolist(),
                               "T_meep": T1.tolist(), "n_quartz": n_q.tolist(),
                               "max_abs_err": float(np.max(np.abs(R1 - R_fresnel))), "R_center": float(R1[ic1]),
                               "R_fresnel_center": float(R_fresnel[ic1]), "R_plus_T_center": float(R1[ic1] + T1[ic1])},
                   "cylinder": {k: base[k] for k in ("R", "T", "S", "sum", "conservation", "R_sub", "P_sc_over_inc", "sc_parts", "sigma_um", "Q_sca", "inc_flux")},
                   "mie": {"x": x_size, "Q_sca_tm": Q_mie},
                   "convergence": convergence, "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
{% endhighlight %}
</details>

§4의 발췌 코드와 달리 전체 코드에는 1D Fresnel 실험, 그림 저장·GIF 녹화·result.json 기록이 들어 있다. 그림 helper `blogfig.py`는 시리즈 공통이며 같은 폴더(`code/`)에 있다. 전체 코드와 helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**실행 결과 (2026-10-23 실행)**:
```
A. Fresnel: max|R_meep - R_fresnel| = 1.62e-04; R @ 0.533 um: meep 0.03513, Fresnel 0.03505; R+T = 1.00000; n = 1.4533 (0.80 um) .. 1.4701 (0.40 um)
B. total-field budget: R = 0.0823, T = 0.6736, S = 0.2430, R+T+S = 0.9988 (conservation residual -0.0018); R from subtracted field = 0.0857
B. scattered field: P_sc/inc = 0.4963 left=0.0857 right=0.2153 top=0.0977 bottom=0.0977; sigma = 3.772 um, Q_sca = 2.515 (2D Mie, x = 3.04: 2.513)
convergence res=40: R=0.0861 T=0.6626 S=0.2510 sum=0.9997 Q_sca=2.628
```

**재현 환경**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · 실행 `python reference_subtraction.py` (약 28 s, 단일 코어)

## 확인 질문

1. 왼쪽 면에서는 "total flux의 차"(0.0823)와 "산란장 flux"(0.0857)가 가깝고 위·아래 면에서는 다르다. 어느 쪽 면의 어떤 성질 때문인가?
2. 손실이 있는 원기둥(복소 굴절률)이면 R + T + S는 1보다 큰가, 작은가? 그 차이를 무엇이라 부르는가?
3. 04편 도파로의 R은 산란장 monitor(`load_minus_flux_data`) 하나로 쟀다. 그것이 정당한 이유를 이 글의 용어로 말해 보라.

## 9. 더 읽기

- [공식 예제 refl-quartz.py](https://github.com/NanoComp/meep/blob/master/python/examples/refl-quartz.py) (1D 정규화 run + Fresnel)
- [공식 예제 cylinder_cross_section.py](https://github.com/NanoComp/meep/blob/master/python/examples/cylinder_cross_section.py) (3D 원통 좌표계의 산란 단면적)
- [공식 튜토리얼: Transmittance / Reflectance 정규화](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend) · [`load_minus_flux_data` 레퍼런스](https://meep.readthedocs.io/en/latest/Python_User_Interface/#flux-spectra)
- 이전 글: [02 · 경계 조건과 PML]({{ site.baseurl }}/boundary-pml/) · 다음 글: [04 · Straight waveguide와 guided mode]({{ site.baseurl }}/straight-waveguide/)
