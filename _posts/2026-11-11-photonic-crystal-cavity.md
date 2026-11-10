---
layout: lesson
lesson_title: "구멍을 뚫은 도파로는 어떻게 빛을 가둘까요?"
lesson_summary: "주기적인 구멍이 만든 부분 밴드 갭에 결함을 하나 넣습니다. 공진 투과 피크의 폭과 Harminv의 Q를 비교하고, 구멍 수·해상도·종료 조건에 따라 결과가 달라지는 이유를 확인합니다."
lesson_goals:
  - "주기 도파로의 부분 밴드 갭과 결함 공진 모드를 연결한다."
  - "기준 도파로로 정규화한 R·T·방사 수지와 공진 피크를 구한다."
  - "주파수 표본·시간 종료·해상도 검사를 구분하고, Q 포화의 해석 범위를 설명한다."
lesson_prerequisites: "03편 기준 계산 · 04편 도파로 모드 · 12편 Harminv와 Q · 17편 Bloch 위상"
date: 2026-11-11
title: "Meep Example 26 · 결함에 빛을 가두기 — 주기 도파로 밴드, 공진 투과, Q 검산"
title_en: "Meep Example 26 · Trapping light in a defect — waveguide bands, resonant transmission, and Q checks"
lang: ko
translation_key: photonic-crystal-cavity
series: meep-examples
part: 26
level: intermediate
runtime: "저장된 MPI 2 계산: N 3 Harminv 약 1–2초, 투과 약 19초(decay 1e−5); 다른 모드는 조건에 따라 다름"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Resonant_Modes_and_Transmission_in_a_Waveguide_Cavity/"
tags: [meep, fdtd, photonic-crystal, cavity, harminv, band-gap, transmission]
image: /assets/meep/26/results.png
excerpt: "구멍 도파로의 결함 모드와 좁은 투과 피크를 계산합니다. N 3의 Harminv Q 372.4와 선폭 Q 370.4를 맞추되, 문서의 높은 Q 포화값은 재현되지 않았음을 구분합니다."
---
<h2 id="observe">1. 관찰하기: 통과하지 못하는 대역에 좁은 길이 생깁니다</h2>

04편의 직선 도파로에 일정한 간격으로 구멍을 뚫으면 모든 주파수가 잘 지나갈까요? 구멍 사이 한 간격만 넓히면, 주변의 주기 구조가 진행을 막는 대역 안에 **빛이 머무는 결함 모드**가 생깁니다. 이 모드를 통해 좁은 주파수 범위의 빛이 다시 반대편으로 전달됩니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/26/results.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/26/results.png' | relative_url }}" alt="실제 계산의 주기 도파로 밴드, N 3 결함 공진 투과 피크, 구멍 수별 Q와 해상도별 공진 주파수" loading="eager"></a>
<figcaption>저장된 Meep 결과입니다. 위 왼쪽은 선택한 대칭의 주기 도파로 밴드, 위 오른쪽은 N = 3의 투과, 아래는 Q와 해상도 검사입니다. N은 한쪽 구멍 수이므로 N = 3은 구멍 여섯 개입니다. 주황 대역은 이 모델의 부분 유도모드 갭이며, 모든 편광·방향의 완전한 3D 밴드 갭이 아닙니다.</figcaption>
</figure>

<details markdown="1">
<summary>핵심 수치와 검증 범위</summary>

N = 3, res 20에서 Harminv는 f = 0.234454153 c/a, Q = 372.408을 줍니다. 촘촘한 투과 스펙트럼의 Lorentz 맞춤은 f₀ = 0.234450094, Q = 370.395로 Q 차이 0.541%입니다. 시간 종료를 decay 1e−3→1e−5로 엄격하게 바꾸면 R + T + S 범위는 0.8806–1.1479에서 0.99585–1.00799로 좋아집니다. 그러나 N = 14의 Q ≈ 6082(res 20), ≈ 6402(res 80)는 문서 본문의 약 8750과 일치하지 않습니다. 이 불일치를 해결했다고 주장하지 않습니다. 새 전자기장 계산 없이 저장된 장·JSON·로그를 사용합니다.

</details>

<h2 id="predict">2. 예측하기: 구멍을 늘리면 Q는 끝없이 커질까요?</h2>

<fieldset class="prediction">
<legend>결함 양쪽의 구멍 수 N을 늘릴 때 무엇을 예상하나요?</legend>
<label><input type="radio" name="photonic-crystal-cavity-prediction" value="radiation"> 포트로 새는 양이 줄어도 공기 쪽 방사가 남으면 Q 증가가 둔해질 수 있다.</label>
<label><input type="radio" name="photonic-crystal-cavity-prediction" value="infinite"> 주기 구조이므로 Q는 반드시 무한히 증가한다.</label>
<label><input type="radio" name="photonic-crystal-cavity-prediction" value="same"> 구멍 수는 바뀌어도 공진 수명에는 영향을 주지 않는다.</label>
</fieldset>

<details markdown="1">
<summary>예측의 근거</summary>

이 구조는 도파로 방향으로만 빛을 가둡니다. 옆 공기로 나가는 방사가 가능하므로 이상적인 모드에도 여러 누설 경로가 있습니다. 서로 독립적인 손실률로 표현하면 $1/Q=1/Q_{\rm port}+1/Q_{\rm rad}$입니다. N에 따른 Q 증가가 둔해지는 것은 이 설명과 맞지만, 유한 격자·PML·Harminv의 검사도 필요합니다. 포화값 하나만으로 물리적 방사 Q를 확정하지 않습니다.

</details>

<h2 id="understand">3. 원리 이해하기: 밴드 갭 → 결함 모드 → 공진 투과</h2>

{% include chapter-illustration.html %}

반복 간격 a를 길이 단위로 씁니다. ε = 13, 폭 1.2a의 도파로에서 공기 구멍 반지름은 0.36a입니다. 중앙에 가장 가까운 구멍 중심은 x = ±0.7a, 그 다음은 ±1.7a, ±2.7a입니다. 즉 중앙 한 간격만 d = 1.4a로 넓혔습니다. **N = 3은 양쪽 각각 세 개**이며 총 여섯 개입니다.

1. **주기 셀**: 길이 a의 셀과 x Bloch 위상을 써서 유도모드 밴드를 계산합니다. 선택한 Hz 대칭의 k = 0.5/a에서 두 경계 주파수는 0.199902와 0.304970 c/a입니다.
2. **결함 공진**: 유한한 구멍 배열 사이에 넓어진 간격을 넣습니다. 갭 안의 모드는 중앙에 집중되고 포트와 공기로 누설합니다.
3. **투과 실험**: 왼쪽에서 Ey 선원 펄스를 넣고 구멍 없는 도파로를 분모로 삼습니다. 공진 근처의 투과 피크가 수명과 연결됩니다.

$$
Q=\frac{f_0}{\Delta f_{\rm FWHM}},\qquad
T(f)\approx \frac{A}{1+4Q^2[(f-f_0)/f_0]^2}+C.
$$

이 Lorentz 모양은 저장된 좁은 피크의 맞춤 모형입니다. 비대칭 배경·여러 공진이 있으면 한 피크 모형을 그대로 쓰지 않습니다. Harminv는 source가 끝난 뒤 Hz의 감쇠에서 같은 공진의 주파수와 Q를 추정합니다.

| 계산 모드 | 셀·경계 | 광원·측정 |
|---|---|---|
| `bands` | 1a × 12a, y PML 1a, x Bloch | Hz 점원, k 21점, 각 점 Harminv 시간 300 |
| `harminv` | 길이 2(N+3)a + 0.4a, 높이 6a, 전면 PML 1a | 중앙 Hz 점원, x·y 거울 대칭, source 뒤 400 |
| `trans` | N = 3이면 12.4a × 6a, 전면 PML 1a | 왼쪽 Ey 선원, 기준 도파로와 결함 구조의 flux·Hz DFT |

투과 광원은 `EigenModeSource`가 아닙니다. 실제 source 검사의 기본 모드 전력/flux 비는 대역 전체에서 0.96971–0.99982입니다. 이 분모에 모든 주파수가 완벽하게 단일 모드로 입사했다고 가정하지 않습니다.

<h2 id="run">4. 실행하기: 밴드, 감쇠, 투과를 분리합니다</h2>

[Python 코드 다운로드]({{ '/code/photonic_crystal_cavity.py' | relative_url }}) · [출처·SHA-256]({{ '/assets/meep/26/provenance.json' | relative_url }}) · [실제 투과 로그]({{ '/assets/meep/26/trans_r20_dec1e5.log' | relative_url }})

Meep·NumPy 환경에서 실행하며 외부 helper는 필요하지 않습니다. 저장된 Lorentz 맞춤 수치는 아래 summary에서 가져오므로 CLI에 새로운 최적화 패키지를 추가하지 않았습니다.

```bash
python code/photonic_crystal_cavity.py --help
python code/photonic_crystal_cavity.py --mode bands --out work/cavity-bands
python code/photonic_crystal_cavity.py --mode harminv -N 3 --tag N3 --out work/cavity-harminv
python code/photonic_crystal_cavity.py --mode trans -N 3 --decay 1e-5 --tag N3-strict --out work/cavity-trans
```

1. **파라미터**: a = 1, ε·폭·구멍 크기·결함 간격을 고정합니다.
2. **구조**: `bands`는 한 주기, 나머지는 2N개 구멍의 결함 구조입니다.
3. **광원**: 밴드·고유 공진은 Hz 점원, 투과는 Ey 선원을 씁니다.
4. **경계**: 주기 셀과 열린 공진기의 경계를 구분합니다. Harminv의 거울 위상도 그대로 유지합니다.
5. **모니터**: 투과는 전체 폭의 T·R·위아래 방사 S, broadband 500점과 피크 주변 261점을 모읍니다.
6. **실행**: Harminv는 고정 후속 시간, 투과는 `stop_when_fields_decayed`를 씁니다. 기본 decay 1e−3 대신 검증된 비교에는 1e−5를 지정합니다.
7. **후처리**: 빈 도파로 분모로 R/T/S를 구하고 JSON·NPZ를 저장합니다. 서로 다른 모드는 다른 `--out`을 쓰면 결과를 쉽게 비교할 수 있습니다.

```python
R = -cavity_reflected_flux / reference_incident_flux
T = cavity_transmitted_flux / reference_incident_flux
S = (upper_outward_flux + lower_outward_flux) / reference_incident_flux
balance = R + T + S
```

<h2 id="interpret">5. 결과 해석하기: 좁은 피크를 놓치지 않아야 합니다</h2>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/26/forward_dft.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/26/forward_dft.png' | relative_url }}" alt="실제 세 주파수의 Hz 세기, 투과·반사·방사 전력 수지와 공진 피크의 Lorentz 맞춤" loading="lazy"></a>
<figcaption>왼쪽은 f = 0.18, 0.2345, 0.27 c/a의 |Hz|²입니다. 오른쪽 위는 에너지 수지, 아래는 촘촘히 읽은 공진 피크입니다. 각 장 패널은 색 범위를 따로 잡았으므로 패널 간 밝기를 전력으로 비교하지 않습니다.</figcaption>
</figure>

| N = 3, res 20의 검사 | 저장된 결과 | 해석 |
|---|---|---|
| Harminv | f = 0.234454153, Q = 372.408 | source 뒤 400의 추정 |
| 좁은 피크 Lorentz 맞춤 | f₀ = 0.234450094, Q = 370.395 | Q 차이 0.541% |
| 261점 좁은 구간의 최대 T | 0.928430, f = 0.23445 | 100% 투과 주장은 아님 |
| 500점 넓은 구간의 공진 부근 T | 0.829747, f = 0.234569 | 피크 사이를 읽어 작게 측정 |
| R + T + S, decay 1e−3 | 0.880632–1.147894 | 종료 조건이 부족한 비교 |
| R + T + S, decay 1e−5 | 0.995845–1.007986 | 이 설정에서 수지가 약 1% 안 |

피크가 좁아지면 **시간을 충분히 계산하는 것과 주파수를 촘촘히 읽는 것**을 각각 확인해야 합니다. 감쇠 종료는 특정 점의 장을 감시하므로 보편적인 오차 보증이 아닙니다. 위 수지는 같은 N = 3·res 20에서 실제로 비교한 결과입니다.

### Q 증가와 문서 수치 불일치를 나눠 읽습니다

res 20의 기본 모드 Q는 N = 2/4/6/8/10/12/14에서 62.46 / 1604.36 / 5748.04 / 6014.98 / 6082.39 / 6099.60 / 6081.56입니다. N이 커지면 증가가 둔해집니다. 그러나 다음 검사가 남아 있습니다.

| 설정 | 공진 f (c/a) | Q |
|---|---|---|
| N 3, res 20 | 0.234454153 | 372.408 |
| N 3, res 40 | 0.234893768 | 380.244 |
| N 3, res 60 | 0.234940116 | 380.267 |
| N 14, res 40 | 0.234980965 | 6379.389 |
| N 14, res 60 | 0.235027254 | 6436.946 |
| N 14, res 80 | 0.235014047 | 6401.640 |

N = 14, res 20에서 Harminv 시간을 400→3000으로 늘리면 Q = 6066.89, 셀 높이를 6→12로 늘리면 Q = 6081.70입니다. 이 검사들이 **문서 본문의 Q ≈ 8750을 회복하지는 못했습니다**. res 20 결과는 원래 노트북의 약 6080과 맞지만, 그 사실을 높은 해상도의 확정값으로 읽지 않습니다. 원인은 이 자료에서 해결되지 않았습니다. 더 높은 주파수의 두 번째 모드나 음의 Q로 검출된 항목을 기본 모드의 성공 수치에 섞지 않습니다.

<h2 id="check">6. 확인하기: 더 높은 해상도면 피크 문제도 해결될까요?</h2>

<details markdown="1">
<summary>질문 1 · 500개 주파수를 읽었는데도 피크를 놓칠 수 있나요?</summary>

전체 구간이 넓으면 한 칸이 선폭에 비해 큽니다. 주파수 개수만 보지 말고 피크 주변 Δf와 표본 간격을 비교하세요. 이 예제는 넓은 500점 계산과 별도의 좁은 261점 monitor를 같은 run에 넣었습니다. 보간으로 없는 피크 정보를 만들어서는 안 됩니다.

</details>

<details markdown="1">
<summary>질문 2 · 작은 Harminv fit error가 격자 수렴을 보장하나요?</summary>

fit error는 주어진 시간 기록에 대한 모형 맞춤 지표입니다. 원기둥 경계의 격자 표현·PML·source·모드 선택에 대한 물리 오차와 다릅니다. 주파수 위치, Q, 에너지 수지와 해상도·시간 검사를 따로 확인합니다.

</details>

### 직접 한 가지만 바꾸기

N = 3·res 20을 고정해 `--decay 1e-3`와 `1e-5`의 수지를 비교하세요. 다음에는 `--mode harminv -N 3 --resolution 40`으로 격자만 바꿉니다. 투과의 거친 표본 T 하나를 서로 다른 공진 주파수 사이에서 곧바로 비교하지 마세요. [12 · 고리 공진기]({{ '/ring-resonator/' | relative_url }})와 비교하면 빛을 가두는 방식은 달라도 Q를 검산하는 원칙은 같습니다.

<h2 id="reference">7. 참고 자료와 재현 기록</h2>

- 공식 설명: [Meep · Band Diagram, Resonant Modes, and Transmission of a Waveguide Cavity](https://meep.readthedocs.io/en/latest/Python_Tutorials/Resonant_Modes_and_Transmission_in_a_Waveguide_Cavity/).
- 고정 원본: [holey-wvg-cavity.py](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/holey-wvg-cavity.py), [holey-wvg-bands.py](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/holey-wvg-bands.py), commit f7811d4.
- 추가분: 전폭 에너지 상자, source 모드 검사, 피크 주변 촘촘한 monitor, 종료·해상도·Harminv 시간·셀 높이 비교와 한·영 학습 구성입니다. CLI는 기존 물리 설정을 옮기고 선택적 애니메이션 helper를 제거했습니다. 원래 그림 생성의 Lorentz 맞춤 수치는 [summary]({{ '/assets/meep/26/summary.json' | relative_url }})에 보존했습니다.
- 데이터: [기본 종료 JSON]({{ '/assets/meep/26/trans_r20.json' | relative_url }}), [엄격한 종료 JSON]({{ '/assets/meep/26/trans_r20_dec1e5.json' | relative_url }}), [엄격한 종료의 장·스펙트럼 NPZ]({{ '/assets/meep/26/trans_r20_dec1e5.npz' | relative_url }}), [N별 Harminv]({{ '/assets/meep/26/harminv_QvsN_r20.json' | relative_url }}), [주기 밴드]({{ '/assets/meep/26/bands_r20.json' | relative_url }}), [출처·한계·해시]({{ '/assets/meep/26/provenance.json' | relative_url }}).
- 연결: [04 · 유도모드]({{ '/straight-waveguide/' | relative_url }}) → [12 · 공진과 Q]({{ '/ring-resonator/' | relative_url }}) → 이 글. 흡수와 누설의 차이는 [25 · 흡수 전력]({{ '/absorbed-power/' | relative_url }})에서 비교합니다. upstream Meep 라이선스가 계속 적용됩니다.

<details markdown="1">
<summary>전체 실행 코드 펼치기</summary>

{% highlight python %}
"""Band gap, resonant modes and transmission of a perforated waveguide cavity.

Adapted from NanoComp/meep holey-wvg-cavity.py and holey-wvg-bands.py at
f7811d4157ea22f19d4ca76bc41c71b6e055763e, via holey_repro.py.
Upstream licensing remains applicable; see assets/meep/26/provenance.json.
Publication uses archived calculations. No optional animation helpers are needed.
Modes: bands (periodic cell), harminv (defect modes), trans (two-run spectrum).
"""
import argparse
import json
import os
import time

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["bands", "trans", "harminv"], required=True)
    ap.add_argument("--resolution", type=float, default=20)
    ap.add_argument("-N", type=int, nargs="+", default=[3])
    ap.add_argument("--sy", type=float, default=6)
    ap.add_argument("--fcen", type=float, default=0.25)
    ap.add_argument("--df", type=float, default=0.2)
    ap.add_argument("--window", type=float, default=400, help="harminv: time after source ends (default 400)")
    ap.add_argument("--decay", type=float, default=1e-3, help="trans: field-decay threshold (default 1e-3)")
    ap.add_argument("--noavg", action="store_true", help="disable subpixel averaging")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default="photonic-crystal-cavity-output")
    a = ap.parse_args()
    import meep as mp
    if a.resolution <= 0 or a.sy <= 2 or a.window <= 0 or not 0 < a.decay < 1 or any(n < 0 for n in a.N):
        ap.error("require resolution/window > 0, sy > 2, 0 < decay < 1, N >= 0")
    os.makedirs(a.out, exist_ok=True)
    T0 = time.time()
    eps, w, r, d, pad, dpml = 13, 1.2, 0.36, 1.4, 2, 1
    WG = mp.Medium(epsilon=eps)


    def geom(N):
        g = [mp.Block(size=mp.Vector3(mp.inf, w, mp.inf), material=WG)]
        for i in range(N):
            g.append(mp.Cylinder(r, center=mp.Vector3(d / 2 + i)))
            g.append(mp.Cylinder(r, center=mp.Vector3(-(d / 2 + i))))
        return g


    def dump(name, obj):
        if mp.am_master():
            json.dump(obj, open(os.path.join(a.out, name), "w"), indent=1, default=float)


    if a.mode == "bands":
        sim = mp.Simulation(cell_size=mp.Vector3(1, 12), geometry=[mp.Block(size=mp.Vector3(mp.inf, w, mp.inf), material=WG), mp.Cylinder(radius=r)],
                            sources=[mp.Source(mp.GaussianSource(0.25, fwidth=1.5), component=mp.Hz, center=mp.Vector3(0.1234))],
                            symmetries=[mp.Mirror(direction=mp.Y, phase=-1)], boundary_layers=[mp.PML(1, direction=mp.Y)], resolution=a.resolution)
        kpts = mp.interpolate(19, [mp.Vector3(0), mp.Vector3(0.5)])
        fs = sim.run_k_points(300, kpts)
        dump(f"bands_r{a.resolution:g}.json", dict(kx=[k.x for k in kpts], freqs=[[float(np.real(f)) for f in fl] for fl in fs], wall=time.time() - T0))
        if mp.am_master():
            print("BANDS done", time.time() - T0, flush=True)
        return

    if a.mode == "harminv":
        rows = []
        for N in a.N:
            sx = 2 * (pad + dpml + N) + d - 1
            sim = mp.Simulation(cell_size=mp.Vector3(sx, a.sy), geometry=geom(N), boundary_layers=[mp.PML(dpml)], resolution=a.resolution,
                                sources=[mp.Source(mp.GaussianSource(a.fcen, fwidth=a.df), component=mp.Hz, center=mp.Vector3())],
                                symmetries=[mp.Mirror(mp.Y, phase=-1), mp.Mirror(mp.X, phase=-1)], eps_averaging=not a.noavg)
            h = mp.Harminv(mp.Hz, mp.Vector3(), a.fcen, a.df)
            t1 = time.time()
            sim.run(mp.after_sources(h), until_after_sources=a.window)
            modes = [dict(f=m.freq, Q=m.Q, amp=abs(m.amp), err=abs(m.err)) for m in h.modes]
            rows.append(dict(N=N, sy=a.sy, res=a.resolution, window=a.window, noavg=a.noavg, modes=modes, wall=time.time() - t1))
            if mp.am_master():
                print("HARM " + json.dumps(rows[-1], default=float), flush=True)
            sim.reset_meep()
        dump(f"harminv_{a.tag or 'run'}.json", dict(args=vars(a), rows=rows))
        return

    # ---------------- trans
    N = a.N[0]
    sx = 2 * (pad + dpml + N) + d - 1
    X = 0.5 * sx - dpml
    Y = a.sy - 2 * dpml
    x_t = X - 0.5
    x_src = -X
    x_r = x_src + 0.5
    FR = (a.fcen, a.df, 500)
    FRD = (0.2345, 0.013, 261)
    F3 = [0.18, 0.2345, 0.27]


    def make(Nh):
        sim = mp.Simulation(cell_size=mp.Vector3(sx, a.sy), geometry=geom(Nh), boundary_layers=[mp.PML(dpml)], resolution=a.resolution,
                            sources=[mp.Source(mp.GaussianSource(a.fcen, fwidth=a.df), component=mp.Ey, center=mp.Vector3(x_src), size=mp.Vector3(0, w))],
                            symmetries=[mp.Mirror(mp.Y, phase=-1)])
        fl = dict(
            up=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(x_t), size=mp.Vector3(0, 2 * w))),
            tran=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(x_t), size=mp.Vector3(0, Y))),
            refl=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(x_r), size=mp.Vector3(0, Y))),
            side_p=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(0.5 * (x_r + x_t), 0.5 * Y), size=mp.Vector3(x_t - x_r))),
            side_m=sim.add_flux(*FR, mp.FluxRegion(center=mp.Vector3(0.5 * (x_r + x_t), -0.5 * Y), size=mp.Vector3(x_t - x_r), weight=-1)),
            dense=sim.add_flux(*FRD, mp.FluxRegion(center=mp.Vector3(x_t), size=mp.Vector3(0, Y))),
        )
        mode = sim.add_mode_monitor(*FR, mp.ModeRegion(center=mp.Vector3(x_r), size=mp.Vector3(0, Y)))
        return sim, fl, mode


    pt_t = mp.Vector3(x_t)
    res = {}
    for label, Nh in (("wg", 0), ("cav", N)):
        sim, fl, mode = make(Nh)
        if label == "cav":
            sim.load_minus_flux_data(fl["refl"], refl_data)
        dft = sim.add_dft_fields([mp.Hz], F3, center=mp.Vector3(), size=mp.Vector3(2 * X, Y))
        tr = {"t": [], "v": []}
        steps = [mp.at_every(0.25, lambda s: (tr["t"].append(s.meep_time()), tr["v"].append(float(np.real(s.get_field_point(mp.Ey, mp.Vector3(x_r)))))))]
        t1 = time.time()
        sim.run(*steps, until_after_sources=mp.stop_when_fields_decayed(50, mp.Ey, pt_t, a.decay))
        out = {k: np.array(mp.get_fluxes(v)) for k, v in fl.items()}
        out["freqs"] = np.array(mp.get_flux_freqs(fl["up"]))
        out["dfreqs"] = np.array(mp.get_flux_freqs(fl["dense"]))
        cf = sim.get_eigenmode_coefficients(mode, [1], eig_parity=mp.EVEN_Z)
        out["a_fwd"], out["a_bwd"] = cf.alpha[0, :, 0], cf.alpha[0, :, 1]
        out["Hz"] = np.array([sim.get_dft_array(dft, mp.Hz, i) for i in range(3)])
        out["eps"] = sim.get_array(component=mp.Dielectric, center=mp.Vector3(), size=mp.Vector3(2 * X, Y))
        out["trace_t"], out["trace_v"] = np.array(tr["t"]), np.array(tr["v"])
        out["t_end"], out["wall"] = sim.meep_time(), time.time() - t1
        if label == "wg":
            refl_data = sim.get_flux_data(fl["refl"])
        res[label] = out
        if mp.am_master():
            print(f"TRANS {label} t_end={out['t_end']:.1f} wall={out['wall']:.0f}s", flush=True)
        sim.reset_meep()
    if mp.am_master():
        flat = {f"{lab}_{k}": v for lab, o in res.items() for k, v in o.items()}
        np.savez_compressed(os.path.join(a.out, f"trans_{a.tag or 'r%g' % a.resolution}.npz"), N=N, sx=sx, sy=a.sy, X=X, Y=Y, x_t=x_t, x_r=x_r, x_src=x_src, F3=F3, **flat)
        inc = res["wg"]["tran"]
        R = -res["cav"]["refl"] / inc
        T = res["cav"]["tran"] / inc
        S = (res["cav"]["side_p"] + res["cav"]["side_m"]) / inc
        tot = R + T + S
        i0 = int(np.argmin(np.abs(res["wg"]["freqs"] - 0.2345)))
        mf = np.abs(res["wg"]["a_fwd"]) ** 2 / res["wg"]["refl"]
        summ = dict(tag=a.tag, res=a.resolution, N=N, decay=a.decay, t_end_cav=res["cav"]["t_end"], sum_minmax=[float(tot.min()), float(tot.max())],
                    sum_at=float(tot[i0]), T_at=float(T[i0]), R_at=float(R[i0]), S_at=float(S[i0]),
                    mode_frac_minmax=[float(mf.min()), float(mf.max())], wall=time.time() - T0)
        dump(f"trans_{a.tag or 'r%g' % a.resolution}.json", summ)
        print("RESULT " + json.dumps(summ, default=float), flush=True)


if __name__ == "__main__":
    main()
{% endhighlight %}

</details>
