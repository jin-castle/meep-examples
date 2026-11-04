---
layout: term
permalink: /terms/pml/
lang: ko
title: "PML (Perfectly Matched Layer) — Meep 개념 사전"
term_label: "PML"
term_full: "Perfectly Matched Layer · 완전 정합층"
axis: numerics
axis_label: "수치해석"
order: 20
lesson_summary: "유한한 계산 상자의 가장자리에서 나가는 파를 되돌려 보내지 않고 감쇠시키는 영역입니다. 흡수 재료가 아니라 좌표를 복소수로 늘리는 수학적 장치이고, 셀 안쪽 가장자리를 차지합니다."
glance:
  - { k: "Meep 코드", v: "`boundary_layers=[mp.PML(thickness)]`" }
  - { k: "기본값", v: "두께는 기본값 없음 · `R_asymptotic=1e-15` · 전도도는 층 안에서 2차(u²)로 켜짐" }
  - { k: "자리", v: "셀 가장자리에서 안쪽으로 두께 d. 셀을 키우지 않으므로 PML 없는 영역은 `cell − 2d`" }
  - { k: "두께 경험칙", v: "가장 긴 파장의 절반 안팎에서 시작해 두 배씩 늘리며 결과가 바뀌지 않는지 확인 (공식 문서)" }
  - { k: "이 사이트의 측정", v: "02편, 2D 진공 점원의 반사 지표: 경계층 없음 1.03 · Absorber 1 µm 1.9 × 10⁻² · PML 1 µm 4.5 × 10⁻⁴" }
  - { k: "대신 쓰는 것", v: "PML이 실패하는 경우(주기 매질, backward-wave 모드, 비스듬히 닿는 도파로, 분산 재료와 겹침)는 `mp.Absorber`" }
related:
  - { url: "/boundary-pml/", label: "02 · 계산 경계의 반사는 어떻게 줄일까요?" }
  - { url: "/waveguide-bend-90/", label: "05 · 도파로의 굽힘 반지름은 손실에 어떤 영향을 줄까요?" }
  - { url: "/binary-grating/", label: "06 · 격자의 회절 방향과 효율은 어떻게 구할까요?" }
  - { url: "/cavity-ldos/", label: "11 · 두 거울 사이에서 쌍극자의 방출은 어떻게 달라질까요?" }
tags: [meep, fdtd, pml, absorber, boundary]
---

<h2 id="what">1. 무엇인가</h2>

FDTD는 유한한 상자 안의 장만 계산합니다. 상자 가장자리에 아무것도 지정하지 않으면 Meep은 그곳을 완전 도체 벽으로 다룹니다. 접선 전기장이 0인 벽이라 도착한 파가 전부 되돌아옵니다. 실제로 열린 공간에 놓인 소자를 계산하려면 가장자리에 닿은 파가 돌아오지 않고 사라져야 합니다.

PML은 그 일을 하는 경계 영역입니다. 층 안에서 경계에 수직인 좌표 $x$를 복소수 좌표로 바꿉니다.

$$\tilde{x} = x + \frac{i}{\omega}\int^{x}\sigma(x')\,dx'$$

$\sigma(x)$는 층 안에서 0부터 서서히 커지는 함수입니다. 평면파 $e^{i(k_x x - \omega t)}$에 이 치환을 넣으면 진동은 그대로이고 크기만 줄어듭니다.

$$e^{ik_x \tilde{x}} = e^{ik_x x}\,\exp\!\left(-\frac{k_x}{\omega}\int^{x}\sigma\,dx'\right)$$

연속 방정식에서는 층 경계면의 임피던스가 바깥과 정확히 맞기 때문에 주파수와 입사각에 관계없이 반사가 0입니다. 이름의 matched가 이 뜻입니다. 공식 문서는 PML을 이론상 모든 주파수와 입사각의 전자기파를 반사 없이 흡수하는 매질로 설명합니다.

격자에서는 사정이 다릅니다. $\sigma$가 갑자기 켜지면 그 불연속에서 수치 반사가 생기므로, Meep은 층 깊이 $u$ (0 → 1)에 대해 $\sigma \propto u^2$로 천천히 켭니다. 전체 세기는 해상도나 두께가 무한한 극한에서 남는 반사가 `R_asymptotic` = 10⁻¹⁵이 되도록 정합니다. 그래서 실제로 남는 반사는 대부분 이 이산화 반사이고, 층이 두꺼울수록 $\sigma$가 완만하게 변해 줄어듭니다. PML 두께를 늘리는 것은 흡수를 세게 하는 일이 아니라 켜지는 기울기를 완만하게 하는 일입니다.

<details markdown="1">
<summary>더 깊이 · 감쇠가 각도와 모드 종류에 따라 달라지는 이유</summary>

위 식의 감쇠율은 $k_x/\omega$에 비례합니다. 굴절률 $n$인 매질에서 입사각 $\theta$로 들어오는 파는 $k_x/\omega = n\cos\theta / c$이므로, 경계를 스치듯 지나가는 파($\theta \to 90°$)는 같은 두께에서 덜 감쇠합니다. 연속 방정식에서는 반사가 여전히 0이지만, 감쇠가 약하면 층 끝의 금속 벽에서 돌아오는 성분이 커지고 이산화 반사의 비중도 커집니다. 점원이 넓은 각도로 퍼지는 02편 실험에서 셀 모서리 쪽이 가장 까다로운 이유입니다.

소멸파(evanescent wave) $e^{-\kappa x}$는 $k_x = i\kappa$입니다. 같은 치환을 넣으면 위상만 바뀌고 추가 감쇠가 생기지 않습니다. 표준 PML은 소멸파를 더 빨리 없애 주지 못하므로, 도파로나 공진기의 소멸장이 PML에 닿지 않게 셀을 충분히 크게 잡으라는 것이 공식 문서의 권고입니다.

`mp.Absorber`는 같은 $u^2$ 프로파일로 전기·자기 전도도를 함께 켜는 스칼라 흡수층입니다(1D를 제외하면 PML이 아닙니다). 정합 조건이 없어 층 입구에서 반사가 생기므로 같은 두께에서 PML보다 반사가 크고, 보통 더 두껍게 씁니다.

</details>

<h2 id="why">2. 왜 필요한가</h2>

경계에서 돌아온 파는 계산 결과에 실제 소자에는 없는 반사원을 하나 더합니다. 투과율, 방사 손실, 공진기의 Q, 점광원의 방출률이 모두 이 가짜 반사의 영향을 받습니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/terms-pml/01_anim_pml.gif" data-lightbox>
    <img src="{{ site.baseurl }}/assets/meep/terms-pml/01_anim_pml.gif" alt="2D 진공, 중앙 Ez 점원(파장 1.55 µm), resolution 12, 내부 8 × 8 µm. 위 줄은 Ez: 경계층 없음은 벽에서 돌아온 파가 내부를 채우고, Absorber와 PML은 바깥 1 µm 층에서 파가 줄어든다. 아래 줄은 경계가 돌려보낸 장(큰 참조 셀을 뺀 값)을 50배로 키운 것: 경계층 없음은 포화, Absorber는 층 입구에서 반사된 무늬가 남고, PML은 거의 비어 있다." data-animation-src="{{ site.baseurl }}/assets/meep/terms-pml/01_anim_pml.gif" data-static-src="{{ site.baseurl }}/assets/meep/terms-pml/01_anim_pml.png">
  </a>
  <button class="animation-toggle" type="button" hidden>애니메이션 정지</button>
  <figcaption>같은 점원을 세 경계에서 계산했습니다(위 줄 Ez, 색 범위 같음). 아래 줄은 경계가 돌려보낸 장만 보려고, 경계가 닿지 않는 큰 참조 셀의 장을 빼고 50배로 키운 것입니다. Absorber는 층 입구에서 생긴 반사가 50배에서 또렷하게 보이고(t &gt; 20의 최대 지표 4.5 × 10⁻²), PML은 같은 배율에서도 거의 보이지 않습니다(9.5 × 10⁻⁵). 지표는 02편과 같은 정의이지만 source 위치와 시각이 달라 02편 표의 수와 직접 비교하지는 않습니다.</figcaption>
</figure>
 02편은 같은 점원과 같은 셀에서 경계 처리만 바꿔 경계가 돌려보낸 장을 쟀습니다.

| 경계 처리 | 반사 지표 (02편, 2D 진공, res 12) |
|---|---|
| 경계층 없음 (Meep 기본 벽) | 1.03 |
| `mp.Absorber(1.0)` | 1.9 × 10⁻² |
| `mp.PML(0.25)` | 1.5 × 10⁻² |
| `mp.PML(0.5)` | 7.9 × 10⁻⁴ |
| `mp.PML(1.0)` | 4.5 × 10⁻⁴ |
| `mp.PML(2.0)` | 4.2 × 10⁻⁴ |

<p class="lesson-note">이 지표는 경계가 돌려보낸 장의 RMS를 입사 장의 시간 최대 RMS로 나눈 값입니다. 전력 반사율이 아닙니다. 0.5 µm 이후 4 × 10⁻⁴ 근처에서 더 줄지 않는 원인은 02편에서 확정하지 못했습니다(해상도 12 → 24에서 4.5 → 5.1 × 10⁻⁴).</p>

05편 굽은 도파로에서는 이 값이 방사 손실 측정의 하한이 됩니다. 꺾인 곳에서 새어 나간 빛이 PML에 흡수되어야 1 − T − R을 방사 손실로 읽을 수 있기 때문입니다.

<h2 id="meep-code">3. Meep 코드에서</h2>

### 기본 형태: 모든 변에 같은 두께

```python
# code/boundary_pml.py (02편), (4) simulation & boundaries
def make_sim(cell, layers, center=mp.Vector3(), resolution=RESOLUTION):
    """layers = [] (reflecting), [mp.PML(d)] or [mp.Absorber(d)]."""
    return mp.Simulation(cell_size=mp.Vector3(*cell), resolution=resolution, geometry=[],
                         boundary_layers=layers, sources=point_source(center), Courant=0.5)

# the layer is ADDED outside the fixed L x L interior
cell = L + 2 * d
```

- 무엇: `boundary_layers`에 `mp.PML(d)`를 넣으면 셀의 모든 변 안쪽에 두께 d의 층이 생깁니다. 빈 리스트면 반사 벽입니다.
- 왜: PML은 셀 크기를 늘리지 않고 셀 안쪽을 씁니다. 그래서 관심 영역 L을 고정하려면 셀을 `L + 2*d`로 직접 키워야 합니다.
- 틀리면: 셀을 그대로 두고 d만 키우면 비교 영역이 층 안으로 들어갑니다. 02편 첫 실행에서 "PML이 두꺼울수록 반사가 크다"는 거꾸로 된 결과가 이렇게 나왔습니다.

### 방향과 면을 골라서

```python
# code/binary_grating.py (06편): PML in x only, Bloch-periodic in y
boundary_layers=[mp.PML(DPML, direction=mp.X)], ..., k_point=mp.Vector3()

# code/cavity_ldos.py (11편): no z PML, the cell walls are the mirrors
pml = [mp.PML(thickness=DPML, direction=mp.R)]

# code/extraction_efficiency.py (14편): bottom has no PML = ground plane
boundary_layers=[mp.PML(DPML, direction=mp.R), mp.PML(DPML, direction=mp.Z, side=mp.High)]
```

- 무엇: `direction`은 어느 축의 경계에 층을 둘지, `side`는 그 축의 양쪽(`mp.ALL`, 기본값) 중 어느 쪽(`mp.Low`/`mp.High`)에 둘지 정합니다.
- 왜: 주기 구조는 주기 방향에 PML 대신 Bloch 주기 경계(`k_point`)를 씁니다. PML을 빼면 그 면은 다시 완전 도체 벽이 되므로, 거울이나 접지면을 일부러 만들 때도 같은 방법을 씁니다.
- 틀리면: 격자의 주기 방향에도 PML을 넣으면 무한 주기 구조가 아니라 PML로 잘린 유한 구조를 계산하게 됩니다.

### 층 안에 있는 물체

```python
# code/straight_waveguide.py (04편)
geometry = [mp.Block(center=mp.Vector3(0, 0),
                     size=mp.Vector3(mp.inf, w_core),   # infinite in x: runs straight through the PML
```

공식 튜토리얼의 말대로 PML은 셀 안쪽에 있고 그 자리의 물체와 겹칩니다. 도파로는 PML을 지나 셀 끝까지 이어져야 모드가 층 안에서 감쇠합니다. PML 앞에서 도파로가 끝나면 그 끝면이 반사원이 됩니다.

<h2 id="in-examples">4. 예제에서의 쓰임</h2>

| 예제 | PML의 역할 | 배치 |
|---|---|---|
| [01 점원과 선원]({{ site.baseurl }}/point-line-source/) | 실험 A·B는 PML 없이 첫 벽 반사 전까지만 보고, 실험 C는 flux를 재려고 진공을 열린 공간으로 만듦 | C만 모든 변 |
| [02 경계 조건]({{ site.baseurl }}/boundary-pml/) | 비교 대상 자체 | 모든 변, 두께 0.25–2 µm |
| [04 직선 도파로]({{ site.baseurl }}/straight-waveguide/)·[05 굽은 도파로]({{ site.baseurl }}/waveguide-bend-90/) | 도파로 양 끝을 무한히 긴 선로로 만듦, 방사 손실 흡수 | 모든 변, 도파로가 층을 관통 |
| [06 회절 격자]({{ site.baseurl }}/binary-grating/)·[07 meta-atom]({{ site.baseurl }}/meta-atom/) | 반사·투과된 회절파 흡수 | 전파 방향만, 주기 방향은 `k_point` |
| [10 점광원 3D 방사]({{ site.baseurl }}/dipole-pattern-3d/) | 방사 방향 흡수, 거울 면은 비움 | z만 또는 z의 한쪽 |
| [11 두 거울 사이]({{ site.baseurl }}/cavity-ldos/) | 옆으로 새는 빛 흡수 | r(또는 x, y)만, z 벽이 거울 |
| [13 회전 대칭]({{ site.baseurl }}/cylindrical-dipole/)·[14 박막 광추출]({{ site.baseurl }}/extraction-efficiency/) | 원통 좌표의 r·z 경계 흡수 | r과 z 위쪽, 아래는 접지면 |

<h2 id="pitfalls">5. 돌아가는데 틀리는 경우</h2>

코드는 오류 없이 끝나지만 숫자가 틀리는 경우입니다. 증상에서 출발해 원인을 좁힙니다.

| 증상 | 원인 | 확인법 | 고침 |
|---|---|---|---|
| PML을 두껍게 할수록 반사·손실이 커 보임 | 측정 영역이나 monitor가 PML 안으로 들어감 | layout 그림에서 PML 안쪽 경계와 monitor 끝의 거리 계산 | 셀을 `L + 2d`로 키워 PML 없는 영역을 고정 (02편) |
| source 근처의 장이나 방출률이 이상함, Harminv Q가 낮게 나옴 | source나 공진기의 소멸장이 PML에 닿아 인공 흡수가 생김 (공식 FAQ) | PML과의 간격을 두 배로 늘려 값이 바뀌는지 비교 | 간격을 파장의 절반 이상으로 늘림 |
| 모든 숫자 검사는 통과하는데 설계가 다른 해상도에서 무너짐 | monitor가 PML 경계선에 정확히 걸침. 흡수가 아직 약해 결과가 정상처럼 보임 | 실행 전에 monitor·source·설계 영역과 PML 안쪽 경계의 거리를 계산 | 셀을 키우거나 monitor를 안쪽으로 이동 |
| 격자·주기 구조에서 반사가 줄지 않거나 장이 발산 | 주기 매질에는 진짜 PML이 없음, band edge 근처는 군속도가 작아 흡수가 약함 | `mp.Absorber`로 바꿔 결과 비교 | Absorber 사용, 두께를 늘림 |
| 금속 경계면(표면 플라즈몬)에서 장이 커짐 | backward-wave 모드에서 PML이 발산 | PML을 Absorber로 바꾸면 사라지는지 확인 | Absorber 사용 |
| 분산 재료가 셀 끝까지 이어진 구조에서 발산 | 분산 재료와 PML이 겹쳐 불안정 (공식 Materials 문서) | 재료를 PML 앞에서 끊거나 Absorber로 교체 | Absorber 사용, [Courant 조건]({{ site.baseurl }}/terms/courant-condition/)도 함께 확인 |
| 셀 끝에서 도파로가 끝나는데 반사가 큼 | 도파로 끝면이 PML 앞에서 반사 | `mp.inf` 길이로 바꿔 R 비교 | 도파로를 셀 끝까지 연장 |
| 폭이 아주 좁은 Gaussian(거의 CW)에서 잔여 장이 남음 | 갑자기 켜지고 꺼질 때 생긴 고주파 성분이 PML에 덜 흡수됨 (공식 FAQ) | source 스펙트럼 그림 확인 | 측정 대역과 비슷한 `fwidth` 사용 |

<p class="lesson-note">세 번째 행은 한 2D bend 역설계 작업에서 실제로 있었던 일입니다. 출력 monitor가 PML 안쪽 경계선 위에 놓였는데 투과율·에너지 보존·gradient 검사가 모두 정상 범위였고, layout 그림을 보고서야 발견했습니다. 결과 숫자만으로는 배치 오류를 잡을 수 없습니다.</p>

<h2 id="inverse-design">6. inverse design에서</h2>

adjoint 계산은 같은 셀에서 두 번 돌립니다. forward run은 입력 source에서, adjoint run은 목적함수를 재는 monitor 위치에서 거꾸로 빛을 보냅니다. 두 run이 같은 PML을 쓰므로 PML이 반사를 남기면 그 반사는 두 장 모두에 들어갑니다. gradient는 계산된 문제에 대해서는 정확하지만 그 문제가 실제 열린 공간과 다릅니다. 최적화기는 PML에서 돌아온 파까지 이용하는 설계를 찾을 수 있고, 그 설계는 PML을 바꾸면 성능이 달라집니다.

그래서 역설계에서는 두 가지를 먼저 확인합니다. 첫째, 설계 영역과 adjoint source가 되는 monitor가 PML 안쪽 경계에서 충분히 떨어져 있는지 실행 전에 계산합니다. 위 표의 세 번째 사례가 바로 이 확인을 건너뛴 경우였습니다. 둘째, 최적화가 끝난 설계를 PML 두께나 셀 크기를 바꾼 새 시뮬레이션으로 다시 재서 성능이 유지되는지 봅니다. [09편]({{ site.baseurl }}/bend-inverse/)이 최종 설계를 새 `Simulation`에서 다시 측정하는 것도 같은 이유입니다.

<h2 id="connections">7. 연결</h2>

- 함께 보면 좋은 개념: [Courant 조건]({{ site.baseurl }}/terms/courant-condition/) (분산 재료와 PML이 겹칠 때의 발산), [Flux 정규화]({{ site.baseurl }}/terms/flux-normalization/) (monitor와 PML의 간격)
- 측정과 해설: [02 · 경계 조건과 PML]({{ site.baseurl }}/boundary-pml/)
- 애니메이션 코드: [code/pml_flux_gif.py](https://github.com/jin-castle/meep-examples/blob/main/code/pml_flux_gif.py) (Meep 1.33.0, 단일 코어 약 1분) · [anim.json]({{ site.baseurl }}/assets/meep/terms-pml/anim.json)
- Meep 공식 문서: [Perfectly Matched Layer](https://meep.readthedocs.io/en/master/Perfectly_Matched_Layer/) · [Python API: PML, Absorber](https://meep.readthedocs.io/en/master/Python_User_Interface/#pml) · [FAQ: Checking convergence](https://meep.readthedocs.io/en/master/FAQ/#checking-convergence)
- 참고 문헌: S. G. Johnson, [Notes on Perfectly Matched Layers](https://arxiv.org/abs/2108.05348) (MIT 강의 노트, arXiv 2021)
