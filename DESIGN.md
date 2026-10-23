# Meep Examples design contract

## 1. Brief and reference
An approachable Korean Meep encyclopedia: see the path light takes, then open a real, reproducible example. Translate the approved `meep-homepage-concept-v1.png` and `meep-adjoint-scroll-storyboard-v3.png` references into HTML, CSS and SVG. The only requested visual correction is a spatially meaningful, pixelated signed gradient instead of a decorative blurred color field.

Primary users: a first-time FDTD learner choosing an example; an experienced reader searching for PML or adjoint; a reader using keyboard, magnification or reduced motion. Existing article URLs and their scientific content remain the source material.

## 2. Palette, type and spacing
- Paper #ffffff, soft paper #f5f8fa, ink #0d1b2a, secondary ink #526579, rule #dce5eb.
- Cyan brand #0087ad, bright cyan field #42dfff, cyan pale #e7f7fb; amber adjoint #ffb648.
- Physics canvas #071b2b, grid #173447, muted canvas ink #aec3d2, geometry #718899.
- Positive/negative gradient: preserve the original RdBu_r colors of the published image; the density map uses 0 white to 1 black.
- Font: system Korean sans stack (`Pretendard`, `Noto Sans KR`, `Apple SD Gothic Neo`, `Malgun Gothic`, sans-serif); no remote font dependency. Mono labels: ui-monospace.
- Type scale: 12, 13, 14, 16, 18, 20, 24, 28, 32, 40, 48, 56, 64px; fluid display clamps to 40–64px. Body line height 1.75, headings 1.2.
- Base space 4px; steps 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96px. Reading copy max 65ch; page max 1480px.
- Depth: rules and tonal surfaces; small 8px corners for physics panel and cards, 4px for controls. Field glow is confined to the physics canvas.

## 3. Layout
Native document scrolling; a stable header; a narrow desktop knowledge rail; airy headline beside the dark simulation diagram; compact question-first example cards. The scrollytelling scene stays in a sticky aside while three explanation chapters pass. On phones the scene sticks below the header and the brief chapters scroll below it. No wheel interception, forced snapping or nested page scroll.

Spatial reference: StyleGallery `sticky-aside` and `ram-grid` (https://github.com/changeroa/StyleGallery). Extract layout ideas only; no source copying. Header and catalog retain immediate access while the story is optional.

## 4. Motion and scientific meaning
One atmosphere: light traveling through a schematic guide. Native SVG wavefronts with CSS motion, 1.8s propagation cycle, 200ms ease-out state transition. IntersectionObserver selects chapters and pauses scenes offscreen; visibilitychange pauses hidden tabs. Reduced motion and the visible pause control retain a static, fully readable field and all three stages. No motion library, shader or new runtime dependency.

Mechanism consultation: beui.dev `tabs` (https://beui.dev/r/tabs/raw) for explicit selected state and reduced-motion treatment; react-bits `ShapeGrid` (https://reactbits.dev/r/ShapeGrid-TS-TW.json) for visibility pause. Physics sequence is a novel educational interaction, implemented independently with IntersectionObserver and SVG rather than copying those components.

Forward: cyan input at left, output above. Adjoint: amber objective-derived source at the output, original input inactive, same geometry. These are two separate computations, not two beams interfering. Stage three: saved fields → sensitivity postprocessing → optimizer → density update within the square only.

Authentic data: the middle panel of `assets/meep/09/04_gradient.png` is the original initial signed adjoint gradient, rendered without smoothing. Show the 11×11 map directly with its symmetric ±13.404 scale, no invented numeric cells. The final density values come from `assets/meep/09/result.json`, using index x*11+y, y increasing upward. A visual transition between uniform 0.5 and the saved final design is explicitly not the intermediate MMA history. Forward/adjoint wavefronts are illustrative, not numerical fields. Do not invent measured efficiencies or turn gray densities into a supposedly fabricated smooth bend.

## 5. Reusable patterns and states
- Header links and knowledge rail: normal, hover, keyboard focus. Real anchor destinations.
- Example card: question, compact schematic, part/title, description, article link. Whole card is one link.
- Filter buttons: native buttons with aria-pressed; selected uses ink wash, never an accent border. Search is a labeled input, combined with category; live result count, explicit empty state and reset.
- Story scene: three numbered stage links, three visible explanation chapters, one sticky figure. Stage state is reflected in its label and description as well as color. No live-region announcement on every scroll.
- Dictionary: native details/summary, usable without JavaScript.
- Focus: visible 3px cyan outline, 3px offset; 44px touch target minimum for controls. Links remain underlined in prose.

## 6. Verification and accepted limits
Check desktop and narrow viewport, all stages in both scroll directions, search/filter/empty/reset, keyboard links, pause, reduced motion, all article URLs, no horizontal overflow, and existing article rendering. Verify GitHub Pages build and live version after push. Local preview strips front matter; production compilation authority is the Pages build. Static SVG and canvas image have explicit dimensions. JavaScript is deferred and progressive: every current article is discoverable without it.

Mobile refinement: use two large square data maps with 12–13px HTML legends instead of shrinking SVG annotation text. Keep chapter copy immediately below the sticky scene using its measured height, and preserve spaces at responsive line breaks. Density reveal uses a 1s opacity transition between the initial background and stored final values; it does not depict intermediate MMA iterations. Reduced motion and pause show final data immediately.

No new dependencies. No fabricated simulation run. The published example is an educational five-evaluation demonstration, not a converged or fabrication-ready design. Lighthouse scores are reported only if measured through an available real-browser audit surface; never inferred from code.
