#!/usr/bin/env bash
# Fetch ENDF/B-VIII.0 HDF5 cross-section library for OpenMC.
# About 4 GB. Done once per workstation.
#
# Usage:  bash scripts/fetch_xs.sh
set -euo pipefail

XS_DIR="${XS_DIR:-data/xs}"
URL="https://anl.box.com/shared/static/uhbxlrx7hvxqw27psymfbhi7bx7s6u6a.xz"
ARCHIVE="endfb-viii.0-hdf5.tar.xz"

mkdir -p "$XS_DIR"
cd "$XS_DIR"

if [[ -f "endfb-viii.0-hdf5/cross_sections.xml" ]]; then
    echo "[fetch_xs] Cross sections already present at $(pwd)/endfb-viii.0-hdf5/"
    exit 0
fi

echo "[fetch_xs] Downloading $URL (~4 GB) ..."
curl -L -o "$ARCHIVE" "$URL"

echo "[fetch_xs] Extracting ..."
tar xJf "$ARCHIVE"
rm "$ARCHIVE"

echo "[fetch_xs] Done. Set OPENMC_CROSS_SECTIONS=$(pwd)/endfb-viii.0-hdf5/cross_sections.xml"
