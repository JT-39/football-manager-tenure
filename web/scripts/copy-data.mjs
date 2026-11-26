// Copies the cleaned spells table from the Python pipeline into the website's
// public folder, so the site can fetch it. `make data` builds the source file.
import { copyFileSync, mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const source = resolve(here, '../../data/processed/spells.json')
const target = resolve(here, '../public/data/spells.json')

mkdirSync(dirname(target), { recursive: true })
copyFileSync(source, target)
console.log(`Copied ${source} -> ${target}`)
