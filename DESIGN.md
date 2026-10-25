# Meep Examples design contract

## 1. Brief and reference
An approachable Korean Meep encyclopedia: see the path light takes, then open a real, reproducible example. Preserve the approved paper/cyan/amber identity while upgrading the inverse-design story with centered ports, forward/adjoint DFT capture, complex-field overlap, gradient and a verified geometry update.

Primary users: a first-time FDTD learner choosing an example; an experienced reader searching for PML or adjoint; a reader using keyboard, magnification or reduced motion. Existing article URLs and their scientific content remain the source material.

## 2. Palette, type and spacing
- Paper #ffffff, soft paper #f5f8fa, ink #0d1b2a, secondary ink #526579, rule #dce5eb.
- Cyan brand #0087ad, bright cyan field #42dfff, cyan pale #e7f7fb; amber adjoint #ffb648.
- Physics canvas #071b2b, grid #173447, muted canvas ink #aec3d2, geometry #718899.
- Signed fields and gradient: RdBu, negative red to zero white to positive blue; density uses0 white to1 black.
- Font: system Korean sans stack (`Pretendard`, `Noto Sans KR`, `Apple SD Gothic Neo`, `Malgun Gothic`, sans-serif); no remote font dependency. Mono labels: ui-monospace.
- Type scale: 12, 13, 14, 16, 18, 20, 24, 28, 32, 40, 48, 56, 64px; fluid display clamps to 40–64px. Body line height 1.75, headings 1.2.
- Base space 4px; steps 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96px. Reading copy max 65ch; page max 1480px.
- Depth: rules and tonal surfaces; small 8px corners for physics panel and cards, 4px for controls. Field glow is confined to the physics canvas.

## 3. Layout
Native document scrolling; a stable header; a narrow desktop knowledge rail; airy headline beside the dark simulation diagram; compact question-first example cards. The scrollytelling scene stays in a sticky aside while four explanation chapters pass. On phones the scene sticks below the header and the brief chapters scroll below it. No wheel interception, forced snapping or nested page scroll.

Spatial reference: StyleGallery `sticky-aside` and `ram-grid` (https://github.com/changeroa/StyleGallery). Extract layout ideas only; no source copying. Header and catalog retain immediate access while the story is optional.

## 4. Motion and scientific meaning
The current four-stage implementation and scientific source are specified in the dated contract below. The entire input/design/output field, captured RdBu images, gradient and stored density endpoint are actual high-resolution numerical data. Forward and adjoint are separate computations with the same initial geometry, frequency and design region.

The visible scene automatically plays all four stages in a continuous24-second loop. Scrolling does not select or interrupt chapters. IntersectionObserver pauses scenes offscreen; visibilitychange pauses hidden tabs. Native transport supports reversible seeking, replay and speed. Reduced motion retains static stage endpoints and full keyboard navigation. The original input is inactive during the objective-derived adjoint run. The optimizer changes only the design square; connected ports stay fixed.

## 5. Reusable patterns and states
- Header links and knowledge rail: normal, hover, keyboard focus. Real anchor destinations.
- Example card: question, compact schematic, part/title, description, article link. Whole card is one link.
- Filter buttons: native buttons with aria-pressed; selected uses ink wash, never an accent border. Search is a labeled input, combined with category; live result count, explicit empty state and reset.
- Story scene: four numbered stage links, four visible explanation chapters, one sticky figure. Stage state is reflected in its label and description as well as color. No live-region announcement on every scroll.
- Dictionary: native details/summary, usable without JavaScript.
- Focus: visible 3px cyan outline, 3px offset; 44px touch target minimum for controls. Links remain underlined in prose.

## 6. Verification and accepted limits
Check desktop and narrow viewport, all stages in both scroll directions, search/filter/empty/reset, keyboard links, pause, reduced motion, all article URLs, no horizontal overflow, and existing article rendering. Verify GitHub Pages build and live version after push. Local preview strips front matter; production compilation authority is the Pages build. Static SVG and canvas image have explicit dimensions. JavaScript is deferred and progressive: every current article is discoverable without it.

Mobile refinement: retain three saved-image tiles with readable HTML labels. Wrap transport controls on narrow screens; disable stickiness on short viewports. Density reveal crossfades the initial and evaluated endpoint without inventing intermediate iterations.

No fabricated simulation run. The published example is an educational five-evaluation demonstration, not a converged or fabrication-ready design. Lighthouse scores are reported only if measured through an available real-browser audit surface; never inferred from code.

### 2026-10-23: DFT capture and verified high-resolution update
Vendor GSAP 3.15.0 core locally with its upstream copyright and license notice. This is the user-requested exception to the earlier no-motion-library constraint. No framework, build step, plugin or CDN request is added. A seekable 24-second GSAP playhead drives deterministic SVG transforms and opacity. Four chapters cover forward DFT capture (0–6s), adjoint capture in the same geometry (6–12s), complex-field overlap and sensitivity postprocessing (12–18s), then one evaluated density update (18–24s).

The apparatus uses a light grid surface and black unfilled waveguide outlines. Its input meets the center of the square's left edge; its output meets the center of the top edge. Guide width is half the design square's width. Input, design region and output share one physical coordinate mapping and one full-field RdBu scale per computation. Saved crops use that same scale. The hero also shows the actual updated-forward DFT, with no synthetic wavefront or glow. Existing dark surfaces frame the saved images and transport; blue and red distinguish capture cues. A camera frame, one soft flash per capture (white opacity at most0.28), and a traveling image preserve each snapshot's identity. Captured copies converge on the gradient tile; a gradient copy returns to the region. DFT is accumulated frequency-domain data; the camera is a storage metaphor. After the density update, the evaluated forward field returns across both ports and the region.

Scientific source: new Meep1.33.0 execution at60pixels/µm,61×61 density variables, wavelength1.55µm,1×1µm design square,6×5µm cell and1µm PML. Display Ez monitors were recorded during the same forward/adjoint runs used by the native Meep gradient. Full-cell fields are360×300; the design monitor includes62×62 samples with boundary padding. Physical coordinates crop the exact design square;720px PNG export uses nearest native samples. No low-resolution figure crop or invented field is used. All field and signed-gradient images use RdBu: negative red, zero white, positive blue, with independent symmetric limits recorded in JSON. Density uses white0 to black1.

Two directional finite differences validate the initial adjoint derivative: maximum relative error1.8392736457e-5 (0.001839%). One accepted projected gradient-ascent step has maximum density change0.15. The output mode-power objective changes from2.9157725347 to38.4147296510 in unnormalized source/optimizer units; this is not transmission efficiency or a converged binary geometry. The visible density crossfade compares uniform0.5 with this evaluated endpoint; it does not depict intermediate optimizer history. Flat arrays index x*Ny+y with y increasing upward. The exact gradient uses complex fields, source normalization and the discretized MaterialGrid derivative; two displayed Re(Ez) images alone do not reproduce it.

Assets and metadata: assets/meep/09/highres/. Reproduction code: code/highres_bend/. Original published09 data and code/bend_inverse.py remain byte-identical. Raw complex arrays and execution evidence are packaged separately from the static-site payload.

Native transport includes play/pause, replay, speed, labeled seeking and four stage links. Scrubbing is reversible and triggers no queued capture callbacks. Reduced motion and missing GSAP use four static endpoints; their range control has four integer positions so backward keyboard input works. Hidden/offscreen scenes preserve time and resume automatic playback when visible unless the user paused it. Stage links start playback at the chosen stage and continue through the remaining stages into the next loop. Pause intent survives scrolling. Narrow controls wrap; short viewports use a nonsticky figure.

### DFT propagation during capture
Forward and adjoint display32 native phase samples of Re(Ez exp(-iφ)), with one fixed symmetric ±max|Ez| range per computation. This is steady-state DFT phase playback. The existing apparatus and saved-map layout stay intact. Each six-second field stage plays four1.5-second phase cycles. At its midpoint (global3/9s), phase0 is photographed: the copy holds for0.28s, then flies to its saved tile while the original phase motion continues through both waveguides and the design region. The saved copy stays at phase0 for gradient presentation. Frames use a deterministic8×4 sprite, driven by the same GSAP playhead as the shutter, so pause, speed, reverse seeking and offscreen suspension also control the field. Reduced motion, unavailable GSAP or failed sprite decoding retain the phase0 field and manual stages. The phase label states normal steady state; no wavefront arrival or turn-on delay is inferred from DFT data.

## 7. Guided lessons: parts 01 and 09
Preserve this site's paper, ink and cyan identity. A lesson answers one question through observation, prediction, explanation, execution, interpretation and a final check. Keep the original English summary, detailed numerical evidence, complete code and scientific limits accessible through native disclosures. Never move a necessary validity caveat exclusively into a collapsed panel. Existing routes and simulation scripts are immutable for this presentation change.

The reusable `lesson` layout owns a short Korean title, three learning goals, previous/next article links, desktop chapter navigation and a mobile collapsible table of contents. Content section IDs are `observe`, `predict`, `understand`, `run`, `interpret`, `check`, and `reference`. Front matter: `layout: lesson`, `lesson_title`, `lesson_summary`, `lesson_goals` (three strings), `lesson_prerequisites`. Each post retains its original `part`, metadata and an explicit original permalink.

Lesson tokens reuse palette above. Add semantic token names for the type scale (small 14px, label 12px, body 18px, lead 20px, h3 23px, h2 28px, title 40px / narrow 30px), body line height 1.8, prose measure 760px, sidebar 224px, shell 1160px, header 64px, mobile TOC 48px. Name spacing steps 4, 8, 12, 16, 20, 24, 32, 40, 48, 64px in CSS. Neutral rules separate sections; cyan is reserved for actions, selected navigation and small pedagogical cues. No new decorative animation or font dependency.

Primitives: `lesson-note` for one insight or explicit limit; `lesson-figure` with a literal observational caption and original-image link (`data-lightbox`); `figure-pair` stacks at narrow widths; `prediction` with native labeled radio choices plus a native details explanation; native details for derivations, code walkthrough and reference evidence. Concept diagrams stay visible in the explanation section with prose describing their meaning. Tables and code scroll within their own labeled regions, never the page. Long strings wrap outside code. Figures preserve numerical pixels; enlargement uses a keyboard-accessible native dialog with close, Escape, original-image fallback and focus restoration. GIFs stay outside disclosures and play automatically, including without JavaScript. Controls allow stopping and resuming; reduced motion uses static images, and hiding a tab pauses playback without losing the reader's chosen play/stop state. No learner answer is persisted or transmitted.

QA: both posts at 1440px and 390/320px, no document horizontal overflow, 18px readable prose, complete TOC destinations, keyboard operation, prediction/answer disclosure, image enlargement/close, long tables/code, reduced motion, JS-disabled reading fallback. Regression checks compare embedded full Python programs and image/reference inventories with commit d343a0c; scientific scripts and data remain byte-identical. Actual Pages compilation and live browser checks establish production success. Accepted debt: the remaining articles retain the original post layout until separately requested. Lighthouse cannot be claimed without an available measured audit surface.

## 8. Intro videos at the top of every example (2026-10-26)
User-requested exception to "no new decorative animation": each example opens with an 8-second muted MP4 loop (1280×720, H.264, about 0.6–1.4 MB, JPG poster) that shows the device in 3D with the post's own Meep field. `_includes/intro-video.html` (self-contained CSS/JS) is included first in `lesson-intro` by `_layouts/lesson.html`; post 14 (minima `post` layout) gets the include from `build_site.py`. Captions and aria labels live in `_data/intros.yml`; the include renders nothing for a part without an entry.

Scientific content: fields are re-recorded with the parameters of the simulation behind each post's GIF (150 frames, true Meep times) and drawn as a ray-marched volume, Re(field) in matplotlib RdBu (red negative, blue positive, zero transparent). All simulations are 2D (or 1D radial for post 13, revolved with exp(imφ)), so the out-of-plane height is display only and the field is the same at every height; each caption says so in one line. Post 10's mirror is an image dipole in the computation; only the physical half is shown. Approved look: pale cyan backdrop, cyan SiO2/glass, gold high-index cores, ink/metal grey for PEC.

Behaviour: autoplay, loop, playsinline; a visible stop/play button; paused when the tab is hidden or the video is off screen; `prefers-reduced-motion` starts paused on the poster. Source project: `C:\Users\bgs43\Desktop\meep_intro` (field exporters, Three.js scenes, render script).
