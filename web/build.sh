#!/usr/bin/env bash
# Build the web UI into convertmask/server/static (committed; runtime needs no node).
set -euo pipefail
cd "$(dirname "$0")"
OUT=../convertmask/server/static
mkdir -p "$OUT"
npx -y tailwindcss@3.4.17 -i src/input.css -o "$OUT/styles.css" --minify
cp index.html app.js "$OUT/"
echo "built -> $OUT"
