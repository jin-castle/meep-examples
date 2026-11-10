---
layout: lesson
lesson_title: "재료가 흡수한 전력은 어떻게 확인할까요?"
lesson_summary: "손실이 있는 SiO₂ 원기둥의 흡수 지도를 그리고, 내부 DFT 적분과 닫힌 flux 상자로 흡수 전력을 각각 구합니다. 두 방법이 해상도와 함께 가까워지는 과정과, 측정 상자를 옮겼을 때 남는 차이를 확인합니다."
lesson_goals:
  - "전기장 세기와 흡수 전력 밀도를 구분한다."
  - "복소 E·D의 부피 적분과 안쪽 방향 flux의 표면 적분을 비교한다."
  - "해상도 오차, 측정면 의존성, 흡수 단면적과 효율을 구분한다."
lesson_prerequisites: "03편 기준 계산과 산란 · 20편 복소 유전율과 재료 분산"
date: 2026-11-11
title: "Meep Example 25 · 흡수된 전력의 위치 — DFT 밀도 적분과 닫힌 flux 상자"
title_en: "Meep Example 25 · Where power is absorbed — a DFT density integral and a closed flux box"
lang: ko
translation_key: absorbed-power
series: meep-examples
part: 25
level: intermediate
runtime: "저장된 MPI 4 계산: res 50/100/200 약 7초/54초/9분; 단일 코어 시간은 미측정"
meep_version: "1.33.0"
official_example: "https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#absorbed-power-density-map-of-a-lossy-cylinder"
tags: [meep, fdtd, absorption, dft, flux, convergence, dispersive-material]
image: /assets/meep/25/forward_dft.png
excerpt: "약한 손실을 가진 SiO₂ 원기둥의 흡수 전력을 두 방법으로 계산합니다. res 50→200에서 차이가 3.66%→0.249%로 줄지만, 상자 크기 검사는 별도의 한계로 남습니다."
---
<h2 id="observe">1. 관찰하기: 밝은 곳이 곧 흡수가 큰 곳일까요?</h2>

20편에서는 재료의 복소 유전율을 넣었습니다. 이제 실제로 **어디에서 얼마의 전력을 흡수하는지** 확인합니다. 2D SiO₂ 원기둥에 왼쪽에서 평면파 펄스를 넣고, 진공 파장 1 µm의 DFT 장을 읽습니다.

<figure class="lesson-figure">
<a href="{{ '/assets/meep/25/forward_dft.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/25/forward_dft.png' | relative_url }}" alt="실제 Meep의 원기둥 주변 DFT 전기장 세기, 원기둥 내부 흡수 전력 밀도, 해상도별 적분과 flux 전력 비교" loading="eager"></a>
<figcaption>저장된 실제 계산입니다. 왼쪽은 |Ez|², 가운데는 2πf Im(Ez* Dz), 오른쪽은 적분한 전력입니다. 광원은 왼쪽에 있고 흡수 밀도 최댓값은 뒤쪽 x ≈ 0.98 µm에 있습니다. 가운데 그림은 어두운 쪽이 큰 값이므로 색 막대를 함께 읽으세요. 전기장 지도와 흡수 지도는 서로 다른 물리량입니다.</figcaption>
</figure>

<details markdown="1">
<summary>무엇을 검증했나요?</summary>

반지름 1 µm의 무한 원기둥, 2D Ez, Meep materials의 `SiO2`, λ = 1 µm 한 점입니다. ε = 2.132084 + 0.000985244i의 작은 손실이 있습니다. res 100에서 부피 적분은 0.131204225, 작은 flux 상자는 0.132491690으로 0.9717% 차이입니다. res 50→100→200에서 이 차이는 3.6556%→0.9717%→0.2494%로 줄었습니다. 그러나 res 100의 큰 상자는 작은 상자와 3.3803% 달라, 등록된 2% 기준을 통과하지 못했습니다. 이 글은 새 전자기장 계산 없이 저장된 결과를 사용합니다.

</details>

<h2 id="predict">2. 예측하기: 안에서 사라진 전력과 들어온 순전력</h2>

<fieldset class="prediction">
<legend>광원을 포함하지 않는 닫힌 상자 안에 손실 원기둥이 있습니다. 충분히 정확한 계산에서 무엇을 기대할까요?</legend>
<label><input type="radio" name="absorbed-power-prediction" value="balance"> 내부 흡수 밀도의 적분과, 상자로 들어오는 순전력이 같다.</label>
<label><input type="radio" name="absorbed-power-prediction" value="scattered"> 바깥으로 나가는 산란 전력이 항상 흡수 전력과 같다.</label>
<label><input type="radio" name="absorbed-power-prediction" value="field"> |Ez|²를 합하면 재료 손실과 관계없이 흡수 전력이 된다.</label>
</fieldset>

<details markdown="1">
<summary>예측과 판정 기준</summary>

포인팅 정리는 상자 안의 손실과 경계를 통과하는 순전력을 연결합니다. 이 자료에서는 res 100의 두 방법 차이 < 1.5%, 큰/작은 상자 차이 < 2%, res 200/50의 방법 차이 비 < 0.5를 미리 기준으로 삼았습니다. 앞과 마지막 검사는 통과했지만 상자 크기 검사는 실패했습니다. 해상도를 올리면 모든 검사가 자동으로 해결된다고 예측하지 않습니다.

</details>

<h2 id="understand">3. 원리 이해하기: 같은 흡수를 두 경로로 셉니다</h2>

{% include chapter-illustration.html %}

Meep 공식 예제의 DFT 정규화에서 흡수 전력 밀도와 적분은 다음과 같습니다. 일반적인 진폭 관례의 식에서 1/2를 따로 가져와 이 코드에 추가하면 안 됩니다.

$$
p_{\rm abs}=2\pi f\,\operatorname{Im}(\mathbf E^*\!\cdot\mathbf D),\qquad
P_{\rm vol}\approx\sum_{i,j}p_{\mathrm{abs},ij}\,\Delta x\Delta y.
$$

2D Ez 예제이므로 Ez와 Dz만 씁니다. `yee_grid=True`로 공식 예제와 같은 DFT 표본을 모으고, 면적 가중치는 1/resolution²입니다. |E|²가 커도 손실이 없는 진공에서는 흡수 밀도가 0입니다. 이 계산은 전자기 에너지 손실을 구하며 온도 상승이나 열 확산을 풀지 않습니다.

다른 경로는 전체장의 **안쪽 방향 순 flux**입니다.

$$
P_{\rm box}=-\oint_{\partial V}\mathbf S\cdot\hat{\mathbf n}\,d\ell.
$$

상자 각 면의 `weight`는 왼쪽 +1, 오른쪽 −1, 위 −1, 아래 +1입니다. 이것은 흡수 측정이므로 total field를 씁니다. 산란만 구하는 별도 상자에는 03편처럼 빈 셀 DFT 장을 빼고, 바깥 방향 전력으로 읽습니다. 같은 flux 값이라도 전체장과 산란장의 역할을 섞으면 안 됩니다.

| 항목 | 고정 조건 | 이유 |
|---|---|---|
| 구조 | SiO₂, r = 1 µm, z로 무한 | 공식 2D 원기둥 조건 |
| 셀·경계 | 8 × 8 µm, PML 1 µm, 공기 여유 2 µm | 계산 경계와 물체 분리 |
| 광원 | x = −3 µm, y 폭 8 µm, Ez Gaussian 펄스 | `is_integrated=True`로 PML까지 걸친 선원 처리 |
| 주파수 | f = 1 µm⁻¹, fwidth = 0.1 f | 한 주파수의 흡수 비교 |
| 측정 | DFT/작은 상자 [−1,1]², 큰 상자 [−2,2]² | 부피·표면 검산 및 위치 의존성 검사 |
| 종료 | source 이후 100, 최종 t = 200 | 원래 결과와 같은 유한 기록 길이 |

<h2 id="run">4. 실행하기: 빈 셀 다음 손실 원기둥</h2>

[Python 코드 다운로드]({{ '/code/absorbed_power.py' | relative_url }}) · [출처·SHA-256]({{ '/assets/meep/25/provenance.json' | relative_url }}) · [res 100 실제 로그]({{ '/assets/meep/25/abs_r100.log' | relative_url }})

Meep·NumPy가 있는 환경에서 실행합니다. 다운로드 코드는 외부 helper 없이 동작하며, `--help`에는 Meep import가 필요하지 않습니다.

```bash
python code/absorbed_power.py --help
python code/absorbed_power.py --resolution 100 --tag abs_r100 --out work/abs-r100
python code/absorbed_power.py --resolution 200 --tag abs_r200 --out work/abs-r200
```

1. **파라미터**: r·λ·PML을 고정하고 해상도만 바꿉니다.
2. **구조**: 빈 셀을 먼저 만들고 두 번째 계산에 `SiO2` 원기둥을 넣습니다.
3. **광원**: 두 계산의 위치·폭·펄스를 똑같이 둡니다.
4. **경계**: 네 방향 PML과 y 거울 대칭을 씁니다.
5. **모니터**: 빈 셀에서 입사 세기와 기준 장을 저장합니다. 원기둥에서는 E·D와 세 flux 상자(작은 total, 큰 total, 큰 scattered)를 모읍니다.
6. **실행**: 각각 source가 끝난 뒤 100까지 실행합니다. MPI 장 모으기 호출은 모든 rank가 도달하게 둡니다.
7. **후처리**: 밀도 적분·순 flux·산란 단면적을 JSON에, 지도와 source trace를 NPZ에 저장합니다.

```python
density = 2 * np.pi * frequency * np.imag(np.conj(electric) * displacement)
volume_power = float(np.sum(density) / resolution ** 2)
surface_power = mp.get_fluxes(small_box)[0]
error = abs(volume_power - surface_power) / surface_power
```

<h2 id="interpret">5. 결과 해석하기: 가까워진 방법과 남아 있는 상자 차이</h2>

| 해상도 (px/µm) | 내부 DFT 적분 | 작은 상자 순전력 | 큰 상자 순전력 | DFT/작은 상자 차이 |
|---|---|---|---|---|
| 50 | 0.131200795 | 0.136178929 | 0.154296396 | 3.6556% |
| 100 | 0.131204225 | 0.132491690 | 0.136970288 | 0.9717% |
| 200 | 0.131072200 | 0.131399930 | 0.132511796 | 0.2494% |

<figure class="lesson-figure">
<a href="{{ '/assets/meep/25/resolution_ladder.png' | relative_url }}" data-lightbox><img src="{{ '/assets/meep/25/resolution_ladder.png' | relative_url }}" alt="해상도 50,100,200에서 DFT와 작은 flux 상자의 상대 차이가 감소하는 실제 계산" loading="lazy"></a>
<figcaption>해상도를 두 배로 할 때 두 방법의 차이가 약 4분의 1로 줄어듭니다. 세 점에서 관측한 경향이며 모든 재료·파장에 대한 수렴 차수를 증명하는 것은 아닙니다.</figcaption>
</figure>

res 100의 DFT 적분과 flux 전력은 2020 공식 노트북 값에 각각 상대 5.12 × 10⁻⁸, 2.76 × 10⁻⁵로 가깝습니다. 원자료의 전체 판정 표기는 `supported`이지만, **큰 상자 검사 한 개는 실패**했습니다. res 100의 상자 차이는 3.3803%, res 200에도 약 0.846%가 남습니다. 종료 뒤 잔여 에너지·DFT 기록 길이·표본 위치 등의 원인을 분리한 실험은 없으므로 원인이 확정됐다고 말하지 않습니다.

흡수 단면적을 지름 2r로 나눈 $Q_{\rm abs}=P_{\rm box}/(I_0\,2r)$는 res 100에서 0.010595, 산란의 대응량 $Q_{\rm sca}$는 2.001215입니다. **이 Q는 공진기의 quality factor도, 전체 입사광 중 흡수 효율도 아닙니다.** 2D 산란 단면적의 지름 정규화 값이므로 Q_sca가 1보다 클 수 있습니다. 출력 전력 수치는 이 source·DFT 정규화의 값이며 와트로 바로 읽지 않습니다.

<h2 id="check">6. 확인하기: 상자 안에 source나 PML이 들어가면요?</h2>

<details markdown="1">
<summary>질문 1 · 흡수 상자의 장에도 빈 셀을 빼야 하나요?</summary>

흡수는 전체장의 닫힌 순 flux로 잽니다. 산란장만 빼면 다른 물리량을 적분합니다. 이 코드에서는 흡수용 total 상자와 산란용 reference-subtracted 상자를 따로 만듭니다. 상자가 source나 PML까지 포함하면 광원 공급 전력·계산 경계 흡수를 물체의 흡수에 섞게 됩니다.

</details>

<details markdown="1">
<summary>질문 2 · res 200에서 두 방법이 0.25% 이내이면 검증이 끝났나요?</summary>

다른 상자 크기, source 이후 시간, 재료의 유효 대역을 독립적으로 확인해야 합니다. 이 자료는 한 파장·한 재료이고, 큰 상자의 차이 원인은 미해결입니다. 낮은 해상도 20의 초기 시도는 분산 재료에서 NaN이 기록되어 있어 검증 표에서 제외했습니다.

</details>

### 직접 한 가지만 바꾸기

res 100을 고정하고 `--after-sources 200`으로 바꿔 큰/작은 상자 차이를 다시 기록해 보세요. 종료 시간과 해상도를 동시에 바꾸지 않아야 원인을 구분할 수 있습니다. 새 결과는 위 표의 저장된 결과와 별도로 표시합니다. 다음에는 [26 · 결함 도파로 공진기]({{ '/photonic-crystal-cavity/' | relative_url }})에서 흡수가 없는 구조의 손실을 방사와 포트 누설로 구분합니다.

<h2 id="reference">7. 참고 자료와 재현 기록</h2>

- 공식 설명: [Meep Basics · Absorbed Power Density Map of a Lossy Cylinder](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#absorbed-power-density-map-of-a-lossy-cylinder).
- 고정 원본: [absorbed_power_density.py, commit f7811d4](https://github.com/NanoComp/meep/blob/f7811d4157ea22f19d4ca76bc41c71b6e055763e/python/examples/absorbed_power_density.py). 원본의 물리 조건과 DFT 관례를 따릅니다.
- 추가분: 해상도 사다리, 큰 상자 검사, reference run의 입사 정규화·산란 전력, 한·영 학습 구성과 standalone CLI입니다. 원래 애니메이션 helper 의존성은 CLI에서 제거했습니다. 상단 개념 영상은 DFT 결과와 구분해 읽습니다.
- 데이터: [res 50]({{ '/assets/meep/25/abs_r50.json' | relative_url }}), [res 100]({{ '/assets/meep/25/abs_r100.json' | relative_url }}), [res 200]({{ '/assets/meep/25/abs_r200.json' | relative_url }}), [res 100 DFT 데이터]({{ '/assets/meep/25/abs_r100.npz' | relative_url }}), [실패도 보존한 판정]({{ '/assets/meep/25/aggregate_verdict.json' | relative_url }}), [출처·해시]({{ '/assets/meep/25/provenance.json' | relative_url }}).
- 연결: [03 · 입사장 빼기]({{ '/reference-subtraction/' | relative_url }}) → [20 · 재료 분산]({{ '/material-dispersion/' | relative_url }}) → 이 글. 코드에는 upstream Meep 라이선스가 계속 적용됩니다.

<details markdown="1">
<summary>전체 실행 코드 펼치기</summary>

{% highlight python %}
"""Measure absorption in a lossy cylinder using volume and surface integrals.

Adapted from NanoComp/meep absorbed_power_density.py at
f7811d4157ea22f19d4ca76bc41c71b6e055763e and the project's abs_repro.py.
Upstream licensing remains applicable; see assets/meep/25/provenance.json.
Publication reuses archived fields; this CLI executes a new run only on request.
"""
import argparse
import json
from pathlib import Path
import time

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolution", type=float, default=100, help="pixels per micrometre")
    parser.add_argument("--after-sources", type=float, default=100, help="Meep time after pulse ends")
    parser.add_argument("--tag", default="abs_r100", help="output filename stem")
    parser.add_argument("--out", type=Path, default=Path("absorbed-power-output"))
    args = parser.parse_args()
    if args.resolution <= 0 or args.after_sources <= 0:
        parser.error("resolution and after-sources must be positive")
    if not args.tag or Path(args.tag).name != args.tag:
        parser.error("tag must be a filename stem")
    import meep as mp
    from meep.materials import SiO2

    start = time.time()
    dpml, radius, air = 1.0, 1.0, 2.0
    length = 2 * (dpml + air + radius)
    frequency, big_half_width = 1.0, radius + 1.0

    def make(geometry):
        source = mp.Source(
            mp.GaussianSource(frequency, fwidth=0.1 * frequency, is_integrated=True),
            center=mp.Vector3(-0.5 * length + dpml), size=mp.Vector3(0, length), component=mp.Ez)
        return mp.Simulation(
            resolution=args.resolution, cell_size=mp.Vector3(length, length),
            boundary_layers=[mp.PML(dpml)], sources=[source], k_point=mp.Vector3(),
            symmetries=[mp.Mirror(mp.Y)], geometry=geometry)

    def inward_box(sim, half_width):
        h = half_width
        return sim.add_flux(
            frequency, 0, 1,
            mp.FluxRegion(center=mp.Vector3(x=-h), size=mp.Vector3(0, 2 * h), weight=+1),
            mp.FluxRegion(center=mp.Vector3(x=+h), size=mp.Vector3(0, 2 * h), weight=-1),
            mp.FluxRegion(center=mp.Vector3(y=+h), size=mp.Vector3(2 * h, 0), weight=-1),
            mp.FluxRegion(center=mp.Vector3(y=-h), size=mp.Vector3(2 * h, 0), weight=+1))

    # Empty-cell run: incident intensity and fields to subtract for scattering.
    sim = make([])
    incident = sim.add_flux(frequency, 0, 1, mp.FluxRegion(
        center=mp.Vector3(x=-big_half_width), size=mp.Vector3(0, 2 * radius)))
    reference_box = inward_box(sim, big_half_width)
    trace = {"t": [], "v": []}

    def record_trace(current_sim):
        trace["t"].append(current_sim.meep_time())
        probe = mp.Vector3(-0.5 * length + dpml + 0.5)
        trace["v"].append(float(np.real(current_sim.get_field_point(mp.Ez, probe))))

    sim.run(mp.at_every(0.05, record_trace), until_after_sources=args.after_sources)
    intensity = mp.get_fluxes(incident)[0] / (2 * radius)
    reference_data = sim.get_flux_data(reference_box)
    sim.reset_meep()

    sim = make([mp.Cylinder(material=SiO2, radius=radius, height=mp.inf)])
    material_fields = sim.add_dft_fields(
        [mp.Dz, mp.Ez], frequency, 0, 1, center=mp.Vector3(),
        size=mp.Vector3(2 * radius, 2 * radius), yee_grid=True)
    small_box = inward_box(sim, radius)
    big_box = inward_box(sim, big_half_width)
    scattered_box = inward_box(sim, big_half_width)
    sim.load_minus_flux_data(scattered_box, reference_data)
    field_map = sim.add_dft_fields([mp.Ez], frequency, 0, 1,
                                  center=mp.Vector3(), size=mp.Vector3(length - 2 * dpml, length - 2 * dpml))
    sim.run(until_after_sources=args.after_sources)
    displacement = sim.get_dft_array(material_fields, mp.Dz, 0)
    electric = sim.get_dft_array(material_fields, mp.Ez, 0)
    # Use the exact Meep tutorial DFT convention; do not add a separate 1/2.
    density = 2 * np.pi * frequency * np.imag(np.conj(electric) * displacement)
    volume_power = float(np.sum(density) / args.resolution ** 2)
    surface_power = mp.get_fluxes(small_box)[0]
    large_surface_power = mp.get_fluxes(big_box)[0]
    scattered_power = -mp.get_fluxes(scattered_box)[0]
    epsilon = SiO2.epsilon(frequency)[0][0]
    summary = dict(
        res=args.resolution, t_end=sim.meep_time(), timesteps=sim.timestep(),
        P_dft=volume_power, P_box=surface_power,
        err=abs(volume_power - surface_power) / surface_power, P_box_big=large_surface_power,
        P_scat=scattered_power, I0=intensity,
        Q_abs=surface_power / (intensity * 2 * radius),
        Q_scat=scattered_power / (intensity * 2 * radius),
        eps_SiO2=[float(epsilon.real), float(epsilon.imag)], wall=time.time() - start)
    # Field gathers are collective: every MPI rank must reach them.
    electric_map = sim.get_dft_array(field_map, mp.Ez, 0)
    epsilon_map = sim.get_array(component=mp.Dielectric, center=mp.Vector3(),
                                size=mp.Vector3(length - 2 * dpml, length - 2 * dpml))
    if mp.am_master():
        args.out.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(args.out / f"{args.tag}.npz", apd=density, Ezmap=electric_map,
                            eps=epsilon_map, trace_t=np.array(trace["t"]), trace_v=np.array(trace["v"]))
        (args.out / f"{args.tag}.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print("RESULT " + json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
{% endhighlight %}

</details>
