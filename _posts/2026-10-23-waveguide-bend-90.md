---
layout: post
date: 2026-10-23
title: "Meep Example 05 · Bent waveguide와 radius trade-off — 2-run flux 정규화, sharp bend 기준값, radius sweep"
title_en: "Meep Example 05 · Bent waveguide and the radius trade-off — two-run flux normalization, sharp-bend baseline, radius sweep"
lang: ko
series: meep-examples
part: 5
level: beginner
runtime: "95 s (sharp bend 10 s + radius sweep + convergence)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend"
tags: [meep, fdtd, waveguide, bend, flux, normalization]
image: /assets/meep/05/02_field.png
excerpt: "a dielectric waveguide (ε = 12, width 1) turns a sharp 90° corner. We measure how much power goes around the corner, how much comes back, and how much leaks out."
---
## TL;DR (English)

![hero]({{ site.baseurl }}/assets/meep/05/02_field.png)

- **What**: a dielectric waveguide (ε = 12, width 1) turns a sharp 90° corner. We measure how much power goes around the corner, how much comes back, and how much leaks out.
- **Result**: T = 0.20, R = 0.22, radiated = 0.58 at the center wavelength. Most of the light is lost at the sharp corner. Rounding it recovers the light: T = 0.91 at a bend radius of 0.35 µm and 0.99 at 0.70 µm.
- **Takeaway**: two-run flux normalization. A straight reference run gives the input power and the incident fields; subtracting them in the bend run leaves only the reflection. A sharp corner is not usable in a photonic circuit.
- **Code**: full script at the bottom, ~95 s on one core (the sharp bend alone takes 10 s).

## 0. 이 글에서 배우는 것

- `add_flux`와 `FluxRegion`으로 단면을 지나는 power(flux) 재기
- 2-run 정규화: 직선 기준 run의 `get_flux_data` → bend run의 `load_minus_flux_data`로 입사 성분을 빼고 반사만 남기기
- 뒤로 가는 flux는 음수라는 것, 그리고 에너지 수지 T + R + L = 1로 결과를 검산하는 법
- 코너에 반지름을 주면서 손실이 사라지는 지점(knee)을 찾는 radius sweep
- 물리 교훈: 급격한 직각 꺾임은 빛의 절반 이상을 밖으로 버린다. 그래서 광회로는 곡선 굽힘을 쓴다

**전제 지식**: 04편의 도파로·모드 개념. **공식 예제**: [Transmittance Spectrum of a Waveguide Bend](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend). **이전 글**: [04 · Straight waveguide와 guided mode]({{ site.baseurl }}/straight-waveguide/) · **다음 글**: [06 · Binary grating과 diffraction order]({{ site.baseurl }}/binary-grating/)

## 1. 무엇을 알고 싶은가

04편의 직선 도파로는 넣은 빛을 전부 내보냈다. 같은 도파로를 직각으로 꺾으면 얼마가 코너를 돌아 나가고(T), 얼마가 되돌아오고(R), 얼마가 밖으로 새는가(L). 이 예제를 고른 이유는 두 가지다. 답을 미리 알 수 없는 첫 문제이고, 투과율을 잴 때 기준 run을 먼저 돌려 나누는 Meep의 관례가 여기서 처음 나온다.

### 어디에 쓰이는가

bend 반지름은 칩 면적을 정하는 숫자다. 반지름을 두 배로 하면 고리 하나의 면적은 네 배가 되고, foundry의 설계 규칙에는 최소 반지름이 적혀 있다.

| 응용 | 이 글의 어떤 것을 쓰는가 | 그 다음에 필요한 것 |
|---|---|---|
| PIC 배선과 면적(footprint) | 반지름–손실 곡선과 knee | 09편 역설계 bend |
| ring resonator·spiral delay line | 작은 반지름의 곡률 손실이 Q와 FSR을 정한다 | 12편 고리 |
| foundry PDK의 최소 bend radius 규칙 | knee 1.5~2a가 그 규칙의 근거 | — |
| 입력 대비 출력의 모든 측정 | 2-run 정규화 | 06편 이후 전부 |


## 2. 물리 한 페이지

<!-- concept-illustration:part-05:start -->

![직선 기준, 날카로운 L자 굽힘, 둥근 굽힘을 비교한다. 입력은 왼쪽, 출력은 위쪽이며 날카로운 코너의 반사와 바깥 방사 경로를 표시한다.]({{ site.baseurl }}/assets/meep/05/00_concept.png)

*공기 속 ε = 12 유전체 도파로에서 직선 기준과 날카로운 직각, 둥근 굽힘을 비교합니다. 유효 입사광은 왼쪽에서 +x 방향으로 들어오고 출력은 위쪽 +y 방향입니다. 코너에서는 투과·반사·바깥 방사가 나뉠 수 있습니다. 그림의 R ≈ 0.70 µm는 둥근 굽힘의 중심선 곡률반경 0.6975 µm를 반올림한 값입니다. 점선은 위치 안내선입니다. 화살표 굵기는 계산된 전력 비율을 나타내지 않습니다. 파장을 1550 nm로 읽는 이 글의 환산에서 폭은 232.5 nm입니다.*

<!-- concept-illustration:part-05:end -->

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

![source]({{ site.baseurl }}/assets/meep/05/00_source.png)
*source의 시간 파형(왼쪽)과 power 스펙트럼(오른쪽). width = 1/fwidth = 10, 펄스 정점 t0 = 50. monitor 대역(1162–2325 nm) 가장자리의 source power는 중심의 0.005%다. 그래서 §5 스펙트럼의 양 끝 값은 0에 가까운 수를 0에 가까운 수로 나눈 것이고, 경향만 본다.*

**강의 노트북과의 차이**: 강의 week 6은 n 3.4/1.44, 폭 0.6 µm의 곡선 bend에서 radius 0.6–3.0 µm를 훑는다. 이 글은 공식 sharp bend(ε = 12, w = 1a)를 기준값으로 두고, 같은 구조의 코너만 둥글려 radius를 훑는다.

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

### ②′ 둥근 코너 — 사분원 고리

```python
r = radius
cx, cy = xcen - r, ycen + r                      # center of the quarter ring
big = r + w / 2 + 1.0
geom = [mp.Cylinder(radius=r + w / 2, center=mp.Vector3(cx, cy), material=wg),    # outer disk: waveguide
        mp.Cylinder(radius=r - w / 2, center=mp.Vector3(cx, cy), material=air),   # inner disk: air -> ring
        # keep only the lower-right quadrant (x > cx, y < cy): cover the other three with air
        mp.Block(center=mp.Vector3(cx - big / 2, cy), size=mp.Vector3(big, 2 * big), material=air),
        mp.Block(center=mp.Vector3(cx + big / 2, cy + big / 2), size=mp.Vector3(big, big), material=air)]
# the two arms are appended AFTER this list, so they are drawn on top of the air blocks
```

- **무엇**: 반지름 r + w/2의 원판에서 r − w/2의 원판을 빼 고리를 만들고, 공기 블록으로 세 사분면을 덮어 오른쪽 아래 1/4만 남긴다. 수평 암은 x = xcen − r에서, 수직 암은 y = ycen + r에서 고리와 만난다.
- **왜**: Meep의 geometry는 나중 객체가 앞 객체를 덮어쓴다. 그래서 "원판 → 공기 원판 → 공기 블록 → 암" 순서가 곧 차집합 연산이다. r = 0이면 고리가 없고 sharp 코너로 돌아간다.
- **틀리면**: 암을 공기 블록보다 먼저 넣으면 블록이 암의 끝을 지운다. 공기 블록을 빠뜨리면 고리 전체가 남아 도파로가 원을 그린다.

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

### 코너를 둥글리면: radius sweep

![radius sweep]({{ site.baseurl }}/assets/meep/05/04_radius_sweep.png)
*같은 구조에서 코너 반지름만 바꿨을 때의 T, R, 방사. 반지름 0이 위의 sharp bend다. 축은 a = 232.5 nm로 환산한 µm.*

![round]({{ site.baseurl }}/assets/meep/05/05_field_round.png)
*반지름 3a = 0.70 µm. 수평 암의 정상파 마디가 사라지고(반사 0.03%), 코너 밖으로 새는 빛이 거의 없다.*

![sharp animation]({{ site.baseurl }}/assets/meep/05/06_anim_sharp.gif)
*sharp 코너의 시간 전개. 펄스가 코너에 닿는 순간 cladding으로 큰 파면이 퍼져 나가고, 수직 암으로는 일부만 올라간다. 되돌아오는 파가 수평 암에서 입사파와 겹친다.*

![round animation]({{ site.baseurl }}/assets/meep/05/06_anim_round.gif)
*반지름 3a 코너의 시간 전개. 같은 펄스가 코너를 돌아 수직 암 위의 투과 단면(파란 선)까지 거의 그대로 간다.*

| 반지름 | µm | T | R | 방사 |
|---|---|---|---|---|
| 0 (sharp) | 0 | 0.200 | 0.220 | 0.580 |
| 0.5a | 0.12 | 0.487 | 0.052 | 0.462 |
| 1a | 0.23 | 0.746 | 0.001 | 0.253 |
| 1.5a | 0.35 | 0.907 | 0.001 | 0.092 |
| 2a | 0.47 | 0.964 | 0.000 | 0.036 |
| 3a | 0.70 | 0.986 | 0.000 | 0.014 |
| 4a | 0.93 | 1.003 | 0.000 | −0.003 |
| 6a | 1.40 | 1.000 | 0.000 | 0.000 |

반사는 반지름 1a(파장의 1/7)에서 이미 사라진다. 방사는 더 천천히 줄어 1.5a에서 10% 아래로, 3a에서 1% 대로 내려간다. 손실이 꺾이는 무릎(knee)은 1.5–2a, 즉 도파로 안 파장(1.92a)의 한 배 근처다. 그보다 큰 반지름은 면적만 늘린다. 4a에서 T가 1을 0.3% 넘는 것은 정규화 run과 bend run의 수치 오차이지 이득이 아니다.

### 수렴성 (sharp bend)

| resolution | dpml | T | R | 방사 | 비고 |
|---|---|---|---|---|---|
| 25 | 1.0 | 0.200 | 0.220 | 0.580 | 기준 |
| 10 | 1.0 | 0.198 | 0.229 | 0.573 | 공식 예제 해상도 |
| 40 | 1.0 | 0.189 | 0.224 | 0.587 | 해상도 1.6배 |
| 25 | 1.5 | 0.170 | 0.217 | 0.612 | PML 두껍게. source·monitor 면이 0.5a 안쪽으로 |

해상도 10에서 40까지 T는 5% 안에서 움직인다. 그런데 PML을 두껍게 하면서 source와 monitor 면을 0.5a 안쪽으로 옮기자 T가 15% 내려갔다. 코너에서 방사된 빛이 투과 단면과 PML 사이에서 어떻게 잡히느냐에 따라 값이 달라진다는 뜻이다. sharp bend의 T = 0.20은 첫째 자리까지만 의미가 있다. 둥근 bend(R ≥ 2a)는 방사가 거의 없어서 이 민감도가 사라진다.

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

### 주장할 수 있는 것 / 없는 것

- 할 수 있는 것: sharp bend는 power의 절반 이상을 방사로 잃는다. 반지름을 도파로 안 파장의 한 배(1.5–2a, 0.35–0.47 µm) 이상 주면 손실이 10% 아래로 떨어지고, 3a 이상에서는 더 얻을 것이 없다.
- 할 수 없는 것: sharp bend의 T = 0.20의 둘째 자리. 해상도와 monitor 위치에 따라 0.17–0.20으로 움직인다. 3D 도파로나 다른 굴절률 대비에서의 knee 위치. 방사 monitor 없이 잔여로 추정한 방사량의 정확한 값.

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
| `w` 1 → 0.6a (좁은 도파로) | 모드가 덜 갇혀 같은 반지름에서 손실이 커지고 knee가 큰 R로 이동 | sweep 곡선 |
| `fcen` 0.15 → 0.10 (파장 10a = 2325 nm) | 모드가 덜 갇혀 T ↑, L ↓ | 스펙트럼 그림의 2325 nm 값과 비교 |
| `resolution` 25 → 10 (공식 값) | 코너가 거칠어져 T·R이 수 % 흔들림 | T 차이 |
| `eps_wg` 12 → 4 | confinement 약화. 코너에서 더 많이 새지만 모드 자체도 넓어짐 | T, L |

## 8. 전체 코드

<details>
<summary>bend90.py (클릭해서 펼치기)</summary>
{% highlight python %}
"""Meep Example 05 - Bent waveguide and the radius trade-off (two-run flux normalization).

A dielectric waveguide (eps = 12, width 1) turns a 90 degree corner.
Run 1: straight waveguide  -> input power P_in and the "incident" flux data at the reflection plane.
Run 2: bent waveguide      -> transmitted flux (vertical arm) and reflected flux (incident part subtracted).
T = P_tran / P_in,  R = -P_refl / P_in,  radiation loss = 1 - T - R.
The sharp corner (radius 0) follows the official bend-flux tutorial; then the corner is rounded
with a quarter-ring of radius R and T is swept over R to find where the loss disappears.

Run:  python bend90.py            (~3 min on one core: sharp + radius sweep + convergence)
Out:  00_source.png, 01_layout.png, 02_field.png, 03_spectrum.png, 04_radius_sweep.png,
      05_field_round.png, 06_anim_sharp.gif, 06_anim_round.gif, result.json   (-> ../assets/05/)
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
from blogfig import (Label, animate_fields, annotated_layout, field_figure, line_figure,   # noqa: E402
                     record_frames, source_figure, spectrum_figure)

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

RESOLUTION = 25          # pixels per unit -> width = 25 px, wavelength in the guide (1.92) = 48 px
DPML = 1.0               # PML thickness
sx = sy = 16.0           # square cell, PML included

ycen = -4.0              # y of the input (horizontal) arm
xcen = +4.0              # x of the output (vertical) arm  -> corner at (xcen, ycen)
span = mp.Vector3(0, w + 2)   # source / monitor line: core + 1 unit on each side (evanescent tail)


def positions(dpml):
    """Source and monitor planes measured from the PML edge, so a thicker PML keeps them outside it."""
    edge = sx / 2 - dpml
    return {"src_x": -edge + 0.5,          # source: 0.5 outside the left PML
            "refl_x": -edge + 1.5,         # reflection flux plane: downstream of the source
            "tran_straight_x": edge - 0.5,  # transmission plane for the straight reference run
            "tran_bend_y": edge - 0.5}      # transmission plane for the bend run (on the vertical arm)


# ---------------------------------------------------------------- (2) materials & geometry
def make_geometry(bend: bool, radius: float = 0.0):
    """Straight reference (bend=False), sharp corner (radius=0) or rounded corner (radius>0).

    The rounded corner is a quarter ring: outer cylinder (waveguide) minus inner cylinder (air),
    cut down to one quadrant with air blocks; the two arms are drawn last so they stay intact.
    """
    wg = mp.Medium(epsilon=eps_wg)
    air = mp.Medium(epsilon=1.0)
    if not bend:
        return [mp.Block(center=mp.Vector3(0, ycen), size=mp.Vector3(mp.inf, w), material=wg)]
    r = radius
    cx, cy = xcen - r, ycen + r                      # center of the quarter ring
    geom = []
    if r > 0:
        big = r + w / 2 + 1.0
        geom += [mp.Cylinder(radius=r + w / 2, center=mp.Vector3(cx, cy), material=wg),
                 mp.Cylinder(radius=r - w / 2, center=mp.Vector3(cx, cy), material=air)]
        # keep only the lower-right quadrant (x > cx, y < cy)
        geom += [mp.Block(center=mp.Vector3(cx - big / 2, cy), size=mp.Vector3(big, 2 * big), material=air),
                 mp.Block(center=mp.Vector3(cx + big / 2, cy + big / 2), size=mp.Vector3(big, big), material=air)]
    # sharp corner: the arms overlap by w x w so the outer corner is filled (official geometry);
    # rounded corner: the arms stop where the ring begins
    x_end = xcen + w / 2 if r == 0 else xcen - r     # horizontal arm: left PML -> corner / ring
    horizontal = mp.Block(center=mp.Vector3(0.5 * (-sx / 2 + x_end), ycen),
                          size=mp.Vector3(sx / 2 + x_end, w), material=wg)
    y_start = ycen - w / 2 if r == 0 else ycen + r   # vertical arm: corner / ring -> top PML
    vertical = mp.Block(center=mp.Vector3(xcen, 0.5 * (y_start + sy / 2)),
                        size=mp.Vector3(w, sy / 2 - y_start), material=wg)
    return geom + [horizontal, vertical]


# ---------------------------------------------------------------- (3) source
def make_sources(dpml):
    """A plain Ez line source (not an eigenmode source), as in the official tutorial."""
    p = positions(dpml)
    return [mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ez,
                      center=mp.Vector3(p["src_x"], ycen), size=span)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(bend: bool, radius=0.0, resolution=RESOLUTION, dpml=DPML):
    return mp.Simulation(cell_size=mp.Vector3(sx, sy), resolution=resolution,
                         boundary_layers=[mp.PML(dpml)],
                         geometry=make_geometry(bend, radius), sources=make_sources(dpml))


_reference = {}


def reference_run(resolution, dpml):
    """RUN 1 (cached per resolution/PML): straight guide -> P_in and the incident flux data."""
    key = (resolution, dpml)
    if key in _reference:
        return _reference[key]
    p = positions(dpml)
    sim = make_sim(bend=False, resolution=resolution, dpml=dpml)
    # ------------------------------------------------------------ (5) monitors, run 1
    refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
    tran0 = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["tran_straight_x"], ycen), size=span))
    # ------------------------------------------------------------ (6) run 1 & stop condition
    sim.run(until_after_sources=mp.stop_when_fields_decayed(
                25, mp.Ez, mp.Vector3(p["tran_straight_x"], ycen), 1e-6))
    _reference[key] = {"P_in": np.array(mp.get_fluxes(tran0)),      # what actually travels down the guide
                       "refl_data": sim.get_flux_data(refl),         # incident fields at the reflection plane
                       "freqs": np.array(mp.get_flux_freqs(tran0))}
    return _reference[key]


def bend_run(radius=0.0, resolution=RESOLUTION, dpml=DPML, figures=False, field_png=None):
    """RUN 2: the bend. Returns T, R, L spectra (fractions of P_in)."""
    ref = reference_run(resolution, dpml)
    p = positions(dpml)
    sim = make_sim(bend=True, radius=radius, resolution=resolution, dpml=dpml)
    # ------------------------------------------------------------ (5) monitors, run 2
    refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
    sim.load_minus_flux_data(refl, ref["refl_data"])  # subtract the incident part -> reflection only
    tran = sim.add_flux(fcen, df, nfreq,
                        mp.FluxRegion(center=mp.Vector3(xcen, p["tran_bend_y"]), size=mp.Vector3(w + 2, 0)))
    decay_pt = (xcen, p["tran_bend_y"])
    if figures:
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
                Label("Ez line source", (p["src_x"], ycen - 1.6), (-6.3, -6.2), step=3, color="red"),
                Label("flux: reflection (minus incident)", (p["refl_x"], ycen + 1.6), (-6.3, 0.2), step=5, color="blue"),
                Label("flux: transmission", (xcen - 1.5, p["tran_bend_y"]), (0.0, 5.0), step=5, color="blue"),
            ])
    want_field = figures or field_png is not None
    if want_field:
        nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml, sy - 2 * dpml))
        dft = sim.add_dft_fields([mp.Ez], fcen, 0, 1, where=nonpml)
    # ------------------------------------------------------------ (6) run 2 & stop condition
    sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
    # ------------------------------------------------------------ (7) post-processing
    T = np.array(mp.get_fluxes(tran)) / ref["P_in"]      # transmitted fraction
    R = -np.array(mp.get_fluxes(refl)) / ref["P_in"]     # backward flux is negative -> flip the sign
    L = 1.0 - T - R                                      # what is left: radiated out at the corner
    if want_field:
        ez = sim.get_dft_array(dft, mp.Ez, 0)
        eps = sim.get_array(vol=nonpml, component=mp.Dielectric)
        extent_um = [v * a_um for v in (-(sx / 2 - dpml), sx / 2 - dpml, -(sy / 2 - dpml), sy / 2 - dpml)]
        field_figure(ez, extent_um, os.path.join(OUT, field_png or "02_field.png"), core_halfwidth=None,
                     eps=eps, wl=round(a_nm / fcen), wl_unit="nm", component="Ez",
                     layout="row", aspect="equal", unit="um")
    return {"T": T, "R": R, "L": L, "freqs": ref["freqs"]}


t_all = time.time()
ic = nfreq // 2

# source waveform and spectrum; the monitor band is fcen +- df/2
src_info = source_figure(fcen, df, os.path.join(OUT, "00_source.png"), mon_fcen=fcen, mon_df=df,
                         wl_scale=a_nm, wl_unit="nm", time_unit="a/c")

# ================================================================ sharp corner (official example)
t0 = time.time()
sharp = bend_run(0.0, figures=True)
wall_sharp = time.time() - t0
wl = 1 / sharp["freqs"]
print(f"sharp: T = {sharp['T'][ic]:.4f}, R = {sharp['R'][ic]:.4f}, radiation loss = {sharp['L'][ic]:.4f}  ({wall_sharp:.0f} s incl. reference)")
print(f"T over band {wl.min():.2f}-{wl.max():.2f}: {sharp['T'].min():.3f} .. {sharp['T'].max():.3f}")
spectrum_figure(wl * a_nm, {"T (transmitted)": sharp["T"], "R (reflected)": sharp["R"], "1 - T - R (radiated)": sharp["L"]},
                os.path.join(OUT, "03_spectrum.png"), unit="nm", mark=1550, mark_label="1550 nm (fcen)")

# ================================================================ radius sweep
radii = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]
sweep = []
for r in radii:
    if r == 0.0:
        res = sharp
    else:
        res = bend_run(r, field_png=("05_field_round.png" if r == 3.0 else None))
    sweep.append({"radius_a": r, "radius_um": r * a_um, "radius_over_wl": r * fcen,
                  "T": float(res["T"][ic]), "R": float(res["R"][ic]), "L": float(res["L"][ic])})
    print(f"radius {r:.1f} a ({r*a_um:.2f} um): T={res['T'][ic]:.4f} R={res['R'][ic]:.4f} L={res['L'][ic]:.4f}")
line_figure([s["radius_um"] for s in sweep],
            {"T (transmitted)": [s["T"] for s in sweep], "R (reflected)": [s["R"] for s in sweep],
             "1 - T - R (radiated)": [s["L"] for s in sweep]},
            os.path.join(OUT, "04_radius_sweep.png"), xlabel=f"bend radius [um]  (a = {a_nm:.1f} nm, wl = 1550 nm)")

# ================================================================ animations: sharp corner vs rounded corner (radius 3a)
# Fresh simulations with the same source; record from before the pulse peak (t0 = 5/df) until the
# pulse has gone from the source to the top monitor along the guide (distance ~ 21 a at n_eff ~ 2.5).
p = positions(DPML)
nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * DPML, sy - 2 * DPML))
extent_um = [v * a_um for v in (-(sx / 2 - DPML), sx / 2 - DPML, -(sy / 2 - DPML), sy / 2 - DPML)]
for tag, r_anim in (("sharp", 0.0), ("round", 3.0)):
    sim_anim = make_sim(bend=True, radius=r_anim)
    sim_anim.init_sim()
    eps_anim = sim_anim.get_array(vol=nonpml, component=mp.Dielectric)
    frames, times = record_frames(sim_anim, nonpml, mp.Ez, t_start=5.0 / df - 2.0 / df,
                                  t_end=5.0 / df + 21.0 * 2.5 + 10.0, n_frames=60)
    animate_fields(frames, times, extent_um, os.path.join(OUT, f"06_anim_{tag}.gif"), eps=eps_anim,
                   lines=[((p["src_x"] * a_um, (ycen - 1.5) * a_um), (p["src_x"] * a_um, (ycen + 1.5) * a_um), "red", "Ez source"),
                          (((xcen - 1.5) * a_um, p["tran_bend_y"] * a_um), ((xcen + 1.5) * a_um, p["tran_bend_y"] * a_um), "blue", "flux: transmission")],
                   time_unit="a/c", figsize=(5.4, 4.8), title=f"{tag} corner", legend_loc="lower right")

# ================================================================ convergence (sharp corner)
convergence = [{"resolution": RESOLUTION, "dpml": DPML, "T": sweep[0]["T"], "R": sweep[0]["R"], "L": sweep[0]["L"]}]
for res_px, dpml in ((10, 1.0), (40, 1.0), (25, 1.5)):   # change one thing at a time
    t0 = time.time()
    r = bend_run(0.0, resolution=res_px, dpml=dpml)
    convergence.append({"resolution": res_px, "dpml": dpml, "T": float(r["T"][ic]), "R": float(r["R"][ic]),
                        "L": float(r["L"][ic]), "wall_s": time.time() - t0})
    print(f"convergence res={res_px} dpml={dpml}: T={r['T'][ic]:.4f} R={r['R'][ic]:.4f} L={r['L'][ic]:.4f}")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"T": sweep[0]["T"], "R": sweep[0]["R"], "loss": sweep[0]["L"],
                   "a_nm": a_nm, "wavelengths_a": wl.tolist(), "wavelengths_nm": (wl * a_nm).tolist(),
                   "T_spectrum": sharp["T"].tolist(), "R_spectrum": sharp["R"].tolist(),
                   "radius_sweep": sweep, "convergence": convergence, "source": src_info,
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__},
                  f, indent=2)
{% endhighlight %}
</details>

§4의 발췌 코드와 달리 전체 코드에는 그림 저장·result.json 기록이 들어 있다. 그림 helper `blogfig.py`(`annotated_layout`, `field_figure`, `spectrum_figure`)는 시리즈 공통이며 같은 폴더(`code/`)에 있다. 전체 코드와 helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**실행 결과 (2026-10-23 재실행)**:
```
sharp: T = 0.1997, R = 0.2202, radiation loss = 0.5801  (10 s incl. reference)
T over band 5.00-10.00: 0.169 .. 0.512
radius 0.0 a (0.00 um): T=0.1997 R=0.2202 L=0.5801
radius 0.5 a (0.12 um): T=0.4865 R=0.0518 L=0.4617
radius 1.0 a (0.23 um): T=0.7458 R=0.0014 L=0.2528
radius 1.5 a (0.35 um): T=0.9073 R=0.0009 L=0.0918
radius 2.0 a (0.47 um): T=0.9638 R=0.0005 L=0.0358
radius 3.0 a (0.70 um): T=0.9859 R=0.0003 L=0.0138
radius 4.0 a (0.93 um): T=1.0031 R=0.0001 L=-0.0031
radius 6.0 a (1.40 um): T=0.9995 R=0.0000 L=0.0005
convergence res=10 dpml=1.0: T=0.1983 R=0.2287 L=0.5730
convergence res=40 dpml=1.0: T=0.1894 R=0.2241 L=0.5865
convergence res=25 dpml=1.5: T=0.1703 R=0.2173 L=0.6124
```

**재현 환경**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · 실행 `python bend90.py` (약 12 s, 단일 코어)

## 확인 질문

1. `load_minus_flux_data` 줄을 지우면 R은 어느 방향으로 틀어지는가? T는 변하는가?
2. radius sweep에서 반사는 1a에서 사라지는데 방사는 3a까지 남는다. 두 손실의 원인이 어떻게 다른가?
3. 수렴성 표에서 PML을 두껍게 했을 때 T가 내려간 이유로 생각할 수 있는 것은 무엇인가? 어떻게 확인하겠는가?

## 9. 더 읽기

- [공식 튜토리얼: Transmittance Spectrum of a Waveguide Bend](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend)
- [`add_flux` / `load_minus_flux_data` 레퍼런스](https://meep.readthedocs.io/en/latest/Python_User_Interface/#flux-spectra) · [`Cylinder` 레퍼런스](https://meep.readthedocs.io/en/latest/Python_User_Interface/#cylinder)
- 이전 글: [04 · Straight waveguide와 guided mode]({{ site.baseurl }}/straight-waveguide/) · 다음 글: [06 · Binary grating과 diffraction order]({{ site.baseurl }}/binary-grating/)
