# scripts/

Runnable entry points. Each script is self-documenting at the top.

| Script | What it does |
|---|---|
| `fetch_xs.sh` | Download the ENDF/B-VIII.0 HDF5 cross-section library (~4 GB). Run once per workstation. |
| `hello_reactor.py` | PWR pin-cell smoke test. Confirms the OpenMC toolchain is wired up. |

## Convention
- Scripts must work from the repo root: `python scripts/<name>.py` or `bash scripts/<name>.sh`
- Outputs go under `sims/<tool>/<run_name>/`
- No script writes outside the repo without saying so
- Every script that produces a number prints the expected value alongside it
