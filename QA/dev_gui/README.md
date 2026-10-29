# dev_gui tests

Vitest tests of the JS modules in `dev_gui/src/modules`.

- `unit/`: fast tests in a simulated DOM (happy-dom), for pure logic and DOM building.
- `browser/`: tests in a real headless Chromium, for browser storage (OPFS), Workers, `File`, zip.js.
  `browser/import-all.test.js` checks that every module loads as a native ES module.

## Run

```bash
cd dev_gui && npm install            # the modules' own dependencies
cd ../QA/dev_gui && npm install      # test tooling only
npx playwright install chromium      # once, for the browser tests
npm test                             # or test:unit, test:browser, test:watch
```

`npm test` from `dev_gui` runs the same suite.

## Notes

- Modules are imported with the `@modules/` alias (`dev_gui/src/modules`).
  App packages used by the tests (e.g. `@zip.js/zip.js`) resolve from `dev_gui/node_modules`.
- `setup.js` answers `/gui/i18n`, fetched by `alert-box.js` at import time.
- `vitest.config.mjs` has two test-only plugins for code written for webpack:
  every CSS import becomes an empty module, and `botdetect-clean.min.js` (UMD) gets a default export.
- A module that can't load yet can be listed in `EXPECTED` in `browser/import-all.test.js`
  (it then runs as an expected failure).
- Screenshots of failed browser tests go to `.vitest/` (ignored).
