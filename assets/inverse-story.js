(() => {
  "use strict";
  const scene = document.querySelector(".inverse-figure");
  if (!scene) return;
  const $ = selector => scene.querySelector(selector);
  const links = [...scene.querySelectorAll("[data-stage-link]")];
  const chapters = [...document.querySelectorAll(".story-step")];
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const progress = $("#sequence-progress");
  const playButton = $("#sequence-play");
  const toggle = $("#motion-toggle");
  const duration = 24;
  const names = ["FORWARD DFT", "ADJOINT DFT", "FIELD OVERLAP", "GEOMETRY UPDATE"];
  const descriptions = [
    "입력 광원을 켜고 같은 설계 영역의 forward DFT 장을 누적·저장합니다.",
    "입력 광원은 끄고, 목적함수가 정한 출력의 adjoint source로 같은 설계 영역의 DFT 장을 저장합니다.",
    "저장한 두 복소장을 후처리해 설계 변수에 대한 초기 gradient를 구합니다. 표시한 실수부 이미지의 단순한 곱이 아닙니다.",
    "유한차분 검증을 통과한 gradient로 설계 영역을 한 번 갱신합니다. 실제 계산에서 출력이 증가한 61×61 밀도이며 포트는 고정됩니다."
  ];
  const clamp = value => Math.min(1, Math.max(0, value));
  const ramp = (time, start, length) => clamp((time - start) / length);
  const smooth = value => value * value * (3 - 2 * value);
  const opacity = (selector, value) => $(selector).style.opacity = String(value);
  const text = (selector, value) => { if ($(selector).textContent !== value) $(selector).textContent = value; };
  let time = 0;
  let currentStage = 0;
  let userPaused = motion.matches;
  let visible = false;
  let desiredPlaying = false;
  let stageStop = 5.99;
  let manual = false;
  let densityReady = false;
  const hasTimeline = Boolean(window.gsap);
  const staticMode = () => motion.matches || !hasTimeline;
  const playhead = { time: 0 };
  let timeline;

  // Attribute transforms are deterministic SVG coordinates, so reverse seeking
  // restores every layer without queued capture callbacks or layout animation.
  function move(selector, x, y, scale = 1, rotation = 0) {
    $(selector).setAttribute("transform", `translate(${x} ${y}) scale(${scale}) rotate(${rotation} 56 56)`);
  }
  function captured(selector, start, targetX, t) {
    const flight = smooth(ramp(t, start, 1.8));
    move(selector, 430 + (targetX - 430) * flight, 100 + 230 * flight - Math.sin(Math.PI * flight) * 40, 150 / 112 + (1 - 150 / 112) * flight, Math.sin(Math.PI * flight) * -6);
    opacity(selector, ramp(t, start, .2));
  }
  function render(value) {
    time = Math.max(0, Math.min(duration, value));
    const stage = Math.min(4, Math.floor(time / 6) + 1);
    if (stage !== currentStage) {
      currentStage = stage;
      scene.dataset.stage = String(stage);
      text("#scene-stage", `0${stage} / ${names[stage - 1]}`);
      text("#physics-description", descriptions[stage - 1]);
      links.forEach(link => {
        if (Number(link.dataset.stageLink) === stage) link.setAttribute("aria-current", "step");
        else link.removeAttribute("aria-current");
      });
    }
    const forward = stage === 1;
    const adjoint = stage === 2;
    const updating = stage === 4;
    const local = time - (stage - 1) * 6;
    const staticFrame = staticMode();
    const captureStart = forward ? 3 : 9;
    const accumulating = (forward || adjoint) && local < 3;
    const updated = densityReady ? smooth(ramp(time, 21, 2.2)) : 0;
    opacity("#forward-field", forward ? ramp(time, .3, 2) : stage === 3 ? 1 : updating ? 1 - ramp(time, 18, .6) : 0);
    opacity("#adjoint-field", adjoint ? ramp(time, 6.3, 2) : 0);
    const evaluatedField = densityReady ? ramp(time, 23.2, .7) : 0;
    opacity("#updated-field", evaluatedField);
    opacity("#density-grid", updated);
    $("#input-beacon").style.stroke = forward || evaluatedField > 0 ? "var(--field-positive)" : "var(--layout-black)";
    $("#output-beacon").style.stroke = adjoint ? "var(--field-negative)" : "var(--layout-black)";
    text("#input-caption", forward || evaluatedField > 0 ? "INPUT · ON" : "INPUT · OFF");
    text("#output-caption", adjoint ? "ADJOINT · ON" : "OUTPUT");
    const captureColor = adjoint ? "var(--field-negative)" : "var(--field-positive)";
    $("#capture-frame").style.stroke = captureColor;
    $("#capture-camera").style.stroke = captureColor;
    $("#capture-scan").style.stroke = captureColor;
    opacity("#capture-camera", forward || adjoint ? 1 : .25);
    opacity("#capture-frame", forward || adjoint ? 1 : .35);
    opacity("#capture-scan", accumulating && !staticFrame ? .7 : 0);
    $("#capture-scan").setAttribute("transform", `translate(0 ${150 * ramp(local, 0, 3)})`);
    const flash = !staticFrame && (forward || adjoint) ? .28 * Math.max(0, 1 - Math.abs(time - captureStart) / .2) : 0;
    opacity("#capture-flash", flash);
    text("#capture-caption", forward || adjoint ? accumulating ? "DFT 누적" : "저장 완료" : "CAPTURED");
    text("#geometry-caption", updating ? evaluatedField >= .99 ? "갱신 후 DFT · RES 60" : updated >= .99 ? "gradient ascent · 1회" : "gradient → 밀도 갱신" : "ρ = 0.5 · 같은 구조");
    captured("#forward-snapshot", 3, 48, time);
    captured("#adjoint-snapshot", 9, 260, time);
    const overlap = smooth(ramp(time, 12.5, 2.2));
    const overlapOpacity = ramp(time, 12.5, .4) * (1 - ramp(time, 15.2, .8));
    move("#forward-overlap", 48 + 460 * overlap, 330 - 36 * Math.sin(Math.PI * overlap), 1, -8 * Math.sin(Math.PI * overlap));
    move("#adjoint-overlap", 260 + 248 * overlap, 330 + 36 * Math.sin(Math.PI * overlap), 1, 8 * Math.sin(Math.PI * overlap));
    opacity("#forward-overlap", .75 * overlapOpacity);
    opacity("#adjoint-overlap", .65 * overlapOpacity);
    opacity("#gradient-snapshot", ramp(time, 15.2, 1));
    const transfer = smooth(ramp(time, 18.8, 2));
    move("#gradient-transfer", 508 - 78 * transfer + 28 * Math.sin(Math.PI * transfer), 330 - 230 * transfer, 1 + (150 / 112 - 1) * transfer);
    opacity("#gradient-transfer", ramp(time, 18.8, .3) * (1 - ramp(time, 21, .6)) * .85);
    opacity("#gradient-return", updating ? .75 : 0);
    opacity("#optimizer-caption", updating ? 1 : 0);
    text("#forward-status", time < .3 ? "촬영 대기" : time < 3 ? "DFT 누적 중" : time < 4.8 ? "이미지 저장 중" : "저장 완료");
    text("#adjoint-status", time < 6.3 ? "촬영 대기" : time < 9 ? "DFT 누적 중" : time < 10.8 ? "이미지 저장 중" : "저장 완료");
    text("#gradient-status", time < 12.5 ? "두 장 기다리는 중" : time < 16.2 ? "복소장 겹침·후처리" : "초기 ∂J/∂ρ · 61×61");
    const summary = forward ? accumulating ? "설계 영역의 forward DFT 장을 누적합니다." : "첫 번째 장을 찍어 저장합니다."
      : adjoint ? accumulating ? "같은 구조의 adjoint DFT 장을 누적합니다." : "두 번째 장을 찍어 저장합니다."
      : stage === 3 ? time < 16.2 ? "저장한 두 복소장을 겹쳐 민감도를 구합니다." : "픽셀마다 바꿀 방향이 gradient로 남습니다."
      : densityReady ? time < 23.2 ? "Gradient를 받아 설계 영역의 밀도를 바꿉니다." : "갱신한 구조의 forward DFT를 다시 확인합니다." : "최종 밀도를 불러오지 못했습니다. 계산 결과 링크를 확인하세요.";
    text("#scene-summary", summary);
    text("#scene-note", updating ? "균일 0.5 → 검증한 1회 갱신 · 최대 밀도 변화 0.15" : "입력·설계 영역·출력 모두 RES 60 실제 DFT");
    progress.min = staticFrame ? "1" : "0";
    progress.max = staticFrame ? "4" : String(duration);
    progress.step = staticFrame ? "1" : ".01";
    progress.value = String(staticFrame ? stage : time);
    progress.setAttribute("aria-valuetext", `${names[stage - 1]} · ${time.toFixed(1)}초`);
    text("#sequence-time", `00:${String(Math.floor(time)).padStart(2, "0")} / 00:24`);
    scene.dataset.time = time.toFixed(2);
  }
  function syncPlayback() {
    const running = desiredPlaying && !userPaused && !document.hidden && visible && !staticMode();
    if (timeline) running ? timeline.play() : timeline.pause();
    scene.dataset.playing = String(running);
    playButton.textContent = staticMode() ? "다음 단계 보기" : running ? "일시정지" : time >= 23.99 ? "다시 재생" : "전체 흐름 재생";
    playButton.setAttribute("aria-label", staticMode() ? "다음 계산 단계 보기" : running ? "애니메이션 일시정지" : "전체 역설계 흐름 재생");
    document.body.classList.toggle("motion-paused", userPaused || document.hidden);
    document.body.classList.toggle("motion-reduced", motion.matches);
    toggle.textContent = userPaused ? "동작 재생하기" : "동작 멈추기";
    toggle.setAttribute("aria-pressed", String(userPaused));
  }
  function seek(value) {
    if (timeline) timeline.time(value, true);
    playhead.time = value;
    render(value);
  }
  if (hasTimeline) {
    timeline = gsap.timeline({ paused: true }).to(playhead, {
      time: duration, duration, ease: "none", onUpdate: () => {
        if (playhead.time >= stageStop) {
          timeline.pause();
          desiredPlaying = false;
          seek(stageStop);
          syncPlayback();
        } else render(playhead.time);
      }
    });
  }
  function selectStage(stage, isManual = false) {
    if (isManual) manual = true;
    stageStop = Math.min(duration, stage * 6 - .01);
    seek(staticMode() ? stageStop : (stage - 1) * 6);
    desiredPlaying = !staticMode();
    syncPlayback();
  }
  async function loadDensity() {
    try {
      const response = await fetch("./assets/meep/09/highres/result.json");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const { x_updated: values, grid_shape: shape } = await response.json();
      const [nx, ny] = shape || [];
      if (nx !== 61 || ny !== 61 || !Array.isArray(values) || values.length !== nx * ny || values.some(v => !Number.isFinite(v) || v < 0 || v > 1)) throw new Error("Invalid density data");
      const cells = document.createDocumentFragment();
      for (let row = 0; row < ny; row += 1) {
        for (let x = 0; x < nx; x += 1) {
          // Same NumPy reshape(Nx, Ny).T, origin='lower' as the source plot.
          const density = values[x * ny + (ny - 1 - row)];
          const shade = Math.round(255 * (1 - density));
          const cell = document.createElementNS("http://www.w3.org/2000/svg", "rect");
          Object.entries({ x: 430 + x * 150 / nx, y: 100 + row * 150 / ny, width: 150 / nx, height: 150 / ny, fill: `rgb(${shade},${shade},${shade})` }).forEach(([key, value]) => cell.setAttribute(key, String(value)));
          cells.append(cell);
        }
      }
      $("#density-grid").replaceChildren(cells);
      densityReady = true;
      render(time);
    } catch (error) {
      scene.dataset.densityError = "true";
      text("#density-data-status", "밀도 데이터 로딩 실패 · 위 계산 결과 링크 참고");
      render(time);
      console.warn("Meep density data:", error.message);
    }
  }
  links.forEach(link => link.addEventListener("click", event => { event.preventDefault(); selectStage(Number(link.dataset.stageLink), true); }));
  playButton.addEventListener("click", () => {
    manual = true;
    if (staticMode()) { selectStage(currentStage % 4 + 1, true); return; }
    if (desiredPlaying && !userPaused) desiredPlaying = false;
    else {
      if (time >= 23.99) seek(0);
      stageStop = duration;
      desiredPlaying = true;
      userPaused = false;
    }
    syncPlayback();
  });
  $("#sequence-replay").addEventListener("click", () => {
    manual = true;
    stageStop = duration;
    seek(staticMode() ? 5.99 : 0);
    desiredPlaying = !staticMode();
    userPaused = motion.matches;
    syncPlayback();
  });
  progress.addEventListener("input", () => {
    manual = true;
    desiredPlaying = false;
    const value = Number(progress.value);
    seek(staticMode() ? value * 6 - .01 : value);
    syncPlayback();
  });
  $("#sequence-speed").addEventListener("change", event => { if (timeline) timeline.timeScale(Number(event.target.value)); });
  toggle.hidden = false;
  $(".sequence-transport").hidden = false;
  toggle.addEventListener("click", () => { userPaused = !userPaused; syncPlayback(); });
  document.addEventListener("visibilitychange", syncPlayback);
  motion.addEventListener("change", () => { userPaused = motion.matches; selectStage(currentStage || 1, manual); });

  // Scroll selects chapters; transport interaction takes ownership until the
  // reader scrolls again. Observer notifications cannot overwrite a scrub.
  let chapterObserver;
  function observeChapters() {
    if (!("IntersectionObserver" in window)) return;
    if (chapterObserver) chapterObserver.disconnect();
    const sticky = getComputedStyle(scene).position === "sticky";
    const narrow = matchMedia("(max-width: 680px)").matches;
    const inset = narrow && sticky ? Math.min(innerHeight - 96, Math.ceil(scene.getBoundingClientRect().height) + 80) : 150;
    const ratios = new Map();
    chapterObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => ratios.set(entry.target, entry.isIntersecting ? entry.intersectionRatio : 0));
      const active = chapters.reduce((best, chapter) => (ratios.get(chapter) || 0) > (ratios.get(best) || 0) ? chapter : best, chapters[0]);
      if (!manual && (ratios.get(active) || 0) > 0 && Number(active.dataset.step) !== currentStage) selectStage(Number(active.dataset.step));
    }, { rootMargin: `-${inset}px 0px -12% 0px`, threshold: [0, .1, .25, .5, .75, 1] });
    chapters.forEach(chapter => chapterObserver.observe(chapter));
  }
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(entries => {
      entries.forEach(entry => {
        entry.target.classList.toggle("is-offscreen", !entry.isIntersecting);
        if (entry.target === scene) { visible = entry.isIntersecting; syncPlayback(); }
      });
    }).observe(scene);
    const hero = document.querySelector(".hero-figure");
    if (hero) new IntersectionObserver(entries => entries.forEach(entry => entry.target.classList.toggle("is-offscreen", !entry.isIntersecting))).observe(hero);
  } else visible = true;
  if ("ResizeObserver" in window) new ResizeObserver(() => {
    document.documentElement.style.setProperty("--scene-height", `${Math.ceil(scene.getBoundingClientRect().height)}px`);
    observeChapters();
  }).observe(scene);
  else observeChapters();
  ["wheel", "touchstart"].forEach(type => window.addEventListener(type, () => { manual = false; }, { passive: true }));
  document.addEventListener("keydown", event => {
    if (["PageDown", "PageUp", "Home", "End", "ArrowDown", "ArrowUp", " "].includes(event.key) && !/^(INPUT|SELECT|BUTTON|TEXTAREA)$/.test(event.target.tagName)) manual = false;
  });
  const hashStage = () => ({ "#forward": 1, "#adjoint": 2, "#gradient": 3, "#update": 4 })[location.hash];
  window.addEventListener("hashchange", () => { if (hashStage()) selectStage(hashStage()); });
  selectStage(hashStage() || 1);
  loadDensity();
})();
