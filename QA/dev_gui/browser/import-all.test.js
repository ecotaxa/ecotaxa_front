import { describe, it, expect } from 'vitest';

// Every module must load in a real browser: catches syntax errors, broken imports
// and missing dependencies. Runs in the browser group because several modules touch
// browser APIs as soon as they are imported.
// Unused modules are left out:
// - g6-graph.js: not used
// - js-captcha-mouse.js: not used
// - files/worker_createsynaccesshandle.js: not used, and its syntax error (`await` in a
//   non-async function) breaks Vite's scan of every file of the glob
const modules = import.meta.glob([
  '@modules/**/*.js',
  '!@modules/g6-graph.js',
  '!@modules/js-captcha-mouse.js',
  '!@modules/files/worker_createsynaccesshandle.js',
]);

// Modules known not to load as native ES modules, with the reason.
// They run as it.fails so they stay visible: once fixed, the test turns red,
// and the entry must be removed from this list.
const EXPECTED = {};

async function importModule(load) {
  // rethrow with the full browser message (the default one is truncated)
  return load().catch((err) => {
    throw new Error(`${err.name}: ${err.message}`);
  });
}

describe('every module imports', () => {
  Object.entries(modules).forEach(([path, load]) => {
    const name = path.replace(/^.*(@modules|src\/modules)\//, '');
    if (EXPECTED[name]) {
      it.fails(`${name} (known: ${EXPECTED[name]})`, async () => {
        await importModule(load);
      });
    } else {
      it(name, async () => {
        expect(await importModule(load)).toBeDefined();
      });
    }
  });
});
