import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8').replaceAll('\r\n', '\n');
const sources = JSON.parse(read('_data/sources.json'));
const ids = ['scope', 'reuse', 'code', 'images', 'sources', 'third-party'];
const notices = read('THIRD_PARTY_NOTICES.md');
const pages = ['rights-and-licenses.md', 'en/rights-and-licenses.md'];

assert.equal(sources.length, 16, 'All 14 lessons and both topics must be attributed');
assert.equal(new Set(sources.map(source => source.id)).size, 16, 'Unique source anchors');
assert.deepEqual(sources.filter(source => source.part).map(source => source.part), Array.from({ length: 14 }, (_, i) => i + 1));
const posts = fs.readdirSync(path.join(root, '_posts')).filter(file => file.endsWith('.md')).map(file => ({ file, text: read('_posts/' + file) }));
for (const source of sources) {
  for (const lang of ['ko', 'en']) {
    assert(source.title[lang]?.trim(), `${source.id}: ${lang} title`);
    assert(source.contribution[lang]?.trim(), `${source.id}: ${lang} contribution`);
  }
  assert(source.references.length, `${source.id}: original references`);
  for (const reference of source.references) {
    assert.equal(new URL(reference.url).protocol, 'https:');
    assert(notices.includes(reference.url), `${source.id}: source missing from notices`);
  }
  for (const file of source.files) assert(fs.existsSync(path.join(root, file)), `${source.id}: missing ${file}`);
  if (source.part) {
    const post = posts.find(post => Number(post.text.match(/^part:\s*(\d+)/m)?.[1]) === source.part);
    assert(post, `${source.id}: lesson exists`);
    const route = post.text.match(/^permalink:\s*(\S+)/m)?.[1] || '/' + post.file.replace(/^\d{4}-\d{2}-\d{2}-/, '').replace(/\.md$/, '') + '/';
    assert.equal(route, source.url, `${source.id}: lesson route matches attribution`);
    assert(fs.existsSync(path.join(root, 'en/lessons', source.url.slice(1, -1) + '.md')), `${source.id}: English counterpart exists`);
  }
}
for (const file of pages) {
  const text = read(file);
  assert.match(text, /^layout: rights$/m);
  assert(text.includes('{% include source-inventory.html %}'));
  for (const id of ids) {
    assert.equal(text.split(`id="${id}"`).length - 1, 1, `${file}: unique ${id}`);
    assert(text.includes(`id: ${id},`), `${file}: TOC matches ${id}`);
  }
  for (const evidence of ['License_and_Copyright', 'THIRD_PARTY_NOTICES.md', 'manifest.json', 'comparison-provenance.json', 'ca145119e5bd0f0804d846ea42e35e4c3daa91de']) {
    assert(text.includes(evidence), `${file}: missing ${evidence}`);
  }
}
for (const layout of ['lesson', 'topic', 'explorer', 'rights']) {
  assert(read(`_layouts/${layout}.html`).includes('{% include rights-link.html %}'), `${layout}: discoverable rights page`);
}
for (const layout of ['lesson', 'topic']) {
  assert(read(`_layouts/${layout}.html`).includes('{% include source-credit.html %}'), `${layout}: source credit`);
}
assert.match(read('LICENSES/Meep-GPL-2.0.txt'), /Version 2, June 1991/);
assert.match(read('code/optical_beams/source/LICENSE'), /Copyright \(c\) 2018 Daniel Kotik/);
assert(notices.includes('GSAP Standard License'));
console.log('PASS local: 16 attributed lessons/topics, bilingual policies, notices, license copy and shared links');

if (process.argv.includes('--live')) {
  const base = 'https://jin-castle.github.io/meep-examples';
  const rights = '/rights-and-licenses/';
  const routes = ['/', rights, ...sources.map(source => source.url)].flatMap(route => [route, '/en' + route]);
  const failures = [];
  let cursor = 0;
  await Promise.all(Array.from({ length: 4 }, async () => {
    while (cursor < routes.length) {
      const route = routes[cursor++];
      try {
        const response = await fetch(base + route, { signal: AbortSignal.timeout(30000) });
        const html = (await response.text()).replaceAll('&#39;', "'").replaceAll('&#x27;', "'").replaceAll('&quot;', '"').replaceAll('&amp;', '&');
        const lang = route.startsWith('/en/') ? 'en' : 'ko';
        const localePrefix = lang === 'en' ? '/en' : '';
        assert.equal(response.status, 200, `${route}: HTTP status`);
        assert(html.includes(`<html lang="${lang}"`), `${route}: document language`);
        assert(html.includes(`href="/meep-examples${localePrefix}${rights}"`), `${route}: localized footer link`);
        assert(!/\{%\s*(?:include|assign)|\{\{\s*(?:site\.|ui\.)/.test(html), `${route}: unrendered Liquid`);
        if (route.endsWith(rights)) {
          assert(html.includes('id="theme-select"'), `${route}: theme control`);
          assert(html.includes(`rel="canonical" href="${base}${route}"`), `${route}: canonical`);
          assert.equal((html.match(/class="source-record"/g) || []).length, 16, `${route}: complete source inventory`);
          for (const id of ids) assert(html.includes(`id="${id}"`), `${route}: ${id} anchor`);
          for (const source of sources) {
            assert(html.includes(`id="source-${source.id}"`), `${route}: ${source.id} anchor`);
            assert(html.includes(source.contribution[lang]), `${route}: localized contribution for ${source.id}`);
            assert(html.includes(`href="/meep-examples${localePrefix}${source.url}"`), `${route}: ${source.id} lesson link`);
          }
          const other = lang === 'en' ? rights : '/en' + rights;
          assert(html.includes(`hreflang="${lang === 'en' ? 'ko' : 'en'}" href="${base}${other}"`), `${route}: language alternate`);
        } else if (route !== '/' && route !== '/en/') {
          const source = sources.find(source => route === source.url || route === '/en' + source.url);
          assert(html.includes('source-credit'), `${route}: rendered source credit`);
          assert(html.includes(`rights-and-licenses/#source-${source.id}`), `${route}: matching source anchor`);
          assert(html.includes(source.contribution[lang]), `${route}: correct contribution`);
        }
      } catch (error) { failures.push(String(error)); }
    }
  }));
  assert.deepEqual(failures, [], JSON.stringify(failures, null, 2));
  console.log(`PASS live: ${routes.length} routes, both policies, all localized source credits and footer links`);
}
