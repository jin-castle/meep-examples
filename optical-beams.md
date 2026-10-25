---
layout: topic
permalink: /optical-beams/
title: "Beam Lab — 경계 곡률, vortex 전하 부호와 Airy 감쇠"
title_en: "Beam Lab — curvature, signed vortex and finite-energy Airy"
lang: ko
translation_key: optical-beams
series: meep-examples
topic_label: BEAM LAB
lesson_title: "광원과 경계를 바꾸면 빔은 어떻게 달라질까요?"
lesson_summary: "Meep으로 경계 곡률, vortex 위상 전하의 부호, Airy 광원의 감쇠를 하나씩 바꾸어 비교합니다. 광원에 설정한 값과 계산된 전기장을 구분해 결과를 해석합니다."
lesson_goals:
  - "같은 광원으로 경계 곡률만 바꾸어 장의 분포를 비교합니다."
  - "광원에 설정한 전하 ±2와 복소장에서 측정한 위상 감김을 구분합니다."
  - "Airy 감쇠와 빔 분포의 관계를 관찰하고 계산의 한계를 설명합니다."
lesson_prerequisites: "01편 광원 · 02편 PML · 03편 참조 계산"
calc_note: "Meep 계산 · CPU 한 코어 · Gaussian 3조건, 3D vortex 2조건, Airy 2조건. 복소 DFT 장을 저장해 분석합니다."
toc:
  - { id: observe, label: "세 가지 조건 비교" }
  - { id: curved, label: "경계의 곡률 바꾸기" }
  - { id: vortex, label: "위상 전하의 부호 바꾸기" }
  - { id: vortex-animation, label: "움직이는 3D 파면" }
  - { id: vortex-material, label: "이전 매질 경계 실험" }
  - { id: airy, label: "Airy 감쇠 바꾸기" }
  - { id: run, label: "계산 조건과 실행 방법" }
  - { id: verify, label: "검증과 해석 범위" }
  - { id: reference, label: "참고 자료와 재현 기록" }
related:
  - { url: "/point-line-source/", label: "01 · 점 광원과 선 광원" }
  - { url: "/reference-subtraction/", label: "03 · 반사율과 투과율 측정" }
  - { url: "/metalens/", label: "Metalens · 위상으로 빛을 모으기" }
date: 2026-10-24
tags: [meep, beam-lab, gaussian-beam, vortex, airy, fdtd]
image: /assets/meep/beam-lab/overview.png
excerpt: "새로 작성한 전류 광원과 Meep 제어 코드로 곡률, vortex 전하 부호, Airy 감쇠를 비교하는 일곱 가지 실험."
---

<h2 id="observe">1. 곡률·위상 전하·감쇠 비교하기</h2>

Beam Lab에서는 **직접 작성한 광원 프로파일과 Meep 코드로 빔의 장 분포를 비교**합니다. 경계 곡률은 빔의 분포에 어떤 영향을 줄까요? Vortex 전하의 부호를 바꾸면 위상은 어떻게 달라질까요? Airy 광원의 꼬리를 더 강하게 감쇠시키면 어떤 무늬가 나타날까요?

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/overview.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/overview.png" alt="새 Beam Lab에서 계산한 경계 곡률, vortex 전하 부호와 Airy 감쇠 비교" loading="eager"></a>
  <figcaption>일곱 조건의 계산 결과입니다. Gaussian·Airy 그림은 복소 DFT 전기장 크기의 제곱 합, vortex 단면은 복소 E<sub>z</sub>의 위상입니다. 표시하는 물리량이 다르므로 그림 간 색상으로 장의 크기를 비교할 수 없습니다.</figcaption>
</figure>

[Optical-beams-MEEP](https://danielkotik.github.io/Optical-beams-MEEP/)에서 빔의 종류와 시각화 아이디어를 참고했습니다. 이번 구현은 표준 해석식을 유한 전류 광원으로 구성하고, 다른 경계·매개변수·관측 방법으로 계산합니다. 기존 원본 코드 실행과 Blender 3D vortex는 [재현 기록]({{ '/optical-beams/archive/' | relative_url }})에 남아 있습니다.

<h2 id="curved">2. 같은 광원, 다른 경계 곡률</h2>

Gaussian 광원의 중심 입사각은 20°이고, 굴절률은 1에서 1.5로 바뀝니다. 경계는 **x = κy²**입니다. κ=0은 평면, +0.10/a는 +x 방향으로 열린 포물선, −0.10/a는 −x 방향으로 열린 포물선입니다. 같은 광원과 색상 척도를 사용해 경계의 영향만 비교합니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/gaussian_curvature.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/gaussian_curvature.png" alt="입사각 20도 Gaussian 광원과 평면 및 양·음 곡률의 포물선 경계에서 측정한 DFT 장 비교" loading="lazy"></a>
  <figcaption>밝기는 세 조건의 공통 최대값으로 나눈 Σ|DFT E<sub>j</sub>|²입니다. 경계선과 그 뒤의 밝은 영역을 함께 보세요. 같은 최대 전류로 구동했지만, 입사 전력을 정규화한 투과율은 아닙니다.</figcaption>
</figure>

먼저 경계 뒤 밝은 영역의 폭과 방향을 비교하세요. 곡률이 생기면 위치에 따라 법선 방향도 달라집니다. 20°는 원점의 법선을 기준으로 한 광원 중심각이며, 경계 전체에서의 입사각이 아닙니다. 평면파의 Snell 법칙은 평면 경계의 중심 방향을 예상하는 기준이지만, 유한 빔의 간섭 무늬 전체를 결정하지는 않습니다.

<h2 id="vortex">3. 위상 전하 +2와 −2</h2>

광원에는 LG의 p=0 형태를 사용합니다. 반지름에 따른 크기는 두 조건에서 같고, 위상 인자 exp(imθ)의 **m 부호만** 바꿉니다. 광원 둘레를 한 바퀴 돌 때 위상 변화가 +4π 또는 −4π가 됩니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/vortex_charge.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/vortex_charge.png" alt="입력 전하 +2와 -2에 대한 실제 Meep DFT Ez의 위상 단면과 위상 감김 측정 경로" loading="lazy"></a>
  <figcaption>색은 입력 광원 그림이 아니라 실제 계산된 복소 E<sub>z</sub>의 위상입니다. 원을 따라 위상 감김을 다시 측정하며, 장 크기가 단면 최대값의 5%보다 작은 픽셀은 가렸습니다. 제목의 측정값과 입력 전하를 비교하세요.</figcaption>
</figure>

중심의 약한 장에서는 위상이 안정적으로 정의되지 않습니다. 중심 픽셀의 색보다 장이 충분한 닫힌 경로에서의 위상 변화를 확인하세요. 이 광원은 **LG 형태의 유한 E<sub>z</sub> 전류 시트**이며, 정확한 비근축 벡터 LG 해를 주입하는 모델은 아닙니다.

<h2 id="vortex-animation">4. 3D 등위면으로 보는 전기장의 위상 변화</h2>

복소 DFT 장에서 Re(Ẽ<sub>z</sub> exp(−iφ))를 재구성합니다. 양의 등위면은 청록, 음의 등위면은 산호색입니다. 두 전하의 파면이 어떻게 다르게 움직이는지 나란히 비교하세요.

<figure class="lesson-figure lesson-animation">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/vortex_phase.gif" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/vortex_poster.png" data-animation-src="{{ site.baseurl }}/assets/meep/beam-lab/vortex_phase.gif" data-static-src="{{ site.baseurl }}/assets/meep/beam-lab/vortex_poster.png" alt="실제 DFT 장에서 재구성한 전하 +2와 -2의 양·음 3D 등위면 위상 애니메이션" loading="lazy"></a>
  <figcaption>원래 격자의 부호 있는 E<sub>z</sub> 등위면입니다. 두 계산 전체의 최대 |Ẽ<sub>z</sub>|를 기준으로 ±25%를 고정해 사용합니다. 24프레임이 2π 위상 주기를 나타내고, 화면에서는 80ms씩 총 1.92초로 반복됩니다.</figcaption>
  <button type="button" class="animation-toggle" hidden>애니메이션 재생</button>
</figure>

주파수 f=1 c/a이므로 한 위상 주기는 1 a/c입니다. 이 영상은 단일 주파수 복소장의 위상 재구성이며, 광원이 켜진 뒤 빛이 도착하는 과도 과정을 담은 시간 샘플은 아닙니다.

[여섯 위상 비교]({{ '/assets/meep/beam-lab/contact_sheet.png' | relative_url }}) · [계산·렌더링 검사 기록]({{ '/assets/meep/beam-lab/checks.json' | relative_url }})

<h2 id="vortex-material">5. 이전 매질 경계 실험과의 차이</h2>

이번 ±2 전하 비교는 **진공 안에서 광원 위상만 바꾸는 실험**이므로 매질 블록이 없습니다. 이전 유전체 경계의 흰 vortex, 두 단면과 반투명 블록은 다른 실험입니다. [이전 3D 애니메이션]({{ '/optical-beams/archive/#vortex-animation' | relative_url }})과 [블록의 반투명·광택 재질 비교]({{ '/optical-beams/archive/#vortex-material' | relative_url }})에서 그대로 볼 수 있습니다. 렌더링 광택을 추가하는 것과 FDTD에 실제 거울 경계를 넣는 것은 서로 다른 변경입니다.

<h2 id="airy">6. Airy 광원의 감쇠를 바꾸면 분포는 어떻게 달라질까요?</h2>

광원은 Ai(y/s) exp(αy/s)이고 유한한 개구에서 잘립니다. α=0.08과 0.20을 비교합니다. α가 커지면 음의 y 방향 진동 꼬리가 더 강하게 억제됩니다. 두 조건 모두 진공이므로 밝은 무늬의 변화에 굴절 경계가 개입하지 않습니다.

<figure class="lesson-figure">
  <a href="{{ site.baseurl }}/assets/meep/beam-lab/airy_apodization.png" data-lightbox><img src="{{ site.baseurl }}/assets/meep/beam-lab/airy_apodization.png" alt="진공에서 Airy 전류 광원의 감쇠 계수 0.08과 0.20을 비교한 실제 DFT 장" loading="lazy"></a>
  <figcaption>같은 척도의 Σ|DFT E<sub>j</sub>|² 비교입니다. 주엽의 궤적뿐 아니라 옆으로 이어지는 무늬와 퍼짐도 살펴보세요. 유한 개구와 지수 감쇠를 적용한 광원이며, 무한한 이상적 Airy beam과 구분합니다.</figcaption>
</figure>

<h2 id="run">7. 계산 조건과 실행 방법</h2>

길이 단위는 a이며 진공 파장은 a입니다. 실제 μm 치수를 지정한 소자 모델은 아닙니다. 광원은 유한한 E<sub>z</sub> 전류 시트여서 양방향으로 방사하며, 저장하는 관측 영역은 전방입니다.

| 실험 | 바꾸는 값 | 고정하는 조건 |
|---|---|---|
| Gaussian | κ = 0, +0.10/a, −0.10/a | 중심각 20°, n=1→1.5, waist 0.9a |
| Vortex | m = +2, −2 | 진공, p=0 형태, waist 1a |
| Airy | α = 0.08, 0.20 | 진공, 같은 유한 개구와 길이 척도 |

2D 해상도는 20/a, 3D는 12/a, PML 두께는 0.8a입니다. 24 a/c까지 구동한 뒤 8 a/c 동안 복소 DFT 장을 누적합니다. 실제 시작·종료 시각은 각 실행 기록에 저장합니다. 유한 대기 시간을 두었다는 사실만으로 정상상태 수렴이 입증되지는 않습니다.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VTK_SMP_MAX_THREADS=1
python -m unittest discover -s code/beam_lab -p 'test_*.py'
python code/beam_lab/run.py --suite --output output/beam-lab
python code/beam_lab/render.py --data output/beam-lab --output assets/meep/beam-lab
```

[실행 설명](https://github.com/jin-castle/meep-examples/tree/main/code/beam_lab)에서 환경과 개별 조건 실행 방법을 확인할 수 있습니다. `profiles.py`는 광원 식, `run.py`는 Meep 제어와 데이터 저장, `render.py`는 측정값 분석과 그림 제작을 담당합니다.

<h2 id="verify">8. 검증 항목과 결과의 해석 범위</h2>

[checks.json]({{ '/assets/meep/beam-lab/checks.json' | relative_url }})에는 조건별 설정, 실제 관측 시각, 코드·데이터 해시, 측정한 위상 감김과 애니메이션 검사 결과가 들어 있습니다. 위상 감김은 입력값을 복사하지 않고 저장된 DFT 장에서 다시 계산합니다. 3D 등위면은 공간 stride 1로 추출하며 mesh decimation을 적용하지 않습니다.

이 비교는 유한 격자에서의 장 시각화입니다. 해상도·PML·정상상태 수렴 연구, 입사 전력 정규화, 투과 효율 측정은 포함하지 않습니다. 최대 전류를 같게 맞춰도 주입 전력이 같아지는 것은 아닙니다. 밝기 비교를 효율 수치로 읽지 마세요.

<h2 id="reference">9. 참고 자료와 이전 재현 기록</h2>

- [Meep Python API](https://meep.readthedocs.io/en/latest/Python_User_Interface/): 시뮬레이터와 복소 DFT 관측 기능.
- [SciPy Airy 함수](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.airy.html): Ai 계산.
- [Optical-beams-MEEP · Daniel Kotik와 Jörg Götte](https://danielkotik.github.io/Optical-beams-MEEP/): 빔 주제와 시각화 아이디어의 참고 자료.
- [기존 원본 코드 재현 기록]({{ '/optical-beams/archive/' | relative_url }}): 과거 실행 데이터, Blender 렌더링, 원본 그림 비교와 해당 MIT 고지.

새 Beam Lab은 `optbeam`이나 보존된 원본 실행 코드를 불러오지 않습니다. 과거 데이터의 출처는 재현 기록에 유지하고, 이 글의 새 실험과 구분합니다. 코드·번역·편집에는 AI 도구를 활용했으며, 파일별 이용 조건은 [권리 및 라이선스]({{ '/rights-and-licenses/#source-optical-beams' | relative_url }})에 정리했습니다.
