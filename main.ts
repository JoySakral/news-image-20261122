// News-image entry runner (Node 22, standard library only).
// The entry is the PNG beside this file; this program copies it into the
// output directory (MAKEFUN_OUTPUT_DIR, or /output inside the grader).
// The gate takes one PNG or JPEG of at most 1 MiB and 1024 by 1024 pixels,
// and the judge sees exactly the bytes copied, so the copy must be exact.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const MAX_BYTES = 1024 * 1024;
const MAX_DIMENSION = 1024;

const sourcePath = new URL('./entry.png', import.meta.url);
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const outputPath = join(outputDir, 'entry.png');

// The source must exist and be a regular file before anything else happens.
if (!existsSync(sourcePath)) {
  throw new Error(`entry image not found: ${sourcePath}`);
}
const sourceStat = statSync(sourcePath);
if (!sourceStat.isFile()) {
  throw new Error(`entry image is not a file: ${sourcePath}`);
}
if (sourceStat.size === 0 || sourceStat.size > MAX_BYTES) {
  throw new Error(`entry image size ${sourceStat.size} bytes is outside the 1 byte..1 MiB range`);
}

// Read the PNG dimensions straight from the IHDR chunk (stdlib only):
// an 8-byte signature, then a 4-byte length and the "IHDR" tag, then width
// and height as big-endian 32-bit integers.
function pngDimensions(path) {
  const bytes = readFileSync(path);
  const expected = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  if (!bytes.subarray(0, 8).equals(expected)) {
    throw new Error('entry image is not a PNG file');
  }
  if (bytes.subarray(12, 16).toString('ascii') !== 'IHDR') {
    throw new Error('entry image has no IHDR chunk');
  }
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

const { width, height } = pngDimensions(sourcePath);
if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
  throw new Error(`entry image is ${width}x${height}, larger than the 1024x1024 limit`);
}

mkdirSync(outputDir, { recursive: true });
copyFileSync(sourcePath, outputPath);

const copiedStat = statSync(outputPath);
if (copiedStat.size !== sourceStat.size) {
  throw new Error(`copied entry.png is ${copiedStat.size} bytes, expected ${sourceStat.size}`);
}

// Byte-level check: the judge sees exactly what is copied, so the output
// must be identical to the source, not just the same length.
const sourceBytes = readFileSync(sourcePath);
const copiedBytes = readFileSync(outputPath);
if (!sourceBytes.equals(copiedBytes)) {
  throw new Error('copied entry.png differs from the source');
}

console.log(`entry.png ${width}x${height}, ${sourceStat.size} bytes -> ${outputPath} (byte-identical)`);
