---
layout: post
date: 2026-10-21
title: "Meep Example 01 · Point source와 line source — 파원 배치, 펄스 시각 t0, flux box로 보는 방향 분포"
title_en: "Meep Example 01 · Point source and line source — source placement, the pulse time t0, and a flux box for directionality"
lang: ko
series: meep-examples
part: 1
level: beginner
runtime: "21 s (single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#fields-in-a-waveguide"
tags: [meep, fdtd, source, point-source, line-source, flux]
image: /assets/meep/01/02_snapshots.png
excerpt: "a single Ez source in an empty 2D cell, first as a point, then as a 3 µm line. Snapshots after the pulse peak, and a box of four flux planes around the source."
---
## TL;DR (English)

![hero]({{ site.baseurl }}/assets/meep/01/02_snapshots.png)

- **What**: a single Ez source in an empty 2D cell, first as a point, then as a 3 µm line. Snapshots after the pulse peak, and a box of four flux planes around the source.
- **Result**: the point source radiates exactly 25 % through each side of the box; the 3 µm line sends 92 % through the two sides facing it. The wavefront peak sits on the circle r = c (t − t0).
- **Takeaway**: in FDTD a picture is a time stamp. Know the pulse time t0 = 5/fwidth before you read any field, and derive the recording window from the source and the distances, not by guessing.
- **Code**: full script at the bottom, ~21 s on one core.

## 0. 이 글에서 배우는 것

- `mp.Source`의 `center`와 `size`. `size=(0,0,0)`이면 점원, `(0, L, 0)`이면 길이 L의 선원
- `GaussianSource`의 펄스 폭 width = 1/fwidth와 정점 시각 t0 = 5/fwidth. 스냅샷·애니메이션의 시각은 여기서 유도한다
- Meep의 시간 단위: c = 1이라 파면은 1 time unit에 1 µm를 간다
- `add_flux`와 `FluxRegion`으로 source를 둘러싼 네 면의 power를 재고 방향 분포를 숫자로 만들기
- PML이 없으면 벽이 거울이라는 것. 이것이 02편 PML의 동기다

**전제 지식**: 파동이 파장과 속도를 가진다는 것. **공식 예제**: [Basics 튜토리얼의 첫 예제](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#fields-in-a-waveguide)(도파로 안의 점원), [Antenna radiation pattern](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-an-antenna)(점원의 등방성). **다음 글**: 02 · 경계 조건과 PML

## 1. 무엇을 알고 싶은가

Meep 시뮬레이션은 빛을 넣는 source로 시작한다. 구조도 monitor도 없는 빈 상자에 source 하나만 두면 source 자체가 무엇을 하는지 보인다. 점 하나에서 나온 빛은 어떤 모양으로 퍼지는가, 그 모양은 몇 time unit 뒤에 어디까지 가는가, 짧은 선에서 나온 빛은 무엇이 다른가. 세 질문의 답은 그림 한 장이 아니라 시각이 찍힌 그림 여러 장과 네 개의 숫자다.

## 2. 물리 한 페이지

2D에서 Ez 점원은 지면에 수직한 무한 선전류다. 그 빛은 원통파로 퍼진다. 파면은 동심원이고, 진폭은 1/√r로 줄며, 방향 의존성은 없다. 펄스의 정점이 t0에 나갔다면 시각 t의 정점 위치는 r = c (t − t0)이고 Meep에서 c = 1이다.

$$
E_z(r,t)\propto \frac{1}{\sqrt r}\,\cos\!\big(k r-\omega t\big),\qquad r_{\mathrm{peak}}(t)=c\,(t-t_0),\qquad
P_{+x}=P_{-x}=P_{+y}=P_{-y}=\tfrac14 P
$$

길이 L의 선원은 선 위의 점원들을 같은 위상으로 더한 것이다. L이 파장보다 길면 선에 수직한 방향(±x)으로는 파면이 평면에 가깝게 보강되고, 선 방향(±y)으로는 서로 상쇄된다. 양 끝에서는 회절로 둥근 파면이 남는다.

| 기호 | 뜻 | 코드 변수 |
|------|----|-----------|
| width | 펄스 포락선 폭 (시간) | `1 / fwidth` |
| $t_0$ | 펄스 정점 시각 = 5 × width | `t0 = CUTOFF / fwidth` |
| $r_{\mathrm{peak}}$ | 시각 t에 정점 파면이 있는 반지름 | `r_front = offsets[-1]` |
| $d_{\mathrm{wall}}$ | source에서 가장 가까운 벽까지 거리 | `d_wall` |
| $P_{\pm x}, P_{\pm y}$ | box 네 면을 바깥쪽으로 지나는 power | `mp.get_fluxes(mons["+x"])` 등 |

**가정과 유효 범위**: 2D, 진공, Ez 편광. 선원은 같은 위상·같은 진폭의 균일 선전류. 스냅샷 실험은 PML 없이, flux 실험은 PML을 두고 한다.

### 결과 보기 전에 맞춰보기

| 물리량 | 내 예측 | 근거 |
|--------|---------|------|
| 점원 파면 모양 | 동심원 | 2D 점원의 방위 대칭 |
| t0 + 3.6에서 정점 반지름 | 3.6 µm | c = 1 |
| 점원 box 네 면 비율 | 각 0.25 | 등방 |
| 선원(3 µm ≈ 2λ) ±x 비율 | 0.8 이상 | 선에 수직한 방향으로 보강, 선 방향으로 상쇄 |
| PML 없는 셀 | 벽에서 되돌아온 파가 보임 | 경계가 완전 도체처럼 반사 |

**판정 기준**: 점원 네 면이 1% 이상 다르면 flux 면의 weight(법선 방향) 실수. 정점 파면이 예측 원에서 벗어나면 t0를 잘못 알았거나 `until`을 절대 시각으로 착각한 것.

## 3. 시뮬레이션 설계도

![layout]({{ site.baseurl }}/assets/meep/01/01_layout.png)
*flux 실험(C)의 배치. 빨간 점 = Ez 점원(원점), 파란 사각형 = 반쪽 길이 2.5 µm의 flux box 네 면(법선은 바깥쪽), 녹색 빗금 = PML, 보라 × = 종료 조건 감시점. 동그라미 숫자는 §4의 코드 단계 번호다. ① 파라미터, ② 구조(없음: 진공), ③ source, ④ PML, ⑤ flux 면, ⑥ 종료 감시점, ⑦ 후처리는 그릴 것이 없다. 스냅샷 실험(A, B)은 PML 없는 12 × 8 µm 셀에 source를 (−2, 0)에 둔다.*

| 파라미터 | 값 | 왜 이 값인가 | 바꾸면 |
|----------|-----|-------------|--------|
| `wl` | 1.55 µm | 통신 파장. 시간 단위는 µm/c | 파면 간격이 바뀐다 |
| `fwidth` | 0.5 × fcen = 0.323 | 넓은 대역 = 짧은 펄스(약 2주기). 동심원이 겹치지 않고 또렷 | 좁히면 펄스가 길어져 고리가 뭉개진다 |
| `t0` | 5/fwidth = 15.5 | Meep 기본 cutoff 5 | fwidth가 정하므로 직접 고를 수 없다 |
| `RESOLUTION` | 20 px/µm | 파장당 31 px | 10이면 파면이 거칠어진다 |
| 스냅샷 셀, source | 12 × 8 µm, (−2, 0) | 가장 가까운 벽까지 4 µm | source를 벽에 붙이면 반사가 바로 섞인다 |
| 마지막 스냅샷 | t0 + 3.6 | 정점이 벽(4 µm)에 닿기 전 | 더 늦추면 정점의 반사가 보인다 |
| `line_len` | 3.0 µm | 약 2 파장. 지향성이 뚜렷해지는 길이 | 파장보다 짧으면 점원과 비슷 |
| flux 셀, `half` | 10 × 10 µm, 2.5 µm | box가 선원 끝(±1.5)과 PML(±4) 사이 | box가 선원에 닿으면 면이 source를 가른다 |

![source]({{ site.baseurl }}/assets/meep/01/00_source.png)
*source의 시간 파형(왼쪽)과 스펙트럼(오른쪽). width = 3.1, 정점 t0 = 15.5. 정점보다 2 × width = 6.2 앞선 약한 앞머리가 먼저 나간다. 이 앞머리는 t0 전에 이미 4 µm 벽에 닿는다. §5의 가장자리 잔무늬가 그것이다.*

**강의 노트북과의 차이**: 강의 week 2는 fwidth 0.18(긴 펄스)로 스냅샷만 본다. 이 글은 짧은 펄스로 고리를 또렷하게 하고, PML을 둔 flux box 실험(C)을 더해 방향 분포를 숫자로 만든다.

## 4. 코드 따라가기

> 읽는 순서: 단위·파라미터 → 재료·구조 → source → Simulation·경계 → monitor → 실행·종료 → 후처리.
> 이 글은 실험이 셋(A 스냅샷, B 점원 vs 선원, C flux box)이라 ④~⑦이 두 번 나온다.

### ① 단위와 파라미터 — 어떤 숫자를 고정하는가

```python
import numpy as np
import meep as mp

# 1 length unit = 1 um, c = 1: a wave travels 1 um per time unit, so time is in um/c.
wl = 1.55                     # wavelength [um]
fcen = 1 / wl                 # center frequency [1/um]
fwidth = 0.5 * fcen           # wide band -> short pulse (~2 periods): clean concentric rings
CUTOFF = 5.0                  # Meep default: GaussianSource peaks at t0 = CUTOFF / fwidth
t0 = CUTOFF / fwidth          # pulse peak time
RESOLUTION = 20               # pixels per um (31 px per wavelength)

sx_a, sy_a = 12.0, 8.0        # experiment A/B cell, no PML
src_a = mp.Vector3(-2.0, 0.0) # source off-center: nearest wall 4 um away
line_len = 3.0                # finite line source length [um]
d_wall = min(sx_a / 2 - abs(src_a.x), sy_a / 2 - abs(src_a.y))
```

- **무엇**: 파장과 대역폭을 정하고, 거기서 펄스 정점 시각 t0를 계산해 둔다.
- **왜**: `GaussianSource`는 t = 0에 켜지지 않는다. 포락선이 t0 = 5/fwidth에서 최대이고 그 앞뒤 2·width 동안 서서히 켜지고 꺼진다. 이 시각을 모르면 "언제 찍을지"를 정할 수 없다.
- **틀리면**: fwidth를 좁게 잡으면 width가 길어져 고리가 여러 겹 겹치고, t0도 늦어져 같은 `until`로는 source가 켜지기 전에 끝난다.

> **함정**: `until`이 작아 source가 켜지기 전에 멈추면 필드는 수치 잡음뿐이다. 그 상태에서 정규화해 그리면 화면 가득 무늬가 나온다. 계산이 틀린 게 아니라 시각이 틀린 것이다.

### ② 재료와 구조 — 무엇이 어디에 있는가

```python
geometry = []                 # nothing: an empty cell is vacuum (default_material = air)
```

- **무엇**: 구조가 없다. 빈 셀은 진공이다.
- **왜**: 이 글의 대상은 source 자체다. 구조가 있으면 반사·산란이 섞여 source가 무엇을 하는지 보이지 않는다.
- **틀리면**: `default_material`을 바꾸면 빈 셀이 그 재료로 채워진다. 파장이 n분의 1로 줄고 파면 반지름 예측 c(t − t0)도 c/n으로 바뀐다.

### ③ Source — 빛을 어떻게 넣는가

```python
def make_source(center, size=mp.Vector3(0, 0, 0)):
    """size (0,0,0) = point source; size (0, L, 0) = line source of length L along y."""
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center, size=size)]
```

- **무엇**: 한 점(또는 한 선)에서 Ez 성분으로 가우시안 펄스를 낸다.
- **왜**: `size`가 source의 종류를 정한다. 0이면 점원, 한 축만 길이를 주면 선원이다. 선원은 그 선 위의 모든 점이 같은 위상으로 진동한다.
- **틀리면**: `component`를 `Ex`나 `Ey`로 바꾸면 2D에서는 면내 편광(Hz 모드)이 되어 점원이라도 방향 의존성이 생긴다. 등방성 검증에는 Ez를 쓴다.

### ④ Simulation과 경계 — 계산 상자와 PML

```python
def make_sim(cell, sources, dpml=0.0, resolution=RESOLUTION):
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=[mp.PML(dpml)] if dpml > 0 else [], sources=sources)
```

- **무엇**: 셀 크기와 source, 그리고 PML 유무만 다른 `Simulation`.
- **왜**: 스냅샷 실험은 일부러 PML 없이 돌린다. 경계가 무엇을 하는지 보기 위해서다. flux 실험은 PML을 둔다. 되돌아온 파가 섞이면 네 면의 power가 source의 것이 아니게 된다.
- **틀리면**: PML 없이 오래 돌리면 파가 벽 사이를 수십 번 왕복해 정상파로 가득 찬다. 02편의 주제다.

### ⑤ Monitor — 무엇을 재는가 (flux box)

```python
half = 2.5
sides = {
    "+x": mp.FluxRegion(center=mp.Vector3(+half, 0), size=mp.Vector3(0, 2 * half)),
    "-x": mp.FluxRegion(center=mp.Vector3(-half, 0), size=mp.Vector3(0, 2 * half), weight=-1),
    "+y": mp.FluxRegion(center=mp.Vector3(0, +half), size=mp.Vector3(2 * half, 0)),
    "-y": mp.FluxRegion(center=mp.Vector3(0, -half), size=mp.Vector3(2 * half, 0), weight=-1),
}
mons = {k: sim.add_flux(fcen, 0, 1, reg) for k, reg in sides.items()}
```

- **무엇**: source를 둘러싼 정사각형의 네 변. 각 변을 지나는 Poynting flux를 중심 주파수 하나에서 누적한다.
- **왜**: Meep의 flux는 면의 양의 법선(+x 또는 +y) 방향이 양수다. 왼쪽과 아래 면은 바깥이 −x, −y이므로 `weight=-1`을 줘야 네 값이 모두 "밖으로 나가는 power"가 된다.
- **틀리면**: weight를 빼먹으면 −x 면 값이 음수가 되어 합이 0 근처로 떨어진다. box가 선원 끝에 닿으면 그 면이 source를 가로질러 값이 뒤틀린다.

### ⑥ 실행과 종료 조건 — 언제 멈추는가

```python
# A: snapshots. `until` counts from NOW, so pass the difference to the next target time.
prev = 0.0
for off in (0.0, 0.8, 1.6, 2.4, 3.2, 3.6):
    sim.run(until=(t0 + off) - prev)
    prev = t0 + off
    fields.append(sim.get_array(center=mp.Vector3(), size=mp.Vector3(sx_a, sy_a), component=mp.Ez))

# C: flux. run until the pulse has left through the PML.
sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(half + 0.8, 0), 1e-6))
```

- **무엇**: 스냅샷은 정점 t0부터 0.8씩 늘려 가며 멈추고 필드를 꺼낸다. flux는 펄스가 완전히 빠져나갈 때까지 돌린다.
- **왜**: `get_array`는 멈춘 그 순간의 필드다. 언제 멈추느냐가 그림의 전부를 정한다. `until`은 절대 시각이 아니라 "지금부터 얼마"라서 차이를 넘긴다.
- **틀리면**: `until=t0 + off`를 매번 넘기면 두 번째 스냅샷부터 시각이 두 배씩 늘어난다. flux를 고정 시간에 끊으면 펄스 꼬리가 빠져 합이 작아진다.

### ⑦ 후처리 — 숫자로 바꾸기

```python
p = {k: float(mp.get_fluxes(m)[0]) for k, m in mons.items()}
total = sum(p.values())
fractions = {k: v / total for k, v in p.items()}            # point: 0.25 each by symmetry

# is the peak on the predicted circle?  mean |Ez| on the ring vs. over the whole cell
rr = np.hypot(gx, gy)                                        # distance from the source on the grid
ring = np.abs(ez_last)[(rr > r_front - 0.4) & (rr < r_front + 0.4)].mean()
everywhere = np.abs(ez_last).mean()
```

- **무엇**: 네 면 power를 합으로 나눠 비율로 만들고, 마지막 스냅샷에서 예측 원 위의 평균 |Ez|를 셀 평균과 비교한다.
- **왜**: 비율로 만들면 source의 절대 세기(단위가 임의다)가 사라져 점원과 선원을 바로 비교할 수 있다. 원 위 평균이 셀 평균보다 뚜렷이 크면 정점이 예측 위치에 있는 것이다.
- **틀리면**: 합이 아니라 한 면으로 나누면 "비율"이 1을 넘는다. 원 두께(±0.4)를 파장보다 넓게 잡으면 고리 여러 개가 평균에 들어가 대비가 사라진다.

## 5. 결과

![snapshots]({{ site.baseurl }}/assets/meep/01/02_snapshots.png)
*PML 없는 12 × 8 µm 셀, 점원 (−2, 0). 펄스 정점 t0 = 15.5부터 0.8씩 뒤의 여섯 장, 색 범위는 공통. 정점 고리가 매 장 0.8 µm씩 커지고 멀어질수록 옅어진다(1/√r). 마지막 장의 점선 원이 예측 r = 3.6 µm다. 가장자리의 가는 잔무늬는 정점보다 6 µm 앞선 약한 앞머리가 벽에서 되돌아온 것이다.*

![point animation]({{ site.baseurl }}/assets/meep/01/05_anim_point.gif)
*점원, PML 없음, 12 × 12 µm 셀 중앙. 펄스가 켜지기 전(t0 − 2·width)부터 정점이 벽 근처에 닿기 직전까지. 동심원이 사방으로 같은 속도로 퍼진다.*

![line animation]({{ site.baseurl }}/assets/meep/01/05_anim_line.gif)
*같은 조건의 3 µm 선원. 선에 수직한 ±x로는 평면파에 가까운 파면이 나가고, 선 방향 ±y로는 거의 나가지 않으며, 양 끝에서 회절한 둥근 파면이 보인다.*

![point vs line]({{ site.baseurl }}/assets/meep/01/03_point_vs_line.png)
*같은 시각 t0 + 3.6의 점원(왼쪽)과 선원(오른쪽). 선원은 ±x 방향 진폭이 점원보다 크고 ±y 방향은 약하다.*

![flux box]({{ site.baseurl }}/assets/meep/01/04_flux_box.png)
*flux box 네 면의 power 비율. 점원은 네 면이 정확히 0.25. 3 µm 선원은 ±x 두 면이 0.459씩, ±y 두 면이 0.041씩이다.*

| 물리량 | 값 | 비교 대상 |
|--------|-----|-----------|
| 예측 원(r = 3.6 µm) 위 평균 \|Ez\| / 셀 평균 | 0.162 / 0.128 = 1.26 | 1보다 뚜렷이 크면 정점이 원 위 |
| 점원 네 면 비율 | 0.2500, 0.2500, 0.2500, 0.2500 | 등방 0.25 |
| 선원 ±x 두 면 합 | 0.919 | — |
| 선원 ±y 두 면 합 | 0.081 | — |

### 예측과 비교

| 물리량 | 내 예측 (§2) | 시뮬레이션 | 판정 |
|--------|-------------|-----------|------|
| 점원 파면 모양 | 동심원 | 동심원 (그림, GIF) | ✅ |
| t0 + 3.6에서 정점 반지름 | 3.6 µm | 원 위 평균이 셀 평균의 1.26배 | ✅ |
| 점원 box 네 면 비율 | 각 0.25 | 각 0.2500 | ✅ |
| 선원 ±x 비율 | 0.8 이상 | 0.919 | ✅ |
| PML 없는 셀 | 벽 반사가 보임 | 앞머리의 반사가 가장자리에 보임 | ✅ |

예측은 모두 맞았지만 한 가지는 예상보다 일찍 나타났다. "정점이 벽에 닿기 전"이라는 조건은 정점에만 해당하고, 정점보다 2·width 앞선 앞머리는 t0 전에 이미 벽에 닿아 있다. 짧은 펄스일수록 앞머리와 정점의 거리가 짧으니 넓은 대역을 고른 것이 그나마 도움이 됐다. 벽을 없애려면 PML이 필요하다.

### 수렴성

| resolution | dpml | 점원 max\|비율 − 0.25\| | 선원 ±x 합 | 비고 |
|---|---|---|---|---|
| 20 | 1.0 | 10⁻¹⁶ | 0.9188 | 기준 |
| 40 | 1.0 | 10⁻¹⁶ | 0.9182 | 해상도 2배 |
| 20 | 2.0 | 10⁻¹⁶ | 0.9188 | PML 2배 |

점원의 0.25는 격자 대칭이 만드는 값이라 해상도와 무관하게 정확하다. 선원의 지향성 0.919는 해상도와 PML 두께에 0.1% 안에서 둔감하다.

### 주장할 수 있는 것 / 없는 것

- 할 수 있는 것: 2D Ez 점원은 등방이고, 파면 정점은 c(t − t0)를 따른다. 2λ 길이의 균일 선원은 power의 92%를 선에 수직한 두 방향으로 보낸다.
- 할 수 없는 것: 먼 곳(far field)의 방사 패턴. box 면은 source에서 2.5 µm(1.6λ)뿐이라 근접장이다. 공식 antenna 예제는 near2far로 1000λ에서 등방성을 0.5% 안으로 확인하며, 08편에서 다룬다. 3D 점원(쌍극자)은 등방이 아니다.

## 6. 흔한 실수

| 증상 | 원인 | 고치는 법 |
|------|------|----------|
| 애니메이션이 처음부터 무늬로 가득 | `until`이 t0보다 작아 source가 켜지기 전에 끝남 + 정규화 | 녹화 구간을 t0 − 2·width부터로 |
| 동심원이 타원으로 보임 | `imshow(aspect="auto")` | `aspect="equal"` |
| 멀어져도 진폭이 안 줄어 보임 | 패널마다 따로 정규화 | 모든 패널에 같은 vmin/vmax |
| 두 번째 스냅샷부터 시각이 튐 | `until`에 절대 시각을 넘김 | 직전 시각과의 차이를 넘김 |
| 네 면 합이 0 근처 | −x, −y 면에 `weight=-1` 누락 | 바깥 법선 방향으로 weight |
| 오래 돌리면 화면이 정상파로 가득 | PML 없음 | `mp.PML(1.0)` (02편) |

## 7. 직접 해보기

| 바꿀 것 | 예상 변화 | 확인할 수치 |
|---------|----------|------------|
| `line_len` 3 → 1.0 µm (파장보다 짧게) | 지향성이 사라져 네 면이 비슷해짐 | ±x 합 |
| `line_len` 3 → 6 µm | ±x 비율 더 증가, 회절 끝이 상대적으로 작아짐 | ±x 합 |
| `fwidth` 0.323 → 0.18 (강의 값) | 펄스가 길어져 고리가 여러 겹, t0가 27.8로 늦어짐 | t0, 스냅샷 |
| `component` Ez → Hz | 면내 편광. 점원인데도 방향 의존성 등장 | 네 면 비율 |

## 8. 전체 코드

<details>
<summary>point_line_source.py (클릭해서 펼치기)</summary>
{% highlight python %}
"""Meep Example 01 - Point source and line source.

Three small experiments in an empty 2D cell:
  A. a point Ez source, no PML: snapshots after the pulse peak t0, before the first wall reflection,
     with the predicted wavefront radius c*(t - t0) drawn on top;
  B. point source vs a finite line source at the same instant;
  C. with PML: a flux box around each source measures how the power is split between the four
     sides (point: 25 % each; line: mostly +-x), and the four sides add up to the emitted power.

Run:  python point_line_source.py          (~40 s on one core)
Out:  00_source.png, 01_layout.png, 02_snapshots.png, 03_point_vs_line.png, 04_flux_box.png,
      05_anim_point.gif, 05_anim_line.gif, result.json   (-> ../assets/01/)
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
from blogfig import Label, animate_fields, annotated_layout, bar_figure, panel_grid, record_frames, source_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "01")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# 1 length unit = 1 um, c = 1: a wave travels 1 um per time unit, so time is in um/c.
wl = 1.55                     # wavelength [um]
fcen = 1 / wl                 # center frequency [1/um]
fwidth = 0.5 * fcen           # wide band -> short pulse (~2 periods): clean concentric rings
CUTOFF = 5.0                  # Meep default: GaussianSource peaks at t0 = CUTOFF / fwidth
t0 = CUTOFF / fwidth          # pulse peak time
RESOLUTION = 20               # pixels per um (31 px per wavelength)

# experiment A/B: no PML, source off-center so the nearest wall is 4 um away
sx_a, sy_a = 12.0, 8.0
src_a = mp.Vector3(-2.0, 0.0)
line_len = 3.0                # finite line source length [um] (about 2 wavelengths)
d_wall = min(sx_a / 2 - abs(src_a.x), sy_a / 2 - abs(src_a.y))   # 4 um: reflections return after t0 + 2*d_wall

# experiment C: with PML, source at the center, flux box of half-size `half` around it
sx_c = sy_c = 10.0
DPML = 1.0
half = 2.5


# ---------------------------------------------------------------- (2) materials & geometry
# nothing: an empty cell is vacuum (default_material = air). geometry = [] is the point of this post.

# ---------------------------------------------------------------- (3) source
def make_source(center, size=mp.Vector3(0, 0, 0)):
    """size (0,0,0) = point source; size (0, L, 0) = line source of length L along y."""
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center, size=size)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(cell, sources, dpml=0.0, resolution=RESOLUTION):
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=[mp.PML(dpml)] if dpml > 0 else [], sources=sources)


t_all = time.time()
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ A. snapshots before any reflection
offsets = [0.0, 0.8, 1.6, 2.4, 3.2, 3.6]          # time after the pulse peak; last one < d_wall
sim = make_sim((sx_a, sy_a), make_source(src_a))
fields, titles, prev = [], [], 0.0
for off in offsets:
    target = t0 + off
    sim.run(until=target - prev)                   # `until` counts from NOW, so pass the difference
    prev = target
    fields.append(sim.get_array(center=mp.Vector3(), size=mp.Vector3(sx_a, sy_a), component=mp.Ez))
    titles.append(f"t = {target:.1f}  (t0 + {off:.1f})")
extent_a = [-sx_a / 2, sx_a / 2, -sy_a / 2, sy_a / 2]
r_front = offsets[-1]                              # c = 1: the peak has travelled this far
panel_grid(fields, titles, extent_a, os.path.join(OUT, "02_snapshots.png"), marks=[(src_a.x, src_a.y)],
           circles={len(fields) - 1: (src_a.x, src_a.y, r_front, f"predicted r = {r_front:.1f} um")},
           suptitle="point source, no PML: wavefront after the pulse peak (one color scale)")

# does the field really sit on the predicted circle?  mean |Ez| on the ring vs. over the cell
ez_last = fields[-1]
gx, gy = np.meshgrid(np.linspace(-sx_a / 2, sx_a / 2, ez_last.shape[0]) - src_a.x,
                     np.linspace(-sy_a / 2, sy_a / 2, ez_last.shape[1]) - src_a.y, indexing="ij")
rr = np.hypot(gx, gy)
ring = np.abs(ez_last)[(rr > r_front - 0.4) & (rr < r_front + 0.4)].mean()
everywhere = np.abs(ez_last).mean()
print(f"A. t0 = {t0:.2f}; at t0 + {r_front}: mean |Ez| on the predicted ring = {ring:.4f}, cell mean = {everywhere:.4f} (ratio {ring/everywhere:.2f})")

# ================================================================ B. point vs line at the same instant
t_snap = t0 + 3.6
sim_line = make_sim((sx_a, sy_a), make_source(src_a, mp.Vector3(0, line_len, 0)))
sim_line.run(until=t_snap)
ez_line = sim_line.get_array(center=mp.Vector3(), size=mp.Vector3(sx_a, sy_a), component=mp.Ez)
panel_grid([ez_last, ez_line], ["point source", f"line source, length {line_len:g} um"], extent_a,
           os.path.join(OUT, "03_point_vs_line.png"), ncols=2, marks=[(src_a.x, src_a.y)],
           lines={1: ((src_a.x, src_a.y - line_len / 2), (src_a.x, src_a.y + line_len / 2))},
           suptitle=f"same instant t = t0 + 3.6, no PML")


# ================================================================ B'. animations: point and line source, no PML, until the first reflection
sq = 12.0                                           # square cell, source at the center: symmetric spreading
width = 1.0 / fwidth
for kind, size in (("point", mp.Vector3(0, 0, 0)), ("line", mp.Vector3(0, line_len, 0))):
    sim_anim = make_sim((sq, sq), make_source(mp.Vector3(0, 0), size))
    frames, times = record_frames(sim_anim, mp.Volume(center=mp.Vector3(), size=mp.Vector3(sq, sq)), mp.Ez,
                                  t_start=t0 - 2 * width, t_end=t0 + 0.9 * sq / 2, n_frames=45)
    marker = ([((0, -line_len / 2), (0, line_len / 2), "k", "line source")] if kind == "line" else None)
    animate_fields(frames, times, [-sq / 2, sq / 2, -sq / 2, sq / 2], os.path.join(OUT, f"05_anim_{kind}.gif"),
                   lines=marker, points=([(0, 0, "k", "point source")] if kind == "point" else None),
                   figsize=(5.2, 4.6), title=f"{kind} source, no PML")

# ================================================================ C. flux box: where does the power go?
def flux_split(size, resolution=RESOLUTION, dpml=DPML, layout=False):
    """Power through the four sides of a box around the source, as fractions of the total."""
    sim = make_sim((sx_c, sy_c), make_source(mp.Vector3(0, 0), size), dpml=dpml, resolution=resolution)
    # ------------------------------------------------------------ (5) monitors: four flux planes, outward normals
    sides = {
        "+x": mp.FluxRegion(center=mp.Vector3(+half, 0), size=mp.Vector3(0, 2 * half)),
        "-x": mp.FluxRegion(center=mp.Vector3(-half, 0), size=mp.Vector3(0, 2 * half), weight=-1),
        "+y": mp.FluxRegion(center=mp.Vector3(0, +half), size=mp.Vector3(2 * half, 0)),
        "-y": mp.FluxRegion(center=mp.Vector3(0, -half), size=mp.Vector3(2 * half, 0), weight=-1),
    }
    mons = {k: sim.add_flux(fcen, 0, 1, reg) for k, reg in sides.items()}
    decay_pt = (half + 0.8, 0)
    if layout:
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=dpml, figsize=(6.8, 6.4),
            title="experiment C: point source in vacuum, PML, four flux planes around it",
            params_text=f"wl={wl} um  fwidth={fwidth:.3f}\nres={resolution}/um  cell={sx_c:g}x{sy_c:g}  dpml={dpml:g}",
            params_xy=(-3.8, 3.75), decay_point=decay_pt, decay_text_xy=(2.0, -0.6),
            labels=[
                Label("geometry = []  (vacuum)", (-2.0, 2.0), (-3.5, 2.6), step=2, color="black"),
                Label("point source (Ez)", (0, 0), (-3.5, -1.6), step=3, color="red"),
                Label("flux planes, normals outward", (half, 1.0), (0.3, 1.9), step=5, color="blue"),
            ])
    # ------------------------------------------------------------ (6) run until the pulse has left
    sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
    # ------------------------------------------------------------ (7) post-processing
    p = {k: float(mp.get_fluxes(m)[0]) for k, m in mons.items()}
    total = sum(p.values())
    return {k: v / total for k, v in p.items()}, total


t_c = time.time()
frac_point, P_point = flux_split(mp.Vector3(0, 0, 0), layout=True)
frac_line, P_line = flux_split(mp.Vector3(0, line_len, 0))
print(f"C. point source: " + "  ".join(f"{k}={v:.4f}" for k, v in frac_point.items()) + f"  (total {P_point:.4g})")
print(f"C. line source : " + "  ".join(f"{k}={v:.4f}" for k, v in frac_line.items()) + f"  (total {P_line:.4g}, x-sides {frac_line['+x']+frac_line['-x']:.3f})")
bar_figure(list(frac_point), {"point source": list(frac_point.values()), f"line source ({line_len:g} um)": list(frac_line.values())},
           os.path.join(OUT, "04_flux_box.png"), ylabel="fraction of emitted power", reference=0.25, reference_label="isotropic: 0.25")

# convergence of the point-source split (should be 0.25 each by symmetry)
convergence = [{"resolution": RESOLUTION, "dpml": DPML, "max_dev_from_0.25": max(abs(v - 0.25) for v in frac_point.values()),
                "x_sides_line": frac_line["+x"] + frac_line["-x"]}]
for res, dpml in ((40, 1.0), (20, 2.0)):
    fp, _ = flux_split(mp.Vector3(0, 0, 0), resolution=res, dpml=dpml)
    fl, _ = flux_split(mp.Vector3(0, line_len, 0), resolution=res, dpml=dpml)
    convergence.append({"resolution": res, "dpml": dpml, "max_dev_from_0.25": max(abs(v - 0.25) for v in fp.values()),
                        "x_sides_line": fl["+x"] + fl["-x"]})
    print(f"convergence res={res} dpml={dpml}: point max|frac-0.25|={convergence[-1]['max_dev_from_0.25']:.2e}, line x-sides={convergence[-1]['x_sides_line']:.4f}")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"t0": t0, "fwidth": fwidth, "d_wall": d_wall, "r_front": r_front,
                   "ring_mean_abs_ez": ring, "cell_mean_abs_ez": everywhere,
                   "point_fractions": frac_point, "line_fractions": frac_line, "line_len": line_len,
                   "P_point": P_point, "P_line": P_line, "convergence": convergence,
                   "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
{% endhighlight %}
</details>

§4의 발췌 코드와 달리 전체 코드에는 그림 저장·GIF 녹화·result.json 기록이 들어 있다. 그림 helper `blogfig.py`(`panel_grid`, `bar_figure`, `record_frames`, `animate_fields` 등)는 시리즈 공통이며 같은 폴더(`code/`)에 있다. 전체 코드와 helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**실행 결과 (2026-10-23 실행)**:
```
A. t0 = 15.50; at t0 + 3.6: mean |Ez| on the predicted ring = 0.1618, cell mean = 0.1282 (ratio 1.26)
C. point source: +x=0.2500  -x=0.2500  +y=0.2500  -y=0.2500  (total 2.44)
C. line source : +x=0.4594  -x=0.4594  +y=0.0406  -y=0.0406  (total 3.594, x-sides 0.919)
convergence res=40 dpml=1.0: point max|frac-0.25|=1.11e-16, line x-sides=0.9182
convergence res=20 dpml=2.0: point max|frac-0.25|=1.94e-16, line x-sides=0.9188
```

**재현 환경**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · 실행 `python point_line_source.py` (약 21 s, 단일 코어)

## 확인 질문

1. fwidth를 반으로 줄이면 t0와 width는 각각 어떻게 되는가? 같은 셀에서 "정점이 벽에 닿기 전" 스냅샷을 찍을 수 있는 시간 여유는 늘어나는가, 줄어드는가?
2. 선원의 ±y 두 면에 8%가 남는다. 이 power는 선의 어디에서 나오는가?
3. 04편의 `EigenModeSource`도 결국 `size`가 있는 선원이다. 그런데 왜 한쪽으로만 빛이 나가는가?

## 9. 더 읽기

- [공식 Basics 튜토리얼: Fields in a Waveguide](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#fields-in-a-waveguide) (점원으로 시작하는 첫 예제)
- [공식 Antenna radiation pattern 예제](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-an-antenna) (점원 등방성, near2far)
- [`Source` / `GaussianSource` 레퍼런스](https://meep.readthedocs.io/en/latest/Python_User_Interface/#source) · [`FluxRegion` 레퍼런스](https://meep.readthedocs.io/en/latest/Python_User_Interface/#fluxregion)
- 다음 글: 02 · 경계 조건과 PML
