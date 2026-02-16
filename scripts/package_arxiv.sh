#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
BUILD_DIR="$PAPER_DIR/build"
STAGE_DIR="$BUILD_DIR/arxiv_source_staging"
ZIP_PATH="$BUILD_DIR/arxiv_source_upload.zip"

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR/figures" "$STAGE_DIR/sections" "$STAGE_DIR/appendices" "$STAGE_DIR/generated"

cp "$PAPER_DIR/main.tex" "$STAGE_DIR/main.tex"
cp "$PAPER_DIR/references.bib" "$STAGE_DIR/references.bib"

if [[ -f "$BUILD_DIR/main.bbl" ]]; then
  cp "$BUILD_DIR/main.bbl" "$STAGE_DIR/main.bbl"
elif [[ -f "$PAPER_DIR/main.bbl" ]]; then
  cp "$PAPER_DIR/main.bbl" "$STAGE_DIR/main.bbl"
fi

if [[ -d "$PAPER_DIR/sections" ]]; then
  cp "$PAPER_DIR/sections/"*.tex "$STAGE_DIR/sections/" 2>/dev/null || true
fi
if [[ -d "$PAPER_DIR/appendices" ]]; then
  cp "$PAPER_DIR/appendices/"*.tex "$STAGE_DIR/appendices/" 2>/dev/null || true
fi
if [[ -d "$PAPER_DIR/generated" ]]; then
  cp "$PAPER_DIR/generated/"*.tex "$STAGE_DIR/generated/" 2>/dev/null || true
fi
if [[ -d "$PAPER_DIR/figures" ]]; then
  cp "$PAPER_DIR/figures/"*.png "$STAGE_DIR/figures/" 2>/dev/null || true
  cp "$PAPER_DIR/figures/"*.jpg "$STAGE_DIR/figures/" 2>/dev/null || true
  cp "$PAPER_DIR/figures/"*.pdf "$STAGE_DIR/figures/" 2>/dev/null || true
fi

find "$STAGE_DIR" -name "*.aux" -delete
find "$STAGE_DIR" -name "*.log" -delete
find "$STAGE_DIR" -name "*.out" -delete
find "$STAGE_DIR" -name "*.toc" -delete

rm -f "$ZIP_PATH"
(
  cd "$STAGE_DIR"
  zip -r "$ZIP_PATH" . >/dev/null
)

echo "[package_arxiv] Wrote $ZIP_PATH"
