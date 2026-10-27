import { describe, it, expect } from 'vitest';
import {
  format_bytes,
  generate_uuid,
  string_to_boolean,
  is_object,
  create_box,
  decodeURIComponentSafe,
  unescape_html,
  decode_HTMLEntities,
  html_spinner,
  fetchSettings,
  error_content,
} from '@modules/utils.js';

describe('format_bytes', () => {
  it('formats zero and small values in Bytes', () => {
    expect(format_bytes(0)).toBe('0 Bytes');
    expect(format_bytes(1023)).toBe('1023 Bytes');
  });
  it('switches unit at 1024', () => {
    expect(format_bytes(1024)).toBe('1 KB');
    expect(format_bytes(1073741824)).toBe('1 GB');
  });
  it('rounds to 2 decimals', () => {
    // MAX_UPLOAD_SIZE of the local back config
    expect(format_bytes(6442450941)).toBe('6 GB');
    expect(format_bytes(1536)).toBe('1.5 KB');
  });
});

describe('generate_uuid', () => {
  it('returns distinct v4 uuids', () => {
    const a = generate_uuid();
    expect(a).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
    expect(generate_uuid()).not.toBe(a);
  });
});

describe('string_to_boolean', () => {
  it('reads true-ish and false-ish strings', () => {
    expect(string_to_boolean(' Yes ')).toBe(true);
    expect(string_to_boolean('1')).toBe(true);
    expect(string_to_boolean('no')).toBe(false);
    expect(string_to_boolean('')).toBe(false);
    expect(string_to_boolean(false)).toBe(false);
  });
});

describe('is_object', () => {
  it('accepts plain objects only', () => {
    expect(is_object({})).toBe(true);
    expect(is_object([])).toBe(false);
    expect(is_object(null)).toBe(false);
    expect(is_object('x')).toBe(false);
  });
});

describe('create_box', () => {
  it('builds the element with classes, dataset and attributes', () => {
    const el = create_box('div', {
      class: ['a', 'b'],
      dataset: { type: 'file' },
      title: 'hello',
    });
    expect(el.tagName).toBe('DIV');
    expect([...el.classList]).toEqual(['a', 'b']);
    expect(el.dataset.type).toBe('file');
    expect(el.getAttribute('title')).toBe('hello');
  });
  it('sets text as text, never as markup', () => {
    // what DOMPurify strips depends on the DOM implementation: checked in a real browser
    const el = create_box('span', { text: '<b>bold</b>' });
    expect(el.children.length).toBe(0);
  });
  it('appends to the parent, with the separator only between children', () => {
    const parent = document.createElement('p');
    const first = create_box('span', { text: 'a' }, parent, ', ');
    create_box('span', { text: 'b' }, parent, ', ');
    expect(first.parentNode).toBe(parent);
    expect(parent.textContent).toBe('a, b');
  });
});

describe('decodeURIComponentSafe', () => {
  it('decodes valid sequences', () => {
    expect(decodeURIComponentSafe('a%20b')).toBe('a b');
  });
  it('keeps an invalid % instead of throwing', () => {
    expect(decodeURIComponentSafe('50% done')).toBe('50% done');
  });
  it('returns an empty string for undefined or null', () => {
    expect(decodeURIComponentSafe(undefined)).toBe('');
    expect(decodeURIComponentSafe(null)).toBe('');
  });
});

describe('html entities', () => {
  it('unescape_html reverses tom-select escaping', () => {
    expect(unescape_html('&lt;b&gt; &amp; &quot;x&quot;')).toBe('<b> & "x"');
  });
  it('decode_HTMLEntities decodes named and numeric entities', () => {
    expect(decode_HTMLEntities('&eacute;&#233;')).toBe('éé');
  });
});

describe('html_spinner', () => {
  it('forwards classes and size', () => {
    const svg = html_spinner('text-stone-500 mr-1', 'h-4 w-4');
    expect(svg).toContain('animate-spin');
    expect(svg).toContain('h-4 w-4');
    expect(svg).toContain('text-stone-500 mr-1');
  });
});

describe('fetchSettings', () => {
  it('adds the ajax header and defaults', () => {
    const opts = fetchSettings({ headers: { a: '1' } });
    expect(opts.headers).toEqual({ a: '1', 'X-Requested-With': 'XMLHttpRequest' });
    expect(opts.credentials).toBe('include');
    expect(opts.redirect).toBe('error');
  });
});

describe('error_content', () => {
  it('turns any rejection into a string', () => {
    expect(error_content({ status: 404, statusText: 'Not Found' })).toBe('404 Not Found');
    expect(error_content(new Error('boom'))).toBe('boom');
    expect(error_content('plain')).toBe('plain');
    expect(error_content(undefined)).toBe('Unknown error');
  });
});
