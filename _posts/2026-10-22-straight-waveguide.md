---
layout: post
date: 2026-10-22
title: "Meep Example 01 · Straight Waveguide — 넣은 빛이 전부 나오는가?"
title_en: "Meep Example 01 · Straight Waveguide — Does all the light come out?"
lang: ko
series: meep-examples
part: 1
level: beginner
runtime: "35 s (single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/"
tags: [meep, fdtd, waveguide, eigenmode, mode-decomposition]
image: /assets/meep/01/02_field.png
excerpt: "a 2D silicon strip waveguide (0.5 µm wide, SiO₂ cladding) with the fundamental TE mode injected at one end and measured at the other."
---
## TL;DR (English)

![hero]({{ site.baseurl }}/assets/meep/01/02_field.png)

- **What**: a 2D silicon strip waveguide (0.5 µm wide, SiO₂ cladding) with the fundamental TE mode injected at one end and measured at the other.
- **Result**: T = 1.0000, R = 8×10⁻⁶ at 1.55 µm. Everything that goes in comes out.
- **Takeaway**: start with a problem whose answer you already know. If T ≠ 1 here, your *measurement setup* is wrong, not your device.
- **Code**: full script at the bottom, ~35 s on one core.

## 0. 이 글에서 배우는 것

- `EigenModeSource`로 도파로의 기본 모드(fundamental mode)를 깨끗하게 주입하기
- mode monitor와 `get_eigenmode_coefficients`로 투과율(transmission)·반사율(reflection) 구하기
- 2D에서 TE 편광을 고르는 규칙 (`eig_parity=mp.ODD_Y`)
- 물리 교훈: 정답을 아는 문제로 측정 도구를 먼저 검증한다

**전제 지식**: 굴절률이 높은 곳에 빛이 갇힌다는 것(전반사). **다음 글**: [02 · 90° Waveguide Bend]({{ site.baseurl }}/waveguide-bend-90/)

## 1. 무엇을 알고 싶은가

실리콘 광도파로는 "빛의 전선"이다. 전선에 전류를 흘리면 반대쪽에서 거의 그대로 나오듯, 직선 도파로에 빛을 넣으면 반대쪽에서 전부 나와야 한다. 이 글은 그 당연한 사실을 Meep으로 확인한다. 정답(T = 1)을 이미 아는 문제를 일부러 고른 이유는, 빛을 넣는 도구(source)와 재는 도구(monitor)가 제대로 동작하는지를 **구조와 분리해서** 검증하기 위해서다. 여기서 1이 나오지 않으면 이후 어떤 구조를 시뮬레이션해도 결과를 믿을 수 없다.

## 2. 물리 한 페이지

core(실리콘, n = 3.48)가 cladding(SiO₂, n = 1.44)보다 굴절률이 높으면 빛은 전반사로 core 안에 갇혀 전파한다. 갇힌 빛의 형태를 모드(mode)라 부르고, 가장 단순한 모양이 기본 모드 TE0이다. 균일한 직선에는 반사를 일으킬 불연속이 없으므로 손실 없이 전달된다.

$$
T=\frac{|a^{+}_{\mathrm{out}}|^2}{|a^{+}_{\mathrm{in}}|^2},\qquad
R=\frac{|a^{-}_{\mathrm{in}}|^2}{|a^{+}_{\mathrm{in}}|^2},\qquad
T+R=1 \ (\text{lossless})
$$

| 기호 | 뜻 | 코드 변수 |
|------|----|-----------|
| $n_{\mathrm{core}}, n_{\mathrm{clad}}$ | core / cladding 굴절률 | `n_si`, `n_sio2` |
| $a^{+}_{\mathrm{in}}$ | 입력 monitor에서 앞으로 가는 TE0 진폭 | `ci.alpha[0, :, 0]` |
| $a^{-}_{\mathrm{in}}$ | 입력 monitor에서 뒤로 가는(반사) TE0 진폭 | `ci.alpha[0, :, 1]` |
| $a^{+}_{\mathrm{out}}$ | 출력 monitor에서 앞으로 가는 TE0 진폭 | `co.alpha[0, :, 0]` |

**가정과 유효 범위**: 2D(z 방향 무한), lossless 재료, 폭 0.5 µm에서 TE 단일 모드.

### 🎯 결과 보기 전에 맞춰보기

| 물리량 | 내 예측 | 근거 |
|--------|---------|------|
| T | 1.000 (오차 10⁻³ 이내) | 반사·산란을 일으킬 것이 없다 |
| R | ≪ 10⁻³ | 불연속 없음. 격자 이산화 잔차만 남는다 |
| 필드 모양 | core 안에서 폭을 유지하며 전파, 밖에서 급감 | guided mode의 정의 |

**판정 기준**: \|T − 1\| > 0.01 또는 R > 10⁻³이면 구조가 아니라 source/monitor 배치나 정규화를 의심한다.

## 3. 시뮬레이션 설계도

![layout]({{ site.baseurl }}/assets/meep/01/01_layout.png)
*무엇을 봐야 하는가: 검은 띠 = Si core(`geometry`, 양끝이 PML을 관통), 빨간 선 = `EigenModeSource`(x = −5), 파란 선 = mode monitor 두 개(x = −4 입력·반사, x = +5 투과), 녹색 빗금 = PML, 보라 × = 종료 조건이 감시하는 점(x = 5.5). 동그라미 숫자는 §4의 코드 단계 번호다. ① 파라미터 박스, ② 구조, ③ source, ④ PML, ⑤ monitor, ⑥ 종료 감시점이고, ⑦ 후처리는 그릴 것이 없다. source와 monitor는 core보다 넓은 3 µm 선이다.*

| 파라미터 | 값 | 왜 이 값인가 | 바꾸면 |
|----------|-----|-------------|--------|
| `wl` | 1.55 µm | 통신 표준 파장 | 모드 수·n_eff 변화 |
| `w_core` | 0.5 µm | 표준 strip, TE 단일 모드 | 넓히면 고차 모드 등장 |
| `resolution` | 50 px/µm | core 25 px, 매질 내 파장 22 px | 20 이하: T가 1에서 벗어남 |
| `dpml` | 1.0 µm | ≈ λ/1.5, 반사 억제 충분 | 얇으면 PML 반사로 R ↑ |
| `sx, sy` | 14 × 6 µm | source·monitor·PML 사이 간격 확보 | 좁히면 monitor가 PML에 닿음 |
| 선 폭 `cross` | 3.0 µm | core + 바깥으로 새는 꼬리(evanescent tail) 포함 | core 폭만 잡으면 T < 1 |

## 4. 코드 따라가기

> 읽는 순서: **단위·파라미터 → 재료·구조 → source → Simulation·경계 → monitor → 실행·종료 → 후처리**.
> Meep 스크립트는 거의 항상 이 7단계 순서다.

### ① 단위와 파라미터 — 어떤 숫자를 고정하는가

```python
import numpy as np
import meep as mp
import matplotlib.pyplot as plt

# Meep is unit-free. We choose 1 length unit = 1 um, so frequency = 1 / wavelength.
wl   = 1.55              # wavelength [um]
fcen = 1 / wl            # center frequency [1/um]
df   = 0.2 * fcen        # source bandwidth (Gaussian pulse)
nfreq = 11               # number of frequencies the monitors record

w_core = 0.5             # Si strip width [um]
n_si, n_sio2 = 3.48, 1.44

resolution = 50          # pixels per um  -> core = 25 px, lambda/n_si = 22 px
dpml = 1.0               # PML thickness [um]
sx, sy = 14.0, 6.0       # cell size [um], PML included
```

- **무엇**: 길이 단위(µm)를 정하고, 그 단위로 파장·주파수·구조 치수·격자 밀도를 고정한다.
- **왜**: Meep에는 단위가 없다. "1 = 1 µm"로 정하면 주파수는 1/µm가 되고, 1.55 µm 파장은 f = 0.645가 된다. 모든 숫자는 이 약속 위에 있다.
- **틀리면**: `resolution`이 낮으면 core가 몇 픽셀로만 표현되어 모드 형태가 왜곡되고 T가 1에서 벗어난다. `df`가 너무 좁으면 펄스가 길어져 실행 시간이 늘어난다.

> ⚠️ **초보 함정**: `fcen = 1.55`라고 쓰는 실수. Meep의 주파수는 파장의 역수다.

### ② 재료와 구조 — 무엇이 어디에 있는가

```python
geometry = [mp.Block(center=mp.Vector3(0, 0),
                     size=mp.Vector3(mp.inf, w_core),   # infinite in x: runs straight through the PML
                     material=mp.Medium(index=n_si))]
# background (cladding) is set later via default_material=SiO2
```

- **무엇**: 폭 0.5 µm, 길이 무한한 실리콘 띠 하나.
- **왜**: 길이를 `mp.inf`로 두면 도파로가 PML 안까지 이어진다. PML은 "계속 이어지는 구조"를 흡수할 때 반사가 가장 적다.
- **틀리면**: cell보다 짧게 두면 끝면에서 반사가 생겨 R이 커진다.

### ③ Source — 빛을 어떻게 넣는가

```python
cross = mp.Vector3(0, 3.0)   # a vertical line 3 um tall: wider than the core to include the evanescent tail

sources = [mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=df),
                              center=mp.Vector3(-5.0, 0), size=cross,
                              eig_band=1,               # 1-indexed: the fundamental mode
                              eig_parity=mp.ODD_Y)]     # 2D TE polarization (Ey, Hx, Hz)
```

- **무엇**: x = −5 위치의 세로선에서, 도파로의 기본 모드 모양으로 가우시안 펄스를 주입한다.
- **왜**: 점 source나 평면파를 넣으면 모드에 맞지 않는 성분이 함께 들어가 반사·방사 잡음을 만든다. `EigenModeSource`는 MPB로 모드를 먼저 풀어 그 모양대로 넣기 때문에 "순수한 TE0"이 들어간다.
- **틀리면**: `eig_parity`를 `EVEN_Y`로 두면 2D에서는 TM이 되어 전혀 다른 모드를 넣는다. `size`를 core 폭만큼만 잡으면 꼬리가 잘려 T < 1.

> ⚠️ **초보 함정**: `eig_band=0`은 없다. 1부터 센다.

### ④ Simulation과 경계 — 계산 상자와 PML

```python
sim = mp.Simulation(cell_size=mp.Vector3(sx, sy),
                    resolution=resolution,
                    boundary_layers=[mp.PML(dpml)],        # absorbing layer on all four sides
                    geometry=geometry,
                    sources=sources,
                    default_material=mp.Medium(index=n_sio2))

sim.plot2D()                       # ALWAYS look at the layout before running
plt.savefig("01_layout.png", dpi=150)
```

- **무엇**: 지금까지 만든 재료·구조·source를 14 × 6 µm 상자에 넣고, 네 변에 1 µm PML을 두른다.
- **왜**: PML(perfectly matched layer)은 상자 경계에 닿은 빛을 반사 없이 흡수해 "무한히 넓은 공간"을 흉내 낸다. `plot2D`는 §3 그림을 만든다. 실행 전에 반드시 눈으로 확인한다.
- **틀리면**: `boundary_layers`를 빼면 경계가 거울이 되어 빛이 되돌아오고 R이 커진다.

### ⑤ Monitor — 무엇을 재는가

```python
mon_in  = sim.add_mode_monitor(fcen, 0.1 * fcen, nfreq,
                               mp.ModeRegion(center=mp.Vector3(-4.0, 0), size=cross))
mon_out = sim.add_mode_monitor(fcen, 0.1 * fcen, nfreq,
                               mp.ModeRegion(center=mp.Vector3(+5.0, 0), size=cross))

# optional: steady-state field map of the whole non-PML region (for the figure in section 5)
dft = sim.add_dft_fields([mp.Ey], fcen, 0, 1,
                         where=mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2*dpml, sy - 2*dpml)))
```

- **무엇**: source 바로 뒤(x = −4)와 반대쪽 끝(x = +5)에 모드 분해용 monitor 두 개, 그리고 전체 영역의 정상상태 필드 저장.
- **왜**: 입력 monitor 하나로 "앞으로 가는 양"과 "뒤로 오는 양(반사)"을 동시에 분리할 수 있다. 그래서 reflection monitor를 source 앞이 아니라 **뒤**에 둔다.
- **틀리면**: monitor를 source와 같은 x에 두면 주입 중인 필드와 섞여 계수가 오염된다. PML 안에 두면 흡수된 값을 잰다.

### ⑥ 실행과 종료 조건 — 언제 멈추는가

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25,                     # check every 25 time units
            mp.Ey,                  # which field component to watch
            mp.Vector3(5.5, 0),     # where to watch: just past the output monitor
            1e-6))                  # stop when |Ey|^2 has decayed to 1e-6 of its peak
```

- **무엇**: source가 꺼진 뒤, 출력 monitor 근처의 필드가 최대값의 10⁻⁶으로 줄어들 때까지 돈다.
- **왜**: 펄스가 monitor를 완전히 지나가야 주파수 분해(DFT)가 정확하다. 고정 시간(`until=200`)은 구조가 바뀌면 틀릴 수 있어서 쓰지 않는다.
- **틀리면**: 너무 일찍 멈추면 monitor에 펄스 꼬리가 덜 들어와 T가 1보다 작게 나오고, 스펙트럼에 물결이 생긴다.

### ⑦ 후처리 — 숫자로 바꾸기

```python
ci = sim.get_eigenmode_coefficients(mon_in,  [1], eig_parity=mp.ODD_Y)
co = sim.get_eigenmode_coefficients(mon_out, [1], eig_parity=mp.ODD_Y)

p_in_fwd  = np.abs(ci.alpha[0, :, 0])**2    # forward power at the input monitor   (a_in+)
p_in_back = np.abs(ci.alpha[0, :, 1])**2    # backward power at the input monitor  (a_in-)
p_out_fwd = np.abs(co.alpha[0, :, 0])**2    # forward power at the output monitor  (a_out+)

T = p_out_fwd / p_in_fwd                    # section 2, first formula
R = p_in_back / p_in_fwd                    # section 2, second formula
ic = nfreq // 2                             # index of the center frequency
print(f"T = {T[ic]:.4f}, R = {R[ic]:.2e}, T+R = {T[ic]+R[ic]:.4f}")
```

- **무엇**: 두 monitor의 필드를 TE0 모드에 투영해 진폭 $a^{\pm}$를 얻고, §2의 식으로 T·R을 계산한다.
- **왜**: `alpha[band, freq, direction]`의 마지막 축이 0 = 앞, 1 = 뒤다. 입력 monitor의 "뒤" 성분이 곧 반사다.
- **틀리면**: `eig_parity`를 source와 다르게 주면 다른 모드에 투영되어 T가 엉뚱하게 나온다.

## 5. 결과

![field]({{ site.baseurl }}/assets/meep/01/02_field.png)
*무엇을 봐야 하는가: 가는 실선은 유전율 경계, 즉 Si core의 윤곽이다. 위 = Re(Ey) 파면. 줄무늬 간격이 매질 내 파장(≈ λ/n_eff)이다. 아래 = \|Ey\| 포락선. 윤곽선 안에만 밝고 밖에서 급감하면 잘 갇힌 것이다. x = −5 왼쪽이 어두운 것은 source가 오른쪽으로만 쏘기 때문이다.*

| 물리량 | 값 | 비교 대상 |
|--------|-----|-----------|
| T @ 1.55 µm | 1.0000 | 이론 1 |
| R @ 1.55 µm | 8.0 × 10⁻⁶ | 이론 0 |
| T + R | 1.0000 | 에너지 보존 |
| T (1.48–1.63 µm) | 0.99999–1.00001 | 대역 전체에서 평탄 |

### 예측과 비교

| 물리량 | 내 예측 (§2) | 시뮬레이션 | 판정 |
|--------|-------------|-----------|------|
| T | 1.000 ± 0.001 | 1.0000 | ✅ |
| R | ≪ 10⁻³ | 8 × 10⁻⁶ | ✅ |
| 필드 모양 | core 안에 갇힘 | 그림 확인 | ✅ |

불일치 없음. 균일 직선에는 반사원이 없으므로 맞을 수밖에 없고, 그래서 이 결과는 구조가 아니라 **source·monitor·PML·정규화 셋업이 옳다**는 증거로 쓴다.

**검증 체크**: T + R = 1.0000 · source(x = −5)와 monitor(x = −4, +5) 모두 PML(|x| > 6) 밖 · 종료는 field decay 기준.

## 6. 흔한 실수

| 증상 | 원인 | 고치는 법 |
|------|------|----------|
| T ≈ 0.9 이하 | source/monitor 선 폭이 core만큼만 | `cross`를 core보다 넓게 (여기선 3 µm) |
| T가 들쭉날쭉한 스펙트럼 | 종료가 너무 빠름 | `stop_when_fields_decayed` 임계값 낮추기 |
| 전혀 다른 모드 모양 | 2D에서 `EVEN_Y` 사용 | 2D TE는 `ODD_Y` |
| `eig_band=0` 오류 | 0-index로 착각 | 1부터 |
| R이 10⁻³ 이상 | PML 얇음 또는 구조가 PML 전에 끊김 | `dpml ≥ λ/2`, 길이 `mp.inf` |

## 7. 직접 해보기

| 바꿀 것 | 예상 변화 | 확인할 수치 |
|---------|----------|------------|
| `resolution` 50 → 20 | T가 1에서 조금 벗어남 | \|T − 1\| |
| `w_core` 0.5 → 1.2 µm | 고차 모드 등장, `eig_band=2`도 guided | MPB 모드 수 |
| `dpml` 1.0 → 0.2 µm | PML 반사로 R 증가 | R |

## 8. 전체 코드

<details>
<summary>straight_waveguide.py (클릭해서 펼치기)</summary>

```python
"""Meep Example 01 - Straight Waveguide.

2D silicon strip waveguide in SiO2. Inject the fundamental TE mode at one end,
measure transmission T and reflection R with mode monitors. Expected: T = 1, R = 0.

Run:  python straight_waveguide.py            (~25 s on one core)
Out:  01_layout.png, 02_field.png, result.json
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blogfig import Label, annotated_layout, field_figure   # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "01")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
# Meep is unit-free. We choose 1 length unit = 1 um, so frequency = 1 / wavelength.
wl   = 1.55              # wavelength [um]
fcen = 1 / wl            # center frequency [1/um]
df   = 0.2 * fcen        # source bandwidth (Gaussian pulse)
nfreq = 11               # number of frequencies the monitors record

w_core = 0.5             # Si strip width [um]
n_si, n_sio2 = 3.48, 1.44

resolution = 50          # pixels per um  -> core = 25 px, lambda/n_si = 22 px
dpml = 1.0               # PML thickness [um]
sx, sy = 14.0, 6.0       # cell size [um], PML included

# ---------------------------------------------------------------- (2) materials & geometry
geometry = [mp.Block(center=mp.Vector3(0, 0),
                     size=mp.Vector3(mp.inf, w_core),   # infinite in x: runs straight through the PML
                     material=mp.Medium(index=n_si))]
# background (cladding) is set below via default_material = SiO2

# ---------------------------------------------------------------- (3) source
cross = mp.Vector3(0, 3.0)   # a vertical line 3 um tall: wider than the core to include the evanescent tail
src_x, mon_in_x, mon_out_x = -5.0, -4.0, +5.0

sources = [mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=df),
                              center=mp.Vector3(src_x, 0), size=cross,
                              eig_band=1,               # 1-indexed: the fundamental mode
                              eig_parity=mp.ODD_Y)]     # 2D TE polarization (Ey, Hx, Hz)

# ---------------------------------------------------------------- (4) simulation & boundaries
sim = mp.Simulation(cell_size=mp.Vector3(sx, sy),
                    resolution=resolution,
                    boundary_layers=[mp.PML(dpml)],        # absorbing layer on all four sides
                    geometry=geometry,
                    sources=sources,
                    default_material=mp.Medium(index=n_sio2))

# ---------------------------------------------------------------- (5) monitors
mon_in  = sim.add_mode_monitor(fcen, 0.1 * fcen, nfreq,
                               mp.ModeRegion(center=mp.Vector3(mon_in_x, 0), size=cross))
mon_out = sim.add_mode_monitor(fcen, 0.1 * fcen, nfreq,
                               mp.ModeRegion(center=mp.Vector3(mon_out_x, 0), size=cross))

# ALWAYS look at the layout before running (drawn here so the mode monitors show up)
decay_pt = (mon_out_x + 0.5, 0)   # where stop_when_fields_decayed watches (step 6)
annotated_layout(
    sim, os.path.join(OUT, "01_layout.png"), dpml=dpml,
    title="2D Si strip waveguide (w = 0.5 um): TE0 EigenModeSource, mode monitors, PML",
    params_text=f"wl={wl} um  res={resolution}/um\ncell={sx}x{sy}  dpml={dpml}\nn_si={n_si}  n_sio2={n_sio2}",
    params_xy=(-2.2, 1.85), decay_point=decay_pt, decay_text_xy=(2.6, 1.0),
    labels=[
        Label("Si core (geometry)", (1.5, 0.0), (1.0, -1.2), step=2, color="black"),
        Label("EigenModeSource", (src_x, 1.3), (src_x + 1.2, 2.5), step=3, color="red"),
        Label("mode monitor: in / reflection", (mon_in_x, -1.3), (mon_in_x - 1.0, -2.5), step=5, color="blue"),
        Label("mode monitor: out", (mon_out_x, -1.3), (mon_out_x - 0.6, -2.5), step=5, color="blue"),
    ])

# steady-state field map of the whole non-PML region (for the figure in section 5)
nonpml = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx - 2 * dpml, sy - 2 * dpml))
dft = sim.add_dft_fields([mp.Ey], fcen, 0, 1, where=nonpml)

# ---------------------------------------------------------------- (6) run & stop condition
t0 = time.time()
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25,                         # check every 25 time units
            mp.Ey,                      # which field component to watch
            mp.Vector3(*decay_pt),      # where to watch: just past the output monitor
            1e-6))                      # stop when |Ey|^2 has decayed to 1e-6 of its peak
wall = time.time() - t0

# ---------------------------------------------------------------- (7) post-processing
ci = sim.get_eigenmode_coefficients(mon_in,  [1], eig_parity=mp.ODD_Y)
co = sim.get_eigenmode_coefficients(mon_out, [1], eig_parity=mp.ODD_Y)

p_in_fwd  = np.abs(ci.alpha[0, :, 0]) ** 2    # forward power at the input monitor   (a_in+)
p_in_back = np.abs(ci.alpha[0, :, 1]) ** 2    # backward power at the input monitor  (a_in-)
p_out_fwd = np.abs(co.alpha[0, :, 0]) ** 2    # forward power at the output monitor  (a_out+)

T = p_out_fwd / p_in_fwd                      # section 2, first formula
R = p_in_back / p_in_fwd                      # section 2, second formula
freqs = np.array(mp.get_flux_freqs(mon_in))
ic = nfreq // 2                               # index of the center frequency
print(f"T = {T[ic]:.6f}, R = {R[ic]:.2e}, T+R = {T[ic] + R[ic]:.6f}  (wall {wall:.1f} s)")
print(f"T over band {1/freqs.max():.3f}-{1/freqs.min():.3f} um: {T.min():.5f} .. {T.max():.5f}")

ey = sim.get_dft_array(dft, mp.Ey, 0)
eps = sim.get_array(vol=nonpml, component=mp.Dielectric)   # structure outline for the figure
extent = [-(sx / 2 - dpml), sx / 2 - dpml, -(sy / 2 - dpml), sy / 2 - dpml]
field_figure(ey, extent, os.path.join(OUT, "02_field.png"), core_halfwidth=None, wl=wl, eps=eps)

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"T": float(T[ic]), "R": float(R[ic]), "T_plus_R": float(T[ic] + R[ic]),
                   "T_band_min": float(T.min()), "T_band_max": float(T.max()),
                   "wavelengths_um": (1 / freqs).tolist(), "T_spectrum": T.tolist(),
                   "R_spectrum": R.tolist(), "wall_s": wall, "meep": mp.__version__},
                  f, indent=2)
```

</details>

§4의 발췌 코드와 달리 전체 코드에는 그림 저장·result.json 기록이 들어 있다. 그림 helper `blogfig.py`(`annotated_layout`, `field_figure`)는 시리즈 공통이며 같은 폴더(`code/`)에 있다. 전체 코드와 helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**실행 결과 (2026-10-23 재실행)**:
```
T = 1.000000, R = 8.04e-06, T+R = 1.000008  (wall 34.9 s)
T over band 1.476-1.632 um: 0.99999 .. 1.00001
```

**재현 환경**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · 실행 `python straight_waveguide.py` (약 35 s, 단일 코어)

## 9. 더 읽기

- 공식 Mode Decomposition 튜토리얼: https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/
- `EigenModeSource` 레퍼런스: https://meep.readthedocs.io/en/latest/Python_User_Interface/#eigenmodesource
- 다음 글: [02 · 90° Waveguide Bend — 직각으로 꺾으면 얼마나 새는가]({{ site.baseurl }}/waveguide-bend-90/)
