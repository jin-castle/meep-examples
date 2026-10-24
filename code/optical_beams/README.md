# Optical-beams-MEEP 원본 실행 기록

이 폴더는 재현 코드와 원본 소스를 보관합니다. 게시된 그림·실행 검사·출처는
[`assets/meep/optical-beams/`](../../assets/meep/optical-beams/)에 있습니다.
아래 명령을 실행하면 이 코드 폴더에 새 결과와 그림이 생성됩니다.

Daniel Kotik와 Jörg Götte의 Optical-beams-MEEP에서 제공하는 Gaussian, Laguerre–Gauss, Airy 예제를 PyMeep로 실행하는 교육용 재현 코드입니다. 평면·곡면 Gaussian, LG 3D와 Airy 2D 실행을 모두 완료했고, 게시 그림은 이번 Meep 실행에서 얻은 전자기장 데이터를 새로 그렸습니다.

## 실행한 조건

| 항목 | 값 |
|---|---|
| 경계면 | planar dielectric interface |
| 편광 | s 편광, 2D에서 Ez |
| 굴절률 | n1=1.54, n2=1.00 |
| 입사각 | 30도와 45도, 경계면 법선 기준 |
| 셀 / PML | 5a × 5a / 0.25a |
| 주파수 | 12 c/a, 진공파장 a/12 |
| 해상도 | 184.8 pixels/a; 높은 굴절률 매질 파장당 10픽셀 |
| 실행 시간 | 10 a/c = 진공 광학 주기 120개 |
| 자원 | MPI 1 process, OMP/BLAS/MKL 각 1 thread |

입사각 30도만 원본 기본값 45도에서 변경했습니다. 45도 사례는 원본 물리·수치 기본값을 그대로 사용했습니다. 해상도, PML, 소스, Courant=0.5와 종료시간을 변경하지 않았습니다. 길이 단위 a의 실제 길이를 지정하지 않았으므로 이 예제에 마이크로미터 단위를 붙이지 않습니다.

## 결과를 읽는 방법

- `wavefront_comparison.png`: 두 조건의 실제 최종 순간장 Ez(t)를 회색 유전율 배경에 표시합니다. 두 조건은 동일한 발산형 색상 척도를 사용합니다. 약한 장을 배경과 합성하기 위한 불투명도 sqrt(|Ez|/공통최대값)는 표시만 바꾸며 데이터는 변경하지 않습니다.
- `intensity_comparison.png`: 마지막 두 광학 주기의 실제 샘플에 cos/sin/DC 최소제곱 적합을 수행해 얻은 시간평균 Ez²=|phasor|²/2입니다. 선형 hot 척도와 공통 최대값을 사용합니다. 이것은 Poynting flux 또는 투과효율이 아닙니다.
- `planar30.gif`, `planar45.gif`: 마지막 두 주기에 수집한 62개 실제 FDTD 순간장입니다. 표시용으로 공간 격자를 3칸 간격으로 사용하고 느리게 재생합니다. phasor를 인위적으로 회전시킨 애니메이션이 아닙니다.
- 각 사례의 `planar/*e2_s*.h5`: 원본 코드가 출력한 실수 순간장 제곱 Ez(t)²입니다. 시간평균 세기 그림과 구분해야 합니다.

임계각은 asin(1/1.54)=40.4927도입니다. 30도 입사에서 평면파 Snell 굴절각은 50.3539도이고, 투과 영역의 국소 phasor 위상 기울기로 구한 각은 50.6618도입니다(법선 기준, 차이 0.3080도). 반사 방향은 전역 +x축 기준 30도 사례에서 119.9757도(기대 120도), 45도 사례에서 90.8507도(중심 입사파 기대 90도)입니다. 이 값은 빔 중심 또는 에너지 흐름의 직접 측정이 아닌 국소 위상 진단입니다.

45도는 중심 입사파가 임계각을 넘는 조건입니다. 유한 폭 Gaussian beam은 각도 분포를 가지므로 전체 투과가 정확히 0이라고 단정하지 않습니다. 마지막 두 주기 조화파 적합의 상대 L2 잔차는 각각 0.0822%, 0.0207%입니다. 격자 수렴, PML 수렴, 입사장 분리와 flux 정규화는 수행하지 않았습니다.

## 재현

기존 WSL conda `pmp` 환경의 Python 3.11.15 / Meep 1.33.0 / optbeam 2.1.2 / NumPy 2.4.6 / SciPy 1.17.1 / h5py 3.16.0을 사용했습니다. Scheme/Guile 실행 파일이 없어 같은 프로젝트에서 공식 제공하는 Python 스크립트를 실행했습니다. optbeam 원본의 순수 Python 경로를 사용하므로 Cython 설치나 원본 수정이 필요하지 않았습니다.

이 폴더에서 PyMeep 환경을 활성화한 뒤:

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python run_original.py --upstream source --output planar30 --chi 30 > planar30.log 2>&1
python run_original.py --upstream source --output planar45 --chi 45 > planar45.log 2>&1
python render_results.py --data-dir . > render.log 2>&1
```

`run_original.py`는 원본 `Gauss2d.py`를 수정하지 않고 호출합니다. 추가한 관측 콜백만으로 마지막 두 주기를 저장하며 원본 HDF5 출력도 실행합니다. `checks.json`에는 실제 실행 환경, 배열 유한성, 원본 순간장 제곱과 HDF5의 일치, 위상 방향 진단, 제한 사항을 보관했습니다. `result.json`은 사이트용 요약입니다.

## 곡면 Gaussian: 평면·오목·볼록 비교

원본의 `interface` 선택만 바꾸어 45도 조건의 concave와 convex를 각각 실행했습니다. 평면 45도 결과는 기존 실행의 NPZ, 원본 HDF5, `run.json` SHA-256 일치를 확인해 재사용했습니다. 세 조건 모두 t=10 a/c, 924 × 924 배열이며 원본 순간장 제곱 HDF5와 저장한 Ez²의 최대 절대 차이는 약 1.42 × 10⁻¹⁴입니다.

곡률 매개변수는 원본 기본값 kr_c=150, 반경은 r_c=150/(2π·12)=1.98944a입니다. `concave`는 n1 원기둥 내부와 n2 외부, `convex`는 n2 원기둥 내부와 n1 외부인 원본 명칭을 따릅니다. 45도는 원점에서의 접선 법선에 대한 각도입니다. 곡면 전체에 같은 입사각이 적용되는 것은 아닙니다.

공개 파일은 [`curved/`](../../assets/meep/optical-beams/curved/)에 있습니다.

- `curved_comparison.png`와 `*_hot.png`: 같은 시각의 실수 순간장 Ez(t)²를 검은 배경과 선형 hot 색상으로 표시합니다. 패널마다 최대값을 1로 정규화해 간섭 줄무늬 형태를 비교합니다.
- `curved_common_scale.png`: 세 조건의 공통 최대값 222.3696을 사용합니다. 회색 선은 실제 유전율 경계, 청록색 선은 소스 구간, 흰색 +는 원점입니다. 패널별 정규화 그림과 함께 읽어야 합니다.
- `*_hot.gif`: 마지막 두 주기의 실제 FDTD 샘플 62개를 각각 제곱했습니다. 공간 격자를 3칸 간격으로 표시하고 느리게 재생하며, 각 애니메이션의 색상 최대값은 고정합니다.
- `checks.json`, `provenance.json`, `runs/*/run.json`과 로그: 실행 종료, 원본 해시, 배열 검사와 재사용 근거를 기록합니다. 큰 NPZ/HDF5 배열은 사이트에 올리지 않습니다.

이 hot 그림은 시간평균 Ez²가 아닙니다. 순간 제곱장의 밝고 어두운 줄무늬는 광학 위상에 따라 움직이므로 세 정적 패널은 동일한 t=10을 사용했습니다. 초점 폭, 집광효율, 빔 중심, 반사·투과 flux는 측정하지 않았습니다.

**소스 매질 주의:** concave의 소스 중심은 n1에 있지만 소스 구간의 약한 꼬리 일부가 n2와 만납니다. 401개 소스 위치에서 J²로 가중한 n1 밖 비율은 0.0273%입니다. 이것은 지정한 소스 포락선의 가중치이며 에너지·투과율 측정값이 아닙니다. planar와 convex의 검사한 소스 구간은 모두 n1입니다. 따라서 세 그림을 소스 매질까지 완전히 동일한 곡률 대조 실험으로 해석하지 않습니다.

이 코드 폴더에서 새로 세 조건을 실행하고 렌더링하려면:

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python run_original.py --upstream source --output output/curved/planar45 --chi 45 --interface planar > output-planar45.log 2>&1
python run_original.py --upstream source --output output/curved/concave45 --chi 45 --interface concave > output-concave45.log 2>&1
python run_original.py --upstream source --output output/curved/convex45 --chi 45 --interface convex > output-convex45.log 2>&1
python render_curved.py --data-dir output/curved > output-curved-render.log 2>&1
```

`--interface`의 기본값은 `planar`입니다. 곡면 실행에서도 위 평면 예제의 해상도, PML, 주파수, Courant와 종료시간을 유지합니다. 새 `run.json`에는 실제 실행 바이트의 `source_sha256`과 비교용 `source_sha256_lf_normalized`를 함께 저장합니다. 렌더러는 알려진 원본의 CRLF/LF 해시와 LF 정규화 해시를 검사합니다. 정규화 필드가 없는 기존 실행도 알려진 두 원본 해시 중 하나일 때만 허용합니다.

## Laguerre–Gauss 3D와 Airy 2D

원본 `LaguerreGauss3d.py`와 `Airy2d.py` 및 대응 Scheme 파일도 `source/scripts/`에 보존했습니다. `run_gallery.py`는 원본 Python 스크립트를 불러오되, LG 소스 적분과 출력 수집을 아래 방식으로 처리합니다.

| 항목 | Laguerre–Gauss 3D | Airy 2D |
|---|---|---|
| 소스 | m=2, e_z=1, e_y=0, kw_0=8, kr_w=0 | s 편광, kw_0=7, kr_w=0, M=0, W=4 |
| 굴절률 / 각도 | n1=1, n2=1.54 / 45도 | n1=n2=1 / 45도 |
| 셀 | 5a × 5a × 4a | 10a × 10a |
| 주파수 / 해상도 | 5 c/a / 77 pixels/a | 12 c/a / 180 pixels/a |
| PML / Courant | 0.25a / 1/3 | 0.25a / 0.5 |
| 종료시간 | 10 a/c = 진공 주기 50개 | 90 a/c = 진공 주기 1080개 |

LG의 원본 방위각 φ 적분을 Bessel 함수 J_m을 이용해 해석적으로 축약하고 남은 θ 적분을 수치 계산합니다. 근축 근사를 추가하지 않았고 FDTD 격자, 물리 조건, 시간 간격과 종료시간도 바꾸지 않았습니다. 네 사분면을 포함하는 23개 위치에서 원본 이중 적분과 대조한 최대 절대 오차는 4.52 × 10⁻¹⁰, 진폭이 10⁻⁶을 넘는 점들의 최대 상대 오차는 2.50 × 10⁻⁹입니다. 이 수치는 검사 위치의 소스 함수 동등성 검사이며 전체 공간의 오차 상한은 아닙니다. 세부 값은 LG 출력 폴더의 `source-validation.json`에 저장합니다.

출력은 Meep native `get_array`로 수집합니다. LG는 각 성분을 공통 배열 중심으로 보간한 뒤 real2=Σ_j Re(E_j)², imag2=Σ_j Im(E_j)²를 저장하며, 둘의 합은 Σ_j |E_j|²입니다. 원본의 비선형 `output_field_function` 콜백과는 보간·제곱 순서가 달라 바이트 단위 일치를 주장하지 않습니다. z=0 종단면과 x=−1.5a 횡단면의 복소 성분도 별도로 보존합니다. Airy는 t=90의 실제 Ez와 Ez², 유전율을 저장합니다.

그림은 선형 hot 색상을 사용합니다. LG의 별도 2D 단면은 전체 3D real2 최대값의 20%를 색상 상한으로 사용해 그보다 큰 값은 포화시킵니다. Airy의 색상 상한은 해당 순간장 제곱의 전체 최대값입니다. 서로 다른 패널 밝기를 효율 비교로 해석하지 않습니다.

3D는 `prepare_vortex_scene.py`가 VTK 9.5.2의 `vtkContourFilter`로 전체 해상도 등위면을 추출하고 `render_vortex_blender.py`가 Blender 4.5.14 Cycles CPU 한 스레드로 렌더링합니다. 가장자리 30칸을 제외한 하반부 325×325×125 표본을 stride=1로 사용합니다. 원본의 inclusive 끝점 규칙을 따라 z의 첫 양의 표본 +0.0064935a까지 포함합니다. real2 등위면은 전체 real2 최대값의 2%이며 삼각형 1,308,590개입니다. 메시 축소나 형상 평활화 없이 VTK 법선을 사용합니다. 실제 셀 5a×5a×4a와 native 좌표를 유지하며 과거 원본 렌더러의 높이 3.5a 하드코딩을 적용하지 않습니다.

입사 쪽 x=−2.0974026a와 반사 쪽 y=2.1103896a의 native 경계 단면 두 개, x=y 매질 경계를 보여 주는 회전된 반투명 블록, Snell 법칙의 입사·반사·굴절 방향을 나타내는 빨간 선을 함께 그립니다. 각 스칼라의 두 단면 색상 상한도 그 스칼라의 전체 최대값 2%입니다. 원본 Mayavi 카메라의 polar elevation과 순차 회전을 적용합니다. 블록은 표시용 유한 범위이며 실제 시뮬레이션의 추가 매질 경계를 뜻하지 않고, 빨간 선은 측정한 에너지 궤적이 아닙니다.

실제 셀 범위와 주석에 5% 화면 여백이 생기도록 카메라 거리만 조정합니다. 기본 출력은 1200×1200, Cycles 64 samples, 노이즈 제거 사용이며 장 데이터와 등위면 형상은 변경하지 않습니다. `native3d-checks.json`은 원본 장의 해시, 모든 등위면 꼭짓점에서 보간한 장 값의 잔차와 실제 방향선 끝점 좌표를 검사합니다.

- `vortex_3d.png`: 순간 실수장 제곱 합 Σ Re(Ej)²의 등위면입니다. 재료 표면이 아닙니다.
- `vortex_3d_modulus.png`: 같은 저장 장에서 Σ |Ej|²를 계산한 대안이며 자체 최대값의 2%를 사용합니다.
- `vortex_3d_comparison.png`: 왼쪽은 원본 프로젝트의 200픽셀 PNG를 확대한 참조, 가운데는 이전 stride6 그림, 오른쪽은 native-grid 재렌더입니다. 이전 방식은 순간 제곱장 파면을 undersampling하여 형상을 훼손했으므로 재현 예시로 사용하지 않습니다.

원본 Mayavi 스크립트는 기본적으로 real2+imag2를 선택하고 real2만 선택하는 줄도 제공합니다. 역사적 PNG의 정확한 실행·렌더링 설정은 제공되지 않았으므로 픽셀 동일성을 주장하지 않습니다. 렌더 샘플 수·해상도·실제 버전은 최종 렌더 메타데이터를 기준으로 확인합니다.

이 코드 폴더에서 실행하려면:

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p output/gallery/lg output/gallery/airy
python run_gallery.py --upstream source --output output/gallery/lg --beam lg > output/gallery/lg/run.log 2>&1
python run_gallery.py --upstream source --output output/gallery/airy --beam airy > output/gallery/airy/run.log 2>&1
python -m pip install vtk==9.5.2
python prepare_vortex_scene.py output/gallery
blender --background --factory-startup --threads 1 --python render_vortex_blender.py -- output/gallery
python render_gallery.py output/gallery > output-gallery-render.log 2>&1
```

전처리는 Meep을 실행한 WSL 과학계산 Python 환경에서 수행합니다. Blender는 별도 설치한 4.5.14 실행 파일이며 자체 Python·NumPy를 사용하므로 WSL 환경에 `bpy`를 설치하지 않습니다. 명령의 `blender`를 실제 실행 파일 경로로 바꾸세요. WSL에서 Windows Blender를 호출할 때는 `--python` 스크립트와 `--` 뒤 결과 폴더에 Windows 절대 경로를 전달합니다. 저장된 `lg/fields.h5`와 `airy/fields.npz`가 있으면 시뮬레이션 명령 두 개를 생략하고 전처리부터 실행할 수 있습니다.

LG는 약 4,565만 셀 규모입니다. 2026-10-24 단일 코어 실행은 실제 385 × 385 × 308 배열, t=10, 2,310단계로 완료됐고 모든 배열이 유한했습니다. 소스 검사·초기화·출력을 포함한 측정 시간은 3,105.36초(51.76분), 관측 메모리는 약 9.77 GiB였습니다. 이어 실행한 원본 Airy도 1800 × 1800 배열, t=90, 32,400단계로 완료됐으며 모든 배열이 유한했습니다. 측정 시간은 399.49초(6.66분)이고 유전율은 전 영역에서 1입니다.

LG의 x=−1.5a 횡단면에서 반경 0.6a 원을 따라 측정한 복소 Ez 위상 감김은 2.0으로 소스 차수 m=2와 일치했습니다. 두 단면의 Re²+Im²=|E|² 상대 오차는 5.58 × 10⁻¹⁶ 이하이고 Airy Ez² 일치 검사는 정확히 통과했습니다. `vortex_longitudinal.png`, `vortex_transverse.png`, `vortex_3d.png`, `airy_free_space.png`의 해시와 검사 결과는 갤러리 출력의 `checks.json`, 실행 종료·조건은 각 `result.json`, 등위면 삼각형 수·표시 기준과 출처는 `provenance.json`에 보존했습니다.

Airy 소스 초기화에서는 원본 수치 적분의 세분화 한계·느린 수렴 경고 3개가 기록됐습니다. 유한한 장과 정상 종료만으로 소스 적분의 수렴이나 물리 정확도를 보장하지 않으며, 격자·PML 수렴과 flux 효율 검사는 하지 않았습니다. 원본 갤러리 이미지의 모든 생성 파라미터가 제공된 것은 아니므로 여기서는 보존한 기본값의 실행을 재현합니다.

## LG 3D 위상 애니메이션 재현

이 경로는 요청한 3D 등위면 애니메이션을 생성합니다. 위 정적 렌더 단계에서 만든 `output/gallery/vortex_3d.blend`, `output/gallery/native3d/scene.json`, `output/gallery/lg/fields.h5`가 먼저 필요합니다. 기존 3D 파일의 `real2`와 `imag2`만으로는 위상 변화에 필요한 교차항 C를 복원할 수 없으므로, 아래 `--capture-motion` 실행을 한 번 추가해야 합니다. 새 패키지를 설치하지 않고 앞서 사용한 Meep·VTK·Blender 환경을 재사용합니다.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p output/gallery/animation/data/lg
python run_gallery.py --upstream source --beam lg --capture-motion --output output/gallery/animation/data/lg > output/gallery/animation/data/lg/run.log 2>&1
python prepare_vortex_animation.py output/gallery --frames 24
blender --background --factory-startup --threads 1 --python-exit-code 1 --python animate_vortex_blender.py -- output/gallery --material diffuse --samples 16 --resolution 720
python package_vortex_animation.py output/gallery --duration-ms 80
```

물리 조건과 native 해상도 77 pixels/a, CPU 한 코어를 유지하고 t₀=10 a/c에서 A=Σ Re(Ej)², B=Σ Im(Ej)², C=Σ Re(Ej)Im(Ej)를 저장합니다. 이어 실제 FDTD를 0.11 a/c 더 진행해 최소 네 시각을 검사합니다. 표시 대상 하반부 체적과 두 단면의 모든 native 표본을 포함해 계산한 상대 L2 오차가 세 영역에서 각각 1% 미만이어야 전처리를 통과합니다. 이번 추가 실행은 정상 종료했고, 네 시각을 직접 비교한 최대 상대 L2 오차는 9.36116×10⁻⁴(0.09361%)로 통과했습니다.

재구성식은 `F²(φ) = A cos²φ + B sin²φ + 2C sinφ cosφ`입니다. `exp(−iφ)` 시간 관례에서 교차항 부호는 양수입니다. t₀의 복소 순간장에 단색파 위상 변화를 적용한 결과이며, 실제 과도응답 영상을 저장한 것도 DFT 누적장을 사용한 것도 아닙니다. f=5 c/a에서 제곱장의 반복 주기는 T/2=0.1 a/c입니다. 24개 프레임은 끝점을 제외한 φ∈[0,π)를 표시하고, 80 ms는 프레임 재생시간입니다.

전체 3D 영역의 각 voxel에서 위상 최대값 `(A+B+sqrt((A−B)²+4C²))/2`를 계산한 뒤 그 전역 최대값의 2%를 모든 프레임의 등위면과 단면 색상 상한으로 고정합니다. 정적 장면과 같은 가장자리 30칸 제외·하반부 범위에서 native voxel을 stride=1로 모두 사용하며 메시 축소나 형상 평활화는 하지 않습니다. 기존 장면의 두 측정 단면 위치, 매질 블록, 빨간 방향선과 카메라를 유지하고 장 등위면과 단면 텍스처를 위상에 맞춰 갱신합니다. 방향선은 측정한 에너지 궤적이 아닙니다.

기본 `--material diffuse`는 원본 Mayavi의 색상 `(0.227, 0.188, 0.188)`과 opacity=0.5를 참고한 반투명 표시입니다. 원본 설정은 거울 재질이 아니며, 표시용 불투명도 0.5를 물리적 투과율 50%로 해석하지 않습니다. 아래 선택적 정적 미리보기로 약한 광택을 비교할 수 있습니다. 재질 변경은 Meep 장이나 유전율 경계를 바꾸지 않습니다.

```bash
blender --background --factory-startup --threads 1 --python-exit-code 1 --python animate_vortex_blender.py -- output/gallery --preview --material glossy --samples 16 --resolution 720
```

생성 대상은 `output/gallery/animation/vortex/`의 `vortex_wavefront.gif`, `vortex_wavefront.webp`, `poster.png`, `contact_sheet.png`입니다. 직접 FDTD 비교는 `animation/data/lg/motion-validation.json`, 전처리·고정 정규화는 `animation/vortex/animation.json`, 렌더 완료는 `animation/vortex/rendered/render.json`, 패키징 검사는 `animation/vortex/checks.json`에서 확인합니다. 이는 해당 격자에서의 위상 재구성 검사이며 격자·PML 수렴이나 투과효율 검증을 대체하지 않습니다. WSL에서 Windows Blender를 호출할 때의 절대 경로 규칙은 위 정적 렌더와 같습니다.

## 출처와 라이선스

- 원본 설명: https://danielkotik.github.io/Optical-beams-MEEP/
- 실행 소스: https://github.com/DanielKotik/Optical-beams-MEEP/tree/ca145119e5bd0f0804d846ea42e35e4c3daa91de
- 소스 SHA-256은 실제 실행한 CRLF 바이트를 기준으로 보존합니다. Git 저장소가 LF로 정규화할 수 있으므로 CRLF→LF 변환 후의 비교용 해시도 기록합니다. 평면·곡면 기록의 키는 `source_sha256_lf_normalized`, 갤러리 `provenance.json`의 키는 `source_hashes.*.canonical_lf_sha256`입니다.
- `Gauss2d.py` 및 `optbeam/`는 v2.1.2 릴리스와 동일함을 git diff로 확인했습니다. 현재 고정 commit의 추가 변경은 문서, 인용 정보, 빌드 설정에 있습니다.
- 버전별 소프트웨어 인용: Daniel Kotik & Jörg Götte, Optical-beams-MEEP v2.1.2 (2021), https://doi.org/10.5281/zenodo.5211251
- Zenodo는 이 레코드를 software로 분류합니다. 별도의 동료심사 논문이라고 표기하지 않습니다.
- 원본 코드는 MIT License, Copyright (c) 2018 Daniel Kotik입니다. 배포 시 `source/LICENSE`를 함께 보존합니다.

`source/`에는 사용한 원본 소스의 복사본, MIT 전문, CITATION.cff를 포함했습니다. `run_original.py`, `render_results.py`, `render_curved.py`, `run_gallery.py`, `prepare_vortex_scene.py`, `render_vortex_blender.py`, `render_gallery.py`, `prepare_vortex_animation.py`, `animate_vortex_blender.py`, `package_vortex_animation.py`는 이 교육용 재현을 위해 추가한 실행·관측·그림 코드입니다. 원본 소스 파일은 수정하지 않습니다.
