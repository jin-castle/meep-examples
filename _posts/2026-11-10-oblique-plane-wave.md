---
layout: lesson
lesson_title: "원하는 방향으로 평면파를 어떻게 넣을까요?"
lesson_summary: "EigenModeSource의 파수 벡터와 Bloch 경계를 함께 설정해 0°·40°·120°·210°의 평면파를 만듭니다. 줄무늬의 기울기를 위상으로 검산한 뒤, 다음 편의 각도별 반사 측정에 연결합니다."
lesson_goals:
  - "유한 선원과 주기 경계를 잇는 평면파의 차이를 설명한다."
  - "eig_kpoint와 k_point의 역할을 구분하고, x축 기준 입사각을 설정한다."
  - "복소 Ez의 위상 기울기로 방향과 파수 크기를 검사하고, FFT 진단의 한계를 설명한다."
lesson_prerequisites: "01편 점원·선원 · 02편 PML · 03편 reference run · 04편 EigenModeSource"
date: 2026-11-10
title: "Meep Example 17 · 원하는 방향의 평면파 — EigenModeSource, Bloch 위상, 파수 검산"
title_en: "Meep Example 17 · A plane wave in the desired direction — EigenModeSource, Bloch phase, and wavevector checks"
lang: ko
translation_key: oblique-plane-wave
series: meep-examples
part: 17
level: beginner
runtime: "저장된 res 50 계산: 각도당 약 1–3초(WSL, MPI 4); 한 코어 시간은 별도 측정하지 않음"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Eigenmode_Source/#planewaves-in-homogeneous-media"
tags: [meep, fdtd, plane-wave, eigenmode-source, bloch, oblique-incidence]
image: /assets/meep/17/01_planewave.png
excerpt: "균일한 n = 1.5 매질에서 원하는 방향의 평면파를 만들고, 4개 각도의 위상 기울기와 공간 FFT를 검사합니다. 입사광을 먼저 검산한 다음 18편의 계면 반사로 넘어갑니다."
---
<h2 id="observe">1. 관찰하기: 광원은 세워 두고 파면을 돌립니다</h2>

01편의 짧은 선원은 양 끝에서 둥근 파면을 만들었습니다. 여기서는 셀의 y 전체를 채우는 광원과 Bloch 경계를 써서, **광원 선을 회전시키지 않고** 평면파의 방향을 바꿉니다. 물체를 놓기 전에 광원부터 확인하는 실험입니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/17/01_planewave.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/17/01_planewave.png' | relative_url }}" alt="균일한 굴절률 1.5 매질의 실제 Meep Ez: 왼쪽부터 요청 각도 0도, 40도, 120도, 210도. 120도와 210도에서는 파가 왼쪽으로 나간다." loading="eager"></a>
<figcaption>2026-11-09에 저장한 실제 Meep 계산의 Re Ez입니다. 빨강·파랑은 전기장 부호이며 밝기는 광 세기가 아닙니다. x = 0의 세로 광원은 그대로이고, 0°·40°는 +x 쪽, 120°·210°는 −x 쪽으로 진행합니다. 패널마다 색 범위를 따로 정했으므로 패널 사이 진폭을 비교하지 않습니다.</figcaption>
</figure>

<details markdown="1">
<summary>계산 요약과 검증 범위</summary>

- **무엇을 계산했나요?** 2D Ez, 균일 매질 n = 1.5, 진공 파장 1 µm, 셀 14 × 10 µm, x 방향 PML 2 µm입니다. y 방향은 `k_point`가 정하는 Bloch 경계입니다.
- **어떤 결과인가요?** 요청한 0°·40°·120°·210°의 위상 추정 오차는 최대 0.0614°이고, 파수 크기 오차는 최대 0.164%입니다. 공간 FFT의 반대쪽 창/피크 창 비는 최대 0.002884입니다.
- **어디까지 검증했나요?** 이 네 각도의 균일·무손실 매질만 검사했습니다. FFT 창 비는 반사 전력 계수가 아닙니다. 같은 원자료 프로젝트의 회전 도파로·스침 입사 검증은 실패한 항목이 있으므로 그 결과를 이 성공 범위에 포함하지 않습니다.
- **실행 시간은요?** 원래 로그의 MPI 4 실행은 각도당 약 1–3초입니다. 아래 코드는 한 코어로도 실행할 수 있지만 같은 시간이라고 보장하지 않습니다. 이번 게시 작업에서는 전자기장을 다시 계산하지 않았습니다.

</details>

<h2 id="predict">2. 예측하기: 120°이면 빛은 어느 쪽으로 갈까요?</h2>

<fieldset class="prediction">
<legend>각도는 +x축에서 반시계 방향입니다. 40°에서 120°로 바꾸면 어떻게 될까요?</legend>
<label><input type="radio" name="oblique-plane-wave-prediction" value="left"> x 방향 진행이 오른쪽에서 왼쪽으로 바뀐다.</label>
<label><input type="radio" name="oblique-plane-wave-prediction" value="right"> 광원이 세로이므로 언제나 오른쪽으로 진행한다.</label>
<label><input type="radio" name="oblique-plane-wave-prediction" value="rotate-source"> 광원 선을 함께 돌리지 않으면 각도를 바꿀 수 없다.</label>
</fieldset>

<details markdown="1">
<summary>예측의 근거와 검사 기준 보기</summary>

파면에 수직인 벡터가 진행 방향입니다. $k_x=nf\cos\theta$이므로 40°에서는 양수, 120°에서는 음수입니다. `EigenModeSource`는 지정한 모드의 전기·자기 등가 전류를 함께 써서 진행 방향을 선택합니다.

| 검사 | 계산 전 예측 | 이번 자료의 판정 기준 |
|---|---|---|
| 방향 | 0°·40°: +x, 120°·210°: −x | 위상 각도 오차 < 0.5° |
| 파수 크기 | n f = 1.5 cycles/µm | 상대 오차 < 1% |
| 반대 방향 공간 성분 | 전방 피크보다 작음 | 저장된 FFT 창 비 < 0.01 |

210°와 −150°는 같은 방향입니다. 각도 오차를 구할 때 360° 주기를 먼저 맞춥니다. 이 기준은 이 실험의 검사 기준이며 모든 구조에 적용하는 정확도 보증이 아닙니다.

</details>

<h2 id="understand">3. 원리 이해하기: 모드의 방향과 경계의 위상을 맞춥니다</h2>

{% include chapter-illustration.html %}

Meep의 `k_point` 단위는 라디안/길이가 아니라 **cycles/길이**입니다. 균일 매질에서

$$
E_z(\mathbf r,t)\propto \exp\left[2\pi i(\mathbf k\cdot\mathbf r-ft)\right],\qquad
\mathbf k=nf(\cos\theta,\sin\theta),\qquad |\mathbf k|=nf.
$$

여기서는 길이 단위를 1 µm로 잡아 f = 1, n = 1.5입니다. 40°의 목표 벡터는 약 (1.14907, 0.96418) cycles/µm입니다. `eig_kpoint`는 **주입할 고유모드의 방향**을, 시뮬레이션의 `k_point`는 **셀 경계를 건널 때의 위상**을 정합니다. 둘을 같은 벡터로 지정합니다. y 경계에서는

$$
E_z(x,y+L_y)=e^{2\pi i k_yL_y}E_z(x,y).
$$

따라서 셀 위·아래를 이은 파면이 끊기지 않습니다. 이 예제는 x에만 PML을 두고 y에는 PML을 두지 않습니다. 유한 빔이 아니라 균일 매질을 주기적으로 이어 표현한 평면파입니다.

| 설정 | 하는 일 | 잘못 설정하면 |
|---|---|---|
| `size=Vector3(0, 10, 0)` | y 전체를 채우는 세로 광원 | 짧은 선원 양 끝의 회절이 섞임 |
| `eig_kpoint=k_point` | 원하는 파수 방향의 모드 선택 | 경계 위상과 다른 광원 주입 |
| `direction=mp.NO_DIRECTION` | 비스듬한 고유모드 탐색 방향을 명시 | 축 방향 자동 탐색과 혼동 |
| `eig_parity=mp.ODD_Z` | 2D Ez 편광 선택 | 다른 편광/모드를 선택 |
| `eig_vol`의 y 폭 `1/resolution` | 균일 매질의 작은 고유모드 계산 구간 | 광원 전체 폭과 모드 계산 폭을 혼동 |
| 0°에서만 `EVEN_Y`와 `Mirror(Y)` | 수평 진행의 거울 대칭 이용 | 비스듬한 파에 맞지 않는 대칭 강제 |

### 줄무늬를 눈으로 보는 대신 위상을 잽니다

이웃한 두 점의 복소장을 곱하면 일정한 시간 위상은 사라지고 공간 위상차가 남습니다.

$$
k_x\approx \frac{\arg\sum_{i,j}E_{i+1,j}E^*_{i,j}}{2\pi\Delta x},\quad
k_y\approx \frac{\arg\sum_{i,j}E_{i,j+1}E^*_{i,j}}{2\pi\Delta y},\quad
\theta_{\rm fit}=\operatorname{atan2}(k_y,k_x).
$$

저장된 분석은 중앙 6 × 6 µm 영역을 씁니다. 이웃 픽셀 위상차가 π를 넘으면 접힘이 생기므로 해상도가 필요합니다. 이 측정은 주로 단일 평면파가 있는 장의 방향 검사입니다. 반사파·여러 모드가 섞인 장을 하나의 벡터로 설명하는 방법은 아닙니다.

<h2 id="run">4. 실행하기: 균일 매질에서 광원만 먼저 검사합니다</h2>

[전체 Python 코드 다운로드]({{ '/code/oblique_plane_wave.py' | relative_url }}) · [실행·출처 기록]({{ '/assets/meep/17/provenance.json' | relative_url }}) · [40° 원래 실행 로그]({{ '/assets/meep/17/pw_a40.log' | relative_url }})

기존 Meep 환경에서 실행합니다. 필요한 패키지는 Meep와 NumPy이며 `--plot`을 붙일 때만 Matplotlib을 사용합니다. 별도 프로젝트 helper나 데이터 경로는 필요하지 않습니다.

```bash
python code/oblique_plane_wave.py --help
python code/oblique_plane_wave.py --angle 40 --tag pw_a40 --out work/plane-wave-40 --plot
python code/oblique_plane_wave.py --angle 120 --tag pw_a120 --out work/plane-wave-120 --plot
```

### 일곱 단계로 코드를 읽습니다

1. **단위·파라미터**: f = 1, n = 1.5, 해상도 50 px/µm, 종료 시각 23.56을 고정합니다.
2. **구조·재료**: `default_material=mp.Medium(index=1.5)`이며 물체나 계면이 없습니다.
3. **광원**: x = 0에 y 폭 10 µm의 연속파 `EigenModeSource`를 놓습니다.
4. **경계**: x 방향 PML 2 µm, y 방향 Bloch 경계를 설정합니다. 전체 셀은 14 × 10 µm입니다.
5. **측정**: PML을 뺀 중앙 10 × 10 µm의 복소 Ez를 저장하고, 중앙 6 × 6 µm에서 위상을 분석합니다.
6. **종료**: 원래 예제와 같은 고정 시각까지 계산합니다. 감쇠 종료나 시간 수렴 검사는 아닙니다.
7. **후처리**: 각도·파수·공간 FFT 지표를 JSON에, 장을 NPZ에 씁니다. `--plot`은 Re Ez PNG를 추가합니다.

```python
k_point = mp.Vector3(1.5, 0, 0).rotate(mp.Vector3(0, 0, 1), angle)
source = mp.EigenModeSource(
    src=mp.ContinuousSource(1.0), center=mp.Vector3(),
    size=mp.Vector3(0, 10, 0), direction=mp.NO_DIRECTION,
    eig_kpoint=k_point, eig_band=1, eig_parity=mp.ODD_Z,
    eig_vol=mp.Volume(center=mp.Vector3(), size=mp.Vector3(0, 1 / resolution, 0)))
```

위 코드는 비스듬한 경우의 핵심만 발췌했습니다. 실행 가능한 다운로드 코드에는 0°의 대칭 분기, 시뮬레이션, 분석, 저장이 모두 있습니다. 90°·270°처럼 광원 선에 평행한 진행은 여기의 네 각도 검증에 포함하지 않습니다.

<h2 id="interpret">5. 결과 해석하기: 각도, 파수, FFT는 다른 검사입니다</h2>

다음 수치는 그림을 만든 원래 JSON에서 가져왔습니다. 새 계산이나 도식 애니메이션에서 추정한 값이 아닙니다.

| 요청 각도 | 위상으로 잰 각도 | 각도 오차 | 잰 파수 크기 | FFT 창 비 |
|---|---|---|---|---|
| 0° | 약 0.00000° | < 0.000001° | 1.501556 | 2.884 × 10⁻³ |
| 40° | 40.06136° | 0.06136° | 1.498089 | 4.603 × 10⁻¹⁰ |
| 120° | 120.02029° | 0.02029° | 1.500307 | 2.035 × 10⁻¹⁰ |
| 210° | −149.94588° | 0.05412° | 1.497551 | 2.133 × 10⁻⁸ |

최대 파수 상대 오차는 $|1.497551-1.5|/1.5=0.001633$입니다. 네 각도 모두 예측 방향과 맞고, 저장된 각도·파수 기준을 통과합니다. 공간 FFT 피크만 쓰면 40°가 40.60°, 120°가 122.01°로 읽힙니다. 유한한 6 µm 창의 주파수 칸이 거칠기 때문에, 이 예제의 정밀한 방향 비교에는 위상 기울기를 사용합니다.

**FFT 창 비를 반사율로 읽지 마세요.** Hann 창을 씌운 공간 FFT에서 피크 주변 7 × 7칸과 반대쪽의 창을 비교한 진단값입니다. 원래 코드의 반대 인덱스 관례까지 유지했으므로 정확히 −k에 중심을 둔 전력 적분이라고도 볼 수 없습니다. 유한 창, 광원 근처 장, 정착 시간과 창 위치에 영향을 받으며 Poynting flux로 정규화하지 않았습니다. 특히 0° 값 0.002884가 물체의 0.2884% 반사라는 뜻은 아닙니다. 여기에는 물체가 없습니다.

### 통과한 범위와 남은 한계

| 항목 | 이 글에서 말할 수 있는 것 | 추가 검사가 필요한 것 |
|---|---|---|
| 입사 방향 | 이 네 각도에서 최대 오차 0.0614° | 모든 각도, 모든 주파수 |
| 파수 크기 | n f = 1.5와 0.164% 이내 | 해상도·종료 시각의 독립 수렴 |
| 단방향성 | FFT 반대쪽 창 성분이 작음 | 반사 flux·모드 전력에 의한 정량 검사 |
| 실제 구조 | 균일 매질의 광원 검사 | 계면, 유한 빔, 회전 도파로, 스침 입사 |

전체 원자료 프로젝트의 판정은 `refuted`입니다. 평면파의 C7·C7b·C8은 통과했지만, 회전 도파로의 문서 수치 비교와 스침 입사에서는 실패·측정면 배치 문제가 있었습니다. 예를 들어 스침 입사의 수평 진단면 비는 80°에서 0.888, 84°에서 0.307로 등록된 기준을 만족하지 못했습니다. 이를 평면파 네 각도의 결과로 덮거나 도파로 일반 성능으로 확대하지 않습니다. [전체 판정 JSON]({{ '/assets/meep/17/aggregate_verdict.json' | relative_url }})에 실패 항목도 그대로 보존했습니다.

<h2 id="check">6. 확인하기: 각도는 맞는데 파수 크기가 다르면요?</h2>

<details markdown="1">
<summary>질문 1 · 40° 줄무늬가 보이면 광원 설정 검증이 끝난 것일까요?</summary>

아닙니다. `atan2`는 방향만 검사합니다. n 또는 f를 잘못 넣어도 방향은 맞을 수 있습니다. 파수 크기가 n f인지, `eig_kpoint`와 `k_point`가 일치하는지 함께 확인합니다. 라디안과 cycles 단위를 섞으면 2π 오차가 날 수 있습니다.

</details>

<details markdown="1">
<summary>질문 2 · y PML을 추가하면 더 열린 공간의 같은 평면파일까요?</summary>

경계 조건이 달라집니다. 여기서는 Bloch 위상으로 위·아래 셀을 이어 평면파를 만듭니다. 유한 빔과 네 방향 PML을 쓰려면 광원의 폭·프로파일·주입법을 별도로 구성하고 끝단 회절을 검사해야 합니다. [Beam Lab]({{ '/optical-beams/' | relative_url }})의 유한 빔과 비교해 보세요.

</details>

### 직접 한 가지만 바꿔보기

먼저 40°의 해상도를 50→100으로 바꾸고 각도·파수 오차가 어떻게 달라지는지 저장하세요. 다음에는 해상도를 50으로 돌려놓고 `--until 47.12`만 바꿉니다. 두 변수를 동시에 바꾸지 않아야 공간 격자와 정착 시간의 영향을 구분할 수 있습니다. 이 실험의 새 결과는 위에 실린 검증값과 분리해서 기록합니다.

이제 입사광이 원하는 방향인지 확인했습니다. [18 · 입사각에 따른 계면 반사]({{ '/angular-reflectance/' | relative_url }})에서는 계면을 넣고 기준 계산으로 R/T를 구합니다. 그 뒤 [06 · 격자 회절]({{ '/binary-grating/' | relative_url }})의 수직 입사 조건을 각도 실험으로 확장할 수 있습니다.

<h2 id="reference">7. 참고 자료와 재현 기록</h2>

- 공식 원리: [Meep · Eigenmode Source — Planewaves in Homogeneous Media](https://meep.readthedocs.io/en/latest/Python_Tutorials/Eigenmode_Source/#planewaves-in-homogeneous-media).
- 고정 원본: [NanoComp/meep · oblique-planewave.py, commit f7811d4](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/oblique-planewave.py). 원본의 광원·매질·셀 조건을 사용했습니다.
- 이 글의 추가분: 네 각도의 저장된 위상/FFT 결과 해설, 실행 인자, 독립 출력 디렉터리, 선택적 PNG 저장, 한·영 학습 구성입니다. 코드는 Meep 원본의 라이선스 조건을 따릅니다.
- 자료: [0° JSON]({{ '/assets/meep/17/pw_a0.json' | relative_url }}), [40° JSON]({{ '/assets/meep/17/pw_a40.json' | relative_url }}), [120° JSON]({{ '/assets/meep/17/pw_a120.json' | relative_url }}), [210° JSON]({{ '/assets/meep/17/pw_a210.json' | relative_url }}), [SHA-256·출처 목록]({{ '/assets/meep/17/provenance.json' | relative_url }}).
- 이전 개념: [01 · 점원·선원]({{ '/point-line-source/' | relative_url }}), [04 · 도파로 고유모드 광원]({{ '/straight-waveguide/' | relative_url }}). 다음 측정: [18 · 각도별 반사]({{ '/angular-reflectance/' | relative_url }}).

<details markdown="1">
<summary>전체 실행 코드 펼치기</summary>

{% highlight python %}
"""Launch and measure the official homogeneous-medium oblique plane wave.

Adapted from NanoComp/meep python/examples/oblique-planewave.py at
f7811d4157ea22f19d4ca76bc41c71b6e055763e and the project's pw_run.py.
Upstream tutorial: https://meep.readthedocs.io/en/latest/Python_Tutorials/Eigenmode_Source/#planewaves-in-homogeneous-media
Keep the upstream Meep license; see assets/meep/17/provenance.json.
The published figures use the archived 2026-11-09 runs, not a new execution.
"""

import argparse
import json
import math
from pathlib import Path
import time

import numpy as np


def measure_field(field, resolution):
    """Preserve the archived phase-fit and windowed-FFT diagnostics."""
    dx = 1 / resolution
    crop = slice(int(2 * resolution), int(8 * resolution))
    sub = field[crop, crop]
    result = {"complex": bool(np.iscomplexobj(field))}
    if np.iscomplexobj(field):
        kx = np.angle(np.sum(sub[1:, :] * np.conj(sub[:-1, :]))) / (2 * math.pi * dx)
        ky = np.angle(np.sum(sub[:, 1:] * np.conj(sub[:, :-1]))) / (2 * math.pi * dx)
        result.update(kx=float(kx), ky=float(ky), k_mag=float(math.hypot(kx, ky)),
                      angle_fit=float(math.degrees(math.atan2(ky, kx))), k_expected=1.5)
    window = np.hanning(sub.shape[0])[:, None] * np.hanning(sub.shape[1])[None, :]
    power = np.abs(np.fft.fftshift(np.fft.fft2(sub * window))) ** 2
    fx = np.fft.fftshift(np.fft.fftfreq(sub.shape[0], dx))
    fy = np.fft.fftshift(np.fft.fftfreq(sub.shape[1], dx))
    i, j = np.unravel_index(np.argmax(power), power.shape)

    def box(ii, jj, radius=3):
        return power[max(ii - radius, 0):ii + radius + 1,
                     max(jj - radius, 0):jj + radius + 1].sum()

    # Retain the archive's mirrored FFT-index convention for comparability.
    # This finite-window spectral ratio is NOT reflected Poynting power.
    ib, jb = power.shape[0] - 1 - i, power.shape[1] - 1 - j
    result.update(fft_peak_k=[float(fx[i]), float(fy[j])],
                  fft_peak_angle=float(math.degrees(math.atan2(fy[j], fx[i]))),
                  backward_fraction_fft=float(box(ib, jb) / box(i, j)))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--angle", type=float, default=40, help="CCW degrees from +x")
    parser.add_argument("--resolution", type=float, default=50, help="pixels per micrometre")
    parser.add_argument("--until", type=float, default=23.56, help="Meep time units")
    parser.add_argument("--tag", default="pw_a40", help="output filename stem")
    parser.add_argument("--out", type=Path, default=Path("oblique-plane-wave-output"))
    parser.add_argument("--plot", action="store_true", help="also save a real-Ez PNG with matplotlib")
    args = parser.parse_args()
    if args.resolution < 4 or args.until <= 0:
        parser.error("resolution must be >= 4 and until must be positive")
    if not args.tag or Path(args.tag).name != args.tag:
        parser.error("tag must be a filename stem")
    import meep as mp

    start = time.time()
    angle = math.radians(args.angle % 360)
    k_point = mp.Vector3(1.5, 0, 0).rotate(mp.Vector3(0, 0, 1), angle)
    if angle == 0:
        direction, parity, mirrors, eig_vol = mp.AUTOMATIC, mp.EVEN_Y + mp.ODD_Z, [mp.Mirror(mp.Y)], None
    else:
        direction, parity, mirrors = mp.NO_DIRECTION, mp.ODD_Z, []
        eig_vol = mp.Volume(center=mp.Vector3(), size=mp.Vector3(0, 1 / args.resolution, 0))
    source = mp.EigenModeSource(
        src=mp.ContinuousSource(1.0), center=mp.Vector3(), size=mp.Vector3(0, 10, 0),
        direction=direction, eig_kpoint=k_point, eig_band=1, eig_parity=parity, eig_vol=eig_vol)
    sim = mp.Simulation(
        cell_size=mp.Vector3(14, 10, 0), resolution=args.resolution,
        boundary_layers=[mp.PML(2, direction=mp.X)], sources=[source],
        k_point=k_point, default_material=mp.Medium(index=1.5), symmetries=mirrors)
    sim.run(until=args.until)
    field = np.asarray(sim.get_array(component=mp.Ez, center=mp.Vector3(), size=mp.Vector3(10, 10)))
    result = dict(res=args.resolution, angle=args.angle, until=args.until,
                  steps=sim.timestep(), wall=time.time() - start, **measure_field(field, args.resolution))
    if mp.am_master():
        args.out.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.out / f"{args.tag}.npz", Ez=field, extent=np.array([-5, 5, -5, 5]))
        (args.out / f"{args.tag}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        if args.plot:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            limit = np.percentile(np.abs(field.real), 99.5)
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.imshow(field.real.T, origin="lower", extent=(-5, 5, -5, 5),
                      cmap="RdBu_r", vmin=-limit, vmax=limit)
            ax.set(xlabel="x (µm)", ylabel="y (µm)", title=f"Re Ez, requested angle {args.angle:g}°")
            fig.savefig(args.out / f"{args.tag}.png", dpi=150, bbox_inches="tight")
            plt.close(fig)
        print("RESULT " + json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
{% endhighlight %}

</details>
