# Simulations

Input decks and run scripts for each simulation toolchain.

## Layout
- `openmc/` — neutronics (Monte Carlo transport, depletion)
- `griffin/` — multiphysics reactor analysis (MOOSE-based)
- `openfoam/` — thermal-hydraulics, CFD

## Convention
Each subdirectory contains:
- `inputs/` — the actual input files (deterministic, version-controlled)
- `scripts/` — Python wrappers that build, run, post-process
- `results/` — committed only for small artifacts (CSV, key plots); large HDF5/Exodus files go to releases or external storage
- `README.md` — what's being simulated, against what reference, what we expect

## Reproducibility rule
Every figure or claim in the papers must trace back to an input deck here, runnable via a single script.
