import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';
import { playwright } from '@vitest/browser-playwright';

// Tests of dev_gui/src/modules. The modules and their dependencies stay in dev_gui
// (dev_gui/node_modules must be installed); only the test tooling is installed here.
const here = path.dirname(fileURLToPath(import.meta.url));
const devgui = path.resolve(here, '../../dev_gui');
// app packages imported by the tests themselves resolve from dev_gui, like the modules do
const fromDevGui = createRequire(path.join(devgui, 'package.json'));
// production build output (npm run build in dev_gui): its CSS can be loaded by browser tests
const dist = path.resolve(here, '../../appli/static/gui/dist');

// two test groups:
// - unit: fast, simulated DOM (happy-dom) - pure logic and DOM building
// - browser: real headless Chromium - browser storage (OPFS), Workers, File, zip.js
export default defineConfig({
  resolve: {
    alias: {
      '@modules': path.join(devgui, 'src/modules'),
      '@dist': dist,
      '@zip.js/zip.js': fromDevGui.resolve('@zip.js/zip.js'),
    },
  },
  server: {
    fs: {
      allow: [here, devgui, dist],
    },
  },
  plugins: [{
    // CSS is not under test. Modules import CSS the webpack way (`import x from '….css'`,
    // default export from style-loader, tailwind @apply on classes defined elsewhere):
    // replace every CSS file by an empty module (except `?raw` imports: built CSS read by tests)
    name: 'css-stub',
    enforce: 'pre',
    resolveId(source) {
      const [file, query = ''] = source.split('?');
      // glob patterns (import.meta.glob('….css')) are resolved through plugins too: leave them
      if (file.endsWith('.css') && !file.includes('*') && !/(^|&)raw(&|$)/.test(query)) return '\0css-stub';
    },
    load(id) {
      if (id === '\0css-stub') return 'export default "";';
    },
  }, {
    // botdetect-clean.min.js is a UMD bundle: webpack reads it as CommonJS (default export =
    // module.exports); served as a native ES module it only sets the global self.BotDetect
    name: 'botdetect-shim',
    transform(code, id) {
      if (id.split('?')[0].endsWith('/botdetect-clean.min.js')) {
        return code + '\nexport default self.BotDetect;\n';
      }
    },
  }],
  test: {
    projects: [{
        extends: true,
        test: {
          name: 'unit',
          environment: 'happy-dom',
          include: ['unit/**/*.test.js'],
          setupFiles: ['setup.js'],
        },
      },
      {
        extends: true,
        test: {
          name: 'browser',
          include: ['browser/**/*.test.js'],
          setupFiles: ['setup.js'],
          browser: {
            enabled: true,
            provider: playwright(),
            headless: true,
            instances: [{
              browser: 'chromium'
            }],
          },
        },
      },
    ],
  },
});
