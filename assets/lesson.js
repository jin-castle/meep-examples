(() => {
  'use strict';
  const english = document.documentElement.lang === 'en';
  const content = document.querySelector('.lesson-content');
  if (!content) return;

  content.querySelectorAll('table').forEach((table, index) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-scroll';
    wrapper.tabIndex = 0;
    wrapper.setAttribute('role', 'region');
    wrapper.setAttribute('aria-label', english ? `Table ${index + 1}, scroll horizontally` : `표 ${index + 1}, 가로로 스크롤할 수 있습니다`);
    table.before(wrapper);
    wrapper.append(table);
  });
  content.querySelectorAll('pre').forEach((pre, index) => {
    pre.tabIndex = 0;
    pre.setAttribute('aria-label', english ? `Code or execution log ${index + 1}, scroll horizontally` : `코드 또는 실행 기록 ${index + 1}, 가로로 스크롤할 수 있습니다`);
  });

  const mobileToc = document.querySelector('.mobile-toc');
  mobileToc?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => { mobileToc.open = false; }));
  const sections = [...content.querySelectorAll('h2[id]')];
  const navLinks = [...document.querySelectorAll('.lesson-sidebar nav a, .mobile-toc nav a')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const entered = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!entered) return;
      navLinks.forEach(link => {
        if (link.hash === `#${entered.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-10% 0px -65% 0px' });
    sections.forEach(section => observer.observe(section));
  }

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const animations = [...content.querySelectorAll('img[data-animation-src][data-static-src]')].map(img => {
    const button = img.closest('figure')?.querySelector('.animation-toggle');
    if (!button) return null;
    let requestedPlaying = !reducedMotion.matches;
    const render = () => {
      const playing = requestedPlaying && !document.hidden;
      img.src = playing ? img.dataset.animationSrc : img.dataset.staticSrc;
      button.textContent = english ? (playing ? 'Pause animation' : 'Play animation') : (playing ? '애니메이션 정지' : '애니메이션 재생');
      button.setAttribute('aria-pressed', String(playing));
    };
    render();
    button.hidden = false;
    button.addEventListener('click', () => {
      requestedPlaying = !requestedPlaying;
      render();
    });
    return { render, setReducedMotion: reduce => { requestedPlaying = !reduce; render(); } };
  }).filter(Boolean);
  reducedMotion.addEventListener('change', event => animations.forEach(animation => animation.setReducedMotion(event.matches)));
  document.addEventListener('visibilitychange', () => animations.forEach(animation => animation.render()));

  const dialog = document.querySelector('.lesson-lightbox');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const image = dialog.querySelector('.lightbox-image');
  const caption = dialog.querySelector('.lightbox-caption');
  const original = dialog.querySelector('.lightbox-original');
  let opener;
  content.querySelectorAll('a[data-lightbox]').forEach(link => link.addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    const thumbnail = link.querySelector('img');
    const figure = link.closest('figure');
    const staticSrc = thumbnail?.dataset.staticSrc;
    const isAnimated = /\.gif(?:$|\?)/i.test(link.href);
    image.src = reducedMotion.matches && isAnimated && staticSrc ? staticSrc : link.href;
    image.alt = thumbnail?.alt || link.getAttribute('aria-label') || (english ? 'Enlarge simulation result' : '시뮬레이션 결과 확대');
    caption.textContent = figure?.querySelector('figcaption')?.textContent || image.alt;
    original.href = link.href;
    opener = link;
    dialog.showModal();
    event.preventDefault();
  }));
  dialog.querySelector('.lightbox-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => {
    image.removeAttribute('src');
    opener?.focus({ preventScroll: true });
  });
})();
