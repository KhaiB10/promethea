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
    ACTIVE_CORE_HEIGHT_HET,
    CORE_RADIUS_HET,
)


# Acceptance envelopes per mode.
ENVELOPE = {
    "homog":       (1.00, 1.15, "homogenized v0"),
    "het":         (0.98, 1.05, "heterogeneous v1 (rods withdrawn, IRPhE salt)"),
    "het_clipped": (0.98, 1.05, "heterogeneous v1c (edge stringers clipped at core cylinder)"),
    "het_lh":      (0.98, 1.10, "heterogeneous v1c + lower-head mix 90.8/9.2 (Phase 1.1.c step 1)"),
}


def build_model(quick: bool = False, mode: str = "homog") -> openmc.Model:
    irphe = mode in ("het", "het_clipped", "het_lh")
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
    if env_batches:
        b = int(env_batches)
        settings.batches = b
        settings.inactive = max(10, b // 4)
    if env_particles:
        settings.particles = int(env_particles)
    print(f"[msre_{mode}] settings: batches={settings.batches} "
          f"inactive={settings.inactive} particles={settings.particles}")

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
    args = parser.parse_args()

    # Allow CI to pick mode without code edits.
    env_mode = os.environ.get("PROMETHEA_MODE", "").lower()
    if env_mode in ("het", "het_clipped", "het_lh", "homog"):
        mode = env_mode
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
