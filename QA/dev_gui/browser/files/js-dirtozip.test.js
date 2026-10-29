import { describe, it, expect, afterEach } from 'vitest';
import { ZipReader, BlobReader } from '@zip.js/zip.js';
import { JsDirToZip } from '@modules/files/js-dirtozip.js';
import { ModuleEventEmitter } from '@modules/module-event-emitter.js';

// Real Chromium: real browser storage (OPFS), real File objects, real zip.js.
// No upload: the flow stops when the archive is ready to be sent.

const MAXSIZE = 1000; // small server limit, so no big files are needed
let count = 0;

function setPage(attrs = {}) {
  const div = document.createElement('div');
  div.className = 'test-page';
  div.dataset.max_upload_size = String(MAXSIZE);
  Object.entries(attrs).forEach(([k, v]) => div.dataset[k] = v);
  document.body.append(div);
}

// collects every event JsDirToZip sends to its listener
function start(attrs = {}) {
  setPage(attrs);
  const listener = `test-${++count}`;
  const events = [];
  ['complete', 'message', 'reject', 'counter'].forEach((type) => {
    ModuleEventEmitter.on(type, (e) => events.push({ type, ...e }), listener);
  });
  const dz = JsDirToZip({ listener });
  const waitFor = (match, timeout = 10000) => new Promise((resolve, reject) => {
    const t0 = Date.now();
    const poll = () => {
      const found = events.find(match);
      if (found) return resolve(found);
      if (Date.now() - t0 > timeout) return reject(new Error('event not received: ' + JSON.stringify(events)));
      setTimeout(poll, 20);
    };
    poll();
  });
  return { dz, events, waitFor };
}

// JsDirToZip cleans the browser storage on creation (not awaited), then reports the quota
async function ready(waitFor) {
  await waitFor((e) => e.type === 'message' && e.id === 'quota');
}

function file(name, size) {
  return new File(['x'.repeat(size)], name);
}

async function zipEntries(name) {
  const root = await navigator.storage.getDirectory();
  const handle = await root.getFileHandle(name);
  const reader = new ZipReader(new BlobReader(await handle.getFile()));
  const entries = await reader.getEntries();
  await reader.close();
  return entries.map((e) => e.filename).sort();
}

afterEach(async () => {
  document.querySelectorAll('.test-page').forEach((el) => el.remove());
  const root = await navigator.storage.getDirectory();
  for await (const [key] of root.entries()) await root.removeEntry(key).catch(() => {});
});

describe('JsDirToZip in a real browser', () => {
  it('zips accepted files and closes the archive', async () => {
    const { dz, waitFor } = start();
    await ready(waitFor);
    await dz.scanBrowse([file('a.tsv', 100), file('b.png', 100)], { zipname: 'normal' });
    await waitFor((e) => e.type === 'complete' && e.name === 'endzip');
    // what the Upload button does: close the archive (it is then ready to be sent)
    ModuleEventEmitter.emit('endzip', { name: 'endzip' }, dz.uuid);
    await waitFor((e) => e.type === 'complete' && e.name === 'sendfile');
    expect(await zipEntries('normal.zip')).toEqual(['a.tsv', 'b.png']);
  });

  it('rejects files with another extension, without error', async () => {
    const { dz, events, waitFor } = start();
    await ready(waitFor);
    await dz.scanBrowse([file('a.tsv', 100), file('c.bin', 100)], { zipname: 'rejected' });
    await waitFor((e) => e.type === 'complete' && e.name === 'endzip');
    expect(events.filter((e) => e.type === 'reject').map((e) => e.path)).toEqual(['/c.bin']);
    expect(events.some((e) => e.name === 'errorfile')).toBe(false);
    ModuleEventEmitter.emit('endzip', { name: 'endzip' }, dz.uuid);
    await waitFor((e) => e.type === 'complete' && e.name === 'sendfile');
    expect(await zipEntries('rejected.zip')).toEqual(['a.tsv']);
  });

  it('stops on a single file over the limit', async () => {
    const { dz, events, waitFor } = start();
    await ready(waitFor);
    await dz.scanBrowse([file('big.png', 2 * MAXSIZE)], { zipname: 'toobigfile' });
    const error = await waitFor((e) => e.type === 'message' && e.name === 'errorfile');
    expect(error.message).toBe('The file /big.png is too large to upload (over 1000 Bytes).');
    await waitFor((e) => e.type === 'complete' && e.name === 'ready');
    expect(events.some((e) => e.name === 'endzip')).toBe(false);
  });

  it('stops when the archive grows over the limit', async () => {
    const { dz, events, waitFor } = start();
    await ready(waitFor);
    await dz.scanBrowse([file('p1.png', 400), file('p2.png', 400), file('p3.png', 400)], { zipname: 'toobigarchive' });
    const error = await waitFor((e) => e.type === 'message' && e.name === 'errorfile');
    expect(error.message).toMatch(/^The archive is too large to upload \(over 1000 Bytes\)/);
    expect(error.path).toBe('/p3.png');
    await waitFor((e) => e.type === 'complete' && e.name === 'ready');
    expect(events.some((e) => e.name === 'endzip')).toBe(false);
  });

  it('uses the translated message from the template', async () => {
    const { dz, waitFor } = start({ toolargefile: 'X {file} {max}' });
    await ready(waitFor);
    await dz.scanBrowse([file('big.png', 2 * MAXSIZE)], { zipname: 'template' });
    const error = await waitFor((e) => e.type === 'message' && e.name === 'errorfile');
    expect(error.message).toBe('X /big.png 1000 Bytes');
  });

  // A "too large" error used to leave the archive's exclusive writable open: the file stayed
  // locked, the next upload fell back to '1_<name>.zip', the third one failed with
  // NoModificationAllowedError.
  it('can upload a folder again after two "too large" errors', async () => {
    for (let i = 0; i < 2; i++) {
      const { dz, waitFor } = start();
      await ready(waitFor);
      await dz.scanBrowse([file('big.png', 2 * MAXSIZE)], { zipname: 'again' });
      await waitFor((e) => e.type === 'complete' && e.name === 'ready');
      document.querySelectorAll('.test-page').forEach((el) => el.remove());
    }
    const { dz, waitFor } = start();
    await ready(waitFor);
    await dz.scanBrowse([file('a.tsv', 100)], { zipname: 'again' });
    await waitFor((e) => e.type === 'complete' && e.name === 'endzip', 3000);
    ModuleEventEmitter.emit('endzip', { name: 'endzip' }, dz.uuid);
    await waitFor((e) => e.type === 'complete' && e.name === 'sendfile');
    // same name as the first time: the locked archives were released and removed
    expect(await zipEntries('again.zip')).toEqual(['a.tsv']);
  });
});
