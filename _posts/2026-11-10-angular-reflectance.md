---
layout: lesson
lesson_title: "비스듬히 비추면 반사율은 어떻게 바뀔까요?"
lesson_summary: "Bloch kx를 고정한 공기–유전체 경계에 P 편광 펄스를 넣고, 각 주파수의 실제 입사각으로 Fresnel 식과 비교합니다. Brewster 최소와 해상도 수렴, 에너지 수지의 남은 오차를 함께 확인합니다."
lesson_goals:
  - "입력각과 주파수별 실제 입사각을 구분한다."
  - "빈 셀의 입사 flux와 빼기 정규화로 R과 T를 계산한다."
  - "Fresnel 오차의 수렴과 에너지 수지 잔차를 따로 검사한다."
lesson_prerequisites: "17편 경사 평면파와 Bloch 위상 · 03편 reference run 빼기"
date: 2026-11-10
title: "Meep Example 18 · 비스듬히 비춘 빛 — 각도별 반사율과 Brewster 각"
title_en: "Meep Example 18 · Light at an angle — angular reflectance and the Brewster angle"
lang: ko
translation_key: angular-reflectance
series: meep-examples
part: 18
level: intermediate
runtime: "기존 저장 실행: 0°·45°·75° 해상도 사다리, 각도·해상도에 따라 수초–수분"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#angular-reflectance-spectrum-of-a-planar-interface"
tags: [meep, fdtd, fresnel, brewster, oblique, bloch, convergence]
image: /assets/meep/18/02_results.ko.png
excerpt: "공기에서 굴절률 3.5 유전체로 P 편광 펄스를 보내 Fresnel 반사와 Brewster 각을 확인합니다. 고정 kx의 각도 정의와 해상도·에너지 수지 검사를 배웁니다."
---
<h2 id="observe">1. 관찰하기: 반사가 작아지는 각도</h2>

17편에서 평면파의 진행 방향을 정했다면, 이번에는 그 빛을 평평한 경계면에 비춥니다. 공기에서 굴절률 3.5의 무손실 유전체로 들어가는 P 편광의 반사율을 보세요. 수직 입사보다 비스듬한 입사에서 반사가 더 작아지는 구간이 있습니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/18/02_results.ko.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/18/02_results.ko.png' | relative_url }}" alt="실제 입사각에 따른 P 편광 반사율과 Fresnel 해석식, 해상도 200의 세 입력각 반사 스펙트럼" loading="eager"></a>
<figcaption>2026-11-08에 저장한 Meep 1.33.0 결과입니다. 왼쪽은 해상도 50에서 각 주파수의 실제 각도로 표시한 값, 오른쪽은 해상도 200의 스펙트럼입니다. θ₀는 λ = 0.8 µm에서 정한 입력각이며, 곡선 하나가 모든 파장에서 같은 각도를 뜻하지 않습니다.</figcaption>
</figure>

P 편광은 전기장이 입사면 안에 있는 경우입니다. 공기–유전체 경계의 Brewster 각은 약 **74.05°**입니다. λ = 0.8 µm, 입력각 75°의 저장 결과는 해상도 50에서 R = **0.00226**입니다. 최소에 가깝지만 정확히 Brewster 각을 계산한 점은 아닙니다.

이 예제는 기존 저장 데이터를 다시 그렸습니다. 새 시뮬레이션을 실행한 결과는 아닙니다. 해상도 50은 공식 노트북의 850개 반사율 표본을 최대 절대 차 0.000131로 재현하지만, Fresnel 해석해와의 오차는 훨씬 큽니다. 기존 출력과의 일치와 물리적 정확성을 따로 확인하는 이유입니다.

<h2 id="predict">2. 예측하기: 한 펄스는 한 각도일까요?</h2>

<fieldset class="prediction">
<legend>kx를 고정하고 0.4–0.8 µm 펄스를 넣으면 입사각은 어떻게 될까요?</legend>
<label><input type="radio" name="angular-reflectance-prediction" value="vary"> 주파수에 따라 입사각이 달라진다.</label>
<label><input type="radio" name="angular-reflectance-prediction" value="fixed"> 펄스의 모든 주파수가 입력각으로 들어간다.</label>
</fieldset>

입력각 θ₀ = 75°는 이 코드에서 가장 긴 파장 0.8 µm의 각도입니다. 가장 짧은 파장 0.4 µm에서는 주파수가 두 배이므로 sin θ가 절반이 되어 실제 입사각은 약 **28.88°**입니다. 아래 원리에서 확인해 보세요.

| 검사할 예측 | 비교 방법 |
|---|---|
| P 반사는 74.05° 부근에서 작아진다 | 실제 각도를 구한 뒤 Fresnel 곡선과 비교 |
| 해상도를 높이면 R의 오차가 줄어든다 | 같은 θ₀ = 0°·45°·75°, 같은 50개 주파수에서 비교 |
| 무손실 경계에서는 R + T = 1이다 | 반사율의 정확성과 별도로 에너지 수지 잔차 검사 |

<h2 id="understand">3. 원리 이해하기: 고정된 kx와 변하는 각도</h2>

{% include chapter-illustration.html %}

입사면을 x–z, 경계면을 z = 0으로 둡니다. 횡방향 구조가 일정하므로 x 방향의 Bloch 위상을 이용하면 z 방향 격자만 가진 셀로 경사 입사를 계산할 수 있습니다. 비수직 입사에서는 코드의 `dimensions=3`이 벡터 장 성분과 횡방향 파수를 유지하며, 셀의 x·y 길이는 0입니다.

Meep의 `k_point`는 2π를 제외한 파수입니다. 길이 단위가 µm이고 공기의 굴절률이 1이면

$$
k_x=f_{\min}\sin\theta_0,\qquad
\theta(f)=\sin^{-1}\!\left(\frac{k_x}{f}\right),\qquad
f_{\min}=1/0.8.
$$

소스의 `fcen`에서 정의한 각도와 혼동하지 마세요. 여기서는 공식 예제처럼 **fmin에서 θ₀를 정합니다**. 한 고정각의 광대역 응답을 구하려면 주파수마다 그 각도에 맞는 kx로 별도 계산하는 등의 구성이 필요합니다.

Snell 법칙으로 투과각 θt를 구하면 P 편광의 반사율은

$$
\sin\theta_t=\frac{\sin\theta}{3.5},\qquad
R_p=\left|\frac{\cos\theta_t-3.5\cos\theta}
{\cos\theta_t+3.5\cos\theta}\right|^2,\qquad
\theta_B=\tan^{-1}(3.5).
$$

반사 진폭 계수의 부호 관례는 달라도 절댓값 제곱은 같습니다. θ = 0°에서는 R = ((3.5 − 1)/(3.5 + 1))² ≈ 0.30864입니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/18/01_layout.ko.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/18/01_layout.ko.png' | relative_url }}" alt="z 방향 12 µm 셀의 PML과 source 및 R·T flux 면, 빈 셀 펄스 파형과 입사 flux 스펙트럼" loading="lazy"></a>
<figcaption>왼쪽은 실제 코드 좌표를 표시한 1D 배치도입니다. 가운데와 오른쪽은 저장된 빈 셀 계산 결과입니다. θ₀마다 입사 flux가 다르므로 각 계산의 분모를 그대로 사용합니다.</figcaption>
</figure>

| 항목 | 설정 |
|---|---|
| 구조 | z &lt; 0 공기, z &gt; 0 무손실 n = 3.5 반공간 |
| 셀·경계 | z 길이 12 µm, 양 끝 PML 1 µm |
| 소스 | z = −5 µm, Ex GaussianSource, 0.4–0.8 µm |
| 측정면 | 반사 z = −3 µm, 투과 z = +2 µm, 50개 주파수 |
| 정규화 | 같은 kx의 빈 셀 → 입사 flux와 복소 flux 데이터 저장 |
| 종료 | 소스 종료 후, 감시점 Ex의 절댓값 제곱을 50 시간 단위 구간의 최댓값으로 확인해 과거 최대의 10⁻⁹ 이하일 때 종료 |
| 비교 범위 | res 50: θ₀ = 0°…80°(5° 간격), res 100·200: 0°·45°·75° |

가정은 평평한 무손실·비분산 경계와 P 편광입니다. 유한 개구 빔, S 편광, 거친 표면 또는 분산 재료 결과로 일반화하지 않습니다.

<h2 id="run">4. 실행하기: 빈 셀을 빼고 반사·투과 재기</h2>

[전체 Python 코드 다운로드]({{ '/code/angular_reflectance.py' | relative_url }}) · [저장 데이터와 그림의 출처·해시]({{ '/assets/meep/18/provenance.json' | relative_url }})

Meep과 NumPy가 설치된 환경에서 실행합니다. 시리즈의 Meep 환경을 그대로 쓸 수 있습니다. 새 그림을 확인하는 데에는 아래 실행이 필요하지 않습니다.

```bash
# 세 입력각, 공식 스크립트의 해상도 200
python angular_reflectance.py --resolution 200 --theta 0 45 75 --out out18 --tag r200
# 같은 각도에서 해상도만 바꾸어 비교
python angular_reflectance.py --resolution 50 --theta 0 45 75 --out out18 --tag r50
python angular_reflectance.py --resolution 100 --theta 0 45 75 --out out18 --tag r100
```

처음에는 0° 하나로 소스·정규화를 확인해도 좋습니다. 전체 명령은 실제 FDTD 계산이며 각 각도마다 빈 셀과 경계가 있는 셀을 계산합니다.

```python
k = mp.Vector3(z=fmin).rotate(mp.Vector3(y=1), math.radians(angle))
reflection = sim.add_flux(fcen, df, 50,
                         mp.FluxRegion(center=mp.Vector3(z=-3)))
# 빈 셀에서 empty_data와 incident를 먼저 저장한 뒤, 새 sim에서:
sim.load_minus_flux_data(reflection, empty_data)
R = -reflected_flux / incident
T = transmitted_flux / incident
```

반사면의 양의 법선은 +z지만 반사파는 −z로 흐르므로 R 앞에 마이너스가 붙습니다. 투과면에는 입사장이 따로 없으므로 total flux를 그대로 정규화합니다. 03편처럼 **전력이 아니라 복소 장을 빼야** 입사·반사의 간섭 항을 제거할 수 있습니다.

코드는 `.npz`와 `.json`을 저장합니다. `freqs`, `kx`, `R`, `T`, `theta_actual_deg`, `R_fresnel`을 함께 기록하므로 주파수별 실제 각도로 검산할 수 있습니다. 과거 저장 `.npz`에는 마지막 두 배열이 없으며, 그림 스크립트가 `kx`와 `freqs`에서 계산합니다.

<h2 id="interpret">5. 결과 해석하기: 수렴하는 값과 남은 잔차</h2>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/18/03_convergence.ko.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/18/03_convergence.ko.png' | relative_url }}" alt="동일한 세 입력각에서 해상도를 올릴 때 줄어드는 Fresnel 오차와 75도에서 남는 R 더하기 T 빼기 1 잔차" loading="lazy"></a>
<figcaption>새 계산 없이 저장된 결과를 재검산했습니다. 왼쪽 Fresnel 오차는 동일한 세 입력각에서 비교했습니다. 오른쪽은 θ₀ = 75°의 수지이며, 해상도 200에도 λ = 0.8 µm 근처에 약 1.5% 잔차가 남습니다.</figcaption>
</figure>

| 해상도 (px/µm) | 최대 반사율 절대 오차 (공통 세 각도) | 최대 에너지 수지 절대 잔차 |
|---|---|---|
| 50 | 0.06350 | 0.13714 (17개 입력각 전체) |
| 100 | 0.01395 | 0.01269 (세 입력각) |
| 200 | 0.003398 | 0.01454 (세 입력각) |

최대 반사율 오차는 max |R − RFresnel|, 수지 잔차는 max |R + T − 1|입니다. 50→200의 Fresnel 오차 비는 **0.0535**입니다. 해상도 민감성이 크다는 근거이며, 오차의 원인을 모두 증명한 것은 아닙니다.

수지는 res 100→200에서 단조 감소하지 않습니다. 스침 입사에서 남는 오차의 원인으로 PML·종료 조건 등을 시험할 수 있지만, 이 저장 실험에서는 원인을 분리하지 않았습니다. **약 1.5%의 수지 잔차를 흡수율로 해석하면 안 됩니다.** 재료는 무손실입니다.

파장이 짧아질수록 고굴절률 매질 안의 격자점 수가 줄어드는 것도 확인하세요. λ = 0.4 µm, n = 3.5, res 50이면 매질 내 파장당 약 5.7점뿐입니다. 공식 노트북과 같은 설정도 목적에 맞게 수렴을 확인해야 합니다.

<h2 id="check">6. 확인하기: 각도·정규화·정확성</h2>

<details markdown="1">
<summary>질문 1. θ₀ = 75°에서 λ = 0.4 µm의 실제 입사각은?</summary>

약 **28.88°**입니다. kx는 (1/0.8)sin75°로 고정이고 f = 1/0.4이므로 sin θ = 0.5sin75°입니다. 따라서 이 스펙트럼 전체를 ‘75° 반사 스펙트럼’으로 이름 붙이면 오해가 생깁니다.

</details>

<details markdown="1">
<summary>질문 2. R + T가 1.015이면 1.5%의 이득이 있나요?</summary>

아닙니다. 이 모델은 무손실·무이득입니다. 수치 잔차이며, 정규화·해상도·PML·종료 조건을 점검할 대상입니다. 이 데이터만으로 어느 원인이 지배적인지 결정하지 않습니다.

</details>

<details markdown="1">
<summary>질문 3. 정확히 같은 노트북 결과를 냈으면 충분한가요?</summary>

이전 출력의 재현과 정확도는 다른 검사입니다. 여기서는 850개 노트북 값을 잘 재현해도 res 50의 Fresnel 오차가 최대 0.0635입니다. 해석해, 해상도 사다리, 에너지 수지를 함께 확인합니다.

</details>

다음 실험으로는 각 파장에 맞춰 kx를 바꿔 **같은 실제 각도**의 스펙트럼을 구성해 보세요. 먼저 새 계산의 비교 기준과 종료·PML 조건을 정하고, 기존 저장 결과와 구분해 기록합니다.

<h2 id="reference">7. 참고와 다음 단계</h2>

- [03 · Reference run 빼기]({{ '/reference-subtraction/' | relative_url }}): 입사장을 제거하는 정규화 복습
- [17 · 경사 평면파]({{ '/oblique-plane-wave/' | relative_url }}): 진행 방향과 Bloch 위상
- [06 · 이진 격자]({{ '/binary-grating/' | relative_url }}) · [07 · Meta-atom]({{ '/meta-atom/' | relative_url }}): 경계면에서 주기 구조의 각도 응답으로 확장
- [14 · 광추출]({{ '/extraction-efficiency/' | relative_url }}): 여러 각도로 나오는 빛의 전력 합산
- [공식 Meep 튜토리얼](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#angular-reflectance-spectrum-of-a-planar-interface) · [고정 버전 원본 코드](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/refl-angular.py)
- [Meep 종료 조건 API](https://meep.readthedocs.io/en/latest/Python_User_Interface/#run-and-step-functions): `stop_when_fields_decayed`의 제곱 장 기준과 구간 검사

원본 예제의 경계·재료·소스·정규화 설정을 따르고, 투과 monitor와 데이터 저장을 추가했습니다. 그림은 저장 결과의 교육용 재구성입니다. [검산 수치]({{ '/assets/meep/18/verified_metrics.json' | relative_url }})와 [그림 재생성 스크립트]({{ '/assets/meep/18/plot_saved_results.py' | relative_url }})를 함께 제공합니다. 데이터의 생성 시각·원본 파일 SHA-256은 [provenance.json]({{ '/assets/meep/18/provenance.json' | relative_url }})에 있습니다.
