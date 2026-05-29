#!/usr/bin/env bash
# Codespaces post-create: install OpenMC + Promethea deps.
#
# Runs once when the Codespace is first built. Cached afterwards.
# Cross-sections are NOT downloaded here (would slow every rebuild).
# Run `bash scripts/fetch_xs.sh` manually once your Codespace is up.

set -euo pipefail

echo "[promethea] Creating conda env from environment.yml ..."
conda env create -f environment.yml || conda env update -f environment.yml

# Make the env available in every new terminal session.
echo "conda activate promethea" >> ~/.bashrc

echo ""
echo "============================================================"
echo " Promethea Codespace ready."
echo ""
echo " Next steps:"
echo "   1. Open a new terminal (auto-activates the promethea env)"
echo "   2. bash scripts/fetch_xs.sh     # ~4 GB, one-time, 10-30 min"
echo "   3. python scripts/hello_reactor.py             # smoke test"
echo "   4. python benchmarks/msre/run_criticality.py   # MSRE v0"
echo "============================================================"
