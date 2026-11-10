---
layout: lesson
lesson_title: "폭이 있는 빛은 하나의 입사각으로 설명할 수 있을까요?"
lesson_summary: "17·18편의 평면파를 유한 폭 Gaussian beam으로 바꿔 봅니다. 굴절과 임계각을 저장된 실제 장으로 확인하고, 빔의 각도 분포 때문에 평면파의 전반사 조건을 그대로 적용할 수 없는 이유를 배웁니다."
lesson_goals:
  - "유한 폭의 빔이 여러 방향의 평면파를 포함함을 설명한다."
  - "Snell 각과 국소 복소장 위상으로 측정한 방향을 비교한다."
  - "전기장 제곱의 밝기와 정규화된 반사·투과 전력을 구분한다."
lesson_prerequisites: "01편 점원·선원 · 17편 평면파와 파수 · 18편 각도별 계면 반사"
date: 2026-11-11
title: "Meep Example 19 · 폭이 있는 빛 — Gaussian beam의 굴절과 임계각"
title_en: "Meep Example 19 · Light with a finite width — Gaussian refraction and the critical angle"
lang: ko
translation_key: gaussian-beam
series: meep-examples
part: 19
level: intermediate
runtime: "저장된 한 코어 실행: 각 조건 약 21–23초 (장비에 따라 다름)"
meep_version: "1.33.0"
official_example: "https://danielkotik.github.io/Optical-beams-MEEP/"
tags: [meep, gaussian, beam, angular-spectrum, refraction, critical-angle, finite-aperture]
image: /assets/meep/19/gaussian-cycle-mean.png
excerpt: "유한 폭 Gaussian beam의 30°·45° 입사를 비교하고, Snell 굴절각과 각도 분포·전반사 해석의 한계를 확인합니다."
---
<h2 id="observe">1. 관찰하기: 30°와 45°에서 달라지는 빔</h2>

17편의 평면파는 셀 끝까지 이어지는 하나의 진행 방향을 가졌습니다. 실제 레이저처럼 폭이 있는 빛은 어떨까요? 아래는 굴절률 **1.54에서 1.00으로** 향하는 s 편광 Gaussian beam입니다. 왼쪽 빔은 경계를 통과해 굴절하고, 오른쪽은 반사된 빔이 두드러집니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/19/gaussian-cycle-mean.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/19/gaussian-cycle-mean.png' | relative_url }}" alt="굴절률 1.54에서 1로 입사하는 30도와 45도 Gaussian beam의 주기 평균 Ez 제곱, 공통 선형 색상 척도" loading="eager"></a>
<figcaption>2026-10-23의 실제 Meep 실행 자료를 새로 그렸습니다. 밝기는 마지막 두 주기의 cos/sin/DC 적합으로 구한 |Ez phasor|²/2이며, 두 패널이 같은 선형 척도를 씁니다. 가는 선은 실제 유전율 경계입니다. 밝기는 Poynting flux나 투과 효율이 아닙니다.</figcaption>
</figure>

이 계면의 평면파 임계각은 **40.4927°**입니다. 중심 입사각 30°는 그보다 작고 45°는 큽니다. 하지만 유한 폭 빔 전체가 정확히 한 각도인 것은 아니므로, 오른쪽 그림을 보고 “투과 전력이 정확히 0”이라고 판정하지 않습니다.

이 편은 Daniel Kotik와 Jörg Götte의 **Optical-beams-MEEP 원본 코드 재현 기록** 중 평면 경계 두 조건을 입문 학습으로 재구성합니다. 별도 [Beam Lab]({{ '/optical-beams/' | relative_url }})의 곡률·LG·Airy 실험과는 모델·실행 자료가 다릅니다. 이전 [재현 아카이브]({{ '/optical-beams/archive/' | relative_url }})의 출처를 유지하며 새 계산으로 이름 붙이지 않았습니다.

<h2 id="predict">2. 예측하기: 임계각을 넘으면 빔 전체가 전반사할까요?</h2>

<fieldset class="prediction">
<legend>Gaussian beam의 중심 입사각이 임계각보다 크면 어떤 결론이 안전할까요?</legend>
<label><input type="radio" name="gaussian-beam-prediction" value="spectrum"> 중심 평면파는 전반사 조건이지만 빔 전체의 각도 분포도 확인해야 한다.</label>
<label><input type="radio" name="gaussian-beam-prediction" value="zero"> 유한 폭과 관계없이 전체 투과 전력은 반드시 정확히 0이다.</label>
</fieldset>

<details markdown="1">
<summary>예측의 근거 보기</summary>

첫 선택이 맞습니다. 좁은 빔일수록 넓은 횡방향 파수 분포를 포함합니다. 중심이 임계각 위에 있어도 일부 성분은 그 아래일 수 있습니다. 계면 가까이의 장은 소멸장일 수도 있으므로 밝기만으로 원거리 투과 전력을 결정할 수도 없습니다. 이 저장 실험에는 입사장 분리와 정규화된 flux 측정이 없습니다.

</details>

| 비교할 질문 | 이 자료로 확인할 수 있는 것 |
|---|---|
| 30°의 빔이 어디로 굴절하는가? | 국소 phasor 위상 방향과 중심 평면파의 Snell 예측 비교 |
| 45°는 임계각을 넘는가? | 주어진 굴절률로 계산한 중심 입사각의 조건 |
| 투과 효율은 얼마인가? | 이 자료로는 판정하지 않음; 별도 입사장 분리·flux 정규화 필요 |

<h2 id="understand">3. 원리 이해하기: 폭과 각도 분포는 짝입니다</h2>

{% include chapter-illustration.html %}

waist 평면의 Gaussian 진폭을 대략 E(y) ∝ exp[−(y/w₀)²]로 쓰면 그 횡방향 파수 스펙트럼도 Gaussian입니다.

$$
\widetilde E(\kappa_y)\propto
\exp[-(\kappa_y w_0/2)^2],\qquad
\kappa_x=\sqrt{(n_1\kappa_0)^2-\kappa_y^2},\qquad
\kappa_0=2\pi/\lambda_0.
$$

여기의 κ는 **radian/길이**입니다. 17편의 Meep `k_point`(cycles/길이)와는 2π 차이가 있습니다. w₀를 줄이면 스펙트럼이 넓어져 서로 다른 방향의 성분이 더 섞입니다. 단일 평면파의 입사각과 빔의 중심 입사각은 구분해야 합니다.

실행한 원본은 이 스펙트럼의 전파 성분 −n₁κ₀ ≤ κy ≤ n₁κ₀를 적분하여, waist에서 떨어진 **유한 source 선의 복소 전류 프로파일**을 만듭니다. source 위치에 단순 실수 Gaussian만 넣는 구성과 같지 않습니다. 빔의 진행 중심은 +x이며, 계면의 방향을 바꾸어 입사각 30°·45°를 만듭니다.

중심 평면파의 Snell 예측과 임계각은 다음과 같습니다.

$$
n_1\sin\theta_i=n_2\sin\theta_t,\qquad
\theta_c=\sin^{-1}(n_2/n_1),\qquad n_1=1.54,\ n_2=1.00.
$$

30°에서는 θt = 50.3539°입니다. 45°에서는 우변에 대응하는 실수 투과각이 없습니다. 이는 **중심 성분의 조건**이며, 빔의 모든 성분에 같은 각도를 강제하는 것은 아닙니다. 18편의 공기→고굴절률 P 편광 반사와 달리, 여기서는 고굴절률→저굴절률 **s 편광**을 사용합니다.

<h2 id="run">4. 직접 실행하기: 유한 source와 열린 경계를 씁니다</h2>

[실행 진입 코드]({{ '/code/gaussian_beam.py' | relative_url }})는 저장소의 `code/optical_beams/run_original.py`와 MIT 원본 `source/`를 호출합니다. 파일 하나만 따로 내려받기보다 **저장소 전체 checkout**을 사용하세요. 기존 Meep 1.33.0 환경의 NumPy·SciPy·h5py가 필요하며, 별도 패키지 설치 없이 보관된 `optbeam` 순수 Python 소스를 사용합니다.

```bash
# 저장소 루트에서 실행합니다. 내부 wrapper가 CPU 라이브러리를 한 스레드로 설정합니다.
python code/gaussian_beam.py --help
python code/gaussian_beam.py --angle 30 --out results/gaussian19
python code/gaussian_beam.py --angle 45 --out results/gaussian19
```

각 명령은 실제 Meep 계산을 수행하며 `planar30/` 또는 `planar45/` 아래에 `fields.npz`, `run.json`과 원본 HDF5 출력을 만듭니다. 이 글을 작성할 때에는 위 명령을 다시 실행하지 않고 이전 결과를 재사용했습니다.

| 단계 | 이번 구성 |
|---|---|
| 단위 | 길이 a, f = 12 c/a, λ₀ = a/12; a에 실제 µm 값을 지정하지 않음 |
| source | x = −2.15a, y = −1…1a의 Ez 전류 선, 연속파, 원본 angular-spectrum 프로파일 |
| waist 파라미터 | w₀ = 8/(2π·12) = 0.1061a; waist 위치 x = −60/(2π·12) = −0.7958a |
| 격자와 경계 | 5a × 5a, 해상도 184.8/a, 네 면 PML 0.25a, Courant = 0.5 |
| 관측 | 종료 시각 t = 10a/c; 마지막 두 광주기의 62개 표본으로 cos/sin/DC 적합 |
| 보관 | 원래 924 × 924 장·좌표; 이 편의 공개 NPZ는 그중 phasor·ε·x·y를 손실 없이 추출 |

w₀는 waist 진폭의 모형 파라미터이며 source 선에서 직접 측정한 빔 폭이 아닙니다. 이 편은 빔 폭의 전파 곡선이나 해상도·PML 수렴을 검증하지 않았습니다.

그림과 국소 위상 진단만 다시 만들려면 NumPy·Matplotlib 환경에서 저장소 루트의 다음 명령을 사용하세요. 이 명령은 전자기장을 새로 풀지 않습니다.

```bash
python assets/meep/19/plot_saved_results.py
```

<h2 id="interpret">5. 결과 해석하기: 위상 방향과 전력은 다릅니다</h2>

<figure class="lesson-figure">
<a href="{{ '/assets/meep/19/gaussian-signed-phase.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/19/gaussian-signed-phase.png' | relative_url }}" alt="두 Gaussian beam 계산의 추출된 복소 Ez phasor 실수부, 공통 부호 색상 척도와 유전율 경계" loading="lazy"></a>
<figcaption>저장된 phasor의 한 위상 Re(Ez)를 동일한 부호 척도로 표시했습니다. 파랑은 양수, 빨강은 음수입니다. 이는 새 시간 전개나 실제 최종 시각의 순간장을 나타내는 그림이 아닙니다. 계면 부근의 줄무늬에는 입사·반사의 간섭도 포함됩니다.</figcaption>
</figure>

| 확인량 | 30° 조건 | 45° 조건 |
|---|---:|---:|
| 중심 성분과 임계각의 관계 | 30° < 40.4927° | 45° > 40.4927° |
| 중심 평면파의 Snell 투과각 | 50.3539° | 실수 투과각 없음 |
| 투과 영역의 국소 위상 각도 | 50.6618° | 해당 진단을 하지 않음 |
| 마지막 두 주기 적합의 상대 L2 잔차 | 0.0822% | 0.0207% |

30° 투과 영역에서 국소 위상 기울기로 잰 각도는 법선 기준 50.6618°이며 중심 평면파 예측과 0.3080° 차이입니다. 진폭이 큰 표본에 |phasor|² 가중치를 주고, 투과 방향을 따라 0.6–1.6a, 횡방향 반폭 0.12a의 작은 창을 사용했습니다. 이것은 **국소 파면 방향 진단**이며 빔 중심, 전체 에너지 흐름 또는 전력 효율을 직접 잰 값이 아닙니다.

작은 조화파 적합 잔차는 마지막 두 주기의 장을 잘 표현했다는 뜻입니다. 격자 오차가 그만큼 작거나 전체 정상상태가 수렴했다는 보증은 아닙니다. 높은 굴절률 매질의 파장당 격자점은 10개이며, 별도 격자·PML·종료 시각 사다리는 없습니다.

평균 Ez² 그림의 간섭 무늬와 밝기를 R 또는 T로 읽지 마세요. 서로 다른 매질에서는 같은 |E|²가 같은 전력 flux를 뜻하지 않습니다. 반사·투과 효율이 필요하면 03·18편처럼 기준 계산과 장 분리, 적절한 flux 면을 추가해야 합니다.

<h2 id="check">6. 이해 확인하기: 평면파에서 빔으로 바뀐 것은 무엇일까요?</h2>

<details markdown="1">
<summary>왜 17편처럼 Bloch 주기를 써서 y 끝을 이어 주지 않나요?</summary>

한 개의 유한 빔을 열린 공간에서 보려 하기 때문입니다. 여기서는 네 면에 PML을 두고 유한 source를 사용합니다. 횡방향 주기를 넣으면 유한 빔의 반복 배열이 되므로 다른 모델입니다.

</details>

<details markdown="1">
<summary>45° 그림에 경계 너머 장이 있으면 전반사 법칙이 틀린 것인가요?</summary>

아닙니다. 중심 성분은 임계각 위이지만 빔은 각도 분포를 가집니다. 또한 전반사에서도 계면 너머 소멸장이 존재할 수 있습니다. 장의 존재와 원거리 전력 전달은 별도 관측량입니다.

</details>

<details markdown="1">
<summary>두 패널의 밝기 비교로 어느 조건의 투과 효율이 높은지 수치로 말할 수 있나요?</summary>

공통 색상 척도는 장 크기 비교를 돕지만 입사 전력 정규화와 Poynting flux를 대신하지 않습니다. 이 자료에는 그런 효율 수치가 없습니다.

</details>

다음에는 [Beam Lab]({{ '/optical-beams/' | relative_url }})에서 다른 source 모델로 곡률을 바꿔 보세요. 파장까지 바꾸려면 [20편 분산 재료]({{ '/material-dispersion/' | relative_url }})의 재료 적용 범위도 확인합니다. 좁은 빔의 집광을 정량 평가하려면 [16편 near2far]({{ '/zone-plate-near2far/' | relative_url }})의 측정면·표본 간격 검산을 함께 읽으세요.

<h2 id="reference">7. 코드·저장 자료와 출처</h2>

- 실행: [gaussian_beam.py]({{ '/code/gaussian_beam.py' | relative_url }}), 기존 [run_original.py]({{ '/code/optical_beams/run_original.py' | relative_url }}), [재현 README]({{ '/code/optical_beams/README.md' | relative_url }})
- native 추출 자료: [30° phasor·ε·좌표]({{ '/assets/meep/19/planar30-fields.npz' | relative_url }}), [45° phasor·ε·좌표]({{ '/assets/meep/19/planar45-fields.npz' | relative_url }})
- [원래 결과 요약]({{ '/assets/meep/19/archived-results.json' | relative_url }}), [원래 검산의 공개 요약]({{ '/assets/meep/19/validation.json' | relative_url }}), [재계산한 진단]({{ '/assets/meep/19/verified_metrics.json' | relative_url }}), [출처·SHA-256]({{ '/assets/meep/19/provenance.json' | relative_url }}), [그림 코드]({{ '/assets/meep/19/plot_saved_results.py' | relative_url }})
- Daniel Kotik·Jörg Götte, [Optical-beams-MEEP 설명](https://danielkotik.github.io/Optical-beams-MEEP/), [고정 원본 ca145119](https://github.com/DanielKotik/Optical-beams-MEEP/tree/ca145119e5bd0f0804d846ea42e35e4c3daa91de), [v2.1.2 DOI](https://doi.org/10.5281/zenodo.5211251)
- 원본은 **MIT License, Copyright (c) 2018 Daniel Kotik**입니다. [라이선스 전문]({{ '/assets/meep/19/Optical-beams-MIT-LICENSE.txt' | relative_url }})을 보존합니다. 원본 Gaussian 구현과 별도 Beam Lab 구현의 출처를 혼합하지 않습니다.
