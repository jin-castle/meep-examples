---
layout: post
date: 2026-10-21
title: "Meep Example 02 · 경계 조건과 PML — 반사 경계, PML, Absorber를 같은 잣대로 재기"
title_en: "Meep Example 02 · Boundary conditions and PML — reflecting walls, PML and Absorber on one ruler"
lang: ko
series: meep-examples
part: 2
level: beginner
runtime: "10 s (single core)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Perfectly_Matched_Layer/"
tags: [meep, fdtd, pml, absorber, boundary]
image: /assets/meep/02/02_fieldmaps.png
excerpt: "the same point source in the same empty cell, three boundary treatments: Meep's default (a perfect reflector), `mp.PML`, and `mp.Absorber`. A padded reference run isolates what the boundary sends back."
---
## TL;DR (English)

![hero]({{ site.baseurl }}/assets/meep/02/02_fieldmaps.png)

- **What**: the same point source in the same empty cell, three boundary treatments: Meep's default (a perfect reflector), `mp.PML`, and `mp.Absorber`. A padded reference run isolates what the boundary sends back.
- **Result**: no layer reflects 100 % of the pulse; a 1 µm Absorber 1.9 %; a 1 µm PML 0.045 %. PML reflection drops steeply up to 0.5 µm and then floors near 4 × 10⁻⁴.
- **Takeaway**: the cell edge is a mirror unless you say otherwise. PML is not a material you add; it is a coordinate stretch that makes the edge look infinitely far away. Measure it by subtracting a run whose walls are too far to matter.
- **Code**: full script at the bottom, ~10 s on one core.

## 0. 이 글에서 배우는 것

- `boundary_layers=[]`가 무엇을 뜻하는지. Meep의 기본 경계는 완전 반사체다
- `mp.PML(d)`와 `mp.Absorber(d)`의 차이, 두께 d를 고르는 기준
- 경계 반사를 재는 두 가지 지표. 간단한 edge-band RMS와, 경계를 멀리 밀어낸 참조 run을 빼는 깨끗한 지표
- 참조 빼기(reference subtraction). 03편의 incident·scattered field 분리와 같은 기법이다

**전제 지식**: 01편의 source와 t0. **공식 문서**: [Perfectly Matched Layer](https://meep.readthedocs.io/en/latest/Perfectly_Matched_Layer/), [absorber-1d 예제](https://github.com/NanoComp/meep/blob/master/python/examples/absorber-1d.py). **이전 글**: [01 · Point source와 line source]({{ site.baseurl }}/point-line-source/) · **다음 글**: [03 · Reference run 빼기]({{ site.baseurl }}/reference-subtraction/)

## 1. 무엇을 알고 싶은가

01편의 스냅샷 가장자리에는 벽에서 되돌아온 잔무늬가 있었다. 그 벽을 없애는 것이 이 글의 주제다. 계산 상자는 유한한데 물리는 무한한 공간을 가정한다. Meep은 상자 가장자리에 흡수층을 두어 "나간 빛은 돌아오지 않는다"를 흉내 낸다. 흡수층이 없으면 무슨 일이 생기는지, PML과 Absorber는 얼마나 다른지, 두께는 얼마면 충분한지를 같은 source와 같은 시각에서 숫자로 비교한다.

## 2. 물리 한 페이지

<!-- concept-illustration:part-02:start -->

![같은 진공 셀에서 왼쪽은 흡수층 없이 경계에서 반사되는 파, 오른쪽은 사방 PML 안에서 감쇠하는 파를 비교한다.]({{ site.baseurl }}/assets/meep/02/00_concept.png)

*이 코드의 흡수층 없는 경계에서는 파가 되돌아옵니다. 같은 12 × 8 µm 진공 셀에서 네 변의 안쪽에 두께 1 µm PML을 두면 파가 흡수층을 지나며 감쇠합니다. 두 패널은 같은 위치의 Ez 점원과 같은 관측 시각을 비교합니다. PML은 실제 장치의 벽이나 센서가 아닌 계산용 흡수 영역입니다. 별도 B 실험의 장 RMS 반사 지표와 전력 반사율은 구분해야 합니다.*

<!-- concept-illustration:part-02:end -->


Meep의 기본 경계는 전기장이 0인 벽(완전 도체)이다. 파는 부호가 뒤집혀 전부 되돌아온다. PML(perfectly matched layer)은 흡수 재료가 아니라 좌표 변환이다. 층 안에서 좌표를 복소수로 늘려 파가 층에 들어가면서 반사 없이 지수적으로 줄게 만든다. 이론적으로는 입사각과 무관하게 반사가 0이고, 실제 반사는 격자 이산화와 유한 두께에서 온다. `mp.Absorber`는 그 대신 전도도를 서서히 키우는 보통 흡수 재료다. 반사가 0이 되는 조건이 없으므로 같은 두께에서 PML보다 더 되돌려 보낸다.

경계가 보낸 반사만 떼어 내려면 비교 대상이 필요하다. 경계를 PAD만큼 밀어낸 큰 셀을 같은 시각까지 돌리면, 안쪽 비교 영역에는 아직 아무것도 되돌아오지 않았다. 작은 셀과 큰 셀의 차이가 곧 경계의 반사다.

$$
R=\frac{\mathrm{rms}\big(E_{\mathrm{test}}-E_{\mathrm{ref}}\big)\big|_{t_B}}{\max_t \mathrm{rms}\big(E_{\mathrm{ref}}\big)},\qquad
t_B = t_0 + 1.5\,\frac{L}{2}\sqrt2
$$

| 기호 | 뜻 | 코드 변수 |
|------|----|-----------|
| $E_{\mathrm{test}}$ | 경계층을 둔 L × L 셀의 비교 영역 필드 | `test = crop(...)` |
| $E_{\mathrm{ref}}$ | 경계를 PAD = 6 µm 밀어낸 셀의 같은 영역 필드 | `ref` from `reference()` |
| $\max_t \mathrm{rms}(E_{\mathrm{ref}})$ | 펄스가 비교 영역을 지날 때의 최대 RMS (분모) | `peak` |
| $t_B$ | 정점이 셀 모서리까지 갔다 되돌아온 뒤의 시각 | `t_B` |
| edge RMS | 경계 1 µm 안쪽 띠의 \|Ez\| RMS (간단 지표) | `edge_rms(field)` |

**가정과 유효 범위**: 2D 진공, Ez 점원, 한 시각의 스냅샷 비교. 분모는 비교 시각의 참조 필드가 아니라 참조의 시간 최대값이다. 비교 시각에는 펄스가 이미 영역을 빠져나가 분모가 작아지기 때문이다.

### 결과 보기 전에 맞춰보기

| 물리량 | 내 예측 | 근거 |
|--------|---------|------|
| 경계층 없음의 R | 1에 가까움 | 완전 반사 |
| PML 1 µm의 R | 10⁻³ 이하 | 파장(1.55 µm)의 2/3 두께면 충분하다는 관례 |
| Absorber 1 µm vs PML 1 µm | Absorber가 10배 이상 나쁨 | 임피던스 정합 없음 |
| PML 두께를 늘리면 | 계속 줄다가 바닥에 닿음 | 두께 반사는 지수적으로 줄고, 이산화 반사가 남는다 |
| 해상도를 2배로 | PML R이 줄어듦 | 이산화 반사 감소 |

**판정 기준**: 경계층 없음의 R이 1에서 크게 벗어나면 참조 run의 PAD가 모자라 반사가 섞인 것. PML R이 두께에 따라 오르내리면 비교 영역이 PML과 겹친 것.

## 3. 시뮬레이션 설계도

![layout]({{ site.baseurl }}/assets/meep/02/01_layout.png)
*실험 A의 배치(PML 1 µm). 빨간 점 = Ez 점원(−2.5, 0), 녹색 빗금 = PML. 경계층 없음 case는 같은 셀에서 PML만 없다. 이 글에는 monitor가 없다. 비교하는 것은 필드 자체이고, ⑥ 종료 조건도 고정 시각이라 감시점이 없다. 동그라미 숫자는 §4의 단계 번호다.*

| 파라미터 | 값 | 왜 이 값인가 | 바꾸면 |
|----------|-----|-------------|--------|
| `fwidth` | 0.4 (width 2.5, t0 = 12.5) | 짧은 펄스라 파면 하나를 추적하고 비교 시각이 짧다 | 좁히면 t0와 비교 시각이 늦어진다 |
| `RESOLUTION` | 12 px/µm | 파장당 18 px. 강의 값. 10 s 안에 7 case | 24로 올리면 PML R 변화를 볼 수 있다(§5) |
| 실험 A 셀, source | 12 × 8 µm, (−2.5, 0) | 가장 먼 모서리 9.4 µm | source를 PML에 붙이면 PML이 근접장을 흡수해 결과가 왜곡 |
| `t_compare` | t0 + 1.5 × 9.4 = 26.6 | 정점이 모든 모서리에 닿고 되돌아온 뒤 | 더 이르면 반사가 아직 안 돌아옴 |
| 실험 B 내부 L, PAD | 8 µm, 6 µm | 참조 셀 20 µm. t_B = 21까지 반사가 비교 영역에 못 온다 | PAD를 줄이면 참조에 반사가 섞여 R이 과소 |
| 비교 영역 `HALF` | 3 µm (층에서 1 µm 안쪽) | 층을 내부 밖에 더하므로 영역이 층과 겹치지 않는다 | 겹치면 두꺼운 PML일수록 R이 커 보인다 |
| `Courant` | 0.5 | Meep 기본값. 강의와 같은 값으로 고정 | — |

![source]({{ site.baseurl }}/assets/meep/02/00_source.png)
*source의 시간 파형과 스펙트럼. width 2.5, 정점 t0 = 12.5. 짧은 펄스라 앞머리와 정점의 간격도 5 µm로 짧다.*

**강의 노트북과의 차이**: 강의 week 3은 edge RMS로 두께를 비교하고, 1주차의 numpy FDTD를 2D로 확장해 Mur 1차 흡수경계를 직접 구현해 PML과 비교한다(Mur 1.8 × 10⁻², PML 6.6 × 10⁻⁵). 이 글은 Meep 안에서 끝낸다. Mur 대신 Meep에 있는 `mp.Absorber`를 비교 대상으로 두고, 두께 sweep도 참조 빼기 지표로 한다. 처음 돌렸을 때 두꺼운 PML이 더 나쁘게 나왔다. 비교 영역이 PML과 겹쳤기 때문이고, 층을 내부 밖에 더하도록 고쳐서 해결했다.

## 4. 코드 따라가기

> 읽는 순서: 단위·파라미터 → 재료·구조 → source → Simulation·경계 → monitor → 실행·종료 → 후처리.
> 실험 A(필드 맵)와 B(참조 빼기)는 ④와 ⑦이 다르다. ⑤ monitor는 없다.

### ① 단위와 파라미터 — 어떤 숫자를 고정하는가

```python
wl = 1.55                     # wavelength [um]; 1 unit = 1 um, c = 1
fcen = 1 / wl
fwidth = 0.4                  # short pulse (width 2.5): a single wavefront is easy to follow
t0 = 5.0 / fwidth             # pulse peak (Meep cutoff = 5)
RESOLUTION = 12               # pixels per um (18 px per wavelength)

sx, sy = 12.0, 8.0            # experiment A cell
src = mp.Vector3(-2.5, 0.0)
corner = max(np.hypot(sx / 2 * ax - src.x, sy / 2 * ay - src.y) for ax in (-1, 1) for ay in (-1, 1))
t_compare = t0 + 1.5 * corner # the wavefront has reached every corner and (if reflected) come back

L, PAD, HALF = 8.0, 6.0, 3.0  # experiment B: interior, reference padding, compared half-size
t_B = t0 + 1.5 * (L / 2 * np.sqrt(2))
```

- **무엇**: 파장과 펄스, 두 실험의 셀 치수, 그리고 비교 시각 두 개를 source와 거리에서 유도한다.
- **왜**: 두 case를 "같은 시각"에 비교해야 지표가 의미를 가진다. 그 시각은 정점이 가장 먼 모서리까지 갔다 돌아올 만큼 뒤여야 한다. c = 1이니 거리가 곧 시간이다.
- **틀리면**: 비교 시각이 이르면 반사가 아직 안 돌아와 경계층 없음도 깨끗해 보인다. PAD가 L/2보다 작으면 참조에도 반사가 섞인다.

### ② 재료와 구조 — 무엇이 어디에 있는가

```python
geometry = []                 # vacuum. Only the boundary layer changes between runs
```

- **무엇**: 없다.
- **왜**: 경계만 비교하려면 경계 말고는 아무것도 바뀌면 안 된다.
- **틀리면**: 구조를 넣으면 구조의 반사와 경계의 반사가 섞여 어느 쪽인지 알 수 없다.

### ③ Source — 빛을 어떻게 넣는가

```python
def point_source(center):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center)]
```

- **무엇**: 01편과 같은 Ez 점원.
- **왜**: 점원은 사방으로 퍼지니 경계의 모든 각도를 한 번에 시험한다. 2D에서 Mur 같은 1차 흡수경계가 무너지는 이유가 이것이다.
- **틀리면**: 평면파 source로 바꾸면 수직 입사만 시험하게 되어 비스듬한 입사의 반사를 놓친다.

### ④ Simulation과 경계 — 계산 상자와 PML

```python
def make_sim(cell, layers, center=mp.Vector3(), resolution=RESOLUTION):
    """layers = [] (reflecting), [mp.PML(d)] or [mp.Absorber(d)]."""
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=layers, sources=point_source(center), Courant=0.5)

# experiment B: the layer is ADDED outside the fixed 8 x 8 interior
cell = L + 2 * d
```

- **무엇**: `boundary_layers`만 바꾸는 `Simulation`. 빈 리스트면 반사 경계, `mp.PML(d)` 또는 `mp.Absorber(d)`면 두께 d의 층이 셀 가장자리 안쪽에 생긴다.
- **왜**: PML은 셀을 키우지 않고 가장자리 d만큼을 흡수층으로 쓴다. 그래서 실험 B에서는 셀을 L + 2d로 키워 PML 없는 내부를 8 µm로 고정했다. 비교 영역이 층과 겹치면 안 된다.
- **틀리면**: 셀을 고정한 채 d를 키우면 비교 영역이 PML 안으로 들어가고, PML 안에서는 필드가 일부러 줄어들므로 "두꺼울수록 반사가 크다"는 거꾸로 된 결과가 나온다. 처음 실행에서 실제로 그랬다.

> **함정**: `mp.PML(d)`는 셀 바깥에 붙는 것이 아니라 셀 안쪽 d를 차지한다. 구조·source·monitor는 모두 PML 안쪽 경계에서 떨어져 있어야 한다.

### ⑤ Monitor — 무엇을 재는가

이 글에는 monitor가 없다. 비교 대상이 특정 시각의 필드 전체이기 때문이다. 대신 참조 run에서 비교 영역의 RMS 시간 최대값을 `mp.at_every(0.25, track)`로 기록해 분모로 쓴다.

```python
def track(s):
    a = s.get_array(center=mp.Vector3(), size=mp.Vector3(2 * HALF, 2 * HALF), component=mp.Ez)
    peak[0] = max(peak[0], rms(a))
sim.run(mp.at_every(0.25, track), until=t_B)
```

- **무엇**: 0.25 time unit마다 비교 영역의 RMS를 재서 최대값을 남긴다.
- **왜**: 반사를 "입사 최대값 대비"로 말하려면 펄스가 영역을 지나갈 때의 크기가 필요하다. 비교 시각의 값으로 나누면 펄스가 이미 빠져나간 뒤라 분모가 작아 비율이 부풀려진다.
- **틀리면**: `at_every` 간격이 펄스 폭(2.5)보다 길면 최대값을 놓친다.

### ⑥ 실행과 종료 조건 — 언제 멈추는가

```python
sim.run(until=t_compare)      # experiment A: both cases stop at the SAME absolute time
sim.run(until=t_B)            # experiment B: likewise
```

- **무엇**: 고정 시각에 멈춘다. 04편 이후의 `stop_when_fields_decayed`와 다르다.
- **왜**: 여기서는 "필드가 사라질 때까지"가 아니라 "경계 반사가 돌아온 직후"의 한 장면을 비교한다. 경계층 없는 case는 필드가 영원히 사라지지 않으므로 decay 조건을 쓸 수도 없다.
- **틀리면**: 두 case를 다른 시각에 찍으면 펄스 위치가 달라 비교가 안 된다.

### ⑦ 후처리 — 숫자로 바꾸기

```python
def edge_rms(field):                                   # experiment A: 1 um band along the edges
    band = (np.abs(x)[:, None] > sx / 2 - 1.0) | (np.abs(y)[None, :] > sy / 2 - 1.0)
    return float(np.sqrt(np.mean(np.abs(field[band]) ** 2)))

def reflection(layers, d=0.0, resolution=RESOLUTION): # experiment B: test - reference
    ref, peak = reference(resolution)
    sim = make_sim((L + 2 * d, L + 2 * d), layers, resolution=resolution)
    sim.run(until=t_B)
    test = crop(sim.get_array(..., component=mp.Ez), L + 2 * d)
    return rms(test - ref) / peak
```

- **무엇**: 실험 A는 가장자리 띠의 RMS 하나로, 실험 B는 (test − ref)의 RMS를 입사 최대값으로 나눈 비율로 요약한다.
- **왜**: edge RMS는 쉽지만 "경계가 돌려보낸 것"과 "아직 나가는 중인 것"을 구분하지 못한다. 참조 빼기는 나가는 펄스가 양쪽에 똑같이 있어 상쇄되고 반사만 남는다.
- **틀리면**: test와 ref의 격자가 어긋나면 빼기에서 펄스 자체가 남아 R이 커진다. 두 셀의 반쪽 길이가 격자 간격의 정수배여야 한다.

## 5. 결과

![fieldmaps]({{ site.baseurl }}/assets/meep/02/02_fieldmaps.png)
*실험 A. 같은 source, 같은 시각 t = 26.6. 왼쪽은 경계층 없음, 오른쪽은 PML 1 µm, 색 범위 공통. 점선 두 사각형 사이가 edge RMS를 재는 띠다. 왼쪽은 되돌아온 파가 셀을 채웠고 오른쪽은 비어 간다.*

![animation]({{ site.baseurl }}/assets/meep/02/05_anim_compare.gif)
*같은 두 case의 시간 전개. 펄스가 켜지기 전부터 가장 먼 모서리를 왕복할 때까지. 왼쪽은 벽에 닿는 순간 되돌아오고, 오른쪽은 PML에 들어가며 사라진다.*

![reflection]({{ site.baseurl }}/assets/meep/02/03_reflection.png)
*실험 B. 경계가 돌려보낸 RMS를 입사 최대 RMS로 나눈 값(로그 축). 경계층 없음 1.0, Absorber 1 µm 1.9 × 10⁻², PML 1 µm 4.5 × 10⁻⁴.*

![pml sweep]({{ site.baseurl }}/assets/meep/02/04_pml_sweep.png)
*PML 두께 sweep. 0.25 → 0.5 µm에서 20배 줄고, 1 µm부터는 4 × 10⁻⁴ 근처에서 더 내려가지 않는다. 빨간 점선이 Absorber 1 µm.*

| 지표 | 경계층 없음 | Absorber 1 µm | PML 1 µm |
|---|---|---|---|
| edge RMS (실험 A) | 0.122 | — | 0.0015 |
| R = 반사 / 입사 최대 (실험 B) | 1.03 | 1.9 × 10⁻² | 4.5 × 10⁻⁴ |

| PML 두께 | 0.25 µm | 0.5 µm | 1 µm | 1.5 µm | 2 µm |
|---|---|---|---|---|---|
| R | 1.5 × 10⁻² | 7.9 × 10⁻⁴ | 4.5 × 10⁻⁴ | 4.3 × 10⁻⁴ | 4.2 × 10⁻⁴ |

### 예측과 비교

| 물리량 | 내 예측 (§2) | 시뮬레이션 | 판정 |
|--------|-------------|-----------|------|
| 경계층 없음의 R | ≈ 1 | 1.03 | ✅ |
| PML 1 µm의 R | 10⁻³ 이하 | 4.5 × 10⁻⁴ | ✅ |
| Absorber vs PML (1 µm) | Absorber 10배 이상 나쁨 | 41배 | ✅ |
| 두께를 늘리면 | 줄다가 바닥 | 0.5 µm 이후 4 × 10⁻⁴에서 바닥 | ✅ |
| 해상도 2배 | PML R 감소 | 4.5 → 5.1 × 10⁻⁴, 거의 같음 | ❌ |

해상도를 올려도 PML의 바닥이 내려가지 않았다. 바닥이 이산화 반사라면 해상도에 따라 줄어야 한다. 그렇지 않았으니 이 바닥의 원인은 다른 데 있다. 후보는 두 가지다. PML이 근접장(source에서 3 µm, 2파장)의 소멸파 성분을 완전히 흡수하지 못하는 것, 그리고 test와 reference 셀의 격자가 정확히 같지 않아 빼기에 남는 수치 잔차. 둘을 가르려면 source를 PML에서 더 멀리 두고 다시 재야 한다. 아래 "주장할 수 없는 것"에 적는다.

### 수렴성

| resolution | 경계층 없음 | PML 1 µm | Absorber 1 µm |
|---|---|---|---|
| 12 | 1.03 | 4.5 × 10⁻⁴ | 1.86 × 10⁻² |
| 24 | 1.04 | 5.1 × 10⁻⁴ | 1.85 × 10⁻² |

세 값 모두 해상도에 둔감하다. 경계의 우열(1 : 0.02 : 0.0005)은 해상도 12로도 확정된다.

### 주장할 수 있는 것 / 없는 것

- 할 수 있는 것: Meep의 기본 경계는 완전 반사체다. 같은 두께에서 PML은 Absorber보다 40배 적게 돌려보낸다. 이 설정에서 PML은 0.5 µm(파장의 1/3)면 10⁻³ 아래로 내려가고 1 µm 이상은 더 얻을 것이 없다.
- 할 수 없는 것: PML R의 바닥 4 × 10⁻⁴가 어디서 오는지. 해상도 의존이 없으므로 이산화 반사만은 아니며, 근접장이나 격자 정렬 잔차일 수 있다. 다른 파장·재료·3D에서의 두께 기준. 구조가 PML을 관통할 때(04편 도파로)의 반사는 이 실험에 없다.

## 6. 흔한 실수

| 증상 | 원인 | 고치는 법 |
|------|------|----------|
| 오래 돌리면 화면이 정상파로 가득 | `boundary_layers=[]` | `mp.PML(...)` |
| PML을 두껍게 할수록 반사가 커짐 | 비교 영역 또는 monitor가 PML 안으로 들어감 | 셀을 키워 PML 없는 내부를 고정 |
| PML을 넣었는데 source 근처가 이상함 | source가 PML에 너무 가까움 | PML 안쪽 경계에서 파장의 절반 이상 띄우기 |
| 참조 빼기 R이 1보다 훨씬 작게 나옴(경계층 없음인데) | 비교 시각이 일러 반사가 아직 안 옴, 또는 PAD 부족 | t_B를 모서리 왕복 뒤로, PAD ≥ L/2 |
| 반사 비율이 1을 훌쩍 넘음 | 비교 시각의 참조 필드로 나눔 | 참조의 시간 최대 RMS로 나누기 |
| 도파로가 PML에서 반사 | 구조가 PML 전에 끊김 | 구조를 `mp.inf`로 PML 관통(04편) |

## 7. 직접 해보기

| 바꿀 것 | 예상 변화 | 확인할 수치 |
|---------|----------|------------|
| source를 PML에서 더 멀리 (L 8 → 12, PAD 유지) | 근접장 원인이면 바닥이 내려감 | PML 1 µm의 R |
| `Courant` 0.5 → 0.3 | 시간 이산화 변화. 바닥이 움직이는지 | PML R |
| `mp.Absorber` 두께 1 → 3 µm | Absorber는 두께로 보상 가능. PML 1 µm에 근접? | R |
| `fwidth` 0.4 → 0.15 (긴 펄스, 좁은 대역) | 단일 파장에 가까운 반사. 값이 달라지는지 | R |

## 8. 전체 코드

<details>
<summary>boundary_pml.py (클릭해서 펼치기)</summary>
{% highlight python %}
"""Meep Example 02 - Boundary conditions and PML.

Same point source, same cell, different boundary treatment.
  A. field maps at one instant: no absorbing layer (Meep's default = perfect reflector) vs PML 1 um,
     summarised by the RMS of Ez in a 1 um band along the edges.
  B. a clean reflection metric: a padded reference run whose boundaries are so far away that nothing
     comes back in time; whatever differs inside the compared region is reflection from the boundary.
       R = rms(E_test - E_ref) / max_t rms(E_ref)
     Cases: no layer, PML 0.25..2 um, Absorber 1 um; convergence in resolution.
  C. GIF: reflecting boundary vs PML, side by side.

Run:  python boundary_pml.py           (~2 min on one core)
Out:  00_source.png, 01_layout.png, 02_fieldmaps.png, 03_reflection.png, 04_pml_sweep.png,
      05_anim_compare.gif, result.json   (-> ../assets/02/)
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
from blogfig import (Label, animate_compare, annotated_layout, bar_figure, line_figure,   # noqa: E402
                     panel_grid, record_frames, source_figure)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "02")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- (1) units & parameters
wl = 1.55                     # wavelength [um]; 1 unit = 1 um, c = 1
fcen = 1 / wl
fwidth = 0.4                  # short pulse (width 2.5): a single wavefront is easy to follow
t0 = 5.0 / fwidth             # pulse peak (Meep cutoff = 5)
width = 1.0 / fwidth
RESOLUTION = 12               # pixels per um (18 px per wavelength); cheap, course value

# experiment A / C: rectangular cell, source off-center
sx, sy = 12.0, 8.0
src = mp.Vector3(-2.5, 0.0)
corner = max(np.hypot(sx / 2 * ax - src.x, sy / 2 * ay - src.y) for ax in (-1, 1) for ay in (-1, 1))
t_compare = t0 + 1.5 * corner # the wavefront has reached every corner and (if reflected) come back

# experiment B: the PML-free interior is always L x L; a layer of thickness d is ADDED outside it
# (cell = L + 2d), so the compared region |x|,|y| <= HALF never overlaps the layer.
# The reference domain is padded by PAD on each side: nothing reflected reaches the compared region by t_B.
L = 8.0
PAD = 6.0
HALF = L / 2 - 1.0            # compared region: |x|,|y| <= 3 um, 1 um inside the layer
t_B = t0 + 1.5 * (L / 2 * np.sqrt(2))

# ---------------------------------------------------------------- (2) materials & geometry
# none: vacuum. The only thing that changes between runs is the boundary layer.


# ---------------------------------------------------------------- (3) source
def point_source(center):
    return [mp.Source(mp.GaussianSource(fcen, fwidth=fwidth), component=mp.Ez, center=center)]


# ---------------------------------------------------------------- (4) simulation & boundaries
def make_sim(cell, layers, center=mp.Vector3(), resolution=RESOLUTION):
    """layers = [] (reflecting), [mp.PML(d)] or [mp.Absorber(d)]."""
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=layers, sources=point_source(center), Courant=0.5)


t_all = time.time()
source_figure(fcen, fwidth, os.path.join(OUT, "00_source.png"), wl_scale=1000.0, wl_unit="nm", time_unit="um/c")

# ================================================================ A. field maps at t_compare, edge-band RMS
def edge_rms(field):
    x = np.linspace(-sx / 2, sx / 2, field.shape[0], endpoint=False)
    y = np.linspace(-sy / 2, sy / 2, field.shape[1], endpoint=False)
    band = (np.abs(x)[:, None] > sx / 2 - 1.0) | (np.abs(y)[None, :] > sy / 2 - 1.0)
    return float(np.sqrt(np.mean(np.abs(field[band]) ** 2)))


maps, edges = {}, {}
for name, layers in (("no layer", []), ("PML 1 um", [mp.PML(1.0)])):
    sim = make_sim((sx, sy), layers, center=src)
    if name == "PML 1 um":
        annotated_layout(
            sim, os.path.join(OUT, "01_layout.png"), dpml=1.0, figsize=(7.4, 5.4),
            title="experiment A: point source, PML 1 um (the 'no layer' case is the same cell without PML)",
            params_text=f"wl={wl} um  fwidth={fwidth}\nres={RESOLUTION}/um  cell={sx:g}x{sy:g}  dpml=1.0",
            params_xy=(-4.6, 3.6), pml_xy=(1.5, -3.5),
            labels=[Label("geometry = []  (vacuum)", (1.0, 1.5), (0.0, 2.6), step=2, color="black"),
                    Label("point source (Ez)", (src.x, src.y), (-4.6, -1.6), step=3, color="red"),
                    Label("no monitor: the field itself is the result", (3.0, -0.3), (0.2, -1.8), step=5, color="blue")])
    sim.run(until=t_compare)                      # (6) the SAME absolute time for both cases
    maps[name] = sim.get_array(center=mp.Vector3(), size=mp.Vector3(sx, sy), component=mp.Ez)   # (7)
    edges[name] = edge_rms(maps[name])
extent_a = [-sx / 2, sx / 2, -sy / 2, sy / 2]
panel_grid([maps["no layer"], maps["PML 1 um"]],
           [f"no absorbing layer: edge RMS {edges['no layer']:.3f}", f"PML 1 um: edge RMS {edges['PML 1 um']:.4f}"],
           extent_a, os.path.join(OUT, "02_fieldmaps.png"), ncols=2, marks=[(src.x, src.y)],
           rects=[(-sx / 2, -sy / 2, sx, sy), (-sx / 2 + 1, -sy / 2 + 1, sx - 2, sy - 2)],
           suptitle=f"same source, same time t = {t_compare:.1f}: only the boundary differs")
print(f"A. t0 = {t0:.1f}, t_compare = {t_compare:.1f}; edge RMS no layer = {edges['no layer']:.4f}, PML 1 um = {edges['PML 1 um']:.4f} (ratio {edges['no layer']/edges['PML 1 um']:.1f})")


# ================================================================ B. padded reference: reflection = test - reference
def crop(field, size):
    """Central square |x|,|y| <= HALF of a field over a `size` x `size` cell."""
    n = field.shape[0]
    axis = (np.arange(n) + 0.5) / n * size - size / 2
    m = np.abs(axis) <= HALF
    return field[np.ix_(m, m)]


def rms(a):
    return float(np.sqrt(np.mean(np.abs(a) ** 2)))


_ref_cache = {}


def reference(resolution):
    """Big domain (L + 2 PAD): no reflection reaches the compared region before t_B. Also tracks the
    peak RMS inside that region over time, the denominator of the reflection metric."""
    if resolution in _ref_cache:
        return _ref_cache[resolution]
    big = L + 2 * PAD
    sim = make_sim((big, big), [], resolution=resolution)
    peak = [0.0]

    def track(s):
        a = s.get_array(center=mp.Vector3(), size=mp.Vector3(2 * HALF, 2 * HALF), component=mp.Ez)
        peak[0] = max(peak[0], rms(a))

    sim.run(mp.at_every(0.25, track), until=t_B)
    field = crop(sim.get_array(center=mp.Vector3(), size=mp.Vector3(big, big), component=mp.Ez), big)
    _ref_cache[resolution] = (field, peak[0])
    return _ref_cache[resolution]


def reflection(layers, d=0.0, resolution=RESOLUTION):
    """Reflection metric for a boundary layer of thickness d (0 = no layer, Meep's reflecting default)."""
    ref, peak = reference(resolution)
    cell = L + 2 * d
    sim = make_sim((cell, cell), layers, resolution=resolution)
    sim.run(until=t_B)
    test = crop(sim.get_array(center=mp.Vector3(), size=mp.Vector3(cell, cell), component=mp.Ez), cell)
    if test.shape != ref.shape:                   # grids of the two domains may differ by a pixel
        k = min(test.shape[0], ref.shape[0]); test, ref = test[:k, :k], ref[:k, :k]
    return rms(test - ref) / peak


cases = {"no layer": ([], 0.0), "Absorber 1 um": ([mp.Absorber(1.0)], 1.0)}
cases.update({f"PML {d:g} um": ([mp.PML(d)], d) for d in (0.25, 0.5, 1.0, 1.5, 2.0)})
R = {k: reflection(layers, d) for k, (layers, d) in cases.items()}
for k, v in R.items():
    print(f"B. {k:14s} reflection / peak incident = {v:.3e}")
bar_figure(["no layer", "Absorber 1 um", "PML 1 um"], {"reflected RMS / peak incident RMS": [R["no layer"], R["Absorber 1 um"], R["PML 1 um"]]},
           os.path.join(OUT, "03_reflection.png"), ylabel="reflected RMS / peak incident RMS", logy=True, fmt="{:.1e}")
thick = [0.25, 0.5, 1.0, 1.5, 2.0]
line_figure(thick, {"PML": [R[f"PML {t:g} um"] for t in thick]}, os.path.join(OUT, "04_pml_sweep.png"),
            xlabel="PML thickness [um]", ylabel="reflected RMS / peak incident RMS", logy=True,
            hline=R["Absorber 1 um"], hline_label="Absorber 1 um")

convergence = [{"resolution": RESOLUTION, "no layer": R["no layer"], "PML 1 um": R["PML 1 um"], "Absorber 1 um": R["Absorber 1 um"]}]
for res in (24,):
    row = {"resolution": res, "no layer": reflection([], 0.0, res), "PML 1 um": reflection([mp.PML(1.0)], 1.0, res),
           "Absorber 1 um": reflection([mp.Absorber(1.0)], 1.0, res)}
    convergence.append(row)
    print(f"convergence res={res}: " + "  ".join(f"{k}={v:.2e}" for k, v in row.items() if k != "resolution"))

# ================================================================ C. GIF: reflecting vs PML, side by side
vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(sx, sy))
sets, titles = [], []
for name, layers in (("no absorbing layer (reflecting)", []), ("PML 1 um", [mp.PML(1.0)])):
    s_anim = make_sim((sx, sy), layers, center=src)
    frames, times = record_frames(s_anim, vol, mp.Ez, t_start=t0 - 2 * width, t_end=t0 + 1.6 * corner, n_frames=60)
    sets.append(frames); titles.append(name)
animate_compare(sets, titles, times, extent_a, os.path.join(OUT, "05_anim_compare.gif"),
                points=[(src.x, src.y, "k", "source")], suptitle="same source and time")

if mp.am_master():
    with open(os.path.join(OUT, "result.json"), "w") as f:
        json.dump({"t0": t0, "t_compare": t_compare, "t_B": t_B, "edge_rms": edges, "reflection": R,
                   "convergence": convergence, "wall_s_total": time.time() - t_all, "meep": mp.__version__}, f, indent=2)
{% endhighlight %}
</details>

§4의 발췌 코드와 달리 전체 코드에는 그림 저장·GIF 녹화·result.json 기록이 들어 있다. 그림 helper `blogfig.py`(`panel_grid`, `bar_figure`, `line_figure`, `animate_compare` 등)는 시리즈 공통이며 같은 폴더(`code/`)에 있다. 전체 코드와 helper: [https://github.com/jin-castle/meep-examples/blob/main/code](https://github.com/jin-castle/meep-examples/blob/main/code).

**실행 결과 (2026-10-23 실행)**:
```
A. t0 = 12.5, t_compare = 26.6; edge RMS no layer = 0.1216, PML 1 um = 0.0015 (ratio 79.0)
B. no layer       reflection / peak incident = 1.031e+00
B. Absorber 1 um  reflection / peak incident = 1.861e-02
B. PML 0.25 um    reflection / peak incident = 1.496e-02
B. PML 0.5 um     reflection / peak incident = 7.926e-04
B. PML 1 um       reflection / peak incident = 4.508e-04
B. PML 1.5 um     reflection / peak incident = 4.271e-04
B. PML 2 um       reflection / peak incident = 4.220e-04
convergence res=24: no layer=1.04e+00  PML 1 um=5.09e-04  Absorber 1 um=1.85e-02
```

**재현 환경**: meep 1.33.0 · Python 3.11 · `conda install -c conda-forge pymeep` · 실행 `python boundary_pml.py` (약 10 s, 단일 코어)

## 확인 질문

1. edge RMS는 경계층 없음과 PML을 79배로 가르고, 참조 빼기는 2300배로 가른다. 왜 edge RMS가 훨씬 작은 차이를 내는가?
2. 실험 B에서 셀을 고정한 채 PML 두께를 키웠을 때 R이 커진 이유는? 그때 R은 무엇을 재고 있었는가?
3. 04편의 도파로는 PML을 관통한다. 관통하지 않고 PML 앞에서 끝나면 무엇이 반사되는가?

## 9. 더 읽기

- [공식 문서: Perfectly Matched Layer](https://meep.readthedocs.io/en/latest/Perfectly_Matched_Layer/) (PML의 원리와 한계, Absorber를 쓰는 경우)
- [공식 예제 absorber-1d.py](https://github.com/NanoComp/meep/blob/master/python/examples/absorber-1d.py) (PML과 Absorber를 같은 셀에서 교체)
- [`PML` / `Absorber` 레퍼런스](https://meep.readthedocs.io/en/latest/Python_User_Interface/#pml)
- 이전 글: [01 · Point source와 line source]({{ site.baseurl }}/point-line-source/) · 다음 글: [03 · Reference run 빼기]({{ site.baseurl }}/reference-subtraction/)
