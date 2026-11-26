import { describe, it, expect, vi, afterEach } from 'vitest';
import { JsTomSelect } from '@modules/js-tom-select.js';
import { samples_filters, focus_target } from '@modules/js-map.js';

afterEach(() => {
  document.querySelectorAll('.test-page').forEach((el) => el.remove());
});

// same markup as v2/explore/index.html
function filtersPage() {
  const div = document.createElement('div');
  div.className = 'test-page';
  div.innerHTML = `<div id="menu"><button type="button" id="trigger" aria-expanded="false" disabled>Filters</button>
    <form id="form">
      <div><label for="filt_projid">Projects</label>
      <select id="filt_projid" name="projid" class="js-autocomplete" data-type="exploreproject" multiple></select></div>
      <div><label for="filt_mapn">North</label><input id="filt_mapn" name="MapN" type="number" step="any"></div>
      <div><label for="filt_maps">South</label><input id="filt_maps" name="MapS" type="number" step="any"></div>
      <button type="submit" id="apply">Apply</button><button type="reset" id="reset">Reset</button>
    </form></div><span id="text"></span>`;
  document.body.append(div);
  const form = div.querySelector('#form');
  const select = div.querySelector('select');
  JsTomSelect.applyTo(select);
  const load = vi.fn(async () => true);
  const selection = { clear: vi.fn() };
  const map = { getViewport: () => document.createElement('div') };
  const focus = vi.fn(async () => {});
  samples_filters(form, map, selection, load, div.querySelector('#text'), focus);
  return { div, form, select, load, selection, focus, menu: div.querySelector('#menu'), text: div.querySelector('#text') };
}

const tags = (text) => [...text.querySelectorAll('.item')].map((tag) => tag.firstChild.textContent);
const removeTag = (text, label) => [...text.querySelectorAll('.item')]
  .find((tag) => tag.firstChild.textContent === label).querySelector('.remove').click();

describe('js-map samples filters', () => {
  it('removes a project from its tag, from the form and the search', async () => {
    const { div, select, load, text } = filtersPage();
    select.tomselect.addOptions([{ id: 12, text: 'Tara' }, { id: 13, text: 'Malina' }]);
    select.tomselect.addItems(['12', '13']);
    div.querySelector('#filt_mapn').value = '50';
    div.querySelector('#apply').click();
    removeTag(text, 'Projects: Tara');
    expect(tags(text)).toEqual(['Projects: Malina', 'North: 50']);
    expect(select.tomselect.items).toEqual(['13']);
    expect(load).toHaveBeenLastCalledWith('projid=13&MapN=50');
  });

  it('removes a number from its tag, the form staying closed', async () => {
    const { div, load, text } = filtersPage();
    const north = div.querySelector('#filt_mapn');
    north.value = '50';
    div.querySelector('#apply').click();
    removeTag(text, 'North: 50');
    expect(north.value).toBe('');
    expect(tags(text)).toEqual([]);
    expect(load).toHaveBeenLastCalledWith('');
    expect(div.querySelector('#trigger').getAttribute('aria-expanded')).toBe('false');
  });

  it('does not apply the values changed in the form when removing a tag', async () => {
    const { div, load, text } = filtersPage();
    const north = div.querySelector('#filt_mapn');
    const south = div.querySelector('#filt_maps');
    north.value = '50';
    south.value = '-10';
    div.querySelector('#apply').click();
    north.value = '60';
    removeTag(text, 'South: -10');
    expect(load).toHaveBeenLastCalledWith('MapN=50');
    expect(tags(text)).toEqual(['North: 50']);
    // not the applied value any more: left as typed
    expect(north.value).toBe('60');
  });

  it('displays the applied filters as tags, with the project names', async () => {
    const { div, select, load, selection, text } = filtersPage();
    select.tomselect.addOptions([{ id: 12, text: 'Tara' }, { id: 13, text: 'Malina' }]);
    select.tomselect.addItems(['12', '13']);
    div.querySelector('#filt_mapn').value = '50';
    div.querySelector('#apply').click();
    expect(tags(text)).toEqual(['Projects: Tara', 'Projects: Malina', 'North: 50']);
    expect(load).toHaveBeenCalledWith('projid=12%2C13&MapN=50');
    expect(selection.clear).toHaveBeenCalled();
  });

  it('opens and closes the form with its button', async () => {
    const { div } = filtersPage();
    const trigger = div.querySelector('#trigger');
    // enabled once the map is ready
    expect(trigger.disabled).toBe(false);
    trigger.click();
    expect(trigger.getAttribute('aria-expanded')).toBe('true');
    trigger.click();
    expect(trigger.getAttribute('aria-expanded')).toBe('false');
  });

  it('closes the form when applied, the focus back on the button', async () => {
    const { div } = filtersPage();
    const trigger = div.querySelector('#trigger');
    trigger.click();
    div.querySelector('#filt_mapn').focus();
    div.querySelector('#apply').click();
    expect(trigger.getAttribute('aria-expanded')).toBe('false');
    expect(document.activeElement).toBe(trigger);
  });

  it('keeps the form open on reset', async () => {
    const { div } = filtersPage();
    const trigger = div.querySelector('#trigger');
    trigger.click();
    div.querySelector('#reset').click();
    expect(trigger.getAttribute('aria-expanded')).toBe('true');
  });

  it('empties the text on reset', async () => {
    const { div, text, load } = filtersPage();
    div.querySelector('#filt_maps').value = '-10';
    div.querySelector('#apply').click();
    expect(tags(text)).toEqual(['South: -10']);
    div.querySelector('#reset').click();
    expect(tags(text)).toEqual([]);
    expect(load).toHaveBeenLastCalledWith(undefined);
  });
});

describe('js-map focus on the applied filters', () => {
  const entry = (name, value) => ({ name, value, label: name, text: value });

  it('moves the map once the samples are loaded, with the applied filters', async () => {
    const { div, load, focus } = filtersPage();
    div.querySelector('#filt_maps').value = '-60';
    div.querySelector('#apply').click();
    await vi.waitFor(() => expect(focus).toHaveBeenCalledTimes(1));
    expect(load).toHaveBeenCalledBefore(focus);
    expect(focus.mock.calls[0][0].map(({ name, value }) => [name, value])).toEqual([['MapS', '-60']]);
  });

  it('moves the map back to the whole world on reset and when the last tag is removed', async () => {
    const { div, text, focus } = filtersPage();
    div.querySelector('#filt_mapn').value = '50';
    div.querySelector('#apply').click();
    removeTag(text, 'North: 50');
    await vi.waitFor(() => expect(focus).toHaveBeenCalledTimes(2));
    expect(focus).toHaveBeenLastCalledWith([]);
    div.querySelector('#reset').click();
    await vi.waitFor(() => expect(focus).toHaveBeenCalledTimes(3));
    expect(focus).toHaveBeenLastCalledWith([]);
  });

  it('does not move the map when a newer load replaced this one', async () => {
    const { div, load, focus } = filtersPage();
    load.mockResolvedValueOnce(false);
    div.querySelector('#apply').click();
    await vi.waitFor(() => expect(load).toHaveBeenCalled());
    await Promise.resolve();
    expect(focus).not.toHaveBeenCalled();
  });

  it('shows Antarctic samples in the Antarctic view', () => {
    const lonlats = [[-60, -65], [140, -66.5]];
    expect(focus_target([entry('projid', '12')], lonlats)).toEqual({ points: lonlats, view: 'south' });
  });

  it('shows Arctic samples in the Arctic view', () => {
    expect(focus_target([], [[10, 78], [-150, 72]]).view).toBe('north');
  });

  it('stays in the world view for samples at mid latitudes or in both zones', () => {
    expect(focus_target([], [[5, 43], [-20, 70]]).view).toBe('world');
    expect(focus_target([], [[0, -70], [0, 75]]).view).toBe('world');
  });

  it('shows the complete box of the filters rather than the samples', () => {
    const box = ['MapN', '-62', 'MapS', '-78', 'MapW', '-70', 'MapE', '-30'];
    const entries = [];
    for (let i = 0; i < box.length; i += 2) entries.push(entry(box[i], box[i + 1]));
    const target = focus_target(entries, [[0, 10]]);
    expect(target.view).toBe('south');
    const lons = target.points.map(p => p[0]);
    const lats = target.points.map(p => p[1]);
    expect([Math.min(...lons), Math.max(...lons)]).toEqual([-70, -30]);
    expect([Math.min(...lats), Math.max(...lats)]).toEqual([-78, -62]);
  });

  it('crosses the antimeridian when west is greater than east', () => {
    const entries = [entry('MapN', '10'), entry('MapS', '-10'), entry('MapW', '170'), entry('MapE', '-170')];
    const lons = focus_target(entries, []).points.map(p => p[0]);
    expect([Math.min(...lons), Math.max(...lons)]).toEqual([170, 190]);
  });

  it('uses the samples when the box is not complete', () => {
    const lonlats = [[5, 43]];
    expect(focus_target([entry('MapN', '50')], lonlats).points).toEqual(lonlats);
  });

  it('does not move without box nor samples', () => {
    expect(focus_target([entry('projid', '12')], [])).toBeNull();
  });
});
