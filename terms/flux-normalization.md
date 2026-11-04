---
layout: term
permalink: /terms/flux-normalization/
lang: ko
title: "Flux 정규화 — Meep 개념 사전"
term_label: "Flux 정규화"
term_full: "Flux monitor normalization · 2-run 정규화와 반사 빼기"
axis: block
axis_label: "Meep 블록"
order: 30
lesson_summary: "flux monitor가 돌려주는 값은 source 세기와 스펙트럼에 따라 정해지는 임의 단위입니다. 투과율과 반사율이 되려면 같은 조건의 reference run에서 잰 입사 전력으로 나누고, 반사면에서는 입사장을 먼저 빼야 합니다."
glance:
  - { k: "Meep 코드", v: "`add_flux` → `get_fluxes` · `get_flux_data` → (다음 run에서) `load_minus_flux_data`" }
  - { k: "정의", v: "T(f) = P_tran(f) / P_inc(f), R(f) = −P_refl(f) / P_inc(f). P_refl은 입사장을 뺀 반사면의 flux" }
  - { k: "필요한 것", v: "구조만 뺀 reference run. 셀·resolution·source·monitor 위치·배경 재료가 같아야 함" }
  - { k: "부호", v: "flux는 좌표의 양의 방향이 +. −x로 돌아가는 반사는 음수로 나와 −1을 곱함" }
  - { k: "이 사이트의 측정", v: "04편 직선 도파로 T 1.0000, R 8 × 10⁻⁶ · 05편 sharp bend T 0.20, R 0.22, 방사 0.58 · 03편 원기둥 R + T + S 0.999" }
  - { k: "먼저 의심할 것", v: "T > 1이나 R < 0이면 구조보다 reference 불일치, 대역 가장자리, 이른 종료를 먼저 본다" }
related:
  - { url: "/reference-subtraction/", label: "03 · 물체의 산란장은 어떻게 분리할까요?" }
  - { url: "/straight-waveguide/", label: "04 · 직선 도파로의 투과율은 어떻게 구할까요?" }
  - { url: "/waveguide-bend-90/", label: "05 · 도파로의 굽힘 반지름은 손실에 어떤 영향을 줄까요?" }
  - { url: "/bend-inverse/", label: "09 · 도파로의 굽힘 구조는 어떻게 역설계할까요?" }
tags: [meep, fdtd, flux, normalization, transmission, reflection]
---

<h2 id="what">1. 무엇인가</h2>

`sim.add_flux(fcen, df, nfreq, mp.FluxRegion(...))`는 계산이 도는 동안 한 면 위의 접선 전기장과 자기장을 주파수마다 Fourier 변환해 누적합니다. 계산이 끝나면 `mp.get_fluxes(flux)`가 그 면을 지나는 Poynting flux를 주파수별로 돌려줍니다.

$$P(f) \propto \operatorname{Re}\int_{\text{면}} \big(\tilde{\mathbf{E}}^{*}(f)\times\tilde{\mathbf{H}}(f)\big)\cdot\hat{\mathbf{n}}\,dA$$

이 값에는 source의 세기와 스펙트럼 $|s(f)|^2$가 곱해져 있습니다. Gaussian source는 중심 주파수에서 멀어질수록 power가 작으므로, 같은 구조에서도 주파수마다 flux가 다릅니다. 공식 FAQ의 말대로 Poynting flux는 차원이 있는 양이라 어떤 값(양수든 음수든)도 될 수 있습니다. 구조가 빛에 한 일만 남기려면 구조가 없는 계산의 flux로 나눠 $|s(f)|^2$를 지웁니다. 이것이 2-run 정규화입니다.

반사는 한 단계가 더 필요합니다. 반사면은 source와 구조 사이에 있어서 입사파와 반사파가 같은 면을 지납니다. flux는 장에 대해 2차라서 두 파의 flux가 그냥 더해지지 않고 교차항이 생깁니다.

$$P[\mathbf{E}_{\text{inc}}+\mathbf{E}_{\text{r}}] = P[\mathbf{E}_{\text{inc}}] + P[\mathbf{E}_{\text{r}}] + (\text{교차항})$$

그래서 Meep은 flux를 빼지 않고 장을 뺍니다. reference run에서 반사면의 Fourier 변환 장을 `get_flux_data`로 저장해 두고, 구조가 있는 run에서 같은 monitor를 만든 직후 `load_minus_flux_data`로 그 장의 부호를 바꿔 넣습니다. 이후 누적되는 값은 $\tilde{\mathbf{E}}-\tilde{\mathbf{E}}_{\text{inc}}$, 곧 반사된(산란된) 장만의 flux입니다. 두 run에서 반사면은 source에 대해 같은 위치에 있어야 위상이 맞습니다.

<details markdown="1">
<summary>더 깊이 · 언제 flux 빼기와 장 빼기가 같아지는가</summary>

입사파와 반사파가 같은 도파로 모드의 정방향·역방향이고 손실이 없으면, 교차항의 실수부가 0이 되어 $P_{\text{total}} = P_{\text{inc}} - P_{\text{r}}$입니다. 이 경우에는 flux를 빼도 반사율이 나옵니다. 여러 모드가 섞이거나, 산란파가 입사파와 같은 방향으로도 퍼지거나(03편의 원기둥), monitor가 근접장 영역에 있으면 교차항이 남습니다. 03편은 닫힌 box에서 산란장만의 flux를 더해 산란 단면적 Q_sca = 2.515를 얻었고 2D Mie 해석값 2.513과 비교했습니다. 같은 box로 total flux를 재면 box 밖으로 나가는 순 전력, 곧 흡수 전력의 음수가 나옵니다. 무손실 원기둥에서는 0이라 산란에 대해 아무것도 알려 주지 않습니다.

전체 flux와 특정 모드의 power도 다른 양입니다. flux monitor는 면을 지나는 모든 power(모든 모드와 방사)를 셉니다. 특정 모드만 보려면 `get_eigenmode_coefficients`로 모드 계수 $|a|^2$를 잽니다. 04편 직선 도파로에서는 두 값이 1.0000으로 같았고, 05편 bend에서는 둘의 차이가 방사·고차 모드로 간 몫입니다.

</details>

<h2 id="why">2. 왜 필요한가</h2>

정규화 없이 `get_fluxes`를 출력하면 source 진폭을 두 배로 했을 때 값이 네 배가 됩니다. 이 숫자로는 구조끼리 비교할 수 없습니다. reference로 나눈 뒤에야 에너지 보존 같은 물리적 검사가 가능해집니다.

| 계산 | 정규화된 결과 | 검산 |
|---|---|---|
| [04 직선 도파로]({{ site.baseurl }}/straight-waveguide/) | T = 1.0000, R = 8.0 × 10⁻⁶ (1.55 µm) | 반사원이 없으니 T + R = 1이어야 함 |
| [05 sharp bend]({{ site.baseurl }}/waveguide-bend-90/) | T = 0.20, R = 0.22, 방사 = 1 − T − R = 0.58 | radius 0.70 µm에서 T 0.99로 회복 |
| [03 유전체 원기둥]({{ site.baseurl }}/reference-subtraction/) | R = 0.082, T = 0.674, 옆 S = 0.243, 합 0.999 | 무손실이니 합이 1 |

04편이 맞아야 하는 답(T = 1)으로 먼저 측정 장치를 확인하는 이유가 여기에 있습니다. 직선에서 T가 1이 아니면 구조가 아니라 source·monitor·정규화 설정이 틀린 것입니다.

<h2 id="meep-code">3. Meep 코드에서</h2>

05편 bend의 두 run입니다. run 1은 직선 도파로(구조 없음에 해당하는 reference), run 2는 bend입니다.

```python
# code/bend90.py (05편), RUN 1: straight guide -> P_in and the incident flux data
sim = make_sim(bend=False, resolution=resolution, dpml=dpml)
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
tran0 = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["tran_straight_x"], ycen), size=span))
sim.run(until_after_sources=mp.stop_when_fields_decayed(
            25, mp.Ez, mp.Vector3(p["tran_straight_x"], ycen), 1e-6))
P_in = np.array(mp.get_fluxes(tran0))        # what actually travels down the guide
refl_data = sim.get_flux_data(refl)          # incident fields at the reflection plane
```

- 무엇: 반사면 `refl`과 투과면 `tran0` 두 monitor를 두고, 장이 충분히 줄 때까지 돌린 뒤 입사 전력 `P_in`과 반사면의 입사장 `refl_data`를 저장합니다.
- 왜: 분모 `P_in`은 source 근처가 아니라 도파로를 따라 실제로 진행한 전력이어야 합니다. 선원(line source)은 일부를 도파로 밖으로 방사하므로 source 바로 앞에서 재면 그 몫까지 셉니다.
- 틀리면: 종료를 너무 이르게 하면 Fourier 변환이 덜 누적되어 `P_in` 자체가 틀립니다. 이 오차는 run 2의 T에 그대로 곱해집니다.

```python
# RUN 2: the bend (same cell, resolution, source, monitor positions)
sim = make_sim(bend=True, radius=radius, resolution=resolution, dpml=dpml)
refl = sim.add_flux(fcen, df, nfreq, mp.FluxRegion(center=mp.Vector3(p["refl_x"], ycen), size=span))
sim.load_minus_flux_data(refl, ref["refl_data"])  # subtract the incident part -> reflection only
tran = sim.add_flux(fcen, df, nfreq,
                    mp.FluxRegion(center=mp.Vector3(xcen, p["tran_bend_y"]), size=mp.Vector3(w + 2, 0)))
sim.run(until_after_sources=mp.stop_when_fields_decayed(25, mp.Ez, mp.Vector3(*decay_pt), 1e-6))
T = np.array(mp.get_fluxes(tran)) / ref["P_in"]      # transmitted fraction
R = -np.array(mp.get_fluxes(refl)) / ref["P_in"]     # backward flux is negative -> flip the sign
L = 1.0 - T - R                                      # what is left: radiated out at the corner
```

- 무엇: 반사면 monitor를 run 1과 같은 자리에 만들고 곧바로 입사장을 뺍니다. 투과면은 bend 출구에 새로 둡니다. 둘 다 run 1의 `P_in`으로 나눕니다.
- 왜: `load_minus_flux_data`는 같은 모양의 monitor에만 넣을 수 있고, 위상이 맞으려면 source에 대한 위치가 같아야 합니다. 반사는 −x로 가므로 flux가 음수로 나와 −1을 곱합니다.
- 틀리면: 투과면에도 `load_minus_flux_data`를 걸면 total flux가 아니라 산란장 flux가 나옵니다. run 2에서 셀이나 resolution을 바꾸면 배열 크기가 맞지 않아 실패하거나, 실패하지 않더라도 엉뚱한 장을 뺍니다(03편).

<h2 id="in-examples">4. 예제에서의 쓰임</h2>

| 예제 | 분모(reference) | 특징 |
|---|---|---|
| [01 점원과 선원]({{ site.baseurl }}/point-line-source/) | 같은 run에서 source를 둘러싼 네 면의 합 | reference run 없이 비율만 봄. 점원은 각 면 0.25 |
| [03 reference 빼기]({{ site.baseurl }}/reference-subtraction/) | 물체 없는 run의 입사 flux와 입사장 | 1D Fresnel 비교(오차 1.6 × 10⁻⁴), 닫힌 box의 산란장 flux로 Q_sca |
| [04 직선 도파로]({{ site.baseurl }}/straight-waveguide/) | 같은 run의 입력면 | 전체 flux와 mode 1 power를 함께 기록 |
| [05 bend]({{ site.baseurl }}/waveguide-bend-90/) | 직선 도파로 run | 위 코드. resolution·PML마다 reference를 다시 계산해 캐시 |
| [06 회절 격자]({{ site.baseurl }}/binary-grating/) | 격자를 빼고 유리로 채운 셀 | source가 유리 안에 있으므로 reference 배경도 유리 |
| [07 meta-atom]({{ site.baseurl }}/meta-atom/) | 막대 폭 w = 0인 빈 단위 셀 | 투과 위상 arg t(w)도 이 reference에 대한 상대값 |
| [09 bend 역설계]({{ site.baseurl }}/bend-inverse/) | 직선 도파로 run의 mode 1 power | 최종 설계를 새 `Simulation`에서 같은 함수로 다시 잼 |

<h2 id="pitfalls">5. 돌아가는데 틀리는 경우</h2>

공식 FAQ는 반사율·투과율이 0보다 작거나 1보다 큰 원인을 다섯 가지로 듭니다. 이 사이트의 글에서 겪은 경우를 더해 증상별로 정리했습니다.

| 증상 | 원인 | 확인법 | 고침 |
|---|---|---|---|
| T > 1 또는 R + T > 1 | reference와 구조 run이 비교 가능하지 않음(셀, resolution, source, monitor 위치, 배경 재료 중 하나가 다름) | 두 run의 설정을 나란히 출력해 비교 | 같은 설정으로 reference를 다시 계산. 다른 resolution의 reference를 재사용하지 않음 |
| 대역 가장자리에서 값이 튀거나 1을 넘음 | 가장자리 주파수의 source power가 너무 작아 반올림 오차가 커짐 | source 스펙트럼에서 가장자리의 상대 power 확인 | `fwidth`를 측정 대역과 비슷하게, 가장자리 값은 보고하지 않음 |
| decay 허용값을 조이면 T가 변함 | 장이 다 빠져나가기 전에 종료해 Fourier 변환이 덜 누적됨 | 허용값을 10배 조여 다시 실행 | 투과면 근처 점에서 `stop_when_fields_decayed`, 또는 `stop_when_dft_decayed` |
| 반사율이 음수 | −1을 곱하지 않음, 또는 monitor가 source 뒤에 있음 | 반사면이 source와 구조 사이에 있는지 확인 | 위치를 고치고 −flux로 계산 |
| 투과율이 실제보다 작고 1 − T − R이 이상하게 큼 | 투과면에도 `load_minus_flux_data`를 걸어 산란장만 잼 | 어느 monitor에 데이터를 넣었는지 확인 | 반사면에만 사용 |
| 직선 reference인데 T가 1에서 벗어남 | reference의 monitor가 source에 너무 가까워 도파로 밖 방사까지 셈 | monitor를 source에서 멀리 옮겨 `P_in` 비교 | 충분히 떨어뜨리거나 `EigenModeSource` 사용 |
| 구조 근처 monitor에서 값이 위치마다 다름 | monitor가 근접장·소멸장 영역에 있음 | monitor를 조금씩 옮겨 비교 | 구조에서 더 떨어뜨림 |
| monitor를 옮기지 않았는데 PML 두께를 바꾸면 값이 변함 | monitor가 PML 안이나 경계에 걸침 | [PML]({{ site.baseurl }}/terms/pml/) 안쪽 경계와 monitor 끝의 거리 계산 | PML 밖으로 이동 |
| 모드 투과율이 1을 넘음 | 정규화 관례가 다른 두 함수의 값을 섞음(`mpa.EigenmodeCoefficient`의 \|a\|²과 `get_eigenmode_coefficients`의 \|α\|²) | 분자와 분모를 어떤 함수로 쟀는지 확인 | 같은 함수로 다시 측정 (09편) |

<h2 id="inverse-design">6. inverse design에서</h2>

adjoint 최적화의 목적함수는 보통 flux가 아니라 모드 계수의 제곱 $|a|^2$나 특정 위치의 장(`mpa.EigenmodeCoefficient`, `mpa.FourierFields`)입니다. 이 값은 최적화기 쪽 정규화 관례를 따르므로 투과율이 아닙니다. 09편에서 최적화가 끝났을 때 목적함수는 J = 222.4였고, 이를 다른 함수로 잰 입력 power 210.6으로 나누면 1.056이 됩니다. 1보다 큰 투과율이 아니라 관례가 다른 두 수를 나눈 결과입니다. 09편은 최종 설계를 새 `Simulation`에 넣고 reference와 같은 `get_eigenmode_coefficients`로 다시 재서 mode 1 투과율 0.7801을 보고했습니다.

목적함수를 상수(reference 입력 power)로 나눠도 gradient의 방향은 바뀌지 않고 크기만 바뀝니다. 그래서 정규화는 최적화 중에는 걸음 크기에만 영향을 주고, 보고할 때는 결과의 의미를 정합니다. 두 용도를 섞지 않는 것이 핵심입니다.

종료 조건은 더 엄격해집니다. adjoint run도 monitor의 Fourier 변환 장으로 gradient를 만들기 때문에, forward run에서 충분했던 decay 허용값이 adjoint에서는 모자랄 수 있습니다. 한 2D bend 역설계 작업에서 decay 허용값 10⁻³으로 둔 adjoint run이 일찍 멈춰 gradient가 유한 차분과 47 % 어긋났고, forward 결과는 정상이었습니다. 허용값은 adjoint run을 기준으로 정하고, gradient를 유한 차분과 비교해 확인합니다.

<h2 id="connections">7. 연결</h2>

- 함께 보면 좋은 개념: [PML]({{ site.baseurl }}/terms/pml/) (monitor와 PML의 간격), [Courant 조건]({{ site.baseurl }}/terms/courant-condition/)
- 측정과 해설: [03 · reference 빼기]({{ site.baseurl }}/reference-subtraction/) · [05 · 2-run 정규화]({{ site.baseurl }}/waveguide-bend-90/)
- Meep 공식 문서: [Basics: Transmittance spectrum of a waveguide bend](https://meep.readthedocs.io/en/master/Python_Tutorials/Basics/#transmittance-spectrum-of-a-waveguide-bend) · [Introduction: Transmittance/reflectance spectra](https://meep.readthedocs.io/en/master/Introduction/#transmittancereflectance-spectra) · [Python API: Flux spectra](https://meep.readthedocs.io/en/master/Python_User_Interface/#flux-spectra) · [FAQ: reflectance/transmittance below zero or above one](https://meep.readthedocs.io/en/master/FAQ/#why-are-my-reflectancetransmittance-values-less-than-zero-andor-greater-than-one)
