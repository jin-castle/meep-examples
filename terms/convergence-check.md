---
layout: term
permalink: /terms/convergence-check/
lang: ko
concept_id: convergence-check
title: "수렴 확인 — Meep 개념 사전"
term_label: "수렴 확인"
term_full: "Convergence check · 근사를 바꿔도 결과가 멈추는지"
axis: validation
axis_label: "검증"
order: 40
lesson_summary: "resolution, 실행 시간, PML 두께, 셀 여유처럼 계산이 둔 근사를 하나씩 두 배로 바꿔도 보고할 결과가 원하는 허용 오차 안에서 변하지 않는지 확인하는 절차입니다. 필요한 resolution을 미리 알려 주는 공식이 없어서 이 방법이 가장 확실합니다."
glance:
  - { k: "방법 (공식 FAQ)", v: "resolution, 실행 시간, PML 두께를 하나씩 두 배로 바꿔 보고할 값을 비교" }
  - { k: "판정", v: "보고할 양이 정한 허용 오차 안에서 멈추면 수렴. 허용 오차는 실행 전에 정한다" }
  - { k: "먼저 닫히는 것", v: "에너지 합(R+T+S)과 주파수. 개별 비율, Q, 효율, 최적화된 설계 성능은 늦게 닫힌다" }
  - { k: "이 사이트의 측정", v: "01~14편의 15개 양: 합·주파수는 0.3 % 안, Q 27 %, 박막 추출 효율 최대 54 %, 역설계 성능 18 %" }
  - { k: "보고 형식", v: "설정 2~3점과 각 값을 표로. 수렴하지 않은 양은 그렇다고 적는다" }
related:
  - { url: "/reference-subtraction/", label: "03 · 물체의 산란장은 어떻게 분리할까요?" }
  - { url: "/straight-waveguide/", label: "04 · 직선 도파로의 투과율은 어떻게 구할까요?" }
  - { url: "/ring-resonator/", label: "12 · 고리 공진기의 빛은 얼마나 오래 남을까요?" }
  - { url: "/extraction-efficiency/", label: "14 · 박막 속 빛은 얼마나 공기로 빠져나올까요?" }
calc_note: "그림은 새 계산이 아니라 01~14편의 수렴 표에 발행된 수치를 모은 것입니다(code/convergence_overview.py)."
tags: [meep, fdtd, convergence, resolution, validation]
---

<h2 id="what">1. 무엇인가</h2>

시뮬레이션은 연속인 문제를 유한한 격자, 유한한 셀, 유한한 시간으로 바꿔서 풉니다. 바꾼 것마다 오차가 생기고, 그 오차가 보고할 결과에 비해 작은지는 계산해 보기 전에는 알 수 없습니다. 수렴 확인은 근사 하나를 더 정밀하게 바꿔 다시 계산하고, 결과가 변하지 않는지 보는 절차입니다.

공식 FAQ는 필요한 resolution을 미리 알려 주는 간단한 공식은 없고, resolution을 두 배로 올려 관심 있는 답이 원하는 허용 오차 안에서 변하지 않는지 확인하는 것이 가장 믿을 만한 방법이라고 적습니다. 두 배로 확인할 대상으로는 resolution, Fourier 스펙트럼을 위한 실행 시간, PML 두께를 듭니다.

| 근사 | 바꾸는 설정 | 관련 개념 |
|---|---|---|
| 공간·시간 이산화 | `resolution` | [resolution]({{ site.baseurl }}/terms/resolution/) |
| 실행 시간 | `stop_when_fields_decayed`의 허용값, `until` | 종료 조건 |
| 열린 경계 | PML 두께 | [PML]({{ site.baseurl }}/terms/pml/) |
| 셀 크기 | 구조와 경계·monitor 사이 여유 | 배치 여유 |
| 주파수 표본 | `nfreq`, DFT 대역 | flux 스펙트럼 |
| 원통 좌표의 m 급수 | 더할 m의 개수 | 원통 좌표 |

<details markdown="1">
<summary>더 깊이 · 두 점으로 수렴한 값을 추정하기</summary>

오차가 격자 간격의 $p$제곱에 비례하면($Q(\Delta x) \approx Q_\infty + C\,\Delta x^p$) 간격 $\Delta x$와 $\Delta x/2$의 두 결과로 수렴값을 추정할 수 있습니다(Richardson 외삽).

$$Q_\infty \approx Q_{\Delta x/2} + \frac{Q_{\Delta x/2} - Q_{\Delta x}}{2^p - 1}$$

균일 매질의 수치 분산은 $p = 2$입니다([resolution]({{ site.baseurl }}/terms/resolution/)의 측정에서 두 배마다 오차가 1/4). 재료 경계가 계단으로 놓이는 오차는 $p$가 일정하지 않고 결과가 오르내릴 수 있어서 이 외삽이 맞지 않습니다. 공식 FAQ는 subpixel averaging이 수렴을 더 빠르고 매끄럽게 만든다고 적습니다. 세 점 이상이 단조롭게 줄어드는지 먼저 보고, 그렇지 않으면 외삽하지 말고 범위로 보고합니다.

</details>

<h2 id="why">2. 왜 필요한가</h2>

이 사이트의 01~14편이 수렴 표에 적은 값을 한 장에 모았습니다. 막대는 resolution을 올렸을 때 각 값이 몇 % 움직였는지입니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-convergence/01_overview.png" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-convergence/01_overview.png" alt="01~14편의 15개 결과가 두 resolution 사이에서 움직인 상대 변화(로그 축). 초록인 전력 합(06편 T+R 0.04 %, 03편 R+T+S 0.09 %)과 12편 공진 주파수(0.22 %)는 1 % 아래이고, 파랑인 개별 비율은 0.0004 %에서 13 %까지 퍼져 있으며, 12편 Q 27 %, 09편 역설계 투과율 18 %, 14편 박막 추출 효율 54 %가 가장 크다." loading="lazy">
  </a>
  <figcaption>01~14편 수렴 표의 발행 수치. 초록은 에너지 합, 파랑은 개별 비율·효율, 보라는 공진, 빨강은 최적화된 설계를 다시 잰 값입니다. 점선이 1 %입니다.</figcaption>
</figure>

세 가지가 보입니다.

- 합은 먼저 닫힙니다. 03편 원기둥의 R+T+S는 0.9988에서 0.9997로 0.09 % 움직였지만, 그 안의 R, T, Q_sca는 1.6~4.6 % 움직였습니다. resolution 20에서 Q_sca가 Mie 해석값과 0.1 % 맞았던 것은 우연에 가까웠습니다.
- 같은 계산에서 나온 양도 수렴 속도가 다릅니다. 12편 고리 공진기의 공진 주파수는 resolution 10 → 20에서 0.22 % 움직였지만 Q는 27 % 움직였고, 30에서는 다시 내려갔습니다(1675 → 2132 → 1610).
- 최적화된 설계와 얇은 구조가 가장 크게 움직입니다. 09편 역설계는 18 %, 14편 0.29 µm 박막 속 쌍극자의 추출 효율은 최대 54 % 달랐습니다.

<p class="lesson-note">그래서 수렴은 계산 전체가 아니라 보고할 양마다 따로 확인합니다. 에너지 합이 1로 닫혔다고 개별 값이 수렴했다고 볼 수 없습니다(<a href="{{ site.baseurl }}/terms/energy-conservation/">에너지 보존 검사</a>).</p>

<h2 id="meep-code">3. Meep 코드에서</h2>

```python
# code/straight_waveguide.py (04편): convergence, resolution x PML
for res, dpml in ((25, 1.0), (70, 1.0), (50, 0.5)):   # change one thing at a time
    sim, mon_in, mon_out = build(res, dpml)
    r = run_and_measure(sim, mon_in, mon_out)
    convergence.append({"resolution": res, "dpml": dpml, "T": float(r["T"][ic]), "R": float(r["R"][ic]),
                        "T_total": float(r["T_total"][ic]), "wall_s": time.time() - t0})
```

- 무엇: 기준(resolution 50, PML 1 µm)에서 resolution을 절반·1.4배로, PML을 절반으로 바꾼 run을 하나씩 더 돌리고, 같은 양(T, R, T_total)과 실행 시간을 표로 남깁니다.
- 왜: 한 번에 한 설정만 바꿔야 변화의 원인을 알 수 있습니다. 실행 시간을 함께 적어 두면 다음 계산에서 resolution을 고를 근거가 됩니다.
- 틀리면: 구조 run의 resolution만 바꾸고 reference run을 그대로 두면 resolution 차이가 아니라 정규화 차이를 보게 됩니다(09편). `build()`와 `run_and_measure()`가 reference까지 다시 계산하도록 두는 이유입니다.

수렴 표의 모양은 이렇게 남깁니다(04편).

| resolution | PML | T | R | 비고 |
|---|---|---|---|---|
| 50 | 1.0 | 1.000000 | 8.0 × 10⁻⁶ | 기준 |
| 25 | 1.0 | 0.999996 | 2.1 × 10⁻⁴ | resolution 절반 |
| 70 | 1.0 | 1.000000 | 1.4 × 10⁻⁶ | resolution 1.4배 |
| 50 | 0.5 | 1.000000 | 8.1 × 10⁻⁶ | PML 절반 |

<h2 id="in-examples">4. 예제에서의 쓰임</h2>

| 예제 | 바꾼 것 | 수렴한 것 | 수렴하지 않은 것 |
|---|---|---|---|
| [02 경계 조건]({{ site.baseurl }}/boundary-pml/) | resolution 12 → 24, PML 두께 | 경계 처리의 순위 | PML 반사 지표 바닥값(4.5 → 5.1 × 10⁻⁴, 원인 미확정) |
| [03 reference 빼기]({{ site.baseurl }}/reference-subtraction/) | resolution 20 → 40 | R+T+S | Q_sca 4.5 %, R 4.6 % |
| [04 직선 도파로]({{ site.baseurl }}/straight-waveguide/) | resolution 25·50·70, PML | T, R | — |
| [05 굽은 도파로]({{ site.baseurl }}/waveguide-bend-90/) | resolution 10·25·40, PML 1.5 | R 1.8 % | T 5.5 %, PML을 키우면 monitor 위치가 바뀌어 T 0.170 |
| [06 회절 격자]({{ site.baseurl }}/binary-grating/) | resolution 25 → 50 | 회절 효율 0.08 %, T+R | — |
| [12 고리 공진기]({{ site.baseurl }}/ring-resonator/) | resolution 10·20·30 | 공진 주파수 0.3 % 안 | Q (비단조) |
| [14 박막 광추출]({{ site.baseurl }}/extraction-efficiency/) | resolution 40·80, 원통·3D | 쌍극자 높이 h ≤ 0.4: 2~5 % | h ≥ 0.6: 18~54 % |

<h2 id="pitfalls">5. 돌아가는데 틀리는 경우</h2>

| 증상 | 원인 | 확인법 | 고침 |
|---|---|---|---|
| 두 점이 거의 같아 수렴했다고 판단했는데 세 번째 점에서 달라짐 | 계단 경계 때문에 결과가 오르내리며 우연히 가까웠음 | 세 점 이상을 표로 보고 단조로운지 확인 | 비단조이면 범위로 보고 (12편 Q, 03편 Q_sca) |
| 에너지 합은 1인데 개별 값이 해상도마다 다름 | 합은 오차가 서로 상쇄되어 먼저 닫힘 | 보고할 값 각각을 표에 | 합이 아니라 보고할 값으로 판정 |
| resolution을 바꾸면 결과가 바뀌는데 원인을 모름 | resolution과 PML·셀·monitor 위치를 함께 바꿈 | 바뀐 설정을 나열 | 한 번에 하나만 바꿈. PML 두께를 바꾸면 monitor가 같이 움직이는지도 확인 (05편) |
| 수렴 표의 변화가 들쭉날쭉함 | 실행 시간이 모자라 DFT가 덜 누적됨 | decay 허용값을 10배 조여 기준을 다시 계산 | 실행 시간 수렴을 resolution보다 먼저 확인 |
| 높은 resolution 쪽만 정규화가 이상함 | reference run을 다른 resolution에서 재사용 | 두 run의 resolution 비교 | resolution마다 reference를 다시 계산 |
| 대역 가장자리에서만 수렴하지 않음 | source power가 작아 반올림 오차가 커짐 | source 스펙트럼의 가장자리 power 확인 | 중심 대역 값으로 판정하거나 fwidth를 넓힘 |

<h2 id="inverse-design">6. inverse design에서</h2>

역설계에서는 수렴을 두 군데에서 따로 봅니다. 첫째는 gradient입니다. adjoint gradient를 유한 차분과 비교하는 검사도 resolution과 종료 조건에 따라 결과가 달라집니다. 한 2D bend 작업에서는 decay 허용값 10⁻³으로 둔 adjoint run이 일찍 멈춰 gradient가 유한 차분과 47 % 어긋났고, forward 결과는 정상이었습니다. 종료 조건의 수렴은 adjoint run 기준으로 확인합니다.

둘째는 최종 성능입니다. 최적화는 대개 낮은 resolution에서 돌리므로, 최종 설계를 높은 resolution의 새 시뮬레이션에서 다시 재야 보고할 수 있습니다. 09편은 resolution 10에서 0.780이던 성능을 20에서 0.639로 보고하고 "해상도 수렴이 확인되지 않음"이라고 적었습니다. 수렴하지 않은 결과도 그 사실과 함께 적으면 쓸모가 있습니다.

<h2 id="connections">7. 연결</h2>

- 함께 보면 좋은 개념: [resolution]({{ site.baseurl }}/terms/resolution/), [에너지 보존 검사]({{ site.baseurl }}/terms/energy-conservation/), [flux 정규화]({{ site.baseurl }}/terms/flux-normalization/), [PML]({{ site.baseurl }}/terms/pml/)
- 코드: [code/convergence_overview.py](https://github.com/jin-castle/meep-examples/blob/main/code/convergence_overview.py) · 모은 수치 [overview.json]({{ site.baseurl }}/assets/meep/terms-convergence/overview.json)
- Meep 공식 문서: [FAQ: Checking convergence](https://meep.readthedocs.io/en/master/FAQ/#checking-convergence) · [Subpixel Smoothing](https://meep.readthedocs.io/en/master/Subpixel_Smoothing/)
