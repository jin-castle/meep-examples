---
layout: lesson
lesson_title: "재료의 굴절률이 파장에 따라 바뀌면?"
lesson_summary: "상수 굴절률 대신 fused_quartz와 Lorentz 분산 모델을 넣습니다. 석영의 반사 스펙트럼을 Fresnel 식과 검산하고, 모드 주파수로 유전율을 추정할 때 생기는 오차를 살펴봅니다."
lesson_goals:
  - "상수 index와 주파수에 의존하는 복소 유전율의 차이를 설명한다."
  - "빈 셀 기준 계산을 빼서 분산 재료의 반사율을 구하고 해상도 수렴을 확인한다."
  - "실수 k의 복소 모드 주파수와 실수 주파수의 재료 응답을 구분한다."
lesson_prerequisites: "02편 PML · 03편 기준 계산과 Fresnel 반사 · 12편 모드 주파수"
date: 2026-11-10
title: "Meep Example 20 · 재료의 색을 넣기 — 석영 반사와 Lorentz 분산"
title_en: "Meep Example 20 · Giving materials a spectrum — quartz reflection and Lorentz dispersion"
lang: ko
series: meep-examples
part: 20
level: intermediate
runtime: "석영 res 200: 40,001 time steps; Lorentz: k점 101개 (시간은 장비에 따라 다름)"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Material_Dispersion/"
tags: [meep, fdtd, material, dispersion, quartz, lorentz, fresnel, convergence]
image: /assets/meep/20/quartz-reflectance.png
excerpt: "분산 석영의 반사율을 Sellmeier–Fresnel 식과 맞추고, Lorentz 매질에서 모드로 유전율을 역산하는 검산의 한계를 확인합니다."
---
<h2 id="observe">1. 관찰하기: 같은 유리도 색에 따라 반사율이 다릅니다</h2>

03편에서는 한 굴절률의 계면을 계산했습니다. 이제 공기에서 **분산 석영(fused quartz) 반공간**으로 빛을 넣고, 진공 파장 0.4–0.8 µm의 반사율을 한 펄스로 구합니다. 표면 모양은 그대로인데 짧은 파장일수록 반사율이 조금 커집니다.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/20/quartz-reflectance.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/20/quartz-reflectance.png" alt="공기와 분산 석영의 수직 입사 반사율, 해상도 100과 200의 Fresnel 오차 비교" loading="eager"></a>
<figcaption>저장된 Meep 1.33.0 계산을 다시 그린 결과입니다. 왼쪽은 반사율, 오른쪽은 Sellmeier–Fresnel 식과의 절대 차이입니다. 점은 계산, 선은 이론이며 해상도 100→200에서 최대 오차가 약 4배 줄어듭니다.</figcaption>
</figure>

석영 결과와 함께 **구조가 없는 Lorentz 매질의 모드 계산**도 살펴봅니다. 이 두 실험은 검산 상태가 다릅니다. 석영 반사는 목표 오차 안에 들어오지만, 아래의 단순 유전율 역산은 1% 목표를 통과하지 못했습니다. 잘 맞는 그림과 아직 설명하지 못한 오차를 함께 읽는 것이 이 예제의 핵심입니다.

<details markdown="1">
<summary>실험 조건과 기존 예제와의 연결</summary>

| 실험 | 모델과 조건 | 확인할 물리량 |
|---|---|---|
| 석영 반사 | 1D, 공기/석영 반공간, 양 끝 PML 1 µm, 0.4–0.8 µm, 50개 주파수 | 빈 셀로 정규화한 R(λ), Fresnel과의 차이 |
| Lorentz 매질 | 0D Bloch 셀, ε∞ = 2.25, 두 공진 항, 해상도 20 | k = 0.3–2.2의 복소 모드 주파수 202개 |

03편의 정규화 방법은 그대로 쓰고 재료만 바꿉니다. 07편 위상 library와 metalens를 여러 파장에서 설계할 때도 재료 분산을 포함해야 합니다. 18편의 각도 의존성과 이번 편의 파장 의존성을 각각 검산한 뒤 함께 다루세요.

</details>

<h2 id="predict">2. 예측하기: 고정된 index 하나로 충분할까요?</h2>

<fieldset class="prediction">
<legend>굴절률을 상수 1.5로 고정한 무손실 반공간의 수직 입사 반사율은 파장에 따라 어떻게 될까요?</legend>
<label><input type="radio" name="material-dispersion-prediction" value="constant"> 이상적인 연속계에서는 4%로 일정하다.</label>
<label><input type="radio" name="material-dispersion-prediction" value="dispersion"> 구조가 없어도 석영과 같은 파장 의존성이 자동으로 생긴다.</label>
</fieldset>

<details markdown="1">
<summary>예측과 검산 기준 보기</summary>

첫 선택이 맞습니다. 상수 n이면 R = [(n−1)/(n+1)]² = 0.04입니다. `mp.Medium(index=1.5)`는 석영의 Sellmeier 분산을 자동으로 넣지 않습니다. 관측된 파장 의존성이 재료에서 왔는지, 격자 오차에서 왔는지 분리하려면 이론과 해상도 비교가 필요합니다.

석영 실험의 사전 기준은 **max |RMeep−RFresnel| < 5×10⁻⁴**입니다. 해상도 200에서 통과하고, 100에서는 통과하지 못합니다. Lorentz 단순 역산의 별도 기준 1%는 이번 저장 결과에서 통과하지 못합니다.

</details>

<h2 id="understand">3. 원리 이해하기: 재료에도 응답 시간이 있습니다</h2>

{% include chapter-illustration.html %}

유전 분극이 전기장을 즉시 따라가지 않으면 응답은 주파수에 의존합니다. Meep은 시간 영역에서 보조 분극 방정식을 함께 적분합니다. 일반적인 스칼라 Lorentz 항을 Meep의 보통 주파수 단위로 쓰면 다음과 같습니다.

$$
\varepsilon(f)=\varepsilon_\infty+\sum_j\frac{\sigma_j f_j^2}{f_j^2-f^2-i\gamma_j f}.
$$

여기서 `frequency`는 fⱼ, `gamma`는 γⱼ, `sigma`는 σⱼ입니다. 모든 값의 주파수 단위를 맞춰야 합니다. 시간 의존성 exp(−iωt)에서 수동 재료의 양의 Im ε는 흡수와 연결되지만, 이 편의 석영 실험은 흡수 전력을 독립적으로 측정하지 않습니다. PML에서 빠진 전력을 재료 흡수로 세어서는 안 됩니다.

{% highlight python %}
material = mp.Medium(
    epsilon=2.25,
    E_susceptibilities=[
        mp.LorentzianSusceptibility(frequency=1.1, gamma=1e-5, sigma=0.5),
        mp.LorentzianSusceptibility(frequency=0.5, gamma=0.1, sigma=2e-5),
    ],
)
{% endhighlight %}

이 교육용 두 공진 모델과 석영은 **다른 재료**입니다. 석영 실험은 `from meep.materials import fused_quartz`를 사용합니다. 길이 단위를 1 µm로 잡았으므로 λ = 0.4–0.8은 µm이고 f = 1/λ입니다. 재료 라이브러리의 적용 파장 범위를 벗어나 외삽하지 마세요.

수직 입사에서는 비자성·투명 재료의 n(λ) = √ε(λ)를 사용하여

$$
R(\lambda)=\left|\frac{1-n(\lambda)}{1+n(\lambda)}\right|^2
$$

로 검산합니다. 코드의 Sellmeier 식과 Meep의 석영 모델을 같은 파장에서 평가합니다.

<h2 id="run">4. 직접 실행하기: 재료만 바꾸고 정규화는 유지합니다</h2>

Meep 1.33.0 Python 환경에서 실행하세요. 석영 스크립트는 NumPy와 Matplotlib도 사용하며, 두 파일 모두 단독으로 실행할 수 있습니다. 저장된 이 글의 결과는 새 계산 없이 아래 자료로 확인할 수도 있습니다.

{% highlight bash %}
# 먼저 석영 반사: 빈 셀과 재료 셀을 순서대로 계산합니다.
OMP_NUM_THREADS=1 python code/dispersive_quartz.py --out results/quartz200 --resolution 200
OMP_NUM_THREADS=1 python code/dispersive_quartz.py --out results/quartz100 --resolution 100

# 확장 실험: 실수 Bloch k마다 펄스 후 복소 모드 주파수를 찾습니다.
OMP_NUM_THREADS=1 python code/material_dispersion.py --out results/lorentz20 --resolution 20
{% endhighlight %}

석영은 `reflquartz.json`, `refl_quartz.png`를, Lorentz 실험은 `matdisp.json`을 만듭니다. `--out`은 실행 위치를 기준으로 한 출력 폴더입니다. `--help`로 인자를 볼 수 있습니다. 한 코어 설정은 WSL/Linux 셸 예시이며 실행 시간은 장비와 종료 조건에 따라 달라집니다.

석영에서 꼭 유지할 순서는 다음과 같습니다.

1. 구조 없는 셀에서 입사 flux와 복소 DFT 자료를 저장합니다.
2. `reset_meep()` 뒤 같은 광원·주파수·측정면에 석영 반공간을 추가합니다.
3. `load_minus_flux_data()`로 입사장을 먼저 빼고 R = −Φrefl/Φinc를 계산합니다.
4. 50개 파장에서 이론과 비교한 뒤 해상도 100→200의 차이를 확인합니다.

{% highlight python %}
empty_flux = mp.get_fluxes(refl)
empty_data = sim.get_flux_data(refl)
# 재료를 넣은 새 sim에서 같은 위치의 refl 모니터를 만듭니다.
sim.load_minus_flux_data(refl, empty_data)
# source 종료 뒤 장이 감쇠할 때까지 계산한 다음:
R_meep = -np.asarray(mp.get_fluxes(refl)) / np.asarray(empty_flux)
{% endhighlight %}

<h2 id="interpret">5. 결과 해석하기: 맞은 검산과 남은 오차를 나눠 봅니다</h2>

| 석영 비교 | 해상도 100 | 해상도 200 |
|---|---:|---:|
| 최대 절대 반사율 오차 | 6.594×10⁻⁴ | 1.678×10⁻⁴ |
| 5×10⁻⁴ 기준 | 미달 | 통과 |

해상도 200에서 0.8 µm의 R은 0.034182(이론 0.034143), 0.4 µm에서는 0.036390(이론 0.036222)입니다. **절대 오차 1.68×10⁻⁴는 0.0168%p**입니다. 이를 반사율 자체에 대한 상대 오차 0.0168%라고 읽으면 안 됩니다. 이 계산은 총 40,001 time step, Meep 시간 100.0025에서 끝났습니다.

<figure class="lesson-figure">
<a href="{{ site.baseurl }}/assets/meep/20/lorentz-validation.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/20/lorentz-validation.png" alt="Lorentz 매질의 두 모드 분지와 단순 실수 주파수 유전율 추정의 상대 오차" loading="lazy"></a>
<figcaption>같은 저장 자료의 Lorentz 확장 실험입니다. 오른쪽은 (k/Re f)²와 Re ε(Re f)를 비교한 단순 추정의 오차입니다. 공진에서 0.05 이상 떨어진 표본도 1% 목표를 모두 만족하지 못합니다. 전체 복소 유전율이 검증되었다는 그림이 아닙니다.</figcaption>
</figure>

`run_k_points`는 **실수 k에서 복소 f**를 반환합니다. 반면 보통의 재료 스펙트럼 ε(f)는 실수 f에서 봅니다. 두 종류의 값을 섞으면 특히 허수부를 공정하게 비교할 수 없습니다. 엄밀한 모드 검산에는 같은 복소 주파수에서 모델을 평가하고, 격자 분산과 추출된 모드의 신뢰도를 함께 확인해야 합니다.

저장된 검산은 f > 0.02이며 두 공진 0.5와 1.1에서 각각 0.05보다 멀리 떨어진 193개 표본에 대해 **(k/Re f)²와 Re ε(Re f)**의 상대 차이를 계산했습니다. 중앙값 1.862%, 최대 37.176%로 목표 1%에 미달했습니다. 사후 Yee 분산 보정은 중앙값을 0.333%로 줄였지만 최대는 37.030%로 남았습니다. 보정은 사후 진단이며, 큰 편차의 모드가 무엇인지는 확인되지 않았습니다. 이 결과만으로 재료 모델이나 Meep 전체를 검증 또는 반박할 수 없습니다.

<h2 id="check">6. 이해 확인하기: 어떤 오차를 줄이고 있나요?</h2>

<details markdown="1">
<summary>왜 상수 index=1.5를 넣고 Sellmeier 식과 비교하면 안 되나요?</summary>

두 계산이 다른 재료를 사용하기 때문입니다. 먼저 동일한 ε(λ)를 맞추고, 그다음 격자 오차를 평가해야 합니다. 상수 index는 단일 파장 근사에는 쓸 수 있지만 넓은 대역의 분산을 표현하지 못합니다.

</details>

<details markdown="1">
<summary>해상도 200에서 석영 반사 검산이 통과하면 Lorentz 모드 역산도 검증된 것인가요?</summary>

아닙니다. 1D 석영 반사와 0D Bloch 모드 추출은 재료·관측량·오차 원인이 다릅니다. 각각의 기준을 따로 통과해야 합니다. 이 자료에서는 전자만 설정한 기준을 만족합니다.

</details>

<details markdown="1">
<summary>복소 모드 f의 허수부를 버리고 실수 주파수 ε와 비교하면 무엇을 놓치나요?</summary>

감쇠하는 모드의 복소 주파수와 정상상태 실수 주파수 응답의 차이를 놓칩니다. 단순 역산은 빠른 진단으로 쓰고, 정확한 비교는 같은 주파수 인수·시간 부호·단위에서 해야 합니다. 약하게 여기된 모드와 유한 시간 추출 오차도 확인해야 합니다.

</details>

다음 실험에서는 광원·측정면을 유지한 채 석영 해상도를 더 높여 보세요. 이후 [07편 위상 library]({{ site.baseurl }}/meta-atom/)로 돌아가 상수 굴절률을 쓰는 근사와 실제 분산을 포함하는 설계의 차이를 정리하면 됩니다. 각도도 바꾸려면 [18편 각도별 반사]({{ site.baseurl }}/angular-reflectance/)의 k∥ 정규화 조건을 함께 확인하세요.

<h2 id="reference">7. 코드와 참고 자료</h2>

- 실행 코드: [dispersive_quartz.py]({{ site.baseurl }}/code/dispersive_quartz.py), [material_dispersion.py]({{ site.baseurl }}/code/material_dispersion.py)
- 저장 결과: [석영 res 200]({{ site.baseurl }}/assets/meep/20/quartz-r200.json), [res 100]({{ site.baseurl }}/assets/meep/20/quartz-r100.json), [Lorentz 복소 모드]({{ site.baseurl }}/assets/meep/20/lorentz-modes.json)
- 검산: [요약]({{ site.baseurl }}/assets/meep/20/summary.json), [사후 진단]({{ site.baseurl }}/assets/meep/20/posthoc-numdisp.json), [출처·SHA-256]({{ site.baseurl }}/assets/meep/20/provenance.json), [그림 재생성 코드]({{ site.baseurl }}/assets/meep/20/render_results.py)
- 공식 Meep: [Material Dispersion](https://meep.readthedocs.io/en/latest/Python_Tutorials/Material_Dispersion/), [Materials](https://meep.readthedocs.io/en/latest/Materials/#material-dispersion), [Material Library](https://meep.readthedocs.io/en/latest/Materials/#materials-library)
- 계산의 원본: [material-dispersion.py](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/material-dispersion.py), [refl-quartz.py](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/refl-quartz.py). 본문은 저장된 계산을 교육용으로 재구성했으며 새 시뮬레이션을 수행하지 않았습니다.
