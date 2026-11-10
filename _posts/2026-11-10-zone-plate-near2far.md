---
layout: post
date: 2026-11-10
title: "Meep Example 16 · 꺼낸 빛을 모으기 — 원통좌표 near2far와 이진 위상 zone plate"
title_en: "Meep Example 16 · Collecting the extracted light — near-to-far field in cylindrical coordinates and a binary-phase zone plate"
lang: ko
series: meep-examples
part: 16
level: intermediate
runtime: "N 25: 23 s FDTD + far-field 점 1,500개 (≈ 4 min single core); N 100 ≈ 30 min"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/#focusing-properties-of-a-binary-phase-zone-plate"
tags: [meep, fdtd, near2far, zone-plate, cylindrical, diffractive-lens, focusing]
image: /assets/meep/16/02_results.png
excerpt: "a binary-phase glass zone plate (N = 25/50/100 zones, f = 200 µm, λ = 0.5 µm) on a glass substrate, illuminated from below by an x-polarized planewave written in cylindrical coordinates as m = −1 (Er − iEφ). The focal spot lies 200 µm outside the cell, so the fields there come from a near-to-far transformation (`add_near2far` + `get_farfields`) of the fields on the top and side faces of the cell."
---
## TL;DR (English)

![hero]({{ site.baseurl }}/assets/meep/16/02_results.png)

- **What**: a binary-phase glass zone plate (N = 25/50/100 zones, f = 200 µm, λ = 0.5 µm) on a glass substrate, illuminated from below by an x-polarized planewave written in cylindrical coordinates as m = −1 (Er − iEφ). The focal spot lies 200 µm outside the cell, so the fields there come from a near-to-far transformation (`add_near2far` + `get_farfields`) of the fields on the top and side faces of the cell.
- **Result**: the three documented curves come out as drawn — focus at z = 199.8–199.9 µm for all N, peak |E|² 4683 / 17403 / 64881 (ratios 3.7 and 13.9 versus N² = 4 and 16), first zero of the focal spot 1.204 / 0.901 / 0.701 µm versus the scalar 1.22·Δr_N = 1.261 / 0.907 / 0.667 µm (within 5 %), FWHM ratio N 100 / N 25 = 0.54 (1/√N → 0.5). Resolution 25 is converged (peak 2 %, FWHM 0.1 % from 25 to 50). Transmitted/incident net flux 0.99–1.00, but the far power integrated over a hemisphere with 1° steps is only 70–76 % of the near flux.
- **Takeaway**: near2far gives the field anywhere outside the cell from one run, but each far point costs an integral over the near surface — sampling matters twice: the far scan step for the focal profile, and the angular step if you integrate the far power. Here a 1° angular step misses the λ/D ≈ 0.15–0.3° fringes of a 100–200 µm aperture and under-counts the power by 25–30 %.
- **Code**: full script at the bottom; N 25 takes ~4 min on one core (the far-field points, not the FDTD, dominate).

## 0. 이 글에서 배우는 것

- 원통좌표에서 x 편광 평면파를 m = −1 하나로 쓰는 법(Er와 −iEφ)과 `is_integrated` 평면파 source
- `add_near2far`의 면을 어디에 두고(공기, PML 안쪽), `get_farfields`로 셀 밖 임의 선·면의 장을 얻는 법
- 영역판의 설계식 r_n² = nλ(f + nλ/4)와 분해능 1.22·Δr_N, 피크 세기 ∝ N²
- far-field 전력을 적분해 near flux와 맞춰 보는 에너지 수지 — 각 표본이 거칠면 어떻게 틀리는가

**전제 지식**: 13편의 원통좌표와 m, 10편의 near2far. **공식 예제**: [Focusing properties of a binary-phase zone plate](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/#focusing-properties-of-a-binary-phase-zone-plate), 스크립트 [zone_plate.py](https://github.com/NanoComp/meep/blob/master/python/examples/zone_plate.py). **이전 글**: 15 · 점광원이 수천 개일 때 · **다음 글**: 17 · 비스듬한 평면파 만들기

## 1. 무엇을 알고 싶은가

14편까지 빛은 구조 안에서 밖으로 나갔다. 나간 빛을 멀리서 한 점에 모으는 가장 단순한 소자가 영역판이다. 반지름을 λ/2 광로차마다 끊어 홀수 영역의 위상을 π 뒤집으면 모든 영역이 초점에서 더해진다. 질문은 둘이다. 셀이 6.5 µm 두께뿐인데 200 µm 밖의 초점을 Meep으로 볼 수 있는가(near2far), 그리고 영역 수 N을 네 배 늘리면 초점 폭이 반으로 주는가.

### 어디에 쓰이는가

X선·EUV 현미경의 대물렌즈가 영역판이고(굴절 렌즈가 없는 파장대), 가시광에서는 평판 회절 렌즈·metalens의 출발점이다. 바깥 영역 폭 Δr_N이 분해능을 정하므로 "얼마나 가늘게 깎을 수 있나"가 곧 성능이다.

| 응용 | 이 글의 어떤 것을 쓰는가 | 그 다음에 필요한 것 |
|---|---|---|
| X선 zone plate 현미경 | 초점 크기 1.22·Δr_N, 피크 ∝ N² | 효율(회절 차수 분배) |
| 평판 회절 렌즈·metalens | near2far 초점 프로파일, 셀 밖 PSF | 07편 meta-atom, metalens 주제 페이지 |
| LED·레이저 패키지 광학 | 꺼낸 빛의 far-field 분포 | 14편 광추출 |

## 2. 물리 한 페이지

n번째 영역 가장자리에서 초점까지의 거리가 f + nλ/2가 되게 하면

$$
r_n^2 = n\lambda\left(f + \frac{n\lambda}{4}\right),\qquad
\Delta r \approx 1.22\,\Delta r_N,\qquad I_{\mathrm{peak}} \propto N^2
$$

Δr_N = r_N − r_{N−1}은 가장 바깥 영역 폭이고 분해능(첫 영점 반지름)을 정한다. 유리(n 1.5) 0.5 µm는 광로차 0.25 µm = λ/2 → 홀수 영역의 π 위상. near2far는 셀 표면의 등가 전류(E, H)에서 자유 공간 Green 함수로 밖의 장을 적분한다. 원통좌표에서는 φ 적분이 더 들어가 점당 비용이 크고, far 점이 near 면에 가까울수록 느리다(문서).

| 기호 | 뜻 | 코드 변수 |
|---|---|---|
| N | 영역 수 | `num_zones` |
| f | 초점 거리 200 µm | `focal_length_um` |
| r_n | 영역 반지름 | `zone_radius_um` |
| Δr_N | 바깥 영역 폭 | `outer_zone_width` |

**가정과 유효 범위**: 원통좌표 m = −1(x 편광 평면파), 무손실 유리, 셀 밖은 진공, far 점은 φ = 0 평면(r–z).

### 결과 보기 전에 맞춰보기

| 물리량 | 내 예측 | 근거 |
|--------|---------|------|
| z 피크 위치 | 200 ± 1 µm | 설계식 |
| 피크 비 N 50/25, 100/25 | 4, 16 | ∝ N² |
| 첫 영점 r₀ | 1.26 / 0.91 / 0.67 µm | 1.22·Δr_N |
| 반구 far 전력 / near 윗면 flux | 1 ± 0.1 | 전력 보존 |
| 투과/입사 net flux | 1 ± 0.03 | 무손실 |

**판정 기준**: z 피크가 200에서 수 µm 벗어나거나 피크 비가 N²에서 2배 넘게 벗어나면 near 면 위치·m 부호를 의심한다.

## 3. 시뮬레이션 설계도

![layout]({{ site.baseurl }}/assets/meep/16/01_layout_source.png)
*(a) r ≤ 20 µm 구간: 유리 기판과 영역판(진한 파랑), 초록 점선 near2far·투과 flux 윗면, 빨강 평면파 source(기판 안), 주황 입사 flux 면, ▲ 종료 감시점(r 중앙 z 0). 셀 r은 R_N + 3 µm. (b) r 중앙 z 0의 Re Er(t). (c) 스펙트럼 — fwidth 0.2 f.*

| 항목 | 값 | 출처 | 비고 |
|---|---|---|---|
| 해상도 | 25 px/µm | 공식 예제 | 사다리 12.5/25/50 (N 25) |
| 셀 | r = R_N + 2 + 1, z = 1 + 2 + 0.5 + 2 + 1 | 공식 예제 | PML 1 전면 |
| 영역판 | N 25/50/100, 유리 1.5, 높이 0.5 | 공식 예제·문서 | |
| source | Er + (−i)Eφ Gaussian f 2 fwidth 0.4 is_integrated | 공식 예제 | 기판 안 |
| near2far | 윗면(z = size_z/2 − 1) + 옆면(공기) | 공식 예제 | |
| far 스캔 | r 0…size_r − 1 @ z f; z f ± 50 @ r 0; 간격 0.1 µm | 공식 예제 | |
| 추가 | 투과·입사 flux, 반구(R = f, 91점) 적분, DFT Er 지도 | 이 글 | 장 불변 |
| 종료 | decay(50, Er, (size_r/2, 0, 0), 1e-6) | 공식 예제 | |

**강의 노트북과의 차이**: 공식 노트북(2024-02)은 N 25만 돌리고 그림만 저장했다. 이 글은 N 세 값과 해상도 사다리, 수지 monitor를 더했다.

## 4. 코드 따라가기

### ① 파라미터 — 영역 반지름

```python
zone_radius_um = np.array([math.sqrt(n*wavelength_um*(focal_length_um + n*wavelength_um/4)) for n in range(1, num_zones+1)])
size_r_um = zone_radius_um[-1] + padding_um + pml_um
```
무엇: 설계식으로 N개 반지름을 만들고 셀 r 크기를 맨 바깥 영역에 맞춘다. 왜: 셀이 영역판보다 작으면 바깥 영역이 잘려 초점이 흐려진다. 틀리면: r_n² 대신 r_n을 쓰면 영역 간격이 일정해져 초점이 생기지 않는다.

### ② 구조 — 큰 원반부터 겹쳐 쌓기

```python
for n in range(num_zones-1, -1, -1):
    geometry.append(mp.Block(material=glass if n % 2 == 0 else mp.vacuum,
                             size=mp.Vector3(zone_radius_um[n], 0, height_um),
                             center=mp.Vector3(0.5*zone_radius_um[n], 0, z_lens)))
```
무엇: 반지름이 큰 원반부터 작은 원반 순으로 유리/진공을 번갈아 덮어 고리 패턴을 만든다. 왜: Meep은 나중 객체가 앞 객체를 덮으므로 고리를 따로 그리지 않아도 된다. 틀리면: 순서를 뒤집으면 가장 큰 원반 하나만 남는다.

### ③ Source — x 편광 평면파를 m = −1로

```python
sources = [mp.Source(mp.GaussianSource(f, fwidth=0.2*f, is_integrated=True), component=mp.Er, center=..., size=mp.Vector3(size_r_um)),
           mp.Source(mp.GaussianSource(f, fwidth=0.2*f, is_integrated=True), component=mp.Ep, ..., amplitude=-1j)]
```
무엇: Er와 −iEφ를 같은 진폭으로 넣으면 m = −1 원편광 평면파 하나가 되고, 선형 x 편광의 결과와 같다(13편). 왜: 원통좌표에서 평면파는 m = ±1 성분으로 쓰인다. 틀리면: Er만 넣으면 m = ±1이 섞여 φ 의존이 달라진다. `is_integrated`를 빼면 source 면이 PML에 닿는 가장자리에서 가짜 회절이 생긴다.

### ④ Simulation과 경계

```python
sim = mp.Simulation(cell_size=cell_size, boundary_layers=[mp.PML(1.0)], resolution=25, sources=sources,
                    geometry=geometry, dimensions=mp.CYLINDRICAL, m=-1)
```
무엇: 원통좌표, m = −1, PML 전면. 왜: 축(r = 0)은 경계가 아니라 해석적으로 처리되고 z 위아래는 기판과 공기로 열려 있다. 틀리면: m = 0으로 두면 Er 평면파가 정의되지 않는다.

### ⑤ Monitor — near2far 면은 공기 안

```python
n2f = sim.add_near2far(f, 0, 1,
    mp.Near2FarRegion(center=mp.Vector3(0.5*(size_r-pml), 0, z_top), size=mp.Vector3(size_r-pml, 0, 0)),
    mp.Near2FarRegion(center=mp.Vector3(size_r-pml, 0, z_top-0.5*(height+padding)), size=mp.Vector3(0, 0, height+padding)))
```
무엇: 윗면과 옆면 두 조각으로 영역판 위쪽을 감싼다. 왜: near2far는 균일 매질(여기선 공기) 안의 면에서만 정확하다 — 기판을 지나는 면은 안 된다. 틀리면: 면을 유리 안으로 내리면 far field가 수 배 틀린다.

### ⑥ 실행 — 장이 사라질 때까지

```python
sim.run(until_after_sources=mp.stop_when_fields_decayed(50.0, mp.Er, mp.Vector3(0.5*size_r, 0, 0), 1e-6))
```
무엇: 중앙 점의 Er가 최대의 1e-6까지 줄 때까지. 왜: near2far는 DFT 누적이라 펄스가 다 지나가야 한다. 틀리면: 일찍 끊으면 far field에 가짜 무늬가 생긴다.

### ⑦ 후처리 — 셀 밖 200 µm의 장

```python
ff_r = sim.get_farfields(n2f, 10, center=mp.Vector3(0.5*r_max, 0, z_f), size=mp.Vector3(r_max, 0, 0))
ff_z = sim.get_farfields(n2f, 10, center=mp.Vector3(0, 0, z_f), size=mp.Vector3(0, 0, 100))
I = |Ex|² + |Ey|² + |Ez|²
```
무엇: 초점면의 r 스캔과 축의 z 스캔을 0.1 µm 간격으로 받는다. 왜: 초점 폭이 1 µm쯤이라 0.1 µm면 FWHM을 잴 수 있다. 틀리면: 점 수가 비용이다(점당 0.1–0.9 s) — far 점이 near 면 가까이 가면 더 느려진다.

## 5. 결과

![results]({{ site.baseurl }}/assets/meep/16/02_results.png)
*(a) 축 위 z 스캔(r 0), N 25/50/100. (b) 초점면 r 스캔. ▽는 공식 문서 그림의 첫 영점을 눈으로 읽은 값. (c) 피크 |E|²와 첫 영점 r₀ vs N — 점선 N², 빨강 점선 1.22·Δr_N.*

![forward]({{ site.baseurl }}/assets/meep/16/03_forward_dft.png)
*(a) |Er| DFT @ λ 0.5(로그색, r ≤ 20): 영역판 뒤 회절. (b) N 25 z 스캔과 FWHM_z. (c) 에너지 수지: 투과/입사 net flux, 반구 far 전력 / near 윗면 flux.*

| N | z 피크 (µm) | 피크 \|E\|² | 피크 비 (N 25 기준) | 첫 영점 r₀ (µm) | 1.22·Δr_N (µm) | FWHM_r (µm) | 투과/입사 | 반구(91점)/near |
|---|---|---|---|---|---|---|---|---|
| 25 | 199.85 | 4683 | 1 | 1.204 | 1.261 | 1.052 | 0.996 | 0.758 |
| 50 | 199.85 | 17403 | 3.72 | 0.901 | 0.907 | 0.766 | 0.991 | 0.735 |
| 100 | 199.75 | 64881 | 13.9 | 0.701 | 0.667 | 0.564 | 0.990 | 0.697 |

문서 그림(눈읽기)의 피크 비는 3.4·14, 첫 영점은 1.3/0.9/0.65 µm다. r 스캔 간격이 0.1 µm라 r₀는 그 격자에 묶인다.

![animation]({{ site.baseurl }}/assets/meep/16/05_anim.gif)
*N 25, res 25: 평면파 펄스가 기판을 지나 영역판(r ≤ 20 µm 표시)을 통과하는 Re Er(r, z, t). 프레임 간격은 광 주기의 (n + 1/8)배. 아래 띠는 r 중앙 z 0의 Er.*

### 예측과 비교

| 물리량 | 내 예측 (§2) | 시뮬레이션 | 판정 |
|--------|-------------|-----------|------|
| z 피크 | 200 ± 1 | 199.75–199.85 | ✅ |
| 피크 비 50/25, 100/25 | 4, 16 | 3.72, 13.9 | ✅ (N²보다 7~13 % 낮음) |
| 첫 영점 r₀ | 1.26 / 0.91 / 0.67 | 1.204 / 0.901 / 0.701 (−4.5 / −0.7 / +5.1 %) | ✅ |
| 반구 far / near flux | 1 ± 0.1 | 0.76 / 0.73 / 0.70 | ❌ |
| 투과/입사 net flux | 1 ± 0.03 | 0.996 / 0.991 / 0.990 | ✅ |

다섯 예측 중 넷이 맞았다. 피크 비가 N²보다 조금 낮은 것은 바깥 영역일수록 입사각이 커져 효율이 떨어지고(NA 0.24 → 0.46) 유리 0.5 µm의 π 위상이 비스듬한 광선에는 정확히 π가 아니기 때문으로 본다 — 수치로 확인하진 않았다. 빗나간 것은 반구 적분이다. R = f = 200 µm의 반구를 θ 0~90°를 91점으로 나눠 적분하면 near 윗면 flux의 70~76 %만 나오고 N이 클수록 낮다. 구경 D ≈ 2R_N이 100~200 µm이면 far-field 각 무늬의 간격이 λ/D ≈ 0.14~0.29°라 1° 표본은 무늬를 몇 개씩 건너뛴다. res 12.5에서 0.96이 나온 것은 표본이 우연히 봉우리에 걸린 쪽이다. 같은 run을 θ 1801점(0.05°)으로 다시 적분하면 near flux의 1.025가 나와 표본 부족이 원인임이 확인된다. 투과/입사 net flux가 1에 가까운 것은 근거리 수지 자체는 맞다는 뜻이고, 틀린 것은 far 적분의 표본이다.

### 수렴성

| 변수 | 값 | 결과 | 비고 |
|---|---|---|---|
| 해상도 (N 25) | 12.5 / 25 / 50 | z 피크 199.45 / 199.85 / 199.95; 피크 3616 / 4683 / 4789; FWHM_r 1.047 / 1.052 / 1.054 | 25 → 50 피크 2.2 %, FWHM 0.1 % — res 25 수렴 |
| far 스캔 간격 | 0.1 µm (upstream) | r₀가 세 해상도에서 1.2043으로 같음 | 격자에 묶임. 분해능 비교엔 0.02 µm 이하 |
| 반구 θ 표본 | 91점 (1°) | far/near 0.70~0.76 | 1801점(0.05°) 진단: far/near 1.025 — 표본 문제 확인 |
| 실행 시간 | N 25 609 s, N 50 1439 s, N 100 3413 s (4 run 동시) | far 점당 1.5~3.7 s | 단독이면 0.1~0.5 s/점 |

### 주장할 수 있는 것 / 없는 것

- 할 수 있는 것: 현재 Meep(1.33)의 원통 near2far가 공식 zone plate 그림(N 25/50/100)을 그대로 재현하고, 초점 위치·크기·세기가 스칼라 이론(f, 1.22·Δr_N, N²)과 5 % 안에서 맞는다. upstream res 25는 수렴해 있다.
- 할 수 없는 것(등록 기준으로는): 91점 반구 적분의 전력 보존 — 진단(1801점)에서는 1.025로 맞는다. 해상도에 따른 r₀ 변화(far 격자에 묶임). 피크 비가 N²보다 낮은 이유(가설만).

## 6. 흔한 실수

| 증상 | 원인 | 고치는 법 |
|------|------|----------|
| far field가 수 배 틀림 | near2far 면이 유리 안 | 면을 공기(PML 안쪽)로 |
| 초점이 없음 | r_n 설계식 오타, 또는 원반 쌓는 순서 | r_n² 식, 큰 원반부터 |
| 반구 적분 전력이 near flux보다 작음 | θ 표본이 각 무늬(λ/D)보다 거침 | 표본 간격 < λ/(2D) |
| r = 0 열만 진함 / 그림 뒤집힘 | cyl get_array는 (z, r) 순서 | 전치하지 않는다 |
| 점당 수 초 | far 점이 near 면 근처, 또는 다른 run과 동시 실행 | 스캔 범위를 줄이거나 단독 실행 |
| source 가장자리 회절 | is_integrated 없음 | 켠다 |

## 7. 직접 해보기

| 바꿀 것 | 예상 변화 | 확인할 수치 |
|---------|----------|------------|
| N 200 | 피크 4배, r₀ 0.47 µm | 피크 비, r₀ |
| 높이 0.5 → 0.4 (위상 0.8π) | 피크 감소 | 피크 비 |
| far 간격 0.1 → 0.02 | FWHM 소수점 안정 | FWHM_r |
| 반구 θ 표본 91 → 1801 | 전력 비 → 1 | P_far/P_top |

## 8. 전체 코드

`code/zone_plate_near2far.py` — 인자 `--num-zones --resolution --far-res --hemi --anim`. PROJ-013 재현용 monitor(flux·반구·DFT·녹화)가 들어 있다.

<details>
<summary>zone_plate_near2far.py (클릭해서 펼치기)</summary>
{% highlight python %}
"""E 트랙 — Meep 공식 예제 zone_plate.py·.ipynb 재현 (Cylindrical_Coordinates.md "Focusing Properties of a Binary-Phase Zone Plate").
원본: NanoComp/meep python/examples/zone_plate.py @ upstream/COMMIT :10–164 그대로
(cyl m=−1, res 25, PML 1, 기판 유리 2(+PML), 홈 높이 0.5, padding 2, λ 0.5 fwidth 0.2 f, 평면파 Er + (−i)Eφ is_integrated(기판 안 z = −size_z/2 + pml),
N zones r_n² = nλ(f + nλ/4), f 200; near2far 면: 윗면 z = size_z/2 − pml(폭 size_r − pml) + 옆면; stop_when_fields_decayed(50, Er, (size_r/2, 0, 0), 1e-6);
far field r 스캔(z = f, 0…size_r−pml)·z 스캔(r 0, f ± 50) 간격 1/far_res).
더한 것(장 불변): 투과 flux 면(near2far 윗면과 같은 위치)·입사 flux(기판 안 source 위 z), 반구 far-field 적분 전력(수지), DFT Er 지도, source 점 파형, (--anim) 녹화, 피크·FWHM·첫 영점 후처리, 해상도 인자.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import meep as mp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_blog", "tools"))
ap = argparse.ArgumentParser()
ap.add_argument("--num-zones", type=int, default=25)
ap.add_argument("--resolution", type=float, default=25)
ap.add_argument("--far-res", type=float, default=10, help="far-field 스캔 점/µm (upstream 10)")
ap.add_argument("--scan-z", type=float, default=100)
ap.add_argument("--rscan-max", type=float, default=None, help="r 스캔 끝(기본 size_r − pml; 작게 주면 빠름)")
ap.add_argument("--hemi", type=int, default=0, help="반구 far-field 적분 점 수(0이면 생략), 반지름 = f")
ap.add_argument("--anim", action="store_true")
ap.add_argument("--tag", default="zp")
ap.add_argument("--out", required=True)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
resolution_um = a.resolution
pml_um, substrate_um, padding_um, height_um = 1.0, 2.0, 2.0, 0.5
focal_length_um, scan_length_z_um, farfield_resolution_um = 200, a.scan_z, a.far_res
wavelength_um = 0.5
frequency = 1 / wavelength_um
fwidth = 0.2 * frequency
num_zones = a.num_zones
zone_radius_um = np.array([math.sqrt(n * wavelength_um * (focal_length_um + n * wavelength_um / 4)) for n in range(1, num_zones + 1)])
size_r_um = zone_radius_um[-1] + padding_um + pml_um
size_z_um = pml_um + substrate_um + height_um + padding_um + pml_um
cell_size = mp.Vector3(size_r_um, 0, size_z_um)
src_z = -0.5 * size_z_um + pml_um
sources = [mp.Source(mp.GaussianSource(frequency, fwidth=fwidth, is_integrated=True), component=mp.Er, center=mp.Vector3(0.5 * size_r_um, 0, src_z), size=mp.Vector3(size_r_um)),
           mp.Source(mp.GaussianSource(frequency, fwidth=fwidth, is_integrated=True), component=mp.Ep, center=mp.Vector3(0.5 * size_r_um, 0, src_z), size=mp.Vector3(size_r_um), amplitude=-1j)]
glass = mp.Medium(index=1.5)
geometry = [mp.Block(material=glass, size=mp.Vector3(size_r_um, 0, pml_um + substrate_um), center=mp.Vector3(0.5 * size_r_um, 0, -0.5 * size_z_um + 0.5 * (pml_um + substrate_um)))]
z_lens = -0.5 * size_z_um + pml_um + substrate_um + 0.5 * height_um
for n in range(num_zones - 1, -1, -1):
    geometry.append(mp.Block(material=glass if n % 2 == 0 else mp.vacuum, size=mp.Vector3(zone_radius_um[n], 0, height_um), center=mp.Vector3(0.5 * zone_radius_um[n], 0, z_lens)))
sim = mp.Simulation(cell_size=cell_size, boundary_layers=[mp.PML(thickness=pml_um)], resolution=resolution_um, sources=sources, geometry=geometry, dimensions=mp.CYLINDRICAL, m=-1)
z_top = 0.5 * size_z_um - pml_um
n2f = sim.add_near2far(frequency, 0, 1, mp.Near2FarRegion(center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, z_top), size=mp.Vector3(size_r_um - pml_um, 0, 0)),
                       mp.Near2FarRegion(center=mp.Vector3(size_r_um - pml_um, 0, z_top - 0.5 * (height_um + padding_um)), size=mp.Vector3(0, 0, height_um + padding_um)))
# 추가 monitor: 투과 flux(윗면), 입사 flux(기판 안, source 위 0.5), DFT Er 지도
fl_top = sim.add_flux(frequency, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, z_top), size=mp.Vector3(size_r_um - pml_um, 0, 0)))
fl_inc = sim.add_flux(frequency, 0, 1, mp.FluxRegion(center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, src_z + 0.5), size=mp.Vector3(size_r_um - pml_um, 0, 0)))
dm = sim.add_dft_fields([mp.Er], [frequency], center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, 0), size=mp.Vector3(size_r_um - pml_um, 0, size_z_um - 2 * pml_um))
probe = mp.Vector3(0.5 * size_r_um, 0, 0)
tv = {"t": [], "v": []}


def rec_probe(s_):
    v = s_.get_field_point(mp.Er, probe)
    if mp.am_master():
        tv["t"].append(s_.meep_time()); tv["v"].append([float(np.real(v)), float(np.imag(v))])


steps = [mp.at_every(0.1, rec_probe)]
rec = None
if a.anim:
    from field_anim import Recorder
    rec = Recorder(sim, mp.Er, mp.Vector3(0.5 * (size_r_um - pml_um), 0, 0), mp.Vector3(min(size_r_um - pml_um, 20.0), 0, size_z_um - 2 * pml_um), dt=0.25, t_max=30.0, probe=probe, period=1 / frequency)
    steps += [rec.step, rec.pstep]
t1 = time.time()
sim.run(*steps, until_after_sources=mp.stop_when_fields_decayed(50.0, mp.Er, probe, 1e-6))
out = {"tag": a.tag, "num_zones": num_zones, "resolution": resolution_um, "far_res": farfield_resolution_um, "size_r": size_r_um, "size_z": size_z_um, "R_N": float(zone_radius_um[-1]), "outer_zone_width": float(zone_radius_um[-1] - zone_radius_um[-2]),
       "steps": int(round(sim.meep_time() / sim.fields.dt)), "t_end": sim.meep_time(), "wall_fdtd": time.time() - t1}
out["flux_top"] = float(mp.get_fluxes(fl_top)[0]); out["flux_inc"] = float(mp.get_fluxes(fl_inc)[0]); out["T_top_over_inc"] = out["flux_top"] / out["flux_inc"]
z_f = -0.5 * size_z_um + pml_um + substrate_um + height_um + focal_length_um
r_max = a.rscan_max if a.rscan_max else (size_r_um - pml_um)
t2 = time.time()
ff_r = sim.get_farfields(n2f, farfield_resolution_um, center=mp.Vector3(0.5 * r_max, 0, z_f), size=mp.Vector3(r_max, 0, 0))
ff_z = sim.get_farfields(n2f, farfield_resolution_um, center=mp.Vector3(0, 0, z_f), size=mp.Vector3(0, 0, scan_length_z_um))
out["wall_farfield"] = time.time() - t2
Ir = np.abs(ff_r["Ex"]) ** 2 + np.abs(ff_r["Ey"]) ** 2 + np.abs(ff_r["Ez"]) ** 2
Iz = np.abs(ff_z["Ex"]) ** 2 + np.abs(ff_z["Ey"]) ** 2 + np.abs(ff_z["Ez"]) ** 2
rr = np.linspace(0, r_max, Ir.size); zz = np.linspace(focal_length_um - 0.5 * scan_length_z_um, focal_length_um + 0.5 * scan_length_z_um, Iz.size)


def fwhm_first_zero(x, y):
    i0 = int(np.argmax(y)); half = y[i0] / 2
    j = i0
    while j + 1 < len(y) and y[j + 1] > half:
        j += 1
    xr = x[j] + (x[j + 1] - x[j]) * (y[j] - half) / (y[j] - y[j + 1]) if j + 1 < len(y) else x[-1]
    k = i0
    while k - 1 >= 0 and y[k - 1] > half:
        k -= 1
    xl = x[k] - (x[k] - x[k - 1]) * (y[k] - half) / (y[k] - y[k - 1]) if k - 1 >= 0 else x[0]
    m = i0
    while m + 1 < len(y) and y[m + 1] < y[m]:
        m += 1
    return float(xr - xl), float(x[m])


out["I_peak_r"] = float(Ir.max()); out["r_peak"] = float(rr[int(np.argmax(Ir))]); out["I_peak_z"] = float(Iz.max()); out["z_peak"] = float(zz[int(np.argmax(Iz))])
w_r, r_first_min = fwhm_first_zero(rr, Ir)
out["fwhm_r_half_profile"] = w_r; out["fwhm_r_full"] = 2 * (w_r if rr[int(np.argmax(Ir))] == 0 else w_r)   # r ≥ 0 반쪽 → 전체 폭 2×(반폭) (피크가 r=0일 때)
out["r_first_min"] = r_first_min
w_z, _ = fwhm_first_zero(zz, Iz); out["fwhm_z"] = w_z
if a.hemi:
    t3 = time.time()
    th = np.linspace(0, 0.5 * math.pi, a.hemi)
    Rh = focal_length_um
    P = 0.0; rows = []
    for t_ in th:
        pt = mp.Vector3(Rh * math.sin(t_), 0, z_f - focal_length_um + Rh * math.cos(t_))
        E = sim.get_farfield(n2f, pt)
        Ex, Ey, Ez, Hx, Hy, Hz = [E[i] for i in range(6)]
        Sx = np.real(Ey * np.conj(Hz) - Ez * np.conj(Hy)); Sz = np.real(Ex * np.conj(Hy) - Ey * np.conj(Hx))
        Sr = Sx * math.sin(t_) + Sz * math.cos(t_)
        rows.append([float(t_), float(Sr)])
    th_a = np.array([r_[0] for r_ in rows]); Sr_a = np.array([r_[1] for r_ in rows])
    P = float(np.trapezoid(Sr_a * 2 * math.pi * Rh**2 * np.sin(th_a), th_a))   # m = ±1 성분의 φ 평균은 축대칭 → φ 적분 = 2π (Sr은 φ 평균값)
    out["P_far_hemisphere"] = P; out["hemi_rows"] = rows; out["P_far_over_flux_top"] = P / out["flux_top"] if out["flux_top"] else None; out["wall_hemi"] = time.time() - t3
er = sim.get_dft_array(dm, mp.Er, 0)
eps = sim.get_array(component=mp.Dielectric, center=mp.Vector3(0.5 * (size_r_um - pml_um), 0, 0), size=mp.Vector3(size_r_um - pml_um, 0, size_z_um - 2 * pml_um))
if mp.am_master():
    out["probe"] = tv
    out["wall_total"] = time.time() - T0
    np.savez_compressed(os.path.join(a.out, a.tag + "_fields.npz"), er=er, eps=np.real(eps), extent=np.array([0, size_r_um - pml_um, -(size_z_um / 2 - pml_um), size_z_um / 2 - pml_um]), rr=rr, Ir=Ir, zz=zz, Iz=Iz)
    if rec is not None:
        pass
    json.dump(out, open(os.path.join(a.out, a.tag + ".json"), "w"), indent=1)
    print(f"RESULT N={num_zones} res={resolution_um:g} z_peak={out['z_peak']:.2f} I_peak_z={out['I_peak_z']:.1f} I_peak_r={out['I_peak_r']:.1f} fwhm_r_full={out['fwhm_r_full']:.3f} r_first_min={out['r_first_min']:.3f} fwhm_z={out['fwhm_z']:.2f} T={out['T_top_over_inc']:.4f} Pfar/Ptop={out.get('P_far_over_flux_top')} steps={out['steps']} wall={out['wall_total']:.0f}s", flush=True)
if rec is not None:
    rec.save(os.path.join(a.out, a.tag + "_anim.npz"), eps=True, meta=dict(title=f"zone plate N={num_zones} Er(r,z,t)", extent=[0, min(size_r_um - pml_um, 20.0), -(size_z_um / 2 - pml_um), size_z_um / 2 - pml_um], probe_label="r 중앙 z 0"))

{% endhighlight %}
</details>

## 확인 질문

1. 홀수 영역의 유리 두께 0.5 µm가 왜 π 위상인가? (§2)
2. near2far 면을 기판 안에 두면 안 되는 이유는? (§4 ⑤)
3. 반구 far 전력 적분이 near flux보다 작게 나왔다면 먼저 무엇을 의심하는가? (§5 수지, §6)

## 9. 더 읽기

- Meep 문서 [Cylindrical Coordinates — zone plate](https://meep.readthedocs.io/en/latest/Python_Tutorials/Cylindrical_Coordinates/#focusing-properties-of-a-binary-phase-zone-plate), [Near-to-far field spectra](https://meep.readthedocs.io/en/latest/Python_User_Interface/#near-to-far-field-spectra).
- LBL CXRO, [Zone plate theory](http://zoneplate.lbl.gov/theory) — Δr = 1.22 Δr_N.
- 이 글의 원 기록: PROJ-013 재현 보고서 e-zone-plate(사전 등록 기준 14개; 사람 확인 대기).
