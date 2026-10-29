import { describe, it, expect } from 'vitest';
import { compressed_estimate, acceptFile } from '@modules/files/js-dirtozip.js';

describe('compressed_estimate', () => {
  it('halves the size of compressible text files', () => {
    expect(compressed_estimate({ name: 'data.tsv', size: 1001 })).toBe(500);
    expect(compressed_estimate({ name: 'notes.txt', size: 10 })).toBe(5);
  });
  it('keeps the size of already compressed files', () => {
    expect(compressed_estimate({ name: 'img.png', size: 1001 })).toBe(1001);
    expect(compressed_estimate({ name: 'arch.zip', size: 7 })).toBe(7);
  });
});

describe('acceptFile', () => {
  it('accepts the listed extensions', () => {
    ['a.tsv', 'b.png', 'c.jpg', 'd.jpeg', 'e.zip', 'f.gz', 'g.7z', 'h.bz2'].forEach((name) => {
      expect(acceptFile({ name }), name).toBe(true);
    });
  });
  it('rejects other extensions', () => {
    expect(acceptFile({ name: 'huge.bin' })).toBe(false);
    expect(acceptFile({ name: 'doc.pdf' })).toBe(false);
  });

  it('rejects partial extensions (.ts, .sv, .pn)', () => {
    expect(acceptFile({ name: 'x.ts' })).toBe(false);
    expect(acceptFile({ name: 'x.sv' })).toBe(false);
    expect(acceptFile({ name: 'x.pn' })).toBe(false);
  });
  it('accepts upper case extensions (.PNG)', () => {
    expect(acceptFile({ name: 'X.PNG' })).toBe(true);
  });
  it('rejects names without extension', () => {
    expect(acceptFile({ name: 'tsv' })).toBe(false);
    expect(acceptFile({ name: 'README' })).toBe(false);
  });
});
