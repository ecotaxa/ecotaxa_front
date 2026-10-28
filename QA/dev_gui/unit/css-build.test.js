// @vitest-environment node
import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

// The CSS files imported by JS modules go through dev_gui's postcss config (tailwind) in the
// webpack build. Each one is processed on its own here: an @apply of a class defined only in
// style.css then fails, as it does in the build when style.css isn't processed first.
const here = path.dirname(fileURLToPath(import.meta.url));
const devgui = path.resolve(here, '../../../dev_gui');
const fromDevGui = createRequire(path.join(devgui, 'package.json'));
const postcss = fromDevGui('postcss');
const postcssConfig = fromDevGui('./postcss.config.js');

const cssdir = path.join(devgui, 'src/css');
// style.css is the tailwind entry (@tailwind directives), built by itself
const modulecss = fs.readdirSync(cssdir).filter((f) => f.endsWith('.css') && f !== 'style.css');

async function build(file) {
  const from = path.join(cssdir, file);
  // postcss-loader calls the config with the file being built
  const plugins = Object.entries(postcssConfig({ file: from }).plugins).map(([name, options]) => fromDevGui(name)(options));
  const result = await postcss(plugins).process(fs.readFileSync(from, 'utf8'), { from });
  return result.css;
}

// tailwind keeps its contexts for the life of the process: an order of build is checked in a new one,
// run from dev_gui as webpack is
function buildInNewProcess(files) {
  const script = `
    const fs = require('fs'), path = require('path');
    const postcss = require('postcss');
    const postcssConfig = require('./postcss.config.js');
    (async () => {
      const css = {};
      for (const file of JSON.parse(process.argv[1])) {
        const from = path.join(${JSON.stringify(cssdir)}, file);
        const plugins = Object.entries(postcssConfig({ file: from }).plugins).map(([name, options]) => require(name)(options));
        css[file] = (await postcss(plugins).process(fs.readFileSync(from, 'utf8'), { from })).css;
      }
      process.stdout.write(JSON.stringify(css));
    })();`;
  return JSON.parse(execFileSync(process.execPath, ['-e', script, JSON.stringify(files)], { cwd: devgui, maxBuffer: 64 * 1024 * 1024 }));
}

describe('module CSS builds on its own', () => {
  it('finds the module CSS files', () => {
    expect(modulecss).toEqual(expect.arrayContaining(['js-tree.css', 'tom-select.css']));
  });

  modulecss.forEach((file) => {
    it(file, async () => {
      await expect(build(file)).resolves.toBeTypeOf('string');
    });
  });

  // webpack builds the CSS files in parallel: the output must not depend on style.css being processed first
  it('module CSS is the same after style.css', () => {
    const alone = buildInNewProcess(modulecss);
    const after = buildInNewProcess(['style.css', ...modulecss]);
    modulecss.forEach((file) => expect(after[file], file).toBe(alone[file]));
  }, 60000);

  it('tom-select.css keeps the item delete icon', async () => {
    const css = await build('tom-select.css');
    expect(css).toMatch(/\.ts-wrapper \.item \.ts-delet::before\s*\{\s*content:\s*url\(/);
  });
});

describe('tailwind content', () => {
  // the build output is minified: its identifiers become classes (e.g. `!on` → .\!on), and the CSS
  // of a build would depend on the JS of the previous one
  it('does not scan the build output', () => {
    const { content } = fromDevGui('./tailwind.config.js');
    content.forEach((glob) => expect(path.resolve(devgui, glob)).not.toContain(path.join('appli', 'static', 'gui')));
  });
});
