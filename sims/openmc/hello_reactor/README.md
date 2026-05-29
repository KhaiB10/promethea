# hello_reactor — toolchain smoke test

The canonical "does OpenMC work on this machine" calculation.

## What it is
A single PWR fuel pin cell:
- 3.0 wt% U-235 enriched UO₂ pellet
- Zircaloy-4 clad
- Light water moderator (with thermal scattering on H-in-H₂O)
- Reflective boundary conditions (infinite lattice)

## Expected result
**k-inf ≈ 1.18 ± ~0.001** (cold, clean, no boron, no fission-product poisons)

This is a published, widely reproduced number. If we get within ~0.5 % of it, the toolchain is healthy. If we don't, something is wrong with our install, our cross sections, or our input deck — and we fix that before we touch the MSRE benchmark.

## Run it
```bash
# Inside the Docker container (or any env with OpenMC + ENDF/B-VIII.0 installed)
python scripts/hello_reactor.py
```

Outputs land in this directory. The script prints k-eff with uncertainty.

## What it is NOT
This is not a Promethea design simulation. It is a "the plumbing works" check that every reactor physicist runs first. The actual project starts with the MSRE benchmark in `benchmarks/msre/`.

## References
- OpenMC documentation, "Modeling a Pin-Cell" tutorial
- Westinghouse 17×17 PWR fuel assembly specifications (public)
