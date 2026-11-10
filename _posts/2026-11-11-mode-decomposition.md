---
layout: lesson
lesson_title: "모드 전력과 전체 flux는 언제 같은 답을 줄까요?"
lesson_summary: "선형 테이퍼의 반사 기본 모드와 기준 장을 뺀 signed flux를 비교합니다. 해상도 50에서 음수 반사 추정값이 나온 저장 사례를 통해 측정 정의, 전방 잔차와 수렴 실패를 진단합니다."
lesson_goals:
  - "복소 모드 계수의 방향과 전력 정규화를 읽는다."
  - "전체 flux와 특정 모드의 전력이 세는 범위를 구분한다."
  - "음수 반사 추정값을 보존하고 측정 실패를 물리 결과와 구분한다."
lesson_prerequisites: "03편 reference 빼기 · 04편 guided mode · 05편 굽힘 손실"
date: 2026-11-11
title: "Meep Example 27 · 원하는 모드만 세기 — 테이퍼의 모드 분해와 flux 진단"
title_en: "Meep Example 27 · Counting selected modes — taper decomposition and flux diagnostics"
lang: ko
translation_key: mode-decomposition
series: meep-examples
part: 27
level: intermediate
runtime: "저장된 Lt 1·2·4·8 sweep: res 25 약 477초, res 50 약 1,051초"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#reflectance-of-a-waveguide-taper"
tags: [meep, fdtd, waveguide, taper, mode-decomposition, flux, diagnostics]
image: /assets/meep/27/02_diagnostic.ko.png
excerpt: "폭 1→2 µm 테이퍼에서 기본 모드 반사와 전체 flux 추정값을 비교합니다. 음수 반사와 남은 전방 성분을 숨기지 않고, 측정·정규화의 검증 방법을 배웁니다."
---
<h2 id="observe">1. 관찰하기: 해상도를 높였더니 반사가 음수?</h2>

04·05편에서 도파로의 총 전력을 쟀다면, 이제 원하는 모드의 전력만 분해합니다. 폭 1 µm에서 2 µm로 이어지는 선형 테이퍼의 길이 Lt를 1·2·4·8 µm로 바꿉니다. 기본 모드의 후방 전력과 반사면의 signed flux는 같은 답을 줄까요?

<figure class="lesson-figure">
<a href="{{ '/assets/meep/27/02_diagnostic.ko.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/27/02_diagnostic.ko.png' | relative_url }}" alt="해상도 25와 50의 기본 모드 반사와 signed flux 추정값, 기준 장을 뺀 뒤 반사면에 남은 전방 기본 모드 전력" loading="eager"></a>
<figcaption>2026-11-08 저장 Meep 1.33.0 진단 결과입니다. 음수 값을 절댓값으로 바꾸거나 0으로 자르지 않았습니다. 오른쪽은 출력 투과율이 아니라, 반사 측정면에서 기준 장을 뺀 뒤 남은 전방 성분입니다.</figcaption>
</figure>

res 25에서는 두 값이 양수이며 길이와 함께 작아집니다. 그러나 res 50의 signed flux 반사 추정값은 **−0.00477…−0.00521**입니다. 수동·무손실 구조의 물리적 반사율이 음수라는 뜻이 아니라, **이 계산의 반사 측정이 검증을 통과하지 못했다**는 신호입니다.

이 글의 목적은 저장된 실패를 진단하는 것입니다. 두 방법의 일치나 반사율 ∝ 1/Lt²를 검증했다는 예제가 아닙니다. 기존 데이터를 다시 그렸으며 새 계산을 실행하지 않았습니다.

<h2 id="predict">2. 예측하기: 보기 좋은 곡선보다 먼저 할 일</h2>

<fieldset class="prediction">
<legend>해상도 50에서 반사 추정값이 음수이면 어떻게 처리할까요?</legend>
<label><input type="radio" name="mode-decomposition-prediction" value="diagnose"> 부호를 보존하고 기준 계산·전방 잔차·수렴을 검사한다.</label>
<label><input type="radio" name="mode-decomposition-prediction" value="absolute"> 절댓값을 취해 작은 반사율로 보고한다.</label>
</fieldset>

로그 그래프에 음수가 표시되지 않는다고 삭제하면 실패 원인을 놓칩니다. 아래 그래프는 선형 축에 부호를 그대로 표시하고, 양수인 res 25 결과만 별도의 로그 축에서 봅니다.

<h2 id="understand">3. 원리 이해하기: 방향이 있는 모드 계수</h2>

{% include chapter-illustration.html %}

모드 분해는 측정면의 복소 DFT 장을 고유 모드에 투영합니다. 이 예제의 +x 기준에서 `alpha[0,0,0]`은 전방, `alpha[0,0,1]`은 후방 기본 모드 계수입니다. 전력 정규화된 계수의 절댓값 제곱을 기준 입사 전력으로 나누면 해당 모드의 전력 비가 됩니다.

$$
R_{\mathrm{mode}}=
\frac{|\alpha_{\mathrm{back,taper}}|^2}
{|\alpha_{\mathrm{forward,reference}}|^2},\qquad
R_{\mathrm{flux}}=-\frac{P_{\mathrm{subtracted}}}{P_{\mathrm{reference}}}.
$$

`load_minus_flux_data`는 기준의 복소 장을 빼므로, 남은 flux가 순수 후방파일 때는 음의 x 흐름이 되어 R 앞의 마이너스로 양수가 됩니다. 하지만 전방 잔차나 다른 모드·방사 성분이 있으면 특정 후방 모드와 전체 순 flux는 같은 양이 아닙니다. 완전한 기저와 일관된 정규화가 있다면 모든 성분의 합으로 전력 수지를 맞춰야 합니다.

유한 격자에서는 Meep과 모드 계산에 쓰는 MPB의 이산화 차이도 고려해야 합니다. 공식 예제는 작은 반사를 분해할 때도 기준 장 빼기를 사용합니다. 이 일반적인 주의점이 이번 음수 오차의 원인으로 입증된 것은 아닙니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/27/01_field.ko.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/27/01_field.ko.png' | relative_url }}" alt="길이 8 µm 테이퍼의 저장된 복소 DFT 전기장 Re Ez와 실제 유전체 경계" loading="lazy"></a>
<figcaption>res 25, Lt = 8 µm의 실제 DFT Re Ez입니다. 검은 선은 유전체 경계입니다. 진행하는 장이 매끈하게 보여도 작은 반사율의 측정 정확성이 보장되지는 않습니다.</figcaption>
</figure>

| 항목 | 설정 |
|---|---|
| 구조 | ε = 12, 폭 1→2 µm 선형 테이퍼, 양쪽 직선부 각 10 µm |
| 주파수 | λ = 6.67 µm, GaussianSource 폭 0.2f |
| 경계 | x PML 6 µm, y PML 2 µm, y 거울 대칭 |
| source | 기본 EigenModeSource, ODD_Z + EVEN_Y |
| 반사면 | 입력 직선부의 0.7Lw 위치, 횡방향 전체 모드 꼬리를 포함 |
| 기준 계산 | 같은 셀·소스·측정면의 폭 1 µm 직선 도파로 |
| 출력 측정 | 폭 2 µm 쪽 총 flux; 출력 모드별 분해는 없음 |
| 종료 | 소스 종료 후 반사면 Ez 제곱 크기의 구간 최대가 과거 최대의 10⁻⁹ 이하인지 50 시간 단위로 검사 |

2D 무손실 도파로 모델입니다. 폭 2 µm 출력부에는 여러 모드가 가능하므로 총 출력 flux를 곧바로 특정 모드의 S21로 해석하지 않습니다.

<h2 id="run">4. 실행하기: 같은 정의를 기록하며 두 방법 비교</h2>

[독립 실행 코드]({{ '/code/mode_decomposition.py' | relative_url }}) · [원본·자산 SHA-256]({{ '/assets/meep/27/provenance.json' | relative_url }})

Meep·NumPy 환경에서 아래 명령은 실제 새 계산을 실행합니다. 제공 코드는 실패한 저장 설정을 유지하므로, 실행 자체가 정확한 반사율을 보장하지 않습니다.

```bash
python mode_decomposition.py --resolution 25 --Lt 1 2 4 8 --out out27 --tag r25
python mode_decomposition.py --resolution 50 --Lt 1 2 4 8 --out out27 --tag r50
```

각 Lt에서 직선 기준과 테이퍼를 차례로 계산합니다. 처음에는 `--Lt 1`만 실행해 출력 필드와 부호를 확인할 수 있습니다.

```python
# taper sim의 monitor에 기준 복소 장을 뺀다.
sim.load_minus_flux_data(flux, incident_flux_data)
coeff = sim.get_eigenmode_coefficients(flux, [1],
                                      eig_parity=mp.ODD_Z + mp.EVEN_Y)
R_mode = abs(coeff.alpha[0, 0, 1])**2 / incident_mode_power
R_flux = -subtracted_flux / incident_flux
```

JSON의 `R_coeff`, `R_flux`, `T_flux`와 함께 전방 잔차 `residual_forward_coeff_power`를 확인하세요. 과거 원자료의 같은 항목 이름은 `T_coeff_in`입니다. 이름의 T 때문에 출력 투과율로 오해하지 마세요. 새 코드의 `R_flux_is_nonnegative`는 최소한의 부호 검사이며 정확성 인증이 아닙니다.

<h2 id="interpret">5. 결과 해석하기: 수렴 실패를 숨기지 않기</h2>

| Lt (µm) | res 25 기본 모드 R | res 25 flux 추정 R | res 50 기본 모드 R | res 50 signed flux 추정 R |
|---|---|---|---|---|
| 1 | 0.00033425 | 0.00041190 | 0.00043445 | −0.00477163 |
| 2 | 0.00008612 | 0.00009790 | 0.00017031 | −0.00510573 |
| 4 | 0.00004647 | 0.00004959 | 0.00011592 | −0.00516962 |
| 8 | 0.00002143 | 0.00002189 | 0.00007969 | −0.00520829 |

res 50의 전방 잔차는 입사 기본 모드 전력의 약 **0.00527**로, 후방 성분보다 큽니다. 이것은 남은 장이 순수 반사파가 아니라는 진단 근거입니다. 잔차가 왜 발생했는지는 이 데이터만으로 분리하지 않았습니다. 따라서 음수를 0으로 바꾸거나, 원인을 단정해 수정된 반사율을 만들어 내지 않습니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/27/03_comparison.ko.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/27/03_comparison.ko.png' | relative_url }}" alt="res 25의 양수 반사 추정값 감소와 두 해상도의 출력 총 flux 비" loading="lazy"></a>
<figcaption>왼쪽은 res 25의 관측된 감소만 보여줍니다. 오른쪽은 총 출력 flux이며 특정 출력 모드의 투과율이 아닙니다. 일부 값의 1 초과도 수치 잔차로 남겨 두었습니다.</figcaption>
</figure>

두 방법 상대 차의 최대는 res 25에서 0.2323, res 50에서 66.35로 커졌습니다. 작고 음수인 R 때문에 상대값이 매우 커질 수 있으므로 절대값·부호도 함께 봅니다. Lt 16은 저장 계산에 없으며, Lt 1…8 기본 모드의 로그 기울기 −1.28을 1/Lt²의 검증으로 제시하지 않습니다. 원래 재현 가설은 **기각(refuted)**입니다.

다음 진단은 기준 run의 소스·격자·측정면·정규화가 일관되는지 확인하고, 전방 잔차와 감쇠 조건·반사면 위치를 하나씩 비교하는 것입니다. 아직 수행하지 않은 변경을 해결책으로 단정하지 않습니다.

<h2 id="check">6. 확인하기: 데이터로 말할 수 있는 범위</h2>

<details markdown="1"><summary>Rflux가 음수인데 Rmode는 양수면 모드 분해가 정답인가요?</summary>

양수는 필요한 조건일 뿐입니다. 해상도에 따른 변화와 기준 장 잔차가 크므로 이 자료만으로 수렴한 반사율을 정할 수 없습니다.

</details>

<details markdown="1"><summary>Tflux가 거의 1이면 기본 모드 전달도 거의 1인가요?</summary>

출력 총 flux는 여러 guided mode와 측정면을 지나는 다른 성분을 함께 셉니다. 원하는 출력 모드의 전력을 알려면 그 면에서 해당 모드를 분해해야 합니다.

</details>

<details markdown="1"><summary>음수를 로그 그래프에 넣기 위해 절댓값을 취해도 되나요?</summary>

진단에서는 부호가 핵심입니다. 선형 축을 사용하고 실패한 추정값으로 표시하세요. 절댓값을 물리적 반사율로 보고하지 않습니다.

</details>

<h2 id="reference">7. 참고와 다음 단계</h2>

- [03 · Reference 빼기]({{ '/reference-subtraction/' | relative_url }}) · [04 · 직선 도파로]({{ '/straight-waveguide/' | relative_url }}) · [05 · 굽힘 손실]({{ '/waveguide-bend-90/' | relative_url }})
- [09 · 도파로 역설계]({{ '/bend-inverse/' | relative_url }}): 총 전력이 아닌 목표 모드 overlap을 목적에 맞게 선택
- [21 · 편광 격자]({{ '/polarization-grating/' | relative_url }}): 차수별 모드 전력과 총 flux의 수지 비교
- [공식 테이퍼 튜토리얼](https://meep.readthedocs.io/en/latest/Python_Tutorials/Mode_Decomposition/#reflectance-of-a-waveguide-taper) · [고정 버전 코드](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/mode-decomposition.py)
- [검산 수치]({{ '/assets/meep/27/verified_metrics.json' | relative_url }}) · [그림 재생성 코드]({{ '/assets/meep/27/plot_saved_results.py' | relative_url }}) · [원래 판정]({{ '/assets/meep/27/source_result.json' | relative_url }})

공식 예제를 바탕으로 반사면의 전방 잔차, 총 출력 flux와 DFT 지도 저장을 더한 재현 자료입니다. 원본 문서의 일반적 결론과 이 저장 실행에서 확인하지 못한 결론을 구분해 읽으세요.
