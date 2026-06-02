"""
benchmarks/msbr/run_homog_cell.py

Homogenized companion to run_unit_cell.py. Same particles/batches/seed
env-var contract; calls geometry_unit_cell_homog.build_unit_cell_geometry
instead of the heterogeneous builder.

Outputs:
  sims/openmc/msbr_homog_cell/  -- OpenMC working directory
  out/msbr_homog_run.log        -- captured stdout (CI redirects)
  out/msbr_homog_breeding.txt   -- BR sidecar (BR is trivial in
                                   the homogenized cell because the
                                   blanket-salt 232Th is mixed
                                   straight into the fuel region;
                                   we still tally it for parity)

Note on BR: the homogenized cell mixes 232Th-bearing blanket salt
into the same region as 233U-bearing fuel salt. This destroys the
spatial separation that gives the real two-fluid MSBR its high
breeding ratio, so the homogenized BR is NOT a physically meaningful
breeding figure -- it's a sanity-check tally only. The point of
this run is the *k-eff comparison*.
"""
from __future__ import annotations

import os
import pathlib
import sys

import openmc

from .geometry_unit_cell_homog import build_unit_cell_geometry
from .tallies import (
    build_breeding_tallies,
    read_breeding_results,
    format_summary,
)


def main() -> int:
    particles = int(os.environ.get("PROMETHEA_PARTICLES", 20000))
    batches = int(os.environ.get("PROMETHEA_BATCHES", 60))
    inactive = max(10, batches // 6)
    seed_env = os.environ.get("PROMETHEA_SEED", "").strip()

    work = pathlib.Path("sims/openmc/msbr_homog_cell").resolve()
    work.mkdir(parents=True, exist_ok=True)
    os.chdir(work)

    print(f"[msbr-homog] particles/batch = {particles}")
    print(f"[msbr-homog] total batches   = {batches}  (inactive: {inactive})")
    if seed_env:
        print(f"[msbr-homog] seed            = {seed_env}")

    geometry, materials = build_unit_cell_geometry()

    settings = openmc.Settings()
    settings.particles = particles
    settings.batches = batches
    settings.inactive = inactive
    settings.run_mode = "eigenvalue"
    settings.verbosity = 6
    if seed_env:
        settings.seed = int(seed_env)
    bounds = [-1.0, -1.0, -0.5, 1.0, 1.0, 0.5]
    settings.source = openmc.IndependentSource(
        space=openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True)
    )

    # BR tally: pass the mixed material as "fuel_salt" so the existing
    # tally module finds 233U absorption + 232Th capture in one place.
    # build_breeding_tallies accepts a single material via fuel_salt only.
    mixed = materials[0]
    tallies = build_breeding_tallies(fuel_salt=mixed, blanket_salt=None)

    materials.export_to_xml()
    geometry.export_to_xml()
    settings.export_to_xml()
    tallies.export_to_xml()

    openmc.run()

    sp_paths = sorted(work.glob("statepoint.*.h5"))
    if sp_paths:
        sp_path = str(sp_paths[-1])
        try:
            results = read_breeding_results(
                sp_path, fuel_salt=mixed, blanket_salt=None,
            )
            summary = format_summary(results)
            print(summary)
            out_dir = work.parent.parent.parent / "out"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "msbr_homog_breeding.txt").write_text(summary + "\n")
        except Exception as exc:  # noqa: BLE001
            print(f"[msbr-homog] BR extraction failed: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
