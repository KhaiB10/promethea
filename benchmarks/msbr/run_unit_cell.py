"""
benchmarks/msbr/run_unit_cell.py

v0.4.0 first-light MSBR k_inf calculation. Runs the unit-cell geometry
(geometry_unit_cell.build_unit_cell_geometry) under reflective BCs to
get a k_inf at the ORNL-4528 20 kW/L design materials.

This is NOT a reactor calculation. It tells us:
  1. The OpenMC nuclide library has the 233U / 232Th / 7Li nuclides at
     the chosen temperature.
  2. The material recipes give plausible k_inf (well-moderated
     thermal-spectrum unit cell with 0.2 mol% 233U + interstitial
     blanket salt).
  3. The geometry compiles and tallies are wireable.

Inputs (env vars; align with benchmark-msre conventions):
  PROMETHEA_PARTICLES   particles per batch (default 20000)
  PROMETHEA_BATCHES     total batches (default 60)
  PROMETHEA_SEED        optional positive int for RNG
  OPENMC_CROSS_SECTIONS path to cross_sections.xml (required)

Output:
  sims/openmc/msbr_unit_cell/  — OpenMC working directory
  out/msbr_run.log             — captured stdout from the OpenMC run
"""
from __future__ import annotations

import os
import pathlib
import sys

import openmc

from .geometry_unit_cell import build_unit_cell_geometry


def main() -> int:
    particles = int(os.environ.get("PROMETHEA_PARTICLES", 20000))
    batches = int(os.environ.get("PROMETHEA_BATCHES", 60))
    inactive = max(10, batches // 6)
    seed_env = os.environ.get("PROMETHEA_SEED", "").strip()

    work = pathlib.Path("sims/openmc/msbr_unit_cell").resolve()
    work.mkdir(parents=True, exist_ok=True)
    os.chdir(work)

    print(f"[msbr] particles/batch = {particles}")
    print(f"[msbr] total batches   = {batches}  (inactive: {inactive})")
    if seed_env:
        print(f"[msbr] seed            = {seed_env}")

    geometry, materials = build_unit_cell_geometry()

    settings = openmc.Settings()
    settings.particles = particles
    settings.batches = batches
    settings.inactive = inactive
    settings.run_mode = "eigenvalue"
    settings.verbosity = 6
    if seed_env:
        settings.seed = int(seed_env)
    # Box source spanning the bore (more efficient than the default)
    bounds = [-1.0, -1.0, -0.5, 1.0, 1.0, 0.5]
    settings.source = openmc.IndependentSource(
        space=openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True)
    )

    materials.export_to_xml()
    geometry.export_to_xml()
    settings.export_to_xml()

    openmc.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
