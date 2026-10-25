---
layout: rights
title: "권리 및 라이선스"
description: "원본 자료의 출처, 이 프로젝트에서 추가한 내용, 코드·글·그림의 이용 조건을 안내합니다."
permalink: /rights-and-licenses/
lang: ko
updated: "2026-10-24"
toc:
  - { id: scope, label: "관리자와 권리 범위" }
  - { id: reuse, label: "자료를 이용하려면" }
  - { id: code, label: "코드 재구성과 라이선스" }
  - { id: images, label: "그림과 AI 도구" }
  - { id: sources, label: "글별 출처와 추가 기여" }
  - { id: third-party, label: "외부 소프트웨어·문의" }
---

<h2 id="scope">관리자와 권리 범위</h2>

이 사이트는 [jin-castle](https://github.com/jin-castle)이 관리·편집하는 Meep 학습 프로젝트입니다. Meep 공식 사이트나 공식 문서의 일부가 아니며, 원본 개발자·논문 저자의 보증이나 제휴를 뜻하지 않습니다.

프로젝트에서 추가한 부분은 한/영 해설과 학습 순서, 관찰·예측·코드 실행·결과 해석을 연결한 구성, 추가 실험과 검증, 공통 그림 helper, 실행 기록, 웹 화면과 상호작용입니다. 이 목록은 프로젝트의 작업 범위를 설명하며, 모든 요소가 한 사람의 독립 창작물이거나 독점적 저작권 대상이라는 주장은 아닙니다. 코드·번역·그림 제작에는 AI 도구를 활용했습니다.

원본 예제·라이브러리·논문·인용 자료의 권리는 해당 권리자에게 있습니다. 물리 법칙, 일반적인 아이디어와 알고리즘, 단순한 수치·사실 자체에 대한 독점권을 주장하지 않습니다. 공동연구·기관·과제 자료가 추가되면 해당 계약과 기여 관계를 별도로 표시합니다.

<h2 id="reuse">자료를 이용하려면</h2>

- **원본·제삼자 자료:** 해당 파일의 라이선스와 원저작자 고지가 우선합니다. 이 사이트의 안내가 이미 부여된 이용 권한을 제한하지 않습니다.
- **프로젝트에서 새로 추가한 글·창작 도해·화면 구성:** 보호되는 창작적 표현에 관해 별도 표시가 없으면 권리를 유보합니다. 출처를 표시하는 것만으로 글 전체의 복제·번역·재배포 허락이 생기지는 않습니다. 법령상 허용되는 인용 등은 별개입니다.
- **코드:** 저장소 전체에 적용하는 새 MIT·CC 라이선스를 부여하지 않습니다. 기존 원본의 라이선스와 파일별 조건을 먼저 확인하세요. 독립 작성 부분의 이용 허락이 필요하면 대상 파일을 지정해 문의하세요.
- **계산 결과와 AI 그림:** 아래의 제작 방식과 예외를 확인하세요. 공개 파일이나 생성 기록이 있다는 사실만으로 독점적인 권리나 재사용 허락을 입증하지는 않습니다.

글을 소개할 때는 작성자, 글 제목, 페이지 링크와 확인일을 함께 적는 것을 권합니다. 예: `jin-castle, 「원통 좌표와 회전 대칭」, Meep Examples, 해당 페이지 URL, 확인일`.

<h2 id="code">코드 재구성과 라이선스</h2>

함수·클래스·설정 파일로 나누고, 공통 helper와 실험·검증 단계를 추가하는 재구성은 학습과 재현성에 도움이 됩니다. 그러나 **원본 코드를 재배치·수정하거나 변수명을 바꾸는 것만으로 원본의 라이선스 의무가 없어지지는 않습니다.** 수정·배포하는 코드에는 적용되는 원본 조건, 저작권 고지, 필요한 소스와 변경 사항 안내를 유지해야 합니다.

[Meep 공식 라이선스 안내](https://meep.readthedocs.io/en/latest/License_and_Copyright/)는 Meep을 GNU GPL v2 또는 이후 버전으로 배포하며, **Meep 배포 코드를 포함하지 않고 사용자가 작성하여 실행 시 불러오는 Python·Scheme 제어 파일**에는 해당 GPL 제한이 자동 적용되지 않는다고 설명합니다. 공식 예제 코드를 복사·개작한 파일인지와 독립적으로 작성한 제어 파일인지는 별도로 판단해야 합니다.

이 저장소의 여러 과학 코드와 글은 공식 예제와 변경한 조건을 명시하고 있습니다. 현재 목록은 출처와 추가 작업을 정리한 것으로, 모든 파일의 줄별 복사·독립 작성 여부를 확정한 감사 결과는 아닙니다. 원본에서 가져온 부분을 독점적인 자체 코드로 표시하거나, 구조화만을 이유로 다른 라이선스로 바꾸지 않습니다. Meep의 고지와 GPL 사본 위치는 [THIRD_PARTY_NOTICES.md](https://github.com/jin-castle/meep-examples/blob/main/THIRD_PARTY_NOTICES.md)에서 확인할 수 있습니다.

현재 [Beam Lab]({{ '/optical-beams/' | relative_url }})의 `code/beam_lab/`는 광원 프로파일·Meep 제어·분석을 새로 작성한 구현입니다. Optical-beams-MEEP는 시각화와 주제의 참고 자료이며, 이 구현은 보존된 `optbeam`이나 기존 실행 wrapper를 불러오지 않습니다. 기존 원본 코드의 실행 결과·3D vortex·렌더링은 [별도 재현 기록]({{ '/optical-beams/archive/' | relative_url }})에 보존하고, 해당 원본 코드와 MIT 고지를 계속 유지합니다.

<h2 id="images">그림과 AI 도구</h2>

**개념도:** `assets/illustrations/`의 14개 챕터 그림은 imagegen으로 제작한 설명용 PNG입니다. 각 챕터마다 한국어·영어와 light·dark의 네 버전을 제공합니다. 프롬프트·크기·해시는 [생성 manifest]({{ '/assets/illustrations/manifest.json' | relative_url }})에 기록했습니다. 개념도는 계산된 장이나 최적화 결과가 아닙니다.

**계산 그림:** `assets/meep/`의 장·스펙트럼·밀도·GIF 등은 게시된 실행·렌더링 코드 및 계산 기록과 연결됩니다. 이 결과를 테마에 맞추기 위해 생성형 AI로 다시 그리거나 색상 반전하지 않습니다. 그림을 새로 렌더링했다는 사실이 원본 코드·모델·인용 자료의 권리를 이전하지는 않습니다.

**재현 기록의 원본 이미지 예외:** Optical beams [재현 기록]({{ '/optical-beams/archive/' | relative_url }})의 `gallery/vortex_3d_comparison.png` 왼쪽 패널은 Daniel Kotik 프로젝트의 원본 이미지입니다. [고정된 원본 링크](https://github.com/DanielKotik/Optical-beams-MEEP/blob/ca145119e5bd0f0804d846ea42e35e4c3daa91de/scripts/Laguerre_Gauss_3d/img/vortex_beam_m_2_3d_half_resized.png)와 [비교 그림 출처 기록]({{ '/assets/meep/optical-beams/gallery/comparison-provenance.json' | relative_url }})을 함께 보존합니다. 이 이미지와 기존 실행 결과는 새 Beam Lab 실험 결과로 표시하지 않습니다.

AI 산출물 전체에 사람의 독점 저작권이 자동으로 생긴다고 주장하지 않습니다. 사람이 창작적으로 작성·수정·구성한 부분과 도구가 생성한 부분을 구분하며, 보호 여부와 범위는 실제 기여에 따라 달라집니다. manifest는 제작 기록이며 저작권 등록증이나 독점 소유권 증명이 아닙니다. [한국저작권위원회 안내](https://library.copyright.or.kr/userInfo.do/10220/contents/7522251)를 참고하세요.

<h2 id="sources">글별 출처와 추가 기여</h2>

다음은 14개 챕터와 두 주제 글의 주요 출처·구현·프로젝트 추가 작업입니다. 각 글의 참고 자료에는 세부 API, 논문과 관련 이슈를 더 기록했습니다. Meep의 `latest` 문서와 `master` 코드 링크는 갱신될 수 있으며, 정확한 과거 실행 소스를 고정했다는 뜻은 아닙니다. 게시된 주요 실행 환경은 Meep 1.33.0이며 Optical-beams 재현 기록의 원본은 별도 commit으로 고정했습니다.

{% include source-inventory.html %}

<h2 id="third-party">외부 소프트웨어·문의</h2>

- **Meep:** Massachusetts Institute of Technology(MIT) 및 기여자, GNU GPL v2 또는 이후 버전. Python 제어 파일 예외의 범위는 위 설명을 따릅니다.
- **Optical-beams-MEEP:** Daniel Kotik·Jörg Götte의 프로젝트. 현재 Beam Lab의 시각화·주제 참고 자료이며, 별도 재현 기록에서 실행한 원본 코드도 보존합니다. 보존한 원본 코드는 MIT License이며 `Copyright (c) 2018 Daniel Kotik` 고지와 [라이선스 전문](https://github.com/jin-castle/meep-examples/blob/main/code/optical_beams/source/LICENSE)을 유지합니다.
- **GSAP 3.15.0:** GreenSock, [GSAP Standard License](https://gsap.com/standard-license/). 로컬 배포 파일의 원본 고지를 보존합니다.
- **MathJax 2.7.9:** cdnjs에서 불러오는 수식 렌더러, [Apache License 2.0](https://github.com/mathjax/MathJax/blob/2.7.9/LICENSE).
- **Jekyll·Minima 및 빌드 도구:** GitHub Pages 환경에서 사용합니다. 버전별 라이선스와 관련 링크는 고지 파일에 정리했습니다. CSS의 글꼴 이름은 설치된 글꼴의 대체 목록이며 글꼴 파일을 함께 배포하지 않습니다.

범위·버전·원본 고지·알려진 한계는 [THIRD_PARTY_NOTICES.md](https://github.com/jin-castle/meep-examples/blob/main/THIRD_PARTY_NOTICES.md)를 기준으로 함께 확인하세요. 출처 정정이나 이용 허락 요청은 [GitHub 저장소](https://github.com/jin-castle/meep-examples)에 해당 페이지·파일과 원하는 이용 범위를 알려주세요.
