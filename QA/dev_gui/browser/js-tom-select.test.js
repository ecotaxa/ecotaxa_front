import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import { page } from 'vitest/browser';
import manifest from '@dist/manifest.json';
import { JsTomSelect } from '@modules/js-tom-select.js';

// Real Chromium with the real production CSS (dev_gui `npm run build`): every CSS file of
// the build manifest is injected, as the app would load them.
const builtcss = import.meta.glob('@dist/*.css', { query: '?raw', import: 'default' });

beforeAll(async () => {
  const wanted = Object.entries(manifest).filter(([k]) => k.endsWith('.css')).map(([, v]) => v.split('/').pop());
  for (const [path, load] of Object.entries(builtcss)) {
    if (!wanted.includes(path.split('/').pop())) continue;
    const style = document.createElement('style');
    style.textContent = await load();
    document.head.append(style);
  }
});

afterEach(() => {
  document.querySelectorAll('.test-page').forEach((el) => el.remove());
});

// same markup as the taxa preset of project settings (projectsettings.html);
// collection settings (_settings_aggregated.html) adds `readonly`
function taxoSelect(options, attrs = '') {
  const div = document.createElement('div');
  div.className = 'test-page';
  div.innerHTML = `<select id="inittaxo" class="form-multiselect js js-autocomplete taxolb" name="inittaxo[]"
    data-type="taxo" multiple ${attrs} autocomplete=off>${options.map(([id, name, status]) =>
      `<option value="${id}" data-status="${status}" selected="selected"> ${name}</option>`).join('')}</select>`;
  document.body.append(div);
  const select = div.querySelector('select');
  JsTomSelect.applyTo(select);
  return select.tomselect;
}

describe('js-tom-select taxo items', () => {
  it('strikes through selected deprecated taxa', async () => {
    const ts = taxoSelect([[11, 'Deprecated taxon', 'D'], [12, 'Active taxon', 'A']]);
    const deprecated = ts.getItem('11');
    const active = ts.getItem('12');
    await page.screenshot({ element: ts.wrapper, path: '../.vitest/tom-select-deprecated.png' });
    expect(deprecated.classList.contains('deprecated')).toBe(true);
    expect(active.classList.contains('deprecated')).toBe(false);
    // the line must be drawn under the label text, not only computed on the item box
    const label = [...deprecated.querySelectorAll('*'), deprecated].find((el) =>
      [...el.childNodes].some((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim()));
    expect(getComputedStyle(deprecated).textDecorationLine).toBe('line-through');
    expect(label, 'element holding the label text').toBeDefined();
    expect(getComputedStyle(active).textDecorationLine).toBe('none');
  });

  it('strikes through deprecated taxa in a readonly select (collection settings)', () => {
    const ts = taxoSelect([[21, 'Deprecated taxon', 'D'], [22, 'Active taxon', 'A']], 'readonly');
    expect(ts.isDisabled).toBe(true);
    expect(ts.getItem('21').classList.contains('deprecated')).toBe(true);
    expect(getComputedStyle(ts.getItem('21')).textDecorationLine).toBe('line-through');
    expect(ts.getItem('22').classList.contains('deprecated')).toBe(false);
  });

  it('strikes through a deprecated taxon added from the suggestions', () => {
    const ts = taxoSelect([[31, 'Active taxon', 'A']]);
    // what the /search/taxo suggestions give
    ts.addOption({ id: '32', text: 'Added deprecated taxon', status: 'D' });
    ts.addItem('32');
    const added = ts.getItem('32');
    expect(added.classList.contains('deprecated')).toBe(true);
    expect(getComputedStyle(added).textDecorationLine).toBe('line-through');
  });

  it('strikes through a deprecated taxon in the export taxonomy mapping', () => {
    // same markup as a "Grouping for concentration" select of taxonomy/_taxo_recast.html
    const div = document.createElement('div');
    div.className = 'test-page';
    div.innerHTML = `<div class="ts-line"><select name="simple-item-recast-1" id="simple-item-recast-41" data-create=false
      data-taxonomy class="form-select js js-autocomplete" autocomplete="off" data-type="taxo" data-role="replace" data-discard>
      <option selected="selected" value=41 data-status="D">Deprecated taxon</option><option value="">_not_used_</option>
      </select></div>`;
    document.body.append(div);
    const select = div.querySelector('select');
    JsTomSelect.applyTo(select);
    const item = select.tomselect.getItem('41');
    expect(item.classList.contains('deprecated')).toBe(true);
    expect(getComputedStyle(item).textDecorationLine).toBe('line-through');
  });

  it('strikes through a deprecated taxon in the DwC-A export mapping', () => {
    // same markup as the WoRMS select of taxonomy/_dwca_taxo_recast.html
    const div = document.createElement('div');
    div.className = 'test-page';
    div.innerHTML = `<div class="ts-line"><select data-create=false name="item-worms-1" id="item-worms-51" data-worms
      class="form-select js js-autocomplete" autocomplete="off" data-selattr="lineage" data-lineage="Deprecated taxon,living"
      data-id_lineage="51,1" data-type="taxo" data-role="replace" data-discard>
      <option selected="selected" value=51 data-status="D">Deprecated taxon</option><option value="">_not_used_</option>
      </select></div>`;
    document.body.append(div);
    const select = div.querySelector('select');
    JsTomSelect.applyTo(select);
    const item = select.tomselect.getItem('51');
    expect(item.classList.contains('deprecated')).toBe(true);
    expect(getComputedStyle(item).textDecorationLine).toBe('line-through');
  });
});
