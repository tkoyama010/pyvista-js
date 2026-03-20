#!/usr/bin/env node
'use strict';

// CommonJS require() respects NODE_PATH, which pre-commit sets to the hook's
// node_modules. This bypasses Prettier 3.x's ESM import() resolution that
// only looks in the project's node_modules (cwd-based).
const prettier = require('prettier');
const plugin = require('prettier-plugin-jinja-template');
const fs = require('fs');

const files = process.argv.slice(2);

Promise.all(
  files.map(async (file) => {
    const source = fs.readFileSync(file, 'utf8');
    const formatted = await prettier.format(source, {
      parser: 'jinja-template',
      plugins: [plugin],
    });
    if (source !== formatted) {
      fs.writeFileSync(file, formatted);
    }
  })
).catch((err) => {
  console.error(err);
  process.exit(1);
});
