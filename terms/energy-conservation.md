---
layout: term
permalink: /terms/energy-conservation/
lang: ko
concept_id: energy-conservation
title: "에너지 보존 검사 — Meep 개념 사전"
term_label: "에너지 보존 검사"
term_full: "Energy conservation check · 전력 수지"
axis: validation
axis_label: "검증"
order: 50
lesson_summary: "구조에 들어간 전력이 반사·투과·방사·흡수로 모두 나뉘었는지, 그 합이 입사 전력과 같은지 확인하는 검사입니다. 정규화·monitor 배치·종료 조건의 큰 실수를 빠르게 거르지만, 합이 맞는다고 개별 값이 맞는 것은 아닙니다."
glance:
  - { k: "정의", v: "무손실이면 R + T + (옆·방사 flux) = 1, 손실이 있으면 여기에 흡수 A를 더해 1" }
  - { k: "Meep에서", v: "모든 출구 면(또는 구조를 둘러싼 닫힌 flux box)의 flux를 같은 입사 전력으로 나눠 더한다" }
  - { k: "잡는 것", v: "정규화 불일치(합 > 1), 빠진 출구·이른 종료·PML 안 monitor(합 < 1)" }
  - { k: "못 잡는 것", v: "개별 값의 resolution 오차. 03편은 합 0.999인데 산란 단면적이 4.5 % 움직였다" }
  - { k: "이 사이트의 측정", v: "03편 R+T+S 0.9988 / 0.9997 · 06편 T+R 0.9994 / 0.9998 · 04편 T+R 1.0000" }
  - { k: "주의", v: "1 − T − R을 방사 손실로 정의하면(05편) 합은 항상 1이라 검사가 아니다" }
related:
  - { url: "/reference-subtraction/", label: "03 · 물체의 산란장은 어떻게 분리할까요?" }
  - { url: "/straight-waveguide/", label: "04 · 직선 도파로의 투과율은 어떻게 구할까요?" }
  - { url: "/waveguide-bend-90/", label: "05 · 도파로의 굽힘 반지름은 손실에 어떤 영향을 줄까요?" }
  - { url: "/binary-grating/", label: "06 · 격자의 회절 방향과 효율은 어떻게 구할까요?" }
tags: [meep, fdtd, energy-conservation, flux, validation]
---

<h2 id="what">1. 무엇인가</h2>

시간 조화 장에서 Poynting 정리는 닫힌 면 밖으로 나가는 평균 전력이 면 안의 source가 낸 전력에서 흡수된 전력을 뺀 값과 같다고 말합니다. 구조에 빛을 쏘는 계산이라면, 입사 전력은 반사·투과·옆으로의 산란이나 방사·흡수로 모두 나뉘어야 합니다.

$$R + T + S + A = 1,\qquad R = \frac{P_{\text{refl}}}{P_{\text{inc}}},\; T = \frac{P_{\text{tran}}}{P_{\text{inc}}},\; S = \frac{P_{\text{side}}}{P_{\text{inc}}}$$

$A$는 흡수 비율이고 무손실 구조에서는 0입니다. 에너지 보존 검사는 각 항을 따로 잰 뒤 합이 1인지 보는 것입니다. 각 항은 모두 같은 입사 전력 $P_{\text{inc}}$로 나눠야 하므로 [flux 정규화]({{ site.baseurl }}/terms/flux-normalization/)가 먼저입니다.

이 검사는 코드가 오류 없이 돌았지만 측정 장치가 틀린 경우를 빨리 거릅니다. 합이 1보다 크면 대개 분모가 틀렸거나 반사의 부호나 입사장 빼기를 잘못한 것입니다. 1보다 작으면 빠진 출구가 있거나, monitor가 소멸장 꼬리를 잘랐거나, 계산이 일찍 끝났거나, monitor가 PML 안에 있습니다.

<details markdown="1">
<summary>더 깊이 · 검사가 되는 합과 되지 않는 합</summary>

검사가 되려면 각 항을 독립적으로 재야 합니다. 05편 굽은 도파로는 T와 R만 재고 방사 손실을 $L = 1 - T - R$로 정의했습니다. 이 경우 $T + R + L$은 정의상 항상 1이므로 아무것도 확인하지 않습니다. L을 검사하려면 구조를 둘러싼 닫힌 flux box로 방사 전력을 직접 재야 합니다.

03편은 원기둥을 닫힌 box로 둘러싸고 네 면의 flux를 모두 쟀습니다. total 장의 box 밖 순 전력은 흡수 전력의 음수이므로, 무손실 원기둥에서는 0이어야 합니다. 이렇게 측정한 R, T, S의 합이 0.9988이었습니다. 반대로 산란장만의 flux를 box에서 더한 값(0.496)은 R+T+S보다 작아야 하는데, 산란장과 입사장의 간섭항이 빠지기 때문입니다.

</details>

<h2 id="why">2. 왜 필요한가</h2>

이 사이트의 예제는 결과를 보고하기 전에 이 검사를 먼저 했습니다.

| 예제 | 합 | 값 | 의미 |
|---|---|---|---|
| [03 원기둥 산란]({{ site.baseurl }}/reference-subtraction/) | R + T + S | 0.9988 (res 20), 0.9997 (res 40) | 닫힌 box의 네 면을 모두 잼 |
| [04 직선 도파로]({{ site.baseurl }}/straight-waveguide/) | T + R | 1.0000 | 반사원이 없는 기준 구조로 측정 장치 확인 |
| [06 회절 격자]({{ site.baseurl }}/binary-grating/) | T + R | 0.9994 (res 25), 0.9998 (res 50) | 모든 회절 차수를 한 주기 면으로 잼 |
| [05 굽은 도파로]({{ site.baseurl }}/waveguide-bend-90/) | T + R + L | 1 (정의) | 검사 아님. L = 1 − T − R |

하지만 합이 맞는 것과 결과가 맞는 것은 다릅니다. 03편에서 R+T+S는 resolution 20과 40에서 모두 1에 가깝게 닫혔지만, 그 안의 R은 4.6 %, 산란 단면적 Q_sca는 4.5 % 움직였습니다. 오차가 항 사이에서 서로 옮겨 가면 합은 그대로입니다. [수렴 확인]({{ site.baseurl }}/terms/convergence-check/)의 그림에서도 전력 합은 15개 양 중 가장 빨리 닫히는 쪽에 있습니다.

<p class="lesson-note">에너지 보존 검사는 필요조건입니다. 통과하면 정규화와 monitor 배치에 큰 실수가 없다는 뜻이고, 개별 값의 정확도는 resolution 수렴과 해석해 비교로 따로 확인합니다.</p>

<h2 id="meep-code">3. Meep 코드에서</h2>

```python
# code/reference_subtraction.py (03편): the closed flux box around the cylinder
REGIONS = {
    "left":   lambda: mp.FluxRegion(center=mp.Vector3(-xm, 0), size=mp.Vector3(0, 2 * ym)),
    "right":  lambda: mp.FluxRegion(center=mp.Vector3(+xm, 0), size=mp.Vector3(0, 2 * ym)),
    "top":    lambda: mp.FluxRegion(center=mp.Vector3(0, +ym), size=mp.Vector3(2 * xm, 0)),
    "bottom": lambda: mp.FluxRegion(center=mp.Vector3(0, -ym), size=mp.Vector3(2 * xm, 0), weight=-1),
}
```

- 무엇: 원기둥을 둘러싼 네 면의 flux monitor입니다. 아래 면에 `weight=-1`을 주어 네 면 모두 바깥 방향이 양수가 되게 합니다.
- 왜: Meep의 flux는 좌표의 양의 방향이 기준이라, 닫힌 box에서는 면마다 바깥 방향 부호를 맞춰야 합이 "box 밖으로 나간 전력"이 됩니다.
- 틀리면: 부호를 맞추지 않으면 위·아래 면이 서로 상쇄되어 옆 산란 S가 0에 가깝게 나오고, 합이 1보다 작아집니다.

```python
# total-field budget: flux DIFFERENCES to the empty run (exact by energy conservation)
R = -(tot["left"] - inc_side["left"]) / inc                            # backward: -x is outward on the left
T = tot["right"] / inc                                                 # what a detector behind the cylinder sees
S = ((tot["top"] - inc_side["top"]) + (tot["bottom"] - inc_side["bottom"])) / inc   # sideways, both signs outward
conservation = sum(outward(tot).values()) / inc                        # total field: must be 0 (lossless)
```

- 무엇: 물체 없는 run의 각 면 flux(`inc_side`)를 빼서 R과 S를 구하고, 모두 같은 입사 전력 `inc`로 나눕니다. `conservation`은 total 장이 box 밖으로 낸 순 전력입니다.
- 왜: 무손실 원기둥이면 `conservation`은 0이고 R + T + S는 1입니다. 두 값이 서로 독립적인 검사가 됩니다.
- 틀리면: 입사 전력을 면마다 다른 값으로 나누면 합이 1을 벗어납니다.

<h2 id="in-examples">4. 예제에서의 쓰임</h2>

| 예제 | 어떻게 쟀나 | 검사로서의 의미 |
|---|---|---|
| [01 점원과 선원]({{ site.baseurl }}/point-line-source/) | 진공 점원을 둘러싼 네 면 | 각 면 0.25로, 합과 대칭을 함께 확인 |
| [03 reference 빼기]({{ site.baseurl }}/reference-subtraction/) | 닫힌 box, total과 산란장 두 가지 | R + T + S 0.999, 산란장 flux 합 0.496 < 0.999 |
| [04 직선 도파로]({{ site.baseurl }}/straight-waveguide/) | 입력·출력 면 | T + R = 1.0000이 측정 장치의 기준 |
| [05 굽은 도파로]({{ site.baseurl }}/waveguide-bend-90/) | 입력·출력 면, L = 1 − T − R | 검사가 아니라 L의 정의 |
| [06 회절 격자]({{ site.baseurl }}/binary-grating/) | 한 주기 면 전체의 반사·투과 | 모든 회절 차수의 합 0.9994 |

<h2 id="pitfalls">5. 돌아가는데 틀리는 경우</h2>

| 증상 | 원인 | 확인법 | 고침 |
|---|---|---|---|
| 합이 1보다 큼 | 분모가 다른 reference, 반사 부호 누락, 반사면에서 입사장을 빼지 않음 | 각 항의 분모와 부호를 출력 | 같은 reference로 나누고 반사면에만 입사장 빼기 ([flux 정규화]({{ site.baseurl }}/terms/flux-normalization/)) |
| 무손실인데 합이 1보다 작음 | 옆으로 나가는 출구를 재지 않음 | 구조를 닫힌 box로 둘러 다시 잼 | 모든 출구에 monitor |
| 합이 0.9 근처에서 멈춤 | monitor 면이 모드의 소멸장 꼬리를 자름 | monitor 폭을 늘려 비교 | 면을 cladding까지 넓힘 |
| 합이 실행할 때마다 다름 | 장이 다 빠져나가기 전에 종료 | decay 허용값을 조여 다시 계산 | 투과면 근처 점에서 감쇠를 확인하고 종료 |
| PML 두께를 바꾸면 합이 변함 | monitor가 PML 안이나 경계에 걸침 | [PML]({{ site.baseurl }}/terms/pml/) 안쪽 경계와 monitor 끝의 거리 계산 | monitor를 PML 밖으로 |
| 손실 재료가 있는데 합이 1 | 흡수를 따로 재지 않고 나머지를 흡수로 둠 | 흡수 전력을 닫힌 box의 total flux로 직접 잼 | A를 독립적으로 재서 합에 넣음 |
| 합은 1인데 resolution을 올리면 값이 바뀜 | 오차가 항 사이에서 옮겨 감 | 보고할 값 각각의 수렴 표 | [수렴 확인]({{ site.baseurl }}/terms/convergence-check/) |

<h2 id="inverse-design">6. inverse design에서</h2>

역설계의 목적함수는 보통 출력 포트 하나의 전력입니다. 최적화기는 그 값만 올리므로, 반사·다른 포트·방사로 간 전력이 얼마인지 모른 채 설계가 끝날 수 있습니다. 최종 설계는 모든 출구를 따로 재는 새 시뮬레이션으로 다시 측정하고, 합이 1인지 확인한 뒤 보고합니다. 09편은 mode 1 투과율 0.7801과 전체 flux 투과율을 함께 쟀고, 그 차이 약 0.024를 출력면을 지났지만 mode 1로 잡히지 않은 몫으로 적었습니다.

목적함수의 정규화 관례가 다른 함수와 섞이면 투과율이 1을 넘는 일도 있습니다. 09편에서 J를 다른 함수로 잰 입력 전력으로 나누면 1.056이 나왔습니다. 에너지 보존 검사에서 1을 넘는 값이 보이면 구조를 의심하기 전에 분자와 분모를 같은 함수로 쟀는지 확인합니다.

<h2 id="connections">7. 연결</h2>

- 함께 보면 좋은 개념: [flux 정규화]({{ site.baseurl }}/terms/flux-normalization/), [수렴 확인]({{ site.baseurl }}/terms/convergence-check/), [PML]({{ site.baseurl }}/terms/pml/)
- 측정과 해설: [03 · reference 빼기]({{ site.baseurl }}/reference-subtraction/) · [06 · 회절 격자]({{ site.baseurl }}/binary-grating/)
- Meep 공식 문서: [Introduction: Transmittance/reflectance spectra](https://meep.readthedocs.io/en/master/Introduction/#transmittancereflectance-spectra) · [Basics: Mie scattering of a lossless dielectric sphere](https://meep.readthedocs.io/en/master/Python_Tutorials/Basics/#mie-scattering-of-a-lossless-dielectric-sphere) · [Basics: Absorbed power density map of a lossy cylinder](https://meep.readthedocs.io/en/master/Python_Tutorials/Basics/#absorbed-power-density-map-of-a-lossy-cylinder)
