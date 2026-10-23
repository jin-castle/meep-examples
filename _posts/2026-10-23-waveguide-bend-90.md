---
layout: post
date: 2026-10-23
title: "Meep Example 05 · Bent waveguide와 radiation loss — sharp bend의 2-run flux 정규화"
title_en: "Meep Example 05 · Bent waveguide and radiation loss — two-run flux normalization on a sharp bend"
lang: ko
series: meep-examples
part: 5
level: beginner
runtime: "12 s (two runs, single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend"
tags: [meep, fdtd, waveguide, bend, flux, normalization]
image: /assets/meep/05/02_field.png
excerpt: "a dielectric waveguide (ε = 12, width 1) turns a sharp 90° corner. We measure how much power goes around the corner, how much comes back, and how much leaks out."
---
## TL;DR (English)

![hero]({{ site.baseurl }}/assets/meep/05/02_field.png)

- **What**: a dielectric waveguide (ε = 12, width 1) turns a sharp 90° corner. We measure how much power goes around the corner, how much comes back, and how much leaks out.
- **Result**: T = 0.20, R = 0.22, radiated = 0.58 at the center wavelength. Most of the light is lost at the corner.
- **Takeaway**: two-run flux normalization. A straight reference run gives the input power and the incident fields; subtracting them in the bend run leaves only the reflection. A sharp corner is not usable in a photonic circuit.
- **Code**: full script at the bottom, ~12 s on one core.

## 0. 이 글에서 배우는 것

- `add_flux`와 `FluxRegion`으로 단면을 지나는 power(flux) 재기
- 2-run 정규화: 직선 기준 run의 `get_flux_data` → bend run의 `load_minus_flux_data`로 입사 성분을 빼고 반사만 남기기
- 뒤로 가는 flux는 음수라는 것, 그리고 에너지 수지 T + R + L = 1로 결과를 검산하는 법
- 물리 교훈: 급격한 직각 꺾임은 빛의 절반 이상을 밖으로 버린다. 그래서 광회로는 곡선 굽힘을 쓴다

**전제 지식**: 04편의 도파로·모드 개념. **이전 글**: [04 · Straight waveguide와 guided mode]({{ site.baseurl }}/straight-waveguide/) · **다음 글**: 06 · Binary grating과 diffraction order

## 1. 무엇을 알고 싶은가

04편의 직선 도파로는 넣은 빛을 전부 내보냈다. 같은 도파로를 직각으로 꺾으면 얼마가 코너를 돌아 나가고(T), 얼마가 되돌아오고(R), 얼마가 밖으로 새는가(L). 이 예제를 고른 이유는 두 가지다. 답을 미리 알 수 없는 첫 문제이고, 투과율을 잴 때 기준 run을 먼저 돌려 나누는 Meep의 관례가 여기서 처음 나온다.

## 2. 물리 한 페이지

도파로를 따라가던 모드는 코너에서 갑자기 방향이 바뀐 도파로를 만난다. 입력 모드와 수직 암의 모드는 모양이 겹치는 부분이 작아서(mode mismatch), 겹치지 않는 부분만큼 밖으로 방사되거나 되돌아간다. 닫힌 해석해는 없고, 에너지 보존이 결과를 구속한다.

$$
T=\frac{P_{\mathrm{tran}}}{P_{\mathrm{in}}},\qquad
R=\frac{-P_{\mathrm{refl}}}{P_{\mathrm{in}}},\qquad
T+R+L_{\mathrm{rad}}=1
$$

| 기호 | 뜻 | 코드 변수 |
|------|----|-----------|
| $P_{\mathrm{in}}$ | 직선 기준 run에서 도파로를 지나간 power | `P_in` |
| $P_{\mathrm{tran}}$ | bend run에서 수직 암 단면을 지나는 power | `mp.get_fluxes(tran)` |
| $P_{\mathrm{refl}}$ | bend run의 반사 단면 flux. 입사 성분을 뺀 값이라 뒤로 가는 power만 남고 **음수** | `mp.get_fluxes(refl)` |
| $L_{\mathrm{rad}}$ | 코너에서 밖으로 새는 power. 직접 재지 않고 잔여로 추정 | `L = 1 - T - R` |

**가정과 유효 범위**: 2D, lossless 재료(잔여는 전부 방사), Ez 편광(면에 수직한 전기장), 공식 예제의 무차원 단위(길이 단위 a, ε = 12, 파장 6.67a). 그림에서는 a = 232.5 nm로 읽어 중심 파장을 1550 nm, 길이를 µm로 표시한다.

### 결과 보기 전에 맞춰보기

| 물리량 | 내 예측 | 근거 |
|--------|---------|------|
| T | 0.5 미만, 수십 % | 굴절률 대비가 크고(√12 ≈ 3.5) 코너가 급해 모드 겹침이 작다 |
| R | 수십 % | 코너 벽이 거울처럼 일부를 되돌린다 |
| L (방사) | 가장 큰 몫 | 코너에서 위상이 맞는 방향이 없어 대부분 밖으로 흩어진다 |
| 필드 모양 | 코너 주변 cladding으로 퍼지는 방사 lobe, 수직 암은 희미 | mode mismatch |
| T + R | 1 이하 | 에너지 보존 |

**판정 기준**: T + R > 1이면 정규화나 부호 오류. T > 0.9면 코너가 실제로 꺾이지 않은 것(구조 오류)을 의심.

## 3. 시뮬레이션 설계도

![layout]({{ site.baseurl }}/assets/meep/05/01_layout.png)
*검은 L자 = 수평 암 + 수직 암(`geometry`, 양 끝이 PML 관통), 빨간 선 = Ez line source(x = −6.5), 파란 세로선 = 반사 flux 단면(x = −5.5, source 하류), 파란 가로선 = 투과 flux 단면(y = +6.5, 수직 암 위), 녹색 빗금 = PML, 보라 × = bend run의 종료 조건이 감시하는 점(4, 6.5). 좌표는 코드의 a 단위이고 축 눈금은 a = 232.5 nm로 환산한 µm다(cell 16a = 3.72 µm). 동그라미 숫자는 §4의 코드 단계 번호다. ① 파라미터 박스, ② 구조, ③ source, ④ PML, ⑤ monitor, ⑥ 종료 감시점이고, ⑦ 후처리는 그릴 것이 없다. 기준 run(직선)은 같은 source·반사 단면에 수평 암만 쭉 이어진 구조다.*

| 파라미터 | 값 | 왜 이 값인가 | 바꾸면 |
|----------|-----|-------------|--------|
| `eps_wg`, `w` | 12, 1 | 공식 튜토리얼 값 (n ≈ 3.46) | ε 낮추면 confinement 약해져 L ↑ |
| `fcen`, `df` | 0.15, 0.1 | 파장 6.67a = 1550 nm (a = 232.5 nm). 대역 5–10a = 1160–2325 nm | 대역 가장자리는 source power가 작아 값이 튄다 |
| `resolution` | 25 | 공식 10 → 상향. 도파로 폭 25 px, 유도 파장 48 px | 10이면 코너 형상이 거칠어 수치 변동 |
| `dpml` | 1.0 | 파장의 1/6 이상. 양 암이 PML을 관통 | 얇으면 PML 반사가 R에 섞임 |
| `sx = sy` | 16 | 코너 주변 방사가 PML에 닿기 전 퍼질 여유 | 좁히면 방사가 monitor에 되돌아옴 |
| `src_x`, `refl_x` | −6.5, −5.5 | source는 PML 밖 0.5, 반사 단면은 source **하류** 1.0 | 반사 단면이 source 상류면 입사 성분 분리 실패 |
| `span` | w + 2 | core 양쪽 1a씩 evanescent tail 포함 | core 폭만 잡으면 P_in 과소 → T 과대 |

## 4. 코드 따라가기

> 읽는 순서는 04편과 같다: 단위·파라미터 → 재료·구조 → source → Simulation·경계 → monitor → 실행·종료 → 후처리.
> 이번에는 run이 두 번이라 ⑤·⑥이 기준 run과 bend run에 한 번씩 나온다.

### ① 단위와 파라미터 — 어떤 숫자를 고정하는가

```python
import numpy as np
import meep as mp

# Dimensionless units as in the official tutorial: 1 length unit = a (think 1 um).
eps_wg = 12.0            # waveguide permittivity (n = sqrt(12) = 3.46)
w = 1.0                  # waveguide width
fcen = 0.15              # center frequency -> wavelength 1/0.15 = 6.67 units
df = 0.1                 # source bandwidth
nfreq = 11               # number of frequencies in the flux monitors

resolution = 25          # pixels per unit -> width = 25 px, wavelength in the guide (1.92) = 48 px
dpml = 1.0               # PML thickness
sx = sy = 16.0           # square cell, PML included

ycen = -4.0              # y of the input (horizontal) arm
xcen = +4.0              # x of the output (vertical) arm  -> corner at (xcen, ycen)

src_x = -6.5             # source: 0.5 outside the left PML (PML edge at x = -7)
refl_x = -5.5            # reflection flux plane: downstream of the source
tran_straight_x = +6.5   # transmission plane for the straight reference run
tran_bend_y = +6.5       # transmission plane for the bend run (on the vertical arm)
span = mp.Vector3(0, w + 2)   # source / monitor line: core + 1 unit on each side (evanescent tail)
```

- **무엇**: 공식 튜토리얼의 무차원 설정(ε = 12, w = 1, f = 0.15)과 코너 위치, source·monitor 좌표를 고정한다.
- **왜**: 04편은 1 = 1 µm였지만 여기서는 길이 단위 a를 정하지 않는다. Maxwell 방정식은 scale-invariant라서 a = 1 µm로 읽으면 파장 6.67 µm, a = 0.23 µm로 읽으면 1.55 µm 결과가 그대로 된다. 이 글의 그림은 그 둘째 읽기(a = 232.5 nm)로 환산해 파장은 nm, 길이는 µm로 표시한다. 좌표는 모두 PML 경계(±7)를 기준으로 잡는다.
- **틀리면**: `refl_x`를 source보다 왼쪽(상류)에 두면 입사 펄스가 그 단면을 지나지 않아 `load_minus_flux_data`가 뺄 것이 없고 R이 엉뚱해진다.

> **함정**: `df = 0.1`은 대역 5–10a로 넓다. 가장자리 파장에서는 source power가 거의 없어 T·R이 튄다. 중심 근처만 믿는다(§5).

### ② 재료와 구조 — 무엇이 어디에 있는가

```python
def make_geometry(bend: bool):
    """Straight reference (bend=False) or the L-shaped bend (bend=True). Same width and material."""
    wg = mp.Medium(epsilon=eps_wg)
    if not bend:
        return [mp.Block(center=mp.Vector3(0, ycen), size=mp.Vector3(mp.inf, w), material=wg)]
    horizontal = mp.Block(center=mp.Vector3(0.5 * (-sx / 2 + xcen + w / 2), ycen),
                          size=mp.Vector3(sx / 2 + xcen + w / 2, w), material=wg)   # left PML -> corner
    vertical = mp.Block(center=mp.Vector3(xcen, 0.5 * (ycen - w / 2 + sy / 2)),
                        size=mp.Vector3(w, sy / 2 - ycen + w / 2), material=wg)     # corner -> top PML
    return [horizontal, vertical]
```

- **무엇**: 같은 함수가 플래그 하나로 직선 기준 구조와 L자 bend 구조를 만든다. 두 `Block`은 코너에서 폭 w만큼 겹쳐 빈틈 없는 직각을 이룬다.
- **왜**: 기준 run과 bend run은 구조만 다르고 나머지는 같아야 정규화가 성립한다. 함수로 묶으면 재료·폭·좌표가 어긋날 여지가 없다. 수평 암은 왼쪽 PML을, 수직 암은 위쪽 PML을 관통해야 끝면 반사가 없다.
- **틀리면**: 수평 암을 코너에서 `xcen - w/2`까지만 그리면 코너에 빈 사각형이 생겨 R이 커진다. 수직 암이 cell 안에서 끝나면 끝면 반사가 T에 섞인다.

### ③ Source — 빛을 어떻게 넣는가

```python
# A plain Ez line source (not an eigenmode source), as in the official tutorial.
sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ez,
                     center=mp.Vector3(src_x, ycen), size=span)]
```

- **무엇**: 수평 암을 가로지르는 길이 3a의 세로선에서 Ez 성분 가우시안 펄스를 쏜다.
- **왜**: 04편의 `EigenModeSource`와 달리 모드 모양을 맞추지 않은 단순 선 source다. 모드가 아닌 성분도 섞여 들어가지만, 기준 run이 실제로 도파로를 따라간 power를 재므로 그 몫은 P_in에서 빠진다. 2-run 정규화가 필요한 이유 중 하나다.
- **틀리면**: `component`를 `Ey`로 바꾸면 2D에서 면내 편광이 되어 다른 모드(다른 confinement)를 보게 된다. `size`를 core 폭만큼만 잡아도 돌아가지만 모드 결합이 나빠져 방사 잡음이 늘어난다.

### ④ Simulation과 경계 — 계산 상자와 PML

```python
def make_sim(bend: bool):
    return mp.Simulation(cell_size=mp.Vector3(sx, sy), resolution=resolution,
                         boundary_layers=[mp.PML(dpml)],
                         geometry=make_geometry(bend), sources=sources)
```

- **무엇**: 16 × 16 상자, 네 변 PML 1a, 같은 source·해상도로 구조만 바꿔 `Simulation`을 만드는 함수.
- **왜**: Meep의 `Simulation` 객체는 run이 끝나면 필드가 남아 있어 재사용하기 어렵다. 매 run마다 새로 만드는 것이 가장 안전하고, 함수로 묶으면 두 run의 설정 일치가 보장된다.
- **틀리면**: 두 run에서 `resolution`이나 `cell_size`가 다르면 격자 위치가 달라져 `load_minus_flux_data`가 크기가 다른 배열을 빼려다 오류를 낸다.

### ⑤ Monitor — 무엇을 재는가 (기준 run)

```python
sim = make_sim(bend=False)
refl  = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(refl_x, ycen), size=span))
tran0 = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(tran_straight_x, ycen), size=span))
```

- **무엇**: 직선 구조에 반사 단면(x = −5.5)과 투과 단면(x = +6.5)을 둔다. `add_flux`는 그 선을 지나는 Poynting flux를 주파수별로 누적한다.
- **왜**: 직선은 반사가 없으므로 투과 단면 flux가 곧 source가 도파로에 넣은 power P_in이다. 반사 단면은 이 run에서는 입사 펄스를 기록하는 용도다.
- **틀리면**: 투과 단면을 PML 안에 두면 이미 흡수된 값을 재서 P_in이 작아지고 T가 과대평가된다.

### ⑥ 실행과 종료 조건 (기준 run)

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(tran_straight_x, ycen), 1e-6))

P_in = np.array(mp.get_fluxes(tran0))     # what actually travels down the guide = input power
refl_data = sim.get_flux_data(refl)       # incident fields at the reflection plane (to subtract later)
freqs = np.array(mp.get_flux_freqs(tran0))
```

- **무엇**: 투과 단면 근처의 Ez가 최대값의 10⁻⁶으로 줄 때까지 돌리고, P_in과 반사 단면의 DFT 필드 데이터를 꺼내 둔다.
- **왜**: `get_fluxes`는 숫자(power)지만 `get_flux_data`는 필드 자체다. 다음 run에서 필드 수준에서 빼야 간섭항까지 정확히 제거된다. power끼리 빼면 틀린다.
- **틀리면**: 종료가 이르면 펄스 꼬리가 단면을 다 지나지 못해 P_in이 작아지고, 다음 run의 입사 데이터도 불완전해 R에 잔여 입사 성분이 남는다.

### ⑤′ Monitor — 무엇을 재는가 (bend run)

```python
sim = make_sim(bend=True)
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(refl_x, ycen), size=span))
sim.load_minus_flux_data(refl, refl_data)  # subtract the incident part -> this monitor now sees reflection only
tran = sim.add_flux(fcen, df, nfreq,
                    mp.FluxRegion(center=mp.Vector3(xcen, tran_bend_y), size=mp.Vector3(w + 2, 0)))
```

- **무엇**: bend 구조에 같은 위치의 반사 단면을 만들고, 기준 run의 입사 데이터를 음수로 미리 채운다. 투과 단면은 수직 암 위(y = +6.5)의 가로선이다.
- **왜**: 반사 단면에는 입사 펄스(오른쪽으로)와 반사 펄스(왼쪽으로)가 모두 지나간다. 입사 성분을 미리 빼 두면 run이 끝났을 때 반사 성분만 남는다.
- **틀리면**: 이 줄을 빼먹으면 반사 단면이 입사까지 세어 flux가 큰 양수가 되고 T + R이 1을 넘는다.

> **함정**: 투과 단면의 `size`가 `(w + 2, 0)`, 즉 가로선이다. 수직 암에서는 빛이 +y로 가므로 단면은 x 방향으로 펼쳐야 한다. `span`을 그대로 쓰면 세로선이 되어 빛과 평행하게 놓인다.

### ⑥′ 실행과 종료 조건 (bend run)

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(xcen, tran_bend_y), 1e-6))
```

- **무엇**: 이번에는 수직 암 끝(투과 단면 위치)의 Ez가 줄어들 때까지 돌린다.
- **왜**: 감시점은 빛이 마지막으로 지나가는 곳이어야 한다. bend에서는 그곳이 수직 암 끝이다.
- **틀리면**: 감시점을 기준 run과 같은 (+6.5, −4)로 두면 bend 구조에서는 그곳에 도파로가 없어 필드가 금방 사라지고, 투과 펄스가 다 지나기 전에 run이 끝난다.

### ⑦ 후처리 — 숫자로 바꾸기

```python
T = np.array(mp.get_fluxes(tran)) / P_in      # transmitted fraction
R = -np.array(mp.get_fluxes(refl)) / P_in     # backward flux is negative -> flip the sign
L = 1.0 - T - R                               # what is left: radiated out at the corner
ic = nfreq // 2
print(f"T = {T[ic]:.4f}, R = {R[ic]:.4f}, radiation loss = {L[ic]:.4f}")
```

- **무엇**: 두 flux를 P_in으로 나눠 T·R을 얻고, 1에서 뺀 나머지를 방사 손실로 해석한다.
- **왜**: Meep의 flux는 방향이 있다. 반사 단면의 flux는 −x 방향이라 음수로 나오므로 부호를 뒤집어야 반사된 양이 된다. `1 - T - R`은 방사 monitor를 따로 두지 않았을 때의 잔여 추정이다.
- **틀리면**: 부호를 안 뒤집으면 R이 음수, L이 1을 넘는다.

## 5. 결과

![field]({{ site.baseurl }}/assets/meep/05/02_field.png)
*가는 실선(왼쪽 검정, 오른쪽 흰색)은 유전율 경계, 즉 L자 도파로의 윤곽이다. 왼쪽 Re(Ez)는 수평 암(y = −4)을 따라 또렷한 줄무늬가 오다가 코너(4, −4)a = (0.93, −0.93) µm에서 위쪽·오른쪽 cladding으로 큰 파면이 퍼져 나간다. 오른쪽 \|Ez\|에서 수평 암은 밝고 수직 암(x = 4)은 훨씬 어둡다. 밝기 차이가 T ≈ 0.2이고, 코너 주변의 흐릿한 빛이 방사 58%다. 수평 암의 줄무늬가 균일하지 않고 마디가 보이는 것은 반사파와의 정상파(standing wave) 간섭이다.*

![spectrum]({{ site.baseurl }}/assets/meep/05/03_spectrum.png)
*중심 파장 1550 nm(점선) 근처에서 방사(초록)가 가장 크고 T(파랑)는 0.2 부근이다. 대역 가장자리(1160 nm, 2325 nm)는 source power가 작아 값이 튀므로 경향만 본다. 파장이 길수록 T가 올라가는 것은 모드가 덜 갇혀(cladding으로 더 퍼져) 코너의 급격함을 덜 느끼기 때문이다.*

| 물리량 | 값 @ 1550 nm (6.67a) | 비교 대상 |
|--------|-----------|-----------|
| T | 0.1997 | 공식 튜토리얼도 "낮은 T" 시연 목적 |
| R | 0.2202 | — |
| L (방사, 잔여) | 0.5801 | — |
| T + R | 0.4199 | ≤ 1 성립 |

### 예측과 비교

| 물리량 | 내 예측 (§2) | 시뮬레이션 | 판정 |
|--------|-------------|-----------|------|
| T | 0.5 미만 | 0.20 | ✅ |
| R | 수십 % | 0.22 | ✅ |
| L | 가장 큰 몫 | 0.58 | ✅ |
| 필드 모양 | 코너 방사 lobe, 수직 암 희미 | 그림 확인 | ✅ |
| T + R | ≤ 1 | 0.42 | ✅ |

방향은 모두 맞았지만 T = 0.20이라는 값은 계산해 봐야 안다. T + R ≤ 1은 예측이 아니라 검산이다. 깨지면 물리가 아니라 코드가 틀린 것이다.

**검증 체크**: T + R = 0.42 ≤ 1 · source(x = −6.5)·반사 단면(−5.5)·투과 단면(y = 6.5) 모두 PML(|x|, |y| > 7) 밖 · 두 run 모두 field decay 기준 종료.

## 6. 흔한 실수

| 증상 | 원인 | 고치는 법 |
|------|------|----------|
| T + R > 1 | `load_minus_flux_data`를 빼먹음 | bend run에서 반사 monitor를 만든 **직후** 호출 |
| R이 음수 | 뒤로 가는 flux 부호를 안 뒤집음 | `R = -get_fluxes(refl) / P_in` |
| `load_minus_flux_data` 배열 크기 오류 | 두 run의 resolution·cell·monitor 위치 불일치 | `make_sim` 같은 함수로 두 run 생성 |
| 투과 T ≈ 0 | 투과 단면이 세로선(`span`)으로 빛과 평행 | 수직 암에서는 `size=(w+2, 0)` 가로선 |
| 스펙트럼 가장자리가 튐 | 대역이 넓어 가장자리 source power ≈ 0 | `df`를 줄이거나 중심 ±30%만 해석 |
| R이 이상하게 큼 | 반사 단면이 source 상류, 또는 PML 얇음 | 반사 단면은 source **하류**, `dpml ≥ λ/6` |

## 7. 직접 해보기

| 바꿀 것 | 예상 변화 | 확인할 수치 |
|---------|----------|------------|
| 코너를 반지름 R의 1/4 원호로 (`mp.Cylinder` 두 개 차집합) | R이 파장 몇 배만 되어도 T가 0.9 이상 | T, L |
| `fcen` 0.15 → 0.10 (파장 10a = 2325 nm) | 모드가 덜 갇혀 T ↑, L ↓ | 스펙트럼 그림의 2325 nm 값과 비교 |
| `resolution` 25 → 10 (공식 값) | 코너가 거칠어져 T·R이 수 % 흔들림 | T 차이 |
| `eps_wg` 12 → 4 | confinement 약화. 코너에서 더 많이 새지만 모드 자체도 넓어짐 | T, L |

## 8. 전체 코드

<details>
<summary>bend90.py (클릭해서 펼치기)</summary>
{% highlight python %}
"""Meep Example 02 - 90 degree Waveguide Bend (two-run flux normalization).

A dielectric waveguide (eps = 12, width 1) turns a sharp 90 degree corner.
Run 1: straight waveguide  -> input power P_in and the "incident" flux data at the reflection plane.
Run 2: bent waveguide      -> transmitted flux (vertical arm) and reflected flux (incident part subtracted).
T = P_tran / P_in,  R = -P_refl / P_in,  radiation loss = 1 - T - R.
Follows the official bend-flux tutorial (dimensionless units, a = 1).

Run:  python bend90.py            (~2 min on one core)
Out:  01_layout.png, 02_field.png, 03_spectrum.png, result.json
"""
import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import meep as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, annotated_layout, field_figure, spectrum_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "05")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# Dimensionless units as in the official tutorial: 1 length unit = a (think 1 um).
eps_wg = 12.0            # waveguide permittivity (n = sqrt(12) = 3.46)
w = 1.0                  # waveguide width
fcen = 0.15              # center frequency -> wavelength 1/0.15 = 6.67 units
df = 0.1                 # source bandwidth
nfreq = 11               # number of frequencies in the flux monitors

# Physical reading used only for the figures: choose a so that the center wavelength is 1550 nm.
a_nm = 1550 * fcen       # = 232.5 nm per unit  -> waveguide width 233 nm, cell 3.72 um
a_um = a_nm / 1000

resolution = 25          # pixels per unit -> width = 25 px, wavelength in the guide (1.92) = 48 px
dpml = 1.0               # PML thickness
sx = sy = 16.0           # square cell, PML included

ycen = -4.0              # y of the input (horizontal) arm
xcen = +4.0              # x of the output (vertical) arm  -> corner at (xcen, ycen)

src_x = -6.5             # source: 0.5 outside the left PML (PML edge at x = -7)
refl_x = -5.5            # reflection flux plane: downstream of the source
tran_straight_x = +6.5   # transmission plane for the straight reference run
tran_bend_y = +6.5       # transmission plane for the bend run (on the vertical arm)
span = mp.Vector3(0, w + 2)   # source / monitor line: core + 1 unit on each side (evanescent tail)


# ---------------------------------------------------------------- (2) materials & geometry
def make_geometry(bend: bool):
    """Straight reference (bend=False) or the L-shaped bend (bend=True). Same width and material."""
    wg = mp.Medium(epsilon=eps_wg)
    if not bend:
        return [mp.Block(center=mp.Vector3(0, ycen), size=mp.Vector3(mp.inf, w), material=wg)]
    horizontal = mp.Block(center=mp.Vector3(0.5 * (-sx / 2 + xcen + w / 2), ycen),
                          size=mp.Vector3(sx / 2 + xcen + w / 2, w), material=wg)   # left PML -> corner
    vertical = mp.Block(center=mp.Vector3(xcen, 0.5 * (ycen - w / 2 + sy / 2)),
                        size=mp.Vector3(w, sy / 2 - ycen + w / 2), material=wg)     # corner -> top PML
    return [horizontal, vertical]


# ---------------------------------------------------------------- (3) source
# A plain Ez line source (not an eigenmode source), as in the official tutorial.
# It excites mostly the guided mode plus some radiation; the straight reference run
# measures exactly what the source puts into the guide, so that part cancels out.
sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ez,
                     center=mp.Vector3(src_x, ycen), size=span)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(bend: bool):
    return mp.Simulation(cell_size=mp.Vector3(sx, sy), resolution=resolution,
                         boundary_layers=[mp.PML(dpml)],
                         geometry=make_geometry(bend), sources=sources)


t0 = time.time()

# ================================================================ RUN 1: straight reference
sim = make_sim(bend=False)
# ---------------------------------------------------------------- (5) monitors, run 1
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(refl_x, ycen), size=span))
tran0 = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(tran_straight_x, ycen), size=span))

# ---------------------------------------------------------------- (6) run 1 & stop condition
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(tran_straight_x, ycen), 1e-6))

P_in = np.array(mp.get_fluxes(tran0))     # what actually travels down the guide = input power
refl_data = sim.get_flux_data(refl)       # incident fields at the reflection plane (to subtract later)
freqs = np.array(mp.get_flux_freqs(tran0))
t_run1 = time.time() - t0

# ================================================================ RUN 2: bend
sim = make_sim(bend=True)
# ---------------------------------------------------------------- (5) monitors, run 2
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(refl_x, ycen), size=span))
sim.load_minus_flux_data(refl, refl_data)  # subtract the incident part -> this monitor now sees reflection only
tran = sim.add_flux(fcen, df, nfreq,
                    mp.FluxRegion(center=mp.Vector3(xcen, tran_bend_y), size=mp.Vector3(w + 2, 0)))

decay_pt = (xcen, tran_bend_y)   # where stop_when_fields_decayed watches in the bend run (step 6)
annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=dpml, unit="um", axis_scale=a_um, axis_step=0.5,
    figsize=(7.5, 7.2), pml_xy=(-3.0, -sy / 2 + dpml / 2),
    params_text=(f"a = {a_nm:.1f} nm  (1 Meep unit)\n"
                 f"eps={eps_wg:g}  w={w:g}a={w*a_nm:.1f}nm  dpml={dpml:g}a\n"
                 f"wl={1/fcen:.2f}a={a_nm/fcen:.0f}nm  res={resolution}/a  cell={sx:g}a"),
    params_xy=(-6.6, 6.6), decay_point=decay_pt, decay_text_xy=(4.6, 5.6),
    title="90-deg waveguide bend (eps = 12, w = 1): Ez line source, flux monitors, PML",
    labels=[
        Label("horizontal arm (geometry)", (-1.0, ycen), (-3.5, -1.8), step=2, color="black"),
        Label("vertical arm (geometry)", (xcen - 0.5, 2.0), (-2.5, 3.5), step=2, color="black"),
        Label("Ez line source", (src_x, ycen - 1.6), (-6.3, -6.2), step=3, color="red"),
        Label("flux: reflection (minus incident)", (refl_x, ycen + 1.6), (-6.3, 0.2), step=5, color="blue"),
        Label("flux: transmission", (xcen - 1.5, tran_bend_y), (0.0, 5.0), step=5, color="blue"),
    ])

nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml, sy - 2 * dpml))
dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)

# ---------------------------------------------------------------- (6) run 2 & stop condition
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
wall = time.time() - t0

# ---------------------------------------------------------------- (7) post-processing
T = np.array(mp.get_fluxes(tran)) / P_in      # transmitted fraction
R = -np.array(mp.get_fluxes(refl)) / P_in     # backward flux is negative -> flip the sign
L = 1.0 - T - R                               # what is left: radiated out at the corner
ic = nfreq // 2
wl = 1 / freqs
print(f"T = {T[ic]:.4f}, R = {R[ic]:.4f}, radiation loss = {L[ic]:.4f}  (run1 {t_run1:.0f} s, total {wall:.0f} s)")
print(f"T over band {wl.min():.2f}-{wl.max():.2f}: {T.min():.3f} .. {T.max():.3f}")

ez = sim.get_dft_array(dft, mp.Ez, 0)
eps = sim.get_array(vol=nonpml, component=mp.Dielectric)   # structure outline for the figure
extent_um = [v * a_um for v in (-(sx / 2 - dpml), sx / 2 - dpml, -(sy / 2 - dpml), sy / 2 - dpml)]
field_figure(ez, extent_um, os.path.join(OUT, "02_field.png"), core_halfwidth=None, eps=eps,
             wl=round(a_nm / fcen), wl_unit="nm", component="Ez", layout="row", aspect="equal", unit="um")
spectrum_figure(wl * a_nm, {"T (transmitted)": T, "R (reflected)": R, "1 - T - R (radiated)": L},
                os.path.join(OUT, "03_spectrum.png"), unit="nm", mark=1550, mark_label="1550 nm (fcen)")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"T": float(T[ic]), "R": float(R[ic]), "loss": float(L[ic]),
                   "a_nm": a_nm, "wavelengths_a": wl.tolist(), "wavelengths_nm": (wl * a_nm).tolist(),
                   "T_spectrum": T.tolist(),
                   "R_spectrum": R.tolist(), "P_in_spectrum": P_in.tolist(),
                   "wall_s": wall, "run1_s": t_run1, "meep": mp.__version__},
                  f, indent=2)
{% endhighlight %}
</details>

§4의 발췌 코드와 달리 전체 코드에는 그림 저장·result.json 기록이 들어 있다. 그림 helper `blogfig.py`(`annotated_layout`, `field_figure`, `spectrum_figure`)는 시리즈 공통이며 같은 폴더(`code/`)에 있다. 전체 코드와 helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**실행 결과 (2026-10-23 재실행)**:
```
T = 0.1997, R = 0.2202, radiation loss = 0.5801  (run1 6 s, total 12 s)
T over band 5.00-10.00: 0.169 .. 0.512
```

**재현 환경**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · 실행 `python bend90.py` (약 12 s, 단일 코어)

## 9. 더 읽기

- 공식 튜토리얼 (Transmittance Spectrum of a Waveguide Bend): https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend
- `add_flux` / `load_minus_flux_data` 레퍼런스: https://meep.readthedocs.io/en/latest/Python_User_Interface/#flux-spectra
- 이전 글: [04 · Straight waveguide와 guided mode]({{ site.baseurl }}/straight-waveguide/) · 다음 글: 06 · Binary grating과 diffraction order
