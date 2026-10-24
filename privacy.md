---
layout: rights
title: "개인정보 및 방문 통계"
eyebrow: "PRIVACY & ANALYTICS"
description: "방문 통계의 목적, 수집 항목과 선택 방법을 안내합니다."
permalink: /privacy/
lang: ko
updated: "2026-10-24"
toc:
  - { id: analytics, label: "선택적 방문 통계" }
  - { id: choices, label: "동의와 철회" }
  - { id: search, label: "검색 통계와 보고서" }
  - { id: hosting, label: "호스팅·외부 서비스" }
---

<h2 id="analytics">선택적 방문 통계</h2>

[jin-castle](https://github.com/jin-castle)은 학습 자료를 개선하기 위해 Google Analytics 4(GA4)를 사용합니다. **동의하기 전에는 Google Analytics 태그를 불러오거나 통계 요청을 보내지 않습니다.** 거부해도 모든 학습 자료를 읽을 수 있습니다.

동의하면 페이지 조회·방문과 참여 시간·유입 사이트·브라우저 및 기기 정보·대략적인 지역 등의 통계가 Google로 전송·처리됩니다. 전송 과정에서 IP 주소가 Google 서버에 전달될 수 있습니다. 로그인 정보·이메일·이름을 분석 항목으로 보내지 않으며, 페이지 주소의 쿼리와 해시 및 유입 URL의 경로·쿼리는 제거합니다. 검색창 입력값과 캠페인 매개변수는 별도로 수집하지 않습니다.

이 프로젝트 전용 경로에 `meep_ga`로 시작하는 쿠키를 사용하며 만료 기간은 60일로 설정합니다. Google Signals·광고 개인화와 향상된 측정 기능은 사용하지 않습니다. Google의 처리 방식은 [Google 서비스를 사용하는 사이트 및 앱의 정보 이용 안내](https://policies.google.com/technologies/partner-sites)와 [Google 개인정보처리방침](https://policies.google.com/privacy)에서 확인할 수 있습니다.

<h2 id="choices">동의와 철회</h2>

모든 페이지 하단의 **통계 수집 설정**에서 동의하거나 철회할 수 있습니다. 철회하면 이 사이트의 GA 수집을 중단하고 프로젝트의 분석 쿠키를 삭제한 뒤, 이미 태그가 실행된 경우 페이지를 새로 불러옵니다. 철회 이전에 전송된 통계까지 소급 삭제되는 것은 아닙니다.

동의·거부 선택은 이 브라우저의 로컬 저장소(`meep-examples:analytics-consent:v1`)에 보관합니다. 저장소를 지우면 다시 선택하게 됩니다. 저장소를 사용할 수 없는 경우 현재 페이지의 선택만 적용되어 다음 페이지에서 다시 물을 수 있습니다. 언어·테마 선택도 브라우저에 저장하며 이 설정 자체를 분석 이벤트로 보내지 않습니다.

거부 선택을 로컬 저장소에 기록하지 못하면 추적에 사용하지 않는 `meep_analytics_denied` 쿠키로 거부 상태를 60일간 보관합니다. 쿠키와 저장소 모두 차단되어 선택을 저장할 수 없으면 현재 페이지의 수집을 중단하고 이를 화면에 알립니다.

<h2 id="search">검색 통계와 보고서</h2>

GA4 방문 수는 **동의하고 태그가 정상 실행된 방문** 기준입니다. 거부·광고 차단·브라우저 설정의 영향을 받으므로 전체 실제 방문자 수와 일치하지 않을 수 있습니다. 연결 전의 방문 기록을 복원하지 않습니다.

Google Search Console은 Google 검색에서 이 사이트의 노출·클릭·검색어·검색 순위 등을 확인하는 별도 도구입니다. 사이트 방문자를 위한 추가 추적 스크립트를 설치하지 않습니다. 검색어별 전체 시장 검색량을 뜻하지 않으며, Google이 일부 검색어를 익명화하거나 생략할 수 있습니다.

분석 보고서는 관리자 Google 계정의 권한으로 보호합니다. 공개 사이트에는 방문자별 기록이나 대시보드 데이터를 게시하지 않습니다. 관련 문의는 [관리자 GitHub 프로필](https://github.com/jin-castle)에 안내된 연락 수단을 이용하세요.

<h2 id="hosting">호스팅·외부 서비스</h2>

사이트는 GitHub Pages에서 제공합니다. 분석 동의와 별개로 웹페이지 제공에 필요한 요청은 호스팅 사업자가 처리합니다. [GitHub 개인정보처리방침](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement)을 참고하세요. 수식 렌더링 등 외부 리소스를 요청하거나 외부 링크로 이동하면 해당 서비스의 개인정보처리방침이 적용됩니다.
