#!/usr/bin/env node
'use strict'

const { spawnSync } = require('child_process')

const result = spawnSync('standard-readme', ['README.md'], {
  encoding: 'utf8',
  cwd: process.cwd(),
  env: process.env,
})

process.stdout.write(result.stdout || '')
process.stderr.write(result.stderr || '')

if (result.status !== 0 || (result.stdout || '').includes(' warning')) {
  process.exit(1)
}
