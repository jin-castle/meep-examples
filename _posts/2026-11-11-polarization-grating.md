---
layout: lesson
lesson_title: "편광을 바꾸면 빛이 꺾이는 방향도 바뀔까요?"
lesson_summary: "액정의 광축을 공간에 따라 회전시킨 비등방 격자에서 Ez ± iEy 입사의 ±1차 전력을 분해합니다. 편광 선택성과 입사 전력 기준 효율을 구분하고, 해석식과의 남은 차이도 확인합니다."
lesson_goals:
  - "회전된 유전율 텐서를 epsilon_diag와 epsilon_offdiag로 표현한다."
  - "두 전기장 성분의 ±π/2 위상차로 입력을 바꾼다."
  - "회절 차수 전력과 총 투과 전력을 서로 다른 분모로 해석한다."
lesson_prerequisites: "06편 회절 차수 · 07편 위상 제어 · 20편 재료 모델"
date: 2026-11-11
title: "Meep Example 21 · 편광으로 빛을 나누기 — 비등방 액정 편광 격자"
title_en: "Meep Example 21 · Steering with polarization — anisotropic liquid-crystal gratings"
lang: ko
translation_key: polarization-grating
series: meep-examples
part: 21
level: intermediate
runtime: "저장된 원편광 4조건: 조건당 약 13–18초, 해상도 50"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#diffraction-spectrum-of-liquid-crystal-polarization-gratings"
tags: [meep, fdtd, anisotropy, polarization, liquid-crystal, diffraction]
image: /assets/meep/21/02_orders.ko.png
excerpt: "유전율 텐서의 광축을 회전시킨 액정 격자에서 입력 편광의 위상 부호만 바꿔 ±1차 회절을 선택합니다. 단일 차수 선택과 100% 투과는 다름을 배웁니다."
---
<h2 id="observe">1. 관찰하기: 위상 부호를 바꾸면 반대 차수로</h2>

06편은 굴절률 모양으로 회절 차수를 나눴습니다. 이번에는 두께가 일정한 액정 안에서 **광축 방향**을 주기적으로 바꿉니다. 아래 막대의 입력은 Ez + iEy와 Ez − iEy입니다. 두 성분의 크기는 같고 상대 위상 부호만 다릅니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/21/02_orders.ko.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/21/02_orders.ko.png' | relative_url }}" alt="위상 지연 0.5와 1에서 입력 Ez 더하기 또는 빼기 iEy에 따른 -1,0,+1 차수의 실제 전력" loading="eager"></a>
<figcaption>2026-11-09 저장 Meep 1.33.0 결과를 다시 그렸습니다. 막대는 빈 유리 셀의 입사 전력으로 정규화했습니다. Δnd/λ = 0.5에서는 부호에 따라 −1차 또는 +1차로, 1에서는 대부분 0차로 갑니다.</figcaption>
</figure>

반파 지연(Δnd/λ = 0.5)의 Ez + iEy 입력은 −1차에 **0.94294**, 총 투과는 **0.94355**입니다. 반대 부호는 같은 전력을 +1차로 보냅니다. ±1차 중 한쪽의 선택성이 거의 100%여도, 입사 전력이 모두 투과한다는 뜻은 아닙니다.

이 글은 기존 저장 데이터의 재구성입니다. 새 FDTD 계산을 실행하지 않았으며, 상단 개념 애니메이션과 아래 수치 결과를 구분합니다.

<h2 id="predict">2. 예측하기: 두께를 두 배로 늘리면?</h2>

<fieldset class="prediction">
<legend>반파 지연 0.5에서 전파 지연 1로 두께를 두 배 늘리면 어떻게 될까요?</legend>
<label><input type="radio" name="polarization-grating-prediction" value="zero"> 편광 변환이 줄어들고 0차로 돌아온다.</label>
<label><input type="radio" name="polarization-grating-prediction" value="stronger"> 같은 ±1차 효율이 두 배가 된다.</label>
</fieldset>

단순 지연판 모델의 변환 성분은 sin²(πΔnd/λ)입니다. 따라서 0.5에서 최대, 1에서 0을 예측합니다. 실제 격자는 반사와 이산화 오차도 가지므로 ‘반드시 정확히 0’이라는 수치 기준과는 구분합니다.

<h2 id="understand">3. 원리 이해하기: 굴절률 하나가 아닌 텐서</h2>

{% include chapter-illustration.html %}

이 구조는 진행축 x, 주기축 y입니다. 액정의 주굴절률은 nₒ = 1.55, nₑ = 1.709이며 Δn = 0.159입니다. λ = 0.54 µm, 주기 Λ = 6.5 µm에서 광축이 φ(y) = πy/Λ로 회전합니다. 광축은 π 회전하면 같은 물성을 갖습니다.

$$
\boldsymbol\varepsilon(y)=R_x(\phi)
\operatorname{diag}(n_o^2,n_o^2,n_e^2)R_x^T(\phi),\qquad
p=\frac{\Delta n\,d}{\lambda}.
$$

여기서 d는 **총 액정 두께**입니다. 반파 지연이면 d = 1.69811 µm, 전파 지연이면 d = 3.39623 µm입니다. 회전된 텐서의 비대각 성분이 Ey와 Ez를 결합하므로 두 편광을 분리한 스칼라 2D 계산으로 대체할 수 없습니다.

```python
e = Rx * epsilon_diag * Rx.transpose()
material = mp.Medium(
    epsilon_diag=mp.Vector3(e[0].x, e[1].y, e[2].z),
    epsilon_offdiag=mp.Vector3(e[1].x, e[2].x, e[2].y))
```

광축 패턴이 변환된 편광에 공간 위상을 주므로 부호에 따라 ±1차가 선택됩니다. 공기 출력의 회절각은 sin θₘ = mλ/Λ이므로 ±1차는 **±4.76545°**입니다. 오른손·왼손 원편광 명칭은 관찰 방향 관례에 따라 달라질 수 있어, 이 글은 입력을 Ez ± iEy로 직접 표시합니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/21/01_field.ko.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/21/01_field.ko.png' | relative_url }}" alt="Ez 더하기 iEy 입력의 실제 복소 DFT 전기장 Re Ez와 액정 두께 경계" loading="lazy"></a>
<figcaption>반파 지연 조건의 실제 복소 DFT 장 중 Re Ez입니다. 점선은 액정 앞·뒤 경계이며 왼쪽은 n = 1.55 기판, 오른쪽은 공기입니다. 색은 전력이나 광축 지도가 아닙니다.</figcaption>
</figure>

| 항목 | 설정 |
|---|---|
| 구조 | n = 1.55 기판 1 µm, 액정 격자, 공기 여유 1 µm |
| 경계 | x 양 끝 PML 1 µm, y 주기 경계 Λ = 6.5 µm |
| 소스 | 기판 안의 두 선원 Ez 및 amplitude = ±i인 Ey |
| 주파수 | f = 1/0.54, Gaussian 폭 0.05f |
| 정규화 | 균일 n = 1.55 셀의 투과 flux |
| 측정 | 공기 쪽 총 flux, 명시적 m = −1·0·+1의 S·P 모드 전력 합 |
| 종료 | 빈 셀은 소스 종료 뒤 100, 구조 셀은 300 시간 단위 |

선형·무손실 비등방 재료의 수직 입사 예제입니다. 전압에 따른 액정 재배향, 색 분산, 실제 제작 오차는 포함하지 않습니다.

<h2 id="run">4. 실행하기: 입력 위상과 지연만 바꾸기</h2>

[독립 실행 Python 코드]({{ '/code/polarization_grating.py' | relative_url }}) · [데이터 출처와 SHA-256]({{ '/assets/meep/21/provenance.json' | relative_url }})

Meep·NumPy 환경에서 아래 명령은 실제 새 계산을 수행합니다. 저장된 예제를 보는 데에는 실행이 필요하지 않습니다.

```bash
python polarization_grating.py --phase 0.5 --chir 1 --out out21 --tag half_plus
python polarization_grating.py --phase 0.5 --chir -1 --out out21 --tag half_minus
python polarization_grating.py --phase 1 --chir 1 --out out21 --tag full_plus
python polarization_grating.py --phase 1 --chir -1 --out out21 --tag full_minus
```

`--phase`는 p = Δnd/λ, `--chir 1`은 Ez + iEy입니다. 이 코드는 원편광 네 조건을 재현하며, 아래에 별도 진단으로 제시한 선형 입사 두께 sweep을 실행하는 코드는 아닙니다.

```python
for m in (-1, 0, 1):
    # S와 P를 각각 분해한 뒤 전력을 더한다.
    plane_wave = mp.DiffractedPlanewave((0, m, 0), mp.Vector3(0, 1, 0), S, P)
    coeff = sim.get_eigenmode_coefficients(monitor, plane_wave)
    power = abs(coeff.alpha[0, 0, 0])**2 / incident_flux
```

`.json`에 차수별 `S`, `P`, `total`, 총 `Tflux`를, `.npz`에 복소 `Ez`, `Ey`, 공간 범위를 저장합니다. `total/Tflux`는 투과된 빛 중의 몫이고 `total` 자체는 입사 전력 대비 효율입니다.

<h2 id="interpret">5. 결과 해석하기: 선택성과 효율은 다른 수치</h2>

| p | 입력 | −1차 / 입사 | 0차 / 입사 | +1차 / 입사 | 총 T |
|---|---|---|---|---|---|
| 0.5 | Ez + iEy | 0.94294 | 0.000627 | 약 4.2×10⁻¹¹ | 0.94355 |
| 0.5 | Ez − iEy | 약 4.2×10⁻¹¹ | 0.000627 | 0.94294 | 0.94355 |
| 1 | Ez + iEy | 0.001696 | 0.92469 | 약 1.6×10⁻⁹ | 0.92638 |
| 1 | Ez − iEy | 약 1.6×10⁻⁹ | 0.92469 | 0.001696 | 0.92638 |

p = 0.5의 우세 차수/(+1차 + −1차)는 약 0.99999999996이지만 입사 전력 대비는 약 **94.29%**입니다. p = 1에서는 **0차/T = 99.8176%**입니다. 세 측정 차수의 합/T는 1.000007–1.000010으로 총 flux와 잘 맞습니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/21/03_validation.ko.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/21/03_validation.ko.png' | relative_url }}" alt="별도 선형 입사 두께 sweep의 해석식 오차와 해상도 50의 R,T,R 더하기 T" loading="lazy"></a>
<figcaption>추가 저장 실험의 선형 입사 sweep입니다. 해석식 비교 효율은 원본 노트북의 차수 정규화·각도 보정 관례를 따릅니다. 오른쪽은 별도로 입사 전력으로 정규화한 flux입니다.</figcaption>
</figure>

원편광의 차수 선택과 별개로, 선형 입사의 cos²·sin² 해석식 비교는 최대 절대 차이가 해상도 30에서 **0.15015**, 50에서 **0.06119**입니다. 감소했지만 사전 기준 0.03을 넘습니다. 전체 재현 판정은 **미결(inconclusive)**이며 ‘해석식과 완전히 일치’라고 결론내리지 않습니다. 해상도 50의 평균 R은 0.06252, 평균 T는 0.93746입니다.

비틀린 이중층의 저장 결과도 원자료에 있으나, 같은 sweep 매개변수에서 총 두께가 단일층의 두 배이므로 여기서는 공정한 동일 두께 성능 비교로 사용하지 않습니다.

<h2 id="check">6. 확인하기: 분모를 먼저 말하기</h2>

<details markdown="1"><summary>±1차 중 선택성이 100%이면 투과 효율도 100%일까요?</summary>

아닙니다. 선택성은 우세 차수/(+1차 + −1차), 입사 효율은 우세 차수/입사 전력입니다. 이 데이터의 반파 지연 입사 효율은 약 94.29%입니다.

</details>

<details markdown="1"><summary>epsilon만 하나 지정하면 같은 결과를 낼 수 있나요?</summary>

광축 회전과 비대각 결합이 사라집니다. 이 예제의 핵심은 위치별 텐서와 두 편광 성분의 결합입니다.

</details>

<details markdown="1"><summary>해상도 50이 30보다 나으면 해석식을 검증한 것인가요?</summary>

수렴 방향의 근거는 되지만 정한 정확도 기준을 통과한 것은 아닙니다. 실패한 0.03 기준과 실제 차이 0.06119를 함께 기록해야 합니다.

</details>

<h2 id="reference">7. 참고와 다음 단계</h2>

- [06 · 이진 격자]({{ '/binary-grating/' | relative_url }}) · [07 · Meta-atom]({{ '/meta-atom/' | relative_url }}): 회절 차수와 공간 위상
- [20 · 재료 분산]({{ '/material-dispersion/' | relative_url }}): 재료 모델의 가정과 검증
- [27 · 모드 분해]({{ '/mode-decomposition/' | relative_url }}): 모드 전력과 전체 flux를 구분하는 검사
- [공식 튜토리얼](https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#diffraction-spectrum-of-liquid-crystal-polarization-gratings) · [고정 버전 원본](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/polarization_grating.py)
- [검산 수치]({{ '/assets/meep/21/verified_metrics.json' | relative_url }}) · [그림 재생성 코드]({{ '/assets/meep/21/plot_saved_results.py' | relative_url }}) · [원래 재현 판정]({{ '/assets/meep/21/source_result.json' | relative_url }})

원본의 광축·소스·경계 모델을 유지하고 원편광의 부호별 차수 monitor와 저장 기능을 추가한 재현 자료를 사용했습니다. 다음 단계에서는 파장이나 광축 패턴을 하나씩 바꾸고, 모드 전력의 합과 총 flux를 함께 검사해 보세요.
