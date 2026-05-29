# Getting Started

How to go from a fresh `git clone` to a running OpenMC simulation in about 30 minutes (most of which is the cross-section download).

## Option A — Docker (recommended)

Requires only Docker. No conda, no compiler, no OpenMC install on your host.

```bash
# 1. Clone
git clone https://github.com/KhaiB10/promethea
cd promethea

# 2. Build the image (one-time, ~10 min)
docker build -t promethea:dev .

# 3. Fetch cross-section data (one-time, ~4 GB, ~10 min)
docker run --rm -v $PWD:/workspace promethea:dev bash scripts/fetch_xs.sh

# 4. Run the toolchain smoke test
docker run --rm -v $PWD:/workspace promethea:dev python scripts/hello_reactor.py
```

You should see something like:

```
============================================================
  k-eff (combined estimator) = 1.18xxx +/- 0.001xx
  Expected (cold, clean PWR pin cell): k-inf ~ 1.18
============================================================

[hello_reactor] Toolchain check PASSED.
```

If you do, your install is healthy and you can move on to the MSRE benchmark.

## Option B — Native conda (Linux/macOS)

```bash
# 1. Clone
git clone https://github.com/KhaiB10/promethea
cd promethea

# 2. Create the env
micromamba create -n promethea -f environment.yml   # or: conda env create
micromamba activate promethea

# 3. Fetch cross sections
bash scripts/fetch_xs.sh
export OPENMC_CROSS_SECTIONS=$PWD/data/xs/endfb-viii.0-hdf5/cross_sections.xml

# 4. Smoke test
python scripts/hello_reactor.py
```

## Option C — Native pip / Windows

OpenMC is not on PyPI and Windows is unsupported upstream. Use Docker (Option A) or WSL2.

## What's next
After the smoke test passes:
1. Read `arch/PROMETHEA-v0-CONCEPT.md` for the working design
2. Read `docs/ROADMAP.md` for the milestone plan
3. Read `docs/PRINCIPLES.md` for how we work
4. Start on `benchmarks/msre/` — the real Phase 1.1 work

## Troubleshooting
- `OPENMC_CROSS_SECTIONS not set` → re-run `fetch_xs.sh` and export the path
- `Could not find nuclide ...` → cross-section library is incomplete; re-download
- `k-eff way off 1.18` → almost always wrong cross-section data version; verify ENDF/B-VIII.0
- File an issue on GitHub with the full error message
