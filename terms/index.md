---
layout: concepts
permalink: /terms/
lang: ko
title: "개념 사전 — Meep Examples"
lesson_title: "Meep 개념 사전"
lesson_summary: "Meep 코드를 짜고 결과를 읽을 때 필요한 FDTD 개념을 하나씩 정리합니다. 항목마다 정의와 수식, Meep 코드 블록, 예제에서의 쓰임, 코드는 돌아가는데 결과가 틀리는 경우, inverse design에서 달라지는 점을 같은 순서로 적습니다."
axes:
  - { key: numerics, label: "수치해석", note: "격자와 시간 간격, 경계, 수렴처럼 FDTD라는 계산 방법에서 나오는 개념입니다." }
  - { key: block, label: "Meep 블록", note: "source, monitor, 경계, 재료처럼 Meep 코드에서 한 덩어리로 쓰는 요소와 그 사용 규칙입니다." }
  - { key: em, label: "전자기학", note: "편광, 모드, 회절, LDOS처럼 계산 결과를 해석하는 데 필요한 물리 개념입니다." }
  - { key: invdes, label: "Inverse design", note: "설계 영역, 목적함수, adjoint gradient처럼 역설계에서 새로 등장하는 개념입니다." }
---

[Meep 공식 문서](https://meep.readthedocs.io/en/master/)는 API와 튜토리얼을 잘 설명하지만, 한 개념이 코드의 어느 줄에 해당하고 어떤 실수가 결과를 조용히 틀리게 만드는지는 여러 페이지에 흩어져 있습니다. 이 사전은 그것을 개념 단위로 모읍니다. 수치는 이 사이트의 예제 글이나 이 페이지에서 실행한 Meep 계산에서 인용하고, 출처가 공식 문서인 문장은 링크를 붙입니다.

모든 항목은 같은 일곱 절로 되어 있습니다. 무엇인가 · 왜 필요한가 · Meep 코드에서 · 예제에서의 쓰임 · 돌아가는데 틀리는 경우 · inverse design에서 · 연결. 예제 글을 읽다가 모르는 개념이 나오면 이 사전에서 해당 항목의 1절과 3절을 먼저 보고, 계산 결과가 이상하면 5절의 증상 표에서 시작하세요.

항목은 예제 글에 실제로 쓰인 개념부터 차례로 추가합니다.
