# Optical-beams-MEEP 원본 실행 기록

이 폴더는 재현 코드와 원본 소스를 보관합니다. 게시된 그림·실행 검사·출처는
[`assets/meep/optical-beams/`](../../assets/meep/optical-beams/)에 있습니다.
아래 명령을 실행하면 이 코드 폴더에 새 결과와 그림이 생성됩니다.

Daniel Kotik와 Jörg Götte의 Optical-beams-MEEP에서 제공하는 `Gauss2d.py`를 실제 PyMeep로 실행한 교육용 예제입니다. 원본 이미지의 재사용이 아니라 이번 실행의 전자기장 데이터를 새로 그렸습니다.

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

## 출처와 라이선스

- 원본 설명: https://danielkotik.github.io/Optical-beams-MEEP/
- 실행 소스: https://github.com/DanielKotik/Optical-beams-MEEP/tree/ca145119e5bd0f0804d846ea42e35e4c3daa91de
- `Gauss2d.py` 및 `optbeam/`는 v2.1.2 릴리스와 동일함을 git diff로 확인했습니다. 현재 고정 commit의 추가 변경은 문서, 인용 정보, 빌드 설정에 있습니다.
- 버전별 소프트웨어 인용: Daniel Kotik & Jörg Götte, Optical-beams-MEEP v2.1.2 (2021), https://doi.org/10.5281/zenodo.5211251
- Zenodo는 이 레코드를 software로 분류합니다. 별도의 동료심사 논문이라고 표기하지 않습니다.
- 원본 코드는 MIT License, Copyright (c) 2018 Daniel Kotik입니다. 배포 시 `source/LICENSE`를 함께 보존합니다.

`source/`에는 실제 실행한 원본 소스의 복사본, MIT 전문, CITATION.cff를 포함했습니다. 두 개의 wrapper/render 스크립트는 이 교육용 재현을 위해 추가했습니다.
