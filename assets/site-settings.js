(() => {
  'use strict';
  const root = document.documentElement;
  const select = document.querySelector('#theme-select');
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let choice = window.meepThemeChoice || 'system';
  function render() {
    const theme = choice === 'system' ? (system.matches ? 'dark' : 'light') : choice;
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
    if (select) select.value = choice;
    document.querySelectorAll('[data-variant-base]').forEach(img => {
      const locale = img.dataset.variantLocale || root.lang || 'ko';
      const source = `${img.dataset.variantBase}.${locale}.${theme}.png`;
      if (img.getAttribute('src') !== source) img.src = source;
      const link = img.closest('a[data-lightbox]');
      if (link) link.href = source;
    });
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', theme === 'dark' ? '#0d1722' : '#ffffff');
  }
  select?.addEventListener('change', () => {
    choice = select.value;
    try { localStorage.setItem('meep-theme', choice); } catch (_) {}
    render();
  });
  system.addEventListener('change', () => { if (choice === 'system') render(); });
  window.addEventListener('storage', event => {
    if (event.key !== 'meep-theme' && event.key !== null) return;
    choice = ['light', 'dark'].includes(event.newValue) ? event.newValue : 'system';
    render();
  });
  function syncLocaleAnchors() {
    document.querySelectorAll('[data-locale-link]').forEach(link => {
      const destination = new URL(link.href);
      destination.hash = location.hash;
      link.href = destination.href;
    });
  }
  syncLocaleAnchors();
  window.addEventListener('hashchange', syncLocaleAnchors);
  const header = document.querySelector('.site-header, .lesson-header');
  if (header) {
    const measureHeader = () => root.style.setProperty('--header', `${Math.ceil(header.getBoundingClientRect().height)}px`);
    measureHeader();
    if ('ResizeObserver' in window) new ResizeObserver(measureHeader).observe(header);
  }
  render();
  if (select) select.closest('label').hidden = false;
})();
