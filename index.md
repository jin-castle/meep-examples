---
layout: default
title: Meep Examples
---

<div class="home">
<p>Meep(FDTD) 공식 예제를 <strong>처음 보는 사람도 따라갈 수 있게</strong> 풀어 쓴 시리즈입니다.
글마다 같은 구조로 되어 있습니다: 질문 → 물리 한 페이지(결과 보기 전 예측) → 설계도 → 코드 7단계(무엇 / 왜 / 틀리면) → 결과와 예측 비교 → 흔한 실수 → 직접 해보기 → 전체 코드. 시즌 1(01–09)은 응용전자기학 실습 10주차를 따르고(편 번호 = 주차 − 1), 시즌 2부터는 한 주인공을 따라가는 서사로 이어집니다.</p>

<p><em>A walkthrough series of the official Meep (FDTD) examples for first-time users. Korean body, English TL;DR at the top of every post, English code comments. All scripts live in <a href="https://github.com/jin-castle/meep-examples/tree/main/code">code/</a> and were re-run with Meep 1.33.0 before publishing. Posts are listed in series order.</em></p>

{% assign ordered = site.posts | sort: "part" %}
<h2 class="post-list-heading">시즌 1 · 강의 10주차 (01–09)</h2>
<p>빛을 넣고(소스) → 가두고(경계) → 재고(reference run) → 도파관으로 보내고 → 꺾고 → 격자로 갈라 → 렌즈로 모으고 → 컴퓨터가 설계한다.</p>
<ul class="post-list">
{% for post in ordered %}{% if post.part <= 9 %}
  <li>
    <span class="post-meta">Part {{ post.part }} · {{ post.date | date: "%Y-%m-%d" }}</span>
    <h3><a class="post-link" href="{{ post.url | relative_url }}">{{ post.title | escape }}</a></h3>
    {% if post.excerpt %}<p>{{ post.excerpt | strip_html | truncate: 200 }}</p>{% endif %}
  </li>
{% endif %}{% endfor %}
</ul>
<h2 class="post-list-heading">시즌 2 · 점광원의 여행 (10–16)</h2>
<p>01편의 점광원으로 돌아간다. 점광원 옆에 무엇을 두면 빛의 방향과 양이 바뀌고, 그 빛을 어떻게 꺼내 멀리 보내는가. 거울 → 두 거울 사이(LDOS) → 고리에 가두기 → 회전 대칭 → 광추출 효율 → 수천 개의 점광원 → 꺼낸 빛을 모으기.</p>
<ul class="post-list">
{% for post in ordered %}{% if post.part >= 10 %}
  <li>
    <span class="post-meta">Part {{ post.part }} · {{ post.date | date: "%Y-%m-%d" }}</span>
    <h3><a class="post-link" href="{{ post.url | relative_url }}">{{ post.title | escape }}</a></h3>
    {% if post.excerpt %}<p>{{ post.excerpt | strip_html | truncate: 200 }}</p>{% endif %}
  </li>
{% endif %}{% endfor %}
</ul>
<p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | relative_url }}">via RSS</a></p>
</div>
