// Check rendered neighbors, including gaps in the reserved chapter numbering.
// node _tools/check-pagination.mjs --site ../site-preview
// node _tools/check-pagination.mjs --live
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sources = JSON.parse(await fs.readFile(path.join(root, '_data/sources.json'), 'utf8'));
const lessons = sources.filter(item => item.part).sort((a, b) => a.part - b.part);
const live = process.argv.includes('--live');
const siteFlag = process.argv.indexOf('--site');
if (siteFlag !== -1) assert(process.argv[siteFlag + 1], '--site requires a build directory');
const site = path.resolve(siteFlag === -1 ? path.join(root, '_site') : process.argv[siteFlag + 1]);
let checked = 0;
for (const lang of ['ko', 'en']) {
  const prefix = lang === 'en' ? '/en' : '';
  for (let index = 0; index < lessons.length; index++) {
    const item = lessons[index];
    const route = prefix + item.url;
    let html;
    if (live) {
      const response = await fetch('https://jin-castle.github.io/meep-examples' + route);
      assert.equal(response.status, 200, route);
      html = await response.text();
    } else {
      html = await fs.readFile(path.join(site, route, 'index.html'), 'utf8');
    }
    const nav = html.match(/<nav class="lesson-pagination"[^>]*>([\s\S]*?)<\/nav>/)?.[1];
    assert(nav !== undefined, `${route}: pagination present`);
    const actual = [...nav.matchAll(/<a href="([^"]+)"/g)].map(match => match[1]);
    const neighbors = [lessons[index - 1], lessons[index + 1]].filter(Boolean);
    assert.deepEqual(actual, neighbors.map(n => '/meep-examples' + prefix + n.url), route);
    for (const neighbor of neighbors) assert(nav.includes(String(neighbor.part)), `${route}: chapter label`);
    checked++;
  }
}
console.log(`PASS ${live ? 'live' : 'built'}: ${checked} localized chapter navigations, including numbering gaps`);
