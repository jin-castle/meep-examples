import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const root = new URL('../', import.meta.url);
const read = file => fs.readFileSync(new URL(file, root), 'utf8');
const source = read('assets/analytics.js');
const id = read('_config.yml').match(/measurement_id:\s*"(G-[A-Z0-9]+)"/)[1];
const token = read('_config.yml').match(/google_site_verification:\s*"([^"]+)"/)[1];
const base = 'https://jin-castle.github.io/meep-examples';

function browser({ stored = null, unavailable = false, writeDenied = false, denialFallback = false, cookiesBlocked = false, url = base + '/en/point-line-source/?lesson=cache#understand' } = {}) {
  const buttons = ['denied', 'granted'].map(choice => ({ dataset: { choice }, focus() {}, addEventListener(_, fn) { this.click = fn; } }));
  const settings = { hidden: true, focus() {}, addEventListener(_, fn) { this.click = fn; } };
  const status = {};
  const privacy = {};
  const banner = { hidden: false, setAttribute() {}, querySelector: selector => selector === '.analytics-status' ? status : selector.startsWith('[data-choice') ? buttons[0] : privacy, querySelectorAll: () => buttons };
  const tags = [];
  const cookieWrites = [];
  const cookies = new Map([['meep_ga', 'old'], ['meep_ga_4BL7PWF8YR', 'old'], ['other_site', 'keep']]);
  if (denialFallback) cookies.set('meep_analytics_denied', '1');
  const storage = new Map(stored ? [['meep-examples:analytics-consent:v1', stored]] : []);
  const events = {};
  const location = new URL(url);
  let reloads = 0;
  location.reload = () => { reloads++; };
  const document = {
    currentScript: { dataset: { measurementId: id, siteUrl: base + '/', privacyUrl: '/meep-examples/en/privacy/' } },
    documentElement: { lang: 'en' },
    referrer: 'https://example.org/private/path?email=private@example.org',
    createElement: name => name === 'section' ? banner : {},
    body: { append() {} }, head: { append: tag => tags.push(tag) },
    querySelectorAll: () => [settings],
    get cookie() { return [...cookies].map(([name, value]) => `${name}=${value}`).join('; '); },
    set cookie(value) {
      cookieWrites.push(value);
      if (cookiesBlocked) return;
      const [name, content] = value.split(';')[0].split('=');
      if (value.includes('Max-Age=0;')) cookies.delete(name);
      else cookies.set(name, content);
    }
  };
  const window = { addEventListener: (name, fn) => { events[name] = fn; } };
  const localStorage = {
    getItem(key) { if (unavailable) throw Error('unavailable'); return storage.get(key) ?? null; },
    setItem(key, value) { if (unavailable || writeDenied) throw Error('unavailable'); storage.set(key, value); }
  };
  vm.runInNewContext(source, { document, window, localStorage, location, URL, Date });
  return { buttons, settings, banner, tags, cookieWrites, cookies, storage, window, events, status, privacy, denyWrites() { writeDenied = true; }, get reloads() { return reloads; } };
}

let b = browser();
assert.equal(b.tags.length, 0, 'No Google script before consent');
assert.equal(b.window.dataLayer, undefined, 'No event queue before consent');
assert.equal(b.banner.hidden, false, 'First visit can choose');
b.buttons[0].click();
assert.equal(b.tags.length, 0, 'Declining never loads Google');
assert.equal(b.banner.hidden, true);
assert.equal(b.storage.get('meep-examples:analytics-consent:v1'), 'denied');
b.settings.click();
assert.equal(b.banner.hidden, false, 'Settings can reopen');
b.buttons[1].click();
b.settings.click();
b.buttons[1].click();
assert.equal(b.tags.length, 1, 'Repeated acceptance initializes only once');
assert.equal(b.tags[0].src, `https://www.googletagmanager.com/gtag/js?id=${id}`);
const commands = b.window.dataLayer.map(args => Array.from(args));
const configs = commands.filter(args => args[0] === 'config');
assert.equal(configs.length, 1, 'Exactly one initial pageview configuration');
assert.equal(configs[0][2].page_location, base + '/en/point-line-source/');
assert.equal(configs[0][2].page_referrer, 'https://example.org/');
assert.equal(configs[0][2].allow_google_signals, false);
assert.equal(configs[0][2].allow_ad_personalization_signals, false);
assert.equal(configs[0][2].cookie_path, '/meep-examples/');
assert.equal(commands[0][2].ad_user_data, 'denied');
assert.equal(commands[1][2].analytics_storage, 'granted');
b.cookies.set('meep_ga', 'new');
b.cookies.set('meep_ga_4BL7PWF8YR', 'new');
const cookieWriteCount = b.cookieWrites.length;
b.buttons[0].click();
assert.equal(b.window[`ga-disable-${id}`], true, 'Withdrawal disables collection');
assert.equal(b.reloads, 1, 'Withdrawal removes loaded listeners through reload');
const deletions = b.cookieWrites.slice(cookieWriteCount).filter(value => value.startsWith('meep_ga'));
assert.equal(deletions.length, 2, 'Both analytics cookies are deleted');
assert(deletions.every(value => value.includes('Path=/meep-examples/')));
assert.equal(b.cookies.get('other_site'), 'keep', 'Other projects retain their cookies');
assert.equal(b.cookies.has('meep_ga'), false);

b = browser({ stored: 'denied' });
assert.equal(b.tags.length, 0);
assert.equal(b.banner.hidden, true, 'Remembered refusal is respected');
b = browser({ stored: 'granted' });
assert.equal(b.tags.length, 1, 'Remembered permission loads the tag');
b.events.storage({ key: 'meep-examples:analytics-consent:v1', newValue: 'denied' });
assert.equal(b.window[`ga-disable-${id}`], true, 'Revocation in another tab is respected');
assert.equal(b.reloads, 1);
b = browser({ unavailable: true });
b.buttons[1].click();
assert.equal(b.tags.length, 1, 'Storage failure still allows an explicit current-page choice');
b.buttons[0].click();
assert.equal(b.reloads, 1, 'Storage failure does not prevent withdrawal');
b = browser({ stored: 'granted', writeDenied: true });
assert.equal(b.tags.length, 0, 'A stale grant in read-only storage fails closed');
assert.equal(b.banner.hidden, false);
b.buttons[1].click();
b.buttons[0].click();
assert.equal(b.window[`ga-disable-${id}`], true);
assert.equal(browser({ stored: 'granted', writeDenied: true }).tags.length, 0, 'Reload cannot restart a stale read-only grant');
b = browser({ stored: 'granted' });
b.denyWrites();
b.buttons[0].click();
assert.equal(b.cookies.get('meep_analytics_denied'), '1', 'Failed storage write uses a denial-only fallback');
assert.equal(b.reloads, 1);
assert.equal(browser({ stored: 'granted', denialFallback: true }).tags.length, 0, 'Transient write recovery cannot restore revoked permission');
b = browser({ stored: 'granted', cookiesBlocked: true });
b.denyWrites();
b.buttons[0].click();
assert.equal(b.reloads, 0, 'No reload if denial cannot be persisted anywhere');
assert.equal(b.window[`ga-disable-${id}`], true);
assert.equal(b.banner.hidden, false, 'Unsaved choice is explained');
b.buttons[1].click();
assert.equal(b.window[`ga-disable-${id}`], false, 'A subsequent explicit allowance can resume on the current page');
assert.equal(b.tags.length, 1, 'Resuming does not create a duplicate tag');
for (const url of ['http://localhost:4000/meep-examples/', 'https://jin-castle.github.io/other-project/', 'https://jin-castle.github.io/meep-examples-other/']) {
  b = browser({ stored: 'granted', url });
  assert.equal(b.tags.length, 0, `Production guard: ${url}`);
  assert.equal(b.settings.hidden, true);
}
console.log('PASS local analytics: consent, refusal, repeat grant, withdrawal, scoped cookies, cross-tab revocation, blocked storage, URL privacy and production guards');

if (process.argv.includes('--live')) {
  const sources = JSON.parse(read('_data/sources.json'));
  const routes = ['/', '/privacy/', '/rights-and-licenses/', ...sources.map(s => s.url)].flatMap(route => [route, '/en' + route]);
  let cursor = 0;
  await Promise.all(Array.from({ length: 4 }, async () => {
    while (cursor < routes.length) {
      const route = routes[cursor++];
      const response = await fetch(base + route, { signal: AbortSignal.timeout(30000) });
      assert.equal(response.status, 200, route);
      const html = await response.text();
      assert.equal((html.match(/id="meep-analytics"/g) || []).length, 1, route + ': one initialization');
      assert(html.includes(`data-measurement-id="${id}"`), route + ': configured ID');
      assert(html.includes(`name="google-site-verification" content="${token}"`), route + ': verification');
      assert(!/<script[^>]+src="https:\/\/www.googletagmanager/.test(html), route + ': no unconditional Google script');
      const locale = route.startsWith('/en/') ? '/en' : '';
      assert(html.includes(`href="/meep-examples${locale}/privacy/"`), route + ': localized privacy');
    }
  }));
  const xml = await (await fetch(base + '/sitemap.xml')).text();
  const urls = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);
  assert.equal(urls.length, new Set(urls).size, 'No duplicate sitemap URLs');
  for (const route of routes) assert(urls.includes(base + route), 'Sitemap contains ' + route);
  assert(!xml.includes('{%'), 'Sitemap Liquid is rendered');
  console.log(`PASS live analytics: ${routes.length} bilingual routes and ${urls.length} sitemap URLs`);
}
