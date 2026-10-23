(() => {
  "use strict";
  const cards = [...document.querySelectorAll(".example-card")];
  const search = document.querySelector("#search");
  const filters = [...document.querySelectorAll("[data-filter]")];
  let category = "all";
  const normalize = value => value.normalize("NFKC").toLocaleLowerCase("ko").trim();
  function filterCards() {
    const terms = normalize(search.value).split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.forEach(card => {
      const haystack = normalize(`${card.textContent} ${card.dataset.search}`);
      const match = (category === "all" || category === card.dataset.category) && terms.every(term => haystack.includes(term));
      card.hidden = !match;
      if (match) visible += 1;
    });
    document.querySelector("#result-count").textContent = `${visible}개의 예제${terms.length ? ` · “${search.value.trim()}” 검색 결과` : " · 질문에서 시작해 보세요"}`;
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

  const scene = document.querySelector(".story-figure");
  const steps = [...document.querySelectorAll("[data-step]")];
  const stageLinks = [...document.querySelectorAll("[data-stage-link]")];
  const stages = {
    1: ["01 / FORWARD", "Forward field", "입력에서 목표 출력으로 진행하는 빛의 개념도입니다. 수치 시뮬레이션 장을 나타내지 않습니다.", "빛을 보내고 출력을 관찰합니다.", "전파 방향 개념도 · 수치장 아님"],
    2: ["02 / ADJOINT", "Adjoint field", "같은 구조에서 출력에 놓인 adjoint source가 별도 계산을 수행합니다. 원래 입력 광원은 꺼져 있습니다.", "목표 출력에서 구조의 영향을 되짚습니다.", "같은 구조 · 별도의 계산 · 입력 광원 OFF"],
    3: ["03 / GRADIENT → UPDATE", "실제 signed adjoint gradient와 저장된 밀도", "09편에서 계산한 초기 11 곱하기 11 signed gradient입니다. 파랑은 음수, 빨강은 양수입니다. 오른쪽은 MMA 5회 평가 뒤 저장된 밀도이며 단일 gradient step 결과가 아닙니다.", "픽셀마다 민감도를 읽고, 밀도를 갱신합니다.", "실제 초기 gradient → MMA 5회 평가 후 밀도 · 09편"]
  };
  let densityRequested = false;
  async function loadDensity() {
    if (densityRequested) return;
    densityRequested = true;
    try {
      const response = await fetch("./assets/meep/09/result.json");
      if (!response.ok) throw new Error(`Density request: ${response.status}`);
      const result = await response.json();
      const values = result.x_optimized;
      if (!Array.isArray(values) || values.length !== 121 || values.some(value => !Number.isFinite(value) || value < 0 || value > 1)) throw new Error("Invalid density data");
      const grid = document.querySelector("#density-grid");
      const cells = document.createDocumentFragment();
      for (let row = 0; row < 11; row += 1) {
        for (let x = 0; x < 11; x += 1) {
          // NumPy reshape(Nx, Ny).T with origin='lower': y grows upward.
          const density = values[x * 11 + (10 - row)];
          const shade = Math.round(255 * (1 - density));
          const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
          rect.setAttribute("x", String(410 + x * 12));
          rect.setAttribute("y", String(230 + row * 12));
          rect.setAttribute("width", "12");
          rect.setAttribute("height", "12");
          rect.setAttribute("fill", `rgb(${shade},${shade},${shade})`);
          const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
          title.textContent = `ρ[${x},${10 - row}] = ${density.toFixed(4)}`;
          rect.append(title); cells.append(rect);
        }
      }
      grid.replaceChildren(cells);
    } catch (error) {
      document.querySelector("#density-label").textContent = "밀도 로딩 실패 · 아래 계산 결과 링크 참고";
      const mobileDensity = document.querySelector(".mobile-data-panels figure:last-child");
      mobileDensity.querySelector("svg").setAttribute("aria-label", "밀도 데이터를 불러오지 못했습니다");
      mobileDensity.querySelector("figcaption").textContent = "밀도 로딩 실패 · 계산 결과 링크 참고";
      document.querySelector(".scene-explanation").dataset.densityError = "true";
      console.warn("Meep design data could not be loaded", error.message);
    }
  }
  function setStage(stage) {
    const content = stages[stage];
    scene.dataset.stage = stage;
    ["#scene-stage", "#physics-title", "#physics-description", "#scene-summary", "#scene-note"].forEach((selector, index) => { document.querySelector(selector).textContent = content[index]; });
    stageLinks.forEach(link => {
      if (link.dataset.stageLink === String(stage)) link.setAttribute("aria-current", "step");
      else link.removeAttribute("aria-current");
    });
    if (Number(stage) === 3) loadDensity();
  }
  stageLinks.forEach(link => link.addEventListener("click", () => setStage(link.dataset.stageLink)));
  if ("IntersectionObserver" in window) {
    const ratios = new Map();
    let stepObserver;
    function observeChapters() {
      if (stepObserver) stepObserver.disconnect();
      ratios.clear();
      const narrow = window.matchMedia("(max-width: 680px)").matches;
      const topInset = narrow ? Math.min(window.innerHeight - 96, Math.ceil(scene.getBoundingClientRect().height) + 80) : 150;
      stepObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => ratios.set(entry.target, entry.isIntersecting ? entry.intersectionRatio : 0));
        const active = steps.reduce((best, step) => (ratios.get(step) || 0) > (ratios.get(best) || 0) ? step : best, steps[0]);
        if ((ratios.get(active) || 0) > 0) setStage(active.dataset.step);
      }, { rootMargin: `-${topInset}px 0px -12% 0px`, threshold: [0, .1, .25, .5, .75, 1] });
      steps.forEach(step => stepObserver.observe(step));
    }
    observeChapters();
    if ("ResizeObserver" in window) {
      new ResizeObserver(() => {
        document.documentElement.style.setProperty("--scene-height", `${Math.ceil(scene.getBoundingClientRect().height)}px`);
        observeChapters();
      }).observe(scene);
    }
    let resizeTimer;
    window.addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(observeChapters, 150); });
    const visibilityObserver = new IntersectionObserver(entries => entries.forEach(entry => entry.target.classList.toggle("is-offscreen", !entry.isIntersecting)));
    document.querySelectorAll(".animated-scene").forEach(element => visibilityObserver.observe(element));
  }
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const toggle = document.querySelector("#motion-toggle");
  let paused = motion.matches;
  function updateMotion() {
    document.body.classList.toggle("motion-paused", paused || document.hidden);
    document.body.classList.toggle("motion-reduced", motion.matches);
    toggle.textContent = paused ? "애니메이션 재생하기" : "애니메이션 멈추기";
    toggle.setAttribute("aria-pressed", String(paused));
  }
  toggle.hidden = false;
  toggle.addEventListener("click", () => { paused = !paused; updateMotion(); });
  document.addEventListener("visibilitychange", updateMotion);
  motion.addEventListener("change", () => { paused = motion.matches; updateMotion(); });
  updateMotion();
  const initialStage = { "#forward": 1, "#adjoint": 2, "#update": 3 }[window.location.hash];
  if (initialStage) setStage(initialStage);
})();
