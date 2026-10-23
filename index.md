---
layout: default
title: Meep Examples
---

<div class="home">
<p>Meep(FDTD) 공식 예제를 <strong>처음 보는 사람도 따라갈 수 있게</strong> 풀어 쓴 시리즈입니다.
글마다 같은 구조로 되어 있습니다: 질문 → 물리 한 페이지(결과 보기 전 예측) → 설계도 → 코드 7단계(무엇 / 왜 / 틀리면) → 결과와 예측 비교 → 흔한 실수 → 직접 해보기 → 전체 코드. 순서는 응용전자기학 실습 10주차를 따릅니다(편 번호 = 주차 − 1).</p>

<p><em>A walkthrough series of the official Meep (FDTD) examples for first-time users. Korean body, English TL;DR at the top of every post, English code comments. All scripts live in <a href="https://github.com/jin-castle/meep-examples/tree/main/code">code/</a> and were re-run with Meep 1.33.0 before publishing. Posts are listed in series order.</em></p>

<h2 class="post-list-heading">Posts</h2>
<ul class="post-list">
{% assign ordered = site.posts | sort: "part" %}
{% for post in ordered %}
  <li>
    <span class="post-meta">Part {{ post.part }} · {{ post.date | date: "%Y-%m-%d" }}</span>
    <h3><a class="post-link" href="{{ post.url | relative_url }}">{{ post.title | escape }}</a></h3>
    {% if post.excerpt %}<p>{{ post.excerpt | strip_html | truncate: 200 }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
<p class="rss-subscribe">subscribe <a href="{{ "/feed.xml" | relative_url }}">via RSS</a></p>
</div>
