(() => {
  "use strict";
  const english = document.documentElement.lang === "en";
  const tr = (ko, en) => english ? en : ko;
  const scene = document.querySelector(".inverse-figure");
  if (!scene) return;
  const $ = selector => scene.querySelector(selector);
  const links = [...scene.querySelectorAll("[data-stage-link]")];
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const progress = $("#sequence-progress");
  const playButton = $("#sequence-play");
  const toggle = $("#motion-toggle");
  const duration = 24;
  const captureAt = 3;
  const phaseCycleSeconds = 1.5;
  const phaseFrames = 32;
  const sheetColumns = 8;
  const phaseReady = { forward: false, adjoint: false };
  const names = ["FORWARD DFT", "ADJOINT DFT", "FIELD OVERLAP", "GEOMETRY UPDATE"];
  const descriptions = [
    tr("Forward DFT의 정상상태 위상 전파 중간에 설계 영역을 촬영합니다. 저장된 이미지는 멈추고, 원래 장의 위상 전파는 계속됩니다.", "Capture the design region during steady-state phase playback of the forward DFT. The saved image stays still while the original field continues its phase evolution."),
    tr("입력 광원은 끄고 출력의 adjoint source로 계산한 DFT를 위상 재생합니다. 같은 설계 영역을 촬영한 뒤에도 전파는 이어집니다.", "Turn off the input source and replay the phase of the DFT computed using an adjoint source at the output. Phase evolution continues after capturing the same design region."),
    tr("저장한 두 복소장을 후처리해 설계 변수에 대한 현재 gradient를 구합니다. 표시한 실수부 이미지의 단순한 곱이 아닙니다.", "Postprocess the two saved complex fields to obtain the current gradient with respect to the design variables. This is not simply the product of the displayed real-part images."),
    tr("유한차분 검증을 통과한 gradient로 설계 영역을 갱신하고 다음 계산에 사용합니다. 실제 계산에서 출력이 증가한 61×61 밀도이며 포트는 고정됩니다.", "Update the design region using a gradient checked against finite differences, then use it in the next calculation. This 61×61 density increased the output in the actual calculation; the ports stay fixed.")
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
  let densityReady = false;
  const hasTimeline = Boolean(window.gsap);
  const staticMode = () => motion.matches || !hasTimeline;
  const playhead = { time: 0 };
  let timeline;
  let records = [], iteration = 0, loading = false, finished = false, requestId = 0;
  let currentRecord, fallbackRecord, densityBlend = -1, pendingPosition = 0;
  const bundles = new Map();
  const assetRoot = new URL(`${(document.documentElement.dataset.baseurl || "").replace(/\/$/, "")}/assets/`, document.baseURI);
  const historyRoot = new URL("meep/09/iterations/", assetRoot);
  const assetVersion = new URL(document.currentScript.src).searchParams.get("v");
  function dataURL(path, root = assetRoot) {
    const url = new URL(path, root);
    if (assetVersion) url.searchParams.set("v", assetVersion);
    return url;
  }
  Object.assign(scene.dataset, { iteration: "0", iterationCount: "1", historyReady: "false", loading: "false", finished: "false" });
  const densityCanvas = $("#current-density");
  const densityContext = densityCanvas.getContext("2d");
  function drawDensity(before, after, blend) {
    if (blend === densityBlend) return;
    densityBlend = blend;
    const pixels = densityContext.createImageData(61, 61);
    for (let row = 0; row < 61; row++) for (let x = 0; x < 61; x++) {
      const source = x * 61 + 60 - row;
      const shade = Math.round(255 * (1 - (before[source] + (after[source] - before[source]) * blend)));
      pixels.data.set([shade, shade, shade, 255], (row * 61 + x) * 4);
    }
    densityContext.putImageData(pixels, 0, 0);
    densityCanvas.dataset.blend = blend.toFixed(4);
    densityCanvas.dataset.iteration = String(iteration);
  }
  const imageTargets = {
    forward_scene: "#forward-field .field-base", adjoint_scene: "#adjoint-field .field-base",
    forward_phases: "#forward-phase-sheet", adjoint_phases: "#adjoint-phase-sheet",
    forward_capture: "#dft-forward-map image", adjoint_capture: "#dft-adjoint-map image",
    gradient_design: "#initial-gradient-map image", updated_forward_scene: "#updated-field"
  };
  async function bundle(index) {
    if (!bundles.has(index)) bundles.set(index, Promise.all(Object.keys(imageTargets).map(async key => {
      const image = new Image();
      image.src = dataURL(records[index][key], historyRoot).href;
      await image.decode();
      if (key.endsWith("_phases") && (image.naturalWidth !== 2880 || image.naturalHeight !== 1200)) throw new Error("Invalid phase sheet");
      return [key, image];
    })).catch(error => { bundles.delete(index); throw error; }));
    return bundles.get(index);
  }
  async function selectIteration(index, position = 0) {
    const request = ++requestId;
    loading = true;
    pendingPosition = position;
    scene.dataset.loading = "true";
    text("#iteration-status", tr("다음 계산 데이터 준비 중 · 현재 장면 유지", "Preparing the next calculation · Keeping the current scene"));
    syncPlayback();
    try {
      const images = await bundle(index);
      if (request !== requestId) return;
      // Commit all decoded images together so a frame cannot mix iterations.
      for (const [key, image] of images) document.querySelector(imageTargets[key]).setAttribute("href", image.src);
      iteration = index;
      currentRecord = records[index];
      densityBlend = -1;
      drawDensity(currentRecord.x_before, currentRecord.x_after, 0);
      $("#density-before").setAttribute("href", densityCanvas.toDataURL());
      drawDensity(currentRecord.x_before, currentRecord.x_after, 1);
      const updatedImage = document.createElementNS("http://www.w3.org/2000/svg", "image");
      for (const [key, value] of Object.entries({ x: 430, y: 100, width: 150, height: 150, href: densityCanvas.toDataURL(), style: "image-rendering:pixelated" })) updatedImage.setAttribute(key, value);
      $("#density-grid").replaceChildren(updatedImage);
      phaseReady.forward = phaseReady.adjoint = densityReady = true;
      finished = false;
      loading = false;
      Object.assign(scene.dataset, { iteration: String(index), historyReady: "true", loading: "false", finished: "false", forwardPhaseReady: "true", adjointPhaseReady: "true" });
      $("#iteration-select").value = String(index);
      text("#density-data-status", "");
      scene.querySelectorAll(".data-credit a").forEach((link, i) => { link.href = dataURL(i < 3 ? currentRecord[["forward_scene", "adjoint_scene", "gradient_design"][i]] : "manifest.json", historyRoot).href; });
      seek(pendingPosition);
      syncPlayback();
      if (index + 1 < records.length) bundle(index + 1).catch(() => {});
    } catch (error) {
      if (request !== requestId) return;
      loading = false;
      scene.dataset.loading = "false";
      desiredPlaying = false;
      $("#iteration-select").value = String(iteration);
      text("#density-data-status", tr("다음 계산 데이터 로딩 실패 · 현재 기록 유지 · 선택기로 다시 시도", "Next calculation failed to load · Keeping the current record · Retry using the selector"));
      syncPlayback();
      console.warn("Meep iteration:", error.message);
    }
  }
  function completeCycle() {
    if (currentRecord && iteration + 1 < records.length) { selectIteration(iteration + 1); return; }
    finished = true;
    scene.dataset.finished = "true";
    render(duration);
    syncPlayback();
  }
  async function loadHistory() {
    try {
      const response = await fetch(dataURL("manifest.json", historyRoot));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const manifest = await response.json();
      const validDensity = values => Array.isArray(values) && values.length === 3721 && values.every(v => Number.isFinite(v) && v >= 0 && v <= 1);
      if (!Array.isArray(manifest.records) || !manifest.records.length) throw new Error("Empty iteration history");
      if (manifest.phase_frame_count !== 32 || manifest.phase_columns !== 8 || manifest.phase_rows !== 4 || manifest.scene_pixels?.join() !== "360,300") throw new Error("Unsupported phase dimensions");
      manifest.records.forEach((record, i, all) => {
        if (!validDensity(record.x_before) || !validDensity(record.x_after) || record.grid_shape?.join() !== "61,61" || record.gradient_shape?.join() !== "61,61" || !Array.isArray(record.gradient) || record.gradient.length !== 3721 || record.gradient.some(value => !Number.isFinite(value)) || !Number.isFinite(record.objective_before) || !Number.isFinite(record.objective_after) || record.objective_after <= record.objective_before || Object.keys(imageTargets).some(key => typeof record[key] !== "string")) throw new Error("Invalid iteration record");
        if (i && record.x_before.some((value, cell) => value !== all[i - 1].x_after[cell])) throw new Error("Broken density chain");
      });
      records = manifest.records;
      const select = $("#iteration-select");
      select.replaceChildren(...records.map((record, i) => new Option(`${i + 1} / ${records.length}`, String(i))));
      select.disabled = false;
      scene.dataset.iterationCount = String(records.length);
      await selectIteration(0, time);

    } catch (error) {
      $("#iteration-select").replaceChildren(new Option(tr("기존 1회", "Original single step"), "0"));
      text("#iteration-status", tr("반복 기록 없음 · 기존 1회 계산 표시", "No iteration history · Showing the original single step"));
      text("#iteration-objective", tr("Unnormalized J · 반복 기록 로딩 실패", "Unnormalized J · Iteration history failed to load"));
      console.warn("Meep history:", error.message);
    }
  }

  // Attribute transforms are deterministic SVG coordinates, so reverse seeking
  // restores every layer without queued capture callbacks or layout animation.
  function move(selector, x, y, scale = 1, rotation = 0) {
    $(selector).setAttribute("transform", `translate(${x} ${y}) scale(${scale}) rotate(${rotation} 56 56)`);
  }
  function captured(selector, start, targetX, t) {
    const flight = smooth(ramp(t, start + .28, 1.8));
    move(selector, 430 + (targetX - 430) * flight, 100 + 230 * flight - Math.sin(Math.PI * flight) * 40, 150 / 112 + (1 - 150 / 112) * flight, Math.sin(Math.PI * flight) * -6);
    opacity(selector, ramp(t, start, .08));
  }
  function phaseField(kind, local, active) {
    const playingPhase = active && phaseReady[kind] && !staticMode();
    const cycle = (((local - captureAt) / phaseCycleSeconds) % 1 + 1) % 1;
    const frame = playingPhase ? Math.floor(cycle * phaseFrames + 1e-7) % phaseFrames : 0;
    const sheet = $(`#${kind}-phase-sheet`);
    sheet.setAttribute("x", String(-(frame % sheetColumns) * 360));
    sheet.setAttribute("y", String(-Math.floor(frame / sheetColumns) * 300));
    $(`#${kind}-phase`).dataset.frame = String(frame);
    opacity(`#${kind}-phase`, playingPhase ? 1 : 0);
    return frame;
  }
  async function loadPhaseSheet(kind) {
    try {
      const image = new Image();
      image.src = $(`#${kind}-phase-sheet`).getAttribute("href");
      await image.decode();
      if (image.naturalWidth !== 2880 || image.naturalHeight !== 1200) throw new Error("Invalid DFT phase sheet");
      phaseReady[kind] = true;
      scene.dataset[`${kind}PhaseReady`] = "true";
      render(time);
    } catch (error) {
      scene.dataset[`${kind}PhaseError`] = "true";
      console.warn("Meep phase animation:", error.message);
    }
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
    const captureStart = forward ? captureAt : 6 + captureAt;
    const beforeCapture = (forward || adjoint) && local < captureAt;
    const forwardFrame = phaseField("forward", local, forward);
    const adjointFrame = phaseField("adjoint", local, adjoint);
    const phaseKind = adjoint ? "adjoint" : "forward";
    const phaseAnimated = (forward || adjoint) && phaseReady[phaseKind] && !staticFrame;
    text("#phase-label", phaseAnimated ? `${tr("DFT 위상", "DFT phase")} ${Math.round((adjoint ? adjointFrame : forwardFrame) * 360 / phaseFrames)}° · ${tr("정상상태", "Steady state")}` : tr("DFT 저장 위상 · 정상상태", "Saved DFT phase · Steady state"));
    const updated = densityReady ? smooth(ramp(time, 21, 2.2)) : 0;
    opacity("#forward-field", forward ? ramp(time, .3, 2) : stage === 3 ? 1 : updating ? 1 - ramp(time, 18, .6) : 0);
    opacity("#adjoint-field", adjoint ? ramp(time, 6.3, 2) : 0);
    const evaluatedField = densityReady ? ramp(time, 23.2, .7) : 0;
    opacity("#updated-field", evaluatedField);
    opacity("#density-grid", updated);
    const densityRecord = currentRecord || fallbackRecord;
    if (densityRecord) {
      drawDensity(densityRecord.x_before, densityRecord.x_after, updated);
      text("#iteration-objective", `Unnormalized J: ${densityRecord.objective_before.toPrecision(5)} → ${densityRecord.objective_after.toPrecision(5)}`);
      text("#iteration-status", finished ? tr("저장된 반복 완료 · 마지막 갱신 구조 유지", "Saved iterations complete · Keeping the final updated geometry") : !currentRecord ? tr("반복 기록 없음 · 기존 1회 계산 표시", "No iteration history · Showing the original single step") : `${tr("반복", "Iteration")} ${iteration + 1}/${records.length} · ${tr("현재 밀도", "Current density")} ρ · ${updated > 0 ? tr("갱신 중", "Updating") : tr("갱신 전", "Before update")}`);
    }
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
    opacity("#capture-scan", beforeCapture && !staticFrame ? .7 : 0);
    $("#capture-scan").setAttribute("transform", `translate(0 ${150 * ramp(local, 0, captureAt)})`);
    const flash = !staticFrame && (forward || adjoint) ? .28 * Math.max(0, 1 - Math.abs(time - captureStart) / .2) : 0;
    opacity("#capture-flash", flash);
    text("#capture-caption", forward || adjoint ? beforeCapture ? tr("촬영 대기", "Waiting to capture") : local < 3.28 ? tr("찰칵 · DFT", "Captured · DFT") : tr("저장 완료", "Saved") : "CAPTURED");
    text("#geometry-caption", updating ? evaluatedField >= .99 ? tr("갱신 후 DFT · RES 60", "Updated DFT · RES 60") : updated >= .99 ? `gradient ascent · ${tr(`${iteration + 1}회`, `step ${iteration + 1}`)}` : tr("gradient → 밀도 갱신", "gradient → density update") : `ρ${iteration} · ${tr("현재 구조", "Current geometry")}`);
    captured("#forward-snapshot", captureAt, 48, time);
    captured("#adjoint-snapshot", 6 + captureAt, 260, time);
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
    text("#forward-status", time < .3 ? tr("촬영 대기", "Waiting to capture") : time < 3 ? tr("위상 전파 중", "Phase evolving") : time < 5.08 ? tr("DFT 저장 중", "Saving DFT") : tr("저장 완료", "Saved"));
    text("#adjoint-status", time < 6.3 ? tr("촬영 대기", "Waiting to capture") : time < 9 ? tr("위상 전파 중", "Phase evolving") : time < 11.08 ? tr("DFT 저장 중", "Saving DFT") : tr("저장 완료", "Saved"));
    text("#gradient-status", time < 12.5 ? tr("두 장 기다리는 중", "Waiting for both fields") : time < 16.2 ? tr("복소장 겹침·후처리", "Complex-field overlap and postprocessing") : tr("현재 ∂J/∂ρ · 61×61", "Current ∂J/∂ρ · 61×61"));
    const summary = forward ? beforeCapture ? tr("Forward 장이 전파되는 중간에 촬영합니다.", "Capture the forward field during phase evolution.") : tr("DFT 한 장을 저장해도 전파는 계속됩니다.", "Phase evolution continues after saving a DFT snapshot.")
      : adjoint ? beforeCapture ? tr("Adjoint 장이 전파되는 중간에 다시 촬영합니다.", "Capture the adjoint field during its phase evolution.") : tr("두 번째 DFT를 저장하며 전파를 이어갑니다.", "Save the second DFT snapshot while phase evolution continues.")
      : stage === 3 ? time < 16.2 ? tr("저장한 두 복소장을 겹쳐 민감도를 구합니다.", "Overlap the two saved complex fields to compute sensitivity.") : tr("픽셀마다 바꿀 방향이 gradient로 남습니다.", "The gradient gives an update direction for every pixel.")
      : densityReady ? time < 23.2 ? tr("Gradient를 받아 설계 영역의 밀도를 바꿉니다.", "Use the gradient to update the density in the design region.") : tr("갱신한 구조의 forward DFT를 다시 확인합니다.", "Check the forward DFT of the updated geometry.") : tr("최종 밀도를 불러오지 못했습니다. 계산 결과 링크를 확인하세요.", "The final density could not be loaded. Check the calculation result links.");
    text("#scene-summary", finished ? tr("저장된 계산이 끝났습니다. 마지막 갱신 구조와 forward DFT를 유지합니다.", "The saved calculations are complete. Keeping the final updated geometry and forward DFT.") : summary);
    text("#scene-note", updating ? tr("현재 밀도 → 실제 갱신 밀도 · 다음 계산의 시작 구조", "Current density → computed updated density · Starting geometry for the next calculation") : adjoint ? tr("Adjoint는 반복별 최대 진폭으로 정규화 · 촬영본은 위상 0°에 고정", "Adjoint normalized to each iteration's peak · Snapshots fixed at phase 0°") : tr("복소 DFT의 정상상태 위상 재생 · 촬영본은 위상 0°에 고정", "Steady-state phase playback of complex DFT · Snapshots fixed at phase 0°"));
    progress.min = staticFrame ? "1" : "0";
    progress.max = staticFrame ? "4" : String(duration);
    progress.step = staticFrame ? "1" : ".01";
    progress.value = String(staticFrame ? stage : time);
    progress.setAttribute("aria-valuetext", `${names[stage - 1]} · ${time.toFixed(1)}${tr("초", " seconds")}`);
    text("#sequence-time", `00:${String(Math.floor(time)).padStart(2, "0")} / 00:24`);
    scene.dataset.time = time.toFixed(2);
  }
  function syncPlayback() {
    const running = desiredPlaying && !userPaused && !document.hidden && visible && !staticMode() && !loading && !finished;
    if (timeline) running ? timeline.play() : timeline.pause();
    scene.dataset.playing = String(running);
    playButton.textContent = staticMode() ? tr("다음 단계 보기", "Next stage") : running ? tr("일시정지", "Pause") : time >= 23.99 ? tr("다시 재생", "Replay") : tr("전체 흐름 재생", "Play full sequence");
    playButton.setAttribute("aria-label", staticMode() ? tr("다음 계산 단계 보기", "Show the next calculation stage") : running ? tr("애니메이션 일시정지", "Pause animation") : tr("전체 역설계 흐름 재생", "Play the full inverse-design sequence"));
    document.body.classList.toggle("motion-paused", userPaused || document.hidden);
    document.body.classList.toggle("motion-reduced", motion.matches);
    toggle.textContent = userPaused ? tr("동작 재생하기", "Resume motion") : tr("동작 멈추기", "Pause motion");
    toggle.setAttribute("aria-pressed", String(userPaused));
  }
  function seek(value) {
    if (loading) pendingPosition = value;
    if (timeline) timeline.time(value, true);
    playhead.time = value;
    render(value);
  }
  if (hasTimeline) {
    timeline = gsap.timeline({ paused: true, onComplete: completeCycle }).to(playhead, {
      time: duration, duration, ease: "none", onUpdate: () => render(playhead.time)
    });
  }
  function selectStage(stage) {
    if (finished) { finished = false; desiredPlaying = false; scene.dataset.finished = "false"; }
    seek(staticMode() ? stage * 6 - .01 : (stage - 1) * 6);
    syncPlayback();
  }
  async function loadDensity() {
    try {
      const response = await fetch(dataURL("meep/09/highres/result.json"));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();
      const { x_updated: values, grid_shape: shape } = result;
      const [nx, ny] = shape || [];
      if (nx !== 61 || ny !== 61 || !Array.isArray(values) || values.length !== nx * ny || values.some(v => !Number.isFinite(v) || v < 0 || v > 1)) throw new Error("Invalid density data");
      fallbackRecord = { x_before: result.x_initial, x_after: values, objective_before: result.objective_initial, objective_after: result.objective_updated };
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
      text("#density-data-status", tr("밀도 데이터 로딩 실패 · 위 계산 결과 링크 참고", "Density data failed to load · See the calculation result links above"));
      render(time);
      console.warn("Meep density data:", error.message);
    }
  }
  links.forEach(link => link.addEventListener("click", event => {
    event.preventDefault();
    const stage = Number(link.dataset.stageLink);
    history.replaceState(null, "", link.hash);
    alignChapter(stage);
  }));
  $("#iteration-select").addEventListener("change", event => selectIteration(Number(event.target.value), staticMode() ? 5.99 : 0));
  playButton.addEventListener("click", () => {
    if (staticMode()) { if (currentStage === 4 && records.length && iteration + 1 < records.length) selectIteration(iteration + 1, 5.99); else if (currentStage === 4) completeCycle(); else selectStage(currentStage + 1); return; }
    if (desiredPlaying && !userPaused && !finished) { desiredPlaying = false; userPaused = true; }
    else {
      if (finished || time >= 23.99) { if (records.length) selectIteration(finished ? 0 : Math.min(iteration + 1, records.length - 1)); else { finished = false; scene.dataset.finished = "false"; seek(0); } }
      desiredPlaying = true;
      userPaused = false;
    }
    syncPlayback();
  });
  $("#sequence-replay").addEventListener("click", () => {
    finished = false;
    scene.dataset.finished = "false";
    if (records.length) selectIteration(0, staticMode() ? 5.99 : 0);
    else seek(staticMode() ? 5.99 : 0);
    desiredPlaying = !staticMode();
    userPaused = motion.matches;
    syncPlayback();
  });
  progress.addEventListener("input", () => {
    desiredPlaying = false;
    userPaused = true;
    finished = false;
    scene.dataset.finished = "false";
    const value = Number(progress.value);
    seek(staticMode() ? value * 6 - .01 : value);
    syncPlayback();
  });
  $("#sequence-speed").addEventListener("change", event => { if (timeline) timeline.timeScale(Number(event.target.value)); });
  toggle.hidden = false;
  $(".sequence-transport").hidden = false;
  toggle.addEventListener("click", () => { userPaused = !userPaused; if (!userPaused) desiredPlaying = true; syncPlayback(); });
  document.addEventListener("visibilitychange", syncPlayback);
  motion.addEventListener("change", () => { userPaused = motion.matches; selectStage(currentStage || 1); });
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
  }).observe(scene);
  const chapters = [...document.querySelectorAll(".story-step[data-step]")];
  let scrollChapter = 0, lastScrollY = window.scrollY, scrollPending = false;
  function activationLine() {
    const header = document.querySelector(".site-header").getBoundingClientRect().bottom;
    return matchMedia("(max-width: 680px)").matches ? header + 8 + scene.getBoundingClientRect().height + 32 : header + 100;
  }
  function alignChapter(stage) {
    scrollChapter = stage;
    scene.dataset.scrollChapter = String(stage);
    const chapter = chapters.find(article => Number(article.dataset.step) === stage);
    window.scrollTo({ top: window.scrollY + chapter.getBoundingClientRect().top - activationLine() + 1, behavior: "instant" });
    selectStage(stage);
  }
  function followScroll() {
    scrollPending = false;
    if (window.scrollY === lastScrollY) return;
    lastScrollY = window.scrollY;
    const line = activationLine();
    const chapter = chapters.find(article => { const box = article.getBoundingClientRect(); return box.top <= line && box.bottom > line; });
    if (!chapter) return;
    const stage = Number(chapter.dataset.step);
    if (stage === scrollChapter) return;
    // Small focus/anchor shifts near a boundary must not override playback.
    const box = chapter.getBoundingClientRect();
    if (scrollChapter && (box.top > line - 12 || box.bottom < line + 12)) return;
    scrollChapter = stage;
    scene.dataset.scrollChapter = String(stage);
    selectStage(stage);
  }
  window.addEventListener("scroll", () => { if (!scrollPending) { scrollPending = true; requestAnimationFrame(followScroll); } }, { passive: true });
  const hashStage = () => ({ "#forward": 1, "#adjoint": 2, "#gradient": 3, "#update": 4 })[location.hash];
  window.addEventListener("hashchange", () => { if (hashStage()) alignChapter(hashStage()); });
  window.addEventListener("load", () => { if (hashStage()) alignChapter(hashStage()); });
  desiredPlaying = !staticMode();
  selectStage(hashStage() || 1);
  Promise.all([loadDensity(), loadPhaseSheet("forward"), loadPhaseSheet("adjoint")]).then(loadHistory);
})();
