// @vitest-environment node
import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
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
  const plugins = Object.entries(postcssConfig.plugins).map(([name, options]) => {
    // tailwind looks for its config in the current directory: the tests don't run from dev_gui
    if (name === 'tailwindcss') options = { ...options, config: path.join(devgui, 'tailwind.config.js') };
    return fromDevGui(name)(options);
  });
  const from = path.join(cssdir, file);
  const result = await postcss(plugins).process(fs.readFileSync(from, 'utf8'), { from });
  return result.css;
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

  it('tom-select.css keeps the item delete icon', async () => {
    const css = await build('tom-select.css');
    expect(css).toMatch(/\.ts-wrapper \.item \.ts-delet::before\s*\{\s*content:\s*url\(/);
  });
});
