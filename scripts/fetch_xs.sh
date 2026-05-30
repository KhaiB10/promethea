#!/usr/bin/env bash
# Fetch a prebuilt OpenMC HDF5 cross-section library archive.
# Archives are ~1.7-2.7 GB compressed. Done once per cache lifetime per
# library. Sources are the canonical anl.box.com mirrors listed at
# https://openmc.org/data/.
#
# Usage:
#   bash scripts/fetch_xs.sh                  # default: endfb-viii.0
#   bash scripts/fetch_xs.sh endfb-vii.1
#   bash scripts/fetch_xs.sh jeff-3.3
#
# Supported libraries (key -> extracted dir / URL):
#   endfb-viii.0  -> endfb-viii.0-hdf5/cross_sections.xml
#   endfb-vii.1   -> endfb-vii.1-hdf5/cross_sections.xml
#   jeff-3.3      -> jeff-3.3-hdf5/cross_sections.xml
set -euo pipefail

LIB="${1:-endfb-viii.0}"
XS_DIR="${XS_DIR:-data/xs}"

case "$LIB" in
    endfb-viii.0)
        URL="https://anl.box.com/shared/static/uhbxlrx7hvxqw27psymfbhi7bx7s6u6a.xz"
        DIRNAME="endfb-viii.0-hdf5"
        ARCHIVE="endfb-viii.0-hdf5.tar.xz"
        ;;
    endfb-vii.1)
        URL="https://anl.box.com/shared/static/9igk353zpy8fn9ttvtrqgzvw1vtejoz6.xz"
        DIRNAME="endfb-vii.1-hdf5"
        ARCHIVE="endfb-vii.1-hdf5.tar.xz"
        ;;
    jeff-3.3)
        URL="https://anl.box.com/shared/static/4jwkvrr9pxlruuihcrgti75zde6g7bum.xz"
        DIRNAME="jeff-3.3-hdf5"
        ARCHIVE="jeff-3.3-hdf5.tar.xz"
        ;;
    *)
        echo "[fetch_xs] Unknown library: $LIB" >&2
        echo "[fetch_xs] Supported: endfb-viii.0, endfb-vii.1, jeff-3.3" >&2
        exit 1
        ;;
esac

mkdir -p "$XS_DIR"
cd "$XS_DIR"

if [[ -f "$DIRNAME/cross_sections.xml" ]]; then
    echo "[fetch_xs] Cross sections already present at $(pwd)/$DIRNAME/"
    exit 0
fi

echo "[fetch_xs] Library: $LIB"
echo "[fetch_xs] Downloading $URL ..."
curl -L -o "$ARCHIVE" "$URL"

echo "[fetch_xs] Extracting ..."
tar xJf "$ARCHIVE"
rm "$ARCHIVE"

if [[ ! -f "$DIRNAME/cross_sections.xml" ]]; then
    echo "[fetch_xs] WARNING: extracted archive did not produce expected dir '$DIRNAME'." >&2
    echo "[fetch_xs] Contents of $(pwd):" >&2
    ls -la >&2
    exit 2
fi

echo "[fetch_xs] Done. Set OPENMC_CROSS_SECTIONS=$(pwd)/$DIRNAME/cross_sections.xml"
