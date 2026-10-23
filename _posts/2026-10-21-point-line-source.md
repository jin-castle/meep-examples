---
layout: lesson
permalink: /point-line-source/
lesson_title: "점과 선, 빛은 어떻게 퍼질까?"
lesson_summary: "광원의 모양만 바꾸면 빛이 퍼지는 방향도 달라질까? 파면을 먼저 관찰하고, 촬영 시각과 네 면의 power로 그 차이를 확인합니다."
lesson_goals:
  - "점원과 선원의 파면을 보고 빛이 강하게 나가는 방향을 설명한다."
  - "펄스 정점 시각 t0로부터 스냅샷의 파면 위치를 계산한다."
  - "flux box 네 면의 비율을 읽고 측정의 한계를 구분한다."
lesson_prerequisites: "파장과 파동의 속도를 알면 시작할 수 있습니다. 코드 실행에는 Meep와 Python 환경이 필요합니다."
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
<details markdown="1">
<summary>English summary</summary>

- **What**: a single Ez source in an empty 2D cell, first as a point, then as a 3 µm line. Snapshots after the pulse peak, and a box of four flux planes around the source.
- **Result**: the point source radiates exactly 25 % through each side of the box; the 3 µm line sends 92 % through the two sides facing it. The wavefront peak sits on the circle r = c (t − t0).
- **Takeaway**: in FDTD a picture is a time stamp. Know the pulse time t0 = 5/fwidth before you read any field, and derive the recording window from the source and the distances, not by guessing.
- **Code**: full script at the bottom, ~21 s on one core.

</details>

<h2 id="observe">1. 관찰 · 광원의 모양이 바꾸는 것</h2>

빈 공간에 빛을 넣는 **source(광원)** 하나만 둡니다. 왼쪽은 점 하나, 오른쪽은 세로로 놓인 길이 3 µm의 선입니다. 두 그림은 같은 시각에 찍었습니다. 색이 강한 부분이 어느 방향으로 뻗는지 먼저 살펴보세요.

<div class="figure-pair">
<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/01/03_point_vs_line.png" data-lightbox aria-label="점원 파면과 공통 색상 막대 원본 확대">
    <svg viewBox="0 90 460 370" role="img" aria-labelledby="point-field-title"><title id="point-field-title">점원에서 동심원 모양으로 퍼지는 실제 Re(Ez) 파면</title><image href="{{ site.baseurl }}/assets/meep/01/03_point_vs_line.png" width="1065" height="463" /></svg>
  </a>
  <figcaption>점원: 동심원 모양으로 퍼집니다.</figcaption>
</figure>
<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/01/03_point_vs_line.png" data-lightbox aria-label="선원 파면과 공통 색상 막대 원본 확대">
    <svg viewBox="460 90 460 370" role="img" aria-labelledby="line-field-title"><title id="line-field-title">세로 3 마이크로미터 선원에서 좌우로 더 강하게 퍼지는 실제 Re(Ez) 파면</title><image href="{{ site.baseurl }}/assets/meep/01/03_point_vs_line.png" width="1065" height="463" /></svg>
  </a>
  <figcaption>세로 선원: 좌우로 더 강하게 퍼집니다.</figcaption>
</figure>
</div>
<p class="lesson-figure-scale">두 그림은 같은 시각 t0 + 3.6, PML 없는 셀의 결과입니다. 색 범위는 Re(Ez) −1(빨강)부터 +1(파랑)까지 같습니다. 그림을 누르면 색상 막대를 포함한 원본을 볼 수 있습니다.</p>

<aside class="lesson-note" markdown="1">
**이 그림의 조건**은 진공의 2D Ez 시뮬레이션입니다. 여기서 점원은 화면에 수직한 z 방향으로 이어진 선전류의 단면입니다. 실제 3D 점광원·쌍극자의 방사 패턴과 구분해야 합니다.
</aside>

### 어디에 쓰이는가

점원과 선원은 소자가 아니라 모든 시뮬레이션의 입력이다. 어떤 source를 어디에 두느냐가 뒤의 모든 수치를 정하므로, 이 글의 세 실험은 그대로 다음 문제들의 첫 단계가 된다.

| 응용 | 이 글의 어떤 것을 쓰는가 | 그 다음에 필요한 것 |
|---|---|---|
| LED·OLED·양자점 발광층 모델 | 점원 = 발광 분자 하나(전기 쌍극자). 펄스 시각 t0와 방향 분포 | 10편의 3D 패턴, 11편의 LDOS |
| 안테나·RF 소자 | 점원의 방사 패턴, 선원의 방향성(배열 안테나의 가장 단순한 형태) | 10편의 near2far |
| 광섬유·격자 결합기의 입사 빔 | 선원 = 유한한 폭의 입사파. 파면이 평면에 가까워지는 조건 | 17편 평면파, 19편 Gaussian beam |
| 모든 flux 측정 | source를 둘러싼 flux box와 면의 방향 규칙 | 03편의 reference run |

<h2 id="predict">2. 예측 · 네 방향으로 똑같이 나갈까?</h2>

광원을 정사각형 상자로 둘러싸고 각 면을 통과하는 power를 잰다고 생각해 보세요. 세로 선원에서 나온 전체 power 중 **좌우 두 면(±x)을 지나는 몫**은 어느 쪽에 가까울까요?

<fieldset class="prediction">
  <legend>결과를 읽기 전에 하나를 골라보세요.</legend>
  <label><input type="radio" name="direction-prediction" value="equal"> 약 50% · 네 면으로 비슷하게 나간다</label>
  <label><input type="radio" name="direction-prediction" value="horizontal"> 80% 이상 · 선에 수직인 좌우로 더 많이 나간다</label>
  <label><input type="radio" name="direction-prediction" value="vertical"> 20% 이하 · 선을 따라 위아래로 더 많이 나간다</label>
</fieldset>

<details markdown="1">
<summary>예측의 근거 확인하기</summary>

선 위의 모든 점은 같은 위상으로 진동합니다. 선에 수직인 좌우 방향에서는 파동이 잘 보강되므로 **80% 이상**을 예상할 수 있습니다. 정확한 값은 뒤의 flux 측정에서 확인합니다. 점원이라면 대칭 때문에 네 면이 각각 25%이고 좌우 두 면의 합은 50%입니다.

</details>

<h2 id="understand">3. 원리 · 모양과 시각을 함께 읽기</h2>

<!-- concept-illustration:part-01:start -->

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/01/00_concept.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/01/00_concept.png" alt="점원의 동심원과 세로 선원의 좌우 파면 및 끝 회절을 비교하는 개념도. 생략한 z 방향은 무한히 이어진다." loading="lazy">
  </a>
  <figcaption>광원의 모양을 설명하는 개념도입니다. 선원 끝에서는 회절이 생겨 둥근 파면이 남습니다. 실제 flux 측정에는 아래 설계도의 PML과 상자를 사용합니다.</figcaption>
</figure>

<!-- concept-illustration:part-01:end -->

### 파면의 모양

2D Ez 점원의 빛은 원통파로 퍼집니다. 파면은 동심원이고 멀어질수록 진폭이 대략 1/√r로 줄어듭니다. 길이 L의 선원은 선 위의 점원들이 같은 위상으로 진동하는 경우입니다. L이 파장보다 길면 선에 수직한 ±x 방향에서는 보강되고, 선을 따른 ±y 방향에서는 서로 상쇄됩니다. 유한한 선의 양 끝에는 회절이 남습니다.

### 파면은 언제 출발했을까?

이 펄스는 시각 0에 가장 강하지 않습니다. **정점 시각 t0 = 5/fwidth = 15.5**를 먼저 계산해야 합니다. 진공에서 c = 1이므로 정점이 출발한 뒤 3.6 time unit이 지나면 정점 파면의 반지름은 3.6 µm입니다.

$$r_{\mathrm{peak}} = c\,(t-t_0)$$

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/01/00_source.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/01/00_source.png" alt="가우시안 광원의 시간 파형과 스펙트럼. 펄스 폭은 3.1, 정점 시각은 15.5다." loading="lazy">
  </a>
  <figcaption>펄스 폭은 3.1, 정점은 t0 = 15.5입니다. 정점보다 먼저 나간 약한 앞머리는 벽에 먼저 도착합니다.</figcaption>
</figure>

<aside class="lesson-note" markdown="1">
**정점이 벽에 닿기 전에도 반사는 보일 수 있습니다.** 정점보다 약 2 × width = 6.2 앞선 약한 앞머리가 먼저 벽에 도착하기 때문입니다. 파면 사진을 찍는 A/B 실험에는 PML이 없고, power를 재는 C 실험에는 PML이 있습니다.
</aside>

<details markdown="1">
<summary>수식과 기호를 더 자세히 보기</summary>

$$
E_z(r,t)\propto \frac{1}{\sqrt r}\,\cos\!\big(k r-\omega t\big),\qquad r_{\mathrm{peak}}(t)=c\,(t-t_0),\qquad
P_{+x}=P_{-x}=P_{+y}=P_{-y}=\tfrac14 P
$$

| 기호 | 뜻 | 코드 변수 |
|------|----|-----------|
| width | 펄스 포락선 폭 (시간) | `1 / fwidth` |
| $t_0$ | 펄스 정점 시각 = 5 × width | `t0 = CUTOFF / fwidth` |
| $r_{\mathrm{peak}}$ | 시각 t에 정점 파면이 있는 반지름 | `r_front = offsets[-1]` |
| $d_{\mathrm{wall}}$ | source에서 가장 가까운 벽까지 거리 | `d_wall` |
| $P_{\pm x}, P_{\pm y}$ | box 네 면을 바깥쪽으로 지나는 power | `mp.get_fluxes(mons["+x"])` 등 |

</details>

<h2 id="run">4. 실행 · 선의 길이 하나만 바꿔보기</h2>

먼저 원본 코드를 실행해 기준 결과를 얻습니다. 재현 환경은 **Meep 1.33.0 · Python 3.11**, 기록된 실행 시간은 단일 코어 약 21초입니다. [전체 코드와 공통 helper](https://github.com/jin-castle/meep-examples/blob/main/code)에서 `point_line_source.py`와 `blogfig.py`를 같은 폴더에 두세요. 아래의 [전체 코드](#reference)도 사용할 수 있습니다.

```bash
OMP_NUM_THREADS=1 python point_line_source.py
```

실행이 끝나면 `C. line source` 줄의 **x-sides**를 찾습니다. 원본의 값은 약 **0.919**입니다. 이어서 `line_len = 3.0`을 `line_len = 1.0`으로 바꾸고 다시 실행해 보세요. 파장 1.55 µm보다 짧은 선은 점원에 가까워지므로 좌우 비율이 줄어들 것으로 예상합니다. 두 값을 메모해 비교하면 됩니다. 변경한 실행의 수치는 직접 확인해야 합니다.

### 무엇을 측정하는가

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/01/01_layout.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/01/01_layout.png" alt="C 실험의 중앙 광원, 네 면 flux box, 외곽 PML, 필드 감쇠 감시점 배치." loading="lazy">
  </a>
  <figcaption>C 실험은 10 × 10 µm 셀의 중앙 광원을 네 면의 flux box로 둘러쌉니다. 상자의 반쪽 길이는 2.5 µm이고, 바깥 PML은 되돌아오는 파를 흡수합니다.</figcaption>
</figure>

네 면의 power를 모두 더한 뒤 각 면의 값을 그 합으로 나눕니다. 왼쪽(−x)과 아래(−y) 면은 **바깥쪽을 양수로 세기 위해 `weight=-1`**이 필요합니다. A/B의 파면 사진은 별도의 12 × 8 µm 셀, 광원 (−2, 0), PML 없음 조건입니다.

<details markdown="1">
<summary>설계 파라미터와 강의 예제의 차이</summary>

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

**강의 노트북과의 차이**: 강의 week 2는 fwidth 0.18(긴 펄스)로 스냅샷만 본다. 이 글은 짧은 펄스로 고리를 또렷하게 하고, PML을 둔 flux box 실험(C)을 더해 방향 분포를 숫자로 만든다.

</details>

<details markdown="1">
<summary>코드 따라가기 · 일곱 단계의 역할과 주의점</summary>

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

</details>

<h2 id="interpret">5. 해석 · 사진을 숫자로 확인하기</h2>

**선원의 좌우 두 면을 지나는 power는 전체의 약 92%입니다.** 점원은 네 면에 25%씩 나누어집니다. 처음 보았던 파면의 차이가 flux 측정에서도 드러납니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/01/04_flux_box.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/01/04_flux_box.png" alt="네 면의 power 비율. 점원은 면마다 0.25, 선원은 좌우 면마다 0.4594, 위아래 면마다 0.0406이다." loading="lazy">
  </a>
  <figcaption>선원은 좌우 두 면에 합계 0.919, 위아래 두 면에 0.081을 보냅니다. 유한한 선의 끝에서 생기는 회절 때문에 위아래의 값도 0이 아닙니다.</figcaption>
</figure>

<aside class="lesson-note" markdown="1">
**이 수치는 가까운 상자의 면별 power 비율입니다.** box는 광원에서 2.5 µm(약 1.6λ) 떨어져 있으므로 먼 곳의 방사 패턴을 측정한 것은 아닙니다. far field는 near2far가 필요합니다. 또한 2D Ez 점원의 대칭을 3D 쌍극자의 등방성으로 일반화할 수 없습니다.
</aside>

### 시간이 지나면 정점은 어디에 있을까?

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/01/02_snapshots.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/01/02_snapshots.png" alt="펄스 정점 t0부터 t0 + 3.6까지 점원 파면이 퍼지는 여섯 스냅샷. 마지막 점선 원의 반지름은 3.6 µm다." loading="lazy">
  </a>
  <figcaption>마지막 점선 원은 예측 반지름 3.6 µm입니다. 원 위 평균 |Ez|는 셀 평균의 1.26배입니다. 여섯 장은 공통 색 범위를 사용합니다.</figcaption>
</figure>

PML 없는 12 × 8 µm 셀에서 정점 파면은 커지며 옅어집니다. 가장자리의 잔무늬는 정점보다 먼저 나간 약한 앞머리가 벽에서 되돌아온 것입니다. 반사를 흡수하는 방법은 [02 · 경계 조건과 PML]({{ site.baseurl }}/boundary-pml/)에서 이어집니다.

<details markdown="1">
<summary>시간에 따른 변화를 애니메이션으로 보기</summary>

애니메이션은 위 스냅샷과 달리 **12 × 12 µm 셀 중앙**에 광원을 둡니다. PML 없이 t0 − 2·width부터 정점이 벽 근처에 닿기 전까지 기록했습니다. 재생 전에는 앞서 본 A/B의 정적 비교 그림을 보여줍니다. 그림 링크로 원본 GIF도 열 수 있습니다.

<div class="figure-pair">
  <figure class="lesson-figure lesson-animation">
    <a href="{{ site.baseurl }}/assets/meep/01/05_anim_point.gif" data-lightbox>
      <img src="{{ site.baseurl }}/assets/meep/01/02_snapshots.png" data-animation-src="{{ site.baseurl }}/assets/meep/01/05_anim_point.gif" data-static-src="{{ site.baseurl }}/assets/meep/01/02_snapshots.png" alt="점원 관찰. 정적 그림은 12 × 8 µm 셀의 여섯 스냅샷이며, 재생하면 12 × 12 µm 셀 중앙 점원의 동심원 파면을 보여준다." loading="lazy">
    </a>
    <button class="animation-toggle" type="button" hidden>애니메이션 재생</button>
    <figcaption>점원: 동심원이 모든 방향으로 퍼집니다. 정적 그림과 애니메이션은 셀 배치가 다릅니다.</figcaption>
  </figure>
  <figure class="lesson-figure lesson-animation">
    <a href="{{ site.baseurl }}/assets/meep/01/05_anim_line.gif" data-lightbox>
      <img src="{{ site.baseurl }}/assets/meep/01/03_point_vs_line.png" data-animation-src="{{ site.baseurl }}/assets/meep/01/05_anim_line.gif" data-static-src="{{ site.baseurl }}/assets/meep/01/03_point_vs_line.png" alt="선원 관찰. 정적 그림은 점원과 선원의 비교이며, 재생하면 12 × 12 µm 셀 중앙 3 µm 선원의 좌우 파면과 끝 회절을 보여준다." loading="lazy">
    </a>
    <button class="animation-toggle" type="button" hidden>애니메이션 재생</button>
    <figcaption>선원: 좌우로 강하게 나가는 파면과 끝 회절을 비교합니다. 정적 그림과 애니메이션은 셀 배치가 다릅니다.</figcaption>
  </figure>
</div>

</details>

<details markdown="1">
<summary>수치 비교와 수렴성 검증 기록</summary>

| 물리량 | 값 | 비교 대상 |
|--------|-----|-----------|
| 예측 원(r = 3.6 µm) 위 평균 \|Ez\| / 셀 평균 | 0.162 / 0.128 = 1.26 | 1보다 뚜렷이 크면 정점이 원 위 |
| 점원 네 면 비율 | 0.2500, 0.2500, 0.2500, 0.2500 | 등방 0.25 |
| 선원 ±x 두 면 합 | 0.919 | — |
| 선원 ±y 두 면 합 | 0.081 | — |

### 예측과 비교

| 물리량 | 물리적 예측 | 시뮬레이션 | 판정 |
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

</details>

<details markdown="1">
<summary>결과가 다를 때 · 흔한 실수 찾기</summary>

| 증상 | 원인 | 고치는 법 |
|------|------|----------|
| 애니메이션이 처음부터 무늬로 가득 | `until`이 t0보다 작아 source가 켜지기 전에 끝남 + 정규화 | 녹화 구간을 t0 − 2·width부터로 |
| 동심원이 타원으로 보임 | `imshow(aspect="auto")` | `aspect="equal"` |
| 멀어져도 진폭이 안 줄어 보임 | 패널마다 따로 정규화 | 모든 패널에 같은 vmin/vmax |
| 두 번째 스냅샷부터 시각이 튐 | `until`에 절대 시각을 넘김 | 직전 시각과의 차이를 넘김 |
| 네 면 합이 0 근처 | −x, −y 면에 `weight=-1` 누락 | 바깥 법선 방향으로 weight |
| 오래 돌리면 화면이 정상파로 가득 | PML 없음 | `mp.PML(1.0)` (02편) |

</details>

<h2 id="check">6. 확인 · 두 문장으로 설명해보기</h2>

1. fwidth를 반으로 줄이면 펄스 폭 width와 정점 시각 t0는 어떻게 달라질까요? 같은 시각에 찍은 두 그림을 바로 비교해도 될까요?
2. 세로 선원의 power가 좌우로 더 많이 나가는 이유는 무엇일까요? 위아래에도 약 8%가 남는 이유는 무엇일까요?

<details markdown="1">
<summary>내 설명과 비교하기</summary>

**1.** width = 1/fwidth와 t0 = 5/fwidth이므로 둘 다 두 배가 됩니다. 같은 절대 시각이어도 펄스의 진행 단계가 다릅니다. t − t0를 기준으로 읽어야 하며, 앞머리와 벽 반사가 섞이는지도 확인해야 합니다.

**2.** 같은 위상으로 진동하는 선 위의 점들이 좌우 방향에서 보강됩니다. 유한한 선의 양 끝에는 회절이 있어 위아래 방향에도 power가 남습니다.

</details>

이제 광원의 모양과 촬영 시각을 함께 읽을 수 있습니다. 다음에는 광원이 아니라 **상자의 경계**를 바꿔 반사가 어떻게 달라지는지 확인합니다: [02 · 경계 조건과 PML]({{ site.baseurl }}/boundary-pml/).

<h2 id="reference">7. 참고 · 전체 코드와 재현 기록</h2>

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

위의 코드 따라가기 발췌와 달리 전체 코드에는 그림 저장·GIF 녹화·result.json 기록이 들어 있습니다. 그림 helper `blogfig.py`(`panel_grid`, `bar_figure`, `record_frames`, `animate_fields` 등)는 시리즈 공통이며 같은 폴더(`code/`)에 있습니다. 전체 코드와 helper: [GitHub의 code 폴더](https://github.com/jin-castle/meep-examples/blob/main/code).

<details markdown="1">
<summary>기록된 실행 출력과 재현 환경</summary>

**실행 결과 (2026-10-23 실행)**:
```
A. t0 = 15.50; at t0 + 3.6: mean |Ez| on the predicted ring = 0.1618, cell mean = 0.1282 (ratio 1.26)
C. point source: +x=0.2500  -x=0.2500  +y=0.2500  -y=0.2500  (total 2.44)
C. line source : +x=0.4594  -x=0.4594  +y=0.0406  -y=0.0406  (total 3.594, x-sides 0.919)
convergence res=40 dpml=1.0: point max|frac-0.25|=1.11e-16, line x-sides=0.9182
convergence res=20 dpml=2.0: point max|frac-0.25|=1.94e-16, line x-sides=0.9188
```

**재현 환경**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · 실행 `python point_line_source.py` (약 21 s, 단일 코어)

</details>

### 더 읽기

- [공식 Basics 튜토리얼: Fields in a Waveguide](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#fields-in-a-waveguide) (점원으로 시작하는 첫 예제)
- [공식 Antenna radiation pattern 예제](https://meep.readthedocs.io/en/latest/Python_Tutorials/Near_to_Far_Field_Spectra/#radiation-pattern-of-an-antenna) (점원 등방성, near2far)
- [`Source` / `GaussianSource` 레퍼런스](https://meep.readthedocs.io/en/latest/Python_User_Interface/#source) · [`FluxRegion` 레퍼런스](https://meep.readthedocs.io/en/latest/Python_User_Interface/#fluxregion)
- 다음 글: [02 · 경계 조건과 PML]({{ site.baseurl }}/boundary-pml/)
