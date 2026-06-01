"""
benchmarks/msre/run_criticality.py

Phase 1.1 acceptance test: run the MSRE criticality model in OpenMC
and report k-eff vs the published acceptance envelope.

Two configurations are supported:

  Homogenized v0 (default)
      Salt and graphite smeared in core; loose envelope 1.00 - 1.15.
      Used to validate the toolchain end to end.

  Heterogeneous (--het)
      Explicit 5.08 cm graphite stringers with 1.016 x 3.048 cm fuel
      channels, on a 2-inch square pitch lattice. IRPhE first-criticality
      salt loading (1.408 wt % U-235 in salt at 33.3 wt % U-235 enrichment).
      Acceptance envelope 0.98 - 1.05, target ~1.020 (published OpenMC
      CSG result with rods withdrawn).

Usage
-----
    python benchmarks/msre/run_criticality.py            # homogenized v0
    python benchmarks/msre/run_criticality.py --het      # heterogeneous v1
    python benchmarks/msre/run_criticality.py --quick    # fast smoke run
    python benchmarks/msre/run_criticality.py --het --quick

Environment overrides (used by GitHub Actions CI)
-------------------------------------------------
    PROMETHEA_BATCHES    = override batch count
    PROMETHEA_PARTICLES  = override particles per batch
    PROMETHEA_MODE       = "homog" or "het" (alternative to --het)

Outputs
-------
    sims/openmc/msre_<mode>/  XML inputs, statepoint, tallies
    stdout                    k-eff line and PASS / REVIEW banner
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

try:
    import openmc
except ImportError:
    print("ERROR: OpenMC is not installed in this environment.", file=sys.stderr)
    print("       Use the Docker image or `micromamba install -c conda-forge openmc`.",
          file=sys.stderr)
    sys.exit(1)

# Make the benchmarks/msre directory importable when run as a script.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from materials import build_all, BENCHMARK_TEMP_K            # noqa: E402
from geometry import build_geometry, ACTIVE_CORE_HEIGHT, CORE_RADIUS  # noqa: E402
from geometry_het import (                                    # noqa: E402
    build_geometry_het,
    build_geometry_het_clipped,
    build_geometry_het_lh,
    build_geometry_het_can,
    build_geometry_het_rods_out,
    build_geometry_het_baskets,
    build_geometry_het_critical,
    ACTIVE_CORE_HEIGHT_HET,
    CORE_RADIUS_HET,
)


# Acceptance envelopes per mode.
ENVELOPE = {
    "homog":       (1.00, 1.15, "homogenized v0"),
    "het":         (0.98, 1.05, "heterogeneous v1 (rods withdrawn, IRPhE salt)"),
    "het_clipped": (0.98, 1.05, "heterogeneous v1c (edge stringers clipped at core cylinder)"),
    "het_lh":      (0.98, 1.10, "heterogeneous v1c + lower-head mix 90.8/9.2 (Phase 1.1.c step 1)"),
    "het_can":     (0.98, 1.10, "heterogeneous v1c + lower head + INOR-8 core can (Phase 1.1.c step 2)"),
    "het_rods_out":(0.98, 1.10, "het_can + 4 control rod thimbles, rods fully withdrawn (Phase 1.1.c step 3)"),
    "het_baskets": (0.98, 1.10, "het_rods_out + sample-basket fill at 4th position (Phase 1.1.c step 4)"),
    "het_critical":(0.98, 1.10, "het_baskets + 1 rod inserted 4.4 in (Phase 1.1.c step 5, IRPhE config)"),
}


def build_model(quick: bool = False, mode: str = "homog") -> openmc.Model:
    irphe = mode in ("het", "het_clipped", "het_lh", "het_can", "het_rods_out", "het_baskets", "het_critical")
    mats_dict, mats = build_all(temperature_K=BENCHMARK_TEMP_K, irphe=irphe)

    if mode == "het":
        geometry, extra_mats = build_geometry_het(mats_dict)
        core_radius = CORE_RADIUS_HET
        active_h    = ACTIVE_CORE_HEIGHT_HET
    elif mode == "het_clipped":
        geometry, extra_mats = build_geometry_het_clipped(mats_dict)
        core_radius = CORE_RADIUS_HET
        active_h    = ACTIVE_CORE_HEIGHT_HET
    elif mode == "het_lh":
        geometry, extra_mats = build_geometry_het_lh(mats_dict)
        core_radius = CORE_RADIUS_HET
        active_h    = ACTIVE_CORE_HEIGHT_HET
    elif mode == "het_can":
        geometry, extra_mats = build_geometry_het_can(mats_dict)
        core_radius = CORE_RADIUS_HET
        active_h    = ACTIVE_CORE_HEIGHT_HET
    elif mode == "het_rods_out":
        geometry, extra_mats = build_geometry_het_rods_out(mats_dict)
        core_radius = CORE_RADIUS_HET
        active_h    = ACTIVE_CORE_HEIGHT_HET
    elif mode == "het_baskets":
        geometry, extra_mats = build_geometry_het_baskets(mats_dict)
        core_radius = CORE_RADIUS_HET
        active_h    = ACTIVE_CORE_HEIGHT_HET
    elif mode == "het_critical":
        geometry, extra_mats = build_geometry_het_critical(mats_dict)
        core_radius = CORE_RADIUS_HET
        active_h    = ACTIVE_CORE_HEIGHT_HET
    else:
        geometry, extra_mats = build_geometry(mats_dict)
        core_radius = CORE_RADIUS
        active_h    = ACTIVE_CORE_HEIGHT

    for em in extra_mats:
        mats.append(em)

    settings = openmc.Settings()
    settings.temperature = {"method": "interpolation",
                            "range": (293.15, 1200.0)}
    if quick:
        settings.batches = 30
        settings.inactive = 10
        settings.particles = 5_000
    else:
        settings.batches = 120
        settings.inactive = 30
        settings.particles = 50_000

    # CI / env overrides — let the GitHub Actions workflow scale runs
    # without code edits. Inactive batches scale with total batches.
    env_batches = os.environ.get("PROMETHEA_BATCHES")
    env_particles = os.environ.get("PROMETHEA_PARTICLES")
    env_seed = os.environ.get("PROMETHEA_SEED")
    if env_batches:
        b = int(env_batches)
        settings.batches = b
        settings.inactive = max(10, b // 4)
    if env_particles:
        settings.particles = int(env_particles)
    if env_seed:
        # OpenMC seed must be a positive 64-bit int. We accept any
        # positive integer from the workflow input; default OpenMC
        # behavior (seed=1) is preserved when PROMETHEA_SEED is unset,
        # so v0.2.0 runs remain bit-for-bit reproducible.
        seed = int(env_seed)
        if seed < 1:
            raise ValueError(f"PROMETHEA_SEED must be >= 1, got {seed}")
        settings.seed = seed
    seed_str = f" seed={settings.seed}" if env_seed else ""
    print(f"[msre_{mode}] settings: batches={settings.batches} "
          f"inactive={settings.inactive} particles={settings.particles}{seed_str}")

    # Initial source — a thin slab through the middle of the active core,
    # restricted to fissionable material to get a fast initial guess.
    half_h = active_h / 2.0
    src_box = openmc.stats.Box(
        [-core_radius * 0.8, -core_radius * 0.8, -half_h * 0.5],
        [+core_radius * 0.8, +core_radius * 0.8, +half_h * 0.5],
        only_fissionable=True,
    )
    settings.source = openmc.IndependentSource(space=src_box)
    settings.output = {"summary": False}

    return openmc.Model(geometry=geometry, materials=mats, settings=settings)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true",
                        help="Fast smoke run (fewer batches/particles).")
    parser.add_argument("--het", action="store_true",
                        help="Use heterogeneous lattice geometry + IRPhE salt.")
    parser.add_argument("--het-clipped", action="store_true",
                        help="Heterogeneous geometry with edge stringers clipped at core cylinder.")
    parser.add_argument("--het-lh", action="store_true",
                        help="Clipped het geometry + lower-head 90.8/9.2 mix (Phase 1.1.c step 1).")
    parser.add_argument("--het-can", action="store_true",
                        help="het_lh + INOR-8 core can shell (Phase 1.1.c step 2).")
    parser.add_argument("--het-rods-out", action="store_true",
                        help="het_can + 4 control rod thimbles, rods withdrawn (Phase 1.1.c step 3).")
    parser.add_argument("--het-baskets", action="store_true",
                        help="het_rods_out + sample-basket fill at 4th position (Phase 1.1.c step 4).")
    parser.add_argument("--het-critical", action="store_true",
                        help="het_baskets + 1 rod inserted 4.4 in (Phase 1.1.c step 5, IRPhE configuration).")
    args = parser.parse_args()

    # Allow CI to pick mode without code edits.
    env_mode = os.environ.get("PROMETHEA_MODE", "").lower()
    if env_mode in ("het", "het_clipped", "het_lh", "het_can", "het_rods_out", "het_baskets", "het_critical", "homog"):
        mode = env_mode
    elif args.het_critical:
        mode = "het_critical"
    elif args.het_baskets:
        mode = "het_baskets"
    elif args.het_rods_out:
        mode = "het_rods_out"
    elif args.het_can:
        mode = "het_can"
    elif args.het_lh:
        mode = "het_lh"
    elif args.het_clipped:
        mode = "het_clipped"
    elif args.het:
        mode = "het"
    else:
        mode = "homog"

    lo, hi, label = ENVELOPE[mode]

    repo_root = _HERE.parents[1]
    run_dir = repo_root / "sims" / "openmc" / f"msre_{mode}"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    os.chdir(run_dir)

    xs_lib = os.environ.get("PROMETHEA_XS_LIBRARY", "")
    xs_xml = os.environ.get("OPENMC_CROSS_SECTIONS", "")
    if xs_lib:
        print(f"[msre_{mode}] xs_library={xs_lib}  OPENMC_CROSS_SECTIONS={xs_xml}")

    print(f"[msre_{mode}] Building model (quick={args.quick}, mode={mode}) ...")
    model = build_model(quick=args.quick, mode=mode)

    print(f"[msre_{mode}] Running OpenMC in {run_dir} ...")
    sp_path = model.run(output=True)

    with openmc.StatePoint(sp_path) as sp:
        keff = sp.keff
        k = keff.nominal_value
        sd = keff.std_dev

    passed = lo <= k <= hi
    banner = "PASS" if passed else "REVIEW"

    print()
    print("=" * 64)
    print(f"  k-eff (combined) = {k:.5f} +/- {sd:.5f}")
    print(f"  Acceptance envelope ({label}): {lo:.2f} <= k <= {hi:.2f}")
    print(f"  Result: {banner}")
    print("=" * 64)
    if not passed:
        print("  Note: out-of-envelope does not necessarily mean a bug.")
        print("        Inspect material build, S(a,b) treatment, and source.")
        sys.exit(2)


if __name__ == "__main__":
    main()
