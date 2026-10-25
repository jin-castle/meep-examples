(() => {
  'use strict';
  const config = document.currentScript;
  if (!config) return;
  const id = config.dataset.measurementId;
  const site = new URL(config.dataset.siteUrl);
  if (!/^G-[A-Z0-9]+$/.test(id || '') || location.origin !== site.origin || !location.pathname.startsWith(site.pathname)) return;
  const key = 'meep-examples:analytics-consent:v1';
  const disable = `ga-disable-${id}`;
  const english = document.documentElement.lang === 'en';
  let choice = null;
  try {
    choice = localStorage.getItem(key);
    if (choice === 'granted') localStorage.setItem(key, choice);
  } catch (_) { choice = null; }
  const hasDeniedFallback = () => document.cookie.split(';').some(entry => entry.trim() === 'meep_analytics_denied=1');
  if (hasDeniedFallback()) choice = 'denied';
  let started = false;
  let returnFocus = null;
  const banner = document.createElement('section');
  banner.className = 'analytics-consent';
  banner.hidden = true;
  banner.setAttribute('aria-labelledby', 'analytics-consent-title');
  banner.innerHTML = english
    ? '<div><h2 id="analytics-consent-title">Help improve these lessons</h2><p>With your permission, Google Analytics uses cookies to measure visits, pages read and referral sources. Optional; the lessons work without it. <a class="analytics-privacy">Privacy details</a></p><p class="analytics-status" role="status"></p></div><div class="analytics-actions"><button type="button" data-choice="denied">Decline analytics</button><button type="button" data-choice="granted">Allow analytics</button></div>'
    : '<div><h2 id="analytics-consent-title">더 나은 학습 자료를 위한 방문 통계</h2><p>동의하면 Google Analytics 쿠키로 방문·조회한 페이지·유입 경로를 측정합니다. 선택 사항이며 거부해도 학습에 제한이 없습니다. <a class="analytics-privacy">개인정보 안내</a></p><p class="analytics-status" role="status"></p></div><div class="analytics-actions"><button type="button" data-choice="denied">통계 수집 거부</button><button type="button" data-choice="granted">통계 수집 동의</button></div>';
  banner.querySelector('.analytics-privacy').href = config.dataset.privacyUrl;
  document.body.append(banner);
  const status = banner.querySelector('.analytics-status');
  function show() {
    status.textContent = choice === 'granted'
      ? (english ? 'Current choice: allowed. You can withdraw below.' : '현재: 동의. 아래에서 동의를 철회할 수 있습니다.')
      : choice === 'denied' ? (english ? 'Current choice: declined.' : '현재: 거부.') : '';
    banner.hidden = false;
  }
  function clearCookies() {
    for (const entry of document.cookie.split(';')) {
      const name = entry.trim().split('=')[0];
      if (name.startsWith('meep_ga')) document.cookie = `${name}=; Max-Age=0; Path=${site.pathname}; SameSite=Lax; Secure`;
    }
  }
  function start() {
    window[disable] = false;
    if (started) return;
    started = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
    window.gtag('consent', 'update', { analytics_storage: 'granted' });
    window.gtag('js', new Date());
    let referrer = '';
    try { referrer = new URL(document.referrer).origin + '/'; } catch (_) {}
    window.gtag('config', id, {
      page_location: location.origin + location.pathname,
      page_referrer: referrer,
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      cookie_domain: 'none',
      cookie_path: site.pathname,
      cookie_prefix: 'meep',
      cookie_expires: 60 * 60 * 24 * 60,
      cookie_update: false
    });
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = `https://www.googletagmanager.com/gtag/js?id=${id}`;
    document.head.append(tag);
  }
  function apply(value) {
    choice = value;
    let saved = true;
    try { localStorage.setItem(key, value); } catch (_) { saved = false; }
    if (!saved && value === 'denied') {
      document.cookie = `meep_analytics_denied=1; Max-Age=5184000; Path=${site.pathname}; SameSite=Lax; Secure`;
      saved = hasDeniedFallback();
    } else {
      document.cookie = `meep_analytics_denied=; Max-Age=0; Path=${site.pathname}; SameSite=Lax; Secure`;
    }
    banner.hidden = true;
    returnFocus?.focus({ preventScroll: true });
    if (value === 'granted') start();
    else {
      window[disable] = true;
      clearCookies();
      // Reload only after stopping an already-loaded tag, to remove its listeners.
      if (started && saved) location.reload();
      if (!saved) {
        show();
        status.textContent = english
          ? 'Analytics is off on this page. Your browser could not save the choice; clear this site’s storage to remove any earlier allowance.'
          : '현재 페이지의 통계 수집을 중단했습니다. 브라우저에 선택을 저장할 수 없습니다. 이전 동의 기록은 이 사이트의 저장소를 지워 제거할 수 있습니다.';
      }
    }
  }
  banner.querySelectorAll('[data-choice]').forEach(button => button.addEventListener('click', () => apply(button.dataset.choice)));
  document.querySelectorAll('.analytics-settings').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', () => {
      returnFocus = button;
      show();
      banner.querySelector('[data-choice="denied"]').focus({ preventScroll: true });
    });
  });
  window.addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    if (event.newValue !== 'granted') {
      window[disable] = true;
      clearCookies();
      if (started) location.reload();
      else { choice = event.newValue; if (choice !== 'denied') show(); }
    }
  });
  if (choice === 'granted') start();
  else {
    window[disable] = true;
    clearCookies();
    if (choice !== 'denied') show();
  }
})();
