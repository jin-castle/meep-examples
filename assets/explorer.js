(() => {
  "use strict";
  const english = document.documentElement.lang === "en";
  const cards = [...document.querySelectorAll(".example-card")];
  const search = document.querySelector("#search");
  const filters = [...document.querySelectorAll("[data-filter]")];
  let category = "all";
  const normalize = value => value.normalize("NFKC").toLocaleLowerCase(english ? "en" : "ko").trim();
  function filterCards() {
    const terms = normalize(search.value).split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.forEach(card => {
      const haystack = normalize(`${card.textContent} ${card.dataset.search}`);
      const match = (category === "all" || category === card.dataset.category) && terms.every(term => haystack.includes(term));
      card.hidden = !match;
      if (match) visible += 1;
    });
    document.querySelector("#result-count").textContent = english
      ? `${visible} example${visible === 1 ? "" : "s"}${terms.length ? ` · Results for “${search.value.trim()}”` : " · Start with a question"}`
      : `${visible}개의 예제${terms.length ? ` · “${search.value.trim()}” 검색 결과` : " · 질문에서 시작해 보세요"}`;
    document.querySelector("#no-results").hidden = visible !== 0;
    filters.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.filter === category)));
  }
  search.addEventListener("input", filterCards);
  filters.forEach(button => button.addEventListener("click", () => { category = button.dataset.filter; filterCards(); }));
  document.querySelector("#reset-search").addEventListener("click", () => { category = "all"; search.value = ""; filterCards(); search.focus(); });
  document.querySelectorAll("[data-topic-link]").forEach(link => link.addEventListener("click", () => { category = link.dataset.topicLink; search.value = ""; filterCards(); }));
  document.querySelector(".header-search").addEventListener("click", () => { search.focus({ preventScroll: true }); });
  document.addEventListener("keydown", event => {
    if (event.key === "/" && !event.ctrlKey && !event.metaKey && !event.altKey && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) {
      event.preventDefault(); search.focus(); search.scrollIntoView({ block: "center" });
    }
  });

})();
