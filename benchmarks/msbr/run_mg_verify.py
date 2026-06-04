"""
benchmarks/msbr/run_mg_verify.py

v0.5.0 OpenMC multi-group self-verification. Asks: does the standard
industrial workflow (CE -> homogenized MGXS library -> MG transport)
recover the continuous-energy reference k_inf on the ORNL MSBR
heterogeneous fuel cell?

This is methods-level verification. CE is the reference (no group
discretization). MG is what production reactor codes actually run.
A large Δ_MG = k_CE - k_MG would mean that standard homogenization
breaks on the MSBR cell — the same physics that drives the v0.4.0
epithermal η ratio (3.72×) would then also break legacy reactor-code
predictions.

Pipeline:
  1. Run CE heterogeneous cell with MGXS tallies over an 8-group
     structure (CASMO-8-like; thermal/epi/fast boundaries chosen to
     match the v0.4.0 spectrum decomposition).
  2. Extract MGXS library from the CE statepoint.
  3. Rebuild the same geometry in MG mode with macroscopic
     cross-sections derived from the CE tally.
  4. Run MG with matching particle budget.
  5. Compute Δ_MG = k_CE − k_MG in pcm and write a result doc.

Inputs (env vars; align with other runners):
  PROMETHEA_PARTICLES   particles per batch (default 20000)
  PROMETHEA_BATCHES     total batches (default 60)
  PROMETHEA_SEED        optional positive int for RNG
  OPENMC_CROSS_SECTIONS path to cross_sections.xml (required for CE)

Output:
  sims/openmc/msbr_mg_verify_ce/  — CE working dir (reference)
  sims/openmc/msbr_mg_verify_mg/  — MG working dir
  out/msbr_mg_verify.json         — k_CE, k_MG, Δ in pcm
  out/msbr_mg_verify.log          — pipeline log
"""
from __future__ import annotations

import json
import math
import os
import pathlib
import sys

import numpy as np
import openmc
import openmc.mgxs

from .geometry_unit_cell import build_unit_cell_geometry


# ---------------------------------------------------------------------------
# Energy group structure. Three-group is too coarse for production code
# verification (it cannot resolve thermal upscattering, narrow resonances,
# or the U-238/Th-232 capture region). Eight groups is the CASMO-style
# coarse standard used by industrial lattice codes. Boundaries chosen
# so the v0.4.0 thermal/epi/fast boundaries (0.625 eV and 0.1 MeV) sit
# on group edges, keeping the spectrum doc cross-comparable.
# ---------------------------------------------------------------------------
GROUP_BOUNDS_EV = [
    0.0,
    0.058,        # well into the thermal Maxwell peak
    0.14,         # thermal
    0.625,        # cd-cutoff (matches v0.4.0 thermal/epi boundary)
    9.118,        # below the 233U 22 eV resonance
    1.305e2,      # epi
    9.119e3,      # epi/fast notional
    1.0e5,        # 0.1 MeV (matches v0.4.0 epi/fast boundary)
    2.0e7,        # upper bound (20 MeV)
]
GROUPS = openmc.mgxs.EnergyGroups(GROUP_BOUNDS_EV)


def _settings(particles, batches, inactive, seed_env, run_mode="eigenvalue",
              energy_mode="continuous-energy"):
    s = openmc.Settings()
    s.particles = particles
    s.batches = batches
    s.inactive = inactive
    s.run_mode = run_mode
    s.energy_mode = energy_mode
    s.verbosity = 6
    if energy_mode == "continuous-energy":
        s.temperature = {"method": "interpolation"}
    if seed_env:
        s.seed = int(seed_env)
    bounds = [-1.0, -1.0, -0.5, 1.0, 1.0, 0.5]
    s.source = openmc.IndependentSource(
        space=openmc.stats.Box(
            bounds[:3], bounds[3:],
            only_fissionable=(energy_mode == "continuous-energy"),
        )
    )
    return s


def _run_ce_with_mgxs(work_ce, particles, batches, inactive, seed_env):
    """Step 1: CE run with MGXS library tallied on the heterogeneous cell."""
    work_ce.mkdir(parents=True, exist_ok=True)
    os.chdir(work_ce)

    geometry, materials = build_unit_cell_geometry()

    # Build an MGXS library covering every CE material.
    mgxs_lib = openmc.mgxs.Library(geometry)
    mgxs_lib.energy_groups = GROUPS
    mgxs_lib.mgxs_types = [
        "total", "absorption", "nu-fission", "fission",
        "nu-scatter matrix", "multiplicity matrix", "chi",
    ]
    mgxs_lib.domain_type = "material"
    mgxs_lib.domains = materials
    mgxs_lib.correction = None    # don't use transport correction
    mgxs_lib.build_library()

    settings = _settings(particles, batches, inactive, seed_env)
    tallies = openmc.Tallies()
    mgxs_lib.add_to_tallies_file(tallies, merge=True)

    materials.export_to_xml()
    geometry.export_to_xml()
    settings.export_to_xml()
    tallies.export_to_xml()

    openmc.run()

    sp_paths = sorted(work_ce.glob("statepoint.*.h5"))
    sp_path = sp_paths[-1]
    sp = openmc.StatePoint(str(sp_path))
    k_ce = float(sp.keff.nominal_value)
    k_ce_s = float(sp.keff.std_dev)
    print(f"[mg_verify] CE k_inf = {k_ce:.6f} ± {k_ce_s:.6f}")

    # Load tallies into the library
    mgxs_lib.load_from_statepoint(sp)
    return k_ce, k_ce_s, mgxs_lib, materials


def _build_mg_library(mgxs_lib, materials, mg_h5_path):
    """Step 2: extract MGXSLibrary from the CE tallies.

    xsdata_names MUST be passed explicitly; otherwise create_mg_library
    falls back to 'set1', 'set2', … and the MG materials cannot find
    macroscopic data by material name.
    """
    names = [m.name for m in materials]
    mg_library = mgxs_lib.create_mg_library(xs_type="macro", xsdata_names=names)
    mg_library.export_to_hdf5(str(mg_h5_path))
    print(f"[mg_verify] MG library written: {mg_h5_path}")
    print(f"[mg_verify] xsdata names      : {names}")
    return mg_library, names


def _run_mg(work_mg, mg_h5_path, mat_names, particles, batches,
            inactive, seed_env):
    """Step 3+4: rebuild geometry with Macroscopic fills and run MG."""
    work_mg.mkdir(parents=True, exist_ok=True)
    os.chdir(work_mg)

    geometry, ce_materials = build_unit_cell_geometry()

    # Build MG materials with macroscopic fills using the CE-tallied names.
    # CE material names are 'MSBR_fuel_salt', 'MSBR_blanket_salt',
    # 'MSBR_graphite', 'MSBR_hastelloyN'. The MGXS library's xsdata
    # names default to the source material names.
    name_to_mg = {}
    for ce_mat in ce_materials:
        mg_mat = openmc.Material(name=ce_mat.name)
        mg_mat.set_density("macro", 1.0)
        mg_mat.add_macroscopic(ce_mat.name)
        name_to_mg[ce_mat.name] = mg_mat

    # Walk the geometry and swap CE -> MG materials by name match.
    for cell in geometry.get_all_cells().values():
        fill = cell.fill
        if isinstance(fill, openmc.Material):
            mg = name_to_mg.get(fill.name)
            if mg is not None:
                cell.fill = mg

    mg_materials = openmc.Materials(list(name_to_mg.values()))
    mg_materials.cross_sections = str(mg_h5_path)

    settings = _settings(particles, batches, inactive, seed_env,
                         energy_mode="multi-group")

    mg_materials.export_to_xml()
    geometry.export_to_xml()
    settings.export_to_xml()

    openmc.run()

    sp_paths = sorted(work_mg.glob("statepoint.*.h5"))
    sp_path = sp_paths[-1]
    sp = openmc.StatePoint(str(sp_path))
    k_mg = float(sp.keff.nominal_value)
    k_mg_s = float(sp.keff.std_dev)
    print(f"[mg_verify] MG k_inf = {k_mg:.6f} ± {k_mg_s:.6f}")
    return k_mg, k_mg_s


def main() -> int:
    particles = int(os.environ.get("PROMETHEA_PARTICLES", 20000))
    batches = int(os.environ.get("PROMETHEA_BATCHES", 60))
    inactive = max(10, batches // 6)
    seed_env = os.environ.get("PROMETHEA_SEED", "").strip()
    repo_root = pathlib.Path(__file__).resolve().parents[2]

    print(f"[mg_verify] particles/batch = {particles}")
    print(f"[mg_verify] total batches   = {batches}  (inactive: {inactive})")
    print(f"[mg_verify] group structure = {len(GROUP_BOUNDS_EV) - 1} groups")
    if seed_env:
        print(f"[mg_verify] seed            = {seed_env}")

    work_ce = (repo_root / "sims/openmc/msbr_mg_verify_ce").resolve()
    work_mg = (repo_root / "sims/openmc/msbr_mg_verify_mg").resolve()

    # Step 1+2: CE reference run with MGXS tallies
    k_ce, k_ce_s, mgxs_lib, materials = _run_ce_with_mgxs(
        work_ce, particles, batches, inactive, seed_env,
    )
    mg_h5 = work_mg / "mgxs.h5"
    mg_h5.parent.mkdir(parents=True, exist_ok=True)
    mg_library, mat_names = _build_mg_library(mgxs_lib, materials, mg_h5)

    # Step 3+4: MG verification run
    k_mg, k_mg_s = _run_mg(
        work_mg, mg_h5, mat_names, particles, batches, inactive, seed_env,
    )

    # Step 5: comparison
    dk = k_ce - k_mg
    dk_s = math.sqrt(k_ce_s ** 2 + k_mg_s ** 2)
    dk_pcm = dk * 1e5
    dk_pcm_s = dk_s * 1e5
    z = dk / dk_s if dk_s > 0 else float("inf")

    result = {
        "k_ce": k_ce, "k_ce_stddev": k_ce_s,
        "k_mg": k_mg, "k_mg_stddev": k_mg_s,
        "delta_pcm": dk_pcm, "delta_pcm_stddev": dk_pcm_s,
        "z_score": z,
        "particles_per_batch": particles,
        "batches": batches, "inactive": inactive,
        "n_groups": len(GROUP_BOUNDS_EV) - 1,
        "group_bounds_ev": GROUP_BOUNDS_EV,
    }

    out_dir = repo_root / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "msbr_mg_verify.json").write_text(json.dumps(result, indent=2))

    summary = (
        f"\n[mg_verify] Results\n"
        f"  k_CE = {k_ce:.6f} ± {k_ce_s:.6f}\n"
        f"  k_MG = {k_mg:.6f} ± {k_mg_s:.6f}\n"
        f"  Δ_MG = k_CE - k_MG = {dk_pcm:+.1f} ± {dk_pcm_s:.1f} pcm (z = {z:+.2f})\n"
    )
    print(summary)
    (out_dir / "msbr_mg_verify.log").write_text(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
